[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][switch]$AuthorizeSingleRecovery04Run,
    [Parameter(Mandatory = $true)]
    [ValidatePattern("^[0-9a-fA-F]{64}$")]
    [string]$ExpectedExecutionContractSha256,
    [string]$ProjectRoot = "D:\Skyguard52",
    [string]$UnrealRoot = "D:\UE_5.8",
    [ValidateRange(300, 1800)][int]$TimeoutSeconds = 1200
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
if (-not $AuthorizeSingleRecovery04Run) {
    throw "Explicit -AuthorizeSingleRecovery04Run is required."
}
$ExecutionContractPath = Join-Path $ProjectRoot "Docs\AAA_Review\M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_RECOVERY04_EXECUTION_CONTRACT.json"
$RecoveryContractPath = Join-Path $ProjectRoot "Docs\AAA_Review\M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_RECOVERY04_CONTRACT.json"
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
    (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}
function Quote-Argument {
    param([Parameter(Mandatory = $true)][string]$Value)
    if ($Value -notmatch '[\s"]') { return $Value }
    '"' + ($Value -replace '(\\*)"', '$1$1\"' -replace '(\\+)$', '$1$1') + '"'
}
function Join-Arguments {
    param([Parameter(Mandatory = $true)][string[]]$Values)
    (($Values | ForEach-Object { Quote-Argument $_ }) -join " ")
}
function Get-DescendantProcessIds {
    param([Parameter(Mandatory = $true)][int]$RootProcessId)
    $all = @(Get-CimInstance Win32_Process | Select-Object ProcessId, ParentProcessId)
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
    @($found)
}
function Stop-OwnedProcessTree {
    param([Parameter(Mandatory = $true)][int]$RootProcessId)
    $descendants = @(Get-DescendantProcessIds -RootProcessId $RootProcessId)
    [array]::Reverse($descendants)
    foreach ($ownedId in $descendants) {
        Stop-Process -Id $ownedId -Force -ErrorAction SilentlyContinue
    }
    Stop-Process -Id $RootProcessId -Force -ErrorAction SilentlyContinue
    @($descendants)
}
function Get-TreeHashMap {
    param(
        [Parameter(Mandatory = $true)][string]$RootPath,
        [string[]]$Suffixes = @()
    )
    $result = [ordered]@{}
    if (Test-Path -LiteralPath $RootPath -PathType Container) {
        foreach ($file in @(Get-ChildItem -LiteralPath $RootPath -Recurse -File | Sort-Object FullName)) {
            if ($Suffixes.Count -gt 0 -and $Suffixes -notcontains $file.Extension.ToLowerInvariant()) {
                continue
            }
            $relative = $file.FullName.Substring($ProjectRoot.Length).TrimStart("\").Replace("\", "/")
            $result[$relative] = Get-Sha256 $file.FullName
        }
    }
    $result
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
        -ArgumentList (Join-Arguments $Arguments) -WorkingDirectory $ProjectRoot `
        -RedirectStandardOutput $Stdout -RedirectStandardError $Stderr `
        -PassThru -WindowStyle Hidden
    $finished = $process.WaitForExit($BoundSeconds * 1000)
    $terminated = @()
    if (-not $finished) {
        $terminated = @(Stop-OwnedProcessTree -RootProcessId $process.Id)
        $process.WaitForExit()
    }
    $process.Refresh()
    [ordered]@{
        pid = $process.Id
        exit_code = if ($finished) { [int]$process.ExitCode } else { $null }
        timed_out = -not $finished
        terminated_descendant_pids = $terminated
        started_at_utc = $started.ToString("o")
        finished_at_utc = [DateTime]::UtcNow.ToString("o")
        stdout = $Stdout
        stderr = $Stderr
    }
}

foreach ($required in @($ExecutionContractPath, $RecoveryContractPath, $ProjectFile, $EditorExe)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
        throw "Missing Recovery04 input: $required"
    }
}
$actualExecutionHash = Get-Sha256 $ExecutionContractPath
if ($actualExecutionHash -ne $ExpectedExecutionContractSha256.ToLowerInvariant()) {
    throw "Recovery04 execution contract hash mismatch; Unreal was not launched."
}
$execution = Get-Content -LiteralPath $ExecutionContractPath -Raw | ConvertFrom-Json
if ($execution.authorization.authorize_switch -ne "AuthorizeSingleRecovery04Run" -or
    $execution.promotion_allowed -ne $false -or $execution.p3_4_closed -ne $false) {
    throw "Recovery04 execution policy mismatch."
}
foreach ($record in $execution.bound_files.PSObject.Properties.Value) {
    $path = Join-Path $ProjectRoot $record.path
    if (-not (Test-Path -LiteralPath $path -PathType Leaf) -or
        (Get-Item -LiteralPath $path).Length -ne [int64]$record.bytes -or
        (Get-Sha256 $path) -ne $record.sha256) {
        throw "Recovery04 bound-file mismatch: $path"
    }
}

