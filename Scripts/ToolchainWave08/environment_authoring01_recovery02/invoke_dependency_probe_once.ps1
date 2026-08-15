param(
    [switch]$AuthorizeSingleDependencyProbe,
    [switch]$OfflineContractTest
)

$ErrorActionPreference = 'Stop'
$ProjectRoot = 'D:\Skyguard52'
$IsolatedRoot = 'D:\SG52T08_ENV01'
$Editor = 'D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$Project = Join-Path $IsolatedRoot 'Skyguard52.uproject'
$ScriptRoot = Join-Path $ProjectRoot 'Scripts\ToolchainWave08\environment_authoring01_recovery02'
$ProbeSource = Join-Path $ScriptRoot 'probe_environment_dependencies.py'
$ExpectedInputHash = '5c8b7c6b0c6024767fa8a671523b5626213bd029d591270654080aed5fc7ced4'
$InputMap = Join-Path $IsolatedRoot 'Content\ToolchainWave08\Environment\Lvl_M01_T08_WaterLandmassPCG_Prototype01.umap'
$OriginalOutput = Join-Path $IsolatedRoot 'Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentAuthoring01.umap'
$RecoveryOutput = Join-Path $IsolatedRoot 'Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentAuthoring01_Recovery02.umap'
$script:UnrealLaunchFunctionEntered = $false

function Get-Sha256([string]$Path) {
    $stream = [System.IO.File]::Open($Path,[System.IO.FileMode]::Open,[System.IO.FileAccess]::Read,[System.IO.FileShare]::Read)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($sha.ComputeHash($stream))).Replace('-','').ToLowerInvariant() }
    finally { $sha.Dispose(); $stream.Dispose() }
}

function Write-JsonAtomic([string]$Path, $Value) {
    $parent = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $parent)) { [System.IO.Directory]::CreateDirectory($parent) | Out-Null }
    $temporary = "$Path.tmp"
    $Value | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath $temporary -Encoding UTF8
    Move-Item -LiteralPath $temporary -Destination $Path -Force
}

function Assert-File([string]$Path, [int64]$Bytes, [string]$Hash) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw "Missing authority: $Path" }
    $item = Get-Item -LiteralPath $Path
    if ($item.Length -ne $Bytes) { throw "Byte-count mismatch: $Path" }
    if ((Get-Sha256 $Path) -ne $Hash) { throw "SHA-256 mismatch: $Path" }
}

function Assert-NumericExitCode($Code) {
    if ($null -eq $Code) { throw 'Null exit code rejected' }
    if (-not ($Code -is [int])) { throw "Nonnumeric exit code rejected: $($Code.GetType().FullName)" }
}

function Get-TemporaryTestRoot([string]$Kind) {
    $base = Join-Path ([System.IO.Path]::GetTempPath()) 'Skyguard52\ToolchainWave08\EnvironmentAuthoring01Recovery02'
    $leaf = '{0}_{1}' -f $Kind,[Guid]::NewGuid().ToString('N')
    $root = Join-Path $base $leaf
    [System.IO.Directory]::CreateDirectory($root) | Out-Null
    return $root
}

function Get-FutureGovernedPaths {
    return @(
        'D:\Skyguard52\Saved\BuildAttempts\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY02_DEPENDENCY_PROBE\attempt_01',
        'D:\Skyguard52\Saved\Reports\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY02_DEPENDENCY_PROBE_TERMINAL_MANIFEST.json',
        'D:\Skyguard52\Saved\Reports\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY02_DEPENDENCY_PROBE_EMERGENCY_RECEIPT.jsonl',
        'D:\Skyguard52\Saved\BuildAttempts\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY02\attempt_01',
        'D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentAuthoring01_Recovery02.umap'
    )
}

