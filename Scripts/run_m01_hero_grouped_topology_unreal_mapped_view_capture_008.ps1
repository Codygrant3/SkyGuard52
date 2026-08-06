[CmdletBinding()]
param(
    [string]$ProjectRoot = "D:\Skyguard52",
    [string]$UnrealRoot = "D:\UE_5.8",
    [ValidateRange(120, 900)]
    [int]$TimeoutSeconds = 420
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$BuildId = "BLD_M01_HERO_GROUPED_TOPOLOGY_008"
$ExpectedPersistenceHash = "2bd9bbaf4750d57d3a3b9ca92dde14995a5b84d4332294a2ce61bfd690d8f185"
$ExpectedCandidateReceiptHash = "50dc373729c801cfb91be84bcde0b8e5a79142cf4e542d0691dc7e77a340d131"
$AttemptRoot = Join-Path $ProjectRoot "Saved\BuildAttempts\M01_HERO_GROUPED_TOPOLOGY_UNREAL_008\attempt_20260802T173639559Z"
$CaptureRoot = Join-Path $AttemptRoot "mapped_view_capture_02"
$ProjectFile = Join-Path $ProjectRoot "Skyguard52.uproject"
$EditorExe = Join-Path $UnrealRoot "Engine\Binaries\Win64\UnrealEditor.exe"
$CaptureScript = Join-Path $ProjectRoot "Scripts\capture_m01_hero_grouped_topology_unreal_mapped_views_008.py"
$PersistenceReport = Join-Path $ProjectRoot "Saved\Reports\M01_HERO_GROUPED_TOPOLOGY_UNREAL_CANDIDATE_008_PERSISTENCE.json"
$CandidateReceipt = Join-Path $AttemptRoot "receipt.json"
$ReviewMap = "/Game/Skyguard/Candidates/Mission01/HeroGroupedTopology_008/Review/Lvl_M01_HeroGroupedTopology_008_Review"
$StdoutPath = Join-Path $AttemptRoot "mapped_view_capture_02.stdout.log"
$StderrPath = Join-Path $AttemptRoot "mapped_view_capture_02.stderr.log"
$EngineLogPath = Join-Path $AttemptRoot "mapped_view_capture_02.engine.log"
$SupervisorReceipt = Join-Path $AttemptRoot "mapped_view_capture_02_supervisor_receipt.json"
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
    foreach ($processId in $descendants) {
        Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
    }
    Stop-Process -Id $RootProcessId -Force -ErrorAction SilentlyContinue
    return @($descendants)
}

if (-not (Test-Path -LiteralPath $EditorExe -PathType Leaf)) {
    throw "UnrealEditor.exe is missing: $EditorExe"
}
foreach ($path in @($ProjectFile, $CaptureScript, $PersistenceReport, $CandidateReceipt)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "Required input is missing: $path"
    }
}
if ((Get-Sha256 $PersistenceReport) -ne $ExpectedPersistenceHash) {
    throw "Fresh persistence report hash mismatch"
}
if ((Get-Sha256 $CandidateReceipt) -ne $ExpectedCandidateReceiptHash) {
    throw "Successful candidate receipt hash mismatch"
}
foreach ($path in @($CaptureRoot, $StdoutPath, $StderrPath, $EngineLogPath, $SupervisorReceipt)) {
    if (Test-Path -LiteralPath $path) {
        throw "Immutable mapped-view attempt output already exists: $path"
    }
}
$heavy = @(Get-Process -ErrorAction SilentlyContinue |
    Where-Object { $HeavyNames -contains $_.ProcessName } |
    Select-Object Id, ProcessName, StartTime)
if ($heavy.Count -ne 0) {
    throw "Mapped-view lane requires zero heavy processes: $($heavy | ConvertTo-Json -Compress)"
}
$os = Get-CimInstance Win32_OperatingSystem
$freePhysicalGiB = [Math]::Round(([double]$os.FreePhysicalMemory * 1KB) / 1GB, 3)
if ($freePhysicalGiB -lt 24.0) {
    throw "Mapped-view lane requires at least 24 GiB free RAM; found $freePhysicalGiB"
}