$AttemptRoot = Join-Path $ProjectRoot $execution.outputs.attempt_root
$CaptureRoot = Join-Path $ProjectRoot $execution.outputs.capture_root
$SupervisorReceipt = Join-Path $ProjectRoot $execution.outputs.supervisor_receipt
$Preflight = Join-Path $AttemptRoot "preflight_snapshot.json"
$ExecutionAudit = Join-Path $AttemptRoot "execution_audit.json"
$CaptureScript = Join-Path $ProjectRoot $execution.bound_files.recovery_capture.path
$Auditor = Join-Path $ProjectRoot $execution.bound_files.execution_auditor.path
$Readiness = Join-Path $ProjectRoot $execution.bound_files.readiness_auditor.path
if (Test-Path -LiteralPath $AttemptRoot) {
    throw "Immutable Recovery04 output exists: $AttemptRoot"
}
$heavy = @(Get-Process -ErrorAction SilentlyContinue | Where-Object { $HeavyNames -contains $_.ProcessName })
if ($heavy.Count -ne 0) {
    throw "Recovery04 requires zero heavy processes."
}
$os = Get-CimInstance Win32_OperatingSystem
$freeGiB = [Math]::Round(([double]$os.FreePhysicalMemory * 1KB) / 1GB, 3)
if ($freeGiB -lt [double]$execution.resource_preflight.minimum_free_physical_gib) {
    throw "Recovery04 has only $freeGiB GiB free RAM."
}
$readinessText = & $Python $Readiness 2>&1
if ($LASTEXITCODE -ne 0 -or
    ($readinessText -join "`n") -notmatch
    "PASS_OFFLINE_READY_AWAITING_SEPARATE_RECOVERY04_AUTHORIZATION") {
    throw "Recovery04 readiness failed; Unreal was not launched."
}

$original = Get-TreeHashMap `
    -RootPath (Join-Path $ProjectRoot "Content\Skyguard\Candidates\Mission01\HeroGroupedTopology_008") `
    -Suffixes @(".uasset", ".umap")
$attempt03 = Get-TreeHashMap `
    -RootPath (Join-Path $ProjectRoot "Content\Skyguard\Candidates\Mission01\HeroGroupedTopology_008_Attempt03") `
    -Suffixes @(".uasset", ".umap")
$runtime = Get-TreeHashMap -RootPath (Join-Path $ProjectRoot "Content\Skyguard\Maps") -Suffixes @(".uasset", ".umap")
$config = Get-TreeHashMap -RootPath (Join-Path $ProjectRoot "Config")
if ($attempt03.Count -ne 1) {
    throw "Recovery04 requires exactly one pre-existing review-map package."
}
New-Item -ItemType Directory -Path $AttemptRoot | Out-Null
[ordered]@{
    schema = "skyguard.m01.hero-grouped-topology-attempt03-recovery04-preflight.v1"
    execution_contract_sha256 = $actualExecutionHash
    recovery_contract_sha256 = Get-Sha256 $RecoveryContractPath
    heavy_process_count = $heavy.Count
    free_physical_gib = $freeGiB
    original_candidate_packages = $original
    attempt03_packages = $attempt03
    runtime_map_packages = $runtime
    config_files = $config
    promotion_allowed = $false
    p3_4_closed = $false
} | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $Preflight -Encoding UTF8

