[CmdletBinding()]
param(
    [switch]$AuthorizeSingleBinding,
    [switch]$OfflineContractTest,
    [string]$OfflineEvidenceRoot
)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'

$Root='D:\Skyguard52'
$PluginRoot='D:\Skyguard52\Plugins\SkyguardRecovery03NativeRecovery05'
$TargetDir=Join-Path $PluginRoot 'Binaries\Win64'
$AttemptRoot='D:\Skyguard52\Saved\BuildAttempts\PHASE4_M01_RECOVERY05_RUNTIME_BINDING01\binding_attempt_01'
$TerminalManifest='D:\Skyguard52\Saved\Reports\PHASE4_M01_RECOVERY05_RUNTIME_BINDING01_TERMINAL_SUPERVISOR_MANIFEST.json'
$EmergencyReceipt='D:\Skyguard52\Saved\Reports\PHASE4_M01_RECOVERY05_RUNTIME_BINDING01_EMERGENCY_RECEIPT.jsonl'
$AcceptedFreeze='D:\Skyguard52\Docs\AAA_Review\PHASE4_M01_RECOVERY05_BUILDPLUGIN01_RECOVERY01_ATTEMPT01_TERMINAL_FREEZE.json'
$PostMigration='D:\Skyguard52\Saved\Reports\PHASE4_M01_RECOVERY05_ACTIVE_PLUGIN_ROOT_MIGRATION01_POST_MIGRATION_INVENTORY.json'
$Descriptor=Join-Path $PluginRoot 'SkyguardRecovery03NativeRecovery05.uplugin'
$Sources=[ordered]@{
 'UnrealEditor-SkyguardRecovery03NativeRecovery05.dll'='D:\SG52R05P02\Binaries\Win64\UnrealEditor-SkyguardRecovery03NativeRecovery05.dll'
 'UnrealEditor-SkyguardRecovery03NativeRecovery05.pdb'='D:\SG52R05P02\Binaries\Win64\UnrealEditor-SkyguardRecovery03NativeRecovery05.pdb'
 'UnrealEditor.modules'='D:\SG52R05P02\Binaries\Win64\UnrealEditor.modules'
}
$Expected=[ordered]@{
 'UnrealEditor-SkyguardRecovery03NativeRecovery05.dll'=[ordered]@{bytes=177664;sha256='a231397c5a0692424963c88a62a7f463d74cb9fc6a96c677527ae9521ee38b3b'}
 'UnrealEditor-SkyguardRecovery03NativeRecovery05.pdb'=[ordered]@{bytes=24514560;sha256='cf52429896a8e18ff3b0ba4f631c335e1a0cf8c83d15ec93f79f84524c0e4268'}
 'UnrealEditor.modules'=[ordered]@{bytes=146;sha256='0afbc2d8947a01a59e9e17ed031eca5618f33a30a5733438740ac5888fafe36a'}
}

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
function Assert-DescriptorPath([string]$Path){
 $d=Get-Content -Raw -LiteralPath $Path|ConvertFrom-Json
 if($d.EnabledByDefault-ne$false-or-not($d.EnabledByDefault-is[bool])){throw 'Active descriptor is not Boolean-false disabled by default.'}
 if(@($d.Modules).Count-ne1-or$d.Modules[0].Name-ne'SkyguardRecovery03NativeRecovery05'){throw 'Active module identity mismatch.'}
}
function Assert-Descriptor{Assert-DescriptorPath $Descriptor}
function Assert-RollbackUnambiguous($Rollback){
 if($Rollback.target_was_absent-ne$true){throw 'Rollback target-origin is ambiguous.'}
 if($null-eq$Rollback.created_files){throw 'Rollback created-file inventory is absent.'}
 foreach($file in @($Rollback.created_files)){if([string]::IsNullOrWhiteSpace([string]$file)){throw 'Rollback contains an ambiguous file path.'}}
}
function Assert-Sources{
 foreach($name in $Sources.Keys){$e=$Expected[$name];Assert-File $Sources[$name] ([long]$e.bytes) $e.sha256}
}
function Assert-TargetFresh([string]$Path){
 if(Test-Path -LiteralPath $Path){throw "Binding target already exists: $Path"}
}
function Assert-NoHeavy{
 $p=@(Get-Process -ErrorAction SilentlyContinue|Where-Object{$_.ProcessName-match'^(UnrealEditor|UnrealEditor-Cmd|ShaderCompileWorker|AutomationTool|UnrealBuildTool|blender|dotnet|cl|link)$'})
 if($p.Count){throw "Heavy process active: $($p.ProcessName-join', ')"}
}
function Assert-Authorities{
 Assert-File $AcceptedFreeze 5587 '9aca763d4019d2b071b88575ed7b9e799a627d27c676bb8f04d19d70cd5633c0'
 Assert-File $Descriptor 465 '63e70f723e27f3c29536834dac8a7757629e43b02c13a02ae954fe2c432d57a5'
 Assert-File $PostMigration 12569 '8c4db237b825e88941b48c232898f087cb0fe23253b4a3f96500af52d3cb9fc6'
 $inventory=Get-Content -Raw $PostMigration|ConvertFrom-Json
 foreach($r in $inventory.records){Assert-File $r.current_path ([long]$r.bytes) $r.sha256}
 Assert-Descriptor;Assert-Sources
}
function Invoke-Binding([string]$Destination,[string]$EvidenceRoot){
 Assert-TargetFresh $Destination
 $rollback=[ordered]@{schema='skyguard.runtime-binding01-rollback.v1';target_was_absent=$true;created_directory=$Destination;created_files=@();rollback_required=$false;rollback_completed=$false}
 Write-Json (Join-Path $EvidenceRoot 'rollback_manifest.json') $rollback
 [IO.Directory]::CreateDirectory($Destination)|Out-Null
 try{
  foreach($name in $Sources.Keys){
   $target=Join-Path $Destination $name
   if(Test-Path $target){throw "No-overwrite violation: $target"}
   [IO.File]::Copy($Sources[$name],$target,$false)
   $rollback.created_files+=@($target);$rollback.rollback_required=$true
   Write-Json (Join-Path $EvidenceRoot 'rollback_manifest.json') $rollback
   $e=$Expected[$name];Assert-File $target ([long]$e.bytes) $e.sha256
  }
  $actual=@(Get-ChildItem -LiteralPath $Destination -File)
  if($actual.Count-ne3){throw 'Unexpected binding target file count.'}
  foreach($file in $actual){if(-not$Sources.Contains($file.Name)){throw "Unexpected target file: $($file.Name)"}}
  $rollback.rollback_required=$false
  Write-Json (Join-Path $EvidenceRoot 'rollback_manifest.json') $rollback
 }catch{
  $rollback.rollback_required=$true
  foreach($file in $rollback.created_files){if(Test-Path $file){Remove-Item -LiteralPath $file -Force}}
  if((Test-Path $Destination)-and@(Get-ChildItem $Destination -Force).Count-eq0){Remove-Item -LiteralPath $Destination -Force}
  $rollback.rollback_completed=$true
  Write-Json (Join-Path $EvidenceRoot 'rollback_manifest.json') $rollback
  throw
 }
}

