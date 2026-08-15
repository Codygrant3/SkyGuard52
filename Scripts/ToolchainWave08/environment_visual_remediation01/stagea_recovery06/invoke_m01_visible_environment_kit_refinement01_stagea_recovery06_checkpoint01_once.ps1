[CmdletBinding()]
param(
    [switch]$AuthorizeSingleBlender,
    [switch]$OfflineContractTest,
    [string]$OfflineEvidenceRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Root = 'D:\Skyguard52'
$Gate = 'M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY06_CHECKPOINT01'
$Contract = Join-Path $Root 'Docs\Toolchain\ToolchainWave08\EnvironmentVisibleKitRefinement01StageARecovery06\execution_contract.json'
$RecoverySource = Join-Path $Root 'Scripts\ToolchainWave08\environment_visual_remediation01\stagea_recovery06\build_m01_visible_environment_kit_refinement01_stagea_recovery06_checkpoint01.py'
$BaseSource = Join-Path $Root 'Scripts\ToolchainWave08\environment_visual_remediation01\build_m01_visible_environment_kit_refinement01_stagea.py'
$Recovery05TerminalFreeze = Join-Path $Root 'Docs\AAA_Review\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY05_CHECKPOINT01_ATTEMPT01_TERMINAL_FREEZE.json'
$Recovery05FailureAnalysis = Join-Path $Root 'Saved\Reports\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY05_CHECKPOINT01_ATTEMPT01_FAILURE_ANALYSIS.json'
$Recovery05ArtifactInventory = Join-Path $Root 'Saved\Reports\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY05_CHECKPOINT01_ATTEMPT01_ARTIFACT_INVENTORY.json'
$Blender = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
$AttemptRoot = Join-Path $Root 'Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY06_CHECKPOINT01\attempt_01'
$OutputRoot = Join-Path $Root 'Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentKit_Refinement01_StageA_Recovery06_Checkpoint01'
$TerminalManifest = Join-Path $Root 'Saved\Reports\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY06_CHECKPOINT01_TERMINAL_SUPERVISOR.json'
$EmergencyReceipt = Join-Path $Root 'Saved\Reports\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY06_CHECKPOINT01_EMERGENCY_RECEIPT.jsonl'
$TimeoutSeconds = 3600

function Get-Sha256Lower([string]$Path) {
    if (-not [IO.File]::Exists($Path)) { throw "Missing file: $Path" }
    $stream = $null
    $hasher = $null
    try {
        $stream = [IO.File]::Open($Path, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::Read)
        $hasher = [Security.Cryptography.SHA256]::Create()
        return ([BitConverter]::ToString($hasher.ComputeHash($stream))).Replace('-', '').ToLowerInvariant()
    }
    finally {
        if ($null -ne $hasher) { $hasher.Dispose() }
        if ($null -ne $stream) { $stream.Dispose() }
    }
}

function Assert-File([string]$Path, [long]$Bytes, [string]$Sha256) {
    $item = Get-Item -LiteralPath $Path -ErrorAction Stop
    if ($item.Length -ne $Bytes) { throw "Byte mismatch: $Path" }
    if ((Get-Sha256Lower $Path) -ne $Sha256.ToLowerInvariant()) { throw "Hash mismatch: $Path" }
}

function Write-JsonAtomic([string]$Path, $Value) {
    $parent = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $parent)) { [IO.Directory]::CreateDirectory($parent) | Out-Null }
    $temporary = "$Path.tmp"
    [IO.File]::WriteAllText($temporary, ($Value | ConvertTo-Json -Depth 50), [Text.UTF8Encoding]::new($false))
    if (Test-Path -LiteralPath $Path) {
        $backup = "$Path.atomic.backup"
        [IO.File]::Replace($temporary, $Path, $backup)
        if (Test-Path -LiteralPath $backup) { Remove-Item -LiteralPath $backup -Force }
    }
    else { [IO.File]::Move($temporary, $Path) }
}

