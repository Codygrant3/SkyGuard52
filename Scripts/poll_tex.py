from pathlib import Path
import time, subprocess
log=Path(r'D:\Skyguard52\Saved\Logs\skyguard-aaa-tex.log')
pid=int(Path(r'D:\Skyguard52\Saved\Logs\aaa-tex.pid').read_text().strip())
print('pid',pid)
for i in range(50):
    alive=subprocess.run(['powershell','-NoProfile','-Command',f"if(Get-Process -Id {pid} -ErrorAction SilentlyContinue){{'1'}}else{{'0'}}"],capture_output=True,text=True).stdout.strip()
    print('t',i,'alive',alive,'size',log.stat().st_size if log.exists() else 0)
    if log.exists():
        hits=[ln for ln in log.read_text(encoding='utf-8',errors='replace').splitlines() if 'SkyguardAAA' in ln or 'Fatal error' in ln or 'import failed' in ln]
        for h in hits[-10:]:
            print(h[:240])
    if alive=='0':
        break
    time.sleep(4)
print('DONE')
# asset counts
root=Path(r'D:\Skyguard52\Content\Skyguard')
print('materials', len(list((root/'Materials').glob('*.uasset'))) if (root/'Materials').exists() else 0)
print('imported', len(list((root/'Textures'/'Imported').rglob('*.uasset'))) if (root/'Textures'/'Imported').exists() else 0)
print('map', (root/'Maps'/'Lvl_SkyguardCoast.umap').stat().st_size if (root/'Maps'/'Lvl_SkyguardCoast.umap').exists() else None)
