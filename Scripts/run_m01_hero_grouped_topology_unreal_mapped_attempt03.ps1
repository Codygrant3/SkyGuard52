[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [switch]$AuthorizeSingleAttempt03Run,
    [Parameter(Mandatory = $true)]
    [ValidatePattern("^[0-9a-fA-F]{64}$")]
    [string]$ExpectedExecutionContractSha256,
    [string]$ProjectRoot = "D:\Skyguard52",
    [string]$UnrealRoot = "D:\UE_5.8",
    [ValidateRange(300, 1800)]
    [int]$TimeoutSeconds = 1200
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

if (-not $AuthorizeSingleAttempt03Run) {
    throw "Explicit -AuthorizeSingleAttempt03Run is required."
}

$ExecutionContractPath = Join-Path $ProjectRoot "Docs\AAA_Review\M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_EXECUTION_CONTRACT.json"
$AttemptContractPath = Join-Path $ProjectRoot "Docs\AAA_Review\M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_CONTRACT.json"
$ProjectFile = Join-Path $ProjectRoot "Skyguard52.uproject"
$EditorExe = Join-Path $UnrealRoot "Engine\Binaries\Win64\UnrealEditor.exe"
$Python = (Get-Command python -ErrorAction Stop).Source
$HeavyNames = @(
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
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function ConvertTo-CommandLineArgument {
    param([Parameter(Mandatory = $true)][string]$Value)
    if ($Value -notmatch '[\s"]') {
        return $Value
    }
    return '"' + ($Value -replace '(\\*)"', '$1$1\"' -replace '(\\+)$', '$1$1') + '"'
}

function Join-CommandLine {
    param([Parameter(Mandatory = $true)][string[]]$Arguments)
    return (($Arguments | ForEach-Object {
        ConvertTo-CommandLineArgument $_
    }) -join " ")
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
    $files = @(Get-ChildItem -LiteralPath $RootPath -Recurse -File |
        Sort-Object FullName)
    foreach ($file in $files) {
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

function Assert-HashMapsEqual {
    param(
        [Parameter(Mandatory = $true)]$Expected,
        [Parameter(Mandatory = $true)]$Actual,
        [Parameter(Mandatory = $true)][string]$Label
    )
    $expectedProperties = @($Expected.PSObject.Properties)
    $actualProperties = @($Actual.GetEnumerator())
    if ($expectedProperties.Count -ne $actualProperties.Count) {
        throw "$Label package count mismatch."
    }
    foreach ($property in $expectedProperties) {
        if (-not $Actual.Contains($property.Name) -or
            $Actual[$property.Name] -ne [string]$property.Value) {
            throw "$Label hash mismatch: $($property.Name)"
        }
    }
}

function Invoke-BoundedProcess {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [Parameter(Mandatory = $true)][string]$StdoutPath,
        [Parameter(Mandatory = $true)][string]$StderrPath,
        [Parameter(Mandatory = $true)][int]$BoundSeconds,
        [switch]$Hidden
    )
    $start = [DateTime]::UtcNow
    $startParameters = @{
        FilePath = $FilePath
        ArgumentList = (Join-CommandLine $Arguments)
        WorkingDirectory = $ProjectRoot
        RedirectStandardOutput = $StdoutPath
        RedirectStandardError = $StderrPath
        PassThru = $true
    }
    if ($Hidden) {
        $startParameters["WindowStyle"] = "Hidden"
    }
    $process = Start-Process @startParameters
    $deadline = $start.AddSeconds($BoundSeconds)
    $peakWorkingSet = 0L
    while (-not $process.HasExited -and [DateTime]::UtcNow -lt $deadline) {
        $ids = @($process.Id) + @(Get-DescendantProcessIds -RootProcessId $process.Id)
        foreach ($sampleId in $ids) {
            $sample = Get-Process -Id $sampleId -ErrorAction SilentlyContinue
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
    $terminated = @()
    if ($timedOut) {
        $terminated = @(Stop-OwnedProcessTree -RootProcessId $process.Id)
    }
    $process.WaitForExit()
    $process.Refresh()
    $exitCode = if ($timedOut) { $null } else { [int]$process.ExitCode }
    return [ordered]@{
        pid = $process.Id
        exit_code = $exitCode
        timed_out = $timedOut
        terminated_descendant_pids = $terminated
        started_at_utc = $start.ToString("o")
        finished_at_utc = [DateTime]::UtcNow.ToString("o")
        peak_working_set_mib = [Math]::Round($peakWorkingSet / 1MB, 3)
        stdout = $StdoutPath
        stderr = $StderrPath
    }
}

foreach ($required in @($ExecutionContractPath, $AttemptContractPath, $ProjectFile, $EditorExe)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
        throw "Required input is missing: $required"
    }
}
$actualExecutionContractHash = Get-Sha256 $ExecutionContractPath
if ($actualExecutionContractHash -ne $ExpectedExecutionContractSha256.ToLowerInvariant()) {
    throw "Execution contract hash mismatch; Unreal was not launched."
}
$execution = Get-Content -LiteralPath $ExecutionContractPath -Raw |
    ConvertFrom-Json
if ($execution.authorization.authorize_switch -ne "AuthorizeSingleAttempt03Run" -or
    $execution.promotion_allowed -ne $false -or
    $execution.p3_4_closed -ne $false) {
    throw "Execution contract policy mismatch; Unreal was not launched."
}
foreach ($record in $execution.bound_files.PSObject.Properties.Value) {
    $path = Join-Path $ProjectRoot $record.path
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "Bound execution file is missing: $path"
    }
    if ((Get-Item -LiteralPath $path).Length -ne [int64]$record.bytes) {
        throw "Bound execution file byte count changed: $path"
    }
    if ((Get-Sha256 $path) -ne $record.sha256) {
        throw "Bound execution file hash changed: $path"
    }
}

$AttemptRoot = Join-Path $ProjectRoot $execution.outputs.attempt_root
$SweepRoot = Join-Path $ProjectRoot $execution.outputs.sweep_root
$SelectionRoot = Join-Path $ProjectRoot $execution.outputs.selection_root
$SupervisorReceipt = Join-Path $ProjectRoot $execution.outputs.supervisor_receipt
$PreflightSnapshot = Join-Path $AttemptRoot "preflight_snapshot.json"
$ExecutionAudit = Join-Path $AttemptRoot "execution_audit.json"
$BuildReport = Join-Path $ProjectRoot $execution.outputs.build_report
$Attempt03Content = Join-Path $ProjectRoot $execution.outputs.attempt03_content
$Entrypoint = Join-Path $ProjectRoot $execution.bound_files.unreal_entrypoint.path
$ReadinessAuditor = Join-Path $ProjectRoot $execution.bound_files.offline_readiness_auditor.path
$Selector = Join-Path $ProjectRoot $execution.bound_files.offline_selector.path
$ExecutionAuditor = Join-Path $ProjectRoot $execution.bound_files.execution_auditor.path
$FailedReview = Join-Path $ProjectRoot $execution.bound_files.failed_visual_review.path
$ReviewMap = $execution.review_map

foreach ($immutable in @($AttemptRoot, $BuildReport, $Attempt03Content)) {
    if (Test-Path -LiteralPath $immutable) {
        throw "Immutable Attempt03 target already exists: $immutable"
    }
}
$heavy = @(Get-Process -ErrorAction SilentlyContinue |
    Where-Object { $HeavyNames -contains $_.ProcessName } |
    Select-Object Id, ProcessName, StartTime)
if ($heavy.Count -ne 0) {
    throw "Attempt03 lane requires zero heavy processes: $($heavy | ConvertTo-Json -Compress)"
}
$os = Get-CimInstance Win32_OperatingSystem
$freePhysicalGiB = [Math]::Round(([double]$os.FreePhysicalMemory * 1KB) / 1GB, 3)
if ($freePhysicalGiB -lt [double]$execution.resource_preflight.minimum_free_physical_gib) {
    throw "Attempt03 lane has only $freePhysicalGiB GiB free RAM."
}

$readinessText = & $Python $ReadinessAuditor 2>&1
if ($LASTEXITCODE -ne 0) {
    throw "Offline Attempt03 readiness failed; Unreal was not launched."
}
$readiness = $readinessText -join [Environment]::NewLine
if ($readiness -notmatch "PASS_OFFLINE_READY_AWAITING_SEPARATE_UNREAL_ATTEMPT03_AUTHORIZATION") {
    throw "Offline readiness pass marker missing; Unreal was not launched."
}

$failedReviewData = Get-Content -LiteralPath $FailedReview -Raw |
    ConvertFrom-Json
$originalCandidate = Get-TreeHashMap `
    -RootPath (Join-Path $ProjectRoot "Content\Skyguard\Candidates\Mission01\HeroGroupedTopology_008") `
    -Suffixes @(".uasset", ".umap")
Assert-HashMapsEqual `
    -Expected $failedReviewData.persistence.current_package_hashes `
    -Actual $originalCandidate `
    -Label "Original candidate"
$runtimeMaps = Get-TreeHashMap `
    -RootPath (Join-Path $ProjectRoot "Content\Skyguard\Maps") `
    -Suffixes @(".uasset", ".umap")
$configFiles = Get-TreeHashMap -RootPath (Join-Path $ProjectRoot "Config")

New-Item -ItemType Directory -Path $AttemptRoot | Out-Null
$readiness | Set-Content -LiteralPath (
    Join-Path $AttemptRoot "offline_readiness.log"
) -Encoding UTF8
[ordered]@{
    schema = "skyguard.m01.hero-grouped-topology-attempt03-preflight.v1"
    recorded_at_utc = [DateTime]::UtcNow.ToString("o")
    execution_contract_sha256 = $actualExecutionContractHash
    contract_sha256 = Get-Sha256 $AttemptContractPath
    failed_review_sha256 = Get-Sha256 $FailedReview
    heavy_process_count = $heavy.Count
    free_physical_gib = $freePhysicalGiB
    attempt03_content_absent = $true
    original_candidate_packages = $originalCandidate
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
    $unrealArguments = @(
        $ProjectFile,
        "-ExecutePythonScript=$Entrypoint",
        "-ScriptErrorsAreFatal",
        "-SkyguardAttempt03SweepOutput=$SweepRoot",
        "-SkyguardAttempt03ReviewMap=$ReviewMap",
        "-unattended",
        "-nop4",
        "-NoSplash",
        "-RenderOffscreen",
        "-windowed",
        "-ResX=2048",
        "-ResY=2048",
        "-d3d12",
        "-sm6",
        "-NoVSync",
        "-stdout",
        "-FullStdOutLogOutput",
        "-abslog=$EngineLog",
        "-NoAssetRegistryCache",
        "-ExecCmds=r.ScreenPercentage 100,sg.ViewDistanceQuality 3,sg.ShadowQuality 3,sg.PostProcessQuality 3,sg.TextureQuality 3,sg.EffectsQuality 3"
    )
    $unrealProcess = Invoke-BoundedProcess `
        -FilePath $EditorExe `
        -Arguments $unrealArguments `
        -StdoutPath $UnrealStdout `
        -StderrPath $UnrealStderr `
        -BoundSeconds $TimeoutSeconds `
        -Hidden
    $combined = ""
    foreach ($log in @($UnrealStdout, $UnrealStderr, $EngineLog)) {
        if (Test-Path -LiteralPath $log -PathType Leaf) {
            $combined += [Environment]::NewLine + (
                Get-Content -LiteralPath $log -Raw
            )
        }
    }
    $criticalPattern = "Fatal error|LowLevelFatalError|Assertion failed|Ensure condition failed|GPU Crash|DXGI_ERROR_DEVICE_|Out of video memory|Ran out of memory|LogPython: Error|Traceback \(most recent call last\)"
    $rhiValidated = $combined -match "\[M01Grouped008Attempt03Capture\]\[RHI_VALIDATED\]\s+D3D12\|SM6"
    $oneProcessPassed = $combined -match "PASS_ATTEMPT03_ONE_PROCESS_BUILD_AND_SWEEP_AWAITING_OFFLINE_SELECTION"
    $criticalSignature = $combined -match $criticalPattern
    $SweepManifest = Join-Path $SweepRoot "capture_manifest.json"
    $sweepPngs = if (Test-Path -LiteralPath $SweepRoot -PathType Container) {
        @(Get-ChildItem -LiteralPath $SweepRoot -File -Filter "*.png")
    } else {
        @()
    }
    if ($unrealProcess.timed_out -or
        $unrealProcess.exit_code -ne 0 -or
        -not $rhiValidated -or
        -not $oneProcessPassed -or
        $criticalSignature -or
        -not (Test-Path -LiteralPath $SweepManifest -PathType Leaf) -or
        $sweepPngs.Count -ne 63) {
        throw "One-process Unreal build/sweep failed closed."
    }

    $selectorArguments = @(
        $Selector,
        "--manifest", $SweepManifest,
        "--output", $SelectionRoot
    )
    $selectorProcess = Invoke-BoundedProcess `
        -FilePath $Python `
        -Arguments $selectorArguments `
        -StdoutPath $SelectorStdout `
        -StderrPath $SelectorStderr `
        -BoundSeconds 180 `
        -Hidden
    $SelectionReceipt = Join-Path $SelectionRoot "exposure_selection_receipt.json"
    if ($selectorProcess.timed_out -or
        $selectorProcess.exit_code -ne 0 -or
        -not (Test-Path -LiteralPath $SelectionReceipt -PathType Leaf)) {
        throw "Offline global-EV selector failed closed."
    }

    $auditorArguments = @(
        $ExecutionAuditor,
        "--preflight", $PreflightSnapshot,
        "--sweep-manifest", $SweepManifest,
        "--selection-receipt", $SelectionReceipt,
        "--output", $ExecutionAudit
    )
    $auditorProcess = Invoke-BoundedProcess `
        -FilePath $Python `
        -Arguments $auditorArguments `
        -StdoutPath $AuditorStdout `
        -StderrPath $AuditorStderr `
        -BoundSeconds 180 `
        -Hidden
    if ($auditorProcess.timed_out -or
        $auditorProcess.exit_code -ne 0 -or
        -not (Test-Path -LiteralPath $ExecutionAudit -PathType Leaf)) {
        throw "Independent Attempt03 execution audit failed closed."
    }
    $audit = Get-Content -LiteralPath $ExecutionAudit -Raw | ConvertFrom-Json
    if ($audit.gate -ne "PASS_ATTEMPT03_EXECUTION_AWAITING_ORIGINAL_RESOLUTION_REVIEW" -or
        $audit.promotion_allowed -ne $false -or
        $audit.p3_4_closed -ne $false) {
        throw "Independent Attempt03 execution audit gate mismatch."
    }

    $remainingHeavy = @(Get-Process -ErrorAction SilentlyContinue |
        Where-Object { $HeavyNames -contains $_.ProcessName } |
        Select-Object Id, ProcessName)
    if ($remainingHeavy.Count -ne 0) {
        throw "Heavy process remained after bounded Attempt03 execution."
    }
    $receipt = [ordered]@{
        schema = "skyguard.m01.hero-grouped-topology-unreal-mapped-attempt03-supervisor.v1"
        gate = "PASS_ATTEMPT03_EXECUTION_AWAITING_ORIGINAL_RESOLUTION_REVIEW"
        completed_at_utc = [DateTime]::UtcNow.ToString("o")
        execution_contract_sha256 = $actualExecutionContractHash
        attempt_root = $AttemptRoot
        preflight_snapshot = [ordered]@{
            path = $PreflightSnapshot
            sha256 = Get-Sha256 $PreflightSnapshot
        }
        unreal_process = $unrealProcess
        selector_process = $selectorProcess
        auditor_process = $auditorProcess
        checks = [ordered]@{
            exactly_one_unreal_process_launched = $true
            rhi_d3d12_sm6_validated = $rhiValidated
            exact_63_sweep_pngs = $sweepPngs.Count -eq 63
            critical_log_signature_absent = -not $criticalSignature
            immutable_package_hash_audit_passed = $true
            heavy_process_count_after = $remainingHeavy.Count
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
        next_gate = "original-resolution human visual review of nine canonical captures"
    }
    $receipt | ConvertTo-Json -Depth 20 |
        Set-Content -LiteralPath $SupervisorReceipt -Encoding UTF8
    Write-Output ($receipt | ConvertTo-Json -Depth 20)
} catch {
    $failure = $_.Exception.Message
    if ($null -ne $unrealProcess -and $unrealProcess.timed_out -eq $false) {
        # The process result is already terminal. Never kill unrelated processes.
    }
    $failReceipt = [ordered]@{
        schema = "skyguard.m01.hero-grouped-topology-unreal-mapped-attempt03-supervisor.v1"
        gate = "FAIL_CLOSED_ATTEMPT03_NOT_ACCEPTED"
        failed_at_utc = [DateTime]::UtcNow.ToString("o")
        failure = $failure
        execution_contract_sha256 = $actualExecutionContractHash
        attempt_root = $AttemptRoot
        unreal_process = $unrealProcess
        selector_process = $selectorProcess
        auditor_process = $auditorProcess
        promotion_allowed = $false
        p3_4_closed = $false
    }
    if (-not (Test-Path -LiteralPath $SupervisorReceipt)) {
        $failReceipt | ConvertTo-Json -Depth 20 |
            Set-Content -LiteralPath $SupervisorReceipt -Encoding UTF8
    }
    throw "Attempt03 failed closed. See $SupervisorReceipt. $failure"
}
