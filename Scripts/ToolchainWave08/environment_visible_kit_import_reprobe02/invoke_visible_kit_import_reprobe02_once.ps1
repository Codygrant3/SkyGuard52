param([switch]$AuthorizeSingleUnreal,[switch]$OfflineContractTest)
$ErrorActionPreference='Stop'
$Original='D:\Skyguard52\Scripts\ToolchainWave08\environment_visible_kit_import_probe01\invoke_visible_kit_import_probe01_once.ps1'
$ExpectedOriginal='eab53e136c16b0c3d9e35067f2711ca7f0c7d72d0d85bb20bf0e3745133da9ef'
function Get-Sha256([string]$Path){$s=$null;$a=$null;try{$s=[IO.File]::OpenRead($Path);$a=[Security.Cryptography.SHA256]::Create();return([BitConverter]::ToString($a.ComputeHash($s))).Replace('-','').ToLowerInvariant()}finally{if($null-ne$a){$a.Dispose()};if($null-ne$s){$s.Dispose()}}}
if((Get-Sha256 $Original)-ne$ExpectedOriginal){throw 'Frozen ImportProbe01 supervisor hash mismatch.'}
$Source=[IO.File]::ReadAllText($Original)
$Pattern='(?s)^param\(.*?\)\r?\n'
if([regex]::Matches($Source,$Pattern).Count-ne1){throw 'Expected one leading param block.'}
$Source=[regex]::Replace($Source,$Pattern,'',1)
if(([regex]::Matches($Source,'throw"')).Count-ne8){throw 'Expected eight inherited throw-spacing defects.'}
$Source=$Source.Replace('throw"','throw "')
$Replacements=@(
 @('environment_visible_kit_import_probe01\probe_visible_kit_import01.py','environment_visible_kit_import_reprobe02\probe_visible_kit_import_reprobe02.py'),
 @('environment_visible_kit_import_probe01\verify_visible_kit_import_probe01_offline.py','environment_visible_kit_import_reprobe02\verify_visible_kit_import_reprobe02_offline.py'),
 @('M01VisibleEnvironmentKitImportProbe01\execution_contract.json','M01VisibleEnvironmentKitImportReprobe02\execution_contract.json'),
 @('Docs\AAA_Review\M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_CHECKPOINT02_ACCEPTANCE_FREEZE.json','Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentProductionReset01_UnrealReady01_MetadataNormalized01\metadata_normalization_receipt.json'),
 @('Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentProductionReset01_Checkpoint02\exports\SM_M01_Apartment_Production_A.glb','Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentProductionReset01_UnrealReady01_MetadataNormalized01\exports\SM_M01_Apartment_Production_A_UNREAL_READY.glb'),
 @('20cf9b0fd2a2d8a9b60939b5b63a29527d66569d695b01c6dc9620b04d3d1955','411f7093f1a3376056838a7c171eac746f032fd04488cb8082664386606f5532'),
 @('ce3b54cd5c29c117ab9711aa766d6adc6bb39ffbc7d30a8e4a69c864acf7516a','005f7887ab0f7f6499cb0026259c9878ae6c15abeee55d25ee9fca14c8ca2e33'),
 @('be6e48531050f08d5fda3c278c88484446e19b16ca32772e26057b75db3b92ca','e6f2e9ee43fdb86f048cac8769348ecab90fc75362530de1194728f467e43d62'),
 @('efc54d13040f45efbabcb9e55d99754be161c15fc80804e5ea30440deb368284','2f057979659d29d5b83fa0fd4540d61433f8de0c805a536a630807ba72dec44a'),
 @('5c09c9eb7bf17057ec277b958165005e71e3ecac6a9430df47eddeceab9a7849','c1ecb14007710c4aaa4dd0c363177cba6ea4411eeeae495b56ca2e89a0f5e09a'),
 @('VisibleKitImportProbe01','VisibleKitImportReprobe02'),
 @('M01_VISIBLE_ENVIRONMENT_KIT_IMPORT_PROBE01','M01_VISIBLE_ENVIRONMENT_KIT_IMPORT_REPROBE02'),
 @('visible-environment-kit-import-probe01','visible-environment-kit-import-reprobe02'),
 @('PASSED_VISIBLE_KIT_IMPORT_PROBE_READY_FOR_FULL_INTEGRATION_DESIGN','PASSED_CONSOLIDATED_IMPORT_REPROBE_READY_FOR_FULL_KIT_IMPORT_DESIGN')
)
foreach($pair in $Replacements){$old=[string]$pair[0];$new=[string]$pair[1];if(-not$Source.Contains($old)){throw "ImportReprobe02 binding token absent: $old"};$Source=$Source.Replace($old,$new)}
if($Source.Contains('throw"')){throw 'Recovery02 still contains an invalid throw expression.'}
Invoke-Expression $Source
