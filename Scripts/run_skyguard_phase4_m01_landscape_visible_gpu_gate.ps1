[CmdletBinding()]
param(
    [string]$ProjectRoot = "D:\Skyguard52",
    [string]$UnrealRoot = "D:\UE_5.8",
    [ValidateRange(60, 1800)]
    [int]$BuildTimeoutSeconds = 900,
    [ValidateRange(60, 180)]
    [int]$EditorTimeoutSeconds = 180,
    [ValidateRange(60, 180)]
    [int]$ProfileTimeoutSeconds = 180,
    [switch]$SkipBuild
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$ContractId = "P4.5-M01-LANDSCAPE-VISIBLE-004"
$BaselineMap = "/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_ProductionEnvironment_v5_attempt03"
$CandidateMap = "/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_LandscapeMaterialValidation_v4_attempt04"
$BaselineHash = "447e7ac49dc6c843f33bfc177ff46134b10035b6c6765d354ef790acf7f58d72"
$ProjectFile = Join-Path $ProjectRoot "Skyguard52.uproject"
$BuildTool = Join-Path $UnrealRoot "Engine\Build\BatchFiles\Build.bat"
$EditorCmd = Join-Path $UnrealRoot "Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
$EditorExe = Join-Path $UnrealRoot "Engine\Binaries\Win64\UnrealEditor.exe"
$Builder = Join-Path $ProjectRoot "Scripts\build_skyguard_phase4_m01_landscape_material_validation.py"
$EditorVerifier = Join-Path $ProjectRoot "Scripts\verify_skyguard_phase4_m01_landscape_material_assets.py"
$CaptureScript = Join-Path $ProjectRoot "Scripts\capture_skyguard_phase4_m01_landscape_visible_review.py"
$GateVerifier = Join-Path $ProjectRoot "Scripts\verify_skyguard_phase4_m01_landscape_visible_gpu_gate.py"
$BaselineFile = Join-Path $ProjectRoot "Content\Skyguard\Maps\Lvl_M01_CoastalIntercept_ProductionEnvironment_v5_attempt03.umap"
$CandidateFile = Join-Path $ProjectRoot "Content\Skyguard\Maps\Lvl_M01_CoastalIntercept_LandscapeMaterialValidation_v4_attempt04.umap"
$CandidateMaterialFile = Join-Path $ProjectRoot "Content\Skyguard\Materials\Mission01\LandscapeValidation_v4\M_M01_Landscape_Validation_v4.uasset"
$CandidateAcceptedHash = "cb2c13f3ce18a3462620306bcef4610d87c2f0cf28a7815b444bd68ab773a021"
$CandidateMaterialAcceptedHash = "e54682b64f43dbaf0e2c61f08436d495493c6db1f28998cce9583d0542c4042e"
$FailedAttemptFile = Join-Path $ProjectRoot "Content\Skyguard\Maps\Lvl_M01_CoastalIntercept_LandscapeMaterialValidation_v1_attempt01.umap"
$FailedAttemptHash = "88203beaea1f100c50c4863e3e119023871e49807f6d6ae8da06b95e2b206970"
$FailedAttempt02File = Join-Path $ProjectRoot "Content\Skyguard\Maps\Lvl_M01_CoastalIntercept_LandscapeMaterialValidation_v2_attempt02.umap"
$FailedAttempt02Hash = "30007074a179e686db10dd47f6d7ee8bb9542ba61df275abf5583b3919e3818b"
$FailedAttempt02MaterialFile = Join-Path $ProjectRoot "Content\Skyguard\Materials\Mission01\LandscapeValidation_v2\M_M01_Landscape_Validation_v2.uasset"
$FailedAttempt02MaterialHash = "ff94f8358db66c695871ac664259d1d659d9e705b48524574f794fb8cd67df23"
$FailedAttempt03File = Join-Path $ProjectRoot "Content\Skyguard\Maps\Lvl_M01_CoastalIntercept_LandscapeMaterialValidation_v3_attempt03.umap"
$FailedAttempt03Hash = "eacc1a073feb01e322bb0ba8679f07201b3410e4e1849094a4fddad04f5863e0"
$FailedAttempt03MaterialFile = Join-Path $ProjectRoot "Content\Skyguard\Materials\Mission01\LandscapeValidation_v3\M_M01_Landscape_Validation_v3.uasset"
$FailedAttempt03MaterialHash = "d87d02f7ba3fa2c0dcd78b99a6103f63f6567253f5177ad0bfbe0680ffcd7d91"
$EditorAcceptance = Join-Path $ProjectRoot "Saved\Reports\PHASE4_M01_LANDSCAPE_MATERIAL_EDITOR_ACCEPTANCE_ATTEMPT04.json"
$LatestGate = Join-Path $ProjectRoot "Saved\Reports\PHASE4_M01_LANDSCAPE_VISIBLE_GPU_REVIEW_ATTEMPT04_LATEST.json"
$RunRoot = Join-Path $ProjectRoot "Saved\Profiling\Phase4\M01_LandscapeVisible_Attempt04"
$ReportsRoot = Join-Path $ProjectRoot "Saved\Reports"
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

function ConvertTo-CommandLineArgument {
    param([Parameter(Mandatory = $true)][string]$Value)
    if ($Value -notmatch '[\s"]') {
        return $Value
    }
    return '"' + ($Value -replace '(\\*)"', '$1$1\"' -replace '(\\+)$', '$1$1') + '"'
}

function Join-CommandLine {
    param([Parameter(Mandatory = $true)][string[]]$Arguments)
    return (($Arguments | ForEach-Object { ConvertTo-CommandLineArgument $_ }) -join " ")
}

function Save-Json {
    param(
        [Parameter(Mandatory = $true)]$Value,
        [Parameter(Mandatory = $true)][string]$Path
    )
    $Value | ConvertTo-Json -Depth 16 | Set-Content -LiteralPath $Path -Encoding UTF8
}

function Get-Sha256 {
    param([Parameter(Mandatory = $true)][string]$Path)
    $algorithm = [System.Security.Cryptography.SHA256]::Create()
    try {
        $stream = [System.IO.File]::OpenRead($Path)
        try {
            return ([System.BitConverter]::ToString(
                $algorithm.ComputeHash($stream)
            ) -replace "-", "").ToLowerInvariant()
        }
        finally {
            $stream.Dispose()
        }
    }
    finally {
        $algorithm.Dispose()
    }
}

function Get-ExactHeavyProcesses {
    return @(
        Get-Process -ErrorAction SilentlyContinue |
            Where-Object { $ExactHeavyNames -contains $_.ProcessName } |
            Select-Object Id, ProcessName, StartTime
    )
}

function Get-DescendantProcessIds {
    param([Parameter(Mandatory = $true)][int]$RootProcessId)
    $allProcesses = @(Get-CimInstance Win32_Process | Select-Object ProcessId, ParentProcessId)
    $descendants = [System.Collections.Generic.List[int]]::new()
    $frontier = [System.Collections.Generic.Queue[int]]::new()
    $frontier.Enqueue($RootProcessId)
    while ($frontier.Count -gt 0) {
        $parentId = $frontier.Dequeue()
        foreach ($candidate in $allProcesses) {
            if ([int]$candidate.ParentProcessId -eq $parentId) {
                $childId = [int]$candidate.ProcessId
                $descendants.Add($childId)
                $frontier.Enqueue($childId)
            }
        }
    }
    return @($descendants)
}

function Stop-OwnedProcessTree {
    param([Parameter(Mandatory = $true)][int]$RootProcessId)
    $descendants = @(Get-DescendantProcessIds -RootProcessId $RootProcessId)
    [array]::Reverse($descendants)
    foreach ($processId in $descendants) {
        Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
    }
    Stop-Process -Id $RootProcessId -Force -ErrorAction SilentlyContinue
    return @($descendants)
}

function Invoke-BoundedProcess {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$FilePath,
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [Parameter(Mandatory = $true)][string]$StdoutPath,
        [Parameter(Mandatory = $true)][string]$StderrPath,
        [Parameter(Mandatory = $true)][int]$TimeoutSeconds,
        [string]$EngineLogPath = "",
        [string]$WorkingDirectory = $ProjectRoot
    )
    $startedAt = [DateTime]::UtcNow
    $argumentString = Join-CommandLine -Arguments $Arguments
    $process = Start-Process -FilePath $FilePath `
        -ArgumentList $argumentString `
        -WorkingDirectory $WorkingDirectory `
        -RedirectStandardOutput $StdoutPath `
        -RedirectStandardError $StderrPath `
        -PassThru -WindowStyle Hidden
    $peakWorkingSet = 0L
    $loadedModules = [System.Collections.Generic.HashSet[string]]::new(
        [System.StringComparer]::OrdinalIgnoreCase
    )
    $deadline = $startedAt.AddSeconds($TimeoutSeconds)
    while (-not $process.HasExited -and [DateTime]::UtcNow -lt $deadline) {
        $ids = @($process.Id) + @(Get-DescendantProcessIds -RootProcessId $process.Id)
        foreach ($processId in $ids) {
            $sample = Get-Process -Id $processId -ErrorAction SilentlyContinue
            if ($null -ne $sample) {
                $peakWorkingSet = [Math]::Max($peakWorkingSet, [int64]$sample.WorkingSet64)
                try {
                    foreach ($module in $sample.Modules) {
                        if ($module.FileName) {
                            [void]$loadedModules.Add($module.FileName)
                        }
                    }
                }
                catch {
                    # Protected/system processes may refuse module enumeration.
                }
            }
        }
        Start-Sleep -Milliseconds 500
        $process.Refresh()
    }
    $timedOut = -not $process.HasExited
    $terminatedDescendants = @()
    if ($timedOut) {
        $terminatedDescendants = @(Stop-OwnedProcessTree -RootProcessId $process.Id)
    }
    $process.WaitForExit()
    $process.Refresh()
    $exitCode = $null
    if (-not $timedOut) {
        try {
            $exitCode = [int]$process.ExitCode
        }
        catch {
            $exitCode = $null
        }
    }
    $modulePaths = @($loadedModules | Sort-Object)
    $injectedCandidates = @(
        $modulePaths |
            Where-Object {
                -not $_.StartsWith($UnrealRoot, [System.StringComparison]::OrdinalIgnoreCase) -and
                -not $_.StartsWith($ProjectRoot, [System.StringComparison]::OrdinalIgnoreCase) -and
                -not $_.StartsWith($env:WINDIR, [System.StringComparison]::OrdinalIgnoreCase)
            }
    )
    return [ordered]@{
        name = $Name
        file_path = $FilePath
        arguments = $Arguments
        command_line = "$FilePath $argumentString"
        pid = $process.Id
        started_at_utc = $startedAt.ToString("o")
        finished_at_utc = [DateTime]::UtcNow.ToString("o")
        duration_seconds = [Math]::Round(([DateTime]::UtcNow - $startedAt).TotalSeconds, 3)
        timeout_seconds = $TimeoutSeconds
        timed_out = $timedOut
        process_exit_observed = [bool]$process.HasExited
        terminated_descendant_pids = $terminatedDescendants
        exit_code = $exitCode
        peak_working_set_mib = [Math]::Round($peakWorkingSet / 1MB, 3)
        loaded_module_paths = $modulePaths
        injected_module_candidates = $injectedCandidates
        stdout = $StdoutPath
        stderr = $StderrPath
        engine_log = $EngineLogPath
    }
}

function Assert-StageSucceeded {
    param([Parameter(Mandatory = $true)]$Stage)
    if ($Stage.timed_out -or -not $Stage.process_exit_observed) {
        throw "Stage did not exit cleanly: $($Stage.name)"
    }
    if ($null -ne $Stage.exit_code -and [int]$Stage.exit_code -ne 0) {
        throw "Stage exited nonzero: $($Stage.name) code=$($Stage.exit_code)"
    }
    $combined = ""
    foreach ($path in @($Stage.stdout, $Stage.stderr, $Stage.engine_log)) {
        if ($path -and (Test-Path -LiteralPath $path -PathType Leaf)) {
            $combined += [Environment]::NewLine + (Get-Content -LiteralPath $path -Raw)
        }
    }
    if ($combined -match "Fatal error|LowLevelFatalError|Assertion failed|Ensure condition failed|GPU Crash|DXGI_ERROR_DEVICE_|Out of video memory|Ran out of memory|LogPython: Error|Traceback \(most recent call last\)") {
        throw "Critical log signature in stage: $($Stage.name)"
    }
}

function Assert-CaptureRHIValidated {
    param([Parameter(Mandatory = $true)]$Stage)
    $combined = ""
    foreach ($path in @($Stage.stdout, $Stage.stderr, $Stage.engine_log)) {
        if ($path -and (Test-Path -LiteralPath $path -PathType Leaf)) {
            $combined += [Environment]::NewLine + (Get-Content -LiteralPath $path -Raw)
        }
    }
    if ($combined -notmatch "\[SkyguardP45LandscapeCapture\]\[RHI_VALIDATED\]\s+D3D12\|SM6") {
        throw "Capture stage did not prove active D3D12|SM6 before screenshots: $($Stage.name)"
    }
    if ($combined -match 'rhiname="Null"|RHI\.RHIName>Null<') {
        throw "Capture stage reported NullRHI: $($Stage.name)"
    }
}

function Wait-ForZeroHeavyProcesses {
    param([ValidateRange(1, 60)][int]$TimeoutSeconds = 30)
    $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
    do {
        $found = @(Get-ExactHeavyProcesses)
        if ($found.Count -eq 0) {
            return @()
        }
        Start-Sleep -Seconds 1
    } while ([DateTime]::UtcNow -lt $deadline)
    return @(Get-ExactHeavyProcesses)
}

function Get-CsvFiles {
    param([Parameter(Mandatory = $true)][string[]]$Roots)
    return @(
        Get-ChildItem -LiteralPath $Roots -File -Recurse -ErrorAction SilentlyContinue |
            Where-Object { $_.Extension -in @(".csv", ".gz") } |
            Select-Object -ExpandProperty FullName
    )
}

function Select-NewProfileCsv {
    param(
        [Parameter(Mandatory = $true)][string[]]$Before,
        [Parameter(Mandatory = $true)][string[]]$Roots
    )
    $newFiles = @(
        Get-CsvFiles -Roots $Roots |
            Where-Object { $Before -notcontains $_ } |
            ForEach-Object { Get-Item -LiteralPath $_ }
    )
    if ($newFiles.Count -eq 0) {
        throw "Measured profile produced no new CSV artifact"
    }
    return ($newFiles | Sort-Object Length, LastWriteTimeUtc -Descending | Select-Object -First 1).FullName
}

function Invoke-ProfileStage {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$Map,
        [Parameter(Mandatory = $true)][int]$Seconds,
        [Parameter(Mandatory = $true)][string]$LogsRoot,
        [Parameter(Mandatory = $true)][bool]$Measured,
        [Parameter(Mandatory = $true)][string]$ArtifactsRoot
    )
    $stdout = Join-Path $LogsRoot ($Name + ".stdout.log")
    $stderr = Join-Path $LogsRoot ($Name + ".stderr.log")
    $engineLog = Join-Path $LogsRoot ($Name + ".engine.log")
    $args = @(
        $ProjectFile,
        $Map,
        "-game",
        "-windowed",
        "-ResX=1920",
        "-ResY=1080",
        "-d3d12",
        "-sm6",
        "-NoVSync",
        "-benchmark",
        "-benchmarkseconds=$Seconds",
        "-fps=60",
        "-NoSplash",
        "-NoLoadingScreen",
        "-ExecCmds=r.SetRes 1920x1080w,r.ScreenPercentage 100,sg.ViewDistanceQuality 3,sg.ShadowQuality 3,sg.PostProcessQuality 3,sg.TextureQuality 3,sg.EffectsQuality 3,sg.FoliageQuality 3,BugItGo 22500 -9000 8500 -28 90 0",
        "-abslog=$engineLog"
    )
    if ($Measured) {
        $trace = Join-Path $ArtifactsRoot ($Name + ".utrace")
        $args += @(
            "-trace=cpu,gpu,frame,bookmark,loadtime,file,assetload",
            "-tracefile=$trace",
            "-tracefiletrunc",
            "-traceautostart=1",
            "-csvCaptureFrames=$($Seconds * 60)",
            "-csvCategories=Global",
            "-csvGpuStats",
            "-csvNamedEvents"
        )
    }
    return Invoke-BoundedProcess `
        -Name $Name `
        -FilePath $EditorExe `
        -Arguments $args `
        -StdoutPath $stdout `
        -StderrPath $stderr `
        -EngineLogPath $engineLog `
        -TimeoutSeconds $ProfileTimeoutSeconds
}

