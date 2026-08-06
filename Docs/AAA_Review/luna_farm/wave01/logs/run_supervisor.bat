@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "D:\Skyguard52\Docs\AAA_Review\luna_farm\run_luna_wave01.ps1" > "D:\Skyguard52\Docs\AAA_Review\luna_farm\wave01\logs\supervisor.log" 2>&1
echo EXIT=%ERRORLEVEL%> "D:\Skyguard52\Docs\AAA_Review\luna_farm\wave01\logs\supervisor.exit.txt"
