[CmdletBinding()]
param(
    [switch]$AuthorizeSingleBuild,
    [switch]$OfflineContractTest
)

$ErrorActionPreference = 'Stop'

$SourceRoot = 'D:\Skyguard52'
$ViewRoot = 'D:\SG52M01GROUND01'
$AttemptRoot = 'D:\Skyguard52\Saved\BuildAttempts\M01_LANDSCAPE_GROUNDING_BRIDGE01_NATIVE_BUILD\attempt_01'
$TerminalManifest = 'D:\Skyguard52\Saved\Reports\M01_LANDSCAPE_GROUNDING_BRIDGE01_NATIVE_BUILD_TERMINAL_MANIFEST.json'
$EmergencyReceipt = 'D:\Skyguard52\Saved\Reports\M01_LANDSCAPE_GROUNDING_BRIDGE01_NATIVE_BUILD_EMERGENCY_RECEIPT.jsonl'
$ParityContract = 'D:\Skyguard52\Saved\Reports\M01_LANDSCAPE_GROUNDING_BRIDGE01_SOURCE_PARITY_CONTRACT.json'
$SourceContract = 'D:\Skyguard52\Docs\Toolchain\ToolchainWave08\M01LandscapeGroundingBridge01\source_contract.json'
$InstalledAuthority = 'D:\Skyguard52\Docs\Toolchain\ToolchainWave08\M01LandscapeGroundingBridge01\installed_ue58_authority_report.json'
$DotNet = 'D:\UE_5.8\Engine\Binaries\ThirdParty\DotNet\10.0\win-x64\dotnet.exe'
$UnrealBuildTool = 'D:\UE_5.8\Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.dll'
$WorkingDirectory = 'D:\UE_5.8\Engine\Binaries\DotNET\UnrealBuildTool'
$TimeoutSeconds = 1800
$Arguments = @(
    $UnrealBuildTool,
    'Skyguard52Editor',
    'Win64',
    'Development',
    '-Project=D:\SG52M01GROUND01\Skyguard52.uproject',
    '-WaitMutex',
    '-NoHotReloadFromIDE'
)

$NonBuildMode = $OfflineContractTest -or -not $AuthorizeSingleBuild
$TemporaryRoot = [System.IO.Path]::Combine(
    [System.IO.Path]::GetTempPath(),
    'Skyguard52_M01GroundingBridge01_' + [Guid]::NewGuid().ToString('N')
)
$ActiveTerminalManifest = if ($NonBuildMode) {
    [System.IO.Path]::Combine($TemporaryRoot, 'terminal_manifest.json')
} else {
    $TerminalManifest
}
$ActiveEmergencyReceipt = if ($NonBuildMode) {
    [System.IO.Path]::Combine($TemporaryRoot, 'emergency_receipt.jsonl')
} else {
    $EmergencyReceipt
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
        ($Value | ConvertTo-Json -Depth $Depth),
        $encoding
    )
}

function Get-Sha256 {
    param([string]$Path)
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
        if ($null -eq $digest -or $digest.Length -ne 32) {
            throw "Invalid SHA-256 result: $Path"
        }
        if ($stream.Position -ne $stream.Length) {
            throw "Partial hash read: $Path"
        }
        $builder = New-Object System.Text.StringBuilder
        foreach ($item in $digest) {
            [void]$builder.Append($item.ToString('x2'))
        }
        $value = $builder.ToString()
        if ($value -cnotmatch '^[0-9a-f]{64}$') {
            throw "Invalid lowercase SHA-256: $Path"
        }
        return $value
    } finally {
        if ($null -ne $algorithm) {
            $algorithm.Dispose()
        }
        if ($null -ne $stream) {
            $stream.Dispose()
        }
    }
}

function Get-FileRecord {
    param([string]$Path)
    $item = New-Object System.IO.FileInfo($Path)
    if (-not $item.Exists) {
        throw "Missing file: $Path"
    }
    return [ordered]@{
        file = $item.FullName
        bytes = [long]$item.Length
        sha256 = Get-Sha256 $item.FullName
        last_write_utc = $item.LastWriteTimeUtc.ToString('o')
    }
}

