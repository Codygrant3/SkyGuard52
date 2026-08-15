param([switch]$AuthorizeSingleUnrealPreview, [switch]$OfflineContractTest)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$Base = 'D:\Skyguard52\Scripts\GrokProduction\invoke_m01_window_recovery06_unrealready01_mapped_preview01_recovery01_once.ps1'
$BaseSha256 = 'b27cbfd163922636146d114f1da0aabd323a95870d3e3a72ce99beba1da0c80d'
$PriorFreeze = 'D:\Skyguard52\Docs\AAA_Review\M01_WINDOW_RECOVERY06_UNREALREADY01_MAPPED_PREVIEW01_RECOVERY01_ATTEMPT01_TERMINAL_FREEZE.json'
$PriorFreezeSha256 = '020b9d899b171588350e01514ee9d4110d608d06d24d6a96f8811b0804fba029'

function Get-Sha256([string]$Path){$s=$null;$h=$null;try{$s=[IO.File]::Open($Path,[IO.FileMode]::Open,[IO.FileAccess]::Read,[IO.FileShare]::Read);$h=[Security.Cryptography.SHA256]::Create();return([BitConverter]::ToString($h.ComputeHash($s))).Replace('-','').ToLowerInvariant()}finally{if($null-ne$h){$h.Dispose()};if($null-ne$s){$s.Dispose()}}}

if(-not(Test-Path -LiteralPath $Base -PathType Leaf)-or(Get-Sha256 $Base)-ne$BaseSha256){throw 'Frozen Recovery01 supervisor changed'}
if(-not(Test-Path -LiteralPath $PriorFreeze -PathType Leaf)-or(Get-Sha256 $PriorFreeze)-ne$PriorFreezeSha256){throw 'Recovery01 terminal freeze changed'}

$source=Get-Content -LiteralPath $Base -Raw
$source=$source.Replace('RECOVERY01','RECOVERY02').Replace('Recovery01','Recovery02').Replace('recovery01','recovery02')
$source=$source.Replace('GW02PreviewR01','GW02PreviewR02')
$source=$source.Replace(
    "`$FailedFreeze=Join-Path `$Root 'Docs\AAA_Review\M01_WINDOW_RECOVERY06_UNREALREADY01_MAPPED_PREVIEW01_ATTEMPT01_TERMINAL_FREEZE.json'",
    "`$FailedFreeze=Join-Path `$Root 'Docs\AAA_Review\M01_WINDOW_RECOVERY06_UNREALREADY01_MAPPED_PREVIEW01_RECOVERY01_ATTEMPT01_TERMINAL_FREEZE.json'"
)
$source=$source.Replace(
    "`$Executor='2b4d8c5ecdfd017cea50edff4c7e4bf44e5f33a5e95a6378890103b5a17c4f29'",
    "`$Executor='73d0bfcc45f287c27e0f79f04c3f92fe69be1384bbfec80fe6f8faf7cae0e943'"
)
$source=$source.Replace(
    "`$FailedFreeze='ad8bd030855536b5c43872a5cfa19a63104bea060e7b90a086deb697ef235f8a'",
    "`$FailedFreeze='020b9d899b171588350e01514ee9d4110d608d06d24d6a96f8811b0804fba029'"
)
if([regex]::Matches($source,'Start-Process -FilePath \$Editor').Count-ne1){throw 'Derived Recovery02 supervisor launch count changed'}
foreach($required in @('mapped_preview01_recovery02.py','MAPPED_PREVIEW01_RECOVERY02','GW02PreviewR02','PASSED_RECOVERY02_AUTOMATIC_AWAITING_DIRECT_VISUAL_REVIEW')){if($source-notmatch[regex]::Escape($required)){throw "Derived Recovery02 supervisor correction missing: $required"}}

$derived=[scriptblock]::Create($source)
& $derived -AuthorizeSingleUnrealPreview:$AuthorizeSingleUnrealPreview -OfflineContractTest:$OfflineContractTest
