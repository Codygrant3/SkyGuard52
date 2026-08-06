$ErrorActionPreference = "Stop"

$ProjectRoot = "D:\Skyguard52"
$ProjectFile = Join-Path $ProjectRoot "Skyguard52.uproject"
$UnrealRoot = "D:\UE_5.8"
$BuildTool = Join-Path $UnrealRoot "Engine\Build\BatchFiles\Build.bat"
$UnrealCmd = Join-Path $UnrealRoot "Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
$BuildScript = Join-Path $ProjectRoot "Scripts\build_skyguard_m01_environment_runtime_v1.py"
$AuditScript = Join-Path $ProjectRoot "Scripts\verify_skyguard_m01_environment_runtime_v1.py"
$LogDirectory = Join-Path $ProjectRoot "Saved\Logs"

$OpenEditors = @(Get-Process UnrealEditor -ErrorAction SilentlyContinue)
if ($OpenEditors.Count -gt 0) {
    Write-Error "READY_TO_RUN: close the visible UnrealEditor before building or saving the isolated environment map. No process was terminated."
    exit 2
}

New-Item -ItemType Directory -Force -Path $LogDirectory | Out-Null

& $BuildTool Skyguard52Editor Win64 Development "-Project=$ProjectFile" -WaitMutex -NoHotReloadFromIDE
if ($LASTEXITCODE -ne 0) {
    throw "Skyguard52Editor build failed with exit code $LASTEXITCODE"
}

& $UnrealCmd $ProjectFile "-ExecutePythonScript=$BuildScript" -unattended -nop4 -nosplash -NullRHI "-abslog=$(Join-Path $LogDirectory 'M01EnvironmentBuild.log')"
if ($LASTEXITCODE -ne 0) {
    throw "Mission 1 environment map build failed with exit code $LASTEXITCODE"
}

& $UnrealCmd $ProjectFile "-ExecutePythonScript=$AuditScript" -unattended -nop4 -nosplash -NullRHI "-abslog=$(Join-Path $LogDirectory 'M01EnvironmentAudit.log')"
if ($LASTEXITCODE -ne 0) {
    throw "Mission 1 environment persistence audit failed with exit code $LASTEXITCODE"
}

& $UnrealCmd $ProjectFile "-ExecCmds=Automation RunTests Skyguard52.Environment.Mission01; Automation RunTests Skyguard52.Boss.Pathfinder" "-TestExit=Automation Test Queue Empty" -unattended -nop4 -nosplash -NullRHI "-abslog=$(Join-Path $LogDirectory 'M01EnvironmentAndPathfinderAutomation.log')"
if ($LASTEXITCODE -ne 0) {
    throw "Mission 1 environment/Pathfinder automation failed with exit code $LASTEXITCODE"
}

Write-Output "PASS: Mission 1 environment runtime v1 build, round-trip audit, and native automation completed."
