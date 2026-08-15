[CmdletBinding()]
param(
    [switch]$AuthorizeSingleBlender,
    [switch]$OfflineContractTest,
    [string]$OfflineEvidenceRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Root = 'D:\Skyguard52'
$Gate = 'M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY10_CHECKPOINT01'
$Contract = Join-Path $Root 'Docs\Toolchain\ToolchainWave08\EnvironmentVisibleKitRefinement01StageARecovery10\execution_contract.json'
$Worker = Join-Path $Root 'Scripts\ToolchainWave08\environment_visual_remediation01\stagea_recovery10\build_m01_visible_environment_kit_refinement01_stagea_recovery10_checkpoint01.py'
$R09Freeze = Join-Path $Root 'Docs\AAA_Review\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY09_CHECKPOINT01_ATTEMPT01_TERMINAL_FREEZE.json'
$ProbeResult = Join-Path $Root 'Saved\Reports\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY10_STORM_REVIEW_LIGHT_PROBE_RESULT.json'
$StandingAuthorization = Join-Path $Root 'Docs\AAA_Review\SKYGUARD52_STANDING_BLENDER_UNREAL_AUTHORIZATION_FREEZE_2026-08-09.json'
$Blender = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
$AttemptRoot = Join-Path $Root 'Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY10_CHECKPOINT01\attempt_01'
$OutputRoot = Join-Path $Root 'Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentKit_Refinement01_StageA_Recovery10_Checkpoint01'
$TerminalManifest = Join-Path $Root 'Saved\Reports\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY10_CHECKPOINT01_TERMINAL_SUPERVISOR.json'
$EmergencyReceipt = Join-Path $Root 'Saved\Reports\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY10_CHECKPOINT01_EMERGENCY_RECEIPT.jsonl'
$TimeoutSeconds = 3600

function Get-Sha256Lower([string]$Path) {
    if (-not [IO.File]::Exists($Path)) { throw "Missing file: $Path" }
    $stream = $null
    $hasher = $null
    try {
        $stream = [IO.File]::Open($Path, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::Read)
        $hasher = [Security.Cryptography.SHA256]::Create()
        return (($hasher.ComputeHash($stream) | ForEach-Object { $_.ToString('x2') }) -join '')
    }
    finally {
        if ($null -ne $hasher) { $hasher.Dispose() }
        if ($null -ne $stream) { $stream.Dispose() }
    }
}

function Assert-File([string]$Path, [long]$Bytes, [string]$Sha256) {
    $item = Get-Item -LiteralPath $Path -ErrorAction Stop
    if ($item.Length -ne $Bytes) { throw "Byte-count drift: $Path" }
    if ((Get-Sha256Lower $Path) -ne $Sha256) { throw "SHA-256 drift: $Path" }
}

function Write-JsonAtomic([string]$Path, [object]$Payload) {
    $parent = [IO.Path]::GetDirectoryName($Path)
    if (-not [string]::IsNullOrWhiteSpace($parent)) { [IO.Directory]::CreateDirectory($parent) | Out-Null }
    $temporary = "$Path.tmp"
    [IO.File]::WriteAllText($temporary, (($Payload | ConvertTo-Json -Depth 16) + [Environment]::NewLine), [Text.UTF8Encoding]::new($false))
    [IO.File]::Move($temporary, $Path)
}

function Write-TerminalEvidence([string]$ManifestPath, [string]$EmergencyPath, [object]$Payload) {
    try {
        Write-JsonAtomic $ManifestPath $Payload
        return 'manifest'
    }
    catch {
        try {
            $parent = [IO.Path]::GetDirectoryName($EmergencyPath)
            if (-not [string]::IsNullOrWhiteSpace($parent)) { [IO.Directory]::CreateDirectory($parent) | Out-Null }
            $line = [ordered]@{ at_utc=[DateTime]::UtcNow.ToString('o'); gate=$Gate; classification='FAILED_WITH_EVIDENCE'; manifest_error=$_.Exception.Message } | ConvertTo-Json -Compress
            [IO.File]::AppendAllText($EmergencyPath, $line + [Environment]::NewLine, [Text.UTF8Encoding]::new($false))
            return 'emergency'
        }
        catch { return 'lost' }
    }
}

function Get-HeavyProcesses {
    return @(Get-Process -ErrorAction SilentlyContinue | Where-Object {
        $_.ProcessName -match '^(UnrealEditor|UnrealEditor-Cmd|Blender|ShaderCompileWorker|AutomationTool|UnrealBuildTool|dotnet|MSBuild|cl|link)$'
    })
}

function Assert-Authorities {
    Assert-File $R09Freeze 2226 '9c16aa6217e4c5a4480bd8e76ec4681d8567da7e9459b3baed021291cd5db97c'
    $freeze = Get-Content -LiteralPath $R09Freeze -Raw | ConvertFrom-Json
    if ($freeze.classification -ne 'FAILED_WITH_EVIDENCE' -or [int]$freeze.member_count -ne 6 -or [int]$freeze.verified_members -ne 6) { throw 'Recovery09 terminal freeze drift' }
    foreach ($member in @($freeze.members)) { Assert-File ([string]$member.path) ([long]$member.bytes) ([string]$member.sha256) }
    Assert-File $Contract 4230 '703559a67a18f254ab281225dc2c062794d479a72571e5ac54aea6bf3a9c7b76'
    Assert-File $Worker 11271 '097f473dd9bed0c94b39653f5dd5a7f046137d2fa5bc43e6e9e10e1406e535ba'
    Assert-File $ProbeResult 1335 '2c780572a701482d52d3bc1fd52acc95bf29788d2bc0938ccf809a1cef4cd531'
    Assert-File $StandingAuthorization 1415 '1366fc227908148199776d866d3f3a94bd56919d54babf5d64be9c26633df4e1'
    Assert-File $Blender 112975320 'e27fbfea8564aa645d4463cb0949695fd85562b9de6df9561b06859a1074adf7'
    $contractData = Get-Content -LiteralPath $Contract -Raw | ConvertFrom-Json
    if ($contractData.gate -ne $Gate) { throw 'Gate contract drift' }
    if ([int]$contractData.execution.timeout_seconds -ne $TimeoutSeconds) { throw 'Timeout contract drift' }
    if ([int]$contractData.output_contract.expected_total_file_count -ne 16 -or [int]$contractData.output_contract.checkpoint_png_count -ne 9) { throw 'Output contract drift' }
    if ($contractData.targeted_review_lighting_contract.storm_probe_candidate -ne 'B' -or [double]$contractData.targeted_review_lighting_contract.storm_fill_energy -ne 2800.0 -or [double]$contractData.targeted_review_lighting_contract.storm_moon_energy -ne 2400.0 -or -not [bool]$contractData.targeted_review_lighting_contract.storm_probe_passed_all_three_cameras) { throw 'Storm review-light contract drift' }
}

function Assert-FutureNamespacesAbsent {
    foreach ($path in @($AttemptRoot, $OutputRoot, $TerminalManifest, $EmergencyReceipt)) {
        if (Test-Path -LiteralPath $path) { throw "Future namespace exists: $path" }
    }
}

function Get-ProducedInventory([string]$RootPath) {
    return @(Get-ChildItem -LiteralPath $RootPath -Recurse -File | Sort-Object FullName | ForEach-Object {
        [ordered]@{ relative_path=$_.FullName.Substring($RootPath.Length).TrimStart('\'); bytes=$_.Length; sha256=Get-Sha256Lower $_.FullName }
    })
}

function Assert-PngDimensions([IO.FileInfo[]]$Files, [int]$Width, [int]$Height) {
    foreach ($file in $Files) {
        $header = [IO.File]::ReadAllBytes($file.FullName)
        if ($header.Length -lt 24 -or $header[0] -ne 137 -or $header[1] -ne 80 -or $header[2] -ne 78 -or $header[3] -ne 71) { throw "Invalid PNG header: $($file.FullName)" }
        $actualWidth = ([int]$header[16] -shl 24) -bor ([int]$header[17] -shl 16) -bor ([int]$header[18] -shl 8) -bor [int]$header[19]
        $actualHeight = ([int]$header[20] -shl 24) -bor ([int]$header[21] -shl 16) -bor ([int]$header[22] -shl 8) -bor [int]$header[23]
        if ($actualWidth -ne $Width -or $actualHeight -ne $Height) { throw "PNG dimensions failed: $($file.FullName)" }
    }
}

$state = [ordered]@{
    schema='skyguard.m01-visible-environment-kit-refinement01-stagea-recovery10-checkpoint01.supervisor-terminal.v1'
    gate=$Gate
    classification='FAILED_WITH_EVIDENCE'
    terminal=$false
    mode=if ($OfflineContractTest) { 'offline_contract_test' } else { 'single_blender_execution' }
    supervisor_launch_count=1
    blender_launch_count=0
    retry_count=0
    unreal_launch_count=0
    preflight_passed=$false
    governed_attempt_namespace_created=$false
    output_namespace_created=$false
    blender_pid=$null
    native_handle_retained=$false
    start_utc=[DateTime]::UtcNow.ToString('o')
    end_utc=$null
    timeout=$false
    exit_code=$null
    exit_code_type=$null
    failure_stage=$null
    failure_message=$null
    output_counts=[ordered]@{ blend=0; glb=0; checkpoint_png=0; final_png=0; texture_png=0; receipt=0 }
    receipt_states=[ordered]@{}
    produced_files=@()
    process_tree_samples=@()
}

$hasOfflineRoot = ($OfflineContractTest -and -not [string]::IsNullOrWhiteSpace($OfflineEvidenceRoot))
$manifestPath = if ($hasOfflineRoot) { Join-Path $OfflineEvidenceRoot 'terminal_manifest.json' } else { $TerminalManifest }
$emergencyPath = if ($hasOfflineRoot) { Join-Path $OfflineEvidenceRoot 'emergency_receipt.jsonl' } else { $EmergencyReceipt }
$writeTerminal = ($hasOfflineRoot -or $AuthorizeSingleBlender)
$stage = 'INITIALIZATION'
$exit = 1

try {
    $stage = 'AUTHORITY_PREFLIGHT'
    if ($AuthorizeSingleBlender -and $OfflineContractTest) { throw 'Authorized and offline modes are mutually exclusive' }
    if ($OfflineContractTest -and [string]::IsNullOrWhiteSpace($OfflineEvidenceRoot)) { throw '-OfflineEvidenceRoot is required' }
    Assert-Authorities
    if (@(Get-HeavyProcesses).Count -ne 0) { throw 'A governed heavy process is already active' }
    Assert-FutureNamespacesAbsent

    if ($OfflineContractTest) {
        [IO.Directory]::CreateDirectory($OfflineEvidenceRoot) | Out-Null
        $workerText = [IO.File]::ReadAllText($Worker)
        foreach ($token in @('"storm_review_lighting_aimed"','fill_energy=2800.0','if condition in ("night", "storm"):', 'recovery09_attempt_or_output_reused": False')) {
            if ($workerText -notlike "*$token*") { throw "Offline contract token is missing: $token" }
        }
        $state.preflight_passed = $true
        $state.classification = 'PASS'
        $state.receipt_states = [ordered]@{ recovery09_preserved=$true; storm_probe_candidate_b=$true; checkpoint_only=$true }
        $exit = 0
    }
    else {
        if (-not $AuthorizeSingleBlender) { throw 'Normal mode requires -AuthorizeSingleBlender' }
        $state.preflight_passed = $true
        [IO.Directory]::CreateDirectory((Join-Path $AttemptRoot 'source')) | Out-Null
        $state.governed_attempt_namespace_created = $true
        $attemptSource = Join-Path $AttemptRoot 'source\build_m01_visible_environment_kit_refinement01_stagea_recovery10_checkpoint01.py'
        [IO.File]::Copy($Worker, $attemptSource, $false)
        [IO.File]::Copy($Contract, (Join-Path $AttemptRoot 'execution_contract.json'), $false)
        Assert-File $attemptSource 11271 '097f473dd9bed0c94b39653f5dd5a7f046137d2fa5bc43e6e9e10e1406e535ba'
        Write-JsonAtomic (Join-Path $AttemptRoot 'preflight_receipt.json') ([ordered]@{
            schema='skyguard.m01-visible-environment-kit-refinement01-stagea-recovery10-checkpoint01.preflight.v1'
            at_utc=[DateTime]::UtcNow.ToString('o')
            recovery09_terminal_freeze_sha256='9c16aa6217e4c5a4480bd8e76ec4681d8567da7e9459b3baed021291cd5db97c'
            recovery09_terminal_members_verified=6
            recovery_source_sha256='097f473dd9bed0c94b39653f5dd5a7f046137d2fa5bc43e6e9e10e1406e535ba'
            storm_probe_candidate='B'
            standing_authorization=$true
            retry_count=0
            passed=$true
        })
        $stdout = Join-Path $AttemptRoot 'blender.stdout.log'
        $stderr = Join-Path $AttemptRoot 'blender.stderr.log'
        $arguments = @('--background','--factory-startup','--python',$attemptSource,'--','--output',$OutputRoot,'--asset-id','m01-visible-environment-kit-refinement01-stagea','--expected-source-sha256','097f473dd9bed0c94b39653f5dd5a7f046137d2fa5bc43e6e9e10e1406e535ba')
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
            $sample = @(Get-CimInstance Win32_Process -Filter "ProcessId=$($process.Id) OR ParentProcessId=$($process.Id)" -ErrorAction SilentlyContinue | Select-Object Name,ProcessId,ParentProcessId,CommandLine)
            $state.process_tree_samples += @([ordered]@{ timestamp_utc=[DateTime]::UtcNow.ToString('o'); processes=$sample })
            Start-Sleep -Seconds 3
            $process.Refresh()
        }
        $process.WaitForExit()
        $process.Refresh()
        $code = $process.ExitCode
        $state.exit_code = [int]$code
        $state.exit_code_type = $code.GetType().FullName
        if ($code -ne 0) { throw "Blender returned exit code $code" }
        if (-not (Test-Path -LiteralPath $OutputRoot)) { throw 'Blender did not create the Recovery10 output namespace' }
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
        $state.output_counts = [ordered]@{ blend=$blendFiles.Count; glb=$glbFiles.Count; checkpoint_png=$checkpointFiles.Count; final_png=$finalFiles.Count; texture_png=$textureFiles.Count; receipt=$receiptFiles.Count }
        if ($blendFiles.Count -ne 1 -or $glbFiles.Count -ne 0 -or $checkpointFiles.Count -ne 9 -or $finalFiles.Count -ne 0 -or $textureFiles.Count -ne 0 -or $receiptFiles.Count -ne 6) { throw "Checkpoint-only output cardinality failed: $($state.output_counts | ConvertTo-Json -Compress)" }
        Assert-PngDimensions $checkpointFiles 1920 1080
        $dimension = Get-Content -LiteralPath (Join-Path $OutputRoot 'dimension_receipt.json') -Raw | ConvertFrom-Json
        $topology = Get-Content -LiteralPath (Join-Path $OutputRoot 'topology_uv_receipt.json') -Raw | ConvertFrom-Json
        $checkpoints = Get-Content -LiteralPath (Join-Path $OutputRoot 'checkpoint_receipt.json') -Raw | ConvertFrom-Json
        $sourceParity = Get-Content -LiteralPath (Join-Path $OutputRoot 'source_parity_receipt.json') -Raw | ConvertFrom-Json
        $terminal = Get-Content -LiteralPath (Join-Path $OutputRoot 'terminal_receipt.json') -Raw | ConvertFrom-Json
        $nightEntries = @($checkpoints.checkpoints | Where-Object { $_.condition -eq 'night' })
        $stormEntries = @($checkpoints.checkpoints | Where-Object { $_.condition -eq 'storm' })
        $state.receipt_states = [ordered]@{
            dimensions=[bool]$dimension.passed
            topology_uv=[bool]$topology.passed
            structural_counts=([int]$topology.structural_counts.buildings -eq 5 -and [int]$topology.structural_counts.vehicles -eq 8 -and [int]$topology.structural_counts.trees -eq 10)
            checkpoints=([bool]$checkpoints.passed -and [int]$checkpoints.count -eq 9)
            night_targeted=($nightEntries.Count -eq 3 -and @($nightEntries | Where-Object { -not [bool]$_.night_review_lighting_aimed }).Count -eq 0)
            storm_targeted=($stormEntries.Count -eq 3 -and @($stormEntries | Where-Object { -not [bool]$_.storm_review_lighting_aimed }).Count -eq 0)
            source_parity=([bool]$sourceParity.passed -and [string]$sourceParity.sha256 -eq '097f473dd9bed0c94b39653f5dd5a7f046137d2fa5bc43e6e9e10e1406e535ba')
            terminal=([bool]$terminal.automatic_validation_passed -and [string]$terminal.status -eq 'CHECKPOINT_COMPLETED_AWAITING_DIRECT_FULL_RESOLUTION_VISUAL_REVIEW' -and -not [bool]$terminal.finalization_authorized)
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
