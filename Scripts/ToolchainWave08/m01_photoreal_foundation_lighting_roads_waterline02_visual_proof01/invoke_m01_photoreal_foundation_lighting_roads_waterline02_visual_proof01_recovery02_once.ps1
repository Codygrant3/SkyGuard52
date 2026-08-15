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

$transformed = Get-Content -LiteralPath $source -Raw
$pattern = "(?ms)^else \{\r?\n    \`$arguments\['AuthorizeSingleUnrealProof'\] = \`$true\r?\n\}\r?\n& \`$scriptBlock @arguments\s*$"
$matches = [regex]::Matches($transformed, $pattern)
if ($matches.Count -ne 1) { throw "Expected exactly one redundant authorization dispatch; found $($matches.Count)" }
$transformed = [regex]::Replace($transformed, $pattern, '& $scriptBlock @arguments')
if ($transformed.Contains("`$arguments['AuthorizeSingleUnrealProof']")) { throw 'Recovery02 retained the redundant authorization dispatch' }
if ([regex]::Matches($transformed, [regex]::Escape('Start-Process -FilePath $editor')).Count -ne 1) { throw 'Recovery02 must retain exactly one transformed Unreal launch validation path' }

$scriptBlock = [ScriptBlock]::Create($transformed)
$arguments = @{}
if ($OfflineContractTest) {
    $arguments['OfflineContractTest'] = $true
    if ($OfflineEvidenceRoot) { $arguments['OfflineEvidenceRoot'] = $OfflineEvidenceRoot }
}
& $scriptBlock @arguments
