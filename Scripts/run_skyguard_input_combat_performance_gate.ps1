[CmdletBinding()]
param(
    [string]$ProjectRoot = "D:\Skyguard52",
    [ValidateSet("CombatProfile", "CombatSoak")]
    [string]$CaptureKind = "CombatProfile",
    [ValidateRange(1, 3)]
    [int]$RepeatIndex = 1,
    [string]$PackageExe = "",
    [string]$PrerequisiteReceipt = "",
    [switch]$ValidateOnly
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$contractPath = Join-Path $ProjectRoot "Scripts\skyguard_input_combat_performance_contract_v1.json"
$verifier = Join-Path $ProjectRoot "Scripts\verify_skyguard_input_combat_performance_gate.py"
$reportsRoot = Join-Path $ProjectRoot "Saved\Reports"
$attemptsRoot = Join-Path $ProjectRoot "Saved\Profiling\InputCombat"

function ConvertTo-CommandLineArgument {
    param([Parameter(Mandatory = $true)][string]$Value)
    if ($Value -notmatch '[\s"]') { return $Value }
    return '"' + ($Value -replace '(\\*)"', '$1$1\"' -replace '(\\+)$', '$1$1') + '"'
}

function Get-DescendantProcessIds {
    param([Parameter(Mandatory = $true)][int]$RootProcessId)
    $all = @(Get-CimInstance Win32_Process | Select-Object ProcessId, ParentProcessId)
    $result = [System.Collections.Generic.List[int]]::new()
    $queue = [System.Collections.Generic.Queue[int]]::new()
    $queue.Enqueue($RootProcessId)
    while ($queue.Count -gt 0) {
        $parent = $queue.Dequeue()
        foreach ($candidate in $all) {
            if ([int]$candidate.ParentProcessId -eq $parent) {
                $child = [int]$candidate.ProcessId
                $result.Add($child)
                $queue.Enqueue($child)
            }
        }
    }
    return @($result)
}

function Stop-ExactProcessTree {
    param([Parameter(Mandatory = $true)][int]$RootProcessId)
    $descendants = @(Get-DescendantProcessIds -RootProcessId $RootProcessId)
    [array]::Reverse($descendants)
    foreach ($child in $descendants) {
        Stop-Process -Id $child -Force -ErrorAction SilentlyContinue
    }
    Stop-Process -Id $RootProcessId -Force -ErrorAction SilentlyContinue
}

function Get-CaptureMachineEventEvidence {
    param(
        [Parameter(Mandatory = $true)][DateTime]$StartTime,
        [Parameter(Mandatory = $true)][DateTime]$EndTime
    )

    $systemEvents = @(
        Get-WinEvent -FilterHashtable @{
            LogName = "System"
            StartTime = $StartTime
            EndTime = $EndTime
        } -ErrorAction SilentlyContinue |
            Where-Object {
                $_.Level -in @(1, 2) -and (
                    $_.ProviderName -match "^(nvlddmkm|Display|Microsoft-Windows-WHEA-Logger|Microsoft-Windows-Kernel-Power)$" -or
                    $_.Id -in @(13, 14, 18, 19, 20, 41, 46, 4101)
                )
            } |
            Select-Object -First 500
    )
    $applicationEvents = @(
        Get-WinEvent -FilterHashtable @{
            LogName = "Application"
            StartTime = $StartTime
            EndTime = $EndTime
        } -ErrorAction SilentlyContinue |
            Where-Object {
                $_.Level -in @(1, 2) -and (
                    $_.ProviderName -match "^(Application Error|Windows Error Reporting)$" -or
                    $_.Message -match "(?i)(Skyguard52|UnrealEditor|Unreal Engine|NahimicSvc)"
                )
            } |
            Select-Object -First 500
    )
    $records = @(
        foreach ($event in @($systemEvents + $applicationEvents)) {
            $propertyValues = @(
                $event.Properties | ForEach-Object { [string]$_.Value }
            )
            $message = if ([string]::IsNullOrWhiteSpace($event.Message)) {
                $propertyValues -join " | "
            } else {
                [string]$event.Message
            }
            [ordered]@{
                log_name = [string]$event.LogName
                time_created_utc = $event.TimeCreated.ToUniversalTime().ToString("o")
                provider = [string]$event.ProviderName
                event_id = [int]$event.Id
                level = [string]$event.LevelDisplayName
                record_id = [long]$event.RecordId
                message = $message
                properties = $propertyValues
            }
        }
    )
    $gpuDriverCount = @(
        $records | Where-Object {
            $_.provider -match "^(nvlddmkm|Display)$"
        }
    ).Count
    $wheaCount = @(
        $records | Where-Object {
            $_.provider -eq "Microsoft-Windows-WHEA-Logger"
        }
    ).Count
    $skyguardUnrealCount = @(
        $records | Where-Object {
            $_.message -match "(?i)(Skyguard52|UnrealEditor|Unreal Engine)"
        }
    ).Count
    $nahimicCount = @(
        $records | Where-Object {
            $_.message -match "(?i)NahimicSvc"
        }
    ).Count
    return [ordered]@{
        schema = "skyguard.input-combat-machine-events.v1"
        window_start_utc = $StartTime.ToUniversalTime().ToString("o")
        window_end_utc = $EndTime.ToUniversalTime().ToString("o")
        query_complete = $true
        captured_event_limit_per_log = 500
        counts = [ordered]@{
            total = $records.Count
            gpu_driver_or_display = $gpuDriverCount
            whea = $wheaCount
            skyguard_or_unreal_application = $skyguardUnrealCount
            nahimic_application = $nahimicCount
        }
        events = $records
    }
}

foreach ($required in @($contractPath, $verifier)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
        throw "Required input-combat gate file is missing: $required"
    }
}

