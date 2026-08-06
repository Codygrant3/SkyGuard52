param(
    [string]$UnrealRoot = "D:\UE_5.8",
    [int]$BuildTimeoutSeconds = 900,
    [int]$EditorStageTimeoutSeconds = 900
)

$ErrorActionPreference = "Stop"
$Root = "D:\Skyguard52"
$Project = Join-Path $Root "Skyguard52.uproject"
$BuildTool = Join-Path $UnrealRoot "Engine\Build\BatchFiles\Build.bat"
$UnrealCmd = Join-Path $UnrealRoot "Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
$AttemptId = "attempt_{0}" -f (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssfffZ")
$AttemptRoot = Join-Path $Root "Saved\BuildAttempts\PHASE4_M01_PCG_LANDSCAPE\$AttemptId"
$ReceiptPath = Join-Path $AttemptRoot "gate_receipt.json"
$LatestPath = Join-Path $Root "Saved\Reports\PHASE4_M01_PCG_LANDSCAPE_GATE_LATEST.json"
New-Item -ItemType Directory -Path $AttemptRoot -Force | Out-Null

$stageResults = [System.Collections.Generic.List[object]]::new()
$terminalState = "EXECUTION_FAILED"
$failure = $null

function Get-HeavyProcesses {
    @(Get-Process -ErrorAction SilentlyContinue | Where-Object {
        $_.ProcessName -in @(
            "UnrealEditor",
            "UnrealEditor-Cmd",
            "UnrealBuildTool",
            "AutomationTool",
            "ShaderCompileWorker",
            "UbaAgent",
            "UbaServer",
            "CrashReportClient",
            "Skyguard52"
        )
    })
}

function Assert-NoHeavyProcesses {
    param([string]$When)
    $active = @(Get-HeavyProcesses)
    if ($active.Count -gt 0) {
        $description = ($active | ForEach-Object {
            "$($_.ProcessName):$($_.Id)"
        }) -join ", "
        throw "Heavy process overlap ${When}: $description"
    }
}

function Wait-NoHeavyProcesses {
    param(
        [string]$When,
        [int]$TimeoutSeconds = 30
    )
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    do {
        $active = @(Get-HeavyProcesses)
        if ($active.Count -eq 0) {
            return
        }
        Start-Sleep -Milliseconds 500
    } while ((Get-Date) -lt $deadline)
    Assert-NoHeavyProcesses $When
}

function Stop-AttemptProcessTree {
    param([System.Diagnostics.Process]$Process)
    if ($Process -and -not $Process.HasExited) {
        & taskkill.exe /PID $Process.Id /T /F 2>&1 | Out-Null
        try { $Process.WaitForExit(10000) | Out-Null } catch {}
    }
}

function Invoke-BoundedStage {
    param(
        [string]$Name,
        [string]$FilePath,
        [string]$Arguments,
        [int]$TimeoutSeconds
    )
    Assert-NoHeavyProcesses "before $Name"
    $stdout = Join-Path $AttemptRoot "$Name.stdout.log"
    $stderr = Join-Path $AttemptRoot "$Name.stderr.log"
    $started = (Get-Date).ToUniversalTime()
    $process = $null
    try {
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
            Stop-AttemptProcessTree $process
            throw "$Name exceeded its bounded $TimeoutSeconds-second timeout"
        }
        # Ensure redirected async streams have fully flushed before scanning.
        $process.WaitForExit()
        # Refresh after the parameterless wait. Without this, some nested
        # cmd/Build.bat invocations can expose a stale/null ExitCode even
        # though the child has exited and its redirected streams are complete.
        $process.Refresh()
        $exitCode = [int]$process.ExitCode
        $criticalPatterns = @(
            "Fatal error",
            "Ensure condition failed",
            "Assertion failed",
            "Unhandled Exception",
            "GPU Crashed",
            "LogPython: Error"
        )
        $criticalHits = @()
        foreach ($path in @($stdout, $stderr)) {
            if (Test-Path -LiteralPath $path) {
                $criticalHits += @(
                    Select-String `
                        -LiteralPath $path `
                        -Pattern $criticalPatterns `
                        -SimpleMatch `
                        -ErrorAction SilentlyContinue |
                    ForEach-Object { "${path}:$($_.LineNumber):$($_.Line.Trim())" }
                )
            }
        }
        $ended = (Get-Date).ToUniversalTime()
        $result = [ordered]@{
            name = $Name
            started_at_utc = $started.ToString("o")
            ended_at_utc = $ended.ToString("o")
            duration_seconds = [math]::Round(($ended - $started).TotalSeconds, 3)
            exit_code = $exitCode
            stdout = $stdout
            stderr = $stderr
            critical_hits = $criticalHits
            pass = ($exitCode -eq 0 -and $criticalHits.Count -eq 0)
        }
        $stageResults.Add([pscustomobject]$result)
        if (-not $result.pass) {
            throw "$Name failed: exit=$exitCode critical_hits=$($criticalHits.Count)"
        }
    }
    finally {
        if ($process -and -not $process.HasExited) {
            Stop-AttemptProcessTree $process
        }
    }
    Wait-NoHeavyProcesses "after $Name"
}

