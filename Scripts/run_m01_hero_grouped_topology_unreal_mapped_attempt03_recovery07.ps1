[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [switch]$AuthorizeSingleRecovery07Run,
    [Parameter(Mandatory = $true)]
    [ValidatePattern("^[0-9a-fA-F]{64}$")]
    [string]$ExpectedExecutionContractSha256,
    [string]$ProjectRoot = "D:\Skyguard52",
    [string]$UnrealRoot = "D:\UE_5.8",
    [ValidateRange(300, 900)]
    [int]$TimeoutSeconds = 600
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
if (-not $AuthorizeSingleRecovery07Run) {
    throw "Explicit -AuthorizeSingleRecovery07Run is required."
}

$ContractPath = Join-Path $ProjectRoot (
    "Docs\AAA_Review\" +
    "M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_" +
    "RECOVERY07_EXECUTION_CONTRACT.json"
)
$ProjectFile = Join-Path $ProjectRoot "Skyguard52.uproject"
$EditorExe = Join-Path $UnrealRoot "Engine\Binaries\Win64\UnrealEditor.exe"
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
        -RedirectStandardOutput $Stdout `
        -RedirectStandardError $Stderr `
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

foreach ($required in @($ContractPath, $ProjectFile, $EditorExe)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
        throw "Missing post-build Recovery07 input: $required"
    }
}
$actualHash = Get-Sha256 $ContractPath
if ($actualHash -ne $ExpectedExecutionContractSha256.ToLowerInvariant()) {
    throw "Recovery07 execution contract hash mismatch; Unreal was not launched."
}
$execution = Get-Content -LiteralPath $ContractPath -Raw | ConvertFrom-Json
if ($execution.authorization.authorize_switch -ne
        "AuthorizeSingleRecovery07Run" -or
    $execution.post_build_activation_bound -ne $true -or
    $execution.promotion_allowed -ne $false -or
    $execution.p3_4_closed -ne $false) {
    throw "Recovery07 post-build execution policy mismatch."
}
foreach ($record in $execution.bound_files.PSObject.Properties.Value) {
    $path = Join-Path $ProjectRoot $record.path
    if (-not (Test-Path -LiteralPath $path -PathType Leaf) -or
        (Get-Item -LiteralPath $path).Length -ne [int64]$record.bytes -or
        (Get-Sha256 $path) -ne $record.sha256) {
        throw "Recovery07 bound-file mismatch: $path"
    }
}

