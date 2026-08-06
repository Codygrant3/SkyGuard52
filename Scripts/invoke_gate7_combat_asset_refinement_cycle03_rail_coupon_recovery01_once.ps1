param(
    [switch]$OfflineContractTest,
    [switch]$AuthorizeSingleBlender
)

$ErrorActionPreference = 'Stop'

$Gate = 'GATE7_COMBAT_ASSET_REFINEMENT_CYCLE03_RAIL_COUPON_RECOVERY01_ATTEMPT01'
$AttemptRoot = 'D:\Skyguard52\Saved\BuildAttempts\GATE7_COMBAT_ASSET_REFINEMENT_CYCLE03_RAIL_COUPON_RECOVERY01\attempt_01'
$OutputRoot = 'D:\Skyguard52\Blender\GATE7_COMBAT_ASSET_REFINEMENT_CYCLE03_RAIL_COUPON_RECOVERY01_ATTEMPT01'
$ExternalManifest = 'D:\Skyguard52\Saved\Reports\GATE7_COMBAT_ASSET_REFINEMENT_CYCLE03_RAIL_COUPON_RECOVERY01_TERMINAL_SUPERVISOR_MANIFEST.json'
$EmergencyReceipt = 'D:\Skyguard52\Saved\Reports\GATE7_COMBAT_ASSET_REFINEMENT_CYCLE03_RAIL_COUPON_RECOVERY01_EMERGENCY_RECEIPT.jsonl'
$ContractAuthority = 'D:\Skyguard52\References\CombatAssets\CombatAsset_Refinement_Cycle03_Rail_Coupon_Recovery01_OfflineDesign\contracts\GATE7_COMBAT_ASSET_REFINEMENT_CYCLE03_RAIL_COUPON_RECOVERY01_EXECUTION_CONTRACT.json'
$ContractBytes = 6798
$ContractSha256 = 'f57e5251344e8eda6b8ab6a91a50bf745d9b8ca2b5316558acb0438253b520a0'
$SourceAuthority = 'D:\Skyguard52\References\CombatAssets\CombatAsset_Refinement_Cycle03_Rail_Coupon_Recovery01_OfflineDesign\source\blender_gate7_combat_asset_refinement_cycle03_rail_coupon_recovery01_attempt01.py'
$BlenderExecutable = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
$TimeoutSeconds = 1200

$State = [ordered]@{
    gate = $Gate
    classification = 'FAILED_WITH_EVIDENCE'
    terminal = $false
    mode = if ($OfflineContractTest) { 'offline_contract_test' } else { 'single_blender_execution' }
    supervisor_launch_count = 1
    blender_launch_count = 0
    retry_count = 0
    unreal_launch_count = 0
    preflight_passed = $false
    governed_attempt_namespace_created = $false
    output_namespace_created = $false
    blender_pid = $null
    native_handle_retained = $false
    start_utc = [DateTime]::UtcNow.ToString('o')
    end_utc = $null
    timeout = $false
    exit_code = $null
    exit_code_type = $null
    failure_stage = $null
    failure_message = $null
    output_counts = [ordered]@{ blend = 0; glb = 0; png = 0 }
    dimension_receipt_state = 'NOT_EVALUATED'
    glb_structure_state = 'NOT_EVALUATED'
    terminal_receipt_state = 'NOT_EVALUATED'
    produced_files = @()
    process_tree_samples = @()
}
$ScriptExitCode = 1

function Get-Sha256Lower([string]$Path) {
    $stream = $null
    $sha = $null
    try {
        if ([string]::IsNullOrWhiteSpace($Path)) { throw 'Hash path is null or empty.' }
        $stream = [System.IO.File]::Open($Path, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::ReadWrite)
        $sha = [System.Security.Cryptography.SHA256]::Create()
        $digest = $sha.ComputeHash($stream)
        if ($null -eq $digest -or $digest.Length -ne 32) { throw 'SHA-256 returned a null or invalid digest.' }
        return ([System.BitConverter]::ToString($digest)).Replace('-', '').ToLowerInvariant()
    }
    finally {
        if ($sha) { $sha.Dispose() }
        if ($stream) { $stream.Dispose() }
    }
}

function Verify-FileAuthority([string]$Path, [long]$ExpectedBytes, [string]$ExpectedHash) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw "Missing authority: $Path" }
    $item = Get-Item -LiteralPath $Path
    if ($item.Length -ne $ExpectedBytes) { throw "Byte-count mismatch for $Path. Expected $ExpectedBytes, received $($item.Length)." }
    $actual = Get-Sha256Lower $Path
    if ($actual -ne $ExpectedHash.ToLowerInvariant()) { throw "SHA-256 mismatch for $Path" }
    return [ordered]@{ path = $Path; bytes = $item.Length; sha256 = $actual }
}

