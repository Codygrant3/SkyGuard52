[CmdletBinding()]
param([switch]$AuthorizeSingleUnrealProof, [switch]$OfflineContractTest, [string]$OfflineEvidenceRoot)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$source = 'D:\Skyguard52\Scripts\ToolchainWave08\m01_visible_environment_stage07a_hero_corridor01_correction01_visual_proof01\invoke_m01_visible_environment_stage07a_hero_corridor01_correction01_visual_proof01_once.ps1'
$expectedBytes = 5003
$expectedSha256 = '87840e9a3afd8477ca5d0b11ae1409bd127edcc9b72f02f1eab4bb03bfa63f1d'

function Get-LowerSha256([string]$Path) {
    $stream=$null;$algorithm=$null
    try {$stream=[IO.File]::OpenRead($Path);$algorithm=[Security.Cryptography.SHA256]::Create();return ([BitConverter]::ToString($algorithm.ComputeHash($stream))).Replace('-','').ToLowerInvariant()}
    finally {if($null-ne$algorithm){$algorithm.Dispose()};if($null-ne$stream){$stream.Dispose()}}
}
if(-not(Test-Path -LiteralPath $source -PathType Leaf)){throw 'Frozen failed-attempt supervisor missing'}
$item=Get-Item -LiteralPath $source
if($item.Length-ne$expectedBytes-or(Get-LowerSha256 $source)-ne$expectedSha256){throw 'Frozen failed-attempt supervisor changed'}
try {& $source -OfflineContractTest -OfflineEvidenceRoot $OfflineEvidenceRoot} catch {}
$transformed=$global:SkyguardTransformedSupervisorSource
if([string]::IsNullOrWhiteSpace($transformed)){throw 'Correction01 transformed supervisor unavailable'}

$replacements=@(
 @('M01_VISIBLE_ENVIRONMENT_STAGE07A_HERO_CORRIDOR01_CORRECTION01_VISUAL_PROOF01','M01_VISIBLE_ENVIRONMENT_STAGE07A_HERO_CORRIDOR01_CORRECTION01_VISUAL_PROOF01_RECOVERY01'),
 @('M01-VISIBLE-ENVIRONMENT-STAGE07A-HERO-CORRIDOR01-CORRECTION01-VISUAL-PROOF01','M01-VISIBLE-ENVIRONMENT-STAGE07A-HERO-CORRIDOR01-CORRECTION01-VISUAL-PROOF01-RECOVERY01'),
 @('M01VisibleEnvironmentStage07AHeroCorridor01Correction01VisualProof01.csv','M01VisibleEnvironmentStage07AHeroCorridor01Correction01VisualProof01Recovery01.csv'),
 @('m01_visible_environment_stage07a_hero_corridor01_correction01_visual_proof01','m01_visible_environment_stage07a_hero_corridor01_correction01_visual_proof01_recovery01'),
 @('visible-environment-stage07a-hero-corridor01-correction01-visual-proof01','visible-environment-stage07a-hero-corridor01-correction01-visual-proof01-recovery01')
)
foreach($pair in $replacements){if(-not$transformed.Contains($pair[0])){throw "Recovery01 supervisor token absent: $($pair[0])"};$transformed=$transformed.Replace($pair[0],$pair[1])}
$old="    foreach (`$record in @(`$freeze.members) + @(`$binding.members)) {"
$new="    foreach (`$record in @(`$freeze.members)) {"
if($transformed.Contains($old)) {
    $transformed=$transformed.Replace($old,$new)
}
elseif(-not$transformed.Contains($new)) {
    throw 'Recovery01 inherited binding-member contract changed'
}
if([regex]::Matches($transformed,[regex]::Escape('Start-Process -FilePath $editor')).Count-ne1){throw 'Recovery01 must contain exactly one Unreal launch'}
$global:SkyguardTransformedSupervisorSource=$transformed
$block=[ScriptBlock]::Create($transformed)
$arguments=@{}
if($AuthorizeSingleUnrealProof){$arguments.AuthorizeSingleUnrealProof=$true}
if($OfflineContractTest){$arguments.OfflineContractTest=$true;if($OfflineEvidenceRoot){$arguments.OfflineEvidenceRoot=$OfflineEvidenceRoot}}
& $block @arguments
