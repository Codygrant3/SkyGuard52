param([switch]$OfflineContractTest)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Project = 'D:\SG52T08_ENV01\Skyguard52.uproject'
$Editor = 'D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$InputMap = 'D:\SG52T08_ENV01\Content\M01\Lvl_M01_VisibleEnvironmentKit02_PresentationRefinement01_Recovery01.umap'
$OutputMap = 'D:\SG52T08_ENV01\Content\M01\Lvl_M01_PhotorealFoundation_NonVegetation01.umap'
$StandingAuthorization = 'D:\Skyguard52\Production\standing_heavy_process_authorization.json'
$Author = 'D:\Skyguard52\Scripts\ToolchainWave08\m01_photoreal_foundation_nonvegetation01\author_nonvegetation01.py'
$Verifier = 'D:\Skyguard52\Scripts\ToolchainWave08\m01_photoreal_foundation_nonvegetation01\verify_authoring_offline.py'
$Contract = 'D:\Skyguard52\Docs\Toolchain\ToolchainWave08\M01PhotorealFoundationNonVegetation01\quality_contract.json'
$ProbeTerminal = 'D:\Skyguard52\Saved\Reports\M01_PHOTOREAL_FOUNDATION_WAVE01_NONVEGETATION01_PROBE_TERMINAL_MANIFEST.json'
$ProbeReceipt = 'D:\Skyguard52\Saved\BuildAttempts\M01_PHOTOREAL_FOUNDATION_WAVE01_NONVEGETATION01_PROBE\attempt_01\probe_receipt.json'
$AttemptRoot = 'D:\Skyguard52\Saved\BuildAttempts\M01_PHOTOREAL_FOUNDATION_WAVE01_NONVEGETATION01_AUTHORING\attempt_01'
$Receipt = Join-Path $AttemptRoot 'authoring_receipt.json'
$TerminalManifest = 'D:\Skyguard52\Saved\Reports\M01_PHOTOREAL_FOUNDATION_WAVE01_NONVEGETATION01_AUTHORING_TERMINAL_MANIFEST.json'
$EmergencyReceipt = 'D:\Skyguard52\Saved\Reports\M01_PHOTOREAL_FOUNDATION_WAVE01_NONVEGETATION01_AUTHORING_EMERGENCY_RECEIPT.jsonl'
$TimeoutSeconds = 1200