function Get-FileRecord([string]$Path) {
    $item = Get-Item -LiteralPath $Path
    return [ordered]@{ path = $item.FullName; bytes = $item.Length; sha256 = Get-Sha256Lower $item.FullName }
}

function Write-JsonAtomic([string]$Path, $Value) {
    $parent = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $parent)) { New-Item -ItemType Directory -Path $parent | Out-Null }
    $temporary = "$Path.tmp.$([Guid]::NewGuid().ToString('N'))"
    $json = $Value | ConvertTo-Json -Depth 20
    [System.IO.File]::WriteAllText($temporary, $json + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
    [System.IO.File]::Move($temporary, $Path)
}

function Write-EmergencyLine([string]$Path, $Value) {
    $parent = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $parent)) { New-Item -ItemType Directory -Path $parent | Out-Null }
    $line = ($Value | ConvertTo-Json -Depth 8 -Compress) + [Environment]::NewLine
    [System.IO.File]::AppendAllText($Path, $line, [System.Text.UTF8Encoding]::new($false))
}

function Write-TerminalEvidence([string]$ManifestPath, [string]$EmergencyPath, $Value) {
    try {
        Write-JsonAtomic $ManifestPath $Value
        return 'manifest'
    }
    catch {
        $emergency = [ordered]@{
            gate = $Value.gate
            classification = $Value.classification
            terminal = $true
            timestamp_utc = [DateTime]::UtcNow.ToString('o')
            manifest_error = $_.Exception.Message
            failure_stage = $Value.failure_stage
        }
        Write-EmergencyLine $EmergencyPath $emergency
        return 'emergency'
    }
}

function Get-Contract {
    $null = Verify-FileAuthority $ContractAuthority $ContractBytes $ContractSha256
    return ([System.IO.File]::ReadAllText($ContractAuthority) | ConvertFrom-Json)
}

function Verify-ContractAuthorities($Contract) {
    $records = @()
    foreach ($authority in @($Contract.authority_files)) {
        $records += Verify-FileAuthority ([string]$authority.path) ([long]$authority.bytes) ([string]$authority.sha256)
    }
    $records += Verify-FileAuthority $BlenderExecutable ([long]$Contract.execution_rules.blender_bytes) ([string]$Contract.execution_rules.blender_sha256)
    return $records
}

