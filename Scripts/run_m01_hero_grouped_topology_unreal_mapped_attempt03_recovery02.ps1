[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][switch]$AuthorizeSingleRecovery02Run,
    [Parameter(Mandatory = $true)]
    [ValidatePattern("^[0-9a-fA-F]{64}$")]
    [string]$ExpectedExecutionContractSha256,
    [string]$ProjectRoot = "D:\Skyguard52",
    [string]$UnrealRoot = "D:\UE_5.8",
    [ValidateRange(300, 1800)][int]$TimeoutSeconds = 1200
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
if (-not $AuthorizeSingleRecovery02Run) {
    throw "Explicit -AuthorizeSingleRecovery02Run is required."
}

$ExecutionContractPath = Join-Path $ProjectRoot "Docs\AAA_Review\M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_RECOVERY02_EXECUTION_CONTRACT.json"
$RecoveryContractPath = Join-Path $ProjectRoot "Docs\AAA_Review\M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_RECOVERY02_CONTRACT.json"
$ProjectFile = Join-Path $ProjectRoot "Skyguard52.uproject"
$EditorExe = Join-Path $UnrealRoot "Engine\Binaries\Win64\UnrealEditor.exe"
$Python = (Get-Command python -ErrorAction Stop).Source
$HeavyNames = @(
    "UnrealEditor", "UnrealEditor-Cmd", "UnrealBuildTool", "AutomationTool",
    "ShaderCompileWorker", "UbaAgent", "UbaServer", "CrashReportClient",
    "Skyguard52", "blender"
)

function Get-Sha256 {
    param([Parameter(Mandatory = $true)][string]$Path)
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Quote-Argument {
    param([Parameter(Mandatory = $true)][string]$Value)
    if ($Value -notmatch '[\s"]') { return $Value }
    return '"' + ($Value -replace '(\\*)"', '$1$1\"' -replace '(\\+)$', '$1$1') + '"'
}

function Join-Arguments {
    param([Parameter(Mandatory = $true)][string[]]$Values)
    return (($Values | ForEach-Object { Quote-Argument $_ }) -join " ")
}

function Get-DescendantProcessIds {
    param([Parameter(Mandatory = $true)][int]$RootProcessId)
    $all = @(Get-CimInstance Win32_Process |
        Select-Object ProcessId, ParentProcessId)
    $queue = [System.Collections.Generic.Queue[int]]::new()
    $found = [System.Collections.Generic.List[int]]::new()
    $queue.Enqueue($RootProcessId)
    while ($queue.Count -gt 0) {
        $parent = $queue.Dequeue()
        foreach ($candidate in $all) {
            if ([int]$candidate.ParentProcessId -eq $parent) {
                $child = [int]$candidate.ProcessId
                $found.Add($child)
                $queue.Enqueue($child)
            }
        }
    }
    return @($found)
}

function Stop-OwnedProcessTree {
    param([Parameter(Mandatory = $true)][int]$RootProcessId)
    $descendants = @(Get-DescendantProcessIds -RootProcessId $RootProcessId)
    [array]::Reverse($descendants)
    foreach ($ownedProcessId in $descendants) {
        Stop-Process -Id $ownedProcessId -Force -ErrorAction SilentlyContinue
    }
    Stop-Process -Id $RootProcessId -Force -ErrorAction SilentlyContinue
    return @($descendants)
}

function Get-TreeHashMap {
    param(
        [Parameter(Mandatory = $true)][string]$RootPath,
        [string[]]$Suffixes = @()
    )
    $result = [ordered]@{}
    if (-not (Test-Path -LiteralPath $RootPath -PathType Container)) {
        return $result
    }
    foreach ($file in @(Get-ChildItem -LiteralPath $RootPath -Recurse -File |
        Sort-Object FullName)) {
        if ($Suffixes.Count -gt 0 -and
            $Suffixes -notcontains $file.Extension.ToLowerInvariant()) {
            continue
        }
        $relative = $file.FullName.Substring($ProjectRoot.Length).
            TrimStart("\").Replace("\", "/")
        $result[$relative] = Get-Sha256 $file.FullName
    }
    return $result
}

function Invoke-Bounded {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [Parameter(Mandatory = $true)][string]$Stdout,
        [Parameter(Mandatory = $true)][string]$Stderr,
        [Parameter(Mandatory = $true)][int]$BoundSeconds
    )
    $started = [DateTime]::UtcNow
    $process = Start-Process -FilePath $FilePath `
        -ArgumentList (Join-Arguments $Arguments) `
        -WorkingDirectory $ProjectRoot `
        -RedirectStandardOutput $Stdout -RedirectStandardError $Stderr `
        -PassThru -WindowStyle Hidden
    $deadline = $started.AddSeconds($BoundSeconds)
    $peak = 0L
    while (-not $process.HasExited -and [DateTime]::UtcNow -lt $deadline) {
        foreach ($sampleId in @($process.Id) + @(
            Get-DescendantProcessIds -RootProcessId $process.Id
        )) {
            $sample = Get-Process -Id $sampleId -ErrorAction SilentlyContinue
            if ($null -ne $sample) {
                $peak = [Math]::Max($peak, [int64]$sample.WorkingSet64)
            }
        }
        Start-Sleep -Milliseconds 500
        $process.Refresh()
    }
    $timedOut = -not $process.HasExited
    $terminated = if ($timedOut) {
        @(Stop-OwnedProcessTree -RootProcessId $process.Id)
    } else { @() }
    $process.WaitForExit()
    $process.Refresh()
    return [ordered]@{
        pid = $process.Id
        exit_code = if ($timedOut) { $null } else { [int]$process.ExitCode }
        timed_out = $timedOut
        terminated_descendant_pids = $terminated
        started_at_utc = $started.ToString("o")
        finished_at_utc = [DateTime]::UtcNow.ToString("o")
        peak_working_set_mib = [Math]::Round($peak / 1MB, 3)
        stdout = $Stdout
        stderr = $Stderr
    }
}

foreach ($required in @(
    $ExecutionContractPath, $RecoveryContractPath, $ProjectFile, $EditorExe
)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
        throw "Required Recovery02 input is missing: $required"
    }
}
$actualExecutionHash = Get-Sha256 $ExecutionContractPath
if ($actualExecutionHash -ne $ExpectedExecutionContractSha256.ToLowerInvariant()) {
    throw "Recovery02 execution contract hash mismatch; Unreal was not launched."
}
$execution = Get-Content -LiteralPath $ExecutionContractPath -Raw |
    ConvertFrom-Json
