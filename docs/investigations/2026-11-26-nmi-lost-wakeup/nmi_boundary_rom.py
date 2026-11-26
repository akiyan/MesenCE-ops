#!/usr/bin/env python3
"""Make a test ROM (SNES, LoROM, 32 KiB) that shows after which instruction the VBlank NMI is taken.

A scheduler that updates a word of signal bits without holding off the NMI loses a bit that the NMI
sets between its read and its write:

    seq:  STA $22,X     ; 95 22     5 cycles (16-bit A, 8-bit X, D = 0): 8 + 8 + 6 + 8 + 8 master clocks
          LDA $32,X     ; B5 32     5 cycles
          AND #$FFFC    ; 29 FC FF  3 cycles
          STA $32,X     ; 95 32     5 cycles

The ROM runs this sequence around the NMI at 96 start positions, 2 master clocks apart, for the frames
of each field (the frames differ by 4 master clocks without interlace). Each test:

  1. waits for the wanted field ($213F bit 7), then WAI: the NMI's return puts the CPU at a fixed
     distance from the NMI;
  2. burns about a frame (COARSE turns of DEX / BNE, 36 clocks each) and jumps to the test's pad:
     i times LDY #0 (16 clocks) and 95 - i times NOP (14 clocks);
  3. runs the sequence; the NMI handler keeps its return address and sets bit 3 of $3A;
  4. stores the return address and the word at $1000 + 4 * (96 * field + test).

At the end the screen shows, for each field, the 96 tests in three rows of 32: first where the NMI
was taken ('-' before the sequence, 0 before its STA, 2 after it, 4 after the LDA, 7 after the AND,
9 after the last STA, '+' later), then whether bit 3 is still set (1) or was lost (0). $1C becomes 1.
The bit is lost where the NMI is taken at 4 or 7.

  nmi_boundary_rom.py OUT.sfc [--coarse N]
"""
import argparse
from pathlib import Path
import struct

TESTS = 96
RESULTS = 0x1000
COARSE = 9570          # turns of the coarse loop: puts the sequence around the NMI on MesenCE (calibrated 2026-11-26)
SEQ_OFFSETS = (0, 2, 4, 7, 9)   # return addresses inside the sequence: before STA, after it, after LDA, AND, STA

GLYPHS = {
    '0': '01110 10001 10011 10101 11001 10001 01110', '1': '00100 01100 00100 00100 00100 00100 01110',
    '2': '01110 10001 00001 00010 00100 01000 11111', '3': '11110 00001 00001 01110 00001 00001 11110',
    '4': '00010 00110 01010 10010 11111 00010 00010', '5': '11111 10000 11110 00001 00001 10001 01110',
    '6': '00110 01000 10000 11110 10001 10001 01110', '7': '11111 00001 00010 00100 01000 01000 01000',
    '8': '01110 10001 10001 01110 10001 10001 01110', '9': '01110 10001 10001 01111 00001 00010 01100',
    'A': '01110 10001 10001 11111 10001 10001 10001', 'B': '11110 10001 10001 11110 10001 10001 11110',
    'C': '01110 10001 10000 10000 10000 10001 01110', 'D': '11100 10010 10001 10001 10001 10010 11100',
    'E': '11111 10000 10000 11110 10000 10000 11111', 'F': '11111 10000 10000 11110 10000 10000 10000',
    '-': '00000 00000 00000 11111 00000 00000 00000', '+': '00000 00100 00100 11111 00100 00100 00000',
    ' ': '00000 00000 00000 00000 00000 00000 00000',
}
CHARS = '0123456789ABCDEF-+ '
MINUS, PLUS, BLANK = CHARS.index('-'), CHARS.index('+'), CHARS.index(' ')


def font():
    """2bpp tiles (16 bytes each): the glyph in plane 0, one dot from the left, one line from the top."""
    out = bytearray()
    for ch in CHARS:
        rows = [0] + [int(row, 2) << 2 for row in GLYPHS[ch].split()]
        for row in rows:
            out += bytes([row, 0])
    return bytes(out)


