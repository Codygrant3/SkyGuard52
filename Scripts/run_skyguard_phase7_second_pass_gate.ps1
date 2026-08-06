[CmdletBinding()]
param(
    [string]$ProjectRoot = "D:\Skyguard52",
    [string]$UnrealRoot = "D:\UE_5.8",
    [ValidateRange(60, 3600)]
    [int]$BuildTimeoutSeconds = 900,
    [ValidateRange(60, 3600)]
    [int]$AutomationTimeoutSeconds = 1200,
    [switch]$SkipBuild,
    [switch]$ValidateOnly
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$project = Join-Path $ProjectRoot "Skyguard52.uproject"
$buildTool = Join-Path $UnrealRoot "Engine\Build\BatchFiles\Build.bat"
$editorCmd = Join-Path $UnrealRoot "Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
$verifier = Join-Path $ProjectRoot "Scripts\verify_skyguard_phase7_second_pass_gate.py"
$attemptsRoot = Join-Path $ProjectRoot "Saved\BuildAttempts\PHASE7_SECOND_PASS"
$reportsRoot = Join-Path $ProjectRoot "Saved\Reports"
$latestReport = Join-Path $reportsRoot "PHASE7_SECOND_PASS_GATE_LATEST.json"
$expectedFamilies = [ordered]@{
    "Skyguard52.Mission01Integration" = 2
    "Skyguard52.Mission02" = 4
    "Skyguard52.Mission03" = 4
    "Skyguard52.Mission04" = 4
    "Skyguard52.Mission05" = 4
    "Skyguard52.Mission06" = 4
    "Skyguard52.Mission07" = 4
    "Skyguard52.Mission08" = 4
    "Skyguard52.Mission09" = 5
    "Skyguard52.Mission10" = 4
}

function Save-Json {
    param(
        [Parameter(Mandatory = $true)]$Value,
        [Parameter(Mandatory = $true)][string]$LiteralPath
    )
    $Value | ConvertTo-Json -Depth 12 |
        Set-Content -LiteralPath $LiteralPath -Encoding UTF8
}

function Quote-Argument {
    param([Parameter(Mandatory = $true)][string]$Value)
    if ($Value -notmatch '[\s"]') { return $Value }
    return '"' + ($Value -replace '(\\*)"', '$1$1\"' -replace '(\\+)$', '$1$1') + '"'
}

function Invoke-BoundedProcess {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$FilePath,
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [Parameter(Mandatory = $true)][string]$StdoutPath,
        [Parameter(Mandatory = $true)][string]$StderrPath,
        [Parameter(Mandatory = $true)][int]$TimeoutSeconds
    )
    $startedAt = [DateTime]::UtcNow
    $argumentString = ($Arguments | ForEach-Object { Quote-Argument $_ }) -join " "
    $process = Start-Process -FilePath $FilePath `
        -ArgumentList $argumentString `
        -WorkingDirectory $ProjectRoot `
        -RedirectStandardOutput $StdoutPath `
        -RedirectStandardError $StderrPath `
        -PassThru -WindowStyle Hidden
    $timedOut = -not $process.WaitForExit($TimeoutSeconds * 1000)
    if ($timedOut) {
        & taskkill.exe /PID $process.Id /T /F | Out-Null
        $process.WaitForExit()
    }
    else {
        $process.WaitForExit()
    }
    $process.Refresh()
    $exitCode = $null
    if (-not $timedOut -and $process.HasExited) {
        try { $exitCode = [int]$process.ExitCode } catch { $exitCode = $null }
    }
    return [ordered]@{
        name = $Name
        file_path = $FilePath
        arguments = $Arguments
        pid = $process.Id
        started_at_utc = $startedAt.ToString("o")
        finished_at_utc = [DateTime]::UtcNow.ToString("o")
        timed_out = $timedOut
        timeout_seconds = $TimeoutSeconds
        exit_code = $exitCode
        stdout = $StdoutPath
        stderr = $StderrPath
    }
}

foreach ($required in @($project, $buildTool, $editorCmd, $verifier)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
        throw "Required Phase 7 second-pass file is missing: $required"
    }
}

$stamp = [DateTime]::UtcNow.ToString("yyyyMMddTHHmmssfffZ")
$attempt = Join-Path $attemptsRoot ("attempt_" + $stamp)
$logs = Join-Path $attempt "logs"
$reportExport = Join-Path $attempt "automation-report"
$manifestPath = Join-Path $attempt "run_manifest.json"
$gatePath = Join-Path $attempt "gate_report.json"
New-Item -ItemType Directory -Path $logs, $reportExport, $reportsRoot -Force |
    Out-Null

$manifest = [ordered]@{
    schema = "skyguard.phase7.second-pass-run.v1"
    attempt_id = Split-Path $attempt -Leaf
    created_at_utc = [DateTime]::UtcNow.ToString("o")
    project_root = $ProjectRoot
    project = $project
    unreal_root = $UnrealRoot
    expected_families = $expectedFamilies
    expected_test_count = 39
    controls = [ordered]@{
        skip_build = [bool]$SkipBuild
        validate_only = [bool]$ValidateOnly
        build_timeout_seconds = $BuildTimeoutSeconds
        automation_timeout_seconds = $AutomationTimeoutSeconds
        null_rhi = $true
    }
    stages = @()
    automation_report = Join-Path $reportExport "index.json"
    automation_stdout = Join-Path $logs "automation.stdout.log"
    automation_stderr = Join-Path $logs "automation.stderr.log"
    gate_report = $gatePath
    latest_gate_report = $latestReport
    terminal_state = "CREATED"
}
Save-Json -Value $manifest -LiteralPath $manifestPath

$busy = @(
    Get-Process -ErrorAction SilentlyContinue |
        Where-Object {
            $_.ProcessName -match
                '^(UnrealEditor|UnrealEditor-Cmd|ShaderCompileWorker|Skyguard52|UnrealBuildTool|AutomationTool|blender)$'
        }
)
if ($busy.Count -gt 0) {
    $manifest.terminal_state = "BLOCKED_ACTIVE_HEAVYWEIGHT_PROCESS"
    $manifest.active_processes = @(
        $busy | Select-Object ProcessName, Id, Responding
    )
    Save-Json -Value $manifest -LiteralPath $manifestPath
    & py -3 $verifier --manifest $manifestPath --output $gatePath `
        --latest-output $latestReport
    exit 2
}

