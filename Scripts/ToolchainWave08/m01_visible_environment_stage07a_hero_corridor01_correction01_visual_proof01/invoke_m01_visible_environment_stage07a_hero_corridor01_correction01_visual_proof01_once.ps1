[CmdletBinding()]
param(
    [switch]$AuthorizeSingleUnrealProof,
    [switch]$OfflineContractTest,
    [string]$OfflineEvidenceRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$source = 'D:\Skyguard52\Scripts\ToolchainWave08\m01_visible_environment_stage07a_hero_corridor01_visual_proof01\invoke_m01_visible_environment_stage07a_hero_corridor01_visual_proof01_once.ps1'
$expectedBytes = 3756
$expectedSha256 = '0be79dd9b2fe11ad526cb3a80d55da804839c7ff89b21401a1a801d3a71805a3'

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

if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { throw "Frozen Stage07A proof supervisor is missing: $source" }
$item = Get-Item -LiteralPath $source
if ($item.Length -ne $expectedBytes -or (Get-LowerSha256 $source) -ne $expectedSha256) { throw 'Frozen Stage07A proof supervisor changed' }

try { & $source -OfflineContractTest -OfflineEvidenceRoot $OfflineEvidenceRoot } catch {}
$transformed = $global:SkyguardTransformedSupervisorSource
if ([string]::IsNullOrWhiteSpace($transformed)) { throw 'Transformed Stage07A supervisor unavailable' }

$replacements = @(
    @('PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_VISIBLE_ENVIRONMENT_STAGE07A_HERO_CORRIDOR01_VISUAL_PROOF01_EXECUTION', 'PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_VISIBLE_ENVIRONMENT_STAGE07A_HERO_CORRIDOR01_CORRECTION01_VISUAL_PROOF01_EXECUTION'),
    @('M01_VISIBLE_ENVIRONMENT_STAGE07A_HERO_CORRIDOR01_VISUAL_PROOF01', 'M01_VISIBLE_ENVIRONMENT_STAGE07A_HERO_CORRIDOR01_CORRECTION01_VISUAL_PROOF01'),
    @('M01-VISIBLE-ENVIRONMENT-STAGE07A-HERO-CORRIDOR01-VISUAL-PROOF01', 'M01-VISIBLE-ENVIRONMENT-STAGE07A-HERO-CORRIDOR01-CORRECTION01-VISUAL-PROOF01'),
    @('M01VisibleEnvironmentStage07AHeroCorridor01VisualProof01.csv', 'M01VisibleEnvironmentStage07AHeroCorridor01Correction01VisualProof01.csv'),
    @('m01_visible_environment_stage07a_hero_corridor01_visual_proof01', 'm01_visible_environment_stage07a_hero_corridor01_correction01_visual_proof01'),
    @('visible-environment-stage07a-hero-corridor01-visual-proof01', 'visible-environment-stage07a-hero-corridor01-correction01-visual-proof01'),
    @('Lvl_M01_VisibleEnvironmentStage07AHeroCorridor01', 'Lvl_M01_VisibleEnvironmentStage07AHeroCorridor01Correction01')
)
foreach ($pair in $replacements) {
    if (-not $transformed.Contains($pair[0])) { throw "Missing Correction01 proof token: $($pair[0])" }
    $transformed = $transformed.Replace($pair[0], $pair[1])
}
$oldContractCheck = "    `$freeze = Assert-JsonObject `$offlineFreeze`r`n    `$binding = Assert-JsonObject `$bindingFreeze`r`n    if (`$freeze.classification -ne 'PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_VISIBLE_ENVIRONMENT_STAGE07A_HERO_CORRIDOR01_CORRECTION01_VISUAL_PROOF01_EXECUTION') { throw 'Offline freeze classification mismatch' }`r`n    if (`$binding.classification -ne 'PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_VISIBLE_ENVIRONMENT_STAGE07A_HERO_CORRIDOR01_CORRECTION01_VISUAL_PROOF01_EXECUTION') { throw 'Binding freeze classification mismatch' }`r`n    foreach (`$record in @(`$freeze.members) + @(`$binding.members)) {"
$newContractCheck = "    `$freeze = Assert-JsonObject `$offlineFreeze`r`n    `$binding = Assert-JsonObject `$bindingFreeze`r`n    if (`$freeze.classification -ne 'PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_VISIBLE_ENVIRONMENT_STAGE07A_HERO_CORRIDOR01_CORRECTION01_VISUAL_PROOF01_EXECUTION') { throw 'Offline freeze classification mismatch' }`r`n    if (`$binding.classification -ne 'PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_VISIBLE_ENVIRONMENT_STAGE07A_HERO_CORRIDOR01_CORRECTION01_VISUAL_PROOF01_EXECUTION') { throw 'Binding freeze classification mismatch' }`r`n    foreach (`$record in @(`$freeze.members)) {"
if (-not $transformed.Contains($oldContractCheck)) { throw 'Correction01 inherited freeze-member anchor changed' }
$transformed = $transformed.Replace($oldContractCheck, $newContractCheck)
if ([regex]::Matches($transformed, [regex]::Escape('Start-Process -FilePath $editor')).Count -ne 1) { throw 'Correction01 supervisor must contain exactly one Unreal launch' }
$global:SkyguardTransformedSupervisorSource = $transformed
$block = [ScriptBlock]::Create($transformed)
$arguments = @{}
if ($AuthorizeSingleUnrealProof) { $arguments['AuthorizeSingleUnrealProof'] = $true }
if ($OfflineContractTest) {
    $arguments['OfflineContractTest'] = $true
    if ($OfflineEvidenceRoot) { $arguments['OfflineEvidenceRoot'] = $OfflineEvidenceRoot }
}
& $block @arguments