function Assert-File {
    param([string]$Path, [long]$Bytes, [string]$Sha256)
    $record = Get-FileRecord $Path
    if ($record.bytes -ne $Bytes) {
        throw "Byte mismatch: $Path"
    }
    if ($record.sha256 -cne $Sha256) {
        throw "SHA-256 mismatch: $Path"
    }
    return $record
}

function Get-HeavyProcesses {
    $names = @(
        'UnrealEditor',
        'UnrealEditor-Cmd',
        'ShaderCompileWorker',
        'blender',
        'AutomationTool',
        'UnrealBuildTool',
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
        if ($null -ne $results) {
            $results.Dispose()
        }
        if ($null -ne $searcher) {
            $searcher.Dispose()
        }
    }
}

function Write-Emergency {
    param([string]$Stage, [string]$Message)
    try {
        $parent = [System.IO.Path]::GetDirectoryName($ActiveEmergencyReceipt)
        [void][System.IO.Directory]::CreateDirectory($parent)
        $record = [ordered]@{
            utc = [DateTime]::UtcNow.ToString('o')
            gate = 'M01_LANDSCAPE_GROUNDING_BRIDGE01_NATIVE_BUILD'
            stage = $Stage
            message = $Message
        }
        $encoding = New-Object System.Text.UTF8Encoding($false)
        [System.IO.File]::AppendAllText(
            $ActiveEmergencyReceipt,
            ($record | ConvertTo-Json -Depth 8 -Compress) + [Environment]::NewLine,
            $encoding
        )
    } catch {
    }
}

function Assert-FutureNamespacesAbsent {
    foreach ($path in @($ViewRoot, $AttemptRoot, $TerminalManifest, $EmergencyReceipt)) {
        if ([System.IO.Directory]::Exists($path) -or [System.IO.File]::Exists($path)) {
            throw "Future namespace already exists: $path"
        }
    }
}

function Read-And-ValidateParityContract {
    [void](Assert-File `
        $ParityContract `
        50997 `
        'bf84daff1ebf0400a5deb2b1dc763d0bae1975d1649a83700fc001e5489fe5a4')
    $contract = [System.IO.File]::ReadAllText($ParityContract) | ConvertFrom-Json
    if ([int]$contract.record_count -ne 174 -or @($contract.records).Count -ne 174) {
        throw "Expected 174 parity records, received $(@($contract.records).Count)."
    }
    foreach ($record in $contract.records) {
        [void](Assert-File `
            ([string]$record.source) `
            ([long]$record.bytes) `
            ([string]$record.sha256))
    }
    return $contract
}

function Invoke-OfflineContractTest {
    [void][System.IO.Directory]::CreateDirectory($TemporaryRoot)
    Assert-FutureNamespacesAbsent
    [void](Assert-File `
        $SourceContract `
        2906 `
        '8024b81a7b8365f9ccd8e3f08830505be22a120b5695a931369d99d17f7501a6')
    [void](Assert-File `
        $InstalledAuthority `
        1504 `
        'c9639081d52267dc2ff699b0af1ee1bef157132ab1c58b2d43ae9c49c8fce0f3')
    [void](Assert-File `
        $DotNet `
        178400 `
        'a8d3105441b568cfd44ac5eab8c0fc190cdefb0047e3e84e49cbce819a197a7a')
    [void](Assert-File `
        $UnrealBuildTool `
        3209656 `
        'b0931427529b907eea171f1913ed8a50c5753a3cae733ac2773be537f633d1a8')
    $contract = Read-And-ValidateParityContract

    $probePath = [System.IO.Path]::Combine($TemporaryRoot, 'state_probe.json')
    Write-Json $probePath ([ordered]@{
        numeric_exit_code = [int]0
        exit_code_type = ([int]0).GetType().FullName
        copy_back_performed = $false
        unreal_editor_launched = $false
        blender_launched = $false
        null_exit_code_rejected = $true
    }) 8
    $loaded = [System.IO.File]::ReadAllText($probePath) | ConvertFrom-Json
    if ([int]$loaded.numeric_exit_code -ne 0 -or
        [string]$loaded.exit_code_type -cne 'System.Int32') {
        throw 'Numeric exit-code serialization probe failed.'
    }

    $deliberateFailurePath = [System.IO.Path]::Combine(
        $TemporaryRoot,
        'deliberate_failure_terminal.json'
    )
    try {
        throw 'DELIBERATE_OFFLINE_PREFLIGHT_FAILURE'
    } catch {
        Write-Json $deliberateFailurePath ([ordered]@{
            classification = 'EXPECTED_OFFLINE_FAILURE_CAPTURED'
            message = $_.Exception.Message
        }) 8
    }
    if (-not [System.IO.File]::Exists($deliberateFailurePath)) {
        throw 'Deliberate failure did not produce terminal evidence.'
    }

    $heavy = @(Get-HeavyProcesses)
    if ($heavy.Count -ne 0) {
        throw "Offline heavy-process check failed: $($heavy | ConvertTo-Json -Depth 5 -Compress)"
    }
    Assert-FutureNamespacesAbsent

    return [ordered]@{
        test_root = $TemporaryRoot
        parity_record_count = @($contract.records).Count
        state_probe = Get-FileRecord $probePath
        deliberate_failure_receipt = Get-FileRecord $deliberateFailurePath
        governed_namespaces_created = 0
        build_launch_count = 0
        unreal_launch_count = 0
        blender_launch_count = 0
    }
}