function Invoke-OfflineContractTest {
    $testRoot = Get-TemporaryTestRoot 'offline_contract_test'
    $successTerminal = Join-Path $testRoot 'success_terminal.json'
    $failureTerminal = Join-Path $testRoot 'induced_failure_terminal.json'
    $emergency = Join-Path $testRoot 'emergency_receipt.jsonl'
    $summary = Join-Path $testRoot 'offline_test_summary.json'
    $failures = @()
    $governedBefore = @(Get-FutureGovernedPaths | Where-Object { Test-Path -LiteralPath $_ })
    if ($governedBefore.Count -ne 0) { $failures += "Governed namespace existed before offline test: $($governedBefore -join ', ')" }
    try { Assert-NumericExitCode ([int]0) } catch { $failures += $_.Exception.Message }
    try { Assert-NumericExitCode $null; $failures += 'Null exit code was accepted' } catch {}
    try { Assert-NumericExitCode '0'; $failures += 'Nonnumeric exit code was accepted' } catch {}
    try {
        Write-JsonAtomic $successTerminal ([ordered]@{schema='skyguard.recovery02.offline-success.v1';classification='PASS';exit_code=[int]0;exit_code_type=([int]0).GetType().FullName;unreal_launch_count=0;retry_count=0})
        $loaded = Get-Content -Raw -LiteralPath $successTerminal | ConvertFrom-Json
        if ($loaded.classification -ne 'PASS' -or $loaded.exit_code -ne 0) { throw 'Success terminal validation failed' }
    } catch { $failures += $_.Exception.Message }
    try {
        throw 'DELIBERATE_TEMPORARY_PREFLIGHT_FAILURE'
    } catch {
        Write-JsonAtomic $failureTerminal ([ordered]@{schema='skyguard.recovery02.offline-induced-failure.v1';classification='EXPECTED_FAILURE';failure=$_.Exception.Message;unreal_launch_count=0;retry_count=0})
    }
    try {
        $blockingParent = Join-Path $testRoot 'blocking_parent_file'
        Set-Content -LiteralPath $blockingParent -Value 'file blocks directory creation' -Encoding UTF8
        $impossibleTerminal = Join-Path $blockingParent 'terminal.json'
        Write-JsonAtomic $impossibleTerminal ([ordered]@{classification='SHOULD_NOT_WRITE'})
        $failures += 'Manifest-write failure was not induced'
    } catch {
        Add-Content -LiteralPath $emergency -Value (([ordered]@{schema='skyguard.recovery02.offline-emergency.v1';classification='EXPECTED_EMERGENCY';failure=$_.Exception.Message;unreal_launch_count=0}) | ConvertTo-Json -Compress)
    }
    foreach($path in @($successTerminal,$failureTerminal,$emergency)) { if (-not(Test-Path -LiteralPath $path -PathType Leaf)) { $failures += "Missing temporary test evidence: $path" } }
    if ($script:UnrealLaunchFunctionEntered) { $failures += 'Unreal launch function was entered in offline mode' }
    $governedAfter = @(Get-FutureGovernedPaths | Where-Object { Test-Path -LiteralPath $_ })
    if ($governedAfter.Count -ne 0) { $failures += "Offline test created governed namespace: $($governedAfter -join ', ')" }
    $result = [ordered]@{schema='skyguard.toolchain-wave08.m01-authoring01-recovery02.offline-test.v1';classification=if($failures.Count-eq0){'PASS'}else{'FAIL'};test_root=$testRoot;success_terminal=$successTerminal;failure_terminal=$failureTerminal;emergency_receipt=$emergency;unreal_launch_count=0;retry_count=0;governed_before=$governedBefore;governed_after=$governedAfter;failures=$failures}
    Write-JsonAtomic $summary $result
    Write-Output "OFFLINE_TEST_ROOT=$testRoot"
    Write-Output "OFFLINE_TEST_SUMMARY=$summary"
    if ($failures.Count -ne 0) { return [int]1 }
    Write-Output 'PASS_OFFLINE_CONTRACT_TEST'
    return [int]0
}

function Invoke-AuthorizationRefusal {
    $testRoot = Get-TemporaryTestRoot 'authorization_refusal'
    $receipt = Join-Path $testRoot 'authorization_refusal.json'
    Write-JsonAtomic $receipt ([ordered]@{schema='skyguard.recovery02.authorization-refusal.v1';classification='AUTHORIZATION_REQUIRED';unreal_launch_count=0;retry_count=0})
    Write-Output "AUTHORIZATION_REFUSAL_RECEIPT=$receipt"
    Write-Output 'AUTHORIZATION_REQUIRED'
    return [int]2
}

