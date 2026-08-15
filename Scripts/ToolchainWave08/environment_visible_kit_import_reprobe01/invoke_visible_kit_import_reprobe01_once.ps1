param([switch]$AuthorizeSingleUnreal,[switch]$OfflineContractTest)
$ErrorActionPreference='Stop'
$Original='D:\Skyguard52\Scripts\ToolchainWave08\environment_visible_kit_import_probe01\invoke_visible_kit_import_probe01_once.ps1'
$ExpectedOriginal='eab53e136c16b0c3d9e35067f2711ca7f0c7d72d0d85bb20bf0e3745133da9ef'
function Get-Sha256([string]$Path){$s=$null;$a=$null;try{$s=[IO.File]::OpenRead($Path);$a=[Security.Cryptography.SHA256]::Create();return([BitConverter]::ToString($a.ComputeHash($s))).Replace('-','').ToLowerInvariant()}finally{if($null-ne$a){$a.Dispose()};if($null-ne$s){$s.Dispose()}}}
if((Get-Sha256 $Original)-ne$ExpectedOriginal){throw'Frozen ImportProbe01 supervisor hash mismatch.'}
$Source=[IO.File]::ReadAllText($Original)
$Pattern='(?s)^param\(.*?\)\r?\n'
if([regex]::Matches($Source,$Pattern).Count-ne1){throw'Expected one leading param block.'}
$Source=[regex]::Replace($Source,$Pattern,'',1)
$Replacements=@(
 @('environment_visible_kit_import_probe01\probe_visible_kit_import01.py','environment_visible_kit_import_reprobe01\probe_visible_kit_import_reprobe01.py'),
 @('environment_visible_kit_import_probe01\verify_visible_kit_import_probe01_offline.py','environment_visible_kit_import_reprobe01\verify_visible_kit_import_reprobe01_offline.py'),
 @('M01VisibleEnvironmentKitImportProbe01\execution_contract.json','M01VisibleEnvironmentKitImportReprobe01\execution_contract.json'),
 @('Docs\AAA_Review\M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_CHECKPOINT02_ACCEPTANCE_FREEZE.json','Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentProductionReset01_UnrealReady01_MetadataNormalized01\metadata_normalization_receipt.json'),
 @('Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentProductionReset01_Checkpoint02\exports\SM_M01_Apartment_Production_A.glb','Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentProductionReset01_UnrealReady01_MetadataNormalized01\exports\SM_M01_Apartment_Production_A_UNREAL_READY.glb'),
 @('20cf9b0fd2a2d8a9b60939b5b63a29527d66569d695b01c6dc9620b04d3d1955','689fd92b6b01f81f9e13c569940cf30d6e6f32b3e15a92e51282db1715b81033'),
 @('ce3b54cd5c29c117ab9711aa766d6adc6bb39ffbc7d30a8e4a69c864acf7516a','a2dee0bb0852f5b6c21674715130625f58b8e42da791964cdd29e2a555c2023d'),
 @('be6e48531050f08d5fda3c278c88484446e19b16ca32772e26057b75db3b92ca','344d6000757341f55a19f258508b686d8d4f3d37631049bd48b36db41a678831'),
 @('efc54d13040f45efbabcb9e55d99754be161c15fc80804e5ea30440deb368284','2f057979659d29d5b83fa0fd4540d61433f8de0c805a536a630807ba72dec44a'),
 @('5c09c9eb7bf17057ec277b958165005e71e3ecac6a9430df47eddeceab9a7849','c1ecb14007710c4aaa4dd0c363177cba6ea4411eeeae495b56ca2e89a0f5e09a'),
 @('VisibleKitImportProbe01','VisibleKitImportReprobe01'),
 @('M01_VISIBLE_ENVIRONMENT_KIT_IMPORT_PROBE01','M01_VISIBLE_ENVIRONMENT_KIT_IMPORT_REPROBE01'),
 @('visible-environment-kit-import-probe01','visible-environment-kit-import-reprobe01'),
 @('PASSED_VISIBLE_KIT_IMPORT_PROBE_READY_FOR_FULL_INTEGRATION_DESIGN','PASSED_CONSOLIDATED_IMPORT_REPROBE_READY_FOR_FULL_KIT_IMPORT_DESIGN')
)
foreach($pair in $Replacements){$old=[string]$pair[0];$new=[string]$pair[1];if(-not$Source.Contains($old)){throw"ImportReprobe01 binding token absent: $old"};$Source=$Source.Replace($old,$new)}
Invoke-Expression $Source
