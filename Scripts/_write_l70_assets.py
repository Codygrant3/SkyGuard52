from pathlib import Path
Path(r"D:\Skyguard52\Docs\AAA_Review\true_art_track\SLICE13_PLAN.md").write_text(
"""# True-Art Slice13 - L70 (on L69 freeze)
Updated: 2026-08-01
Goal: VFX core language + stronger airframe/city material response; no FOV point lights.

## Hard rules
1. No extra PointLight FOV stacks (L66 reject)
2. Keep L52 HF densify core in FOV
3. Behind-wall hero content only (x >= bx+3)
4. Single small bounded Niagara + readable mesh VFX cores
5. Host 11/11 absolute else REJECT to L69

## Content
- Airframe response mats M_L70_*Resp (fallback L68 ANR)
- Prop disc/blades + yak multi-slot + exhaust pin
- Combat/ADS: rifle multi-slot + muzzle/smoke/sparks + cores/filaments/shells
- City/ocean: brick/concrete response + windows + foam + bounded spray
""",
encoding="utf-8",
)
Path(r"D:\Skyguard52\Saved\Logs\run_loop70_once.bat").write_text(
"""@echo off
set UE=D:\\UE_5.8\\Engine\\Binaries\\Win64\\UnrealEditor-Cmd.exe
set PROJ=D:\\Skyguard52\\Skyguard52.uproject
set PY=D:\\Skyguard52\\Scripts\\build_skyguard_aaa_loop70_true_art_slice13_capture.py
set LOG=D:\\Skyguard52\\Saved\\Logs\\skyguard-aaa-loop70.log
echo start %date% %time% > %LOG%
\"%UE%\" \"%PROJ%\" -unattended -nop4 -nosplash -stdout -FullStdOutLogOutput -ExecutePythonScript=\"%PY%\" >> %LOG% 2>&1
echo exit=%ERRORLEVEL% >> %LOG%
""",
encoding="ascii",
)
print("plan+bat ok")
