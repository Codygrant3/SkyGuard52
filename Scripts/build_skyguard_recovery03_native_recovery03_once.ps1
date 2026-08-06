[CmdletBinding()]
param(
    [switch]$OfflineContractTest,
    [switch]$AuthorizeSingleBuild
)

$ErrorActionPreference = 'Stop'
$root = 'D:\Skyguard52'
$attemptRoot = 'D:\Skyguard52\Saved\BuildAttempts\PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY03_NATIVE_BUILD_RECOVERY03\build_attempt_01'
$runtimeRoot = 'D:\Skyguard52\Saved\BuildAttempts\PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY03_NATIVE_BUILD_RECOVERY03\runtime_attempt_01'
$packageRoot = 'D:\SG52R03B04'
$pluginRoot = 'D:\Skyguard52\Plugins\SkyguardRecovery03NativeRecovery01'
$plugin = 'D:\Skyguard52\Plugins\SkyguardRecovery03NativeRecovery01\SkyguardRecovery03NativeRecovery01.uplugin'
$dotnet = 'D:\UE_5.8\Engine\Binaries\ThirdParty\DotNet\10.0\win-x64\dotnet.exe'
$automationAssembly = 'D:\UE_5.8\Engine\Binaries\DotNET\AutomationTool\AutomationTool.dll'
$workingDirectory = 'D:\UE_5.8\Engine\Binaries\DotNET\AutomationTool'
$normalManifest = 'D:\Skyguard52\Saved\Reports\PHASE4_M01_RECOVERY03_NATIVE_BUILD_RECOVERY03_TERMINAL_SUPERVISOR_MANIFEST.json'
$normalEmergency = 'D:\Skyguard52\Saved\Reports\PHASE4_M01_RECOVERY03_NATIVE_BUILD_RECOVERY03_EMERGENCY_RECEIPT.jsonl'
$offlineRoot = [System.IO.Path]::Combine($env:TEMP, 'SkyguardRecovery03OfflineContractTest')
$terminalManifest = if ($OfflineContractTest) { [System.IO.Path]::Combine($offlineRoot, 'terminal_manifest.json') } else { $normalManifest }
$emergencyReceipt = if ($OfflineContractTest) { [System.IO.Path]::Combine($offlineRoot, 'emergency_receipt.jsonl') } else { $normalEmergency }
$timeoutSeconds = 1200
$arguments = @(
    $automationAssembly,
    'BuildPlugin',
    "-Plugin=$plugin",
    "-Package=$packageRoot",
    '-TargetPlatforms=Win64',
    '-Rocket',
    '-StrictIncludes',
    '-NoP4'
)

function ConvertTo-JsonEscapedString([string]$Value) {
    if ($null -eq $Value) { return 'null' }
    $builder = New-Object System.Text.StringBuilder
    [void]$builder.Append('"')
    foreach ($character in $Value.ToCharArray()) {
        $code = [int][char]$character
        switch ($code) {
            8 { [void]$builder.Append('\b') }
            9 { [void]$builder.Append('\t') }
            10 { [void]$builder.Append('\n') }
            12 { [void]$builder.Append('\f') }
            13 { [void]$builder.Append('\r') }
            34 { [void]$builder.Append('\"') }
            92 { [void]$builder.Append('\\') }
            default {
                if ($code -lt 32) {
                    [void]$builder.Append(('\u{0:x4}' -f $code))
                } else {
                    [void]$builder.Append($character)
                }
            }
        }
    }
    [void]$builder.Append('"')
    return $builder.ToString()
}

