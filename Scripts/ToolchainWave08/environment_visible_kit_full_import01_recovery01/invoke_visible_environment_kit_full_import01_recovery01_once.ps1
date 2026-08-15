param([switch]$AuthorizeSingleUnreal,[switch]$OfflineContractTest)
$ErrorActionPreference='Stop'
$Original='D:\Skyguard52\Scripts\ToolchainWave08\environment_visible_kit_full_import01\invoke_visible_environment_kit_full_import01_once.ps1'
$ExpectedOriginal='7d7b54b65fb73891c440806b6e04e2f173d8a3b81da5a15ed1ee940e4c96fe3b'
function Get-Sha256([string]$Path){$s=$null;$a=$null;try{$s=[IO.File]::OpenRead($Path);$a=[Security.Cryptography.SHA256]::Create();return([BitConverter]::ToString($a.ComputeHash($s))).Replace('-','').ToLowerInvariant()}finally{if($null-ne$a){$a.Dispose()};if($null-ne$s){$s.Dispose()}}}
if((Get-Sha256 $Original)-ne$ExpectedOriginal){throw 'Frozen FullImport01 supervisor hash mismatch.'}
$Source=[IO.File]::ReadAllText($Original)
$Pattern='(?s)^param\(.*?\)\r?\n'
if([regex]::Matches($Source,$Pattern).Count-ne1){throw 'Expected one leading param block.'}
$Source=[regex]::Replace($Source,$Pattern,'',1)
$Replacements=@(
 @('environment_visible_kit_full_import01\import_visible_environment_kit01.py','environment_visible_kit_full_import01_recovery01\import_visible_environment_kit01_recovery01.py'),
 @('environment_visible_kit_full_import01\verify_visible_environment_kit_full_import01_offline.py','environment_visible_kit_full_import01_recovery01\verify_visible_environment_kit_full_import01_recovery01_offline.py'),
 @('M01VisibleEnvironmentKitFullImport01\execution_contract.json','M01VisibleEnvironmentKitFullImport01Recovery01\execution_contract.json'),
 @('Docs\AAA_Review\M01_VISIBLE_ENVIRONMENT_KIT_IMPORT_REPROBE03_ACCEPTANCE_FREEZE.json','Docs\AAA_Review\M01_VISIBLE_ENVIRONMENT_METADATA_NORMALIZATION02_ACCEPTANCE_FREEZE.json'),
 @('Docs\AAA_Review\M01_VISIBLE_ENVIRONMENT_UNREAL_READY02_ACCEPTANCE_FREEZE.json','Docs\AAA_Review\M01_VISIBLE_ENVIRONMENT_KIT_FULL_IMPORT01_ATTEMPT01_TERMINAL_FREEZE.json'),
 @('VisibleEnvironmentProductionReset01_UnrealReady02\exports','VisibleEnvironmentProductionReset01_UnrealReady02_MetadataNormalized01\exports'),
 @('M01_VISIBLE_ENVIRONMENT_KIT_FULL_IMPORT01\attempt_01','M01_VISIBLE_ENVIRONMENT_KIT_FULL_IMPORT01_RECOVERY01\attempt_01'),
 @('M01_VISIBLE_ENVIRONMENT_KIT_FULL_IMPORT01_TERMINAL_SUPERVISOR','M01_VISIBLE_ENVIRONMENT_KIT_FULL_IMPORT01_RECOVERY01_TERMINAL_SUPERVISOR'),
 @('M01_VISIBLE_ENVIRONMENT_KIT_FULL_IMPORT01_EMERGENCY_RECEIPT','M01_VISIBLE_ENVIRONMENT_KIT_FULL_IMPORT01_RECOVERY01_EMERGENCY_RECEIPT'),
 @('D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\VisibleEnvironmentKit01','D:\SG52T08_ENV01\Content\M01\EnvKit02'),
 @('5db48b5f2862a6406b12534e85137f2a98021058816976f1f2e1f94d5191e3df','a1a7e6d301ce01b540462c8f15dcbb2036c18f566fe1e6c122a72d4f5aee3636'),
 @('831fc50961bf62c834cbc816f60863cfb32b2df8cae0a0fe1f20e4ccd02ecaad','cedf40d5aa7c292605daeb282f70a9ab1ab1e2698177a75e0d9ec8ba86c0990d'),
 @('783ca2f4196a7b41153f1403590f2c3b0ce776ef88e2745544e6ae10ac0c001d','bc0fa66bcdf9c3b0f7750f96ccebfd8a8467c3ed303d2de64c7568bd83e25429'),
 @('ce332b3648c848eaead2c898e27dd215c949758bf46350d15574daa889f29184','f0e6880f7a628960bdf02ef16026b4226d2ed5a78b81933ce10246d51990edbb'),
 @('9f0bce85b5011ca8b002e52fdb651fffe6adcb10f541c74583cc13599199dc20','ac9f4cdc6bcb75bfd93c0ea2b1dd9484543c63ca6d194d9a1a4258b37ad62712'),
 @('SM_M01_Apartment_Production_A_CONSOLIDATED.glb','M01_APARTMENT_A.glb'),
 @('77b04f21f75f97b337eb89d142b5d672d9be5eaaa79184ee9f44421d35e51080','62f117c58a9cbe02e57ffe7ebcdc4d1b7ad7401635ecc5ef0ad1f2f07281b33a'),
 @('SM_M01_CoastalDistrict_Production_A_CONSOLIDATED.glb','M01_COASTAL_DISTRICT_A.glb'),
 @('7c76f069a0f72592b4cdf0928529c1fc35405fa175cea27f5697124313f85c0a','7c42cd930495aa39ef58a4e7f80b02b2b3af7f345f5477bff3130fd0bd6d7b34'),
 @('SM_M01_CornerResidence_Production_C_CONSOLIDATED.glb','M01_CORNER_RESIDENCE_C.glb'),
 @('6c5fe2a8ce70a4dbf0d0bec910261e7eef68183ca6103f3b756c4f0f0065cdb8','809aeb6e36256279320ed7688e81f9f14eb4553b027a711c277309cda6e24702'),
 @('SM_M01_Lighthouse_Production_A_CONSOLIDATED.glb','M01_LIGHTHOUSE_A.glb'),
 @('50e38c728d2497a6689bd352dcc8c4cb3de0e9ab8f2dfb50b5d518680d608301','e0502f12494a031a1187ea85defa11ac8038910301cd0bb4bf743dca17f7ba0a'),
 @('SM_M01_Midrise_Production_B_CONSOLIDATED.glb','M01_MIDRISE_B.glb'),
 @('6c4b22ab84b79510345215772da2649b0cb101089d87336b4604944a74ca3155','5d93c46206631953b8affacee6bb757ef7bab674476276df08b61ff684cbc794'),
 @('skyguard.m01-visible-environment-kit-full-import01.supervisor.v1','skyguard.m01-visible-environment-kit-full-import01-recovery01.supervisor.v1'),
 @('PASSED_FULL_VISIBLE_ENVIRONMENT_KIT_IMPORT_READY_FOR_REVERSIBLE_MAP_ASSEMBLY_DESIGN','PASSED_FULL_VISIBLE_ENVIRONMENT_KIT_IMPORT_RECOVERY01_READY_FOR_REVERSIBLE_MAP_ASSEMBLY')
)
foreach($pair in $Replacements){$old=[string]$pair[0];$new=[string]$pair[1];if(-not$Source.Contains($old)){throw "FullImport Recovery01 binding token absent: $old"};$Source=$Source.Replace($old,$new)}
if($Source.Contains('VisibleEnvironmentKit01')-or$Source.Contains('M01_VISIBLE_ENVIRONMENT_KIT_FULL_IMPORT01\attempt_01')){throw 'Recovery01 supervisor retains a failed namespace.'}
Invoke-Expression $Source
