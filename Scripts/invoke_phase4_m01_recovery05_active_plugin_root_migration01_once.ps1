param(
    [switch]$AuthorizeSingleMigration,
    [switch]$OfflineContractTest
)

$ErrorActionPreference = 'Stop'

$PluginsRoot = 'D:\Skyguard52\Plugins'
$QuarantineRoot = 'D:\Skyguard52\Saved\PluginQuarantine\PHASE4_M01_RECOVERY05_ACTIVE_ROOT_MIGRATION01'
$AttemptRoot = 'D:\Skyguard52\Saved\MigrationAttempts\PHASE4_M01_RECOVERY05_ACTIVE_ROOT_MIGRATION01\attempt_01'
$TerminalManifest = 'D:\Skyguard52\Saved\Reports\PHASE4_M01_RECOVERY05_ACTIVE_PLUGIN_ROOT_MIGRATION01_TERMINAL_MANIFEST.json'
$EmergencyReceipt = 'D:\Skyguard52\Saved\Reports\PHASE4_M01_RECOVERY05_ACTIVE_PLUGIN_ROOT_MIGRATION01_EMERGENCY_RECEIPT.jsonl'
$InventoryPath = 'D:\Skyguard52\Saved\Reports\PHASE4_M01_RECOVERY05_ACTIVE_PLUGIN_ROOT_MIGRATION01_PLUGIN_ROOT_INVENTORY.json'
$ContractPath = 'D:\Skyguard52\Saved\Reports\PHASE4_M01_RECOVERY05_ACTIVE_PLUGIN_ROOT_MIGRATION01_MIGRATION_CONTRACT.json'
$TerminalFreeze = 'D:\Skyguard52\Docs\AAA_Review\PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_RECOVERY04_ATTEMPT01_TERMINAL_FREEZE.json'
$OfflineRoot = [System.IO.Path]::Combine(
    [System.IO.Path]::GetTempPath(),
    'Skyguard52_ActivePluginRootMigration01_OfflineContractTest'
)
$ActiveManifest = if ($OfflineContractTest) {
    [System.IO.Path]::Combine($OfflineRoot, 'terminal_manifest.json')
} else {
    $TerminalManifest
}
$ActiveEmergency = if ($OfflineContractTest) {
    [System.IO.Path]::Combine($OfflineRoot, 'emergency_receipt.jsonl')
} else {
    $EmergencyReceipt
}

$Moves = @(
    [pscustomobject][ordered]@{
        order = 1
        root = 'SkyguardRecovery03NativeRecovery01'
        source = 'D:\Skyguard52\Plugins\SkyguardRecovery03NativeRecovery01'
        destination = 'D:\Skyguard52\Saved\PluginQuarantine\PHASE4_M01_RECOVERY05_ACTIVE_ROOT_MIGRATION01\SkyguardRecovery03NativeRecovery01'
    },
    [pscustomobject][ordered]@{
        order = 2
        root = 'SkyguardRecovery03NativeRecovery04'
        source = 'D:\Skyguard52\Plugins\SkyguardRecovery03NativeRecovery04'
        destination = 'D:\Skyguard52\Saved\PluginQuarantine\PHASE4_M01_RECOVERY05_ACTIVE_ROOT_MIGRATION01\SkyguardRecovery03NativeRecovery04'
    },
    [pscustomobject][ordered]@{
        order = 3
        root = 'SkyguardRecovery03'
        source = 'D:\Skyguard52\Plugins\SkyguardRecovery03'
        destination = 'D:\Skyguard52\Saved\PluginQuarantine\PHASE4_M01_RECOVERY05_ACTIVE_ROOT_MIGRATION01\SkyguardRecovery03'
    }
)