function Write-TerminalEvidence([string]$ManifestPath, [string]$EmergencyPath, $State) {
    try {
        Write-JsonAtomic $ManifestPath $State
        return 'manifest'
    }
    catch {
        try {
            $parent = Split-Path -Parent $EmergencyPath
            if (-not (Test-Path -LiteralPath $parent)) { [IO.Directory]::CreateDirectory($parent) | Out-Null }
            $line = [ordered]@{
                schema = 'skyguard.m01-visible-environment-kit-refinement01-stagea-recovery06-checkpoint01.emergency.v1'
                classification = 'FAILED_WITH_EVIDENCE'
                at_utc = [DateTime]::UtcNow.ToString('o')
                terminal_write_error = $_.Exception.Message
                state = $State
            } | ConvertTo-Json -Depth 50 -Compress
            [IO.File]::AppendAllText($EmergencyPath, $line + [Environment]::NewLine, [Text.UTF8Encoding]::new($false))
            return 'emergency'
        }
        catch { return 'lost' }
    }
}

function Get-PngDimensions([string]$Path) {
    $bytes = [IO.File]::ReadAllBytes($Path)
    if ($bytes.Length -lt 24) { throw "Truncated PNG header: $Path" }
    $signature = [byte[]](137, 80, 78, 71, 13, 10, 26, 10)
    for ($index = 0; $index -lt $signature.Length; $index++) {
        if ($bytes[$index] -ne $signature[$index]) { throw "Invalid PNG signature: $Path" }
    }
    if ($bytes[12] -ne 73 -or $bytes[13] -ne 72 -or $bytes[14] -ne 68 -or $bytes[15] -ne 82) {
        throw "Missing PNG IHDR chunk: $Path"
    }
    $width = ([int]$bytes[16] * 16777216) + ([int]$bytes[17] * 65536) + ([int]$bytes[18] * 256) + [int]$bytes[19]
    $height = ([int]$bytes[20] * 16777216) + ([int]$bytes[21] * 65536) + ([int]$bytes[22] * 256) + [int]$bytes[23]
    if ($width -le 0 -or $height -le 0) { throw "Invalid PNG dimensions: $Path" }
    return [ordered]@{ width = [int]$width; height = [int]$height }
}

function Assert-PngSet($Files, [int]$Width, [int]$Height, [string]$Label) {
    foreach ($file in @($Files)) {
        $dimensions = Get-PngDimensions $file.FullName
        if ($dimensions.width -ne $Width -or $dimensions.height -ne $Height) {
            throw "$Label PNG dimensions invalid: $($file.FullName)"
        }
    }
}

function New-PngHeaderFixture([string]$Path, [int]$Width, [int]$Height) {
    $bytes = [byte[]]::new(24)
    [byte[]]$signature = @(137, 80, 78, 71, 13, 10, 26, 10)
    [Array]::Copy($signature, 0, $bytes, 0, 8)
    $bytes[8] = 0; $bytes[9] = 0; $bytes[10] = 0; $bytes[11] = 13
    $bytes[12] = 73; $bytes[13] = 72; $bytes[14] = 68; $bytes[15] = 82
    $bytes[16] = [byte](($Width -shr 24) -band 255)
    $bytes[17] = [byte](($Width -shr 16) -band 255)
    $bytes[18] = [byte](($Width -shr 8) -band 255)
    $bytes[19] = [byte]($Width -band 255)
    $bytes[20] = [byte](($Height -shr 24) -band 255)
    $bytes[21] = [byte](($Height -shr 16) -band 255)
    $bytes[22] = [byte](($Height -shr 8) -band 255)
    $bytes[23] = [byte]($Height -band 255)
    [IO.File]::WriteAllBytes($Path, $bytes)
}

function Assert-Throws([scriptblock]$Action, [string]$Label) {
    $threw = $false
    try { & $Action } catch { $threw = $true }
    if (-not $threw) { throw "Expected rejection did not occur: $Label" }
}

function Get-GovernedHeavyProcesses {
    return @(Get-Process -ErrorAction SilentlyContinue | Where-Object {
        $_.ProcessName -match '^(UnrealEditor|UnrealEditor-Cmd|Blender|ShaderCompileWorker|AutomationTool|UnrealBuildTool|dotnet|MSBuild|cl|link)$'
    })
}

