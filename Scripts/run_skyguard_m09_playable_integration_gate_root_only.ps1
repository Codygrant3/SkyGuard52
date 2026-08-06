[CmdletBinding()]
param(
    [switch]$RootAuthorized,
    [string]$ProjectRoot = "D:\Skyguard52",
    [string]$UnrealRoot = "D:\UE_5.8",
    [ValidateRange(60, 1800)][int]$StageTimeoutSeconds = 600
)
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
if (-not $RootAuthorized) {
    throw "Root-only serialized gate. The root supervisor must pass -RootAuthorized."
}
$project = Join-Path $ProjectRoot "Skyguard52.uproject"
$build = Join-Path $UnrealRoot "Engine\Build\BatchFiles\Build.bat"
$cmd = Join-Path $UnrealRoot "Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
$builder = Join-Path $ProjectRoot "Scripts\build_skyguard_m09_playable_integration.py"
$verifier = Join-Path $ProjectRoot "Scripts\verify_skyguard_m09_playable_integration.py"
$sourceAudit = Join-Path $ProjectRoot "Scripts\audit_skyguard_m09_playable_source.py"
$stamp = [DateTime]::UtcNow.ToString("yyyyMMddTHHmmssfffZ")
$attempt = Join-Path $ProjectRoot "Saved\Reports\M09_Playable\attempt_$stamp"
New-Item -ItemType Directory -Force -Path $attempt | Out-Null
foreach ($file in @($project, $build, $cmd, $builder, $verifier, $sourceAudit)) {
    if (-not (Test-Path -LiteralPath $file -PathType Leaf)) {
        throw "Missing: $file"
    }
}
$active = @(Get-CimInstance Win32_Process | Where-Object {
    $_.Name -in @(
        "UnrealEditor.exe", "UnrealEditor-Cmd.exe",
        "UnrealBuildTool.exe", "AutomationTool.exe",
        "ShaderCompileWorker.exe", "UbaAgent.exe", "UbaServer.exe"
    ) -or (
        $_.Name -eq "dotnet.exe" -and
        $_.CommandLine -match "UnrealBuildTool|AutomationTool"
    )
})
if ($active.Count) {
    throw "Shared Unreal lane is active; refusing duplicate launch"
}

function ConvertTo-Argument {
    param([Parameter(Mandatory = $true)][string]$Value)
    if ($Value -notmatch '[\s"]') { return $Value }
    return '"' + (
        $Value -replace '(\\*)"', '$1$1\"' -replace '(\\+)$', '$1$1'
    ) + '"'
}

function Invoke-Stage(
    [string]$Name,
    [string]$File,
    [string[]]$Arguments,
    [string]$SuccessPattern
) {
    $out = Join-Path $attempt "$Name.stdout.log"
    $err = Join-Path $attempt "$Name.stderr.log"
    $argumentLine = (
        $Arguments | ForEach-Object { ConvertTo-Argument $_ }
    ) -join " "
    $process = Start-Process -FilePath $File `
        -ArgumentList $argumentLine `
        -RedirectStandardOutput $out `
        -RedirectStandardError $err `
        -PassThru -WindowStyle Hidden
    [ordered]@{
        stage = $Name
        pid = $process.Id
        started_utc = [DateTime]::UtcNow.ToString("o")
        stdout = $out
        stderr = $err
    } | ConvertTo-Json | Set-Content (
        Join-Path $attempt "$Name.process.json"
    ) -Encoding utf8
    if (-not $process.WaitForExit($StageTimeoutSeconds * 1000)) {
        throw "$Name timed out with authoritative PID $($process.Id); wait, never duplicate"
    }
    $process.WaitForExit()
    $process.Refresh()
    $text = (
        Get-Content $out -Raw -ErrorAction SilentlyContinue
    ) + (
        Get-Content $err -Raw -ErrorAction SilentlyContinue
    )
    $bad = @(
        @(
            "Fatal error", "Assertion failed", "Unhandled Exception",
            "LogPython: Error:", "Traceback (most recent call last)"
        ) | Where-Object { $text -match [regex]::Escape($_) }
    )
    $exitCode = $process.ExitCode
    if ($null -eq $exitCode -and $SuccessPattern -and $text -match $SuccessPattern) {
        $exitCode = 0
    }
    if ($null -eq $exitCode -or $exitCode -ne 0 -or $bad.Count) {
        throw "$Name failed: exit=$exitCode markers=$($bad -join ', ')"
    }
}

Invoke-Stage "source_audit" "python" @($sourceAudit) '"gate": "PASS"'
Invoke-Stage "build" $build @(
    "Skyguard52Editor", "Win64", "Development", $project,
    "-WaitMutex", "-NoHotReloadFromIDE"
) "Result:\s+Succeeded"
Invoke-Stage "compose" $cmd @(
    $project, "-run=pythonscript", "-script=$builder",
    "-unattended", "-nop4", "-nosplash", "-NullRHI",
    "-stdout", "-FullStdOutLogOutput"
) "LogExit:\s+Exiting\."
Invoke-Stage "audit" $cmd @(
    $project, "-run=pythonscript", "-script=$verifier",
    "-unattended", "-nop4", "-nosplash", "-NullRHI",
    "-stdout", "-FullStdOutLogOutput"
) "LogExit:\s+Exiting\."
Invoke-Stage "automation" $cmd @(
    $project, "-ExecCmds=Automation RunTests Skyguard52.Mission09",
    "-TestExit=Automation Test Queue Empty", "-unattended", "-nop4",
    "-nosplash", "-NullRHI", "-stdout", "-FullStdOutLogOutput"
) "Automation Test Queue Empty 4 tests performed"

$log = Get-Content (Join-Path $attempt "automation.stdout.log") -Raw
$required = @(
    "Skyguard52.Mission09.Integration.GovernedContractEscalationAndPoolBounds",
    "Skyguard52.Mission09.IronRain.DispensersClimbCrossAndSecondIgla",
    "Skyguard52.Mission09.IronRain.DifficultRifleFuelControlFinish",
    "Skyguard52.Mission09.Integration.DeterministicSuccessAndInfrastructureFailure"
)
$missing = @($required | Where-Object {
    $log -notmatch (
        "Test Completed\. Result=\{Success\}.*Path=\{" +
        [regex]::Escape($_) + "\}"
    )
})
$success = ([regex]::Matches($log, "Test Completed\. Result=\{Success\}")).Count
$failure = ([regex]::Matches($log, "Test Completed\. Result=\{Fail\}")).Count
$audit = Get-Content (
    Join-Path $ProjectRoot "Saved\Reports\M09_PLAYABLE_INTEGRATION_AUDIT.json"
) -Raw | ConvertFrom-Json
$gate = if (
    $audit.gate -eq "PASS" -and $success -eq 4 -and
    $failure -eq 0 -and $missing.Count -eq 0
) { "PASS" } else { "FAIL" }
$receipt = [ordered]@{
    schema = "skyguard.m09-playable-supervisor.v1"
    gate = $gate
    attempt = $attempt
    root_authorized = $true
    automation = [ordered]@{
        success = $success
        failure = $failure
        required = $required
        missing = $missing
    }
    persistence_audit = $audit
    packaging_performed = $false
    config_modified = $false
    soak_matrix_modified = $false
}
$receipt | ConvertTo-Json -Depth 12 | Set-Content (
    Join-Path $ProjectRoot "Saved\Reports\M09_PLAYABLE_INTEGRATION_GATE_LATEST.json"
) -Encoding utf8
if ($gate -ne "PASS") { throw "M09 playable gate failed" }
Write-Output "M09_PLAYABLE_INTEGRATION_GATE=PASS"
