[CmdletBinding()]
param(
    [switch]$AuthorizeSingleUnrealAuthoring,
    [switch]$OfflineContractTest
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ProjectRoot = 'D:\SG52T08_ENV01'
$Project = Join-Path $ProjectRoot 'Skyguard52.uproject'
$Editor = 'D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$Contract = 'D:\Skyguard52\Scripts\ToolchainWave08\m01_visible_environment_stage03\stage03_authoring_contract.json'
$Worker = 'D:\Skyguard52\Scripts\ToolchainWave08\m01_visible_environment_stage03\author_m01_visible_environment_stage03.py'
$AttemptRoot = 'D:\Skyguard52\Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_STAGE03_AUTHORING01\attempt_01'
$AttemptWorker = Join-Path $AttemptRoot 'author_m01_visible_environment_stage03.py'
$Receipt = Join-Path $AttemptRoot 'authoring_receipt.json'
$Stdout = Join-Path $AttemptRoot 'unreal.stdout.log'
$Stderr = Join-Path $AttemptRoot 'unreal.stderr.log'
$Samples = Join-Path $AttemptRoot 'process_tree_samples.json'
$Preflight = Join-Path $AttemptRoot 'preflight.json'
$ExternalTerminal = 'D:\Skyguard52\Saved\Reports\M01_VISIBLE_ENVIRONMENT_STAGE03_AUTHORING01_TERMINAL_MANIFEST.json'
$EmergencyReceipt = 'D:\Skyguard52\Saved\Reports\M01_VISIBLE_ENVIRONMENT_STAGE03_AUTHORING01_EMERGENCY_RECEIPT.jsonl'

function Get-LowerSha256([string]$Path) {
    $stream = $null; $algorithm = $null
    try {
        $stream = [IO.File]::Open($Path, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::Read)
        $algorithm = [Security.Cryptography.SHA256]::Create()
        return ([BitConverter]::ToString($algorithm.ComputeHash($stream))).Replace('-', '').ToLowerInvariant()
    }
    finally {
        if ($null -ne $algorithm) { $algorithm.Dispose() }
        if ($null -ne $stream) { $stream.Dispose() }
    }
}

function Write-JsonAtomic([string]$Path, $Value) {
    $directory = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $directory)) { New-Item -ItemType Directory -Path $directory -Force | Out-Null }
    $temporary = "$Path.tmp"
    [IO.File]::WriteAllText($temporary, (($Value | ConvertTo-Json -Depth 40) + [Environment]::NewLine), [Text.UTF8Encoding]::new($false))
    Move-Item -LiteralPath $temporary -Destination $Path -Force
}

function Assert-FileRecord($Entry, [string]$Label) {
    $path = [string]$Entry.path
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "$Label missing: $path" }
    $item = Get-Item -LiteralPath $path
    if ($item.Length -ne [long]$Entry.bytes) { throw "$Label byte mismatch: $path" }
    if ((Get-LowerSha256 $path) -ne [string]$Entry.sha256) { throw "$Label hash mismatch: $path" }
}

function Get-HeavyProcesses {
    return @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {
        $_.Name -match '^(UnrealEditor(-Cmd)?|Blender|ShaderCompileWorker|AutomationTool|UnrealBuildTool|cl|link)(\.exe)?$'
    })
}

function Assert-Fresh($Value) {
    foreach ($key in @('path','attempt','terminal_manifest','emergency_receipt')) {
        $path = [string]$Value.output.$key
        if (Test-Path -LiteralPath $path) { throw "Fresh namespace already exists: $path" }
    }
}

