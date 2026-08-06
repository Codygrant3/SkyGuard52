param(
    [switch]$OfflineContractTest,
    [switch]$AuthorizeSingleBlender
)

$ErrorActionPreference = 'Stop'

$Gate = 'GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY03_ATTEMPT01'
$ProjectRoot = 'D:\Skyguard52'
$AttemptRoot = 'D:\Skyguard52\Saved\BuildAttempts\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY03\attempt_01'
$OutputRoot = 'D:\Skyguard52\Blender\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY03_ATTEMPT01'
$ExternalManifest = 'D:\Skyguard52\Saved\Reports\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY03_TERMINAL_SUPERVISOR_MANIFEST.json'
$EmergencyReceipt = 'D:\Skyguard52\Saved\Reports\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY03_EMERGENCY_RECEIPT.jsonl'
$BlenderExecutable = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
$SourceAuthority = 'D:\Skyguard52\References\CombatAssets\CombatBlockout_Cycle02_Recovery03_OfflineDesign\source\blender_gate7_combat_blockout_cycle02_recovery03_attempt01.py'
$ContractAuthority = 'D:\Skyguard52\Saved\Reports\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY03_CORRECTION_CONTRACT.json'
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
    terminal_receipt_state = 'NOT_EVALUATED'
    produced_files = @()
    process_tree_samples = @()
}
$ScriptExitCode = 1
$WriteGovernedTerminal = -not $OfflineContractTest

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
    if ([string]::IsNullOrWhiteSpace($actual)) { throw "Null hash for $Path" }
    if ($actual -cne $actual.ToLowerInvariant()) { throw "Hash was not lowercase for $Path" }
    if ($actual -ne $ExpectedHash.ToLowerInvariant()) { throw "SHA-256 mismatch for $Path" }
    return [ordered]@{ path = $Path; bytes = $item.Length; sha256 = $actual }
}

function Write-JsonAtomic([string]$Path, $Value) {
    $parent = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $parent)) { New-Item -ItemType Directory -Path $parent | Out-Null }
    $temporary = "$Path.tmp.$([Guid]::NewGuid().ToString('N'))"
    $json = $Value | ConvertTo-Json -Depth 16
    [System.IO.File]::WriteAllText($temporary, $json + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
    [System.IO.File]::Move($temporary, $Path)
}

function Write-EmergencyLine([string]$Path, $Value) {
    $parent = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $parent)) { New-Item -ItemType Directory -Path $parent | Out-Null }
    $line = ($Value | ConvertTo-Json -Depth 8 -Compress) + [Environment]::NewLine
    [System.IO.File]::AppendAllText($Path, $line, [System.Text.UTF8Encoding]::new($false))
}

