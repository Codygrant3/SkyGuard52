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

try { . $source -OfflineContractTest -OfflineEvidenceRoot $OfflineEvidenceRoot } catch { }
$transformed = $global:SkyguardTransformedSupervisorSource
if ([string]::IsNullOrWhiteSpace($transformed)) { throw 'Stage02 transformed base supervisor was not exposed' }

# Use collision-free placeholders so nested tokens are substituted exactly once.
$map = [ordered]@{
    'PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01_EXECUTION' = '__SG52_READY__'
    'M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01' = '__SG52_UPPER__'
    'M01-POLYHAVEN-VEGETATION-STAGING02-VISUAL-PROOF01' = '__SG52_KEBAB__'
    'M01PolyHavenVegetationStaging02VisualProof01.csv' = '__SG52_CSV__'
    'm01_polyhaven_vegetation_staging02_visual_proof01' = '__SG52_LOWER__'
    'polyhaven-vegetation-staging02-visual-proof01' = '__SG52_LOWER_KEBAB__'
}
foreach ($entry in $map.GetEnumerator()) {
    if (-not $transformed.Contains($entry.Key)) { throw "Recovery03 binding token is absent: $($entry.Key)" }
    $transformed = $transformed.Replace($entry.Key, $entry.Value)
}
$transformed = $transformed.Replace('__SG52_READY__', 'PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01_RECOVERY03_EXECUTION')
$transformed = $transformed.Replace('__SG52_UPPER__', 'M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01_RECOVERY03')
$transformed = $transformed.Replace('__SG52_KEBAB__', 'M01-POLYHAVEN-VEGETATION-STAGING02-VISUAL-PROOF01-RECOVERY03')
$transformed = $transformed.Replace('__SG52_CSV__', 'M01PolyHavenVegetationStaging02VisualProof01Recovery03.csv')
$transformed = $transformed.Replace('__SG52_LOWER__', 'm01_polyhaven_vegetation_staging02_visual_proof01_recovery03')
$transformed = $transformed.Replace('__SG52_LOWER_KEBAB__', 'polyhaven-vegetation-staging02-visual-proof01-recovery03')
if ($transformed.Contains('RECOVERY03_RECOVERY03') -or $transformed.Contains('recovery03_recovery03')) { throw 'Recovery03 duplicate suffix detected' }
if ([regex]::Matches($transformed, [regex]::Escape('Start-Process -FilePath $editor')).Count -ne 1) { throw 'Recovery03 supervisor must contain exactly one Unreal launch path' }
$scriptBlock = [ScriptBlock]::Create($transformed)
$arguments = @{}
if ($AuthorizeSingleUnrealProof) { $arguments['AuthorizeSingleUnrealProof'] = $true }
if ($OfflineContractTest) {
    $arguments['OfflineContractTest'] = $true
    if ($OfflineEvidenceRoot) { $arguments['OfflineEvidenceRoot'] = $OfflineEvidenceRoot }
}
& $scriptBlock @arguments
