from pathlib import Path
import time, subprocess
log=Path(r'D:\Skyguard52\Saved\Logs\place-cpp.log')
pid=int(Path(r'D:\Skyguard52\Saved\Logs\place-cpp.pid').read_text().strip())
for i in range(25):
    alive=subprocess.run(['powershell','-NoProfile','-Command',f"if(Get-Process -Id {pid} -ErrorAction SilentlyContinue){{'1'}}else{{'0'}}"],capture_output=True,text=True).stdout.strip()
    print('place',i,alive)
    if log.exists():
        hits=[ln for ln in log.read_text(encoding='utf-8',errors='replace').splitlines() if 'SkyguardAAA' in ln or 'Fatal' in ln or 'module' in ln.lower() and 'Skyguard' in ln]
        for h in hits[-8:]: print(h[:230])
    if alive=='0': break
    time.sleep(3)
print('game procs:')
print(subprocess.run(['powershell','-NoProfile','-Command',"Get-Process Skyguard52,UnrealEditor -EA 0 | Select Id,ProcessName,CPU,StartTime | Format-Table | Out-String"],capture_output=True,text=True).stdout)
print('exe exists', Path(r'D:\Skyguard52\Binaries\Win64\Skyguard52.exe').exists(), Path(r'D:\Skyguard52\Binaries\Win64\Skyguard52.exe').stat().st_size)
print('map', Path(r'D:\Skyguard52\Content\Skyguard\Maps\Lvl_SkyguardCoast.umap').stat().st_size)