$Expected = @{
    Project = @{ Bytes = 3703; Sha256 = '7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a' }
    Editor = @{ Bytes = 512952; Sha256 = '0fb325cf215cc800ce260a1890af3f3dc314b8cc6331061d4e7e7246489af2e0' }
    InputMap = @{ Bytes = 845823; Sha256 = '7ff5370b03b090c1111395e7873da9d8333c1063d3492d30c4e6e7a7006a3430' }
    StandingAuthorization = @{ Bytes = 2146; Sha256 = '48277d7edd869cc2b841c3993e8f7599bec5291ddf23e9c442b33e09b870c089' }
    Author = @{ Bytes = 20306; Sha256 = '8b0a5b88cb23bf0f402268d0679b17db4e68fec3a72ad3dc67e79320e60f1a2f' }
    Verifier = @{ Bytes = 1685; Sha256 = '2d83fd4ae1750e34fec769199ef793e5da12b19a52482db111ec1444a4d85e97' }
    Contract = @{ Bytes = 1542; Sha256 = '3aa5f27fb02433270287ec5a4d0c3242e97d31d724adfb32c91167c357a1b9a8' }
    ProbeTerminal = @{ Bytes = 9544; Sha256 = '0efcef67c523e122bd213ee6044103ff84200bf3aadffad29fc0abab32b0c076' }
    ProbeReceipt = @{ Bytes = 301213; Sha256 = '6605f68ac8be0fdb4e67cf7eecd462e4daafe3a2cc926d7d9451a4b1649f0d46' }
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
    [System.IO.File]::WriteAllText($temporary, ($Payload | ConvertTo-Json -Depth 24) + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
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
    Assert-File $ProbeTerminal $Expected.ProbeTerminal.Bytes $Expected.ProbeTerminal.Sha256 'Accepted probe terminal'
    Assert-File $ProbeReceipt $Expected.ProbeReceipt.Bytes $Expected.ProbeReceipt.Sha256 'Accepted probe receipt'
    $probe = Get-Content -LiteralPath $ProbeReceipt -Raw | ConvertFrom-Json
    if ($probe.classification -ne 'PASSED_READY_FOR_M01_NONVEGETATION01_AUTHORING' -or -not [bool]$probe.map_unchanged) {
        throw 'Accepted probe evidence is not ready for authoring'
    }
}

if ($OfflineContractTest) {
    Assert-Authorities
    if ([System.IO.Directory]::Exists($AttemptRoot)) { throw "Future attempt exists: $AttemptRoot" }
    if ([System.IO.File]::Exists($OutputMap)) { throw "Future output map exists: $OutputMap" }
    if ([System.IO.File]::Exists($TerminalManifest)) { throw "Future terminal exists: $TerminalManifest" }
    if (@(Get-HeavyProcesses).Count -ne 0) { throw 'Heavy process active during offline test' }
    $source = [System.IO.File]::ReadAllText($Author)
    foreach ($token in @('M01_RS01_Tree_', 'M_M01_Window', 'M_M01_Glass', 'M_ENV_Road_Marking', 'maximum_equal_spacing_repetition_per_row')) {
        if (-not $source.Contains($token)) { throw "Authoring token missing: $token" }
    }
    [pscustomobject]@{ classification = 'PASSED_OFFLINE_CONTRACT'; unreal_launch_count = 0; retries = 0; governed_namespaces_created = 0 } | ConvertTo-Json
    [Environment]::Exit([int]0)
}

$state = [ordered]@{
    schema = 'skyguard.m01-photoreal-foundation.nonvegetation01.authoring-supervisor.v1'
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
    if ($state.receipt_classification -ne 'PASSED_M01_PHOTOREAL_FOUNDATION_NONVEGETATION01_AUTOMATIC') { throw "Authoring receipt failed: $($state.receipt_classification)" }
    if (-not [System.IO.File]::Exists($OutputMap)) { throw "Output map missing: $OutputMap" }
    Assert-File $InputMap $Expected.InputMap.Bytes $Expected.InputMap.Sha256 'Accepted input map after authoring'
    $state.input_unchanged = $true
    $state.output_bytes = ([System.IO.FileInfo]::new($OutputMap)).Length
    $state.output_sha256 = Get-Sha256 $OutputMap
    if ($payload.output_sha256 -ne $state.output_sha256) { throw 'Output-map hash does not match authoring receipt' }
    if ([int]$payload.actor_count_after -ne 120) { throw 'Output actor count is not 120' }
    if ([int]$payload.quality_metrics.removed_rejected_tree_count -ne 60) { throw 'Rejected tree count did not reach 60' }
    if ([int]$payload.quality_metrics.city_dark_glass_usage -ne 0) { throw 'Dark city glass remains' }
    if ([int]$payload.quality_metrics.bright_road_marking_usage -ne 0) { throw 'Bright road markings remain' }
    if ([int]$payload.quality_metrics.maximum_equal_spacing_repetition_per_row -gt 2) { throw 'Equal-spacing repetition exceeds contract' }
    if ([double]$payload.quality_metrics.minimum_adjacent_building_aabb_gap_cm -lt 250.0) { throw 'Building gap is below contract' }
    $state.classification = 'PASSED_M01_PHOTOREAL_FOUNDATION_NONVEGETATION01_AUTOMATIC'
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

$state | ConvertTo-Json -Depth 24
[Environment]::Exit([int]$finalExit)
