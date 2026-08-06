[CmdletBinding()]
param(
    [string]$ProjectRoot = "D:\Skyguard52",
    [string]$UnrealRoot = "D:\UE_5.8",
    [string]$MissionMatrix = "D:\Skyguard52\Docs\AAA_Review\PHASE8_MISSION_SOAK_MATRIX.json",
    [string]$ProvenanceLedger = "D:\Skyguard52\Saved\Reports\M01_TEXTURE_MATERIAL_PROVENANCE_LEDGER.json",
    [string]$RuntimeValidationReceipt = "",
    [ValidateRange(300, 14400)]
    [int]$PackageTimeoutSeconds = 3600,
    [ValidateRange(60, 3600)]
    [int]$MissionTimeoutPaddingSeconds = 180,
    [ValidateRange(30, 1800)]
    [int]$ShippingSmokeSeconds = 120,
    [ValidateSet("Engineering", "AAA", "FriendFacing")]
    [string]$ReleaseTier = "Engineering",
    [bool]$EngineeringAudioException = $true,
    [switch]$SkipDevelopmentPackage,
    [switch]$SkipShippingPackage,
    [switch]$SkipMissionSoak,
    [switch]$RunRuntimeValidation,
    [switch]$ValidateOnly
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$ProjectFile = Join-Path $ProjectRoot "Skyguard52.uproject"
$RunUat = Join-Path $UnrealRoot "Engine\Build\BatchFiles\RunUAT.bat"
$Verifier = Join-Path $ProjectRoot "Scripts\verify_skyguard_phase8_release_gate.py"
$Phase8Root = Join-Path $ProjectRoot "Saved\Releases\Phase8"
$ReportsRoot = Join-Path $ProjectRoot "Saved\Reports"
$DefaultInput = Join-Path $ProjectRoot "Config\DefaultInput.ini"
$DefaultEngine = Join-Path $ProjectRoot "Config\DefaultEngine.ini"
$DefaultGame = Join-Path $ProjectRoot "Config\DefaultGame.ini"
$SourceRoot = Join-Path $ProjectRoot "Source\Skyguard52"
$CookContractVerifier = Join-Path $ProjectRoot "Scripts\verify_skyguard_phase8_cook_contract.py"
$RuntimeValidationSupervisor = Join-Path $ProjectRoot "Scripts\run_skyguard_phase8_runtime_validation.ps1"
$ReleaseTierVerifier = Join-Path $ProjectRoot "Scripts\verify_skyguard_phase8_release_tier.py"
$EffectiveEngineeringAudioException = [bool](
    $ReleaseTier -eq "Engineering" -and $EngineeringAudioException
)

function ConvertTo-CommandLineArgument {
    param([Parameter(Mandatory = $true)][string]$Value)
    if ($Value -notmatch '[\s"]') { return $Value }
    return '"' + ($Value -replace '(\\*)"', '$1$1\"' -replace '(\\+)$', '$1$1') + '"'
}

function Join-CommandLine {
    param([Parameter(Mandatory = $true)][string[]]$Arguments)
    return (($Arguments | ForEach-Object { ConvertTo-CommandLineArgument $_ }) -join " ")
}

function Get-DescendantProcessIds {
    param([Parameter(Mandatory = $true)][int]$RootProcessId)
    $all = @(Get-CimInstance Win32_Process | Select-Object ProcessId, ParentProcessId)
    $result = [System.Collections.Generic.List[int]]::new()
    $queue = [System.Collections.Generic.Queue[int]]::new()
    $queue.Enqueue($RootProcessId)
    while ($queue.Count -gt 0) {
        $parentId = $queue.Dequeue()
        foreach ($candidate in $all) {
            if ([int]$candidate.ParentProcessId -eq $parentId) {
                $childId = [int]$candidate.ProcessId
                $result.Add($childId)
                $queue.Enqueue($childId)
            }
        }
    }
    return @($result)
}

function Stop-ExactProcessTree {
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
        [string]$WorkingDirectory = $ProjectRoot
    )
    $started = [DateTime]::UtcNow
    $argumentString = Join-CommandLine $Arguments
    $process = Start-Process -FilePath $FilePath -ArgumentList $argumentString `
        -WorkingDirectory $WorkingDirectory -RedirectStandardOutput $StdoutPath `
        -RedirectStandardError $StderrPath -PassThru -WindowStyle Hidden
    $timedOut = -not $process.WaitForExit($TimeoutSeconds * 1000)
    $terminated = @()
    if ($timedOut) {
        $terminated = @(Stop-ExactProcessTree $process.Id)
        $process.WaitForExit()
    }
    else {
        $process.WaitForExit()
    }
    $process.Refresh()
    $exitCode = $null
    if (-not $timedOut -and $process.HasExited) {
        try { $exitCode = [int]$process.ExitCode } catch { $exitCode = $null }
    }
    return [ordered]@{
        name = $Name
        file_path = $FilePath
        arguments = $Arguments
        command_line = "$FilePath $argumentString"
        pid = $process.Id
        started_at_utc = $started.ToString("o")
        finished_at_utc = [DateTime]::UtcNow.ToString("o")
        duration_seconds = [Math]::Round(([DateTime]::UtcNow - $started).TotalSeconds, 3)
        timeout_seconds = $TimeoutSeconds
        timed_out = $timedOut
        process_exit_observed = [bool]$process.HasExited
        terminated_descendant_pids = $terminated
        exit_code = $exitCode
        stdout = $StdoutPath
        stderr = $StderrPath
    }
}

