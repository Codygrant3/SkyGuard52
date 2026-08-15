param(
    [switch]$OfflineContractTest,
    [switch]$AuthorizeSingleBlender
)

$ErrorActionPreference = 'Stop'

$Gate = 'M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA'
$AttemptRoot = 'D:\Skyguard52\Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA\attempt_01'
$OutputRoot = 'D:\Skyguard52\Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentKit_Refinement01_StageA'
$ExternalManifest = 'D:\Skyguard52\Saved\Reports\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_TERMINAL_SUPERVISOR.json'
$EmergencyReceipt = 'D:\Skyguard52\Saved\Reports\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_EMERGENCY_RECEIPT.jsonl'
$ContractAuthority = 'D:\Skyguard52\Docs\Toolchain\ToolchainWave08\EnvironmentVisibleKitRefinement01StageA\execution_contract.json'
$ContractBytes = 6624
$ContractSha256 = '7a80c7ede6a6de0fa652214efe96cd4475fc38a82eb280360e66f3d39554d685'
$SourceAuthority = 'D:\Skyguard52\Scripts\ToolchainWave08\environment_visual_remediation01\build_m01_visible_environment_kit_refinement01_stagea.py'
$BlenderExecutable = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
$TimeoutSeconds = 2700

$State = [ordered]@{
    schema = 'skyguard.m01-visible-environment-kit-refinement01-stagea.supervisor-terminal.v1'
    gate = $Gate
    classification = 'FAILED_WITH_EVIDENCE'
    terminal = $false
    mode = if ($OfflineContractTest) { 'offline_contract_test' } elseif ($AuthorizeSingleBlender) { 'single_blender_execution' } else { 'authorization_refusal' }
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
    executable = $BlenderExecutable
    arguments = @()
    working_directory = $AttemptRoot
    output_counts = [ordered]@{ blend = 0; glb = 0; checkpoint_png = 0; final_png = 0; texture_png = 0 }
    receipt_states = [ordered]@{}
    produced_files = @()
    process_tree_samples = @()
}
$ScriptExitCode = 1
$WriteGovernedTerminal = (-not $OfflineContractTest -and $AuthorizeSingleBlender)

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
    if ($item.Length -ne $ExpectedBytes) { throw "Byte-count mismatch for $Path. Expected $ExpectedBytes; received $($item.Length)." }
    $actual = Get-Sha256Lower $Path
    if ($actual -ne $ExpectedHash.ToLowerInvariant()) { throw "SHA-256 mismatch for $Path" }
    return [ordered]@{ path = $item.FullName; bytes = $item.Length; sha256 = $actual }
}

function Get-FileRecord([string]$Path) {
    $item = Get-Item -LiteralPath $Path
    return [ordered]@{ path = $item.FullName; bytes = $item.Length; sha256 = Get-Sha256Lower $item.FullName }
}

function Write-JsonAtomic([string]$Path, $Value) {
    $parent = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $parent)) { New-Item -ItemType Directory -Path $parent | Out-Null }
    $temporary = "$Path.tmp.$([Guid]::NewGuid().ToString('N'))"
    $json = $Value | ConvertTo-Json -Depth 40
    [System.IO.File]::WriteAllText($temporary, $json + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
    [System.IO.File]::Move($temporary, $Path)
}

function Write-EmergencyLine([string]$Path, $Value) {
    $parent = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $parent)) { New-Item -ItemType Directory -Path $parent | Out-Null }
    $line = ($Value | ConvertTo-Json -Depth 12 -Compress) + [Environment]::NewLine
    [System.IO.File]::AppendAllText($Path, $line, [System.Text.UTF8Encoding]::new($false))
}

