param([switch]$AuthorizeSingleUnreal,[switch]$OfflineContractTest)
$ErrorActionPreference='Stop'
$Root='D:\Skyguard52'
$Project='D:\SG52T08_ENV01\Skyguard52.uproject'
$Map='D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentRealismStack03.umap'
$Editor='D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$Importer=Join-Path $Root 'Scripts\ToolchainWave08\environment_visible_kit_full_import01\import_visible_environment_kit01.py'
$Verifier=Join-Path $Root 'Scripts\ToolchainWave08\environment_visible_kit_full_import01\verify_visible_environment_kit_full_import01_offline.py'
$Contract=Join-Path $Root 'Docs\Toolchain\ToolchainWave08\M01VisibleEnvironmentKitFullImport01\execution_contract.json'
$Acceptance=Join-Path $Root 'Docs\AAA_Review\M01_VISIBLE_ENVIRONMENT_KIT_IMPORT_REPROBE03_ACCEPTANCE_FREEZE.json'
$ReadyAcceptance=Join-Path $Root 'Docs\AAA_Review\M01_VISIBLE_ENVIRONMENT_UNREAL_READY02_ACCEPTANCE_FREEZE.json'
$Authorization=Join-Path $Root 'Production\standing_heavy_process_authorization.json'
$ExportRoot=Join-Path $Root 'Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentProductionReset01_UnrealReady02\exports'
$Attempt=Join-Path $Root 'Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_KIT_FULL_IMPORT01\attempt_01'
$Terminal=Join-Path $Root 'Saved\Reports\M01_VISIBLE_ENVIRONMENT_KIT_FULL_IMPORT01_TERMINAL_SUPERVISOR.json'
$Emergency=Join-Path $Root 'Saved\Reports\M01_VISIBLE_ENVIRONMENT_KIT_FULL_IMPORT01_EMERGENCY_RECEIPT.jsonl'
$Destination='D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\VisibleEnvironmentKit01'
$Receipt=Join-Path $Attempt 'full_kit_import_receipt.json'
$TimeoutSeconds=1800
$Expected=[ordered]@{
 $Importer='5db48b5f2862a6406b12534e85137f2a98021058816976f1f2e1f94d5191e3df'
 $Verifier='831fc50961bf62c834cbc816f60863cfb32b2df8cae0a0fe1f20e4ccd02ecaad'
 $Contract='783ca2f4196a7b41153f1403590f2c3b0ce776ef88e2745544e6ae10ac0c001d'
 $Acceptance='ce332b3648c848eaead2c898e27dd215c949758bf46350d15574daa889f29184'
 $ReadyAcceptance='9f0bce85b5011ca8b002e52fdb651fffe6adcb10f541c74583cc13599199dc20'
 $Authorization='48277d7edd869cc2b841c3993e8f7599bec5291ddf23e9c442b33e09b870c089'
 (Join-Path $ExportRoot 'SM_M01_Apartment_Production_A_CONSOLIDATED.glb')='77b04f21f75f97b337eb89d142b5d672d9be5eaaa79184ee9f44421d35e51080'
 (Join-Path $ExportRoot 'SM_M01_CoastalDistrict_Production_A_CONSOLIDATED.glb')='7c76f069a0f72592b4cdf0928529c1fc35405fa175cea27f5697124313f85c0a'
 (Join-Path $ExportRoot 'SM_M01_CornerResidence_Production_C_CONSOLIDATED.glb')='6c5fe2a8ce70a4dbf0d0bec910261e7eef68183ca6103f3b756c4f0f0065cdb8'
 (Join-Path $ExportRoot 'SM_M01_Lighthouse_Production_A_CONSOLIDATED.glb')='50e38c728d2497a6689bd352dcc8c4cb3de0e9ab8f2dfb50b5d518680d608301'
 (Join-Path $ExportRoot 'SM_M01_Midrise_Production_B_CONSOLIDATED.glb')='6c4b22ab84b79510345215772da2649b0cb101089d87336b4604944a74ca3155'
 $Project='7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a'
 $Map='c68de75000c25569f38b9307fd8760cce85236e2f3166785350ea0c641de81e8'
 $Editor='0fb325cf215cc800ce260a1890af3f3dc314b8cc6331061d4e7e7246489af2e0'
}
function Get-Sha256([string]$Path){$s=$null;$a=$null;try{$s=[IO.File]::OpenRead($Path);$a=[Security.Cryptography.SHA256]::Create();return([BitConverter]::ToString($a.ComputeHash($s))).Replace('-','').ToLowerInvariant()}finally{if($null-ne$a){$a.Dispose()};if($null-ne$s){$s.Dispose()}}}
function Get-Record([string]$Path){$i=Get-Item -LiteralPath $Path -ErrorAction Stop;[ordered]@{path=$i.FullName;bytes=[int64]$i.Length;sha256=Get-Sha256 $i.FullName}}
function Write-JsonAtomic([string]$Path,[object]$Value){$parent=Split-Path -Parent $Path;[IO.Directory]::CreateDirectory($parent)|Out-Null;$tmp=$Path+'.tmp.'+[Diagnostics.Process]::GetCurrentProcess().Id;[IO.File]::WriteAllText($tmp,(($Value|ConvertTo-Json -Depth 20)+[Environment]::NewLine),[Text.UTF8Encoding]::new($false));if(Test-Path -LiteralPath $Path){throw "Terminal namespace already exists: $Path"};[IO.File]::Move($tmp,$Path)}
function Get-HeavyProcesses{$exact=@('Blender','UnrealEditor','UnrealEditor-Cmd','ShaderCompileWorker','AutomationTool','UnrealBuildTool','cl','link','dotnet');@(Get-Process -ErrorAction SilentlyContinue|Where-Object{$exact-contains$_.ProcessName-or$_.ProcessName-like'UnrealEditor*'-or$_.ProcessName-like'ShaderCompileWorker*'}|Select-Object ProcessName,Id,StartTime,CPU,WorkingSet64)}
$State=[ordered]@{schema='skyguard.m01-visible-environment-kit-full-import01.supervisor.v1';classification='FAILED_WITH_EVIDENCE';started_utc=[DateTime]::UtcNow.ToString('o');ended_utc=$null;failure_stage=$null;failure_message=$null;supervisor_launch_count=1;unreal_launch_count=0;retry_count=0;timed_out=$false;actual_exit_code=$null;actual_exit_code_type=$null;unreal_pid=$null;process_handle_retained=$false;offline_contract_test=[bool]$OfflineContractTest;exact_executable=$Editor;exact_arguments=@();working_directory=$Root;authorities=@();heavy_processes_before=@();process_samples=@();produced_files=@();receipt=$null}
$Exit=1
try{
 $State.failure_stage='preflight'
 foreach($entry in $Expected.GetEnumerator()){if(-not(Test-Path -LiteralPath $entry.Key -PathType Leaf)){throw "Missing authority: $($entry.Key)"};$actual=Get-Sha256 $entry.Key;if($actual-ne$entry.Value){throw "Authority hash mismatch: $($entry.Key) expected=$($entry.Value) actual=$actual"};$State.authorities+=Get-Record $entry.Key}
 $auth=Get-Content -LiteralPath $Authorization -Raw|ConvertFrom-Json;if($auth.status-ne'ACTIVE'-or$auth.execution_policy.per_run_user_authorization_required-ne$false){throw 'Standing authorization is not active.'}
 if(Test-Path -LiteralPath $Attempt){throw "Fresh attempt namespace exists: $Attempt"};if(Test-Path -LiteralPath $Terminal){throw "Fresh terminal namespace exists: $Terminal"};if(Test-Path -LiteralPath $Destination){throw "Fresh import destination exists: $Destination"}
 if($OfflineContractTest){$State.classification='PASS_OFFLINE_CONTRACT';$Exit=0;return}
 if(-not$AuthorizeSingleUnreal){$State.classification='REFUSED_MISSING_MECHANICAL_GUARD';$Exit=2;return}
 $State.heavy_processes_before=@(Get-HeavyProcesses);if($State.heavy_processes_before.Count-ne0){throw "Heavy process gate failed: $($State.heavy_processes_before.ProcessName -join ', ')"}
 [IO.Directory]::CreateDirectory($Attempt)|Out-Null;$stdout=Join-Path $Attempt 'unreal.stdout.log';$stderr=Join-Path $Attempt 'unreal.stderr.log';$engineLog=Join-Path $Attempt 'unreal-engine.log';$samples=Join-Path $Attempt 'process_tree_samples.jsonl'
 $arguments=@($Project,'-run=pythonscript',('-script='+$Importer),'-unattended','-nop4','-nosplash','-nullrhi','-NoSound','-stdout','-FullStdOutLogOutput',('-abslog='+$engineLog),'-DisablePlugins=Fab,Bridge,EditorTelemetry,RuntimeTelemetry,EOSShared','-ini:EditorSettings:[/Script/UnrealEd.AnalyticsPrivacySettings]:bSendUsageData=False')
 $State.exact_arguments=$arguments;$State.failure_stage='launch';$process=Start-Process -FilePath $Editor -ArgumentList $arguments -WorkingDirectory $Root -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru;$State.unreal_launch_count=1;$State.unreal_pid=[int]$process.Id;$null=$process.Handle;$State.process_handle_retained=$true;$deadline=[DateTime]::UtcNow.AddSeconds($TimeoutSeconds);$State.failure_stage='wait'
 while(-not$process.HasExited){$process.Refresh();$sample=[ordered]@{utc=[DateTime]::UtcNow.ToString('o');pid=[int]$process.Id;working_set=[int64]$process.WorkingSet64;cpu_seconds=[double]$process.TotalProcessorTime.TotalSeconds};$State.process_samples+=$sample;[IO.File]::AppendAllText($samples,(($sample|ConvertTo-Json -Compress)+[Environment]::NewLine),[Text.UTF8Encoding]::new($false));if([DateTime]::UtcNow-ge$deadline){$State.timed_out=$true;try{$process.Kill()}catch{};throw "Unreal full-kit import exceeded $TimeoutSeconds seconds."};Start-Sleep -Seconds 2}
 $process.WaitForExit();$process.Refresh();$State.actual_exit_code=[int]$process.ExitCode;$State.actual_exit_code_type=$process.ExitCode.GetType().FullName;if($process.ExitCode-ne0){throw "Unreal returned exit code $($process.ExitCode)."}
 $State.failure_stage='postflight';if(-not(Test-Path -LiteralPath $Receipt -PathType Leaf)){throw 'Full-kit import receipt missing.'};$receiptObject=Get-Content -LiteralPath $Receipt -Raw|ConvertFrom-Json;$State.receipt=Get-Record $Receipt;if($receiptObject.classification-ne'PASSED_FULL_VISIBLE_ENVIRONMENT_KIT_IMPORT_READY_FOR_REVERSIBLE_MAP_ASSEMBLY_DESIGN'){throw "Unexpected receipt classification: $($receiptObject.classification)"};if([int]$receiptObject.static_mesh_count-ne14){throw "Unexpected StaticMesh count: $($receiptObject.static_mesh_count)"};if([int]$receiptObject.material_slot_total-ne54){throw "Unexpected material-slot total: $($receiptObject.material_slot_total)"};if(-not(Test-Path -LiteralPath $Destination -PathType Container)){throw 'Import destination was not created.'};$assets=@(Get-ChildItem -LiteralPath $Destination -Recurse -File -Filter '*.uasset');if($assets.Count-lt14){throw 'Import destination contains too few uassets.'};$State.produced_files=@(Get-ChildItem -LiteralPath $Destination -Recurse -File|Sort-Object FullName|ForEach-Object{Get-Record $_.FullName});$State.classification='PASSED_FULL_VISIBLE_ENVIRONMENT_KIT_IMPORT_READY_FOR_REVERSIBLE_MAP_ASSEMBLY_DESIGN';$State.failure_stage=$null;$Exit=0
}catch{$State.classification='FAILED_WITH_EVIDENCE';if($null-eq$State.failure_stage){$State.failure_stage='supervisor'};$State.failure_message=$_.Exception.Message;$Exit=1}finally{$State.ended_utc=[DateTime]::UtcNow.ToString('o');if(-not$OfflineContractTest){try{Write-JsonAtomic $Terminal $State}catch{$emergencyObject=[ordered]@{utc=[DateTime]::UtcNow.ToString('o');classification=$State.classification;stage='terminal_manifest_write';message=$_.Exception.Message};[IO.Directory]::CreateDirectory((Split-Path -Parent $Emergency))|Out-Null;[IO.File]::AppendAllText($Emergency,(($emergencyObject|ConvertTo-Json -Compress)+[Environment]::NewLine),[Text.UTF8Encoding]::new($false));$Exit=1}}}
[Environment]::Exit([int]$Exit)
