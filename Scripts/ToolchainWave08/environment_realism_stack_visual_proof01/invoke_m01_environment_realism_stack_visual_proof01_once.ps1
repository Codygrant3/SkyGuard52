[CmdletBinding()]
param(
    [switch]$AuthorizeSingleUnrealProof,
    [switch]$OfflineContractTest,
    [string]$OfflineEvidenceRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$source = 'D:\Skyguard52\Scripts\ToolchainWave08\environment_authoring01_recovery07_mapped_visual_proof01_recovery04\invoke_recovery07_mapped_visual_proof01_recovery04_once.ps1'
$expectedBytes = 23753
$expectedSha256 = '09d15557b2f71f63ee4f8c82a43d1b9e95b5fe9d9d38b1e3b7f9f9520a2102e2'
$oldPrefix = 'TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY07_MAPPED_VISUAL_PROOF01_RECOVERY04'
$newPrefix = 'M01_ENVIRONMENT_REALISM_STACK_VISUAL_PROOF01'
$oldContractId = 'T08-M01-ENV-AUTH01-RECOVERY07-MAPPED-VISUAL-PROOF01-RECOVERY04'
$newContractId = 'M01-ENVIRONMENT-REALISM-STACK-VISUAL-PROOF01'
$oldMap = 'Lvl_M01_T08_EnvironmentAuthoring01_Recovery07'
$newMap = 'Lvl_M01_T08_EnvironmentRealismStack01_Recovery02'
$oldClassification = 'PASSED_READY_FOR_EXPLICIT_SINGLE_RECOVERY07_MAPPED_VISUAL_PROOF01_RECOVERY04_AUTHORIZATION'
$newClassification = 'PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_ENVIRONMENT_REALISM_STACK_VISUAL_PROOF01_EXECUTION'

function Get-LowerSha256([string]$Path) {
    $stream = $null
    $algorithm = $null
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

if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { throw "Frozen supervisor authority is missing: $source" }
$item = Get-Item -LiteralPath $source
if ($item.Length -ne $expectedBytes -or (Get-LowerSha256 $source) -ne $expectedSha256) {
    throw 'Frozen Recovery04 supervisor authority changed'
}

$transformed = Get-Content -LiteralPath $source -Raw
foreach ($required in @($oldPrefix, $oldContractId, $oldMap, 'Recovery07MappedVisualProof01Recovery04.csv', 'recovery07_mapped_visual_proof01_recovery04', $oldClassification)) {
    if (-not $transformed.Contains($required)) { throw "Supervisor transformation target is missing: $required" }
}
$transformed = $transformed.Replace($oldPrefix, $newPrefix)
$transformed = $transformed.Replace($oldContractId, $newContractId)
$transformed = $transformed.Replace($oldMap, $newMap)
$transformed = $transformed.Replace('Recovery07MappedVisualProof01Recovery04.csv', 'M01EnvironmentRealismStackVisualProof01.csv')
$transformed = $transformed.Replace('environment_authoring01_recovery07_mapped_visual_proof01_recovery04', 'environment_realism_stack_visual_proof01')
$transformed = $transformed.Replace('capture_recovery07_mapped_visual_proof01_recovery04.py', 'capture_m01_environment_realism_stack_visual_proof01.py')
$transformed = $transformed.Replace('adjudicate_recovery07_mapped_visual_proof01_recovery04_once.py', 'adjudicate_m01_environment_realism_stack_visual_proof01_once.py')
$transformed = $transformed.Replace('recovery07_mapped_visual_proof01_recovery04', 'm01_environment_realism_stack_visual_proof01')
$transformed = $transformed.Replace($oldClassification, $newClassification)
$transformed = $transformed.Replace(
    '$script = Get-Content -LiteralPath $PSCommandPath -Raw',
    '$script = $global:SkyguardTransformedSupervisorSource'
)
$transformed = $transformed.Replace(
    '[System.IO.File]::Move($temporary, $Path)',
    "if (Test-Path -LiteralPath `$Path) { [System.IO.File]::Replace(`$temporary, `$Path, `$null) } else { [System.IO.File]::Move(`$temporary, `$Path) }"
)
$transformed = $transformed.Replace(
    'skyguard.t08.m01.recovery07-mapped-proof01',
    'skyguard.m01-environment-realism-stack.visual-proof01'
)

foreach ($stale in @($oldPrefix, $oldContractId, $oldMap, 'Recovery07MappedVisualProof01Recovery04.csv', 'recovery07_mapped_visual_proof01_recovery04', $oldClassification)) {
    if ($transformed.Contains($stale)) { throw "Supervisor transformation left stale token: $stale" }
}
if ([regex]::Matches($transformed, [regex]::Escape('Start-Process -FilePath $editor')).Count -ne 1) {
    throw 'Transformed supervisor does not contain exactly one Unreal launch path'
}

$scriptBlock = [ScriptBlock]::Create($transformed)
$global:SkyguardTransformedSupervisorSource = $transformed
$arguments = @{}
if ($AuthorizeSingleUnrealProof) { $arguments['AuthorizeSingleUnrealProof'] = $true }
if ($OfflineContractTest) { $arguments['OfflineContractTest'] = $true }
if ($OfflineEvidenceRoot) { $arguments['OfflineEvidenceRoot'] = $OfflineEvidenceRoot }
& $scriptBlock @arguments