function ConvertTo-SelfContainedJson($Value) {
    if ($null -eq $Value) { return 'null' }
    if ($Value -is [bool]) { if ($Value) { return 'true' } else { return 'false' } }
    if ($Value -is [byte] -or $Value -is [sbyte] -or $Value -is [int16] -or
        $Value -is [uint16] -or $Value -is [int32] -or $Value -is [uint32] -or
        $Value -is [int64] -or $Value -is [uint64] -or $Value -is [single] -or
        $Value -is [double] -or $Value -is [decimal]) {
        return [System.Convert]::ToString($Value, [System.Globalization.CultureInfo]::InvariantCulture)
    }
    if ($Value -is [string] -or $Value -is [char] -or $Value -is [datetime]) {
        return ConvertTo-JsonEscapedString ([string]$Value)
    }
    if ($Value -is [System.Collections.IDictionary]) {
        $pairs = New-Object System.Collections.Generic.List[string]
        foreach ($key in $Value.Keys) {
            $pairs.Add((ConvertTo-JsonEscapedString ([string]$key)) + ':' + (ConvertTo-SelfContainedJson $Value[$key]))
        }
        return '{' + [string]::Join(',', $pairs.ToArray()) + '}'
    }
    if ($Value -is [System.Collections.IEnumerable]) {
        $items = New-Object System.Collections.Generic.List[string]
        foreach ($item in $Value) { $items.Add((ConvertTo-SelfContainedJson $item)) }
        return '[' + [string]::Join(',', $items.ToArray()) + ']'
    }
    $properties = [ordered]@{}
    foreach ($property in $Value.PSObject.Properties) { $properties[$property.Name] = $property.Value }
    return ConvertTo-SelfContainedJson $properties
}

function Write-SelfContainedJson([string]$Path, $Value) {
    $parent = [System.IO.Path]::GetDirectoryName($Path)
    if (-not [string]::IsNullOrWhiteSpace($parent)) {
        [void][System.IO.Directory]::CreateDirectory($parent)
    }
    $encoding = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path, (ConvertTo-SelfContainedJson $Value), $encoding)
}

function Get-SelfContainedSha256([string]$Path) {
    if (-not [System.IO.File]::Exists($Path)) { throw "Missing file: $Path" }
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
        if ($null -eq $digest -or $digest.Length -ne 32) { throw "Invalid SHA-256 result: $Path" }
        if ($stream.Position -ne $stream.Length) { throw "Partial hash read: $Path" }
        $builder = New-Object System.Text.StringBuilder
        foreach ($value in $digest) { [void]$builder.Append($value.ToString('x2')) }
        $result = $builder.ToString()
        if ($result -cnotmatch '^[0-9a-f]{64}$') { throw "Invalid lowercase SHA-256 formatting: $Path" }
        return $result
    } finally {
        if ($null -ne $algorithm) { $algorithm.Dispose() }
        if ($null -ne $stream) { $stream.Dispose() }
    }
}

function Assert-FrozenFile([string]$Path, [long]$Bytes, [string]$Sha256) {
    if (-not [System.IO.File]::Exists($Path)) { throw "Missing authority: $Path" }
    $info = New-Object System.IO.FileInfo($Path)
    if ($info.Length -ne $Bytes) { throw "Authority byte mismatch: $Path" }
    if ((Get-SelfContainedSha256 $Path) -cne $Sha256) { throw "Authority hash mismatch: $Path" }
}

function Get-HeavyProcesses {
    $heavyNames = @('UnrealEditor', 'UnrealEditor-Cmd', 'ShaderCompileWorker', 'blender', 'AutomationTool', 'UnrealBuildTool', 'dotnet')
    $found = @()
    foreach ($candidate in [System.Diagnostics.Process]::GetProcesses()) {
        try {
            if ($heavyNames -contains $candidate.ProcessName) {
                $found += [ordered]@{ pid = $candidate.Id; name = $candidate.ProcessName }
            }
        } finally {
            $candidate.Dispose()
        }
    }
    return @($found)
}

