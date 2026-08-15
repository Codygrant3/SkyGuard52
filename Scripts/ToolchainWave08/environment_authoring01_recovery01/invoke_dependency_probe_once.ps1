param(
    [switch]$AuthorizeSingleDependencyProbe,
    [switch]$OfflineContractTest
)

$ErrorActionPreference = 'Stop'
$ProjectRoot = 'D:\Skyguard52'
$IsolatedRoot = 'D:\SG52T08_ENV01'
$Editor = 'D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$Project = Join-Path $IsolatedRoot 'Skyguard52.uproject'
$ScriptRoot = Join-Path $ProjectRoot 'Scripts\ToolchainWave08\environment_authoring01_recovery01'
$ProbeSource = Join-Path $ScriptRoot 'probe_environment_dependencies.py'
$Attempt = Join-Path $ProjectRoot 'Saved\BuildAttempts\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY01_DEPENDENCY_PROBE\attempt_01'
$Terminal = Join-Path $ProjectRoot 'Saved\Reports\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY01_DEPENDENCY_PROBE_TERMINAL_MANIFEST.json'
$Emergency = Join-Path $ProjectRoot 'Saved\Reports\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY01_DEPENDENCY_PROBE_EMERGENCY_RECEIPT.jsonl'
$InputMap = Join-Path $IsolatedRoot 'Content\ToolchainWave08\Environment\Lvl_M01_T08_WaterLandmassPCG_Prototype01.umap'
$OriginalOutput = Join-Path $IsolatedRoot 'Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentAuthoring01.umap'
$RecoveryOutput = Join-Path $IsolatedRoot 'Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentAuthoring01_Recovery01.umap'
$ExpectedInputHash = '5c8b7c6b0c6024767fa8a671523b5626213bd029d591270654080aed5fc7ced4'
$started = [DateTime]::UtcNow
$preflightPassed = $false
$run = $null
$failure = $null
$classification = 'FAILED_WITH_EVIDENCE'

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
    $Value | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $temporary -Encoding UTF8
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

