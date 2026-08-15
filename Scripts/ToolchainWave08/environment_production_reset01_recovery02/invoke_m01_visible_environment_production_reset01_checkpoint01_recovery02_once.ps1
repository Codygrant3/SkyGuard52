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
 @('environment_production_reset01\build_m01_visible_environment_production_reset01_checkpoint01.py','environment_production_reset01_recovery02\build_m01_visible_environment_production_reset01_checkpoint01_recovery02.py'),
 @('environment_production_reset01\adjudicate_m01_visible_environment_production_reset01_checkpoint01.py','environment_production_reset01_recovery02\adjudicate_m01_visible_environment_production_reset01_checkpoint01_recovery02.py'),
 @('environment_production_reset01\verify_m01_visible_environment_production_reset01_checkpoint01_offline.py','environment_production_reset01_recovery02\verify_m01_visible_environment_production_reset01_checkpoint01_recovery02_offline.py'),
 @('M01VisibleEnvironmentProductionReset01Checkpoint01\execution_contract.json','M01VisibleEnvironmentProductionReset01Checkpoint01Recovery02\execution_contract.json'),
 @('fefa08e50cb9e78d8d5a3965635d8f065df251d8861c777821c2a88d64eaf891','125b89a03a2a89ca1e0f0c87b9791d2807f4e866ef370d58c0051e45ecd597b1'),
 @('7b74c7d08a0918172b064553865dbd9d1868fca4e56f38be5f2e659c4046b440','9171c085805262eec86ed7b3c722ccab0c927f018a4fb51519a682ecbab6288e'),
 @('f81dad2cc122d2708023882701360f0fa9fdcdf1577b57470e690a18e55235db','4218c262f76b7c6a3d4f13e82d8a9b3d645412717609a5328ee95bb93143771e'),
 @('31a497e335fa3ec75de9ad6b0f62dbf6ea61c3fbcf910d08f645c8544e7d351c','5812a1afd9807ab392bc910c1741ce74b2df0a3caf7240dbe370f4ea892758d5'),
 @('VisibleEnvironmentProductionReset01_Checkpoint01','VisibleEnvironmentProductionReset01_Checkpoint01_Recovery02'),
 @('M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_CHECKPOINT01','M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_CHECKPOINT01_RECOVERY02')
)
foreach($pair in $Replacements){$old=[string]$pair[0];$new=[string]$pair[1];if(-not$Source.Contains($old)){throw"Recovery02 binding token absent: $old"};$Source=$Source.Replace($old,$new)}
Invoke-Expression $Source
