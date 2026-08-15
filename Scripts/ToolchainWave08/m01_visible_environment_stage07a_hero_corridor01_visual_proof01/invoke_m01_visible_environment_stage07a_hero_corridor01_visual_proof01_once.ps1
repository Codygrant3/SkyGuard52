[CmdletBinding()]
param(
    [switch]$AuthorizeSingleUnrealProof,
    [switch]$OfflineContractTest,
    [string]$OfflineEvidenceRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$source = 'D:\Skyguard52\Scripts\ToolchainWave08\m01_visible_environment_stage06_district_correction01_visual_proof01\invoke_m01_visible_environment_stage06_district_correction01_visual_proof01_once.ps1'
$expectedBytes = 3821
$expectedSha256 = '1b1a0775db26c7f15f45aa3373fb3ddd6321ac63a7e65f47a911d92930b88c9d'

function Get-LowerSha256([string]$Path) {
    $stream = $null; $algorithm = $null
    try {
        $stream = [System.IO.File]::Open($Path, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::Read)
        $algorithm = [System.Security.Cryptography.SHA256]::Create()
        return ([System.BitConverter]::ToString($algorithm.ComputeHash($stream))).Replace('-', '').ToLowerInvariant()
    }
    finally {
        if ($null -ne $algorithm) { $algorithm.Dispose() }
        if ($null -ne $stream) { $stream.Dispose() }
    }
}

if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { throw "Frozen Stage06 proof supervisor is missing: $source" }
$item = Get-Item -LiteralPath $source
if ($item.Length -ne $expectedBytes -or (Get-LowerSha256 $source) -ne $expectedSha256) { throw 'Frozen Stage06 proof supervisor changed' }

try { & $source -OfflineContractTest -OfflineEvidenceRoot $OfflineEvidenceRoot } catch {}
$transformed = $global:SkyguardTransformedSupervisorSource
if ([string]::IsNullOrWhiteSpace($transformed)) { throw 'Transformed Stage06 supervisor unavailable' }

$replacements = @(
    @('PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_VISIBLE_ENVIRONMENT_STAGE06_DISTRICT_CORRECTION01_VISUAL_PROOF01_EXECUTION', 'PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_VISIBLE_ENVIRONMENT_STAGE07A_HERO_CORRIDOR01_VISUAL_PROOF01_EXECUTION'),
    @('M01_VISIBLE_ENVIRONMENT_STAGE06_DISTRICT_CORRECTION01_VISUAL_PROOF01', 'M01_VISIBLE_ENVIRONMENT_STAGE07A_HERO_CORRIDOR01_VISUAL_PROOF01'),
    @('M01-VISIBLE-ENVIRONMENT-STAGE06-DISTRICT-CORRECTION01-VISUAL-PROOF01', 'M01-VISIBLE-ENVIRONMENT-STAGE07A-HERO-CORRIDOR01-VISUAL-PROOF01'),
    @('M01VisibleEnvironmentStage06DistrictCorrection01VisualProof01.csv', 'M01VisibleEnvironmentStage07AHeroCorridor01VisualProof01.csv'),
    @('m01_visible_environment_stage06_district_correction01_visual_proof01', 'm01_visible_environment_stage07a_hero_corridor01_visual_proof01'),
    @('visible-environment-stage06-district-correction01-visual-proof01', 'visible-environment-stage07a-hero-corridor01-visual-proof01'),
    @('Lvl_M01_VisibleEnvironmentStage06DistrictCorrection01', 'Lvl_M01_VisibleEnvironmentStage07AHeroCorridor01')
)
foreach ($pair in $replacements) {
    if (-not $transformed.Contains($pair[0])) { throw "Missing Stage07A proof source token: $($pair[0])" }
    $transformed = $transformed.Replace($pair[0], $pair[1])
}
foreach ($stale in @('M01_VISIBLE_ENVIRONMENT_STAGE06_DISTRICT_CORRECTION01_VISUAL_PROOF01', 'Lvl_M01_VisibleEnvironmentStage06DistrictCorrection01')) {
    if ($transformed.Contains($stale)) { throw "Stage07A proof supervisor retained stale token: $stale" }
}
if ([regex]::Matches($transformed, [regex]::Escape('Start-Process -FilePath $editor')).Count -ne 1) { throw 'Stage07A supervisor must contain exactly one Unreal launch' }
$global:SkyguardTransformedSupervisorSource = $transformed
$block = [ScriptBlock]::Create($transformed)
$arguments = @{}
if ($AuthorizeSingleUnrealProof) { $arguments['AuthorizeSingleUnrealProof'] = $true }
if ($OfflineContractTest) {
    $arguments['OfflineContractTest'] = $true
    if ($OfflineEvidenceRoot) { $arguments['OfflineEvidenceRoot'] = $OfflineEvidenceRoot }
}
& $block @arguments
