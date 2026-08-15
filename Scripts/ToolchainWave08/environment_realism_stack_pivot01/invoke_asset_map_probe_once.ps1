param(
    [switch]$AuthorizeSingleUnreal,
    [switch]$OfflineContractTest
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Project = 'D:\SG52T08_ENV01\Skyguard52.uproject'
$Editor = 'D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$Probe = 'D:\Skyguard52\Scripts\ToolchainWave08\environment_realism_stack_pivot01\probe_environment_realism_stack_pivot01.py'
$MapFile = 'D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentAuthoring01_Recovery07.umap'
$StandingAuthorization = 'D:\Skyguard52\Production\standing_heavy_process_authorization.json'
$AttemptRoot = 'D:\Skyguard52\Saved\BuildAttempts\M01_ENVIRONMENT_REALISM_STACK_PIVOT01_ASSET_PROBE\attempt_01'
$Receipt = Join-Path $AttemptRoot 'asset_map_probe_receipt.json'
$TerminalManifest = 'D:\Skyguard52\Saved\Reports\M01_ENVIRONMENT_REALISM_STACK_PIVOT01_ASSET_PROBE_TERMINAL_MANIFEST.json'
$EmergencyReceipt = 'D:\Skyguard52\Saved\Reports\M01_ENVIRONMENT_REALISM_STACK_PIVOT01_ASSET_PROBE_EMERGENCY_RECEIPT.jsonl'
$TimeoutSeconds = 1200

$Expected = @{
    Project = @{ Bytes = 3703; Sha256 = '7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a' }
    Editor = @{ Bytes = 512952; Sha256 = '0fb325cf215cc800ce260a1890af3f3dc314b8cc6331061d4e7e7246489af2e0' }
    Probe = @{ Bytes = 10601; Sha256 = 'b4c23815a353de49051d4ff7c639cf5afc5c14b728001112b6cd3b3c9610a4ad' }
    Map = @{ Bytes = 625041; Sha256 = '401fb7a86321c05f977347185e41fd0ea0436ef7ec3d06d635935ad5f4ce702f' }
    StandingAuthorization = @{ Bytes = 2146; Sha256 = '48277d7edd869cc2b841c3993e8f7599bec5291ddf23e9c442b33e09b870c089' }
}

function Get-Sha256([string]$Path) {
    $stream = [System.IO.File]::Open($Path, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::Read)
    $hasher = [System.Security.Cryptography.SHA256]::Create()
    try {
        return ([System.BitConverter]::ToString($hasher.ComputeHash($stream))).Replace('-', '').ToLowerInvariant()
    }
    finally {
        $hasher.Dispose()
        $stream.Dispose()
    }
}

function Assert-FileRecord([string]$Path, [int64]$Bytes, [string]$Sha256, [string]$Label) {
    if (-not [System.IO.File]::Exists($Path)) {
        throw "$Label is missing: $Path"
    }
    $info = [System.IO.FileInfo]::new($Path)
    if ($info.Length -ne $Bytes) {
        throw "$Label byte count mismatch: $($info.Length) != $Bytes"
    }
    $actual = Get-Sha256 $Path
    if ($actual -ne $Sha256) {
        throw "$Label SHA-256 mismatch: $actual != $Sha256"
    }
}

function Write-JsonAtomic([string]$Path, [object]$Payload) {
    $parent = [System.IO.Path]::GetDirectoryName($Path)
    [System.IO.Directory]::CreateDirectory($parent) | Out-Null
    $temporary = "$Path.tmp"
    $json = $Payload | ConvertTo-Json -Depth 20
    [System.IO.File]::WriteAllText($temporary, $json + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
    [System.IO.File]::Move($temporary, $Path)
}

function Get-HeavyProcesses {
    return @(
        Get-Process -ErrorAction SilentlyContinue |
            Where-Object { $_.ProcessName -match '^(UnrealEditor|UnrealEditor-Cmd|Blender|ShaderCompileWorker|AutomationTool|UnrealBuildTool|cl|link)$' } |
            Select-Object Id, ProcessName
    )
}

function Assert-FrozenAuthorities {
    Assert-FileRecord $Project $Expected.Project.Bytes $Expected.Project.Sha256 'Isolated project'
    Assert-FileRecord $Editor $Expected.Editor.Bytes $Expected.Editor.Sha256 'UE 5.8 editor'
    Assert-FileRecord $Probe $Expected.Probe.Bytes $Expected.Probe.Sha256 'Read-only probe'
    Assert-FileRecord $MapFile $Expected.Map.Bytes $Expected.Map.Sha256 'Recovery07 map'
    Assert-FileRecord $StandingAuthorization $Expected.StandingAuthorization.Bytes $Expected.StandingAuthorization.Sha256 'Standing authorization'
}

if ($AuthorizeSingleUnreal -and $OfflineContractTest) {
    [Console]::Error.WriteLine('Offline and authorized modes are mutually exclusive')
    [Environment]::Exit([int]3)
}

if ($OfflineContractTest) {
    Assert-FrozenAuthorities
    if ([System.IO.Directory]::Exists($AttemptRoot)) { throw "Future attempt already exists: $AttemptRoot" }
    if ([System.IO.File]::Exists($TerminalManifest)) { throw "Future terminal manifest already exists: $TerminalManifest" }
    if ([System.IO.File]::Exists($EmergencyReceipt)) { throw "Future emergency receipt already exists: $EmergencyReceipt" }
    $heavy = @(Get-HeavyProcesses)
    if ($heavy.Count -ne 0) { throw "Heavy process active during offline test: $($heavy | ConvertTo-Json -Compress)" }
    $source = [System.IO.File]::ReadAllText($Probe)
    foreach ($required in @('world_saved', 'map_unchanged', 'static_mesh_assets', 'material_assets', 'get_all_level_actors')) {
        if (-not $source.Contains($required)) { throw "Probe contract token missing: $required" }
    }
    [pscustomobject]@{
        classification = 'PASSED_M01_ENVIRONMENT_REALISM_STACK_PIVOT01_ASSET_PROBE_OFFLINE_CONTRACT'
        attempt_absent = $true
        terminal_absent = $true
        heavy_process_count = 0
        unreal_launch_count = 0
    } | ConvertTo-Json -Depth 4
    [Environment]::Exit([int]0)
}

if (-not $AuthorizeSingleUnreal) {
    [Console]::Error.WriteLine('Single Unreal probe authorization guard was not supplied')
    [Environment]::Exit([int]2)
}

$state = [ordered]@{
    schema = 'skyguard.m01-environment-realism-stack-pivot01.asset-probe-supervisor.v1'
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
    crash = $false
    peak_working_set_bytes = [int64]0
    process_samples = @()
    receipt_path = $Receipt
    receipt_classification = $null
    map_unchanged = $false
    world_saved = $null
    failure = $null
}

$exitCode = 1
try {
    $state.stage = 'preflight'
    Assert-FrozenAuthorities
    if ([System.IO.Directory]::Exists($AttemptRoot)) { throw "Attempt namespace already exists: $AttemptRoot" }
    if ([System.IO.File]::Exists($TerminalManifest)) { throw "Terminal manifest already exists: $TerminalManifest" }
    if ([System.IO.File]::Exists($EmergencyReceipt)) { throw "Emergency receipt already exists: $EmergencyReceipt" }
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
    if ($null -eq $handle) { throw 'Failed to retain the native process handle' }
    $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
    while (-not $process.HasExited -and [DateTime]::UtcNow -lt $deadline) {
        $process.Refresh()
        if ($process.WorkingSet64 -gt $state.peak_working_set_bytes) {
            $state.peak_working_set_bytes = [int64]$process.WorkingSet64
        }
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
        throw "Unreal dependency probe exceeded $TimeoutSeconds seconds"
    }
    $process.WaitForExit()
    $process.Refresh()
    $state.exit_code = [int]$process.ExitCode
    $state.exit_code_type = $process.ExitCode.GetType().FullName
    if ($state.exit_code -ne 0) { throw "Unreal dependency probe returned exit code $($state.exit_code)" }
    if ($state.exit_code_type -ne 'System.Int32') { throw "Unexpected exit-code type: $($state.exit_code_type)" }
    if (-not [System.IO.File]::Exists($Receipt)) { throw "Probe receipt is missing: $Receipt" }

    $state.stage = 'receipt_validation'
    $receiptPayload = Get-Content -LiteralPath $Receipt -Raw | ConvertFrom-Json
    $state.receipt_classification = [string]$receiptPayload.classification
    $state.map_unchanged = [bool]$receiptPayload.map_unchanged
    $state.world_saved = [bool]$receiptPayload.world_saved
    if ($state.receipt_classification -ne 'PASSED_READY_FOR_ENVIRONMENT_REALISM_STACK_PIVOT01_AUTHORING_DESIGN') {
        throw "Probe receipt classification failed: $($state.receipt_classification)"
    }
    if (-not $state.map_unchanged) { throw 'Recovery07 map changed during read-only probe' }
    if ($state.world_saved) { throw 'Read-only probe reported a world save' }
    Assert-FileRecord $MapFile $Expected.Map.Bytes $Expected.Map.Sha256 'Recovery07 map after probe'

    $state.classification = 'PASSED_READY_FOR_ENVIRONMENT_REALISM_STACK_PIVOT01_AUTHORING_DESIGN'
    $state.stage = 'complete'
    $exitCode = 0
}
catch {
    $state.failure = [ordered]@{
        type = $_.Exception.GetType().FullName
        message = $_.Exception.Message
        script_stack_trace = $_.ScriptStackTrace
    }
    $state.stage = 'failed'
    $exitCode = 1
}
finally {
    $state.ended_utc = [DateTime]::UtcNow.ToString('o')
    try {
        Write-JsonAtomic $TerminalManifest $state
        if ([System.IO.Directory]::Exists($AttemptRoot)) {
            Write-JsonAtomic (Join-Path $AttemptRoot 'terminal.json') $state
        }
    }
    catch {
        try {
            $emergency = [ordered]@{
                at_utc = [DateTime]::UtcNow.ToString('o')
                classification = 'FAILED_WITH_EVIDENCE'
                terminal_write_error = $_.Exception.Message
                stage = $state.stage
                pid = $state.pid
            } | ConvertTo-Json -Compress
            [System.IO.File]::AppendAllText($EmergencyReceipt, $emergency + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
        }
        catch {}
        $exitCode = 1
    }
}

$state | ConvertTo-Json -Depth 20
[Environment]::Exit([int]$exitCode)
