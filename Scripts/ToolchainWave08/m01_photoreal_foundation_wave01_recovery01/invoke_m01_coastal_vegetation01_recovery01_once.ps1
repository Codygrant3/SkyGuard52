param(
    [switch]$AuthorizeSingleBlender,
    [switch]$OfflineContractTest
)

$ErrorActionPreference = 'Stop'
$Source = 'D:\Skyguard52\Scripts\ToolchainWave08\m01_photoreal_foundation_wave01\invoke_m01_coastal_vegetation01_once.ps1'
$ExpectedBytes = 10362
$ExpectedSha256 = 'c49376c8dacc42799947c74ddc0816d8713914f2d2b94958b4373e3dca16e610'
$RecoveryWorker = 'D:\Skyguard52\Scripts\ToolchainWave08\m01_photoreal_foundation_wave01_recovery01\worker_m01_coastal_vegetation01_recovery01.py'
$RecoveryWorkerBytes = 1455
$RecoveryWorkerSha256 = '700289a8875741c7a07630f5011721f50c5cae33f20aacdb7f5e2c9492aa6b11'

function Get-Sha256Hex([string]$Path) {
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

foreach ($authority in @(
    @($Source, $ExpectedBytes, $ExpectedSha256),
    @($RecoveryWorker, $RecoveryWorkerBytes, $RecoveryWorkerSha256)
)) {
    if (-not [System.IO.File]::Exists([string]$authority[0])) { throw "Missing immutable authority: $($authority[0])" }
    $item = [System.IO.FileInfo]::new([string]$authority[0])
    if ($item.Length -ne [long]$authority[1] -or (Get-Sha256Hex ([string]$authority[0])) -ne [string]$authority[2]) {
        throw "Immutable authority mismatch: $($authority[0])"
    }
}

$sourceText = [System.IO.File]::ReadAllText($Source)
$replacements = @(
    @('m01_photoreal_foundation_wave01\worker_m01_coastal_vegetation01.py', 'm01_photoreal_foundation_wave01_recovery01\worker_m01_coastal_vegetation01_recovery01.py', 1),
    @('M01_PHOTOREAL_FOUNDATION_WAVE01_COASTAL_VEGETATION01', 'M01_PHOTOREAL_FOUNDATION_WAVE01_COASTAL_VEGETATION01_RECOVERY01', 2),
    @('m01-photoreal-foundation-wave01-coastal-vegetation01', 'm01-photoreal-foundation-wave01-coastal-vegetation01-recovery01', 1),
    @('26824', '1455', 1),
    @('dd623a698979b6740f4e9ecbd08caab0d43f8552102253e753d774899b923b60', '700289a8875741c7a07630f5011721f50c5cae33f20aacdb7f5e2c9492aa6b11', 1)
)
foreach ($replacement in $replacements) {
    $old = [string]$replacement[0]
    $new = [string]$replacement[1]
    $expectedCount = [int]$replacement[2]
    $actualCount = [regex]::Matches($sourceText, [regex]::Escape($old)).Count
    if ($actualCount -ne $expectedCount) { throw "Recovery01 binding count mismatch for $old : $actualCount != $expectedCount" }
    $sourceText = $sourceText.Replace($old, $new)
}

$binding = [scriptblock]::Create($sourceText)
$arguments = @{}
if ($AuthorizeSingleBlender) { $arguments.AuthorizeSingleBlender = $true }
if ($OfflineContractTest) { $arguments.OfflineContractTest = $true }
& $binding @arguments
exit ([int]$LASTEXITCODE)