function Invoke-CapturedProcess([string]$FilePath, [string[]]$Arguments, [int]$TimeoutMilliseconds, [string]$Attempt) {
    $script:UnrealLaunchFunctionEntered = $true
    $startInfo = [System.Diagnostics.ProcessStartInfo]::new()
    $startInfo.FileName = $FilePath
    $startInfo.Arguments = $Arguments -join ' '
    $startInfo.WorkingDirectory = $IsolatedRoot
    $startInfo.UseShellExecute = $false
    $startInfo.CreateNoWindow = $true
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    $startInfo.EnvironmentVariables['SKYGUARD_DEPENDENCY_PROBE_ATTEMPT'] = $Attempt
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
        $samples += [ordered]@{sampled_at_utc=[DateTime]::UtcNow.ToString('o');processes=@(Get-Process -ErrorAction SilentlyContinue | Where-Object {$_.ProcessName -match '^Unreal|ShaderCompileWorker'} | Select-Object Id,ProcessName,StartTime)}
        if ($watch.ElapsedMilliseconds -ge $TimeoutMilliseconds) { $timedOut=$true; try {$process.Kill()} catch {}; break }
    }
    $process.WaitForExit(); $process.Refresh()
    $stdout=$stdoutTask.GetAwaiter().GetResult(); $stderr=$stderrTask.GetAwaiter().GetResult(); $exitCode=$process.ExitCode
    Assert-NumericExitCode $exitCode
    $record=[pscustomobject]@{FilePath=$FilePath;Arguments=$Arguments;ProcessId=$process.Id;NativeHandleRetained=($nativeHandle-ne[IntPtr]::Zero);StartedAtUtc=$startedAt.ToString('o');CompletedAtUtc=[DateTime]::UtcNow.ToString('o');ExitCode=$exitCode;ExitCodeType=$exitCode.GetType().FullName;TimedOut=$timedOut;Stdout=$stdout;Stderr=$stderr;Samples=$samples}
    $process.Dispose(); return $record
}

# Mode dispatch occurs before the governed lifecycle is initialized.
if ($OfflineContractTest -and $AuthorizeSingleDependencyProbe) {
    Write-Error 'Offline and authorized modes are mutually exclusive'
    [Environment]::Exit([int]3)
}
if ($OfflineContractTest) {
    $testCode = Invoke-OfflineContractTest
    [Environment]::Exit([int]$testCode)
}
if (-not $AuthorizeSingleDependencyProbe) {
    $refusalCode = Invoke-AuthorizationRefusal
    [Environment]::Exit([int]$refusalCode)
}

# Governed paths and the outer terminal lifecycle exist only in authorized mode.
$Attempt = 'D:\Skyguard52\Saved\BuildAttempts\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY02_DEPENDENCY_PROBE\attempt_01'
$Terminal = 'D:\Skyguard52\Saved\Reports\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY02_DEPENDENCY_PROBE_TERMINAL_MANIFEST.json'
$Emergency = 'D:\Skyguard52\Saved\Reports\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY02_DEPENDENCY_PROBE_EMERGENCY_RECEIPT.jsonl'
$FutureAuthoringAttempt = 'D:\Skyguard52\Saved\BuildAttempts\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY02\attempt_01'
$started = [DateTime]::UtcNow
$preflightPassed = $false
$run = $null
$failure = $null
$classification = 'FAILED_WITH_EVIDENCE'