$AttemptRoot = Join-Path $ProjectRoot $execution.outputs.attempt_root
$CaptureRoot = Join-Path $ProjectRoot $execution.outputs.capture_root
$SupervisorReceipt = Join-Path $ProjectRoot `
    $execution.outputs.supervisor_receipt
if (Test-Path -LiteralPath $AttemptRoot) {
    throw "Immutable Recovery07 output exists: $AttemptRoot"
}
$heavy = @(
    Get-Process -ErrorAction SilentlyContinue |
        Where-Object { $HeavyNames -contains $_.ProcessName }
)
if ($heavy.Count -ne 0) {
    throw "Recovery07 requires zero heavy processes."
}
$os = Get-CimInstance Win32_OperatingSystem
$freeGiB = [Math]::Round(
    ([double]$os.FreePhysicalMemory * 1KB) / 1GB,
    3
)
if ($freeGiB -lt [double]$execution.resource_preflight.minimum_free_physical_gib) {
    throw "Recovery07 has only $freeGiB GiB free RAM."
}

New-Item -ItemType Directory -Path $AttemptRoot | Out-Null
$Preflight = Join-Path $AttemptRoot "preflight_snapshot.json"
[ordered]@{
    schema = "skyguard.m01.hero-grouped-topology-recovery07-preflight.v1"
    execution_contract_sha256 = $actualHash
    compiled_module_sha256 = $execution.bound_files.compiled_module.sha256
    heavy_process_count = $heavy.Count
    free_physical_gib = $freeGiB
    promotion_allowed = $false
    p3_4_closed = $false
} | ConvertTo-Json -Depth 10 |
    Set-Content -LiteralPath $Preflight -Encoding UTF8

$UnrealOut = Join-Path $AttemptRoot "unreal.stdout.log"
$UnrealErr = Join-Path $AttemptRoot "unreal.stderr.log"
$EngineLog = Join-Path $AttemptRoot "unreal.engine.log"
$unrealProcess = $null
try {
    $unrealProcess = Invoke-Bounded -FilePath $EditorExe -Arguments @(
        $ProjectFile,
        $execution.review_map,
        "-game",
        (
            "-SkyguardM01Recovery07ContractId=" +
            $execution.native_runtime.required_contract_id
        ),
        "-SkyguardM01Recovery07ExpectedMap=$($execution.review_map)",
        "-SkyguardM01Recovery07Output=$CaptureRoot",
        "-unattended", "-nop4", "-NoSplash", "-RenderOffscreen",
        "-windowed", "-ForceRes", "-ResX=2048", "-ResY=2048",
        "-d3d12", "-sm6", "-NoVSync",
        "-stdout", "-FullStdOutLogOutput", "-abslog=$EngineLog",
        "-NoAssetRegistryCache",
        (
            "-ExecCmds=r.ScreenPercentage 100," +
            "sg.ViewDistanceQuality 3,sg.ShadowQuality 3," +
            "sg.PostProcessQuality 3,sg.TextureQuality 3," +
            "sg.EffectsQuality 3"
        )
    ) -Stdout $UnrealOut -Stderr $UnrealErr `
        -BoundSeconds $TimeoutSeconds

    $CaptureReceipt = Join-Path $CaptureRoot "capture_receipt.json"
    $combined = ""
    foreach ($log in @($UnrealOut, $UnrealErr, $EngineLog)) {
        if (Test-Path -LiteralPath $log) {
            $combined += "`n" + (Get-Content -LiteralPath $log -Raw)
        }
    }
    $critical = $combined -match (
        "Fatal error|LowLevelFatalError|Assertion failed|GPU Crash|" +
        "DXGI_ERROR_DEVICE_|Out of video memory"
    )
    if ($unrealProcess.timed_out -or $unrealProcess.exit_code -ne 0 -or
        $critical -or
        -not (Test-Path -LiteralPath $CaptureReceipt -PathType Leaf)) {
        throw "Recovery07 high-resolution native capture failed closed."
    }
    $capture = Get-Content -LiteralPath $CaptureReceipt -Raw |
        ConvertFrom-Json
    $pilot = @($capture.pilot_captures)
    $views = @($capture.full_view_captures)
    $viewFiles = @(
        Get-ChildItem -LiteralPath (Join-Path $CaptureRoot "full_views") `
            -Filter "*.png" -File
    )
    $viewHashes = @($viewFiles | ForEach-Object { Get-Sha256 $_.FullName })
    if ($capture.gate -ne
            "PASS_RECOVERY07_HIGHRES_CAPTURE_AWAITING_OFFLINE_AUDIT" -or
        $capture.live_viewport_resolution_independent -ne $true -or
        $capture.required_output_width -ne 2048 -or
        $capture.required_output_height -ne 2048 -or
        $pilot.Count -ne 3 -or $views.Count -ne 9 -or
        @($pilot | Where-Object {
            $_.width -ne 2048 -or $_.height -ne 2048 -or
            $_.liveness_passed -ne $true
        }).Count -ne 0 -or
        @($views | Where-Object {
            $_.width -ne 2048 -or $_.height -ne 2048 -or
            $_.hard_bounds_passed -ne $true
        }).Count -ne 0 -or
        @($viewHashes | Select-Object -Unique).Count -ne 9 -or
        $combined -notmatch "\[RECOVERY07\]\[STATE\]" -or
        $combined -notmatch "\[RECOVERY07\]\[CAPTURE_CALLBACK\]") {
        throw "Recovery07 receipt or diagnostic acceptance failed."
    }
    $remaining = @(
        Get-Process -ErrorAction SilentlyContinue |
            Where-Object { $HeavyNames -contains $_.ProcessName }
    )
    if ($remaining.Count -ne 0) {
        throw "Heavy process remained after Recovery07."
    }
    $receipt = [ordered]@{
        schema = (
            "skyguard.m01.hero-grouped-topology-" +
            "recovery07-supervisor.v1"
        )
        gate = (
            "PASS_RECOVERY07_EXECUTION_" +
            "AWAITING_ORIGINAL_RESOLUTION_REVIEW"
        )
        execution_contract_sha256 = $actualHash
        unreal_process = $unrealProcess
        capture_receipt = $CaptureReceipt
        capture_receipt_sha256 = Get-Sha256 $CaptureReceipt
        exact_2048_highres_callback_count = 12
        unique_full_view_hash_count = 9
        promotion_allowed = $false
        p3_4_closed = $false
    }
    $receipt | ConvertTo-Json -Depth 20 |
        Set-Content -LiteralPath $SupervisorReceipt -Encoding UTF8
    Write-Output ($receipt | ConvertTo-Json -Depth 20)
} catch {
    [ordered]@{
        schema = (
            "skyguard.m01.hero-grouped-topology-" +
            "recovery07-supervisor.v1"
        )
        gate = "FAIL_CLOSED_RECOVERY07_NOT_ACCEPTED"
        failure = $_.Exception.Message
        execution_contract_sha256 = $actualHash
        unreal_process = $unrealProcess
        promotion_allowed = $false
        p3_4_closed = $false
    } | ConvertTo-Json -Depth 20 |
        Set-Content -LiteralPath $SupervisorReceipt -Encoding UTF8
    throw
}
