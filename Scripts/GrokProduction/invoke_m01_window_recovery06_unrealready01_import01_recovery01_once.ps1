param([switch]$AuthorizeSingleUnreal, [switch]$OfflineContractTest)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$Root = 'D:\Skyguard52'
$Project = 'D:\SG52T08_ENV01\Skyguard52.uproject'
$Editor = 'D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$Author = Join-Path $Root 'Scripts\GrokProduction\author_m01_window_recovery06_unrealready01_import01_recovery01.py'
$Verifier = Join-Path $Root 'Scripts\GrokProduction\verify_m01_window_recovery06_unrealready01_import01_recovery01_offline.py'
$Contract = Join-Path $Root 'Docs\GrokProduction\Wave02\M01_WINDOW_RECOVERY06_UNREALREADY01_REVERSIBLE_UNREAL_IMPORT01_RECOVERY01_CONTRACT.json'
$Source = Join-Path $Root 'Production\Attempts\m01-hero-prewar-window-bay-a01-recovery06-unrealready01-grok-mcp\attempt_20260811T013000000000Z\output\M01_Hero_Prewar_Window_Bay_A01_Recovery06_UnrealReady01.glb'
$AcceptanceFreeze = Join-Path $Root 'Docs\AAA_Review\M01_HERO_PREWAR_WINDOW_BAY_A01_RECOVERY06_UNREALREADY01_GROK_MCP_ATTEMPT01_ACCEPTANCE_FREEZE.json'
$FailedFreeze = Join-Path $Root 'Docs\AAA_Review\M01_WINDOW_RECOVERY06_UNREALREADY01_REVERSIBLE_UNREAL_IMPORT01_ATTEMPT01_TERMINAL_FREEZE.json'
$PipelineProbe = Join-Path $Root 'Saved\BuildAttempts\M01_WINDOW_INTERCHANGE_PIPELINE_PROBE01\attempt_01\probe_receipt.json'
$Authorization = Join-Path $Root 'Production\standing_heavy_process_authorization.json'
$Destination = 'D:\SG52T08_ENV01\Content\T08\GW01'
$Attempt = Join-Path $Root 'Saved\BuildAttempts\M01_WINDOW_RECOVERY06_UNREALREADY01_REVERSIBLE_UNREAL_IMPORT01_RECOVERY01\attempt_01'
$Receipt = Join-Path $Attempt 'import_receipt.json'
$Terminal = Join-Path $Root 'Saved\Reports\M01_WINDOW_RECOVERY06_UNREALREADY01_REVERSIBLE_UNREAL_IMPORT01_RECOVERY01_TERMINAL_SUPERVISOR.json'
$Emergency = Join-Path $Root 'Saved\Reports\M01_WINDOW_RECOVERY06_UNREALREADY01_REVERSIBLE_UNREAL_IMPORT01_RECOVERY01_EMERGENCY_RECEIPT.jsonl'
$TimeoutSeconds = 2700
$Expected = [ordered]@{
    $Author = '1bbc40d6c0063a60e26be1921698ec43aa18d522a520fb6e5e75532d602e6d79'
    $Verifier = 'ac392c1399f8789113f19425b7f61deb3da21dd696859c4db7744352cfb740e3'
    $Contract = 'c9fed6143fc393f1dfea69a8f6a3783ffbe1727595169ccaad01aada923a9aaf'
    $Source = 'e27b61da25d93fac047c7941b7087325e6500f30790b92b66ac002dc69421805'
    $AcceptanceFreeze = 'fc406a78a464cb1a418baf479047ac04ea9e5df850f3f986ccc41c1d537be154'
    $FailedFreeze = '0217140083c4440ac5e902e39f09f41bcb1414cbc00ae92593db5b88aa6d6719'
    $PipelineProbe = '3e8f99b1a6b962e445463ad2bdd316c81a36b343fdefc865c17d75af984f75aa'
    $Authorization = '48277d7edd869cc2b841c3993e8f7599bec5291ddf23e9c442b33e09b870c089'
    $Project = '7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a'
    $Editor = '0fb325cf215cc800ce260a1890af3f3dc314b8cc6331061d4e7e7246489af2e0'
}

