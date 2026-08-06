[CmdletBinding()]
param(
    [string]$ProjectRoot = "D:\Skyguard52",
    [string]$UnrealRoot = "D:\UE_5.8",
    [ValidateRange(60, 1800)]
    [int]$BuildTimeoutSeconds = 900,
    [ValidateRange(60, 300)]
    [int]$EditorTimeoutSeconds = 240,
    [ValidateRange(100, 240)]
    [int]$ProfileTimeoutSeconds = 150,
    [switch]$SkipBuild
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$ContractId = "P4.5-M01-LANDSCAPE-VISIBLE-005"
$BaselineMap = "/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_ProductionEnvironment_v5_attempt03"
$CandidateMap = "/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_LandscapeMaterialValidation_v5_attempt05"
$BaselineFile = Join-Path $ProjectRoot "Content\Skyguard\Maps\Lvl_M01_CoastalIntercept_ProductionEnvironment_v5_attempt03.umap"
$BaselineHash = "447e7ac49dc6c843f33bfc177ff46134b10035b6c6765d354ef790acf7f58d72"
$Attempt04File = Join-Path $ProjectRoot "Content\Skyguard\Maps\Lvl_M01_CoastalIntercept_LandscapeMaterialValidation_v4_attempt04.umap"
$Attempt04Hash = "cb2c13f3ce18a3462620306bcef4610d87c2f0cf28a7815b444bd68ab773a021"
$Attempt04MaterialFile = Join-Path $ProjectRoot "Content\Skyguard\Materials\Mission01\LandscapeValidation_v4\M_M01_Landscape_Validation_v4.uasset"
$Attempt04MaterialHash = "e54682b64f43dbaf0e2c61f08436d495493c6db1f28998cce9583d0542c4042e"
$CandidateFile = Join-Path $ProjectRoot "Content\Skyguard\Maps\Lvl_M01_CoastalIntercept_LandscapeMaterialValidation_v5_attempt05.umap"
$CandidateMaterialFile = Join-Path $ProjectRoot "Content\Skyguard\Materials\Mission01\LandscapeValidation_v5_attempt05\M_M01_Landscape_Validation_v5_attempt05.uasset"
$CoverageMaterialFile = Join-Path $ProjectRoot "Content\Skyguard\Materials\Diagnostics\M_P45_LandscapeCoverage_Unlit_v1.uasset"
$ComponentMaterialFile = Join-Path $ProjectRoot "Content\Skyguard\Materials\Diagnostics\M_P45_LandscapeComponentId_Unlit_v1.uasset"
$ProjectFile = Join-Path $ProjectRoot "Skyguard52.uproject"
$BuildTool = Join-Path $UnrealRoot "Engine\Build\BatchFiles\Build.bat"
$EditorCmd = Join-Path $UnrealRoot "Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
$EditorExe = Join-Path $UnrealRoot "Engine\Binaries\Win64\UnrealEditor.exe"
$Builder = Join-Path $ProjectRoot "Scripts\build_skyguard_phase4_m01_landscape_material_validation_attempt05.py"
$EditorVerifier = Join-Path $ProjectRoot "Scripts\verify_skyguard_phase4_m01_landscape_material_assets_attempt05.py"
$CaptureScript = Join-Path $ProjectRoot "Scripts\capture_skyguard_phase4_m01_landscape_visible_review_attempt05.py"
$GateVerifier = Join-Path $ProjectRoot "Scripts\verify_skyguard_phase4_m01_landscape_visible_gpu_gate_attempt05.py"
$EditorAcceptance = Join-Path $ProjectRoot "Saved\Reports\PHASE4_M01_LANDSCAPE_MATERIAL_EDITOR_ACCEPTANCE_ATTEMPT05.json"
$LatestGate = Join-Path $ProjectRoot "Saved\Reports\PHASE4_M01_LANDSCAPE_VISIBLE_GPU_REVIEW_ATTEMPT05_LATEST.json"
$RunRoot = Join-Path $ProjectRoot "Saved\Profiling\Phase4\M01_LandscapeVisible_Attempt05"
$CsvRoot = Join-Path $ProjectRoot "Saved\Profiling\CSV"
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
    $Value | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $Path -Encoding UTF8
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

function Invoke-BoundedProcess {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$FilePath,
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [Parameter(Mandatory = $true)][string]$LogsRoot,
        [Parameter(Mandatory = $true)][int]$TimeoutSeconds,
        [int[]]$AcceptedExitCodes = @(0)
    )
    $stdout = Join-Path $LogsRoot ($Name + ".stdout.log")
    $stderr = Join-Path $LogsRoot ($Name + ".stderr.log")
    $engineLog = Join-Path $LogsRoot ($Name + ".engine.log")
    $argumentsWithLog = @($Arguments)
    if ($FilePath -in @($EditorExe, $EditorCmd)) {
        $argumentsWithLog += "-abslog=$engineLog"
    }
    $argumentLine = ($argumentsWithLog | ForEach-Object { ConvertTo-Argument $_ }) -join " "
    $started = [DateTime]::UtcNow
    $process = Start-Process -FilePath $FilePath `
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
                $peakWorkingSet = [Math]::Max($peakWorkingSet, [int64]$sample.WorkingSet64)
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
    $stage = [ordered]@{
        name = $Name
        command_line = "$FilePath $argumentLine"
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
        injected_module_candidates = @()
    }
    if ($timedOut -or $exitCode -notin $AcceptedExitCodes) {
        throw "Stage failed: $Name timed_out=$timedOut exit_code=$exitCode"
    }
    $combined = @($stdout, $stderr, $engineLog) |
        Where-Object { Test-Path -LiteralPath $_ -PathType Leaf } |
        ForEach-Object { Get-Content -LiteralPath $_ -Raw }
    if (($combined -join "`n") -match "Fatal error|Assertion failed|GPU Crash|DXGI_ERROR_DEVICE_|Out of video memory|LogPython: Error|Traceback \(most recent call last\)") {
        throw "Critical log signature in stage: $Name"
    }
    return $stage
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
    $ProjectFile, $BuildTool, $EditorCmd, $EditorExe, $Builder,
    $EditorVerifier, $CaptureScript, $GateVerifier, $BaselineFile,
    $Attempt04File, $Attempt04MaterialFile
)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
        throw "Required file missing: $required"
    }
}
if ((Get-Sha256 $BaselineFile) -ne $BaselineHash) {
    throw "Immutable baseline hash failed"
}
if (
    (Get-Sha256 $Attempt04File) -ne $Attempt04Hash -or
    (Get-Sha256 $Attempt04MaterialFile) -ne $Attempt04MaterialHash
) {
    throw "Immutable attempt04 failed-evidence hash changed"
}
if (@(Get-ExactHeavyProcesses).Count -ne 0) {
    throw "Exclusive heavy lane is not free"
}