$UnrealOut = Join-Path $AttemptRoot "unreal.stdout.log"
$UnrealErr = Join-Path $AttemptRoot "unreal.stderr.log"
$EngineLog = Join-Path $AttemptRoot "unreal.engine.log"
$AuditorOut = Join-Path $AttemptRoot "auditor.stdout.log"
$AuditorErr = Join-Path $AttemptRoot "auditor.stderr.log"
$unrealProcess = $null
$auditorProcess = $null
try {
    $unrealProcess = Invoke-Bounded -FilePath $EditorExe -Arguments @(
        $ProjectFile, "-ExecutePythonScript=$CaptureScript", "-ScriptErrorsAreFatal",
        "-SkyguardAttempt03Recovery04Output=$CaptureRoot",
        "-SkyguardAttempt03Recovery04ReviewMap=$($execution.review_map)",
        "-unattended", "-nop4", "-NoSplash", "-RenderOffscreen", "-windowed",
        "-ResX=2048", "-ResY=2048", "-d3d12", "-sm6", "-NoVSync",
        "-stdout", "-FullStdOutLogOutput", "-abslog=$EngineLog",
        "-NoAssetRegistryCache",
        "-ExecCmds=r.ScreenPercentage 100,sg.ViewDistanceQuality 3,sg.ShadowQuality 3,sg.PostProcessQuality 3,sg.TextureQuality 3,sg.EffectsQuality 3"
    ) -Stdout $UnrealOut -Stderr $UnrealErr -BoundSeconds $TimeoutSeconds
    $combined = ""
    foreach ($log in @($UnrealOut, $UnrealErr, $EngineLog)) {
        if (Test-Path -LiteralPath $log) { $combined += "`n" + (Get-Content -LiteralPath $log -Raw) }
    }
    $critical = $combined -match "Fatal error|LowLevelFatalError|Assertion failed|GPU Crash|DXGI_ERROR_DEVICE_|Out of video memory|LogPython: Error|Traceback \(most recent call last\)"
    $rhi = $combined -match "\[M01Grouped008Attempt03Capture\]\[RHI_VALIDATED\]\s+D3D12\|SM6"
    $marker = $combined -match "PASS_RECOVERY04_NINE_VIEWS_AWAITING_OFFLINE_AUDIT"
    $PilotReceipt = Join-Path $CaptureRoot "pilot_receipt.json"
    $Manifest = Join-Path $CaptureRoot "capture_manifest.json"
    $pilotPngs = if (Test-Path (Join-Path $CaptureRoot "pilot")) {
        @(Get-ChildItem (Join-Path $CaptureRoot "pilot") -Filter "*.png" -File)
    } else { @() }
    $fullPngs = if (Test-Path (Join-Path $CaptureRoot "full_views")) {
        @(Get-ChildItem (Join-Path $CaptureRoot "full_views") -Filter "*.png" -File)
    } else { @() }
    if ($unrealProcess.timed_out -or $unrealProcess.exit_code -ne 0 -or
        -not $rhi -or -not $marker -or $critical -or
        -not (Test-Path $PilotReceipt) -or -not (Test-Path $Manifest) -or
        $pilotPngs.Count -ne 6 -or $fullPngs.Count -ne 9) {
        throw "Recovery04 base-lighting capture failed closed."
    }
    $pilot = Get-Content $PilotReceipt -Raw | ConvertFrom-Json
    if ($pilot.gate -ne "PASS_RECOVERY04_BASE_LIGHTING_LIVE_EXPOSURE_SELECTED_FULL_VIEWS_ALLOWED") {
        throw "Recovery04 pilot gate failed."
    }
    $auditorProcess = Invoke-Bounded -FilePath $Python -Arguments @(
        $Auditor, "--preflight", $Preflight, "--capture-manifest", $Manifest,
        "--output", $ExecutionAudit
    ) -Stdout $AuditorOut -Stderr $AuditorErr -BoundSeconds 180
    if ($auditorProcess.timed_out -or $auditorProcess.exit_code -ne 0 -or
        -not (Test-Path $ExecutionAudit)) {
        throw "Recovery04 audit failed closed."
    }
    $audit = Get-Content $ExecutionAudit -Raw | ConvertFrom-Json
    if ($audit.gate -ne "PASS_RECOVERY04_EXECUTION_AWAITING_ORIGINAL_RESOLUTION_REVIEW") {
        throw "Recovery04 audit gate mismatch."
    }
    $remaining = @(Get-Process -ErrorAction SilentlyContinue | Where-Object { $HeavyNames -contains $_.ProcessName })
    if ($remaining.Count -ne 0) { throw "Heavy process remained after Recovery04." }
    $receipt = [ordered]@{
        schema = "skyguard.m01.hero-grouped-topology-unreal-mapped-attempt03-recovery04-supervisor.v1"
        gate = "PASS_RECOVERY04_EXECUTION_AWAITING_ORIGINAL_RESOLUTION_REVIEW"
        execution_contract_sha256 = $actualExecutionHash
        unreal_process = $unrealProcess
        auditor_process = $auditorProcess
        checks = [ordered]@{
            exactly_one_unreal_process = $true
            exact_base_lighting_lifecycle = $true
            pilot_passed_before_full_views = $true
            exact_6_pilot_pngs = $pilotPngs.Count -eq 6
            exact_9_full_view_pngs = $fullPngs.Count -eq 9
            rhi_d3d12_sm6 = $rhi
            critical_log_absent = -not $critical
        }
        promotion_allowed = $false
        p3_4_closed = $false
        next_gate = "original-resolution review of nine Recovery04 images"
    }
    $receipt | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $SupervisorReceipt -Encoding UTF8
    Write-Output ($receipt | ConvertTo-Json -Depth 20)
} catch {
    [ordered]@{
        schema = "skyguard.m01.hero-grouped-topology-unreal-mapped-attempt03-recovery04-supervisor.v1"
        gate = "FAIL_CLOSED_RECOVERY04_NOT_ACCEPTED"
        failure = $_.Exception.Message
        execution_contract_sha256 = $actualExecutionHash
        unreal_process = $unrealProcess
        auditor_process = $auditorProcess
        promotion_allowed = $false
        p3_4_closed = $false
    } | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $SupervisorReceipt -Encoding UTF8
    throw
}