if ($execution.authorization.authorize_switch -ne "AuthorizeSingleRecovery02Run" -or
    $execution.promotion_allowed -ne $false -or
    $execution.p3_4_closed -ne $false) {
    throw "Recovery02 execution policy mismatch; Unreal was not launched."
}
foreach ($record in $execution.bound_files.PSObject.Properties.Value) {
    $path = Join-Path $ProjectRoot $record.path
    if (-not (Test-Path -LiteralPath $path -PathType Leaf) -or
        (Get-Item -LiteralPath $path).Length -ne [int64]$record.bytes -or
        (Get-Sha256 $path) -ne $record.sha256) {
        throw "Recovery02 bound-file mismatch: $path"
    }
}

$AttemptRoot = Join-Path $ProjectRoot $execution.outputs.attempt_root
$CaptureRoot = Join-Path $ProjectRoot $execution.outputs.capture_root
$SelectionRoot = Join-Path $ProjectRoot $execution.outputs.selection_root
$SupervisorReceipt = Join-Path $ProjectRoot $execution.outputs.supervisor_receipt
$PreflightSnapshot = Join-Path $AttemptRoot "preflight_snapshot.json"
$ExecutionAudit = Join-Path $AttemptRoot "execution_audit.json"
$CaptureScript = Join-Path $ProjectRoot $execution.bound_files.recovery_capture.path
$Selector = Join-Path $ProjectRoot $execution.bound_files.recovery_selector.path
$ExecutionAuditor = Join-Path $ProjectRoot $execution.bound_files.execution_auditor.path
$ReadinessAuditor = Join-Path $ProjectRoot $execution.bound_files.readiness_auditor.path
$ReviewMap = $execution.review_map
$ReviewMapPackage = Join-Path $ProjectRoot $execution.bound_files.review_map_package.path

