param(
    [switch]$OfflineContractTest,
    [switch]$AuthorizeSingleUnrealSmoke
)

$ErrorActionPreference = 'Stop'
$AttemptRoot = 'D:\Skyguard52\Saved\BuildAttempts\TOOLCHAIN_WAVE08_ENVIRONMENT_M01_CLONE_SMOKE_RECOVERY01\attempt_01'
$SourceProbe = 'D:\Skyguard52\Scripts\ToolchainWave08\environment_clone_recovery01\environment_clone_probe_recovery01.py'
$Probe = Join-Path $AttemptRoot 'environment_clone_probe_recovery01.py'
$ProbeResult = Join-Path $AttemptRoot 'probe_result.json'
$PreflightResult = Join-Path $AttemptRoot 'preflight_receipt.json'
$Terminal = Join-Path $AttemptRoot 'terminal_manifest.json'
$Stdout = Join-Path $AttemptRoot 'unreal_stdout.log'
$Stderr = Join-Path $AttemptRoot 'unreal_stderr.log'
$ProcessSamples = Join-Path $AttemptRoot 'process_tree_samples.json'
$Editor = 'D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$ProjectRoot = 'D:\SG52T08_ENV01'
$Project = Join-Path $ProjectRoot 'Skyguard52.uproject'
$CanonicalProject = 'D:\Skyguard52\Skyguard52.uproject'
$EnvironmentContract = 'D:\Skyguard52\Docs\Toolchain\ToolchainWave08\environment_prototype_contract.json'
$PreparationTerminal = 'D:\Skyguard52\Saved\Reports\TOOLCHAIN_WAVE08_ENVIRONMENT_PREPARE_TERMINAL.json'
$FailedFreeze = 'D:\Skyguard52\Docs\AAA_Review\TOOLCHAIN_WAVE08_ENVIRONMENT_M01_CLONE_SMOKE_ATTEMPT01_TERMINAL_FREEZE.json'
$CanonicalSourceMap = 'D:\Skyguard52\Content\Skyguard\Maps\Lvl_M01_CoastalIntercept_ProductionEnvironment_v4.umap'
$IsolatedSourceMap = 'D:\SG52T08_ENV01\Content\Skyguard\Maps\Lvl_M01_CoastalIntercept_ProductionEnvironment_v4.umap'
$CloneMap = 'D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_WaterLandmassPCG_Prototype01.umap'
$ExpectedProbeHash = 'b0d5a6738100c4aa73ed01bad42a434c6fdd7418d5e0211be73ebccaff5bb6a2'

