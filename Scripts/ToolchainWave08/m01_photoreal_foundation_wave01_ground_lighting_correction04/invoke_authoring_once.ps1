param([switch]$OfflineContractTest)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Project = 'D:\SG52T08_ENV01\Skyguard52.uproject'
$Editor = 'D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$InputMap = 'D:\SG52T08_ENV01\Content\M01\Lvl_M01_PhotorealFoundation_StructuralCleanup03.umap'
$OutputMap = 'D:\SG52T08_ENV01\Content\M01\Lvl_M01_PhotorealFoundation_GroundLightingCorrection04.umap'
$MaterialDirectory = 'D:\SG52T08_ENV01\Content\M01\GroundLightingCorrection04'
$StandingAuthorization = 'D:\Skyguard52\Production\standing_heavy_process_authorization.json'
$ProbeFreeze = 'D:\Skyguard52\Docs\AAA_Review\M01_PHOTOREAL_FOUNDATION_WAVE01_GROUND_LIGHTING_PROBE04_TERMINAL_FREEZE.json'
$ProbeAdjudication = 'D:\Skyguard52\Docs\AAA_Review\M01_PHOTOREAL_FOUNDATION_WAVE01_GROUND_LIGHTING_PROBE04_ADJUDICATION.json'
$Author = 'D:\Skyguard52\Scripts\ToolchainWave08\m01_photoreal_foundation_wave01_ground_lighting_correction04\author_ground_lighting_correction04.py'
$Verifier = 'D:\Skyguard52\Scripts\ToolchainWave08\m01_photoreal_foundation_wave01_ground_lighting_correction04\verify_authoring_offline.py'
$Contract = 'D:\Skyguard52\Docs\Toolchain\ToolchainWave08\M01PhotorealFoundationGroundLightingCorrection04\quality_contract.json'
$AttemptRoot = 'D:\Skyguard52\Saved\BuildAttempts\M01_PHOTOREAL_FOUNDATION_WAVE01_GROUND_LIGHTING_CORRECTION04_AUTHORING\attempt_01'
$Receipt = Join-Path $AttemptRoot 'authoring_receipt.json'
$TerminalManifest = 'D:\Skyguard52\Saved\Reports\M01_PHOTOREAL_FOUNDATION_WAVE01_GROUND_LIGHTING_CORRECTION04_AUTHORING_TERMINAL_MANIFEST.json'
$EmergencyReceipt = 'D:\Skyguard52\Saved\Reports\M01_PHOTOREAL_FOUNDATION_WAVE01_GROUND_LIGHTING_CORRECTION04_AUTHORING_EMERGENCY_RECEIPT.jsonl'
$TimeoutSeconds = 1800