$stamp = [DateTime]::UtcNow.ToString("yyyyMMddTHHmmssfffZ")
$AttemptRoot = Join-Path $RunRoot "attempt_$stamp"
$LogsRoot = Join-Path $AttemptRoot "logs"
$ArtifactsRoot = Join-Path $AttemptRoot "artifacts"
$BaselineCaptureRoot = Join-Path $ArtifactsRoot "captures\baseline"
$CandidateCaptureRoot = Join-Path $ArtifactsRoot "captures\candidate"
$ManifestPath = Join-Path $AttemptRoot "run_manifest.json"
$GatePath = Join-Path $AttemptRoot "gate_report.json"
New-Item -ItemType Directory -Force -Path $LogsRoot, $ArtifactsRoot | Out-Null

$manifest = [ordered]@{
    schema = "skyguard.phase4.m01-landscape-visible-supervisor.v2"
    contract_id = $ContractId
    attempt_id = "attempt_$stamp"
    created_at_utc = [DateTime]::UtcNow.ToString("o")
    baseline_map = $BaselineMap
    candidate_map = $CandidateMap
    baseline_sha256_before = Get-Sha256 $BaselineFile
    baseline_sha256_after = $null
    candidate_sha256_before = $null
    candidate_sha256_after = $null
    candidate_material_sha256_before = $null
    candidate_material_sha256_after = $null
    controls = [ordered]@{
        sequential_processes_only = $true
        same_process_warmup_and_measurement = $true
        warmup_seconds = 30
        measured_seconds = 60
        boot_csv_capture_forbidden = $true
        active_rhi_required = "D3D12|SM6"
        maximum_total_gpu_lane_minutes = 8
        pcg_generation_allowed = $false
        network_download_allowed = $false
    }
    stages = @()
    artifacts = [ordered]@{
        baseline_capture_root = $BaselineCaptureRoot
        candidate_capture_root = $CandidateCaptureRoot
        baseline_csv = $null
        candidate_csv = $null
        baseline_profile_receipt = Join-Path $ArtifactsRoot "baseline_profile_receipt.json"
        candidate_profile_receipt = Join-Path $ArtifactsRoot "candidate_profile_receipt.json"
        editor_acceptance = $EditorAcceptance
    }
    terminal_state = "RUNNING"
    errors = @()
}
Save-Json $manifest $ManifestPath

