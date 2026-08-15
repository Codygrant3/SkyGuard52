[CmdletBinding()]
param(
    [switch]$OfflineContractTest,
    [string]$OfflineEvidenceRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$source = 'D:\Skyguard52\Scripts\ToolchainWave08\m01_coastal_corridor_c06r01_axis_recovery01_visual_proof01\invoke_m01_coastal_corridor_c06r01_axis_recovery01_visual_proof01_once.ps1'
$expectedBytes = 4586
$expectedSha256 = '6599ab27c752e03d46a6f24f7c64f9b8f4aa8e55b91b3d1bbc502e3fff60e899'

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

if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { throw "Frozen corridor Axis Recovery01 proof supervisor is missing: $source" }
$item = Get-Item -LiteralPath $source
if ($item.Length -ne $expectedBytes -or (Get-LowerSha256 $source) -ne $expectedSha256) { throw 'Frozen corridor Axis Recovery01 proof supervisor changed' }

$transformed = Get-Content -LiteralPath $source -Raw
$replacements = @(
    @('PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_COASTAL_CORRIDOR_C06R01_AXIS_RECOVERY01_VISUAL_PROOF01_EXECUTION', 'PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_COASTAL_CORRIDOR_C06R01_AXIS_RECOVERY01_VISUAL_PROOF01_RECOVERY01_EXECUTION'),
    @('M01_COASTAL_CORRIDOR_C06R01_AXIS_RECOVERY01_VISUAL_PROOF01', 'M01_COASTAL_CORRIDOR_C06R01_AXIS_RECOVERY01_VISUAL_PROOF01_RECOVERY01'),
    @('M01-COASTAL-CORRIDOR-C06R01-AXIS-RECOVERY01-VISUAL-PROOF01', 'M01-COASTAL-CORRIDOR-C06R01-AXIS-RECOVERY01-VISUAL-PROOF01-RECOVERY01'),
    @('M01CoastalCorridorC06R01AxisRecovery01VisualProof01.csv', 'M01CoastalCorridorC06R01AxisRecovery01VisualProof01Recovery01.csv'),
    @('capture_m01_coastal_corridor_c06r01_axis_recovery01_visual_proof01.py', 'capture_m01_coastal_corridor_c06r01_axis_recovery01_visual_proof01_recovery01.py'),
    @('adjudicate_m01_coastal_corridor_c06r01_axis_recovery01_visual_proof01_once.py', 'adjudicate_m01_coastal_corridor_c06r01_axis_recovery01_visual_proof01_recovery01_once.py'),
    @('m01_coastal_corridor_c06r01_axis_recovery01_visual_proof01', 'm01_coastal_corridor_c06r01_axis_recovery01_visual_proof01_recovery01'),
    @('coastal-corridor-c06r01-axis-recovery01-visual-proof01', 'coastal-corridor-c06r01-axis-recovery01-visual-proof01-recovery01')
)
foreach ($pair in $replacements) {
    $oldLiteral = "'$($pair[0])'"
    $newLiteral = "'$($pair[1])'"
    if (-not $transformed.Contains($oldLiteral)) { throw "Proof supervisor Recovery01 binding token is absent: $($pair[0])" }
    $transformed = $transformed.Replace($oldLiteral, $newLiteral)
}
foreach ($pair in $replacements) {
    if ($transformed.Contains("'$($pair[0])'")) { throw "Proof supervisor Recovery01 retained stale token: $($pair[0])" }
}
foreach ($required in @(
    'M01_COASTAL_CORRIDOR_C06R01_AXIS_RECOVERY01_VISUAL_PROOF01_RECOVERY01',
    'M01-COASTAL-CORRIDOR-C06R01-AXIS-RECOVERY01-VISUAL-PROOF01-RECOVERY01',
    'M01CoastalCorridorC06R01AxisRecovery01VisualProof01Recovery01.csv',
    'm01_coastal_corridor_c06r01_axis_recovery01_visual_proof01_recovery01',
    '$timeoutSeconds = 1200'
)) {
    if (-not $transformed.Contains($required)) { throw "Proof supervisor Recovery01 output binding is missing: $required" }
}
if ([regex]::Matches($transformed, [regex]::Escape('Start-Process -FilePath $editor')).Count -ne 1) { throw 'Transformed Recovery01 supervisor must contain exactly one Unreal launch path' }

$scriptBlock = [ScriptBlock]::Create($transformed)
$arguments = @{}
if ($OfflineContractTest) {
    $arguments['OfflineContractTest'] = $true
    if ($OfflineEvidenceRoot) { $arguments['OfflineEvidenceRoot'] = $OfflineEvidenceRoot }
}
& $scriptBlock @arguments
