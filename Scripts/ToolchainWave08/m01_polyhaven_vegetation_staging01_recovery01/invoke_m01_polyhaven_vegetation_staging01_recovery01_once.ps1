param(
    [switch]$OfflineContractTest,
    [switch]$AuthorizeSingleUnrealStaging
)

$ErrorActionPreference = 'Stop'
$CanonicalRoot = 'D:\Skyguard52'
$ProjectRoot = 'D:\SG52T08_ENV01'
$Project = Join-Path $ProjectRoot 'Skyguard52.uproject'
$Editor = 'D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$Contract = 'D:\Skyguard52\Scripts\ToolchainWave08\m01_polyhaven_vegetation_staging01_recovery01\vegetation_staging01_recovery01_contract.json'
$Worker = 'D:\Skyguard52\Scripts\ToolchainWave08\m01_polyhaven_vegetation_staging01_recovery01\author_m01_polyhaven_vegetation_staging01_recovery01.py'
$AttemptRoot = 'D:\Skyguard52\Saved\BuildAttempts\M01_POLYHAVEN_VEGETATION_STAGING01_RECOVERY01\attempt_01'
$AttemptWorker = Join-Path $AttemptRoot 'author_m01_polyhaven_vegetation_staging01_recovery01.py'
$Receipt = Join-Path $AttemptRoot 'authoring_receipt.json'
$Stdout = Join-Path $AttemptRoot 'unreal.stdout.log'
$Stderr = Join-Path $AttemptRoot 'unreal.stderr.log'
$ProcessSamples = Join-Path $AttemptRoot 'process_tree_samples.json'
$Preflight = Join-Path $AttemptRoot 'preflight.json'
$ExternalTerminal = 'D:\Skyguard52\Saved\Reports\M01_POLYHAVEN_VEGETATION_STAGING01_RECOVERY01_TERMINAL_MANIFEST.json'
$EmergencyReceipt = 'D:\Skyguard52\Saved\Reports\M01_POLYHAVEN_VEGETATION_STAGING01_RECOVERY01_EMERGENCY_RECEIPT.jsonl'
$AssetDiskRoot = 'D:\SG52T08_ENV01\Content\M01\SourceBacked\VegetationStaging01Recovery01'
$InputMap = 'D:\SG52T08_ENV01\Content\M01\Lvl_M01_HeroStreetShoreCell03Recovery01.umap'
$OutputMap = 'D:\SG52T08_ENV01\Content\M01\Lvl_M01_PolyHavenVegetationStaging01Recovery01.umap'

function Get-Sha256([string]$Path) {
    $stream = [System.IO.File]::Open($Path, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::Read)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($sha.ComputeHash($stream))).Replace('-', '').ToLowerInvariant() }
    finally { $sha.Dispose(); $stream.Dispose() }
}

function Write-JsonAtomic([string]$Path, $Value) {
    $directory = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $directory)) { New-Item -ItemType Directory -Path $directory -Force | Out-Null }
    $temporary = "$Path.tmp"
    [System.IO.File]::WriteAllText($temporary, (($Value | ConvertTo-Json -Depth 40) + [Environment]::NewLine), [System.Text.UTF8Encoding]::new($false))
    Move-Item -LiteralPath $temporary -Destination $Path -Force
}

function Assert-FileRecord([string]$Path, [long]$Bytes, [string]$Hash, [string]$Label) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw "$Label missing: $Path" }
    $item = Get-Item -LiteralPath $Path
    if ($item.Length -ne $Bytes) { throw "$Label byte mismatch: $Path" }
    if ((Get-Sha256 $Path) -ne $Hash) { throw "$Label hash mismatch: $Path" }
}

function Assert-NumericExitCode($Code) {
    if ($null -eq $Code) { throw 'Process exit code is null' }
    if ($Code.GetType().FullName -ne 'System.Int32') { throw "Process exit code type is $($Code.GetType().FullName)" }
}

function Get-HeavyProcesses {
    return @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {
        $_.Name -match '^(UnrealEditor(-Cmd)?|Blender|ShaderCompileWorker|AutomationTool|UnrealBuildTool|cl|link)(\.exe)?$'
    })
}

function Assert-ContractAuthorities {
    $value = Get-Content -LiteralPath $Contract -Raw | ConvertFrom-Json
    if ($value.classification -ne 'PASSED_READY_FOR_EXPLICIT_SINGLE_UNREAL_STAGING_AUTHORIZATION') { throw 'Contract classification changed' }
    Assert-FileRecord $Project ([long]$value.project.bytes) ([string]$value.project.sha256) 'Project'
    Assert-FileRecord $Editor ([long]$value.editor.bytes) ([string]$value.editor.sha256) 'Editor'
    foreach ($entry in @($value.accepted_source_authorities)) {
        Assert-FileRecord ([string]$entry.path) ([long]$entry.bytes) ([string]$entry.sha256) 'Accepted source authority'
    }
    Assert-FileRecord ([string]$value.input_map.path) ([long]$value.input_map.bytes) ([string]$value.input_map.sha256) 'Accepted input map'
    foreach ($entry in @($value.assets)) {
        Assert-FileRecord ([string]$entry.gltf) ([long]$entry.gltf_bytes) ([string]$entry.gltf_sha256) 'Accepted source glTF'
    }
}

