[CmdletBinding()]
param(
    [switch]$OfflineContractTest,
    [string]$OfflineEvidenceRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$source = 'D:\Skyguard52\Scripts\ToolchainWave08\environment_visible_kit_presentation_refinement01_recovery01_visual_proof01\invoke_m01_visible_environment_kit_presentation_refinement01_recovery01_visual_proof01_once.ps1'
$expectedBytes = 4878
$expectedSha256 = 'cd0b2ef368bd6caf8108c03bf5d5b636c01a864fd425f25a2619737385e9a4bf'

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

if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { throw "Frozen presentation proof supervisor is missing: $source" }
$item = Get-Item -LiteralPath $source
if ($item.Length -ne $expectedBytes -or (Get-LowerSha256 $source) -ne $expectedSha256) { throw 'Frozen presentation proof supervisor changed' }

$transformed = Get-Content -LiteralPath $source -Raw
$replacements = @(
    @('PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_VISIBLE_ENVIRONMENT_PRESENTATION_REFINEMENT01_RECOVERY01_VISUAL_PROOF01_EXECUTION', 'PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_PHOTOREAL_FOUNDATION_WAVE01_NONVEGETATION01_VISUAL_PROOF01_EXECUTION'),
    @('M01_VISIBLE_ENVIRONMENT_PRESENTATION_REFINEMENT01_RECOVERY01_VISUAL_PROOF01', 'M01_PHOTOREAL_FOUNDATION_WAVE01_NONVEGETATION01_VISUAL_PROOF01'),
    @('M01-VISIBLE-ENVIRONMENT-PRESENTATION-REFINEMENT01-RECOVERY01-VISUAL-PROOF01', 'M01-PHOTOREAL-FOUNDATION-WAVE01-NONVEGETATION01-VISUAL-PROOF01'),
    @('Lvl_M01_VisibleEnvironmentKit02_PresentationRefinement01_Recovery01', 'Lvl_M01_PhotorealFoundation_NonVegetation01'),
    @('M01VisibleEnvironmentPresentationRefinement01Recovery01VisualProof01.csv', 'M01PhotorealFoundationWave01NonVegetation01VisualProof01.csv'),
    @('capture_m01_visible_environment_kit_presentation_refinement01_recovery01_visual_proof01.py', 'capture_m01_photoreal_foundation_nonvegetation01_visual_proof01.py'),
    @('adjudicate_m01_visible_environment_kit_presentation_refinement01_recovery01_visual_proof01_once.py', 'adjudicate_m01_photoreal_foundation_nonvegetation01_visual_proof01_once.py'),
    @('m01_visible_environment_presentation_refinement01_recovery01_visual_proof01', 'm01_photoreal_foundation_wave01_nonvegetation01_visual_proof01'),
    @('environment_visible_kit_presentation_refinement01_recovery01_visual_proof01', 'm01_photoreal_foundation_nonvegetation01_visual_proof01'),
    @('visible-environment-presentation-refinement01-recovery01-visual-proof01', 'photoreal-foundation-wave01-nonvegetation01-visual-proof01')
)
foreach ($pair in $replacements) {
    if (-not $transformed.Contains($pair[0])) { throw "Proof supervisor binding token is absent: $($pair[0])" }
    $transformed = $transformed.Replace($pair[0], $pair[1])
}
foreach ($pair in $replacements) {
    if ($transformed.Contains($pair[0])) { throw "Proof supervisor retained stale token: $($pair[0])" }
}
foreach ($required in @(
    'M01_PHOTOREAL_FOUNDATION_WAVE01_NONVEGETATION01_VISUAL_PROOF01',
    'M01-PHOTOREAL-FOUNDATION-WAVE01-NONVEGETATION01-VISUAL-PROOF01',
    'Lvl_M01_PhotorealFoundation_NonVegetation01',
    'M01PhotorealFoundationWave01NonVegetation01VisualProof01.csv',
    'm01_photoreal_foundation_nonvegetation01_visual_proof01',
    '$timeoutSeconds = 1200'
)) {
    if (-not $transformed.Contains($required)) { throw "Proof supervisor output binding is missing: $required" }
}
if ([regex]::Matches($transformed, [regex]::Escape('Start-Process -FilePath $editor')).Count -ne 1) { throw 'Transformed supervisor must contain exactly one Unreal launch path' }

$global:SkyguardTransformedSupervisorSource = $transformed
$scriptBlock = [ScriptBlock]::Create($transformed)
$arguments = @{}
if ($OfflineContractTest) {
    $arguments['OfflineContractTest'] = $true
    if ($OfflineEvidenceRoot) { $arguments['OfflineEvidenceRoot'] = $OfflineEvidenceRoot }
}
else {
    # Standing authorization removes the need for a fresh user confirmation while
    # retaining the frozen single-launch guard in the proven supervisor.
    $arguments['AuthorizeSingleUnrealProof'] = $true
}
& $scriptBlock @arguments