function Get-Sha256 {
    param([string]$Path)
    $hash = [System.Security.Cryptography.SHA256]::Create()
    $stream = $null
    try {
        $stream = [System.IO.File]::Open(
            $Path,
            [System.IO.FileMode]::Open,
            [System.IO.FileAccess]::Read,
            [System.IO.FileShare]::Read
        )
        return [BitConverter]::ToString($hash.ComputeHash($stream)).Replace('-', '').ToLowerInvariant()
    } finally {
        if ($null -ne $stream) { $stream.Dispose() }
        $hash.Dispose()
    }
}

function Assert-File {
    param([string]$Path, [int64]$Bytes, [string]$Sha256)
    $item = New-Object System.IO.FileInfo($Path)
    if (-not $item.Exists) { throw "Missing file: $Path" }
    if ($item.Length -ne $Bytes) { throw "Byte mismatch: $Path" }
    if ((Get-Sha256 $Path) -cne $Sha256) { throw "Hash mismatch: $Path" }
}

function Write-Json {
    param([string]$Path, $Value)
    $parent = [System.IO.Path]::GetDirectoryName($Path)
    if (-not [string]::IsNullOrWhiteSpace($parent)) {
        [void][System.IO.Directory]::CreateDirectory($parent)
    }
    $encoding = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText(
        $Path,
        ($Value | ConvertTo-Json -Depth 30),
        $encoding
    )
}

function Write-Emergency {
    param([string]$Stage, [string]$Message)
    try {
        $parent = [System.IO.Path]::GetDirectoryName($ActiveEmergency)
        [void][System.IO.Directory]::CreateDirectory($parent)
        $record = [ordered]@{
            utc = [DateTime]::UtcNow.ToString('o')
            stage = $Stage
            message = $Message
        }
        $encoding = New-Object System.Text.UTF8Encoding($false)
        [System.IO.File]::AppendAllText(
            $ActiveEmergency,
            ($record | ConvertTo-Json -Compress) + [Environment]::NewLine,
            $encoding
        )
    } catch {
    }
}

function Get-HeavyProcesses {
    $names = @(
        'UnrealEditor', 'UnrealEditor-Cmd', 'ShaderCompileWorker',
        'AutomationTool', 'UnrealBuildTool', 'blender', 'blender-launcher',
        'cl', 'link', 'dotnet'
    )
    return @(
        Get-Process -ErrorAction SilentlyContinue |
            Where-Object { $names -contains $_.ProcessName } |
            Select-Object ProcessName, Id
    )
}

function Get-Inventory {
    Assert-File $InventoryPath 5457 'a8c6e995807a94d6074f2ad6611f6a98e6d7340dd4892498db855077dc574fe2'
    return Get-Content -LiteralPath $InventoryPath -Raw | ConvertFrom-Json
}

