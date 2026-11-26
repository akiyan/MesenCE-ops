-- Probe for the lost wake-up described in README.md (run with mesen-headless ROM probe.lua).
-- PROBE_SRAM: an 8 KiB save RAM image of the title that resumes shortly before the scene.
-- PROBE_OUT: the log (TSV). PROBE_DELAY: frames from each input wait to its button press (60).
-- The addresses are the title's: $00:ADC0 input wait, $00:B415 "palette override, red" command,
-- $00:B0D9 background command, $00:8215 the scheduler's read of the signal word, $00:80DA NMI.
-- Lines: pal_red FRAME; lda8215 +n line hClock (the read, in the scenario's coroutine); nmi +n ...
-- (the NMI taken while that coroutine waits for signal 8); bgtrans FRAME +n picture (the scenario
-- went on). No bgtrans line after pal_red: the wake-up was lost.
local out=assert(os.getenv('PROBE_OUT'))
local f=assert(io.open(os.getenv('PROBE_SRAM'),'rb'));local image=f:read('*a');f:close()
for i=1,#image do emu.write(i-1,string.byte(image,i),emu.memType.snesSaveRam) end
local log=assert(io.open(out,'wb'))
local frame,t0=0,nil
local presses={{1501,'a'},{1801,'a'},{2101,'a'},{2401,'a'}}
emu.addMemoryCallback(function() presses[#presses+1]={frame+tonumber(os.getenv('PROBE_DELAY') or '60'),'a'} end,emu.callbackType.exec,0xADC0,0xADC0,emu.cpuType.snes,emu.memType.snesMemory)
emu.addMemoryCallback(function()
 if not t0 and emu.read16(0x15D6,emu.memType.snesWorkRam,false)==31 then t0=frame;log:write('pal_red\t'..frame..'\n');log:flush() end
end,emu.callbackType.exec,0xB415,0xB415,emu.cpuType.snes,emu.memType.snesMemory)
emu.addMemoryCallback(function()
 if t0 then log:write(string.format('bgtrans\t%d\t+%d\tpicture=%d\n',frame,frame-t0,emu.read16(0x15D8,emu.memType.snesWorkRam,false)));log:flush() end
end,emu.callbackType.exec,0xB0D9,0xB0D9,emu.cpuType.snes,emu.memType.snesMemory)
emu.addMemoryCallback(function()
 if not t0 or frame-t0>12 then return end
 if emu.read16(0x0300,emu.memType.snesWorkRam,false)~=8 or emu.read16(0x032A,emu.memType.snesWorkRam,false)~=8 then return end
 local st=emu.getState()
 log:write(string.format('nmi\t+%d\tline=%s\thClock=%s\tactive=%04X\tfield=%s\n',frame-t0,tostring(st['ppu.scanline']),tostring(st['memoryManager.hClock']),emu.read16(0x033A,emu.memType.snesWorkRam,false)));log:flush()
end,emu.callbackType.exec,0x80DA,0x80DA,emu.cpuType.snes,emu.memType.snesMemory)
emu.addMemoryCallback(function()
 if not t0 or frame-t0>12 or emu.read16(0x0300,emu.memType.snesWorkRam,false)~=8 then return end
 local st=emu.getState()
 log:write(string.format('lda8215\t+%d\tline=%s\thClock=%s\n',frame-t0,tostring(st['ppu.scanline']),tostring(st['memoryManager.hClock'])));log:flush()
end,emu.callbackType.exec,0x8215,0x8215,emu.cpuType.snes,emu.memType.snesMemory)
emu.addEventCallback(function()
 local input={a=false,b=false,x=false,y=false,l=false,r=false,start=false,select=false,up=false,down=false,left=false,right=false}
 for _,p in ipairs(presses) do if frame+1>=p[1] and frame+1<p[1]+3 then input[p[2]]=true end end
 emu.setInput(input,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if (t0 and frame-t0>=3600) or frame>20000 then log:write('end\t'..frame..'\n');log:close();emu.stop(0) end
end,emu.eventType.endFrame)
