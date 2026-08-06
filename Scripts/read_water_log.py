from pathlib import Path
log=Path(r'D:\Skyguard52\Saved\Logs\skyguard-aaa-water.log')
t=log.read_text(encoding='utf-8', errors='replace').splitlines() if log.exists() else []
hits=[ln for ln in t if 'SkyguardAAA' in ln or 'Fatal error' in ln or 'Water' in ln]
print('hits', len(hits))
print('\n'.join(hits[-30:]))
print('TAIL')
print('\n'.join(t[-20:]))
print('map', Path(r'D:\Skyguard52\Content\Skyguard\Maps\Lvl_SkyguardCoast.umap').stat().st_size)