$Authorities = @(
    @{ Path = $FailedFreeze; Bytes = 4229; Hash = 'add1b36607fc51c3224fe4618cebd6bb7d80ea8ef5db7602d3c65044908c1e5d'; Label = 'Failed Attempt01 freeze' },
    @{ Path = 'D:\Skyguard52\Saved\BuildAttempts\TOOLCHAIN_WAVE08_ENVIRONMENT_M01_CLONE_SMOKE\attempt_01\terminal_manifest.json'; Bytes = 3960; Hash = '203b60b942143b7f492d00a95aaca8c6d9a9fc23e2898273f74a79ee0257119b'; Label = 'Failed Attempt01 terminal manifest' },
    @{ Path = 'D:\Skyguard52\Saved\BuildAttempts\TOOLCHAIN_WAVE08_ENVIRONMENT_M01_CLONE_SMOKE\attempt_01\probe_result.json'; Bytes = 2961; Hash = '9b56b8610cbb4b77917ba6f4d16802c45eaa02a700875d9b673ccf359344b75b'; Label = 'Failed Attempt01 probe result' },
    @{ Path = 'D:\Skyguard52\Saved\BuildAttempts\TOOLCHAIN_WAVE08_ENVIRONMENT_M01_CLONE_SMOKE\attempt_01\unreal_stdout.log'; Bytes = 225846; Hash = '01994691ba55681fc7715430f63003c6a3baeb8c7cf165684173f93655ebf249'; Label = 'Failed Attempt01 stdout' },
    @{ Path = $PreparationTerminal; Bytes = 735239; Hash = '1e467aa78e73cf117c4d13a8116022587479c83f0a952fcee43c151eb0059387'; Label = 'Environment preparation terminal' },
    @{ Path = $EnvironmentContract; Bytes = 3645; Hash = 'd48c1f86ea5cf6c8387446c75dd99fd905cf01c81d1181d409dcb1ff35317ef8'; Label = 'Environment contract' },
    @{ Path = $Project; Bytes = 3703; Hash = '7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a'; Label = 'Isolated descriptor' },
    @{ Path = $CanonicalSourceMap; Bytes = 6599; Hash = '3a3026f0387d2329c8c45e8b28e8889065d0098367933bf0193be39f744f9fd3'; Label = 'Canonical source map' },
    @{ Path = $IsolatedSourceMap; Bytes = 6599; Hash = '3a3026f0387d2329c8c45e8b28e8889065d0098367933bf0193be39f744f9fd3'; Label = 'Isolated source map' },
    @{ Path = 'D:\UE_5.8\Engine\Plugins\Experimental\Water\Water.uplugin'; Bytes = 1020; Hash = '83c357a92d54ff2e5ec2d28fc134ab4f1bcdaf463b3dd51d45f2c551480d3493'; Label = 'Water descriptor' },
    @{ Path = 'D:\UE_5.8\Engine\Plugins\Experimental\Landmass\Landmass.uplugin'; Bytes = 554; Hash = '838b95dd84be61ccffb777718f8efc8548ec8d5fc33a8395d50503a29d17a695'; Label = 'Landmass descriptor' },
    @{ Path = 'D:\UE_5.8\Engine\Plugins\PCGInterops\PCGGeometryScriptInterop\PCGGeometryScriptInterop.uplugin'; Bytes = 893; Hash = '38b7374731b422e11e7d1a174df4f47eaec6f996d7885d1e260cc07226bc4519'; Label = 'PCG descriptor' },
    @{ Path = 'D:\UE_5.8\Engine\Plugins\Experimental\Water\Source\Runtime\Public\WaterBodyOceanActor.h'; Bytes = 1151; Hash = '0296740c86b5f8e8dc7d0acda296bb2baa5abf811918513b4c36b1f8cf31acac'; Label = 'Water class header' },
    @{ Path = 'D:\UE_5.8\Engine\Plugins\Experimental\Water\Intermediate\Build\Win64\UnrealEditor\Inc\Water\UHT\WaterBodyOceanActor.generated.h'; Bytes = 5334; Hash = '1627302c59610317812c076b6e276dc4abb8175eb5e2d4a4933aa409bd385908'; Label = 'Water generated header' },
    @{ Path = 'D:\UE_5.8\Engine\Plugins\Experimental\Landmass\Source\Editor\Public\LandmassActor.h'; Bytes = 5905; Hash = '7b6c84d7dfed8c57d55501dbe2f0f9269aa84c73e154f95bf10bb71a6b5514a4'; Label = 'Landmass class header' },
    @{ Path = 'D:\UE_5.8\Engine\Plugins\Experimental\Landmass\Intermediate\Build\Win64\UnrealEditor\Inc\LandmassEditor\UHT\LandmassActor.generated.h'; Bytes = 4763; Hash = '433f64d4c9e1ef37a0624fa9e86af36bd2b3027d6a99e30062bda3e17e08a2c6'; Label = 'Landmass generated header' },
    @{ Path = 'D:\UE_5.8\Engine\Plugins\PCGInterops\PCGGeometryScriptInterop\Source\PCGGeometryScriptInterop\Public\Elements\PCGCreateEmptyDynamicMesh.h'; Bytes = 1038; Hash = 'f7d3814dee9d690ca7623017f91ae668a456722a4854967cfe4754a25265ba00'; Label = 'PCG class header' },
    @{ Path = 'D:\UE_5.8\Engine\Plugins\PCGInterops\PCGGeometryScriptInterop\Intermediate\Build\Win64\UnrealEditor\Inc\PCGGeometryScriptInterop\UHT\PCGCreateEmptyDynamicMesh.generated.h'; Bytes = 3914; Hash = '40ac05a3645df561c33afd709761fc1b03e61c551faeae8d881d3d58081e2e27'; Label = 'PCG generated header' },
    @{ Path = $SourceProbe; Bytes = 9130; Hash = $ExpectedProbeHash; Label = 'Recovery01 probe' }
)

function Get-Sha256([string]$Path) {
    $stream = [System.IO.File]::Open($Path, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::Read)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($sha.ComputeHash($stream))).Replace('-', '').ToLowerInvariant() }
    finally { $sha.Dispose(); $stream.Dispose() }
}