$arguments = @(
    $ProjectFile,
    $ReviewMap,
    "-ExecutePythonScript=$CaptureScript",
    "-ScriptErrorsAreFatal",
    "-SkyguardMappedViewMap=$ReviewMap",
    "-SkyguardMappedViewOutput=$CaptureRoot",
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
    "-abslog=$EngineLogPath",
    "-ExecCmds=r.ScreenPercentage 100,sg.ViewDistanceQuality 3,sg.ShadowQuality 3,sg.PostProcessQuality 3,sg.TextureQuality 3,sg.EffectsQuality 3"
)
$startedAt = [DateTime]::UtcNow
$process = Start-Process `
    -FilePath $EditorExe `
    -ArgumentList (Join-CommandLine $arguments) `
    -WorkingDirectory $ProjectRoot `
    -RedirectStandardOutput $StdoutPath `
    -RedirectStandardError $StderrPath `
    -PassThru `
    -WindowStyle Hidden
$deadline = $startedAt.AddSeconds($TimeoutSeconds)
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
$terminatedDescendants = @()
if ($timedOut) {
    $terminatedDescendants = @(Stop-OwnedProcessTree -RootProcessId $process.Id)
}
$process.WaitForExit()
$process.Refresh()
$exitCode = if ($timedOut) { $null } else { [int]$process.ExitCode }

$combined = ""
foreach ($path in @($StdoutPath, $StderrPath, $EngineLogPath)) {
    if (Test-Path -LiteralPath $path -PathType Leaf) {
        $combined += [Environment]::NewLine + (Get-Content -LiteralPath $path -Raw)
    }
}
$criticalPattern = "Fatal error|LowLevelFatalError|Assertion failed|Ensure condition failed|GPU Crash|DXGI_ERROR_DEVICE_|Out of video memory|Ran out of memory|LogPython: Error|Traceback \(most recent call last\)"
$rhiValidated = $combined -match "\[M01Grouped008Capture\]\[RHI_VALIDATED\]\s+D3D12\|SM6"
$capturePassed = $combined -match "PASS_UNREAL_MAPPED_VIEW_CAPTURE_AWAITING_ORIGINAL_RESOLUTION_REVIEW"
$criticalSignature = $combined -match $criticalPattern
$manifestPath = Join-Path $CaptureRoot "capture_manifest.json"
$manifestExists = Test-Path -LiteralPath $manifestPath -PathType Leaf
$pngs = if (Test-Path -LiteralPath $CaptureRoot -PathType Container) {
    @(Get-ChildItem -LiteralPath $CaptureRoot -File -Filter "*.png")
} else {
    @()
}
$gate = if (
    -not $timedOut -and
    $exitCode -eq 0 -and
    $rhiValidated -and
    $capturePassed -and
    -not $criticalSignature -and
    $manifestExists -and
    $pngs.Count -eq 9
) {
    "PASS_CAPTURE_COMPLETE_AWAITING_ORIGINAL_RESOLUTION_REVIEW"
} else {
    "FAIL_CLOSED_CAPTURE_NOT_ACCEPTED"
}
$receipt = [ordered]@{
    schema = "skyguard.m01.hero-grouped-topology-unreal-mapped-capture-supervisor.v1"
    gate = $gate
    build_id = $BuildId
    started_at_utc = $startedAt.ToString("o")
    finished_at_utc = [DateTime]::UtcNow.ToString("o")
    preflight = [ordered]@{
        persistence_sha256 = Get-Sha256 $PersistenceReport
        candidate_receipt_sha256 = Get-Sha256 $CandidateReceipt
        heavy_process_count = $heavy.Count
        free_physical_gib = $freePhysicalGiB
    }
    process = [ordered]@{
        pid = $process.Id
        exit_code = $exitCode
        timed_out = $timedOut
        terminated_descendant_pids = $terminatedDescendants
        peak_working_set_mib = [Math]::Round($peakWorkingSet / 1MB, 3)
        stdout = $StdoutPath
        stderr = $StderrPath
        engine_log = $EngineLogPath
    }
    checks = [ordered]@{
        rhi_d3d12_sm6_validated = $rhiValidated
        script_pass_marker = $capturePassed
        critical_log_signature_absent = -not $criticalSignature
        manifest_exists = $manifestExists
        exact_nine_pngs = $pngs.Count -eq 9
    }
    capture_manifest = if ($manifestExists) {
        [ordered]@{
            path = $manifestPath
            sha256 = Get-Sha256 $manifestPath
        }
    } else {
        $null
    }
    promotion_allowed = $false
    p3_4_closed = $false
}
$receipt | ConvertTo-Json -Depth 12 |
    Set-Content -LiteralPath $SupervisorReceipt -Encoding UTF8
if ($gate -ne "PASS_CAPTURE_COMPLETE_AWAITING_ORIGINAL_RESOLUTION_REVIEW") {
    throw "Mapped-view capture failed closed. See $SupervisorReceipt"
}
Write-Output ($receipt | ConvertTo-Json -Depth 12)