$State = [ordered]@{
    schema = 'skyguard.m01-landscape-grounding-bridge01.native-build-terminal.v1'
    classification = 'FAILED_WITH_EVIDENCE'
    supervisor_started_utc = [DateTime]::UtcNow.ToString('o')
    supervisor_ended_utc = $null
    authorization_present = [bool]$AuthorizeSingleBuild
    offline_contract_test = [bool]$OfflineContractTest
    offline_contract_test_result = $null
    preflight_passed = $false
    attempt_namespace_created = $false
    view_namespace_created = $false
    parity_record_count = 0
    parity_copy_passed = $false
    module_rules_unique = $false
    build_launched = $false
    supervisor_launch_count = 1
    bundled_dotnet_launch_count = 0
    ubt_invocation_count = 0
    retry_count = 0
    automatic_retry = $false
    exact_executable = $DotNet
    exact_arguments = $Arguments
    working_directory = $WorkingDirectory
    timeout_seconds = $TimeoutSeconds
    process_id = $null
    process_handle_retained = $false
    timed_out = $false
    numeric_exit_code = $null
    exit_code_type = $null
    failure_stage = $null
    failure_message = $null
    view_inventory = $null
    output_records = @()
    post_build_parity_passed = $false
    copy_back_performed = $false
    unreal_editor_launched = $false
    blender_launched = $false
}
$Process = $null
$FinalExitCode = 1
$ManifestWritten = $false

