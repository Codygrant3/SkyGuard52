[CmdletBinding()]
param(
    [switch]$OfflineContractTest,
    [string]$OfflineEvidenceRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$source = 'D:\Skyguard52\Scripts\ToolchainWave08\m01_coastal_corridor_c06r01_axis_recovery01_visual_proof01_recovery01\invoke_m01_coastal_corridor_c06r01_axis_recovery01_visual_proof01_recovery01_once.ps1'
$expectedBytes = 4099
$expectedSha256 = '9725a4c802bb4502fe284fc3296023ae0d0a415fc847c14f8e3d89ec8e56f1b2'

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

if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { throw "Frozen corridor proof supervisor binder is missing: $source" }
$item = Get-Item -LiteralPath $source
if ($item.Length -ne $expectedBytes -or (Get-LowerSha256 $source) -ne $expectedSha256) { throw 'Frozen corridor proof supervisor binder changed' }

$transformed = Get-Content -LiteralPath $source -Raw
$replacements = @(
    @('PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_COASTAL_CORRIDOR_C06R01_AXIS_RECOVERY01_VISUAL_PROOF01_RECOVERY01_EXECUTION', 'PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_ACCEPTED_CANDIDATE_ASSEMBLY03_RECOVERY01_VISUAL_PROOF01_EXECUTION'),
    @('M01_COASTAL_CORRIDOR_C06R01_AXIS_RECOVERY01_VISUAL_PROOF01_RECOVERY01', 'M01_ACCEPTED_CANDIDATE_ASSEMBLY03_RECOVERY01_VISUAL_PROOF01'),
    @('M01-COASTAL-CORRIDOR-C06R01-AXIS-RECOVERY01-VISUAL-PROOF01-RECOVERY01', 'M01-ACCEPTED-CANDIDATE-ASSEMBLY03-RECOVERY01-VISUAL-PROOF01'),
    @('M01CoastalCorridorC06R01AxisRecovery01VisualProof01Recovery01.csv', 'M01AcceptedCandidateAssembly03Recovery01VisualProof01.csv'),
    @('capture_m01_coastal_corridor_c06r01_axis_recovery01_visual_proof01_recovery01.py', 'capture_m01_accepted_candidate_assembly03_recovery01_visual_proof01.py'),
    @('adjudicate_m01_coastal_corridor_c06r01_axis_recovery01_visual_proof01_recovery01_once.py', 'adjudicate_m01_accepted_candidate_assembly03_recovery01_visual_proof01_once.py'),
    @('m01_coastal_corridor_c06r01_axis_recovery01_visual_proof01_recovery01', 'm01_accepted_candidate_assembly03_recovery01_visual_proof01'),
    @('coastal-corridor-c06r01-axis-recovery01-visual-proof01-recovery01', 'accepted-candidate-assembly03-recovery01-visual-proof01')
)
foreach ($pair in $replacements) {
    if (-not $transformed.Contains($pair[0])) { throw "Assembly03 proof supervisor binding token is absent: $($pair[0])" }
    $transformed = $transformed.Replace($pair[0], $pair[1])
}
foreach ($pair in $replacements) {
    if ($transformed.Contains($pair[0])) { throw "Assembly03 proof supervisor retained stale token: $($pair[0])" }
}
$scriptBlockAnchor = '$scriptBlock = [ScriptBlock]::Create($transformed)'
if ($transformed.IndexOf($scriptBlockAnchor, [System.StringComparison]::Ordinal) -lt 0) { throw 'Inherited supervisor ScriptBlock anchor is absent' }
$mapBinding = '$transformed = $transformed.Replace(''Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01Recovery01'', ''Lvl_M01_AcceptedCandidateAssembly03_Recovery01'')' + [Environment]::NewLine
$transformed = $transformed.Replace($scriptBlockAnchor, $mapBinding + $scriptBlockAnchor)
if ([regex]::Matches($transformed, [regex]::Escape('Start-Process -FilePath $editor')).Count -ne 1) { throw 'Transformed Assembly03 supervisor must contain exactly one Unreal launch path' }
$global:SkyguardTransformedSupervisorSource = $transformed
$scriptBlock = [ScriptBlock]::Create($transformed)
$arguments = @{}
if ($OfflineContractTest) {
    $arguments['OfflineContractTest'] = $true
    if ($OfflineEvidenceRoot) { $arguments['OfflineEvidenceRoot'] = $OfflineEvidenceRoot }
}
& $scriptBlock @arguments
