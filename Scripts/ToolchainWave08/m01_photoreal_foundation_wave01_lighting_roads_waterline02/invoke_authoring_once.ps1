param([switch]$OfflineContractTest)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Project = 'D:\SG52T08_ENV01\Skyguard52.uproject'
$Editor = 'D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$InputMap = 'D:\SG52T08_ENV01\Content\M01\Lvl_M01_PhotorealFoundation_NonVegetation01.umap'
$OutputMap = 'D:\SG52T08_ENV01\Content\M01\Lvl_M01_PhotorealFoundation_LightingRoadsWaterline02.umap'
$StandingAuthorization = 'D:\Skyguard52\Production\standing_heavy_process_authorization.json'
$Author = 'D:\Skyguard52\Scripts\ToolchainWave08\m01_photoreal_foundation_wave01_lighting_roads_waterline02\author_lighting_roads_waterline02.py'
$Verifier = 'D:\Skyguard52\Scripts\ToolchainWave08\m01_photoreal_foundation_wave01_lighting_roads_waterline02\verify_authoring_offline.py'
$Contract = 'D:\Skyguard52\Docs\Toolchain\ToolchainWave08\M01PhotorealFoundationLightingRoadsWaterline02\quality_contract.json'
$PropertyReceipt = 'D:\Skyguard52\Saved\BuildAttempts\M01_PHOTOREAL_FOUNDATION_WAVE01_LIGHTING_ROADS_WATERLINE02_PROPERTY_PROBE\attempt_01\property_probe_receipt.json'
$PropertyTerminal = 'D:\Skyguard52\Saved\Reports\M01_PHOTOREAL_FOUNDATION_WAVE01_LIGHTING_ROADS_WATERLINE02_PROPERTY_PROBE_TERMINAL_MANIFEST.json'
$AttemptRoot = 'D:\Skyguard52\Saved\BuildAttempts\M01_PHOTOREAL_FOUNDATION_WAVE01_LIGHTING_ROADS_WATERLINE02_AUTHORING\attempt_01'
$Receipt = Join-Path $AttemptRoot 'authoring_receipt.json'
$TerminalManifest = 'D:\Skyguard52\Saved\Reports\M01_PHOTOREAL_FOUNDATION_WAVE01_LIGHTING_ROADS_WATERLINE02_AUTHORING_TERMINAL_MANIFEST.json'
$EmergencyReceipt = 'D:\Skyguard52\Saved\Reports\M01_PHOTOREAL_FOUNDATION_WAVE01_LIGHTING_ROADS_WATERLINE02_AUTHORING_EMERGENCY_RECEIPT.jsonl'
$TimeoutSeconds = 1800

