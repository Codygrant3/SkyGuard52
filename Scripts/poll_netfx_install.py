from pathlib import Path
import time, subprocess
# poll netfx installer and anchors
netfx_pid_path=Path(r'D:\Skyguard52\Saved\Logs\netfx-installer.pid')
netfx_pid=int(netfx_pid_path.read_text().strip()) if netfx_pid_path.exists() else None
print('netfx_pid', netfx_pid)
for i in range(30):
    alive='?'
    if netfx_pid:
        alive=subprocess.run(['powershell','-NoProfile','-Command',f"if(Get-Process -Id {netfx_pid} -ErrorAction SilentlyContinue){{'1'}}else{{'0'}}"],capture_output=True,text=True).stdout.strip()
    paths=[
        r'C:\Program Files (x86)\Microsoft SDKs\Windows\v10.0A',
        r'C:\Program Files (x86)\Microsoft SDKs\NETFXSDK',
        r'C:\Program Files (x86)\Windows Kits\NETFXSDK',
        r'C:\Program Files (x86)\Microsoft SDKs\Windows\v10.0A\bin\NETFX 4.8 Tools',
    ]
    found=[p for p in paths if Path(p).exists()]
    print(f't={i} alive={alive} found={len(found)}')
    for f in found: print(' ', f)
    if alive=='0' and i>1:
        break
    if found:
        break
    time.sleep(5)
# anchors log
alog=Path(r'D:\Skyguard52\Saved\Logs\skyguard-play-anchors.log')
if alog.exists():
    hits=[ln for ln in alog.read_text(encoding='utf-8',errors='replace').splitlines() if 'SkyguardAAA' in ln or 'Fatal' in ln]
    print('anchors_hits', hits[-5:])
print('final netfx paths:')
for p in paths:
    print(Path(p).exists(), p)