class Asm:
    """Bytes at $00:8000 with labels; relative branches and 16-bit addresses are fixed up at the end."""

    def __init__(self, origin=0x8000):
        self.origin, self.code, self.labels, self.fixes = origin, bytearray(), {}, []

    def here(self):
        return self.origin + len(self.code)

    def label(self, name):
        assert name not in self.labels, name
        self.labels[name] = self.here()

    def b(self, *values):
        self.code += bytes(values)

    def w(self, opcode, value):
        """An opcode with a 16-bit operand: a number or a label."""
        self.code.append(opcode)
        if isinstance(value, str):
            self.fixes.append((len(self.code), value, 'abs'))
            value = 0
        self.code += struct.pack('<H', value & 0xFFFF)

    def br(self, opcode, target):
        self.code += bytes([opcode, 0])
        self.fixes.append((len(self.code) - 1, target, 'rel'))

    def data(self, values):
        self.code += bytes(values)

    def finish(self):
        for at, name, kind in self.fixes:
            target = self.labels[name]
            if kind == 'abs':
                struct.pack_into('<H', self.code, at, target)
            else:
                delta = target - (self.origin + at + 1)
                assert -128 <= delta <= 127, (name, delta)
                self.code[at] = delta & 0xFF
        return bytes(self.code)


