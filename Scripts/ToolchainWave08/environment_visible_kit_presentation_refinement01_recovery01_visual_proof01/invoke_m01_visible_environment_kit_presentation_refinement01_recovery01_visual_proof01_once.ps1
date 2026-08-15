[CmdletBinding()]
param(
    [switch]$AuthorizeSingleUnrealProof,
    [switch]$OfflineContractTest,
    [string]$OfflineEvidenceRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$source = 'D:\Skyguard52\Scripts\ToolchainWave08\environment_visible_kit_map_visual_remediation01_recovery01_visual_proof01\invoke_m01_visible_environment_kit_map_visual_remediation01_recovery01_visual_proof01_once.ps1'
$expectedBytes = 5983
$expectedSha256 = 'bc9e70c58c95f71d59b21eb594a75f957fc884ed13e864e3931a244af752bed5'

function Get-LowerSha256([string]$Path) {
    $stream = $null
    $algorithm = $null
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

if (-not (Test-Path -LiteralPath $source -PathType Leaf)) {
    throw "Frozen remediated-map proof supervisor is missing: $source"
}
$item = Get-Item -LiteralPath $source
if ($item.Length -ne $expectedBytes -or (Get-LowerSha256 $source) -ne $expectedSha256) {
    throw 'Frozen remediated-map proof supervisor changed'
}

$transformed = Get-Content -LiteralPath $source -Raw
$replacements = @(
    @('PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_VISIBLE_ENVIRONMENT_KIT_MAP_VISUAL_REMEDIATION01_RECOVERY01_VISUAL_PROOF01_EXECUTION', 'PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_VISIBLE_ENVIRONMENT_PRESENTATION_REFINEMENT01_RECOVERY01_VISUAL_PROOF01_EXECUTION'),
    @('M01_VISIBLE_ENVIRONMENT_KIT_MAP_VISUAL_REMEDIATION01_RECOVERY01_VISUAL_PROOF01', 'M01_VISIBLE_ENVIRONMENT_PRESENTATION_REFINEMENT01_RECOVERY01_VISUAL_PROOF01'),
    @('M01-VISIBLE-ENVIRONMENT-KIT-MAP-VISUAL-REMEDIATION01-RECOVERY01-VISUAL-PROOF01', 'M01-VISIBLE-ENVIRONMENT-PRESENTATION-REFINEMENT01-RECOVERY01-VISUAL-PROOF01'),
    @('Lvl_M01_VisibleEnvironmentKit02_VisualRemediation01_Recovery01', 'Lvl_M01_VisibleEnvironmentKit02_PresentationRefinement01_Recovery01'),
    @('M01VisibleEnvironmentKitMapVisualRemediation01Recovery01VisualProof01.csv', 'M01VisibleEnvironmentPresentationRefinement01Recovery01VisualProof01.csv'),
    @('capture_m01_visible_environment_kit_map_visual_remediation01_recovery01_visual_proof01.py', 'capture_m01_visible_environment_kit_presentation_refinement01_recovery01_visual_proof01.py'),
    @('adjudicate_m01_visible_environment_kit_map_visual_remediation01_recovery01_visual_proof01_once.py', 'adjudicate_m01_visible_environment_kit_presentation_refinement01_recovery01_visual_proof01_once.py'),
    @('m01_visible_environment_kit_map_visual_remediation01_recovery01_visual_proof01', 'm01_visible_environment_presentation_refinement01_recovery01_visual_proof01'),
    @('environment_visible_kit_map_visual_remediation01_recovery01_visual_proof01', 'environment_visible_kit_presentation_refinement01_recovery01_visual_proof01'),
    @('visible-environment-kit-map-visual-remediation01-recovery01-visual-proof01', 'visible-environment-presentation-refinement01-recovery01-visual-proof01')
)
foreach ($pair in $replacements) {
    if (-not $transformed.Contains($pair[0])) {
        throw "Presentation-proof supervisor binding token is absent: $($pair[0])"
    }
    $transformed = $transformed.Replace($pair[0], $pair[1])
}
foreach ($pair in $replacements) {
    if ($transformed.Contains($pair[0])) {
        throw "Presentation-proof supervisor retained stale token: $($pair[0])"
    }
}
foreach ($required in @(
    'M01_VISIBLE_ENVIRONMENT_PRESENTATION_REFINEMENT01_RECOVERY01_VISUAL_PROOF01',
    'M01-VISIBLE-ENVIRONMENT-PRESENTATION-REFINEMENT01-RECOVERY01-VISUAL-PROOF01',
    'Lvl_M01_VisibleEnvironmentKit02_PresentationRefinement01_Recovery01',
    'M01VisibleEnvironmentPresentationRefinement01Recovery01VisualProof01.csv',
    'environment_visible_kit_presentation_refinement01_recovery01_visual_proof01',
    '$timeoutSeconds = 1200'
)) {
    if (-not $transformed.Contains($required)) {
        throw "Presentation-proof supervisor output binding is missing: $required"
    }
}
if ([regex]::Matches($transformed, [regex]::Escape('Start-Process -FilePath $editor')).Count -ne 1) {
    throw 'Transformed supervisor must contain exactly one Unreal launch path'
}

$global:SkyguardTransformedSupervisorSource = $transformed
$scriptBlock = [ScriptBlock]::Create($transformed)
$arguments = @{}
if ($AuthorizeSingleUnrealProof) { $arguments['AuthorizeSingleUnrealProof'] = $true }
if ($OfflineContractTest) { $arguments['OfflineContractTest'] = $true }
if ($OfflineEvidenceRoot) { $arguments['OfflineEvidenceRoot'] = $OfflineEvidenceRoot }
& $scriptBlock @arguments
