[CmdletBinding()]
param(
    [string]$ProjectRoot = "D:\Skyguard52",
    [string]$UnrealRoot = "D:\UE_5.8",
    [ValidateRange(100, 240)]
    [int]$ProfileTimeoutSeconds = 150
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$ContractPath = Join-Path $ProjectRoot "Docs\AAA_Review\PHASE4_M01_LANDSCAPE_VISIBLE_ATTEMPT05_RECOVERY03_CONTRACT.json"
$Contract = Get-Content -LiteralPath $ContractPath -Raw | ConvertFrom-Json
$ProjectFile = Join-Path $ProjectRoot "Skyguard52.uproject"
$EditorExe = Join-Path $UnrealRoot "Engine\Binaries\Win64\UnrealEditor.exe"
$CompiledModule = Join-Path $ProjectRoot "Binaries\Win64\UnrealEditor-Skyguard52.dll"
$GateVerifier = Join-Path $ProjectRoot "Scripts\verify_skyguard_phase4_m01_landscape_visible_gpu_gate_attempt05.py"
$RenderAcceptance = Join-Path $ProjectRoot $Contract.immutable_predecessor_evidence.render_state_acceptance.file
$CaptureRoot = Join-Path $ProjectRoot $Contract.accepted_capture_evidence.root
$BaselineCaptureRoot = Join-Path $CaptureRoot "baseline"
$CandidateCaptureRoot = Join-Path $CaptureRoot "candidate"
$RecoveryRoot = Join-Path $ProjectRoot $Contract.recovery_execution.recovery_root
$LogsRoot = Join-Path $RecoveryRoot "logs"
$ArtifactsRoot = Join-Path $RecoveryRoot "artifacts"
$ManifestPath = Join-Path $RecoveryRoot "recovery_manifest.json"
$GatePath = Join-Path $RecoveryRoot "gate_report.json"
$LatestGate = Join-Path $ProjectRoot "Saved\Reports\PHASE4_M01_LANDSCAPE_VISIBLE_GPU_REVIEW_ATTEMPT05_RECOVERY03_LATEST.json"
$BaselineMap = $Contract.immutable_packages.baseline_map.asset
$CandidateMap = $Contract.immutable_packages.candidate_map.asset
$CsvRoots = @(
    (Join-Path $ProjectRoot "Saved\Profiling\CSV"),
    (Join-Path $env:LOCALAPPDATA "UnrealEngine\5.8\Saved\Profiling\CSV")
)
$ExactHeavyNames = @(
    "UnrealEditor",
    "UnrealEditor-Cmd",
    "UnrealBuildTool",
    "AutomationTool",
    "ShaderCompileWorker",
    "UbaAgent",
    "UbaServer",
    "CrashReportClient",
    "Skyguard52",
    "blender"
)

function Get-Sha256 {
    param([Parameter(Mandatory = $true)][string]$Path)
    $stream = [System.IO.File]::Open(
        [System.IO.Path]::GetFullPath($Path),
        [System.IO.FileMode]::Open,
        [System.IO.FileAccess]::Read,
        [System.IO.FileShare]::Read
    )
    $algorithm = [System.Security.Cryptography.SHA256]::Create()
    try {
        return (
            [System.BitConverter]::ToString(
                $algorithm.ComputeHash($stream)
            ).Replace("-", "")
        ).ToLowerInvariant()
    }
    finally {
        $algorithm.Dispose()
        $stream.Dispose()
    }
}

function Save-Json {
    param(
        [Parameter(Mandatory = $true)]$Value,
        [Parameter(Mandatory = $true)][string]$Path
    )
    $Value | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath $Path -Encoding UTF8
}

function ConvertTo-Argument {
    param([Parameter(Mandatory = $true)][string]$Value)
    if ($Value -notmatch '[\s"]') {
        return $Value
    }
    return '"' + ($Value -replace '(\\*)"', '$1$1\"' -replace '(\\+)$', '$1$1') + '"'
}

function Get-DescendantProcessIds {
    param([Parameter(Mandatory = $true)][int]$RootProcessId)
    $processes = @(Get-CimInstance Win32_Process | Select-Object ProcessId, ParentProcessId)
    $result = [System.Collections.Generic.List[int]]::new()
    $queue = [System.Collections.Generic.Queue[int]]::new()
    $queue.Enqueue($RootProcessId)
    while ($queue.Count -gt 0) {
        $parent = $queue.Dequeue()
        foreach ($candidate in $processes) {
            if ([int]$candidate.ParentProcessId -eq $parent) {
                $child = [int]$candidate.ProcessId
                $result.Add($child)
                $queue.Enqueue($child)
            }
        }
    }
    return @($result)
}

function Stop-OwnedProcessTree {
    param([Parameter(Mandatory = $true)][int]$RootProcessId)
    $descendants = @(Get-DescendantProcessIds -RootProcessId $RootProcessId)
    [array]::Reverse($descendants)
    foreach ($processId in $descendants) {
        Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
    }
    Stop-Process -Id $RootProcessId -Force -ErrorAction SilentlyContinue
}

function Get-ExactHeavyProcesses {
    return @(
        Get-Process -ErrorAction SilentlyContinue |
            Where-Object { $ExactHeavyNames -contains $_.ProcessName } |
            Select-Object Id, ProcessName, StartTime
    )
}

function Wait-ForZeroHeavyProcesses {
    param([ValidateRange(1, 60)][int]$TimeoutSeconds = 30)
    $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
    do {
        $active = @(Get-ExactHeavyProcesses)
        if ($active.Count -eq 0) {
            return @()
        }
        Start-Sleep -Seconds 1
    } while ([DateTime]::UtcNow -lt $deadline)
    return @(Get-ExactHeavyProcesses)
}

function Get-LockedPackageSnapshot {
    $snapshot = [ordered]@{}
    foreach ($property in $Contract.immutable_packages.PSObject.Properties) {
        $path = Join-Path $ProjectRoot $property.Value.file
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
            throw "Missing immutable package: $path"
        }
        $actual = Get-Sha256 -Path $path
        if ($actual -ne $property.Value.sha256) {
            throw "Immutable package hash failed: $path"
        }
        $snapshot[$property.Name] = $actual
    }
    return $snapshot
}

