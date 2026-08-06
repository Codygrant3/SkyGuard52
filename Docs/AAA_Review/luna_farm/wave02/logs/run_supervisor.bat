@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "D:\Skyguard52\Docs\AAA_Review\luna_farm\run_luna_wave02.ps1" -WaveId "wave02" > "D:\Skyguard52\Docs\AAA_Review\luna_farm\wave02\logs\supervisor.log" 2>&1
echo EXIT=%ERRORLEVEL%> "D:\Skyguard52\Docs\AAA_Review\luna_farm\wave02\logs\supervisor.exit.txt"
