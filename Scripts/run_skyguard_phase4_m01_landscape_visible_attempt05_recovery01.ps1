[CmdletBinding()]
param(
    [string]$ProjectRoot = "D:\Skyguard52",
    [string]$UnrealRoot = "D:\UE_5.8",
    [ValidateRange(60, 300)]
    [int]$EditorTimeoutSeconds = 240,
    [ValidateRange(100, 240)]
    [int]$ProfileTimeoutSeconds = 150
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$RecoveryContractPath = Join-Path $ProjectRoot "Docs\AAA_Review\PHASE4_M01_LANDSCAPE_VISIBLE_ATTEMPT05_RECOVERY_CONTRACT_01.json"
$RecoveryContract = Get-Content -LiteralPath $RecoveryContractPath -Raw | ConvertFrom-Json
$ProjectFile = Join-Path $ProjectRoot "Skyguard52.uproject"
$EditorExe = Join-Path $UnrealRoot "Engine\Binaries\Win64\UnrealEditor.exe"
$RenderVerifier = Join-Path $ProjectRoot "Scripts\verify_skyguard_phase4_m01_landscape_render_state_attempt05_recovery01.py"
$CaptureScript = Join-Path $ProjectRoot "Scripts\capture_skyguard_phase4_m01_landscape_visible_review_attempt05.py"
$GateVerifier = Join-Path $ProjectRoot "Scripts\verify_skyguard_phase4_m01_landscape_visible_gpu_gate_attempt05.py"
$RenderAcceptance = Join-Path $ProjectRoot "Saved\Reports\PHASE4_M01_LANDSCAPE_RENDER_STATE_ACCEPTANCE_ATTEMPT05_RECOVERY01.json"
$LatestGate = Join-Path $ProjectRoot "Saved\Reports\PHASE4_M01_LANDSCAPE_VISIBLE_GPU_REVIEW_ATTEMPT05_LATEST.json"
$CsvRoot = Join-Path $ProjectRoot "Saved\Profiling\CSV"
$RecoveryRoot = Join-Path $ProjectRoot $RecoveryContract.recovery_execution.recovery_root
$LogsRoot = Join-Path $RecoveryRoot "logs"
$ArtifactsRoot = Join-Path $RecoveryRoot "artifacts"
$BaselineCaptureRoot = Join-Path $ArtifactsRoot "captures\baseline"
$CandidateCaptureRoot = Join-Path $ArtifactsRoot "captures\candidate"
$ManifestPath = Join-Path $RecoveryRoot "recovery_manifest.json"
$GatePath = Join-Path $RecoveryRoot "gate_report.json"
$BaselineMap = $RecoveryContract.immutable_packages.baseline_map.asset
$CandidateMap = $RecoveryContract.immutable_packages.candidate_map.asset
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
    $resolved = [System.IO.Path]::GetFullPath($Path)
    $stream = [System.IO.File]::Open(
        $resolved,
        [System.IO.FileMode]::Open,
        [System.IO.FileAccess]::Read,
        [System.IO.FileShare]::Read
    )
    $algorithm = [System.Security.Cryptography.SHA256]::Create()
    try {
        $digest = $algorithm.ComputeHash($stream)
        return (
            [System.BitConverter]::ToString($digest).Replace("-", "")
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
    foreach ($property in $RecoveryContract.immutable_packages.PSObject.Properties) {
        $spec = $property.Value
        $path = Join-Path $ProjectRoot $spec.file
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
            throw "Missing immutable package: $path"
        }
        $actual = Get-Sha256 -Path $path
        if ($actual -ne $spec.sha256) {
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
    foreach ($property in $RecoveryContract.immutable_predecessor_evidence.PSObject.Properties) {
        $spec = $property.Value
        $path = Join-Path $ProjectRoot $spec.file
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
            throw "Missing predecessor evidence: $path"
        }
        if ((Get-Sha256 -Path $path) -ne $spec.sha256) {
            throw "Predecessor evidence hash failed: $path"
        }
    }
}

function Invoke-BoundedStage {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [Parameter(Mandatory = $true)][int]$TimeoutSeconds
    )
    $stdout = Join-Path $LogsRoot ($Name + ".stdout.log")
    $stderr = Join-Path $LogsRoot ($Name + ".stderr.log")
    $engineLog = Join-Path $LogsRoot ($Name + ".engine.log")
    $argumentsWithLog = @($Arguments) + @("-abslog=$engineLog")
    $argumentLine = (
        $argumentsWithLog |
            ForEach-Object { ConvertTo-Argument $_ }
    ) -join " "
    $started = [DateTime]::UtcNow
    $process = Start-Process -FilePath $EditorExe `
        -ArgumentList $argumentLine `
        -WorkingDirectory $ProjectRoot `
        -RedirectStandardOutput $stdout `
        -RedirectStandardError $stderr `
        -PassThru -WindowStyle Hidden
    $deadline = $started.AddSeconds($TimeoutSeconds)
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
    $exitCode = if ($timedOut) { $null } else { [int]$process.ExitCode }
    $combined = @($stdout, $stderr, $engineLog) |
        Where-Object { Test-Path -LiteralPath $_ -PathType Leaf } |
        ForEach-Object { Get-Content -LiteralPath $_ -Raw }
    $criticalPatterns = @(
        "Fatal error",
        "Assertion failed",
        "GPU Crash",
        "DXGI_ERROR_DEVICE_",
        "Out of video memory",
        "LogPython: Error",
        "Traceback \(most recent call last\)"
    )
    $criticalMatches = @(
        foreach ($pattern in $criticalPatterns) {
            if (($combined -join "`n") -match $pattern) {
                $pattern
            }
        }
    )
    $lockResult = Get-LockedPackageSnapshotSafe
    return [ordered]@{
        name = $Name
        command_line = "$EditorExe $argumentLine"
        pid = $process.Id
        started_at_utc = $started.ToString("o")
        finished_at_utc = [DateTime]::UtcNow.ToString("o")
        timeout_seconds = $TimeoutSeconds
        timed_out = $timedOut
        process_exit_observed = [bool]$process.HasExited
        exit_code = $exitCode
        peak_working_set_mib = [Math]::Round($peakWorkingSet / 1MB, 3)
        stdout = $stdout
        stderr = $stderr
        engine_log = $engineLog
        critical_log_signatures = $criticalMatches
        injected_module_candidates = @()
        immutable_package_hashes_after = $lockResult.hashes
        immutable_package_lock_error = $lockResult.error
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
        throw "Immutable package lock failed after stage $($Stage.name): $($Stage.immutable_package_lock_error)"
    }
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
    $candidate = Get-ChildItem -LiteralPath $CsvRoot -File -Recurse -ErrorAction SilentlyContinue |
        Where-Object {
            -not $beforeSet.Contains($_.FullName) -and
            $_.LastWriteTimeUtc -ge $StartedAt.AddSeconds(-2) -and
            $_.Extension -in @(".csv", ".gz")
        } |
        Sort-Object LastWriteTimeUtc -Descending |
        Select-Object -First 1
    if ($null -eq $candidate) {
        throw "Measured profile did not produce a new CSV"
    }
    return $candidate.FullName
}

