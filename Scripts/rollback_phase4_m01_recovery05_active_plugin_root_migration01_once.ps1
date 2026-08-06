param([switch]$AuthorizeRollback)

$ErrorActionPreference = 'Stop'
$PluginsRoot = 'D:\Skyguard52\Plugins'
$QuarantineRoot = 'D:\Skyguard52\Saved\PluginQuarantine\PHASE4_M01_RECOVERY05_ACTIVE_ROOT_MIGRATION01'
$AttemptRoot = 'D:\Skyguard52\Saved\MigrationAttempts\PHASE4_M01_RECOVERY05_ACTIVE_ROOT_MIGRATION01\rollback_attempt_01'
$TerminalManifest = 'D:\Skyguard52\Saved\Reports\PHASE4_M01_RECOVERY05_ACTIVE_PLUGIN_ROOT_MIGRATION01_ROLLBACK_TERMINAL_MANIFEST.json'
$InventoryPath = 'D:\Skyguard52\Saved\Reports\PHASE4_M01_RECOVERY05_ACTIVE_PLUGIN_ROOT_MIGRATION01_PLUGIN_ROOT_INVENTORY.json'

$Moves = @(
    [pscustomobject][ordered]@{root='SkyguardRecovery03';source="$QuarantineRoot\SkyguardRecovery03";destination="$PluginsRoot\SkyguardRecovery03"},
    [pscustomobject][ordered]@{root='SkyguardRecovery03NativeRecovery04';source="$QuarantineRoot\SkyguardRecovery03NativeRecovery04";destination="$PluginsRoot\SkyguardRecovery03NativeRecovery04"},
    [pscustomobject][ordered]@{root='SkyguardRecovery03NativeRecovery01';source="$QuarantineRoot\SkyguardRecovery03NativeRecovery01";destination="$PluginsRoot\SkyguardRecovery03NativeRecovery01"}
)

function Get-Sha256 {
    param([string]$Path)
    $hash = [System.Security.Cryptography.SHA256]::Create()
    $stream = $null
    try {
        $stream = [System.IO.File]::OpenRead($Path)
        return [BitConverter]::ToString($hash.ComputeHash($stream)).Replace('-', '').ToLowerInvariant()
    } finally {
        if ($null -ne $stream) { $stream.Dispose() }
        $hash.Dispose()
    }
}

function Assert-File {
    param([string]$Path, [int64]$Bytes, [string]$Sha256)
    $item = New-Object System.IO.FileInfo($Path)
    if (-not $item.Exists -or $item.Length -ne $Bytes -or
        (Get-Sha256 $Path) -cne $Sha256) {
        throw "Rollback file authority mismatch: $Path"
    }
}

function Write-Json {
    param([string]$Path, $Value)
    [void][System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName($Path))
    $encoding = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path, ($Value | ConvertTo-Json -Depth 30), $encoding)
}

function Get-HeavyProcesses {
    $names = @('UnrealEditor','UnrealEditor-Cmd','ShaderCompileWorker','AutomationTool','UnrealBuildTool','blender','blender-launcher','cl','link','dotnet')
    return @(Get-Process -ErrorAction SilentlyContinue | Where-Object { $names -contains $_.ProcessName })
}

$State = [ordered]@{
    schema = 'skyguard.phase4.m01-recovery05-active-plugin-root-migration01-rollback-terminal.v1'
    classification = 'FAILED_WITH_EVIDENCE'
    started_utc = [DateTime]::UtcNow.ToString('o')
    ended_utc = $null
    authorization_present = [bool]$AuthorizeRollback
    moved_roots = @()
    move_count = 0
    retry_count = 0
    delete_count = 0
    overwrite_count = 0
    copy_count = 0
    build_launch_count = 0
    unreal_launch_count = 0
    blender_launch_count = 0
    failure_message = $null
}
$Moved = New-Object System.Collections.ArrayList

try {
    if (-not $AuthorizeRollback) { throw 'Explicit rollback authorization missing.' }
    Assert-File $InventoryPath 5457 'a8c6e995807a94d6074f2ad6611f6a98e6d7340dd4892498db855077dc574fe2'
    if (@(Get-HeavyProcesses).Count -ne 0) { throw 'Heavy process active.' }
    if ([System.IO.Directory]::Exists($AttemptRoot) -or [System.IO.File]::Exists($TerminalManifest)) {
        throw 'Fresh rollback namespace unavailable.'
    }
    foreach ($move in $Moves) {
        if (-not [System.IO.Directory]::Exists($move.source) -or
            [System.IO.Directory]::Exists($move.destination) -or
            [System.IO.File]::Exists($move.destination)) {
            throw "Rollback path state invalid: $($move.root)"
        }
    }
    $inventory = Get-Content -LiteralPath $InventoryPath -Raw | ConvertFrom-Json
    foreach ($record in $inventory.records) {
        $parts = ([string]$record.relative_path).Split('/')
        $root = $parts[0]
        $suffix = ($parts[1..($parts.Count - 1)] -join '\')
        $base = if ($root -eq 'SkyguardRecovery03NativeRecovery05') {
            "$PluginsRoot\$root"
        } else {
            "$QuarantineRoot\$root"
        }
        Assert-File ([System.IO.Path]::Combine($base, $suffix)) ([int64]$record.bytes) ([string]$record.sha256)
    }
    [void][System.IO.Directory]::CreateDirectory($AttemptRoot)
    foreach ($move in $Moves) {
        [System.IO.Directory]::Move($move.source, $move.destination)
        [void]$Moved.Add($move)
        $State.move_count = $Moved.Count
        $State.moved_roots = @($Moved | ForEach-Object { $_.root })
    }
    foreach ($record in $inventory.records) {
        $path = [System.IO.Path]::Combine($PluginsRoot, ([string]$record.relative_path).Replace('/', '\'))
        Assert-File $path ([int64]$record.bytes) ([string]$record.sha256)
    }
    $State.classification = 'PASSED_CONTROLLED_PLUGIN_ROOT_ROLLBACK_COMPLETE'
} catch {
    $State.failure_message = $_.Exception.Message
    if ($Moved.Count -gt 0) {
        for ($index = $Moved.Count - 1; $index -ge 0; $index--) {
            $move = $Moved[$index]
            if ([System.IO.Directory]::Exists($move.destination) -and
                -not [System.IO.Directory]::Exists($move.source)) {
                [System.IO.Directory]::Move($move.destination, $move.source)
            }
        }
    }
    $State.classification = 'FAILED_WITH_EVIDENCE'
} finally {
    $State.ended_utc = [DateTime]::UtcNow.ToString('o')
    try { Write-Json $TerminalManifest $State } catch {}
}

if ($State.classification -eq 'PASSED_CONTROLLED_PLUGIN_ROOT_ROLLBACK_COMPLETE') { exit 0 }
exit 1