function Get-LockedPackageSnapshotSafe {
    try {
        return [ordered]@{
            hashes = Get-LockedPackageSnapshot
            error = $null
        }
    }
    catch {
        return [ordered]@{
            hashes = $null
            error = $_.Exception.Message
        }
    }
}

function Assert-PredecessorEvidence {
    foreach ($property in $Contract.immutable_predecessor_evidence.PSObject.Properties) {
        $path = Join-Path $ProjectRoot $property.Value.file
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
            throw "Missing predecessor evidence: $path"
        }
        if ((Get-Sha256 -Path $path) -ne $property.Value.sha256) {
            throw "Predecessor evidence hash failed: $path"
        }
    }
    $failure = Get-Content -LiteralPath (
        Join-Path $ProjectRoot $Contract.accepted_capture_evidence.hash_manifest
    ) -Raw | ConvertFrom-Json
    $captureRecords = @($failure.captures.files)
    if ($captureRecords.Count -ne 17) {
        throw "Accepted predecessor capture count is not exact 17"
    }
    foreach ($record in $captureRecords) {
        if (
            -not (Test-Path -LiteralPath $record.path -PathType Leaf) -or
            (Get-Sha256 -Path $record.path) -ne $record.sha256
        ) {
            throw "Accepted predecessor capture hash failed: $($record.path)"
        }
    }
}

function Get-CsvFiles {
    return @(
        foreach ($root in $CsvRoots) {
            Get-ChildItem -LiteralPath $root -File -Recurse -ErrorAction SilentlyContinue |
                Where-Object { $_.Extension -in @(".csv", ".gz") } |
                Select-Object -ExpandProperty FullName
        }
    )
}