$state=[ordered]@{schema='skyguard.phase4.m01-recovery05-runtime-binding01-terminal.v1';classification='FAILED_WITH_EVIDENCE';mode=if($OfflineContractTest){'offline_contract_test'}else{'binding'};started_utc=[DateTime]::UtcNow.ToString('o');ended_utc=$null;failure_stage=$null;failure_message=$null;preflight_passed=$false;binding_launch_count=0;copy_count=0;retry_count=0;unreal_launch_count=0;blender_launch_count=0;target_created=$false;rollback_required=$false;rollback_completed=$false}
$manifestPath=if($OfflineContractTest){if([string]::IsNullOrWhiteSpace($OfflineEvidenceRoot)){throw '-OfflineEvidenceRoot required'};Join-Path $OfflineEvidenceRoot 'terminal_manifest.json'}else{$TerminalManifest}
$emergencyPath=if($OfflineContractTest){Join-Path $OfflineEvidenceRoot 'emergency_receipt.jsonl'}else{$EmergencyReceipt}
$stage='initialization';$exit=1
try{
 $stage='preflight';Assert-Authorities;Assert-NoHeavy
 if($OfflineContractTest){
  [IO.Directory]::CreateDirectory($OfflineEvidenceRoot)|Out-Null
  $target=Join-Path $OfflineEvidenceRoot 'binding-target';Invoke-Binding $target $OfflineEvidenceRoot
  foreach($name in $Sources.Keys){$e=$Expected[$name];Assert-File (Join-Path $target $name) ([long]$e.bytes) $e.sha256}
  try{Invoke-Binding $target (Join-Path $OfflineEvidenceRoot 'existing-test');throw 'Existing-target rejection failed'}catch{if($_.Exception.Message-eq'Existing-target rejection failed'){throw}}
  $unexpected=Join-Path $OfflineEvidenceRoot 'unexpected-target';[IO.Directory]::CreateDirectory($unexpected)|Out-Null;[IO.File]::WriteAllText((Join-Path $unexpected 'unexpected.bin'),'x')
  try{Invoke-Binding $unexpected (Join-Path $OfflineEvidenceRoot 'unexpected-test');throw 'Unexpected-file rejection failed'}catch{if($_.Exception.Message-eq'Unexpected-file rejection failed'){throw}}
  $missingSource=$Sources['UnrealEditor.modules'];$Sources['UnrealEditor.modules']=Join-Path $OfflineEvidenceRoot 'missing.modules'
  try{Assert-Sources;throw 'Missing-source rejection failed'}catch{if($_.Exception.Message-eq'Missing-source rejection failed'){throw}}finally{$Sources['UnrealEditor.modules']=$missingSource}
  $wrong=$Expected['UnrealEditor.modules'].sha256;$Expected['UnrealEditor.modules'].sha256=('0'*64)
  try{Assert-Sources;throw 'Wrong-hash rejection failed'}catch{if($_.Exception.Message-eq'Wrong-hash rejection failed'){throw}}finally{$Expected['UnrealEditor.modules'].sha256=$wrong}
  $badDescriptor=Join-Path $OfflineEvidenceRoot 'wrong-descriptor.uplugin';Copy-Item $Descriptor $badDescriptor
  $bd=Get-Content -Raw $badDescriptor|ConvertFrom-Json;$bd.Modules[0].Name='WrongModule';[IO.File]::WriteAllText($badDescriptor,($bd|ConvertTo-Json -Depth 20),[Text.UTF8Encoding]::new($false))
  try{Assert-DescriptorPath $badDescriptor;throw 'Descriptor/module rejection failed'}catch{if($_.Exception.Message-eq'Descriptor/module rejection failed'){throw}}
  $badRollback=Join-Path $OfflineEvidenceRoot 'ambiguous_rollback.json';Write-Json $badRollback ([ordered]@{target_was_absent=$false;created_files=@('unknown')})
  $rb=Get-Content -Raw $badRollback|ConvertFrom-Json
  try{Assert-RollbackUnambiguous $rb;throw 'Rollback ambiguity rejection failed'}catch{if($_.Exception.Message-eq'Rollback ambiguity rejection failed'){throw}}
  foreach($p in @($TargetDir,$AttemptRoot,$TerminalManifest,$EmergencyReceipt)){if(Test-Path $p){throw "Governed namespace exists: $p"}}
  $state.preflight_passed=$true;$state.classification='PASS';$exit=0
 }else{
  if(-not$AuthorizeSingleBinding){throw 'Normal mode requires -AuthorizeSingleBinding'}
  foreach($p in @($TargetDir,$AttemptRoot,$TerminalManifest,$EmergencyReceipt)){if(Test-Path $p){throw "Future namespace exists: $p"}}
  $state.preflight_passed=$true;[IO.Directory]::CreateDirectory($AttemptRoot)|Out-Null
  $stage='binding';$state.binding_launch_count=1;Invoke-Binding $TargetDir $AttemptRoot
  $state.copy_count=3;$state.target_created=$true
  $inventory=@(Get-ChildItem $TargetDir -File|ForEach-Object{[ordered]@{path=$_.FullName;bytes=$_.Length;sha256=Get-Sha256 $_.FullName}})
  Write-Json (Join-Path $AttemptRoot 'post_binding_inventory.json') $inventory
  $state.classification='PASSED_READY_FOR_EXPLICIT_RECOVERY05_UNREAL_PROOF_DESIGN';$exit=0
 }
}catch{$state.failure_stage=$stage;$state.failure_message=$_.Exception.Message;$exit=1}
finally{
 $state.ended_utc=[DateTime]::UtcNow.ToString('o')
 try{Write-Json $manifestPath $state}catch{try{$parent=Split-Path -Parent $emergencyPath;if(-not(Test-Path $parent)){[IO.Directory]::CreateDirectory($parent)|Out-Null};[IO.File]::AppendAllText($emergencyPath,((@{classification='FAILED_WITH_EVIDENCE';message=$_.Exception.Message}|ConvertTo-Json -Compress)+[Environment]::NewLine),[Text.UTF8Encoding]::new($false))}catch{};$exit=1}
}
exit([int]$exit)
