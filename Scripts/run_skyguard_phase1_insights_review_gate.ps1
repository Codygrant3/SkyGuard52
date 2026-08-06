[CmdletBinding()]
param(
    [string]$ProjectRoot = "D:\Skyguard52",
    [string]$PerformanceGateReport = "",
    [string]$UnrealInsightsExe = "D:\UE_5.8\Engine\Binaries\Win64\UnrealInsights.exe",
    [ValidateRange(30, 900)]
    [int]$TimeoutSeconds = 300
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Get-Sha256 {
    param([Parameter(Mandatory = $true)][string]$LiteralPath)
    return (Get-FileHash -Algorithm SHA256 -LiteralPath $LiteralPath).Hash.ToLowerInvariant()
}

function New-Binding {
    param(
        [Parameter(Mandatory = $true)][string]$Label,
        [Parameter(Mandatory = $true)][string]$LiteralPath
    )
    $item = Get-Item -LiteralPath $LiteralPath -ErrorAction Stop
    return [ordered]@{
        label = $Label
        path = $item.FullName
        bytes = [int64]$item.Length
        sha256 = Get-Sha256 -LiteralPath $item.FullName
    }
}

if ([string]::IsNullOrWhiteSpace($PerformanceGateReport)) {
    $PerformanceGateReport = Join-Path $ProjectRoot "Saved\Reports\PHASE1_PERFORMANCE_GATE_LATEST.json"
}
$verifier = Join-Path $ProjectRoot "Scripts\verify_skyguard_phase1_insights_review.py"
$engineContract = "D:\UE_5.8\Engine\Source\Programs\AutomationTool\Scripts\ExportTimerStatisticsFromUtrace.cs"
$engineTests = "D:\UE_5.8\Engine\Source\Developer\TraceInsights\Private\Insights\Tests\FunctionalTests\ExportCommandsTests.cpp"

foreach ($required in @(
    $PerformanceGateReport, $UnrealInsightsExe, $verifier, $engineContract, $engineTests
)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
        throw "Required P1.4 review input is missing: $required"
    }
}

$performance = Get-Content -LiteralPath $PerformanceGateReport -Raw | ConvertFrom-Json
$tracePath = [string]$performance.trace.path
if (-not (Test-Path -LiteralPath $tracePath -PathType Leaf)) {
    throw "Accepted Phase 1 trace is missing: $tracePath"
}

$attemptId = "attempt_" + [DateTime]::UtcNow.ToString("yyyyMMddTHHmmssfffZ")
$attemptRoot = Join-Path $ProjectRoot "Saved\Profiling\Phase1InsightsReview\$attemptId"
$exportRoot = Join-Path $attemptRoot "exports"
New-Item -ItemType Directory -Force -Path $exportRoot | Out-Null

$paths = [ordered]@{
    threads = Join-Path $exportRoot "threads.csv"
    timers = Join-Path $exportRoot "timers.csv"
    timer_statistics = Join-Path $exportRoot "timer_statistics.csv"
    loading_streaming_events = Join-Path $exportRoot "loading_streaming_events.csv"
    shader_pso_events = Join-Path $exportRoot "shader_pso_events.csv"
    niagara_events = Join-Path $exportRoot "niagara_events.csv"
}
$rspPath = Join-Path $attemptRoot "review_commands.rsp"
$logPath = Join-Path $attemptRoot "unreal_insights.log"
$stdoutPath = Join-Path $attemptRoot "unreal_insights.stdout.log"
$stderrPath = Join-Path $attemptRoot "unreal_insights.stderr.log"
$manifestPath = Join-Path $attemptRoot "run_manifest.json"
$reportPath = Join-Path $attemptRoot "review_report.json"

