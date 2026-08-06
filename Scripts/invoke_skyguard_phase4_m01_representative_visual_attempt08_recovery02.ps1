[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$root = 'D:\Skyguard52'
$contractPath = Join-Path $root 'Docs\AAA_Review\PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY02_CONTRACT.json'
$freezePath = Join-Path $root 'Docs\AAA_Review\PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY02_FREEZE.json'
$inventoryPath = Join-Path $root 'Saved\Reports\PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY02_SOURCE_INVENTORY.json'
$executorPath = Join-Path $root 'Scripts\capture_skyguard_phase4_m01_representative_visual_attempt08_recovery02.py'
$preflightReceipt = Join-Path $root 'Saved\Reports\PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY02_EXECUTION_PREFLIGHT.json'
$attemptRoot = Join-Path $root 'Saved\BuildAttempts\PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY02\attempt_01'
$proofRoot = Join-Path $attemptRoot 'proof'
$launcherRoot = Join-Path $root 'Saved\BuildAttempts\PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY02\launcher_attempt_01'
$editor = 'D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$uproject = Join-Path $root 'Skyguard52.uproject'
$expectedEditorBytes = 512952
$expectedEditorVersion = '++UE5+Release-5.8-CL-56057345'
$expectedEditorHash = '0fb325cf215cc800ce260a1890af3f3dc314b8cc6331061d4e7e7246489af2e0'
$timeoutSeconds = 540
$checks = [ordered]@{}
$preflightError = $null

function Get-LowerSha256([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Test-FrozenRecord($Record) {
    $path = if ($Record.absolute_file) { [string]$Record.absolute_file } else { Join-Path $root ([string]$Record.file) }
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { return $false }
    $item = Get-Item -LiteralPath $path
    return ($item.Length -eq [long]$Record.bytes) -and ((Get-LowerSha256 $path) -eq [string]$Record.sha256)
}

function Write-PreflightReceipt([string]$Gate, [string]$ErrorText) {
    $receipt = [ordered]@{
        schema = 'skyguard.phase4.m01-representative-visual-attempt08-recovery02-execution-preflight.v1'
        contract_id = 'P4.6-M01-REPRESENTATIVE-VISUAL-008-RECOVERY-02'
        created_utc = [DateTime]::UtcNow.ToString('o')
        gate = $Gate
        error = $ErrorText
        checks = $checks
        attempt_root_created = (Test-Path -LiteralPath $attemptRoot)
        proof_root_created = (Test-Path -LiteralPath $proofRoot)
        unreal_started = $false
        automatic_retry = $false
    }
    $receipt | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $preflightReceipt -Encoding utf8
}

if (Test-Path -LiteralPath $preflightReceipt) {
    throw "Recovery02 execution preflight receipt already exists; retry is forbidden: $preflightReceipt"
}

try {
    foreach ($required in @($contractPath, $freezePath, $inventoryPath, $executorPath, $uproject, $editor)) {
        if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
            throw "Missing required file: $required"
        }
    }
    $checks.editor_path = $true
    $editorItem = Get-Item -LiteralPath $editor
    $checks.editor_bytes = $editorItem.Length -eq $expectedEditorBytes
    $checks.editor_version = $editorItem.VersionInfo.FileVersion -eq $expectedEditorVersion
    $checks.editor_sha256 = (Get-LowerSha256 $editor) -eq $expectedEditorHash
    if (-not ($checks.editor_bytes -and $checks.editor_version -and $checks.editor_sha256)) {
        throw 'Installed Unreal editor authority mismatch'
    }
    $contract = Get-Content -LiteralPath $contractPath -Raw | ConvertFrom-Json
    $freeze = Get-Content -LiteralPath $freezePath -Raw | ConvertFrom-Json
    $inventory = Get-Content -LiteralPath $inventoryPath -Raw | ConvertFrom-Json
    $records = @($freeze.frozen_files) + @($inventory.immutable_inputs) + @($inventory.recovery02_design_files)
    $bad = @($records | Where-Object { -not (Test-FrozenRecord $_) })
    $checks.frozen_record_count = $records.Count
    $checks.frozen_hashes = $bad.Count -eq 0
    if ($bad.Count -ne 0) {
        throw "Frozen record mismatch: $($bad.file -join ', ')"
    }
    $checks.attempt_absent = -not (Test-Path -LiteralPath $attemptRoot)
    $checks.proof_absent = -not (Test-Path -LiteralPath $proofRoot)
    $checks.launcher_absent = -not (Test-Path -LiteralPath $launcherRoot)
    if (-not ($checks.attempt_absent -and $checks.proof_absent -and $checks.launcher_absent)) {
        throw 'Recovery02 execution namespace already exists'
    }
    $heavyNames = @('UnrealEditor', 'UnrealEditor-Cmd', 'ShaderCompileWorker', 'blender', 'AutomationTool', 'UnrealBuildTool')
    $heavy = @(Get-Process -ErrorAction SilentlyContinue | Where-Object { $heavyNames -contains $_.ProcessName })
    $checks.heavy_process_count = $heavy.Count
    if ($heavy.Count -ne 0) {
        throw "Heavy process preflight failed: $($heavy.ProcessName -join ', ')"
    }
    Write-PreflightReceipt 'PASS_READY_TO_START_SINGLE_UNREAL_PROCESS' $null
} catch {
    $preflightError = $_.Exception.Message
    Write-PreflightReceipt 'FAILED_WITH_EVIDENCE' $preflightError
    throw
}

New-Item -ItemType Directory -Path $launcherRoot | Out-Null
$logs = Join-Path $launcherRoot 'logs'
New-Item -ItemType Directory -Path $logs | Out-Null
$stdout = Join-Path $logs 'recovery02.stdout.log'
$stderr = Join-Path $logs 'recovery02.stderr.log'
$engineLog = Join-Path $logs 'recovery02.engine.log'
$runManifest = Join-Path $launcherRoot 'run_manifest.json'
$arguments = @(
    "`"$uproject`"",
    '-dx12',
    '-sm6',
    '-unattended',
    '-nosplash',
    '-NoSound',
    '-NoVSync',
    '-ExecCmds="r.ScreenPercentage 100,sg.ViewDistanceQuality 3,sg.AntiAliasingQuality 3,sg.ShadowQuality 3,sg.GlobalIlluminationQuality 3,sg.ReflectionQuality 3,sg.PostProcessQuality 3,sg.TextureQuality 3,sg.EffectsQuality 3,sg.FoliageQuality 3,sg.ShadingQuality 3"',
    "-SkyguardRecovery02AttemptRoot=`"$attemptRoot`"",
    "-SkyguardRecovery02ProofRoot=`"$proofRoot`"",
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
$manifest = [ordered]@{
    schema = 'skyguard.phase4.m01-representative-visual-attempt08-recovery02-run.v1'
    contract_id = 'P4.6-M01-REPRESENTATIVE-VISUAL-008-RECOVERY-02'
    started_utc = $startedUtc
    ended_utc = [DateTime]::UtcNow.ToString('o')
    process_id = $process.Id
    actual_exit_code = $actualExitCode
    timed_out = $timedOut
    process_handle_retained = $true
    automatic_retry = $false
    attempt_root = $attemptRoot
    proof_root = $proofRoot
    preflight_receipt = $preflightReceipt
    stdout_log = $stdout
    stderr_log = $stderr
    engine_log = $engineLog
}
$manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $runManifest -Encoding utf8
if ($timedOut) { throw "Recovery02 timed out; evidence frozen at $launcherRoot" }
if ($actualExitCode -ne 0) { throw "Recovery02 failed with exit code $actualExitCode; evidence frozen at $launcherRoot" }