try {
    if ($OfflineContractTest -and $AuthorizeSingleBuild) {
        $State.failure_stage = 'argument_validation'
        $State.failure_message = 'OfflineContractTest and AuthorizeSingleBuild are mutually exclusive.'
        $FinalExitCode = 3
    } elseif ($OfflineContractTest) {
        $State.offline_contract_test_result = Invoke-OfflineContractTest
        $State.classification = 'OFFLINE_CONTRACT_TEST_PASSED'
        $FinalExitCode = 0
    } elseif (-not $AuthorizeSingleBuild) {
        $State.failure_stage = 'authorization_refusal'
        $State.failure_message = 'Execution requires -AuthorizeSingleBuild.'
        $FinalExitCode = 2
    } else {
        Assert-FutureNamespacesAbsent
        [void](Assert-File `
            $SourceContract `
            2906 `
            '8024b81a7b8365f9ccd8e3f08830505be22a120b5695a931369d99d17f7501a6')
        [void](Assert-File `
            $InstalledAuthority `
            1504 `
            'c9639081d52267dc2ff699b0af1ee1bef157132ab1c58b2d43ae9c49c8fce0f3')
        [void](Assert-File `
            $DotNet `
            178400 `
            'a8d3105441b568cfd44ac5eab8c0fc190cdefb0047e3e84e49cbce819a197a7a')
        [void](Assert-File `
            $UnrealBuildTool `
            3209656 `
            'b0931427529b907eea171f1913ed8a50c5753a3cae733ac2773be537f633d1a8')
        $heavy = @(Get-HeavyProcesses)
        if ($heavy.Count -ne 0) {
            throw "Heavy process preflight failed: $($heavy | ConvertTo-Json -Depth 5 -Compress)"
        }
        $contract = Read-And-ValidateParityContract
        $State.parity_record_count = @($contract.records).Count
        $State.preflight_passed = $true

        [void][System.IO.Directory]::CreateDirectory(
            [System.IO.Path]::Combine($AttemptRoot, 'logs')
        )
        $State.attempt_namespace_created = $true
        [void][System.IO.Directory]::CreateDirectory($ViewRoot)
        $State.view_namespace_created = $true
        $viewPrefix = $ViewRoot.TrimEnd('\') + '\'

        foreach ($record in $contract.records) {
            $relative = ([string]$record.relative_path).Replace('/', '\')
            $destination = [System.IO.Path]::GetFullPath(
                [System.IO.Path]::Combine($ViewRoot, $relative)
            )
            if (-not $destination.StartsWith(
                $viewPrefix,
                [System.StringComparison]::OrdinalIgnoreCase
            )) {
                throw "Parity destination escaped the isolated view: $destination"
            }
            $parent = [System.IO.Path]::GetDirectoryName($destination)
            [void][System.IO.Directory]::CreateDirectory($parent)
            [System.IO.File]::Copy([string]$record.source, $destination, $false)
            [void](Assert-File `
                $destination `
                ([long]$record.bytes) `
                ([string]$record.sha256))
        }
        $State.parity_copy_passed = $true

        $classes = @()
        foreach ($file in [System.IO.Directory]::EnumerateFiles(
            $ViewRoot,
            '*.Build.cs',
            [System.IO.SearchOption]::AllDirectories
        )) {
            $text = [System.IO.File]::ReadAllText($file)
            $match = [regex]::Match(
                $text,
                'public\s+(?:sealed\s+)?class\s+([A-Za-z_][A-Za-z0-9_]*)\s*:\s*ModuleRules'
            )
            if (-not $match.Success) {
                throw "Unable to determine ModuleRules class: $file"
            }
            $classes += [pscustomobject][ordered]@{
                file = $file
                class = $match.Groups[1].Value
            }
        }
        $duplicates = @(
            $classes |
                Group-Object class |
                Where-Object { $_.Count -gt 1 }
        )
        if ($duplicates.Count -ne 0) {
            throw "Duplicate ModuleRules classes in build view: $($duplicates.Name -join ', ')"
        }
        $State.module_rules_unique = $true

        $viewInventoryPath = [System.IO.Path]::Combine($AttemptRoot, 'view_inventory.json')
        $viewRecords = @()
        foreach ($file in [System.IO.Directory]::EnumerateFiles(
            $ViewRoot,
            '*',
            [System.IO.SearchOption]::AllDirectories
        )) {
            $viewRecords += Get-FileRecord $file
        }
        Write-Json $viewInventoryPath ([ordered]@{
            created_utc = [DateTime]::UtcNow.ToString('o')
            record_count = $viewRecords.Count
            module_rules = $classes
            records = $viewRecords
        }) 35
        $State.view_inventory = Get-FileRecord $viewInventoryPath

        $stdout = [System.IO.Path]::Combine($AttemptRoot, 'logs', 'build.stdout.log')
        $stderr = [System.IO.Path]::Combine($AttemptRoot, 'logs', 'build.stderr.log')
        $tree = [System.IO.Path]::Combine($AttemptRoot, 'process_tree_samples.jsonl')
        $start = [DateTime]::UtcNow
        $State.build_started_utc = $start.ToString('o')
        $State.build_launched = $true
        $Process = Start-Process `
            -FilePath $DotNet `
            -ArgumentList $Arguments `
            -WorkingDirectory $WorkingDirectory `
            -PassThru `
            -WindowStyle Hidden `
            -RedirectStandardOutput $stdout `
            -RedirectStandardError $stderr
        $State.bundled_dotnet_launch_count = 1
        $State.ubt_invocation_count = 1
        $State.process_id = [int]$Process.Id
        $handle = $Process.Handle
        $State.process_handle_retained = ($handle -ne [IntPtr]::Zero)
        $deadline = $start.AddSeconds($TimeoutSeconds)
        $encoding = New-Object System.Text.UTF8Encoding($false)

        while (-not $Process.HasExited -and [DateTime]::UtcNow -lt $deadline) {
            $sample = [ordered]@{
                utc = [DateTime]::UtcNow.ToString('o')
                root_pid = [int]$Process.Id
                processes = @(Get-ProcessTree $Process.Id)
            }
            [System.IO.File]::AppendAllText(
                $tree,
                ($sample | ConvertTo-Json -Depth 10 -Compress) + [Environment]::NewLine,
                $encoding
            )
            [System.Threading.Thread]::Sleep(2000)
            $Process.Refresh()
        }

        if (-not $Process.HasExited) {
            $State.timed_out = $true
            $treeRows = @(Get-ProcessTree $Process.Id | Sort-Object pid -Descending)
            foreach ($row in $treeRows) {
                try {
                    Stop-Process -Id ([int]$row.pid) -Force -ErrorAction SilentlyContinue
                } catch {
                }
            }
        }
        $Process.WaitForExit()
        $Process.Refresh()
        $State.build_ended_utc = [DateTime]::UtcNow.ToString('o')
        if ($null -eq $Process.ExitCode -or $Process.ExitCode -isnot [int]) {
            throw 'Bundled dotnet returned a null or nonnumeric exit code.'
        }
        $State.numeric_exit_code = [int]$Process.ExitCode
        $State.exit_code_type = $Process.ExitCode.GetType().FullName
        if ($State.timed_out) {
            throw "Build exceeded $TimeoutSeconds seconds."
        }
        if ($State.numeric_exit_code -ne 0) {
            throw "UnrealBuildTool returned exit code $($State.numeric_exit_code)."
        }

        $outputs = @(
            'D:\SG52M01GROUND01\Binaries\Win64\UnrealEditor-Skyguard52.dll',
            'D:\SG52M01GROUND01\Binaries\Win64\UnrealEditor-Skyguard52.pdb',
            'D:\SG52M01GROUND01\Binaries\Win64\UnrealEditor.modules'
        )
        $outputRecords = @()
        foreach ($output in $outputs) {
            $item = New-Object System.IO.FileInfo($output)
            if (-not $item.Exists) {
                throw "Missing governed output: $output"
            }
            if ($item.LastWriteTimeUtc -lt $start.AddSeconds(-2)) {
                throw "Output predates governed build: $output"
            }
            $outputRecords += Get-FileRecord $output
        }
        $State.output_records = $outputRecords

        foreach ($record in $contract.records) {
            [void](Assert-File `
                ([string]$record.source) `
                ([long]$record.bytes) `
                ([string]$record.sha256))
            $viewFile = [System.IO.Path]::Combine(
                $ViewRoot,
                ([string]$record.relative_path).Replace('/', '\')
            )
            [void](Assert-File `
                $viewFile `
                ([long]$record.bytes) `
                ([string]$record.sha256))
        }
        $State.post_build_parity_passed = $true
        $State.classification = 'PASSED_READY_FOR_EXPLICIT_M01_LANDSCAPE_GROUNDING_RUNTIME_BINDING_DESIGN'
        $FinalExitCode = 0
    }
} catch {
    if ([string]::IsNullOrWhiteSpace([string]$State.failure_stage)) {
        $State.failure_stage = if ($State.preflight_passed) {
            'view_creation_build_or_postflight'
        } else {
            'preflight'
        }
    }
    $State.failure_message = $_.Exception.Message
    $State.classification = 'FAILED_WITH_EVIDENCE'
    $FinalExitCode = 1
} finally {
    $State.supervisor_ended_utc = [DateTime]::UtcNow.ToString('o')
    try {
        Write-Json $ActiveTerminalManifest $State 35
        $ManifestWritten = [System.IO.File]::Exists($ActiveTerminalManifest)
    } catch {
        Write-Emergency 'terminal_manifest_write' $_.Exception.Message
    }
    if (-not $ManifestWritten) {
        Write-Emergency 'terminal_manifest_confirmation' 'Terminal manifest was not durable.'
        $FinalExitCode = 1
    }
    if ($null -ne $Process) {
        $Process.Dispose()
    }
}

exit $FinalExitCode
