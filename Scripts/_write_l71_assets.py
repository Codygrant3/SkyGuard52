from pathlib import Path
Path(r"D:\Skyguard52\Docs\AAA_Review\true_art_track\SLICE14_PLAN.md").write_text(
"""# True-Art Slice14 - L71 (on L70 freeze)
Updated: 2026-08-01
Goal: authored VFX look (emissive unlit cores) + prop PBR motion disc; no FOV point lights.

## Hard rules
1. No extra PointLight FOV stacks (L66 reject)
2. Keep L52 HF densify core in FOV
3. Behind-wall hero content only
4. Single small bounded Niagara + readable emissive VFX cores
5. Host 11/11 absolute else REJECT to L70

## Content
- M_L71_PropDiscMotion / PropBlade
- M_L71_VFX_*Emi emissive unlit cores (muzzle/spark/tracer/foam/expl)
- Prop concentric disc rings + multi-blade motion streaks
- Combat/ADS authored cores/filaments/shells/sparks
- City windows + ocean foam emissive accents
""",
encoding="utf-8",
)
Path(r"D:\Skyguard52\Saved\Logs\run_loop71_once.bat").write_text(
"""@echo off
set UE=D:\\UE_5.8\\Engine\\Binaries\\Win64\\UnrealEditor-Cmd.exe
set PROJ=D:\\Skyguard52\\Skyguard52.uproject
set PY=D:\\Skyguard52\\Scripts\\build_skyguard_aaa_loop71_true_art_slice14_capture.py
set LOG=D:\\Skyguard52\\Saved\\Logs\\skyguard-aaa-loop71.log
echo start %date% %time% > %LOG%
\"%UE%\" \"%PROJ%\" -unattended -nop4 -nosplash -stdout -FullStdOutLogOutput -ExecutePythonScript=\"%PY%\" >> %LOG% 2>&1
echo exit=%ERRORLEVEL% >> %LOG%
""",
encoding="ascii",
)
print("assets_ok")