$Expected = @{
    Project = @{ Path = $Project; Bytes = 3703; Sha256 = '7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a' }
    Editor = @{ Path = $Editor; Bytes = 512952; Sha256 = '0fb325cf215cc800ce260a1890af3f3dc314b8cc6331061d4e7e7246489af2e0' }
    InputMap = @{ Path = $InputMap; Bytes = 738931; Sha256 = '142222c49c2ac232c301d14717a61c7a49c104df94ffeaa0e8ad21194184e08d' }
    StandingAuthorization = @{ Path = $StandingAuthorization; Bytes = 2146; Sha256 = '48277d7edd869cc2b841c3993e8f7599bec5291ddf23e9c442b33e09b870c089' }
    ProbeFreeze = @{ Path = $ProbeFreeze; Bytes = 2348; Sha256 = '783c7f99ded4602bf37681d5e8c6849bb8beddcbd82e05687b774da02af07dbe' }
    ProbeAdjudication = @{ Path = $ProbeAdjudication; Bytes = 3773; Sha256 = '09aad176ace5294d056a674fec30730c23262e053f1e9548141cefdc8d3e3635' }
    Author = @{ Path = $Author; Bytes = 20684; Sha256 = 'eba032612dd1ee9de55560b1fef1ec8f88fdf608d96121ef3d1c08132ce818b3' }
    Verifier = @{ Path = $Verifier; Bytes = 3211; Sha256 = 'd3d84f7022d5e1ccc1b24b42eb268f12f1103660daf9140d21878acf95177b5b' }
    Contract = @{ Path = $Contract; Bytes = 2359; Sha256 = '29910c55f5922c03bfcc59165b53c64e206047e5479fd2364be9a89751a04a1c' }
    SandSource = @{ Path = 'D:\SG52T08_ENV01\Content\M01\EnvKit02\M01_COASTAL_DISTRICT_A\Materials\M_ENV_Sand_Coast_2K.uasset'; Bytes = 75214; Sha256 = 'c89452560026d4267a27056083f6669b565b7861d91806fb0dbf27de78bfe53d' }
    PaversSource = @{ Path = 'D:\SG52T08_ENV01\Content\M01\EnvKit02\M01_COASTAL_DISTRICT_A\Materials\M_ENV_Concrete_Pavers_2K.uasset'; Bytes = 75509; Sha256 = 'c8935ce61c95610cbe6473f87fdedf5ec48bc1a0a99120acc55c3c4d7144b1c1' }
    WindowSource = @{ Path = 'D:\SG52T08_ENV01\Content\Skyguard\Meshes\Mission01\Wave1Refinement\m01_wave1_aaa_refinement\Materials\M_M01_Window.uasset'; Bytes = 64861; Sha256 = 'e7d28a85d9e4c09f1e431dcb87c71addcf2dbec1080a0b1a6560418882c26523' }
    GlassSource = @{ Path = 'D:\SG52T08_ENV01\Content\Skyguard\Meshes\Mission01\Wave1Refinement\m01_wave1_aaa_refinement\Materials\M_M01_Glass.uasset'; Bytes = 64846; Sha256 = '90337306075f726504461f4ac4ffb58dcd34f9e54d6c86933b766bc5a7fa312f' }
    FarWaterSource = @{ Path = 'D:\UE_5.8\Engine\Plugins\Experimental\Water\Content\Materials\WaterSurface\Water_FarMesh.uasset'; Bytes = 12296; Sha256 = 'ccfcf0df2bd5bf9db9cc1e9b7d2394dff546e8faad78f7e999e69102aaf77d6d' }
}

function Get-Sha256([string]$Path) {
    $stream = [System.IO.File]::Open($Path, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::Read)
    $hasher = [System.Security.Cryptography.SHA256]::Create()
    try { return ([System.BitConverter]::ToString($hasher.ComputeHash($stream))).Replace('-', '').ToLowerInvariant() }
    finally { $hasher.Dispose(); $stream.Dispose() }
}

function Assert-File([string]$Path, [int64]$Bytes, [string]$Sha256, [string]$Label) {
    if (-not [System.IO.File]::Exists($Path)) { throw "$Label missing: $Path" }
    $info = [System.IO.FileInfo]::new($Path)
    if ($info.Length -ne $Bytes) { throw "$Label byte mismatch: $($info.Length) != $Bytes" }
    $actual = Get-Sha256 $Path
    if ($actual -ne $Sha256) { throw "$Label hash mismatch: $actual != $Sha256" }
}

