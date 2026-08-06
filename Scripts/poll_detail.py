from pathlib import Path
import time, subprocess
log=Path(r'D:\Skyguard52\Saved\Logs\skyguard-aaa-detail.log')
pid=int(Path(r'D:\Skyguard52\Saved\Logs\aaa-detail.pid').read_text().strip())
for i in range(25):
    alive=subprocess.run(['powershell','-NoProfile','-Command',f"if(Get-Process -Id {pid} -ErrorAction SilentlyContinue){{'1'}}else{{'0'}}"],capture_output=True,text=True).stdout.strip()
    print('t',i,'alive',alive,'size',log.stat().st_size if log.exists() else 0)
    if log.exists():
        hits=[ln for ln in log.read_text(encoding='utf-8',errors='replace').splitlines() if 'SkyguardAAA' in ln or 'Fatal error' in ln]
        for h in hits[-8:]: print(h[:220])
    if alive=='0': break
    time.sleep(3)
print('map', Path(r'D:\Skyguard52\Content\Skyguard\Maps\Lvl_SkyguardCoast.umap').stat().st_size)
# netfx
for p in [r'C:\Program Files (x86)\Microsoft SDKs\Windows\v10.0A', r'C:\Program Files (x86)\Microsoft SDKs\NETFXSDK']:
    print('netfx', Path(p).exists(), p)