function Write-GateReceipt {
    $cleanup = @(Get-HeavyProcesses | ForEach-Object {
        [ordered]@{ name = $_.ProcessName; pid = $_.Id }
    })
    $receipt = [ordered]@{
        schema = "skyguard.phase4.m01-pcg-landscape-gate.v1"
        attempt_id = $AttemptId
        attempt_root = $AttemptRoot
        terminal_state = $terminalState
        failure = $failure
        stages = @($stageResults)
        reports = [ordered]@{
            build = Join-Path $Root "Saved\Reports\PHASE4_M01_PCG_LANDSCAPE_BUILD.json"
            editor_acceptance = Join-Path $Root "Saved\Reports\PHASE4_M01_PCG_LANDSCAPE_EDITOR_ACCEPTANCE.json"
            offline_readiness = Join-Path $Root "Saved\Reports\PHASE4_M01_PCG_LANDSCAPE_READINESS_AUDIT.json"
        }
        cleanup = [ordered]@{
            heavy_process_count = $cleanup.Count
            remaining = $cleanup
        }
        promotion = [ordered]@{
            serialized_p4_4_handoff_complete = ($terminalState -eq "EXECUTION_COMPLETE")
            production_vegetation_complete = $false
            visible_gpu_accepted = $false
            aaa_accepted = $false
        }
    }
    $json = $receipt | ConvertTo-Json -Depth 12
    [System.IO.File]::WriteAllText($ReceiptPath, $json + [Environment]::NewLine)
    [System.IO.File]::WriteAllText($LatestPath, $json + [Environment]::NewLine)
}

try {
    Assert-NoHeavyProcesses "at gate start"

    $buildArgs = (
        "/c `"`"$BuildTool`" Skyguard52Editor Win64 Development " +
        "`"$Project`" -WaitMutex -NoHotReload`""
    )
    Invoke-BoundedStage `
        "01_UBT_BUILD" `
        "cmd.exe" `
        $buildArgs `
        $BuildTimeoutSeconds

    $builder = Join-Path $Root "Scripts\build_skyguard_phase4_m01_pcg_landscape_v5.py"
    $builderArgs = (
        "`"$Project`" -run=pythonscript -script=`"$builder`" " +
        "-unattended -nop4 -nosplash -NullRHI -stdout -FullStdOutLogOutput"
    )
    Invoke-BoundedStage `
        "02_NULLRHI_BUILD" `
        $UnrealCmd `
        $builderArgs `
        $EditorStageTimeoutSeconds

    $verifier = Join-Path $Root "Scripts\verify_skyguard_phase4_m01_pcg_landscape_assets.py"
    $verifierArgs = (
        "`"$Project`" -run=pythonscript -script=`"$verifier`" " +
        "-unattended -nop4 -nosplash -NullRHI -stdout -FullStdOutLogOutput"
    )
    Invoke-BoundedStage `
        "03_FRESH_EDITOR_AUDIT" `
        $UnrealCmd `
        $verifierArgs `
        $EditorStageTimeoutSeconds

    $automationArgs = (
        "`"$Project`" " +
        "`"-ExecCmds=Automation RunTests Skyguard52.Environment.Mission01Production`" " +
        "`"-TestExit=Automation Test Queue Empty`" " +
        "-unattended -nop4 -nosplash -NullRHI -stdout -FullStdOutLogOutput"
    )
    Invoke-BoundedStage `
        "04_NATIVE_AUTOMATION" `
        $UnrealCmd `
        $automationArgs `
        $EditorStageTimeoutSeconds

    $automationLog = Join-Path $AttemptRoot "04_NATIVE_AUTOMATION.stdout.log"
    $successCount = @(
        Select-String `
            -LiteralPath $automationLog `
            -Pattern "Test Completed. Result={Success}" `
            -SimpleMatch `
            -ErrorAction SilentlyContinue
    ).Count
    $failureCount = @(
        Select-String `
            -LiteralPath $automationLog `
            -Pattern "Test Completed. Result={Fail}" `
            -SimpleMatch `
            -ErrorAction SilentlyContinue
    ).Count
    if ($successCount -ne 3 -or $failureCount -ne 0) {
        throw "Expected 3/3 Phase 4 native tests; success=$successCount failure=$failureCount"
    }

    foreach ($report in @(
        "PHASE4_M01_PCG_LANDSCAPE_BUILD.json",
        "PHASE4_M01_PCG_LANDSCAPE_EDITOR_ACCEPTANCE.json"
    )) {
        $source = Join-Path $Root "Saved\Reports\$report"
        if (-not (Test-Path -LiteralPath $source)) {
            throw "Required report missing after gate: $source"
        }
        Copy-Item -LiteralPath $source -Destination (Join-Path $AttemptRoot $report)
    }

    $terminalState = "EXECUTION_COMPLETE"
}
catch {
    $failure = $_.Exception.Message
    throw
}
finally {
    # Only exact heavy processes are considered. If a failed child survived,
    # terminate it before the final receipt to protect host stability.
    foreach ($process in @(Get-HeavyProcesses)) {
        try {
            & taskkill.exe /PID $process.Id /T /F 2>&1 | Out-Null
        }
        catch {}
    }
    Start-Sleep -Milliseconds 500
    Write-GateReceipt
}

Write-Output "PHASE4_M01_PCG_LANDSCAPE_GATE=PASS"
Write-Output "ATTEMPT_ROOT=$AttemptRoot"
