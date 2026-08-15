[CmdletBinding()]
param(
    [switch]$AuthorizeSingleBlender,
    [switch]$OfflineContractTest
)

$ErrorActionPreference = 'Stop'
$ProjectRoot = 'D:\Skyguard52'
$AuthorityPath = Join-Path $ProjectRoot 'Saved\Reports\P0_CORE_RIFLE_METHOD05_DETERMINISTIC_STAGEA_EXECUTION_AUTHORITY.json'
$ExpectedAuthorityHash = '4b2f24cdae4405fba5ec9198ae681a1be6d8df8913420d8bb8d360560b8cda4a'
$ControllerPath = Join-Path $ProjectRoot 'Scripts\skyguard_production.py'
$ManifestPath = Join-Path $ProjectRoot 'Production\production_manifest.json'
$AssetId = 'core-rifle-method05-stagea'
$TerminalPath = Join-Path $ProjectRoot 'Saved\Reports\P0_CORE_RIFLE_METHOD05_DETERMINISTIC_STAGEA_SUPERVISOR_TERMINAL.json'
$EmergencyPath = Join-Path $ProjectRoot 'Saved\Reports\P0_CORE_RIFLE_METHOD05_DETERMINISTIC_STAGEA_SUPERVISOR_EMERGENCY_RECEIPT.jsonl'

function Get-UtcNow {
    return [DateTime]::UtcNow.ToString('o')
}

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
    $path = [string]$Record.path
    if (-not [System.IO.File]::Exists($path)) {
        throw "Missing immutable authority: $path"
    }
    $item = [System.IO.FileInfo]::new($path)
    if ($item.Length -ne [int64]$Record.bytes) {
        throw "Byte-count mismatch: $path"
    }
    if ((Get-Sha256Lower $path) -ne [string]$Record.sha256) {
        throw "SHA-256 mismatch: $path"
    }
}

function Get-HeavyProcesses {
    $names = @('UnrealEditor', 'UnrealEditor-Cmd', 'ShaderCompileWorker', 'blender', 'AutomationTool', 'UnrealBuildTool', 'cl', 'link')
    return @(Get-Process -ErrorAction SilentlyContinue | Where-Object { $names -contains $_.ProcessName })
}

function Get-Authority {
    if (-not [System.IO.File]::Exists($AuthorityPath)) {
        throw "Missing execution authority: $AuthorityPath"
    }
    if ((Get-Sha256Lower $AuthorityPath) -ne $ExpectedAuthorityHash) {
        throw 'Execution-authority hash mismatch.'
    }
    $authority = Get-Content -LiteralPath $AuthorityPath -Raw | ConvertFrom-Json
    foreach ($record in $authority.immutable_authorities) {
        Assert-FileAuthority $record
    }
    return $authority
}

function Assert-ManifestBinding($Authority) {
    $manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
    $binding = $Authority.mutable_manifest_binding
    $assets = @($manifest.assets | Where-Object { $_.id -eq $AssetId })
    if ($assets.Count -ne [int]$binding.expected_asset_count) {
        throw 'Manifest must contain exactly one Method05 StageA asset.'
    }
    $asset = $assets[0]
    if ($asset.status -ne [string]$binding.expected_status) {
        throw "Method05 StageA registry state is $($asset.status), not $($binding.expected_status)."
    }
    if ($asset.worker.script -ne [string]$binding.expected_worker_script) {
        throw 'Method05 StageA worker binding mismatch.'
    }
    $actualArguments = @($asset.worker.arguments)
    $expectedArguments = @($binding.expected_worker_arguments)
    if ($actualArguments.Count -ne $expectedArguments.Count) {
        throw 'Method05 StageA worker argument count mismatch.'
    }
    for ($index = 0; $index -lt $expectedArguments.Count; $index++) {
        if ([string]$actualArguments[$index] -cne [string]$expectedArguments[$index]) {
            throw "Method05 StageA worker argument mismatch at index $index."
        }
    }
    if ([int]$asset.worker.minimum_renders -ne [int]$binding.expected_minimum_renders) {
        throw 'Method05 StageA render-count binding mismatch.'
    }
    if ($asset.supersedes_only_after_acceptance -ne [string]$binding.expected_supersedes_only_after_acceptance) {
        throw 'Method05 StageA supersession boundary mismatch.'
    }
    return $asset
}

