param(
    [switch]$OfflineContractTest,
    [switch]$AuthorizeSingleUnrealSmoke
)

$ErrorActionPreference = 'Stop'
$AttemptRoot = 'D:\Skyguard52\Saved\BuildAttempts\TOOLCHAIN_WAVE08_ENVIRONMENT_M01_CLONE_SMOKE_RECOVERY02\attempt_01'
$SourceProbe = 'D:\Skyguard52\Scripts\ToolchainWave08\environment_clone_recovery02\environment_clone_probe_recovery02.py'
$Probe = Join-Path $AttemptRoot 'environment_clone_probe_recovery02.py'
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
$Recovery01Freeze = 'D:\Skyguard52\Docs\AAA_Review\TOOLCHAIN_WAVE08_ENVIRONMENT_M01_CLONE_SMOKE_RECOVERY01_ATTEMPT01_TERMINAL_FREEZE.json'
$CanonicalSourceMap = 'D:\Skyguard52\Content\Skyguard\Maps\Lvl_M01_CoastalIntercept_ProductionEnvironment_v4.umap'
$IsolatedSourceMap = 'D:\SG52T08_ENV01\Content\Skyguard\Maps\Lvl_M01_CoastalIntercept_ProductionEnvironment_v4.umap'
$CloneMap = 'D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_WaterLandmassPCG_Prototype02.umap'
$ExpectedProbeHash = 'a027419c44d2bf49bc4d761fe12aec1b7dc69d95f5ab5ce03b8910332c604e1f'
$ExpectedCanonicalHash = '99461a1a562ede732da52c84f05002dcc88f772cd30fdccd45ff46d6836f3b60'
$ExpectedIsolatedHash = '7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a'
$ExpectedSourceMapHash = '3a3026f0387d2329c8c45e8b28e8889065d0098367933bf0193be39f744f9fd3'

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

function Assert-FileRecord([string]$Path, [long]$Bytes, [string]$Hash, [string]$Label) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw "$Label is missing: $Path" }
    $item = Get-Item -LiteralPath $Path
    if ($item.Length -ne $Bytes) { throw "$Label byte-count mismatch: $Path" }
    if ((Get-Sha256 $Path) -ne $Hash) { throw "$Label hash mismatch: $Path" }
}

function Get-ProductionHeavyProcesses {
    return @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {
        $_.Name -match '^(UnrealEditor(-Cmd)?|Blender|ShaderCompileWorker|AutomationTool|UnrealBuildTool|cl|link)(\.exe)?$'
    })
}

function Assert-CommonAuthorities {
    Assert-FileRecord $Recovery01Freeze 4404 'dc763167d80901256c651638e141fc0e73a1ac81d002252806e2d8454b1903ec' 'Recovery01 terminal freeze'
    Assert-FileRecord $EnvironmentContract 3645 'd48c1f86ea5cf6c8387446c75dd99fd905cf01c81d1181d409dcb1ff35317ef8' 'Environment contract'
    Assert-FileRecord $PreparationTerminal 735239 '1e467aa78e73cf117c4d13a8116022587479c83f0a952fcee43c151eb0059387' 'Environment preparation terminal'
    Assert-FileRecord $CanonicalProject 1542 $ExpectedCanonicalHash 'Canonical descriptor'
    Assert-FileRecord $Project 3703 $ExpectedIsolatedHash 'Isolated descriptor'
    Assert-FileRecord $CanonicalSourceMap 6599 $ExpectedSourceMapHash 'Canonical source map'
    Assert-FileRecord $IsolatedSourceMap 6599 $ExpectedSourceMapHash 'Isolated source map'
    Assert-FileRecord $SourceProbe 9130 $ExpectedProbeHash 'Recovery02 probe'
    $prepared = Get-Content -LiteralPath $PreparationTerminal -Raw | ConvertFrom-Json
    if ($prepared.classification -ne 'PASSED_ISOLATED_M01_VIEW_READY_FOR_SINGLE_UNREAL_CLONE_SMOKE') { throw 'Environment preparation is not accepted' }
    if (@($prepared.output_inventory).Count -ne 2006) { throw 'Preparation inventory count is not 2006' }
    foreach ($member in @($prepared.output_inventory)) {
        $path = Join-Path $ProjectRoot ([string]$member.relative_path)
        Assert-FileRecord $path ([long]$member.bytes) ([string]$member.sha256) 'Prepared view member'
    }
}

