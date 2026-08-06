from pathlib import Path
import time, subprocess

def wait(pid_file, log_file, tag):
    pid=int(Path(pid_file).read_text().strip())
    log=Path(log_file)
    for i in range(30):
        alive=subprocess.run(['powershell','-NoProfile','-Command',f"if(Get-Process -Id {pid} -ErrorAction SilentlyContinue){{'1'}}else{{'0'}}"],capture_output=True,text=True).stdout.strip()
        print(tag,i,alive, log.stat().st_size if log.exists() else 0)
        if log.exists():
            hits=[ln for ln in log.read_text(encoding='utf-8',errors='replace').splitlines() if 'SkyguardAAA' in ln or 'Fatal error' in ln]
            for h in hits[-4:]: print(' ', h[:200])
        if alive=='0':
            return
        time.sleep(3)

wait(r'D:\Skyguard52\Saved\Logs\aaa-cine3.pid', r'D:\Skyguard52\Saved\Logs\skyguard-aaa-cine3.log', 'cine')
wait(r'D:\Skyguard52\Saved\Logs\aaa-combatmock2.pid', r'D:\Skyguard52\Saved\Logs\skyguard-aaa-combatmock2.log', 'combat')
print('map', Path(r'D:\Skyguard52\Content\Skyguard\Maps\Lvl_SkyguardCoast.umap').stat().st_size)
print('netfx', Path(r'C:\Program Files (x86)\Microsoft SDKs\NETFXSDK').exists(), Path(r'C:\Program Files (x86)\Reference Assemblies\Microsoft\Framework\.NETFramework\v4.8').exists())