def program(coarse):
    a = Asm()
    # --- reset: native mode, 16-bit A and X, stack, direct page 0
    a.label('reset')
    a.b(0x78, 0x18, 0xFB)                 # SEI, CLC, XCE
    a.b(0xC2, 0x38)                       # REP #$38 (16-bit A and X, decimal off)
    a.w(0xA2, 0x1FFF); a.b(0x9A)          # LDX #$1FFF, TXS
    a.w(0xA9, 0x0000); a.b(0x5B)          # LDA #0, TCD
    a.b(0xE2, 0x20)                       # SEP #$20 (8-bit A)
    a.b(0xA9, 0x8F); a.w(0x8D, 0x2100)    # screen off
    a.w(0x9C, 0x4200); a.w(0x9C, 0x420B); a.w(0x9C, 0x420C)    # no NMI, DMA or HDMA yet
    a.w(0x9C, 0x2105)                     # BG mode 0
    a.b(0xA9, 0x04); a.w(0x8D, 0x2107)    # BG1 map at VRAM $0400
    a.w(0x9C, 0x210B)                     # BG1 tiles at VRAM $0000
    a.b(0xA9, 0x01); a.w(0x8D, 0x212C)    # BG1 on the main screen
    a.w(0x9C, 0x2121)                     # palette: 0 black, 1 white
    a.w(0x9C, 0x2122); a.w(0x9C, 0x2122)
    a.b(0xA9, 0xFF); a.w(0x8D, 0x2122); a.b(0xA9, 0x7F); a.w(0x8D, 0x2122)
    a.b(0xA9, 0x80); a.w(0x8D, 0x2115)    # VRAM address steps after the high byte
    a.w(0x9C, 0x2116); a.w(0x9C, 0x2117)  # tiles from VRAM $0000
    a.w(0xA2, 0x0000)
    a.label('font_loop')
    a.w(0xBD, 'font'); a.w(0x8D, 0x2118)  # LDA font,X: plane 0 ...
    a.b(0xE8)
    a.w(0xBD, 'font'); a.w(0x8D, 0x2119)  # ... and plane 1
    a.b(0xE8)
    a.w(0xE0, len(font())); a.br(0xD0, 'font_loop')
    a.w(0x9C, 0x2116); a.b(0xA9, 0x04); a.w(0x8D, 0x2117)      # the map: all blank
    a.w(0xA2, 32 * 32)
    a.label('map_loop')
    a.b(0xA9, BLANK); a.w(0x8D, 0x2118); a.w(0x9C, 0x2119)
    a.b(0xCA); a.br(0xD0, 'map_loop')
    a.b(0xC2, 0x20)                       # REP #$20 (16-bit A)
    a.b(0x64, 0x16); a.b(0x64, 0x1A); a.b(0x64, 0x1C); a.b(0x64, 0x1E)   # NMI count, field, done, table base
    a.b(0xE2, 0x20); a.b(0xA9, 0x80); a.w(0x8D, 0x4200); a.b(0xC2, 0x20)  # NMI on
    # --- the tests of one field
    a.label('field_loop')
    a.b(0x64, 0x10)                       # test = 0
    a.label('test_loop')
    a.label('wait_field')                 # start in a frame of the wanted field
    a.b(0xE2, 0x20); a.w(0xAD, 0x213F); a.b(0xC2, 0x20)
    a.w(0x29, 0x0080); a.b(0xC5, 0x1A); a.br(0xF0, 'field_ok')
    a.b(0xCB); a.br(0x80, 'wait_field')   # WAI, again
    a.label('field_ok')
    a.b(0xCB)                             # WAI: the NMI's return is the time base
    a.w(0xA9, 0x0881); a.b(0x85, 0x3A)    # the signal word as the title had it
    a.b(0x64, 0x2A); a.b(0x64, 0x14)      # nothing awaited, no return address yet
    a.b(0xA5, 0x16); a.b(0x85, 0x18)      # the NMI count before the sequence
    a.w(0xA2, coarse)
    a.label('coarse')
    a.b(0xCA); a.br(0xD0, 'coarse')       # DEX, BNE
    a.b(0xE2, 0x10)                       # SEP #$10 (8-bit X and Y)
    a.b(0xA5, 0x10); a.b(0x0A); a.b(0xAA) # LDA test, ASL, TAX
    a.w(0x7C, 'pads')                     # JMP (pads,X)
    # --- the pads: 2 master clocks more for each test
    for i in range(TESTS):
        a.label(f'pad{i}')
        for _ in range(i): a.b(0xA0, 0x00)            # LDY #0: 16 clocks
        for _ in range(TESTS - 1 - i): a.b(0xEA)      # NOP: 14 clocks
        a.w(0x4C, 'seq_pre')
    a.label('pads')
    for i in range(TESTS):
        a.fixes.append((len(a.code), f'pad{i}', 'abs')); a.b(0, 0)
    # --- the sequence
    a.label('seq_pre')
    a.b(0xA2, 0x08)                       # LDX #8
    a.w(0xA9, 0x0008)                     # LDA #$0008: the signal to wait for
    a.label('seq')
    a.b(0x95, 0x22)                       # STA $22,X
    a.b(0xB5, 0x32)                       # LDA $32,X
    a.w(0x29, 0xFFFC)                     # AND #$FFFC
    a.b(0x95, 0x32)                       # STA $32,X
    for _ in range(8): a.b(0xEA)
    a.label('wait_nmi')                   # the NMI of this frame, if it has not come yet
    a.b(0xA5, 0x16); a.b(0xC5, 0x18); a.br(0xF0, 'wait_nmi')
    a.b(0xC2, 0x10)                       # REP #$10 (16-bit X)
    a.b(0xA5, 0x10); a.b(0x0A); a.b(0x0A); a.b(0x18); a.b(0x65, 0x1E); a.b(0xAA)   # X = 4 * test + table base
    a.b(0xA5, 0x14); a.w(0x9D, RESULTS)   # the NMI's return address
    a.b(0xA5, 0x3A); a.w(0x9D, RESULTS + 2)   # the signal word after the sequence
    a.b(0xE6, 0x10); a.b(0xA5, 0x10); a.w(0xC9, TESTS); a.br(0xF0, 'field_done')
    a.w(0x4C, 'test_loop')
    a.label('field_done')
    a.b(0xA5, 0x1A); a.br(0xD0, 'show')   # both fields done
    a.w(0xA9, 0x0080); a.b(0x85, 0x1A)    # the other field
    a.w(0xA9, 4 * TESTS); a.b(0x85, 0x1E)
    a.w(0x4C, 'field_loop')
    # --- the results on the screen: for each field, where the NMI was taken, then bit 3
    a.label('show')
    a.b(0xE2, 0x20); a.w(0x9C, 0x4200); a.b(0xC2, 0x20)        # NMI off
    a.w(0xA9, 0x0400 + 2 * 32); a.w(0x8D, 0x2116)
    for field in range(2):
        base = RESULTS + 4 * TESTS * field
        n = f'{field}'
        a.w(0xA2, 0x0000)
        a.label('where' + n)
        a.w(0xBD, base); a.b(0x38); a.w(0xE9, 'seq')           # LDA base,X, SEC, SBC #seq
        a.br(0x30, 'before' + n)
        a.w(0xC9, 0x0010); a.br(0xB0, 'after' + n)
        a.br(0x80, 'put' + n)
        a.label('before' + n); a.w(0xA9, MINUS); a.br(0x80, 'put' + n)
        a.label('after' + n); a.w(0xA9, PLUS)
        a.label('put' + n)
        a.b(0xE2, 0x20); a.w(0x8D, 0x2118); a.w(0x9C, 0x2119); a.b(0xC2, 0x20)
        a.b(0xE8, 0xE8, 0xE8, 0xE8); a.w(0xE0, 4 * TESTS); a.br(0xD0, 'where' + n)
        a.w(0xA2, 0x0000)
        a.label('bit' + n)
        a.w(0xBD, base + 2); a.w(0x29, 0x0008); a.br(0xF0, 'lost' + n)
        a.w(0xA9, 0x0001)
        a.label('lost' + n)
        a.b(0xE2, 0x20); a.w(0x8D, 0x2118); a.w(0x9C, 0x2119); a.b(0xC2, 0x20)
        a.b(0xE8, 0xE8, 0xE8, 0xE8); a.w(0xE0, 4 * TESTS); a.br(0xD0, 'bit' + n)
    a.b(0xE2, 0x20); a.b(0xA9, 0x0F); a.w(0x8D, 0x2100); a.b(0xC2, 0x20)   # screen on
    a.w(0xA9, 0x0001); a.b(0x85, 0x1C)    # done
    a.label('end'); a.br(0x80, 'end')
    # --- NMI: keep the return address, set bit 3 of the signal word
    a.label('nmi')
    a.b(0xC2, 0x20); a.b(0x48)            # REP #$20, PHA
    a.b(0xA3, 0x04); a.b(0x85, 0x14)      # LDA 4,S (the return address), STA $14
    a.b(0xA5, 0x3A); a.w(0x09, 0x0008); a.b(0x85, 0x3A)
    a.b(0xE6, 0x16)                       # INC the NMI count
    a.b(0xE2, 0x20); a.w(0xAD, 0x4210); a.b(0xC2, 0x20)        # acknowledge
    a.b(0x68, 0x40)                       # PLA, RTI
    a.label('irq'); a.b(0x40)
    a.label('font'); a.data(font())
    code = a.finish()
    return code, a.labels


