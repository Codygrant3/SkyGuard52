param(
    [switch]$AuthorizeSingleUnreal,
    [switch]$OfflineContractTest
)

$ErrorActionPreference = 'Stop'
$Root = 'D:\Skyguard52'
$Editor = 'D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$Project = 'D:\SG52T08_ENV01\Skyguard52.uproject'
$Authoring = Join-Path $Root 'Scripts\ToolchainWave08\environment_realism_stack_authoring02\author_environment_realism_stack02.py'
$AttemptRoot = Join-Path $Root 'Saved\BuildAttempts\M01_ENVIRONMENT_REALISM_STACK_AUTHORING02\attempt_01'
$Receipt = Join-Path $AttemptRoot 'authoring_receipt.json'
$TerminalManifest = Join-Path $Root 'Saved\Reports\M01_ENVIRONMENT_REALISM_STACK_AUTHORING02_TERMINAL_MANIFEST.json'
$EmergencyReceipt = Join-Path $Root 'Saved\Reports\M01_ENVIRONMENT_REALISM_STACK_AUTHORING02_EMERGENCY_RECEIPT.jsonl'
$InputMap = 'D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentRealismStack01_Recovery02.umap'
$OutputMap = 'D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentRealismStack02.umap'
$TimeoutSeconds = 600

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
    if ([System.IO.File]::Exists($temporary)) { throw "Temporary terminal path already exists: $temporary" }
    [System.IO.File]::WriteAllText($temporary, ($Value | ConvertTo-Json -Depth 30) + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
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
    Assert-FileRecord $Authoring 11473 '116adb907c97d125ed349f2aa2d5b703ec6df6418df77a5b81bbe8622c9016fb' 'Authoring02 source'
    Assert-FileRecord $InputMap 860203 '46a8ad9187c836329554d29716bd61ca4a2bc0f8bad7d64f66addc108e93e9d2' 'accepted input map'
    Assert-FileRecord (Join-Path $Root 'Docs\AAA_Review\M01_ENVIRONMENT_REALISM_STACK_VISUAL_PROOF01_ATTEMPT01_TERMINAL_FREEZE.json') 2676 '74dfeff2b346733258dd24206a23d7a8e83e9b2f44a6035e18212dfcf814fd00' 'failed visual-proof authority'
    Assert-FileRecord $Editor 512952 '0fb325cf215cc800ce260a1890af3f3dc314b8cc6331061d4e7e7246489af2e0' 'UnrealEditor-Cmd'
    Assert-FileRecord (Join-Path $Root 'Production\standing_heavy_process_authorization.json') 2146 '48277d7edd869cc2b841c3993e8f7599bec5291ddf23e9c442b33e09b870c089' 'standing authorization'
}

function Test-Near([double]$Actual, [double]$Expected, [double]$Tolerance = 0.001) {
    return [Math]::Abs($Actual - $Expected) -le $Tolerance
}

