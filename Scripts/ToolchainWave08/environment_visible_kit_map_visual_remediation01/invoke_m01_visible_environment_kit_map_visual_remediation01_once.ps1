param([switch]$AuthorizeSingleUnreal,[switch]$OfflineContractTest)
$ErrorActionPreference='Stop'
$Root='D:\Skyguard52'
$Project='D:\SG52T08_ENV01\Skyguard52.uproject'
$InputMap='D:\SG52T08_ENV01\Content\M01\Lvl_M01_VisibleEnvironmentKit02_Recovery02.umap'
$OutputMap='D:\SG52T08_ENV01\Content\M01\Lvl_M01_VisibleEnvironmentKit02_VisualRemediation01.umap'
$Editor='D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$Author=Join-Path $Root 'Scripts\ToolchainWave08\environment_visible_kit_map_visual_remediation01\author_m01_visible_environment_kit_map_visual_remediation01.py'
$Verifier=Join-Path $Root 'Scripts\ToolchainWave08\environment_visible_kit_map_visual_remediation01\verify_m01_visible_environment_kit_map_visual_remediation01_offline.py'
$Contract=Join-Path $Root 'Docs\Toolchain\ToolchainWave08\M01VisibleEnvironmentKitMapVisualRemediation01\execution_contract.json'
$MapAcceptance=Join-Path $Root 'Docs\AAA_Review\M01_VISIBLE_ENVIRONMENT_KIT_MAP_ASSEMBLY02_RECOVERY02_ACCEPTANCE_FREEZE.json'
$FailedVisualFreeze=Join-Path $Root 'Docs\AAA_Review\M01_VISIBLE_ENVIRONMENT_KIT_MAP_VISUAL_PROOF01_ATTEMPT01_TERMINAL_FREEZE.json'
$Authorization=Join-Path $Root 'Production\standing_heavy_process_authorization.json'
$Attempt=Join-Path $Root 'Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_KIT_MAP_VISUAL_REMEDIATION01\attempt_01'
$Receipt=Join-Path $Attempt 'authoring_receipt.json'
$Terminal=Join-Path $Root 'Saved\Reports\M01_VISIBLE_ENVIRONMENT_KIT_MAP_VISUAL_REMEDIATION01_TERMINAL_SUPERVISOR.json'
$Emergency=Join-Path $Root 'Saved\Reports\M01_VISIBLE_ENVIRONMENT_KIT_MAP_VISUAL_REMEDIATION01_EMERGENCY_RECEIPT.jsonl'
$TimeoutSeconds=900
$Expected=[ordered]@{
 $Author='517044b54109fd951b4135594f47cc514047fd60e43254435c1e30913cbce0d2'
 $Verifier='23ccacb3f6c6ae4bbb3e9555cf5629bd8c0fc93092795994b3e1d0921290864a'
 $Contract='d0b191b81a86d5ddf576852870070f9c58ffea70ac95f6db233f69ff88eb208b'
 $MapAcceptance='1c228eaea281be78d5a872c9356828fde1fb91cd6ceaf42ef2ec4aafc9c9e3f4'
 $FailedVisualFreeze='4c94568bf4f57960073e218709ea1a9192560865649143716f918788e4c013cf'
 $Authorization='48277d7edd869cc2b841c3993e8f7599bec5291ddf23e9c442b33e09b870c089'
 $Project='7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a'
 $InputMap='186cb23fc67c78613453552d1da9c203161a63b12cc894f66019784e04b00fee'
 $Editor='0fb325cf215cc800ce260a1890af3f3dc314b8cc6331061d4e7e7246489af2e0'
}
function Get-Sha256([string]$Path){$s=$null;$a=$null;try{$s=[IO.File]::OpenRead($Path);$a=[Security.Cryptography.SHA256]::Create();return([BitConverter]::ToString($a.ComputeHash($s))).Replace('-','').ToLowerInvariant()}finally{if($null-ne$a){$a.Dispose()};if($null-ne$s){$s.Dispose()}}}
function Get-Record([string]$Path){$i=Get-Item -LiteralPath $Path -ErrorAction Stop;[ordered]@{path=$i.FullName;bytes=[int64]$i.Length;sha256=Get-Sha256 $i.FullName}}
function Write-JsonAtomic([string]$Path,[object]$Value){$parent=Split-Path -Parent $Path;[IO.Directory]::CreateDirectory($parent)|Out-Null;$tmp=$Path+'.tmp.'+[Diagnostics.Process]::GetCurrentProcess().Id;[IO.File]::WriteAllText($tmp,(($Value|ConvertTo-Json -Depth 32)+[Environment]::NewLine),[Text.UTF8Encoding]::new($false));if(Test-Path -LiteralPath $Path){throw "Terminal namespace already exists: $Path"};[IO.File]::Move($tmp,$Path)}
function Get-HeavyProcesses{$exact=@('Blender','UnrealEditor','UnrealEditor-Cmd','ShaderCompileWorker','AutomationTool','UnrealBuildTool','cl','link','dotnet');@(Get-Process -ErrorAction SilentlyContinue|Where-Object{$exact-contains$_.ProcessName-or$_.ProcessName-like'UnrealEditor*'-or$_.ProcessName-like'ShaderCompileWorker*'}|Select-Object ProcessName,Id,StartTime,CPU,WorkingSet64)}
$State=[ordered]@{schema='skyguard.m01-visible-environment-kit-map-visual-remediation01.supervisor.v1';classification='FAILED_WITH_EVIDENCE';started_utc=[DateTime]::UtcNow.ToString('o');ended_utc=$null;failure_stage=$null;failure_message=$null;supervisor_launch_count=1;unreal_launch_count=0;retry_count=0;timed_out=$false;actual_exit_code=$null;actual_exit_code_type=$null;unreal_pid=$null;process_handle_retained=$false;offline_contract_test=[bool]$OfflineContractTest;exact_executable=$Editor;exact_arguments=@();working_directory=$Root;authorities=@();heavy_processes_before=@();process_samples=@();receipt=$null;output_map=$null;input_map_unchanged=$false}
$Exit=1
try{
 $State.failure_stage='preflight'
 foreach($entry in $Expected.GetEnumerator()){if(-not(Test-Path -LiteralPath $entry.Key -PathType Leaf)){throw "Missing authority: $($entry.Key)"};$actual=Get-Sha256 $entry.Key;if($actual-ne$entry.Value){throw "Authority hash mismatch: $($entry.Key) expected=$($entry.Value) actual=$actual"};$State.authorities+=Get-Record $entry.Key}
 $auth=Get-Content -LiteralPath $Authorization -Raw|ConvertFrom-Json;if($auth.status-ne'ACTIVE'-or$auth.execution_policy.per_run_user_authorization_required-ne$false){throw 'Standing authorization is not active.'}
 if(Test-Path -LiteralPath $Attempt){throw "Fresh attempt namespace exists: $Attempt"};if(Test-Path -LiteralPath $Terminal){throw "Fresh terminal namespace exists: $Terminal"};if(Test-Path -LiteralPath $OutputMap){throw "Fresh output map exists: $OutputMap"}
 $verifyOutput=& python $Verifier 2>&1;if($LASTEXITCODE-ne0-or($verifyOutput-join"`n")-notmatch'PASS'){throw "Offline verifier failed: $($verifyOutput-join' ')"}
 if($OfflineContractTest){$State.classification='PASS_OFFLINE_CONTRACT';$State.failure_stage=$null;$Exit=0;return}
 if(-not$AuthorizeSingleUnreal){$State.classification='REFUSED_MISSING_MECHANICAL_GUARD';$State.failure_stage='authorization';$Exit=2;return}
 $State.heavy_processes_before=@(Get-HeavyProcesses);if($State.heavy_processes_before.Count-ne0){throw "Heavy process gate failed: $($State.heavy_processes_before.ProcessName -join ', ')"}
 [IO.Directory]::CreateDirectory($Attempt)|Out-Null;$stdout=Join-Path $Attempt 'unreal.stdout.log';$stderr=Join-Path $Attempt 'unreal.stderr.log';$engineLog=Join-Path $Attempt 'unreal-engine.log';$samples=Join-Path $Attempt 'process_tree_samples.jsonl'
 $arguments=@($Project,'-run=pythonscript',('-script='+$Author),'-unattended','-nop4','-nosplash','-nullrhi','-NoSound','-stdout','-FullStdOutLogOutput',('-abslog='+$engineLog),'-DisablePlugins=Fab,Bridge,EditorTelemetry,RuntimeTelemetry,EOSShared','-ini:EditorSettings:[/Script/UnrealEd.AnalyticsPrivacySettings]:bSendUsageData=False')
 $State.exact_arguments=$arguments;$State.failure_stage='launch';$process=Start-Process -FilePath $Editor -ArgumentList $arguments -WorkingDirectory $Root -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru;$State.unreal_launch_count=1;$State.unreal_pid=[int]$process.Id;$null=$process.Handle;$State.process_handle_retained=$true;$deadline=[DateTime]::UtcNow.AddSeconds($TimeoutSeconds);$State.failure_stage='wait'
 while(-not$process.HasExited){$process.Refresh();$sample=[ordered]@{utc=[DateTime]::UtcNow.ToString('o');pid=[int]$process.Id;working_set=[int64]$process.WorkingSet64;cpu_seconds=[double]$process.TotalProcessorTime.TotalSeconds};$State.process_samples+=$sample;[IO.File]::AppendAllText($samples,(($sample|ConvertTo-Json -Compress)+[Environment]::NewLine),[Text.UTF8Encoding]::new($false));if([DateTime]::UtcNow-ge$deadline){$State.timed_out=$true;try{$process.Kill()}catch{};throw "Unreal visual remediation exceeded $TimeoutSeconds seconds."};Start-Sleep -Seconds 2}
 $process.WaitForExit();$process.Refresh();$State.actual_exit_code=[int]$process.ExitCode;$State.actual_exit_code_type=$process.ExitCode.GetType().FullName;if($process.ExitCode-ne0){throw "Unreal returned exit code $($process.ExitCode)."}
 $State.failure_stage='postflight';if(-not(Test-Path -LiteralPath $Receipt -PathType Leaf)){throw 'Authoring receipt missing.'};$payload=Get-Content -LiteralPath $Receipt -Raw|ConvertFrom-Json;$State.receipt=Get-Record $Receipt
 if($payload.classification-ne'PASSED_M01_VISIBLE_ENVIRONMENT_KIT_MAP_VISUAL_REMEDIATION01_AUTOMATIC'){throw "Unexpected receipt classification: $($payload.classification)"}
 if([int]$payload.actor_count-ne179-or[int]$payload.rotated_city_actor_count-ne81-or@($payload.building_placements).Count-ne27){throw 'Actor/placement remediation contract failed.'}
 if(@($payload.building_placements|Where-Object{$_.facade_facing_ocean-ne$true}).Count-ne0){throw 'One or more facades do not face the ocean.'}
 if([Math]::Abs([double]$payload.skylight_after.intensity-3.25)-gt0.001-or$payload.skylight_after.real_time_capture-ne$true-or$payload.skylight_after.lower_hemisphere_is_solid_color-ne$false){throw 'Skylight remediation contract failed.'}
 if(-not(Test-Path -LiteralPath $OutputMap -PathType Leaf)){throw 'VisualRemediation01 output map missing.'};$State.output_map=Get-Record $OutputMap;$State.input_map_unchanged=((Get-Sha256 $InputMap)-eq'186cb23fc67c78613453552d1da9c203161a63b12cc894f66019784e04b00fee');if(-not$State.input_map_unchanged){throw 'Accepted Recovery02 input map changed.'}
 $State.classification='PASSED_M01_VISIBLE_ENVIRONMENT_KIT_MAP_VISUAL_REMEDIATION01_READY_FOR_MAPPED_VISUAL_PROOF';$State.failure_stage=$null;$Exit=0
}catch{$State.classification='FAILED_WITH_EVIDENCE';if($null-eq$State.failure_stage){$State.failure_stage='supervisor'};$State.failure_message=$_.Exception.Message;$Exit=1}finally{$State.ended_utc=[DateTime]::UtcNow.ToString('o');if(-not$OfflineContractTest){try{Write-JsonAtomic $Terminal $State}catch{$emergencyObject=[ordered]@{utc=[DateTime]::UtcNow.ToString('o');classification=$State.classification;stage='terminal_manifest_write';message=$_.Exception.Message};[IO.Directory]::CreateDirectory((Split-Path -Parent $Emergency))|Out-Null;[IO.File]::AppendAllText($Emergency,(($emergencyObject|ConvertTo-Json -Compress)+[Environment]::NewLine),[Text.UTF8Encoding]::new($false));$Exit=1}}}
[Environment]::Exit([int]$Exit)
