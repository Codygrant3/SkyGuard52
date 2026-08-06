[CmdletBinding()]
param(
    [switch]$AuthorizeSingleUnrealProof,
    [switch]$OfflineContractTest,
    [string]$OfflineEvidenceRoot
)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'

$root='D:\Skyguard52'
$editor='D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$uproject=Join-Path $root 'Skyguard52.uproject'
$contract=Join-Path $root 'Docs\AAA_Review\PHASE4_M01_RECOVERY05_UNREAL_PROOF01_CONTRACT.json'
$bindingFreeze=Join-Path $root 'Docs\AAA_Review\PHASE4_M01_RECOVERY05_RUNTIME_BINDING01_TERMINAL_FREEZE.json'
$pluginDescriptor=Join-Path $root 'Plugins\SkyguardRecovery03NativeRecovery05\SkyguardRecovery03NativeRecovery05.uplugin'
$boundDll=Join-Path $root 'Plugins\SkyguardRecovery03NativeRecovery05\Binaries\Win64\UnrealEditor-SkyguardRecovery03NativeRecovery05.dll'
$runtimeAttempt=Join-Path $root 'Saved\BuildAttempts\PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY03_NATIVE_BUILD_RECOVERY01\runtime_attempt_01'
$proofRoot=Join-Path $runtimeAttempt 'proof'
$launcherAttempt=Join-Path $root 'Saved\BuildAttempts\PHASE4_M01_RECOVERY05_UNREAL_PROOF01\launcher_attempt_01'
$executionPreflight=Join-Path $root 'Saved\Reports\PHASE4_M01_RECOVERY05_UNREAL_PROOF01_EXECUTION_PREFLIGHT.json'
$terminalSupervisor=Join-Path $root 'Saved\Reports\PHASE4_M01_RECOVERY05_UNREAL_PROOF01_TERMINAL_SUPERVISOR.json'
$emergencyReceipt=Join-Path $root 'Saved\Reports\PHASE4_M01_RECOVERY05_UNREAL_PROOF01_EMERGENCY_RECEIPT.jsonl'
$timeoutSeconds=600

function Get-Sha256([string]$Path){
 if(-not[IO.File]::Exists($Path)){throw "Missing file: $Path"}
 $s=$null;$h=$null
 try{$s=[IO.File]::Open($Path,[IO.FileMode]::Open,[IO.FileAccess]::Read,[IO.FileShare]::Read);$h=[Security.Cryptography.SHA256]::Create();return([BitConverter]::ToString($h.ComputeHash($s))).Replace('-','').ToLowerInvariant()}
 finally{if($null-ne$h){$h.Dispose()};if($null-ne$s){$s.Dispose()}}
}
function Assert-File([string]$Path,[long]$Bytes,[string]$Hash){
 $i=Get-Item -LiteralPath $Path -ErrorAction Stop
 if($i.Length-ne$Bytes){throw "Byte mismatch: $Path"}
 if((Get-Sha256 $Path)-ne$Hash){throw "Hash mismatch: $Path"}
}
function Write-Json([string]$Path,$Value){
 $parent=Split-Path -Parent $Path;if(-not(Test-Path $parent)){[IO.Directory]::CreateDirectory($parent)|Out-Null}
 $tmp="$Path.tmp";[IO.File]::WriteAllText($tmp,($Value|ConvertTo-Json -Depth 30),[Text.UTF8Encoding]::new($false))
 if(Test-Path $Path){$bak="$Path.atomic.backup";[IO.File]::Replace($tmp,$Path,$bak);if(Test-Path $bak){Remove-Item -LiteralPath $bak -Force}}else{[IO.File]::Move($tmp,$Path)}
}
function Assert-NoHeavy{
 $p=@(Get-Process -ErrorAction SilentlyContinue|Where-Object{$_.ProcessName-match'^(UnrealEditor|UnrealEditor-Cmd|ShaderCompileWorker|AutomationTool|UnrealBuildTool|blender|dotnet|cl|link)$'})
 if($p.Count){throw "Heavy process active: $($p.ProcessName-join', ')"}
}
function Assert-Authorities{
 Assert-File $bindingFreeze 3702 '220a243347ec6bf344bcfae40ff7a42f256aa4b944b8ce3a8188015b14a68ae1'
 Assert-File $editor 512952 '0fb325cf215cc800ce260a1890af3f3dc314b8cc6331061d4e7e7246489af2e0'
 Assert-File $boundDll 177664 'a231397c5a0692424963c88a62a7f463d74cb9fc6a96c677527ae9521ee38b3b'
 Assert-File $pluginDescriptor 465 '63e70f723e27f3c29536834dac8a7757629e43b02c13a02ae954fe2c432d57a5'
 $d=Get-Content -Raw $pluginDescriptor|ConvertFrom-Json
 if($d.EnabledByDefault-ne$false-or$d.Modules[0].Name-ne'SkyguardRecovery03NativeRecovery05'){throw 'Recovery05 descriptor mismatch'}
 $c=Get-Content -Raw $contract|ConvertFrom-Json
 if($c.binding_id-ne'P4.6-M01-RECOVERY05-UNREAL-PROOF-01'){throw 'Proof contract identity mismatch'}
 foreach($r in $c.locked_inputs){Assert-File (Join-Path $root $r.file) ([long]$r.bytes) $r.sha256}
}