if ($ValidateOnly) {
    $manifest.terminal_state = "VALIDATED_NOT_EXECUTED"
    Save-Json -Value $manifest -LiteralPath $manifestPath
    [ordered]@{
        schema = "skyguard.phase7.second-pass-preflight.v1"
        status = "READY_TO_RUN"
        attempt = $attempt
        expected_test_count = 39
        expected_families = $expectedFamilies
    } | ConvertTo-Json -Depth 8
    exit 0
}

if (-not $SkipBuild) {
    $buildStdout = Join-Path $logs "build.stdout.log"
    $buildStderr = Join-Path $logs "build.stderr.log"
    $buildCommand = "$buildTool Skyguard52Editor Win64 Development -Project=$project -WaitMutex -NoHotReloadFromIDE"
    $buildStage = Invoke-BoundedProcess `
        -Name "build_editor" `
        -FilePath $env:ComSpec `
        -Arguments @("/d", "/s", "/c", $buildCommand) `
        -StdoutPath $buildStdout `
        -StderrPath $buildStderr `
        -TimeoutSeconds $BuildTimeoutSeconds
    $manifest.stages += $buildStage
    Save-Json -Value $manifest -LiteralPath $manifestPath
    if ($buildStage.timed_out -or $buildStage.exit_code -ne 0) {
        $manifest.terminal_state = "BUILD_FAILED"
        Save-Json -Value $manifest -LiteralPath $manifestPath
        & py -3 $verifier --manifest $manifestPath --output $gatePath `
            --latest-output $latestReport
        exit 1
    }
}

$automationCommands = "Automation RunTests Skyguard52.Mission"
$automationStage = Invoke-BoundedProcess `
    -Name "mission_01_10_second_pass" `
    -FilePath $editorCmd `
    -Arguments @(
        $project,
        "-ExecCmds=$automationCommands",
        "-TestExit=Automation Test Queue Empty",
        "-unattended",
        "-nop4",
        "-nosplash",
        "-NullRHI",
        "-stdout",
        "-FullStdOutLogOutput",
        "-NoAssetRegistryCache",
        "-ReportExportPath=$reportExport"
    ) `
    -StdoutPath $manifest.automation_stdout `
    -StderrPath $manifest.automation_stderr `
    -TimeoutSeconds $AutomationTimeoutSeconds
$manifest.stages += $automationStage
$manifest.terminal_state = if ($automationStage.timed_out) {
    "AUTOMATION_TIMEOUT"
} elseif ($automationStage.exit_code -ne 0) {
    "AUTOMATION_FAILED"
} else {
    "EXECUTION_COMPLETE"
}
Save-Json -Value $manifest -LiteralPath $manifestPath

& py -3 $verifier --manifest $manifestPath --output $gatePath `
    --latest-output $latestReport
exit $LASTEXITCODE
