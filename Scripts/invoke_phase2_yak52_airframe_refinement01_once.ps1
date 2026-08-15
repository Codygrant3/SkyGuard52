[CmdletBinding()]
param(
    [switch]$AuthorizeSingleBlender,
    [switch]$OfflineContractTest
)

$ErrorActionPreference = 'Stop'
$ProjectRoot = 'D:\Skyguard52'
$AuthorityPath = Join-Path $ProjectRoot 'Saved\Reports\PHASE2_YAK52_AIRFRAME_REFINEMENT01_EXECUTION_AUTHORITY.json'
$ControllerPath = Join-Path $ProjectRoot 'Scripts\skyguard_production.py'
$ManifestPath = Join-Path $ProjectRoot 'Production\production_manifest.json'
$AssetId = 'core-yak52-airframe'
$ExpectedAuthorityHash = '671cf4af67d9e9b73f96a6657221d023e91e86644d63348f2583c176181c4204'

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
    throw 'Execution-authority hash mismatch.'
}
$authority = Get-Content -LiteralPath $AuthorityPath -Raw | ConvertFrom-Json
foreach ($record in $authority.authorities) {
    Assert-FileAuthority $record
}

if ($OfflineContractTest) {
    $manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
    $asset = @($manifest.assets | Where-Object { $_.id -eq $AssetId })
    if ($asset.Count -ne 1) { throw 'Expected exactly one airframe registry entry.' }
    if ($asset[0].worker.script -ne 'Scripts\Workers\worker_core_yak52_airframe_refinement01.py') {
        throw 'The airframe worker is not bound to Refinement01.'
    }
    [Console]::Out.WriteLine('{"classification":"PASS_OFFLINE_CONTRACT_TEST","blender_launch_count":0}')
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
if ($asset.Count -ne 1) { throw 'Expected exactly one airframe registry entry.' }
if ($asset[0].status -ne 'ready') { throw "Airframe registry state is $($asset[0].status), not ready." }
if ($asset[0].worker.script -ne 'Scripts\Workers\worker_core_yak52_airframe_refinement01.py') {
    throw 'The airframe worker is not bound to Refinement01.'
}

& python $ControllerPath run $AssetId
$exitCode = [int]$LASTEXITCODE
[Environment]::Exit($exitCode)
