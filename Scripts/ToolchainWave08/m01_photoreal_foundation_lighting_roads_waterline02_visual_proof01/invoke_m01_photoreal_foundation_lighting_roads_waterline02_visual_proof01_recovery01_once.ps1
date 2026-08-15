[CmdletBinding()]
param(
    [switch]$OfflineContractTest,
    [string]$OfflineEvidenceRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$source = 'D:\Skyguard52\Scripts\ToolchainWave08\m01_photoreal_foundation_lighting_roads_waterline02_visual_proof01\invoke_m01_photoreal_foundation_lighting_roads_waterline02_visual_proof01_once.ps1'
$expectedBytes = 4361
$expectedSha256 = '2fea5006dc12d7121e0794875c0f1c88aa1eb9ff267832adf7149141026ab304'

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

if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { throw "Frozen failed outer supervisor is missing: $source" }
$item = Get-Item -LiteralPath $source
if ($item.Length -ne $expectedBytes -or (Get-LowerSha256 $source) -ne $expectedSha256) { throw 'Frozen failed outer supervisor changed' }

$scriptBlock = [ScriptBlock]::Create((Get-Content -LiteralPath $source -Raw))
if ($OfflineContractTest) {
    $arguments = @{ OfflineContractTest = $true }
    if ($OfflineEvidenceRoot) { $arguments['OfflineEvidenceRoot'] = $OfflineEvidenceRoot }
    & $scriptBlock @arguments
}
else {
    # The inner binding already injects its frozen one-shot authorization guard.
    # Passing a second authorization switch here caused the frozen Attempt01 failure.
    & $scriptBlock
}
