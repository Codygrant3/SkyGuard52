param([switch]$AuthorizeSingleUnreal,[switch]$OfflineContractTest)

Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$Root='D:\Skyguard52'
$Project='D:\SG52T08_ENV01\Skyguard52.uproject'
$InputMap='D:\SG52T08_ENV01\Content\M01\Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01.umap'
$OutputMap='D:\SG52T08_ENV01\Content\M01\Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01Recovery01.umap'
$ImportedAssets='D:\SG52T08_ENV01\Content\M01\CoastalCorridorC06R01'
$Editor='D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$ScriptDir=Join-Path $Root 'Scripts\ToolchainWave08\m01_coastal_corridor_c06r01_unreal_integration01_recovery01'
$Author=Join-Path $ScriptDir 'author_corridor_axis_recovery01.py'
$Verifier=Join-Path $ScriptDir 'verify_corridor_axis_recovery01_offline.py'
$Contract=Join-Path $Root 'Docs\Toolchain\ToolchainWave08\M01CoastalCorridorC06R01UnrealIntegration01Recovery01\execution_contract.json'
$PriorTerminal=Join-Path $Root 'Saved\Reports\M01_COASTAL_CORRIDOR_C06R01_UNREAL_INTEGRATION01_TERMINAL_SUPERVISOR.json'
$PriorReceipt=Join-Path $Root 'Saved\BuildAttempts\M01_COASTAL_CORRIDOR_C06R01_UNREAL_INTEGRATION01\attempt_01\integration_receipt.json'
$Authorization=Join-Path $Root 'Production\standing_heavy_process_authorization.json'
$Attempt=Join-Path $Root 'Saved\BuildAttempts\M01_COASTAL_CORRIDOR_C06R01_UNREAL_INTEGRATION01_RECOVERY01\attempt_01'
$Receipt=Join-Path $Attempt 'axis_correction_receipt.json'
$Terminal=Join-Path $Root 'Saved\Reports\M01_COASTAL_CORRIDOR_C06R01_UNREAL_INTEGRATION01_RECOVERY01_TERMINAL_SUPERVISOR.json'
$Emergency=Join-Path $Root 'Saved\Reports\M01_COASTAL_CORRIDOR_C06R01_UNREAL_INTEGRATION01_RECOVERY01_EMERGENCY_RECEIPT.jsonl'
$TimeoutSeconds=900
$Expected=[ordered]@{
 $Author='7323ef14f5dd845c00c4c046b91e17302322e9bd48bea3dc95bd06d5db81bff3'
 $Verifier='0e0220b7d0d79f2ebfd7525989d7fb0646a4a34fd01d3d0f79d792c038cfae46'
 $Contract='df0316a465c2127d0cad520c3836410cbc3abbbfa1a6994f9561caed143662fc'
 $PriorTerminal='7dd6d65900306771f65643002e8db817efa954e2f68e5cae081ffbf26a9757b1'
 $PriorReceipt='c68ebcf0f4f7314da3a2cc6990b95d0de4f65666c0ec287a55e05fdaf61d13d0'
 $Authorization='48277d7edd869cc2b841c3993e8f7599bec5291ddf23e9c442b33e09b870c089'
 $Project='7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a'
 $InputMap='1e8164704968153e59c69f463ce1b76d03c9deafb32c8d6b239574b1406ae5db'
 $Editor='0fb325cf215cc800ce260a1890af3f3dc314b8cc6331061d4e7e7246489af2e0'
}

