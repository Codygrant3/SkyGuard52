param([switch]$AuthorizeSingleBlender,[switch]$OfflineContractTest)
$ErrorActionPreference='Stop'
$Original='D:\Skyguard52\Scripts\ToolchainWave08\environment_production_reset01\invoke_m01_visible_environment_production_reset01_checkpoint01_once.ps1'
$ExpectedOriginal='6055ce2bed9036a0da0cc21adbef4bcf3679a30dd59b45ef6fd0610e8da47820'
function Get-Sha256([string]$Path){$s=$null;$a=$null;try{$s=[IO.File]::OpenRead($Path);$a=[Security.Cryptography.SHA256]::Create();return([BitConverter]::ToString($a.ComputeHash($s))).Replace('-','').ToLowerInvariant()}finally{if($null-ne$a){$a.Dispose()};if($null-ne$s){$s.Dispose()}}}
if((Get-Sha256 $Original)-ne$ExpectedOriginal){throw'Frozen Checkpoint01 supervisor hash mismatch.'}
$Source=[IO.File]::ReadAllText($Original)
$Pattern='(?s)^param\(.*?\)\r?\n\r?\n'
if([regex]::Matches($Source,$Pattern).Count-ne1){throw'Expected one leading param block.'}
$Source=[regex]::Replace($Source,$Pattern,'',1)
$Replacements=@(
 @('environment_production_reset01\build_m01_visible_environment_production_reset01_checkpoint01.py','environment_production_reset01_checkpoint02\build_m01_visible_environment_production_reset01_checkpoint02.py'),
 @('environment_production_reset01\adjudicate_m01_visible_environment_production_reset01_checkpoint01.py','environment_production_reset01_checkpoint02\adjudicate_m01_visible_environment_production_reset01_checkpoint02.py'),
 @('environment_production_reset01\verify_m01_visible_environment_production_reset01_checkpoint01_offline.py','environment_production_reset01_checkpoint02\verify_m01_visible_environment_production_reset01_checkpoint02_offline.py'),
 @('M01VisibleEnvironmentProductionReset01Checkpoint01\execution_contract.json','M01VisibleEnvironmentProductionReset01Checkpoint02\execution_contract.json'),
 @('fefa08e50cb9e78d8d5a3965635d8f065df251d8861c777821c2a88d64eaf891','d93a9bd59cbe0a1c95f13ca195d4ede0d3709170c3285066481161b3800e7920'),
 @('7b74c7d08a0918172b064553865dbd9d1868fca4e56f38be5f2e659c4046b440','edf8d959731b10f509f89ef231b5078125cc0986cdfac39cd9555c23f6241cdb'),
 @('f81dad2cc122d2708023882701360f0fa9fdcdf1577b57470e690a18e55235db','1cb6b0121c0238e0e47e203ac690e538c17a6c641e59ced9a41aef97c226ad9c'),
 @('31a497e335fa3ec75de9ad6b0f62dbf6ea61c3fbcf910d08f645c8544e7d351c','3a02047e5facc9e002e3801d54da6a4c98cace17a7d3d37e03a2b650ff0d7e9a'),
 @('VisibleEnvironmentProductionReset01_Checkpoint01','VisibleEnvironmentProductionReset01_Checkpoint02'),
 @('M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_CHECKPOINT01','M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_CHECKPOINT02')
)
foreach($pair in $Replacements){$old=[string]$pair[0];$new=[string]$pair[1];if(-not$Source.Contains($old)){throw"Checkpoint02 binding token absent: $old"};$Source=$Source.Replace($old,$new)}
Invoke-Expression $Source
