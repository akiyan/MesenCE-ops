#!/usr/bin/env python3
"""Run the NMI boundary test ROM (nmi_boundary_rom.py) on mesen-headless and print its table.

For each field, a row of the 96 tests: where the NMI was taken ('-' before the sequence, 0 before its
first STA, 2 after it, 4 after the LDA, 7 after the AND, 9 after the last STA, A-F in the NOPs after
it, '+' later), and a row with bit 3 of the signal word (1 kept, 0 lost). The bit must be lost exactly
where the NMI was taken at 4 or 7. --expect compares with the table of MesenCE (the fork of 2.2.1,
2026-11-26): a difference means the timing of the NMI against the instructions changed.

  run_nmi_boundary.py --binary bin/mesen-headless [--expect] [--png OUT.png] [--rom OUT.sfc]
"""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import nmi_boundary_rom  # noqa: E402

MESENCE = {
    0: 'AAAA99999999999999999997777777777774444444444444444444222222222222222222000000000000------------',
    1: 'AAAAA9A99999999999999999997777777777774444444444444444444222222222222222222000000000000---------',
}


def symbol(offset):
    return '-' if offset < 0 else '+' if offset >= 16 else f'{offset:X}'


def run(binary, work, png=None):
    image, labels = nmi_boundary_rom.rom()
    rom = work / 'nmi-boundary.sfc'
    rom.write_bytes(image)
    out = work / 'table.tsv'
    env = dict(os.environ, NMI_BOUNDARY_OUT=str(out), NMI_BOUNDARY_SEQ=str(labels['seq']))
    if png:
        env['NMI_BOUNDARY_PNG'] = str(png)
    subprocess.run([str(binary), '--home', str(work / 'home'), '--timeout', '300', str(rom),
                    str(HERE / 'nmi_boundary.lua')], env=env, check=True, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)
    table = {0: [], 1: []}
    for line in out.read_text().splitlines()[1:]:
        field, test, offset, word = line.split('\t')
        table[int(field)].append((int(offset), int(word, 16)))
    return image, table


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--binary', type=Path, required=True)
    p.add_argument('--expect', action='store_true', help="fail unless the table is MesenCE's")
    p.add_argument('--png', type=Path, help='keep the screen of the results')
    p.add_argument('--rom', type=Path, help='keep the ROM')
    a = p.parse_args()
    with tempfile.TemporaryDirectory(prefix='nmi-boundary-') as temporary:
        image, table = run(a.binary.resolve(), Path(temporary), a.png.resolve() if a.png else None)
    if a.rom:
        a.rom.write_bytes(image)
    failed = False
    for field, rows in table.items():
        if len(rows) != nmi_boundary_rom.TESTS:
            raise SystemExit(f'field {field}: {len(rows)} tests')
        where = ''.join(symbol(offset) for offset, _ in rows)
        kept = ''.join('1' if word & 8 else '0' for _, word in rows)
        print(f'field {field} taken {where}')
        print(f'field {field} bit 3 {kept}')
        for test, (offset, word) in enumerate(rows):
            if (offset in (4, 7)) == bool(word & 8):
                print(f'field {field} test {test}: taken at {offset} but the word is ${word:04X}')
                failed = True
        if not {'2', '4', '7', '9'} <= set(where):
            print(f'field {field}: the tests do not cover the sequence')
            failed = True
        if a.expect and where != MESENCE[field]:
            print(f'field {field} differs from MesenCE:\n              {MESENCE[field]}')
            failed = True
    raise SystemExit(1 if failed else 0)


if __name__ == '__main__':
    main()
