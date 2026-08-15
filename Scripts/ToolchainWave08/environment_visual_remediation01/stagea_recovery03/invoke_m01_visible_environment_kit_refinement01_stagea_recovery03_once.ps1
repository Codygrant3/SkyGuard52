[CmdletBinding()]
param(
    [switch]$AuthorizeSingleBlender,
    [switch]$OfflineContractTest,
    [string]$OfflineEvidenceRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Root = 'D:\Skyguard52'
$Gate = 'M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY03'
$Contract = Join-Path $Root 'Docs\Toolchain\ToolchainWave08\EnvironmentVisibleKitRefinement01StageARecovery03\execution_contract.json'
$RecoverySource = Join-Path $Root 'Scripts\ToolchainWave08\environment_visual_remediation01\stagea_recovery02\build_m01_visible_environment_kit_refinement01_stagea_recovery02.py'
$BaseSource = Join-Path $Root 'Scripts\ToolchainWave08\environment_visual_remediation01\build_m01_visible_environment_kit_refinement01_stagea.py'
$Recovery01Freeze = Join-Path $Root 'Docs\AAA_Review\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY01_ATTEMPT01_TERMINAL_FREEZE.json'
$Recovery02TerminalFreeze = Join-Path $Root 'Docs\AAA_Review\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY02_OFFLINE_CONTRACT_ATTEMPT01_TERMINAL_FREEZE.json'
$Blender = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
$AttemptRoot = Join-Path $Root 'Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY03\attempt_01'
$OutputRoot = Join-Path $Root 'Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentKit_Refinement01_StageA_Recovery03'
$TerminalManifest = Join-Path $Root 'Saved\Reports\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY03_TERMINAL_SUPERVISOR.json'
$EmergencyReceipt = Join-Path $Root 'Saved\Reports\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY03_EMERGENCY_RECEIPT.jsonl'
$TimeoutSeconds = 2700

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
                schema = 'skyguard.m01-visible-environment-kit-refinement01-stagea-recovery03.emergency.v1'
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
    if ($bytes.Length -lt 24 -or $bytes[0] -ne 137 -or $bytes[1] -ne 80 -or $bytes[2] -ne 78 -or $bytes[3] -ne 71) {
        throw "Invalid PNG signature: $Path"
    }
    $width = [int](($bytes[16] -shl 24) -bor ($bytes[17] -shl 16) -bor ($bytes[18] -shl 8) -bor $bytes[19])
    $height = [int](($bytes[20] -shl 24) -bor ($bytes[21] -shl 16) -bor ($bytes[22] -shl 8) -bor $bytes[23])
    return [ordered]@{ width = $width; height = $height }
}

function Assert-PngSet($Files, [int]$Width, [int]$Height, [string]$Label) {
    foreach ($file in @($Files)) {
        $dimensions = Get-PngDimensions $file.FullName
        if ($dimensions.width -ne $Width -or $dimensions.height -ne $Height) {
            throw "$Label PNG dimensions invalid: $($file.FullName)"
        }
    }
}

function Get-GovernedHeavyProcesses {
    return @(Get-Process -ErrorAction SilentlyContinue | Where-Object {
        $_.ProcessName -match '^(UnrealEditor|UnrealEditor-Cmd|Blender|ShaderCompileWorker|AutomationTool|UnrealBuildTool|dotnet|MSBuild|cl|link)$'
    })
}

function Assert-Recovery01Freeze {
    Assert-File $Recovery01Freeze 5197 'fc74e099a87ca1829d3f1e25b90df89112662a1b265dee6308da217f7c6466c9'
    $freeze = Get-Content -LiteralPath $Recovery01Freeze -Raw | ConvertFrom-Json
    if ($freeze.classification -ne 'FAILED_WITH_EVIDENCE' -or [int]$freeze.member_count -ne 13) {
        throw 'Recovery01 terminal freeze classification or cardinality drift'
    }
    foreach ($member in @($freeze.members)) {
        Assert-File ([string]$member.path) ([long]$member.bytes) ([string]$member.sha256)
    }
}

function Assert-Recovery02TerminalFreeze {
    Assert-File $Recovery02TerminalFreeze 1668 'ffcaab137433f713e931c579fb580c8c624646a1131ece36e79f397f4cc6c848'
    $freeze = Get-Content -LiteralPath $Recovery02TerminalFreeze -Raw | ConvertFrom-Json
    if ($freeze.classification -ne 'FAILED_WITH_EVIDENCE_NO_BLENDER_LAUNCHED_RECOVERY02_NAMESPACE_TERMINAL' -or [int]$freeze.member_count -ne 4) {
        throw 'Recovery02 offline-contract terminal freeze classification or cardinality drift'
    }
    foreach ($member in @($freeze.members)) {
        Assert-File ([string]$member.path) ([long]$member.bytes) ([string]$member.sha256)
    }
}

