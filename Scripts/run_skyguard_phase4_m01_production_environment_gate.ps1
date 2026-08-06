param(
    [string]$UnrealRoot = "D:\UE_5.8",
    [int]$TimeoutSeconds = 900
)

$ErrorActionPreference = "Stop"
$Project = "D:\Skyguard52\Skyguard52.uproject"
$Root = "D:\Skyguard52"
$BuildTool = Join-Path $UnrealRoot "Engine\Build\BatchFiles\Build.bat"
$UnrealCmd = Join-Path $UnrealRoot "Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
$LogRoot = Join-Path $Root "Saved\Logs"
New-Item -ItemType Directory -Path $LogRoot -Force | Out-Null

$active = Get-CimInstance Win32_Process | Where-Object {
    $_.Name -match "^UnrealEditor(-Cmd)?\.exe$" -and
    $_.CommandLine -like "*Skyguard52*"
}
if ($active) {
    throw "Skyguard52 Unreal process already active; wait instead of duplicating it: $($active.ProcessId -join ', ')"
}

function Invoke-SupervisedProcess {
    param(
        [string]$Name,
        [string]$FilePath,
        [string]$Arguments
    )
    $stdout = Join-Path $LogRoot "$Name.stdout.log"
    $stderr = Join-Path $LogRoot "$Name.stderr.log"
    $process = Start-Process `
        -FilePath $FilePath `
        -ArgumentList $Arguments `
        -RedirectStandardOutput $stdout `
        -RedirectStandardError $stderr `
        -PassThru `
        -WindowStyle Hidden
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while (-not $process.HasExited -and (Get-Date) -lt $deadline) {
        Start-Sleep -Seconds 2
        $process.Refresh()
    }
    if (-not $process.HasExited) {
        throw "$Name exceeded $TimeoutSeconds seconds; PID $($process.Id) remains authoritative"
    }
    if ($process.ExitCode -ne 0) {
        throw "$Name failed with exit code $($process.ExitCode); inspect $stdout and $stderr"
    }
    $fatal = (Select-String -Path $stdout -Pattern "Fatal error|Ensure condition failed" -ErrorAction SilentlyContinue).Count
    if ($fatal -gt 0) {
        throw "$Name logged $fatal fatal/ensure markers despite exit code zero"
    }
}

$buildArgs = "/c `"`"$BuildTool`" Skyguard52Editor Win64 Development `"$Project`" -WaitMutex -NoHotReload`""
Invoke-SupervisedProcess "Phase4M01Build" "cmd.exe" $buildArgs

$builder = Join-Path $Root "Scripts\build_skyguard_phase4_m01_production_environment.py"
$buildMapArgs = "`"$Project`" -run=pythonscript -script=`"$builder`" -unattended -nop4 -nosplash -NullRHI -stdout -FullStdOutLogOutput"
Invoke-SupervisedProcess "Phase4M01MapBuild" $UnrealCmd $buildMapArgs

$verifier = Join-Path $Root "Scripts\verify_skyguard_phase4_m01_production_environment.py"
$verifyArgs = "`"$Project`" -run=pythonscript -script=`"$verifier`" -unattended -nop4 -nosplash -NullRHI -stdout -FullStdOutLogOutput"
Invoke-SupervisedProcess "Phase4M01MapAudit" $UnrealCmd $verifyArgs

$testArgs = "`"$Project`" `"-ExecCmds=Automation RunTests Skyguard52.Environment.Mission01Production`" `"-TestExit=Automation Test Queue Empty`" -unattended -nop4 -nosplash -NullRHI -stdout -FullStdOutLogOutput"
Invoke-SupervisedProcess "Phase4M01Automation" $UnrealCmd $testArgs

$testLog = Join-Path $LogRoot "Phase4M01Automation.stdout.log"
$success = (Select-String -Path $testLog -Pattern "Test Completed. Result=\{Success\}").Count
$failure = (Select-String -Path $testLog -Pattern "Test Completed. Result=\{Fail\}").Count
if ($success -ne 2 -or $failure -ne 0) {
    throw "Expected exactly two passing Phase 4 tests; found success=$success failure=$failure"
}

Write-Output "PHASE4_M01_PRODUCTION_ENVIRONMENT_GATE=PASS"

