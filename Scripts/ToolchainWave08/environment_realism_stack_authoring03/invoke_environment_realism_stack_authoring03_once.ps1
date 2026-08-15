param([switch]$AuthorizeSingleUnreal, [switch]$OfflineContractTest)

$ErrorActionPreference = 'Stop'
$Root = 'D:\Skyguard52'
$Editor = 'D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$Project = 'D:\SG52T08_ENV01\Skyguard52.uproject'
$Authoring = Join-Path $Root 'Scripts\ToolchainWave08\environment_realism_stack_authoring03\author_environment_realism_stack03.py'
$Attempt = Join-Path $Root 'Saved\BuildAttempts\M01_ENVIRONMENT_REALISM_STACK_AUTHORING03\attempt_01'
$Receipt = Join-Path $Attempt 'authoring_receipt.json'
$Terminal = Join-Path $Root 'Saved\Reports\M01_ENVIRONMENT_REALISM_STACK_AUTHORING03_TERMINAL_MANIFEST.json'
$Emergency = Join-Path $Root 'Saved\Reports\M01_ENVIRONMENT_REALISM_STACK_AUTHORING03_EMERGENCY_RECEIPT.jsonl'
$InputMap = 'D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentRealismStack01_Recovery02.umap'
$OutputMap = 'D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentRealismStack03.umap'
$TimeoutSeconds = 600

function Get-Sha256([string]$Path) {
    $stream = $null; $hasher = $null
    try {
        $stream = [System.IO.File]::Open($Path, 'Open', 'Read', 'Read')
        $hasher = [System.Security.Cryptography.SHA256]::Create()
        return ([BitConverter]::ToString($hasher.ComputeHash($stream))).Replace('-', '').ToLowerInvariant()
    }
    finally {
        if ($null -ne $hasher) { $hasher.Dispose() }
        if ($null -ne $stream) { $stream.Dispose() }
    }
}

function Assert-File([string]$Path, [int64]$Bytes, [string]$Hash, [string]$Label) {
    if (-not [IO.File]::Exists($Path)) { throw "Missing ${Label}: $Path" }
    if ((Get-Item -LiteralPath $Path).Length -ne $Bytes) { throw "$Label byte mismatch" }
    if ((Get-Sha256 $Path) -ne $Hash) { throw "$Label hash mismatch" }
}

function Write-JsonAtomic([string]$Path, [object]$Value) {
    $parent = Split-Path -Parent $Path
    if (-not [IO.Directory]::Exists($parent)) { [IO.Directory]::CreateDirectory($parent) | Out-Null }
    $temporary = $Path + '.tmp'
    if ([IO.File]::Exists($temporary) -or [IO.File]::Exists($Path)) { throw "Terminal evidence path already exists: $Path" }
    [IO.File]::WriteAllText($temporary, ($Value | ConvertTo-Json -Depth 30) + [Environment]::NewLine, [Text.UTF8Encoding]::new($false))
    [IO.File]::Move($temporary, $Path)
}

function Assert-ExitCode($Code) {
    if ($null -eq $Code -or $Code -isnot [Int32]) { throw 'Child exit code is missing or nonnumeric.' }
}

function Get-HeavyProcesses {
    @(Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -match '^(UnrealEditor|UnrealEditor-Cmd|ShaderCompileWorker|AutomationTool|UnrealBuildTool|blender|cl|link|dotnet)$' } | Select-Object Id, ProcessName, StartTime)
}

function Assert-Authorities {
    Assert-File $Authoring 3454 'e42106e12648fbeac033def9c72298d3f0392be088dc8dd1d08cfda24ca8ea28' 'Authoring03 source'
    Assert-File $InputMap 860203 '46a8ad9187c836329554d29716bd61ca4a2bc0f8bad7d64f66addc108e93e9d2' 'accepted input map'
    Assert-File (Join-Path $Root 'Scripts\ToolchainWave08\environment_realism_stack_authoring02\author_environment_realism_stack02.py') 11473 '116adb907c97d125ed349f2aa2d5b703ec6df6418df77a5b81bbe8622c9016fb' 'frozen Authoring02 source'
    Assert-File (Join-Path $Root 'Docs\AAA_Review\M01_ENVIRONMENT_REALISM_STACK_AUTHORING02_ATTEMPT01_TERMINAL_FREEZE.json') 2231 'c7978bf7ea7c1e168ee0eb6548ee1b3d8bdd4119674c1c87305a90b50bf264dc' 'Authoring02 terminal freeze'
    Assert-File $Editor 512952 '0fb325cf215cc800ce260a1890af3f3dc314b8cc6331061d4e7e7246489af2e0' 'UnrealEditor-Cmd'
    Assert-File (Join-Path $Root 'Production\standing_heavy_process_authorization.json') 2146 '48277d7edd869cc2b841c3993e8f7599bec5291ddf23e9c442b33e09b870c089' 'standing authorization'
}

function Test-Near([double]$A, [double]$B, [double]$Tolerance = 0.01) { [Math]::Abs($A - $B) -le $Tolerance }

