[CmdletBinding()]
param(
    [ValidateSet("Plan", "Capture", "RawMerge", "Stabilize", "CookFallback", "VerifyPackage", "VerifyConsumption")]
    [string]$Phase = "Plan",
    [string]$ProjectRoot = "D:\Skyguard52",
    [string]$UnrealRoot = "D:\UE_5.8",
    [string]$PackageAttemptRoot = "",
    [string]$Manifest = "",
    [string]$AttemptRoot = "",
    [ValidatePattern("^[A-Za-z0-9_-]*$")]
    [string]$ReceiptSuffix = "",
    [ValidateRange(60, 900)]
    [int]$CaptureSeconds = 300,
    [ValidateRange(60, 900)]
    [int]$ConsumptionSeconds = 120
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$ProjectFile = Join-Path $ProjectRoot "Skyguard52.uproject"
$Config = Join-Path $ProjectRoot "Config\DefaultEngine.ini"
$MissionMatrix = Join-Path $ProjectRoot "Docs\AAA_Review\PHASE8_MISSION_SOAK_MATRIX.json"
$Verifier = Join-Path $ProjectRoot "Scripts\verify_skyguard_phase8_pso_workflow.py"
$EditorCmd = Join-Path $UnrealRoot "Engine\Binaries\Win64\UnrealEditor-Cmd.exe"

function Get-Sha256 {
    param([Parameter(Mandatory = $true)][string]$LiteralPath)
    $resolved = (Resolve-Path -LiteralPath $LiteralPath).Path
    for ($attempt = 1; $attempt -le 20; $attempt++) {
        $stream = $null
        $sha = $null
        try {
            $stream = [System.IO.File]::OpenRead($resolved)
            $sha = [System.Security.Cryptography.SHA256]::Create()
            return ([BitConverter]::ToString(
                $sha.ComputeHash($stream))).Replace("-", "").ToLowerInvariant()
        } catch [System.IO.IOException] {
            if ($attempt -eq 20) { throw }
            Start-Sleep -Milliseconds 250
        } finally {
            if ($sha) { $sha.Dispose() }
            if ($stream) { $stream.Dispose() }
        }
    }
}

function Get-FileRecord {
    param([Parameter(Mandatory = $true)][string]$LiteralPath)
    $file = Get-Item -LiteralPath $LiteralPath -ErrorAction Stop
    return [ordered]@{
        path = $file.FullName
        bytes = $file.Length
        sha256 = Get-Sha256 -LiteralPath $file.FullName
    }
}

function Save-Json {
    param($Value, [Parameter(Mandatory = $true)][string]$LiteralPath)
    if (Test-Path -LiteralPath $LiteralPath) {
        throw "Refusing to overwrite immutable PSO receipt: $LiteralPath"
    }
    $Value | ConvertTo-Json -Depth 20 |
        Set-Content -LiteralPath $LiteralPath -Encoding UTF8
}

function Get-ReceiptPath {
    param([Parameter(Mandatory = $true)][string]$BaseName)
    $fileName = if ([string]::IsNullOrWhiteSpace($ReceiptSuffix)) {
        "$BaseName.json"
    } else {
        "${BaseName}_$ReceiptSuffix.json"
    }
    return Join-Path $AttemptRoot $fileName
}

function Join-Arguments {
    param([string[]]$Arguments)
    return (($Arguments | ForEach-Object {
        if ($_ -match '[\s"]') { '"' + ($_ -replace '"', '\"') + '"' } else { $_ }
    }) -join " ")
}

function Invoke-Bounded {
    param(
        [string]$Name,
        [string]$FilePath,
        [string[]]$Arguments,
        [string]$Stdout,
        [string]$Stderr,
        [int]$TimeoutSeconds
    )
    $started = [DateTime]::UtcNow
    $process = Start-Process -FilePath $FilePath `
        -ArgumentList (Join-Arguments $Arguments) `
        -WorkingDirectory $ProjectRoot `
        -RedirectStandardOutput $Stdout `
        -RedirectStandardError $Stderr `
        -WindowStyle Hidden -PassThru
    $timedOut = -not $process.WaitForExit($TimeoutSeconds * 1000)
    if ($timedOut) {
        & taskkill.exe /PID $process.Id /T /F | Out-Null
        $process.WaitForExit()
    }
    $process.Refresh()
    $exitCode = if (-not $timedOut -and $process.HasExited) {
        [int]$process.ExitCode
    } else { $null }
    return [ordered]@{
        name = $Name
        started_at_utc = $started.ToString("o")
        finished_at_utc = [DateTime]::UtcNow.ToString("o")
        exit_code = $exitCode
        timed_out = $timedOut
        stdout = $Stdout
        stderr = $Stderr
    }
}

function Assert-PreviousPhase {
    param($State, [string]$Expected)
    if ($State.phase -ne $Expected) {
        throw "PSO phase transition requires $Expected, received $($State.phase)."
    }
    $verification = Get-ReceiptPath "verify_$($Expected.ToLower())"
    if (Test-Path -LiteralPath $verification) {
        throw "Refusing to overwrite immutable PSO verification receipt: $verification"
    }
    & py -3 $Verifier --manifest $Manifest --output $verification
    if ($LASTEXITCODE -ne 0) {
        throw "Prior PSO receipt failed independent verification: $Manifest"
    }
}

foreach ($required in @($ProjectFile, $Config, $MissionMatrix, $Verifier)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
        throw "Missing PSO workflow input: $required"
    }
}

if ($Phase -eq "Plan") {
    if (-not $PackageAttemptRoot) {
        throw "Plan requires -PackageAttemptRoot from a completed Phase 8 package attempt."
    }
    $developmentExe = Join-Path $PackageAttemptRoot "packages\Development\Windows\Skyguard52.exe"
    if (-not $AttemptRoot) {
        $stamp = [DateTime]::UtcNow.ToString("yyyyMMddTHHmmssfffZ")
        $AttemptRoot = Join-Path $ProjectRoot "Saved\Profiling\Phase8PSO\attempt_$stamp"
    }
    New-Item -ItemType Directory -Force -Path $AttemptRoot | Out-Null
    $state = [ordered]@{
        schema = "skyguard.phase8.pso-workflow.v1"
        attempt_root = $AttemptRoot
        phase = "PREFLIGHT"
        config = $Config
        package_attempt_root = $PackageAttemptRoot
        package_executable = Get-FileRecord $developmentExe
        mission_matrix = Get-FileRecord $MissionMatrix
        captures = @()
        stable_keys = @()
        stable_cache = $null
        stabilize_stage = $null
        packaged_cache = $null
        consumption = $null
    }
    $output = Get-ReceiptPath "manifest_preflight"
    Save-Json $state $output
    & py -3 $Verifier --manifest $output --output (Get-ReceiptPath "verify_preflight")
    exit $LASTEXITCODE
}

if (-not $Manifest -or -not (Test-Path -LiteralPath $Manifest -PathType Leaf)) {
    throw "$Phase requires -Manifest from the previous successful PSO phase."
}
$state = Get-Content -LiteralPath $Manifest -Raw | ConvertFrom-Json
if (-not $AttemptRoot) { $AttemptRoot = [string]$state.attempt_root }
New-Item -ItemType Directory -Force -Path $AttemptRoot | Out-Null
$logs = Join-Path $AttemptRoot "logs"
New-Item -ItemType Directory -Force -Path $logs | Out-Null
$matrix = Get-Content -LiteralPath $MissionMatrix -Raw | ConvertFrom-Json

if ($Phase -eq "Capture") {
    Assert-PreviousPhase $state "PREFLIGHT"
    $captureRoot = Join-Path $AttemptRoot "captures"
    New-Item -ItemType Directory -Force -Path $captureRoot | Out-Null
    $packageExe = [string]$state.package_executable.path
    $collectedRoot = Join-Path (Split-Path $packageExe -Parent) `
        "Skyguard52\Saved\CollectedPSOs"
    $captures = @()
    foreach ($mission in $matrix.missions) {
        $before = @(
            Get-ChildItem -LiteralPath $collectedRoot -Filter "*.rec.upipelinecache" `
                -File -ErrorAction SilentlyContinue | ForEach-Object FullName
        )
        $stdout = Join-Path $logs "capture_$($mission.id).stdout.log"
        $stderr = Join-Path $logs "capture_$($mission.id).stderr.log"
        $stage = Invoke-Bounded "capture_$($mission.id)" $packageExe @(
            [string]$mission.map, "-RenderOffscreen", "-d3d12", "-sm6", "-logPSO",
            "-deleteuserpsocache", "-benchmark",
            "-benchmarkseconds=$CaptureSeconds", "-unattended", "-nosplash",
            "-stdout", "-FullStdOutLogOutput",
            '-LogCmds=LogRHI VeryVerbose,LogShaderPipelineCache VeryVerbose,LogPSOHitching Verbose'
        ) $stdout $stderr ($CaptureSeconds + 180)
        $newCaches = @(
            Get-ChildItem -LiteralPath $collectedRoot -Filter "*.rec.upipelinecache" `
                -File -ErrorAction SilentlyContinue |
                Where-Object { $_.FullName -notin $before } |
                Sort-Object LastWriteTimeUtc -Descending
        )
        if ($stage.exit_code -ne 0 -or $stage.timed_out -or $newCaches.Count -lt 1) {
            throw "PSO capture failed for $($mission.id)."
        }
        $copy = Join-Path $captureRoot "$($mission.id).rec.upipelinecache"
        Copy-Item -LiteralPath $newCaches[0].FullName -Destination $copy
        $captures += [ordered]@{
            mission = [string]$mission.id
            map = [string]$mission.map
            cache = Get-FileRecord $copy
            exit_code = $stage.exit_code
            timed_out = $stage.timed_out
            log = $stdout
            stderr = $stderr
        }
    }
    $state.phase = "CAPTURED"
    $state.captures = $captures
    $output = Get-ReceiptPath "manifest_captured"
}
elseif ($Phase -eq "RawMerge") {
    Assert-PreviousPhase $state "CAPTURED"
    if (-not (Test-Path -LiteralPath $EditorCmd -PathType Leaf)) {
        throw "Missing Unreal commandlet: $EditorCmd"
    }
    $stableKeySource = Join-Path $ProjectRoot "Saved\Cooked\Windows"
    $stableKeyFolder = if ([string]::IsNullOrWhiteSpace($ReceiptSuffix)) {
        "stable_keys_raw_merge"
    } else {
        "stable_keys_raw_merge_$ReceiptSuffix"
    }
    $stableKeyRoot = Join-Path $AttemptRoot $stableKeyFolder
    New-Item -ItemType Directory -Force -Path $stableKeyRoot | Out-Null
    $stableKeys = @()
    foreach (
        $source in Get-ChildItem -LiteralPath $stableKeySource -Recurse `
            -Filter "*PCD3D_SM6.shk" -File
    ) {
        $copy = Join-Path $stableKeyRoot $source.Name
        if (Test-Path -LiteralPath $copy) {
            throw "Refusing to overwrite immutable raw-merge stable-key copy: $copy"
        }
        Copy-Item -LiteralPath $source.FullName -Destination $copy
        $stableKeys += Get-FileRecord $copy
    }
    if ($stableKeys.Count -lt 1) {
        throw "Raw merge requires current SM6 stable-key files."
    }

    $mergeFolder = if ([string]::IsNullOrWhiteSpace($ReceiptSuffix)) {
        "raw_merge"
    } else {
        "raw_merge_$ReceiptSuffix"
    }
    $mergeRoot = Join-Path $AttemptRoot $mergeFolder
    New-Item -ItemType Directory -Force -Path $mergeRoot | Out-Null
    $mergeSteps = @()
    $left = [string]$state.captures[0].cache.path
    for ($index = 1; $index -lt $state.captures.Count; $index++) {
        $right = [string]$state.captures[$index].cache.path
        $stepNumber = $index + 1
        $stepId = "{0:D2}" -f $stepNumber
        $merged = Join-Path $mergeRoot "merge_step_$stepId.upipelinecache"
        $stdout = Join-Path $mergeRoot "merge_step_$stepId.stdout.log"
        $stderr = Join-Path $mergeRoot "merge_step_$stepId.stderr.log"
        foreach ($immutable in @($merged, $stdout, $stderr)) {
            if (Test-Path -LiteralPath $immutable) {
                throw "Refusing to overwrite immutable raw-merge artifact: $immutable"
            }
        }
        $stage = Invoke-Bounded "raw_merge_$stepId" $EditorCmd @(
            $ProjectFile, "-run=MergeShaderPipelineCaches",
            $left, $right, $merged, "-Sort=MostUsed",
            "-unattended", "-nop4", "-nosplash", "-nullrhi",
            "-stdout", "-FullStdOutLogOutput"
        ) $stdout $stderr 300
        if ($stage.exit_code -ne 0 -or $stage.timed_out -or
            -not (Test-Path -LiteralPath $merged -PathType Leaf)) {
            throw "Raw PSO merge failed at step $stepId."
        }
        $mergeSteps += [ordered]@{
            mission = [string]$state.captures[$index].mission
            input_left = Get-FileRecord $left
            input_right = Get-FileRecord $right
            output = Get-FileRecord $merged
            stage = $stage
        }
        $left = $merged
    }

    $dumpStdout = Join-Path $mergeRoot "dump_final.stdout.log"
    $dumpStderr = Join-Path $mergeRoot "dump_final.stderr.log"
    $dumpStage = Invoke-Bounded "raw_merge_dump" $EditorCmd @(
        $ProjectFile, "-run=ShaderPipelineCacheTools", "Dump", $left,
        "-unattended", "-nop4", "-nosplash", "-nullrhi",
        "-stdout", "-FullStdOutLogOutput"
    ) $dumpStdout $dumpStderr 300
    if ($dumpStage.exit_code -ne 0 -or $dumpStage.timed_out) {
        throw "Raw PSO merge dump validation failed."
    }
    $dumpText = Get-Content -LiteralPath $dumpStdout -Raw
    $psoMatch = [regex]::Match($dumpText, "Total PSOs logged:\s*(\d+)")
    if (-not $psoMatch.Success -or [int]$psoMatch.Groups[1].Value -lt 1 -or
        $dumpText -match "Fatal error|Assertion failed|GPU Crash|Unhandled Exception") {
        throw "Raw PSO merge dump did not validate a non-empty clean cache."
    }

    $pipelineRoot = Join-Path $ProjectRoot "Build\Windows\PipelineCaches"
    New-Item -ItemType Directory -Force -Path $pipelineRoot | Out-Null
    $accepted = Join-Path $pipelineRoot `
        "Skyguard52_PCD3D_SM6.stable.upipelinecache"
    $priorAccepted = $null
    if (Test-Path -LiteralPath $accepted -PathType Leaf) {
        $priorPath = Join-Path $mergeRoot "prior_accepted_seed.upipelinecache"
        Copy-Item -LiteralPath $accepted -Destination $priorPath
        $priorAccepted = Get-FileRecord $priorPath
    }
    Copy-Item -LiteralPath $left -Destination $accepted -Force
    if ((Get-Sha256 -LiteralPath $left) -ne
        (Get-Sha256 -LiteralPath $accepted)) {
        throw "Accepted raw-merge cache hash does not match validated merge output."
    }

    $state.phase = "STABILIZED"
    $state | Add-Member -NotePropertyName stabilization_mode `
        -NotePropertyValue "raw_recorded_binary_merge" -Force
    $state.stable_keys = $stableKeys
    $state.stable_cache = Get-FileRecord $accepted
    $state.stabilize_stage = [ordered]@{
        mode = "raw_recorded_binary_merge"
        merge_steps = $mergeSteps
        dump_stage = $dumpStage
        dump_log = Get-FileRecord $dumpStdout
        total_pso_count = [int]$psoMatch.Groups[1].Value
        validated_merge_output = Get-FileRecord $left
        prior_accepted_seed = $priorAccepted
    }
    $output = Get-ReceiptPath "manifest_stabilized"
}
elseif ($Phase -eq "Stabilize") {
    Assert-PreviousPhase $state "CAPTURED"
    if (-not (Test-Path -LiteralPath $EditorCmd -PathType Leaf)) {
        throw "Missing Unreal commandlet: $EditorCmd"
    }
    $stableKeySource = Join-Path $ProjectRoot "Saved\Cooked\Windows"
    $stableKeyRoot = Join-Path $AttemptRoot "stable_keys"
    New-Item -ItemType Directory -Force -Path $stableKeyRoot | Out-Null
    $stableKeys = @()
    foreach ($source in Get-ChildItem -LiteralPath $stableKeySource -Recurse -Filter "*PCD3D_SM6.shk" -File) {
        $copy = Join-Path $stableKeyRoot $source.Name
        Copy-Item -LiteralPath $source.FullName -Destination $copy -Force
        $stableKeys += Get-FileRecord $copy
    }
    if ($stableKeys.Count -lt 1) { throw "No cooked .shk stable-key files were found." }
    $pipelineRoot = Join-Path $ProjectRoot "Build\Windows\PipelineCaches"
    New-Item -ItemType Directory -Force -Path $pipelineRoot | Out-Null
    $stable = Join-Path $pipelineRoot "Skyguard52_PCD3D_SM6.spc"
    $stdout = Join-Path $logs "stabilize.stdout.log"
    $stderr = Join-Path $logs "stabilize.stderr.log"
    $stage = Invoke-Bounded "stabilize" $EditorCmd @(
        $ProjectFile, "-run=ShaderPipelineCacheTools", "Expand",
        (Join-Path $AttemptRoot "captures\*.rec.upipelinecache"),
        (Join-Path $stableKeyRoot "*PCD3D_SM6.shk"), $stable,
        "-unattended", "-nop4", "-stdout", "-FullStdOutLogOutput"
    ) $stdout $stderr 1800
    if ($stage.exit_code -ne 0 -or $stage.timed_out -or -not (Test-Path $stable)) {
        throw "PSO stabilization failed."
    }
    $state.phase = "STABILIZED"
    $state | Add-Member -NotePropertyName stabilization_mode `
        -NotePropertyValue "recorded_graphics_binary_spc" -Force
    $state.stable_keys = $stableKeys
    $state.stable_cache = Get-FileRecord $stable
    $state.stabilize_stage = $stage
    $output = Get-ReceiptPath "manifest_stabilized"
}
elseif ($Phase -eq "CookFallback") {
    Assert-PreviousPhase $state "CAPTURED"
    $stableKeySource = Join-Path $ProjectRoot "Saved\Cooked\Windows"
    $fallbackKeyFolder = if ([string]::IsNullOrWhiteSpace($ReceiptSuffix)) {
        "stable_keys_fallback"
    } else {
        "stable_keys_fallback_$ReceiptSuffix"
    }
    $fallbackKeyRoot = Join-Path $AttemptRoot $fallbackKeyFolder
    New-Item -ItemType Directory -Force -Path $fallbackKeyRoot | Out-Null
    $stableKeys = @()
    foreach (
        $source in Get-ChildItem -LiteralPath $stableKeySource -Recurse `
            -Filter "*PCD3D_SM6.shk" -File
    ) {
        $copy = Join-Path $fallbackKeyRoot $source.Name
        if (Test-Path -LiteralPath $copy) {
            throw "Refusing to overwrite immutable fallback stable-key copy: $copy"
        }
        Copy-Item -LiteralPath $source.FullName -Destination $copy
        $stableKeys += Get-FileRecord $copy
    }
    if ($stableKeys.Count -lt 1) {
        throw "Cook fallback requires current SM6 stable-key files."
    }
    $engineDefectEvidence = @(
        Get-ChildItem -LiteralPath (Join-Path $AttemptRoot "diagnostics") `
            -Recurse -Filter "*.stdout.log" -File -ErrorAction SilentlyContinue |
        Where-Object {
            (Get-Content -LiteralPath $_.FullName -Raw) -match
                "Trying to resize TArray to an invalid size|Enclosing block should never be called"
        } |
        ForEach-Object { Get-FileRecord $_.FullName }
    )
    if ($engineDefectEvidence.Count -lt 2) {
        throw "Cook fallback requires at least two independently reproduced UE 5.8 loader-failure logs."
    }
    $state.phase = "STABILIZED"
    $state | Add-Member -NotePropertyName stabilization_mode `
        -NotePropertyValue "cook_native_compute_fallback" -Force
    $state.stable_keys = $stableKeys
    $state.stable_cache = $null
    $state.stabilize_stage = [ordered]@{
        mode = "cook_native_compute_fallback"
        recorded_graphics_cache_status = "BLOCKED_UE58_BINARY_LOADER_DEFECT"
        cook_generated_cache_required = $true
        engine_defect_evidence = $engineDefectEvidence
    }
    $output = Get-ReceiptPath "manifest_stabilized"
}
elseif ($Phase -eq "VerifyPackage") {
    Assert-PreviousPhase $state "STABILIZED"
    if (-not $PackageAttemptRoot) { throw "VerifyPackage requires -PackageAttemptRoot." }
    $development = Join-Path $PackageAttemptRoot "packages\Development"
    $shipping = Join-Path $PackageAttemptRoot "packages\Shipping"
    $developmentExe = Join-Path $development "Windows\Skyguard52.exe"
    $shippingExe = Join-Path $shipping "Windows\Skyguard52.exe"
    $expectedName = "Skyguard52_PCD3D_SM6.stable.upipelinecache"
    $seedCache = Join-Path $ProjectRoot "Build\Windows\PipelineCaches\$expectedName"
    $developmentCache = Get-ChildItem -LiteralPath $development `
        -Recurse -Filter $expectedName -File | Select-Object -First 1
    $shippingCache = Get-ChildItem -LiteralPath $shipping `
        -Recurse -Filter $expectedName -File | Select-Object -First 1
    if (-not (Test-Path -LiteralPath $seedCache -PathType Leaf)) {
        throw "The accepted raw-merge PSO seed cache is missing: $seedCache"
    }
    if (-not $developmentCache -or -not $shippingCache) {
        throw "The loose stable SM6 pipeline cache was not staged into both packages."
    }
    $seedHash = Get-Sha256 -LiteralPath $seedCache
    if ((Get-Sha256 -LiteralPath $developmentCache.FullName) -ne $seedHash -or
        (Get-Sha256 -LiteralPath $shippingCache.FullName) -ne $seedHash) {
        throw "Packaged PSO cache hash does not match the accepted raw-merge seed."
    }
    $utocs = @(Get-ChildItem -LiteralPath $shipping -Recurse -Filter "*.utoc" -File)
    $state.phase = "PACKAGED"
    $state.packaged_cache = [ordered]@{
        mode = "loose_nonufs_runtime_seed"
        package_attempt_root = $PackageAttemptRoot
        development_root = $development
        shipping_root = $shipping
        development_executable = Get-FileRecord $developmentExe
        shipping_executable = Get-FileRecord $shippingExe
        expected_name = $expectedName
        source_cache = Get-FileRecord $seedCache
        development_cache = Get-FileRecord $developmentCache.FullName
        packaged_cache = Get-FileRecord $shippingCache.FullName
        shipping_utocs = @($utocs | ForEach-Object { Get-FileRecord $_.FullName })
    }
    $output = Get-ReceiptPath "manifest_packaged"
}
else {
    Assert-PreviousPhase $state "PACKAGED"
    $packageExe = [string]$state.packaged_cache.development_executable.path
    $firstMap = [string]$matrix.missions[0].map
    $stdout = Join-Path $logs "consumption.stdout.log"
    $stderr = Join-Path $logs "consumption.stderr.log"
    $stage = Invoke-Bounded "consumption" $packageExe @(
        $firstMap, "-RenderOffscreen", "-d3d12", "-sm6", "-benchmark",
        "-benchmarkseconds=$ConsumptionSeconds", "-unattended", "-nosplash",
        "-stdout", "-FullStdOutLogOutput",
        '-LogCmds=LogRHI VeryVerbose,LogShaderPipelineCache VeryVerbose,LogPSOHitching Verbose'
    ) $stdout $stderr ($ConsumptionSeconds + 180)
    $state.phase = "CONSUMED"
    $state.consumption = [ordered]@{
        exit_code = $stage.exit_code
        timed_out = $stage.timed_out
        log = $stdout
        stderr = $stderr
    }
    $output = Get-ReceiptPath "manifest_consumed"
}

Save-Json $state $output
& py -3 $Verifier --manifest $output `
    --output (Get-ReceiptPath "verify_$($state.phase.ToLower())")
exit $LASTEXITCODE
