param(
    [switch]$AuthorizeSingleBinding,
    [switch]$OfflineContractTest
)

$ErrorActionPreference = 'Stop'
$ProjectRoot = 'D:\Skyguard52'
$ContractPath = Join-Path $ProjectRoot 'Docs\Toolchain\ToolchainWave08\M01LandscapeGroundingBridge01\runtime_binding_contract.json'
$StandingAuthorityPath = Join-Path $ProjectRoot 'Production\standing_heavy_process_authorization.json'
$AttemptRoot = Join-Path $ProjectRoot 'Saved\BuildAttempts\M01_LANDSCAPE_GROUNDING_BRIDGE01_RUNTIME_BINDING\attempt_01'
$TerminalPath = Join-Path $ProjectRoot 'Saved\Reports\M01_LANDSCAPE_GROUNDING_BRIDGE01_RUNTIME_BINDING_TERMINAL_MANIFEST.json'
$SourceRoot = 'D:\SG52M01GROUND01\Binaries\Win64'
$TargetRoot = 'D:\SG52T08_ENV01\Binaries\Win64'

function Get-Sha256([string]$Path) {
    $stream = $null
    $sha = $null
    try {
        $stream = [System.IO.File]::Open($Path, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::Read)
        $sha = [System.Security.Cryptography.SHA256]::Create()
        return ([System.BitConverter]::ToString($sha.ComputeHash($stream))).Replace('-', '').ToLowerInvariant()
    }
    finally {
        if ($null -ne $sha) { $sha.Dispose() }
        if ($null -ne $stream) { $stream.Dispose() }
    }
}

function Get-FileRecord([string]$Path) {
    $item = Get-Item -LiteralPath $Path
    return [ordered]@{
        path = $item.FullName
        bytes = [int64]$item.Length
        sha256 = Get-Sha256 $item.FullName
        last_write_utc = $item.LastWriteTimeUtc.ToString('o')
    }
}

function Assert-FileRecord([string]$Path, [object]$Expected) {
    if (-not [System.IO.File]::Exists($Path)) { throw "Missing required file: $Path" }
    $actual = Get-FileRecord $Path
    if ($actual.bytes -ne [int64]$Expected.bytes) { throw "Byte mismatch: $Path" }
    if ($actual.sha256 -ne [string]$Expected.sha256) { throw "SHA-256 mismatch: $Path" }
    return $actual
}

function Get-HeavyProcesses {
    return @(Get-Process -ErrorAction SilentlyContinue | Where-Object {
        $_.ProcessName -match '^(UnrealEditor|UnrealEditor-Cmd|ShaderCompileWorker|AutomationTool|UnrealBuildTool|blender|cl|link)$'
    } | ForEach-Object {
        [ordered]@{ pid = $_.Id; process_name = $_.ProcessName; path = $_.Path }
    })
}

