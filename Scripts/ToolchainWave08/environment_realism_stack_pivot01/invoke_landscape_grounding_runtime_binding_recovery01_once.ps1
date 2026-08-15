param(
    [switch]$AuthorizeSingleBinding,
    [switch]$OfflineContractTest
)

$ErrorActionPreference = 'Stop'
$ProjectRoot = 'D:\Skyguard52'
$ContractPath = Join-Path $ProjectRoot 'Docs\Toolchain\ToolchainWave08\M01LandscapeGroundingBridge01\runtime_binding_recovery01_contract.json'
$StandingAuthorityPath = Join-Path $ProjectRoot 'Production\standing_heavy_process_authorization.json'
$AttemptRoot = Join-Path $ProjectRoot 'Saved\BuildAttempts\M01_LANDSCAPE_GROUNDING_BRIDGE01_RUNTIME_BINDING_RECOVERY01\attempt_01'
$TerminalPath = Join-Path $ProjectRoot 'Saved\Reports\M01_LANDSCAPE_GROUNDING_BRIDGE01_RUNTIME_BINDING_RECOVERY01_TERMINAL_MANIFEST.json'
$SourceRoot = 'D:\SG52M01GROUND01\Binaries\Win64'
$TargetRoot = 'D:\SG52T08_ENV01\Binaries\Win64'
$MoveFlags = 0x00000001 -bor 0x00000008

if (-not ('SkyguardMoveFileExRecovery01' -as [type])) {
    Add-Type -TypeDefinition @'
using System;
using System.ComponentModel;
using System.Runtime.InteropServices;
public static class SkyguardMoveFileExRecovery01
{
    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern bool MoveFileEx(string existingFileName, string newFileName, int flags);
    public static void Replace(string source, string destination, int flags)
    {
        if (!MoveFileEx(source, destination, flags))
            throw new Win32Exception(Marshal.GetLastWin32Error());
    }
}
'@
}

function Get-Sha256([string]$Path) {
    $stream = $null
    $sha = $null
    try {
        $stream = [System.IO.File]::Open($Path, 'Open', 'Read', 'Read')
        $sha = [System.Security.Cryptography.SHA256]::Create()
        return ([BitConverter]::ToString($sha.ComputeHash($stream))).Replace('-', '').ToLowerInvariant()
    }
    finally {
        if ($null -ne $sha) { $sha.Dispose() }
        if ($null -ne $stream) { $stream.Dispose() }
    }
}

function Get-Record([string]$Path) {
    $item = Get-Item -LiteralPath $Path
    return [ordered]@{path=$item.FullName;bytes=[int64]$item.Length;sha256=Get-Sha256 $item.FullName;last_write_utc=$item.LastWriteTimeUtc.ToString('o')}
}

function Assert-Record([string]$Path, [object]$Expected) {
    if (-not [IO.File]::Exists($Path)) { throw "Missing file: $Path" }
    $actual = Get-Record $Path
    if ($actual.bytes -ne [int64]$Expected.bytes -or $actual.sha256 -ne [string]$Expected.sha256) { throw "Authority mismatch: $Path" }
    return $actual
}

function Write-JsonAtomic([string]$Path, [object]$Value) {
    $parent = Split-Path -Parent $Path
    if (-not [IO.Directory]::Exists($parent)) { [IO.Directory]::CreateDirectory($parent) | Out-Null }
    $temporary = $Path + '.tmp'
    [IO.File]::WriteAllText($temporary, ($Value | ConvertTo-Json -Depth 12) + [Environment]::NewLine, [Text.UTF8Encoding]::new($false))
    [SkyguardMoveFileExRecovery01]::Replace($temporary, $Path, $MoveFlags)
}

function Assert-NoHeavyProcess {
    $heavy = @(Get-Process -ErrorAction SilentlyContinue | Where-Object {
        $_.ProcessName -match '^(UnrealEditor|UnrealEditor-Cmd|ShaderCompileWorker|AutomationTool|UnrealBuildTool|blender|cl|link)$'
    })
    if ($heavy.Count -ne 0) { throw "A governed heavy process is active: $($heavy.ProcessName -join ', ')" }
}

function Test-MoveFileExFixture {
    $root = Join-Path ([IO.Path]::GetTempPath()) ('skyguard-binding-recovery01-' + [Guid]::NewGuid().ToString('N'))
    [IO.Directory]::CreateDirectory($root) | Out-Null
    try {
        $source = Join-Path $root 'source.bin'
        $target = Join-Path $root 'target.bin'
        [IO.File]::WriteAllText($source, 'new')
        [IO.File]::WriteAllText($target, 'old')
        [SkyguardMoveFileExRecovery01]::Replace($source, $target, $MoveFlags)
        if ([IO.File]::Exists($source)) { throw 'MoveFileEx fixture source still exists.' }
        if ([IO.File]::ReadAllText($target) -ne 'new') { throw 'MoveFileEx fixture target content mismatch.' }
        return [ordered]@{passed=$true;api='MoveFileExW';flags=$MoveFlags}
    }
    finally {
        if ([IO.Directory]::Exists($root)) { [IO.Directory]::Delete($root, $true) }
    }
}

