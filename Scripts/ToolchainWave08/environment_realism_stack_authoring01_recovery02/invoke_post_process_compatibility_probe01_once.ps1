param(
    [switch]$AuthorizeSingleUnreal,
    [switch]$OfflineContractTest
)

$ErrorActionPreference = 'Stop'
$Root = 'D:\Skyguard52'
$Editor = 'D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$Project = 'D:\SG52T08_ENV01\Skyguard52.uproject'
$Probe = Join-Path $Root 'Scripts\ToolchainWave08\environment_realism_stack_authoring01_recovery02\post_process_compatibility_probe01.py'
$AttemptRoot = Join-Path $Root 'Saved\BuildAttempts\M01_ENVIRONMENT_REALISM_STACK_AUTHORING01_RECOVERY02_POST_PROCESS_COMPATIBILITY_PROBE01\attempt_01'
$Receipt = Join-Path $AttemptRoot 'probe_receipt.json'
$TerminalManifest = Join-Path $Root 'Saved\Reports\M01_ENVIRONMENT_REALISM_STACK_AUTHORING01_RECOVERY02_POST_PROCESS_COMPATIBILITY_PROBE01_TERMINAL_MANIFEST.json'
$EmergencyReceipt = Join-Path $Root 'Saved\Reports\M01_ENVIRONMENT_REALISM_STACK_AUTHORING01_RECOVERY02_POST_PROCESS_COMPATIBILITY_PROBE01_EMERGENCY_RECEIPT.jsonl'
$MapFile = 'D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentAuthoring01_Recovery07.umap'
$TimeoutSeconds = 300

function Get-Sha256([string]$Path) {
    $stream = $null
    $hasher = $null
    try {
        $stream = [System.IO.File]::Open($Path, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::Read)
        $hasher = [System.Security.Cryptography.SHA256]::Create()
        return ([System.BitConverter]::ToString($hasher.ComputeHash($stream))).Replace('-', '').ToLowerInvariant()
    }
    finally {
        if ($null -ne $hasher) { $hasher.Dispose() }
        if ($null -ne $stream) { $stream.Dispose() }
    }
}

function Assert-FileRecord([string]$Path, [int64]$Bytes, [string]$Sha256, [string]$Label) {
    if (-not [System.IO.File]::Exists($Path)) { throw "Missing $Label authority: $Path" }
    $item = Get-Item -LiteralPath $Path
    if ($item.Length -ne $Bytes) { throw "$Label byte mismatch: expected $Bytes, found $($item.Length)" }
    $actual = Get-Sha256 $Path
    if ($actual -ne $Sha256) { throw "$Label hash mismatch: expected $Sha256, found $actual" }
}

