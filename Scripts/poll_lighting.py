from pathlib import Path
import time, subprocess
log=Path(r'D:\Skyguard52\Saved\Logs\skyguard-aaa-lighting.log')
pid=int(Path(r'D:\Skyguard52\Saved\Logs\aaa-lighting.pid').read_text().strip())
print('pid',pid)
for i in range(40):
    alive=subprocess.run(['powershell','-NoProfile','-Command',f"if(Get-Process -Id {pid} -ErrorAction SilentlyContinue){{'1'}}else{{'0'}}"],capture_output=True,text=True).stdout.strip()
    size=log.stat().st_size if log.exists() else 0
    print('tick',i,'alive',alive,'size',size)
    if log.exists():
        hits=[ln for ln in log.read_text(encoding='utf-8',errors='replace').splitlines() if 'SkyguardAAA' in ln or 'Fatal error' in ln][-6:]
        for h in hits: print(h[:220])
    if alive=='0':
        break
    time.sleep(4)
if log.exists():
    print('TAIL')
    print('\n'.join(log.read_text(encoding='utf-8',errors='replace').splitlines()[-15:]))
print('map', Path(r'D:\Skyguard52\Content\Skyguard\Maps\Lvl_SkyguardCoast.umap').stat().st_size)