$State = [ordered]@{
    schema='skyguard.m01-landscape-grounding-bridge01.runtime-binding-recovery01-terminal.v1'
    classification='FAILED_WITH_EVIDENCE'
    started_utc=[DateTime]::UtcNow.ToString('o')
    ended_utc=$null
    stage='initializing'
    authorization_present=[bool]$AuthorizeSingleBinding
    offline_contract_test=[bool]$OfflineContractTest
    standing_authorization_verified=$false
    preflight_passed=$false
    movefileex_fixture=$null
    binding_execution_count=0
    replace_count=0
    child_process_launch_count=0
    unreal_launch_count=0
    blender_launch_count=0
    retry_count=0
    rollback_required=$false
    rollback_performed=$false
    source_records=@()
    target_pre_records=@()
    backup_records=@()
    target_post_records=@()
    failure=$null
}

try {
    if ($OfflineContractTest -and $AuthorizeSingleBinding) { throw 'Offline and authorized modes are mutually exclusive.' }
    $contract = Get-Content -LiteralPath $ContractPath -Raw | ConvertFrom-Json
    $standing = Get-Content -LiteralPath $StandingAuthorityPath -Raw | ConvertFrom-Json
    if ($standing.status -ne 'ACTIVE' -or $standing.execution_policy.per_run_user_authorization_required -ne $false) { throw 'Standing authorization is not active.' }
    $State.standing_authorization_verified = $true
    Assert-NoHeavyProcess
    foreach ($entry in $contract.source_files) { $State.source_records += Assert-Record (Join-Path $SourceRoot $entry.name) $entry }
    foreach ($entry in $contract.pre_binding_target_files) { $State.target_pre_records += Assert-Record (Join-Path $TargetRoot $entry.name) $entry }
    if ([IO.Directory]::Exists($AttemptRoot) -or [IO.File]::Exists($TerminalPath)) { throw 'Recovery01 namespace is not fresh.' }
    if ([IO.Path]::GetPathRoot($SourceRoot) -ne [IO.Path]::GetPathRoot($TargetRoot)) { throw 'Source and target must be on the same volume.' }
    $State.movefileex_fixture = Test-MoveFileExFixture
    $State.preflight_passed = $true
    if ($OfflineContractTest) {
        $State.stage='offline_complete';$State.classification='PASSED_OFFLINE_CONTRACT_TEST';$State.ended_utc=[DateTime]::UtcNow.ToString('o')
        $State | ConvertTo-Json -Depth 12
        [Environment]::Exit([int]0)
    }
    if (-not $AuthorizeSingleBinding) { throw 'Mechanical -AuthorizeSingleBinding guard is required.' }

    [IO.Directory]::CreateDirectory($AttemptRoot) | Out-Null
    $backupRoot = Join-Path $AttemptRoot 'rollback'
    $stageRoot = Join-Path $AttemptRoot 'stage'
    [IO.Directory]::CreateDirectory($backupRoot) | Out-Null
    [IO.Directory]::CreateDirectory($stageRoot) | Out-Null
    $State.stage='backing_up'
    foreach ($entry in $contract.pre_binding_target_files) {
        $target = Join-Path $TargetRoot $entry.name
        $backup = Join-Path $backupRoot $entry.name
        [IO.File]::Copy($target, $backup, $false)
        $State.backup_records += Assert-Record $backup $entry
    }
    $State.stage='staging'
    foreach ($entry in $contract.source_files) {
        $source = Join-Path $SourceRoot $entry.name
        $staged = Join-Path $stageRoot $entry.name
        [IO.File]::Copy($source, $staged, $false)
        [void](Assert-Record $staged $entry)
    }
    $State.stage='binding';$State.binding_execution_count=1;$State.rollback_required=$true
    foreach ($entry in $contract.source_files) {
        [SkyguardMoveFileExRecovery01]::Replace((Join-Path $stageRoot $entry.name),(Join-Path $TargetRoot $entry.name),$MoveFlags)
        $State.replace_count++
    }
    foreach ($entry in $contract.source_files) { $State.target_post_records += Assert-Record (Join-Path $TargetRoot $entry.name) $entry }
    if ($State.replace_count -ne 3) { throw 'Replace count is not exactly three.' }
    $State.rollback_required=$false;$State.stage='complete';$State.classification='PASSED_GROUNDING_BRIDGE_BOUND_READY_FOR_RUNTIME_PROBE'
}
catch {
    $State.failure=[ordered]@{stage=$State.stage;message=$_.Exception.Message;type=$_.Exception.GetType().FullName}
    if ($State.rollback_required -and [IO.Directory]::Exists((Join-Path $AttemptRoot 'rollback'))) {
        try {
            foreach ($entry in $contract.pre_binding_target_files) {
                $backup = Join-Path (Join-Path $AttemptRoot 'rollback') $entry.name
                $restoreStage = Join-Path $AttemptRoot ('restore-' + $entry.name)
                [IO.File]::Copy($backup, $restoreStage, $true)
                [SkyguardMoveFileExRecovery01]::Replace($restoreStage,(Join-Path $TargetRoot $entry.name),$MoveFlags)
            }
            $State.rollback_performed=$true
        } catch { $State.failure.rollback_error=$_.Exception.Message }
    }
}
finally {
    $State.ended_utc=[DateTime]::UtcNow.ToString('o')
    if (-not $OfflineContractTest) {
        Write-JsonAtomic $TerminalPath $State
        if ([IO.Directory]::Exists($AttemptRoot)) { Write-JsonAtomic (Join-Path $AttemptRoot 'terminal.json') $State }
    }
}

if ($State.classification -eq 'PASSED_GROUNDING_BRIDGE_BOUND_READY_FOR_RUNTIME_PROBE') { [Environment]::Exit([int]0) }
[Environment]::Exit([int]1)
