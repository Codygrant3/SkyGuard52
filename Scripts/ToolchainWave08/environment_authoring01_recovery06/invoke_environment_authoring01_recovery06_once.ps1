param(
    [switch]$OfflineContractTest,
    [switch]$AuthorizeSingleUnrealAuthoring
)

$ErrorActionPreference = 'Stop'
$CanonicalRoot = 'D:\Skyguard52'
$ProjectRoot = 'D:\SG52T08_ENV01'
$Project = Join-Path $ProjectRoot 'Skyguard52.uproject'
$CanonicalProject = Join-Path $CanonicalRoot 'Skyguard52.uproject'
$Editor = 'D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$AttemptRoot = 'D:\Skyguard52\Saved\BuildAttempts\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY06\attempt_01'
$ExternalTerminal = 'D:\Skyguard52\Saved\Reports\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY06_TERMINAL_SUPERVISOR_MANIFEST.json'
$EmergencyReceipt = 'D:\Skyguard52\Saved\Reports\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY06_EMERGENCY_RECEIPT.jsonl'
$SourceAuthoring = 'D:\Skyguard52\Scripts\ToolchainWave08\environment_authoring01_recovery06\author_m01_environment_authoring01_recovery06.py'
$AttemptAuthoring = Join-Path $AttemptRoot 'author_m01_environment_authoring01_recovery06.py'
$AssetManifest = 'D:\Skyguard52\Docs\Toolchain\ToolchainWave08\EnvironmentAuthoring01\existing_asset_dependency_inventory.json'
$Receipt = Join-Path $AttemptRoot 'authoring_receipt.json'
$Stdout = Join-Path $AttemptRoot 'unreal_stdout.log'
$Stderr = Join-Path $AttemptRoot 'unreal_stderr.log'
$ProcessSamples = Join-Path $AttemptRoot 'process_tree_samples.json'
$PreflightReceipt = Join-Path $AttemptRoot 'preflight_receipt.json'
$InputMap = 'D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_WaterLandmassPCG_Prototype01.umap'
$OutputMap = 'D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentAuthoring01_Recovery06.umap'
$CanonicalSourceMap = 'D:\Skyguard52\Content\Skyguard\Maps\Lvl_M01_CoastalIntercept_ProductionEnvironment_v4.umap'
$IsolatedSourceMap = 'D:\SG52T08_ENV01\Content\Skyguard\Maps\Lvl_M01_CoastalIntercept_ProductionEnvironment_v4.umap'
$CapabilityFreeze = 'D:\Skyguard52\Docs\AAA_Review\TOOLCHAIN_WAVE08_ENVIRONMENT_M01_CLONE_SMOKE_RECOVERY02_CAPABILITY_ACCEPTANCE_FREEZE.json'
$Recovery02Freeze = 'D:\Skyguard52\Docs\AAA_Review\TOOLCHAIN_WAVE08_ENVIRONMENT_M01_CLONE_SMOKE_RECOVERY02_OFFLINE_DESIGN_FREEZE.json'
$ExpectedAuthoringHash = 'd077cba756dc59149bc0411c46051aa5ff20acb86ac0f489a53fc1557f8d27c0'
$ExpectedAssetManifestHash = 'a234975cd7efd241052d1d4580f8ad4af24b795e5ff735824dbb7a81603d8a59'
$ExpectedCanonicalProjectHash = '99461a1a562ede732da52c84f05002dcc88f772cd30fdccd45ff46d6836f3b60'
$ExpectedIsolatedProjectHash = '7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a'
$ExpectedSourceMapHash = '3a3026f0387d2329c8c45e8b28e8889065d0098367933bf0193be39f744f9fd3'
$ExpectedInputHash = '5c8b7c6b0c6024767fa8a671523b5626213bd029d591270654080aed5fc7ced4'
$DependencyProbeFreeze = 'D:\Skyguard52\Docs\AAA_Review\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY04_DEPENDENCY_PROBE_TERMINAL_FREEZE.json'
$ExpectedDependencyProbeFreezeHash = '6531cf1a9a0c9f83b4f51981e3f52e6c2e65f45dcd99b9216b0c6ca95c1f72fd'
$Recovery04FailureFreeze = 'D:\Skyguard52\Docs\AAA_Review\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY04_ATTEMPT01_TERMINAL_FREEZE.json'
$ExpectedRecovery04FailureFreezeHash = '18f5b8a77e4b48b1a324ba007b7280449d4c417a3e2c458e59b0df2128f3162a'
$Recovery05TerminalFreeze = 'D:\Skyguard52\Docs\AAA_Review\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY05_ATTEMPT01_TERMINAL_FREEZE.json'
$ExpectedRecovery05TerminalFreezeHash = '4fb2b6375021bc74083faccd5c2ad55d5ee1c34119ccfd5853090f347bf0dccb'

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
    $json = $Value | ConvertTo-Json -Depth 30
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
    if ($item.Length -ne $Bytes) { throw "$Label byte mismatch: $Path" }
    if ((Get-Sha256 $Path) -ne $Hash) { throw "$Label hash mismatch: $Path" }
}