function Write-JsonAtomic([string]$Path, [object]$Payload) {
    [System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName($Path)) | Out-Null
    $temporary = "$Path.tmp"
    [System.IO.File]::WriteAllText($temporary, ($Payload | ConvertTo-Json -Depth 60) + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
    [System.IO.File]::Move($temporary, $Path)
}

function Get-HeavyProcesses {
    return @(Get-Process -ErrorAction SilentlyContinue | Where-Object {
        $_.ProcessName -match '^(UnrealEditor|UnrealEditor-Cmd|Blender|ShaderCompileWorker|AutomationTool|UnrealBuildTool|cl|link)$'
    } | Select-Object Id, ProcessName)
}

function Assert-Authorities {
    foreach ($name in $Expected.Keys) {
        $row = $Expected[$name]
        Assert-File $row.Path $row.Bytes $row.Sha256 $name
    }
    $authorization = Get-Content -LiteralPath $StandingAuthorization -Raw | ConvertFrom-Json
    if ($authorization.status -ne 'ACTIVE' -or [bool]$authorization.execution_policy.per_run_user_authorization_required) { throw 'Standing heavy-process authorization is inactive' }
    $adjudication = Get-Content -LiteralPath $ProbeAdjudication -Raw | ConvertFrom-Json
    if ($adjudication.classification -ne 'PASSED_READY_FOR_EVIDENCE_BACKED_GROUND_LIGHTING_CORRECTION04') { throw 'Probe adjudication does not authorize GroundLightingCorrection04' }
}

if ($OfflineContractTest) {
    Assert-Authorities
    if ([System.IO.Directory]::Exists($AttemptRoot)) { throw "Future attempt exists: $AttemptRoot" }
    if ([System.IO.File]::Exists($OutputMap)) { throw "Future output exists: $OutputMap" }
    if ([System.IO.Directory]::Exists($MaterialDirectory)) { throw "Future material directory exists: $MaterialDirectory" }
    if ([System.IO.File]::Exists($TerminalManifest)) { throw "Future terminal exists: $TerminalManifest" }
    if ([System.IO.File]::Exists($EmergencyReceipt)) { throw "Future emergency receipt exists: $EmergencyReceipt" }
    if (@(Get-HeavyProcesses).Count -ne 0) { throw 'Heavy process active during offline contract test' }
    $verifyOutput = & python $Verifier 2>&1
    if ($LASTEXITCODE -ne 0 -or ($verifyOutput -join "`n") -notmatch 'PASS') { throw "Offline verifier failed: $($verifyOutput -join ' ')" }
    [pscustomobject]@{ classification = 'PASSED_OFFLINE_CONTRACT'; unreal_launch_count = 0; retry_count = 0; governed_namespaces_created = 0 } | ConvertTo-Json
    [Environment]::Exit([int]0)
}

$state = [ordered]@{
    schema = 'skyguard.m01-photoreal-foundation.ground-lighting-correction04.authoring-supervisor.v1'
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
    created_materials = @()
    quality_metrics = $null
    input_unchanged = $false
    failure = $null
}

$finalExit = 1
try {
    $state.stage = 'preflight'
    Assert-Authorities
    if ([System.IO.Directory]::Exists($AttemptRoot)) { throw "Attempt exists: $AttemptRoot" }
    if ([System.IO.File]::Exists($OutputMap)) { throw "Output map exists: $OutputMap" }
    if ([System.IO.Directory]::Exists($MaterialDirectory)) { throw "Material directory exists: $MaterialDirectory" }
    if ([System.IO.File]::Exists($TerminalManifest)) { throw "Terminal exists: $TerminalManifest" }
    if ([System.IO.File]::Exists($EmergencyReceipt)) { throw "Emergency receipt exists: $EmergencyReceipt" }
    $heavy = @(Get-HeavyProcesses)
    if ($heavy.Count -ne 0) { throw "Heavy process active: $($heavy | ConvertTo-Json -Compress)" }

    [System.IO.Directory]::CreateDirectory($AttemptRoot) | Out-Null
    $stdout = Join-Path $AttemptRoot 'unreal.stdout.log'
    $stderr = Join-Path $AttemptRoot 'unreal.stderr.log'
    $engineLog = Join-Path $AttemptRoot 'unreal.engine.log'
    $arguments = @(
        $Project, '-Unattended', '-NoSplash', '-NoSound', '-NullRHI', '-NoSaveOnExit',
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
        $state.process_samples += [ordered]@{ at_utc = [DateTime]::UtcNow.ToString('o'); pid = $process.Id; working_set_bytes = [int64]$process.WorkingSet64 }
        Start-Sleep -Seconds 2
    }
    if (-not $process.HasExited) {
        $state.timeout = $true
        Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        throw "Unreal authoring exceeded $TimeoutSeconds seconds"
    }
    $process.WaitForExit(); $process.Refresh()
    $state.exit_code = [int]$process.ExitCode
    $state.exit_code_type = $process.ExitCode.GetType().FullName
    if ($state.exit_code -ne 0) { throw "Unreal authoring returned $($state.exit_code)" }
    if ($state.exit_code_type -ne 'System.Int32') { throw "Unexpected exit-code type: $($state.exit_code_type)" }
    if (-not [System.IO.File]::Exists($Receipt)) { throw "Authoring receipt missing: $Receipt" }

    $state.stage = 'postflight'
    $payload = Get-Content -LiteralPath $Receipt -Raw | ConvertFrom-Json
    $state.receipt_classification = [string]$payload.classification
    $state.quality_metrics = $payload.quality_metrics
    if ($state.receipt_classification -ne 'PASSED_M01_PHOTOREAL_FOUNDATION_GROUND_LIGHTING_CORRECTION04_AUTOMATIC') { throw "Authoring receipt failed: $($state.receipt_classification)" }
    if (-not [System.IO.File]::Exists($OutputMap)) { throw "Output map missing: $OutputMap" }
    Assert-File $InputMap $Expected.InputMap.Bytes $Expected.InputMap.Sha256 'Accepted input map after authoring'
    $state.input_unchanged = $true
    $state.output_bytes = ([System.IO.FileInfo]::new($OutputMap)).Length
    $state.output_sha256 = Get-Sha256 $OutputMap
    if ($payload.output_sha256 -ne $state.output_sha256) { throw 'Output-map hash does not match receipt' }
    if ([int]$payload.actor_count_after -ne 120) { throw 'Output actor count is not 120' }
    if ([int]$payload.quality_metrics.created_material_count -ne 5) { throw 'Created material count is not five' }
    if ([int]$payload.quality_metrics.tiled_beach_bindings -ne 4) { throw 'Beach binding count is not four' }
    if ([int]$payload.quality_metrics.lifted_glazing_actor_count -ne 27) { throw 'Glazing binding count is not 27' }
    if ([int]$payload.quality_metrics.transforms_preserved -ne 120) { throw 'Transform preservation count is not 120' }
    if (-not [System.IO.Directory]::Exists($MaterialDirectory)) { throw 'Created material directory is missing' }
    $materialFiles = @(Get-ChildItem -LiteralPath $MaterialDirectory -Recurse -File -Filter '*.uasset' | Sort-Object FullName)
    if ($materialFiles.Count -ne 5) { throw "Expected five material assets; found $($materialFiles.Count)" }
    $state.created_materials = @($materialFiles | ForEach-Object { [ordered]@{ path = $_.FullName; bytes = $_.Length; sha256 = Get-Sha256 $_.FullName } })
    foreach ($row in @($payload.created_materials)) {
        $match = @($state.created_materials | Where-Object { $_.path -eq [string]$row.file })
        if ($match.Count -ne 1 -or $match[0].bytes -ne [int64]$row.bytes -or $match[0].sha256 -ne [string]$row.sha256) { throw "Material receipt mismatch: $($row.file)" }
    }
    $state.classification = 'PASSED_READY_FOR_GROUND_LIGHTING_CORRECTION04_D3D12_VISUAL_PROOF'
    $state.stage = 'complete'
    $finalExit = 0
}
catch {
    $state.stage = 'failed'
    $state.failure = [ordered]@{ type = $_.Exception.GetType().FullName; message = $_.Exception.Message; script_stack_trace = $_.ScriptStackTrace }
}
finally {
    $state.ended_utc = [DateTime]::UtcNow.ToString('o')
    try {
        Write-JsonAtomic $TerminalManifest $state
        if ([System.IO.Directory]::Exists($AttemptRoot)) { Write-JsonAtomic (Join-Path $AttemptRoot 'terminal.json') $state }
    }
    catch {
        try {
            $line = ([ordered]@{ at_utc = [DateTime]::UtcNow.ToString('o'); classification = 'FAILED_WITH_EVIDENCE'; error = $_.Exception.Message } | ConvertTo-Json -Compress)
            [System.IO.File]::AppendAllText($EmergencyReceipt, $line + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
        } catch {}
        $finalExit = 1
    }
}

$state | ConvertTo-Json -Depth 60
[Environment]::Exit([int]$finalExit)
