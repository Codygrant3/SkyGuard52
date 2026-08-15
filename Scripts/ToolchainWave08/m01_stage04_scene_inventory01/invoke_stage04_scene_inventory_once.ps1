param(
    [switch]$OfflineContractTest,
    [switch]$AuthorizeSingleReadOnlyProbe
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Project = 'D:\SG52T08_ENV01\Skyguard52.uproject'
$Editor = 'D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$MapFile = 'D:\SG52T08_ENV01\Content\M01\Lvl_M01_VisibleEnvironmentStage03.umap'
$StandingAuthorization = 'D:\Skyguard52\Production\standing_heavy_process_authorization.json'
$Probe = 'D:\Skyguard52\Scripts\ToolchainWave08\m01_stage04_scene_inventory01\probe_stage03_scene_inventory.py'
$Contract = 'D:\Skyguard52\Scripts\ToolchainWave08\m01_stage04_scene_inventory01\stage04_scene_inventory_contract.json'
$AttemptRoot = 'D:\Skyguard52\Saved\BuildAttempts\M01_STAGE04_SCENE_INVENTORY01\attempt_01'
$Receipt = Join-Path $AttemptRoot 'scene_inventory.json'
$TerminalManifest = 'D:\Skyguard52\Saved\Reports\M01_STAGE04_SCENE_INVENTORY01_TERMINAL_MANIFEST.json'
$EmergencyReceipt = 'D:\Skyguard52\Saved\Reports\M01_STAGE04_SCENE_INVENTORY01_EMERGENCY_RECEIPT.jsonl'
$TimeoutSeconds = 1200

$Expected = @{
    Project = @{ Bytes = 3703; Sha256 = '7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a' }
    Editor = @{ Bytes = 512952; Sha256 = '0fb325cf215cc800ce260a1890af3f3dc314b8cc6331061d4e7e7246489af2e0' }
    Map = @{ Bytes = 911233; Sha256 = '28c3462ffe39b6fe753e2ba96761aa0e54d3aa947b41c1c9be4c760202980cad' }
    StandingAuthorization = @{ Bytes = 2146; Sha256 = '48277d7edd869cc2b841c3993e8f7599bec5291ddf23e9c442b33e09b870c089' }
    Probe = @{ Bytes = 7256; Sha256 = '52b08aa5e9e4c459cbffd1736cfef8e034101db36979616253c542290bc7904e' }
    Contract = @{ Bytes = 1172; Sha256 = 'a0bf6fef52bbb1f9aed9cc8eb386d24b6bb5ac4c3211e45eed45783e0677a56a' }
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
    return @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {
        $_.Name -match '^(UnrealEditor(-Cmd)?|Blender|ShaderCompileWorker|AutomationTool|UnrealBuildTool|cl|link)(\.exe)?$'
    } | Select-Object ProcessId, Name, CommandLine)
}

function Assert-Authorities {
    Assert-File $Project $Expected.Project.Bytes $Expected.Project.Sha256 'Isolated project'
    Assert-File $Editor $Expected.Editor.Bytes $Expected.Editor.Sha256 'UE 5.8 editor'
    Assert-File $MapFile $Expected.Map.Bytes $Expected.Map.Sha256 'Immutable Stage03 map'
    Assert-File $StandingAuthorization $Expected.StandingAuthorization.Bytes $Expected.StandingAuthorization.Sha256 'Standing authorization'
    Assert-File $Probe $Expected.Probe.Bytes $Expected.Probe.Sha256 'Read-only inventory source'
    Assert-File $Contract $Expected.Contract.Bytes $Expected.Contract.Sha256 'Inventory contract'
    $standing = Get-Content -LiteralPath $StandingAuthorization -Raw | ConvertFrom-Json
    if ($standing.status -ne 'ACTIVE' -or $standing.execution_policy.per_run_user_authorization_required -ne $false) {
        throw 'Standing authorization is inactive or requires per-run approval'
    }
}

function Assert-Fresh {
    foreach ($path in @($AttemptRoot, $TerminalManifest, $EmergencyReceipt)) {
        if (Test-Path -LiteralPath $path) { throw "Fresh namespace already exists: $path" }
    }
}

if ($OfflineContractTest) {
    Assert-Authorities
    Assert-Fresh
    if (@(Get-HeavyProcesses).Count -ne 0) { throw 'Heavy process active during offline test' }
    $source = [System.IO.File]::ReadAllText($Probe)
    foreach ($token in @('read_only', 'world_saved', 'map_unchanged', 'stage04_role', 'actor_count', 'static_mesh')) {
        if (-not $source.Contains($token)) { throw "Probe token missing: $token" }
    }
    [ordered]@{
        classification = 'PASSED_OFFLINE_CONTRACT_READY_FOR_SINGLE_READ_ONLY_STAGE04_INVENTORY'
        unreal_launch_count = 0
        governed_namespaces_created = 0
    } | ConvertTo-Json
    [Environment]::Exit([int]0)
}

$state = [ordered]@{
    schema = 'skyguard.m01-stage04.scene-inventory01.supervisor.v1'
    classification = 'FAILED_WITH_EVIDENCE'
    started_at_utc = [DateTime]::UtcNow.ToString('o')
    completed_at_utc = $null
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
    map_unchanged = $false
    failure = $null
}

$finalExit = 1
try {
    if (-not $AuthorizeSingleReadOnlyProbe) { throw 'Mechanical -AuthorizeSingleReadOnlyProbe guard is required' }
    $state.stage = 'preflight'
    Assert-Authorities
    Assert-Fresh
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
        "-ExecutePythonScript=$Probe", '-ScriptErrorsAreFatal', "-abslog=$engineLog"
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
        throw "Unreal scene inventory exceeded $TimeoutSeconds seconds"
    }
    $process.WaitForExit(); $process.Refresh()
    $state.exit_code = [int]$process.ExitCode
    $state.exit_code_type = $process.ExitCode.GetType().FullName
    if ($state.exit_code -ne 0) { throw "Unreal scene inventory returned $($state.exit_code)" }
    if ($state.exit_code_type -ne 'System.Int32') { throw "Unexpected exit-code type: $($state.exit_code_type)" }
    if (-not [System.IO.File]::Exists($Receipt)) { throw "Scene inventory receipt missing: $Receipt" }

    $state.stage = 'receipt_validation'
    $payload = Get-Content -LiteralPath $Receipt -Raw | ConvertFrom-Json
    $state.receipt_classification = [string]$payload.classification
    $state.map_unchanged = [bool]$payload.map_unchanged
    if ($state.receipt_classification -ne 'PASSED_STAGE04_SCENE_INVENTORY_READY_FOR_FRESH_AUTHORING') { throw "Receipt failed: $($state.receipt_classification)" }
    if (-not $state.map_unchanged) { throw 'Read-only scene inventory changed Stage03 map' }
    Assert-File $MapFile $Expected.Map.Bytes $Expected.Map.Sha256 'Stage03 map after inventory'
    $state.classification = 'PASSED_STAGE04_SCENE_INVENTORY_READY_FOR_FRESH_AUTHORING'
    $state.stage = 'complete'
    $finalExit = 0
}
catch {
    $state.stage = 'failed'
    $state.failure = [ordered]@{ type = $_.Exception.GetType().FullName; message = $_.Exception.Message; script_stack_trace = $_.ScriptStackTrace }
}
finally {
    $state.completed_at_utc = [DateTime]::UtcNow.ToString('o')
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

$state | ConvertTo-Json -Depth 32
[Environment]::Exit([int]$finalExit)