function Assert-Recovery05TerminalFreeze {
    Assert-File $Recovery05TerminalFreeze 3112 'c52c74c2a33b111cd37c53442dda67d9ee93d41d353d653e8111092e9ff69e9a'
    $freeze = Get-Content -LiteralPath $Recovery05TerminalFreeze -Raw | ConvertFrom-Json
    if ($freeze.classification -ne 'FAILED_WITH_EVIDENCE' -or [int]$freeze.member_count -ne 6) {
        throw 'Recovery05 terminal freeze classification or cardinality drift'
    }
    foreach ($member in @($freeze.members)) {
        Assert-File ([string]$member.path) ([long]$member.bytes) ([string]$member.sha256)
    }
    Assert-File $Recovery05FailureAnalysis 2992 'ff9928f08162ef948253cab8b01bf323476f2a6dbb15894fd8c14af119f31168'
    Assert-File $Recovery05ArtifactInventory 2406 '9034528e28b79f40195e5fa3d47d016f3060331bf48cbd8ea7e5ec4d45756a75'
}

function Assert-Authorities {
    Assert-File $Contract 3643 'a35a245beade9a72e5ac3e4d8d119da23426a2908d6e29414dd3f002e409c98e'
    Assert-File $RecoverySource 7427 'a47375d2afe02c2d829311249cf32b50e6fe034cc8b60c32e1eb9dab9bd52399'
    Assert-File $BaseSource 42238 '773e67931108a2f199f763a4d3ce94348ba9ed9a403c049b3b8b4409bb06fd12'
    Assert-File $Blender 112975320 'e27fbfea8564aa645d4463cb0949695fd85562b9de6df9561b06859a1074adf7'
    Assert-Recovery05TerminalFreeze
    $contractData = Get-Content -LiteralPath $Contract -Raw | ConvertFrom-Json
    if ($contractData.gate -ne $Gate) { throw 'Recovery06 Checkpoint01 gate drift' }
    if ([int]$contractData.execution.timeout_seconds -ne 3600) { throw 'Timeout contract drift' }
    if ([int]$contractData.output_contract.expected_total_file_count -ne 16) { throw 'Output file-count contract drift' }
    if ([int]$contractData.output_contract.checkpoint_png_count -ne 9) { throw 'Checkpoint-count contract drift' }
    if ([int]$contractData.output_contract.glb_count -ne 0 -or [int]$contractData.output_contract.final_png_count -ne 0 -or [int]$contractData.output_contract.texture_png_count -ne 0) { throw 'Checkpoint-only output contract drift' }
    if ([int]$contractData.execution.blender_launch_count -ne 1 -or [int]$contractData.execution.automatic_retry_count -ne 0) { throw 'Launch or retry contract drift' }
}

function Assert-FutureNamespacesAbsent {
    foreach ($path in @($AttemptRoot, $OutputRoot, $TerminalManifest, $EmergencyReceipt)) {
        if (Test-Path -LiteralPath $path) { throw "Future namespace exists: $path" }
    }
}

