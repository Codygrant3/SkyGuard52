param([switch]$AuthorizeSingleReadOnlyProbe)

$ErrorActionPreference = 'Stop'
$Project = 'D:\SG52T08_ENV01\Skyguard52.uproject'
$Editor = 'D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$Source = 'D:\Skyguard52\Scripts\ToolchainWave08\m01_polyhaven_vegetation_staging01_recovery01_reflection_probe\probe_ue58_interchange_reflection.py'
$Attempt = 'D:\Skyguard52\Saved\BuildAttempts\M01_POLYHAVEN_VEGETATION_STAGING01_RECOVERY01_REFLECTION_PROBE\attempt_01'
$AttemptSource = Join-Path $Attempt 'probe_ue58_interchange_reflection.py'
$Receipt = Join-Path $Attempt 'reflection_receipt.json'
$Stdout = Join-Path $Attempt 'unreal.stdout.log'
$Stderr = Join-Path $Attempt 'unreal.stderr.log'
$Terminal = 'D:\Skyguard52\Saved\Reports\M01_POLYHAVEN_VEGETATION_STAGING01_RECOVERY01_REFLECTION_PROBE_TERMINAL.json'
$FailureFreeze = 'D:\Skyguard52\Docs\AAA_Review\M01_POLYHAVEN_VEGETATION_STAGING01_ATTEMPT01_TERMINAL_FREEZE.json'

function Get-Sha256([string]$Path) {
    $stream=[System.IO.File]::OpenRead($Path);$sha=[System.Security.Cryptography.SHA256]::Create()
    try{return ([BitConverter]::ToString($sha.ComputeHash($stream))).Replace('-','').ToLowerInvariant()}finally{$sha.Dispose();$stream.Dispose()}
}
function Write-JsonAtomic([string]$Path,$Value){$d=Split-Path -Parent $Path;if(-not(Test-Path $d)){New-Item -ItemType Directory -Path $d|Out-Null};$t="$Path.tmp";[IO.File]::WriteAllText($t,(($Value|ConvertTo-Json -Depth 30)+[Environment]::NewLine),[Text.UTF8Encoding]::new($false));Move-Item $t $Path -Force}
function Get-HeavyProcesses{return @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue|Where-Object{$_.Name -match '^(UnrealEditor(-Cmd)?|Blender|ShaderCompileWorker|AutomationTool|UnrealBuildTool|cl|link)(\.exe)?$'})}

$started=[DateTime]::UtcNow;$process=$null;$exitCode=$null;$timedOut=$false;$failure=$null;$classification='FAILED_WITH_EVIDENCE';$stdout='';$stderr=''
try{
    if(-not $AuthorizeSingleReadOnlyProbe){throw 'Mechanical one-shot probe guard is required'}
    if((Get-Item $FailureFreeze).Length -ne 3162 -or (Get-Sha256 $FailureFreeze) -ne '6ece421d626c1b7ff11dabb918e45155269e9c090e994dd49dde47abbcb0d549'){throw 'Attempt01 failure freeze changed'}
    if((Get-Sha256 $Project) -ne '7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a'){throw 'Isolated project changed'}
    if((Get-Sha256 $Editor) -ne '0fb325cf215cc800ce260a1890af3f3dc314b8cc6331061d4e7e7246489af2e0'){throw 'Editor changed'}
    if((Get-HeavyProcesses).Count -gt 0){throw 'Heavy process detected'}
    foreach($p in @($Attempt,$Terminal)){if(Test-Path $p){throw "Fresh namespace exists: $p"}}
    New-Item -ItemType Directory -Path $Attempt|Out-Null;Copy-Item $Source $AttemptSource
    $si=[Diagnostics.ProcessStartInfo]::new();$si.FileName=$Editor;$si.Arguments=@($Project,'-Unattended','-NoSplash','-NoSound','-NullRHI','-NoSaveOnExit','-stdout','-FullStdOutLogOutput','-DisablePlugins=Fab,Bridge,EditorTelemetry,RuntimeTelemetry,EOSShared','-run=pythonscript',"-script=$AttemptSource") -join ' ';$si.WorkingDirectory='D:\SG52T08_ENV01';$si.UseShellExecute=$false;$si.CreateNoWindow=$true;$si.RedirectStandardOutput=$true;$si.RedirectStandardError=$true
    $process=[Diagnostics.Process]::new();$process.StartInfo=$si;if(-not $process.Start()){throw 'Unreal probe failed to start'};$outTask=$process.StandardOutput.ReadToEndAsync();$errTask=$process.StandardError.ReadToEndAsync();$watch=[Diagnostics.Stopwatch]::StartNew()
    while(-not $process.WaitForExit(1000)){if($watch.Elapsed.TotalSeconds -ge 300){$timedOut=$true;try{$process.Kill()}catch{};break}}
    $process.WaitForExit();$process.Refresh();$exitCode=$process.ExitCode;$stdout=$outTask.GetAwaiter().GetResult();$stderr=$errTask.GetAwaiter().GetResult();[IO.File]::WriteAllText($Stdout,$stdout,[Text.UTF8Encoding]::new($false));[IO.File]::WriteAllText($Stderr,$stderr,[Text.UTF8Encoding]::new($false))
    if($exitCode.GetType().FullName -ne 'System.Int32'){throw 'Exit code type is not System.Int32'};if($timedOut){throw 'Probe timed out'};if($exitCode -ne 0){throw "Probe exit code $exitCode"};if(-not(Test-Path $Receipt)){throw 'Reflection receipt missing'};$r=Get-Content $Receipt -Raw|ConvertFrom-Json;if($r.classification -ne 'PASSED_UE58_INTERCHANGE_REFLECTION_READY_FOR_RECOVERY01_STAGING_DESIGN'){throw "Reflection probe failed: $($r.error)"};$classification=$r.classification
}catch{$failure=$_.Exception.Message}
finally{
    $value=[ordered]@{schema='skyguard.m01-polyhaven-vegetation-staging01-recovery01-reflection-probe-terminal.v1';classification=$classification;started_at_utc=$started.ToString('o');completed_at_utc=[DateTime]::UtcNow.ToString('o');unreal_launch_count=if($null-eq$process){0}else{1};retry_count=0;exit_code=$exitCode;exit_code_type=if($null-eq$exitCode){$null}else{$exitCode.GetType().FullName};timed_out=$timedOut;failure=$failure;receipt=if(Test-Path $Receipt){[ordered]@{path=$Receipt;bytes=(Get-Item $Receipt).Length;sha256=Get-Sha256 $Receipt}}else{$null};content_mutated=$false};Write-JsonAtomic $Terminal $value;Write-Output "CLASSIFICATION=$classification";if($classification -ne 'PASSED_UE58_INTERCHANGE_REFLECTION_READY_FOR_RECOVERY01_STAGING_DESIGN'){exit 1}
}