function Write-JsonAtomic([string]$Path, [object]$Value) {
    $parent = Split-Path -Parent $Path
    if (-not [System.IO.Directory]::Exists($parent)) { [System.IO.Directory]::CreateDirectory($parent) | Out-Null }
    $temporary = $Path + '.tmp'
    [System.IO.File]::WriteAllText($temporary, ($Value | ConvertTo-Json -Depth 20) + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
    [System.IO.File]::Move($temporary, $Path)
}

function Assert-NumericExitCode($Code) {
    if ($null -eq $Code) { throw 'Child process exit code is null.' }
    if ($Code -isnot [System.Int32]) { throw "Child process exit code type is $($Code.GetType().FullName), expected System.Int32." }
}

function Get-HeavyProcesses {
    @(Get-Process -ErrorAction SilentlyContinue | Where-Object {
        $_.ProcessName -match '^(UnrealEditor|UnrealEditor-Cmd|ShaderCompileWorker|AutomationTool|UnrealBuildTool|blender|cl|link|dotnet)$'
    } | Select-Object Id, ProcessName, StartTime)
}

function Assert-FrozenAuthorities {
    Assert-FileRecord $Probe 6414 '5bf2d31a9cccdbfbd55046a70b77311a231ffd68c273f3c0adaf5dea4f3d3102' 'post-process compatibility probe'
    Assert-FileRecord (Join-Path $Root 'Docs\AAA_Review\M01_ENVIRONMENT_REALISM_STACK_AUTHORING01_RECOVERY01_ATTEMPT01_TERMINAL_FREEZE.json') 2882 '31a65382d3124850f95926cc468be6bfba1f3c81c4f78070944996112ec182b9' 'Recovery01 terminal freeze'
    Assert-FileRecord $MapFile 625041 '401fb7a86321c05f977347185e41fd0ea0436ef7ec3d06d635935ad5f4ce702f' 'accepted input map'
    Assert-FileRecord 'D:\UE_5.8\Engine\Source\Runtime\Engine\Classes\Engine\PostProcessVolume.h' 4310 '2a5ea604f48f85e1424cdeb567453b4952bc878152349733af9a053592d0ea51' 'PostProcessVolume header'
    Assert-FileRecord 'D:\UE_5.8\Engine\Source\Runtime\Engine\Classes\Engine\Scene.h' 164040 'cd40d1a65e8635c2a561cc45786f5b588e3f3a119680c075a21dd89764c2591c' 'PostProcessSettings header'
    Assert-FileRecord $Editor 512952 '0fb325cf215cc800ce260a1890af3f3dc314b8cc6331061d4e7e7246489af2e0' 'UnrealEditor-Cmd'
    Assert-FileRecord (Join-Path $Root 'Production\standing_heavy_process_authorization.json') 2146 '48277d7edd869cc2b841c3993e8f7599bec5291ddf23e9c442b33e09b870c089' 'standing authorization'
}

function Invoke-OfflineContractTest {
    $failures = @()
    try { Assert-NumericExitCode ([System.Int32]0) } catch { $failures += $_.Exception.Message }
    try { Assert-NumericExitCode $null; $failures += 'Null exit code was accepted.' } catch {}
    try { Assert-NumericExitCode '0'; $failures += 'String exit code was accepted.' } catch {}
    try { Assert-FrozenAuthorities } catch { $failures += $_.Exception.Message }
    $temporaryRoot = Join-Path ([System.IO.Path]::GetTempPath()) ('skyguard-post-process-probe-' + [Guid]::NewGuid().ToString('N'))
    try {
        [System.IO.Directory]::CreateDirectory($temporaryRoot) | Out-Null
        $temporaryManifest = Join-Path $temporaryRoot 'terminal.json'
        Write-JsonAtomic $temporaryManifest ([ordered]@{ classification = 'OFFLINE_CONTRACT_TEST'; exit_code = [System.Int32]0 })
        $roundTrip = Get-Content -LiteralPath $temporaryManifest -Raw | ConvertFrom-Json
        if ($roundTrip.classification -ne 'OFFLINE_CONTRACT_TEST') { $failures += 'Terminal JSON round-trip failed.' }
    }
    catch { $failures += $_.Exception.Message }
    finally {
        if ([System.IO.Directory]::Exists($temporaryRoot)) { Remove-Item -LiteralPath $temporaryRoot -Recurse -Force }
    }
    if ([System.IO.Directory]::Exists($AttemptRoot)) { $failures += 'Offline test found governed attempt namespace.' }
    if ([System.IO.File]::Exists($TerminalManifest)) { $failures += 'Offline test found governed terminal manifest.' }
    if ($failures.Count -ne 0) {
        [Console]::Error.WriteLine(($failures -join [Environment]::NewLine))
        [Environment]::Exit([System.Int32]1)
    }
    [Console]::Out.WriteLine('PASS_OFFLINE_CONTRACT')
    [Environment]::Exit([System.Int32]0)
}

if ($OfflineContractTest) {
    if ($AuthorizeSingleUnreal) {
        [Console]::Error.WriteLine('Offline and authorized modes are mutually exclusive.')
        [Environment]::Exit([System.Int32]3)
    }
    Invoke-OfflineContractTest
}

$State = [ordered]@{
    schema = 'skyguard.m01-environment-realism-stack-authoring01-recovery02-post-process-compatibility-probe01-supervisor.v1'
    classification = 'FAILED_WITH_EVIDENCE'
    started_utc = [DateTime]::UtcNow.ToString('o')
    ended_utc = $null
    stage = 'initializing'
    authorization_present = [bool]$AuthorizeSingleUnreal
    preflight_passed = $false
    supervisor_launch_count = 1
    unreal_launch_count = 0
    retry_count = 0
    pid = $null
    native_handle_retained = $false
    process_samples = @()
    exit_code = $null
    exit_code_type = $null
    timeout = $false
    crash = $false
    receipt_classification = $null
    map_unchanged = $false
    world_saved = $null
    spawned_actor_destroyed = $null
    accepted_post_process_volume_property = $null
    failure = $null
    executable = $Editor
    arguments = @()
}

$FinalExitCode = [System.Int32]1
try {
    $State.stage = 'preflight'
    if (-not $AuthorizeSingleUnreal) { throw 'Mechanical -AuthorizeSingleUnreal guard is required.' }
    $standing = Get-Content -LiteralPath (Join-Path $Root 'Production\standing_heavy_process_authorization.json') -Raw | ConvertFrom-Json
    if ($standing.status -ne 'ACTIVE' -or $standing.execution_policy.per_run_user_authorization_required -ne $false) { throw 'Standing heavy-process authorization is inactive.' }
    Assert-FrozenAuthorities
    $heavy = @(Get-HeavyProcesses)
    if ($heavy.Count -ne 0) { throw "Governed heavy process is active: $($heavy | ConvertTo-Json -Compress)" }
    if ([System.IO.Directory]::Exists($AttemptRoot)) { throw "Attempt namespace already exists: $AttemptRoot" }
    if ([System.IO.File]::Exists($TerminalManifest)) { throw "Terminal manifest already exists: $TerminalManifest" }
    if ([System.IO.File]::Exists($EmergencyReceipt)) { throw "Emergency receipt already exists: $EmergencyReceipt" }

    $State.preflight_passed = $true
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
        "-ExecutePythonScript=$Probe", '-ScriptErrorsAreFatal', "-abslog=$engineLog"
    )
    $State.arguments = $arguments
    $State.stage = 'unreal_launch'
    $Process = Start-Process -FilePath $Editor -ArgumentList $arguments -WorkingDirectory 'D:\SG52T08_ENV01' -PassThru -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError $stderr
    $State.unreal_launch_count = 1
    $State.pid = $Process.Id
    $NativeHandle = $Process.Handle
    $State.native_handle_retained = ($NativeHandle -ne [IntPtr]::Zero)
    if (-not $State.native_handle_retained) { throw 'Failed to retain native Unreal process handle.' }

    $State.stage = 'running'
    $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
    while (-not $Process.HasExited -and [DateTime]::UtcNow -lt $deadline) {
        $Process.Refresh()
        $State.process_samples += [ordered]@{ at_utc = [DateTime]::UtcNow.ToString('o'); pid = $Process.Id; working_set_bytes = [int64]$Process.WorkingSet64 }
        Start-Sleep -Seconds 2
    }
    if (-not $Process.HasExited) {
        $State.timeout = $true
        Stop-Process -Id $Process.Id -Force -ErrorAction SilentlyContinue
        throw "Compatibility probe exceeded $TimeoutSeconds seconds."
    }
    $Process.WaitForExit()
    $Process.Refresh()
    $CapturedExitCode = $Process.ExitCode
    Assert-NumericExitCode $CapturedExitCode
    $State.exit_code = [System.Int32]$CapturedExitCode
    $State.exit_code_type = $CapturedExitCode.GetType().FullName
    if ($State.exit_code -ne 0) { throw "Compatibility probe returned exit code $($State.exit_code)." }
    if (-not [System.IO.File]::Exists($Receipt)) { throw "Compatibility probe receipt is missing: $Receipt" }

    $State.stage = 'receipt_validation'
    $payload = Get-Content -LiteralPath $Receipt -Raw | ConvertFrom-Json
    $State.receipt_classification = [string]$payload.classification
    $State.map_unchanged = [bool]$payload.map_unchanged
    $State.world_saved = [bool]$payload.world_saved
    $State.spawned_actor_destroyed = [bool]$payload.spawned_actor_destroyed
    $State.accepted_post_process_volume_property = [string]$payload.accepted_post_process_volume_property
    if ($State.receipt_classification -ne 'PASSED_POST_PROCESS_PYTHON_COMPATIBILITY_READY_FOR_AUTHORING_RECOVERY02') { throw "Unexpected receipt classification: $($State.receipt_classification)" }
    if (-not $State.map_unchanged -or $State.world_saved -or -not $State.spawned_actor_destroyed) { throw 'Read-only probe invariant failed.' }
    if ($State.accepted_post_process_volume_property -ne 'unbound') { throw 'Expected PostProcessVolume Python property unbound was not proven.' }
    if (@($payload.post_process_settings_properties | Where-Object { -not $_.supported }).Count -ne 0) { throw 'A required PostProcessSettings property failed runtime validation.' }
    Assert-FileRecord $MapFile 625041 '401fb7a86321c05f977347185e41fd0ea0436ef7ec3d06d635935ad5f4ce702f' 'accepted input map after probe'

    $State.stage = 'complete'
    $State.classification = 'PASSED_POST_PROCESS_PYTHON_COMPATIBILITY_READY_FOR_AUTHORING_RECOVERY02'
    $FinalExitCode = [System.Int32]0
}
catch {
    $State.failure = [ordered]@{ stage = $State.stage; message = $_.Exception.Message; type = $_.Exception.GetType().FullName; script_stack_trace = $_.ScriptStackTrace }
    $State.stage = 'failed'
    $FinalExitCode = [System.Int32]1
}
finally {
    $State.ended_utc = [DateTime]::UtcNow.ToString('o')
    try {
        Write-JsonAtomic $TerminalManifest $State
        if ([System.IO.Directory]::Exists($AttemptRoot)) { Write-JsonAtomic (Join-Path $AttemptRoot 'terminal.json') $State }
    }
    catch {
        try {
            $emergency = [ordered]@{ at_utc = [DateTime]::UtcNow.ToString('o'); classification = 'FAILED_WITH_EVIDENCE'; stage = $State.stage; pid = $State.pid; terminal_write_error = $_.Exception.Message } | ConvertTo-Json -Compress
            [System.IO.File]::AppendAllText($EmergencyReceipt, $emergency + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
        }
        catch {}
        $FinalExitCode = [System.Int32]1
    }
}

$State | ConvertTo-Json -Depth 20
[Environment]::Exit([System.Int32]$FinalExitCode)