foreach ($required in @(
    $ProjectFile,
    $BuildTool,
    $EditorCmd,
    $EditorExe,
    $Builder,
    $EditorVerifier,
    $CaptureScript,
    $GateVerifier,
    $BaselineFile
)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
        throw "Required file is missing: $required"
    }
}
if ((Get-Sha256 -Path $BaselineFile) -ne $BaselineHash) {
    throw "Immutable baseline hash failed before supervisor start"
}
if (
    -not (Test-Path -LiteralPath $FailedAttemptFile -PathType Leaf) -or
    (Get-Sha256 -Path $FailedAttemptFile) -ne $FailedAttemptHash
) {
    throw "Immutable failed attempt01 evidence is missing or changed"
}
if (
    -not (Test-Path -LiteralPath $FailedAttempt02File -PathType Leaf) -or
    (Get-Sha256 -Path $FailedAttempt02File) -ne $FailedAttempt02Hash -or
    -not (Test-Path -LiteralPath $FailedAttempt02MaterialFile -PathType Leaf) -or
    (Get-Sha256 -Path $FailedAttempt02MaterialFile) -ne $FailedAttempt02MaterialHash
) {
    throw "Immutable failed attempt02 evidence is missing or changed"
}
if (
    -not (Test-Path -LiteralPath $FailedAttempt03File -PathType Leaf) -or
    (Get-Sha256 -Path $FailedAttempt03File) -ne $FailedAttempt03Hash -or
    -not (Test-Path -LiteralPath $FailedAttempt03MaterialFile -PathType Leaf) -or
    (Get-Sha256 -Path $FailedAttempt03MaterialFile) -ne $FailedAttempt03MaterialHash
) {
    throw "Immutable failed attempt03 evidence is missing or changed"
}
if (
    (Test-Path -LiteralPath $CandidateFile -PathType Leaf) -or
    (Test-Path -LiteralPath $CandidateMaterialFile -PathType Leaf)
) {
    if (
        -not (Test-Path -LiteralPath $CandidateFile -PathType Leaf) -or
        -not (Test-Path -LiteralPath $CandidateMaterialFile -PathType Leaf) -or
        (Get-Sha256 -Path $CandidateFile) -ne $CandidateAcceptedHash -or
        (Get-Sha256 -Path $CandidateMaterialFile) -ne $CandidateMaterialAcceptedHash
    ) {
        throw "Accepted immutable attempt04 candidate is incomplete or changed"
    }
}
$preflightHeavy = @(Get-ExactHeavyProcesses)
if ($preflightHeavy.Count -ne 0) {
    throw "Exclusive heavy lane is not free: $($preflightHeavy | ConvertTo-Json -Compress)"
}