function Get-NewCsv {
    param(
        [Parameter(Mandatory = $true)][string[]]$Before,
        [Parameter(Mandatory = $true)][DateTime]$StartedAt
    )
    $beforeSet = [System.Collections.Generic.HashSet[string]]::new(
        [System.StringComparer]::OrdinalIgnoreCase
    )
    foreach ($path in $Before) {
        [void]$beforeSet.Add($path)
    }
    $candidate = @(
        foreach ($root in $CsvRoots) {
            Get-ChildItem -LiteralPath $root -File -Recurse -ErrorAction SilentlyContinue
        }
    ) |
        Where-Object {
            -not $beforeSet.Contains($_.FullName) -and
            $_.LastWriteTimeUtc -ge $StartedAt.AddSeconds(-2) -and
            $_.Length -gt 0 -and
            $_.Extension -in @(".csv", ".gz")
        } |
        Sort-Object LastWriteTimeUtc -Descending |
        Select-Object -First 1
    if ($null -eq $candidate) {
        throw "Measured profile did not produce a new nonempty CSV"
    }
    return $candidate.FullName
}

function Invoke-ProfileStage {
    param(
        [Parameter(Mandatory = $true)][string]$Mode,
        [Parameter(Mandatory = $true)][string]$Map,
        [Parameter(Mandatory = $true)][string]$Receipt
    )
    $name = "$($Mode)_profile_measured"
    $stdout = Join-Path $LogsRoot ($name + ".stdout.log")
    $stderr = Join-Path $LogsRoot ($name + ".stderr.log")
    $engineLog = Join-Path $LogsRoot ($name + ".engine.log")
    $arguments = @(
        $ProjectFile,
        $Map,
        "-game",
        "-windowed",
        "-ResX=1920",
        "-ResY=1080",
        "-d3d12",
        "-sm6",
        "-NoVSync",
        "-NoSplash",
        "-NoLoadingScreen",
        "-ExecCmds=r.SetRes 1920x1080w,r.ScreenPercentage 100,sg.ViewDistanceQuality 3,sg.ShadowQuality 3,sg.PostProcessQuality 3,sg.TextureQuality 3,sg.EffectsQuality 3,sg.FoliageQuality 3,BugItGo 22500 -9000 8500 -28 90 0",
        "-trace=cpu,gpu,frame,bookmark,loadtime,file,assetload",
        "-tracefile=$(Join-Path $ArtifactsRoot ($Mode + '.utrace'))",
        "-tracefiletrunc",
        "-traceautostart=1",
        "-csvCategories=Global",
        "-csvGpuStats",
        "-csvNamedEvents",
        "-SkyguardP45ProfileContractId=$($Contract.contract_id)",
        "-SkyguardP45ProfileRunId=recovery03_$Mode",
        "-SkyguardP45ProfileExpectedMap=$Map",
        "-SkyguardP45ProfileReceipt=$Receipt",
        "-SkyguardP45ProfileWarmupSeconds=30",
        "-SkyguardP45ProfileMeasuredSeconds=60",
        "-abslog=$engineLog"
    )
    $argumentLine = (
        $arguments |
            ForEach-Object { ConvertTo-Argument $_ }
    ) -join " "
    $started = [DateTime]::UtcNow
    $process = Start-Process -FilePath $EditorExe `
        -ArgumentList $argumentLine `
        -WorkingDirectory $ProjectRoot `
        -RedirectStandardOutput $stdout `
        -RedirectStandardError $stderr `
        -PassThru -WindowStyle Hidden
    $deadline = $started.AddSeconds($ProfileTimeoutSeconds)
    $peakWorkingSet = 0L
    while (-not $process.HasExited -and [DateTime]::UtcNow -lt $deadline) {
        $ids = @($process.Id) + @(Get-DescendantProcessIds -RootProcessId $process.Id)
        foreach ($processId in $ids) {
            $sample = Get-Process -Id $processId -ErrorAction SilentlyContinue
            if ($null -ne $sample) {
                $peakWorkingSet = [Math]::Max(
                    $peakWorkingSet,
                    [int64]$sample.WorkingSet64
                )
            }
        }
        Start-Sleep -Milliseconds 500
        $process.Refresh()
    }
    $timedOut = -not $process.HasExited
    if ($timedOut) {
        Stop-OwnedProcessTree -RootProcessId $process.Id
    }
    $process.WaitForExit()
    $combined = @($stdout, $stderr, $engineLog) |
        Where-Object { Test-Path -LiteralPath $_ -PathType Leaf } |
        ForEach-Object { Get-Content -LiteralPath $_ -Raw }
    $criticalMatches = @(
        foreach ($pattern in @(
            "Fatal error",
            "Assertion failed",
            "GPU Crash",
            "DXGI_ERROR_DEVICE_",
            "Out of video memory",
            "LogPython: Error",
            "Traceback \(most recent call last\)"
        )) {
            if (($combined -join "`n") -match $pattern) {
                $pattern
            }
        }
    )
    $lock = Get-LockedPackageSnapshotSafe
    return [ordered]@{
        name = $name
        command_line = "$EditorExe $argumentLine"
        pid = $process.Id
        started_at_utc = $started.ToString("o")
        finished_at_utc = [DateTime]::UtcNow.ToString("o")
        timeout_seconds = $ProfileTimeoutSeconds
        timed_out = $timedOut
        process_exit_observed = [bool]$process.HasExited
        exit_code = if ($timedOut) { $null } else { [int]$process.ExitCode }
        peak_working_set_mib = [Math]::Round($peakWorkingSet / 1MB, 3)
        stdout = $stdout
        stderr = $stderr
        engine_log = $engineLog
        critical_log_signatures = $criticalMatches
        injected_module_candidates = @()
        immutable_package_hashes_after = $lock.hashes
        immutable_package_lock_error = $lock.error
    }
}

