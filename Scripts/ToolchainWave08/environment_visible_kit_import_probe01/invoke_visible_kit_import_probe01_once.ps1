param([switch]$AuthorizeSingleUnreal,[switch]$OfflineContractTest)
$ErrorActionPreference='Stop'
$Root='D:\Skyguard52'
$Project='D:\SG52T08_ENV01\Skyguard52.uproject'
$Editor='D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$Probe=Join-Path $Root 'Scripts\ToolchainWave08\environment_visible_kit_import_probe01\probe_visible_kit_import01.py'
$Verifier=Join-Path $Root 'Scripts\ToolchainWave08\environment_visible_kit_import_probe01\verify_visible_kit_import_probe01_offline.py'
$Contract=Join-Path $Root 'Docs\Toolchain\ToolchainWave08\M01VisibleEnvironmentKitImportProbe01\execution_contract.json'
$Acceptance=Join-Path $Root 'Docs\AAA_Review\M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_CHECKPOINT02_ACCEPTANCE_FREEZE.json'
$Authorization=Join-Path $Root 'Production\standing_heavy_process_authorization.json'
$Source=Join-Path $Root 'Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentProductionReset01_Checkpoint02\exports\SM_M01_Apartment_Production_A.glb'
$Attempt=Join-Path $Root 'Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_KIT_IMPORT_PROBE01\attempt_01'
$Terminal=Join-Path $Root 'Saved\Reports\M01_VISIBLE_ENVIRONMENT_KIT_IMPORT_PROBE01_TERMINAL_SUPERVISOR.json'
$Destination='D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\VisibleKitImportProbe01'
$Receipt=Join-Path $Attempt 'import_probe_receipt.json'
$Expected=@{
 $Probe='20cf9b0fd2a2d8a9b60939b5b63a29527d66569d695b01c6dc9620b04d3d1955'
 $Verifier='ce3b54cd5c29c117ab9711aa766d6adc6bb39ffbc7d30a8e4a69c864acf7516a'
 $Contract='be6e48531050f08d5fda3c278c88484446e19b16ca32772e26057b75db3b92ca'
 $Acceptance='efc54d13040f45efbabcb9e55d99754be161c15fc80804e5ea30440deb368284'
 $Authorization='48277d7edd869cc2b841c3993e8f7599bec5291ddf23e9c442b33e09b870c089'
 $Source='5c09c9eb7bf17057ec277b958165005e71e3ecac6a9430df47eddeceab9a7849'
 $Project='7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a'
 $Editor='0fb325cf215cc800ce260a1890af3f3dc314b8cc6331061d4e7e7246489af2e0'
}
$State=[ordered]@{schema='skyguard.m01-visible-environment-kit-import-probe01.supervisor.v1';classification='FAILED_WITH_EVIDENCE';started_utc=[DateTime]::UtcNow.ToString('o');ended_utc=$null;failure_stage=$null;failure_message=$null;supervisor_launch_count=1;unreal_launch_count=0;retry_count=0;timed_out=$false;actual_exit_code=$null;actual_exit_code_type=$null;unreal_pid=$null;process_handle_retained=$false;offline_contract_test=[bool]$OfflineContractTest;exact_executable=$Editor;exact_arguments=@();working_directory=$Root;authorities=@();process_samples=@();produced_files=@();receipt=$null}
function Get-Sha256([string]$Path){$stream=$null;$algo=$null;try{$stream=[IO.File]::OpenRead($Path);$algo=[Security.Cryptography.SHA256]::Create();return([BitConverter]::ToString($algo.ComputeHash($stream))).Replace('-','').ToLowerInvariant()}finally{if($null-ne$algo){$algo.Dispose()};if($null-ne$stream){$stream.Dispose()}}}
function Get-Record([string]$Path){$item=Get-Item -LiteralPath $Path;[ordered]@{path=$Path;bytes=[int64]$item.Length;sha256=Get-Sha256 $Path}}
function Write-JsonAtomic([string]$Path,[object]$Value){$parent=Split-Path -Parent $Path;[IO.Directory]::CreateDirectory($parent)|Out-Null;$tmp=$Path+'.tmp';[IO.File]::WriteAllText($tmp,($Value|ConvertTo-Json -Depth 12),[Text.UTF8Encoding]::new($false));Move-Item -LiteralPath $tmp -Destination $Path -Force}
function Get-Heavy(){Get-Process -ErrorAction SilentlyContinue|Where-Object{$_.ProcessName -match '^(UnrealEditor|UnrealEditor-Cmd|Blender|ShaderCompileWorker|AutomationTool|UnrealBuildTool|cl|link|dotnet)$'}}
try{
 $State.failure_stage='preflight'
 foreach($path in $Expected.Keys){if(-not(Test-Path -LiteralPath $path -PathType Leaf)){throw"Missing authority: $path"};$hash=Get-Sha256 $path;if($hash-ne$Expected[$path]){throw"Authority hash mismatch: $path"};$State.authorities+=Get-Record $path}
 if(Test-Path -LiteralPath $Attempt){throw"Fresh attempt namespace exists: $Attempt"}
 if(Test-Path -LiteralPath $Terminal){throw"Fresh terminal namespace exists: $Terminal"}
 if(Test-Path -LiteralPath $Destination){throw"Fresh import destination exists: $Destination"}
 $heavy=@(Get-Heavy);if($heavy.Count-ne0){throw"Heavy process gate failed: $($heavy.ProcessName -join ', ')"}
 if($OfflineContractTest){$State.classification='PASS_OFFLINE_CONTRACT';return}
 if(-not$AuthorizeSingleUnreal){throw'Explicit mechanical authorization switch absent.'}
 [IO.Directory]::CreateDirectory($Attempt)|Out-Null
 $stdout=Join-Path $Attempt 'unreal.stdout.log';$stderr=Join-Path $Attempt 'unreal.stderr.log';$engineLog=Join-Path $Attempt 'unreal-engine.log'
 $arguments=@($Project,'-run=pythonscript',("-script="+$Probe),'-unattended','-nop4','-nosplash','-nullrhi','-NoSound','-stdout','-FullStdOutLogOutput',('-abslog='+$engineLog),'-DisablePlugins=Fab,Bridge,EditorTelemetry,RuntimeTelemetry,EOSShared','-ini:EditorSettings:[/Script/UnrealEd.AnalyticsPrivacySettings]:bSendUsageData=False')
 $State.exact_arguments=$arguments;$State.failure_stage='launch';$State.unreal_launch_count=1
 $process=Start-Process -FilePath $Editor -ArgumentList $arguments -WorkingDirectory $Root -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru
 $null=$process.Handle;$State.process_handle_retained=$true;$State.unreal_pid=[int]$process.Id
 $deadline=[DateTime]::UtcNow.AddSeconds(1800);$State.failure_stage='wait'
 while(-not$process.HasExited){
  if([DateTime]::UtcNow-ge$deadline){$State.timed_out=$true;Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue;throw'Unreal import probe exceeded 1800 seconds.'}
  $process.Refresh();$State.process_samples+= [ordered]@{utc=[DateTime]::UtcNow.ToString('o');pid=[int]$process.Id;working_set=[int64]$process.WorkingSet64;cpu_seconds=[double]$process.TotalProcessorTime.TotalSeconds};Start-Sleep -Seconds 2
 }
 $process.WaitForExit();$process.Refresh();$State.actual_exit_code=[int]$process.ExitCode;$State.actual_exit_code_type=$process.ExitCode.GetType().FullName
 if($process.ExitCode-ne0){throw"Unreal returned exit code $($process.ExitCode)."}
 $State.failure_stage='postflight'
 if(-not(Test-Path -LiteralPath $Receipt -PathType Leaf)){throw'Import-probe receipt missing.'}
 $receiptObject=Get-Content -LiteralPath $Receipt -Raw|ConvertFrom-Json
 $State.receipt=Get-Record $Receipt
 if($receiptObject.classification-ne'PASSED_VISIBLE_KIT_IMPORT_PROBE_READY_FOR_FULL_INTEGRATION_DESIGN'){throw"Unexpected receipt classification: $($receiptObject.classification)"}
 if(-not(Test-Path -LiteralPath $Destination -PathType Container)){throw'Import destination was not created.'}
 $assets=@(Get-ChildItem -LiteralPath $Destination -Recurse -File -Filter '*.uasset')
 if($assets.Count-lt1){throw'Import destination contains no uassets.'}
 $State.produced_files=@(Get-ChildItem -LiteralPath $Destination -Recurse -File|Sort-Object FullName|ForEach-Object{Get-Record $_.FullName})
 $State.classification='PASSED_VISIBLE_KIT_IMPORT_PROBE_READY_FOR_FULL_INTEGRATION_DESIGN';$State.failure_stage=$null
}catch{$State.failure_message=$_.Exception.Message;if($null-eq$State.failure_stage){$State.failure_stage='supervisor'}}finally{$State.ended_utc=[DateTime]::UtcNow.ToString('o');if(-not$OfflineContractTest){Write-JsonAtomic $Terminal $State}}
if($State.classification-eq'PASS_OFFLINE_CONTRACT'){Write-Output($State|ConvertTo-Json -Depth 8);exit 0}
if($State.classification-ne'PASSED_VISIBLE_KIT_IMPORT_PROBE_READY_FOR_FULL_INTEGRATION_DESIGN'){Write-Error($State.failure_message);exit 1}
Write-Output($State|ConvertTo-Json -Depth 8);exit 0
