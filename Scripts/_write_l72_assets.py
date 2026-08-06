from pathlib import Path
Path(r"D:\Skyguard52\Docs\AAA_Review\true_art_track\SLICE15_PLAN.md").write_text(
"""# True-Art Slice15 - L72 (on L71 freeze)
Updated: 2026-08-01
Goal: formal Niagara shell/emitter author pass + denser capture-safe VFX language; no FOV point lights.

## Hard rules
1. No extra PointLight FOV stacks (L66 reject)
2. Keep L52 HF densify core in FOV
3. Behind-wall hero content only
4. Single small bounded Niagara + emissive cards/cores
5. Host 11/11 absolute else REJECT to L71

## Content
- ensure_slice15_vfx_library() creates/loads NS shells + NS_L72_*Auth variants + emitter shells when API allows
- denser prop concentric discs/blades/streaks
- combat emissive cards + cores/filaments/shells/debris
- city windows + ocean foam cards
- note: empty Niagara shells alone are not AAA; denser authored mesh VFX language is the capture-visible progress
""",
encoding="utf-8",
)
Path(r"D:\Skyguard52\Saved\Logs\run_loop72_once.bat").write_text(
"""@echo off
set UE=D:\\UE_5.8\\Engine\\Binaries\\Win64\\UnrealEditor-Cmd.exe
set PROJ=D:\\Skyguard52\\Skyguard52.uproject
set PY=D:\\Skyguard52\\Scripts\\build_skyguard_aaa_loop72_true_art_slice15_capture.py
set LOG=D:\\Skyguard52\\Saved\\Logs\\skyguard-aaa-loop72.log
echo start %date% %time% > %LOG%
\"%UE%\" \"%PROJ%\" -unattended -nop4 -nosplash -stdout -FullStdOutLogOutput -ExecutePythonScript=\"%PY%\" >> %LOG% 2>&1
echo exit=%ERRORLEVEL% >> %LOG%
""",
encoding="ascii",
)
print("assets_ok")
