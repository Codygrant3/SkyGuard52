from pathlib import Path
import time, subprocess
log=Path(r'D:\Skyguard52\Saved\Logs\skyguard-aaa-sil.log')
pid=int(Path(r'D:\Skyguard52\Saved\Logs\aaa-sil.pid').read_text().strip())
for i in range(20):
    alive=subprocess.run(['powershell','-NoProfile','-Command',f"if(Get-Process -Id {pid} -ErrorAction SilentlyContinue){{'1'}}else{{'0'}}"],capture_output=True,text=True).stdout.strip()
    print('t',i,'alive',alive)
    if log.exists():
        hits=[ln for ln in log.read_text(encoding='utf-8',errors='replace').splitlines() if 'SkyguardAAA' in ln or 'Fatal' in ln]
        for h in hits[-6:]: print(h[:220])
    if alive=='0': break
    time.sleep(3)
print('map', Path(r'D:\Skyguard52\Content\Skyguard\Maps\Lvl_SkyguardCoast.umap').stat().st_size)
print('netfx', Path(r'C:\Program Files (x86)\Microsoft SDKs\NETFXSDK').exists(), Path(r'C:\Program Files (x86)\Reference Assemblies\Microsoft\Framework\.NETFramework\v4.8').exists())