function Assert-FutureNamespacesAbsent($Authority, [bool]$IncludeSupervisorReceipts) {
    if ([System.IO.Directory]::Exists([string]$Authority.future_attempt_root)) {
        throw "Future attempt root already exists: $($Authority.future_attempt_root)"
    }
    if ($IncludeSupervisorReceipts) {
        if ([System.IO.File]::Exists([string]$Authority.future_supervisor_terminal)) {
            throw "Future supervisor terminal already exists: $($Authority.future_supervisor_terminal)"
        }
        if ([System.IO.File]::Exists([string]$Authority.future_emergency_receipt)) {
            throw "Future emergency receipt already exists: $($Authority.future_emergency_receipt)"
        }
    }
}

function Write-JsonAtomic([string]$Path, $Value) {
    $directory = [System.IO.Path]::GetDirectoryName($Path)
    [System.IO.Directory]::CreateDirectory($directory) | Out-Null
    $temporary = "$Path.$([Guid]::NewGuid().ToString('N')).tmp"
    try {
        $json = $Value | ConvertTo-Json -Depth 20
        [System.IO.File]::WriteAllText($temporary, $json + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
        [System.IO.File]::Move($temporary, $Path)
    }
    finally {
        if ([System.IO.File]::Exists($temporary)) {
            [System.IO.File]::Delete($temporary)
        }
    }
}

if ($AuthorizeSingleBlender -and $OfflineContractTest) {
    [Console]::Error.WriteLine('Offline and authorized modes are mutually exclusive.')
    [Environment]::Exit([int]3)
}

if ($OfflineContractTest) {
    $authority = Get-Authority
    $asset = Assert-ManifestBinding $authority
    Assert-FutureNamespacesAbsent $authority $true
    [Console]::Out.WriteLine((@{
        classification = 'PASS_OFFLINE_CONTRACT_TEST'
        asset_id = $asset.id
        authority_records = @($authority.immutable_authorities).Count
        controller_launch_count = 0
        blender_launch_count = 0
        unreal_launch_count = 0
    } | ConvertTo-Json -Compress))
    [Environment]::Exit([int]0)
}

if (-not $AuthorizeSingleBlender) {
    [Console]::Error.WriteLine('Explicit -AuthorizeSingleBlender is required.')
    [Environment]::Exit([int]2)
}

$state = [ordered]@{
    schema = 'skyguard.p0.core-rifle.method05-deterministic-stagea.supervisor-terminal.v1'
    asset_id = $AssetId
    classification = 'FAILED_WITH_EVIDENCE'
    started_at_utc = Get-UtcNow
    ended_at_utc = $null
    authority_sha256 = $ExpectedAuthorityHash
    preflight_passed = $false
    controller_launch_count = 0
    blender_launch_count_expected = 0
    retry_count = 0
    controller_exit_code = $null
    controller_exit_code_type = $null
    failure_stage = 'INITIALIZATION'
    failure_message = $null
    unreal_launched = $false
    external_model_launched = $false
}
$scriptExitCode = [int]1

try {
    $state.failure_stage = 'AUTHORITY_PREFLIGHT'
    $authority = Get-Authority
    $asset = Assert-ManifestBinding $authority
    Assert-FutureNamespacesAbsent $authority $true
    $active = Get-HeavyProcesses
    if ($active.Count -ne 0) {
        throw "Heavy process gate is not clear: $($active.ProcessName -join ', ')"
    }
    $state.preflight_passed = $true

    $state.failure_stage = 'CONTROLLER_EXECUTION'
    $state.controller_launch_count = 1
    $state.blender_launch_count_expected = 1
    & python $ControllerPath run $AssetId
    $controllerExitCode = [int]$LASTEXITCODE
    $state.controller_exit_code = $controllerExitCode
    $state.controller_exit_code_type = $controllerExitCode.GetType().FullName
    if ($controllerExitCode -ne 0) {
        throw "Production controller returned exit code $controllerExitCode."
    }

    $state.failure_stage = $null
    $state.failure_message = $null
    $state.classification = 'PASSED_AUTOMATIC_AWAITING_EXTERNAL_FULL_RESOLUTION_VISUAL_REVIEW'
    $scriptExitCode = [int]0
}
catch {
    $state.failure_message = "$($_.Exception.GetType().FullName): $($_.Exception.Message)"
    $scriptExitCode = [int]1
}
finally {
    $state.ended_at_utc = Get-UtcNow
    try {
        Write-JsonAtomic $TerminalPath $state
    }
    catch {
        $emergency = @{
            schema = 'skyguard.p0.core-rifle.method05-deterministic-stagea.supervisor-emergency.v1'
            at_utc = Get-UtcNow
            terminal_path = $TerminalPath
            error = "$($_.Exception.GetType().FullName): $($_.Exception.Message)"
            state = $state
        } | ConvertTo-Json -Depth 20 -Compress
        [System.IO.File]::AppendAllText($EmergencyPath, $emergency + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
    }
}

[Environment]::Exit($scriptExitCode)