$contract = Get-Content -LiteralPath $contractPath -Raw | ConvertFrom-Json
$duration = if ($CaptureKind -eq "CombatSoak") {
    [int]$contract.capture_matrix.combat_soak.minimum_seconds_each
} else {
    [int]$contract.capture_matrix.combat_profile.minimum_seconds_each
}
$attemptId = "attempt_" + [DateTime]::UtcNow.ToString("yyyyMMddTHHmmssfffZ")
$attemptRoot = Join-Path $attemptsRoot $attemptId
$artifactRoot = Join-Path $attemptRoot "artifacts"
$logsRoot = Join-Path $attemptRoot "logs"
New-Item -ItemType Directory -Force -Path $artifactRoot, $logsRoot, $reportsRoot | Out-Null

$tracePath = Join-Path $artifactRoot "input_combat.utrace"
$gpuSamplesPath = Join-Path $artifactRoot "nvidia_smi_samples.csv"
$machineEventsPath = Join-Path $artifactRoot "windows_machine_events.json"
$manifestPath = Join-Path $attemptRoot "run_manifest.json"
$reportPath = Join-Path $attemptRoot "gate_report.json"
$latestPath = Join-Path $reportsRoot "INPUT_COMBAT_PERFORMANCE_GATE_LATEST.json"

$traceChannels = @($contract.required_trace_channels | ForEach-Object { [string]$_ })
$csvCategories = @($contract.required_csv_categories | ForEach-Object { [string]$_ })
$runtimeArguments = @(
    "/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_Playable_v1",
    "-windowed",
    "-ResX=1920",
    "-ResY=1080",
    "-d3d12",
    "-sm6",
    "-NoVSync",
    "-fps=60",
    "-nop4",
    "-nosplash",
    "-stdout",
    "-FullStdOutLogOutput",
    "-trace=$($traceChannels -join ',')",
    "-tracefile=$tracePath",
    "-tracefiletrunc",
    "-traceautostart=1",
    "-csvCaptureFrames=$($duration * 60)",
    "-csvCategories=$($csvCategories -join ',')",
    "-csvGpuStats",
    "-csvNamedEvents",
    "-csvMetadata=phase=input_combat,kind=$CaptureKind,repeat=$RepeatIndex,attempt=$attemptId",
    "-ExecCmds=stat RHI,stat streaming"
)