function Assert-StagePassed {
    param([Parameter(Mandatory = $true)]$Stage)
    if ($Stage.timed_out) {
        throw "Stage timed out: $($Stage.name)"
    }
    if ($Stage.exit_code -ne 0) {
        throw "Stage exit code failed: $($Stage.name)=$($Stage.exit_code)"
    }
    if (@($Stage.critical_log_signatures).Count -ne 0) {
        throw "Critical log signature in stage: $($Stage.name)"
    }
    if ($null -ne $Stage.immutable_package_lock_error) {
        throw "Immutable package lock failed after stage: $($Stage.name)"
    }
}

foreach ($required in @(
    $ProjectFile,
    $EditorExe,
    $CompiledModule,
    $GateVerifier,
    $RenderAcceptance
)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
        throw "Required recovery03 file missing: $required"
    }
}
if ($Contract.status -ne "OFFLINE_RECOVERY03_DESIGN_READY_PENDING_AUTHORIZATION") {
    throw "Recovery03 contract is not in the reviewed offline-ready state"
}
if (Test-Path -LiteralPath $RecoveryRoot) {
    throw "Recovery03 root already exists; refuse duplicate or overwrite"
}
if (@(Get-ExactHeavyProcesses).Count -ne 0) {
    throw "Exclusive heavy lane is not free"
}
foreach ($property in $Contract.cpp_fix.PSObject.Properties) {
    if ($property.Name -notin @("header", "source")) {
        continue
    }
    $path = Join-Path $ProjectRoot $property.Value.file
    if ((Get-Sha256 -Path $path) -ne $property.Value.sha256) {
        throw "Recovery03 C++ fix source hash failed: $path"
    }
    if ((Get-Item -LiteralPath $CompiledModule).LastWriteTimeUtc -lt (Get-Item -LiteralPath $path).LastWriteTimeUtc) {
        throw "Recovery03 C++ fix has not been compiled"
    }
}

