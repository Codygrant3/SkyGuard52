param([switch]$AuthorizeSingleUnreal,[switch]$OfflineContractTest)

Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$Root='D:\Skyguard52'
$Project='D:\SG52T08_ENV01\Skyguard52.uproject'
$InputMap='D:\SG52T08_ENV01\Content\M01\Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01Recovery01.umap'
$OutputMap='D:\SG52T08_ENV01\Content\M01\Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01Recovery01_PromenadeBollards01.umap'
$Destination='D:\SG52T08_ENV01\Content\M01\PromenadeBollardRecovery01'
$Source='D:\Skyguard52\Production\Attempts\m01-promenade-prop-kit-grok-mcp-recovery01\attempt_20260811T063000000000Z\output\exports\M01_Promenade_Bollard_A.glb'
$Acceptance='D:\Skyguard52\Docs\AAA_Review\M01_PROMENADE_PROP_KIT_GROK_MCP_PRODUCTION_RECOVERY01_POSTREVIEW_TERMINAL_FREEZE.json'
$Editor='D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$Author='D:\Skyguard52\Scripts\GrokProduction\author_m01_promenade_bollard_recovery01_unreal_integration01.py'
$Contract='D:\Skyguard52\Docs\Toolchain\ToolchainWave08\M01PromenadeBollardRecovery01UnrealIntegration01\execution_contract.json'
$Authorization='D:\Skyguard52\Production\standing_heavy_process_authorization.json'
$Attempt='D:\Skyguard52\Saved\BuildAttempts\M01_PROMENADE_BOLLARD_RECOVERY01_UNREAL_INTEGRATION01\attempt_01'
$Receipt=Join-Path $Attempt 'integration_receipt.json'
$Terminal='D:\Skyguard52\Saved\Reports\M01_PROMENADE_BOLLARD_RECOVERY01_UNREAL_INTEGRATION01_TERMINAL_SUPERVISOR.json'
$Emergency='D:\Skyguard52\Saved\Reports\M01_PROMENADE_BOLLARD_RECOVERY01_UNREAL_INTEGRATION01_EMERGENCY_RECEIPT.jsonl'
$TimeoutSeconds=1800

$Expected=[ordered]@{
 $Author='4f77bc814c69be5d6195e4d178306b4da7b0408c9e0aa04ba2f827261647df57'
 $Contract='b9636af50ff0f65c772963730d62fa0fc1f042bc504be962d83f472196daff27'
 $Acceptance='99aa93fb74dff633d472144b44c524b69b43af07453f15092db3583f776484dd'
 $Source='585c830686015d9733640dbbc6d4785d1f23c3fad043a8317642dec1b3ad550f'
 $Authorization='48277d7edd869cc2b841c3993e8f7599bec5291ddf23e9c442b33e09b870c089'
 $Project='7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a'
 $InputMap='a2ccdbe88a77821acb3e601cc129af932f9061f8def90af452d620895ed6a1aa'
 $Editor='0fb325cf215cc800ce260a1890af3f3dc314b8cc6331061d4e7e7246489af2e0'
}

