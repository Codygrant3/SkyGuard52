param([switch]$OfflineContractTest)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Root = 'D:\Skyguard52'
$Project = 'D:\SG52T08_ENV01\Skyguard52.uproject'
$Editor = 'D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$MapFile = 'D:\SG52T08_ENV01\Content\M01\Lvl_M01_PhotorealFoundation_StructuralCleanup03.umap'
$StandingAuthorization = Join-Path $Root 'Production\standing_heavy_process_authorization.json'
$PriorFreeze = Join-Path $Root 'Docs\AAA_Review\M01_PHOTOREAL_FOUNDATION_WAVE01_STRUCTURAL_CLEANUP03_VISUAL_PROOF01_ATTEMPT01_TERMINAL_FREEZE.json'
$DirectReview = Join-Path $Root 'Docs\AAA_Review\M01_PHOTOREAL_FOUNDATION_WAVE01_STRUCTURAL_CLEANUP03_VISUAL_PROOF01_DIRECT_VISUAL_REVIEW.json'
$Probe = Join-Path $Root 'Scripts\ToolchainWave08\m01_photoreal_foundation_wave01_ground_lighting_probe04\probe_ground_lighting04.py'
$AttemptRoot = Join-Path $Root 'Saved\BuildAttempts\M01_PHOTOREAL_FOUNDATION_WAVE01_GROUND_LIGHTING_PROBE04\attempt_01'
$Receipt = Join-Path $AttemptRoot 'ground_lighting_probe_receipt.json'
$TerminalManifest = Join-Path $Root 'Saved\Reports\M01_PHOTOREAL_FOUNDATION_WAVE01_GROUND_LIGHTING_PROBE04_TERMINAL_MANIFEST.json'
$EmergencyReceipt = Join-Path $Root 'Saved\Reports\M01_PHOTOREAL_FOUNDATION_WAVE01_GROUND_LIGHTING_PROBE04_EMERGENCY_RECEIPT.jsonl'
$TimeoutSeconds = 1200