def rom(coarse=COARSE):
    code, labels = program(coarse)
    image = bytearray(b'\xFF' * 0x8000)
    if len(code) > 0x7FB0:
        raise ValueError('The program does not fit the bank')
    image[:len(code)] = code
    image[0x7FC0:0x7FD5] = b'NMI BOUNDARY TEST'.ljust(21)
    image[0x7FD5:0x7FDC] = bytes([0x20, 0x00, 0x05, 0x00, 0x01, 0x33, 0x00])   # LoROM, ROM only, 32 KiB
    for vector in range(0x7FE0, 0x8000, 2):
        struct.pack_into('<H', image, vector, labels['irq'])
    struct.pack_into('<H', image, 0x7FEA, labels['nmi'])     # native NMI
    struct.pack_into('<H', image, 0x7FFC, labels['reset'])   # reset (emulation mode)
    image[0x7FDC:0x7FE0] = bytes([0xFF, 0xFF, 0x00, 0x00])
    checksum = sum(image) & 0xFFFF
    struct.pack_into('<HH', image, 0x7FDC, checksum ^ 0xFFFF, checksum)
    return bytes(image), labels


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('output', type=Path)
    p.add_argument('--coarse', type=int, default=COARSE)
    a = p.parse_args()
    image, labels = rom(a.coarse)
    a.output.write_bytes(image)
    print(f"seq ${labels['seq']:04X}, nmi ${labels['nmi']:04X}, {len(image)} bytes")


if __name__ == '__main__':
    main()
