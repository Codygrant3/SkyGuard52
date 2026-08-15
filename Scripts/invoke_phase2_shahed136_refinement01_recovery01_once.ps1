[CmdletBinding()]
param(
    [switch]$AuthorizeSingleBlender,
    [switch]$OfflineContractTest
)

$ErrorActionPreference = 'Stop'
$ProjectRoot = 'D:\Skyguard52'
$AuthorityPath = Join-Path $ProjectRoot 'Saved\Reports\PHASE2_SHAHED136_REFINEMENT01_RECOVERY01_EXECUTION_AUTHORITY.json'
$ControllerPath = Join-Path $ProjectRoot 'Scripts\skyguard_production.py'
$ManifestPath = Join-Path $ProjectRoot 'Production\production_manifest.json'
$AssetId = 'core-shahed136'
$ExpectedAuthorityHash = '1df0e53bc93c5892bc66b7cbd3a4753178cb197d1a11d4f037360b4ba242b2b5'
$ExpectedWorker = 'Scripts\Workers\worker_core_shahed136_refinement01_recovery01.py'

function Get-Sha256Lower([string]$Path) {
    $stream = [System.IO.File]::Open($Path, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::Read)
    $algorithm = [System.Security.Cryptography.SHA256]::Create()
    try {
        $bytes = $algorithm.ComputeHash($stream)
        return ([System.BitConverter]::ToString($bytes)).Replace('-', '').ToLowerInvariant()
    }
    finally {
        $algorithm.Dispose()
        $stream.Dispose()
    }
}

function Assert-FileAuthority($Record) {
    if (-not [System.IO.File]::Exists([string]$Record.path)) {
        throw "Missing authority: $($Record.path)"
    }
    $item = [System.IO.FileInfo]::new([string]$Record.path)
    if ($item.Length -ne [int64]$Record.bytes) {
        throw "Byte-count mismatch: $($Record.path)"
    }
    if ((Get-Sha256Lower ([string]$Record.path)) -ne [string]$Record.sha256) {
        throw "SHA-256 mismatch: $($Record.path)"
    }
}

function Get-HeavyProcesses {
    $names = @('UnrealEditor', 'UnrealEditor-Cmd', 'ShaderCompileWorker', 'blender', 'AutomationTool', 'UnrealBuildTool', 'cl', 'link')
    return @(Get-Process -ErrorAction SilentlyContinue | Where-Object { $names -contains $_.ProcessName })
}

if ($AuthorizeSingleBlender -and $OfflineContractTest) {
    [Console]::Error.WriteLine('Offline and authorized modes are mutually exclusive.')
    [Environment]::Exit([int]3)
}

if (-not [System.IO.File]::Exists($AuthorityPath)) {
    throw "Missing execution authority: $AuthorityPath"
}
if ((Get-Sha256Lower $AuthorityPath) -ne $ExpectedAuthorityHash) {
    throw 'Recovery01 execution-authority hash mismatch.'
}
$authority = Get-Content -LiteralPath $AuthorityPath -Raw | ConvertFrom-Json
foreach ($record in $authority.authorities) {
    Assert-FileAuthority $record
}

if ($OfflineContractTest) {
    $manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
    $asset = @($manifest.assets | Where-Object { $_.id -eq $AssetId })
    if ($asset.Count -ne 1) { throw 'Expected exactly one Shahed-136 registry entry.' }
    if ($asset[0].worker.script -ne $ExpectedWorker) {
        throw 'The Shahed-136 worker is not bound to the Recovery01 compatibility worker.'
    }
    if ([int]$asset[0].worker.minimum_renders -ne 8) {
        throw 'The Shahed-136 render requirement is not eight.'
    }
    [Console]::Out.WriteLine('{"classification":"PASS_OFFLINE_CONTRACT_TEST","blender_launch_count":0,"compatibility_binding":"RECOVERY01"}')
    [Environment]::Exit([int]0)
}

if (-not $AuthorizeSingleBlender) {
    [Console]::Error.WriteLine('Explicit -AuthorizeSingleBlender is required.')
    [Environment]::Exit([int]2)
}

$active = Get-HeavyProcesses
if ($active.Count -ne 0) {
    throw "Heavy process gate is not clear: $($active.ProcessName -join ', ')"
}

$manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
$asset = @($manifest.assets | Where-Object { $_.id -eq $AssetId })
if ($asset.Count -ne 1) { throw 'Expected exactly one Shahed-136 registry entry.' }
if ($asset[0].status -ne 'ready') { throw "Shahed-136 registry state is $($asset[0].status), not ready." }
if ($asset[0].worker.script -ne $ExpectedWorker) {
    throw 'The Shahed-136 worker is not bound to the Recovery01 compatibility worker.'
}

& python $ControllerPath run $AssetId
$exitCode = [int]$LASTEXITCODE
[Environment]::Exit($exitCode)