function Get-HeavyProcesses {
    return @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {
        $_.Name -match '^(UnrealEditor(-Cmd)?|Blender|ShaderCompileWorker|AutomationTool|UnrealBuildTool|cl|link)(\.exe)?$'
    })
}

function Assert-FreezeMembers([string]$FreezePath, [string]$Classification) {
    $freeze = Get-Content -LiteralPath $FreezePath -Raw | ConvertFrom-Json
    if ($freeze.classification -ne $Classification) { throw "Freeze classification mismatch: $FreezePath" }
    foreach ($member in @($freeze.members)) {
        Assert-FileRecord ([string]$member.path) ([long]$member.bytes) ([string]$member.sha256) 'Frozen member'
    }
}

function Assert-CommonAuthorities {
    Assert-FileRecord $DependencyProbeFreeze 3725 $ExpectedDependencyProbeFreezeHash 'Recovery04 dependency-probe terminal freeze'
    Assert-FreezeMembers $DependencyProbeFreeze 'PASSED_DEPENDENCY_PROBE_READY_FOR_RECOVERY04_FREEZE'
    Assert-FileRecord $Recovery04FailureFreeze 3968 $ExpectedRecovery04FailureFreezeHash 'Recovery04 failed authoring terminal freeze'
    Assert-FreezeMembers $Recovery04FailureFreeze 'FAILED_WITH_EVIDENCE'
    Assert-FileRecord $Recovery05TerminalFreeze 5586 $ExpectedRecovery05TerminalFreezeHash 'Recovery05 commandlet crash terminal freeze'
    Assert-FreezeMembers $Recovery05TerminalFreeze 'FAILED_WITH_EVIDENCE'
    Assert-FileRecord $CapabilityFreeze 2124 '19ffa2ec415b5f12b33964f1c2893c99f2fb8dca46473e57f4b6d29b307b3d6c' 'Capability acceptance freeze'
    Assert-FileRecord $Recovery02Freeze 3927 '419ddfc5b07da8053a0e654528e2d81f138fe4d131d012b871ecea9a89f2c25e' 'Recovery02 offline-design freeze'
    Assert-FreezeMembers $CapabilityFreeze 'PASSED_ENVIRONMENT_CAPABILITY_EVIDENCE_ACCEPTED'
    Assert-FreezeMembers $Recovery02Freeze 'PASSED_RECOVERY02_ENVIRONMENT_CAPABILITY_EVIDENCE_ACCEPTED_AND_SUPERVISOR_CORRECTED'
    Assert-FileRecord $CanonicalProject 1542 $ExpectedCanonicalProjectHash 'Canonical project descriptor'
    Assert-FileRecord $Project 3703 $ExpectedIsolatedProjectHash 'Isolated project descriptor'
    Assert-FileRecord $CanonicalSourceMap 6599 $ExpectedSourceMapHash 'Canonical source map'
    Assert-FileRecord $IsolatedSourceMap 6599 $ExpectedSourceMapHash 'Isolated source map'
    Assert-FileRecord $InputMap 8681 $ExpectedInputHash 'Accepted input clone'
    Assert-FileRecord $SourceAuthoring (Get-Item -LiteralPath $SourceAuthoring).Length $ExpectedAuthoringHash 'Authoring script'
    Assert-FileRecord $AssetManifest (Get-Item -LiteralPath $AssetManifest).Length $ExpectedAssetManifestHash 'Asset manifest'
    $manifest = Get-Content -LiteralPath $AssetManifest -Raw | ConvertFrom-Json
    foreach ($record in @($manifest.accepted_records)) {
        Assert-FileRecord ([string]$record.path) ([long]$record.bytes) ([string]$record.sha256) 'Authoring dependency'
    }
}

function Assert-PreflightAuthorities {
    Assert-CommonAuthorities
    if ((Get-HeavyProcesses).Count -gt 0) { throw 'Production-heavy process detected before launch' }
    if (Test-Path -LiteralPath $AttemptRoot) { throw 'Authoring01 attempt namespace already exists' }
    if (Test-Path -LiteralPath $OutputMap) { throw 'Authoring01 output already exists' }
    if (Test-Path -LiteralPath $ExternalTerminal) { throw 'Authoring01 external terminal manifest already exists' }
    if (Test-Path -LiteralPath $EmergencyReceipt) { throw 'Authoring01 emergency receipt already exists' }
}

