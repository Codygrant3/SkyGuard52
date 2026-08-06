import time, subprocess
from pathlib import Path
for i in range(60):
    r=subprocess.run(['powershell','-NoProfile','-Command',"if(Get-Process winget -ErrorAction SilentlyContinue){'1'}else{'0'}"],capture_output=True,text=True)
    alive=(r.stdout or '').strip()
    print('tick',i,'winget',alive)
    paths=[
     r'C:\Program Files (x86)\Microsoft SDKs\Windows\v10.0A\bin\NETFX 4.8 Tools',
     r'C:\Program Files (x86)\Microsoft SDKs\NETFXSDK',
     r'C:\Program Files (x86)\Windows Kits\NETFXSDK'
    ]
    for p in paths:
        if Path(p).exists():
            print('EXISTS', p)
    if alive=='0':
        break
    time.sleep(5)
print('done')
for p in paths:
    print(p, Path(p).exists())
