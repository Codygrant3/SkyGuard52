param()
$ErrorActionPreference = 'Continue'
$UE = 'D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$UBT = 'D:\UE_5.8\Engine\Build\BatchFiles\Build.bat'
$Proj = 'D:\Skyguard52\Skyguard52.uproject'
$LogDir = 'D:\Skyguard52\Saved\Logs'
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

# Ensure no interactive editor is locking packages
Get-Process | Where-Object { $_.ProcessName -match 'UnrealEditor' } | ForEach-Object {
  Write-Host ("Stopping " + $_.ProcessName + " pid=" + $_.Id)
  Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
}
Start-Sleep -Seconds 2

Write-Host 'Building editor module...'
$buildLog = Join-Path $LogDir 'skyguard-build-loop13.log'
& $UBT Skyguard52Editor Win64 Development -Project="$Proj" -WaitMutex -FromMsBuild 2>&1 | Tee-Object -FilePath $buildLog
Write-Host 'Build finished'

function Invoke-UEPy([string]$script, [string]$logName) {
  $log = Join-Path $LogDir $logName
  if (Test-Path $log) { Remove-Item $log -Force -ErrorAction SilentlyContinue }
  $ueArgs = @(
    $Proj,
    '/Game/Skyguard/Maps/Lvl_SkyguardCoast',
    ('-ExecutePythonScript=' + $script),
    '-unattended', '-nop4', '-nosplash', '-NullRHI', '-log',
    ('-ABSLOG=' + $log)
  )
  Write-Host ('Launching ' + $script)
  $p = Start-Process -FilePath $UE -ArgumentList $ueArgs -PassThru -WindowStyle Hidden
  $deadline = (Get-Date).AddMinutes(30)
  while (-not $p.HasExited -and (Get-Date) -lt $deadline) { Start-Sleep -Seconds 5 }
  if (-not $p.HasExited) {
    Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
    Write-Host ('Timeout ' + $script)
  }
  Write-Host ('ExitCode=' + $p.ExitCode + ' log=' + $log)
  if (Test-Path $log) {
    Select-String -Path $log -Pattern 'SkyguardAAA|Error|Exception|CRITIC|Loop13|Succeeded|Failed' |
      Select-Object -Last 80 | ForEach-Object { $_.Line }
  }
}

Invoke-UEPy 'D:\Skyguard52\Scripts\build_skyguard_aaa_loop13_yak_vfx.py' 'skyguard-aaa-loop13-yak-vfx.log'
Write-Host 'loop13 editor pass finished'
