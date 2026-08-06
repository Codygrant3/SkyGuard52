from pathlib import Path
p = Path(r"D:\Skyguard52\Saved\Logs\run_loop69_once.bat")
p.write_text(
"""@echo off
set UE=D:\\UE_5.8\\Engine\\Binaries\\Win64\\UnrealEditor-Cmd.exe
set PROJ=D:\\Skyguard52\\Skyguard52.uproject
set PY=D:\\Skyguard52\\Scripts\\build_skyguard_aaa_loop69_true_art_slice12_capture.py
set LOG=D:\\Skyguard52\\Saved\\Logs\\skyguard-aaa-loop69.log
echo start %date% %time% > %LOG%
\"%UE%\" \"%PROJ%\" -unattended -nop4 -nosplash -stdout -FullStdOutLogOutput -ExecutePythonScript=\"%PY%\" >> %LOG% 2>&1
echo exit=%ERRORLEVEL% >> %LOG%
""",
encoding="ascii",
)
print("bat_ok", p.exists(), p.stat().st_size)