function Assert-PreflightState([string]$AttemptPath, [string]$ClonePath) {
    if (Test-Path -LiteralPath $AttemptPath) { throw 'Attempt namespace already exists' }
    if (Test-Path -LiteralPath $ClonePath) { throw 'Clone target already exists before launch' }
}

function Assert-PostflightState([string]$AttemptPath, [string]$ClonePath, [string]$ResultPath) {
    if (-not (Test-Path -LiteralPath $AttemptPath -PathType Container)) { throw 'Attempt namespace is missing after execution' }
    if (-not (Test-Path -LiteralPath $ResultPath -PathType Leaf)) { throw 'Probe result is missing after execution' }
    if (-not (Test-Path -LiteralPath $ClonePath -PathType Leaf)) { throw 'Clone target is missing after execution' }
    $result = Get-Content -LiteralPath $ResultPath -Raw | ConvertFrom-Json
    if ($result.classification -ne 'PASSED_ISOLATED_M01_CLONE_AND_ENVIRONMENT_CAPABILITY_SMOKE') { throw 'Probe classification failed' }
    if ($null -ne $result.error) { throw 'Probe contains an error' }
    if (@($result.class_probes).Count -ne 3) { throw 'Probe did not record exactly three class authorities' }
    if (@($result.class_probes | Where-Object { -not $_.module_match }).Count -ne 0) { throw 'Class owning-module mismatch' }
    if (-not $result.source_asset_loaded -or -not $result.clone_asset_absent_before -or -not $result.clone_asset_created -or -not $result.clone_asset_saved -or -not $result.clone_asset_loaded_after -or -not $result.distinct_package_paths) { throw 'Map clone lifecycle evidence failed' }
    if ($result.source_map_save_attempted -or $result.canonical_asset_save_attempted -or $result.environment_authoring_attempted) { throw 'Prohibited mutation was attempted' }
    if ((Get-Sha256 $ClonePath) -ne [string]$result.clone_file_sha256) { throw 'Clone hash does not match probe receipt' }
    if ($result.canonical_descriptor_sha256_before -ne $ExpectedCanonicalHash -or $result.canonical_descriptor_sha256_after -ne $ExpectedCanonicalHash) { throw 'Canonical descriptor authority changed' }
    if ($result.isolated_descriptor_sha256_before -ne $ExpectedIsolatedHash -or $result.isolated_descriptor_sha256_after -ne $ExpectedIsolatedHash) { throw 'Isolated descriptor authority changed' }
    if ($result.canonical_source_sha256_before -ne $ExpectedSourceMapHash -or $result.canonical_source_sha256_after -ne $ExpectedSourceMapHash) { throw 'Canonical source map authority changed' }
    if ($result.isolated_source_sha256_before -ne $ExpectedSourceMapHash -or $result.isolated_source_sha256_after -ne $ExpectedSourceMapHash) { throw 'Isolated source map authority changed' }
}

function Assert-PreflightAuthorities {
    Assert-CommonAuthorities
    if ((Get-ProductionHeavyProcesses).Count -gt 0) { throw 'Production-heavy process detected before launch' }
    Assert-PreflightState $AttemptRoot $CloneMap
}

function Assert-PostflightAuthorities {
    Assert-CommonAuthorities
    Assert-PostflightState $AttemptRoot $CloneMap $ProbeResult
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
        $samples += [ordered]@{ sampled_at_utc=[DateTime]::UtcNow.ToString('o'); processes=@(Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -match '^Unreal|ShaderCompileWorker' } | Select-Object Id,ProcessName,StartTime) }
        if ($watch.ElapsedMilliseconds -ge $TimeoutMilliseconds) { $timedOut=$true; try { $process.Kill() } catch {}; break }
    }
    $process.WaitForExit(); $process.Refresh()
    $stdout=$stdoutTask.GetAwaiter().GetResult(); $stderr=$stderrTask.GetAwaiter().GetResult(); $exitCode=$process.ExitCode
    Assert-NumericExitCode $exitCode
    $record=[pscustomobject]@{FilePath=$FilePath;Arguments=$Arguments;ProcessId=$process.Id;NativeHandleRetained=($nativeHandle -ne [IntPtr]::Zero);StartedAtUtc=$startedAt.ToString('o');CompletedAtUtc=[DateTime]::UtcNow.ToString('o');ExitCode=$exitCode;ExitCodeType=$exitCode.GetType().FullName;TimedOut=$timedOut;Stdout=$stdout;Stderr=$stderr;Samples=$samples}
    $process.Dispose(); return $record
}