Assert-PredecessorEvidence
$initialPackageHashes = Get-LockedPackageSnapshot
New-Item -ItemType Directory -Force -Path $LogsRoot, $ArtifactsRoot | Out-Null

$manifest = [ordered]@{
    schema = "skyguard.phase4.m01-landscape-visible-recovery-supervisor.v1"
    recovery_id = $Contract.recovery_id
    contract_id = $Contract.contract_id
    predecessor_recovery_id = $Contract.fault_boundary.predecessor_recovery
    created_at_utc = [DateTime]::UtcNow.ToString("o")
    baseline_map = $BaselineMap
    candidate_map = $CandidateMap
    baseline_sha256_before = $initialPackageHashes.baseline_map
    baseline_sha256_after = $null
    candidate_sha256_before = $initialPackageHashes.candidate_map
    candidate_sha256_after = $null
    candidate_material_sha256_before = $initialPackageHashes.candidate_material
    candidate_material_sha256_after = $null
    initial_package_hashes = $initialPackageHashes
    controls = [ordered]@{
        authoring_forbidden = $true
        render_state_verifier_forbidden = $true
        capture_forbidden = $true
        active_rhi_required = "D3D12|SM6"
        warmup_seconds = 30
        csv_start_activation_timeout_seconds = 5
        measured_seconds = 60
        boot_csv_capture_forbidden = $true
        world_or_package_save_allowed = $false
        pcg_generation_allowed = $false
        network_download_allowed = $false
        automatic_retry_allowed = $false
        promotion_allowed = $false
    }
    stages = @()
    artifacts = [ordered]@{
        editor_acceptance = $RenderAcceptance
        baseline_capture_root = $BaselineCaptureRoot
        candidate_capture_root = $CandidateCaptureRoot
        baseline_csv = $null
        candidate_csv = $null
        baseline_profile_receipt = Join-Path $ArtifactsRoot "baseline_profile_receipt.json"
        candidate_profile_receipt = Join-Path $ArtifactsRoot "candidate_profile_receipt.json"
    }
    final_package_hashes = $null
    terminal_state = "RUNNING"
    errors = @()
}
Save-Json -Value $manifest -Path $ManifestPath