function Write-JsonAtomic([string]$Path, [object]$Value) {
    $parent = Split-Path -Parent $Path
    if (-not [System.IO.Directory]::Exists($parent)) { [System.IO.Directory]::CreateDirectory($parent) | Out-Null }
    $temporary = $Path + '.tmp'
    $json = $Value | ConvertTo-Json -Depth 12
    [System.IO.File]::WriteAllText($temporary, $json + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
    [System.IO.File]::Move($temporary, $Path)
}

$State = [ordered]@{
    schema = 'skyguard.m01-landscape-grounding-bridge01.runtime-binding-terminal.v1'
    classification = 'FAILED_WITH_EVIDENCE'
    started_utc = [DateTime]::UtcNow.ToString('o')
    ended_utc = $null
    stage = 'initializing'
    authorization_present = [bool]$AuthorizeSingleBinding
    offline_contract_test = [bool]$OfflineContractTest
    standing_authorization_verified = $false
    preflight_passed = $false
    binding_execution_count = 0
    copy_count = 0
    child_process_launch_count = 0
    unreal_launch_count = 0
    blender_launch_count = 0
    retry_count = 0
    rollback_required = $false
    rollback_performed = $false
    source_records = @()
    target_pre_records = @()
    backup_records = @()
    target_post_records = @()
    failure = $null
}

try {
    if ($OfflineContractTest -and $AuthorizeSingleBinding) { throw 'Offline and authorized modes are mutually exclusive.' }
    $contract = Get-Content -LiteralPath $ContractPath -Raw | ConvertFrom-Json
    $standing = Get-Content -LiteralPath $StandingAuthorityPath -Raw | ConvertFrom-Json
    if ($standing.status -ne 'ACTIVE' -or $standing.execution_policy.per_run_user_authorization_required -ne $false) {
        throw 'Standing Blender/Unreal authorization is not active.'
    }
    $State.standing_authorization_verified = $true
    if ((Get-HeavyProcesses).Count -ne 0) { throw 'A governed heavy process is active.' }
    foreach ($entry in $contract.source_files) {
        $State.source_records += Assert-FileRecord (Join-Path $SourceRoot $entry.name) $entry
    }
    foreach ($entry in $contract.pre_binding_target_files) {
        $State.target_pre_records += Assert-FileRecord (Join-Path $TargetRoot $entry.name) $entry
    }
    if ([System.IO.Directory]::Exists($AttemptRoot)) { throw 'Fresh binding attempt namespace is not absent.' }
    if ([System.IO.File]::Exists($TerminalPath)) { throw 'Fresh binding terminal manifest is not absent.' }
    $State.preflight_passed = $true
    if ($OfflineContractTest) {
        $State.stage = 'offline_complete'
        $State.classification = 'PASSED_OFFLINE_CONTRACT_TEST'
        $State.ended_utc = [DateTime]::UtcNow.ToString('o')
        $State | ConvertTo-Json -Depth 12
        [Environment]::Exit([int]0)
    }
    if (-not $AuthorizeSingleBinding) { throw 'Mechanical -AuthorizeSingleBinding guard is required.' }

    [System.IO.Directory]::CreateDirectory($AttemptRoot) | Out-Null
    $backupRoot = Join-Path $AttemptRoot 'rollback'
    $stageRoot = Join-Path $AttemptRoot 'stage'
    [System.IO.Directory]::CreateDirectory($backupRoot) | Out-Null
    [System.IO.Directory]::CreateDirectory($stageRoot) | Out-Null
    $State.stage = 'backing_up'
    foreach ($entry in $contract.pre_binding_target_files) {
        $source = Join-Path $TargetRoot $entry.name
        $backup = Join-Path $backupRoot $entry.name
        [System.IO.File]::Copy($source, $backup, $false)
        $record = Assert-FileRecord $backup $entry
        $State.backup_records += $record
    }

    $State.stage = 'staging'
    foreach ($entry in $contract.source_files) {
        $source = Join-Path $SourceRoot $entry.name
        $staged = Join-Path $stageRoot $entry.name
        [System.IO.File]::Copy($source, $staged, $false)
        [void](Assert-FileRecord $staged $entry)
    }

    $State.stage = 'binding'
    $State.binding_execution_count = 1
    $State.rollback_required = $true
    foreach ($entry in $contract.source_files) {
        $staged = Join-Path $stageRoot $entry.name
        $target = Join-Path $TargetRoot $entry.name
        [System.IO.File]::Replace($staged, $target, $null, $true)
        $State.copy_count++
    }
    foreach ($entry in $contract.source_files) {
        $State.target_post_records += Assert-FileRecord (Join-Path $TargetRoot $entry.name) $entry
    }
    if ($State.copy_count -ne 3) { throw 'Binding copy count is not exactly three.' }
    $State.rollback_required = $false
    $State.stage = 'complete'
    $State.classification = 'PASSED_GROUNDING_BRIDGE_BOUND_READY_FOR_RUNTIME_PROBE'
}
catch {
    $State.failure = [ordered]@{ stage = $State.stage; message = $_.Exception.Message; type = $_.Exception.GetType().FullName }
    if ($State.rollback_required -and [System.IO.Directory]::Exists((Join-Path $AttemptRoot 'rollback'))) {
        try {
            foreach ($entry in $contract.pre_binding_target_files) {
                $backup = Join-Path (Join-Path $AttemptRoot 'rollback') $entry.name
                $target = Join-Path $TargetRoot $entry.name
                if ([System.IO.File]::Exists($backup)) { [System.IO.File]::Copy($backup, $target, $true) }
            }
            $State.rollback_performed = $true
        }
        catch {
            $State.failure.rollback_error = $_.Exception.Message
        }
    }
}
finally {
    $State.ended_utc = [DateTime]::UtcNow.ToString('o')
    if (-not $OfflineContractTest) {
        Write-JsonAtomic $TerminalPath $State
        if ([System.IO.Directory]::Exists($AttemptRoot)) { Write-JsonAtomic (Join-Path $AttemptRoot 'terminal.json') $State }
    }
}

if ($State.classification -ne 'PASSED_GROUNDING_BRIDGE_BOUND_READY_FOR_RUNTIME_PROBE') { [Environment]::Exit([int]1) }
[Environment]::Exit([int]0)