function Invoke-OfflineContractTest {
    $failures = @()
    try { Assert-ExitCode ([Int32]0) } catch { $failures += $_.Exception.Message }
    try { Assert-ExitCode $null; $failures += 'Null exit code accepted' } catch {}
    try { Assert-ExitCode '0'; $failures += 'String exit code accepted' } catch {}
    try { Assert-Authorities } catch { $failures += $_.Exception.Message }
    $source = Get-Content -LiteralPath $Authoring -Raw
    foreach ($token in @('unreal.Rotator(roll=TARGET_SUN_ROTATION[2], pitch=TARGET_SUN_ROTATION[0], yaw=TARGET_SUN_ROTATION[1])', 'Sun rotation mismatch', 'EnvironmentRealismStack03')) {
        if (-not $source.Contains($token)) { $failures += "Missing source token: $token" }
    }
    if ([IO.Directory]::Exists($Attempt) -or [IO.File]::Exists($OutputMap) -or [IO.File]::Exists($Terminal) -or [IO.File]::Exists($Emergency)) { $failures += 'A future governed namespace exists' }
    $tempRoot = Join-Path ([IO.Path]::GetTempPath()) ('sg52-authoring03-' + [Guid]::NewGuid().ToString('N'))
    try {
        [IO.Directory]::CreateDirectory($tempRoot) | Out-Null
        Write-JsonAtomic (Join-Path $tempRoot 'terminal.json') ([ordered]@{ classification='OFFLINE_CONTRACT_TEST'; exit_code=[Int32]0 })
    }
    catch { $failures += $_.Exception.Message }
    finally { if ([IO.Directory]::Exists($tempRoot)) { Remove-Item -LiteralPath $tempRoot -Recurse -Force } }
    if ($failures.Count) { [Console]::Error.WriteLine(($failures -join [Environment]::NewLine)); [Environment]::Exit([Int32]1) }
    [Console]::Out.WriteLine('PASS_OFFLINE_CONTRACT')
    [Environment]::Exit([Int32]0)
}

if ($OfflineContractTest) {
    if ($AuthorizeSingleUnreal) { [Console]::Error.WriteLine('Offline and authorized modes conflict.'); [Environment]::Exit([Int32]3) }
    Invoke-OfflineContractTest
}

$State = [ordered]@{
    schema='skyguard.m01-environment-realism-stack-authoring03-supervisor.v1'; classification='FAILED_WITH_EVIDENCE'; started_utc=[DateTime]::UtcNow.ToString('o'); ended_utc=$null; stage='initializing'; standing_authorization_verified=$false; preflight_passed=$false; supervisor_launch_count=1; unreal_launch_count=0; retry_count=0; pid=$null; native_handle_retained=$false; process_samples=@(); exit_code=$null; exit_code_type=$null; timeout=$false; receipt_classification=$null; input_map_unchanged=$false; output_map_bytes=$null; output_map_sha256=$null; actual_sun_rotation=$null; failure=$null; executable=$Editor; arguments=@()
}
$FinalExitCode = [Int32]1

