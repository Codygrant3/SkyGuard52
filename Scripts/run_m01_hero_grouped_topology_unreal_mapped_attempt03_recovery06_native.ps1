[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [switch]$AuthorizeSingleRecovery06NativeRun,
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

if (-not $AuthorizeSingleRecovery06NativeRun) {
    throw "Explicit -AuthorizeSingleRecovery06NativeRun is required."
}

$ContractPath = Join-Path $ProjectRoot (
    "Docs\AAA_Review\" +
    "M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_" +
    "RECOVERY06_NATIVE_EXECUTION_CONTRACT.json"
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

function Get-TreeHashMap {
    param(
        [Parameter(Mandatory = $true)][string]$RootPath,
        [string[]]$Suffixes = @()
    )
    $result = [ordered]@{}
    if (Test-Path -LiteralPath $RootPath -PathType Container) {
        foreach ($file in @(
            Get-ChildItem -LiteralPath $RootPath -Recurse -File |
                Sort-Object FullName
        )) {
            if ($Suffixes.Count -gt 0 -and
                $Suffixes -notcontains $file.Extension.ToLowerInvariant()) {
                continue
            }
            $relative = $file.FullName.Substring($ProjectRoot.Length).
                TrimStart("\").Replace("\", "/")
            $result[$relative] = Get-Sha256 $file.FullName
        }
    }
    $result
}

function Assert-SourceInventory {
    param([Parameter(Mandatory = $true)][object]$Inventory)
    $actualFiles = @(
        Get-ChildItem -LiteralPath (Join-Path $ProjectRoot "Source") `
            -Recurse -File | Sort-Object FullName
    )
    if ($actualFiles.Count -ne @($Inventory.files).Count) {
        throw "Recovery06 source inventory count changed."
    }
    foreach ($record in @($Inventory.files)) {
        $path = Join-Path $ProjectRoot $record.file
        if (-not (Test-Path -LiteralPath $path -PathType Leaf) -or
            (Get-Item -LiteralPath $path).Length -ne [int64]$record.bytes -or
            (Get-Sha256 $path) -ne $record.sha256) {
            throw "Recovery06 source inventory mismatch: $path"
        }
    }
}

foreach ($required in @($ContractPath, $ProjectFile, $EditorExe)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
        throw "Missing Recovery06 native input: $required"
    }
}

$actualContractHash = Get-Sha256 $ContractPath
if ($actualContractHash -ne
    $ExpectedExecutionContractSha256.ToLowerInvariant()) {
    throw "Recovery06 execution contract hash mismatch; Unreal was not launched."
}
$execution = Get-Content -LiteralPath $ContractPath -Raw | ConvertFrom-Json
if ($execution.authorization.authorize_switch -ne
        "AuthorizeSingleRecovery06NativeRun" -or
    $execution.promotion_allowed -ne $false -or
    $execution.p3_4_closed -ne $false) {
    throw "Recovery06 execution policy mismatch."
}

foreach ($record in $execution.bound_files.PSObject.Properties.Value) {
    $path = Join-Path $ProjectRoot $record.path
    if (-not (Test-Path -LiteralPath $path -PathType Leaf) -or
        (Get-Item -LiteralPath $path).Length -ne [int64]$record.bytes -or
        (Get-Sha256 $path) -ne $record.sha256) {
        throw "Recovery06 bound-file mismatch: $path"
    }
}

$activationPath = Join-Path $ProjectRoot `
    $execution.bound_files.compile_activation.path
$activation = Get-Content -LiteralPath $activationPath -Raw |
    ConvertFrom-Json
if ($activation.gate -ne "PASS_FULL_SKYGUARD52EDITOR_MODULE_COMPILE" -or
    $activation.build_exit_code -ne 0 -or
    $activation.compiled_module.sha256 -ne
        $execution.bound_files.compiled_module.sha256) {
    throw "Recovery06 compile activation gate mismatch."
}
$inventoryPath = Join-Path $ProjectRoot `
    $execution.bound_files.source_inventory.path
$inventory = Get-Content -LiteralPath $inventoryPath -Raw |
    ConvertFrom-Json
Assert-SourceInventory -Inventory $inventory

$AttemptRoot = Join-Path $ProjectRoot $execution.outputs.attempt_root
$CaptureRoot = Join-Path $ProjectRoot $execution.outputs.capture_root
$SupervisorReceipt = Join-Path $ProjectRoot `
    $execution.outputs.supervisor_receipt
$Preflight = Join-Path $AttemptRoot "preflight_snapshot.json"
if (Test-Path -LiteralPath $AttemptRoot) {
    throw "Immutable Recovery06 output exists: $AttemptRoot"
}

$heavy = @(
    Get-Process -ErrorAction SilentlyContinue |
        Where-Object { $HeavyNames -contains $_.ProcessName }
)
if ($heavy.Count -ne 0) {
    throw "Recovery06 requires zero heavy processes."
}
$os = Get-CimInstance Win32_OperatingSystem
$freeGiB = [Math]::Round(
    ([double]$os.FreePhysicalMemory * 1KB) / 1GB,
    3
)
if ($freeGiB -lt
    [double]$execution.resource_preflight.minimum_free_physical_gib) {
    throw "Recovery06 has only $freeGiB GiB free RAM."
}

$original = Get-TreeHashMap `
    -RootPath (Join-Path $ProjectRoot (
        "Content\Skyguard\Candidates\Mission01\HeroGroupedTopology_008"
    )) -Suffixes @(".uasset", ".umap")
$attempt03 = Get-TreeHashMap `
    -RootPath (Join-Path $ProjectRoot (
        "Content\Skyguard\Candidates\Mission01\" +
        "HeroGroupedTopology_008_Attempt03"
    )) -Suffixes @(".uasset", ".umap")
$runtime = Get-TreeHashMap `
    -RootPath (Join-Path $ProjectRoot "Content\Skyguard\Maps") `
    -Suffixes @(".uasset", ".umap")
$config = Get-TreeHashMap -RootPath (Join-Path $ProjectRoot "Config")
if ($attempt03.Count -ne 1) {
    throw "Recovery06 requires exactly one governed review-map package."
}

New-Item -ItemType Directory -Path $AttemptRoot | Out-Null
[ordered]@{
    schema = (
        "skyguard.m01.hero-grouped-topology-attempt03-" +
        "recovery06-native-preflight.v1"
    )
    execution_contract_sha256 = $actualContractHash
    compile_activation_sha256 = (
        $execution.bound_files.compile_activation.sha256
    )
    compiled_module_sha256 = (
        $execution.bound_files.compiled_module.sha256
    )
    source_inventory_sha256 = (
        $execution.bound_files.source_inventory.sha256
    )
    source_inventory_unchanged = $true
    heavy_process_count = $heavy.Count
    free_physical_gib = $freeGiB
    original_candidate_packages = $original
    attempt03_packages = $attempt03
    runtime_map_packages = $runtime
    config_files = $config
    promotion_allowed = $false
    p3_4_closed = $false
} | ConvertTo-Json -Depth 20 |
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
            "-SkyguardM01Recovery05ContractId=" +
            $execution.native_runtime.required_contract_id
        ),
        (
            "-SkyguardM01Recovery05ExpectedMap=" +
            $execution.review_map
        ),
        "-SkyguardM01Recovery05Output=$CaptureRoot",
        "-unattended", "-nop4", "-NoSplash", "-RenderOffscreen",
        "-windowed", "-ResX=2048", "-ResY=2048",
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
    $CaptureReceipt = Join-Path $CaptureRoot "capture_receipt.json"
    if ($unrealProcess.timed_out -or $unrealProcess.exit_code -ne 0 -or
        $critical -or
        -not (Test-Path -LiteralPath $CaptureReceipt -PathType Leaf)) {
        throw "Recovery06 native viewport capture failed closed."
    }

    $capture = Get-Content -LiteralPath $CaptureReceipt -Raw |
        ConvertFrom-Json
    $pilotPngs = @(
        Get-ChildItem -LiteralPath (Join-Path $CaptureRoot "pilot") `
            -Filter "*.png" -File
    )
    $fullPngs = @(
        Get-ChildItem -LiteralPath (Join-Path $CaptureRoot "full_views") `
            -Filter "*.png" -File
    )
    $fullHashes = @($fullPngs | ForEach-Object { Get-Sha256 $_.FullName })
    if ($capture.gate -ne
            "PASS_RECOVERY05_NATIVE_CAPTURE_AWAITING_OFFLINE_AUDIT" -or
        $capture.contract_id -ne
            $execution.native_runtime.required_contract_id -or
        $capture.map -ne $execution.review_map -or
        $capture.native_frame_driven_capture -ne $true -or
        $capture.python_scene_capture_used -ne $false -or
        $capture.world_saved -ne $false -or
        $capture.package_save_invoked -ne $false -or
        $pilotPngs.Count -ne 3 -or $fullPngs.Count -ne 9 -or
        @($fullHashes | Select-Object -Unique).Count -ne 9 -or
        @($capture.pilot_captures |
            Where-Object { $_.liveness_passed -ne $true }).Count -ne 0 -or
        @($capture.full_view_captures |
            Where-Object { $_.hard_bounds_passed -ne $true }).Count -ne 0) {
        throw "Recovery06 native capture receipt failed acceptance."
    }

    $postOriginal = Get-TreeHashMap `
        -RootPath (Join-Path $ProjectRoot (
            "Content\Skyguard\Candidates\Mission01\HeroGroupedTopology_008"
        )) -Suffixes @(".uasset", ".umap")
    $postAttempt03 = Get-TreeHashMap `
        -RootPath (Join-Path $ProjectRoot (
            "Content\Skyguard\Candidates\Mission01\" +
            "HeroGroupedTopology_008_Attempt03"
        )) -Suffixes @(".uasset", ".umap")
    $postRuntime = Get-TreeHashMap `
        -RootPath (Join-Path $ProjectRoot "Content\Skyguard\Maps") `
        -Suffixes @(".uasset", ".umap")
    $postConfig = Get-TreeHashMap `
        -RootPath (Join-Path $ProjectRoot "Config")
    if (($original | ConvertTo-Json -Compress) -ne
            ($postOriginal | ConvertTo-Json -Compress) -or
        ($attempt03 | ConvertTo-Json -Compress) -ne
            ($postAttempt03 | ConvertTo-Json -Compress) -or
        ($runtime | ConvertTo-Json -Compress) -ne
            ($postRuntime | ConvertTo-Json -Compress) -or
        ($config | ConvertTo-Json -Compress) -ne
            ($postConfig | ConvertTo-Json -Compress)) {
        throw "Recovery06 package or config immutability failed."
    }
    Assert-SourceInventory -Inventory $inventory
    $remaining = @(
        Get-Process -ErrorAction SilentlyContinue |
            Where-Object { $HeavyNames -contains $_.ProcessName }
    )
    if ($remaining.Count -ne 0) {
        throw "Heavy process remained after Recovery06."
    }

    $receipt = [ordered]@{
        schema = (
            "skyguard.m01.hero-grouped-topology-unreal-mapped-" +
            "attempt03-recovery06-native-supervisor.v1"
        )
        gate = (
            "PASS_RECOVERY06_NATIVE_EXECUTION_" +
            "AWAITING_ORIGINAL_RESOLUTION_REVIEW"
        )
        execution_contract_sha256 = $actualContractHash
        compile_activation_sha256 = (
            $execution.bound_files.compile_activation.sha256
        )
        compiled_module_sha256 = (
            $execution.bound_files.compiled_module.sha256
        )
        unreal_process = $unrealProcess
        capture_receipt = $CaptureReceipt
        capture_receipt_sha256 = Get-Sha256 $CaptureReceipt
        checks = [ordered]@{
            exactly_one_unreal_process = $true
            source_inventory_unchanged = $true
            exact_3_live_pilot_pngs = $pilotPngs.Count -eq 3
            exact_9_unique_hard_bound_views = (
                $fullPngs.Count -eq 9 -and
                @($fullHashes | Select-Object -Unique).Count -eq 9
            )
            native_frame_driven_capture = $true
            python_scene_capture_used = $false
            package_runtime_config_unchanged = $true
            critical_log_absent = -not $critical
        }
        promotion_allowed = $false
        p3_4_closed = $false
        next_gate = "original-resolution review of nine Recovery06 images"
    }
    $receipt | ConvertTo-Json -Depth 20 |
        Set-Content -LiteralPath $SupervisorReceipt -Encoding UTF8
    Write-Output ($receipt | ConvertTo-Json -Depth 20)
} catch {
    [ordered]@{
        schema = (
            "skyguard.m01.hero-grouped-topology-unreal-mapped-" +
            "attempt03-recovery06-native-supervisor.v1"
        )
        gate = "FAIL_CLOSED_RECOVERY06_NATIVE_NOT_ACCEPTED"
        failure = $_.Exception.Message
        execution_contract_sha256 = $actualContractHash
        compile_activation_sha256 = (
            $execution.bound_files.compile_activation.sha256
        )
        compiled_module_sha256 = (
            $execution.bound_files.compiled_module.sha256
        )
        unreal_process = $unrealProcess
        promotion_allowed = $false
        p3_4_closed = $false
    } | ConvertTo-Json -Depth 20 |
        Set-Content -LiteralPath $SupervisorReceipt -Encoding UTF8
    throw
}
