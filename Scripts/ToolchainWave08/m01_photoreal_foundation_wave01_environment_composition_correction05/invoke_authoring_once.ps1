param(
    [switch]$OfflineContractTest,
    [switch]$AuthorizeSingleUnreal
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Project = 'D:\SG52T08_ENV01\Skyguard52.uproject'
$Editor = 'D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$InputMap = 'D:\SG52T08_ENV01\Content\M01\Lvl_M01_PhotorealFoundation_GroundLightingCorrection04Recovery01.umap'
$OutputMap = 'D:\SG52T08_ENV01\Content\M01\Lvl_M01_PhotorealFoundation_EnvironmentCompositionCorrection05.umap'
$StandingAuthorization = 'D:\Skyguard52\Production\standing_heavy_process_authorization.json'
$Author = 'D:\Skyguard52\Scripts\ToolchainWave08\m01_photoreal_foundation_wave01_environment_composition_correction05\author_environment_composition_correction05.py'
$Verifier = 'D:\Skyguard52\Scripts\ToolchainWave08\m01_photoreal_foundation_wave01_environment_composition_correction05\verify_authoring_offline.py'
$Contract = 'D:\Skyguard52\Docs\Toolchain\ToolchainWave08\M01PhotorealFoundationEnvironmentCompositionCorrection05\quality_contract.json'
$FailedVisualFreeze = 'D:\Skyguard52\Docs\AAA_Review\M01_PHOTOREAL_FOUNDATION_WAVE01_GROUND_LIGHTING_CORRECTION04_RECOVERY01_VISUAL_PROOF01_ATTEMPT01_TERMINAL_FREEZE.json'
$DirectVisualReview = 'D:\Skyguard52\Docs\AAA_Review\M01_PHOTOREAL_FOUNDATION_WAVE01_GROUND_LIGHTING_CORRECTION04_RECOVERY01_VISUAL_PROOF01_ATTEMPT01_DIRECT_VISUAL_REVIEW.json'
$AttemptRoot = 'D:\Skyguard52\Saved\BuildAttempts\M01_PHOTOREAL_FOUNDATION_WAVE01_ENVIRONMENT_COMPOSITION_CORRECTION05_AUTHORING\attempt_01'
$Receipt = Join-Path $AttemptRoot 'authoring_receipt.json'
$TerminalManifest = 'D:\Skyguard52\Saved\Reports\M01_PHOTOREAL_FOUNDATION_WAVE01_ENVIRONMENT_COMPOSITION_CORRECTION05_AUTHORING_TERMINAL_MANIFEST.json'
$EmergencyReceipt = 'D:\Skyguard52\Saved\Reports\M01_PHOTOREAL_FOUNDATION_WAVE01_ENVIRONMENT_COMPOSITION_CORRECTION05_AUTHORING_EMERGENCY_RECEIPT.jsonl'
$TimeoutSeconds = 1800

$Expected = @(
    @{ Path = $Project; Bytes = 3703; Sha256 = '7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a'; Label = 'Isolated project' },
    @{ Path = $Editor; Bytes = 512952; Sha256 = '0fb325cf215cc800ce260a1890af3f3dc314b8cc6331061d4e7e7246489af2e0'; Label = 'UE 5.8 editor' },
    @{ Path = $InputMap; Bytes = 743809; Sha256 = '97902b7dd39556d4409adcdd87a8c995cfef1322a8e827c52cae7a84020093cf'; Label = 'Accepted input map' },
    @{ Path = $StandingAuthorization; Bytes = 2146; Sha256 = '48277d7edd869cc2b841c3993e8f7599bec5291ddf23e9c442b33e09b870c089'; Label = 'Standing authorization' },
    @{ Path = $Author; Bytes = 22628; Sha256 = '250c91c8facdea46ce1e5602eeb47e90cefd609c6b9f908f9f19c67eb5e2c294'; Label = 'Correction05 author' },
    @{ Path = $Verifier; Bytes = 5241; Sha256 = 'a032dd95a4712ac213da622bce2239b88f49f3ae83125ac5f297c3942d7cba0a'; Label = 'Correction05 verifier' },
    @{ Path = $Contract; Bytes = 2934; Sha256 = '6ef70fce7fd71eb0a1b0b652e323774f9411ef14554033a49e7861da333dcfc6'; Label = 'Correction05 contract' },
    @{ Path = $FailedVisualFreeze; Bytes = 4728; Sha256 = '0260193ab363d6c913e346bc561d0b7a65f93fc196f6b9532ebe55cbd8f13068'; Label = 'Failed visual freeze' },
    @{ Path = $DirectVisualReview; Bytes = 6899; Sha256 = 'c8384f95a850c3c1f231eb0bdc05b2d7aa344f279c282b29d6882d97c7a8d346'; Label = 'Direct visual review' },
    @{ Path = 'D:\SG52T08_ENV01\Content\Skyguard\Meshes\Mission01\Wave1Refinement\m01_wave1_aaa_refinement\StaticMeshes\SM_M01_Coast_Beach_Detailed_A.uasset'; Bytes = 86515; Sha256 = '13358d6fc16ae1b648275d8bb5f7cbe8c4af92948d20dc2059a598e6b16a2ffe'; Label = 'UV-mapped beach mesh' },
    @{ Path = 'D:\SG52T08_ENV01\Content\Skyguard\Meshes\Mission01\Wave1Refinement\m01_wave1_aaa_refinement\StaticMeshes\SM_M01_Road_CoastalTransition_Detailed_A.uasset'; Bytes = 94244; Sha256 = 'fa87e9c9cc93d2612c5a461f854234c47cfd91242905e93931a81e103779b144'; Label = 'Cross-street mesh' },
    @{ Path = 'D:\SG52T08_ENV01\Content\M01\GroundLightingCorrection04Recovery01\Materials\MI_M01_BeachSand_Tiled.uasset'; Bytes = 75315; Sha256 = '6c99656214d6a827b083156ea9913d9e55c4d4a177bcd891b614509ede83e4e8'; Label = 'Accepted beach material' },
    @{ Path = 'D:\UE_5.8\Engine\Plugins\Experimental\Water\Content\Materials\WaterSurface\Water_Material_Ocean.uasset'; Bytes = 90080; Sha256 = 'ee16c08c99c9a8b2b1d24241d37455ae50ba01c877d4f9a77dc1588da2ca7ec6'; Label = 'UE ocean material' },
    @{ Path = 'D:\UE_5.8\Engine\Plugins\Experimental\Water\Content\Materials\WaterSurface\Water_FarMesh.uasset'; Bytes = 12296; Sha256 = 'ccfcf0df2bd5bf9db9cc1e9b7d2394dff546e8faad78f7e999e69102aaf77d6d'; Label = 'UE far-water material' },
    @{ Path = 'D:\UE_5.8\Engine\Plugins\Experimental\Water\Content\Waves\GerstnerWaves_Ocean.uasset'; Bytes = 7962; Sha256 = '1f76d0c540daff4af14277b34af7f92184a2b0ee76574c51995233bb39edfb2f'; Label = 'UE ocean waves' }
)

function Get-Sha256([string]$Path) {
    $stream = [System.IO.File]::Open($Path, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::Read)
    $hasher = [System.Security.Cryptography.SHA256]::Create()
    try { return ([System.BitConverter]::ToString($hasher.ComputeHash($stream))).Replace('-', '').ToLowerInvariant() }
    finally { $hasher.Dispose(); $stream.Dispose() }
}

function Assert-File([hashtable]$Row) {
    if (-not [System.IO.File]::Exists($Row.Path)) { throw "$($Row.Label) missing: $($Row.Path)" }
    $info = [System.IO.FileInfo]::new($Row.Path)
    if ($info.Length -ne [int64]$Row.Bytes) { throw "$($Row.Label) byte mismatch: $($info.Length) != $($Row.Bytes)" }
    $actual = Get-Sha256 $Row.Path
    if ($actual -ne [string]$Row.Sha256) { throw "$($Row.Label) hash mismatch: $actual != $($Row.Sha256)" }
}

function Write-JsonAtomic([string]$Path, [object]$Payload) {
    [System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName($Path)) | Out-Null
    $temporary = "$Path.tmp"
    [System.IO.File]::WriteAllText($temporary, ($Payload | ConvertTo-Json -Depth 80) + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
    if ([System.IO.File]::Exists($Path)) { throw "Refusing to overwrite terminal evidence: $Path" }
    [System.IO.File]::Move($temporary, $Path)
}

function Get-HeavyProcesses {
    return @(Get-Process -ErrorAction SilentlyContinue | Where-Object {
        $_.ProcessName -match '^(UnrealEditor|UnrealEditor-Cmd|Blender|ShaderCompileWorker|AutomationTool|UnrealBuildTool|cl|link)$'
    } | Select-Object Id, ProcessName, StartTime)
}

function Assert-Authorities {
    foreach ($row in $Expected) { Assert-File $row }
    $authorization = Get-Content -LiteralPath $StandingAuthorization -Raw | ConvertFrom-Json
    if ($authorization.status -ne 'ACTIVE' -or [bool]$authorization.execution_policy.per_run_user_authorization_required) { throw 'Standing heavy-process authorization is inactive' }
    $failure = Get-Content -LiteralPath $FailedVisualFreeze -Raw | ConvertFrom-Json
    if ($failure.classification -ne 'FAILED_WITH_EVIDENCE') { throw 'Failed visual freeze classification changed' }
    $review = Get-Content -LiteralPath $DirectVisualReview -Raw | ConvertFrom-Json
    if ($review.classification -ne 'FAILED_WITH_EVIDENCE') { throw 'Direct visual review classification changed' }
}

if ($OfflineContractTest) {
    Assert-Authorities
    if ([System.IO.Directory]::Exists($AttemptRoot)) { throw "Future attempt exists: $AttemptRoot" }
    if ([System.IO.File]::Exists($OutputMap)) { throw "Future output exists: $OutputMap" }
    if ([System.IO.File]::Exists($TerminalManifest)) { throw "Future terminal exists: $TerminalManifest" }
    if ([System.IO.File]::Exists($EmergencyReceipt)) { throw "Future emergency receipt exists: $EmergencyReceipt" }
    if (@(Get-HeavyProcesses).Count -ne 0) { throw 'Heavy process active during offline contract test' }
    $verifyOutput = & python $Verifier 2>&1
    if ($LASTEXITCODE -ne 0 -or ($verifyOutput -join "`n") -notmatch 'PASS') { throw "Offline verifier failed: $($verifyOutput -join ' ')" }
    [pscustomobject]@{
        classification = 'PASSED_OFFLINE_CONTRACT'
        unreal_launch_count = 0
        retry_count = 0
        governed_namespaces_created = 0
    } | ConvertTo-Json
    [Environment]::Exit([int]0)
}

if (-not $AuthorizeSingleUnreal) {
    [Console]::Error.WriteLine('Mechanical authorization switch is required; standing project authorization permits the supervisor to supply it.')
    [Environment]::Exit([int]2)
}

$state = [ordered]@{
    schema = 'skyguard.m01-photoreal-foundation.environment-composition-correction05.authoring-supervisor.v1'
    classification = 'FAILED_WITH_EVIDENCE'
    started_utc = [DateTime]::UtcNow.ToString('o')
    ended_utc = $null
    stage = 'initialization'
    executable = $Editor
    arguments = @()
    working_directory = 'D:\SG52T08_ENV01'
    supervisor_launch_count = 1
    unreal_launch_count = 0
    retry_count = 0
    pid = $null
    exit_code = $null
    exit_code_type = $null
    timeout = $false
    peak_working_set_bytes = [int64]0
    process_samples = @()
    receipt_path = $Receipt
    receipt_classification = $null
    output_map = $OutputMap
    output_bytes = $null
    output_sha256 = $null
    quality_metrics = $null
    input_unchanged = $false
    log_guard_passed = $false
    failure = $null
}

$finalExit = 1
try {
    $state.stage = 'preflight'
    Assert-Authorities
    if ([System.IO.Directory]::Exists($AttemptRoot)) { throw "Attempt exists: $AttemptRoot" }
    if ([System.IO.File]::Exists($OutputMap)) { throw "Output map exists: $OutputMap" }
    if ([System.IO.File]::Exists($TerminalManifest)) { throw "Terminal exists: $TerminalManifest" }
    if ([System.IO.File]::Exists($EmergencyReceipt)) { throw "Emergency receipt exists: $EmergencyReceipt" }
    $heavy = @(Get-HeavyProcesses)
    if ($heavy.Count -ne 0) { throw "Heavy process active: $($heavy | ConvertTo-Json -Compress)" }

    [System.IO.Directory]::CreateDirectory($AttemptRoot) | Out-Null
    $stdout = Join-Path $AttemptRoot 'unreal.stdout.log'
    $stderr = Join-Path $AttemptRoot 'unreal.stderr.log'
    $engineLog = Join-Path $AttemptRoot 'unreal.engine.log'
    $arguments = @(
        $Project,
        '-Unattended', '-NoSplash', '-NoSound', '-NullRHI', '-NoSaveOnExit',
        '-stdout', '-FullStdOutLogOutput', '-nop4',
        '-DisablePlugins=Fab,Bridge,EditorTelemetry,RuntimeTelemetry,EOSShared',
        '-ini:EditorSettings:[/Script/UnrealEd.AnalyticsPrivacySettings]:bSendUsageData=False',
        "-ExecutePythonScript=$Author", '-ScriptErrorsAreFatal', "-abslog=$engineLog"
    )
    $state.arguments = $arguments
    $state.stage = 'unreal_launch'
    $process = Start-Process -FilePath $Editor -ArgumentList $arguments -WorkingDirectory $state.working_directory -PassThru -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError $stderr
    $state.unreal_launch_count = 1
    $state.pid = $process.Id
    $handle = $process.Handle
    if ($null -eq $handle) { throw 'Failed to retain native process handle' }
    $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
    while (-not $process.HasExited -and [DateTime]::UtcNow -lt $deadline) {
        $process.Refresh()
        if ($process.WorkingSet64 -gt $state.peak_working_set_bytes) { $state.peak_working_set_bytes = [int64]$process.WorkingSet64 }
        $state.process_samples += [ordered]@{
            at_utc = [DateTime]::UtcNow.ToString('o')
            pid = $process.Id
            working_set_bytes = [int64]$process.WorkingSet64
        }
        Start-Sleep -Seconds 2
    }
    if (-not $process.HasExited) {
        $state.timeout = $true
        Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        throw "Unreal authoring exceeded $TimeoutSeconds seconds"
    }
    $process.WaitForExit()
    $process.Refresh()
    $state.exit_code = [int]$process.ExitCode
    $state.exit_code_type = $process.ExitCode.GetType().FullName
    if ($state.exit_code -ne 0) { throw "Unreal authoring returned $($state.exit_code)" }
    if ($state.exit_code_type -ne 'System.Int32') { throw "Unexpected exit-code type: $($state.exit_code_type)" }
    if (-not [System.IO.File]::Exists($Receipt)) { throw "Authoring receipt missing: $Receipt" }

    $state.stage = 'postflight'
    $payload = Get-Content -LiteralPath $Receipt -Raw | ConvertFrom-Json
    $state.receipt_classification = [string]$payload.classification
    $state.quality_metrics = $payload.quality_metrics
    if ($state.receipt_classification -ne 'PASSED_M01_PHOTOREAL_FOUNDATION_ENVIRONMENT_COMPOSITION_CORRECTION05_AUTOMATIC') { throw "Authoring receipt failed: $($state.receipt_classification)" }
    if (-not [System.IO.File]::Exists($OutputMap)) { throw "Output map missing: $OutputMap" }
    Assert-File @{ Path = $InputMap; Bytes = 743809; Sha256 = '97902b7dd39556d4409adcdd87a8c995cfef1322a8e827c52cae7a84020093cf'; Label = 'Accepted input map after authoring' }
    $state.input_unchanged = $true
    $state.output_bytes = ([System.IO.FileInfo]::new($OutputMap)).Length
    $state.output_sha256 = Get-Sha256 $OutputMap
    if ([string]$payload.output_sha256 -ne $state.output_sha256) { throw 'Output-map hash does not match receipt' }
    if ([int]$payload.actor_count_after -ne 140) { throw 'Output actor count is not 140' }
    if ([int]$payload.quality_metrics.uv_less_terrain_removed -ne 4) { throw 'UV-less terrain removal count is not four' }
    if ([int]$payload.quality_metrics.uv_mapped_beach_modules -ne 24) { throw 'UV-mapped beach module count is not twenty-four' }
    if ([int]$payload.quality_metrics.grounded_cross_streets -ne 15) { throw 'Grounded road count is not fifteen' }
    if ([int]$payload.quality_metrics.varied_building_instances -ne 27) { throw 'Varied building count is not twenty-seven' }
    if ([int]$payload.quality_metrics.matched_water_material_pair -ne 1 -or [int]$payload.quality_metrics.ocean_wave_bindings -ne 1) { throw 'Water correction metrics failed' }
    $combinedLog = ''
    foreach ($path in @($stdout, $stderr, $engineLog)) {
        if ([System.IO.File]::Exists($path)) { $combinedLog += [System.IO.File]::ReadAllText($path) + [Environment]::NewLine }
    }
    if ($combinedLog -match '(?im)Fatal error:|Unhandled Exception|Assertion failed|LogPython:\s*Error') { throw 'Fatal/error signature found in authoring logs' }
    $state.log_guard_passed = $true
    $state.classification = 'PASSED_READY_FOR_ENVIRONMENT_COMPOSITION_CORRECTION05_D3D12_VISUAL_PROOF'
    $state.stage = 'complete'
    $finalExit = 0
}
catch {
    $state.stage = 'failed'
    $state.failure = [ordered]@{
        type = $_.Exception.GetType().FullName
        message = $_.Exception.Message
        script_stack_trace = $_.ScriptStackTrace
    }
}
finally {
    $state.ended_utc = [DateTime]::UtcNow.ToString('o')
    try {
        Write-JsonAtomic $TerminalManifest $state
        if ([System.IO.Directory]::Exists($AttemptRoot)) { Write-JsonAtomic (Join-Path $AttemptRoot 'terminal.json') $state }
    }
    catch {
        try {
            $line = ([ordered]@{
                at_utc = [DateTime]::UtcNow.ToString('o')
                classification = 'FAILED_WITH_EVIDENCE'
                error = $_.Exception.Message
            } | ConvertTo-Json -Compress)
            [System.IO.File]::AppendAllText($EmergencyReceipt, $line + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
        } catch {}
        $finalExit = 1
    }
}

$state | ConvertTo-Json -Depth 80
[Environment]::Exit([int]$finalExit)
