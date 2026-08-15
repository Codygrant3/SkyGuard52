[CmdletBinding()]
param(
    [switch]$OfflineContractTest,
    [string]$OfflineEvidenceRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$source = 'D:\Skyguard52\Scripts\ToolchainWave08\m01_photoreal_foundation_lighting_roads_waterline02_visual_proof01\invoke_m01_photoreal_foundation_lighting_roads_waterline02_visual_proof01_once.ps1'
$expectedBytes = 4361
$expectedSha256 = '2fea5006dc12d7121e0794875c0f1c88aa1eb9ff267832adf7149141026ab304'

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

if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { throw "Frozen LightingRoadsWaterline02 proof supervisor is missing: $source" }
$item = Get-Item -LiteralPath $source
if ($item.Length -ne $expectedBytes -or (Get-LowerSha256 $source) -ne $expectedSha256) { throw 'Frozen LightingRoadsWaterline02 proof supervisor changed' }

$transformed = Get-Content -LiteralPath $source -Raw
$replacements = @(
    @('PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_PHOTOREAL_FOUNDATION_WAVE01_LIGHTING_ROADS_WATERLINE02_VISUAL_PROOF01_EXECUTION', 'PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_PHOTOREAL_FOUNDATION_WAVE01_STRUCTURAL_CLEANUP03_VISUAL_PROOF01_EXECUTION'),
    @('M01_PHOTOREAL_FOUNDATION_WAVE01_LIGHTING_ROADS_WATERLINE02_VISUAL_PROOF01', 'M01_PHOTOREAL_FOUNDATION_WAVE01_STRUCTURAL_CLEANUP03_VISUAL_PROOF01'),
    @('M01-PHOTOREAL-FOUNDATION-WAVE01-LIGHTING-ROADS-WATERLINE02-VISUAL-PROOF01', 'M01-PHOTOREAL-FOUNDATION-WAVE01-STRUCTURAL-CLEANUP03-VISUAL-PROOF01'),
    @('Lvl_M01_PhotorealFoundation_LightingRoadsWaterline02', 'Lvl_M01_PhotorealFoundation_StructuralCleanup03'),
    @('M01PhotorealFoundationWave01LightingRoadsWaterline02VisualProof01.csv', 'M01PhotorealFoundationWave01StructuralCleanup03VisualProof01.csv'),
    @('capture_m01_photoreal_foundation_lighting_roads_waterline02_visual_proof01.py', 'capture_m01_photoreal_foundation_structural_cleanup03_visual_proof01.py'),
    @('adjudicate_m01_photoreal_foundation_lighting_roads_waterline02_visual_proof01_once.py', 'adjudicate_m01_photoreal_foundation_structural_cleanup03_visual_proof01_once.py'),
    @('m01_photoreal_foundation_wave01_lighting_roads_waterline02_visual_proof01', 'm01_photoreal_foundation_wave01_structural_cleanup03_visual_proof01'),
    @('m01_photoreal_foundation_lighting_roads_waterline02_visual_proof01', 'm01_photoreal_foundation_structural_cleanup03_visual_proof01'),
    @('photoreal-foundation-wave01-lighting-roads-waterline02-visual-proof01', 'photoreal-foundation-wave01-structural-cleanup03-visual-proof01')
)
foreach ($pair in $replacements) {
    if (-not $transformed.Contains($pair[0])) { throw "Proof supervisor binding token is absent: $($pair[0])" }
    $transformed = $transformed.Replace($pair[0], $pair[1])
}
foreach ($pair in $replacements) {
    if ($transformed.Contains($pair[0])) { throw "Proof supervisor retained stale token: $($pair[0])" }
}
$authorizationPattern = "(?ms)^else \{\r?\n    \`$arguments\['AuthorizeSingleUnrealProof'\] = \`$true\r?\n\}\r?\n& \`$scriptBlock @arguments\s*$"
$authorizationMatches = [regex]::Matches($transformed, $authorizationPattern)
if ($authorizationMatches.Count -ne 1) { throw "Expected exactly one redundant authorization dispatch; found $($authorizationMatches.Count)" }
$transformed = [regex]::Replace($transformed, $authorizationPattern, '& $scriptBlock @arguments')
if ($transformed.Contains("`$arguments['AuthorizeSingleUnrealProof']")) { throw 'Standing-authorized wrapper retained redundant nested authorization dispatch' }
foreach ($required in @(
    'M01_PHOTOREAL_FOUNDATION_WAVE01_STRUCTURAL_CLEANUP03_VISUAL_PROOF01',
    'M01-PHOTOREAL-FOUNDATION-WAVE01-STRUCTURAL-CLEANUP03-VISUAL-PROOF01',
    'Lvl_M01_PhotorealFoundation_StructuralCleanup03',
    'M01PhotorealFoundationWave01StructuralCleanup03VisualProof01.csv',
    'm01_photoreal_foundation_structural_cleanup03_visual_proof01',
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
