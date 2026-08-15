[CmdletBinding()]
param(
    [switch]$OfflineContractTest,
    [string]$OfflineEvidenceRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$source = 'D:\Skyguard52\Scripts\ToolchainWave08\m01_hero_street_shore_cell01_recovery01_visual_proof01\invoke_m01_hero_street_shore_cell01_recovery01_visual_proof01_once.ps1'
$expectedBytes = 3385
$expectedSha256 = '59f24a27c0a455a401d0475560e8f8d61235984ee1bdec02ab1da48df9aa7cf3'

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

if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { throw "Frozen Cell01 proof supervisor is missing: $source" }
$item = Get-Item -LiteralPath $source
if ($item.Length -ne $expectedBytes -or (Get-LowerSha256 $source) -ne $expectedSha256) { throw 'Frozen Cell01 proof supervisor changed' }

$transformed = Get-Content -LiteralPath $source -Raw
$replacements = @(
    @('PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_HERO_STREET_SHORE_CELL01_RECOVERY01_VISUAL_PROOF01_EXECUTION', 'PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_HERO_STREET_SHORE_CELL02_VISUAL_PROOF01_EXECUTION'),
    @('M01_HERO_STREET_SHORE_CELL01_RECOVERY01_VISUAL_PROOF01', 'M01_HERO_STREET_SHORE_CELL02_VISUAL_PROOF01'),
    @('M01-HERO-STREET-SHORE-CELL01-RECOVERY01-VISUAL-PROOF01', 'M01-HERO-STREET-SHORE-CELL02-VISUAL-PROOF01'),
    @('M01HeroStreetShoreCell01Recovery01VisualProof01.csv', 'M01HeroStreetShoreCell02VisualProof01.csv'),
    @('capture_m01_hero_street_shore_cell01_recovery01_visual_proof01.py', 'capture_m01_hero_street_shore_cell02_visual_proof01.py'),
    @('adjudicate_m01_hero_street_shore_cell01_recovery01_visual_proof01_once.py', 'adjudicate_m01_hero_street_shore_cell02_visual_proof01_once.py'),
    @('m01_hero_street_shore_cell01_recovery01_visual_proof01', 'm01_hero_street_shore_cell02_visual_proof01'),
    @('hero-street-shore-cell01-recovery01-visual-proof01', 'hero-street-shore-cell02-visual-proof01'),
    @('Lvl_M01_HeroStreetShoreCell01_Recovery01', 'Lvl_M01_HeroStreetShoreCell02')
)
foreach ($pair in $replacements) {
    if (-not $transformed.Contains($pair[0])) { throw "Cell02 proof supervisor binding token is absent: $($pair[0])" }
    $transformed = $transformed.Replace($pair[0], $pair[1])
}
if ([regex]::Matches($transformed, [regex]::Escape('Start-Process -FilePath $editor')).Count -ne 1) { throw 'Transformed Cell02 supervisor must contain exactly one Unreal launch path' }
$global:SkyguardTransformedSupervisorSource = $transformed
$scriptBlock = [ScriptBlock]::Create($transformed)
$arguments = @{}
if ($OfflineContractTest) {
    $arguments['OfflineContractTest'] = $true
    if ($OfflineEvidenceRoot) { $arguments['OfflineEvidenceRoot'] = $OfflineEvidenceRoot }
}
& $scriptBlock @arguments