function Get-ProducedInventory([string]$RootPath) {
    return @(
        Get-ChildItem -LiteralPath $RootPath -Recurse -File | Sort-Object FullName | ForEach-Object {
            [ordered]@{
                relative_path = $_.FullName.Substring($RootPath.Length).TrimStart('\')
                bytes = $_.Length
                sha256 = Get-Sha256Lower $_.FullName
            }
        }
    )
}

$state = [ordered]@{
    schema = 'skyguard.m01-visible-environment-kit-refinement01-stagea-recovery06-checkpoint01.supervisor-terminal.v1'
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
    output_counts = [ordered]@{ blend = 0; glb = 0; checkpoint_png = 0; final_png = 0; texture_png = 0; receipt = 0 }
    receipt_states = [ordered]@{}
    produced_files = @()
    process_tree_samples = @()
}

$hasOfflineEvidenceRoot = ($OfflineContractTest -and -not [string]::IsNullOrWhiteSpace($OfflineEvidenceRoot))
$manifestPath = if ($hasOfflineEvidenceRoot) {
    Join-Path $OfflineEvidenceRoot 'terminal_manifest.json'
} else { $TerminalManifest }
$emergencyPath = if ($hasOfflineEvidenceRoot) {
    Join-Path $OfflineEvidenceRoot 'emergency_receipt.jsonl'
} else { $EmergencyReceipt }
$writeTerminal = ($hasOfflineEvidenceRoot -or $AuthorizeSingleBlender)
$stage = 'INITIALIZATION'
$exit = 1

try {
    $stage = 'AUTHORITY_PREFLIGHT'
    if ($AuthorizeSingleBlender -and $OfflineContractTest) { throw 'Authorized and offline modes are mutually exclusive' }
    if ($OfflineContractTest -and [string]::IsNullOrWhiteSpace($OfflineEvidenceRoot)) { throw '-OfflineEvidenceRoot is required' }
    Assert-Authorities
    if (@(Get-GovernedHeavyProcesses).Count -ne 0) { throw 'A governed heavy process is already active' }
    Assert-FutureNamespacesAbsent

    if ($OfflineContractTest) {
        [IO.Directory]::CreateDirectory($OfflineEvidenceRoot) | Out-Null
        $fixtureRoot = Join-Path $OfflineEvidenceRoot 'png_fixtures'
        [IO.Directory]::CreateDirectory($fixtureRoot) | Out-Null
        foreach ($size in @(@(1280,720), @(1920,1080), @(2560,1440), @(2048,2048))) {
            $fixture = Join-Path $fixtureRoot ("png_{0}x{1}.bin" -f $size[0], $size[1])
            New-PngHeaderFixture $fixture ([int]$size[0]) ([int]$size[1])
            $dimensions = Get-PngDimensions $fixture
            if ($dimensions.width -ne $size[0] -or $dimensions.height -ne $size[1]) { throw "PNG fixture decode failed: $fixture" }
        }
        $malformed = Join-Path $fixtureRoot 'malformed.bin'
        [IO.File]::WriteAllBytes($malformed, [byte[]](0..23))
        Assert-Throws { Get-PngDimensions $malformed | Out-Null } 'malformed signature'
        $truncated = Join-Path $fixtureRoot 'truncated.bin'
        [IO.File]::WriteAllBytes($truncated, [byte[]](137,80,78,71,13,10,26,10))
        Assert-Throws { Get-PngDimensions $truncated | Out-Null } 'truncated header'
        $wrong = Join-Path $fixtureRoot 'wrong_dimensions.bin'
        New-PngHeaderFixture $wrong 111 222
        $wrongItem = Get-Item -LiteralPath $wrong
        Assert-Throws { Assert-PngSet @($wrongItem) 1920 1080 'Wrong-dimension fixture' } 'wrong dimensions'
        $wrapperText = [IO.File]::ReadAllText($RecoverySource)
        if ($wrapperText -notmatch 'require\(len\(results\) == 9, "Checkpoint render count is not exactly nine"\)') { throw 'Nine-render checkpoint guard missing' }
        if ($wrapperText -notmatch 'finalization_authorized":False') { throw 'Finalization prohibition missing' }
        if ($wrapperText -notmatch 'recovery05_attempt_or_output_reused": False') { throw 'Recovery05 attempt/output nonreuse receipt missing' }
        $state.preflight_passed = $true
        $state.classification = 'PASS'
        $state.receipt_states = [ordered]@{ png_fixtures = $true; checkpoint_only = $true; recovery05_preserved = $true; generated_call_graph = $true }
        $exit = 0
    }
    else {
        if (-not $AuthorizeSingleBlender) { throw 'Normal mode requires -AuthorizeSingleBlender' }
        $state.preflight_passed = $true
        [IO.Directory]::CreateDirectory((Join-Path $AttemptRoot 'source')) | Out-Null
        $state.governed_attempt_namespace_created = $true
        $attemptSource = Join-Path $AttemptRoot 'source\build_m01_visible_environment_kit_refinement01_stagea_recovery06_checkpoint01.py'
        [IO.File]::Copy($RecoverySource, $attemptSource, $false)
        [IO.File]::Copy($Contract, (Join-Path $AttemptRoot 'execution_contract.json'), $false)
        Assert-File $attemptSource 7427 'a47375d2afe02c2d829311249cf32b50e6fe034cc8b60c32e1eb9dab9bd52399'
        Write-JsonAtomic (Join-Path $AttemptRoot 'preflight_receipt.json') ([ordered]@{
            schema = 'skyguard.m01-visible-environment-kit-refinement01-stagea-recovery06-checkpoint01.preflight.v1'
            at_utc = [DateTime]::UtcNow.ToString('o')
            recovery05_terminal_freeze_sha256 = 'c52c74c2a33b111cd37c53442dda67d9ee93d41d353d653e8111092e9ff69e9a'
            recovery05_terminal_members_verified = 6
            base_source_sha256 = '773e67931108a2f199f763a4d3ce94348ba9ed9a403c049b3b8b4409bb06fd12'
            recovery_source_sha256 = 'a47375d2afe02c2d829311249cf32b50e6fe034cc8b60c32e1eb9dab9bd52399'
            heavy_process_count = 0
            retry_count = 0
            passed = $true
        })

        $stdout = Join-Path $AttemptRoot 'blender.stdout.log'
        $stderr = Join-Path $AttemptRoot 'blender.stderr.log'
        $arguments = @(
            '--background', '--factory-startup', '--python', $attemptSource, '--',
            '--output', $OutputRoot,
            '--asset-id', 'm01-visible-environment-kit-refinement01-stagea',
            '--expected-source-sha256', 'a47375d2afe02c2d829311249cf32b50e6fe034cc8b60c32e1eb9dab9bd52399'
        )
        $stage = 'BLENDER_EXECUTION'
        $state.blender_launch_count = 1
        $process = Start-Process -FilePath $Blender -ArgumentList $arguments -WorkingDirectory $AttemptRoot -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru
        $state.blender_pid = $process.Id
        $null = $process.Handle
        $state.native_handle_retained = $true
        $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
        while (-not $process.HasExited) {
            if ([DateTime]::UtcNow -ge $deadline) {
                $state.timeout = $true
                try { $process.Kill() } catch {}
                throw "Blender exceeded the frozen $TimeoutSeconds-second timeout"
            }
            $sample = @(Get-CimInstance Win32_Process -Filter "ProcessId=$($process.Id) OR ParentProcessId=$($process.Id)" -ErrorAction SilentlyContinue | Select-Object Name, ProcessId, ParentProcessId, CommandLine)
            $state.process_tree_samples += @([ordered]@{ timestamp_utc = [DateTime]::UtcNow.ToString('o'); processes = $sample })
            Start-Sleep -Seconds 3
            $process.Refresh()
        }
        $process.WaitForExit()
        $process.Refresh()
        $code = $process.ExitCode
        $state.exit_code = [int]$code
        $state.exit_code_type = $code.GetType().FullName
        if ($code -ne 0) { throw "Blender returned exit code $code" }
        if (-not (Test-Path -LiteralPath $OutputRoot)) { throw 'Blender did not create the Recovery06 Checkpoint01 output namespace' }
        $state.output_namespace_created = $true

        $stage = 'OUTPUT_VALIDATION'
        $stderrText = if (Test-Path -LiteralPath $stderr) { [IO.File]::ReadAllText($stderr) } else { '' }
        if ($stderrText -match 'Traceback \(most recent call last\)|FAILED_WITH_EVIDENCE|ArrayMemoryError|zero-size array') { throw 'Blender stderr contains a Python traceback or governed build error' }
        $blendFiles = @(Get-ChildItem -LiteralPath $OutputRoot -Recurse -Filter '*.blend' -File)
        $glbFiles = @(Get-ChildItem -LiteralPath $OutputRoot -Recurse -Filter '*.glb' -File)
        $checkpointFiles = @(Get-ChildItem -LiteralPath (Join-Path $OutputRoot 'renders\checkpoints') -Filter '*.png' -File)
        $finalFiles = @(Get-ChildItem -LiteralPath $OutputRoot -Recurse -Filter '*.png' -File | Where-Object { $_.FullName -match '\\renders\\final\\' })
        $textureFiles = @(Get-ChildItem -LiteralPath $OutputRoot -Recurse -Filter '*.png' -File | Where-Object { $_.FullName -match '\\textures\\' })
        $requiredReceipts = @('dimension_receipt.json','topology_uv_receipt.json','checkpoint_receipt.json','source_parity_receipt.json','artifact_inventory.json','terminal_receipt.json')
        $receiptFiles = @($requiredReceipts | ForEach-Object { Get-Item -LiteralPath (Join-Path $OutputRoot $_) -ErrorAction Stop })
        $state.output_counts = [ordered]@{ blend = $blendFiles.Count; glb = $glbFiles.Count; checkpoint_png = $checkpointFiles.Count; final_png = $finalFiles.Count; texture_png = $textureFiles.Count; receipt = $receiptFiles.Count }
        if ($blendFiles.Count -ne 1 -or $glbFiles.Count -ne 0 -or $checkpointFiles.Count -ne 9 -or $finalFiles.Count -ne 0 -or $textureFiles.Count -ne 0 -or $receiptFiles.Count -ne 6) { throw "Checkpoint-only output cardinality failed: $($state.output_counts | ConvertTo-Json -Compress)" }
        Assert-PngSet $checkpointFiles 1920 1080 'Checkpoint'
        $dimension = Get-Content -LiteralPath (Join-Path $OutputRoot 'dimension_receipt.json') -Raw | ConvertFrom-Json
        $topology = Get-Content -LiteralPath (Join-Path $OutputRoot 'topology_uv_receipt.json') -Raw | ConvertFrom-Json
        $checkpoints = Get-Content -LiteralPath (Join-Path $OutputRoot 'checkpoint_receipt.json') -Raw | ConvertFrom-Json
        $sourceParity = Get-Content -LiteralPath (Join-Path $OutputRoot 'source_parity_receipt.json') -Raw | ConvertFrom-Json
        $terminal = Get-Content -LiteralPath (Join-Path $OutputRoot 'terminal_receipt.json') -Raw | ConvertFrom-Json
        $state.receipt_states = [ordered]@{
            dimensions = [bool]$dimension.passed
            topology_uv = [bool]$topology.passed
            structural_counts = ([int]$topology.structural_counts.buildings -eq 5 -and [int]$topology.structural_counts.vehicles -eq 8 -and [int]$topology.structural_counts.trees -eq 10)
            checkpoints = ([bool]$checkpoints.passed -and [int]$checkpoints.count -eq 9)
            source_parity = ([bool]$sourceParity.passed -and [string]$sourceParity.sha256 -eq 'a47375d2afe02c2d829311249cf32b50e6fe034cc8b60c32e1eb9dab9bd52399')
            terminal = ([bool]$terminal.automatic_validation_passed -and [string]$terminal.status -eq 'CHECKPOINT_COMPLETED_AWAITING_DIRECT_FULL_RESOLUTION_VISUAL_REVIEW' -and -not [bool]$terminal.finalization_authorized)
        }
        foreach ($key in $state.receipt_states.Keys) { if (-not $state.receipt_states[$key]) { throw "Receipt validation failed: $key" } }
        $state.produced_files = Get-ProducedInventory $OutputRoot
        if ($state.produced_files.Count -ne 16) { throw "Total output file count is not exactly sixteen: $($state.produced_files.Count)" }
        $state.classification = 'PASSED_AUTOMATIC_AWAITING_MANDATORY_POSTFLIGHT_AND_DIRECT_VISUAL_REVIEW'
        $exit = 0
    }

}
catch {
    $state.failure_stage = $stage
    $state.failure_message = $_.Exception.Message
    $state.classification = 'FAILED_WITH_EVIDENCE'
    if ($_.Exception.Message -eq 'Authorized and offline modes are mutually exclusive') { $exit = 3 }
    elseif ($_.Exception.Message -eq 'Normal mode requires -AuthorizeSingleBlender') { $exit = 2 }
    else { $exit = 1 }
}
finally {
    $state.terminal = $true
    $state.end_utc = [DateTime]::UtcNow.ToString('o')
    if ($writeTerminal) {
        $mode = Write-TerminalEvidence $manifestPath $emergencyPath $state
        if ($mode -eq 'lost') { $exit = 1 }
    }
}

exit ([int]$exit)