function Write-TerminalEvidence([string]$ManifestPath, [string]$EmergencyPath, $Value) {
    try {
        Write-JsonAtomic $ManifestPath $Value
        return 'manifest'
    }
    catch {
        $emergency = [ordered]@{
            schema = 'skyguard.m01-visible-environment-kit-refinement01-stagea.emergency.v1'
            gate = $Value.gate
            classification = $Value.classification
            terminal = $true
            timestamp_utc = [DateTime]::UtcNow.ToString('o')
            manifest_error = $_.Exception.Message
            failure_stage = $Value.failure_stage
            failure_message = $Value.failure_message
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
    foreach ($authority in @($Contract.authorities)) {
        $records += Verify-FileAuthority ([string]$authority.path) ([long]$authority.bytes) ([string]$authority.sha256)
    }
    $records += Verify-FileAuthority $BlenderExecutable ([long]$Contract.execution.blender_bytes) ([string]$Contract.execution.blender_sha256)
    return $records
}

function Get-GovernedHeavyProcesses {
    return @(Get-CimInstance Win32_Process -ErrorAction Stop | Where-Object {
        $_.Name -match '^(blender|UnrealEditor|UnrealEditor-Cmd|ShaderCompileWorker|AutomationTool|UnrealBuildTool|MSBuild|cl|link|dotnet)(\.exe)?$'
    } | Select-Object Name, ProcessId, ParentProcessId, CommandLine)
}

function Get-PngDimensions([string]$Path) {
    $stream = $null
    try {
        $stream = [System.IO.File]::Open($Path, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::Read)
        $header = New-Object byte[] 24
        $read = $stream.Read($header, 0, 24)
        if ($read -ne 24) { throw "PNG header is incomplete: $Path" }
        $signature = @(137,80,78,71,13,10,26,10)
        for ($index = 0; $index -lt 8; $index++) {
            if ($header[$index] -ne $signature[$index]) { throw "PNG signature is invalid: $Path" }
        }
        $width = [System.BitConverter]::ToInt32([byte[]]@($header[19],$header[18],$header[17],$header[16]), 0)
        $height = [System.BitConverter]::ToInt32([byte[]]@($header[23],$header[22],$header[21],$header[20]), 0)
        return [ordered]@{ width = $width; height = $height }
    }
    finally {
        if ($stream) { $stream.Dispose() }
    }
}

function Assert-PngSet($Files, [int]$ExpectedWidth, [int]$ExpectedHeight, [string]$Label) {
    foreach ($file in @($Files)) {
        $dimensions = Get-PngDimensions $file.FullName
        if ($dimensions.width -ne $ExpectedWidth -or $dimensions.height -ne $ExpectedHeight) {
            throw "$Label PNG dimensions are invalid for $($file.FullName): $($dimensions.width)x$($dimensions.height)"
        }
    }
}

function Invoke-OfflineContractTest {
    $testRoot = Join-Path ([System.IO.Path]::GetTempPath()) ('SG52_M01_STAGEA_' + [Guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $testRoot | Out-Null
    $result = [ordered]@{
        schema = 'skyguard.m01-visible-environment-kit-refinement01-stagea.offline-contract-test.v1'
        classification = 'FAIL'
        contract_verified = $false
        authority_count = 0
        all_authorities_verified = $false
        state_serialization_passed = $false
        terminal_serialization_passed = $false
        png_parser_passed = $false
        future_namespaces_absent = $false
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
        $result.all_authorities_verified = ($verified.Count -eq (@($contract.authorities).Count + 1))
        $serialized = $State | ConvertTo-Json -Depth 40
        $result.state_serialization_passed = -not [string]::IsNullOrWhiteSpace($serialized)
        $temporaryManifest = Join-Path $testRoot 'terminal.json'
        $temporaryEmergency = Join-Path $testRoot 'emergency.jsonl'
        $terminalMode = Write-TerminalEvidence $temporaryManifest $temporaryEmergency ([ordered]@{
            gate = $Gate
            classification = 'OFFLINE_CONTRACT_TEST'
            terminal = $true
            failure_stage = $null
            failure_message = $null
        })
        $result.terminal_serialization_passed = ($terminalMode -eq 'manifest' -and (Test-Path -LiteralPath $temporaryManifest))
        $pngFixture = Join-Path $testRoot 'fixture.png'
        [byte[]]$bytes = @(137,80,78,71,13,10,26,10,0,0,0,13,73,72,68,82,0,0,5,0,0,0,2,208)
        [System.IO.File]::WriteAllBytes($pngFixture, $bytes)
        $pngDimensions = Get-PngDimensions $pngFixture
        $result.png_parser_passed = ($pngDimensions.width -eq 1280 -and $pngDimensions.height -eq 720)
        $future = @($AttemptRoot, $OutputRoot, $ExternalManifest, $EmergencyReceipt)
        $result.future_namespaces_absent = (@($future | Where-Object { Test-Path -LiteralPath $_ }).Count -eq 0)
        if (-not $result.contract_verified -or -not $result.all_authorities_verified -or -not $result.state_serialization_passed -or -not $result.terminal_serialization_passed -or -not $result.png_parser_passed) {
            throw 'Offline contract assertion failed.'
        }
        if (-not $result.future_namespaces_absent) { throw 'A governed future namespace exists.' }
        $result.classification = 'PASS'
    }
    catch {
        $result.error = $_.Exception.Message
    }
    return $result
}

try {
    if ($OfflineContractTest -and $AuthorizeSingleBlender) {
        [Console]::Error.WriteLine('Offline and authorized modes are mutually exclusive.')
        $State.classification = 'CONFLICTING_SWITCHES_REFUSED'
        $State.terminal = $true
        $ScriptExitCode = 3
    }
    elseif ($OfflineContractTest) {
        $offlineResult = Invoke-OfflineContractTest
        $offlineResult | ConvertTo-Json -Depth 20
        if ($offlineResult.classification -ne 'PASS') { throw "Offline contract test failed: $($offlineResult.error)" }
        $State.classification = 'OFFLINE_CONTRACT_TEST_PASS'
        $State.terminal = $true
        $ScriptExitCode = 0
    }
    elseif (-not $AuthorizeSingleBlender) {
        [Console]::Error.WriteLine('Explicit -AuthorizeSingleBlender is required.')
        $State.classification = 'AUTHORIZATION_REFUSED'
        $State.terminal = $true
        $ScriptExitCode = 2
    }
    else {
        $State.failure_stage = 'AUTHORITY_PREFLIGHT'
        $contract = Get-Contract
        $authorityRecords = @(Verify-ContractAuthorities $contract)
        foreach ($namespace in @($AttemptRoot, $OutputRoot, $ExternalManifest, $EmergencyReceipt)) {
            if (Test-Path -LiteralPath $namespace) { throw "Governed future namespace already exists: $namespace" }
        }
        $heavy = @(Get-GovernedHeavyProcesses)
        if ($heavy.Count -gt 0) { throw "Heavy process detected: $(($heavy | ForEach-Object { $_.Name + ':' + $_.ProcessId }) -join ', ')" }
        if ([int]$contract.execution.blender_launch_count -ne 1 -or [int]$contract.execution.automatic_retry_count -ne 0 -or [int]$contract.execution.unreal_launch_count -ne 0) {
            throw 'Execution-count contract is invalid.'
        }

        $State.preflight_passed = $true
        $State.failure_stage = 'ATTEMPT_NAMESPACE_CREATION'
        $sourceDirectory = Join-Path $AttemptRoot 'source'
        New-Item -ItemType Directory -Path $sourceDirectory | Out-Null
        $State.governed_attempt_namespace_created = $true
        $sourceCopy = Join-Path $sourceDirectory 'build_m01_visible_environment_kit_refinement01_stagea.py'
        $contractCopy = Join-Path $AttemptRoot 'execution_contract.json'
        Copy-Item -LiteralPath $SourceAuthority -Destination $sourceCopy
        Copy-Item -LiteralPath $ContractAuthority -Destination $contractCopy
        $sourceAuthorityRecord = Get-FileRecord $SourceAuthority
        $sourceCopyRecord = Get-FileRecord $sourceCopy
        if ($sourceAuthorityRecord.sha256 -ne $sourceCopyRecord.sha256 -or $sourceAuthorityRecord.bytes -ne $sourceCopyRecord.bytes) {
            throw 'Attempt source copy does not match the frozen source authority.'
        }
        $null = Verify-FileAuthority $contractCopy $ContractBytes $ContractSha256

        Write-JsonAtomic (Join-Path $AttemptRoot 'preflight_receipt.json') ([ordered]@{
            schema = 'skyguard.m01-visible-environment-kit-refinement01-stagea.preflight.v1'
            gate = $Gate
            classification = 'PASSED_SINGLE_EXECUTION_PREFLIGHT'
            timestamp_utc = [DateTime]::UtcNow.ToString('o')
            contract = Get-FileRecord $contractCopy
            source = $sourceCopyRecord
            verified_authorities = $authorityRecords
            heavy_process_count = 0
            blender_launch_count = 0
            retry_count = 0
            unreal_launch_count = 0
        })

        $stdoutPath = Join-Path $AttemptRoot 'blender.stdout.log'
        $stderrPath = Join-Path $AttemptRoot 'blender.stderr.log'
        $arguments = @(
            '--background',
            '--factory-startup',
            '--python', $sourceCopy,
            '--',
            '--output', $OutputRoot,
            '--asset-id', ([string]$contract.asset_id),
            '--expected-source-sha256', ([string]$sourceCopyRecord.sha256)
        )
        $State.arguments = $arguments
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
        if ($stderrText -match '(?i)traceback \(most recent call last\)|BuildError:') { throw 'Blender stderr contains a Python traceback or governed build error.' }

        $blendFiles = @(Get-ChildItem -LiteralPath $OutputRoot -Filter '*.blend' -File -Recurse)
        $glbFiles = @(Get-ChildItem -LiteralPath (Join-Path $OutputRoot 'exports') -Filter '*.glb' -File)
        $checkpointFiles = @(Get-ChildItem -LiteralPath (Join-Path $OutputRoot 'renders\checkpoints') -Filter '*.png' -File)
        $finalFiles = @(Get-ChildItem -LiteralPath (Join-Path $OutputRoot 'renders\final') -Filter '*.png' -File)
        $textureFiles = @(Get-ChildItem -LiteralPath (Join-Path $OutputRoot 'textures') -Filter '*.png' -File)
        $State.output_counts = [ordered]@{
            blend = $blendFiles.Count
            glb = $glbFiles.Count
            checkpoint_png = $checkpointFiles.Count
            final_png = $finalFiles.Count
            texture_png = $textureFiles.Count
        }
        if ($blendFiles.Count -ne 1 -or $glbFiles.Count -ne 4 -or $checkpointFiles.Count -ne 3 -or $finalFiles.Count -ne 15 -or $textureFiles.Count -ne 5) {
            throw 'Output counts do not match the frozen StageA contract.'
        }
        Assert-PngSet $checkpointFiles 1280 720 'Checkpoint'
        Assert-PngSet $finalFiles 2560 1440 'Final render'
        Assert-PngSet $textureFiles 2048 2048 'Texture'

        foreach ($relativePath in @($contract.output_contract.required_glbs + $contract.output_contract.required_textures + $contract.output_contract.required_receipts)) {
            $requiredPath = Join-Path $OutputRoot ([string]$relativePath)
            if (-not (Test-Path -LiteralPath $requiredPath -PathType Leaf)) { throw "Required output is missing: $requiredPath" }
        }

        $dimensionReceipt = [System.IO.File]::ReadAllText((Join-Path $OutputRoot 'dimension_receipt.json')) | ConvertFrom-Json
        $topologyReceipt = [System.IO.File]::ReadAllText((Join-Path $OutputRoot 'topology_uv_receipt.json')) | ConvertFrom-Json
        $materialReceipt = [System.IO.File]::ReadAllText((Join-Path $OutputRoot 'material_texture_receipt.json')) | ConvertFrom-Json
        $checkpointReceipt = [System.IO.File]::ReadAllText((Join-Path $OutputRoot 'checkpoint_receipt.json')) | ConvertFrom-Json
        $renderReceipt = [System.IO.File]::ReadAllText((Join-Path $OutputRoot 'render_receipt.json')) | ConvertFrom-Json
        $exportReceipt = [System.IO.File]::ReadAllText((Join-Path $OutputRoot 'export_receipt.json')) | ConvertFrom-Json
        $sourceReceipt = [System.IO.File]::ReadAllText((Join-Path $OutputRoot 'source_parity_receipt.json')) | ConvertFrom-Json
        $terminalReceipt = [System.IO.File]::ReadAllText((Join-Path $OutputRoot 'terminal_receipt.json')) | ConvertFrom-Json
        $receiptChecks = [ordered]@{
            dimensions = [bool]$dimensionReceipt.passed
            topology_uv = [bool]$topologyReceipt.passed
            materials_textures = [bool]$materialReceipt.passed
            checkpoints = ([bool]$checkpointReceipt.passed -and [int]$checkpointReceipt.count -eq 3)
            final_renders = ([int]$renderReceipt.count -eq 15)
            exports = ([bool]$exportReceipt.passed -and @($exportReceipt.missing_sockets).Count -eq 0)
            source_parity = ([bool]$sourceReceipt.passed -and [string]$sourceReceipt.sha256 -eq [string]$sourceCopyRecord.sha256)
            terminal = ([bool]$terminalReceipt.automatic_validation_passed -and [string]$terminalReceipt.status -eq [string]$contract.output_contract.terminal_status)
        }
        foreach ($entry in $receiptChecks.GetEnumerator()) {
            if (-not [bool]$entry.Value) { throw "Output receipt failed: $($entry.Key)" }
        }
        $State.receipt_states = $receiptChecks
        $State.produced_files = @(Get-ChildItem -LiteralPath $OutputRoot -File -Recurse | ForEach-Object { Get-FileRecord $_.FullName })
        $State.classification = 'PASSED_AUTOMATIC_AWAITING_EXTERNAL_FULL_RESOLUTION_VISUAL_REVIEW'
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
    $State.output_namespace_created = Test-Path -LiteralPath $OutputRoot
    if ($WriteGovernedTerminal) {
        $null = Write-TerminalEvidence $ExternalManifest $EmergencyReceipt $State
    }
}

exit $ScriptExitCode
