from pathlib import Path
import time, subprocess
# street
log=Path(r'D:\Skyguard52\Saved\Logs\skyguard-aaa-street.log')
pid=int(Path(r'D:\Skyguard52\Saved\Logs\aaa-street.pid').read_text().strip())
for i in range(20):
    alive=subprocess.run(['powershell','-NoProfile','-Command',f"if(Get-Process -Id {pid} -ErrorAction SilentlyContinue){{'1'}}else{{'0'}}"],capture_output=True,text=True).stdout.strip()
    print('street',i,alive, log.stat().st_size if log.exists() else 0)
    if log.exists():
        hits=[ln for ln in log.read_text(encoding='utf-8',errors='replace').splitlines() if 'SkyguardAAA' in ln]
        for h in hits[-5:]: print(h[:200])
    if alive=='0': break
    time.sleep(3)
# netfx
print('netfx installer alive', subprocess.run(['powershell','-NoProfile','-Command',"if(Get-Process -Id 17300 -ErrorAction SilentlyContinue){'1'}else{'0'}"],capture_output=True,text=True).stdout.strip())
for p in [r'C:\Program Files (x86)\Microsoft SDKs\Windows\v10.0A', r'C:\Program Files (x86)\Microsoft SDKs\NETFXSDK']:
    print(p, Path(p).exists())
print('map', Path(r'D:\Skyguard52\Content\Skyguard\Maps\Lvl_SkyguardCoast.umap').stat().st_size)
