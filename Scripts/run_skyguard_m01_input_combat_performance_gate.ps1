[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$PackageAttemptRoot,
    [string]$ProjectRoot = "D:\Skyguard52",
    [string]$Map = "/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_Playable_v1",
    [ValidateRange(1, 10)]
    [int]$MemorySampleSeconds = 1,
    [ValidateRange(30, 600)]
    [int]$ExitGraceSeconds = 180,
    [switch]$ValidateOnly
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$expectedMap = "/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_Playable_v1"
$manifestSchema = "skyguard.m01.input-combat-performance.manifest.v1"
$runtimeHookSource = Join-Path $ProjectRoot "Source\Skyguard52\SkyguardInputCombatPerformanceCapture.cpp"
$runtimeHookHeader = Join-Path $ProjectRoot "Source\Skyguard52\SkyguardInputCombatPerformanceCapture.h"
$verifier = Join-Path $ProjectRoot "Scripts\verify_skyguard_m01_input_combat_performance_gate.py"

function Get-PortableSha256 {
    param([Parameter(Mandatory = $true)][string]$LiteralPath)
    $algorithm = [System.Security.Cryptography.SHA256]::Create()
    try {
        $stream = [System.IO.File]::OpenRead($LiteralPath)
        try {
            return ([System.BitConverter]::ToString(
                $algorithm.ComputeHash($stream))).Replace("-", "").ToLowerInvariant()
        } finally {
            $stream.Dispose()
        }
    } finally {
        $algorithm.Dispose()
    }
}

function New-FileRecord {
    param(
        [Parameter(Mandatory = $true)][string]$Label,
        [Parameter(Mandatory = $true)][string]$LiteralPath
    )
    $item = Get-Item -LiteralPath $LiteralPath -ErrorAction Stop
    if ($item.PSIsContainer) {
        throw "Bound artifact is a directory, not a file: $LiteralPath"
    }
    return [ordered]@{
        label = $Label
        path = $item.FullName
        bytes = [int64]$item.Length
        sha256 = Get-PortableSha256 -LiteralPath $item.FullName
    }
}

function ConvertTo-Argument {
    param([Parameter(Mandatory = $true)][string]$Value)
    if ($Value -notmatch '[\s"]') { return $Value }
    return '"' + ($Value -replace '(\\*)"', '$1$1\"' -replace '(\\+)$', '$1$1') + '"'
}

function Stop-ExactProcessTree {
    param([Parameter(Mandatory = $true)][int]$RootProcessId)
    & taskkill.exe /PID $RootProcessId /T /F | Out-Null
}

function Get-CsvSnapshot {
    param([Parameter(Mandatory = $true)][string[]]$Roots)
    $snapshot = @{}
    foreach ($root in $Roots) {
        if (-not (Test-Path -LiteralPath $root -PathType Container)) { continue }
        foreach ($file in Get-ChildItem -LiteralPath $root -Filter "Profile(*).csv" -File) {
            $snapshot[$file.FullName.ToLowerInvariant()] = [ordered]@{
                path = $file.FullName
                bytes = [int64]$file.Length
                modified_utc = $file.LastWriteTimeUtc.ToString("o")
            }
        }
    }
    return $snapshot
}

function Test-RuntimeHookSource {
    if (-not (Test-Path -LiteralPath $runtimeHookSource -PathType Leaf) -or
        -not (Test-Path -LiteralPath $runtimeHookHeader -PathType Leaf)) {
        return $false
    }
    $source = Get-Content -LiteralPath $runtimeHookSource -Raw
    return (
        $source -match 'SkyguardCombatPerfReceipt' -and
        $source -match 'skyguard\.m01\.input-combat\.runtime-receipt\.v1' -and
        $source -match 'weather_visibility_transition' -and
        $source -match 'automation_injected'
    )
}

function Test-PackagedRuntimeHook {
    param([Parameter(Mandatory = $true)][string]$LiteralPath)

    $marker = "skyguard.m01.input-combat.runtime-receipt.v1"
    $unicodeMarker = [System.Text.Encoding]::ASCII.GetString(
        [System.Text.Encoding]::Unicode.GetBytes($marker)
    )
    $bufferBytes = 1048576
    $overlapBytes = [System.Text.Encoding]::Unicode.GetByteCount($marker) - 1
    [byte[]]$buffer = New-Object byte[] ($bufferBytes + $overlapBytes)
    $carryBytes = 0

    $stream = [System.IO.File]::Open(
        $LiteralPath,
        [System.IO.FileMode]::Open,
        [System.IO.FileAccess]::Read,
        [System.IO.FileShare]::Read
    )
    try {
        while (
            ($bytesRead = $stream.Read($buffer, $carryBytes, $bufferBytes)) -gt 0
        ) {
            $windowBytes = $carryBytes + $bytesRead
            $window = [System.Text.Encoding]::ASCII.GetString(
                $buffer,
                0,
                $windowBytes
            )
            if ($window.Contains($marker)) {
                return $true
            }
            $windowStart = $stream.Position - $bytesRead - $carryBytes
            $unicodeIndex = $window.IndexOf(
                $unicodeMarker,
                [System.StringComparison]::Ordinal
            )
            while ($unicodeIndex -ge 0) {
                if ((($windowStart + $unicodeIndex) % 2) -eq 0) {
                    return $true
                }
                $unicodeIndex = $window.IndexOf(
                    $unicodeMarker,
                    $unicodeIndex + 1,
                    [System.StringComparison]::Ordinal
                )
            }

            $carryBytes = [System.Math]::Min($overlapBytes, $windowBytes)
            if ($carryBytes -gt 0) {
                [System.Array]::Copy(
                    $buffer,
                    $windowBytes - $carryBytes,
                    $buffer,
                    0,
                    $carryBytes
                )
            }
        }

        return $false
    }
    finally {
        $stream.Dispose()
    }
}

if ($Map -ne $expectedMap) {
    throw "This gate is bound to exact M01 map $expectedMap; received $Map"
}
$packageAttempt = (Resolve-Path -LiteralPath $PackageAttemptRoot).Path
$attemptId = Split-Path $packageAttempt -Leaf
$packageRoot = Join-Path $packageAttempt "packages\Development\Windows"
$executable = Join-Path $packageRoot "Skyguard52.exe"
$runtimeExecutable = Join-Path $packageRoot `
    "Skyguard52\Binaries\Win64\Skyguard52.exe"
$packagedPso = Join-Path $packageRoot "Skyguard52\Content\PipelineCaches\Windows\Skyguard52_PCD3D_SM6.stable.upipelinecache"
$sourceMap = Join-Path $ProjectRoot "Content\Skyguard\Maps\Lvl_M01_CoastalIntercept_Playable_v1.umap"
$requiredFiles = @(
    $executable,
    $runtimeExecutable,
    $packagedPso,
    $sourceMap,
    (Join-Path $ProjectRoot "Skyguard52.uproject"),
    (Join-Path $ProjectRoot "Config\DefaultEngine.ini"),
    (Join-Path $ProjectRoot "Config\DefaultGame.ini"),
    (Join-Path $ProjectRoot "Config\DefaultInput.ini"),
    $verifier
)
foreach ($required in $requiredFiles) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
        throw "Required input-combat gate file is missing: $required"
    }
}

$sourceHookReady = Test-RuntimeHookSource
$packageHookReady = Test-PackagedRuntimeHook -LiteralPath $runtimeExecutable
$hookReady = $sourceHookReady -and $packageHookReady
if ($ValidateOnly) {
    $result = [ordered]@{
        schema = "skyguard.m01.input-combat-performance.preflight.v1"
        package_attempt = $packageAttempt
        package_executable = $executable
        package_runtime_binary = $runtimeExecutable
        expected_map = $expectedMap
        resolution = [ordered]@{ x = 1920; y = 1080 }
        combat_capture_count = 3
        combat_capture_seconds = 180
        soak_count = 1
        soak_seconds = 1200
        source_runtime_hook_ready = $sourceHookReady
        packaged_runtime_hook_ready = $packageHookReady
        runtime_hook_ready = $hookReady
        runtime_hook_source = $runtimeHookSource
        status = if ($hookReady) { "READY_TO_RUN" } else { "BLOCKED_RUNTIME_HOOK_MISSING" }
    }
    $result | ConvertTo-Json -Depth 8
    if (-not $hookReady) { exit 2 }
    exit 0
}
if (-not $hookReady) {
    throw "Runtime input-combat telemetry hook is missing. Run -ValidateOnly and implement the hook contract before launching a package."
}

$busy = @(
    Get-Process -ErrorAction SilentlyContinue |
        Where-Object {
            $_.ProcessName -match '^(UnrealEditor|UnrealEditor-Cmd|ShaderCompileWorker|Skyguard52|UnrealBuildTool|AutomationTool)$'
        }
)
if ($busy.Count -gt 0) {
    throw "Unreal/Skyguard build lane is occupied: $($busy.ProcessName -join ', ')"
}

$stamp = [DateTime]::UtcNow.ToString("yyyyMMddTHHmmssfffZ")
$attemptRoot = Join-Path $ProjectRoot "Saved\Profiling\M01InputCombat\attempt_$stamp"
$artifactsRoot = Join-Path $attemptRoot "artifacts"
$logsRoot = Join-Path $attemptRoot "logs"
New-Item -ItemType Directory -Force -Path $artifactsRoot, $logsRoot | Out-Null
$manifestPath = Join-Path $attemptRoot "run_manifest.json"
$gateReportPath = Join-Path $attemptRoot "gate_report.json"

$bindings = @(
    New-FileRecord -Label "package_executable" -LiteralPath $executable
    New-FileRecord -Label "package_runtime_binary" -LiteralPath $runtimeExecutable
    New-FileRecord -Label "source_map" -LiteralPath $sourceMap
    New-FileRecord -Label "uproject" -LiteralPath (Join-Path $ProjectRoot "Skyguard52.uproject")
    New-FileRecord -Label "default_engine_config" -LiteralPath (Join-Path $ProjectRoot "Config\DefaultEngine.ini")
    New-FileRecord -Label "default_game_config" -LiteralPath (Join-Path $ProjectRoot "Config\DefaultGame.ini")
    New-FileRecord -Label "default_input_config" -LiteralPath (Join-Path $ProjectRoot "Config\DefaultInput.ini")
    New-FileRecord -Label "packaged_pso_cache" -LiteralPath $packagedPso
)

$manifest = [ordered]@{
    schema = $manifestSchema
    attempt_id = "attempt_$stamp"
    generated_at_utc = [DateTime]::UtcNow.ToString("o")
    terminal_state = "RUNNING"
    failure = $null
    project_root = $ProjectRoot
    package_attempt_root = $packageAttempt
    package_attempt_id = $attemptId
    package_configuration = "Development"
    expected_map = $expectedMap
    thresholds = [ordered]@{
        mean_frame_time_ms_max = 16.7
        p95_frame_time_ms_max = 22.2
        max_frame_time_ms_max = 100.0
        hitch_over_100ms_max = 0
        soak_memory_slope_bytes_per_minute_max = 8388608
        soak_memory_tail_growth_bytes_max = 268435456
    }
    required_event_counts = [ordered]@{
        aim_input = 1
        ads_started = 1
        ads_left_fire_overlap = 1
        rifle_shot = 5
        weapon_switch = 1
        igla_lock_acquired = 1
        igla_launch = 1
        drone_breakup = 1
        boss_destroyed = 1
        weather_visibility_transition = 1
    }
    bindings = $bindings
    stages = @()
}
$manifest | ConvertTo-Json -Depth 16 |
    Set-Content -LiteralPath $manifestPath -Encoding utf8

$csvRoots = @(
    (Join-Path $packageRoot "Skyguard52\Saved\Profiling\CSV"),
    (Join-Path $env:LOCALAPPDATA "Skyguard52\Saved\Profiling\CSV")
)

function Invoke-InputCombatStage {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][ValidateSet("combat", "soak")][string]$Kind,
        [Parameter(Mandatory = $true)][int]$DurationSeconds
    )
    $runtimeReceipt = Join-Path $artifactsRoot "$Name.runtime_receipt.json"
    $trace = Join-Path $artifactsRoot "$Name.utrace"
    $csvArtifact = Join-Path $artifactsRoot "$Name.csv"
    $memorySeries = Join-Path $artifactsRoot "$Name.memory.csv"
    $stdout = Join-Path $logsRoot "$Name.stdout.log"
    $stderr = Join-Path $logsRoot "$Name.stderr.log"
    $arguments = @(
        $expectedMap,
        "-windowed", "-ResX=1920", "-ResY=1080",
        "-d3d12", "-sm6", "-NoVSync",
        "-stdout", "-FullStdOutLogOutput", "-nosplash",
        "-trace=cpu,gpu,frame,bookmark,loadtime,file,assetload,memory",
        "-tracefile=$trace", "-tracefiletrunc", "-traceautostart=1",
        "-csvCategories=Global", "-csvGpuStats", "-csvNamedEvents",
        "-csvMetadata=gate=m01_input_combat,run=$Name,package=$attemptId",
        "-SkyguardCombatPerfRunId=$Name",
        "-SkyguardCombatPerfKind=$Kind",
        "-SkyguardCombatPerfDurationSeconds=$DurationSeconds",
        "-SkyguardCombatPerfReceipt=$runtimeReceipt",
        "-SkyguardCombatPerfExpectedMap=$expectedMap"
    )
    $argumentLine = ($arguments | ForEach-Object { ConvertTo-Argument $_ }) -join " "
    $beforeCsv = Get-CsvSnapshot -Roots $csvRoots
    $started = [DateTime]::UtcNow
    $process = Start-Process -FilePath $executable -ArgumentList $argumentLine `
        -WorkingDirectory $packageRoot -WindowStyle Normal -PassThru `
        -RedirectStandardOutput $stdout -RedirectStandardError $stderr
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    $samples = [System.Collections.Generic.List[object]]::new()
    $deadline = (Get-Date).AddSeconds($DurationSeconds + $ExitGraceSeconds)
    $timedOut = $false
    while (-not $process.HasExited) {
        if ((Get-Date) -ge $deadline) {
            $timedOut = $true
            Stop-ExactProcessTree -RootProcessId $process.Id
            break
        }
        try {
            $process.Refresh()
            $samples.Add([pscustomobject]@{
                timestamp_utc = [DateTime]::UtcNow.ToString("o")
                elapsed_seconds = [Math]::Round($stopwatch.Elapsed.TotalSeconds, 3)
                working_set_bytes = [int64]$process.WorkingSet64
                private_memory_bytes = [int64]$process.PrivateMemorySize64
                virtual_memory_bytes = [int64]$process.VirtualMemorySize64
                cpu_seconds = [Math]::Round($process.TotalProcessorTime.TotalSeconds, 3)
                handle_count = [int]$process.HandleCount
            })
        } catch {
            if (-not $process.HasExited) { throw }
        }
        Start-Sleep -Seconds $MemorySampleSeconds
        $process.Refresh()
    }
    $process.WaitForExit()
    $process.Refresh()
    $stopwatch.Stop()
    $samples | Export-Csv -LiteralPath $memorySeries -NoTypeInformation -Encoding utf8
    $exitCode = $null
    try { $exitCode = [int]$process.ExitCode } catch { $exitCode = $null }
    $afterCsv = Get-CsvSnapshot -Roots $csvRoots
    $newCsv = @(
        $afterCsv.Keys |
            Where-Object { -not $beforeCsv.ContainsKey($_) } |
            ForEach-Object { $afterCsv[$_].path }
    )
    if ($newCsv.Count -ne 1) {
        throw "$Name produced $($newCsv.Count) new Unreal CSV files; exactly one is required."
    }
    Copy-Item -LiteralPath $newCsv[0] -Destination $csvArtifact
    return [ordered]@{
        name = $Name
        kind = $Kind
        requested_duration_seconds = $DurationSeconds
        resolution = [ordered]@{ x = 1920; y = 1080 }
        pid = $process.Id
        started_at_utc = $started.ToString("o")
        finished_at_utc = [DateTime]::UtcNow.ToString("o")
        observed_duration_seconds = [Math]::Round($stopwatch.Elapsed.TotalSeconds, 3)
        timeout_seconds = $DurationSeconds + $ExitGraceSeconds
        timed_out = $timedOut
        exit_code = $exitCode
        command_line = "$executable $argumentLine"
        runtime_receipt = $runtimeReceipt
        csv = $csvArtifact
        trace = $trace
        memory_series = $memorySeries
        stdout = $stdout
        stderr = $stderr
    }
}

try {
    foreach ($stageSpec in @(
        @{ Name = "combat_01"; Kind = "combat"; Seconds = 180 },
        @{ Name = "combat_02"; Kind = "combat"; Seconds = 180 },
        @{ Name = "combat_03"; Kind = "combat"; Seconds = 180 },
        @{ Name = "soak_01"; Kind = "soak"; Seconds = 1200 }
    )) {
        $stage = Invoke-InputCombatStage `
            -Name $stageSpec.Name -Kind $stageSpec.Kind -DurationSeconds $stageSpec.Seconds
        $manifest.stages += $stage
        $manifest | ConvertTo-Json -Depth 16 |
            Set-Content -LiteralPath $manifestPath -Encoding utf8
        if ($stage.timed_out -or $stage.exit_code -ne 0) {
            throw "$($stage.name) did not complete with a clean zero exit."
        }
        if (-not (Test-Path -LiteralPath $stage.runtime_receipt -PathType Leaf)) {
            throw "$($stage.name) produced no runtime telemetry receipt."
        }
    }
    $manifest.terminal_state = "EXECUTION_COMPLETE"
} catch {
    $manifest.terminal_state = "FAILED_HARNESS"
    $manifest.failure = $_.Exception.Message
} finally {
    $manifest | ConvertTo-Json -Depth 16 |
        Set-Content -LiteralPath $manifestPath -Encoding utf8
}

& py -3 $verifier --manifest $manifestPath --report $gateReportPath
$verifyExit = $LASTEXITCODE
$latest = Join-Path $ProjectRoot "Saved\Reports\M01_INPUT_COMBAT_PERFORMANCE_GATE_LATEST.json"
Copy-Item -LiteralPath $gateReportPath -Destination $latest -Force
$verification = Get-Content -LiteralPath $gateReportPath -Raw | ConvertFrom-Json
if ($manifest.terminal_state -ne "EXECUTION_COMPLETE" -or
    $verifyExit -ne 0 -or $verification.gate -ne "PASS") {
    throw "M01 input-driven combat performance gate failed. Report: $gateReportPath"
}
Write-Output "M01_INPUT_COMBAT_PERFORMANCE_GATE=PASS"
Write-Output "ATTEMPT=$attemptRoot"
Write-Output "REPORT=$gateReportPath"