function Get-Sha256([string]$Path){$stream=$null;$hasher=$null;try{$stream=[IO.File]::Open($Path,[IO.FileMode]::Open,[IO.FileAccess]::Read,[IO.FileShare]::Read);$hasher=[Security.Cryptography.SHA256]::Create();return([BitConverter]::ToString($hasher.ComputeHash($stream))).Replace('-','').ToLowerInvariant()}finally{if($null-ne$hasher){$hasher.Dispose()};if($null-ne$stream){$stream.Dispose()}}}
function Get-Record([string]$Path){$item=Get-Item -LiteralPath $Path -ErrorAction Stop;[ordered]@{path=$item.FullName;bytes=[int64]$item.Length;sha256=Get-Sha256 $item.FullName}}
function Write-JsonAtomic([string]$Path,[object]$Value){$parent=Split-Path -Parent $Path;[IO.Directory]::CreateDirectory($parent)|Out-Null;$temporary=$Path+'.tmp.'+[Diagnostics.Process]::GetCurrentProcess().Id;[IO.File]::WriteAllText($temporary,(($Value|ConvertTo-Json -Depth 40)+[Environment]::NewLine),[Text.UTF8Encoding]::new($false));if(Test-Path -LiteralPath $Path){throw "Refusing to overwrite terminal evidence: $Path"};[IO.File]::Move($temporary,$Path)}
function Get-HeavyProcesses{$exact=@('Blender','UnrealEditor','UnrealEditor-Cmd','ShaderCompileWorker','AutomationTool','UnrealBuildTool','cl','link','dotnet');@(Get-Process -ErrorAction SilentlyContinue|Where-Object{$exact-contains$_.ProcessName-or$_.ProcessName-like'UnrealEditor*'-or$_.ProcessName-like'ShaderCompileWorker*'}|Select-Object ProcessName,Id,StartTime,CPU,WorkingSet64)}