try {
    if (-not $SkipBuild) {
        $manifest.stages += Invoke-BoundedProcess `
            -Name "build_skyguard52_editor" -FilePath $BuildTool `
            -Arguments @("Skyguard52Editor", "Win64", "Development", "-Project=$ProjectFile", "-WaitMutex", "-NoHotReload") `
            -LogsRoot $LogsRoot -TimeoutSeconds $BuildTimeoutSeconds
    }
    if (
        (Test-Path -LiteralPath $CandidateFile) -or
        (Test-Path -LiteralPath $CandidateMaterialFile) -or
        (Test-Path -LiteralPath $CoverageMaterialFile) -or
        (Test-Path -LiteralPath $ComponentMaterialFile)
    ) {
        throw "Attempt05 immutable outputs already exist; never overwrite an attempt"
    }
    $manifest.stages += Invoke-BoundedProcess `
        -Name "author_immutable_candidate_attempt05" -FilePath $EditorCmd `
        -Arguments @($ProjectFile, "-run=pythonscript", "-script=$Builder", "-unattended", "-nop4", "-NoSplash", "-NullRHI") `
        -LogsRoot $LogsRoot -TimeoutSeconds $EditorTimeoutSeconds
    foreach ($output in @($CandidateFile, $CandidateMaterialFile, $CoverageMaterialFile, $ComponentMaterialFile)) {
        if (-not (Test-Path -LiteralPath $output -PathType Leaf)) {
            throw "Attempt05 authoring output missing: $output"
        }
    }
    $manifest.candidate_sha256_before = Get-Sha256 $CandidateFile
    $manifest.candidate_material_sha256_before = Get-Sha256 $CandidateMaterialFile
    $manifest.stages += Invoke-BoundedProcess `
        -Name "verify_immutable_candidate_attempt05" -FilePath $EditorCmd `
        -Arguments @($ProjectFile, "-run=pythonscript", "-script=$EditorVerifier", "-unattended", "-nop4", "-NoSplash", "-NullRHI") `
        -LogsRoot $LogsRoot -TimeoutSeconds $EditorTimeoutSeconds

    foreach ($spec in @(
        [ordered]@{ mode = "baseline"; map = $BaselineMap; root = $BaselineCaptureRoot },
        [ordered]@{ mode = "candidate"; map = $CandidateMap; root = $CandidateCaptureRoot }
    )) {
        $manifest.stages += Invoke-BoundedProcess `
            -Name "$($spec.mode)_capture" -FilePath $EditorExe `
            -Arguments @(
                $ProjectFile, $spec.map, "-ExecutePythonScript=$CaptureScript",
                "-ScriptErrorsAreFatal", "-SkyguardReviewMode=$($spec.mode)",
                "-SkyguardReviewMap=$($spec.map)", "-SkyguardReviewOutput=$($spec.root)",
                "-unattended", "-nop4", "-NoSplash", "-RenderOffscreen",
                "-windowed", "-ResX=1920", "-ResY=1080", "-d3d12", "-sm6"
            ) -LogsRoot $LogsRoot -TimeoutSeconds $EditorTimeoutSeconds
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
        $runId = "$($manifest.attempt_id)_$($profile.mode)"
        $manifest.stages += Invoke-BoundedProcess `
            -Name "$($profile.mode)_profile_measured" -FilePath $EditorExe `
            -Arguments @(
                $ProjectFile, $profile.map, "-game", "-windowed", "-ResX=1920",
                "-ResY=1080", "-d3d12", "-sm6", "-NoVSync", "-NoSplash",
                "-NoLoadingScreen", "-benchmark", "-benchmarkseconds=100", "-fps=60",
                "-ExecCmds=r.SetRes 1920x1080w,r.ScreenPercentage 100,sg.ViewDistanceQuality 3,sg.ShadowQuality 3,sg.PostProcessQuality 3,sg.TextureQuality 3,sg.EffectsQuality 3,sg.FoliageQuality 3,BugItGo 22500 -9000 8500 -28 90 0",
                "-trace=cpu,gpu,frame,bookmark,loadtime,file,assetload",
                "-tracefile=$(Join-Path $ArtifactsRoot ($profile.mode + '.utrace'))",
                "-tracefiletrunc", "-traceautostart=1", "-csvCategories=Global",
                "-csvGpuStats", "-csvNamedEvents",
                "-SkyguardP45ProfileContractId=$ContractId",
                "-SkyguardP45ProfileRunId=$runId",
                "-SkyguardP45ProfileExpectedMap=$($profile.map)",
                "-SkyguardP45ProfileReceipt=$($manifest.artifacts[$receiptKey])",
                "-SkyguardP45ProfileWarmupSeconds=30",
                "-SkyguardP45ProfileMeasuredSeconds=60"
            ) -LogsRoot $LogsRoot -TimeoutSeconds $ProfileTimeoutSeconds
        $manifest.artifacts["$($profile.mode)_csv"] = Get-NewCsv -Before $before -StartedAt $profileStarted
        $profileReceipt = Get-Content -LiteralPath $manifest.artifacts[$receiptKey] -Raw | ConvertFrom-Json
        if ($profileReceipt.gate -ne "PASS") {
            throw "$($profile.mode) same-process profile receipt failed"
        }
    }

    $manifest.baseline_sha256_after = Get-Sha256 $BaselineFile
    $manifest.candidate_sha256_after = Get-Sha256 $CandidateFile
    $manifest.candidate_material_sha256_after = Get-Sha256 $CandidateMaterialFile
    if (
        $manifest.baseline_sha256_after -ne $BaselineHash -or
        $manifest.candidate_sha256_after -ne $manifest.candidate_sha256_before -or
        $manifest.candidate_material_sha256_after -ne $manifest.candidate_material_sha256_before
    ) {
        throw "Immutable package hash changed during evidence capture"
    }
    $manifest.terminal_state = "EVIDENCE_CAPTURED_PENDING_GATE"
    Save-Json $manifest $ManifestPath
    $manifest.stages += Invoke-BoundedProcess `
        -Name "verify_attempt05_visible_gpu_gate" -FilePath "python" `
        -Arguments @($GateVerifier, "--manifest", $ManifestPath, "--output", $GatePath, "--latest-output", $LatestGate) `
        -LogsRoot $LogsRoot -TimeoutSeconds 60 -AcceptedExitCodes @(0, 2)
    $gateReport = Get-Content -LiteralPath $GatePath -Raw | ConvertFrom-Json
    if ($gateReport.technical_gate -ne "PASS") {
        throw "Attempt05 technical GPU gate failed"
    }
    if ($gateReport.gate -eq "PASS") {
        $manifest.terminal_state = "GATE_COMPLETE"
    }
    elseif ($gateReport.gate -eq "INCOMPLETE_HUMAN_REVIEW") {
        $manifest.terminal_state = "TECHNICAL_GATE_PASS_PENDING_HUMAN_REVIEW"
    }
    else {
        throw "Unexpected attempt05 gate state: $($gateReport.gate)"
    }
}
catch {
    $manifest.errors += $_.Exception.Message
    $manifest.terminal_state = "FAILED"
    throw
}
finally {
    $manifest.baseline_sha256_after = Get-Sha256 $BaselineFile
    if (Test-Path -LiteralPath $CandidateFile) {
        $manifest.candidate_sha256_after = Get-Sha256 $CandidateFile
    }
    if (Test-Path -LiteralPath $CandidateMaterialFile) {
        $manifest.candidate_material_sha256_after = Get-Sha256 $CandidateMaterialFile
    }
    Save-Json $manifest $ManifestPath
    $remaining = @(Wait-ForZeroHeavyProcesses -TimeoutSeconds 30)
    if ($remaining.Count -ne 0) {
        throw "Heavy processes remain after attempt05 supervisor"
    }
}
