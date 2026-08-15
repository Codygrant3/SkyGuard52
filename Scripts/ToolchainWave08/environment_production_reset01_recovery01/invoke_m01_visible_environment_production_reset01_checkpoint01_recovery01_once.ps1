param(
    [switch]$AuthorizeSingleBlender,
    [switch]$OfflineContractTest
)

$ErrorActionPreference = 'Stop'
$Original = 'D:\Skyguard52\Scripts\ToolchainWave08\environment_production_reset01\invoke_m01_visible_environment_production_reset01_checkpoint01_once.ps1'
$ExpectedOriginalSha256 = '6055ce2bed9036a0da0cc21adbef4bcf3679a30dd59b45ef6fd0610e8da47820'

function Get-Sha256([string]$Path) {
    $stream = $null
    $algorithm = $null
    try {
        $stream = [System.IO.File]::Open($Path, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::Read)
        $algorithm = [System.Security.Cryptography.SHA256]::Create()
        $bytes = $algorithm.ComputeHash($stream)
        return ([System.BitConverter]::ToString($bytes)).Replace('-', '').ToLowerInvariant()
    }
    finally {
        if ($null -ne $algorithm) { $algorithm.Dispose() }
        if ($null -ne $stream) { $stream.Dispose() }
    }
}

if ((Get-Sha256 $Original) -ne $ExpectedOriginalSha256) {
    throw 'Frozen Checkpoint01 supervisor hash mismatch.'
}

$Source = [System.IO.File]::ReadAllText($Original)
$ParamPattern = '(?s)^param\(.*?\)\r?\n\r?\n'
$ParamMatches = [regex]::Matches($Source, $ParamPattern)
if ($ParamMatches.Count -ne 1) { throw "Expected one leading param block; found $($ParamMatches.Count)." }
$Source = [regex]::Replace($Source, $ParamPattern, '', 1)

$Replacements = @(
    @('environment_production_reset01\build_m01_visible_environment_production_reset01_checkpoint01.py', 'environment_production_reset01_recovery01\build_m01_visible_environment_production_reset01_checkpoint01_recovery01.py'),
    @('environment_production_reset01\adjudicate_m01_visible_environment_production_reset01_checkpoint01.py', 'environment_production_reset01_recovery01\adjudicate_m01_visible_environment_production_reset01_checkpoint01_recovery01.py'),
    @('environment_production_reset01\verify_m01_visible_environment_production_reset01_checkpoint01_offline.py', 'environment_production_reset01_recovery01\verify_m01_visible_environment_production_reset01_checkpoint01_recovery01_offline.py'),
    @('M01VisibleEnvironmentProductionReset01Checkpoint01\execution_contract.json', 'M01VisibleEnvironmentProductionReset01Checkpoint01Recovery01\execution_contract.json'),
    @('fefa08e50cb9e78d8d5a3965635d8f065df251d8861c777821c2a88d64eaf891', 'd8e4350ec53679e895280d451d9452aef2dc3d846b73d7a4d254ee5c303ab284'),
    @('7b74c7d08a0918172b064553865dbd9d1868fca4e56f38be5f2e659c4046b440', '8f850a8690968c6128323263ef8058373850091dc4396f42f55d8eaf9a475d3e'),
    @('f81dad2cc122d2708023882701360f0fa9fdcdf1577b57470e690a18e55235db', '7b0bac4954b824183be71bd246058bf2e3f1134b0f2023954b5e1c6f185680f4'),
    @('31a497e335fa3ec75de9ad6b0f62dbf6ea61c3fbcf910d08f645c8544e7d351c', 'd7dd1efd270fe4be899d940bbb291619d5954fc0a9736859a50d2a35146c4110'),
    @('VisibleEnvironmentProductionReset01_Checkpoint01', 'VisibleEnvironmentProductionReset01_Checkpoint01_Recovery01'),
    @('M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_CHECKPOINT01', 'M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_CHECKPOINT01_RECOVERY01')
)

foreach ($pair in $Replacements) {
    $old = [string]$pair[0]
    $new = [string]$pair[1]
    if (-not $Source.Contains($old)) { throw "Recovery01 supervisor binding token absent: $old" }
    $Source = $Source.Replace($old, $new)
}

if ($Source.Contains('environment_production_reset01\build_m01_visible_environment_production_reset01_checkpoint01.py')) {
    throw 'Original generator path remains after Recovery01 binding.'
}

Invoke-Expression $Source