function Assert-Fresh {
    foreach ($path in @($AttemptRoot, $ExternalTerminal, $EmergencyReceipt, $AssetDiskRoot, $OutputMap)) {
        if (Test-Path -LiteralPath $path) { throw "Fresh namespace already exists: $path" }
    }
}

function Invoke-CapturedProcess([string]$FilePath, [string[]]$Arguments, [int]$TimeoutMilliseconds) {
    $startInfo = [System.Diagnostics.ProcessStartInfo]::new()
    $startInfo.FileName = $FilePath
    $startInfo.Arguments = $Arguments -join ' '
    $startInfo.WorkingDirectory = $ProjectRoot
    $startInfo.UseShellExecute = $false
    $startInfo.CreateNoWindow = $true
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    $process = [System.Diagnostics.Process]::new()
    $process.StartInfo = $startInfo
    $startedAt = [DateTime]::UtcNow
    if (-not $process.Start()) { throw "Process failed to start: $FilePath" }
    $nativeHandle = $process.Handle
    $stdoutTask = $process.StandardOutput.ReadToEndAsync()
    $stderrTask = $process.StandardError.ReadToEndAsync()
    $samples = @()
    $watch = [System.Diagnostics.Stopwatch]::StartNew()
    $timedOut = $false
    while (-not $process.WaitForExit(1000)) {
        $samples += [ordered]@{
            sampled_at_utc = [DateTime]::UtcNow.ToString('o')
            processes = @(Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -match '^Unreal|ShaderCompileWorker' } | Select-Object Id, ProcessName, StartTime)
        }
        if ($watch.ElapsedMilliseconds -ge $TimeoutMilliseconds) {
            $timedOut = $true
            try { $process.Kill() } catch {}
            break
        }
    }
    $process.WaitForExit()
    $process.Refresh()
    $stdout = $stdoutTask.GetAwaiter().GetResult()
    $stderr = $stderrTask.GetAwaiter().GetResult()
    $exitCode = $process.ExitCode
    Assert-NumericExitCode $exitCode
    $result = [pscustomobject]@{
        FilePath = $FilePath
        Arguments = $Arguments
        ProcessId = $process.Id
        NativeHandleRetained = ($nativeHandle -ne [IntPtr]::Zero)
        StartedAtUtc = $startedAt.ToString('o')
        CompletedAtUtc = [DateTime]::UtcNow.ToString('o')
        ExitCode = $exitCode
        ExitCodeType = $exitCode.GetType().FullName
        TimedOut = $timedOut
        Stdout = $stdout
        Stderr = $stderr
        Samples = $samples
    }
    $process.Dispose()
    return $result
}

if ($OfflineContractTest) {
    Assert-ContractAuthorities
    Assert-Fresh
    if ((Get-HeavyProcesses).Count -gt 0) { throw 'Heavy process detected during offline contract test' }
    & python $Worker --offline-contract-test
    if ($LASTEXITCODE -ne 0) { throw "Worker offline contract test returned $LASTEXITCODE" }
    Write-Output 'CLASSIFICATION=PASSED_M01_POLYHAVEN_VEGETATION_STAGING01_RECOVERY01_OFFLINE_CONTRACT'
    exit 0
}