function Invoke-CapturedProcess([string]$FilePath, [string[]]$Arguments, [int]$TimeoutMilliseconds) {
    $startInfo = [Diagnostics.ProcessStartInfo]::new()
    $startInfo.FileName = $FilePath
    $startInfo.Arguments = $Arguments -join ' '
    $startInfo.WorkingDirectory = $ProjectRoot
    $startInfo.UseShellExecute = $false
    $startInfo.CreateNoWindow = $true
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    $process = [Diagnostics.Process]::new(); $process.StartInfo = $startInfo
    $started = [DateTime]::UtcNow
    if (-not $process.Start()) { throw "Process failed to start: $FilePath" }
    $handle = $process.Handle
    $stdoutTask = $process.StandardOutput.ReadToEndAsync(); $stderrTask = $process.StandardError.ReadToEndAsync()
    $rows = @(); $watch = [Diagnostics.Stopwatch]::StartNew(); $timedOut = $false
    while (-not $process.WaitForExit(1000)) {
        $rows += [ordered]@{ sampled_at_utc=[DateTime]::UtcNow.ToString('o'); processes=@(Get-Process -ErrorAction SilentlyContinue | Where-Object {$_.ProcessName -match '^Unreal|ShaderCompileWorker'} | Select-Object Id,ProcessName,StartTime) }
        if ($watch.ElapsedMilliseconds -ge $TimeoutMilliseconds) { $timedOut=$true; try{$process.Kill()}catch{}; break }
    }
    $process.WaitForExit(); $process.Refresh()
    $code = $process.ExitCode
    if ($null -eq $code -or $code.GetType().FullName -ne 'System.Int32') { throw 'Invalid process exit code' }
    $result=[pscustomobject]@{
        FilePath=$FilePath;Arguments=$Arguments;ProcessId=$process.Id;NativeHandleRetained=($handle-ne[IntPtr]::Zero)
        StartedAtUtc=$started.ToString('o');CompletedAtUtc=[DateTime]::UtcNow.ToString('o');ExitCode=$code;ExitCodeType=$code.GetType().FullName
        TimedOut=$timedOut;Stdout=$stdoutTask.GetAwaiter().GetResult();Stderr=$stderrTask.GetAwaiter().GetResult();Samples=$rows
    }
    $process.Dispose(); return $result
}

$value = Get-Content -LiteralPath $Contract -Raw | ConvertFrom-Json
if ($OfflineContractTest) {
    Assert-FileRecord $value.project 'Project'; Assert-FileRecord $value.editor 'Editor'
    Assert-FileRecord $value.input_map 'Input map'
    foreach($entry in @($value.authorities)){Assert-FileRecord $entry 'Authority'}
    foreach($entry in @($value.reused_assets)){Assert-FileRecord $entry 'Reused asset'}
    Assert-Fresh $value
    if(@(Get-HeavyProcesses).Count -gt 0){throw 'Heavy process active during offline test'}
    & python $Worker --offline-contract-test
    if($LASTEXITCODE-ne 0){throw "Worker offline test returned $LASTEXITCODE"}
    Write-Output 'CLASSIFICATION=PASS_M01_VISIBLE_ENVIRONMENT_STAGE03_OFFLINE_CONTRACT'
    exit 0
}