function Invoke-CapturedProcess([string]$FilePath, [string[]]$Arguments, [int]$TimeoutMilliseconds) {
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

try {
    if ($OfflineContractTest) {
        Assert-NumericExitCode ([int]0)
        try { Assert-NumericExitCode $null; throw 'Null-code rejection failed' } catch { if ($_.Exception.Message -eq 'Null-code rejection failed') { throw } }
        if ((Get-Sha256 $ProbeSource).Length -ne 64) { throw 'SHA-256 contract failed' }
        Write-Output 'PASS_OFFLINE_CONTRACT_TEST'
        exit 0
    }
    if (-not $AuthorizeSingleDependencyProbe) { throw 'Explicit -AuthorizeSingleDependencyProbe is required' }
    Assert-File 'D:\Skyguard52\Saved\Reports\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_TERMINAL_SUPERVISOR_MANIFEST.json' 2799 'f68c62dcb0b342c04fc7b2d9b1ee25bf9ba6bcac43173d8acdf1ee52f2c58943'
    Assert-File 'D:\Skyguard52\Saved\BuildAttempts\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01\attempt_01\authoring_receipt.json' 2155 'ed8981bf61b49d3da6c3275816d92f1eec21e8af044bd85f4a819640bb6fdb84'
    Assert-File 'D:\Skyguard52\Docs\AAA_Review\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_OFFLINE_DESIGN_FREEZE.json' 4802 'aa0b68a46b87da4d6ab4049d2cacf2dbd6ef32b28890297657dbb1c6d99a33c5'
    if ((Get-Sha256 $InputMap) -ne $ExpectedInputHash) { throw 'Input map authority mismatch' }
    foreach($path in @($Attempt,$Terminal,$Emergency,$OriginalOutput,$RecoveryOutput)) { if (Test-Path -LiteralPath $path) { throw "Future namespace already exists: $path" } }
    $heavy=@(Get-Process -ErrorAction SilentlyContinue | Where-Object {$_.ProcessName -match '^(UnrealEditor|UnrealEditor-Cmd|Blender|ShaderCompileWorker|AutomationTool|UnrealBuildTool|cl|link)$'})
    if ($heavy.Count -ne 0) { throw 'Heavy process detected' }
    [System.IO.Directory]::CreateDirectory($Attempt) | Out-Null
    Copy-Item -LiteralPath $ProbeSource -Destination (Join-Path $Attempt 'probe_environment_dependencies.py')
    $preflightPassed=$true
    $arguments=@('"'+$Project+'"','-run=pythonscript','-script="'+(Join-Path $Attempt 'probe_environment_dependencies.py')+'"','-NullRHI','-unattended','-NoSplash','-NoSound','-NoSaveOnExit','-stdout','-FullStdOutLogOutput','-UTF8Output')
    $run=Invoke-CapturedProcess $Editor $arguments 600000
    $run.Stdout | Set-Content -LiteralPath (Join-Path $Attempt 'unreal_stdout.log') -Encoding UTF8
    $run.Stderr | Set-Content -LiteralPath (Join-Path $Attempt 'unreal_stderr.log') -Encoding UTF8
    $run.Samples | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath (Join-Path $Attempt 'process_tree_samples.json') -Encoding UTF8
    if ($run.TimedOut) { throw 'Unreal dependency probe timed out' }
    if ($run.ExitCode -ne 0) { throw "Unreal dependency probe returned exit code $($run.ExitCode)" }
    $receipt=Join-Path $Attempt 'dependency_probe_receipt.json'
    if (-not(Test-Path -LiteralPath $receipt)){throw 'Dependency probe receipt missing'}
    $value=Get-Content -Raw -LiteralPath $receipt|ConvertFrom-Json
    if ($value.classification -ne 'PASSED_DEPENDENCY_PROBE_READY_FOR_RECOVERY01_FREEZE'){throw 'Dependency probe classification failed'}
    if ((Get-Sha256 $InputMap) -ne $ExpectedInputHash){throw 'Input map changed during probe'}
    if (Test-Path -LiteralPath $OriginalOutput){throw 'Original output appeared during read-only probe'}
    if (Test-Path -LiteralPath $RecoveryOutput){throw 'Recovery output appeared during read-only probe'}
    $classification='PASSED_DEPENDENCY_PROBE_READY_FOR_RECOVERY01_FREEZE'
} catch {
    $failure=$_.Exception.Message
    $classification='FAILED_WITH_EVIDENCE'
} finally {
    try {
        $artifacts=@()
        if(Test-Path -LiteralPath $Attempt){foreach($f in Get-ChildItem -LiteralPath $Attempt -Recurse -File){$artifacts += [ordered]@{path=$f.FullName;bytes=$f.Length;sha256=Get-Sha256 $f.FullName}}}
        $terminalValue=[ordered]@{schema='skyguard.toolchain-wave08.m01-authoring01-recovery01.dependency-probe-terminal.v1';classification=$classification;started_at_utc=$started.ToString('o');completed_at_utc=[DateTime]::UtcNow.ToString('o');preflight_passed=$preflightPassed;unreal_launch_count=if($null-eq$run){0}else{1};retry_count=0;exit_code=if($null-eq$run){$null}else{$run.ExitCode};exit_code_type=if($null-eq$run){$null}else{$run.ExitCodeType};timed_out=if($null-eq$run){$false}else{$run.TimedOut};failure=$failure;input_hash_after=if(Test-Path -LiteralPath $InputMap){Get-Sha256 $InputMap}else{$null};original_output_exists=(Test-Path -LiteralPath $OriginalOutput);recovery_output_exists=(Test-Path -LiteralPath $RecoveryOutput);artifacts=$artifacts}
        Write-JsonAtomic $Terminal $terminalValue
    } catch {
        try { Add-Content -LiteralPath $Emergency -Value (([ordered]@{created_at_utc=[DateTime]::UtcNow.ToString('o');classification='FAILED_WITH_EVIDENCE';failure=$_.Exception.Message})|ConvertTo-Json -Compress) } catch {}
    }
}

Write-Output "CLASSIFICATION=$classification"
if($classification -ne 'PASSED_DEPENDENCY_PROBE_READY_FOR_RECOVERY01_FREEZE'){exit 1}
exit 0