function Invoke-OfflineContractTest {
    $failures = @()
    try { Assert-NumericExitCode ([System.Int32]0) } catch { $failures += $_.Exception.Message }
    try { Assert-NumericExitCode $null; $failures += 'Null exit code was accepted.' } catch {}
    try { Assert-NumericExitCode '0'; $failures += 'String exit code was accepted.' } catch {}
    try { Assert-FrozenAuthorities } catch { $failures += $_.Exception.Message }
    $source = Get-Content -LiteralPath $Authoring -Raw
    foreach ($token in @('TARGET_LANDSCAPE_SCALE = (100.0, 150.0, 100.0)', 'TARGET_SUN_ROTATION = (-35.0, 75.0, 0.0)', 'TARGET_SKYLIGHT_INTENSITY = 2.0', 'len(result["regrounding_records"]) == 165', 'max(abs(row["gap_cm"])')) {
        if (-not $source.Contains($token)) { $failures += "Authoring source is missing token: $token" }
    }
    $temporaryRoot = Join-Path ([System.IO.Path]::GetTempPath()) ('skyguard-authoring02-' + [Guid]::NewGuid().ToString('N'))
    try {
        [System.IO.Directory]::CreateDirectory($temporaryRoot) | Out-Null
        $temporaryManifest = Join-Path $temporaryRoot 'terminal.json'
        Write-JsonAtomic $temporaryManifest ([ordered]@{ classification = 'OFFLINE_CONTRACT_TEST'; exit_code = [System.Int32]0 })
        $roundTrip = Get-Content -LiteralPath $temporaryManifest -Raw | ConvertFrom-Json
        if ($roundTrip.classification -ne 'OFFLINE_CONTRACT_TEST') { $failures += 'Terminal JSON round-trip failed.' }
    }
    catch { $failures += $_.Exception.Message }
    finally { if ([System.IO.Directory]::Exists($temporaryRoot)) { Remove-Item -LiteralPath $temporaryRoot -Recurse -Force } }
    if ([System.IO.Directory]::Exists($AttemptRoot)) { $failures += 'Governed attempt namespace exists.' }
    if ([System.IO.File]::Exists($OutputMap)) { $failures += 'Governed output map exists.' }
    if ([System.IO.File]::Exists($TerminalManifest)) { $failures += 'Governed terminal manifest exists.' }
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
    schema = 'skyguard.m01-environment-realism-stack-authoring02-supervisor.v1'
    classification = 'FAILED_WITH_EVIDENCE'
    started_utc = [DateTime]::UtcNow.ToString('o')
    ended_utc = $null
    stage = 'initializing'
    authorization_present = [bool]$AuthorizeSingleUnreal
    standing_authorization_verified = $false
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
    input_map_unchanged = $false
    output_map_bytes = $null
    output_map_sha256 = $null
    actor_count = $null
    regrounding_record_count = $null
    waterline_record_count = $null
    landscape_scale_after = $null
    lighting_after = $null
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
    $State.standing_authorization_verified = $true
    Assert-FrozenAuthorities
    $heavy = @(Get-HeavyProcesses)
    if ($heavy.Count -ne 0) { throw "Governed heavy process is active: $($heavy | ConvertTo-Json -Compress)" }
    if ([System.IO.Directory]::Exists($AttemptRoot)) { throw "Attempt namespace already exists: $AttemptRoot" }
    if ([System.IO.File]::Exists($OutputMap)) { throw "Output map already exists: $OutputMap" }
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
        "-ExecutePythonScript=$Authoring", '-ScriptErrorsAreFatal', "-abslog=$engineLog"
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
        throw "Environment authoring exceeded $TimeoutSeconds seconds."
    }
    $Process.WaitForExit()
    $Process.Refresh()
    $CapturedExitCode = $Process.ExitCode
    Assert-NumericExitCode $CapturedExitCode
    $State.exit_code = [System.Int32]$CapturedExitCode
    $State.exit_code_type = $CapturedExitCode.GetType().FullName
    if ($State.exit_code -ne 0) { throw "Environment authoring returned exit code $($State.exit_code)." }
    if (-not [System.IO.File]::Exists($Receipt)) { throw "Authoring receipt is missing: $Receipt" }

    $State.stage = 'receipt_validation'
    $payload = Get-Content -LiteralPath $Receipt -Raw | ConvertFrom-Json
    $State.receipt_classification = [string]$payload.classification
    $State.input_map_unchanged = ($payload.input_sha256_before -eq '46a8ad9187c836329554d29716bd61ca4a2bc0f8bad7d64f66addc108e93e9d2' -and $payload.input_sha256_after -eq $payload.input_sha256_before)
    $State.actor_count = [int]$payload.actor_count
    $State.regrounding_record_count = @($payload.regrounding_records).Count
    $State.waterline_record_count = @($payload.waterline_records).Count
    $State.landscape_scale_after = @($payload.landscape_scale_after)
    $State.lighting_after = $payload.lighting_after
    if ($State.receipt_classification -ne 'PASSED_M01_ENVIRONMENT_REALISM_STACK_AUTHORING02_AUTOMATIC') { throw "Unexpected receipt classification: $($State.receipt_classification)" }
    if (-not $State.input_map_unchanged) { throw 'Accepted input map changed.' }
    if ($State.actor_count -ne 186) { throw "Expected 186 actors, found $($State.actor_count)." }
    if ($State.regrounding_record_count -ne 165) { throw "Expected 165 re-grounded actors, found $($State.regrounding_record_count)." }
    if ($State.waterline_record_count -ne 10) { throw "Expected ten waterline records, found $($State.waterline_record_count)." }
    if ($State.landscape_scale_after.Count -ne 3 -or -not (Test-Near $State.landscape_scale_after[0] 100.0) -or -not (Test-Near $State.landscape_scale_after[1] 150.0) -or -not (Test-Near $State.landscape_scale_after[2] 100.0)) { throw 'Landscape scale contract failed.' }
    if (-not (Test-Near ([double]$State.lighting_after.sun_intensity) 10.0) -or -not (Test-Near ([double]$State.lighting_after.skylight_intensity) 2.0)) { throw 'Lighting intensity contract failed.' }
    if (@($payload.saved_assets).Count -ne 1 -or $payload.saved_assets[0] -ne '/Game/ToolchainWave08/Environment/Lvl_M01_T08_EnvironmentRealismStack02') { throw 'Saved-asset contract failed.' }
    if (-not [System.IO.File]::Exists($OutputMap)) { throw 'Authoring02 output map is missing.' }
    $State.output_map_bytes = (Get-Item -LiteralPath $OutputMap).Length
    $State.output_map_sha256 = Get-Sha256 $OutputMap
    if ($payload.output_sha256 -ne $State.output_map_sha256) { throw 'Output map hash does not match authoring receipt.' }
    Assert-FileRecord $InputMap 860203 '46a8ad9187c836329554d29716bd61ca4a2bc0f8bad7d64f66addc108e93e9d2' 'accepted input map after authoring'

    $State.stage = 'complete'
    $State.classification = 'PASSED_M01_ENVIRONMENT_REALISM_STACK_AUTHORING02_AUTOMATIC'
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

$State | ConvertTo-Json -Depth 30
[Environment]::Exit([System.Int32]$FinalExitCode)