try {
    foreach ($profile in @(
        [ordered]@{
            mode = "baseline"
            map = $BaselineMap
            receipt = $manifest.artifacts.baseline_profile_receipt
        },
        [ordered]@{
            mode = "candidate"
            map = $CandidateMap
            receipt = $manifest.artifacts.candidate_profile_receipt
        }
    )) {
        $before = @(Get-CsvFiles)
        $started = [DateTime]::UtcNow
        $stage = Invoke-ProfileStage `
            -Mode $profile.mode `
            -Map $profile.map `
            -Receipt $profile.receipt
        $manifest.stages += $stage
        Save-Json -Value $manifest -Path $ManifestPath
        Assert-StagePassed -Stage $stage
        $receipt = Get-Content -LiteralPath $profile.receipt -Raw | ConvertFrom-Json
        if (
            $receipt.gate -ne "PASS" -or
            $receipt.rhi -notlike "*D3D12*" -or
            $receipt.feature_level -ne "SM6" -or
            $receipt.same_process_warmup_and_measurement -ne $true -or
            $receipt.startup_frames_excluded -ne $true -or
            [double]$receipt.warmup_seconds -ne 30 -or
            [double]$receipt.csv_start_activation_timeout_seconds -ne 5 -or
            [double]$receipt.measured_seconds -ne 60
        ) {
            throw "$($profile.mode) recovery03 profile receipt failed"
        }
        $manifest.artifacts["$($profile.mode)_csv"] = Get-NewCsv `
            -Before $before `
            -StartedAt $started
        Save-Json -Value $manifest -Path $ManifestPath
    }

    $finalLock = Get-LockedPackageSnapshotSafe
    if ($null -ne $finalLock.error) {
        throw $finalLock.error
    }
    $manifest.final_package_hashes = $finalLock.hashes
    $manifest.baseline_sha256_after = $finalLock.hashes.baseline_map
    $manifest.candidate_sha256_after = $finalLock.hashes.candidate_map
    $manifest.candidate_material_sha256_after = (
        $finalLock.hashes.candidate_material
    )
    $manifest.terminal_state = "EVIDENCE_CAPTURED_PENDING_GATE"
    Save-Json -Value $manifest -Path $ManifestPath

    $stdout = Join-Path $LogsRoot "verify_recovery03_visible_gpu_gate.stdout.log"
    $stderr = Join-Path $LogsRoot "verify_recovery03_visible_gpu_gate.stderr.log"
    $gateArgs = @(
        $GateVerifier,
        "--manifest",
        $ManifestPath,
        "--output",
        $GatePath,
        "--latest-output",
        $LatestGate
    )
    $gateArgumentLine = (
        $gateArgs |
            ForEach-Object { ConvertTo-Argument $_ }
    ) -join " "
    $gateStarted = [DateTime]::UtcNow
    $gateProcess = Start-Process -FilePath "python" `
        -ArgumentList $gateArgumentLine `
        -WorkingDirectory $ProjectRoot `
        -RedirectStandardOutput $stdout `
        -RedirectStandardError $stderr `
        -PassThru -WindowStyle Hidden -Wait
    $gateLock = Get-LockedPackageSnapshotSafe
    $gateStage = [ordered]@{
        name = "verify_recovery03_visible_gpu_gate"
        command_line = "python $gateArgumentLine"
        pid = $gateProcess.Id
        started_at_utc = $gateStarted.ToString("o")
        finished_at_utc = [DateTime]::UtcNow.ToString("o")
        timed_out = $false
        process_exit_observed = [bool]$gateProcess.HasExited
        exit_code = [int]$gateProcess.ExitCode
        stdout = $stdout
        stderr = $stderr
        critical_log_signatures = @()
        injected_module_candidates = @()
        immutable_package_hashes_after = $gateLock.hashes
        immutable_package_lock_error = $gateLock.error
    }
    $manifest.stages += $gateStage
    Save-Json -Value $manifest -Path $ManifestPath
    if ($gateProcess.ExitCode -notin @(0, 2)) {
        throw "Recovery03 visible/GPU verifier process failed"
    }
    if ($null -ne $gateLock.error) {
        throw "Recovery03 final package lock failed"
    }
    $gateReport = Get-Content -LiteralPath $GatePath -Raw | ConvertFrom-Json
    if ($gateReport.technical_gate -ne "PASS") {
        throw "Recovery03 technical visible/GPU gate failed"
    }
    if ($gateReport.gate -eq "PASS") {
        $manifest.terminal_state = "GATE_COMPLETE"
    }
    elseif ($gateReport.gate -eq "INCOMPLETE_HUMAN_REVIEW") {
        $manifest.terminal_state = (
            "TECHNICAL_GATE_PASS_PENDING_HUMAN_REVIEW"
        )
    }
    else {
        throw "Unexpected recovery03 gate state: $($gateReport.gate)"
    }
}
catch {
    $manifest.errors += $_.Exception.Message
    $manifest.terminal_state = "FAILED"
    throw
}
finally {
    $finalLock = Get-LockedPackageSnapshotSafe
    $manifest.final_package_hashes = $finalLock.hashes
    if ($null -ne $finalLock.error) {
        $manifest.errors += $finalLock.error
        $manifest.terminal_state = "FAILED"
    }
    else {
        $manifest.baseline_sha256_after = $finalLock.hashes.baseline_map
        $manifest.candidate_sha256_after = $finalLock.hashes.candidate_map
        $manifest.candidate_material_sha256_after = (
            $finalLock.hashes.candidate_material
        )
    }
    Save-Json -Value $manifest -Path $ManifestPath
    if (@(Wait-ForZeroHeavyProcesses -TimeoutSeconds 30).Count -ne 0) {
        throw "Heavy processes remain after recovery03 supervisor"
    }
}

