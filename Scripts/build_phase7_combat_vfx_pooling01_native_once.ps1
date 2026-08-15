[CmdletBinding()]
param(
    [switch]$AuthorizeSingleBuild,
    [switch]$OfflineContractTest
)

$ErrorActionPreference = 'Stop'

$SourceRoot = 'D:\Skyguard52'
$ViewRoot = 'D:\SG52P7VFX01'
$AttemptRoot = 'D:\Skyguard52\Saved\BuildAttempts\PHASE7_COMBAT_VFX_POOLING01_NATIVE_BUILD\attempt_01'
$TerminalManifest = 'D:\Skyguard52\Saved\Reports\PHASE7_COMBAT_VFX_POOLING01_NATIVE_BUILD_TERMINAL_MANIFEST.json'
$EmergencyReceipt = 'D:\Skyguard52\Saved\Reports\PHASE7_COMBAT_VFX_POOLING01_NATIVE_BUILD_EMERGENCY_RECEIPT.jsonl'
$InputInventory = 'D:\Skyguard52\Saved\Reports\PHASE7_COMBAT_VFX_POOLING01_NATIVE_BUILD_INPUT_INVENTORY.json'
$OfflineValidation = 'D:\Skyguard52\Saved\Reports\PHASE7_COMBAT_VFX_POOLING01_OFFLINE_VALIDATION.json'
$PostchangeInventory = 'D:\Skyguard52\Saved\Reports\PHASE7_COMBAT_VFX_POOLING01_POSTCHANGE_INVENTORY.json'
$DotNet = 'D:\UE_5.8\Engine\Binaries\ThirdParty\DotNet\10.0\win-x64\dotnet.exe'
$UnrealBuildTool = 'D:\UE_5.8\Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.dll'
$WorkingDirectory = 'D:\UE_5.8\Engine\Binaries\DotNET\UnrealBuildTool'
$TimeoutSeconds = 1200
$BuildArguments = @(
    $UnrealBuildTool,
    'Skyguard52Editor',
    'Win64',
    'Development',
    '-Project=D:\SG52P7VFX01\Skyguard52.uproject',
    '-WaitMutex',
    '-NoHotReloadFromIDE'
)

function Get-Sha256 {
    param([Parameter(Mandatory = $true)][string]$Path)
    if (-not [System.IO.File]::Exists($Path)) {
        throw "Missing file: $Path"
    }
    $stream = $null
    $algorithm = $null
    try {
        $stream = New-Object System.IO.FileStream(
            $Path,
            [System.IO.FileMode]::Open,
            [System.IO.FileAccess]::Read,
            [System.IO.FileShare]::Read
        )
        $algorithm = [System.Security.Cryptography.SHA256]::Create()
        $digest = $algorithm.ComputeHash($stream)
        $builder = New-Object System.Text.StringBuilder
        foreach ($item in $digest) {
            [void]$builder.Append($item.ToString('x2'))
        }
        return $builder.ToString()
    } finally {
        if ($null -ne $algorithm) { $algorithm.Dispose() }
        if ($null -ne $stream) { $stream.Dispose() }
    }
}

function Get-FileRecord {
    param([Parameter(Mandatory = $true)][string]$Path)
    $item = New-Object System.IO.FileInfo($Path)
    if (-not $item.Exists) {
        throw "Missing file: $Path"
    }
    return [ordered]@{
        path = $Path
        bytes = [long]$item.Length
        sha256 = Get-Sha256 $Path
        last_write_utc = $item.LastWriteTimeUtc.ToString('o')
    }
}

function Assert-File {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][long]$Bytes,
        [Parameter(Mandatory = $true)][string]$Sha256
    )
    $record = Get-FileRecord $Path
    if ($record.bytes -ne $Bytes) {
        throw "Byte mismatch: $Path"
    }
    if ($record.sha256 -cne $Sha256) {
        throw "SHA-256 mismatch: $Path"
    }
    return $record
}