function Expect-Failure([scriptblock]$Action, [string]$Label) {
    try { & $Action; throw "Expected failure did not occur: $Label" } catch {
        if ($_.Exception.Message -eq "Expected failure did not occur: $Label") { throw }
    }
}

if ($OfflineContractTest) {
    Assert-CommonAuthorities
    if ((Get-ProductionHeavyProcesses).Count -gt 0) { throw 'Production-heavy process detected during offline test' }
    $testRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("SkyguardRecovery02_" + [Guid]::NewGuid().ToString('N'))
    $testAttempt = Join-Path $testRoot 'attempt'
    $testClone = Join-Path $testRoot 'clone.umap'
    $testResult = Join-Path $testAttempt 'probe_result.json'
    try {
        New-Item -ItemType Directory -Path $testRoot | Out-Null
        Assert-PreflightState $testAttempt $testClone
        [System.IO.File]::WriteAllText($testClone, 'clone-a', [System.Text.UTF8Encoding]::new($false))
        Expect-Failure { Assert-PreflightState $testAttempt $testClone } 'preflight existing clone'
        Remove-Item -LiteralPath $testClone -Force
        New-Item -ItemType Directory -Path $testAttempt | Out-Null
        [System.IO.File]::WriteAllText($testClone, 'clone-b', [System.Text.UTF8Encoding]::new($false))
        $valid=[ordered]@{classification='PASSED_ISOLATED_M01_CLONE_AND_ENVIRONMENT_CAPABILITY_SMOKE';error=$null;class_probes=@(@{module_match=$true},@{module_match=$true},@{module_match=$true});source_asset_loaded=$true;clone_asset_absent_before=$true;clone_asset_created=$true;clone_asset_saved=$true;clone_asset_loaded_after=$true;distinct_package_paths=$true;source_map_save_attempted=$false;canonical_asset_save_attempted=$false;environment_authoring_attempted=$false;clone_file_sha256=Get-Sha256 $testClone;canonical_descriptor_sha256_before=$ExpectedCanonicalHash;canonical_descriptor_sha256_after=$ExpectedCanonicalHash;isolated_descriptor_sha256_before=$ExpectedIsolatedHash;isolated_descriptor_sha256_after=$ExpectedIsolatedHash;canonical_source_sha256_before=$ExpectedSourceMapHash;canonical_source_sha256_after=$ExpectedSourceMapHash;isolated_source_sha256_before=$ExpectedSourceMapHash;isolated_source_sha256_after=$ExpectedSourceMapHash}
        Write-JsonAtomic $testResult $valid
        Assert-PostflightState $testAttempt $testClone $testResult
        Remove-Item -LiteralPath $testClone -Force
        Expect-Failure { Assert-PostflightState $testAttempt $testClone $testResult } 'postflight missing clone'
        [System.IO.File]::WriteAllText($testClone, 'clone-c', [System.Text.UTF8Encoding]::new($false))
        Expect-Failure { Assert-PostflightState $testAttempt $testClone $testResult } 'postflight clone hash mismatch'
        $valid.clone_file_sha256=Get-Sha256 $testClone; $valid.classification='FAILED_WITH_EVIDENCE'; Write-JsonAtomic $testResult $valid
        Expect-Failure { Assert-PostflightState $testAttempt $testClone $testResult } 'postflight failed classification'
        $valid.classification='PASSED_ISOLATED_M01_CLONE_AND_ENVIRONMENT_CAPABILITY_SMOKE'; $valid.class_probes[1].module_match=$false; Write-JsonAtomic $testResult $valid
        Expect-Failure { Assert-PostflightState $testAttempt $testClone $testResult } 'postflight module mismatch'
        $valid.class_probes[1].module_match=$true; $valid.canonical_descriptor_sha256_after='wrong'; Write-JsonAtomic $testResult $valid
        Expect-Failure { Assert-PostflightState $testAttempt $testClone $testResult } 'postflight canonical mismatch'
    } finally {
        $resolved=[System.IO.Path]::GetFullPath($testRoot); $temp=[System.IO.Path]::GetFullPath([System.IO.Path]::GetTempPath())
        if ($resolved.StartsWith($temp,[System.StringComparison]::OrdinalIgnoreCase) -and (Test-Path -LiteralPath $resolved)) { Remove-Item -LiteralPath $resolved -Recurse -Force }
    }
    if (Test-Path -LiteralPath $AttemptRoot) { throw 'Governed Recovery02 attempt namespace was created by offline test' }
    if (Test-Path -LiteralPath $CloneMap) { throw 'Governed Recovery02 clone was created by offline test' }
    Write-Output 'CLASSIFICATION=PASSED_RECOVERY02_OFFLINE_CONTRACT_TEST'
    exit 0
}

