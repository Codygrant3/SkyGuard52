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
  $deadline = (Get-Date).AddMinutes(18)
  while (-not $p.HasExited -and (Get-Date) -lt $deadline) { Start-Sleep -Seconds 5 }
  if (-not $p.HasExited) { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue; Write-Host ('Timeout ' + $script) }
  Write-Host ('ExitCode=' + $p.ExitCode + ' log=' + $log)
  if (Test-Path $log) { Select-String -Path $log -Pattern 'SkyguardAAA|Error saving|Exception|CRITIC' | Select-Object -Last 80 | ForEach-Object { $_.Line } }
}
Invoke-UEPy 'D:\Skyguard52\Scripts\build_skyguard_aaa_loop6_world.py' 'skyguard-aaa-loop6-world.log'
Invoke-UEPy 'D:\Skyguard52\Scripts\build_skyguard_aaa_loop6_combat_bp.py' 'skyguard-aaa-loop6-combat.log'
Invoke-UEPy 'D:\Skyguard52\Scripts\build_skyguard_aaa_loop6_vfx.py' 'skyguard-aaa-loop6-vfx.log'
Write-Host 'loop6 editor passes finished'