New-Item -ItemType Directory -Force -Path $RunRoot, $ReportsRoot | Out-Null
$stamp = [DateTime]::UtcNow.ToString("yyyyMMddTHHmmssfffZ")
$AttemptRoot = Join-Path $RunRoot "attempt_$stamp"
$LogsRoot = Join-Path $AttemptRoot "logs"
$ArtifactsRoot = Join-Path $AttemptRoot "artifacts"
$BaselineCaptureRoot = Join-Path $ArtifactsRoot "captures\baseline"
$CandidateCaptureRoot = Join-Path $ArtifactsRoot "captures\candidate"
New-Item -ItemType Directory -Force -Path $AttemptRoot, $LogsRoot, $ArtifactsRoot | Out-Null

$ManifestPath = Join-Path $AttemptRoot "run_manifest.json"
$GatePath = Join-Path $AttemptRoot "gate_report.json"
$ReceiptPath = Join-Path $AttemptRoot "supervisor_receipt.json"
$baselineBefore = Get-Sha256 -Path $BaselineFile
$manifest = [ordered]@{
    schema = "skyguard.phase4.m01-landscape-visible-supervisor.v1"
    contract_id = $ContractId
    attempt_id = "attempt_$stamp"
    created_at_utc = [DateTime]::UtcNow.ToString("o")
    project_root = $ProjectRoot
    baseline_map = $BaselineMap
    candidate_map = $CandidateMap
    baseline_sha256_before = $baselineBefore
    baseline_sha256_after = $null
    candidate_sha256_before = if (Test-Path -LiteralPath $CandidateFile) { Get-Sha256 -Path $CandidateFile } else { $null }
    candidate_sha256_after = $null
    candidate_material_sha256_before = if (Test-Path -LiteralPath $CandidateMaterialFile) { Get-Sha256 -Path $CandidateMaterialFile } else { $null }
    candidate_material_sha256_after = $null
    controls = [ordered]@{
        sequential_processes_only = $true
        warmup_seconds = 30
        measured_seconds = 60
        profile_process_timeout_seconds = $ProfileTimeoutSeconds
        maximum_total_gpu_lane_minutes = 8
        pcg_generation_allowed = $false
        fab_quixel_import_allowed = $false
        network_download_allowed = $false
        prior_nullrhi_overlap_is_performance_evidence = $false
        gpu_capture_host = "normal_editor_execute_python"
        gpu_capture_requires_runtime_rhi_marker = "D3D12|SM6"
    }
    stages = @()
    artifacts = [ordered]@{
        baseline_capture_root = $BaselineCaptureRoot
        candidate_capture_root = $CandidateCaptureRoot
        baseline_csv = $null
        candidate_csv = $null
        editor_acceptance = $EditorAcceptance
    }
    terminal_state = "RUNNING"
    errors = @()
}
Save-Json -Value $manifest -Path $ManifestPath
$gpuLaneStartedAt = $null

