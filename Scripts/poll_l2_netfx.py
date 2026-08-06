from pathlib import Path
import time, subprocess

def alive(pid):
    r=subprocess.run(['powershell','-NoProfile','-Command',f"if(Get-Process -Id {pid} -ErrorAction SilentlyContinue){{'1'}}else{{'0'}}"],capture_output=True,text=True)
    return (r.stdout or '').strip()

# lighting
log=Path(r'D:\Skyguard52\Saved\Logs\skyguard-aaa-lighting2.log')
pid=int(Path(r'D:\Skyguard52\Saved\Logs\aaa-lighting2.pid').read_text().strip())
print('lighting pid',pid)
for i in range(25):
    a=alive(pid)
    print('L',i,a, log.stat().st_size if log.exists() else 0)
    if log.exists():
        hits=[ln for ln in log.read_text(encoding='utf-8',errors='replace').splitlines() if 'SkyguardAAA' in ln or 'Fatal error' in ln]
        for h in hits[-5:]: print(h[:220])
    if a=='0': break
    time.sleep(3)

# netfx
print('netfx processes:')
print(subprocess.run(['powershell','-NoProfile','-Command',"Get-Process NDP481*,setup,msiexec -EA 0 | Select Id,ProcessName,CPU | Format-Table | Out-String"],capture_output=True,text=True).stdout)
for p in [r'C:\Program Files (x86)\Microsoft SDKs\Windows\v10.0A', r'C:\Program Files (x86)\Microsoft SDKs\NETFXSDK', r'C:\Program Files (x86)\Windows Kits\NETFXSDK', r'C:\Program Files (x86)\Reference Assemblies\Microsoft\Framework\.NETFramework\v4.8']:
    print(Path(p).exists(), p)
print('map', Path(r'D:\Skyguard52\Content\Skyguard\Maps\Lvl_SkyguardCoast.umap').stat().st_size)
