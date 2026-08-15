[CmdletBinding()]
param(
    [switch]$AuthorizeSingleUnrealProof,
    [switch]$OfflineContractTest,
    [string]$OfflineEvidenceRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$source = 'D:\Skyguard52\Scripts\ToolchainWave08\m01_visible_environment_stage04_recovery03_visual_proof01_recovery01\invoke_m01_visible_environment_stage04_recovery03_visual_proof01_recovery01_once.ps1'
$expectedBytes = 3610
$expectedSha256 = '1efd02ced4354acc1ec04635d4179ae87faa795a0d097ee6d4630d079bec4ab4'

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

if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { throw "Frozen Stage04 Recovery01 proof supervisor is missing: $source" }
$item = Get-Item -LiteralPath $source
if ($item.Length -ne $expectedBytes -or (Get-LowerSha256 $source) -ne $expectedSha256) { throw 'Frozen Stage04 Recovery01 proof supervisor changed' }

try { & $source -OfflineContractTest -OfflineEvidenceRoot $OfflineEvidenceRoot } catch {}
$transformed = $global:SkyguardTransformedSupervisorSource
if ([string]::IsNullOrWhiteSpace($transformed)) { throw 'Transformed Stage04 Recovery01 supervisor unavailable' }
$pairs = @(
    @('PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_VISIBLE_ENVIRONMENT_STAGE04_RECOVERY03_VISUAL_PROOF01_RECOVERY01_EXECUTION', '__READY__'),
    @('M01_VISIBLE_ENVIRONMENT_STAGE04_RECOVERY03_VISUAL_PROOF01_RECOVERY01', '__UPPER__'),
    @('M01-VISIBLE-ENVIRONMENT-STAGE04-RECOVERY03-VISUAL-PROOF01-RECOVERY01', '__KEBAB__'),
    @('M01VisibleEnvironmentStage04Recovery03VisualProof01Recovery01.csv', '__CSV__'),
    @('m01_visible_environment_stage04_recovery03_visual_proof01_recovery01', '__LOWER__'),
    @('visible-environment-stage04-recovery03-visual-proof01-recovery01', '__LOWER_KEBAB__'),
    @('Lvl_M01_VisibleEnvironmentStage04Recovery03', '__MAP__')
)
foreach ($pair in $pairs) {
    if (-not $transformed.Contains($pair[0])) { throw "Missing Stage05 proof source token: $($pair[0])" }
    $transformed = $transformed.Replace($pair[0], $pair[1])
}
$pairs = @(
    @('__READY__', 'PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_VISIBLE_ENVIRONMENT_STAGE05_COMPOSITION01_RECOVERY01_VISUAL_PROOF01_EXECUTION'),
    @('__UPPER__', 'M01_VISIBLE_ENVIRONMENT_STAGE05_COMPOSITION01_RECOVERY01_VISUAL_PROOF01'),
    @('__KEBAB__', 'M01-VISIBLE-ENVIRONMENT-STAGE05-COMPOSITION01-RECOVERY01-VISUAL-PROOF01'),
    @('__CSV__', 'M01VisibleEnvironmentStage05Composition01Recovery01VisualProof01.csv'),
    @('__LOWER__', 'm01_visible_environment_stage05_composition01_recovery01_visual_proof01'),
    @('__LOWER_KEBAB__', 'visible-environment-stage05-composition01-recovery01-visual-proof01'),
    @('__MAP__', 'Lvl_M01_VisibleEnvironmentStage05Composition01Recovery01')
)
foreach ($pair in $pairs) { $transformed = $transformed.Replace($pair[0], $pair[1]) }
foreach ($stale in @('M01_VISIBLE_ENVIRONMENT_STAGE04_RECOVERY03_VISUAL_PROOF01_RECOVERY01', 'Lvl_M01_VisibleEnvironmentStage04Recovery03')) {
    if ($transformed.Contains($stale)) { throw "Stage05 proof supervisor retained stale token: $stale" }
}
if ([regex]::Matches($transformed, [regex]::Escape('Start-Process -FilePath $editor')).Count -ne 1) { throw 'Stage05 proof supervisor must contain exactly one Unreal launch' }
$global:SkyguardTransformedSupervisorSource = $transformed
$block = [ScriptBlock]::Create($transformed)
$arguments = @{}
if ($AuthorizeSingleUnrealProof) { $arguments['AuthorizeSingleUnrealProof'] = $true }
if ($OfflineContractTest) {
    $arguments['OfflineContractTest'] = $true
    if ($OfflineEvidenceRoot) { $arguments['OfflineEvidenceRoot'] = $OfflineEvidenceRoot }
}
& $block @arguments