function Get-Sha256([string]$Path){$stream=$null;$hasher=$null;try{$stream=[IO.File]::Open($Path,[IO.FileMode]::Open,[IO.FileAccess]::Read,[IO.FileShare]::Read);$hasher=[Security.Cryptography.SHA256]::Create();return([BitConverter]::ToString($hasher.ComputeHash($stream))).Replace('-','').ToLowerInvariant()}finally{if($null-ne$hasher){$hasher.Dispose()};if($null-ne$stream){$stream.Dispose()}}}
function Get-Record([string]$Path){$item=Get-Item -LiteralPath $Path -ErrorAction Stop;[ordered]@{path=$item.FullName;bytes=[int64]$item.Length;sha256=Get-Sha256 $item.FullName}}
function Get-Inventory([string]$Path){@(Get-ChildItem -LiteralPath $Path -Recurse -File|Sort-Object FullName|ForEach-Object{Get-Record $_.FullName})}
function Write-JsonAtomic([string]$Path,[object]$Value){$parent=Split-Path -Parent $Path;[IO.Directory]::CreateDirectory($parent)|Out-Null;$temporary=$Path+'.tmp.'+[Diagnostics.Process]::GetCurrentProcess().Id;[IO.File]::WriteAllText($temporary,(($Value|ConvertTo-Json -Depth 40)+[Environment]::NewLine),[Text.UTF8Encoding]::new($false));if(Test-Path -LiteralPath $Path){throw "Refusing to overwrite terminal evidence: $Path"};[IO.File]::Move($temporary,$Path)}
function Get-HeavyProcesses{$exact=@('Blender','UnrealEditor','UnrealEditor-Cmd','ShaderCompileWorker','AutomationTool','UnrealBuildTool','cl','link','dotnet');@(Get-Process -ErrorAction SilentlyContinue|Where-Object{$exact-contains$_.ProcessName-or$_.ProcessName-like'UnrealEditor*'-or$_.ProcessName-like'ShaderCompileWorker*'}|Select-Object ProcessName,Id,StartTime,CPU,WorkingSet64)}

