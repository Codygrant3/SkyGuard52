from pathlib import Path
import subprocess, time
# water
log=Path(r'D:\Skyguard52\Saved\Logs\skyguard-aaa-water.log')
pid=Path(r'D:\Skyguard52\Saved\Logs\aaa-water.pid')
print('water_pid', pid.read_text().strip() if pid.exists() else None)
for i in range(20):
    alive=subprocess.run(['powershell','-NoProfile','-Command', "if(Get-Process -Id %s -ErrorAction SilentlyContinue){'1'}else{'0'}" % (pid.read_text().strip() if pid.exists() else 0)], capture_output=True, text=True).stdout.strip()
    print('t',i,'alive',alive,'size', log.stat().st_size if log.exists() else 0)
    if log.exists():
        hits=[ln for ln in log.read_text(encoding='utf-8',errors='replace').splitlines() if 'SkyguardAAA' in ln or 'Fatal' in ln][-5:]
        for h in hits: print(h[:200])
    if alive=='0':
        break
    time.sleep(3)
# netfx
for p in [r'C:\Program Files (x86)\Microsoft SDKs\Windows\v10.0A', r'C:\Program Files (x86)\Microsoft SDKs\NETFXSDK']:
    print('netfx', p, Path(p).exists())
# vs process
print('vs', subprocess.run(['powershell','-NoProfile','-Command',"Get-Process setup,vs_installer,vs_setup_bootstrapper -EA 0 | Select Id,ProcessName | Out-String"],capture_output=True,text=True).stdout)
