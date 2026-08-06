[CmdletBinding()]
param(
    [switch]$AuthorizeSingleBuild,
    [switch]$OfflineContractTest,
    [string]$OfflineEvidenceRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Root = 'D:\Skyguard52'
$PluginRoot = 'D:\Skyguard52\Plugins\SkyguardRecovery03NativeRecovery05'
$SourceDescriptor = Join-Path $PluginRoot 'SkyguardRecovery03NativeRecovery05.uplugin'
$PackageRoot = 'D:\SG52R05P02'
$PackagedDescriptor = Join-Path $PackageRoot 'SkyguardRecovery03NativeRecovery05.uplugin'
$AttemptRoot = 'D:\Skyguard52\Saved\BuildAttempts\PHASE4_M01_RECOVERY05_BUILDPLUGIN01_RECOVERY01\build_attempt_01'
$RuntimeRoot = 'D:\Skyguard52\Saved\BuildAttempts\PHASE4_M01_RECOVERY05_BUILDPLUGIN01_RECOVERY01\runtime_attempt_01'
$TerminalManifest = 'D:\Skyguard52\Saved\Reports\PHASE4_M01_RECOVERY05_BUILDPLUGIN01_RECOVERY01_TERMINAL_SUPERVISOR_MANIFEST.json'
$EmergencyReceipt = 'D:\Skyguard52\Saved\Reports\PHASE4_M01_RECOVERY05_BUILDPLUGIN01_RECOVERY01_EMERGENCY_RECEIPT.jsonl'
$Dotnet = 'D:\UE_5.8\Engine\Binaries\ThirdParty\DotNet\10.0\win-x64\dotnet.exe'
$AutomationTool = 'D:\UE_5.8\Engine\Binaries\DotNET\AutomationTool\AutomationTool.dll'
$FailedFreeze = 'D:\Skyguard52\Docs\AAA_Review\PHASE4_M01_RECOVERY05_BUILDPLUGIN01_ATTEMPT01_TERMINAL_FREEZE.json'
$OriginalOfflineFreeze = 'D:\Skyguard52\Docs\AAA_Review\PHASE4_M01_RECOVERY05_BUILDPLUGIN01_OFFLINE_DESIGN_FREEZE.json'
$PostMigrationInventory = 'D:\Skyguard52\Saved\Reports\PHASE4_M01_RECOVERY05_ACTIVE_PLUGIN_ROOT_MIGRATION01_POST_MIGRATION_INVENTORY.json'
$Recovery04Freeze = 'D:\Skyguard52\Docs\AAA_Review\PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_RECOVERY04_ATTEMPT01_TERMINAL_FREEZE.json'
$RejectedDescriptor = 'D:\SG52R05P01\SkyguardRecovery03NativeRecovery05.uplugin'
$BuildArguments = @(
    $AutomationTool,
    'BuildPlugin',
    "-Plugin=$SourceDescriptor",
    "-Package=$PackageRoot",
    '-TargetPlatforms=Win64',
    '-Rocket',
    '-StrictIncludes',
    '-NoP4'
)

function Get-Sha256([string]$Path) {
    if (-not [System.IO.File]::Exists($Path)) { throw "Missing file: $Path" }
    $stream = $null
    $hasher = $null
    try {
        $stream = [System.IO.File]::Open($Path, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::Read)
        $hasher = [System.Security.Cryptography.SHA256]::Create()
        return ([System.BitConverter]::ToString($hasher.ComputeHash($stream))).Replace('-', '').ToLowerInvariant()
    } finally {
        if ($null -ne $hasher) { $hasher.Dispose() }
        if ($null -ne $stream) { $stream.Dispose() }
    }
}

function Assert-File([string]$Path, [long]$Bytes, [string]$Sha256) {
    $item = Get-Item -LiteralPath $Path -ErrorAction Stop
    if ($item.Length -ne $Bytes) { throw "Byte mismatch: $Path" }
    if ((Get-Sha256 $Path) -ne $Sha256.ToLowerInvariant()) { throw "SHA-256 mismatch: $Path" }
}

function Write-JsonAtomic([string]$Path, $Value) {
    $parent = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $parent)) { [System.IO.Directory]::CreateDirectory($parent) | Out-Null }
    $temp = "$Path.tmp"
    [System.IO.File]::WriteAllText($temp, ($Value | ConvertTo-Json -Depth 30), [System.Text.UTF8Encoding]::new($false))
    if (Test-Path -LiteralPath $Path) {
        $backup = "$Path.atomic.backup"
        [System.IO.File]::Replace($temp, $Path, $backup)
        if (Test-Path -LiteralPath $backup) { Remove-Item -LiteralPath $backup -Force }
    } else {
        [System.IO.File]::Move($temp, $Path)
    }
}