if (Test-Path -LiteralPath $AttemptRoot) {
    throw "Immutable Recovery02 output already exists: $AttemptRoot"
}
if ((Get-Sha256 $ReviewMapPackage) -ne
    $execution.bound_files.review_map_package.sha256) {
    throw "Immutable review map changed; Unreal was not launched."
}
$heavy = @(Get-Process -ErrorAction SilentlyContinue |
    Where-Object { $HeavyNames -contains $_.ProcessName })
if ($heavy.Count -ne 0) {
    throw "Recovery02 lane requires zero heavy processes."
}
$os = Get-CimInstance Win32_OperatingSystem
$freePhysicalGiB = [Math]::Round(([double]$os.FreePhysicalMemory * 1KB) / 1GB, 3)
if ($freePhysicalGiB -lt [double]$execution.resource_preflight.minimum_free_physical_gib) {
    throw "Recovery02 lane has only $freePhysicalGiB GiB free RAM."
}
$readinessText = & $Python $ReadinessAuditor 2>&1
if ($LASTEXITCODE -ne 0 -or
    ($readinessText -join "`n") -notmatch
    "PASS_OFFLINE_READY_AWAITING_SEPARATE_RECOVERY02_AUTHORIZATION") {
    throw "Recovery02 offline readiness failed; Unreal was not launched."
}

$originalCandidate = Get-TreeHashMap `
    -RootPath (Join-Path $ProjectRoot "Content\Skyguard\Candidates\Mission01\HeroGroupedTopology_008") `
    -Suffixes @(".uasset", ".umap")
$attempt03Packages = Get-TreeHashMap `
    -RootPath (Join-Path $ProjectRoot "Content\Skyguard\Candidates\Mission01\HeroGroupedTopology_008_Attempt03") `
    -Suffixes @(".uasset", ".umap")
$runtimeMaps = Get-TreeHashMap `
    -RootPath (Join-Path $ProjectRoot "Content\Skyguard\Maps") `
    -Suffixes @(".uasset", ".umap")
$configFiles = Get-TreeHashMap -RootPath (Join-Path $ProjectRoot "Config")
if ($attempt03Packages.Count -ne 1) {
    throw "Recovery02 requires the one immutable Attempt03 review map."
}

New-Item -ItemType Directory -Path $AttemptRoot | Out-Null
($readinessText -join [Environment]::NewLine) |
    Set-Content -LiteralPath (Join-Path $AttemptRoot "offline_readiness.log") -Encoding UTF8
[ordered]@{
    schema = "skyguard.m01.hero-grouped-topology-attempt03-recovery02-preflight.v1"
    recorded_at_utc = [DateTime]::UtcNow.ToString("o")
    execution_contract_sha256 = $actualExecutionHash
    recovery_contract_sha256 = Get-Sha256 $RecoveryContractPath
    heavy_process_count = $heavy.Count
    free_physical_gib = $freePhysicalGiB
    original_candidate_packages = $originalCandidate
    attempt03_packages = $attempt03Packages
    runtime_map_packages = $runtimeMaps
    config_files = $configFiles
    promotion_allowed = $false
    p3_4_closed = $false
} | ConvertTo-Json -Depth 20 |
    Set-Content -LiteralPath $PreflightSnapshot -Encoding UTF8

$UnrealStdout = Join-Path $AttemptRoot "unreal.stdout.log"
$UnrealStderr = Join-Path $AttemptRoot "unreal.stderr.log"
$EngineLog = Join-Path $AttemptRoot "unreal.engine.log"
$SelectorStdout = Join-Path $AttemptRoot "selector.stdout.log"
$SelectorStderr = Join-Path $AttemptRoot "selector.stderr.log"
$AuditorStdout = Join-Path $AttemptRoot "auditor.stdout.log"
$AuditorStderr = Join-Path $AttemptRoot "auditor.stderr.log"
$unrealProcess = $null
$selectorProcess = $null
$auditorProcess = $null