try {
    $State.stage = 'preflight'
    if (-not $AuthorizeSingleUnreal) { throw 'Mechanical -AuthorizeSingleUnreal guard is required.' }
    $standing = Get-Content -LiteralPath (Join-Path $Root 'Production\standing_heavy_process_authorization.json') -Raw | ConvertFrom-Json
    if ($standing.status -ne 'ACTIVE' -or $standing.execution_policy.per_run_user_authorization_required -ne $false) { throw 'Standing authorization is inactive.' }
    $State.standing_authorization_verified = $true
    Assert-Authorities
    $heavy = @(Get-HeavyProcesses)
    if ($heavy.Count) { throw "Heavy process is active: $($heavy | ConvertTo-Json -Compress)" }
    if ([IO.Directory]::Exists($Attempt) -or [IO.File]::Exists($OutputMap) -or [IO.File]::Exists($Terminal) -or [IO.File]::Exists($Emergency)) { throw 'A governed Authoring03 namespace already exists.' }
    $State.preflight_passed = $true

    [IO.Directory]::CreateDirectory($Attempt) | Out-Null
    $stdout = Join-Path $Attempt 'unreal.stdout.log'; $stderr = Join-Path $Attempt 'unreal.stderr.log'; $engineLog = Join-Path $Attempt 'unreal.engine.log'
    $arguments = @($Project, '-Unattended', '-NoSplash', '-NoSound', '-NullRHI', '-NoSaveOnExit', '-stdout', '-FullStdOutLogOutput', '-nop4', '-DisablePlugins=Fab,Bridge,EditorTelemetry,RuntimeTelemetry,EOSShared', '-ini:EditorSettings:[/Script/UnrealEd.AnalyticsPrivacySettings]:bSendUsageData=False', "-ExecutePythonScript=$Authoring", '-ScriptErrorsAreFatal', "-abslog=$engineLog")
    $State.arguments = $arguments; $State.stage = 'unreal_launch'
    $Process = Start-Process -FilePath $Editor -ArgumentList $arguments -WorkingDirectory 'D:\SG52T08_ENV01' -PassThru -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError $stderr
    $State.unreal_launch_count = 1; $State.pid = $Process.Id
    $Handle = $Process.Handle; $State.native_handle_retained = ($Handle -ne [IntPtr]::Zero)
    if (-not $State.native_handle_retained) { throw 'Native process handle was not retained.' }
    $State.stage = 'running'; $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
    while (-not $Process.HasExited -and [DateTime]::UtcNow -lt $deadline) {
        $Process.Refresh(); $State.process_samples += [ordered]@{ at_utc=[DateTime]::UtcNow.ToString('o'); pid=$Process.Id; working_set_bytes=[int64]$Process.WorkingSet64 }; Start-Sleep -Seconds 2
    }
    if (-not $Process.HasExited) { $State.timeout=$true; Stop-Process -Id $Process.Id -Force -ErrorAction SilentlyContinue; throw "Authoring03 exceeded $TimeoutSeconds seconds." }
    $Process.WaitForExit(); $Process.Refresh(); $code=$Process.ExitCode; Assert-ExitCode $code
    $State.exit_code=[Int32]$code; $State.exit_code_type=$code.GetType().FullName
    if ($code -ne 0) { throw "Authoring03 returned exit code $code." }
    if (-not [IO.File]::Exists($Receipt)) { throw 'Authoring03 receipt is missing.' }

    $State.stage='receipt_validation'; $payload=Get-Content -LiteralPath $Receipt -Raw | ConvertFrom-Json
    $State.receipt_classification=[string]$payload.classification; $State.actual_sun_rotation=@($payload.lighting_after.sun_rotation)
    $State.input_map_unchanged=($payload.input_sha256_before -eq '46a8ad9187c836329554d29716bd61ca4a2bc0f8bad7d64f66addc108e93e9d2' -and $payload.input_sha256_after -eq $payload.input_sha256_before)
    if ($State.receipt_classification -ne 'PASSED_M01_ENVIRONMENT_REALISM_STACK_AUTHORING03_AUTOMATIC') { throw "Unexpected classification: $($State.receipt_classification)" }
    if (-not $State.input_map_unchanged -or [int]$payload.actor_count -ne 186 -or @($payload.regrounding_records).Count -ne 165 -or @($payload.waterline_records).Count -ne 10) { throw 'Actor, grounding, waterline, or source-map contract failed.' }
    if ($State.actual_sun_rotation.Count -ne 3 -or -not (Test-Near $State.actual_sun_rotation[0] -35.0) -or -not (Test-Near $State.actual_sun_rotation[1] 75.0) -or -not (Test-Near $State.actual_sun_rotation[2] 0.0)) { throw "Sun rotation contract failed: $($State.actual_sun_rotation -join ',')" }
    if (-not (Test-Near ([double]$payload.lighting_after.sun_intensity) 10.0) -or -not (Test-Near ([double]$payload.lighting_after.skylight_intensity) 2.0)) { throw 'Light intensity contract failed.' }
    if (@($payload.landscape_scale_after).Count -ne 3 -or -not (Test-Near $payload.landscape_scale_after[0] 100.0) -or -not (Test-Near $payload.landscape_scale_after[1] 150.0) -or -not (Test-Near $payload.landscape_scale_after[2] 100.0)) { throw 'Landscape scale contract failed.' }
    if (-not [IO.File]::Exists($OutputMap)) { throw 'Output map is missing.' }
    $State.output_map_bytes=(Get-Item -LiteralPath $OutputMap).Length; $State.output_map_sha256=Get-Sha256 $OutputMap
    if ($payload.output_sha256 -ne $State.output_map_sha256) { throw 'Output hash disagrees with receipt.' }
    Assert-File $InputMap 860203 '46a8ad9187c836329554d29716bd61ca4a2bc0f8bad7d64f66addc108e93e9d2' 'input map after authoring'
    $State.stage='complete'; $State.classification='PASSED_M01_ENVIRONMENT_REALISM_STACK_AUTHORING03_AUTOMATIC'; $FinalExitCode=[Int32]0
}
catch {
    $State.failure=[ordered]@{ stage=$State.stage; message=$_.Exception.Message; type=$_.Exception.GetType().FullName; stack=$_.ScriptStackTrace }; $State.stage='failed'; $FinalExitCode=[Int32]1
}
finally {
    $State.ended_utc=[DateTime]::UtcNow.ToString('o')
    try { Write-JsonAtomic $Terminal $State; if ([IO.Directory]::Exists($Attempt)) { Write-JsonAtomic (Join-Path $Attempt 'terminal.json') $State } }
    catch {
        try { [IO.File]::AppendAllText($Emergency, (([ordered]@{ at_utc=[DateTime]::UtcNow.ToString('o'); classification='FAILED_WITH_EVIDENCE'; stage=$State.stage; error=$_.Exception.Message } | ConvertTo-Json -Compress) + [Environment]::NewLine), [Text.UTF8Encoding]::new($false)) } catch {}
        $FinalExitCode=[Int32]1
    }
}

$State | ConvertTo-Json -Depth 30
[Environment]::Exit([Int32]$FinalExitCode)