function Get-Sha256([string]$Path){$stream=$null;$hasher=$null;try{$stream=[IO.File]::Open($Path,[IO.FileMode]::Open,[IO.FileAccess]::Read,[IO.FileShare]::Read);$hasher=[Security.Cryptography.SHA256]::Create();return([BitConverter]::ToString($hasher.ComputeHash($stream))).Replace('-','').ToLowerInvariant()}finally{if($null-ne$hasher){$hasher.Dispose()};if($null-ne$stream){$stream.Dispose()}}}
function Get-Record([string]$Path){$item=Get-Item -LiteralPath $Path -ErrorAction Stop;[ordered]@{path=$item.FullName;bytes=[int64]$item.Length;sha256=Get-Sha256 $item.FullName}}
function Get-Inventory([string]$Path){@(Get-ChildItem -LiteralPath $Path -Recurse -File|Sort-Object FullName|ForEach-Object{Get-Record $_.FullName})}
function Write-JsonAtomic([string]$Path,[object]$Value){$parent=Split-Path -Parent $Path;[IO.Directory]::CreateDirectory($parent)|Out-Null;$temporary=$Path+'.tmp.'+[Diagnostics.Process]::GetCurrentProcess().Id;[IO.File]::WriteAllText($temporary,(($Value|ConvertTo-Json -Depth 50)+[Environment]::NewLine),[Text.UTF8Encoding]::new($false));if(Test-Path -LiteralPath $Path){throw "Refusing to overwrite terminal evidence: $Path"};[IO.File]::Move($temporary,$Path)}
function Get-HeavyProcesses{$exact=@('Blender','UnrealEditor','UnrealEditor-Cmd','ShaderCompileWorker','AutomationTool','UnrealBuildTool','cl','link','dotnet');@(Get-Process -ErrorAction SilentlyContinue|Where-Object{$exact-contains$_.ProcessName-or$_.ProcessName-like'UnrealEditor*'-or$_.ProcessName-like'ShaderCompileWorker*'}|Select-Object ProcessName,Id,StartTime,CPU,WorkingSet64)}

