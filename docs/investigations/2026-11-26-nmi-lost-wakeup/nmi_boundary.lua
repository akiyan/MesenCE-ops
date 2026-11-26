-- Run nmi_boundary_rom.py's ROM to its end and write its table (NMI_BOUNDARY_OUT, TSV):
-- field, test, the NMI's return address minus the sequence's address, the signal word.
-- NMI_BOUNDARY_SEQ: the sequence's address (the generator prints it). NMI_BOUNDARY_PNG: optional screenshot.
local out=assert(os.getenv('NMI_BOUNDARY_OUT'))
local seq=assert(tonumber(os.getenv('NMI_BOUNDARY_SEQ')))
local png=os.getenv('NMI_BOUNDARY_PNG')
local TESTS,RESULTS=96,0x1000
local frames,done=0,nil
emu.addEventCallback(function()
 frames=frames+1
 local ram=emu.memType.snesWorkRam
 if not done and emu.read16(0x1C,ram,false)==1 then done=frames end
 if done and frames==done+3 then
  local f=assert(io.open(out,'wb'))
  f:write('field\ttest\toffset\tword\n')
  for field=0,1 do for test=0,TESTS-1 do
   local at=RESULTS+4*(TESTS*field+test)
   f:write(string.format('%d\t%d\t%d\t%04X\n',field,test,emu.read16(at,ram,false)-seq,emu.read16(at+2,ram,false)))
  end end
  f:close()
  if png then local g=assert(io.open(png,'wb'));g:write(emu.takeScreenshot());g:close() end
  emu.stop(0)
 end
 if frames>3000 then io.stderr:write('the test ROM did not finish\n');emu.stop(41) end
end,emu.eventType.endFrame)