function Invoke-OfflineContractTest {
    $testRoot = Join-Path ([System.IO.Path]::GetTempPath()) ('SG52_G7_RAIL_R01_' + [Guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $testRoot | Out-Null
    $result = [ordered]@{
        classification = 'FAIL'
        contract_verified = $false
        authority_count = 0
        all_authorities_verified = $false
        state_serialization_passed = $false
        terminal_serialization_passed = $false
        future_attempt_absent = $false
        future_output_absent = $false
        future_manifest_absent = $false
        blender_launch_count = 0
        unreal_launch_count = 0
        error = $null
        temporary_test_root = $testRoot
    }
    try {
        $contract = Get-Contract
        $result.contract_verified = $true
        $verified = @(Verify-ContractAuthorities $contract)
        $result.authority_count = $verified.Count
        $result.all_authorities_verified = ($verified.Count -eq (@($contract.authority_files).Count + 1))
        $serialized = $State | ConvertTo-Json -Depth 20
        $result.state_serialization_passed = -not [string]::IsNullOrWhiteSpace($serialized)
        $temporaryManifest = Join-Path $testRoot 'terminal.json'
        $temporaryEmergency = Join-Path $testRoot 'emergency.jsonl'
        $terminalMode = Write-TerminalEvidence $temporaryManifest $temporaryEmergency ([ordered]@{
            gate = $Gate
            classification = 'OFFLINE_CONTRACT_TEST'
            terminal = $true
            failure_stage = $null
        })
        $result.terminal_serialization_passed = ($terminalMode -eq 'manifest' -and (Test-Path -LiteralPath $temporaryManifest))
        $result.future_attempt_absent = -not (Test-Path -LiteralPath $AttemptRoot)
        $result.future_output_absent = -not (Test-Path -LiteralPath $OutputRoot)
        $result.future_manifest_absent = -not (Test-Path -LiteralPath $ExternalManifest)
        if (-not $result.contract_verified -or -not $result.all_authorities_verified -or -not $result.state_serialization_passed -or -not $result.terminal_serialization_passed) {
            throw 'Offline contract assertion failed.'
        }
        if (-not $result.future_attempt_absent -or -not $result.future_output_absent -or -not $result.future_manifest_absent) {
            throw 'A governed future namespace exists.'
        }
        $result.classification = 'PASS'
    }
    catch {
        $result.error = $_.Exception.Message
    }
    return $result
}

try {
    if ($OfflineContractTest) {
        $offlineResult = Invoke-OfflineContractTest
        $offlineResult | ConvertTo-Json -Depth 12
        if ($offlineResult.classification -ne 'PASS') { throw "Offline contract test failed: $($offlineResult.error)" }
        $State.classification = 'OFFLINE_CONTRACT_TEST_PASS'
        $State.terminal = $true
        $ScriptExitCode = 0
    }
    else {
        if (-not $AuthorizeSingleBlender) { throw 'Explicit -AuthorizeSingleBlender is required.' }
        $State.failure_stage = 'AUTHORITY_PREFLIGHT'
        $contract = Get-Contract
        $null = Verify-ContractAuthorities $contract
        foreach ($namespace in @($AttemptRoot, $OutputRoot, $ExternalManifest, $EmergencyReceipt)) {
            if (Test-Path -LiteralPath $namespace) { throw "Governed future namespace already exists: $namespace" }
        }
        $heavy = @(Get-CimInstance Win32_Process -ErrorAction Stop | Where-Object {
            $_.Name -match '^(blender|UnrealEditor|ShaderCompileWorker|AutomationTool|UnrealBuildTool|cl|link)(\.exe)?$'
        })
        if ($heavy.Count -gt 0) { throw "Heavy process detected: $($heavy.Name -join ', ')" }

        $State.preflight_passed = $true
        $State.failure_stage = 'ATTEMPT_NAMESPACE_CREATION'
        $sourceDirectory = Join-Path $AttemptRoot 'source'
        New-Item -ItemType Directory -Path $sourceDirectory | Out-Null
        $State.governed_attempt_namespace_created = $true
        $sourceCopy = Join-Path $sourceDirectory 'blender_gate7_combat_asset_refinement_cycle03_rail_coupon_recovery01_attempt01.py'
        $contractCopy = Join-Path $AttemptRoot 'GATE7_COMBAT_ASSET_REFINEMENT_CYCLE03_RAIL_COUPON_RECOVERY01_EXECUTION_CONTRACT.json'
        Copy-Item -LiteralPath $SourceAuthority -Destination $sourceCopy
        Copy-Item -LiteralPath $ContractAuthority -Destination $contractCopy
        $sourceAuthorityRecord = Get-FileRecord $SourceAuthority
        $sourceCopyRecord = Get-FileRecord $sourceCopy
        if ($sourceAuthorityRecord.sha256 -ne $sourceCopyRecord.sha256 -or $sourceAuthorityRecord.bytes -ne $sourceCopyRecord.bytes) {
            throw 'Attempt source copy does not match the Recovery01 source authority.'
        }
        $null = Verify-FileAuthority $contractCopy $ContractBytes $ContractSha256

        Write-JsonAtomic (Join-Path $AttemptRoot 'preflight_receipt.json') ([ordered]@{
            gate = $Gate
            classification = 'PASSED_SINGLE_EXECUTION_PREFLIGHT'
            timestamp_utc = [DateTime]::UtcNow.ToString('o')
            contract = Get-FileRecord $contractCopy
            source = $sourceCopyRecord
            blender_launch_count = 0
            retry_count = 0
            unreal_launch_count = 0
        })

        $stdoutPath = Join-Path $AttemptRoot 'blender.stdout.log'
        $stderrPath = Join-Path $AttemptRoot 'blender.stderr.log'
        $arguments = @('--background', '--factory-startup', '--python', $sourceCopy, '--', '--output', $OutputRoot)
        $State.failure_stage = 'BLENDER_LAUNCH'
        $process = Start-Process -FilePath $BlenderExecutable -ArgumentList $arguments -WorkingDirectory $AttemptRoot -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath -PassThru
        $nativeHandle = $process.Handle
        if ($nativeHandle -eq [IntPtr]::Zero) { throw 'Blender native process handle was not retained.' }
        $State.native_handle_retained = $true
        $State.blender_launch_count = 1
        $State.blender_pid = $process.Id
        $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
        while (-not $process.HasExited -and [DateTime]::UtcNow -lt $deadline) {
            $sample = @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {
                $_.ProcessId -eq $process.Id -or $_.ParentProcessId -eq $process.Id
            } | Select-Object Name, ProcessId, ParentProcessId, CommandLine)
            $State.process_tree_samples += [ordered]@{ timestamp_utc = [DateTime]::UtcNow.ToString('o'); processes = $sample }
            Start-Sleep -Seconds 2
            $process.Refresh()
        }
        if (-not $process.HasExited) {
            $State.timeout = $true
            try { $process.Kill() } catch {}
            $process.WaitForExit()
            throw "Blender exceeded the $TimeoutSeconds-second timeout."
        }
        $process.WaitForExit()
        $process.Refresh()
        $capturedExitCode = $process.ExitCode
        if ($null -eq $capturedExitCode) { throw 'Blender exit code is null.' }
        if ($capturedExitCode -isnot [System.Int32]) { throw "Invalid Blender exit-code type: $($capturedExitCode.GetType().FullName)" }
        $State.exit_code = [System.Int32]$capturedExitCode
        $State.exit_code_type = $capturedExitCode.GetType().FullName
        if ($State.exit_code -ne 0) { throw "Blender returned nonzero exit code: $($State.exit_code)" }

        $State.failure_stage = 'OUTPUT_VALIDATION'
        $State.output_namespace_created = Test-Path -LiteralPath $OutputRoot
        if (-not $State.output_namespace_created) { throw 'Blender did not create the governed output namespace.' }
        $stderrText = if (Test-Path -LiteralPath $stderrPath) { [System.IO.File]::ReadAllText($stderrPath) } else { '' }
        if ($stderrText -match '(?i)traceback|error:') { throw 'Blender stderr contains a traceback or error.' }
        $blendFiles = @(Get-ChildItem -LiteralPath $OutputRoot -Filter '*.blend' -File)
        $glbFiles = @(Get-ChildItem -LiteralPath (Join-Path $OutputRoot 'exports') -Filter '*.glb' -File)
        $pngFiles = @(Get-ChildItem -LiteralPath (Join-Path $OutputRoot 'renders') -Filter '*.png' -File)
        $State.output_counts = [ordered]@{ blend = $blendFiles.Count; glb = $glbFiles.Count; png = $pngFiles.Count }
        if ($blendFiles.Count -ne 1 -or $glbFiles.Count -ne 1 -or $pngFiles.Count -ne 11) {
            throw 'Blender output counts do not match the Recovery01 contract.'
        }
        $dimensionReceiptPath = Join-Path $OutputRoot 'dimension_receipt.json'
        $glbReceiptPath = Join-Path $OutputRoot 'glb_structure_receipt.json'
        $inventoryPath = Join-Path $OutputRoot 'artifact_inventory.json'
        $terminalReceiptPath = Join-Path $OutputRoot 'terminal_receipt.json'
        foreach ($required in @($dimensionReceiptPath, $glbReceiptPath, $inventoryPath, $terminalReceiptPath)) {
            if (-not (Test-Path -LiteralPath $required -PathType Leaf)) { throw "Required output receipt is missing: $required" }
        }
        $dimensionReceipt = [System.IO.File]::ReadAllText($dimensionReceiptPath) | ConvertFrom-Json
        $glbReceipt = [System.IO.File]::ReadAllText($glbReceiptPath) | ConvertFrom-Json
        $terminalReceipt = [System.IO.File]::ReadAllText($terminalReceiptPath) | ConvertFrom-Json
        if (-not [bool]$dimensionReceipt.dimension_validation.all_passed) { throw 'Dimension receipt did not pass.' }
        if (-not [bool]$glbReceipt.structure.socket_present -or -not [bool]$glbReceipt.structure.collision_present) {
            throw 'GLB structure receipt is missing the socket or collision.'
        }
        if ($terminalReceipt.gate -ne $Gate -or $terminalReceipt.status -ne 'BLENDER_COMPLETED_AWAITING_EXTERNAL_VISUAL_REVIEW') {
            throw 'Terminal receipt identity or status is invalid.'
        }
        $State.dimension_receipt_state = 'PASSED'
        $State.glb_structure_state = 'PASSED'
        $State.terminal_receipt_state = 'PASSED'
        $State.produced_files = @(Get-ChildItem -LiteralPath $OutputRoot -File -Recurse | ForEach-Object { Get-FileRecord $_.FullName })
        $State.classification = 'PASSED_AUTOMATIC_AWAITING_EXTERNAL_VISUAL_REVIEW'
        $State.failure_stage = $null
        $State.failure_message = $null
        $ScriptExitCode = 0
    }
}
catch {
    $State.classification = 'FAILED_WITH_EVIDENCE'
    if (-not $State.failure_stage) { $State.failure_stage = 'SUPERVISOR' }
    $State.failure_message = $_.Exception.Message
    $ScriptExitCode = 91
}
finally {
    $State.terminal = $true
    $State.end_utc = [DateTime]::UtcNow.ToString('o')
    if (-not $OfflineContractTest) {
        $State.output_namespace_created = Test-Path -LiteralPath $OutputRoot
        $null = Write-TerminalEvidence $ExternalManifest $EmergencyReceipt $State
    }
}

exit $ScriptExitCode