$State=[ordered]@{schema='skyguard.m01-coastal-corridor-c06r01.axis-recovery01.supervisor.v1';classification='FAILED_WITH_EVIDENCE';started_utc=[DateTime]::UtcNow.ToString('o');ended_utc=$null;failure_stage=$null;failure_message=$null;supervisor_launch_count=1;unreal_launch_count=0;retry_count=0;timed_out=$false;actual_exit_code=$null;actual_exit_code_type=$null;unreal_pid=$null;process_handle_retained=$false;offline_contract_test=[bool]$OfflineContractTest;exact_executable=$Editor;exact_arguments=@();working_directory=$Root;authorities=@();heavy_processes_before=@();process_samples=@();receipt=$null;output_map=$null;input_map_unchanged=$false;imported_assets_before=@();imported_assets_after=@();imported_assets_unchanged=$false}
$Exit=1
try{
 $State.failure_stage='preflight'
 foreach($entry in $Expected.GetEnumerator()){if(-not(Test-Path -LiteralPath $entry.Key -PathType Leaf)){throw "Missing authority: $($entry.Key)"};$actual=Get-Sha256 $entry.Key;if($actual-ne$entry.Value){throw "Authority hash mismatch: $($entry.Key) expected=$($entry.Value) actual=$actual"};$State.authorities+=Get-Record $entry.Key}
 $auth=Get-Content -LiteralPath $Authorization -Raw|ConvertFrom-Json
 if($auth.status-ne'ACTIVE'-or$auth.execution_policy.per_run_user_authorization_required-ne$false){throw 'Standing heavy-process authorization is not active.'}
 if(-not(Test-Path -LiteralPath $ImportedAssets -PathType Container)){throw "Imported corridor namespace is missing: $ImportedAssets"}
 if(Test-Path -LiteralPath $Attempt){throw "Fresh attempt namespace exists: $Attempt"}
 if(Test-Path -LiteralPath $Terminal){throw "Fresh terminal namespace exists: $Terminal"}
 if(Test-Path -LiteralPath $OutputMap){throw "Fresh output map exists: $OutputMap"}
 $State.imported_assets_before=@(Get-Inventory $ImportedAssets)
 if($State.imported_assets_before.Count-lt4){throw 'Imported corridor inventory is unexpectedly small.'}
 $verifyOutput=& python $Verifier 2>&1
 if($LASTEXITCODE-ne0-or($verifyOutput-join"`n")-notmatch'PASS_M01_COASTAL_CORRIDOR'){throw "Offline verifier failed: $($verifyOutput-join' ')"}
 $authorTest=& python $Author --offline-contract-test 2>&1
 if($LASTEXITCODE-ne0-or($authorTest-join"`n")-notmatch'PASS_M01_COASTAL_CORRIDOR'){throw "Author offline contract test failed: $($authorTest-join' ')"}
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
 while(-not$process.HasExited){$process.Refresh();$sample=[ordered]@{utc=[DateTime]::UtcNow.ToString('o');pid=[int]$process.Id;working_set=[int64]$process.WorkingSet64;cpu_seconds=[double]$process.TotalProcessorTime.TotalSeconds};$State.process_samples+=$sample;[IO.File]::AppendAllText($samples,(($sample|ConvertTo-Json -Compress)+[Environment]::NewLine),[Text.UTF8Encoding]::new($false));if([DateTime]::UtcNow-ge$deadline){$State.timed_out=$true;try{$process.Kill()}catch{};throw "Unreal corridor axis correction exceeded $TimeoutSeconds seconds."};Start-Sleep -Seconds 2}
 $process.WaitForExit();$process.Refresh();$State.actual_exit_code=[int]$process.ExitCode;$State.actual_exit_code_type=$process.ExitCode.GetType().FullName
 if($process.ExitCode-ne0){throw "Unreal returned exit code $($process.ExitCode)."}
 $State.failure_stage='postflight'
 if(-not(Test-Path -LiteralPath $Receipt -PathType Leaf)){throw 'Axis-correction receipt missing.'}
 $payload=Get-Content -LiteralPath $Receipt -Raw|ConvertFrom-Json;$State.receipt=Get-Record $Receipt
 if($payload.classification-ne'PASSED_M01_COASTAL_CORRIDOR_C06R01_AXIS_RECOVERY01_READY_FOR_D3D12_VISUAL_PROOF'){throw "Unexpected receipt classification: $($payload.classification)"}
 if([int]$payload.actor_count-ne100-or@($payload.transformed_actors).Count-ne3-or[int]$payload.unchanged_non_corridor_actor_count-ne97){throw 'Actor correction contract failed.'}
 foreach($row in @($payload.transformed_actors)){if([double]$row.scale_after[1]-ne-1.0-or[double]$row.bounds_origin_after_cm[1]-le0.0){throw "Corrected actor contract failed: $($row.label)"}}
 if(-not(Test-Path -LiteralPath $OutputMap -PathType Leaf)){throw 'Recovery01 output map missing.'}
 $State.output_map=Get-Record $OutputMap
 $State.input_map_unchanged=((Get-Sha256 $InputMap)-eq'1e8164704968153e59c69f463ce1b76d03c9deafb32c8d6b239574b1406ae5db')
 if(-not$State.input_map_unchanged){throw 'Accepted integration input map changed.'}
 $State.imported_assets_after=@(Get-Inventory $ImportedAssets)
 $beforeJson=$State.imported_assets_before|ConvertTo-Json -Depth 8 -Compress;$afterJson=$State.imported_assets_after|ConvertTo-Json -Depth 8 -Compress
 $State.imported_assets_unchanged=($beforeJson-eq$afterJson)
 if(-not$State.imported_assets_unchanged){throw 'Imported corridor asset namespace changed.'}
 $State.classification='PASSED_M01_COASTAL_CORRIDOR_C06R01_AXIS_RECOVERY01_READY_FOR_D3D12_VISUAL_PROOF';$State.failure_stage=$null;$Exit=0
}catch{$State.classification='FAILED_WITH_EVIDENCE';if($null-eq$State.failure_stage){$State.failure_stage='supervisor'};$State.failure_message=$_.Exception.Message;$Exit=1}finally{$State.ended_utc=[DateTime]::UtcNow.ToString('o');if(-not$OfflineContractTest){try{Write-JsonAtomic $Terminal $State}catch{$emergencyObject=[ordered]@{utc=[DateTime]::UtcNow.ToString('o');classification=$State.classification;stage='terminal_manifest_write';message=$_.Exception.Message};[IO.Directory]::CreateDirectory((Split-Path -Parent $Emergency))|Out-Null;[IO.File]::AppendAllText($Emergency,(($emergencyObject|ConvertTo-Json -Compress)+[Environment]::NewLine),[Text.UTF8Encoding]::new($false));$Exit=1}}}
[Environment]::Exit([int]$Exit)
