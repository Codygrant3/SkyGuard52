[CmdletBinding()]
param(
    [switch]$AuthorizeSingleUnrealProof,
    [switch]$OfflineContractTest,
    [string]$OfflineEvidenceRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$source = 'D:\Skyguard52\Scripts\ToolchainWave08\m01_polyhaven_vegetation_staging02_visual_proof01\invoke_m01_polyhaven_vegetation_staging02_visual_proof01_once.ps1'
$expectedBytes = 3410
$expectedSha256 = '31f0ab182d5334029b44d8c6a07cc9f5af9d44ec500fe3154f6200742d421523'

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

if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { throw "Frozen Stage02 proof supervisor is missing: $source" }
$item = Get-Item -LiteralPath $source
if ($item.Length -ne $expectedBytes -or (Get-LowerSha256 $source) -ne $expectedSha256) { throw 'Frozen Stage02 proof supervisor changed' }

try { & $source -OfflineContractTest -OfflineEvidenceRoot $OfflineEvidenceRoot } catch {}
$transformed = $global:SkyguardTransformedSupervisorSource
if ([string]::IsNullOrWhiteSpace($transformed)) { throw 'Transformed Stage02 supervisor unavailable' }
$pairs = @(
    @('PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01_EXECUTION', '__READY__'),
    @('M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01', '__UPPER__'),
    @('M01-POLYHAVEN-VEGETATION-STAGING02-VISUAL-PROOF01', '__KEBAB__'),
    @('M01PolyHavenVegetationStaging02VisualProof01.csv', '__CSV__'),
    @('m01_polyhaven_vegetation_staging02_visual_proof01', '__LOWER__'),
    @('polyhaven-vegetation-staging02-visual-proof01', '__LOWER_KEBAB__'),
    @('Lvl_M01_PolyHavenVegetationStaging02', '__MAP__')
)
foreach ($pair in $pairs) {
    if (-not $transformed.Contains($pair[0])) { throw "Missing Stage03 source token: $($pair[0])" }
    $transformed = $transformed.Replace($pair[0], $pair[1])
}
$pairs = @(
    @('__READY__', 'PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_VISIBLE_ENVIRONMENT_STAGE03_VISUAL_PROOF01_EXECUTION'),
    @('__UPPER__', 'M01_VISIBLE_ENVIRONMENT_STAGE03_VISUAL_PROOF01'),
    @('__KEBAB__', 'M01-VISIBLE-ENVIRONMENT-STAGE03-VISUAL-PROOF01'),
    @('__CSV__', 'M01VisibleEnvironmentStage03VisualProof01.csv'),
    @('__LOWER__', 'm01_visible_environment_stage03_visual_proof01'),
    @('__LOWER_KEBAB__', 'visible-environment-stage03-visual-proof01'),
    @('__MAP__', 'Lvl_M01_VisibleEnvironmentStage03')
)
foreach ($pair in $pairs) { $transformed = $transformed.Replace($pair[0], $pair[1]) }
foreach ($stale in @('M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01', 'Lvl_M01_PolyHavenVegetationStaging02')) {
    if ($transformed.Contains($stale)) { throw "Stage03 supervisor retained stale token: $stale" }
}
if ([regex]::Matches($transformed, [regex]::Escape('Start-Process -FilePath $editor')).Count -ne 1) { throw 'Transformed Stage03 supervisor must contain exactly one Unreal launch' }
$global:SkyguardTransformedSupervisorSource = $transformed
$block = [ScriptBlock]::Create($transformed)
$arguments = @{}
if ($AuthorizeSingleUnrealProof) { $arguments['AuthorizeSingleUnrealProof'] = $true }
if ($OfflineContractTest) {
    $arguments['OfflineContractTest'] = $true
    if ($OfflineEvidenceRoot) { $arguments['OfflineEvidenceRoot'] = $OfflineEvidenceRoot }
}
& $block @arguments