$started=[DateTime]::UtcNow; $run=$null; $failure=$null; $classification='FAILED_WITH_EVIDENCE'
try {
    if (-not $AuthorizeSingleUnrealSmoke) { throw 'Explicit -AuthorizeSingleUnrealSmoke is required' }
    Assert-PreflightAuthorities
    New-Item -ItemType Directory -Path $AttemptRoot | Out-Null
    Copy-Item -LiteralPath $SourceProbe -Destination $Probe
    Write-JsonAtomic $PreflightResult ([ordered]@{schema='skyguard.toolchain-wave08.environment-clone-recovery02-preflight.v1';classification='PASSED_READY_FOR_SINGLE_UNREAL_CLONE_LAUNCH';checked_at_utc=[DateTime]::UtcNow.ToString('o');preparation_inventory_records_verified=2006;clone_target_absent=$true;heavy_process_count=0})
    $arguments=@($Project,'-Unattended','-NoSplash','-NoSound','-NullRHI','-NoSaveOnExit','-stdout','-FullStdOutLogOutput','-ini:Engine:[/Script/Engine.Engine]:GameUserSettingsClassName=/Script/Engine.GameUserSettings','-run=pythonscript',"-script=$Probe")
    $run=Invoke-CapturedProcess -FilePath $Editor -Arguments $arguments -TimeoutMilliseconds 900000
    [System.IO.File]::WriteAllText($Stdout,$run.Stdout,[System.Text.UTF8Encoding]::new($false));[System.IO.File]::WriteAllText($Stderr,$run.Stderr,[System.Text.UTF8Encoding]::new($false));Write-JsonAtomic $ProcessSamples $run.Samples
    if($run.TimedOut){throw 'Unreal timed out'};if($run.ExitCode -ne 0){throw "Unreal returned exit code $($run.ExitCode)"}
    Assert-PostflightAuthorities
    $classification='PASSED_ISOLATED_M01_CLONE_AND_ENVIRONMENT_CAPABILITY_SMOKE'
} catch { $failure=$_.Exception.Message }
finally {
    if(Test-Path -LiteralPath $AttemptRoot -PathType Container){
        $artifacts=@();foreach($file in Get-ChildItem -LiteralPath $AttemptRoot -File -ErrorAction SilentlyContinue){if($file.FullName -ne $Terminal){$artifacts += [ordered]@{path=$file.FullName;bytes=$file.Length;sha256=Get-Sha256 $file.FullName}}}
        Write-JsonAtomic $Terminal ([ordered]@{schema='skyguard.toolchain-wave08.environment-clone-recovery02-terminal.v1';classification=$classification;started_at_utc=$started.ToString('o');completed_at_utc=[DateTime]::UtcNow.ToString('o');unreal_launch_count=if($null -eq $run){0}else{1};retry_count=0;exit_code=if($null -eq $run){$null}else{$run.ExitCode};exit_code_type=if($null -eq $run){$null}else{$run.ExitCodeType};timed_out=if($null -eq $run){$false}else{$run.TimedOut};failure=$failure;artifacts=$artifacts})
    }
    Write-Output "CLASSIFICATION=$classification"
    if($classification -ne 'PASSED_ISOLATED_M01_CLONE_AND_ENVIRONMENT_CAPABILITY_SMOKE'){exit 1}
}