$arguments=@(
 "`"$uproject`"",
 '/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_ProductionEnvironment_v5_attempt03',
 '-dx12','-sm6','-unattended','-nosplash','-NoSound','-NoVSync',
 '-ExecCmds="r.ScreenPercentage 100,sg.ViewDistanceQuality 3,sg.AntiAliasingQuality 3,sg.ShadowQuality 3,sg.GlobalIlluminationQuality 3,sg.ReflectionQuality 3,sg.PostProcessQuality 3,sg.TextureQuality 3,sg.EffectsQuality 3,sg.FoliageQuality 3,sg.ShadingQuality 3"',
 '-EnablePlugins=SkyguardRecovery03NativeRecovery05',
 '-DisablePlugins=SkyguardRecovery03,SkyguardRecovery03NativeRecovery01,SkyguardRecovery03NativeRecovery04,Fab,Bridge,EditorTelemetry,RuntimeTelemetry,EOSShared',
 '-ini:EditorSettings:[/Script/UnrealEd.AnalyticsPrivacySettings]:bSendUsageData=False',
 '-SkyguardRecovery01ContractId=P4.6-M01-REPRESENTATIVE-VISUAL-008-RECOVERY-03-NATIVE-BUILD-RECOVERY-01',
 '-SkyguardRecovery01Authorization=P4.6-M01-REPRESENTATIVE-VISUAL-008-RECOVERY-03-NATIVE-BUILD-RECOVERY-01-ONE-SHOT',
 '-SkyguardRecovery01ExpectedMap=/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_ProductionEnvironment_v5_attempt03',
 "-SkyguardRecovery01AttemptRoot=`"$runtimeAttempt`""
)

