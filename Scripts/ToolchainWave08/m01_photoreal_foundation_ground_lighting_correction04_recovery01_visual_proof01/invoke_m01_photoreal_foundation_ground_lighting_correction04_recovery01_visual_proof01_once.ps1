[CmdletBinding()]
param(
    [switch]$OfflineContractTest,
    [string]$OfflineEvidenceRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$source = 'D:\Skyguard52\Scripts\ToolchainWave08\m01_photoreal_foundation_structural_cleanup03_visual_proof01\invoke_m01_photoreal_foundation_structural_cleanup03_visual_proof01_once.ps1'
$expectedBytes = 4985
$expectedSha256 = '3e21413fd4da7858dc2d74233aeb4702c6500bd8972f01843c8081976ab7bc8c'

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

if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { throw "Frozen StructuralCleanup03 proof supervisor is missing: $source" }
$item = Get-Item -LiteralPath $source
if ($item.Length -ne $expectedBytes -or (Get-LowerSha256 $source) -ne $expectedSha256) { throw 'Frozen StructuralCleanup03 proof supervisor changed' }

$transformed = Get-Content -LiteralPath $source -Raw
$replacements = @(
    @('PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_PHOTOREAL_FOUNDATION_WAVE01_STRUCTURAL_CLEANUP03_VISUAL_PROOF01_EXECUTION', 'PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_PHOTOREAL_FOUNDATION_WAVE01_GROUND_LIGHTING_CORRECTION04_RECOVERY01_VISUAL_PROOF01_EXECUTION'),
    @('M01_PHOTOREAL_FOUNDATION_WAVE01_STRUCTURAL_CLEANUP03_VISUAL_PROOF01', 'M01_PHOTOREAL_FOUNDATION_WAVE01_GROUND_LIGHTING_CORRECTION04_RECOVERY01_VISUAL_PROOF01'),
    @('M01-PHOTOREAL-FOUNDATION-WAVE01-STRUCTURAL-CLEANUP03-VISUAL-PROOF01', 'M01-PHOTOREAL-FOUNDATION-WAVE01-GROUND-LIGHTING-CORRECTION04-RECOVERY01-VISUAL-PROOF01'),
    @('Lvl_M01_PhotorealFoundation_StructuralCleanup03', 'Lvl_M01_PhotorealFoundation_GroundLightingCorrection04Recovery01'),
    @('M01PhotorealFoundationWave01StructuralCleanup03VisualProof01.csv', 'M01PhotorealFoundationWave01GroundLightingCorrection04Recovery01VisualProof01.csv'),
    @('capture_m01_photoreal_foundation_structural_cleanup03_visual_proof01.py', 'capture_m01_photoreal_foundation_ground_lighting_correction04_recovery01_visual_proof01.py'),
    @('adjudicate_m01_photoreal_foundation_structural_cleanup03_visual_proof01_once.py', 'adjudicate_m01_photoreal_foundation_ground_lighting_correction04_recovery01_visual_proof01_once.py'),
    @('m01_photoreal_foundation_wave01_structural_cleanup03_visual_proof01', 'm01_photoreal_foundation_wave01_ground_lighting_correction04_recovery01_visual_proof01'),
    @('m01_photoreal_foundation_structural_cleanup03_visual_proof01', 'm01_photoreal_foundation_ground_lighting_correction04_recovery01_visual_proof01'),
    @('photoreal-foundation-wave01-structural-cleanup03-visual-proof01', 'photoreal-foundation-wave01-ground-lighting-correction04-recovery01-visual-proof01')
)
foreach ($pair in $replacements) {
    if (-not $transformed.Contains($pair[0])) { throw "Proof supervisor binding token is absent: $($pair[0])" }
    $transformed = $transformed.Replace($pair[0], $pair[1])
}
foreach ($pair in $replacements) {
    if ($transformed.Contains($pair[0])) { throw "Proof supervisor retained stale token: $($pair[0])" }
}
foreach ($required in @(
    'M01_PHOTOREAL_FOUNDATION_WAVE01_GROUND_LIGHTING_CORRECTION04_RECOVERY01_VISUAL_PROOF01',
    'M01-PHOTOREAL-FOUNDATION-WAVE01-GROUND-LIGHTING-CORRECTION04-RECOVERY01-VISUAL-PROOF01',
    'Lvl_M01_PhotorealFoundation_GroundLightingCorrection04Recovery01',
    'M01PhotorealFoundationWave01GroundLightingCorrection04Recovery01VisualProof01.csv',
    'm01_photoreal_foundation_ground_lighting_correction04_recovery01_visual_proof01',
    '$timeoutSeconds = 1200'
)) {
    if (-not $transformed.Contains($required)) { throw "Proof supervisor output binding is missing: $required" }
}
if ([regex]::Matches($transformed, [regex]::Escape('Start-Process -FilePath $editor')).Count -ne 1) { throw 'Transformed supervisor must contain exactly one Unreal launch path' }

$scriptBlock = [ScriptBlock]::Create($transformed)
$arguments = @{}
if ($OfflineContractTest) {
    $arguments['OfflineContractTest'] = $true
    if ($OfflineEvidenceRoot) { $arguments['OfflineEvidenceRoot'] = $OfflineEvidenceRoot }
}
& $scriptBlock @arguments