function Save-Json {
    param($Value, [string]$Path)
    $Value | ConvertTo-Json -Depth 15 | Set-Content -LiteralPath $Path -Encoding UTF8
}

function Get-PortableSha256 {
    param([Parameter(Mandatory = $true)][string]$LiteralPath)
    $resolvedPath = (Resolve-Path -LiteralPath $LiteralPath -ErrorAction Stop).Path
    $stream = [System.IO.File]::Open(
        $resolvedPath,
        [System.IO.FileMode]::Open,
        [System.IO.FileAccess]::Read,
        [System.IO.FileShare]::Read
    )
    $sha256 = [System.Security.Cryptography.SHA256]::Create()
    try {
        $hashBytes = $sha256.ComputeHash($stream)
        return ([System.BitConverter]::ToString($hashBytes)).Replace("-", "").ToLowerInvariant()
    }
    finally {
        $sha256.Dispose()
        $stream.Dispose()
    }
}

function Get-HarnessSelfChecks {
    param([Parameter(Mandatory = $true)][string]$ScratchRoot)
    $probePath = Join-Path $ScratchRoot "sha256_self_test.bin"
    $engineConfigText = if (Test-Path -LiteralPath $DefaultEngine -PathType Leaf) {
        Get-Content -LiteralPath $DefaultEngine -Raw
    } else { "" }
    try {
        [System.IO.File]::WriteAllBytes(
            $probePath,
            [System.Text.Encoding]::ASCII.GetBytes("abc")
        )
        $knownHash = Get-PortableSha256 -LiteralPath $probePath
        [System.IO.File]::WriteAllBytes(
            $probePath,
            [System.Text.Encoding]::ASCII.GetBytes("abcd")
        )
        $tamperedHash = Get-PortableSha256 -LiteralPath $probePath
        return [ordered]@{
            portable_sha256_known_vector = (
                $knownHash -eq "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
            )
            sha256_changes_after_tamper = ($knownHash -ne $tamperedHash)
            frame_range_config_parse_safe = (
                $engineConfigText -notmatch
                    "SmoothedFrameRateRange=\(LowerBound=[^()]+,UpperBound=[^()]+\)"
            )
            known_vector_sha256 = $knownHash
            tampered_sha256 = $tamperedHash
        }
    }
    finally {
        Remove-Item -LiteralPath $probePath -Force -ErrorAction SilentlyContinue
    }
}

