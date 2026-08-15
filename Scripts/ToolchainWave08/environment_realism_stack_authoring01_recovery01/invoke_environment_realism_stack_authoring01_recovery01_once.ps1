param(
    [switch]$AuthorizeSingleUnreal,
    [switch]$OfflineContractTest
)

$ErrorActionPreference = 'Stop'
$Root = 'D:\Skyguard52'
$Editor = 'D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$Project = 'D:\SG52T08_ENV01\Skyguard52.uproject'
$AuthoringScript = Join-Path $Root 'Scripts\ToolchainWave08\environment_realism_stack_authoring01_recovery01\author_environment_realism_stack01_recovery01.py'
$Contract = Join-Path $Root 'Docs\Toolchain\ToolchainWave08\M01EnvironmentRealismStackAuthoring01Recovery01\recovery_contract.json'
$AttemptRoot = Join-Path $Root 'Saved\BuildAttempts\M01_ENVIRONMENT_REALISM_STACK_AUTHORING01_RECOVERY01\attempt_01'
$Receipt = Join-Path $AttemptRoot 'authoring_receipt.json'
$TerminalManifest = Join-Path $Root 'Saved\Reports\M01_ENVIRONMENT_REALISM_STACK_AUTHORING01_RECOVERY01_TERMINAL_MANIFEST.json'
$EmergencyReceipt = Join-Path $Root 'Saved\Reports\M01_ENVIRONMENT_REALISM_STACK_AUTHORING01_RECOVERY01_EMERGENCY_RECEIPT.jsonl'
$InputMap = 'D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentAuthoring01_Recovery07.umap'
$OutputMap = 'D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentRealismStack01_Recovery01.umap'
$TimeoutSeconds = 900

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
    Assert-FileRecord $AuthoringScript 25592 '11a9853988228015ae295baf8335facb8481f8dd3a70393d301af4454556b605' 'Recovery01 authoring script'
    Assert-FileRecord $Contract 1569 'fb4e2489a835537d2f8bfe9e873b74bedf15b500a2be05f3e993f383f8b36832' 'Recovery01 contract'
    Assert-FileRecord (Join-Path $Root 'Docs\AAA_Review\M01_ENVIRONMENT_REALISM_STACK_AUTHORING01_ATTEMPT01_TERMINAL_FREEZE.json') 3322 '5a4d50cc7d292e941624764e9c3dbb69e4d85b73771a4409fc7206035d6b9e57' 'failed Attempt01 terminal freeze'
    Assert-FileRecord 'D:\UE_5.8\Engine\Source\Runtime\Engine\Classes\Components\ExponentialHeightFogComponent.h' 19831 '35381d9c97aaae5020409fe3fd98d65723b22be594ec5154e3a888fd78723669' 'UE 5.8 fog API header'
    Assert-FileRecord (Join-Path $Root 'Docs\AAA_Review\M01_LANDSCAPE_GROUNDING_BRIDGE01_RUNTIME_PROBE_RECOVERY02_ATTEMPT01_TERMINAL_FREEZE.json') 2874 '9a03a0162b521618d23e12c4fc84b84c0b2bf475c82864773da3201037a90a32' 'grounding bridge runtime acceptance'
    Assert-FileRecord $InputMap 625041 '401fb7a86321c05f977347185e41fd0ea0436ef7ec3d06d635935ad5f4ce702f' 'Recovery07 input map'
    Assert-FileRecord 'D:\SG52T08_ENV01\Binaries\Win64\UnrealEditor-Skyguard52.dll' 2937344 '2fdc9a755051df3472b409bab58eb5b152625ff9c1394d4c79c5701832529aa1' 'bound runtime DLL'
    Assert-FileRecord $Editor 512952 '0fb325cf215cc800ce260a1890af3f3dc314b8cc6331061d4e7e7246489af2e0' 'UnrealEditor-Cmd'
}

