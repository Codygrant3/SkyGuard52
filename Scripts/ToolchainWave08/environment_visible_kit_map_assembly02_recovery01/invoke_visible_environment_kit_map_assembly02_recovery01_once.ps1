param([switch]$AuthorizeSingleUnreal,[switch]$OfflineContractTest)
$ErrorActionPreference='Stop'
$Original='D:\Skyguard52\Scripts\ToolchainWave08\environment_visible_kit_map_assembly02\invoke_visible_environment_kit_map_assembly02_once.ps1'
$ExpectedOriginal='d2b5a01a1127b6987fc371adca337648d2ebed8856d2660dddb3d0ed19bae02a'
function Get-Sha256([string]$Path){$s=$null;$a=$null;try{$s=[IO.File]::OpenRead($Path);$a=[Security.Cryptography.SHA256]::Create();return([BitConverter]::ToString($a.ComputeHash($s))).Replace('-','').ToLowerInvariant()}finally{if($null-ne$a){$a.Dispose()};if($null-ne$s){$s.Dispose()}}}
if((Get-Sha256 $Original)-ne$ExpectedOriginal){throw 'Frozen MapAssembly02 supervisor hash mismatch.'}
$Source=[IO.File]::ReadAllText($Original)
$Pattern='(?s)^param\(.*?\)\r?\n'
if([regex]::Matches($Source,$Pattern).Count-ne1){throw 'Expected one leading param block.'}
$Source=[regex]::Replace($Source,$Pattern,'',1)
$Replacements=@(
 @('environment_visible_kit_map_assembly02\author_visible_environment_kit_map_assembly02.py','environment_visible_kit_map_assembly02_recovery01\author_visible_environment_kit_map_assembly02_recovery01.py'),
 @('environment_visible_kit_map_assembly02\verify_visible_environment_kit_map_assembly02_offline.py','environment_visible_kit_map_assembly02_recovery01\verify_visible_environment_kit_map_assembly02_recovery01_offline.py'),
 @('M01VisibleEnvironmentKitMapAssembly02\execution_contract.json','M01VisibleEnvironmentKitMapAssembly02Recovery01\execution_contract.json'),
 @('M01_VISIBLE_ENVIRONMENT_KIT_MAP_ASSEMBLY02\attempt_01','M01_VISIBLE_ENVIRONMENT_KIT_MAP_ASSEMBLY02_RECOVERY01\attempt_01'),
 @('M01_VISIBLE_ENVIRONMENT_KIT_MAP_ASSEMBLY02_TERMINAL_SUPERVISOR','M01_VISIBLE_ENVIRONMENT_KIT_MAP_ASSEMBLY02_RECOVERY01_TERMINAL_SUPERVISOR'),
 @('M01_VISIBLE_ENVIRONMENT_KIT_MAP_ASSEMBLY02_EMERGENCY_RECEIPT','M01_VISIBLE_ENVIRONMENT_KIT_MAP_ASSEMBLY02_RECOVERY01_EMERGENCY_RECEIPT'),
 @('D:\SG52T08_ENV01\Content\M01\Lvl_M01_VisibleEnvironmentKit02.umap','D:\SG52T08_ENV01\Content\M01\Lvl_M01_VisibleEnvironmentKit02_Recovery01.umap'),
 @('3c8d3f1f4d36193c4c24bcdec352a6bce56706f258e45e6c7d3b49bf0f5113f7','444282fd5483852c20c7ada375c9b578be673bb7fdb67b0c76b3d9232df76de2'),
 @('c58c45aa79a690a3990b30bcde72216ec57f82c13c0aaed03e23ba087feabd0f','773328da16ae55a449f63ed211a372f4740d0c982b842ecb752c8fc92013b8ba'),
 @('23f38c2c9148f511c7bc3dc679aea716c84bf551b73ceebf8f36b888089d32a7','2d332e389189d94d21206a5713f3260b1549d29281d16439d2ba23df6d9aa16f'),
 @('skyguard.m01-visible-environment-kit-map-assembly02.supervisor.v1','skyguard.m01-visible-environment-kit-map-assembly02-recovery01.supervisor.v1'),
 @('PASSED_M01_VISIBLE_ENVIRONMENT_KIT_MAP_ASSEMBLY02_AUTOMATIC','PASSED_M01_VISIBLE_ENVIRONMENT_KIT_MAP_ASSEMBLY02_RECOVERY01_AUTOMATIC'),
 @('PASSED_M01_VISIBLE_ENVIRONMENT_KIT_MAP_ASSEMBLY02_READY_FOR_MAPPED_VISUAL_PROOF','PASSED_M01_VISIBLE_ENVIRONMENT_KIT_MAP_ASSEMBLY02_RECOVERY01_READY_FOR_MAPPED_VISUAL_PROOF')
)
foreach($pair in $Replacements){$old=[string]$pair[0];$new=[string]$pair[1];if(-not$Source.Contains($old)){throw "Recovery01 binding token absent: $old"};$Source=$Source.Replace($old,$new)}
$FailedVariable="$"+'FailedAttemptFreeze=Join-Path $Root ''Docs\AAA_Review\M01_VISIBLE_ENVIRONMENT_KIT_MAP_ASSEMBLY02_ATTEMPT01_TERMINAL_FREEZE.json''' + "`n"
$Anchor="$"+'Authorization=Join-Path $Root ''Production\standing_heavy_process_authorization.json''' + "`n"
if(-not$Source.Contains($Anchor)){throw 'Recovery01 failed-freeze variable anchor absent.'}
$Source=$Source.Replace($Anchor,$Anchor+$FailedVariable)
$ExpectedAnchor="$"+'Expected=[ordered]@{' + "`n"
$FailedEntry=' $FailedAttemptFreeze=''e5b1ac566c0ca57fe9e97049ffd8f764a56a8c28c895c634df60bade509e8b6d''' + "`n"
if(-not$Source.Contains($ExpectedAnchor)){throw 'Recovery01 expected-authority anchor absent.'}
$Source=$Source.Replace($ExpectedAnchor,$ExpectedAnchor+$FailedEntry)
if($Source.Contains('M01_VISIBLE_ENVIRONMENT_KIT_MAP_ASSEMBLY02\attempt_01')-or$Source.Contains('Lvl_M01_VisibleEnvironmentKit02.umap')){throw 'Recovery01 supervisor retains a failed namespace.'}
Invoke-Expression $Source