function Get-SourceStaticReceipt {
    $inputText = if (Test-Path -LiteralPath $DefaultInput) {
        Get-Content -LiteralPath $DefaultInput -Raw
    } else { "" }
    $gunnerPath = Join-Path $SourceRoot "SkyguardGunner.cpp"
    $gunnerText = if (Test-Path -LiteralPath $gunnerPath) {
        Get-Content -LiteralPath $gunnerPath -Raw
    } else { "" }
    $sourceFiles = @(Get-ChildItem -LiteralPath $SourceRoot -File -Filter "*.cpp" -ErrorAction SilentlyContinue)
    $allSource = ($sourceFiles | ForEach-Object { Get-Content -LiteralPath $_.FullName -Raw }) -join "`n"
    $requiredActions = @("Fire", "ADS", "SwitchWeapon", "LaunchIgla")
    $requiredAxes = @("Turn", "LookUp")
    $actionChecks = [ordered]@{}
    foreach ($action in $requiredActions) {
        $actionChecks[$action] = (
            $inputText -match "ActionName=`"$action`"" -and
            $gunnerText.Contains("BindAction(TEXT(`"$action`")")
        )
    }
    $axisChecks = [ordered]@{}
    foreach ($axis in $requiredAxes) {
        $axisChecks[$axis] = (
            $inputText -match "AxisName=`"$axis`"" -and
            $gunnerText.Contains("BindAxis(TEXT(`"$axis`")")
        )
    }
    return [ordered]@{
        input = [ordered]@{
            action_checks = $actionChecks
            axis_checks = $axisChecks
            config = $DefaultInput
            implementation = $gunnerPath
        }
        save = [ordered]@{
            save_game_class = $allSource -match "USkyguardCampaignSaveGame"
            builds_save_object = $allSource -match "BuildSaveGame"
            disk_save_call = $allSource -match "SaveGameToSlot|AsyncSaveGameToSlot"
            disk_load_call = $allSource -match "LoadGameFromSlot|AsyncLoadGameFromSlot"
        }
        settings = [ordered]@{
            game_user_settings = $allSource -match "UGameUserSettings|GameUserSettings"
            apply_settings = $allSource -match "ApplySettings"
            persist_settings = $allSource -match "SaveSettings"
        }
        shader_pso = [ordered]@{
            enabled_in_config = (
                (Test-Path -LiteralPath $DefaultEngine) -and
                ((Get-Content -LiteralPath $DefaultEngine -Raw) -match "ShaderPipelineCache")
            )
            source_cache_count = @(
                Get-ChildItem -LiteralPath @(
                    (Join-Path $ProjectRoot "Build"),
                    (Join-Path $ProjectRoot "Content"),
                    (Join-Path $ProjectRoot "Config")
                ) -Recurse -File -ErrorAction SilentlyContinue |
                    Where-Object { $_.Extension -in @(".upipelinecache", ".spc", ".stablepc.csv") }
            ).Count
        }
    }
}

function Get-CrashSnapshot {
    $roots = @(
        (Join-Path $ProjectRoot "Saved\Crashes"),
        (Join-Path $env:LOCALAPPDATA "CrashReportClient\Saved\Crashes")
    )
    return @(
        Get-ChildItem -LiteralPath $roots -Recurse -File -ErrorAction SilentlyContinue |
            ForEach-Object { "$($_.FullName)|$($_.Length)|$($_.LastWriteTimeUtc.Ticks)" }
    )
}