function Get-ProcessTreeSample([int]$RootPid) {
    $searcher = $null
    $results = $null
    try {
        $searcher = New-Object System.Management.ManagementObjectSearcher(
            'SELECT ProcessId,ParentProcessId,Name,CommandLine FROM Win32_Process'
        )
        $results = $searcher.Get()
        $rows = @()
        foreach ($row in $results) {
            $rows += [ordered]@{
                pid = [int]$row.ProcessId
                parent_pid = [int]$row.ParentProcessId
                name = [string]$row.Name
                command_line = [string]$row.CommandLine
            }
        }
        $known = @($RootPid)
        $changed = $true
        while ($changed) {
            $changed = $false
            foreach ($row in $rows) {
                if ($known -contains $row.parent_pid -and $known -notcontains $row.pid) {
                    $known += $row.pid
                    $changed = $true
                }
            }
        }
        return @($rows | Where-Object { $known -contains $_.pid })
    } finally {
        if ($null -ne $results) { $results.Dispose() }
        if ($null -ne $searcher) { $searcher.Dispose() }
    }
}

function Copy-DirectoryFiles([string]$Source, [string]$Destination) {
    if (-not [System.IO.Directory]::Exists($Source)) { throw "Missing copy source: $Source" }
    [void][System.IO.Directory]::CreateDirectory($Destination)
    foreach ($directory in [System.IO.Directory]::EnumerateDirectories($Source, '*', [System.IO.SearchOption]::AllDirectories)) {
        $relative = $directory.Substring($Source.Length).TrimStart('\')
        [void][System.IO.Directory]::CreateDirectory([System.IO.Path]::Combine($Destination, $relative))
    }
    foreach ($file in [System.IO.Directory]::EnumerateFiles($Source, '*', [System.IO.SearchOption]::AllDirectories)) {
        $relative = $file.Substring($Source.Length).TrimStart('\')
        $target = [System.IO.Path]::Combine($Destination, $relative)
        [System.IO.File]::Copy($file, $target, $true)
    }
}

function Write-Emergency([string]$Stage, [string]$Issue) {
    try {
        $record = [ordered]@{
            utc = [DateTime]::UtcNow.ToString('o')
            stage = $Stage
            issue = $Issue
            contract_id = 'P4.6-M01-RECOVERY03-NATIVE-BUILD-RECOVERY03'
        }
        $parent = [System.IO.Path]::GetDirectoryName($emergencyReceipt)
        [void][System.IO.Directory]::CreateDirectory($parent)
        $encoding = New-Object System.Text.UTF8Encoding($false)
        [System.IO.File]::AppendAllText($emergencyReceipt, (ConvertTo-SelfContainedJson $record) + [Environment]::NewLine, $encoding)
    } catch {}
}

$state = [ordered]@{
    schema = 'skyguard.recovery03-native-build-recovery03-terminal-supervisor.v1'
    contract_id = 'P4.6-M01-RECOVERY03-NATIVE-BUILD-RECOVERY03'
    offline_contract_test = [bool]$OfflineContractTest
    supervisor_started_utc = [DateTime]::UtcNow.ToString('o')
    supervisor_ended_utc = $null
    supervisor_launch_count = 1
    bundled_dotnet_launch_count = 0
    automation_tool_invocation_count = 0
    retry_count = 0
    automatic_retry = $false
    preflight_passed = $false
    governed_build_namespace_created = $false
    package_root_created = $false
    process_id = $null
    process_handle_retained = $false
    timed_out = $false
    numeric_exit_code = $null
    exit_code_type = $null
    failure_stage = $null
    failure_message = $null
    produced_files = @()
    rebound = $false
    unreal_editor_launched = $false
    native_build_launched = $false
    terminal_manifest_path = $terminalManifest
}
$process = $null
$processHandle = $null
$finalExitCode = 1
$manifestWritten = $false

try {
    if ($OfflineContractTest) {
        if ([System.IO.Directory]::Exists($offlineRoot)) {
            [System.IO.Directory]::Delete($offlineRoot, $true)
        }
        [void][System.IO.Directory]::CreateDirectory($offlineRoot)
    } else {
        if (-not $AuthorizeSingleBuild) { throw 'Normal build mode requires -AuthorizeSingleBuild.' }
        if ([System.IO.File]::Exists($normalManifest)) { throw "Terminal manifest namespace exists: $normalManifest" }
        if ([System.IO.File]::Exists($normalEmergency)) { throw "Emergency receipt namespace exists: $normalEmergency" }
    }

    $authorities = @(
        @('D:\Skyguard52\Docs\AAA_Review\PHASE4_M01_RECOVERY03_NATIVE_BUILD_RECOVERY02_SUPERVISOR_ATTEMPT01_TERMINAL_FREEZE.json', 2925, 'a52ca2aa1cede3dbdefbb3779954bf0381f16d1a86e5b9dc3913d2965f49c669'),
        @('D:\Skyguard52\Docs\AAA_Review\PHASE4_M01_RECOVERY03_NATIVE_BUILD_RECOVERY02_FREEZE.json', 3528, 'f70f9a8dd1dfc9a7dd0649de8f141ee416c55e20dde3a4764290eab233430026'),
        @('D:\Skyguard52\Docs\AAA_Review\PHASE4_M01_RECOVERY03_NATIVE_BUILD_RECOVERY01_ATTEMPT01_TERMINAL_FREEZE.json', 2765, '2fa345942cc9e4e7b91825257b893479372c7d2b8afcdea8d97067a8239bfb4a'),
        @('D:\Skyguard52\Docs\AAA_Review\PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY03_NATIVE_BUILD_RECOVERY01_FREEZE.json', 3998, '35791f4e8b6557d5c85d354cbb2e0a6ab57933fc9d6942381f462d7077315258'),
        @('D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe', 512952, '0fb325cf215cc800ce260a1890af3f3dc314b8cc6331061d4e7e7246489af2e0'),
        @($dotnet, 178400, 'a8d3105441b568cfd44ac5eab8c0fc190cdefb0047e3e84e49cbce819a197a7a'),
        @($automationAssembly, 34232, 'ff7d013adf719a4e21be224edb70fb97aac78abf9de127ad81afe63b8ee51125'),
        @($plugin, 452, '4953138e24d76aee6db3636ae1c7a0fe3ed84cf1fabcb746c762d2f5a908963e'),
        @('D:\Skyguard52\Plugins\SkyguardRecovery03NativeRecovery01\Source\SkyguardRecovery03NativeRecovery01\SkyguardRecovery03NativeRecovery01.Build.cs', 592, '503a39136a154158474f5d54ad55a00ccaed50c975b008174c3678434d2f1831'),
        @('D:\Skyguard52\Plugins\SkyguardRecovery03NativeRecovery01\Source\SkyguardRecovery03NativeRecovery01\Public\SkyguardRecovery03NativeRecovery01Module.h', 3126, '3f1be719e2a33314b2954858521e49955999b547a581c92c27426d647873a9a4'),
        @('D:\Skyguard52\Plugins\SkyguardRecovery03NativeRecovery01\Source\SkyguardRecovery03NativeRecovery01\Private\SkyguardRecovery03NativeRecovery01Module.cpp', 26674, '65b9e514819cbd531edcb71fb4d754e5180dde2996bc883125c31c2cd27d73c6')
    )
    foreach ($authority in $authorities) {
        Assert-FrozenFile ([string]$authority[0]) ([long]$authority[1]) ([string]$authority[2])
    }

    if ($OfflineContractTest) {
        $missingRejected = $false
        try { [void](Get-SelfContainedSha256 ([System.IO.Path]::Combine($offlineRoot, 'missing.bin'))) } catch { $missingRejected = $true }
        if (-not $missingRejected) { throw 'Missing-file rejection failed.' }

        $wrongBytesRejected = $false
        try { Assert-FrozenFile $plugin 451 '4953138e24d76aee6db3636ae1c7a0fe3ed84cf1fabcb746c762d2f5a908963e' } catch { $wrongBytesRejected = $true }
        if (-not $wrongBytesRejected) { throw 'Wrong-byte-count rejection failed.' }

        $wrongHashRejected = $false
        try { Assert-FrozenFile $plugin 452 ('0' * 64) } catch { $wrongHashRejected = $true }
        if (-not $wrongHashRejected) { throw 'Wrong-hash rejection failed.' }

        $digest = Get-SelfContainedSha256 $plugin
        if ($digest -cnotmatch '^[0-9a-f]{64}$') { throw 'Lowercase digest validation failed.' }
        $state.preflight_passed = $true
        $state.failure_stage = $null
        $state.failure_message = $null
        $finalExitCode = 0
    } else {
        $heavy = @(Get-HeavyProcesses)
        if ($heavy.Count -ne 0) {
            throw "Heavy process preflight failed: $([string]::Join(', ', @($heavy | ForEach-Object { $_.name })))"
        }
        foreach ($path in @($attemptRoot, $runtimeRoot, $packageRoot)) {
            if ([System.IO.Directory]::Exists($path) -or [System.IO.File]::Exists($path)) {
                throw "Future namespace exists: $path"
            }
        }
        $state.preflight_passed = $true
        [void][System.IO.Directory]::CreateDirectory([System.IO.Path]::Combine($attemptRoot, 'logs'))
        $state.governed_build_namespace_created = $true
        $stdoutPath = [System.IO.Path]::Combine($attemptRoot, 'logs', 'build.stdout.log')
        $stderrPath = [System.IO.Path]::Combine($attemptRoot, 'logs', 'build.stderr.log')
        $treePath = [System.IO.Path]::Combine($attemptRoot, 'process_tree_samples.jsonl')
        $state.native_build_launched = $true
        $process = Start-Process -FilePath $dotnet -WorkingDirectory $workingDirectory -ArgumentList $arguments -PassThru -WindowStyle Hidden -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath
        $state.bundled_dotnet_launch_count = 1
        $state.automation_tool_invocation_count = 1
        $state.process_id = $process.Id
        $processHandle = $process.Handle
        $state.process_handle_retained = ($processHandle -ne [IntPtr]::Zero)
        $deadline = [DateTime]::UtcNow.AddSeconds($timeoutSeconds)
        while (-not $process.HasExited -and [DateTime]::UtcNow -lt $deadline) {
            $sample = [ordered]@{
                utc = [DateTime]::UtcNow.ToString('o')
                root_pid = $process.Id
                processes = @(Get-ProcessTreeSample $process.Id)
            }
            $encoding = New-Object System.Text.UTF8Encoding($false)
            [System.IO.File]::AppendAllText($treePath, (ConvertTo-SelfContainedJson $sample) + [Environment]::NewLine, $encoding)
            [System.Threading.Thread]::Sleep(2000)
            $process.Refresh()
        }
        if (-not $process.HasExited) {
            $state.timed_out = $true
            $process.Kill()
        }
        $process.WaitForExit()
        $process.Refresh()
        if ($null -eq $process.ExitCode -or $process.ExitCode -isnot [int]) {
            throw 'Bundled dotnet returned a null or nonnumeric exit code.'
        }
        $state.numeric_exit_code = [int]$process.ExitCode
        $state.exit_code_type = $process.ExitCode.GetType().FullName
        if ($state.numeric_exit_code -ne 0) {
            throw "Bundled dotnet returned exit code $($state.numeric_exit_code)."
        }
        if (-not [System.IO.Directory]::Exists($packageRoot)) { throw 'Successful child produced no package root.' }
        $state.package_root_created = $true
        $produced = @()
        foreach ($file in [System.IO.Directory]::EnumerateFiles($packageRoot, '*', [System.IO.SearchOption]::AllDirectories)) {
            $info = New-Object System.IO.FileInfo($file)
            $produced += [ordered]@{
                file = $file
                bytes = $info.Length
                sha256 = Get-SelfContainedSha256 $file
            }
        }
        $state.produced_files = $produced
        $binaryRoot = [System.IO.Path]::Combine($packageRoot, 'Binaries', 'Win64')
        foreach ($required in @(
            [System.IO.Path]::Combine($binaryRoot, 'UnrealEditor-SkyguardRecovery03NativeRecovery01.dll'),
            [System.IO.Path]::Combine($binaryRoot, 'UnrealEditor-SkyguardRecovery03NativeRecovery01.pdb'),
            [System.IO.Path]::Combine($binaryRoot, 'UnrealEditor.modules')
        )) {
            if (-not [System.IO.File]::Exists($required)) { throw "Missing successful-build artifact: $required" }
        }
        $sourcePairs = @(
            @('D:\Skyguard52\Plugins\SkyguardRecovery03NativeRecovery01\Source\SkyguardRecovery03NativeRecovery01\SkyguardRecovery03NativeRecovery01.Build.cs', [System.IO.Path]::Combine($packageRoot, 'Source', 'SkyguardRecovery03NativeRecovery01', 'SkyguardRecovery03NativeRecovery01.Build.cs')),
            @('D:\Skyguard52\Plugins\SkyguardRecovery03NativeRecovery01\Source\SkyguardRecovery03NativeRecovery01\Public\SkyguardRecovery03NativeRecovery01Module.h', [System.IO.Path]::Combine($packageRoot, 'Source', 'SkyguardRecovery03NativeRecovery01', 'Public', 'SkyguardRecovery03NativeRecovery01Module.h')),
            @('D:\Skyguard52\Plugins\SkyguardRecovery03NativeRecovery01\Source\SkyguardRecovery03NativeRecovery01\Private\SkyguardRecovery03NativeRecovery01Module.cpp', [System.IO.Path]::Combine($packageRoot, 'Source', 'SkyguardRecovery03NativeRecovery01', 'Private', 'SkyguardRecovery03NativeRecovery01Module.cpp'))
        )
        foreach ($pair in $sourcePairs) {
            if ((Get-SelfContainedSha256 $pair[0]) -cne (Get-SelfContainedSha256 $pair[1])) {
                throw "Packaged source mismatch: $($pair[1])"
            }
        }
        Copy-DirectoryFiles ([System.IO.Path]::Combine($packageRoot, 'Binaries')) ([System.IO.Path]::Combine($pluginRoot, 'Binaries'))
        $state.rebound = $true
        $finalExitCode = 0
    }
} catch {
    $state.failure_stage = if ($state.preflight_passed) { 'execution_or_validation' } else { 'preflight' }
    $state.failure_message = $_.Exception.Message
    $finalExitCode = 1
} finally {
    $state.supervisor_ended_utc = [DateTime]::UtcNow.ToString('o')
    try {
        Write-SelfContainedJson $terminalManifest $state
        $manifestWritten = [System.IO.File]::Exists($terminalManifest)
    } catch {
        Write-Emergency 'terminal_manifest' $_.Exception.Message
    }
    if (-not $manifestWritten) {
        Write-Emergency 'terminal_manifest_confirmation' 'Terminal supervisor manifest was not durable.'
        $finalExitCode = 1
    }
    if ($null -ne $process) { $process.Dispose() }
}

if ($OfflineContractTest -and $manifestWritten) {
    [Console]::Out.WriteLine((ConvertTo-SelfContainedJson ([ordered]@{
        gate = if ($finalExitCode -eq 0) { 'PASS' } else { 'FAIL' }
        exit_code = $finalExitCode
        exit_code_type = $finalExitCode.GetType().FullName
        terminal_manifest = $terminalManifest
        governed_build_namespace_created = $state.governed_build_namespace_created
        bundled_dotnet_launch_count = $state.bundled_dotnet_launch_count
        automation_tool_invocation_count = $state.automation_tool_invocation_count
    })))
}
exit $finalExitCode
