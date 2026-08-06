[CmdletBinding()]
param(
    [switch]$AuthorizeSingleBuild,
    [switch]$OfflineContractTest,
    [string]$OfflineEvidenceRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ProjectRoot = 'D:\Skyguard52'
$PluginRoot = 'D:\Skyguard52\Plugins\SkyguardRecovery03NativeRecovery05'
$Descriptor = Join-Path $PluginRoot 'SkyguardRecovery03NativeRecovery05.uplugin'
$PackageRoot = 'D:\SG52R05P01'
$AttemptRoot = 'D:\Skyguard52\Saved\BuildAttempts\PHASE4_M01_RECOVERY05_BUILDPLUGIN01\build_attempt_01'
$RuntimeRoot = 'D:\Skyguard52\Saved\BuildAttempts\PHASE4_M01_RECOVERY05_BUILDPLUGIN01\runtime_attempt_01'
$TerminalManifest = 'D:\Skyguard52\Saved\Reports\PHASE4_M01_RECOVERY05_BUILDPLUGIN01_TERMINAL_SUPERVISOR_MANIFEST.json'
$EmergencyReceipt = 'D:\Skyguard52\Saved\Reports\PHASE4_M01_RECOVERY05_BUILDPLUGIN01_EMERGENCY_RECEIPT.jsonl'
$Dotnet = 'D:\UE_5.8\Engine\Binaries\ThirdParty\DotNet\10.0\win-x64\dotnet.exe'
$AutomationTool = 'D:\UE_5.8\Engine\Binaries\DotNET\AutomationTool\AutomationTool.dll'
$MigrationFreeze = 'D:\Skyguard52\Docs\AAA_Review\PHASE4_M01_RECOVERY05_ACTIVE_PLUGIN_ROOT_MIGRATION01_TERMINAL_FREEZE.json'
$PostMigrationInventory = 'D:\Skyguard52\Saved\Reports\PHASE4_M01_RECOVERY05_ACTIVE_PLUGIN_ROOT_MIGRATION01_POST_MIGRATION_INVENTORY.json'
$Recovery04Freeze = 'D:\Skyguard52\Docs\AAA_Review\PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_RECOVERY04_ATTEMPT01_TERMINAL_FREEZE.json'
$BuildArguments = @(
    $AutomationTool,
    'BuildPlugin',
    "-Plugin=$Descriptor",
    "-Package=$PackageRoot",
    '-TargetPlatforms=Win64',
    '-Rocket',
    '-StrictIncludes',
    '-NoP4'
)

function Get-Sha256([string]$Path) {
    if (-not [System.IO.File]::Exists($Path)) { throw "Missing file: $Path" }
    $stream = $null
    $sha = $null
    try {
        $stream = [System.IO.File]::Open($Path, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::Read)
        $sha = [System.Security.Cryptography.SHA256]::Create()
        return ([System.BitConverter]::ToString($sha.ComputeHash($stream))).Replace('-', '').ToLowerInvariant()
    } finally {
        if ($null -ne $sha) { $sha.Dispose() }
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
    $json = $Value | ConvertTo-Json -Depth 20
    [System.IO.File]::WriteAllText($temp, $json, [System.Text.UTF8Encoding]::new($false))
    [System.IO.File]::Move($temp, $Path)
}

function Assert-Authorities {
    Assert-File $MigrationFreeze 3428 '681254354931d611aeed0bf702086064d50b4b47d90446f2de26faf7a1394f27'
    Assert-File $PostMigrationInventory 12569 '8c4db237b825e88941b48c232898f087cb0fe23253b4a3f96500af52d3cb9fc6'
    Assert-File $Recovery04Freeze 5005 'f23f8858ff4e0b65735cd498e022c7dcc32a0755b13a23f18f878ab363002aa5'
    Assert-File $Dotnet 178400 'a8d3105441b568cfd44ac5eab8c0fc190cdefb0047e3e84e49cbce819a197a7a'
    Assert-File $AutomationTool 34232 'ff7d013adf719a4e21be224edb70fb97aac78abf9de127ad81afe63b8ee51125'
    $inventory = Get-Content -Raw -LiteralPath $PostMigrationInventory | ConvertFrom-Json
    if ($inventory.record_count -ne 23 -or $inventory.active_record_count -ne 5 -or $inventory.quarantine_record_count -ne 18) {
        throw 'Migration inventory counts differ from frozen authority.'
    }
    foreach ($record in $inventory.records) { Assert-File $record.current_path ([long]$record.bytes) $record.sha256 }
    $activeRoots = @(Get-ChildItem -LiteralPath (Join-Path $ProjectRoot 'Plugins') -Directory)
    if ($activeRoots.Count -ne 1 -or $activeRoots[0].Name -ne 'SkyguardRecovery03NativeRecovery05') {
        throw 'Active plugin discovery set is not exactly Recovery05.'
    }
    $descriptorJson = Get-Content -Raw -LiteralPath $Descriptor | ConvertFrom-Json
    if ($descriptorJson.EnabledByDefault -ne $false) { throw 'Recovery05 plugin must remain disabled by default.' }
}

function Assert-NoHeavyProcess {
    $heavy = @(Get-Process -ErrorAction SilentlyContinue | Where-Object {
        $_.ProcessName -match '^(UnrealEditor|UnrealEditor-Cmd|ShaderCompileWorker|AutomationTool|UnrealBuildTool|blender|dotnet|cl|link)$'
    })
    if ($heavy.Count -gt 0) { throw "Heavy process active: $($heavy.ProcessName -join ', ')" }
}

$state = [ordered]@{
    schema = 'skyguard.phase4.m01-recovery05-buildplugin01-terminal-supervisor-manifest.v1'
    classification = 'FAILED_WITH_EVIDENCE'
    mode = if ($OfflineContractTest) { 'offline_contract_test' } else { 'normal_build' }
    started_utc = [DateTime]::UtcNow.ToString('o')
    ended_utc = $null
    failure_stage = $null
    failure_message = $null
    preflight_passed = $false
    governed_namespace_created = $false
    package_root_created = $false
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
    working_directory = (Split-Path -Parent $AutomationTool)
    produced_files = @()
}

$manifestPath = if ($OfflineContractTest) {
    if ([string]::IsNullOrWhiteSpace($OfflineEvidenceRoot)) { throw '-OfflineEvidenceRoot is required in offline mode.' }
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
        try { Assert-File $MigrationFreeze 1 '00'; throw 'Incorrect authority rejection failed.' } catch {
            if ($_.Exception.Message -eq 'Incorrect authority rejection failed.') { throw }
        }
        try { Assert-File 'Z:\definitely-missing\authority.bin' 1 '00'; throw 'Missing-file rejection failed.' } catch {
            if ($_.Exception.Message -eq 'Missing-file rejection failed.') { throw }
        }
        if ($BuildArguments.Count -ne 8 -or $BuildArguments[0] -ne $AutomationTool -or $BuildArguments[1] -ne 'BuildPlugin') {
            throw 'Frozen argument array differs.'
        }
        foreach ($path in @($PackageRoot,$AttemptRoot,$RuntimeRoot,$TerminalManifest,$EmergencyReceipt)) {
            if (Test-Path -LiteralPath $path) { throw "Future governed namespace exists: $path" }
        }
        $state.preflight_passed = $true
        $state.classification = 'PASS'
        $state.exit_code = 0
        $state.exit_code_type = 'System.Int32'
        $exitCode = 0
        return
    }

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
    if (-not $process.HasExited) {
        $state.timeout = $true
        throw 'BuildPlugin exceeded 1200-second timeout.'
    }
    $process.WaitForExit()
    $process.Refresh()
    $nativeCode = $process.ExitCode
    if ($null -eq $nativeCode -or -not ($nativeCode -is [int])) { throw 'Child exit code is null or nonnumeric.' }
    $state.exit_code = $nativeCode
    $state.exit_code_type = $nativeCode.GetType().FullName
    Write-JsonAtomic (Join-Path $AttemptRoot 'process_tree_samples.json') $samples
    if ($nativeCode -ne 0) { throw "BuildPlugin returned exit code $nativeCode." }

    $stage = 'output_validation'
    $required = @(
        (Join-Path $PackageRoot 'Binaries\Win64\UnrealEditor-SkyguardRecovery03NativeRecovery05.dll'),
        (Join-Path $PackageRoot 'Binaries\Win64\UnrealEditor-SkyguardRecovery03NativeRecovery05.pdb'),
        (Join-Path $PackageRoot 'Binaries\Win64\UnrealEditor.modules'),
        (Join-Path $PackageRoot 'SkyguardRecovery03NativeRecovery05.uplugin')
    )
    foreach ($requiredPath in $required) { if (-not (Test-Path -LiteralPath $requiredPath -PathType Leaf)) { throw "Missing required output: $requiredPath" } }
    $sourceInventory = @(Get-ChildItem -LiteralPath $PluginRoot -File -Recurse | ForEach-Object {
        [ordered]@{ path=$_.FullName; bytes=$_.Length; sha256=Get-Sha256 $_.FullName }
    })
    $packageInventory = @(Get-ChildItem -LiteralPath $PackageRoot -File -Recurse | ForEach-Object {
        [ordered]@{ path=$_.FullName; bytes=$_.Length; sha256=Get-Sha256 $_.FullName }
    })
    $state.package_root_created = $true
    $state.produced_files = $packageInventory
    Write-JsonAtomic (Join-Path $AttemptRoot 'source_inventory.json') $sourceInventory
    Write-JsonAtomic (Join-Path $AttemptRoot 'package_inventory.json') $packageInventory
    $state.classification = 'PASSED_READY_FOR_EXPLICIT_RECOVERY05_RUNTIME_BINDING_DESIGN'
    $exitCode = 0
} catch {
    $state.failure_stage = $stage
    $state.failure_message = $_.Exception.Message
    if ($null -ne $process -and $process.HasExited) {
        try {
            $process.Refresh()
            if ($null -ne $process.ExitCode) {
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
            $receipt = [ordered]@{ utc=[DateTime]::UtcNow.ToString('o'); classification='FAILED_WITH_EVIDENCE'; failure_stage='terminal_manifest_write'; message=$_.Exception.Message }
            [System.IO.File]::AppendAllText($emergencyPath, (($receipt | ConvertTo-Json -Compress) + [Environment]::NewLine), [System.Text.UTF8Encoding]::new($false))
        } catch {}
        $exitCode = 1
    }
}

exit ([int]$exitCode)
