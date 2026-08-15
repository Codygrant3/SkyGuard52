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

if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { throw "Frozen Stage02 failed supervisor is missing: $source" }
$item = Get-Item -LiteralPath $source
if ($item.Length -ne $expectedBytes -or (Get-LowerSha256 $source) -ne $expectedSha256) { throw 'Frozen Stage02 failed supervisor changed' }

# Load the failed wrapper only in offline mode so it exposes its fully transformed,
# proven base source without launching Unreal or creating a governed namespace.
try { . $source -OfflineContractTest -OfflineEvidenceRoot $OfflineEvidenceRoot } catch { }
$transformed = $global:SkyguardTransformedSupervisorSource
if ([string]::IsNullOrWhiteSpace($transformed)) { throw 'Stage02 transformed base supervisor was not exposed' }
$replacements = @(
    @('PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01_EXECUTION', 'PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01_RECOVERY01_EXECUTION'),
    @('M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01', 'M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01_RECOVERY01'),
    @('M01-POLYHAVEN-VEGETATION-STAGING02-VISUAL-PROOF01', 'M01-POLYHAVEN-VEGETATION-STAGING02-VISUAL-PROOF01-RECOVERY01'),
    @('M01PolyHavenVegetationStaging02VisualProof01.csv', 'M01PolyHavenVegetationStaging02VisualProof01Recovery01.csv'),
    @('capture_m01_polyhaven_vegetation_staging02_visual_proof01.py', 'capture_m01_polyhaven_vegetation_staging02_visual_proof01_recovery01.py'),
    @('adjudicate_m01_polyhaven_vegetation_staging02_visual_proof01_once.py', 'adjudicate_m01_polyhaven_vegetation_staging02_visual_proof01_recovery01_once.py'),
    @('m01_polyhaven_vegetation_staging02_visual_proof01', 'm01_polyhaven_vegetation_staging02_visual_proof01_recovery01'),
    @('polyhaven-vegetation-staging02-visual-proof01', 'polyhaven-vegetation-staging02-visual-proof01-recovery01')
)
foreach ($pair in $replacements) {
    if (-not $transformed.Contains($pair[0])) { throw "Recovery01 binding token is absent: $($pair[0])" }
    $transformed = $transformed.Replace($pair[0], $pair[1])
}
if ([regex]::Matches($transformed, [regex]::Escape('Start-Process -FilePath $editor')).Count -ne 1) { throw 'Recovery01 supervisor must contain exactly one Unreal launch path' }
$scriptBlock = [ScriptBlock]::Create($transformed)
$arguments = @{}
if ($AuthorizeSingleUnrealProof) { $arguments['AuthorizeSingleUnrealProof'] = $true }
if ($OfflineContractTest) {
    $arguments['OfflineContractTest'] = $true
    if ($OfflineEvidenceRoot) { $arguments['OfflineEvidenceRoot'] = $OfflineEvidenceRoot }
}
& $scriptBlock @arguments
