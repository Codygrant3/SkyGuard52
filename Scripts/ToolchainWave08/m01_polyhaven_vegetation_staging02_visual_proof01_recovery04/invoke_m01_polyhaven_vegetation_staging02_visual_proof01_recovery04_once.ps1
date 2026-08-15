[CmdletBinding()]
param([switch]$AuthorizeSingleUnrealProof,[switch]$OfflineContractTest,[string]$OfflineEvidenceRoot)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$source='D:\Skyguard52\Scripts\ToolchainWave08\m01_polyhaven_vegetation_staging02_visual_proof01\invoke_m01_polyhaven_vegetation_staging02_visual_proof01_once.ps1'
$expectedBytes=3410
$expectedSha256='31f0ab182d5334029b44d8c6a07cc9f5af9d44ec500fe3154f6200742d421523'
function Get-LowerSha256([string]$Path){$stream=$null;$algorithm=$null;try{$stream=[IO.File]::Open($Path,[IO.FileMode]::Open,[IO.FileAccess]::Read,[IO.FileShare]::Read);$algorithm=[Security.Cryptography.SHA256]::Create();return ([BitConverter]::ToString($algorithm.ComputeHash($stream))).Replace('-','').ToLowerInvariant()}finally{if($null-ne $algorithm){$algorithm.Dispose()};if($null-ne $stream){$stream.Dispose()}}}
if(-not(Test-Path -LiteralPath $source -PathType Leaf)){throw "Frozen Stage02 failed supervisor is missing: $source"}
$item=Get-Item -LiteralPath $source
if($item.Length-ne $expectedBytes-or(Get-LowerSha256 $source)-ne $expectedSha256){throw 'Frozen Stage02 failed supervisor changed'}
try{. $source -OfflineContractTest -OfflineEvidenceRoot $OfflineEvidenceRoot}catch{}
$transformed=$global:SkyguardTransformedSupervisorSource
if([string]::IsNullOrWhiteSpace($transformed)){throw 'Stage02 transformed base supervisor was not exposed'}
$pairs=@(
    @('PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01_EXECUTION','__SG52_READY__'),
    @('M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01','__SG52_UPPER__'),
    @('M01-POLYHAVEN-VEGETATION-STAGING02-VISUAL-PROOF01','__SG52_KEBAB__'),
    @('M01PolyHavenVegetationStaging02VisualProof01.csv','__SG52_CSV__'),
    @('m01_polyhaven_vegetation_staging02_visual_proof01','__SG52_LOWER__'),
    @('polyhaven-vegetation-staging02-visual-proof01','__SG52_LOWER_KEBAB__')
)
foreach($pair in $pairs){if(-not $transformed.Contains($pair[0])){throw "Recovery04 binding token is absent: $($pair[0])"};$transformed=$transformed.Replace($pair[0],$pair[1])}
$pairs=@(
    @('__SG52_READY__','PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01_RECOVERY04_EXECUTION'),
    @('__SG52_UPPER__','M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01_RECOVERY04'),
    @('__SG52_KEBAB__','M01-POLYHAVEN-VEGETATION-STAGING02-VISUAL-PROOF01-RECOVERY04'),
    @('__SG52_CSV__','M01PolyHavenVegetationStaging02VisualProof01Recovery04.csv'),
    @('__SG52_LOWER__','m01_polyhaven_vegetation_staging02_visual_proof01_recovery04'),
    @('__SG52_LOWER_KEBAB__','polyhaven-vegetation-staging02-visual-proof01-recovery04')
)
foreach($pair in $pairs){$transformed=$transformed.Replace($pair[0],$pair[1])}
if($transformed.Contains('RECOVERY04_RECOVERY04')-or $transformed.Contains('recovery04_recovery04')){throw 'Recovery04 duplicate suffix detected'}
if([regex]::Matches($transformed,[regex]::Escape('Start-Process -FilePath $editor')).Count-ne 1){throw 'Recovery04 must contain one Unreal launch'}
$scriptBlock=[ScriptBlock]::Create($transformed);$arguments=@{}
if($AuthorizeSingleUnrealProof){$arguments['AuthorizeSingleUnrealProof']=$true}
if($OfflineContractTest){$arguments['OfflineContractTest']=$true;if($OfflineEvidenceRoot){$arguments['OfflineEvidenceRoot']=$OfflineEvidenceRoot}}
& $scriptBlock @arguments