$State=[ordered]@{schema='skyguard.m01-window.reversible-unreal-import01-recovery01.supervisor.v1';classification='FAILED_WITH_EVIDENCE';started_utc=[DateTime]::UtcNow.ToString('o');ended_utc=$null;failure_stage=$null;failure_message=$null;supervisor_launch_count=1;unreal_launch_count=0;retry_count=0;timed_out=$false;actual_exit_code=$null;actual_exit_code_type=$null;unreal_pid=$null;process_handle_retained=$false;offline_contract_test=[bool]$OfflineContractTest;exact_executable=$Editor;exact_arguments=@();working_directory=$Root;authorities=@();heavy_processes_before=@();process_samples=@();receipt=$null;imported_asset_inventory=@();source_unchanged=$false;project_descriptor_unchanged=$false;map_mutations=0;runtime_promotion_performed=$false}
$Exit=1
try{
    $State.failure_stage='preflight'
    foreach($entry in $Expected.GetEnumerator()){if(-not(Test-Path -LiteralPath $entry.Key -PathType Leaf)){throw "Missing authority: $($entry.Key)"};$actual=Get-Sha256 $entry.Key;if($actual-ne$entry.Value){throw "Authority hash mismatch: $($entry.Key) expected=$($entry.Value) actual=$actual"};$State.authorities+=Get-Record $entry.Key}
    $standing=Get-Content -LiteralPath $Authorization -Raw|ConvertFrom-Json
    if($standing.status-ne'ACTIVE'-or$standing.execution_policy.per_run_user_authorization_required-ne$false){throw 'Standing heavy-process authorization is not active.'}
    if(Test-Path -LiteralPath $Attempt){throw "Fresh Recovery01 attempt exists: $Attempt"}
    if(Test-Path -LiteralPath $Terminal){throw "Fresh Recovery01 terminal exists: $Terminal"}
    if(Test-Path -LiteralPath $Destination){throw "Fresh Recovery01 destination exists: $Destination"}
    $verifyOutput=& python $Verifier 2>&1
    if($LASTEXITCODE-ne0-or($verifyOutput-join"`n")-notmatch'PASS_M01_WINDOW_REVERSIBLE'){throw "Recovery01 offline verifier failed: $($verifyOutput-join' ')"}
    $authorOutput=& python $Author --offline-contract-test 2>&1
    if($LASTEXITCODE-ne0-or($authorOutput-join"`n")-notmatch'PASS_M01_WINDOW_REVERSIBLE'){throw "Recovery01 author contract failed: $($authorOutput-join' ')"}
    if($OfflineContractTest){$State.classification='PASS_OFFLINE_CONTRACT';$State.failure_stage=$null;$Exit=0;return}
    if(-not$AuthorizeSingleUnreal){$State.classification='REFUSED_MISSING_MECHANICAL_GUARD';$State.failure_stage='authorization';$Exit=2;return}
    $State.heavy_processes_before=@(Get-HeavyProcesses)
    if($State.heavy_processes_before.Count-ne0){throw "Heavy process gate failed: $($State.heavy_processes_before.ProcessName -join ', ')"}

    [IO.Directory]::CreateDirectory($Attempt)|Out-Null
    $stdout=Join-Path $Attempt 'unreal.stdout.log';$stderr=Join-Path $Attempt 'unreal.stderr.log';$engineLog=Join-Path $Attempt 'unreal.engine.log';$samples=Join-Path $Attempt 'process_tree_samples.jsonl'
    $arguments=@($Project,'-run=pythonscript',('-script='+$Author),'-unattended','-nop4','-nosplash','-nullrhi','-NoSound','-stdout','-FullStdOutLogOutput',('-abslog='+$engineLog),'-DisablePlugins=Fab,Bridge,EditorTelemetry,RuntimeTelemetry,EOSShared','-ini:EditorSettings:[/Script/UnrealEd.AnalyticsPrivacySettings]:bSendUsageData=False')
    $State.exact_arguments=$arguments;$State.failure_stage='launch'
    $process=Start-Process -FilePath $Editor -ArgumentList $arguments -WorkingDirectory $Root -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru
    $State.unreal_launch_count=1;$State.unreal_pid=[int]$process.Id;$null=$process.Handle;$State.process_handle_retained=$true;$deadline=[DateTime]::UtcNow.AddSeconds($TimeoutSeconds);$State.failure_stage='wait'
    while(-not$process.HasExited){$process.Refresh();$sample=[ordered]@{utc=[DateTime]::UtcNow.ToString('o');pid=[int]$process.Id;working_set=[int64]$process.WorkingSet64;cpu_seconds=[double]$process.TotalProcessorTime.TotalSeconds};$State.process_samples+=$sample;[IO.File]::AppendAllText($samples,(($sample|ConvertTo-Json -Compress)+[Environment]::NewLine),[Text.UTF8Encoding]::new($false));if([DateTime]::UtcNow-ge$deadline){$State.timed_out=$true;try{$process.Kill()}catch{};throw "Unreal Recovery01 import exceeded $TimeoutSeconds seconds."};Start-Sleep -Seconds 2}
    $process.WaitForExit();$process.Refresh();$State.actual_exit_code=[int]$process.ExitCode;$State.actual_exit_code_type=$process.ExitCode.GetType().FullName
    if($process.ExitCode-ne0){throw "Unreal returned exit code $($process.ExitCode)."}
    $State.failure_stage='postflight'
    if(-not(Test-Path -LiteralPath $Receipt -PathType Leaf)){throw 'Recovery01 import receipt missing.'}
    $payload=Get-Content -LiteralPath $Receipt -Raw|ConvertFrom-Json;$State.receipt=Get-Record $Receipt
    if($payload.classification-ne'PASSED_M01_WINDOW_RECOVERY06_UNREALREADY01_REVERSIBLE_IMPORT_RECOVERY01_READY_FOR_MAPPED_PREVIEW'){throw "Unexpected receipt classification: $($payload.classification)"}
    if(@($payload.production_static_meshes.PSObject.Properties).Count-ne3){throw 'Production StaticMesh count changed.'}
    if(@($payload.canonical_sockets).Count-ne3){throw 'Canonical socket count changed.'}
    if(@($payload.frame_material_normalization.after).Count-ne5){throw 'Frame material normalization failed.'}
    if([int]$payload.map_mutations-ne0-or[bool]$payload.runtime_promotion_performed){throw 'Recovery01 exceeded its reversible-import boundary.'}
    if(-not(Test-Path -LiteralPath $Destination -PathType Container)){throw 'Recovery01 destination missing.'}
    $State.imported_asset_inventory=@(Get-ChildItem -LiteralPath $Destination -Recurse -File|Sort-Object FullName|ForEach-Object{Get-Record $_.FullName})
    if($State.imported_asset_inventory.Count-lt3){throw 'Recovery01 imported inventory is unexpectedly small.'}
    $State.source_unchanged=((Get-Sha256 $Source)-eq$Expected[$Source]);$State.project_descriptor_unchanged=((Get-Sha256 $Project)-eq$Expected[$Project])
    if(-not$State.source_unchanged-or-not$State.project_descriptor_unchanged){throw 'An immutable source authority changed.'}
    $State.classification='PASSED_M01_WINDOW_RECOVERY06_UNREALREADY01_REVERSIBLE_IMPORT_RECOVERY01_READY_FOR_MAPPED_PREVIEW';$State.failure_stage=$null;$Exit=0
}catch{$State.classification='FAILED_WITH_EVIDENCE';if($null-eq$State.failure_stage){$State.failure_stage='supervisor'};$State.failure_message=$_.Exception.Message;$Exit=1}finally{$State.ended_utc=[DateTime]::UtcNow.ToString('o');if(-not$OfflineContractTest){try{Write-JsonAtomic $Terminal $State}catch{$emergencyObject=[ordered]@{utc=[DateTime]::UtcNow.ToString('o');classification=$State.classification;stage='terminal_manifest_write';message=$_.Exception.Message};[IO.Directory]::CreateDirectory((Split-Path -Parent $Emergency))|Out-Null;[IO.File]::AppendAllText($Emergency,(($emergencyObject|ConvertTo-Json -Compress)+[Environment]::NewLine),[Text.UTF8Encoding]::new($false));$Exit=1}}}
[Environment]::Exit([int]$Exit)
