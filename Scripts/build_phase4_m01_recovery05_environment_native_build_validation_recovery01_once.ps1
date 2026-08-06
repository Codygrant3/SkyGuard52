[CmdletBinding()]
param(
    [switch]$AuthorizeSingleBuild
)

$ErrorActionPreference = 'Stop'

$ProjectRoot = 'D:\Skyguard52'
$AttemptRoot = 'D:\Skyguard52\Saved\BuildAttempts\PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_VALIDATION_RECOVERY01\build_attempt_01'
$TerminalManifest = 'D:\Skyguard52\Saved\Reports\PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_VALIDATION_RECOVERY01_TERMINAL_SUPERVISOR_MANIFEST.json'
$EmergencyReceipt = 'D:\Skyguard52\Saved\Reports\PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_VALIDATION_RECOVERY01_EMERGENCY_RECEIPT.jsonl'
$AcceptedFreeze = 'D:\Skyguard52\Docs\AAA_Review\PHASE4_M01_RECOVERY05_ENVIRONMENT_SOURCE_RECOVERY01_VALIDATION_RECOVERY01_FREEZE.json'
$AcceptedInventory = 'D:\Skyguard52\Saved\Reports\PHASE4_M01_RECOVERY05_ENVIRONMENT_SOURCE_RECOVERY01_VALIDATION_RECOVERY01_ARTIFACT_INVENTORY.json'
$EnvironmentSource = 'D:\Skyguard52\Source\Skyguard52\SkyguardMission01EnvironmentDirector.cpp'
$DotNet = 'D:\UE_5.8\Engine\Binaries\ThirdParty\DotNet\10.0\win-x64\dotnet.exe'
$UnrealBuildTool = 'D:\UE_5.8\Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.dll'
$WorkingDirectory = 'D:\UE_5.8\Engine\Binaries\DotNET\UnrealBuildTool'
$TimeoutSeconds = 1200
$Arguments = @(
    $UnrealBuildTool,
    'Skyguard52Editor',
    'Win64',
    'Development',
    '-Project=D:\Skyguard52\Skyguard52.uproject',
    '-WaitMutex',
    '-NoHotReloadFromIDE'
)

function Write-Utf8Json {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)]$Value,
        [int]$Depth = 20
    )
    $parent = [System.IO.Path]::GetDirectoryName($Path)
    if (-not [string]::IsNullOrWhiteSpace($parent)) {
        [void][System.IO.Directory]::CreateDirectory($parent)
    }
    $encoding = New-Object System.Text.UTF8Encoding($false)
    $json = $Value | ConvertTo-Json -Depth $Depth
    [System.IO.File]::WriteAllText($Path, $json, $encoding)
}

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
        if ($null -eq $digest -or $digest.Length -ne 32) {
            throw "Invalid SHA-256 result: $Path"
        }
        if ($stream.Position -ne $stream.Length) {
            throw "Partial SHA-256 read: $Path"
        }
        $builder = New-Object System.Text.StringBuilder
        foreach ($item in $digest) {
            [void]$builder.Append($item.ToString('x2'))
        }
        $value = $builder.ToString()
        if ($value -cnotmatch '^[0-9a-f]{64}$') {
            throw "Invalid SHA-256 formatting: $Path"
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
    param([Parameter(Mandatory = $true)][string]$Path)
    if (-not [System.IO.File]::Exists($Path)) {
        throw "Missing file: $Path"
    }
    $item = New-Object System.IO.FileInfo($Path)
    return [ordered]@{
        file = $Path
        bytes = [long]$item.Length
        sha256 = Get-Sha256 $Path
        last_write_utc = $item.LastWriteTimeUtc.ToString('o')
    }
}

function Assert-FileAuthority {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][long]$Bytes,
        [Parameter(Mandatory = $true)][string]$Sha256
    )
    $record = Get-FileRecord $Path
    if ($record.bytes -ne $Bytes) {
        throw "Byte-count mismatch for $Path. Expected $Bytes, received $($record.bytes)."
    }
    if ($record.sha256 -cne $Sha256) {
        throw "SHA-256 mismatch for $Path. Expected $Sha256, received $($record.sha256)."
    }
    return $record
}

