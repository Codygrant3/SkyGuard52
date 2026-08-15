[CmdletBinding()]
param(
    [switch]$AuthorizeSingleBlender,
    [switch]$OfflineContractTest
)

$ErrorActionPreference = 'Stop'
$ProjectRoot = 'D:\Skyguard52'
$AuthorityPath = Join-Path $ProjectRoot 'Saved\Reports\PHASE2_REARGUNNER_CHARACTER_REFINEMENT01_RECOVERY01_EXECUTION_AUTHORITY.json'
$ControllerPath = Join-Path $ProjectRoot 'Scripts\skyguard_production.py'
$ManifestPath = Join-Path $ProjectRoot 'Production\production_manifest.json'
$AssetId = 'core-reargunner-character-refinement01'
$FutureAttemptRoot = Join-Path $ProjectRoot 'Production\Attempts\core-reargunner-character-refinement01'
$ExpectedAuthorityHash = '0de4fcf7861826862ed9203b7862c522c24960c341065fe03980b9f4cce65921'

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
    $names = @(
        'UnrealEditor',
        'UnrealEditor-Cmd',
        'ShaderCompileWorker',
        'blender',
        'AutomationTool',
        'UnrealBuildTool',
        'cl',
        'link'
    )
    return @(Get-Process -ErrorAction SilentlyContinue | Where-Object { $names -contains $_.ProcessName })
}

function Assert-ManifestSemanticContract($Contract) {
    if (-not [System.IO.File]::Exists($ManifestPath)) {
        throw "Missing canonical production manifest: $ManifestPath"
    }
    $manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
    $assets = @($manifest.assets | Where-Object { $_.id -eq [string]$Contract.asset_id })
    if ($assets.Count -ne [int]$Contract.asset_cardinality) {
        throw "Character asset cardinality mismatch: $($assets.Count)"
    }
    $asset = $assets[0]
    if ([string]$asset.status -ne [string]$Contract.status) {
        throw "Character asset status mismatch: $($asset.status)"
    }
    if ([string]$asset.worker.script -ne [string]$Contract.worker_script) {
        throw "Character worker binding mismatch: $($asset.worker.script)"
    }
    if ([int]$asset.worker.minimum_renders -ne [int]$Contract.minimum_renders) {
        throw "Character minimum-render count mismatch: $($asset.worker.minimum_renders)"
    }
    $actualArguments = @($asset.worker.arguments | ForEach-Object { [string]$_ })
    $expectedArguments = @($Contract.worker_arguments | ForEach-Object { [string]$_ })
    if ($actualArguments.Count -ne $expectedArguments.Count) {
        throw 'Character worker argument cardinality mismatch.'
    }
    for ($index = 0; $index -lt $expectedArguments.Count; $index++) {
        if ($actualArguments[$index] -cne $expectedArguments[$index]) {
            throw "Character worker argument mismatch at index $index."
        }
    }
    $legacyAssets = @($manifest.assets | Where-Object { $_.id -eq [string]$Contract.legacy_asset_id })
    if ($legacyAssets.Count -ne [int]$Contract.legacy_asset_cardinality) {
        throw "Legacy rear-gunner asset cardinality mismatch: $($legacyAssets.Count)"
    }
    if ([string]$legacyAssets[0].status -ne [string]$Contract.legacy_status) {
        throw "Legacy rear-gunner asset status mismatch: $($legacyAssets[0].status)"
    }
}

if ($AuthorizeSingleBlender -and $OfflineContractTest) {
    [Console]::Error.WriteLine('Offline and authorized modes are mutually exclusive.')
    [Environment]::Exit([int]3)
}

if (-not [System.IO.File]::Exists($AuthorityPath)) {
    throw "Missing Recovery01 execution authority: $AuthorityPath"
}
if ((Get-Sha256Lower $AuthorityPath) -ne $ExpectedAuthorityHash) {
    throw 'Recovery01 execution-authority hash mismatch.'
}
$authority = Get-Content -LiteralPath $AuthorityPath -Raw | ConvertFrom-Json
if ($authority.classification -ne 'PASSED_READY_FOR_EXPLICIT_SINGLE_REARGUNNER_CHARACTER_REFINEMENT01_RECOVERY01_BLENDER_AUTHORIZATION') {
    throw 'Recovery01 execution authority is not classified ready.'
}
foreach ($record in $authority.authorities) {
    Assert-FileAuthority $record
}
Assert-ManifestSemanticContract $authority.manifest_semantic_contract

if ([System.IO.Directory]::Exists($FutureAttemptRoot)) {
    throw "Future attempt namespace already exists: $FutureAttemptRoot"
}

if ($OfflineContractTest) {
    $active = Get-HeavyProcesses
    if ($active.Count -ne 0) {
        throw "Heavy process gate is not clear: $($active.ProcessName -join ', ')"
    }
    [Console]::Out.WriteLine('{"classification":"PASS_RECOVERY01_OFFLINE_CONTRACT_TEST","controller_launch_count":0,"blender_launch_count":0,"retry_count":0,"manifest_validation":"SEMANTIC_PASS"}')
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

& python $ControllerPath run $AssetId
$exitCode = [int]$LASTEXITCODE
[Environment]::Exit($exitCode)