function Write-TerminalEvidence([string]$ManifestPath, [string]$EmergencyPath, $Value, [switch]$ForceManifestFailure) {
    try {
        if ($ForceManifestFailure) { throw 'Deliberate offline manifest-write failure.' }
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

function Get-FileRecord([string]$Path) {
    $item = Get-Item -LiteralPath $Path
    return [ordered]@{ path = $item.FullName; bytes = $item.Length; sha256 = Get-Sha256Lower $item.FullName }
}

function Assert-NullRejected($Value) {
    if ($null -eq $Value) { throw 'Null value rejected as required.' }
}

function Get-Authorities {
    return @(
        [ordered]@{ path = 'D:\Skyguard52\Docs\AAA_Review\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY02_ATTEMPT01_TERMINAL_FREEZE.json'; bytes = 7991; sha256 = '9a255b9ab21c2794951b89631aa9d52588249f91c83999d02d4d372a21d5a873' },
        [ordered]@{ path = 'D:\Skyguard52\Saved\Reports\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY02_ATTEMPT01_POSTFLIGHT.json'; bytes = 10708; sha256 = '1950863e4361d67b935aa8e78aa490918072bfca3bb362290d91994ef5bab666' },
        [ordered]@{ path = 'D:\Skyguard52\Saved\Reports\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY02_TERMINAL_SUPERVISOR_MANIFEST.json'; bytes = 7362; sha256 = 'cb31309f5c7d530719964ac9e19e69f957cd22ddab12f2fc8efbf82cce856894' },
        [ordered]@{ path = 'D:\Skyguard52\Docs\AAA_Review\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY02_OFFLINE_DESIGN_FREEZE.json'; bytes = 4229; sha256 = '211d30e6167dc735cdf5489a413e0cd27d7311b64a2b2f2f2e7f8ce5d6b2da5b' },
        [ordered]@{ path = 'D:\Skyguard52\Scripts\invoke_gate7_combat_blockout_cycle02_recovery02_once.ps1'; bytes = 18751; sha256 = '32fca763ef2d833dcca15e6dc136afbf9fa1d928c38dce70e1b31042b49d6db1' },
        [ordered]@{ path = 'D:\Skyguard52\References\CombatAssets\CombatBlockout_Cycle02_Recovery02_OfflineDesign\source\blender_gate7_combat_blockout_cycle02_recovery02_attempt01.py'; bytes = 19609; sha256 = '7123bd7c45ceb6a7fc299b2ac34ab7eb2749bd89cb1ee1cc66b81cb2a31c2b45' },
        [ordered]@{ path = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'; bytes = 112975320; sha256 = 'e27fbfea8564aa645d4463cb0949695fd85562b9de6df9561b06859a1074adf7' },
        [ordered]@{ path = 'D:\Skyguard52\References\CombatAssets\CombatBlockout_Cycle02_Recovery03_OfflineDesign\source\blender_gate7_combat_blockout_cycle02_recovery03_attempt01.py'; bytes = 19609; sha256 = 'f486afea2547d246d653a5507a9957ea39b1f4dcdcc9a6ac66447ebd7fd84c9a' },
        [ordered]@{ path = 'D:\Skyguard52\Saved\Reports\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY03_CORRECTION_CONTRACT.json'; bytes = 5294; sha256 = '1222a53f3e7adfb69c801610599ea7a18e242d27056f3b5b9674e580132dfa8d' }
    )
}
function Invoke-OfflineTest {
    $testRoot = Join-Path ([System.IO.Path]::GetTempPath()) ('SG52_G7_R03_' + [Guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $testRoot | Out-Null
    $results = [ordered]@{
        authorities_verified = 0
        matching_hash_passed = $false
        missing_file_rejected = $false
        wrong_bytes_rejected = $false
        wrong_hash_rejected = $false
        lowercase_digest_passed = $false
        null_rejected = $false
        state_serialization_passed = $false
        deliberate_failure_manifest_passed = $false
        emergency_receipt_passed = $false
        blender_launch_count = 0
        governed_attempt_absent = $false
        governed_output_absent = $false
    }
    try {
        foreach ($authority in Get-Authorities) {
            $null = Verify-FileAuthority $authority.path $authority.bytes $authority.sha256
            $results.authorities_verified++
        }
        $sample = (Get-Authorities)[0]
        $digest = Get-Sha256Lower $sample.path
        $results.matching_hash_passed = ($digest -eq $sample.sha256)
        $results.lowercase_digest_passed = ($digest -ceq $digest.ToLowerInvariant())
        try { $null = Verify-FileAuthority (Join-Path $testRoot 'missing.bin') 1 ('0' * 64) } catch { $results.missing_file_rejected = $true }
        try { $null = Verify-FileAuthority $sample.path ($sample.bytes + 1) $sample.sha256 } catch { $results.wrong_bytes_rejected = $true }
        try { $null = Verify-FileAuthority $sample.path $sample.bytes ('0' * 64) } catch { $results.wrong_hash_rejected = $true }
        try { Assert-NullRejected $null } catch { $results.null_rejected = $true }
        $serialized = $State | ConvertTo-Json -Depth 16
        $results.state_serialization_passed = -not [string]::IsNullOrWhiteSpace($serialized)

        $temporaryManifest = Join-Path $testRoot 'terminal.json'
        $temporaryEmergency = Join-Path $testRoot 'emergency.jsonl'
        $failureState = [ordered]@{
            gate = $Gate
            classification = 'FAILED_WITH_EVIDENCE'
            terminal = $true
            failure_stage = 'DELIBERATE_OFFLINE_PREFLIGHT_FAILURE'
        }
        $mode = Write-TerminalEvidence $temporaryManifest $temporaryEmergency $failureState
        $results.deliberate_failure_manifest_passed = ($mode -eq 'manifest' -and (Test-Path -LiteralPath $temporaryManifest))
        $mode = Write-TerminalEvidence (Join-Path $testRoot 'never_written.json') $temporaryEmergency $failureState -ForceManifestFailure
        $results.emergency_receipt_passed = ($mode -eq 'emergency' -and (Test-Path -LiteralPath $temporaryEmergency))
        $results.governed_attempt_absent = -not (Test-Path -LiteralPath $AttemptRoot)
        $results.governed_output_absent = -not (Test-Path -LiteralPath $OutputRoot)

        $failed = @($results.GetEnumerator() | Where-Object {
            $_.Key -notin @('authorities_verified', 'blender_launch_count') -and $_.Value -ne $true
        })
        if ($results.authorities_verified -ne (Get-Authorities).Count) { throw 'Not all authorities were verified.' }
        if ($results.blender_launch_count -ne 0) { throw 'Offline test reached Blender launch path.' }
        if ($failed.Count -gt 0) { throw "Offline contract assertions failed: $($failed.Key -join ', ')" }
        return [ordered]@{
            classification = 'PASS'
            exit_code_contract = 'System.Int32:0'
            temporary_test_root = $testRoot
            results = $results
        }
    }
    catch {
        return [ordered]@{
            classification = 'FAIL'
            error = $_.Exception.Message
            temporary_test_root = $testRoot
            results = $results
        }
    }
}

try {
    if ($OfflineContractTest) {
        $offlineResult = Invoke-OfflineTest
        $offlineResult | ConvertTo-Json -Depth 12
        if ($offlineResult.classification -ne 'PASS') { throw "Offline contract test failed: $($offlineResult.error)" }
        $State.classification = 'OFFLINE_CONTRACT_TEST_PASS'
        $State.terminal = $true
        $ScriptExitCode = 0
    }
    else {
        if (-not $AuthorizeSingleBlender) { throw 'Explicit -AuthorizeSingleBlender is required.' }
        $State.failure_stage = 'AUTHORITY_PREFLIGHT'
        foreach ($authority in Get-Authorities) { $null = Verify-FileAuthority $authority.path $authority.bytes $authority.sha256 }
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
        $sourceCopy = Join-Path $sourceDirectory 'blender_gate7_combat_blockout_cycle02_recovery03_attempt01.py'
        $contractCopy = Join-Path $AttemptRoot 'GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY03_CORRECTION_CONTRACT.json'
        Copy-Item -LiteralPath $SourceAuthority -Destination $sourceCopy
        Copy-Item -LiteralPath $ContractAuthority -Destination $contractCopy
        $null = Verify-FileAuthority $sourceCopy 19609 'f486afea2547d246d653a5507a9957ea39b1f4dcdcc9a6ac66447ebd7fd84c9a'
        $null = Verify-FileAuthority $contractCopy 5294 '1222a53f3e7adfb69c801610599ea7a18e242d27056f3b5b9674e580132dfa8d'

        $preflightReceipt = [ordered]@{
            gate = $Gate
            classification = 'PASSED_SINGLE_EXECUTION_PREFLIGHT'
            timestamp_utc = [DateTime]::UtcNow.ToString('o')
            source = Get-FileRecord $sourceCopy
            contract = Get-FileRecord $contractCopy
            blender_launch_count = 0
            retry_count = 0
        }
        Write-JsonAtomic (Join-Path $AttemptRoot 'preflight_receipt.json') $preflightReceipt

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
        if ($null -eq $capturedExitCode) { throw 'Blender exit code is null after handle retention, WaitForExit, and Refresh.' }
        if ($capturedExitCode -isnot [System.Int32]) { throw "Blender exit-code type is invalid: $($capturedExitCode.GetType().FullName)" }
        $State.exit_code = [System.Int32]$capturedExitCode
        $State.exit_code_type = $capturedExitCode.GetType().FullName
        if ($State.exit_code -ne 0) {
            throw "Blender returned nonzero exit code: $($State.exit_code)"
        }

        $State.failure_stage = 'OUTPUT_VALIDATION'
        $State.output_namespace_created = Test-Path -LiteralPath $OutputRoot
        if (-not $State.output_namespace_created) { throw 'Blender did not create the governed output namespace.' }
        $stderrText = if (Test-Path -LiteralPath $stderrPath) { [System.IO.File]::ReadAllText($stderrPath) } else { '' }
        if ($stderrText -match '(?i)traceback|error:') { throw 'Blender stderr contains a traceback or error.' }
        $blendFiles = @(Get-ChildItem -LiteralPath $OutputRoot -Filter '*.blend' -File)
        $glbFiles = @(Get-ChildItem -LiteralPath (Join-Path $OutputRoot 'exports') -Filter '*.glb' -File)
        $pngFiles = @(Get-ChildItem -LiteralPath (Join-Path $OutputRoot 'renders') -Filter '*.png' -File)
        $State.output_counts = [ordered]@{ blend = $blendFiles.Count; glb = $glbFiles.Count; png = $pngFiles.Count }
        if ($blendFiles.Count -ne 1 -or $glbFiles.Count -ne 5 -or $pngFiles.Count -ne 5) {
            throw 'Blender output counts do not match the frozen contract.'
        }
        $dimensionReceiptPath = Join-Path $OutputRoot 'dimension_and_artifact_receipt.json'
        $terminalReceiptPath = Join-Path $OutputRoot 'terminal_receipt.json'
        if (-not (Test-Path -LiteralPath $dimensionReceiptPath) -or -not (Test-Path -LiteralPath $terminalReceiptPath)) {
            throw 'Required Blender receipt is missing.'
        }
        $dimensionReceipt = [System.IO.File]::ReadAllText($dimensionReceiptPath) | ConvertFrom-Json
        $terminalReceipt = [System.IO.File]::ReadAllText($terminalReceiptPath) | ConvertFrom-Json
        if ($terminalReceipt.gate -ne $Gate -or $terminalReceipt.status -ne 'BLENDER_COMPLETED_AWAITING_EXTERNAL_VALIDATION') {
            throw 'Terminal receipt identity or status is invalid.'
        }
        if ($terminalReceipt.render_count -ne 5 -or $terminalReceipt.export_count -ne 5) {
            throw 'Terminal receipt output counts are invalid.'
        }
        $State.terminal_receipt_state = 'VALID'
        $State.produced_files = @(Get-ChildItem -LiteralPath $OutputRoot -Recurse -File | ForEach-Object { Get-FileRecord $_.FullName })
        $State.classification = 'PASSED_AUTOMATIC_AWAITING_VISUAL_REVIEW'
        $State.failure_stage = $null
        $ScriptExitCode = 0
    }
}
catch {
    $State.classification = 'FAILED_WITH_EVIDENCE'
    if ([string]::IsNullOrWhiteSpace($State.failure_stage)) { $State.failure_stage = 'UNCLASSIFIED_SUPERVISOR_FAILURE' }
    $State.failure_message = $_.Exception.Message
    if ($OfflineContractTest) {
        [ordered]@{ classification = 'FAIL'; error = $_.Exception.Message } | ConvertTo-Json -Depth 6
    }
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
