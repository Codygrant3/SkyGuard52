[CmdletBinding()]
param(
    [switch]$OfflineContractTest,
    [string]$OfflineEvidenceRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$source = 'D:\Skyguard52\Scripts\ToolchainWave08\m01_photoreal_foundation_environment_composition_correction05_recovery02_visual_proof01\invoke_m01_photoreal_foundation_environment_composition_correction05_recovery02_visual_proof01_once.ps1'
$expectedBytes = 4936
$expectedSha256 = 'cbd2c99a548c775728c7b2ad3aae9da1db23ad548b097b9eb9d824115edc776a'

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

if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { throw "Frozen EnvironmentCompositionCorrection05 Recovery02 proof supervisor is missing: $source" }
$item = Get-Item -LiteralPath $source
if ($item.Length -ne $expectedBytes -or (Get-LowerSha256 $source) -ne $expectedSha256) { throw 'Frozen EnvironmentCompositionCorrection05 Recovery02 proof supervisor changed' }

$transformed = Get-Content -LiteralPath $source -Raw
$replacements = @(
    @('PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_PHOTOREAL_FOUNDATION_WAVE01_ENVIRONMENT_COMPOSITION_CORRECTION05_RECOVERY02_VISUAL_PROOF01_EXECUTION', 'PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_COASTAL_CORRIDOR_C06R01_AXIS_RECOVERY01_VISUAL_PROOF01_EXECUTION'),
    @('M01_PHOTOREAL_FOUNDATION_WAVE01_ENVIRONMENT_COMPOSITION_CORRECTION05_RECOVERY02_VISUAL_PROOF01', 'M01_COASTAL_CORRIDOR_C06R01_AXIS_RECOVERY01_VISUAL_PROOF01'),
    @('M01-PHOTOREAL-FOUNDATION-WAVE01-ENVIRONMENT-COMPOSITION-CORRECTION05-RECOVERY02-VISUAL-PROOF01', 'M01-COASTAL-CORRIDOR-C06R01-AXIS-RECOVERY01-VISUAL-PROOF01'),
    @('Lvl_M01_PhotorealFoundation_EnvironmentCompositionCorrection05Recovery02', 'Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01Recovery01'),
    @('M01PhotorealFoundationWave01EnvironmentCompositionCorrection05Recovery02VisualProof01.csv', 'M01CoastalCorridorC06R01AxisRecovery01VisualProof01.csv'),
    @('capture_m01_photoreal_foundation_environment_composition_correction05_recovery02_visual_proof01.py', 'capture_m01_coastal_corridor_c06r01_axis_recovery01_visual_proof01.py'),
    @('adjudicate_m01_photoreal_foundation_environment_composition_correction05_recovery02_visual_proof01_once.py', 'adjudicate_m01_coastal_corridor_c06r01_axis_recovery01_visual_proof01_once.py'),
    @('m01_photoreal_foundation_wave01_environment_composition_correction05_recovery02_visual_proof01', 'm01_coastal_corridor_c06r01_axis_recovery01_visual_proof01'),
    @('m01_photoreal_foundation_environment_composition_correction05_recovery02_visual_proof01', 'm01_coastal_corridor_c06r01_axis_recovery01_visual_proof01'),
    @('photoreal-foundation-wave01-environment-composition-correction05-recovery02-visual-proof01', 'coastal-corridor-c06r01-axis-recovery01-visual-proof01')
)
foreach ($pair in $replacements) {
    if (-not $transformed.Contains($pair[0])) { throw "Proof supervisor binding token is absent: $($pair[0])" }
    $transformed = $transformed.Replace($pair[0], $pair[1])
}
foreach ($pair in $replacements) {
    if ($transformed.Contains($pair[0])) { throw "Proof supervisor retained stale token: $($pair[0])" }
}
foreach ($required in @(
    'M01_COASTAL_CORRIDOR_C06R01_AXIS_RECOVERY01_VISUAL_PROOF01',
    'M01-COASTAL-CORRIDOR-C06R01-AXIS-RECOVERY01-VISUAL-PROOF01',
    'Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01Recovery01',
    'M01CoastalCorridorC06R01AxisRecovery01VisualProof01.csv',
    'm01_coastal_corridor_c06r01_axis_recovery01_visual_proof01',
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
