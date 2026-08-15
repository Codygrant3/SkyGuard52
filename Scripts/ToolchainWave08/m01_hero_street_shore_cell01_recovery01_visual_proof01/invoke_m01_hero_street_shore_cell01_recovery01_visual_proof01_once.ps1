[CmdletBinding()]
param(
    [switch]$OfflineContractTest,
    [string]$OfflineEvidenceRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$source = 'D:\Skyguard52\Scripts\ToolchainWave08\m01_accepted_candidate_assembly03_recovery01_visual_proof01\invoke_m01_accepted_candidate_assembly03_recovery01_visual_proof01_once.ps1'
$expectedBytes = 4105
$expectedSha256 = '6fc6d8a383feac7e47358db3f309d3117be3c7b372f86b692be6852cae506545'

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

if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { throw "Frozen Assembly03 proof supervisor is missing: $source" }
$item = Get-Item -LiteralPath $source
if ($item.Length -ne $expectedBytes -or (Get-LowerSha256 $source) -ne $expectedSha256) { throw 'Frozen Assembly03 proof supervisor changed' }

$transformed = Get-Content -LiteralPath $source -Raw
$replacements = @(
    @('PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_ACCEPTED_CANDIDATE_ASSEMBLY03_RECOVERY01_VISUAL_PROOF01_EXECUTION', 'PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_HERO_STREET_SHORE_CELL01_RECOVERY01_VISUAL_PROOF01_EXECUTION'),
    @('M01_ACCEPTED_CANDIDATE_ASSEMBLY03_RECOVERY01_VISUAL_PROOF01', 'M01_HERO_STREET_SHORE_CELL01_RECOVERY01_VISUAL_PROOF01'),
    @('M01-ACCEPTED-CANDIDATE-ASSEMBLY03-RECOVERY01-VISUAL-PROOF01', 'M01-HERO-STREET-SHORE-CELL01-RECOVERY01-VISUAL-PROOF01'),
    @('M01AcceptedCandidateAssembly03Recovery01VisualProof01.csv', 'M01HeroStreetShoreCell01Recovery01VisualProof01.csv'),
    @('capture_m01_accepted_candidate_assembly03_recovery01_visual_proof01.py', 'capture_m01_hero_street_shore_cell01_recovery01_visual_proof01.py'),
    @('adjudicate_m01_accepted_candidate_assembly03_recovery01_visual_proof01_once.py', 'adjudicate_m01_hero_street_shore_cell01_recovery01_visual_proof01_once.py'),
    @('m01_accepted_candidate_assembly03_recovery01_visual_proof01', 'm01_hero_street_shore_cell01_recovery01_visual_proof01'),
    @('accepted-candidate-assembly03-recovery01-visual-proof01', 'hero-street-shore-cell01-recovery01-visual-proof01'),
    @('Lvl_M01_AcceptedCandidateAssembly03_Recovery01', 'Lvl_M01_HeroStreetShoreCell01_Recovery01')
)
foreach ($pair in $replacements) {
    if (-not $transformed.Contains($pair[0])) { throw "Cell proof supervisor binding token is absent: $($pair[0])" }
    $transformed = $transformed.Replace($pair[0], $pair[1])
}
if ([regex]::Matches($transformed, [regex]::Escape('Start-Process -FilePath $editor')).Count -ne 1) { throw 'Transformed cell supervisor must contain exactly one Unreal launch path' }
$global:SkyguardTransformedSupervisorSource = $transformed
$scriptBlock = [ScriptBlock]::Create($transformed)
$arguments = @{}
if ($OfflineContractTest) {
    $arguments['OfflineContractTest'] = $true
    if ($OfflineEvidenceRoot) { $arguments['OfflineEvidenceRoot'] = $OfflineEvidenceRoot }
}
& $scriptBlock @arguments