try {
    Assert-File 'D:\Skyguard52\Saved\Reports\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY01_DEPENDENCY_PROBE_TERMINAL_MANIFEST.json' 839 'e20e164803164cbc8ad1c9f4238510cb8a34237b454c9c9b3e28b25acfcf7292'
    Assert-File 'D:\Skyguard52\Scripts\ToolchainWave08\environment_authoring01_recovery01\invoke_dependency_probe_once.ps1' 9770 '82a614aa0fad9fdd2bed2cbc70d946025df8859f75f995009f0e4de4d587d443'
    Assert-File 'D:\Skyguard52\Scripts\ToolchainWave08\environment_authoring01_recovery01\probe_environment_dependencies.py' 11660 '0285876dae4a91f148988dfdc0d90d7ce4876f7343eba5afcd0355b608c83d9a'
    Assert-File 'D:\Skyguard52\Docs\AAA_Review\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_OFFLINE_DESIGN_FREEZE.json' 4802 'aa0b68a46b87da4d6ab4049d2cacf2dbd6ef32b28890297657dbb1c6d99a33c5'
    Assert-File 'D:\Skyguard52\Saved\Reports\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_TERMINAL_SUPERVISOR_MANIFEST.json' 2799 'f68c62dcb0b342c04fc7b2d9b1ee25bf9ba6bcac43173d8acdf1ee52f2c58943'
    if ((Get-Sha256 $InputMap) -ne $ExpectedInputHash) { throw 'Input map authority mismatch' }
    foreach($path in @($Attempt,$Terminal,$Emergency,$FutureAuthoringAttempt,$OriginalOutput,$RecoveryOutput)) { if(Test-Path -LiteralPath $path){throw "Future namespace already exists: $path"} }
    $heavy=@(Get-Process -ErrorAction SilentlyContinue | Where-Object {$_.ProcessName -match '^(UnrealEditor|UnrealEditor-Cmd|Blender|ShaderCompileWorker|AutomationTool|UnrealBuildTool|cl|link)$'})
    if($heavy.Count-ne0){throw 'Heavy process detected'}
    [System.IO.Directory]::CreateDirectory($Attempt)|Out-Null
    Copy-Item -LiteralPath $ProbeSource -Destination (Join-Path $Attempt 'probe_environment_dependencies.py')
    $preflightPassed=$true
    $arguments=@('"'+$Project+'"','-run=pythonscript','-script="'+(Join-Path $Attempt 'probe_environment_dependencies.py')+'"','-NullRHI','-unattended','-NoSplash','-NoSound','-NoSaveOnExit','-stdout','-FullStdOutLogOutput','-UTF8Output')
    $run=Invoke-CapturedProcess $Editor $arguments 600000 $Attempt
    $run.Stdout|Set-Content -LiteralPath (Join-Path $Attempt 'unreal_stdout.log') -Encoding UTF8
    $run.Stderr|Set-Content -LiteralPath (Join-Path $Attempt 'unreal_stderr.log') -Encoding UTF8
    $run.Samples|ConvertTo-Json -Depth 12|Set-Content -LiteralPath (Join-Path $Attempt 'process_tree_samples.json') -Encoding UTF8
    if($run.TimedOut){throw 'Unreal dependency probe timed out'}
    if($run.ExitCode-ne0){throw "Unreal dependency probe returned exit code $($run.ExitCode)"}
    $receipt=Join-Path $Attempt 'dependency_probe_receipt.json'
    if(-not(Test-Path -LiteralPath $receipt)){throw 'Dependency probe receipt missing'}
    $value=Get-Content -Raw -LiteralPath $receipt|ConvertFrom-Json
    if($value.classification-ne'PASSED_DEPENDENCY_PROBE_READY_FOR_RECOVERY01_FREEZE'){throw 'Dependency probe classification failed'}
    if((Get-Sha256 $InputMap)-ne$ExpectedInputHash){throw 'Input map changed during probe'}
    if(Test-Path -LiteralPath $OriginalOutput){throw 'Original output appeared during read-only probe'}
    if(Test-Path -LiteralPath $RecoveryOutput){throw 'Recovery02 output appeared during read-only probe'}
    $classification='PASSED_DEPENDENCY_PROBE_READY_FOR_RECOVERY02_FREEZE'
} catch {
    $failure=$_.Exception.Message
    $classification='FAILED_WITH_EVIDENCE'
} finally {
    try {
        $artifacts=@()
        if(Test-Path -LiteralPath $Attempt){foreach($file in Get-ChildItem -LiteralPath $Attempt -Recurse -File){$artifacts += [ordered]@{path=$file.FullName;bytes=$file.Length;sha256=Get-Sha256 $file.FullName}}}
        $terminalValue=[ordered]@{schema='skyguard.toolchain-wave08.m01-authoring01-recovery02.dependency-probe-terminal.v1';classification=$classification;started_at_utc=$started.ToString('o');completed_at_utc=[DateTime]::UtcNow.ToString('o');preflight_passed=$preflightPassed;unreal_launch_count=if($null-eq$run){0}else{1};retry_count=0;exit_code=if($null-eq$run){$null}else{$run.ExitCode};exit_code_type=if($null-eq$run){$null}else{$run.ExitCodeType};timed_out=if($null-eq$run){$false}else{$run.TimedOut};failure=$failure;input_hash_after=if(Test-Path -LiteralPath $InputMap){Get-Sha256 $InputMap}else{$null};original_output_exists=(Test-Path -LiteralPath $OriginalOutput);recovery_output_exists=(Test-Path -LiteralPath $RecoveryOutput);artifacts=$artifacts}
        Write-JsonAtomic $Terminal $terminalValue
    } catch {
        try { Add-Content -LiteralPath $Emergency -Value (([ordered]@{created_at_utc=[DateTime]::UtcNow.ToString('o');classification='FAILED_WITH_EVIDENCE';failure=$_.Exception.Message})|ConvertTo-Json -Compress) } catch {}
    }
}

Write-Output "CLASSIFICATION=$classification"
if($classification-ne'PASSED_DEPENDENCY_PROBE_READY_FOR_RECOVERY02_FREEZE'){[Environment]::Exit([int]1)}
[Environment]::Exit([int]0)