function Assert-PostflightAuthorities {
    Assert-CommonAuthorities
    if (-not (Test-Path -LiteralPath $AttemptRoot -PathType Container)) { throw 'Attempt namespace is missing after execution' }
    if (-not (Test-Path -LiteralPath $Receipt -PathType Leaf)) { throw 'Authoring receipt is missing' }
    if (-not (Test-Path -LiteralPath $OutputMap -PathType Leaf)) { throw 'Authoring01 output map is missing' }
    $receiptValue = Get-Content -LiteralPath $Receipt -Raw | ConvertFrom-Json
    if ($receiptValue.classification -ne 'PASSED_M01_ENVIRONMENT_AUTHORING01_RECOVERY06_AUTOMATIC') { throw 'Authoring receipt classification failed' }
    if ($null -ne $receiptValue.error) { throw 'Authoring receipt contains an error' }
    if ($receiptValue.input_sha256_before -ne $ExpectedInputHash -or $receiptValue.input_sha256_after -ne $ExpectedInputHash) { throw 'Input clone parity failed' }
    if ((Get-Sha256 $OutputMap) -ne [string]$receiptValue.output_sha256) { throw 'Output map hash differs from receipt' }
    if (@($receiptValue.saved_assets).Count -ne 1 -or $receiptValue.saved_assets[0] -ne '/Game/ToolchainWave08/Environment/Lvl_M01_T08_EnvironmentAuthoring01_Recovery06') { throw 'Save allowlist evidence failed' }
    if (@($receiptValue.unexpected_assets).Count -ne 0) { throw 'Unexpected Authoring01 assets were created' }
    if ($receiptValue.pcg_seed -ne 520801 -or $receiptValue.pcg_generation -ne 'DISABLED_FIXED_DIRECT_PLACEMENT_ONLY') { throw 'PCG fail-closed contract failed' }
    if ($receiptValue.pcg_registry_initialization.passed -ne $true) { throw 'PCG registry initialization evidence failed' }
    if (@($receiptValue.pcg_tree_validation).Count -ne 3 -or @($receiptValue.pcg_tree_validation | Where-Object { $_.passed -ne $true }).Count -ne 0) { throw 'PCG tree validation evidence failed' }
    if ($null -eq $receiptValue.director_acquisition -or $receiptValue.director_acquisition.after_count -ne 1) { throw 'Environment director acquisition evidence failed' }
    if ($receiptValue.director_acquisition.action -notin @('SPAWNED_DETERMINISTICALLY_IN_FRESH_OUTPUT','REUSED_SINGLE_EXISTING_OUTPUT_DIRECTOR')) { throw 'Environment director acquisition action is invalid' }
    if (@($receiptValue.post_actor_inventory | Where-Object { $_.label -eq 'M01_A01_EnvironmentDirector' }).Count -ne 1) { throw 'Environment director actor count is not exactly one' }
    if (@($receiptValue.post_actor_inventory | Where-Object { $_.label -like 'M01_A01_Tree_*' }).Count -ne 15) { throw 'Vegetation count is not exactly 15' }
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
    try { & $Action; throw "Expected failure did not occur: $Label" }
    catch { if ($_.Exception.Message -eq "Expected failure did not occur: $Label") { throw } }
}

if ($OfflineContractTest) {
    Assert-CommonAuthorities
    if ((Get-HeavyProcesses).Count -gt 0) { throw 'Production-heavy process detected during offline test' }
    $testRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("SkyguardAuthoring01Recovery06_" + [Guid]::NewGuid().ToString('N'))
    try {
        New-Item -ItemType Directory -Path $testRoot | Out-Null
        $testInput = Join-Path $testRoot 'input.umap'
        $testOutput = Join-Path $testRoot 'output.umap'
        [System.IO.File]::WriteAllText($testInput, 'input', [System.Text.UTF8Encoding]::new($false))
        if (Test-Path -LiteralPath $testOutput) { throw 'Temporary output unexpectedly exists' }
        [System.IO.File]::WriteAllText($testOutput, 'output', [System.Text.UTF8Encoding]::new($false))
        Expect-Failure { if (Test-Path -LiteralPath $testOutput) { throw 'Authoring01 output already exists' } } 'existing output'
        $terminalTest = Join-Path $testRoot 'terminal.json'
        Write-JsonAtomic $terminalTest ([ordered]@{classification='OFFLINE_TEST';exit_code=0;exit_code_type='System.Int32';retry_count=0})
        $loaded = Get-Content -LiteralPath $terminalTest -Raw | ConvertFrom-Json
        if ($loaded.exit_code_type -ne 'System.Int32' -or $loaded.retry_count -ne 0) { throw 'Terminal serialization contract failed' }
        Expect-Failure { Assert-NumericExitCode $null } 'null exit code'
    } finally {
        $resolved=[System.IO.Path]::GetFullPath($testRoot); $temp=[System.IO.Path]::GetFullPath([System.IO.Path]::GetTempPath())
        if ($resolved.StartsWith($temp,[System.StringComparison]::OrdinalIgnoreCase) -and (Test-Path -LiteralPath $resolved)) { Remove-Item -LiteralPath $resolved -Recurse -Force }
    }
    if (Test-Path -LiteralPath $AttemptRoot) { throw 'Governed Authoring01 attempt namespace was created by offline test' }
    if (Test-Path -LiteralPath $OutputMap) { throw 'Governed Authoring01 output was created by offline test' }
    Write-Output 'CLASSIFICATION=PASSED_M01_ENVIRONMENT_AUTHORING01_RECOVERY06_OFFLINE_CONTRACT_TEST'
    exit 0
}