function Get-ComparableDescriptorJson($Descriptor) {
    $copy = [ordered]@{}
    foreach ($property in $Descriptor.PSObject.Properties) {
        if ($property.Name -ne 'EnabledByDefault') { $copy[$property.Name] = $property.Value }
    }
    return ($copy | ConvertTo-Json -Depth 30 -Compress)
}

function Assert-OnlyEnabledByDefaultChanged($Before, $After) {
    if ((Get-ComparableDescriptorJson $Before) -cne (Get-ComparableDescriptorJson $After)) {
        throw 'Unexpected packaged-descriptor semantic mutation.'
    }
}

function Assert-DescriptorIdentity($Descriptor) {
    if ($Descriptor.FriendlyName -ne 'Skyguard Recovery03 Native Recovery05') { throw 'Wrong plugin identity.' }
    if (@($Descriptor.Modules).Count -ne 1) { throw 'Wrong module count.' }
    if ($Descriptor.Modules[0].Name -ne 'SkyguardRecovery03NativeRecovery05' -or
        $Descriptor.Modules[0].Type -ne 'Editor' -or
        $Descriptor.Modules[0].LoadingPhase -ne 'PostEngineInit') { throw 'Wrong module identity.' }
}

function Normalize-PackagedDescriptor([string]$Path, [string]$SemanticDiffPath) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw "Missing descriptor: $Path" }
    $beforeText = [System.IO.File]::ReadAllText($Path)
    try { $before = $beforeText | ConvertFrom-Json } catch { throw "Malformed descriptor JSON: $($_.Exception.Message)" }
    Assert-DescriptorIdentity $before
    $beforeComparable = Get-ComparableDescriptorJson $before
    $preHash = Get-Sha256 $Path
    if ($before.PSObject.Properties.Name -contains 'EnabledByDefault') {
        $before.EnabledByDefault = $false
    } else {
        $before | Add-Member -NotePropertyName EnabledByDefault -NotePropertyValue $false
    }
    $temp = "$Path.normalize.tmp"
    [System.IO.File]::WriteAllText($temp, ($before | ConvertTo-Json -Depth 30), [System.Text.UTF8Encoding]::new($false))
    $backup = "$Path.normalize.backup"
    [System.IO.File]::Replace($temp, $Path, $backup)
    if (Test-Path -LiteralPath $backup) { Remove-Item -LiteralPath $backup -Force }
    $after = [System.IO.File]::ReadAllText($Path) | ConvertFrom-Json
    Assert-DescriptorIdentity $after
    if ($after.EnabledByDefault -ne $false -or -not ($after.EnabledByDefault -is [bool])) { throw 'Normalized EnabledByDefault is not Boolean false.' }
    $afterComparable = Get-ComparableDescriptorJson $after
    Assert-OnlyEnabledByDefaultChanged $before $after
    $diff = [ordered]@{
        schema = 'skyguard.phase4.m01-recovery05-buildplugin01-recovery01-semantic-diff.v1'
        classification = 'PASS'
        descriptor = $Path
        pre_sha256 = $preHash
        post_sha256 = Get-Sha256 $Path
        permitted_change = 'EnabledByDefault added_or_changed_to_boolean_false'
        all_other_semantics_unchanged = $true
    }
    Write-JsonAtomic $SemanticDiffPath $diff
    return $diff
}

function Assert-NumericSuccessExitCode($Code) {
    if ($null -eq $Code -or -not ($Code -is [int])) { throw 'Build exit code is null or nonnumeric.' }
    if ($Code -ne 0) { throw "Build exit code is nonzero: $Code" }
}