$Expected = @{
    Project = @{ Bytes = 3703; Sha256 = '7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a' }
    Editor = @{ Bytes = 512952; Sha256 = '0fb325cf215cc800ce260a1890af3f3dc314b8cc6331061d4e7e7246489af2e0' }
    InputMap = @{ Bytes = 736476; Sha256 = '618a260a905680cf5b17c1ac82a114a69f93f947334f45701cd1a8daa2b1f2a1' }
    StandingAuthorization = @{ Bytes = 2146; Sha256 = '48277d7edd869cc2b841c3993e8f7599bec5291ddf23e9c442b33e09b870c089' }
    Author = @{ Bytes = 15355; Sha256 = 'b3474a897bddf65e740eb7a5ebf150a60a565bf7cc7ec0cb7be83d3dbfd53fb8' }
    Verifier = @{ Bytes = 2490; Sha256 = '6a8529eb770f10e692d05484d670b67e4b33b7f51666e60614a0feae542e9208' }
    Contract = @{ Bytes = 1895; Sha256 = 'd25220d8fbecb79e53d009d6b26d478ff3f223aeb408989b9bf6542a55e247b3' }
    PropertyReceipt = @{ Bytes = 127770; Sha256 = '557b5b7abde8d12798318c531e5c14d6aec698a571a34485b0388485a17bb102' }
    PropertyTerminal = @{ Bytes = 3903; Sha256 = 'e69029db3ab4208f7889358296caeb09aa6579384dc71c3b5a1d5fa719f6b292' }
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
    [System.IO.File]::WriteAllText($temporary, ($Payload | ConvertTo-Json -Depth 30) + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
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
    Assert-File $InputMap $Expected.InputMap.Bytes $Expected.InputMap.Sha256 'Accepted input map'
    Assert-File $StandingAuthorization $Expected.StandingAuthorization.Bytes $Expected.StandingAuthorization.Sha256 'Standing authorization'
    Assert-File $Author $Expected.Author.Bytes $Expected.Author.Sha256 'Frozen author'
    Assert-File $Verifier $Expected.Verifier.Bytes $Expected.Verifier.Sha256 'Offline verifier'
    Assert-File $Contract $Expected.Contract.Bytes $Expected.Contract.Sha256 'Quality contract'
    Assert-File $PropertyReceipt $Expected.PropertyReceipt.Bytes $Expected.PropertyReceipt.Sha256 'Property receipt'
    Assert-File $PropertyTerminal $Expected.PropertyTerminal.Bytes $Expected.PropertyTerminal.Sha256 'Property terminal'
    $authorization = Get-Content -LiteralPath $StandingAuthorization -Raw | ConvertFrom-Json
    if ($authorization.status -ne 'ACTIVE' -or [bool]$authorization.execution_policy.per_run_user_authorization_required) { throw 'Standing heavy-process authorization is inactive' }
    $probe = Get-Content -LiteralPath $PropertyReceipt -Raw | ConvertFrom-Json
    if ($probe.classification -ne 'PASSED_READY_FOR_LIGHTING_ROADS_WATERLINE02_AUTHORING_DESIGN' -or -not [bool]$probe.map_unchanged) { throw 'Property probe is not accepted' }
}

if ($OfflineContractTest) {
    Assert-Authorities
    if ([System.IO.Directory]::Exists($AttemptRoot)) { throw "Future attempt exists: $AttemptRoot" }
    if ([System.IO.File]::Exists($OutputMap)) { throw "Future output exists: $OutputMap" }
    if ([System.IO.File]::Exists($TerminalManifest)) { throw "Future terminal exists: $TerminalManifest" }
    if (@(Get-HeavyProcesses).Count -ne 0) { throw 'Heavy process active during offline contract test' }
    $verifyOutput = & python $Verifier 2>&1
    if ($LASTEXITCODE -ne 0 -or ($verifyOutput -join "`n") -notmatch 'PASS') { throw "Offline verifier failed: $($verifyOutput -join ' ')" }
    [pscustomobject]@{ classification = 'PASSED_OFFLINE_CONTRACT'; unreal_launch_count = 0; retry_count = 0; governed_namespaces_created = 0 } | ConvertTo-Json
    [Environment]::Exit([int]0)
}

$state = [ordered]@{
    schema = 'skyguard.m01-photoreal-foundation.lighting-roads-waterline02.authoring-supervisor.v1'
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
    if ($state.receipt_classification -ne 'PASSED_M01_PHOTOREAL_FOUNDATION_LIGHTING_ROADS_WATERLINE02_AUTOMATIC') { throw "Authoring receipt failed: $($state.receipt_classification)" }
    if (-not [System.IO.File]::Exists($OutputMap)) { throw "Output map missing: $OutputMap" }
    Assert-File $InputMap $Expected.InputMap.Bytes $Expected.InputMap.Sha256 'Accepted input map after authoring'
    $state.input_unchanged = $true
    $state.output_bytes = ([System.IO.FileInfo]::new($OutputMap)).Length
    $state.output_sha256 = Get-Sha256 $OutputMap
    if ($payload.output_sha256 -ne $state.output_sha256) { throw 'Output-map hash does not match receipt' }
    if ([int]$payload.actor_count_after -ne 120) { throw 'Output actor count is not 120' }
    if ([int]$payload.quality_metrics.cross_street_dark_concrete_overrides -ne 15) { throw 'CrossStreet correction count is not 15' }
    if ([int]$payload.quality_metrics.district_sand_bindings -ne 4) { throw 'Terrain sand binding count is not four' }
    if ([int]$payload.quality_metrics.proxy_tree_count -ne 0) { throw 'Rejected proxy trees returned' }
    $state.classification = 'PASSED_M01_PHOTOREAL_FOUNDATION_LIGHTING_ROADS_WATERLINE02_AUTOMATIC'
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

$state | ConvertTo-Json -Depth 30
[Environment]::Exit([int]$finalExit)
