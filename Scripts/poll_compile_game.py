from pathlib import Path
import time, subprocess
log=Path(r'D:\Skyguard52\Saved\Logs\compile-game.log')
for i in range(90):
    alive=subprocess.run(['powershell','-NoProfile','-Command',"if(Get-Process dotnet,UnrealBuildTool,MSBuild -ErrorAction SilentlyContinue){'1'}else{'0'}"],capture_output=True,text=True).stdout.strip()
    size=log.stat().st_size if log.exists() else 0
    print(f't={i} build_alive={alive} size={size}')
    if log.exists():
        lines=log.read_text(encoding='utf-8',errors='replace').splitlines()
        # show last compile lines
        for ln in lines[-8:]:
            if ln.strip(): print(ln[:220])
        if any('Result: Succeeded' in ln or 'Result: Failed' in ln for ln in lines[-30:]):
            break
    if alive=='0' and i>2:
        break
    time.sleep(5)
print('FINAL TAIL')
if log.exists():
    print('\n'.join(log.read_text(encoding='utf-8',errors='replace').splitlines()[-40:]))
# binaries
b=Path(r'D:\Skyguard52\Binaries\Win64')
if b.exists():
    for f in sorted(b.glob('*'))[:20]:
        print(f.name, f.stat().st_size)
else:
    print('no binaries dir')