try {
    if (-not $SkipBuild) {
        $stage = Invoke-BoundedProcess `
            -Name "build_skyguard52_editor" `
            -FilePath $BuildTool `
            -Arguments @("Skyguard52Editor", "Win64", "Development", "-Project=$ProjectFile", "-WaitMutex", "-NoHotReload") `
            -StdoutPath (Join-Path $LogsRoot "build.stdout.log") `
            -StderrPath (Join-Path $LogsRoot "build.stderr.log") `
            -TimeoutSeconds $BuildTimeoutSeconds
        $manifest.stages += $stage
        Save-Json -Value $manifest -Path $ManifestPath
        Assert-StageSucceeded -Stage $stage
    }

    if (
        -not (Test-Path -LiteralPath $CandidateFile -PathType Leaf) -and
        (Test-Path -LiteralPath $CandidateMaterialFile -PathType Leaf)
    ) {
        throw "Partial immutable attempt detected: candidate material exists without candidate map. Do not overwrite; govern attempt02."
    }
    if (-not (Test-Path -LiteralPath $CandidateFile -PathType Leaf)) {
        $stage = Invoke-BoundedProcess `
            -Name "author_immutable_candidate" `
            -FilePath $EditorCmd `
            -Arguments @($ProjectFile, "-run=pythonscript", "-script=$Builder", "-unattended", "-nop4", "-NoSplash", "-NullRHI") `
            -StdoutPath (Join-Path $LogsRoot "candidate_build.stdout.log") `
            -StderrPath (Join-Path $LogsRoot "candidate_build.stderr.log") `
            -TimeoutSeconds $EditorTimeoutSeconds
        $manifest.stages += $stage
        Save-Json -Value $manifest -Path $ManifestPath
        Assert-StageSucceeded -Stage $stage
    }

    $stage = Invoke-BoundedProcess `
        -Name "verify_immutable_candidate" `
        -FilePath $EditorCmd `
        -Arguments @($ProjectFile, "-run=pythonscript", "-script=$EditorVerifier", "-unattended", "-nop4", "-NoSplash", "-NullRHI") `
        -StdoutPath (Join-Path $LogsRoot "candidate_verify.stdout.log") `
        -StderrPath (Join-Path $LogsRoot "candidate_verify.stderr.log") `
        -TimeoutSeconds $EditorTimeoutSeconds
    $manifest.stages += $stage
    Save-Json -Value $manifest -Path $ManifestPath
    Assert-StageSucceeded -Stage $stage
    $editorReport = Get-Content -LiteralPath $EditorAcceptance -Raw | ConvertFrom-Json
    if ($editorReport.gate -ne "PASS") {
        throw "Fresh-process candidate acceptance did not pass"
    }

    $gpuLaneStartedAt = [DateTime]::UtcNow
    foreach ($captureSpec in @(
        [ordered]@{ mode = "baseline"; map = $BaselineMap; root = $BaselineCaptureRoot },
        [ordered]@{ mode = "candidate"; map = $CandidateMap; root = $CandidateCaptureRoot }
    )) {
        $name = "$($captureSpec.mode)_capture"
        $engineLog = Join-Path $LogsRoot ($name + ".engine.log")
        $stage = Invoke-BoundedProcess `
            -Name $name `
            -FilePath $EditorExe `
            -Arguments @(
                $ProjectFile,
                $captureSpec.map,
                "-ExecutePythonScript=$CaptureScript",
                "-ScriptErrorsAreFatal",
                "-SkyguardReviewMode=$($captureSpec.mode)",
                "-SkyguardReviewMap=$($captureSpec.map)",
                "-SkyguardReviewOutput=$($captureSpec.root)",
                "-unattended",
                "-nop4",
                "-NoSplash",
                "-RenderOffscreen",
                "-windowed",
                "-ResX=1920",
                "-ResY=1080",
                "-d3d12",
                "-sm6",
                "-NoVSync",
                "-stdout",
                "-FullStdOutLogOutput",
                "-abslog=$engineLog",
                "-ExecCmds=r.ScreenPercentage 100,sg.ViewDistanceQuality 3,sg.ShadowQuality 3,sg.PostProcessQuality 3,sg.TextureQuality 3,sg.EffectsQuality 3,sg.FoliageQuality 3"
            ) `
            -StdoutPath (Join-Path $LogsRoot ($name + ".stdout.log")) `
            -StderrPath (Join-Path $LogsRoot ($name + ".stderr.log")) `
            -EngineLogPath $engineLog `
            -TimeoutSeconds $EditorTimeoutSeconds
        $manifest.stages += $stage
        Save-Json -Value $manifest -Path $ManifestPath
        Assert-StageSucceeded -Stage $stage
        Assert-CaptureRHIValidated -Stage $stage
    }

    $expectedCapturePaths = @()
    foreach ($cameraId in @("C01_ROUTE_WIDE", "C02_SHORE_APPROACH", "C03_SHORE_GRAZE", "C04_INLAND_CLOSE", "C05_COVERAGE_HIGH")) {
        $expectedCapturePaths += Join-Path $BaselineCaptureRoot "baseline_lit_$cameraId.png"
        $expectedCapturePaths += Join-Path $CandidateCaptureRoot "candidate_lit_$cameraId.png"
    }
    $expectedCapturePaths += @(
        (Join-Path $CandidateCaptureRoot "candidate_diagnostic_landscape_lod_C05.png"),
        (Join-Path $CandidateCaptureRoot "candidate_diagnostic_shader_complexity_C04.png"),
        (Join-Path $CandidateCaptureRoot "candidate_diagnostic_component_boundary_C05.png")
    )
    $captureDeadline = [DateTime]::UtcNow.AddSeconds(30)
    while ([DateTime]::UtcNow -lt $captureDeadline) {
        $missing = @($expectedCapturePaths | Where-Object { -not (Test-Path -LiteralPath $_ -PathType Leaf) })
        if ($missing.Count -eq 0) {
            break
        }
        Start-Sleep -Seconds 1
    }
    $missing = @($expectedCapturePaths | Where-Object { -not (Test-Path -LiteralPath $_ -PathType Leaf) })
    if ($missing.Count -ne 0) {
        throw "Required governed captures are missing: $($missing -join ', ')"
    }

    $CsvRoots = @(
        (Join-Path $ProjectRoot "Saved\Profiling"),
        (Join-Path $env:LOCALAPPDATA "UnrealEngine\5.8\Saved\Profiling\CSV")
    )
    foreach ($profile in @(
        [ordered]@{ mode = "baseline"; map = $BaselineMap },
        [ordered]@{ mode = "candidate"; map = $CandidateMap }
    )) {
        $warmName = "$($profile.mode)_profile_warmup"
        $stage = Invoke-ProfileStage -Name $warmName -Map $profile.map -Seconds 30 -LogsRoot $LogsRoot -Measured $false -ArtifactsRoot $ArtifactsRoot
        $manifest.stages += $stage
        Save-Json -Value $manifest -Path $ManifestPath
        Assert-StageSucceeded -Stage $stage

        $csvBefore = @(Get-CsvFiles -Roots $CsvRoots)
        $measuredName = "$($profile.mode)_profile_measured"
        $stage = Invoke-ProfileStage -Name $measuredName -Map $profile.map -Seconds 60 -LogsRoot $LogsRoot -Measured $true -ArtifactsRoot $ArtifactsRoot
        $manifest.stages += $stage
        Save-Json -Value $manifest -Path $ManifestPath
        Assert-StageSucceeded -Stage $stage
        $selectedCsv = Select-NewProfileCsv -Before $csvBefore -Roots $CsvRoots
        if ($profile.mode -eq "baseline") {
            $manifest.artifacts.baseline_csv = $selectedCsv
        }
        else {
            $manifest.artifacts.candidate_csv = $selectedCsv
        }
        Save-Json -Value $manifest -Path $ManifestPath
        if (([DateTime]::UtcNow - $gpuLaneStartedAt).TotalMinutes -gt 8) {
            throw "Exclusive GPU lane exceeded the governed eight-minute ceiling"
        }
    }

    $baselineAfter = Get-Sha256 -Path $BaselineFile
    $manifest.baseline_sha256_after = $baselineAfter
    if ($baselineAfter -ne $BaselineHash -or $baselineAfter -ne $baselineBefore) {
        throw "Immutable baseline changed during the visible GPU gate"
    }
    $manifest.candidate_sha256_after = Get-Sha256 -Path $CandidateFile
    $manifest.candidate_material_sha256_after = Get-Sha256 -Path $CandidateMaterialFile
    if (
        $manifest.candidate_sha256_after -ne $CandidateAcceptedHash -or
        $manifest.candidate_material_sha256_after -ne $CandidateMaterialAcceptedHash
    ) {
        throw "Accepted immutable attempt04 candidate changed during the visible GPU gate"
    }
    $manifest.terminal_state = "EVIDENCE_COMPLETE"
    Save-Json -Value $manifest -Path $ManifestPath

    $python = (Get-Command python -ErrorAction Stop).Source
    $verifyStage = Invoke-BoundedProcess `
        -Name "verify_visible_gpu_gate" `
        -FilePath $python `
        -Arguments @($GateVerifier, "--manifest", $ManifestPath, "--output", $GatePath, "--latest-output", $LatestGate) `
        -StdoutPath (Join-Path $LogsRoot "gate_verify.stdout.log") `
        -StderrPath (Join-Path $LogsRoot "gate_verify.stderr.log") `
        -TimeoutSeconds 60
    $manifest.stages += $verifyStage
    if (Test-Path -LiteralPath $GatePath -PathType Leaf) {
        $gateReport = Get-Content -LiteralPath $GatePath -Raw | ConvertFrom-Json
        $manifest.terminal_state = $gateReport.gate
    }
    else {
        $manifest.terminal_state = "FAIL"
        $manifest.errors += "Gate verifier did not produce a report"
    }
    Save-Json -Value $manifest -Path $ManifestPath
}
catch {
    $manifest.terminal_state = "FAIL"
    $manifest.errors += $_.Exception.Message
    if (Test-Path -LiteralPath $BaselineFile -PathType Leaf) {
        $manifest.baseline_sha256_after = Get-Sha256 -Path $BaselineFile
    }
    if (Test-Path -LiteralPath $CandidateFile -PathType Leaf) {
        $manifest.candidate_sha256_after = Get-Sha256 -Path $CandidateFile
    }
    if (Test-Path -LiteralPath $CandidateMaterialFile -PathType Leaf) {
        $manifest.candidate_material_sha256_after = Get-Sha256 -Path $CandidateMaterialFile
    }
    Save-Json -Value $manifest -Path $ManifestPath
}
finally {
    $remaining = @(Wait-ForZeroHeavyProcesses -TimeoutSeconds 30)
    $gpuHealthEvents = @()
    try {
        $eventStart = [DateTime]::Parse($manifest.created_at_utc).ToLocalTime()
        $gpuHealthEvents = @(
            Get-WinEvent -FilterHashtable @{
                LogName = "Application"
                StartTime = $eventStart
            } -ErrorAction SilentlyContinue |
                Where-Object {
                    $_.ProviderName -in @("Application Error", "Windows Error Reporting", "Display", "nvlddmkm") -and
                    $_.Message -match "UnrealEditor|Skyguard52|DXGI|GPU|nvlddmkm|amdwddmg"
                } |
                Select-Object -First 20 TimeCreated, Id, ProviderName, LevelDisplayName, Message
        )
    }
    catch {
        $gpuHealthEvents = @()
    }
    $injectedModuleCandidates = @(
        $manifest.stages |
            ForEach-Object { @($_.injected_module_candidates) } |
            Where-Object { $_ } |
            Sort-Object -Unique
    )
    $receipt = [ordered]@{
        schema = "skyguard.phase4.m01-landscape-visible-supervisor-receipt.v1"
        contract_id = $ContractId
        attempt_id = $manifest.attempt_id
        finished_at_utc = [DateTime]::UtcNow.ToString("o")
        terminal_state = $manifest.terminal_state
        baseline_sha256_before = $manifest.baseline_sha256_before
        baseline_sha256_after = $manifest.baseline_sha256_after
        exact_heavy_processes_remaining = $remaining
        exact_heavy_process_count = $remaining.Count
        injected_module_candidates = $injectedModuleCandidates
        gpu_health_event_count = $gpuHealthEvents.Count
        gpu_health_events = $gpuHealthEvents
        manifest = $ManifestPath
        gate_report = $GatePath
    }
    if ($remaining.Count -ne 0) {
        $manifest.terminal_state = "FAIL"
        $manifest.errors += "Postflight exact heavy processes did not drain"
        Save-Json -Value $manifest -Path $ManifestPath
        $receipt.terminal_state = "FAIL"
    }
    Save-Json -Value $receipt -Path $ReceiptPath
}

if ($manifest.terminal_state -eq "PASS") {
    exit 0
}
if ($manifest.terminal_state -eq "INCOMPLETE_HUMAN_REVIEW") {
    exit 2
}
exit 1