$Expected = @{
    Project = @{ Bytes = 3703; Sha256 = '7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a' }
    Editor = @{ Bytes = 512952; Sha256 = '0fb325cf215cc800ce260a1890af3f3dc314b8cc6331061d4e7e7246489af2e0' }
    Map = @{ Bytes = 738931; Sha256 = '142222c49c2ac232c301d14717a61c7a49c104df94ffeaa0e8ad21194184e08d' }
    StandingAuthorization = @{ Bytes = 2146; Sha256 = '48277d7edd869cc2b841c3993e8f7599bec5291ddf23e9c442b33e09b870c089' }
    PriorFreeze = @{ Bytes = 7976; Sha256 = '28d6532bd29bd5fab455ca897b0d2e9c32080d2a0a106c7230dd44bcafb9030c' }
    DirectReview = @{ Bytes = 5929; Sha256 = 'e0af33c01d3ba48c95438393626728be25b2b60e408d9ad553006595fcc1de5c' }
    Probe = @{ Bytes = 17424; Sha256 = '0121083c6c706698c20b99fe49c36b3e58e9b6a8e81c0d8804a8f6699064e17a' }
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
    [System.IO.File]::WriteAllText($temporary, ($Payload | ConvertTo-Json -Depth 32) + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
    [System.IO.File]::Move($temporary, $Path)
}

function Get-HeavyProcesses {
    return @(Get-Process -ErrorAction SilentlyContinue | Where-Object {
        $_.ProcessName -match '^(UnrealEditor|UnrealEditor-Cmd|Blender|ShaderCompileWorker|AutomationTool|UnrealBuildTool|cl|link)$'
    } | Select-Object Id, ProcessName)
}

function Assert-Authorities {
    Assert-File $Project $Expected.Project.Bytes $Expected.Project.Sha256 'Isolated project'
    Assert-File $Editor $Expected.Editor.Bytes $Expected.Editor.Sha256 'UE 5.8 editor'
    Assert-File $MapFile $Expected.Map.Bytes $Expected.Map.Sha256 'StructuralCleanup03 map'
    Assert-File $StandingAuthorization $Expected.StandingAuthorization.Bytes $Expected.StandingAuthorization.Sha256 'Standing authorization'
    Assert-File $PriorFreeze $Expected.PriorFreeze.Bytes $Expected.PriorFreeze.Sha256 'Prior terminal freeze'
    Assert-File $DirectReview $Expected.DirectReview.Bytes $Expected.DirectReview.Sha256 'Direct visual review'
    Assert-File $Probe $Expected.Probe.Bytes $Expected.Probe.Sha256 'Ground/lighting probe source'
    $standing = [System.IO.File]::ReadAllText($StandingAuthorization) | ConvertFrom-Json
    if ($standing.status -ne 'ACTIVE' -or $standing.execution_policy.per_run_user_authorization_required -ne $false) {
        throw 'Standing heavy-process authorization is inactive or requires per-run approval'
    }
}

if ($OfflineContractTest) {
    Assert-Authorities
    if ([System.IO.Directory]::Exists($AttemptRoot)) { throw "Future attempt exists: $AttemptRoot" }
    if ([System.IO.File]::Exists($TerminalManifest)) { throw "Future terminal exists: $TerminalManifest" }
    if ([System.IO.File]::Exists($EmergencyReceipt)) { throw "Future emergency receipt exists: $EmergencyReceipt" }
    if (@(Get-HeavyProcesses).Count -ne 0) { throw 'Heavy process active during offline contract test' }
    $source = [System.IO.File]::ReadAllText($Probe)
    foreach ($token in @('landscape_material', 'district_landscape_y_overlap_cm', 'texture_parameters', 'far_distance_material', 'map_unchanged')) {
        if (-not $source.Contains($token)) { throw "Probe token missing: $token" }
    }
    [pscustomobject]@{
        classification = 'PASSED_OFFLINE_READY_FOR_STANDING_AUTHORIZED_SINGLE_GROUND_LIGHTING_PROBE04'
        unreal_launch_count = 0
        governed_namespaces_created = 0
        standing_authorization = $true
    } | ConvertTo-Json
    [Environment]::Exit([int]0)
}

$state = [ordered]@{
    schema = 'skyguard.m01-photoreal-foundation.ground-lighting-probe04-supervisor.v1'
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
    standing_authorization = $true
    pid = $null
    exit_code = $null
    exit_code_type = $null
    timeout = $false
    peak_working_set_bytes = [int64]0
    process_samples = @()
    receipt_path = $Receipt
    receipt_classification = $null
    map_unchanged = $false
    failure = $null
}

$finalExit = 1
try {
    $state.stage = 'preflight'
    Assert-Authorities
    if ([System.IO.Directory]::Exists($AttemptRoot)) { throw "Attempt exists: $AttemptRoot" }
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
        '-Unattended',
        '-NoSplash',
        '-NoSound',
        '-NullRHI',
        '-NoSaveOnExit',
        '-stdout',
        '-FullStdOutLogOutput',
        '-nop4',
        '-DisablePlugins=Fab,Bridge,EditorTelemetry,RuntimeTelemetry,EOSShared',
        '-ini:EditorSettings:[/Script/UnrealEd.AnalyticsPrivacySettings]:bSendUsageData=False',
        "-ExecutePythonScript=$Probe",
        '-ScriptErrorsAreFatal',
        "-abslog=$engineLog"
    )
    $state.arguments = $arguments
    $state.stage = 'unreal_launch'
    $process = Start-Process -FilePath $Editor -ArgumentList $arguments -WorkingDirectory $state.working_directory -PassThru -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError $stderr
    $state.unreal_launch_count = 1
    $state.pid = $process.Id
    $handle = $process.Handle
    if ($null -eq $handle) { throw 'Failed to retain native Unreal process handle' }
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
        throw "Unreal ground/lighting probe exceeded $TimeoutSeconds seconds"
    }
    $process.WaitForExit()
    $process.Refresh()
    $state.exit_code = [int]$process.ExitCode
    $state.exit_code_type = $process.ExitCode.GetType().FullName
    if ($state.exit_code -ne 0) { throw "Unreal ground/lighting probe returned $($state.exit_code)" }
    if ($state.exit_code_type -ne 'System.Int32') { throw "Unexpected exit-code type: $($state.exit_code_type)" }
    if (-not [System.IO.File]::Exists($Receipt)) { throw "Ground/lighting probe receipt missing: $Receipt" }

    $state.stage = 'receipt_validation'
    $payload = [System.IO.File]::ReadAllText($Receipt) | ConvertFrom-Json
    $state.receipt_classification = [string]$payload.classification
    $state.map_unchanged = [bool]$payload.map_unchanged
    if ($state.receipt_classification -ne 'PASSED_READY_FOR_EVIDENCE_BACKED_GROUND_LIGHTING_CORRECTION04') {
        throw "Receipt failed: $($state.receipt_classification)"
    }
    if (-not $state.map_unchanged) { throw 'Ground/lighting probe changed StructuralCleanup03 map' }
    Assert-File $MapFile $Expected.Map.Bytes $Expected.Map.Sha256 'StructuralCleanup03 map after probe'
    $state.classification = 'PASSED_READY_FOR_EVIDENCE_BACKED_GROUND_LIGHTING_CORRECTION04'
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
        }
        catch {}
        $finalExit = 1
    }
}

$state | ConvertTo-Json -Depth 32
[Environment]::Exit([int]$finalExit)