$started = [DateTime]::UtcNow
$run = $null
$failure = $null
$classification = 'FAILED_WITH_EVIDENCE'
$preflightPassed = $false
try {
    if (-not $AuthorizeSingleUnrealStaging) { throw 'Explicit -AuthorizeSingleUnrealStaging guard is required' }
    Assert-ContractAuthorities
    Assert-Fresh
    $heavy = Get-HeavyProcesses
    if ($heavy.Count -gt 0) { throw "Heavy process detected before launch: $($heavy.Name -join ', ')" }
    $preflightPassed = $true
    New-Item -ItemType Directory -Path $AttemptRoot | Out-Null
    Copy-Item -LiteralPath $Worker -Destination $AttemptWorker
    Write-JsonAtomic $Preflight ([ordered]@{
        schema = 'skyguard.m01-polyhaven-vegetation-staging01-recovery01.preflight.v1'
        classification = 'PASSED_READY_FOR_SINGLE_UNREAL_STAGING'
        checked_at_utc = [DateTime]::UtcNow.ToString('o')
        project_sha256 = Get-Sha256 $Project
        input_map_sha256 = Get-Sha256 $InputMap
        heavy_process_count = 0
        fresh_namespaces_absent = $true
    })
    $arguments = @(
        $Project,
        '-Unattended', '-NoSplash', '-NoSound', '-NullRHI', '-NoSaveOnExit',
        '-stdout', '-FullStdOutLogOutput',
        '-DisablePlugins=Fab,Bridge,EditorTelemetry,RuntimeTelemetry,EOSShared',
        '-run=pythonscript', "-script=$AttemptWorker"
    )
    $run = Invoke-CapturedProcess -FilePath $Editor -Arguments $arguments -TimeoutMilliseconds 1800000
    [System.IO.File]::WriteAllText($Stdout, $run.Stdout, [System.Text.UTF8Encoding]::new($false))
    [System.IO.File]::WriteAllText($Stderr, $run.Stderr, [System.Text.UTF8Encoding]::new($false))
    Write-JsonAtomic $ProcessSamples $run.Samples
    if ($run.TimedOut) { throw 'Unreal staging timed out' }
    if ($run.ExitCode -ne 0) { throw "Unreal staging returned exit code $($run.ExitCode)" }
    if (-not (Test-Path -LiteralPath $Receipt -PathType Leaf)) { throw 'Authoring receipt is missing' }
    $receiptValue = Get-Content -LiteralPath $Receipt -Raw | ConvertFrom-Json
    if ($receiptValue.classification -ne 'PASSED_AUTOMATIC_AWAITING_D3D12_VISUAL_AND_PERFORMANCE_PROOF') { throw "Authoring receipt failed: $($receiptValue.error)" }
    if (@($receiptValue.asset_records).Count -ne 5) { throw 'Imported candidate count is not five' }
    if (@($receiptValue.placements).Count -ne 28) { throw 'Placement count is not twenty-eight' }
    if (-not (Test-Path -LiteralPath $AssetDiskRoot -PathType Container)) { throw 'Staged asset namespace is missing' }
    if (-not (Test-Path -LiteralPath $OutputMap -PathType Leaf)) { throw 'Staging map is missing' }
    if ((Get-Sha256 $InputMap) -ne 'c236e6f6b8a811b4cd2562be7598653464b8b30ff917418849e027ae174fc60b') { throw 'Accepted input map changed' }
    $classification = 'PASSED_UNREAL_STAGING_AWAITING_D3D12_VISUAL_AND_PERFORMANCE_PROOF'
} catch {
    $failure = $_.Exception.Message
} finally {
    $artifacts = @()
    if (Test-Path -LiteralPath $AttemptRoot -PathType Container) {
        foreach ($file in Get-ChildItem -LiteralPath $AttemptRoot -File -Recurse -ErrorAction SilentlyContinue) {
            $artifacts += [ordered]@{ path = $file.FullName; bytes = $file.Length; sha256 = Get-Sha256 $file.FullName }
        }
    }
    $terminal = [ordered]@{
        schema = 'skyguard.m01-polyhaven-vegetation-staging01-recovery01.terminal-supervisor.v1'
        classification = $classification
        started_at_utc = $started.ToString('o')
        completed_at_utc = [DateTime]::UtcNow.ToString('o')
        preflight_passed = $preflightPassed
        unreal_launch_count = if ($null -eq $run) { 0 } else { 1 }
        retry_count = 0
        exit_code = if ($null -eq $run) { $null } else { $run.ExitCode }
        exit_code_type = if ($null -eq $run) { $null } else { $run.ExitCodeType }
        timed_out = if ($null -eq $run) { $false } else { $run.TimedOut }
        failure = $failure
        input_map_sha256_after = if (Test-Path -LiteralPath $InputMap) { Get-Sha256 $InputMap } else { $null }
        output_map = if (Test-Path -LiteralPath $OutputMap) { [ordered]@{ path=$OutputMap; bytes=(Get-Item $OutputMap).Length; sha256=Get-Sha256 $OutputMap } } else { $null }
        asset_file_count = if (Test-Path -LiteralPath $AssetDiskRoot) { @(Get-ChildItem -LiteralPath $AssetDiskRoot -File -Recurse).Count } else { 0 }
        artifacts = $artifacts
    }
    try { Write-JsonAtomic $ExternalTerminal $terminal }
    catch {
        $line = ([ordered]@{ created_at_utc=[DateTime]::UtcNow.ToString('o'); classification='FAILED_WITH_EVIDENCE'; failure_stage='terminal_manifest_write'; message=$_.Exception.Message } | ConvertTo-Json -Compress)
        [System.IO.File]::AppendAllText($EmergencyReceipt, $line + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
    }
    Write-Output "CLASSIFICATION=$classification"
    if ($classification -ne 'PASSED_UNREAL_STAGING_AWAITING_D3D12_VISUAL_AND_PERFORMANCE_PROOF') { exit 1 }
}
