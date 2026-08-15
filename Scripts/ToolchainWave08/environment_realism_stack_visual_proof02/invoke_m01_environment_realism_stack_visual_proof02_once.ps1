[CmdletBinding()]
param(
    [switch]$AuthorizeSingleUnrealProof,
    [switch]$OfflineContractTest,
    [string]$OfflineEvidenceRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$source = 'D:\Skyguard52\Scripts\ToolchainWave08\environment_realism_stack_visual_proof01\invoke_m01_environment_realism_stack_visual_proof01_once.ps1'
$expectedBytes = 4773
$expectedSha256 = '21fc39e3db4a9dd97ab8a21ed5677d9d690d8ab2134556d1dee1436bdd241970'

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

if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { throw "Frozen Visual Proof01 supervisor wrapper is missing: $source" }
$item = Get-Item -LiteralPath $source
if ($item.Length -ne $expectedBytes -or (Get-LowerSha256 $source) -ne $expectedSha256) { throw 'Frozen Visual Proof01 supervisor wrapper changed' }

$transformed = Get-Content -LiteralPath $source -Raw
$replacements = @(
    @('M01_ENVIRONMENT_REALISM_STACK_VISUAL_PROOF01', 'M01_ENVIRONMENT_REALISM_STACK_VISUAL_PROOF02'),
    @('M01-ENVIRONMENT-REALISM-STACK-VISUAL-PROOF01', 'M01-ENVIRONMENT-REALISM-STACK-VISUAL-PROOF02'),
    @('Lvl_M01_T08_EnvironmentRealismStack01_Recovery02', 'Lvl_M01_T08_EnvironmentRealismStack03'),
    @('M01EnvironmentRealismStackVisualProof01.csv', 'M01EnvironmentRealismStackVisualProof02.csv'),
    @('environment_realism_stack_visual_proof01', 'environment_realism_stack_visual_proof02'),
    @('capture_m01_environment_realism_stack_visual_proof01.py', 'capture_m01_environment_realism_stack_visual_proof02.py'),
    @('adjudicate_m01_environment_realism_stack_visual_proof01_once.py', 'adjudicate_m01_environment_realism_stack_visual_proof02_once.py'),
    @('m01_environment_realism_stack_visual_proof01', 'm01_environment_realism_stack_visual_proof02'),
    @('visual-proof01', 'visual-proof02'),
    @('PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_ENVIRONMENT_REALISM_STACK_VISUAL_PROOF01_EXECUTION', 'PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_ENVIRONMENT_REALISM_STACK_VISUAL_PROOF02_EXECUTION')
)
foreach ($pair in $replacements) {
    if ($transformed.Contains($pair[0])) { $transformed = $transformed.Replace($pair[0], $pair[1]) }
}

$badAtomic = "if (Test-Path -LiteralPath ```$Path) { [System.IO.File]::Replace(```$temporary, ```$Path, ```$null) } else { [System.IO.File]::Move(```$temporary, ```$Path) }"
$goodAtomic = "if (Test-Path -LiteralPath ```$Path) { ```$backup = ```$Path + '.atomic-backup'; if (Test-Path -LiteralPath ```$backup) { throw ('Atomic backup exists: ' + ```$backup) }; [System.IO.File]::Replace(```$temporary, ```$Path, ```$backup); [System.IO.File]::Delete(```$backup) } else { [System.IO.File]::Move(```$temporary, ```$Path) }"
if (-not $transformed.Contains($badAtomic)) { throw 'Known null-backup atomic writer target is missing' }
$transformed = $transformed.Replace($badAtomic, $goodAtomic)

foreach ($pair in $replacements) {
    if ($transformed.Contains($pair[0])) { throw "Visual Proof02 supervisor retained stale token: $($pair[0])" }
}
foreach ($required in @('M01_ENVIRONMENT_REALISM_STACK_VISUAL_PROOF02', 'M01-ENVIRONMENT-REALISM-STACK-VISUAL-PROOF02', 'Lvl_M01_T08_EnvironmentRealismStack03', 'M01EnvironmentRealismStackVisualProof02.csv', 'environment_realism_stack_visual_proof02')) {
    if (-not $transformed.Contains($required)) { throw "Visual Proof02 supervisor output binding is missing: $required" }
}
if ($transformed.Contains('[System.IO.File]::Replace(`$temporary, `$Path, `$null)')) { throw 'Null-backup File.Replace survived correction' }
if ([regex]::Matches($transformed, [regex]::Escape('Start-Process -FilePath $editor')).Count -ne 1) { throw 'Transformed supervisor must contain exactly one Unreal launch path' }

$global:SkyguardTransformedSupervisorSource = $transformed
$scriptBlock = [ScriptBlock]::Create($transformed)
$arguments = @{}
if ($AuthorizeSingleUnrealProof) { $arguments['AuthorizeSingleUnrealProof'] = $true }
if ($OfflineContractTest) { $arguments['OfflineContractTest'] = $true }
if ($OfflineEvidenceRoot) { $arguments['OfflineEvidenceRoot'] = $OfflineEvidenceRoot }
& $scriptBlock @arguments