$started=[DateTime]::UtcNow;$run=$null;$failure=$null;$classification='FAILED_WITH_EVIDENCE';$preflightPassed=$false
try {
    if(-not $AuthorizeSingleUnrealAuthoring){throw 'Standing-authorized -AuthorizeSingleUnrealAuthoring guard is required'}
    Assert-FileRecord $value.project 'Project'; Assert-FileRecord $value.editor 'Editor'; Assert-FileRecord $value.input_map 'Input map'
    foreach($entry in @($value.authorities)){Assert-FileRecord $entry 'Authority'}
    foreach($entry in @($value.reused_assets)){Assert-FileRecord $entry 'Reused asset'}
    Assert-Fresh $value
    $heavy=@(Get-HeavyProcesses);if($heavy.Count-gt 0){throw "Heavy process active: $($heavy.Name -join ', ')"}
    $preflightPassed=$true
    New-Item -ItemType Directory -Path $AttemptRoot | Out-Null
    Copy-Item -LiteralPath $Worker -Destination $AttemptWorker
    Write-JsonAtomic $Preflight ([ordered]@{schema='skyguard.m01-visible-environment-stage03.preflight.v1';classification='PASS';checked_at_utc=[DateTime]::UtcNow.ToString('o');heavy_process_count=0;fresh_namespaces_absent=$true;input_map_sha256=Get-LowerSha256([string]$value.input_map.path)})
    $arguments=@($Project,'-Unattended','-NoSplash','-NoSound','-NullRHI','-NoSaveOnExit','-stdout','-FullStdOutLogOutput','-DisablePlugins=Fab,Bridge,EditorTelemetry,RuntimeTelemetry,EOSShared','-run=pythonscript',"-script=$AttemptWorker")
    $run=Invoke-CapturedProcess -FilePath $Editor -Arguments $arguments -TimeoutMilliseconds 1800000
    [IO.File]::WriteAllText($Stdout,$run.Stdout,[Text.UTF8Encoding]::new($false));[IO.File]::WriteAllText($Stderr,$run.Stderr,[Text.UTF8Encoding]::new($false));Write-JsonAtomic $Samples $run.Samples
    if($run.TimedOut){throw 'Stage03 authoring timed out'};if($run.ExitCode-ne 0){throw "Stage03 authoring returned $($run.ExitCode)"}
    if(-not(Test-Path -LiteralPath $Receipt)){throw 'Stage03 authoring receipt missing'}
    $receiptValue=Get-Content -LiteralPath $Receipt -Raw|ConvertFrom-Json
    if($receiptValue.classification-ne 'PASSED_STAGE03_AUTHORING_AWAITING_D3D12_VISUAL_PROOF'){throw "Stage03 authoring failed: $($receiptValue.error)"}
    if(-not(Test-Path -LiteralPath ([string]$value.output.path))){throw 'Stage03 output map missing'}
    if((Get-LowerSha256([string]$value.input_map.path))-ne[string]$value.input_map.sha256){throw 'Accepted Stage02 map changed'}
    $classification='PASSED_STAGE03_AUTHORING_AWAITING_D3D12_VISUAL_PROOF'
} catch {$failure=$_.Exception.Message}
finally {
    $artifacts=@();if(Test-Path -LiteralPath $AttemptRoot){foreach($file in Get-ChildItem -LiteralPath $AttemptRoot -Recurse -File){$artifacts+=[ordered]@{path=$file.FullName;bytes=$file.Length;sha256=Get-LowerSha256 $file.FullName}}}
    $launchCount=if($null-eq$run){0}else{1}
    $exitCode=if($null-eq$run){$null}else{$run.ExitCode}
    $exitType=if($null-eq$run){$null}else{$run.ExitCodeType}
    $wasTimedOut=if($null-eq$run){$false}else{$run.TimedOut}
    $mapAfter=if(Test-Path -LiteralPath ([string]$value.input_map.path)){Get-LowerSha256([string]$value.input_map.path)}else{$null}
    $outputRecord=$null
    if(Test-Path -LiteralPath ([string]$value.output.path)){
        $outputRecord=[ordered]@{path=[string]$value.output.path;bytes=(Get-Item ([string]$value.output.path)).Length;sha256=Get-LowerSha256([string]$value.output.path)}
    }
    $terminal=[ordered]@{schema='skyguard.m01-visible-environment-stage03.terminal-supervisor.v1';classification=$classification;started_at_utc=$started.ToString('o');completed_at_utc=[DateTime]::UtcNow.ToString('o');preflight_passed=$preflightPassed;unreal_launch_count=$launchCount;retry_count=0;exit_code=$exitCode;exit_code_type=$exitType;timed_out=$wasTimedOut;failure=$failure;input_map_sha256_after=$mapAfter;output_map=$outputRecord;artifacts=$artifacts}
    try{Write-JsonAtomic $ExternalTerminal $terminal}catch{[IO.File]::AppendAllText($EmergencyReceipt,(([ordered]@{created_at_utc=[DateTime]::UtcNow.ToString('o');classification='FAILED_WITH_EVIDENCE';failure_stage='terminal_manifest_write';message=$_.Exception.Message}|ConvertTo-Json -Compress)+[Environment]::NewLine),[Text.UTF8Encoding]::new($false))}
    Write-Output "CLASSIFICATION=$classification"
    if($classification-ne'PASSED_STAGE03_AUTHORING_AWAITING_D3D12_VISUAL_PROOF'){exit 1}
}