$state=[ordered]@{schema='skyguard.phase4.m01-recovery05-unreal-proof01-terminal-supervisor.v1';gate='FAILED_WITH_EVIDENCE';started_utc=[DateTime]::UtcNow.ToString('o');ended_utc=$null;failure_stage=$null;failure_message=$null;actual_exit_code=$null;actual_exit_code_type=$null;timed_out=$false;launch_count=0;retry_count=0;process_handle_retained=$false;unreal_started=$false;blender_started=$false;arguments=$arguments}
$manifestPath=if($OfflineContractTest){if([string]::IsNullOrWhiteSpace($OfflineEvidenceRoot)){throw '-OfflineEvidenceRoot required'};Join-Path $OfflineEvidenceRoot 'terminal_supervisor.json'}else{$terminalSupervisor}
$preflightPath=if($OfflineContractTest){Join-Path $OfflineEvidenceRoot 'execution_preflight.json'}else{$executionPreflight}
$emergencyPath=if($OfflineContractTest){Join-Path $OfflineEvidenceRoot 'emergency_receipt.jsonl'}else{$emergencyReceipt}
$stage='initialization';$exit=1;$process=$null
try{
 $stage='preflight';Assert-Authorities;Assert-NoHeavy
 foreach($p in @($runtimeAttempt,$proofRoot,$launcherAttempt,$executionPreflight,$terminalSupervisor,$emergencyReceipt)){if(Test-Path $p){throw "Future namespace exists: $p"}}
 $preflight=[ordered]@{schema='skyguard.phase4.m01-recovery05-unreal-proof01-execution-preflight.v1';gate='PASS_READY_TO_START_SINGLE_UNREAL_PROCESS';launch_count=0;retry_count=0;runtime_absent=$true;launcher_absent=$true;heavy_process_count=0;bound_dll_sha256=Get-Sha256 $boundDll}
 Write-Json $preflightPath $preflight
 if($OfflineContractTest){
  if($arguments.Count-ne16){throw 'Frozen Unreal argument count mismatch'}
  $state.gate='PASS_OFFLINE_CONTRACT_TEST';$state.actual_exit_code=0;$state.actual_exit_code_type='System.Int32';$exit=0
 }else{
  if(-not$AuthorizeSingleUnrealProof){throw 'Normal mode requires -AuthorizeSingleUnrealProof'}
  $stage='launcher_namespace';[IO.Directory]::CreateDirectory((Join-Path $launcherAttempt 'logs'))|Out-Null
  $stdout=Join-Path $launcherAttempt 'logs\recovery05.stdout.log';$stderr=Join-Path $launcherAttempt 'logs\recovery05.stderr.log';$engineLog=Join-Path $launcherAttempt 'logs\recovery05.engine.log';$processTree=Join-Path $launcherAttempt 'process_tree_samples.jsonl'
  $runArguments=@($arguments+"-abslog=`"$engineLog`"")
  $stage='unreal_launch'
  $process=Start-Process -FilePath $editor -ArgumentList $runArguments -PassThru -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError $stderr
  $state.launch_count=1;$state.unreal_started=$true;$handle=$process.Handle;$state.process_handle_retained=$null-ne$handle
  $deadline=[DateTime]::UtcNow.AddSeconds($timeoutSeconds)
  while(-not$process.HasExited-and[DateTime]::UtcNow-lt$deadline){
   $sample=[ordered]@{sampled_utc=[DateTime]::UtcNow.ToString('o');supervisor_process_id=$PID;unreal_process_id=$process.Id;unreal_has_exited=$process.HasExited;working_set_bytes=if($process.HasExited){$null}else{$process.WorkingSet64}}
   [IO.File]::AppendAllText($processTree,(($sample|ConvertTo-Json -Compress)+[Environment]::NewLine),[Text.UTF8Encoding]::new($false))
   Start-Sleep -Seconds 2;$process.Refresh()
  }
  if(-not$process.HasExited){$state.timed_out=$true;Stop-Process -Id $process.Id -Force;throw 'Unreal proof exceeded 600-second supervisor timeout'}
  $process.WaitForExit();$process.Refresh();$code=$process.ExitCode
  if($null-eq$code-or-not($code-is[int])){throw 'Unreal exit code is null or nonnumeric'}
  $state.actual_exit_code=[int]$code;$state.actual_exit_code_type=$code.GetType().FullName
  if($code-ne0){throw "Unreal proof returned exit code $code"}
  if(-not(Test-Path (Join-Path $runtimeAttempt 'terminal_receipt.json'))){throw 'Native terminal receipt is absent'}
  $state.gate='UNREAL_EXITED_AWAITING_POSTFLIGHT';$exit=0
 }
}catch{$state.failure_stage=$stage;$state.failure_message=$_.Exception.Message;$exit=1}
finally{
 $state.ended_utc=[DateTime]::UtcNow.ToString('o')
 try{Write-Json $manifestPath $state}catch{try{$parent=Split-Path -Parent $emergencyPath;if(-not(Test-Path $parent)){[IO.Directory]::CreateDirectory($parent)|Out-Null};[IO.File]::AppendAllText($emergencyPath,((@{gate='FAILED_WITH_EVIDENCE';message=$_.Exception.Message}|ConvertTo-Json -Compress)+[Environment]::NewLine),[Text.UTF8Encoding]::new($false))}catch{};$exit=1}
}
exit([int]$exit)