foreach ($required in @(
    $ProjectFile,
    $EditorExe,
    $RenderVerifier,
    $CaptureScript,
    $GateVerifier
)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
        throw "Required recovery file missing: $required"
    }
}
if ($RecoveryContract.status -ne "OFFLINE_RECOVERY_DESIGN_READY_NOT_AUTHORIZED_FOR_UNREAL_EXECUTION") {
    throw "Recovery contract status is not the reviewed offline-ready state"
}
if (Test-Path -LiteralPath $RecoveryRoot) {
    throw "Recovery root already exists; refuse duplicate or overwrite"
}
if (Test-Path -LiteralPath $RenderAcceptance) {
    throw "Recovery render-state receipt already exists; refuse overwrite"
}
if (@(Get-ExactHeavyProcesses).Count -ne 0) {
    throw "Exclusive heavy lane is not free"
}

Assert-PredecessorEvidence
$initialPackageHashes = Get-LockedPackageSnapshot
New-Item -ItemType Directory -Force -Path $LogsRoot, $ArtifactsRoot | Out-Null

$manifest = [ordered]@{
    schema = "skyguard.phase4.m01-landscape-visible-recovery-supervisor.v1"
    recovery_id = $RecoveryContract.recovery_id
    contract_id = $RecoveryContract.contract_id
    predecessor_attempt_id = $RecoveryContract.fault_boundary.attempt_id
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
        authoring_stage_forbidden = $true
        nullrhi_forbidden = $true
        first_unreal_stage = "verify_candidate_render_state_d3d12_sm6"
        active_rhi_required = "D3D12|SM6"
        sequential_processes_only = $true
        warmup_seconds = 30
        measured_seconds = 60
        boot_csv_capture_forbidden = $true
        pcg_generation_allowed = $false
        world_or_package_save_allowed = $false
        network_download_allowed = $false
        promotion_allowed = $false
    }
    stages = @()
    artifacts = [ordered]@{
        render_state_acceptance = $RenderAcceptance
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
    $stage = Invoke-BoundedStage `
        -Name "verify_candidate_render_state_d3d12_sm6" `
        -Arguments @(
            $ProjectFile,
            $CandidateMap,
            "-ExecutePythonScript=$RenderVerifier",
            "-ScriptErrorsAreFatal",
            "-unattended",
            "-nop4",
            "-NoSplash",
            "-RenderOffscreen",
            "-windowed",
            "-ResX=1920",
            "-ResY=1080",
            "-d3d12",
            "-sm6",
            "-NoVSync"
        ) `
        -TimeoutSeconds $EditorTimeoutSeconds
    $manifest.stages += $stage
    Save-Json -Value $manifest -Path $ManifestPath
    Assert-StagePassed -Stage $stage

    $renderReceipt = Get-Content -LiteralPath $RenderAcceptance -Raw | ConvertFrom-Json
    if (
        $renderReceipt.gate -ne "PASS" -or
        $renderReceipt.rhi_validation -ne "D3D12|SM6" -or
        [int]$renderReceipt.landscape_visible_audit.visible_component_count -ne 16 -or
        [int]$renderReceipt.landscape_visible_audit.registered_component_count -ne 16 -or
        [int]$renderReceipt.landscape_visible_audit.render_state_created_component_count -ne 16 -or
        [int]$renderReceipt.landscape_visible_audit.contract_camera_frustum_intersection_count -ne 5
    ) {
        throw "Normal-editor render-state acceptance did not pass exact locks"
    }

    foreach ($spec in @(
        [ordered]@{ mode = "baseline"; map = $BaselineMap; root = $BaselineCaptureRoot },
        [ordered]@{ mode = "candidate"; map = $CandidateMap; root = $CandidateCaptureRoot }
    )) {
        $stage = Invoke-BoundedStage `
            -Name "$($spec.mode)_capture" `
            -Arguments @(
                $ProjectFile,
                $spec.map,
                "-ExecutePythonScript=$CaptureScript",
                "-ScriptErrorsAreFatal",
                "-SkyguardReviewMode=$($spec.mode)",
                "-SkyguardReviewMap=$($spec.map)",
                "-SkyguardReviewOutput=$($spec.root)",
                "-unattended",
                "-nop4",
                "-NoSplash",
                "-RenderOffscreen",
                "-windowed",
                "-ResX=1920",
                "-ResY=1080",
                "-d3d12",
                "-sm6",
                "-NoVSync"
            ) `
            -TimeoutSeconds $EditorTimeoutSeconds
        $manifest.stages += $stage
        Save-Json -Value $manifest -Path $ManifestPath
        Assert-StagePassed -Stage $stage
    }

    $expectedCaptures = @()
    foreach ($cameraId in @(
        "C01_ROUTE_WIDE",
        "C02_SHORE_APPROACH",
        "C03_SHORE_GRAZE",
        "C04_INLAND_CLOSE",
        "C05_COVERAGE_HIGH"
    )) {
        $expectedCaptures += Join-Path $BaselineCaptureRoot "baseline_lit_$cameraId.png"
        $expectedCaptures += Join-Path $CandidateCaptureRoot "candidate_lit_$cameraId.png"
        $expectedCaptures += Join-Path $CandidateCaptureRoot "candidate_diagnostic_landscape_coverage_$cameraId.png"
    }
    $expectedCaptures += @(
        (Join-Path $CandidateCaptureRoot "candidate_diagnostic_component_boundary_C05.png"),
        (Join-Path $CandidateCaptureRoot "candidate_diagnostic_shader_complexity_C04.png")
    )
    $missingCaptures = @(
        $expectedCaptures |
            Where-Object {
                -not (Test-Path -LiteralPath $_ -PathType Leaf) -or
                (Get-Item -LiteralPath $_).Length -eq 0
            }
    )
    if ($missingCaptures.Count -ne 0) {
        throw "Governed capture outputs missing: $($missingCaptures -join ', ')"
    }

    foreach ($profile in @(
        [ordered]@{ mode = "baseline"; map = $BaselineMap },
        [ordered]@{ mode = "candidate"; map = $CandidateMap }
    )) {
        $before = @(
            Get-ChildItem -LiteralPath $CsvRoot -File -Recurse -ErrorAction SilentlyContinue |
                Select-Object -ExpandProperty FullName
        )
        $profileStarted = [DateTime]::UtcNow
        $receiptKey = "$($profile.mode)_profile_receipt"
        $runId = "recovery01_$($profile.mode)"
        $stage = Invoke-BoundedStage `
            -Name "$($profile.mode)_profile_measured" `
            -Arguments @(
                $ProjectFile,
                $profile.map,
                "-game",
                "-windowed",
                "-ResX=1920",
                "-ResY=1080",
                "-d3d12",
                "-sm6",
                "-NoVSync",
                "-NoSplash",
                "-NoLoadingScreen",
                "-benchmark",
                "-benchmarkseconds=100",
                "-fps=60",
                "-ExecCmds=r.SetRes 1920x1080w,r.ScreenPercentage 100,sg.ViewDistanceQuality 3,sg.ShadowQuality 3,sg.PostProcessQuality 3,sg.TextureQuality 3,sg.EffectsQuality 3,sg.FoliageQuality 3,BugItGo 22500 -9000 8500 -28 90 0",
                "-trace=cpu,gpu,frame,bookmark,loadtime,file,assetload",
                "-tracefile=$(Join-Path $ArtifactsRoot ($profile.mode + '.utrace'))",
                "-tracefiletrunc",
                "-traceautostart=1",
                "-csvCategories=Global",
                "-csvGpuStats",
                "-csvNamedEvents",
                "-SkyguardP45ProfileContractId=$($RecoveryContract.contract_id)",
                "-SkyguardP45ProfileRunId=$runId",
                "-SkyguardP45ProfileExpectedMap=$($profile.map)",
                "-SkyguardP45ProfileReceipt=$($manifest.artifacts[$receiptKey])",
                "-SkyguardP45ProfileWarmupSeconds=30",
                "-SkyguardP45ProfileMeasuredSeconds=60"
            ) `
            -TimeoutSeconds $ProfileTimeoutSeconds
        $manifest.stages += $stage
        Save-Json -Value $manifest -Path $ManifestPath
        Assert-StagePassed -Stage $stage
        $manifest.artifacts["$($profile.mode)_csv"] = Get-NewCsv `
            -Before $before -StartedAt $profileStarted
        $profileReceipt = Get-Content `
            -LiteralPath $manifest.artifacts[$receiptKey] `
            -Raw | ConvertFrom-Json
        if ($profileReceipt.gate -ne "PASS") {
            throw "$($profile.mode) same-process profile receipt failed"
        }
        Save-Json -Value $manifest -Path $ManifestPath
    }

    $manifest.final_package_hashes = Get-LockedPackageSnapshot
    $manifest.baseline_sha256_after = $manifest.final_package_hashes.baseline_map
    $manifest.candidate_sha256_after = $manifest.final_package_hashes.candidate_map
    $manifest.candidate_material_sha256_after = (
        $manifest.final_package_hashes.candidate_material
    )
    $manifest.terminal_state = "EVIDENCE_CAPTURED_PENDING_GATE"
    Save-Json -Value $manifest -Path $ManifestPath

    $stdout = Join-Path $LogsRoot "verify_recovery_visible_gpu_gate.stdout.log"
    $stderr = Join-Path $LogsRoot "verify_recovery_visible_gpu_gate.stderr.log"
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
    $gateLockResult = Get-LockedPackageSnapshotSafe
    $gateStage = [ordered]@{
        name = "verify_recovery_visible_gpu_gate"
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
        immutable_package_hashes_after = $gateLockResult.hashes
        immutable_package_lock_error = $gateLockResult.error
    }
    $manifest.stages += $gateStage
    Save-Json -Value $manifest -Path $ManifestPath
    if ($gateProcess.ExitCode -notin @(0, 2)) {
        throw "Recovery visible/GPU verifier process failed"
    }
    if ($null -ne $gateStage.immutable_package_lock_error) {
        throw "Immutable package lock failed after final recovery gate"
    }
    $gateReport = Get-Content -LiteralPath $GatePath -Raw | ConvertFrom-Json
    if ($gateReport.technical_gate -ne "PASS") {
        throw "Recovery technical visible/GPU gate failed"
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
        throw "Unexpected recovery gate state: $($gateReport.gate)"
    }
}
catch {
    $manifest.errors += $_.Exception.Message
    $manifest.terminal_state = "FAILED"
    throw
}
finally {
    $finalLockResult = Get-LockedPackageSnapshotSafe
    $manifest.final_package_hashes = $finalLockResult.hashes
    if ($null -ne $finalLockResult.error) {
        $manifest.errors += $finalLockResult.error
        $manifest.terminal_state = "FAILED"
    }
    else {
        $manifest.baseline_sha256_after = (
            $manifest.final_package_hashes.baseline_map
        )
        $manifest.candidate_sha256_after = (
            $manifest.final_package_hashes.candidate_map
        )
        $manifest.candidate_material_sha256_after = (
            $manifest.final_package_hashes.candidate_material
        )
    }
    Save-Json -Value $manifest -Path $ManifestPath
    $remaining = @(Wait-ForZeroHeavyProcesses -TimeoutSeconds 30)
    if ($remaining.Count -ne 0) {
        throw "Heavy processes remain after recovery supervisor"
    }
}