function Get-PackageExecutable {
    param([string]$ArchiveRoot)
    return Get-ChildItem -LiteralPath $ArchiveRoot -Recurse -File -Filter "Skyguard52.exe" `
        -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -match "[\\/]Windows[\\/]" } |
        Sort-Object FullName |
        Select-Object -First 1
}

New-Item -ItemType Directory -Force -Path $Phase8Root, $ReportsRoot | Out-Null
$stamp = [DateTime]::UtcNow.ToString("yyyyMMddTHHmmssfffZ")
$attemptId = "attempt_$stamp"
$attemptRoot = Join-Path $Phase8Root $attemptId
$logsRoot = Join-Path $attemptRoot "logs"
$packagesRoot = Join-Path $attemptRoot "packages"
$artifactsRoot = Join-Path $attemptRoot "artifacts"
New-Item -ItemType Directory -Force -Path $attemptRoot, $logsRoot, $packagesRoot, $artifactsRoot | Out-Null
$shippingSmokeReceipt = Join-Path $artifactsRoot "shipping_startup_smoke_receipt.json"

$manifestPath = Join-Path $attemptRoot "run_manifest.json"
$gatePath = Join-Path $attemptRoot "gate_report.json"
$latestPath = Join-Path $ReportsRoot "PHASE8_RELEASE_GATE_LATEST.json"

$manifest = [ordered]@{
    schema = "skyguard.phase8.release-run.v1"
    attempt_id = $attemptId
    created_at_utc = [DateTime]::UtcNow.ToString("o")
    project_root = $ProjectRoot
    project_file = $ProjectFile
    unreal_root = $UnrealRoot
    controls = [ordered]@{
        skip_development_package = [bool]$SkipDevelopmentPackage
        skip_shipping_package = [bool]$SkipShippingPackage
        skip_mission_soak = [bool]$SkipMissionSoak
        run_runtime_validation = [bool]$RunRuntimeValidation
        validate_only = [bool]$ValidateOnly
        package_timeout_seconds = $PackageTimeoutSeconds
        mission_timeout_padding_seconds = $MissionTimeoutPaddingSeconds
        shipping_smoke_seconds = $ShippingSmokeSeconds
        release_tier = $ReleaseTier
        engineering_audio_exception = $EffectiveEngineeringAudioException
    }
    mission_matrix = $MissionMatrix
    provenance_ledger = $ProvenanceLedger
    runtime_validation_receipt = $RuntimeValidationReceipt
    release_tier_receipt = $null
    shipping_smoke_receipt = $shippingSmokeReceipt
    source_static_receipt = [ordered]@{}
    harness_self_checks = [ordered]@{}
    cook_contract_preflight = $null
    crash_snapshot_before = @()
    crash_snapshot_after = @()
    stages = @()
    packages = [ordered]@{}
    artifact_inventory = @()
    failure = $null
    terminal_state = "CREATED"
}
Save-Json $manifest $manifestPath

try {
foreach ($required in @(
    $ProjectFile, $RunUat, $Verifier, $CookContractVerifier, $ReleaseTierVerifier,
    $MissionMatrix, $DefaultGame
)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
        throw "Required Phase 8 input is missing: $required"
    }
}
if ($RunRuntimeValidation -and
    -not (Test-Path -LiteralPath $RuntimeValidationSupervisor -PathType Leaf)) {
    throw "Runtime validation supervisor is missing: $RuntimeValidationSupervisor"
}

$missionData = Get-Content -LiteralPath $MissionMatrix -Raw | ConvertFrom-Json
$manifest.source_static_receipt = Get-SourceStaticReceipt
$manifest.harness_self_checks = Get-HarnessSelfChecks -ScratchRoot $artifactsRoot
$manifest.crash_snapshot_before = Get-CrashSnapshot
if (-not (
    $manifest.harness_self_checks.portable_sha256_known_vector -and
    $manifest.harness_self_checks.sha256_changes_after_tamper -and
    $manifest.harness_self_checks.frame_range_config_parse_safe
)) {
    throw "Phase 8 harness SHA-256 self-check failed."
}
Save-Json $manifest $manifestPath

$releaseTierPath = Join-Path $artifactsRoot "release_tier_preflight.json"
$releaseTierArguments = @(
    $ReleaseTierVerifier,
    "--release-tier", $ReleaseTier,
    "--output", $releaseTierPath
)
if ($EffectiveEngineeringAudioException) {
    $releaseTierArguments += "--allow-engineering-audio-exception"
}
& py -3 @releaseTierArguments
$releaseTierPreflightExitCode = $LASTEXITCODE
$manifest.release_tier_receipt = $releaseTierPath
Save-Json $manifest $manifestPath
if ($releaseTierPreflightExitCode -ne 0) {
    $manifest.terminal_state = "RELEASE_TIER_PREFLIGHT_FAILED"
    Save-Json $manifest $manifestPath
    & py -3 $Verifier --manifest $manifestPath --output $gatePath --latest-output $latestPath
    exit 3
}

$cookPreflightPath = Join-Path $artifactsRoot "cook_contract_preflight.json"
& py -3 $CookContractVerifier `
    --project-root $ProjectRoot `
    --default-game $DefaultGame `
    --mission-matrix $MissionMatrix `
    --output $cookPreflightPath
$cookPreflightExitCode = $LASTEXITCODE
if ($cookPreflightExitCode -ne 0) {
    $manifest.cook_contract_preflight = $cookPreflightPath
    $manifest.terminal_state = "COOK_CONTRACT_PREFLIGHT_FAILED"
    Save-Json $manifest $manifestPath
    & py -3 $Verifier --manifest $manifestPath --output $gatePath --latest-output $latestPath
    exit 1
}
$manifest.cook_contract_preflight = $cookPreflightPath
Save-Json $manifest $manifestPath

$active = @(
    Get-CimInstance Win32_Process |
        Where-Object {
            $_.Name -in @(
                "UnrealEditor.exe", "UnrealEditor-Cmd.exe", "Skyguard52.exe",
                "UnrealBuildTool.exe", "AutomationTool.exe", "ShaderCompileWorker.exe"
            )
        } |
        Select-Object ProcessId, Name, CommandLine
)
if ($active.Count -gt 0) {
    $manifest.terminal_state = "BLOCKED_ACTIVE_UNREAL_OR_BUILD_PROCESS"
    $manifest.active_processes = $active
    Save-Json $manifest $manifestPath
    & py -3 $Verifier --manifest $manifestPath --output $gatePath --latest-output $latestPath
    exit 2
}

if ($ValidateOnly) {
    $manifest.terminal_state = "VALIDATED_NOT_EXECUTED"
    Save-Json $manifest $manifestPath
    & py -3 $Verifier --manifest $manifestPath --output $gatePath --latest-output $latestPath
    exit 0
}

$configurations = @()
if (-not $SkipDevelopmentPackage) { $configurations += "Development" }
if (-not $SkipShippingPackage) { $configurations += "Shipping" }

foreach ($configuration in $configurations) {
    $archiveRoot = Join-Path $packagesRoot $configuration
    New-Item -ItemType Directory -Force -Path $archiveRoot | Out-Null
    $stdout = Join-Path $logsRoot "package_$($configuration.ToLower()).stdout.log"
    $stderr = Join-Path $logsRoot "package_$($configuration.ToLower()).stderr.log"
    $uatPayload = "$RunUat BuildCookRun -project=$ProjectFile -noP4 -platform=Win64 " +
        "-clientconfig=$configuration -build -cook -stage -pak -iostore -archive " +
        "-archivedirectory=$archiveRoot -allmaps -prereqs -utf8output"
    $stage = Invoke-BoundedProcess `
        -Name "package_$($configuration.ToLower())" `
        -FilePath $env:ComSpec `
        -Arguments @("/d", "/s", "/c", $uatPayload) `
        -StdoutPath $stdout -StderrPath $stderr `
        -TimeoutSeconds $PackageTimeoutSeconds
    $packageLogText = (
        (Get-Content -LiteralPath $stdout -Raw -ErrorAction SilentlyContinue) +
        "`n" +
        (Get-Content -LiteralPath $stderr -Raw -ErrorAction SilentlyContinue)
    )
    $stage["semantic_success"] = [bool](
        $packageLogText -match "BUILD SUCCESSFUL|AutomationTool exiting with ExitCode=0"
    )
    $stage["semantic_failure"] = [bool](
        $packageLogText -match "BUILD FAILED|Cook failed|AutomationTool exiting with ExitCode=[1-9]"
    )
    $manifest.stages += $stage
    $executable = Get-PackageExecutable $archiveRoot
    $containerFiles = @(
        Get-ChildItem -LiteralPath $archiveRoot -Recurse -File -ErrorAction SilentlyContinue |
            Where-Object { $_.Extension -in @(".pak", ".utoc", ".ucas") } |
            ForEach-Object { $_.FullName }
    )
    $manifest.packages[$configuration] = [ordered]@{
        archive_root = $archiveRoot
        executable = if ($executable) { $executable.FullName } else { $null }
        cooked_container_files = $containerFiles
        cooked_asset_registry = $null
        cooked_asset_registry_sha256 = $null
        cook_contract_report = $null
    }
    Save-Json $manifest $manifestPath
    if (
        $stage.timed_out -or
        $stage.exit_code -ne 0 -or
        -not $stage.semantic_success -or
        $stage.semantic_failure -or
        -not $executable -or
        $containerFiles.Count -eq 0
    ) {
        $manifest.terminal_state = "PACKAGE_FAILED"
        Save-Json $manifest $manifestPath
        & py -3 $Verifier --manifest $manifestPath --output $gatePath --latest-output $latestPath
        exit 1
    }

    $cookedRegistrySource = Join-Path $ProjectRoot `
        "Saved\Cooked\Windows\Skyguard52\Metadata\DevelopmentAssetRegistry.bin"
    $cookedRegistryCopy = Join-Path $artifactsRoot `
        "$($configuration.ToLower())_DevelopmentAssetRegistry.bin"
    if (Test-Path -LiteralPath $cookedRegistrySource -PathType Leaf) {
        Copy-Item -LiteralPath $cookedRegistrySource -Destination $cookedRegistryCopy -Force
        $manifest.packages[$configuration].cooked_asset_registry = $cookedRegistryCopy
        $manifest.packages[$configuration].cooked_asset_registry_sha256 = `
            Get-PortableSha256 -LiteralPath $cookedRegistryCopy
    }
    $cookContractPath = Join-Path $artifactsRoot `
        "$($configuration.ToLower())_cook_contract.json"
    $manifest.packages[$configuration].cook_contract_report = $cookContractPath
    Save-Json $manifest $manifestPath
    & py -3 $CookContractVerifier `
        --project-root $ProjectRoot `
        --default-game $DefaultGame `
        --mission-matrix $MissionMatrix `
        --archive-root $archiveRoot `
        --cooked-asset-registry $cookedRegistryCopy `
        --output $cookContractPath
    $cookContract = if (Test-Path -LiteralPath $cookContractPath -PathType Leaf) {
        Get-Content -LiteralPath $cookContractPath -Raw | ConvertFrom-Json
    } else {
        $null
    }
    if ($null -eq $cookContract -or $cookContract.gate -ne "PASS") {
        $manifest.terminal_state = "PACKAGE_MAP_CONTRACT_FAILED"
        Save-Json $manifest $manifestPath
        & py -3 $Verifier --manifest $manifestPath --output $gatePath --latest-output $latestPath
        exit 1
    }
}

$developmentPackage = if ($manifest.packages.Contains("Development")) {
    $manifest.packages["Development"]
} else { $null }
$developmentExe = if ($developmentPackage) { $developmentPackage.executable } else { $null }
if (-not $SkipMissionSoak -and $developmentExe) {
    foreach ($mission in $missionData.missions) {
        if ([string]::IsNullOrWhiteSpace([string]$mission.map)) { continue }
        $seconds = [int]$mission.soak_seconds
        $stdout = Join-Path $logsRoot "soak_$($mission.id).stdout.log"
        $stderr = Join-Path $logsRoot "soak_$($mission.id).stderr.log"
        $trace = Join-Path $artifactsRoot "soak_$($mission.id).utrace"
        $stage = Invoke-BoundedProcess `
            -Name "mission_soak_$($mission.id)" `
            -FilePath $developmentExe `
            -Arguments @(
                [string]$mission.map,
                "-RenderOffscreen", "-ResX=1920", "-ResY=1080", "-d3d12", "-sm6",
                "-NoVSync", "-benchmark", "-benchmarkseconds=$seconds",
                "-unattended", "-nosplash", "-stdout", "-FullStdOutLogOutput",
                "-trace=cpu,gpu,frame,bookmark,loadtime,file,assetload",
                "-tracefile=$trace", "-tracefiletrunc", "-traceautostart=1",
                "-csvCaptureFrames=$($seconds * 60)", "-csvCategories=Global",
                "-csvGpuStats", "-csvNamedEvents",
                "-csvMetadata=phase=phase8,mission=$($mission.id)"
            ) `
            -StdoutPath $stdout -StderrPath $stderr `
            -TimeoutSeconds ($seconds + $MissionTimeoutPaddingSeconds)
        $manifest.stages += $stage
        Save-Json $manifest $manifestPath
    }
}

$shippingPackage = if ($manifest.packages.Contains("Shipping")) {
    $manifest.packages["Shipping"]
} else { $null }
$shippingExe = if ($shippingPackage) { $shippingPackage.executable } else { $null }
if ($shippingExe) {
    $firstMap = @($missionData.missions | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_.map) })[0].map
    $stage = Invoke-BoundedProcess `
        -Name "shipping_startup_smoke" `
        -FilePath $shippingExe `
        -Arguments @(
            [string]$firstMap, "-RenderOffscreen", "-ResX=1920", "-ResY=1080",
            "-d3d12", "-sm6", "-NoVSync",
            "-SkyguardStartupSmokeSeconds=$ShippingSmokeSeconds",
            "-SkyguardStartupSmokeReceipt=$shippingSmokeReceipt",
            "-unattended", "-nosplash",
            "-stdout", "-FullStdOutLogOutput"
        ) `
        -StdoutPath (Join-Path $logsRoot "shipping_smoke.stdout.log") `
        -StderrPath (Join-Path $logsRoot "shipping_smoke.stderr.log") `
        -TimeoutSeconds ($ShippingSmokeSeconds + $MissionTimeoutPaddingSeconds)
    $manifest.stages += $stage
}

if ($RunRuntimeValidation) {
    if (-not $developmentExe) {
        throw "Runtime validation requires a fresh Development package."
    }
    & powershell -NoProfile -ExecutionPolicy Bypass `
        -File $RuntimeValidationSupervisor `
        -PackageAttemptRoot $attemptRoot
    $runtimeValidationExitCode = $LASTEXITCODE
    if ($runtimeValidationExitCode -ne 0) {
        throw "Packaged runtime validation supervisor failed."
    }
    $runtimeReceipt = Get-ChildItem `
        -LiteralPath $artifactsRoot `
        -Recurse -File -Filter "runtime_validation_receipt.json" |
        Sort-Object LastWriteTimeUtc -Descending |
        Select-Object -First 1
    if (-not $runtimeReceipt) {
        throw "Runtime validation reported success without a receipt."
    }
    $manifest.runtime_validation_receipt = $runtimeReceipt.FullName
    Save-Json $manifest $manifestPath
}

$inventoryInputs = [System.Collections.Generic.List[object]]::new()
foreach ($configuration in @("Development", "Shipping")) {
    if (-not $manifest.packages.Contains($configuration)) { continue }
    $package = $manifest.packages[$configuration]
    $archiveRoot = [string]$package.archive_root
    if (-not (Test-Path -LiteralPath $archiveRoot -PathType Container)) { continue }
    foreach ($file in Get-ChildItem -LiteralPath $archiveRoot -Recurse -File) {
        $inventoryInputs.Add([pscustomobject]@{
            configuration = $configuration
            archive_root = $archiveRoot
            file = $file
        })
    }
}
$manifest.artifact_inventory = @(
    $inventoryInputs |
        Sort-Object configuration, { $_.file.FullName } -Unique |
        ForEach-Object {
            [ordered]@{
                configuration = $_.configuration
                path = $_.file.FullName
                relative_path = $_.file.FullName.Substring($_.archive_root.Length).TrimStart("\")
                bytes = $_.file.Length
                sha256 = Get-PortableSha256 -LiteralPath $_.file.FullName
            }
        }
)
$manifest.crash_snapshot_after = Get-CrashSnapshot
$manifest.terminal_state = "EXECUTION_COMPLETE"
Save-Json $manifest $manifestPath
& py -3 $Verifier --manifest $manifestPath --output $gatePath --latest-output $latestPath
$releaseVerifierExitCode = $LASTEXITCODE
exit $releaseVerifierExitCode
}
catch {
    $manifest.terminal_state = "FAILED_HARNESS"
    $manifest.failure = [ordered]@{
        type = $_.Exception.GetType().FullName
        message = $_.Exception.Message
        position_message = $_.InvocationInfo.PositionMessage
        script_stack_trace = $_.ScriptStackTrace
        failed_at_utc = [DateTime]::UtcNow.ToString("o")
    }
    try { $manifest.crash_snapshot_after = Get-CrashSnapshot } catch {}
    try { Save-Json $manifest $manifestPath } catch {}
    if (Test-Path -LiteralPath $Verifier -PathType Leaf) {
        try {
            & py -3 $Verifier --manifest $manifestPath --output $gatePath --latest-output $latestPath
        }
        catch {}
    }
    Write-Error "Phase 8 release harness failed: $($_.Exception.Message)"
    exit 1
}