function Write-Json {
    param([string]$Path, $Value, [int]$Depth = 30)
    $parent = [System.IO.Path]::GetDirectoryName($Path)
    if (-not [string]::IsNullOrWhiteSpace($parent)) {
        [void][System.IO.Directory]::CreateDirectory($parent)
    }
    $encoding = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText(
        $Path,
        (($Value | ConvertTo-Json -Depth $Depth) + [Environment]::NewLine),
        $encoding
    )
}

function Get-HeavyProcesses {
    $names = @(
        'UnrealEditor',
        'UnrealEditor-Cmd',
        'ShaderCompileWorker',
        'AutomationTool',
        'UnrealBuildTool',
        'blender',
        'dotnet',
        'cl',
        'link'
    )
    $rows = @()
    foreach ($process in [System.Diagnostics.Process]::GetProcesses()) {
        try {
            if ($names -contains $process.ProcessName) {
                $rows += [ordered]@{
                    name = $process.ProcessName
                    pid = [int]$process.Id
                }
            }
        } finally {
            $process.Dispose()
        }
    }
    return @($rows)
}

function Get-ProcessTree {
    param([int]$RootPid)
    $searcher = $null
    $results = $null
    try {
        $searcher = New-Object System.Management.ManagementObjectSearcher(
            'SELECT ProcessId,ParentProcessId,Name,CommandLine FROM Win32_Process'
        )
        $results = $searcher.Get()
        $all = @()
        foreach ($result in $results) {
            $all += [ordered]@{
                pid = [int]$result.ProcessId
                parent_pid = [int]$result.ParentProcessId
                name = [string]$result.Name
                command_line = [string]$result.CommandLine
            }
        }
        $known = @($RootPid)
        $changed = $true
        while ($changed) {
            $changed = $false
            foreach ($row in $all) {
                if ($known -contains $row.parent_pid -and $known -notcontains $row.pid) {
                    $known += $row.pid
                    $changed = $true
                }
            }
        }
        return @($all | Where-Object { $known -contains $_.pid })
    } finally {
        if ($null -ne $results) { $results.Dispose() }
        if ($null -ne $searcher) { $searcher.Dispose() }
    }
}

function Test-GovernedNamespacesAbsent {
    foreach ($path in @($ViewRoot, $AttemptRoot, $TerminalManifest, $EmergencyReceipt)) {
        if ([System.IO.Directory]::Exists($path) -or [System.IO.File]::Exists($path)) {
            throw "Governed namespace already exists: $path"
        }
    }
}