function Get-HeavyProcesses {
    $heavyNames = @(
        'UnrealEditor',
        'UnrealEditor-Cmd',
        'ShaderCompileWorker',
        'blender',
        'AutomationTool',
        'UnrealBuildTool',
        'cl',
        'link',
        'dotnet'
    )
    $rows = @()
    foreach ($process in [System.Diagnostics.Process]::GetProcesses()) {
        try {
            if ($heavyNames -contains $process.ProcessName) {
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

function Get-ProcessTreeSample {
    param([Parameter(Mandatory = $true)][int]$RootPid)
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

function Get-ProjectInventory {
    $paths = New-Object System.Collections.Generic.List[string]
    $paths.Add('D:\Skyguard52\Skyguard52.uproject')
    foreach ($folder in @('D:\Skyguard52\Source', 'D:\Skyguard52\Config')) {
        if ([System.IO.Directory]::Exists($folder)) {
            foreach ($file in [System.IO.Directory]::EnumerateFiles($folder, '*', [System.IO.SearchOption]::AllDirectories)) {
                $paths.Add($file)
            }
        }
    }
    $plugins = 'D:\Skyguard52\Plugins'
    if ([System.IO.Directory]::Exists($plugins)) {
        foreach ($file in [System.IO.Directory]::EnumerateFiles($plugins, '*', [System.IO.SearchOption]::AllDirectories)) {
            if ($file.EndsWith('.uplugin', [System.StringComparison]::OrdinalIgnoreCase) -or
                $file.IndexOf('\Source\', [System.StringComparison]::OrdinalIgnoreCase) -ge 0) {
                $paths.Add($file)
            }
        }
    }
    $binaryRoot = 'D:\Skyguard52\Binaries\Win64'
    if ([System.IO.Directory]::Exists($binaryRoot)) {
        foreach ($file in [System.IO.Directory]::EnumerateFiles($binaryRoot, '*', [System.IO.SearchOption]::TopDirectoryOnly)) {
            $name = [System.IO.Path]::GetFileName($file)
            if ($name -like 'UnrealEditor-Skyguard52*' -or $name -eq 'UnrealEditor.modules') {
                $paths.Add($file)
            }
        }
    }
    $records = @()
    foreach ($path in @($paths | Sort-Object -Unique)) {
        $records += Get-FileRecord $path
    }
    return @($records)
}

function Assert-EnvironmentSource {
    $record = Assert-FileAuthority `
        $EnvironmentSource `
        15032 `
        '73e736b088dd77dfaed42081bd988094d6743057175626db01a1fb9a92ceec44'
    $text = [System.IO.File]::ReadAllText($EnvironmentSource)
    if ($text.Contains("`r")) {
        throw 'Environment source is not LF-only.'
    }
    $mobilityLine = 'Root->SetMobility(EComponentMobility::Static);'
    if ([regex]::Matches($text, [regex]::Escape($mobilityLine)).Count -ne 1) {
        throw 'Environment source does not contain exactly one authorized mobility line.'
    }
    $required = "Root = CreateDefaultSubobject<USceneComponent>(TEXT(`"Mission01EnvironmentRoot`"));`n`tRoot->SetMobility(EComponentMobility::Static);`n`tSetRootComponent(Root);"
    if (-not $text.Contains($required)) {
        throw 'Authorized mobility line is not in the required position.'
    }
    return $record
}

function Assert-AcceptedFreeze {
    [void](Assert-FileAuthority `
        $AcceptedFreeze `
        10044 `
        '0bd0bfee24e28d7cfd8a4f086209ed97cab7d4ffc40b09913e85d9c031b6293a')
    [void](Assert-FileAuthority `
        $AcceptedInventory `
        8302 `
        '2a649b222addfd43bab8d2393a25668549d6f86b744888efe7458d39cc8fd8d0')
    $freeze = [System.IO.File]::ReadAllText($AcceptedFreeze) | ConvertFrom-Json
    if ($freeze.classification -cne 'PASSED_READY_FOR_EXPLICIT_M01_ENVIRONMENT_NATIVE_BUILD_AUTHORIZATION') {
        throw "Unexpected accepted-freeze classification: $($freeze.classification)"
    }
    if (@($freeze.frozen_files).Count -ne 23) {
        throw "Expected 23 frozen records, received $(@($freeze.frozen_files).Count)."
    }
    foreach ($frozen in $freeze.frozen_files) {
        $path = [System.IO.Path]::Combine(
            $ProjectRoot,
            ([string]$frozen.file).Replace('/', '\')
        )
        [void](Assert-FileAuthority $path ([long]$frozen.bytes) ([string]$frozen.sha256))
    }
}

function Write-EmergencyReceipt {
    param(
        [Parameter(Mandatory = $true)][string]$Stage,
        [Parameter(Mandatory = $true)][string]$Message
    )
    try {
        $record = [ordered]@{
            utc = [DateTime]::UtcNow.ToString('o')
            gate = 'PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_VALIDATION_RECOVERY01'
            stage = $Stage
            message = $Message
        }
        $parent = [System.IO.Path]::GetDirectoryName($EmergencyReceipt)
        [void][System.IO.Directory]::CreateDirectory($parent)
        $encoding = New-Object System.Text.UTF8Encoding($false)
        $line = ($record | ConvertTo-Json -Depth 8 -Compress) + [Environment]::NewLine
        [System.IO.File]::AppendAllText($EmergencyReceipt, $line, $encoding)
    } catch {
    }
}

$State = [ordered]@{
    schema = 'skyguard.phase4.m01-recovery05-environment-native-build-validation-recovery01-terminal-supervisor.v1'
    gate = 'PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_VALIDATION_RECOVERY01'
    classification = 'FAILED_WITH_EVIDENCE'
    supervisor_started_utc = [DateTime]::UtcNow.ToString('o')
    supervisor_ended_utc = $null
    authorization_present = [bool]$AuthorizeSingleBuild
    preflight_passed = $false
    build_namespace_created = $false
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
    process_tree_samples_file = $null
    timed_out = $false
    numeric_exit_code = $null
    exit_code_type = $null
    failure_stage = $null
    failure_message = $null
    source_authority = $null
    pre_build_inventory = $null
    post_build_inventory = $null
    produced_outputs = @()
    compiler_linker_validation = $null
    source_parity_after_build = $false
    frozen_authorities_preserved_after_build = $false
    unreal_editor_launched = $false
    blender_launched = $false
}

$Process = $null
$FinalExitCode = 1
$ManifestWritten = $false
$BuildStartUtc = $null

try {
    if (-not $AuthorizeSingleBuild) {
        throw 'Normal execution requires -AuthorizeSingleBuild.'
    }
    if ([System.IO.File]::Exists($TerminalManifest)) {
        throw "Terminal-manifest namespace already exists: $TerminalManifest"
    }
    if ([System.IO.File]::Exists($EmergencyReceipt)) {
        throw "Emergency-receipt namespace already exists: $EmergencyReceipt"
    }
    if ([System.IO.Directory]::Exists($AttemptRoot) -or [System.IO.File]::Exists($AttemptRoot)) {
        throw "Build-attempt namespace already exists: $AttemptRoot"
    }

    Assert-AcceptedFreeze
    $State.source_authority = Assert-EnvironmentSource
    [void](Assert-FileAuthority `
        $DotNet `
        178400 `
        'a8d3105441b568cfd44ac5eab8c0fc190cdefb0047e3e84e49cbce819a197a7a')
    [void](Assert-FileAuthority `
        $UnrealBuildTool `
        3209656 `
        'b0931427529b907eea171f1913ed8a50c5753a3cae733ac2773be537f633d1a8')
    [void](Assert-FileAuthority `
        'D:\Skyguard52\Skyguard52.uproject' `
        1542 `
        '99461a1a562ede732da52c84f05002dcc88f772cd30fdccd45ff46d6836f3b60')
    [void](Assert-FileAuthority `
        'D:\Skyguard52\Source\Skyguard52Editor.Target.cs' `
        489 `
        '83468f9644058f4431f2ffc3fe7e011dbe8a01ce93f9f35fc4f098363fd1e78d')
    [void](Assert-FileAuthority `
        'D:\Skyguard52\Source\Skyguard52.Target.cs' `
        346 `
        'f7a96095d9c7681c33ad259d4f5d6e9b2e593600d4fd2e0c09fe02bcf4358584')
    [void](Assert-FileAuthority `
        'D:\Skyguard52\Binaries\Win64\UnrealEditor-Skyguard52.dll' `
        2891264 `
        '5776561194ddec0fc23c476a41a467aef5d72dcb883b1105deed6ab72daf336f')
    [void](Assert-FileAuthority `
        'D:\Skyguard52\Binaries\Win64\UnrealEditor-Skyguard52.pdb' `
        98291712 `
        '5bd4a7e82d72f71cf7634ea2c09d1126856bcc50675317bb45d8737028ae4cc4')
    [void](Assert-FileAuthority `
        'D:\Skyguard52\Binaries\Win64\UnrealEditor.modules' `
        98 `
        '17821e7c0f6aba09788fc98dd80299e0b4de98cbb09cc2e8c8f9b0e17146bfeb')

    $heavy = @(Get-HeavyProcesses)
    if ($heavy.Count -ne 0) {
        throw "Heavy process preflight failed: $($heavy | ConvertTo-Json -Depth 5 -Compress)"
    }

    $State.preflight_passed = $true
    [void][System.IO.Directory]::CreateDirectory([System.IO.Path]::Combine($AttemptRoot, 'logs'))
    $State.build_namespace_created = $true

    $preInventoryPath = [System.IO.Path]::Combine($AttemptRoot, 'pre_build_inventory.json')
    $preInventory = [ordered]@{
        created_utc = [DateTime]::UtcNow.ToString('o')
        records = @(Get-ProjectInventory)
    }
    Write-Utf8Json $preInventoryPath $preInventory 30
    $State.pre_build_inventory = Get-FileRecord $preInventoryPath

    $stdoutPath = [System.IO.Path]::Combine($AttemptRoot, 'logs', 'build.stdout.log')
    $stderrPath = [System.IO.Path]::Combine($AttemptRoot, 'logs', 'build.stderr.log')
    $treePath = [System.IO.Path]::Combine($AttemptRoot, 'process_tree_samples.jsonl')
    $State.process_tree_samples_file = $treePath

    $BuildStartUtc = [DateTime]::UtcNow
    $State.build_started_utc = $BuildStartUtc.ToString('o')
    $State.build_launched = $true
    $Process = Start-Process `
        -FilePath $DotNet `
        -ArgumentList $Arguments `
        -WorkingDirectory $WorkingDirectory `
        -PassThru `
        -WindowStyle Hidden `
        -RedirectStandardOutput $stdoutPath `
        -RedirectStandardError $stderrPath
    $State.bundled_dotnet_launch_count = 1
    $State.ubt_invocation_count = 1
    $State.process_id = [int]$Process.Id
    $handle = $Process.Handle
    $State.process_handle_retained = ($handle -ne [IntPtr]::Zero)
    $encoding = New-Object System.Text.UTF8Encoding($false)
    $deadline = $BuildStartUtc.AddSeconds($TimeoutSeconds)

    while (-not $Process.HasExited -and [DateTime]::UtcNow -lt $deadline) {
        $sample = [ordered]@{
            utc = [DateTime]::UtcNow.ToString('o')
            root_pid = [int]$Process.Id
            processes = @(Get-ProcessTreeSample $Process.Id)
        }
        $line = ($sample | ConvertTo-Json -Depth 10 -Compress) + [Environment]::NewLine
        [System.IO.File]::AppendAllText($treePath, $line, $encoding)
        [System.Threading.Thread]::Sleep(2000)
        $Process.Refresh()
    }

    if (-not $Process.HasExited) {
        $State.timed_out = $true
        try {
            $Process.Kill()
        } catch {
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
        throw "Build exceeded the governed timeout of $TimeoutSeconds seconds."
    }
    if ($State.numeric_exit_code -ne 0) {
        throw "UnrealBuildTool returned exit code $($State.numeric_exit_code)."
    }

    $logText = ''
    if ([System.IO.File]::Exists($stdoutPath)) {
        $logText += [System.IO.File]::ReadAllText($stdoutPath)
    }
    if ([System.IO.File]::Exists($stderrPath)) {
        $logText += [Environment]::NewLine + [System.IO.File]::ReadAllText($stderrPath)
    }
    $failurePattern = '(?im)(error C\d{4}|fatal error|error LNK\d{4}|unresolved external symbol)'
    if ([regex]::IsMatch($logText, $failurePattern)) {
        throw 'Compiler or linker failure signature was present despite exit code zero.'
    }
    $State.compiler_linker_validation = [ordered]@{
        exit_code_zero = $true
        failure_signature_absent = $true
        stdout = Get-FileRecord $stdoutPath
        stderr = Get-FileRecord $stderrPath
    }

    $requiredOutputs = @(
        'D:\Skyguard52\Binaries\Win64\UnrealEditor-Skyguard52.dll',
        'D:\Skyguard52\Binaries\Win64\UnrealEditor-Skyguard52.pdb',
        'D:\Skyguard52\Binaries\Win64\UnrealEditor.modules'
    )
    $outputRecords = @()
    foreach ($output in $requiredOutputs) {
        $record = Get-FileRecord $output
        $item = New-Object System.IO.FileInfo($output)
        if ($item.LastWriteTimeUtc -lt $BuildStartUtc) {
            throw "Required output was not refreshed by the governed build: $output"
        }
        $outputRecords += $record
    }
    if ($outputRecords[0].sha256 -ceq '5776561194ddec0fc23c476a41a467aef5d72dcb883b1105deed6ab72daf336f') {
        throw 'Editor DLL did not change from the frozen pre-build baseline.'
    }
    if ($outputRecords[1].sha256 -ceq '5bd4a7e82d72f71cf7634ea2c09d1126856bcc50675317bb45d8737028ae4cc4') {
        throw 'Editor PDB did not change from the frozen pre-build baseline.'
    }
    $State.produced_outputs = $outputRecords

    [void](Assert-EnvironmentSource)
    $State.source_parity_after_build = $true
    Assert-AcceptedFreeze
    $State.frozen_authorities_preserved_after_build = $true

    $postInventoryPath = [System.IO.Path]::Combine($AttemptRoot, 'post_build_inventory.json')
    $postInventory = [ordered]@{
        created_utc = [DateTime]::UtcNow.ToString('o')
        records = @(Get-ProjectInventory)
    }
    Write-Utf8Json $postInventoryPath $postInventory 30
    $State.post_build_inventory = Get-FileRecord $postInventoryPath

    $focusedPath = [System.IO.Path]::Combine($AttemptRoot, 'focused_environment_validation.json')
    $focused = [ordered]@{
        classification = 'PASSED'
        environment_source = Get-FileRecord $EnvironmentSource
        lf_only = $true
        authorized_mobility_count = 1
        authorized_mobility_position = 'between_root_creation_and_set_root_component'
        compile_and_link = 'PASS'
        fresh_editor_dll = $outputRecords[0]
        fresh_editor_pdb = $outputRecords[1]
        modules_receipt = $outputRecords[2]
        frozen_authorities_preserved = $true
        unreal_editor_launched = $false
        blender_launched = $false
        retry_count = 0
    }
    Write-Utf8Json $focusedPath $focused 15

    $State.classification = 'PASSED_READY_FOR_EXPLICIT_RECOVERY05_PLUGIN_BUILD_AUTHORIZATION'
    $FinalExitCode = 0
} catch {
    $State.failure_stage = if ($State.preflight_passed) {
        'build_or_postflight'
    } else {
        'preflight'
    }
    $State.failure_message = $_.Exception.Message
    $State.classification = 'FAILED_WITH_EVIDENCE'
    $FinalExitCode = 1
} finally {
    $State.supervisor_ended_utc = [DateTime]::UtcNow.ToString('o')
    try {
        Write-Utf8Json $TerminalManifest $State 30
        $ManifestWritten = [System.IO.File]::Exists($TerminalManifest)
    } catch {
        Write-EmergencyReceipt 'terminal_manifest_write' $_.Exception.Message
    }
    if (-not $ManifestWritten) {
        Write-EmergencyReceipt 'terminal_manifest_confirmation' 'Terminal supervisor manifest was not durable.'
        $FinalExitCode = 1
    }
    if ($null -ne $Process) {
        $Process.Dispose()
    }
}

exit $FinalExitCode