function Write-JsonAtomic([string]$Path, $Value) {
    $temporary = "$Path.tmp"
    $json = $Value | ConvertTo-Json -Depth 20
    [System.IO.File]::WriteAllText($temporary, $json + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
    Move-Item -LiteralPath $temporary -Destination $Path -Force
}

function Assert-NumericExitCode($Code) {
    if ($null -eq $Code) { throw 'Process exit code is null' }
    if ($Code.GetType().FullName -ne 'System.Int32') { throw "Process exit code is not System.Int32: $($Code.GetType().FullName)" }
}

function Assert-FileRecord($Record) {
    if (-not (Test-Path -LiteralPath $Record.Path -PathType Leaf)) { throw "$($Record.Label) is missing: $($Record.Path)" }
    $item = Get-Item -LiteralPath $Record.Path
    if ([long]$Record.Bytes -gt 0 -and $item.Length -ne [long]$Record.Bytes) { throw "$($Record.Label) byte-count mismatch" }
    if ((Get-Sha256 $Record.Path) -ne [string]$Record.Hash) { throw "$($Record.Label) hash mismatch" }
}

function Get-ProductionHeavyProcesses {
    return @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {
        $_.Name -match '^(UnrealEditor(-Cmd)?|Blender|ShaderCompileWorker|AutomationTool|UnrealBuildTool|cl|link)(\.exe)?$'
    })
}

function Assert-Authorities([bool]$RequireAttemptAbsent) {
    foreach ($record in $Authorities) { Assert-FileRecord $record }
    $prepared = Get-Content -LiteralPath $PreparationTerminal -Raw | ConvertFrom-Json
    if ($prepared.classification -ne 'PASSED_ISOLATED_M01_VIEW_READY_FOR_SINGLE_UNREAL_CLONE_SMOKE') { throw 'Environment preparation is not accepted' }
    if (@($prepared.output_inventory).Count -ne 2006) { throw 'Preparation inventory count is not 2006' }
    foreach ($member in @($prepared.output_inventory)) {
        $path = Join-Path $ProjectRoot ([string]$member.relative_path)
        Assert-FileRecord @{ Path = $path; Bytes = [long]$member.bytes; Hash = [string]$member.sha256; Label = 'Prepared view member' }
    }
    if ($RequireAttemptAbsent -and (Test-Path -LiteralPath $AttemptRoot)) { throw 'Recovery01 attempt namespace already exists' }
    if (Test-Path -LiteralPath $CloneMap) { throw 'Clone target already exists' }
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
        $samples += [ordered]@{ sampled_at_utc = [DateTime]::UtcNow.ToString('o'); processes = @(Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -match '^Unreal|ShaderCompileWorker' } | Select-Object Id, ProcessName, StartTime) }
        if ($watch.ElapsedMilliseconds -ge $TimeoutMilliseconds) { $timedOut = $true; try { $process.Kill() } catch {}; break }
    }
    $process.WaitForExit(); $process.Refresh()
    $stdout = $stdoutTask.GetAwaiter().GetResult(); $stderr = $stderrTask.GetAwaiter().GetResult(); $exitCode = $process.ExitCode
    Assert-NumericExitCode $exitCode
    $record = [pscustomobject]@{ FilePath=$FilePath; Arguments=$Arguments; ProcessId=$process.Id; NativeHandleRetained=($nativeHandle -ne [IntPtr]::Zero); StartedAtUtc=$startedAt.ToString('o'); CompletedAtUtc=[DateTime]::UtcNow.ToString('o'); ExitCode=$exitCode; ExitCodeType=$exitCode.GetType().FullName; TimedOut=$timedOut; Stdout=$stdout; Stderr=$stderr; Samples=$samples }
    $process.Dispose()
    return $record
}

if ($OfflineContractTest) {
    Assert-Authorities $true
    if ((Get-ProductionHeavyProcesses).Count -gt 0) { throw 'Production-heavy process detected' }
    $source = Get-Content -LiteralPath $SourceProbe -Raw
    foreach ($token in @('/Script/Water.WaterBodyOcean','/Script/LandmassEditor.LandmassActor','/Script/PCGGeometryScriptInterop.PCGCreateEmptyDynamicMeshSettings','duplicate_asset','save_asset')) {
        if (-not $source.Contains($token)) { throw "Required probe token missing: $token" }
    }
    if ($source.Contains('/Script/Landmass.LandmassBlueprintBrushBase')) { throw 'Invalid Landmass path remains' }
    Write-Output 'CLASSIFICATION=PASSED_OFFLINE_CONTRACT_TEST'
    exit 0
}

