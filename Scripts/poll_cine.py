from pathlib import Path
import time, subprocess
log=Path(r'D:\Skyguard52\Saved\Logs\skyguard-aaa-cine.log')
pid=int(Path(r'D:\Skyguard52\Saved\Logs\aaa-cine.pid').read_text().strip())
for i in range(20):
    alive=subprocess.run(['powershell','-NoProfile','-Command',f"if(Get-Process -Id {pid} -ErrorAction SilentlyContinue){{'1'}}else{{'0'}}"],capture_output=True,text=True).stdout.strip()
    print('t',i,alive)
    if log.exists():
        hits=[ln for ln in log.read_text(encoding='utf-8',errors='replace').splitlines() if 'SkyguardAAA' in ln]
        for h in hits[-5:]: print(h[:220])
    if alive=='0': break
    time.sleep(3)
print('map', Path(r'D:\Skyguard52\Content\Skyguard\Maps\Lvl_SkyguardCoast.umap').stat().st_size)
print('exe', Path(r'D:\Skyguard52\Binaries\Win64\Skyguard52.exe').exists())