$State=[ordered]@{schema='skyguard.m01-promenade-bollard-recovery01.unreal-integration01.supervisor.v1';classification='FAILED_WITH_EVIDENCE';started_utc=[DateTime]::UtcNow.ToString('o');ended_utc=$null;failure_stage=$null;failure_message=$null;supervisor_launch_count=1;unreal_launch_count=0;retry_count=0;timed_out=$false;actual_exit_code=$null;actual_exit_code_type=$null;unreal_pid=$null;process_handle_retained=$false;offline_contract_test=[bool]$OfflineContractTest;exact_executable=$Editor;exact_arguments=@();working_directory=$Root;authorities=@();heavy_processes_before=@();process_samples=@();receipt=$null;output_map=$null;destination_inventory=@();input_map_unchanged=$false;source_glb_unchanged=$false;accepted_freeze_unchanged=$false;rejected_asset_import_count=$null}
$Exit=1
try{
 $State.failure_stage='preflight'
 foreach($entry in $Expected.GetEnumerator()){if(-not(Test-Path -LiteralPath $entry.Key -PathType Leaf)){throw "Missing authority: $($entry.Key)"};$actual=Get-Sha256 $entry.Key;if($actual-ne$entry.Value){throw "Authority hash mismatch: $($entry.Key) expected=$($entry.Value) actual=$actual"};$State.authorities+=Get-Record $entry.Key}
 $auth=Get-Content -LiteralPath $Authorization -Raw|ConvertFrom-Json
 if($auth.status-ne'ACTIVE'-or$auth.execution_policy.per_run_user_authorization_required-ne$false){throw 'Standing heavy-process authorization is not active.'}
 if(Test-Path -LiteralPath $Attempt){throw "Fresh attempt namespace exists: $Attempt"}
 if(Test-Path -LiteralPath $Terminal){throw "Fresh terminal namespace exists: $Terminal"}
 if(Test-Path -LiteralPath $Destination){throw "Fresh Unreal destination exists: $Destination"}
 if(Test-Path -LiteralPath $OutputMap){throw "Fresh output map exists: $OutputMap"}
 $authorTest=& python $Author --offline-contract-test 2>&1
 if($LASTEXITCODE-ne0-or($authorTest-join"`n")-notmatch'PASS_M01_PROMENADE_BOLLARD'){throw "Author offline contract test failed: $($authorTest-join' ')"}
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
 while(-not$process.HasExited){$process.Refresh();$sample=[ordered]@{utc=[DateTime]::UtcNow.ToString('o');pid=[int]$process.Id;working_set=[int64]$process.WorkingSet64;cpu_seconds=[double]$process.TotalProcessorTime.TotalSeconds};$State.process_samples+=$sample;[IO.File]::AppendAllText($samples,(($sample|ConvertTo-Json -Compress)+[Environment]::NewLine),[Text.UTF8Encoding]::new($false));if([DateTime]::UtcNow-ge$deadline){$State.timed_out=$true;try{$process.Kill()}catch{};throw "Unreal bollard integration exceeded $TimeoutSeconds seconds."};Start-Sleep -Seconds 2}
 $process.WaitForExit();$process.Refresh();$State.actual_exit_code=[int]$process.ExitCode;$State.actual_exit_code_type=$process.ExitCode.GetType().FullName
 if($process.ExitCode-ne0){throw "Unreal returned exit code $($process.ExitCode)."}
 $State.failure_stage='postflight'
 if(-not(Test-Path -LiteralPath $Receipt -PathType Leaf)){throw 'Bollard integration receipt missing.'}
 $payload=Get-Content -LiteralPath $Receipt -Raw|ConvertFrom-Json;$State.receipt=Get-Record $Receipt
 if($payload.classification-ne'PASSED_M01_PROMENADE_BOLLARD_RECOVERY01_UNREAL_INTEGRATION01_READY_FOR_D3D12_VISUAL_PROOF'){throw "Unexpected receipt classification: $($payload.classification) error=$($payload.error)"}
 if([int]$payload.actor_count_before-ne100-or[int]$payload.actor_count_after-ne113-or@($payload.placements).Count-ne13){throw 'Bollard placement contract failed.'}
 if(-not(Test-Path -LiteralPath $OutputMap -PathType Leaf)){throw 'Fresh bollard map missing.'}
 if(-not(Test-Path -LiteralPath $Destination -PathType Container)){throw 'Fresh bollard asset namespace missing.'}
 $State.output_map=Get-Record $OutputMap;$State.destination_inventory=@(Get-Inventory $Destination)
 $State.input_map_unchanged=((Get-Sha256 $InputMap)-eq'a2ccdbe88a77821acb3e601cc129af932f9061f8def90af452d620895ed6a1aa')
 $State.source_glb_unchanged=((Get-Sha256 $Source)-eq'585c830686015d9733640dbbc6d4785d1f23c3fad043a8317642dec1b3ad550f')
 $State.accepted_freeze_unchanged=((Get-Sha256 $Acceptance)-eq'99aa93fb74dff633d472144b44c524b69b43af07453f15092db3583f776484dd')
 if(-not$State.input_map_unchanged-or-not$State.source_glb_unchanged-or-not$State.accepted_freeze_unchanged){throw 'Accepted authority changed during integration.'}
 $rejectedPattern='Streetlight|Bench|LitterBin|Railing';$State.rejected_asset_import_count=@($State.destination_inventory|Where-Object{$_.path-match$rejectedPattern}).Count
 if($State.rejected_asset_import_count-ne0){throw 'Rejected prop content entered the Unreal namespace.'}
 if($State.destination_inventory.Count-lt1){throw 'Bollard asset inventory is empty.'}
 $State.classification='PASSED_M01_PROMENADE_BOLLARD_RECOVERY01_UNREAL_INTEGRATION01_READY_FOR_D3D12_VISUAL_PROOF';$State.failure_stage=$null;$Exit=0
}catch{$State.classification='FAILED_WITH_EVIDENCE';if($null-eq$State.failure_stage){$State.failure_stage='supervisor'};$State.failure_message=$_.Exception.Message;$Exit=1}finally{$State.ended_utc=[DateTime]::UtcNow.ToString('o');if(-not$OfflineContractTest){try{Write-JsonAtomic $Terminal $State}catch{$emergencyObject=[ordered]@{utc=[DateTime]::UtcNow.ToString('o');classification=$State.classification;stage='terminal_manifest_write';message=$_.Exception.Message};[IO.Directory]::CreateDirectory((Split-Path -Parent $Emergency))|Out-Null;[IO.File]::AppendAllText($Emergency,(($emergencyObject|ConvertTo-Json -Compress)+[Environment]::NewLine),[Text.UTF8Encoding]::new($false));$Exit=1}}}
[Environment]::Exit([int]$Exit)