function Assert-InventoryAtState {
    param($Inventory, [bool]$Migrated)
    $seen = 0
    foreach ($record in $Inventory.records) {
        $parts = ([string]$record.relative_path).Split('/')
        $root = $parts[0]
        $suffix = ($parts[1..($parts.Count - 1)] -join '\')
        $base = if ($Migrated -and $root -ne 'SkyguardRecovery03NativeRecovery05') {
            [System.IO.Path]::Combine($QuarantineRoot, $root)
        } else {
            [System.IO.Path]::Combine($PluginsRoot, $root)
        }
        $path = [System.IO.Path]::Combine($base, $suffix)
        Assert-File $path ([int64]$record.bytes) ([string]$record.sha256)
        $seen++
    }
    if ($seen -ne 23) { throw "Inventory count mismatch: $seen" }
}

function Assert-InitialDiscoverySet {
    $expected = @(
        'SkyguardRecovery03',
        'SkyguardRecovery03NativeRecovery01',
        'SkyguardRecovery03NativeRecovery04',
        'SkyguardRecovery03NativeRecovery05'
    )
    $actual = @(
        [System.IO.Directory]::EnumerateDirectories($PluginsRoot) |
            ForEach-Object { [System.IO.Path]::GetFileName($_) } |
            Sort-Object
    )
    if (($actual -join '|') -cne (($expected | Sort-Object) -join '|')) {
        throw "Initial plugin discovery set mismatch: $($actual -join ', ')"
    }
}

function Assert-FinalDiscoverySet {
    $actual = @(
        [System.IO.Directory]::EnumerateDirectories($PluginsRoot) |
            ForEach-Object { [System.IO.Path]::GetFileName($_) } |
            Sort-Object
    )
    if (($actual -join '|') -cne 'SkyguardRecovery03NativeRecovery05') {
        throw "Final plugin discovery set mismatch: $($actual -join ', ')"
    }
    $descriptor = [System.IO.Path]::Combine(
        $PluginsRoot,
        'SkyguardRecovery03NativeRecovery05',
        'SkyguardRecovery03NativeRecovery05.uplugin'
    )
    $json = Get-Content -LiteralPath $descriptor -Raw | ConvertFrom-Json
    if ([bool]$json.EnabledByDefault) {
        throw 'Selected Recovery05 plugin unexpectedly enabled by default.'
    }
    $moduleNames = @($json.Modules | ForEach-Object { [string]$_.Name })
    if ($moduleNames.Count -ne 1 -or
        $moduleNames[0] -cne 'SkyguardRecovery03NativeRecovery05') {
        throw 'Selected Recovery05 module identity mismatch.'
    }
}

function Invoke-OfflineContractTest {
    if ([System.IO.Directory]::Exists($OfflineRoot) -or
        [System.IO.File]::Exists($OfflineRoot)) {
        throw "Offline test namespace exists: $OfflineRoot"
    }
    [void][System.IO.Directory]::CreateDirectory($OfflineRoot)
    Assert-File $ContractPath 2938 '4a1a728ed11ebc9eda69b5be92ad1cb3729eb5ca6d2c87681acd662d88b58a02'
    Assert-File $TerminalFreeze 5005 'f23f8858ff4e0b65735cd498e022c7dcc32a0755b13a23f18f878ab363002aa5'
    $inventory = Get-Inventory
    Assert-InventoryAtState $inventory $false
    Assert-InitialDiscoverySet
    if (@(Get-HeavyProcesses).Count -ne 0) { throw 'Heavy process active during offline test.' }
    foreach ($path in @($QuarantineRoot, $AttemptRoot, $TerminalManifest, $EmergencyReceipt)) {
        if ([System.IO.Directory]::Exists($path) -or [System.IO.File]::Exists($path)) {
            throw "Governed future namespace exists: $path"
        }
    }
    if ($Moves.Count -ne 3) { throw 'Migration move count mismatch.' }
    if ((@($Moves | Group-Object root | Where-Object { $_.Count -gt 1 })).Count -ne 0) {
        throw 'Duplicate migration root.'
    }
    return [ordered]@{
        inventory_records_verified = 23
        move_count = 3
        unique_move_roots = 3
        governed_namespaces_created = 0
        directory_move_count = 0
        build_launch_count = 0
        unreal_launch_count = 0
        blender_launch_count = 0
    }
}

$State = [ordered]@{
    schema = 'skyguard.phase4.m01-recovery05-active-plugin-root-migration01-terminal.v1'
    classification = 'FAILED_WITH_EVIDENCE'
    started_utc = [DateTime]::UtcNow.ToString('o')
    ended_utc = $null
    authorization_present = [bool]$AuthorizeSingleMigration
    offline_contract_test = [bool]$OfflineContractTest
    offline_result = $null
    preflight_passed = $false
    attempt_namespace_created = $false
    quarantine_namespace_created = $false
    move_count = 0
    moved_roots = @()
    rollback_attempted = $false
    rollback_complete = $false
    retry_count = 0
    delete_count = 0
    overwrite_count = 0
    copy_count = 0
    build_launch_count = 0
    unreal_launch_count = 0
    blender_launch_count = 0
    failure_stage = $null
    failure_message = $null
}
$ManifestWritten = $false
$Moved = New-Object System.Collections.ArrayList

try {
    if ($OfflineContractTest) {
        $State.offline_result = Invoke-OfflineContractTest
        $State.classification = 'PASSED_OFFLINE_CONTRACT_TEST'
    } else {
        if (-not $AuthorizeSingleMigration) { throw 'Explicit migration authorization missing.' }
        Assert-File $ContractPath 2938 '4a1a728ed11ebc9eda69b5be92ad1cb3729eb5ca6d2c87681acd662d88b58a02'
        Assert-File $TerminalFreeze 5005 'f23f8858ff4e0b65735cd498e022c7dcc32a0755b13a23f18f878ab363002aa5'
        $inventory = Get-Inventory
        Assert-InventoryAtState $inventory $false
        Assert-InitialDiscoverySet
        if (@(Get-HeavyProcesses).Count -ne 0) { throw 'Heavy process active.' }
        foreach ($path in @($QuarantineRoot, $AttemptRoot, $TerminalManifest, $EmergencyReceipt)) {
            if ([System.IO.Directory]::Exists($path) -or [System.IO.File]::Exists($path)) {
                throw "Governed namespace exists: $path"
            }
        }
        foreach ($move in $Moves) {
            if (-not [System.IO.Directory]::Exists($move.source)) {
                throw "Migration source missing: $($move.source)"
            }
            if ([System.IO.Directory]::Exists($move.destination) -or
                [System.IO.File]::Exists($move.destination)) {
                throw "Migration destination collision: $($move.destination)"
            }
        }
        $State.preflight_passed = $true
        [void][System.IO.Directory]::CreateDirectory($AttemptRoot)
        $State.attempt_namespace_created = $true
        [void][System.IO.Directory]::CreateDirectory($QuarantineRoot)
        $State.quarantine_namespace_created = $true

        foreach ($move in $Moves) {
            $State.failure_stage = "move_$($move.order)_$($move.root)"
            [System.IO.Directory]::Move($move.source, $move.destination)
            [void]$Moved.Add($move)
            $State.move_count = $Moved.Count
            $State.moved_roots = @($Moved | ForEach-Object { $_.root })
        }

        Assert-InventoryAtState $inventory $true
        Assert-FinalDiscoverySet
        $State.failure_stage = $null
        $State.classification = 'PASSED_CONTROLLED_ACTIVE_PLUGIN_ROOT_MIGRATION_COMPLETE'
    }
} catch {
    $State.failure_message = $_.Exception.Message
    if (-not $OfflineContractTest -and $Moved.Count -gt 0) {
        $State.rollback_attempted = $true
        try {
            for ($index = $Moved.Count - 1; $index -ge 0; $index--) {
                $move = $Moved[$index]
                if ([System.IO.Directory]::Exists($move.source) -or
                    -not [System.IO.Directory]::Exists($move.destination)) {
                    throw "Automatic rollback path state invalid: $($move.root)"
                }
                [System.IO.Directory]::Move($move.destination, $move.source)
            }
            $State.rollback_complete = $true
        } catch {
            $State.rollback_complete = $false
            $State.failure_message += " | rollback: $($_.Exception.Message)"
        }
    }
    $State.classification = 'FAILED_WITH_EVIDENCE'
} finally {
    $State.ended_utc = [DateTime]::UtcNow.ToString('o')
    try {
        Write-Json $ActiveManifest $State
        $ManifestWritten = $true
    } catch {
        Write-Emergency 'terminal_manifest' $_.Exception.Message
    }
}

if (-not $ManifestWritten) { exit 1 }
if ($State.classification -in @(
    'PASSED_OFFLINE_CONTRACT_TEST',
    'PASSED_CONTROLLED_ACTIVE_PLUGIN_ROOT_MIGRATION_COMPLETE'
)) { exit 0 }
exit 1