function Invoke-OfflineContractTest {
    $failures = @()
    try { Assert-NumericExitCode ([System.Int32]0) } catch { $failures += $_.Exception.Message }
    try { Assert-NumericExitCode $null; $failures += 'Null exit code was accepted.' } catch {}
    try { Assert-NumericExitCode '0'; $failures += 'String exit code was accepted.' } catch {}
    try { Assert-FrozenAuthorities } catch { $failures += $_.Exception.Message }
    try {
        $contractPayload = Get-Content -LiteralPath $Contract -Raw | ConvertFrom-Json
        if (-not $contractPayload.invariants.density_contract_unchanged -or -not $contractPayload.invariants.grounding_contract_unchanged) { $failures += 'Recovery invariants failed.' }
        if ($contractPayload.invariants.automatic_retries -ne 0) { $failures += 'Zero-retry contract failed.' }
    }
    catch { $failures += $_.Exception.Message }
    $temporaryRoot = Join-Path ([System.IO.Path]::GetTempPath()) ('skyguard-realism-authoring01-' + [Guid]::NewGuid().ToString('N'))
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
    schema = 'skyguard.m01-environment-realism-stack-authoring01-recovery01-supervisor.v1'
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
    peak_working_set_bytes = [int64]0
    receipt_classification = $null
    input_map_unchanged = $false
    output_map_bytes = $null
    output_map_sha256 = $null
    created_actor_count = $null
    grounding_record_count = $null
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
        "-ExecutePythonScript=$AuthoringScript",
        '-ScriptErrorsAreFatal',
        "-abslog=$engineLog"
    )
    $State.arguments = $arguments
    $State.stage = 'unreal_launch'
    $Process = Start-Process -FilePath $Editor -ArgumentList $arguments -WorkingDirectory 'D:\SG52T08_ENV01' -PassThru -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError $stderr
    $State.unreal_launch_count = 1
    $State.pid = $Process.Id
    $NativeHandle = $Process.Handle
    $State.native_handle_retained = ($NativeHandle -ne [IntPtr]::Zero)
    if (-not $State.native_handle_retained) { throw 'Failed to retain the native Unreal process handle.' }

    $State.stage = 'running'
    $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
    while (-not $Process.HasExited -and [DateTime]::UtcNow -lt $deadline) {
        $Process.Refresh()
        if ($Process.WorkingSet64 -gt $State.peak_working_set_bytes) { $State.peak_working_set_bytes = [int64]$Process.WorkingSet64 }
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
    $r = Get-Content -LiteralPath $Receipt -Raw | ConvertFrom-Json
    $State.receipt_classification = [string]$r.classification
    if ($State.receipt_classification -ne 'PASSED_M01_ENVIRONMENT_REALISM_STACK_AUTHORING01_RECOVERY01_AUTOMATIC') { throw "Unexpected receipt classification: $($State.receipt_classification)" }
    if ($r.input_sha256_before -ne '401fb7a86321c05f977347185e41fd0ea0436ef7ec3d06d635935ad5f4ce702f' -or $r.input_sha256_after -ne $r.input_sha256_before) { throw 'Input map parity failed.' }
    if (@($r.saved_assets).Count -ne 1 -or $r.saved_assets[0] -ne '/Game/ToolchainWave08/Environment/Lvl_M01_T08_EnvironmentRealismStack01_Recovery01') { throw 'Saved-asset allowlist failed.' }
    if (@($r.unexpected_assets).Count -ne 0) { throw 'Unexpected asset creation was reported.' }
    if (@($r.created_actor_labels).Count -ne 181) { throw "Created actor count mismatch: $(@($r.created_actor_labels).Count)" }
    if (@($r.grounding_records).Count -ne 175) { throw "Grounding record count mismatch: $(@($r.grounding_records).Count)" }
    if ($r.density_metrics.counts.building -ne 36 -or $r.density_metrics.counts.tree -ne 60 -or $r.density_metrics.counts.cross_street -ne 15) { throw 'Density receipt failed.' }
    if (-not $r.shore_contact.passed -or [math]::Abs([double]$r.shore_contact.beach_bottom_delta_cm - 65.0) -gt 1.0) { throw 'Shore-contact receipt failed.' }
    if ($r.post_process.auto_exposure_method -ne 'AEM_MANUAL') { throw 'Manual exposure receipt failed.' }
    if (-not [System.IO.File]::Exists($OutputMap)) { throw 'Output map is missing.' }
    Assert-FileRecord $InputMap 625041 '401fb7a86321c05f977347185e41fd0ea0436ef7ec3d06d635935ad5f4ce702f' 'Recovery07 input map after authoring'
    $State.input_map_unchanged = $true
    $outputItem = Get-Item -LiteralPath $OutputMap
    $State.output_map_bytes = [int64]$outputItem.Length
    $State.output_map_sha256 = Get-Sha256 $OutputMap
    if ($State.output_map_sha256 -ne $r.output_sha256) { throw 'Output map hash differs from the authoring receipt.' }
    $State.created_actor_count = @($r.created_actor_labels).Count
    $State.grounding_record_count = @($r.grounding_records).Count

    $State.stage = 'complete'
    $State.classification = 'PASSED_M01_ENVIRONMENT_REALISM_STACK_AUTHORING01_RECOVERY01_AUTOMATIC'
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