try {
    $unrealProcess = Invoke-Bounded -FilePath $EditorExe -Arguments @(
        $ProjectFile,
        "-ExecutePythonScript=$CaptureScript",
        "-ScriptErrorsAreFatal",
        "-SkyguardAttempt03Recovery02Output=$CaptureRoot",
        "-SkyguardAttempt03Recovery02ReviewMap=$ReviewMap",
        "-unattended", "-nop4", "-NoSplash", "-RenderOffscreen", "-windowed",
        "-ResX=2048", "-ResY=2048", "-d3d12", "-sm6", "-NoVSync",
        "-stdout", "-FullStdOutLogOutput", "-abslog=$EngineLog",
        "-NoAssetRegistryCache",
        "-ExecCmds=r.ScreenPercentage 100,sg.ViewDistanceQuality 3,sg.ShadowQuality 3,sg.PostProcessQuality 3,sg.TextureQuality 3,sg.EffectsQuality 3"
    ) -Stdout $UnrealStdout -Stderr $UnrealStderr -BoundSeconds $TimeoutSeconds
    $combined = ""
    foreach ($log in @($UnrealStdout, $UnrealStderr, $EngineLog)) {
        if (Test-Path -LiteralPath $log -PathType Leaf) {
            $combined += "`n" + (Get-Content -LiteralPath $log -Raw)
        }
    }
    $criticalPattern = "Fatal error|LowLevelFatalError|Assertion failed|Ensure condition failed|GPU Crash|DXGI_ERROR_DEVICE_|Out of video memory|Ran out of memory|LogPython: Error|Traceback \(most recent call last\)"
    $rhiValidated = $combined -match "\[M01Grouped008Attempt03Capture\]\[RHI_VALIDATED\]\s+D3D12\|SM6"
    $capturePassed = $combined -match "PASS_RECOVERY02_SYNCHRONIZED_SWEEP_AWAITING_OFFLINE_GLOBAL_RIG_SELECTION"
    $criticalSignature = $combined -match $criticalPattern
    $PilotReceipt = Join-Path $CaptureRoot "pilot_receipt.json"
    $SweepManifest = Join-Path $CaptureRoot "capture_manifest.json"
    $pilotPngs = if (Test-Path -LiteralPath (Join-Path $CaptureRoot "pilot")) {
        @(Get-ChildItem -LiteralPath (Join-Path $CaptureRoot "pilot") -Filter "*.png" -File)
    } else { @() }
    $sweepPngs = if (Test-Path -LiteralPath (Join-Path $CaptureRoot "sweep")) {
        @(Get-ChildItem -LiteralPath (Join-Path $CaptureRoot "sweep") -Filter "*.png" -File)
    } else { @() }
    if ($unrealProcess.timed_out -or $unrealProcess.exit_code -ne 0 -or
        -not $rhiValidated -or -not $capturePassed -or $criticalSignature -or
        -not (Test-Path -LiteralPath $PilotReceipt -PathType Leaf) -or
        -not (Test-Path -LiteralPath $SweepManifest -PathType Leaf) -or
        $pilotPngs.Count -ne 3 -or $sweepPngs.Count -ne 72) {
        throw "Recovery02 pilot-gated synchronized capture failed closed."
    }
    $pilot = Get-Content -LiteralPath $PilotReceipt -Raw | ConvertFrom-Json
    if ($pilot.gate -ne "PASS_RECOVERY02_PILOT_LIVE_FULL_SWEEP_ALLOWED" -or
        $pilot.unique_png_hash_count -ne 3) {
        throw "Recovery02 pilot liveness receipt failed closed."
    }

    $selectorProcess = Invoke-Bounded -FilePath $Python -Arguments @(
        $Selector, "--manifest", $SweepManifest, "--output", $SelectionRoot
    ) -Stdout $SelectorStdout -Stderr $SelectorStderr -BoundSeconds 180
    $SelectionReceipt = Join-Path $SelectionRoot "rig_selection_receipt.json"
    if ($selectorProcess.timed_out -or $selectorProcess.exit_code -ne 0 -or
        -not (Test-Path -LiteralPath $SelectionReceipt -PathType Leaf)) {
        throw "Recovery02 global-rig selector failed closed."
    }

    $auditorProcess = Invoke-Bounded -FilePath $Python -Arguments @(
        $ExecutionAuditor, "--preflight", $PreflightSnapshot,
        "--sweep-manifest", $SweepManifest,
        "--selection-receipt", $SelectionReceipt,
        "--output", $ExecutionAudit
    ) -Stdout $AuditorStdout -Stderr $AuditorStderr -BoundSeconds 180
    if ($auditorProcess.timed_out -or $auditorProcess.exit_code -ne 0 -or
        -not (Test-Path -LiteralPath $ExecutionAudit -PathType Leaf)) {
        throw "Recovery02 execution audit failed closed."
    }
    $audit = Get-Content -LiteralPath $ExecutionAudit -Raw | ConvertFrom-Json
    if ($audit.gate -ne
        "PASS_RECOVERY02_EXECUTION_AWAITING_ORIGINAL_RESOLUTION_REVIEW") {
        throw "Recovery02 audit gate mismatch."
    }
    $remainingHeavy = @(Get-Process -ErrorAction SilentlyContinue |
        Where-Object { $HeavyNames -contains $_.ProcessName })
    if ($remainingHeavy.Count -ne 0) {
        throw "Heavy process remained after Recovery02."
    }
    $receipt = [ordered]@{
        schema = "skyguard.m01.hero-grouped-topology-unreal-mapped-attempt03-recovery02-supervisor.v1"
        gate = "PASS_RECOVERY02_EXECUTION_AWAITING_ORIGINAL_RESOLUTION_REVIEW"
        completed_at_utc = [DateTime]::UtcNow.ToString("o")
        execution_contract_sha256 = $actualExecutionHash
        attempt_root = $AttemptRoot
        unreal_process = $unrealProcess
        selector_process = $selectorProcess
        auditor_process = $auditorProcess
        checks = [ordered]@{
            exactly_one_unreal_process_launched = $true
            pilot_passed_before_full_sweep = $true
            fresh_capture_and_render_target_per_frame = $true
            existing_review_map_reused_without_reassembly = $true
            rhi_d3d12_sm6_validated = $rhiValidated
            exact_3_pilot_pngs = $pilotPngs.Count -eq 3
            exact_72_sweep_pngs = $sweepPngs.Count -eq 72
            critical_log_signature_absent = -not $criticalSignature
            package_runtime_config_hash_invariance = $true
        }
        pilot_receipt = [ordered]@{
            path = $PilotReceipt
            sha256 = Get-Sha256 $PilotReceipt
        }
        sweep_manifest = [ordered]@{
            path = $SweepManifest
            sha256 = Get-Sha256 $SweepManifest
        }
        selection_receipt = [ordered]@{
            path = $SelectionReceipt
            sha256 = Get-Sha256 $SelectionReceipt
        }
        execution_audit = [ordered]@{
            path = $ExecutionAudit
            sha256 = Get-Sha256 $ExecutionAudit
        }
        promotion_allowed = $false
        p3_4_closed = $false
        next_gate = "original-resolution human review of nine canonical Recovery02 images"
    }
    $receipt | ConvertTo-Json -Depth 20 |
        Set-Content -LiteralPath $SupervisorReceipt -Encoding UTF8
    Write-Output ($receipt | ConvertTo-Json -Depth 20)
} catch {
    $failure = $_.Exception.Message
    [ordered]@{
        schema = "skyguard.m01.hero-grouped-topology-unreal-mapped-attempt03-recovery02-supervisor.v1"
        gate = "FAIL_CLOSED_RECOVERY02_NOT_ACCEPTED"
        failed_at_utc = [DateTime]::UtcNow.ToString("o")
        failure = $failure
        execution_contract_sha256 = $actualExecutionHash
        attempt_root = $AttemptRoot
        unreal_process = $unrealProcess
        selector_process = $selectorProcess
        auditor_process = $auditorProcess
        promotion_allowed = $false
        p3_4_closed = $false
    } | ConvertTo-Json -Depth 20 |
        Set-Content -LiteralPath $SupervisorReceipt -Encoding UTF8
    throw "Recovery02 failed closed. See $SupervisorReceipt. $failure"
}