function To-InsightsPath {
    param([Parameter(Mandatory = $true)][string]$LiteralPath)
    return $LiteralPath.Replace("\", "/")
}

$commands = @(
    "TimingInsights.ExportThreads `"$(To-InsightsPath $paths.threads)`"",
    "TimingInsights.ExportTimers `"$(To-InsightsPath $paths.timers)`"",
    "TimingInsights.ExportTimerStatistics `"$(To-InsightsPath $paths.timer_statistics)`" -maxTimerCount=10000 -sortBy=TotalInclusiveTime -sortOrder=Descending",
    "TimingInsights.ExportTimingEvents `"$(To-InsightsPath $paths.loading_streaming_events)`" -columns=ThreadName,TimerName,StartTime,EndTime,Duration,Depth -timers=*Load*,*Stream*,*IoDispatcher*,*Asset*,*Package*,*PostLoad*",
    "TimingInsights.ExportTimingEvents `"$(To-InsightsPath $paths.shader_pso_events)`" -columns=ThreadName,TimerName,StartTime,EndTime,Duration,Depth -timers=*Shader*,*PipelineState*,*PSO*,*Compile*",
    "TimingInsights.ExportTimingEvents `"$(To-InsightsPath $paths.niagara_events)`" -columns=ThreadName,TimerName,StartTime,EndTime,Duration,Depth -timers=*Niagara*"
)
[System.IO.File]::WriteAllLines($rspPath, $commands, [System.Text.UTF8Encoding]::new($false))

$arguments = @(
    "-OpenTraceFile=`"$tracePath`"",
    "-Unattended",
    "-AutoQuit",
    "-NoUI",
    "-NullRHI",
    "-ABSLOG=`"$logPath`"",
    "-ExecOnAnalysisCompleteCmd=`"@=$(To-InsightsPath $rspPath)`"",
    "-log"
)

$started = [DateTime]::UtcNow
$process = $null
$timedOut = $false
$exitCode = $null
try {
    $process = Start-Process `
        -FilePath $UnrealInsightsExe `
        -ArgumentList $arguments `
        -PassThru `
        -WindowStyle Hidden `
        -RedirectStandardOutput $stdoutPath `
        -RedirectStandardError $stderrPath
    if (-not $process.WaitForExit($TimeoutSeconds * 1000)) {
        $timedOut = $true
        Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        $process.WaitForExit(10000) | Out-Null
    }
    if (-not $timedOut) {
        $exitCode = $process.ExitCode
    }
}
finally {
    if ($null -ne $process -and -not $process.HasExited) {
        Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
    }
}
$finished = [DateTime]::UtcNow

$channels = @(
    ([string]$performance.requested_profile.insights_channels).Split(",") |
        ForEach-Object { $_.Trim() } |
        Where-Object { $_ }
)
$manifest = [ordered]@{
    schema = "skyguard.phase1.insights-review-run.v1"
    attempt_id = $attemptId
    generated_at_utc = [DateTime]::UtcNow.ToString("o")
    source_performance_gate = $PerformanceGateReport
    requested_channels = $channels
    bindings = @(
        New-Binding -Label "accepted_phase1_trace" -LiteralPath $tracePath
        New-Binding -Label "accepted_phase1_performance_report" -LiteralPath $PerformanceGateReport
        New-Binding -Label "unreal_insights_5_8" -LiteralPath $UnrealInsightsExe
        New-Binding -Label "engine_automation_contract" -LiteralPath $engineContract
        New-Binding -Label "engine_functional_test_contract" -LiteralPath $engineTests
        New-Binding -Label "review_command_file" -LiteralPath $rspPath
    )
    execution = [ordered]@{
        visible = $false
        unattended = $true
        null_rhi = $true
        no_ui = $true
        pid = if ($null -ne $process) { $process.Id } else { $null }
        command_line = $UnrealInsightsExe + " " + ($arguments -join " ")
        started_at_utc = $started.ToString("o")
        finished_at_utc = $finished.ToString("o")
        elapsed_seconds = [Math]::Round(($finished - $started).TotalSeconds, 3)
        timeout_seconds = $TimeoutSeconds
        timed_out = $timedOut
        exit_code = $exitCode
        log_path = $logPath
        stdout_path = $stdoutPath
        stderr_path = $stderrPath
    }
    exports = $paths
}
$manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $manifestPath -Encoding utf8

& python $verifier --manifest $manifestPath --output $reportPath
$verifyExit = $LASTEXITCODE

$latest = Join-Path $ProjectRoot "Saved\Reports\PHASE1_INSIGHTS_REVIEW_LATEST.json"
Copy-Item -LiteralPath $reportPath -Destination $latest -Force
Write-Host "P1.4 headless review report: $reportPath"
Write-Host "Latest report: $latest"
exit $verifyExit