$started=[DateTime]::UtcNow
$run=$null
$failure=$null
$classification='FAILED_WITH_EVIDENCE'
$preflightPassed=$false
try {
    if (-not $AuthorizeSingleUnrealAuthoring) { throw 'Explicit -AuthorizeSingleUnrealAuthoring is required' }
    Assert-PreflightAuthorities
    $preflightPassed=$true
    New-Item -ItemType Directory -Path $AttemptRoot | Out-Null
    Copy-Item -LiteralPath $SourceAuthoring -Destination $AttemptAuthoring
    Write-JsonAtomic $PreflightReceipt ([ordered]@{schema='skyguard.toolchain-wave08.m01-authoring01-recovery06-preflight.v1';classification='PASSED_READY_FOR_SINGLE_UNREAL_AUTHORING_RECOVERY06';checked_at_utc=[DateTime]::UtcNow.ToString('o');input_hash=$ExpectedInputHash;output_absent=$true;heavy_process_count=0})
    $arguments=@($Project,'-Unattended','-NoSplash','-NoSound','-NullRHI','-NoSaveOnExit','-stdout','-FullStdOutLogOutput',"-ExecutePythonScript=$AttemptAuthoring",'-ScriptErrorsAreFatal')
    $run=Invoke-CapturedProcess -FilePath $Editor -Arguments $arguments -TimeoutMilliseconds 1200000
    [System.IO.File]::WriteAllText($Stdout,$run.Stdout,[System.Text.UTF8Encoding]::new($false))
    [System.IO.File]::WriteAllText($Stderr,$run.Stderr,[System.Text.UTF8Encoding]::new($false))
    Write-JsonAtomic $ProcessSamples $run.Samples
    if($run.TimedOut){throw 'Unreal authoring timed out'}
    if($run.ExitCode -ne 0){throw "Unreal authoring returned exit code $($run.ExitCode)"}
    Assert-PostflightAuthorities
    $classification='PASSED_M01_ENVIRONMENT_AUTHORING01_RECOVERY06_AUTOMATIC_AWAITING_VISUAL_PROOF'
} catch { $failure=$_.Exception.Message }
finally {
    $artifacts=@()
    if(Test-Path -LiteralPath $AttemptRoot -PathType Container){
        foreach($file in Get-ChildItem -LiteralPath $AttemptRoot -File -ErrorAction SilentlyContinue){$artifacts += [ordered]@{path=$file.FullName;bytes=$file.Length;sha256=Get-Sha256 $file.FullName}}
    }
    $terminalValue=[ordered]@{schema='skyguard.toolchain-wave08.m01-authoring01-recovery06-terminal-supervisor.v1';classification=$classification;started_at_utc=$started.ToString('o');completed_at_utc=[DateTime]::UtcNow.ToString('o');preflight_passed=$preflightPassed;unreal_launch_count=if($null -eq $run){0}else{1};retry_count=0;exit_code=if($null -eq $run){$null}else{$run.ExitCode};exit_code_type=if($null -eq $run){$null}else{$run.ExitCodeType};timed_out=if($null -eq $run){$false}else{$run.TimedOut};failure=$failure;input_hash_after=if(Test-Path -LiteralPath $InputMap){Get-Sha256 $InputMap}else{$null};output_hash=if(Test-Path -LiteralPath $OutputMap){Get-Sha256 $OutputMap}else{$null};artifacts=$artifacts}
    try { Write-JsonAtomic $ExternalTerminal $terminalValue }
    catch {
        $line=([ordered]@{created_at_utc=[DateTime]::UtcNow.ToString('o');classification='FAILED_WITH_EVIDENCE';failure_stage='terminal_manifest_write';message=$_.Exception.Message} | ConvertTo-Json -Compress)
        [System.IO.File]::AppendAllText($EmergencyReceipt,$line+[Environment]::NewLine,[System.Text.UTF8Encoding]::new($false))
    }
    Write-Output "CLASSIFICATION=$classification"
    if($classification -ne 'PASSED_M01_ENVIRONMENT_AUTHORING01_RECOVERY06_AUTOMATIC_AWAITING_VISUAL_PROOF'){exit 1}
}
