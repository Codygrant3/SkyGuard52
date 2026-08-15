param([switch]$AuthorizeSingleUnreal,[switch]$OfflineContractTest)
$ErrorActionPreference='Stop'
$Original='D:\Skyguard52\Scripts\ToolchainWave08\environment_visible_kit_map_visual_remediation01\invoke_m01_visible_environment_kit_map_visual_remediation01_once.ps1'
$ExpectedOriginal='4a4d1a548499abb0366a36410767f0d7d9d55ceb9aa4d62634adcee368229f39'
function Get-Sha256([string]$Path){$s=$null;$a=$null;try{$s=[IO.File]::OpenRead($Path);$a=[Security.Cryptography.SHA256]::Create();return([BitConverter]::ToString($a.ComputeHash($s))).Replace('-','').ToLowerInvariant()}finally{if($null-ne$a){$a.Dispose()};if($null-ne$s){$s.Dispose()}}}
if((Get-Sha256 $Original)-ne$ExpectedOriginal){throw 'Frozen VisualRemediation01 supervisor hash mismatch.'}
$Source=[IO.File]::ReadAllText($Original)
$Pattern='(?s)^param\(.*?\)\r?\n'
if([regex]::Matches($Source,$Pattern).Count-ne1){throw 'Expected one leading param block.'}
$Source=[regex]::Replace($Source,$Pattern,'',1)
$Replacements=@(
 @('environment_visible_kit_map_visual_remediation01\author_m01_visible_environment_kit_map_visual_remediation01.py','environment_visible_kit_map_visual_remediation01_recovery01\author_m01_visible_environment_kit_map_visual_remediation01_recovery01.py'),
 @('environment_visible_kit_map_visual_remediation01\verify_m01_visible_environment_kit_map_visual_remediation01_offline.py','environment_visible_kit_map_visual_remediation01_recovery01\verify_m01_visible_environment_kit_map_visual_remediation01_recovery01_offline.py'),
 @('M01VisibleEnvironmentKitMapVisualRemediation01\execution_contract.json','M01VisibleEnvironmentKitMapVisualRemediation01Recovery01\execution_contract.json'),
 @('Lvl_M01_VisibleEnvironmentKit02_VisualRemediation01.umap','Lvl_M01_VisibleEnvironmentKit02_VisualRemediation01_Recovery01.umap'),
 @('M01_VISIBLE_ENVIRONMENT_KIT_MAP_VISUAL_REMEDIATION01\attempt_01','M01_VISIBLE_ENVIRONMENT_KIT_MAP_VISUAL_REMEDIATION01_RECOVERY01\attempt_01'),
 @('M01_VISIBLE_ENVIRONMENT_KIT_MAP_VISUAL_REMEDIATION01_TERMINAL_SUPERVISOR','M01_VISIBLE_ENVIRONMENT_KIT_MAP_VISUAL_REMEDIATION01_RECOVERY01_TERMINAL_SUPERVISOR'),
 @('M01_VISIBLE_ENVIRONMENT_KIT_MAP_VISUAL_REMEDIATION01_EMERGENCY_RECEIPT','M01_VISIBLE_ENVIRONMENT_KIT_MAP_VISUAL_REMEDIATION01_RECOVERY01_EMERGENCY_RECEIPT'),
 @('517044b54109fd951b4135594f47cc514047fd60e43254435c1e30913cbce0d2','78dcf27d1b503a1434f121a600315f7c91c55d949223aa155501bd9cbea72171'),
 @('23ccacb3f6c6ae4bbb3e9555cf5629bd8c0fc93092795994b3e1d0921290864a','bfa514ac1a2e5b63ed208439c647a53c55cfb0c8c78d89483e188b5f391b7984'),
 @('d0b191b81a86d5ddf576852870070f9c58ffea70ac95f6db233f69ff88eb208b','9d7d439446d549685595541f2e229644d90927ce9e6cebb56ef096f053c76067'),
 @('lower_hemisphere_is_solid_color','lower_hemisphere_is_black'),
 @('PASSED_M01_VISIBLE_ENVIRONMENT_KIT_MAP_VISUAL_REMEDIATION01_AUTOMATIC','PASSED_M01_VISIBLE_ENVIRONMENT_KIT_MAP_VISUAL_REMEDIATION01_RECOVERY01_AUTOMATIC'),
 @('PASSED_M01_VISIBLE_ENVIRONMENT_KIT_MAP_VISUAL_REMEDIATION01_READY_FOR_MAPPED_VISUAL_PROOF','PASSED_M01_VISIBLE_ENVIRONMENT_KIT_MAP_VISUAL_REMEDIATION01_RECOVERY01_READY_FOR_MAPPED_VISUAL_PROOF'),
 @('skyguard.m01-visible-environment-kit-map-visual-remediation01.supervisor.v1','skyguard.m01-visible-environment-kit-map-visual-remediation01-recovery01.supervisor.v1')
)
foreach($pair in $Replacements){$old=[string]$pair[0];$new=[string]$pair[1];if(([regex]::Matches($Source,[regex]::Escape($old))).Count-ne1){throw "Recovery01 supervisor binding count changed: $old"};$Source=$Source.Replace($old,$new)}
$FailureVariable="`$FailedRemediationFreeze=Join-Path `$Root 'Docs\AAA_Review\M01_VISIBLE_ENVIRONMENT_KIT_MAP_VISUAL_REMEDIATION01_ATTEMPT01_TERMINAL_FREEZE.json'`n"
$VariableAnchor="`$FailedVisualFreeze=Join-Path `$Root 'Docs\AAA_Review\M01_VISIBLE_ENVIRONMENT_KIT_MAP_VISUAL_PROOF01_ATTEMPT01_TERMINAL_FREEZE.json'`n"
if(-not$Source.Contains($VariableAnchor)){throw 'Recovery01 failed-attempt variable anchor absent.'}
$Source=$Source.Replace($VariableAnchor,$VariableAnchor+$FailureVariable)
$ExpectedAnchor="`$Expected=[ordered]@{`n"
$FailureEntry=" `$FailedRemediationFreeze='e13134fdfaefdf8e471599c0238eed12898e43cf038dc1f685cdda188d26662b'`n"
if(-not$Source.Contains($ExpectedAnchor)){throw 'Recovery01 expected-authority anchor absent.'}
$Source=$Source.Replace($ExpectedAnchor,$ExpectedAnchor+$FailureEntry)
if($Source.Contains('M01_VISIBLE_ENVIRONMENT_KIT_MAP_VISUAL_REMEDIATION01\attempt_01')-or$Source.Contains('Lvl_M01_VisibleEnvironmentKit02_VisualRemediation01.umap')){throw 'Recovery01 supervisor retains a failed namespace.'}
Invoke-Expression $Source