function Assert-Authorities {
    Assert-File $Contract 5406 'c818c6987f6cf44d8e2f08bb9b1fd7e3b57ada8cf7bbdfab488aff08a10fc728'
    Assert-File $RecoverySource 6111 'ec787aae6b0017078634e11ef4d5ad56ada06ba0133d8c3f6a81ad9206374c61'
    Assert-File $BaseSource 42238 '773e67931108a2f199f763a4d3ce94348ba9ed9a403c049b3b8b4409bb06fd12'
    Assert-File $Blender 112975320 'e27fbfea8564aa645d4463cb0949695fd85562b9de6df9561b06859a1074adf7'
    Assert-Recovery01Freeze
    Assert-Recovery02TerminalFreeze
    $contractData = Get-Content -LiteralPath $Contract -Raw | ConvertFrom-Json
    if ($contractData.gate -ne $Gate) { throw 'Recovery03 gate drift' }
    if ([int]$contractData.bounded_correction.geometry_changes -ne 0) { throw 'Geometry-change contract drift' }
    if ([int]$contractData.bounded_correction.camera_changes -ne 0) { throw 'Camera-change contract drift' }
    if ([int]$contractData.execution.blender_launch_count -ne 1) { throw 'Launch-count contract drift' }
    if ([int]$contractData.execution.automatic_retry_count -ne 0) { throw 'Retry-count contract drift' }
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
    schema = 'skyguard.m01-visible-environment-kit-refinement01-stagea-recovery03.supervisor-terminal.v1'
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
    output_counts = [ordered]@{ blend = 0; glb = 0; checkpoint_png = 0; final_png = 0; texture_png = 0 }
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
        $wrapperText = [IO.File]::ReadAllText($RecoverySource)
        if ([regex]::Matches($wrapperText, [regex]::Escape('bpy.data.images.load(str(path), check_existing=False)')).Count -ne 1) {
            throw 'Saved-PNG measurement load cardinality is not one'
        }
        if ([regex]::Matches($wrapperText, [regex]::Escape('bpy.data.images.remove(measured)')).Count -ne 1) {
            throw 'Temporary measurement datablock cleanup cardinality is not one'
        }
        if ($wrapperText -notmatch 'luma\.size == width \* height and luma\.size > 0') { throw 'Fail-closed luminance validation missing' }
        $state.preflight_passed = $true
        $state.classification = 'PASS'
        $exit = 0
    }
    else {
        if (-not $AuthorizeSingleBlender) { throw 'Normal mode requires -AuthorizeSingleBlender' }
        $state.preflight_passed = $true
        [IO.Directory]::CreateDirectory((Join-Path $AttemptRoot 'source')) | Out-Null
        $state.governed_attempt_namespace_created = $true
        $attemptSource = Join-Path $AttemptRoot 'source\build_m01_visible_environment_kit_refinement01_stagea_recovery02.py'
        [IO.File]::Copy($RecoverySource, $attemptSource, $false)
        [IO.File]::Copy($Contract, (Join-Path $AttemptRoot 'execution_contract.json'), $false)
        Assert-File $attemptSource 6111 'ec787aae6b0017078634e11ef4d5ad56ada06ba0133d8c3f6a81ad9206374c61'
        Write-JsonAtomic (Join-Path $AttemptRoot 'preflight_receipt.json') ([ordered]@{
            schema = 'skyguard.m01-visible-environment-kit-refinement01-stagea-recovery03.preflight.v1'
            at_utc = [DateTime]::UtcNow.ToString('o')
            recovery01_freeze_sha256 = 'fc74e099a87ca1829d3f1e25b90df89112662a1b265dee6308da217f7c6466c9'
            base_source_sha256 = '773e67931108a2f199f763a4d3ce94348ba9ed9a403c049b3b8b4409bb06fd12'
            recovery_source_sha256 = 'ec787aae6b0017078634e11ef4d5ad56ada06ba0133d8c3f6a81ad9206374c61'
            recovery01_members_verified = 13
            recovery02_terminal_freeze_sha256 = 'ffcaab137433f713e931c579fb580c8c624646a1131ece36e79f397f4cc6c848'
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
            '--expected-source-sha256', 'ec787aae6b0017078634e11ef4d5ad56ada06ba0133d8c3f6a81ad9206374c61'
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
            $sample = @(
                Get-CimInstance Win32_Process -Filter "ProcessId=$($process.Id) OR ParentProcessId=$($process.Id)" -ErrorAction SilentlyContinue |
                    Select-Object Name, ProcessId, ParentProcessId, CommandLine
            )
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
        if (-not (Test-Path -LiteralPath $OutputRoot)) { throw 'Blender did not create the Recovery03 output namespace' }
        $state.output_namespace_created = $true

        $stage = 'OUTPUT_VALIDATION'
        $stderrText = if (Test-Path -LiteralPath $stderr) { [IO.File]::ReadAllText($stderr) } else { '' }
        if ($stderrText -match 'Traceback \(most recent call last\)|FAILED_WITH_EVIDENCE|ArrayMemoryError|zero-size array') {
            throw 'Blender stderr contains a Python traceback or governed build error'
        }
        $blendFiles = @(Get-ChildItem -LiteralPath $OutputRoot -Recurse -Filter '*.blend' -File)
        $glbFiles = @(Get-ChildItem -LiteralPath $OutputRoot -Recurse -Filter '*.glb' -File)
        $checkpointFiles = @(Get-ChildItem -LiteralPath (Join-Path $OutputRoot 'renders\checkpoints') -Filter '*.png' -File)
        $finalFiles = @(Get-ChildItem -LiteralPath (Join-Path $OutputRoot 'renders\final') -Filter '*.png' -File)
        $textureFiles = @(Get-ChildItem -LiteralPath (Join-Path $OutputRoot 'textures') -Filter '*.png' -File)
        $state.output_counts = [ordered]@{
            blend = $blendFiles.Count
            glb = $glbFiles.Count
            checkpoint_png = $checkpointFiles.Count
            final_png = $finalFiles.Count
            texture_png = $textureFiles.Count
        }
        if ($blendFiles.Count -ne 1 -or $glbFiles.Count -ne 4 -or $checkpointFiles.Count -ne 3 -or $finalFiles.Count -ne 15 -or $textureFiles.Count -ne 5) {
            throw "Recovery03 output cardinality failed: $($state.output_counts | ConvertTo-Json -Compress)"
        }
        Assert-PngSet $checkpointFiles 1280 720 'Checkpoint'
        Assert-PngSet $finalFiles 2560 1440 'Final render'
        Assert-PngSet $textureFiles 2048 2048 'Texture'

        $requiredReceipts = @('dimension_receipt.json','topology_uv_receipt.json','material_texture_receipt.json','checkpoint_receipt.json','render_receipt.json','export_receipt.json','source_parity_receipt.json','artifact_inventory.json','terminal_receipt.json')
        foreach ($name in $requiredReceipts) {
            if (-not (Test-Path -LiteralPath (Join-Path $OutputRoot $name))) { throw "Missing receipt: $name" }
        }
        $dimension = Get-Content -LiteralPath (Join-Path $OutputRoot 'dimension_receipt.json') -Raw | ConvertFrom-Json
        $topology = Get-Content -LiteralPath (Join-Path $OutputRoot 'topology_uv_receipt.json') -Raw | ConvertFrom-Json
        $materials = Get-Content -LiteralPath (Join-Path $OutputRoot 'material_texture_receipt.json') -Raw | ConvertFrom-Json
        $checkpoints = Get-Content -LiteralPath (Join-Path $OutputRoot 'checkpoint_receipt.json') -Raw | ConvertFrom-Json
        $renders = Get-Content -LiteralPath (Join-Path $OutputRoot 'render_receipt.json') -Raw | ConvertFrom-Json
        $exports = Get-Content -LiteralPath (Join-Path $OutputRoot 'export_receipt.json') -Raw | ConvertFrom-Json
        $sourceParity = Get-Content -LiteralPath (Join-Path $OutputRoot 'source_parity_receipt.json') -Raw | ConvertFrom-Json
        $terminal = Get-Content -LiteralPath (Join-Path $OutputRoot 'terminal_receipt.json') -Raw | ConvertFrom-Json
        $state.receipt_states = [ordered]@{
            dimensions = [bool]$dimension.passed
            topology_uv = [bool]$topology.passed
            materials = [bool]$materials.passed
            checkpoints = ([bool]$checkpoints.passed -and [int]$checkpoints.count -eq 3)
            final_renders = ([bool]$renders.passed -and [int]$renders.count -eq 15)
            exports = [bool]$exports.passed
            source_parity = ([bool]$sourceParity.passed -and [string]$sourceParity.sha256 -eq 'ec787aae6b0017078634e11ef4d5ad56ada06ba0133d8c3f6a81ad9206374c61')
            terminal = ([bool]$terminal.automatic_validation_passed -and [string]$terminal.status -eq 'BLENDER_COMPLETED_AWAITING_EXTERNAL_FULL_RESOLUTION_VISUAL_REVIEW')
        }
        foreach ($key in $state.receipt_states.Keys) {
            if (-not $state.receipt_states[$key]) { throw "Receipt validation failed: $key" }
        }
        $state.produced_files = Get-ProducedInventory $OutputRoot
        $state.classification = 'PASSED_AUTOMATIC_AWAITING_EXTERNAL_FULL_RESOLUTION_VISUAL_REVIEW'
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