function Assert-Authorities {
    [void](Assert-File $InputInventory 34288 '1699bce707a0abcf3289e0dedfd24cf4983ab848f9c8f2fe5cd82ef3fa49eef5')
    [void](Assert-File $OfflineValidation 8615 '699933d09dbccdcb5a4d998f2ddc858ef7e856a5586474a964d387d289e903e9')
    [void](Assert-File $PostchangeInventory 2422 '0ead73d879f07755788cf83ab6ce0aa4583db099280b46937db44f2a58c1a031')
    [void](Assert-File $DotNet 178400 'a8d3105441b568cfd44ac5eab8c0fc190cdefb0047e3e84e49cbce819a197a7a')
    [void](Assert-File $UnrealBuildTool 3209656 'b0931427529b907eea171f1913ed8a50c5753a3cae733ac2773be537f633d1a8')

    $inventory = Get-Content -LiteralPath $InputInventory -Raw | ConvertFrom-Json
    if ([int]$inventory.record_count -ne 170 -or @($inventory.records).Count -ne 170) {
        throw 'Native-build input inventory must contain exactly 170 records.'
    }
    foreach ($record in $inventory.records) {
        $source = [System.IO.Path]::GetFullPath(
            [System.IO.Path]::Combine($SourceRoot, [string]$record.relative_path)
        )
        if (-not $source.StartsWith($SourceRoot + '\', [System.StringComparison]::OrdinalIgnoreCase)) {
            throw "Inventory path escapes the source root: $source"
        }
        [void](Assert-File $source ([long]$record.bytes) ([string]$record.sha256))
    }
    return $inventory
}

if ($OfflineContractTest) {
    if ($AuthorizeSingleBuild) {
        [Console]::Error.WriteLine('Offline and authorized modes are mutually exclusive.')
        [Environment]::Exit([int]3)
    }
    try {
        Test-GovernedNamespacesAbsent
        $inventory = Assert-Authorities
        $heavy = @(Get-HeavyProcesses)
        if ($heavy.Count -ne 0) {
            throw "Heavy processes present: $($heavy | ConvertTo-Json -Compress)"
        }
        [ordered]@{
            classification = 'PASS'
            record_count = @($inventory.records).Count
            build_launch_count = 0
            governed_namespaces_created = 0
        } | ConvertTo-Json -Depth 8
        [Environment]::Exit([int]0)
    } catch {
        [Console]::Error.WriteLine($_.Exception.Message)
        [Environment]::Exit([int]1)
    }
}

if (-not $AuthorizeSingleBuild) {
    [Console]::Error.WriteLine('Explicit -AuthorizeSingleBuild is required.')
    [Environment]::Exit([int]2)
}

$State = [ordered]@{
    schema = 'skyguard.phase7.combat-vfx-pooling01.native-build-terminal.v1'
    classification = 'FAILED_WITH_EVIDENCE'
    stage = 'INITIALIZING'
    failure = $null
    started_at_utc = [DateTime]::UtcNow.ToString('o')
    ended_at_utc = $null
    executable = $DotNet
    arguments = @($BuildArguments)
    working_directory = $WorkingDirectory
    view_root = $ViewRoot
    attempt_root = $AttemptRoot
    supervisor_launch_count = 1
    build_launch_count = 0
    retry_count = 0
    pid = $null
    process_handle_retained = $false
    exit_code = $null
    exit_code_type = $null
    timed_out = $false
    copied_input_count = 0
    copied_input_parity = $false
    output_inventory = @()
    expected_outputs = @()
    copy_back_performed = $false
    unreal_editor_launched = $false
    blender_launched = $false
    process_tree_samples = @()
}
$ExitStatus = 1
$Process = $null

try {
    $State.stage = 'PREFLIGHT'
    Test-GovernedNamespacesAbsent
    $inventory = Assert-Authorities
    $heavy = @(Get-HeavyProcesses)
    if ($heavy.Count -ne 0) {
        throw "Heavy processes present: $($heavy | ConvertTo-Json -Depth 5 -Compress)"
    }

    $State.stage = 'COPY_ISOLATED_VIEW'
    [void][System.IO.Directory]::CreateDirectory($AttemptRoot)
    [void][System.IO.Directory]::CreateDirectory($ViewRoot)
    foreach ($record in $inventory.records) {
        $source = [System.IO.Path]::Combine($SourceRoot, [string]$record.relative_path)
        $destination = [System.IO.Path]::Combine($ViewRoot, [string]$record.relative_path)
        [void][System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName($destination))
        [System.IO.File]::Copy($source, $destination, $false)
        [void](Assert-File $destination ([long]$record.bytes) ([string]$record.sha256))
        $State.copied_input_count = [int]$State.copied_input_count + 1
    }
    $State.copied_input_parity = $State.copied_input_count -eq 170

    $stdout = [System.IO.Path]::Combine($AttemptRoot, 'ubt_stdout.log')
    $stderr = [System.IO.Path]::Combine($AttemptRoot, 'ubt_stderr.log')
    $State.stage = 'BUILD_RUNNING'
    $State.build_launch_count = 1
    $Process = Start-Process `
        -FilePath $DotNet `
        -ArgumentList $BuildArguments `
        -WorkingDirectory $WorkingDirectory `
        -RedirectStandardOutput $stdout `
        -RedirectStandardError $stderr `
        -PassThru
    $State.pid = [int]$Process.Id
    $nativeHandle = $Process.Handle
    $State.process_handle_retained = $nativeHandle -ne [IntPtr]::Zero

    $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
    $nextSample = [DateTime]::UtcNow
    while (-not $Process.HasExited -and [DateTime]::UtcNow -lt $deadline) {
        if ([DateTime]::UtcNow -ge $nextSample) {
            $State.process_tree_samples += [ordered]@{
                utc = [DateTime]::UtcNow.ToString('o')
                rows = @(Get-ProcessTree ([int]$Process.Id))
            }
            $nextSample = [DateTime]::UtcNow.AddSeconds(15)
        }
        Start-Sleep -Milliseconds 1000
        $Process.Refresh()
    }
    if (-not $Process.HasExited) {
        $State.timed_out = $true
        try { $Process.Kill() } catch {}
        throw "Native build timed out after $TimeoutSeconds seconds."
    }
    $Process.WaitForExit()
    $Process.Refresh()
    $State.exit_code = [int]$Process.ExitCode
    $State.exit_code_type = $Process.ExitCode.GetType().FullName
    $State.process_tree_samples += [ordered]@{
        utc = [DateTime]::UtcNow.ToString('o')
        rows = @(Get-ProcessTree ([int]$Process.Id))
    }
    if ($State.exit_code_type -cne 'System.Int32' -or $State.exit_code -ne 0) {
        throw "Native build returned $($State.exit_code_type) $($State.exit_code)."
    }

    $State.stage = 'POSTFLIGHT'
    foreach ($record in $inventory.records) {
        $source = [System.IO.Path]::Combine($SourceRoot, [string]$record.relative_path)
        $destination = [System.IO.Path]::Combine($ViewRoot, [string]$record.relative_path)
        [void](Assert-File $source ([long]$record.bytes) ([string]$record.sha256))
        [void](Assert-File $destination ([long]$record.bytes) ([string]$record.sha256))
    }

    $expected = @(
        [System.IO.Path]::Combine($ViewRoot, 'Binaries\Win64\UnrealEditor-Skyguard52.dll'),
        [System.IO.Path]::Combine($ViewRoot, 'Binaries\Win64\UnrealEditor-Skyguard52.pdb'),
        [System.IO.Path]::Combine($ViewRoot, 'Binaries\Win64\UnrealEditor.modules')
    )
    $State.expected_outputs = @($expected | ForEach-Object { Get-FileRecord $_ })
    $State.output_inventory = @(
        Get-ChildItem -LiteralPath $ViewRoot -Recurse -File | ForEach-Object {
            Get-FileRecord $_.FullName
        }
    )
    $State.classification = 'PASSED_READY_FOR_EXPLICIT_SINGLE_COMBAT_VFX_AUTOMATION_TEST_AUTHORIZATION'
    $State.stage = 'COMPLETE'
    $ExitStatus = 0
} catch {
    $State.failure = $_.Exception.Message
    $State.stage = 'FAILED'
    $State.classification = 'FAILED_WITH_EVIDENCE'
    $ExitStatus = 1
} finally {
    if ($null -ne $Process) {
        try { $Process.Dispose() } catch {}
    }
    $State.ended_at_utc = [DateTime]::UtcNow.ToString('o')
    try {
        Write-Json $TerminalManifest $State 40
    } catch {
        try {
            $parent = [System.IO.Path]::GetDirectoryName($EmergencyReceipt)
            [void][System.IO.Directory]::CreateDirectory($parent)
            $encoding = New-Object System.Text.UTF8Encoding($false)
            $row = [ordered]@{
                utc = [DateTime]::UtcNow.ToString('o')
                classification = 'FAILED_WITH_EVIDENCE'
                stage = 'TERMINAL_MANIFEST_WRITE_FAILED'
                message = $_.Exception.Message
            }
            [System.IO.File]::AppendAllText(
                $EmergencyReceipt,
                (($row | ConvertTo-Json -Depth 8 -Compress) + [Environment]::NewLine),
                $encoding
            )
        } catch {}
        $ExitStatus = 1
    }
}

[Environment]::Exit([int]$ExitStatus)
