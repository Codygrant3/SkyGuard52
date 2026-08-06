[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$root = 'D:\Skyguard52'
$attemptRoot = Join-Path $root 'Saved\BuildAttempts\PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY01\attempt_01'
$proofRoot = Join-Path $attemptRoot 'proof'
$contractPath = Join-Path $root 'Docs\AAA_Review\PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY01_CONTRACT.json'
$executorPath = Join-Path $root 'Scripts\capture_skyguard_phase4_m01_representative_visual_attempt08_recovery01.py'
$editor = 'C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$uproject = Join-Path $root 'Skyguard52.uproject'
$timeoutSeconds = 540

if (Test-Path -LiteralPath $attemptRoot) {
    throw "Recovery01 namespace already exists; retry and reuse are forbidden: $attemptRoot"
}

$heavyNames = @('UnrealEditor', 'UnrealEditor-Cmd', 'ShaderCompileWorker', 'blender', 'AutomationTool', 'UnrealBuildTool')
$heavy = @(Get-Process -ErrorAction SilentlyContinue | Where-Object { $heavyNames -contains $_.ProcessName })
if ($heavy.Count -ne 0) {
    throw "Heavy process preflight failed: $($heavy.ProcessName -join ', ')"
}

foreach ($required in @($contractPath, $executorPath, $editor, $uproject)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
        throw "Missing required file: $required"
    }
}

$attemptParent = Split-Path -Parent $attemptRoot
if (-not (Test-Path -LiteralPath $attemptParent)) {
    New-Item -ItemType Directory -Path $attemptParent | Out-Null
}

$launcherRoot = Join-Path $attemptParent 'launcher_attempt_01'
if (Test-Path -LiteralPath $launcherRoot) {
    throw "Launcher evidence namespace already exists; automatic retry is forbidden: $launcherRoot"
}
New-Item -ItemType Directory -Path $launcherRoot | Out-Null
$logs = Join-Path $launcherRoot 'logs'
New-Item -ItemType Directory -Path $logs | Out-Null
$stdout = Join-Path $logs 'recovery01.stdout.log'
$stderr = Join-Path $logs 'recovery01.stderr.log'
$engineLog = Join-Path $logs 'recovery01.engine.log'
$runManifest = Join-Path $launcherRoot 'run_manifest.json'

$arguments = @(
    "`"$uproject`"",
    '-nullrhi=false',
    '-dx12',
    '-sm6',
    '-unattended',
    '-nosplash',
    '-NoSound',
    '-NoVSync',
    '-ExecCmds="r.ScreenPercentage 100,sg.ViewDistanceQuality 3,sg.AntiAliasingQuality 3,sg.ShadowQuality 3,sg.GlobalIlluminationQuality 3,sg.ReflectionQuality 3,sg.PostProcessQuality 3,sg.TextureQuality 3,sg.EffectsQuality 3,sg.FoliageQuality 3,sg.ShadingQuality 3"',
    "-SkyguardRecovery01AttemptRoot=`"$attemptRoot`"",
    "-SkyguardRecovery01ProofRoot=`"$proofRoot`"",
    "-ExecutePythonScript=`"$executorPath`"",
    "-abslog=`"$engineLog`"",
    '-ScriptErrorsAreFatal'
)

$startedUtc = [DateTime]::UtcNow.ToString('o')
$process = Start-Process -FilePath $editor -ArgumentList $arguments -PassThru -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError $stderr
$timedOut = -not $process.WaitForExit($timeoutSeconds * 1000)
if ($timedOut) {
    Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
    $process.WaitForExit()
}
$actualExitCode = $process.ExitCode
$endedUtc = [DateTime]::UtcNow.ToString('o')

$manifest = [ordered]@{
    schema = 'skyguard.phase4.m01-representative-visual-attempt08-recovery01-run.v1'
    contract_id = 'P4.6-M01-REPRESENTATIVE-VISUAL-008-RECOVERY-01'
    started_utc = $startedUtc
    ended_utc = $endedUtc
    process_id = $process.Id
    actual_exit_code = $actualExitCode
    timed_out = $timedOut
    automatic_retry = $false
    process_handle_retained = $true
    attempt_root = $attemptRoot
    proof_root = $proofRoot
    stdout_log = $stdout
    stderr_log = $stderr
    engine_log = $engineLog
}
$manifest | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $runManifest -Encoding utf8

if ($timedOut) {
    throw "Recovery01 timed out; evidence frozen at $launcherRoot"
}
if ($actualExitCode -ne 0) {
    throw "Recovery01 failed with exit code $actualExitCode; evidence frozen at $launcherRoot"
}
