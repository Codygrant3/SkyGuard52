from pathlib import Path
Path(r"D:\Skyguard52\Docs\AAA_Review\true_art_track\SLICE16_PLAN.md").write_text(
"""# True-Art Slice16 - L73 (on L72 freeze)
Updated: 2026-08-01
Goal: deepen Niagara emitter authoring + denser capture-visible particle language; no FOV point lights.

## Hard rules
1. No extra PointLight FOV stacks (L66 reject)
2. Keep L52 HF densify core in FOV
3. Behind-wall hero content only
4. Bounded Niagara + denser visible particle fields/rings
5. Host 11/11 absolute else REJECT to L72

## Content
- deepen ensure_authored_ns (attach emitter when API allows, fixed bounds/warmup)
- new NS_L73_*Auth variants (MuzzleBurst/SparkRing/ExplPlume/FoamBurst/ContrailDense)
- spawn_particle_field + spawn_burst_ring for still-readable pseudo-particles
- denser prop discs/blades + combat explosion fields
""",
encoding="utf-8",
)
Path(r"D:\Skyguard52\Saved\Logs\run_loop73_once.bat").write_text(
"""@echo off
set UE=D:\\UE_5.8\\Engine\\Binaries\\Win64\\UnrealEditor-Cmd.exe
set PROJ=D:\\Skyguard52\\Skyguard52.uproject
set PY=D:\\Skyguard52\\Scripts\\build_skyguard_aaa_loop73_true_art_slice16_capture.py
set LOG=D:\\Skyguard52\\Saved\\Logs\\skyguard-aaa-loop73.log
echo start %date% %time% > %LOG%
\"%UE%\" \"%PROJ%\" -unattended -nop4 -nosplash -stdout -FullStdOutLogOutput -ExecutePythonScript=\"%PY%\" >> %LOG% 2>&1
echo exit=%ERRORLEVEL% >> %LOG%
""",
encoding="ascii",
)
print("assets_ok")