$sourceFiles = @(
    Get-ChildItem -LiteralPath (Join-Path $ProjectRoot "Source") `
        -File -Recurse -Include *.cpp,*.h -ErrorAction SilentlyContinue
)
$instrumentation = @()
foreach ($window in $contract.required_windows) {
    foreach ($literalKind in @("region", "begin_bookmark", "end_bookmark")) {
        $literal = [string]$window.$literalKind
        $matches = @(
            $sourceFiles | Select-String -SimpleMatch -Pattern $literal -ErrorAction SilentlyContinue
        )
        $instrumentation += [ordered]@{
            window_id = [string]$window.id
            kind = $literalKind
            literal = $literal
            found = $matches.Count -gt 0
            locations = @(
                $matches | ForEach-Object {
                    [ordered]@{
                        path = $_.Path
                        line = $_.LineNumber
                    }
                }
            )
        }
    }
}

$prerequisite = [ordered]@{
    gate = "MISSING"
    path = $PrerequisiteReceipt
    reason = "No prerequisite receipt supplied."
}
if (-not [string]::IsNullOrWhiteSpace($PrerequisiteReceipt) -and
    (Test-Path -LiteralPath $PrerequisiteReceipt -PathType Leaf)) {
    $rawPrerequisite = Get-Content -LiteralPath $PrerequisiteReceipt -Raw | ConvertFrom-Json
    $prerequisite = [ordered]@{
        gate = [string]$rawPrerequisite.gate
        path = (Resolve-Path -LiteralPath $PrerequisiteReceipt).Path
        reason = $null
    }
}

$manifest = [ordered]@{
    schema = "skyguard.input-combat-performance.run.v1"
    attempt_id = $attemptId
    generated_at_utc = [DateTime]::UtcNow.ToString("o")
    capture_kind = $CaptureKind
    repeat_index = $RepeatIndex
    contract = [ordered]@{
        path = (Resolve-Path -LiteralPath $contractPath).Path
        sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $contractPath).Hash.ToLowerInvariant()
    }
    controls = [ordered]@{
        validate_only = [bool]$ValidateOnly
    }
    prerequisite = $prerequisite
    source_instrumentation = $instrumentation
    requested_profile = [ordered]@{
        duration_seconds = $duration
        resolution = [ordered]@{ x = 1920; y = 1080 }
        target_fps = 60
        trace_channels = $traceChannels
        csv_categories = $csvCategories
        runtime_arguments = $runtimeArguments
        external_gpu_telemetry = [ordered]@{
            provider = "nvidia-smi"
            interval_seconds = 1
            fields = @($contract.required_external_gpu_samples.required_fields)
        }
    }
    execution = [ordered]@{
        terminal_state = if ($ValidateOnly) { "VALIDATED_NOT_EXECUTED" } else { "NOT_STARTED" }
        visible_unreal_launched = $false
        package_exe = $PackageExe
    }
    artifacts = [ordered]@{
        trace = $tracePath
        nvidia_smi_samples = $gpuSamplesPath
        windows_machine_events = $machineEventsPath
    }
}
$manifest | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $manifestPath -Encoding utf8

if (-not $ValidateOnly) {
    if ($prerequisite.gate -ne "PASS") {
        $manifest.execution.terminal_state = "BLOCKED_PREREQUISITE"
    }
    elseif (@($instrumentation | Where-Object { -not $_.found }).Count -gt 0) {
        $manifest.execution.terminal_state = "BLOCKED_RUNTIME_BOOKMARKS"
    }
    elseif ([string]::IsNullOrWhiteSpace($PackageExe) -or
        -not (Test-Path -LiteralPath $PackageExe -PathType Leaf)) {
        $manifest.execution.terminal_state = "BLOCKED_PACKAGE_EXE"
    }
    else {
        $nvidiaSmi = Get-Command nvidia-smi.exe -ErrorAction SilentlyContinue
        if ($null -eq $nvidiaSmi) {
            $manifest.execution.terminal_state = "BLOCKED_NVIDIA_SMI_MISSING"
            $manifest | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $manifestPath -Encoding utf8
            & python $verifier --manifest $manifestPath --output $reportPath --latest-output $latestPath
            exit $LASTEXITCODE
        }
        $active = @(
            Get-CimInstance Win32_Process |
                Where-Object {
                    $_.Name -in @("UnrealEditor.exe", "UnrealEditor-Cmd.exe", "Skyguard52.exe")
                }
        )
        if ($active.Count -gt 0) {
            $manifest.execution.terminal_state = "BLOCKED_ACTIVE_UNREAL_PROCESS"
            $manifest.execution.active_pids = @($active | ForEach-Object { [int]$_.ProcessId })
            $manifest | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $manifestPath -Encoding utf8
            & python $verifier --manifest $manifestPath --output $reportPath --latest-output $latestPath
            exit $LASTEXITCODE
        }

        $csvRoots = @(
            (Join-Path $ProjectRoot "Saved\Profiling"),
            (Join-Path $env:LOCALAPPDATA "UnrealEngine\5.8\Saved\Profiling\CSV")
        )
        $csvBefore = @(
            Get-ChildItem -LiteralPath $csvRoots -File -Recurse -ErrorAction SilentlyContinue |
                Where-Object { $_.Extension -in @(".csv", ".gz") } |
                ForEach-Object { $_.FullName }
        )
        "timestamp,utilization_gpu_percent,memory_used_mib,memory_total_mib,temperature_c,pstate" |
            Set-Content -LiteralPath $gpuSamplesPath -Encoding utf8
        $stdoutPath = Join-Path $logsRoot "runtime.stdout.log"
        $stderrPath = Join-Path $logsRoot "runtime.stderr.log"
        $argumentString = ($runtimeArguments | ForEach-Object {
            ConvertTo-CommandLineArgument $_
        }) -join " "
        $started = [DateTime]::UtcNow
        $process = Start-Process `
            -FilePath $PackageExe `
            -ArgumentList $argumentString `
            -WorkingDirectory (Split-Path -Parent $PackageExe) `
            -RedirectStandardOutput $stdoutPath `
            -RedirectStandardError $stderrPath `
            -PassThru
        $manifest.execution.visible_unreal_launched = $true
        $manifest.execution.pid = $process.Id
        $manifest.execution.started_at_utc = $started.ToString("o")
        $manifest.execution.command_line = "$PackageExe $argumentString"
        $manifest.execution.stdout = $stdoutPath
        $manifest.execution.stderr = $stderrPath
        $manifest | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $manifestPath -Encoding utf8

        while (-not $process.HasExited -and
            ([DateTime]::UtcNow - $started).TotalSeconds -lt $duration) {
            $sample = & $nvidiaSmi.Source `
                "--query-gpu=timestamp,utilization.gpu,memory.used,memory.total,temperature.gpu,pstate" `
                "--format=csv,noheader,nounits" 2>$null
            if ($LASTEXITCODE -eq 0 -and $sample) {
                $sample | Add-Content -LiteralPath $gpuSamplesPath -Encoding utf8
            }
            Start-Sleep -Seconds 1
            $process.Refresh()
        }

        $requestedClose = $false
        $forcedTermination = $false
        if (-not $process.HasExited) {
            $requestedClose = $process.CloseMainWindow()
            if (-not $process.WaitForExit(20000)) {
                $forcedTermination = $true
                Stop-ExactProcessTree -RootProcessId $process.Id
                $process.WaitForExit(10000) | Out-Null
            }
        }
        else {
            $process.WaitForExit()
        }
        if ($process.HasExited) {
            # Drain redirected stdout/stderr readers before recording ExitCode.
            $process.WaitForExit()
        }
        $finished = [DateTime]::UtcNow
        $machineEvents = Get-CaptureMachineEventEvidence `
            -StartTime $started.AddSeconds(-2) `
            -EndTime $finished.AddSeconds(2)
        $machineEvents | ConvertTo-Json -Depth 12 |
            Set-Content -LiteralPath $machineEventsPath -Encoding utf8
        $csvAfter = @(
            Get-ChildItem -LiteralPath $csvRoots -File -Recurse -ErrorAction SilentlyContinue |
                Where-Object { $_.Extension -in @(".csv", ".gz") } |
                ForEach-Object { $_.FullName }
        )
        $newCsv = @($csvAfter | Where-Object { $_ -notin $csvBefore })
        $manifest.artifacts.csv_files = $newCsv
        $manifest.execution.finished_at_utc = $finished.ToString("o")
        $manifest.execution.elapsed_seconds = [Math]::Round(($finished - $started).TotalSeconds, 3)
        $manifest.execution.graceful_close_requested = $requestedClose
        $manifest.execution.forced_termination = $forcedTermination
        $manifest.execution.process_exit_observed = [bool]$process.HasExited
        $manifest.execution.exit_code = if ($process.HasExited) { $process.ExitCode } else { $null }
        $manifest.execution.terminal_state = if (
            (Test-Path -LiteralPath $tracePath -PathType Leaf) -and
            $newCsv.Count -gt 0 -and
            (Get-Content -LiteralPath $gpuSamplesPath).Count -gt 1
        ) { "CAPTURE_COMPLETE" } else { "CAPTURE_INCOMPLETE" }
    }
    $manifest | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $manifestPath -Encoding utf8
}

& python $verifier --manifest $manifestPath --output $reportPath --latest-output $latestPath
exit $LASTEXITCODE
