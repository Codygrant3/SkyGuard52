param()
$ErrorActionPreference = 'Continue'
$UE = 'D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$Proj = 'D:\Skyguard52\Skyguard52.uproject'
$LogDir = 'D:\Skyguard52\Saved\Logs'
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
function Invoke-UEPy([string]$script, [string]$logName) {
  $log = Join-Path $LogDir $logName
  if (Test-Path $log) { Remove-Item $log -Force -ErrorAction SilentlyContinue }
  $ueArgs = @($Proj, '/Game/Skyguard/Maps/Lvl_SkyguardCoast', ('-ExecutePythonScript=' + $script), '-unattended', '-nop4', '-nosplash', '-NullRHI', '-log', ('-ABSLOG=' + $log))
  Write-Host ('Launching ' + $script)
  $p = Start-Process -FilePath $UE -ArgumentList $ueArgs -PassThru -WindowStyle Hidden
  $deadline = (Get-Date).AddMinutes(20)
  while (-not $p.HasExited -and (Get-Date) -lt $deadline) { Start-Sleep -Seconds 5 }
  if (-not $p.HasExited) { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue; Write-Host ('Timeout ' + $script) }
  Write-Host ('ExitCode=' + $p.ExitCode + ' log=' + $log)
  if (Test-Path $log) { Select-String -Path $log -Pattern 'SkyguardAAA|Error saving|Exception|CRITIC|module' | Select-Object -Last 100 | ForEach-Object { $_.Line } }
}
Invoke-UEPy 'D:\Skyguard52\Scripts\build_skyguard_aaa_loop9_world.py' 'skyguard-aaa-loop9-world.log'
Invoke-UEPy 'D:\Skyguard52\Scripts\build_skyguard_aaa_loop9_vfx.py' 'skyguard-aaa-loop9-vfx.log'
Invoke-UEPy 'D:\Skyguard52\Scripts\build_skyguard_aaa_loop9_cinematic.py' 'skyguard-aaa-loop9-cine.log'
Write-Host 'loop9 editor passes finished'
