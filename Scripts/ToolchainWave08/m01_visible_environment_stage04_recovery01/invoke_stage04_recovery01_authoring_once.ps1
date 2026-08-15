param(
    [switch]$OfflineContractTest,
    [switch]$AuthorizeSingleUnrealAuthoring
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Root = 'D:\Skyguard52'
$Project = 'D:\SG52T08_ENV01\Skyguard52.uproject'
$Editor = 'D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$InputMap = 'D:\SG52T08_ENV01\Content\M01\Lvl_M01_VisibleEnvironmentStage03.umap'
$OutputMap = 'D:\SG52T08_ENV01\Content\M01\Lvl_M01_VisibleEnvironmentStage04Recovery01.umap'
$Destination = 'D:\SG52T08_ENV01\Content\M01\VisibleEnvironmentStage04Recovery01'
$FailedDestination = 'D:\SG52T08_ENV01\Content\M01\VisibleEnvironmentStage04'
$FailedTerminal = Join-Path $Root 'Saved\Reports\M01_VISIBLE_ENVIRONMENT_STAGE04_AUTHORING01_TERMINAL_MANIFEST.json'
$StandingAuthorization = Join-Path $Root 'Production\standing_heavy_process_authorization.json'
$Author = Join-Path $Root 'Scripts\ToolchainWave08\m01_visible_environment_stage04_recovery01\author_m01_visible_environment_stage04_recovery01.py'
$Contract = Join-Path $Root 'Scripts\ToolchainWave08\m01_visible_environment_stage04_recovery01\stage04_recovery01_authoring_contract.json'
$AttemptRoot = Join-Path $Root 'Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_STAGE04_AUTHORING01_RECOVERY01\attempt_01'
$Receipt = Join-Path $AttemptRoot 'authoring_receipt.json'
$TerminalManifest = Join-Path $Root 'Saved\Reports\M01_VISIBLE_ENVIRONMENT_STAGE04_AUTHORING01_RECOVERY01_TERMINAL_MANIFEST.json'
$EmergencyReceipt = Join-Path $Root 'Saved\Reports\M01_VISIBLE_ENVIRONMENT_STAGE04_AUTHORING01_RECOVERY01_EMERGENCY_RECEIPT.jsonl'
$TimeoutSeconds = 1200

$Expected = @{
    Project = @{ Bytes = 3703; Sha256 = '7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a' }
    Editor = @{ Bytes = 512952; Sha256 = '0fb325cf215cc800ce260a1890af3f3dc314b8cc6331061d4e7e7246489af2e0' }
    InputMap = @{ Bytes = 911233; Sha256 = '28c3462ffe39b6fe753e2ba96761aa0e54d3aa947b41c1c9be4c760202980cad' }
    StandingAuthorization = @{ Bytes = 2146; Sha256 = '48277d7edd869cc2b841c3993e8f7599bec5291ddf23e9c442b33e09b870c089' }
    FailedTerminal = @{ Bytes = 5329; Sha256 = 'f56796e76c3c4d89c4ec4ce15124fb33f654e4aea11cc75c5f538c6d7152dbe8' }
    Author = @{ Bytes = 26199; Sha256 = 'd0b9e659cce94888e7edc07380721cdd163b41776fa97d2c0ab162c072277bfd' }
    Contract = @{ Bytes = 5456; Sha256 = '905285a4c18047b9366e2cdf7d51bc1c68fec2408d81431f49d5c10a51f01caa' }
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
    [System.IO.File]::WriteAllText($temporary, ($Payload | ConvertTo-Json -Depth 64) + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
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
    Assert-File $InputMap $Expected.InputMap.Bytes $Expected.InputMap.Sha256 'Immutable Stage03 map'
    Assert-File $StandingAuthorization $Expected.StandingAuthorization.Bytes $Expected.StandingAuthorization.Sha256 'Standing authorization'
    Assert-File $FailedTerminal $Expected.FailedTerminal.Bytes $Expected.FailedTerminal.Sha256 'Immutable failed Stage04 terminal'
    Assert-File $Author $Expected.Author.Bytes $Expected.Author.Sha256 'Recovery01 authoring source'
    Assert-File $Contract $Expected.Contract.Bytes $Expected.Contract.Sha256 'Recovery01 authoring contract'
    if (-not [System.IO.Directory]::Exists($FailedDestination)) { throw 'Immutable failed Stage04 destination is missing' }
    $standing = Get-Content -LiteralPath $StandingAuthorization -Raw | ConvertFrom-Json
    if ($standing.status -ne 'ACTIVE' -or $standing.execution_policy.per_run_user_authorization_required -ne $false) {
        throw 'Standing authorization is inactive or requires per-run approval'
    }
}

function Assert-Fresh {
    foreach ($path in @($OutputMap, $Destination, $AttemptRoot, $TerminalManifest, $EmergencyReceipt)) {
        if (Test-Path -LiteralPath $path) { throw "Fresh namespace already exists: $path" }
    }
}

if ($OfflineContractTest) {
    Assert-Authorities
    Assert-Fresh
    if (@(Get-HeavyProcesses).Count -ne 0) { throw 'Heavy process active during offline test' }
    & python $Author --offline-contract-test
    if ($LASTEXITCODE -ne 0) { throw "Python offline contract failed: $LASTEXITCODE" }
    [ordered]@{
        classification = 'PASSED_OFFLINE_CONTRACT_READY_FOR_SINGLE_STAGE04_RECOVERY01_UNREAL_AUTHORING'
        unreal_launch_count = 0
        governed_namespaces_created = 0
    } | ConvertTo-Json
    [Environment]::Exit([int]0)
}

$state = [ordered]@{
    schema = 'skyguard.m01-visible-environment-stage04-recovery01.authoring01.supervisor.v1'
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
    input_map_unchanged = $false
    failed_stage04_preserved = $false
    output_map = $null
    failure = $null
}

$finalExit = 1
try {
    if (-not $AuthorizeSingleUnrealAuthoring) { throw 'Mechanical -AuthorizeSingleUnrealAuthoring guard is required' }
    $state.stage = 'preflight'
    Assert-Authorities
    Assert-Fresh
    $heavy = @(Get-HeavyProcesses)
    if ($heavy.Count -ne 0) { throw "Heavy process active: $($heavy | ConvertTo-Json -Compress)" }

    [System.IO.Directory]::CreateDirectory($AttemptRoot) | Out-Null
    Copy-Item -LiteralPath $Author -Destination (Join-Path $AttemptRoot 'author_m01_visible_environment_stage04_recovery01.py')
    Copy-Item -LiteralPath $Contract -Destination (Join-Path $AttemptRoot 'stage04_recovery01_authoring_contract.json')
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
        throw "Unreal Stage04 Recovery01 authoring exceeded $TimeoutSeconds seconds"
    }
    $process.WaitForExit(); $process.Refresh()
    $state.exit_code = [int]$process.ExitCode
    $state.exit_code_type = $process.ExitCode.GetType().FullName
    if ($state.exit_code -ne 0) { throw "Unreal Stage04 Recovery01 authoring returned $($state.exit_code)" }
    if ($state.exit_code_type -ne 'System.Int32') { throw "Unexpected exit-code type: $($state.exit_code_type)" }
    if (-not [System.IO.File]::Exists($Receipt)) { throw "Recovery01 receipt missing: $Receipt" }

    $state.stage = 'receipt_validation'
    $payload = Get-Content -LiteralPath $Receipt -Raw | ConvertFrom-Json
    $state.receipt_classification = [string]$payload.classification
    if ($state.receipt_classification -ne 'PASSED_STAGE04_RECOVERY01_AUTHORING_AWAITING_GOVERNED_D3D12_VISUAL_PROOF') { throw "Receipt failed: $($state.receipt_classification)" }
    if (-not [System.IO.File]::Exists($OutputMap)) { throw 'Stage04 Recovery01 output map missing' }
    Assert-File $InputMap $Expected.InputMap.Bytes $Expected.InputMap.Sha256 'Stage03 map after Recovery01 authoring'
    Assert-File $FailedTerminal $Expected.FailedTerminal.Bytes $Expected.FailedTerminal.Sha256 'Failed Stage04 terminal after Recovery01 authoring'
    if (-not [System.IO.Directory]::Exists($FailedDestination)) { throw 'Failed Stage04 destination was removed' }
    $state.input_map_unchanged = $true
    $state.failed_stage04_preserved = $true
    $outputInfo = [System.IO.FileInfo]::new($OutputMap)
    $state.output_map = [ordered]@{ path = $OutputMap; bytes = $outputInfo.Length; sha256 = Get-Sha256 $OutputMap }
    $state.classification = 'PASSED_STAGE04_RECOVERY01_AUTHORING_AWAITING_GOVERNED_D3D12_VISUAL_PROOF'
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

$state | ConvertTo-Json -Depth 64
[Environment]::Exit([int]$finalExit)
