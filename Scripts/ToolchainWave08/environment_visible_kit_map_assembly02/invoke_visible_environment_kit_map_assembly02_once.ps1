param([switch]$AuthorizeSingleUnreal,[switch]$OfflineContractTest)
$ErrorActionPreference='Stop'
$Root='D:\Skyguard52'
$Project='D:\SG52T08_ENV01\Skyguard52.uproject'
$InputMap='D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentRealismStack03.umap'
$OutputMap='D:\SG52T08_ENV01\Content\M01\Lvl_M01_VisibleEnvironmentKit02.umap'
$Editor='D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$Author=Join-Path $Root 'Scripts\ToolchainWave08\environment_visible_kit_map_assembly02\author_visible_environment_kit_map_assembly02.py'
$Verifier=Join-Path $Root 'Scripts\ToolchainWave08\environment_visible_kit_map_assembly02\verify_visible_environment_kit_map_assembly02_offline.py'
$Contract=Join-Path $Root 'Docs\Toolchain\ToolchainWave08\M01VisibleEnvironmentKitMapAssembly02\execution_contract.json'
$ImportAcceptance=Join-Path $Root 'Docs\AAA_Review\M01_VISIBLE_ENVIRONMENT_KIT_FULL_IMPORT01_RECOVERY01_ACCEPTANCE_FREEZE.json'
$ImportReceipt=Join-Path $Root 'Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_KIT_FULL_IMPORT01_RECOVERY01\attempt_01\full_kit_import_receipt.json'
$MapAcceptance=Join-Path $Root 'Docs\AAA_Review\M01_ENVIRONMENT_REALISM_STACK_AUTHORING03_ATTEMPT01_ACCEPTANCE_FREEZE.json'
$Authorization=Join-Path $Root 'Production\standing_heavy_process_authorization.json'
$Attempt=Join-Path $Root 'Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_KIT_MAP_ASSEMBLY02\attempt_01'
$Receipt=Join-Path $Attempt 'assembly_receipt.json'
$Terminal=Join-Path $Root 'Saved\Reports\M01_VISIBLE_ENVIRONMENT_KIT_MAP_ASSEMBLY02_TERMINAL_SUPERVISOR.json'
$Emergency=Join-Path $Root 'Saved\Reports\M01_VISIBLE_ENVIRONMENT_KIT_MAP_ASSEMBLY02_EMERGENCY_RECEIPT.jsonl'
$TimeoutSeconds=1800
$Expected=[ordered]@{
 $Author='3c8d3f1f4d36193c4c24bcdec352a6bce56706f258e45e6c7d3b49bf0f5113f7'
 $Verifier='c58c45aa79a690a3990b30bcde72216ec57f82c13c0aaed03e23ba087feabd0f'
 $Contract='23f38c2c9148f511c7bc3dc679aea716c84bf551b73ceebf8f36b888089d32a7'
 $ImportAcceptance='6ba97e3de8cb4ca29136a2d48152424d8a62ede840991ff61aa143e5f4cfa3e6'
 $ImportReceipt='04895051591b7df6dfa39f87d1afa9f6bb72944c3cdde80e950d7cdcd35cad63'
 $MapAcceptance='292b67703dac2404f9b1c14974ca9c80256eaf2e2514387b65db23ad3b588b4a'
 $Authorization='48277d7edd869cc2b841c3993e8f7599bec5291ddf23e9c442b33e09b870c089'
 $Project='7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a'
 $InputMap='c68de75000c25569f38b9307fd8760cce85236e2f3166785350ea0c641de81e8'
 $Editor='0fb325cf215cc800ce260a1890af3f3dc314b8cc6331061d4e7e7246489af2e0'
 'D:\SG52T08_ENV01\Content\M01\EnvKit02\M01_APARTMENT_A\StaticMeshes\SM_M01_ApartmentA_DETAILS.uasset'='efdf558ceb9830c2a189a065366b7ab00cdb4c4703959bf2c4fab85b00317a79'
 'D:\SG52T08_ENV01\Content\M01\EnvKit02\M01_APARTMENT_A\StaticMeshes\SM_M01_ApartmentA_GLAZING.uasset'='695586333fc33e44da20d8aff4becbf4c59ac3ef135b7d0b5568b16c1defb716'
 'D:\SG52T08_ENV01\Content\M01\EnvKit02\M01_APARTMENT_A\StaticMeshes\SM_M01_ApartmentA_STRUCTURAL.uasset'='5bd415767b86208e512b5a408f4007ab1fd2d7ffb2a03e0ea22db999f5ac277f'
 'D:\SG52T08_ENV01\Content\M01\EnvKit02\M01_COASTAL_DISTRICT_A\StaticMeshes\SM_M01_CoastalA_HARDSCAPE.uasset'='24158096afeb7e8dc4ea3b79a1cc59df4c33eb79f81f8b7cb9ee2130899a97d6'
 'D:\SG52T08_ENV01\Content\M01\EnvKit02\M01_COASTAL_DISTRICT_A\StaticMeshes\SM_M01_CoastalA_TERRAIN.uasset'='704dadca3d389fec3dc157f7f3482428bd6587413dbf9a26c2941463a35f9662'
 'D:\SG52T08_ENV01\Content\M01\EnvKit02\M01_CORNER_RESIDENCE_C\StaticMeshes\SM_M01_CornerC_DETAILS.uasset'='3d785f89a0917699a031963c640a7300be36ea7dd326cf0c7b5f6b5c7eaae860'
 'D:\SG52T08_ENV01\Content\M01\EnvKit02\M01_CORNER_RESIDENCE_C\StaticMeshes\SM_M01_CornerC_GLAZING.uasset'='a4e623bd71afea3d69a55ce5d98e0152b2ac8390a4f8e2c6657d4d1ae54206b0'
 'D:\SG52T08_ENV01\Content\M01\EnvKit02\M01_CORNER_RESIDENCE_C\StaticMeshes\SM_M01_CornerC_STRUCTURAL.uasset'='45da6a605f829f1ca8dc19c1932f2d447faf456578d84bfdd690d44cc562e910'
 'D:\SG52T08_ENV01\Content\M01\EnvKit02\M01_LIGHTHOUSE_A\StaticMeshes\SM_M01_LighthouseA_DETAILS.uasset'='b1c8b5f538aefe9857149c0ff25dddb32c9d84a0c2f925bbe51e5e20d371c5a8'
 'D:\SG52T08_ENV01\Content\M01\EnvKit02\M01_LIGHTHOUSE_A\StaticMeshes\SM_M01_LighthouseA_GLAZING.uasset'='ffbf0602f53d3888eaac0a390850f77d691d206279ede8255adb636183ff1fb7'
 'D:\SG52T08_ENV01\Content\M01\EnvKit02\M01_LIGHTHOUSE_A\StaticMeshes\SM_M01_LighthouseA_STRUCTURAL.uasset'='1eaa71e85c94a477c7dbfb7880e0bbaa8920d3005744f681ab6526f45d6e4940'
 'D:\SG52T08_ENV01\Content\M01\EnvKit02\M01_MIDRISE_B\StaticMeshes\SM_M01_MidriseB_DETAILS.uasset'='86de006ba5dee7014571ff5ccce9a2bb718111d2bb8754708860f13ec555c8d9'
 'D:\SG52T08_ENV01\Content\M01\EnvKit02\M01_MIDRISE_B\StaticMeshes\SM_M01_MidriseB_GLAZING.uasset'='eef810c22aa44d6cbee5d8aaf6136efd75376c588031a62320fe763a68cc5d15'
 'D:\SG52T08_ENV01\Content\M01\EnvKit02\M01_MIDRISE_B\StaticMeshes\SM_M01_MidriseB_STRUCTURAL.uasset'='b96ab29ba69a3c288ae65062247c00d382db4d82787dec64722716206cb997c7'
}
function Get-Sha256([string]$Path){$s=$null;$a=$null;try{$s=[IO.File]::OpenRead($Path);$a=[Security.Cryptography.SHA256]::Create();return([BitConverter]::ToString($a.ComputeHash($s))).Replace('-','').ToLowerInvariant()}finally{if($null-ne$a){$a.Dispose()};if($null-ne$s){$s.Dispose()}}}
function Get-Record([string]$Path){$i=Get-Item -LiteralPath $Path -ErrorAction Stop;[ordered]@{path=$i.FullName;bytes=[int64]$i.Length;sha256=Get-Sha256 $i.FullName}}
function Write-JsonAtomic([string]$Path,[object]$Value){$parent=Split-Path -Parent $Path;[IO.Directory]::CreateDirectory($parent)|Out-Null;$tmp=$Path+'.tmp.'+[Diagnostics.Process]::GetCurrentProcess().Id;[IO.File]::WriteAllText($tmp,(($Value|ConvertTo-Json -Depth 32)+[Environment]::NewLine),[Text.UTF8Encoding]::new($false));if(Test-Path -LiteralPath $Path){throw "Terminal namespace already exists: $Path"};[IO.File]::Move($tmp,$Path)}
function Get-HeavyProcesses{$exact=@('Blender','UnrealEditor','UnrealEditor-Cmd','ShaderCompileWorker','AutomationTool','UnrealBuildTool','cl','link','dotnet');@(Get-Process -ErrorAction SilentlyContinue|Where-Object{$exact-contains$_.ProcessName-or$_.ProcessName-like'UnrealEditor*'-or$_.ProcessName-like'ShaderCompileWorker*'}|Select-Object ProcessName,Id,StartTime,CPU,WorkingSet64)}
$State=[ordered]@{schema='skyguard.m01-visible-environment-kit-map-assembly02.supervisor.v1';classification='FAILED_WITH_EVIDENCE';started_utc=[DateTime]::UtcNow.ToString('o');ended_utc=$null;failure_stage=$null;failure_message=$null;supervisor_launch_count=1;unreal_launch_count=0;retry_count=0;timed_out=$false;actual_exit_code=$null;actual_exit_code_type=$null;unreal_pid=$null;process_handle_retained=$false;offline_contract_test=[bool]$OfflineContractTest;exact_executable=$Editor;exact_arguments=@();working_directory=$Root;authorities=@();heavy_processes_before=@();process_samples=@();receipt=$null;output_map=$null;input_map_unchanged=$false}
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
 while(-not$process.HasExited){$process.Refresh();$sample=[ordered]@{utc=[DateTime]::UtcNow.ToString('o');pid=[int]$process.Id;working_set=[int64]$process.WorkingSet64;cpu_seconds=[double]$process.TotalProcessorTime.TotalSeconds};$State.process_samples+=$sample;[IO.File]::AppendAllText($samples,(($sample|ConvertTo-Json -Compress)+[Environment]::NewLine),[Text.UTF8Encoding]::new($false));if([DateTime]::UtcNow-ge$deadline){$State.timed_out=$true;try{$process.Kill()}catch{};throw "Unreal map assembly exceeded $TimeoutSeconds seconds."};Start-Sleep -Seconds 2}
 $process.WaitForExit();$process.Refresh();$State.actual_exit_code=[int]$process.ExitCode;$State.actual_exit_code_type=$process.ExitCode.GetType().FullName;if($process.ExitCode-ne0){throw "Unreal returned exit code $($process.ExitCode)."}
 $State.failure_stage='postflight';if(-not(Test-Path -LiteralPath $Receipt -PathType Leaf)){throw 'Assembly receipt missing.'};$payload=Get-Content -LiteralPath $Receipt -Raw|ConvertFrom-Json;$State.receipt=Get-Record $Receipt
 if($payload.classification-ne'PASSED_M01_VISIBLE_ENVIRONMENT_KIT_MAP_ASSEMBLY02_AUTOMATIC'){throw "Unexpected receipt classification: $($payload.classification)"}
 if([int]$payload.actor_count_before-ne186-or[int]$payload.actor_count_after-ne179){throw 'Actor-count contract failed.'}
 if(@($payload.removed_actor_labels).Count-ne99-or@($payload.created_actors).Count-ne92){throw 'Removal/creation contract failed.'}
 if(@($payload.loaded_assets).Count-ne14-or(@($payload.loaded_assets|Measure-Object -Property material_slot_count -Sum).Sum)-ne54){throw 'Loaded asset/material contract failed.'}
 if(@($payload.district_seams_cm).Count-ne3-or@($payload.district_seams_cm|Where-Object{[Math]::Abs([double]$_)-gt1.0}).Count-ne0){throw 'District seam contract failed.'}
 if(@($payload.legacy_placeholder_families_remaining).Count-ne0){throw 'Legacy visible placeholders remain.'}
 if(@($payload.created_actors|Where-Object{$_.grounding-and[Math]::Abs([double]$_.grounding.gap_cm)-gt1.0}).Count-ne0){throw 'Grounding gap contract failed.'}
 if(-not(Test-Path -LiteralPath $OutputMap -PathType Leaf)){throw 'Output map missing.'};$State.output_map=Get-Record $OutputMap;$State.input_map_unchanged=((Get-Sha256 $InputMap)-eq'c68de75000c25569f38b9307fd8760cce85236e2f3166785350ea0c641de81e8');if(-not$State.input_map_unchanged){throw 'Accepted input map changed.'}
 $State.classification='PASSED_M01_VISIBLE_ENVIRONMENT_KIT_MAP_ASSEMBLY02_READY_FOR_MAPPED_VISUAL_PROOF';$State.failure_stage=$null;$Exit=0
}catch{$State.classification='FAILED_WITH_EVIDENCE';if($null-eq$State.failure_stage){$State.failure_stage='supervisor'};$State.failure_message=$_.Exception.Message;$Exit=1}finally{$State.ended_utc=[DateTime]::UtcNow.ToString('o');if(-not$OfflineContractTest){try{Write-JsonAtomic $Terminal $State}catch{$emergencyObject=[ordered]@{utc=[DateTime]::UtcNow.ToString('o');classification=$State.classification;stage='terminal_manifest_write';message=$_.Exception.Message};[IO.Directory]::CreateDirectory((Split-Path -Parent $Emergency))|Out-Null;[IO.File]::AppendAllText($Emergency,(($emergencyObject|ConvertTo-Json -Compress)+[Environment]::NewLine),[Text.UTF8Encoding]::new($false));$Exit=1}}}
[Environment]::Exit([int]$Exit)