function Assert-PackageOutputs([string]$RootPath) {
    $required = @(
        (Join-Path $RootPath 'Binaries\Win64\UnrealEditor-SkyguardRecovery03NativeRecovery05.dll'),
        (Join-Path $RootPath 'Binaries\Win64\UnrealEditor-SkyguardRecovery03NativeRecovery05.pdb'),
        (Join-Path $RootPath 'Binaries\Win64\UnrealEditor.modules'),
        (Join-Path $RootPath 'SkyguardRecovery03NativeRecovery05.uplugin'),
        (Join-Path $RootPath 'Source\SkyguardRecovery03NativeRecovery05\SkyguardRecovery03NativeRecovery05.Build.cs'),
        (Join-Path $RootPath 'Source\SkyguardRecovery03NativeRecovery05\Private\SkyguardRecovery03NativeRecovery05Module.cpp'),
        (Join-Path $RootPath 'Source\SkyguardRecovery03NativeRecovery05\Public\SkyguardRecovery03NativeRecovery05Module.h')
    )
    foreach ($path in $required) { if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Missing required package output: $path" } }
    $pairs = @(
        @((Join-Path $PluginRoot 'Source\SkyguardRecovery03NativeRecovery05\SkyguardRecovery03NativeRecovery05.Build.cs'), $required[4]),
        @((Join-Path $PluginRoot 'Source\SkyguardRecovery03NativeRecovery05\Private\SkyguardRecovery03NativeRecovery05Module.cpp'), $required[5]),
        @((Join-Path $PluginRoot 'Source\SkyguardRecovery03NativeRecovery05\Public\SkyguardRecovery03NativeRecovery05Module.h'), $required[6])
    )
    foreach ($pair in $pairs) { if ((Get-Sha256 $pair[0]) -ne (Get-Sha256 $pair[1])) { throw "Packaged source parity mismatch: $($pair[1])" } }
}

function Assert-Authorities {
    Assert-File $FailedFreeze 4578 'c7a9cda8d8bcefabb5b8466f5117ed318d893fb6e90382633b2c234901e73d42'
    Assert-File $OriginalOfflineFreeze 3205 '7ff4b16005cdee9666f75c447285ead3347444f06a28f2c5b846babcde8c6351'
    Assert-File $SourceDescriptor 465 '63e70f723e27f3c29536834dac8a7757629e43b02c13a02ae954fe2c432d57a5'
    Assert-File $PostMigrationInventory 12569 '8c4db237b825e88941b48c232898f087cb0fe23253b4a3f96500af52d3cb9fc6'
    Assert-File $Recovery04Freeze 5005 'f23f8858ff4e0b65735cd498e022c7dcc32a0755b13a23f18f878ab363002aa5'
    Assert-File $RejectedDescriptor 579 '0f9fb0cd1592c9bcfc2a152d35da23de64f4d7c04fe44c2886f2c181863dd917'
    Assert-File $Dotnet 178400 'a8d3105441b568cfd44ac5eab8c0fc190cdefb0047e3e84e49cbce819a197a7a'
    Assert-File $AutomationTool 34232 'ff7d013adf719a4e21be224edb70fb97aac78abf9de127ad81afe63b8ee51125'
    $inventory = Get-Content -Raw -LiteralPath $PostMigrationInventory | ConvertFrom-Json
    foreach ($record in $inventory.records) { Assert-File $record.current_path ([long]$record.bytes) $record.sha256 }
    $source = Get-Content -Raw -LiteralPath $SourceDescriptor | ConvertFrom-Json
    if ($source.EnabledByDefault -ne $false) { throw 'Active source descriptor is not disabled by default.' }
}

function Assert-NoHeavyProcess {
    $heavy = @(Get-Process -ErrorAction SilentlyContinue | Where-Object {
        $_.ProcessName -match '^(UnrealEditor|UnrealEditor-Cmd|ShaderCompileWorker|AutomationTool|UnrealBuildTool|blender|dotnet|cl|link)$'
    })
    if ($heavy.Count -gt 0) { throw "Heavy process active: $($heavy.ProcessName -join ', ')" }
}

$state = [ordered]@{
    schema = 'skyguard.phase4.m01-recovery05-buildplugin01-recovery01-terminal-supervisor-manifest.v1'
    classification = 'FAILED_WITH_EVIDENCE'
    mode = if ($OfflineContractTest) { 'offline_contract_test' } else { 'normal_build' }
    started_utc = [DateTime]::UtcNow.ToString('o')
    ended_utc = $null
    failure_stage = $null
    failure_message = $null
    preflight_passed = $false
    governed_namespace_created = $false
    package_root_created = $false
    descriptor_normalized = $false
    supervisor_launch_count = 1
    bundled_dotnet_launch_count = 0
    automation_tool_invocation_count = 0
    retry_count = 0
    unreal_editor_launch_count = 0
    blender_launch_count = 0
    timeout = $false
    exit_code = $null
    exit_code_type = $null
    executable = $Dotnet
    arguments = $BuildArguments
    produced_files = @()
}

$manifestPath = if ($OfflineContractTest) {
    if ([string]::IsNullOrWhiteSpace($OfflineEvidenceRoot)) { throw '-OfflineEvidenceRoot is required.' }
    Join-Path $OfflineEvidenceRoot 'terminal_manifest.json'
} else { $TerminalManifest }
$emergencyPath = if ($OfflineContractTest) { Join-Path $OfflineEvidenceRoot 'emergency_receipt.jsonl' } else { $EmergencyReceipt }
$stage = 'initialization'
$process = $null
$exitCode = 1

try {
    $stage = 'authority_preflight'
    Assert-Authorities
    Assert-NoHeavyProcess

    if ($OfflineContractTest) {
        $stage = 'offline_contract_test'
        [System.IO.Directory]::CreateDirectory($OfflineEvidenceRoot) | Out-Null
        $testDescriptor = Join-Path $OfflineEvidenceRoot 'descriptor.uplugin'
        Copy-Item -LiteralPath $RejectedDescriptor -Destination $testDescriptor
        $originalRejectedHash = Get-Sha256 $RejectedDescriptor
        Normalize-PackagedDescriptor $testDescriptor (Join-Path $OfflineEvidenceRoot 'semantic_diff.json') | Out-Null
        if ((Get-Sha256 $RejectedDescriptor) -ne $originalRejectedHash) { throw 'Rejected Attempt01 descriptor changed.' }

        $malformed = Join-Path $OfflineEvidenceRoot 'malformed.uplugin'
        [System.IO.File]::WriteAllText($malformed, '{not-json', [System.Text.UTF8Encoding]::new($false))
        try { Normalize-PackagedDescriptor $malformed (Join-Path $OfflineEvidenceRoot 'malformed_diff.json'); throw 'Malformed JSON rejection failed.' } catch {
            if ($_.Exception.Message -eq 'Malformed JSON rejection failed.') { throw }
        }
        $wrongPlugin = Join-Path $OfflineEvidenceRoot 'wrong-plugin.uplugin'
        Copy-Item $RejectedDescriptor $wrongPlugin
        $wp = Get-Content -Raw $wrongPlugin | ConvertFrom-Json
        $wp.FriendlyName = 'Wrong Plugin'
        [System.IO.File]::WriteAllText($wrongPlugin, ($wp | ConvertTo-Json -Depth 30), [System.Text.UTF8Encoding]::new($false))
        try { Normalize-PackagedDescriptor $wrongPlugin (Join-Path $OfflineEvidenceRoot 'wrong_plugin_diff.json'); throw 'Wrong plugin rejection failed.' } catch {
            if ($_.Exception.Message -eq 'Wrong plugin rejection failed.') { throw }
        }
        $wrongModule = Join-Path $OfflineEvidenceRoot 'wrong-module.uplugin'
        Copy-Item $RejectedDescriptor $wrongModule
        $wm = Get-Content -Raw $wrongModule | ConvertFrom-Json
        $wm.Modules[0].Name = 'WrongModule'
        [System.IO.File]::WriteAllText($wrongModule, ($wm | ConvertTo-Json -Depth 30), [System.Text.UTF8Encoding]::new($false))
        try { Normalize-PackagedDescriptor $wrongModule (Join-Path $OfflineEvidenceRoot 'wrong_module_diff.json'); throw 'Wrong module rejection failed.' } catch {
            if ($_.Exception.Message -eq 'Wrong module rejection failed.') { throw }
        }
        $semanticBefore = Get-Content -Raw $RejectedDescriptor | ConvertFrom-Json
        $semanticAfter = Get-Content -Raw $RejectedDescriptor | ConvertFrom-Json
        $semanticAfter.CreatedBy = 'Unexpected mutation'
        try { Assert-OnlyEnabledByDefaultChanged $semanticBefore $semanticAfter; throw 'Unexpected semantic mutation rejection failed.' } catch {
            if ($_.Exception.Message -eq 'Unexpected semantic mutation rejection failed.') { throw }
        }
        foreach ($badCode in @($null, '0', 7)) {
            try { Assert-NumericSuccessExitCode $badCode; throw 'Invalid exit-code rejection failed.' } catch {
                if ($_.Exception.Message -eq 'Invalid exit-code rejection failed.') { throw }
            }
        }
        Assert-NumericSuccessExitCode ([int]0)
        $missingRoot = Join-Path $OfflineEvidenceRoot 'missing-package'
        [System.IO.Directory]::CreateDirectory($missingRoot) | Out-Null
        try { Assert-PackageOutputs $missingRoot; throw 'Missing-output rejection failed.' } catch {
            if ($_.Exception.Message -eq 'Missing-output rejection failed.') { throw }
        }
        $mockRoot = Join-Path $OfflineEvidenceRoot 'mock-package'
        $mockFiles = @(
            'Binaries\Win64\UnrealEditor-SkyguardRecovery03NativeRecovery05.dll',
            'Binaries\Win64\UnrealEditor-SkyguardRecovery03NativeRecovery05.pdb',
            'Binaries\Win64\UnrealEditor.modules'
        )
        foreach ($relative in $mockFiles) {
            $target = Join-Path $mockRoot $relative
            [System.IO.Directory]::CreateDirectory((Split-Path -Parent $target)) | Out-Null
            [System.IO.File]::WriteAllBytes($target, [byte[]](1))
        }
        Copy-Item $RejectedDescriptor (Join-Path $mockRoot 'SkyguardRecovery03NativeRecovery05.uplugin')
        $mockSourceRoot = Join-Path $mockRoot 'Source\SkyguardRecovery03NativeRecovery05'
        [System.IO.Directory]::CreateDirectory((Join-Path $mockSourceRoot 'Private')) | Out-Null
        [System.IO.Directory]::CreateDirectory((Join-Path $mockSourceRoot 'Public')) | Out-Null
        Copy-Item (Join-Path $PluginRoot 'Source\SkyguardRecovery03NativeRecovery05\SkyguardRecovery03NativeRecovery05.Build.cs') (Join-Path $mockSourceRoot 'SkyguardRecovery03NativeRecovery05.Build.cs')
        Copy-Item (Join-Path $PluginRoot 'Source\SkyguardRecovery03NativeRecovery05\Private\SkyguardRecovery03NativeRecovery05Module.cpp') (Join-Path $mockSourceRoot 'Private\SkyguardRecovery03NativeRecovery05Module.cpp')
        Copy-Item (Join-Path $PluginRoot 'Source\SkyguardRecovery03NativeRecovery05\Public\SkyguardRecovery03NativeRecovery05Module.h') (Join-Path $mockSourceRoot 'Public\SkyguardRecovery03NativeRecovery05Module.h')
        Assert-PackageOutputs $mockRoot
        [System.IO.File]::AppendAllText((Join-Path $mockSourceRoot 'SkyguardRecovery03NativeRecovery05.Build.cs'), 'tamper')
        try { Assert-PackageOutputs $mockRoot; throw 'Source-parity rejection failed.' } catch {
            if ($_.Exception.Message -eq 'Source-parity rejection failed.') { throw }
        }
        foreach ($path in @($PackageRoot,$AttemptRoot,$RuntimeRoot,$TerminalManifest,$EmergencyReceipt)) {
            if (Test-Path -LiteralPath $path) { throw "Future governed namespace exists: $path" }
        }
        $state.preflight_passed = $true
        $state.descriptor_normalized = $true
        $state.classification = 'PASS'
        $state.exit_code = 0
        $state.exit_code_type = 'System.Int32'
        $exitCode = 0
    } else {
        if (-not $AuthorizeSingleBuild) { throw 'Normal mode requires -AuthorizeSingleBuild.' }
        foreach ($path in @($PackageRoot,$AttemptRoot,$RuntimeRoot,$TerminalManifest,$EmergencyReceipt)) {
            if (Test-Path -LiteralPath $path) { throw "Future governed namespace exists: $path" }
        }
        $state.preflight_passed = $true
        $stage = 'attempt_namespace'
        [System.IO.Directory]::CreateDirectory((Join-Path $AttemptRoot 'logs')) | Out-Null
        $state.governed_namespace_created = $true
        $stdout = Join-Path $AttemptRoot 'logs\build.stdout.log'
        $stderr = Join-Path $AttemptRoot 'logs\build.stderr.log'
        $stage = 'child_launch'
        $state.bundled_dotnet_launch_count = 1
        $state.automation_tool_invocation_count = 1
        $process = Start-Process -FilePath $Dotnet -ArgumentList $BuildArguments -WorkingDirectory (Split-Path -Parent $AutomationTool) -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru
        $handle = $process.Handle
        $deadline = [DateTime]::UtcNow.AddSeconds(1200)
        $samples = [System.Collections.Generic.List[object]]::new()
        while (-not $process.HasExited -and [DateTime]::UtcNow -lt $deadline) {
            $samples.Add([ordered]@{ utc=[DateTime]::UtcNow.ToString('o'); pid=$process.Id; handle=$handle; exited=$process.HasExited })
            Start-Sleep -Seconds 2
            $process.Refresh()
        }
        if (-not $process.HasExited) { $state.timeout = $true; throw 'BuildPlugin exceeded 1200-second timeout.' }
        $process.WaitForExit()
        $process.Refresh()
        Assert-NumericSuccessExitCode $process.ExitCode
        $state.exit_code = [int]$process.ExitCode
        $state.exit_code_type = $process.ExitCode.GetType().FullName
        Write-JsonAtomic (Join-Path $AttemptRoot 'process_tree_samples.json') $samples
        $stage = 'package_validation'
        Assert-PackageOutputs $PackageRoot
        $state.package_root_created = $true
        $stage = 'descriptor_normalization'
        Normalize-PackagedDescriptor $PackagedDescriptor (Join-Path $AttemptRoot 'descriptor_semantic_diff.json') | Out-Null
        $state.descriptor_normalized = $true
        $packageInventory = @(Get-ChildItem -LiteralPath $PackageRoot -File -Recurse | ForEach-Object {
            [ordered]@{ path=$_.FullName; bytes=$_.Length; sha256=Get-Sha256 $_.FullName }
        })
        $state.produced_files = $packageInventory
        Write-JsonAtomic (Join-Path $AttemptRoot 'package_inventory.json') $packageInventory
        $state.classification = 'PASSED_READY_FOR_EXPLICIT_RECOVERY05_RUNTIME_BINDING_DESIGN'
        $exitCode = 0
    }
} catch {
    $state.failure_stage = $stage
    $state.failure_message = $_.Exception.Message
    if ($null -ne $process -and $process.HasExited) {
        try {
            $process.Refresh()
            if ($null -ne $process.ExitCode -and $process.ExitCode -is [int]) {
                $state.exit_code = [int]$process.ExitCode
                $state.exit_code_type = $process.ExitCode.GetType().FullName
            }
        } catch {}
    }
    $exitCode = 1
} finally {
    $state.ended_utc = [DateTime]::UtcNow.ToString('o')
    try {
        Write-JsonAtomic $manifestPath $state
    } catch {
        try {
            $parent = Split-Path -Parent $emergencyPath
            if (-not (Test-Path -LiteralPath $parent)) { [System.IO.Directory]::CreateDirectory($parent) | Out-Null }
            $receipt = [ordered]@{ utc=[DateTime]::UtcNow.ToString('o'); classification='FAILED_WITH_EVIDENCE'; stage='terminal_manifest_write'; message=$_.Exception.Message }
            [System.IO.File]::AppendAllText($emergencyPath, (($receipt | ConvertTo-Json -Compress) + [Environment]::NewLine), [System.Text.UTF8Encoding]::new($false))
        } catch {}
        $exitCode = 1
    }
}
exit ([int]$exitCode)
