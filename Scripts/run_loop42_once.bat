@echo off
set NETFXSDKDir=C:\Program Files (x86)\Windows Kits\NETFXSDK\4.8.1\
if exist D:\Skyguard52\Saved\Logs\skyguard-aaa-loop42.log del /f /q D:\Skyguard52\Saved\Logs\skyguard-aaa-loop42.log
"D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" "D:\Skyguard52\Skyguard52.uproject" /Game/Skyguard/Maps/Lvl_SkyguardCoast -ExecutePythonScript=D:\Skyguard52\Scripts\build_skyguard_aaa_loop42_behind_wall_prop_capture.py -unattended -nop4 -nosplash -log -ABSLOG=D:\Skyguard52\Saved\Logs\skyguard-aaa-loop42.log
echo EDITOR_EXIT=%ERRORLEVEL%> D:\Skyguard52\Saved\Logs\loop42_editor_exit.txt