$started = [DateTime]::UtcNow
$run = $null
$failure = $null
$classification = 'FAILED_WITH_EVIDENCE'
try {
    if (-not $AuthorizeSingleUnrealSmoke) { throw 'Explicit -AuthorizeSingleUnrealSmoke is required' }
    Assert-Authorities $true
    if ((Get-ProductionHeavyProcesses).Count -gt 0) { throw 'Production-heavy process gate failed' }
    New-Item -ItemType Directory -Path $AttemptRoot -ErrorAction Stop | Out-Null
    Copy-Item -LiteralPath $SourceProbe -Destination $Probe -ErrorAction Stop
    Assert-FileRecord @{ Path=$Probe; Bytes=9130; Hash=$ExpectedProbeHash; Label='Copied Recovery01 probe' }
    Write-JsonAtomic $PreflightResult ([ordered]@{ schema='skyguard.toolchain-wave08.environment-clone-recovery01-preflight.v1'; classification='PASSED_READY_FOR_SINGLE_UNREAL_CLONE_LAUNCH'; checked_at_utc=[DateTime]::UtcNow.ToString('o'); preparation_inventory_records_verified=2006; class_paths=@('/Script/Water.WaterBodyOcean','/Script/LandmassEditor.LandmassActor','/Script/PCGGeometryScriptInterop.PCGCreateEmptyDynamicMeshSettings'); clone_target_absent=$true; production_heavy_process_count=0 })
    $arguments = @($Project,'-Unattended','-NoSplash','-NoSound','-NullRHI','-NoSaveOnExit','-stdout','-FullStdOutLogOutput','-ini:Engine:[/Script/Engine.Engine]:GameUserSettingsClassName=/Script/Engine.GameUserSettings','-run=pythonscript',"-script=$Probe")
    $run = Invoke-CapturedProcess -FilePath $Editor -Arguments $arguments -TimeoutMilliseconds 900000
    [System.IO.File]::WriteAllText($Stdout, $run.Stdout, [System.Text.UTF8Encoding]::new($false)); [System.IO.File]::WriteAllText($Stderr, $run.Stderr, [System.Text.UTF8Encoding]::new($false)); Write-JsonAtomic $ProcessSamples $run.Samples
    if ($run.TimedOut) { throw 'Unreal timed out' }
    if ($run.ExitCode -ne 0) { throw "Unreal returned exit code $($run.ExitCode)" }
    if (-not (Test-Path -LiteralPath $ProbeResult -PathType Leaf)) { throw 'Probe result was not produced' }
    $result = Get-Content -LiteralPath $ProbeResult -Raw | ConvertFrom-Json
    if ($result.classification -ne 'PASSED_ISOLATED_M01_CLONE_AND_ENVIRONMENT_CAPABILITY_SMOKE') { throw "Probe classification: $($result.classification)" }
    if (@($result.class_probes).Count -ne 3 -or @($result.class_probes | Where-Object { -not $_.module_match }).Count -ne 0) { throw 'Class-probe acceptance failed' }
    if (-not $result.clone_asset_created -or -not $result.clone_asset_saved -or -not $result.clone_asset_loaded_after -or -not $result.distinct_package_paths) { throw 'Map-clone acceptance failed' }
    if ($result.source_map_save_attempted -or $result.canonical_asset_save_attempted -or $result.environment_authoring_attempted) { throw 'Prohibited mutation attempted' }
    Assert-Authorities $false
    $classification = 'PASSED_ISOLATED_M01_CLONE_AND_ENVIRONMENT_CAPABILITY_SMOKE'
} catch { $failure = $_.Exception.Message }
finally {
    if (Test-Path -LiteralPath $AttemptRoot -PathType Container) {
        if ($null -ne $run) {
            if (-not (Test-Path -LiteralPath $Stdout)) { [System.IO.File]::WriteAllText($Stdout, $run.Stdout, [System.Text.UTF8Encoding]::new($false)) }
            if (-not (Test-Path -LiteralPath $Stderr)) { [System.IO.File]::WriteAllText($Stderr, $run.Stderr, [System.Text.UTF8Encoding]::new($false)) }
            if (-not (Test-Path -LiteralPath $ProcessSamples)) { Write-JsonAtomic $ProcessSamples $run.Samples }
        }
        $artifacts=@(); foreach($file in Get-ChildItem -LiteralPath $AttemptRoot -File -ErrorAction SilentlyContinue){if($file.FullName -ne $Terminal){$artifacts += [ordered]@{path=$file.FullName;bytes=$file.Length;sha256=Get-Sha256 $file.FullName}}}
        Write-JsonAtomic $Terminal ([ordered]@{ schema='skyguard.toolchain-wave08.environment-clone-recovery01-terminal.v1'; classification=$classification; started_at_utc=$started.ToString('o'); completed_at_utc=[DateTime]::UtcNow.ToString('o'); unreal_launch_count=if($null -eq $run){0}else{1}; retry_count=0; process_id=if($null -eq $run){$null}else{$run.ProcessId}; exit_code=if($null -eq $run){$null}else{$run.ExitCode}; exit_code_type=if($null -eq $run){$null}else{$run.ExitCodeType}; timed_out=if($null -eq $run){$false}else{$run.TimedOut}; failure=$failure; artifacts=$artifacts })
    }
    Write-Output "CLASSIFICATION=$classification"
    if ($classification -ne 'PASSED_ISOLATED_M01_CLONE_AND_ENVIRONMENT_CAPABILITY_SMOKE') { exit 1 }
}
