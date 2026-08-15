param([switch]$AuthorizeSingleUnrealPreview, [switch]$OfflineContractTest)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$Base = 'D:\Skyguard52\Scripts\GrokProduction\invoke_m01_window_recovery06_unrealready01_mapped_preview01_recovery01_once.ps1'
$BaseSha256 = 'b27cbfd163922636146d114f1da0aabd323a95870d3e3a72ce99beba1da0c80d'
$PriorFreeze = 'D:\Skyguard52\Docs\AAA_Review\M01_WINDOW_RECOVERY06_UNREALREADY01_MAPPED_PREVIEW01_RECOVERY02_ATTEMPT01_TERMINAL_FREEZE.json'
$PriorFreezeSha256 = '4a4eddf078d4164b15128ba51e3c8e76bcb617a74e25c345d19e3d8e0316da81'

function Get-Sha256([string]$Path){$s=$null;$h=$null;try{$s=[IO.File]::Open($Path,[IO.FileMode]::Open,[IO.FileAccess]::Read,[IO.FileShare]::Read);$h=[Security.Cryptography.SHA256]::Create();return([BitConverter]::ToString($h.ComputeHash($s))).Replace('-','').ToLowerInvariant()}finally{if($null-ne$h){$h.Dispose()};if($null-ne$s){$s.Dispose()}}}
if(-not(Test-Path -LiteralPath $Base -PathType Leaf)-or(Get-Sha256 $Base)-ne$BaseSha256){throw 'Frozen Recovery01 supervisor changed'}
if(-not(Test-Path -LiteralPath $PriorFreeze -PathType Leaf)-or(Get-Sha256 $PriorFreeze)-ne$PriorFreezeSha256){throw 'Recovery02 terminal freeze changed'}

$source=Get-Content -LiteralPath $Base -Raw
$source=$source.Replace('RECOVERY01','RECOVERY03').Replace('Recovery01','Recovery03').Replace('recovery01','recovery03')
$source=$source.Replace('GW02PreviewR01','GW02PreviewR03')
$source=$source.Replace(
    "`$FailedFreeze=Join-Path `$Root 'Docs\AAA_Review\M01_WINDOW_RECOVERY06_UNREALREADY01_MAPPED_PREVIEW01_ATTEMPT01_TERMINAL_FREEZE.json'",
    "`$FailedFreeze=Join-Path `$Root 'Docs\AAA_Review\M01_WINDOW_RECOVERY06_UNREALREADY01_MAPPED_PREVIEW01_RECOVERY02_ATTEMPT01_TERMINAL_FREEZE.json'"
)
$source=$source.Replace(
    "`$Executor='2b4d8c5ecdfd017cea50edff4c7e4bf44e5f33a5e95a6378890103b5a17c4f29'",
    "`$Executor='d37b93cc0cb9fc055203b0f10d8ed176845e6c813d3b0f68520ffeb990368081'"
)
$source=$source.Replace(
    "`$FailedFreeze='ad8bd030855536b5c43872a5cfa19a63104bea060e7b90a086deb697ef235f8a'",
    "`$FailedFreeze='4a4eddf078d4164b15128ba51e3c8e76bcb617a74e25c345d19e3d8e0316da81'"
)
if([regex]::Matches($source,'Start-Process -FilePath \$Editor').Count-ne1){throw 'Derived Recovery03 supervisor launch count changed'}
foreach($required in @('mapped_preview01_recovery03.py','MAPPED_PREVIEW01_RECOVERY03','GW02PreviewR03','PASSED_RECOVERY03_AUTOMATIC_AWAITING_DIRECT_VISUAL_REVIEW')){if($source-notmatch[regex]::Escape($required)){throw "Derived Recovery03 supervisor correction missing: $required"}}
$derived=[scriptblock]::Create($source)
& $derived -AuthorizeSingleUnrealPreview:$AuthorizeSingleUnrealPreview -OfflineContractTest:$OfflineContractTest
