param(
    [switch]$OfflineContractTest,
    [switch]$AuthorizeSingleUnrealProof
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Root = 'D:\Skyguard52'
$Project = 'D:\SG52T08_ENV01\Skyguard52.uproject'
$Editor = 'D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe'
$MapAsset = '/Game/M01/Lvl_M01_VisibleEnvironmentStage07BMaterialTerrainDistrictVariety01Recovery01'
$MapFile = 'D:\SG52T08_ENV01\Content\M01\Lvl_M01_VisibleEnvironmentStage07BMaterialTerrainDistrictVariety01Recovery01.umap'
$ExpectedMapSha = '531e0d45ecc43d1632ef480e2fbf0116fdfff27425e6dd28703b88a8b95b6bbe'
$Capture = Join-Path $Root 'Scripts\ToolchainWave08\m01_visible_environment_stage07b_material_terrain_district_variety01_recovery01_visual_proof01_recovery02\capture_stage07b_recovery01_visual_proof01_recovery02.py'
$Contract = Join-Path $Root 'Scripts\ToolchainWave08\m01_visible_environment_stage07b_material_terrain_district_variety01_recovery01_visual_proof01_recovery02\stage07b_recovery01_visual_proof01_recovery02_contract.json'
$AttemptRoot = Join-Path $Root 'Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_STAGE07B_MATERIAL_TERRAIN_DISTRICT_VARIETY01_RECOVERY01_VISUAL_PROOF01_RECOVERY02\attempt_01'
$LauncherRoot = Join-Path $Root 'Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_STAGE07B_MATERIAL_TERRAIN_DISTRICT_VARIETY01_RECOVERY01_VISUAL_PROOF01_RECOVERY02\launcher_attempt_01'
$StartupReceipt = Join-Path $LauncherRoot 'executor_startup_receipt.json'
$Receipt = Join-Path $AttemptRoot 'proof\capture_receipt.json'
$TerminalManifest = Join-Path $Root 'Saved\Reports\M01_VISIBLE_ENVIRONMENT_STAGE07B_MATERIAL_TERRAIN_DISTRICT_VARIETY01_RECOVERY01_VISUAL_PROOF01_RECOVERY02_TERMINAL_SUPERVISOR.json'
$ExecutorStartupTimeoutSeconds = 120
$TimeoutSeconds = 1200

function Get-Sha256([string]$Path) {
    $stream = [System.IO.File]::Open($Path, 'Open', 'Read', 'Read')
    $hasher = [System.Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($hasher.ComputeHash($stream))).Replace('-', '').ToLowerInvariant() }
    finally { $hasher.Dispose(); $stream.Dispose() }
}
function Write-JsonAtomic([string]$Path, [object]$Payload) {
    [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($Path)) | Out-Null
    $temporary = "$Path.tmp"
    [IO.File]::WriteAllText($temporary, ($Payload | ConvertTo-Json -Depth 16) + [Environment]::NewLine, [Text.UTF8Encoding]::new($false))
    [IO.File]::Move($temporary, $Path)
}

if ($OfflineContractTest) {
    $c = Get-Content -LiteralPath $Contract -Raw | ConvertFrom-Json
    if ((Get-Sha256 $MapFile) -ne $ExpectedMapSha) { throw 'Recovery01 map hash drifted' }
    if ($c.runtime.game_flag -ne $false) { throw 'Recovery02 proof must not use the game flag' }
    if ($c.runtime.quoted_execcmds -ne $true) { throw 'Quoted ExecCmds required' }
    if ($c.runtime.stable_shader_polls -ne 2) { throw 'Shader-readiness polls changed' }
    $captureText = Get-Content -LiteralPath $Capture -Raw
    if ($captureText -notmatch 'shader_readiness') { throw 'Stage 7A shader-readiness phase missing from capture' }
    if ($captureText -notmatch 'audit_landscape_material_compilation') { throw 'Stage 7A landscape compilation audit missing' }
    if ($captureText -notmatch 'capture_component2d') { throw 'Stage 7A SceneCapture component binding missing' }
    $script = Get-Content -LiteralPath $MyInvocation.MyCommand.Path -Raw
    $gameArgument = "'" + '-' + 'game' + "'"
    if ($script.Contains($gameArgument)) { throw 'Supervisor must not pass the game flag' }
    $legacyPython = '-ExecutePython' + 'Script'
    if ($script.Contains($legacyPython)) { throw 'Supervisor must not use ExecutePythonScript' }
    if (($script | Select-String -Pattern 'Start-Process -FilePath \$Editor' -AllMatches).Matches.Count -ne 1) { throw 'Must contain exactly one Unreal launch' }
    if (Test-Path -LiteralPath $AttemptRoot) { throw "Fresh proof namespace exists: $AttemptRoot" }
    if (Test-Path -LiteralPath $LauncherRoot) { throw "Fresh launcher namespace exists: $LauncherRoot" }
    [ordered]@{ classification = 'PASSED_OFFLINE_READY_FOR_SINGLE_STAGE07B_RECOVERY01_VISUAL_PROOF01_RECOVERY02'; unreal_launch_count = 0 } | ConvertTo-Json
    [Environment]::Exit(0)
}

$state = [ordered]@{
    schema = 'skyguard.m01-visible-environment-stage07b-recovery01.visual-proof01-recovery02.supervisor.v1'
    classification = 'FAILED_WITH_EVIDENCE'
    started_at_utc = [DateTime]::UtcNow.ToString('o')
    completed_at_utc = $null
    executable = $Editor
    unreal_launch_count = 0
    retry_count = 0
    pid = $null
    exit_code = $null
    timed_out = $false
    executor_startup_receipt_observed = $false
    failure = $null
}
$finalExit = 1
try {
    if (-not $AuthorizeSingleUnrealProof) { throw 'Mechanical -AuthorizeSingleUnrealProof guard is required' }
    if ((Get-Sha256 $MapFile) -ne $ExpectedMapSha) { throw 'Recovery01 map hash drifted' }
    if (Test-Path -LiteralPath $AttemptRoot) { throw "Fresh proof namespace exists: $AttemptRoot" }
    if (Test-Path -LiteralPath $LauncherRoot) { throw "Fresh launcher namespace exists: $LauncherRoot" }
    if (Test-Path -LiteralPath $TerminalManifest) { throw "Fresh proof manifest exists: $TerminalManifest" }
    $heavy = @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object { $_.Name -match '^(UnrealEditor(-Cmd)?|Blender|ShaderCompileWorker)(\.exe)?$' })
    if ($heavy.Count -ne 0) { throw 'Heavy process active' }
    [IO.Directory]::CreateDirectory((Join-Path $LauncherRoot 'logs')) | Out-Null
    [IO.Directory]::CreateDirectory($AttemptRoot) | Out-Null
    $stdout = Join-Path $LauncherRoot 'logs\proof.stdout.log'
    $stderr = Join-Path $LauncherRoot 'logs\proof.stderr.log'
    $engineLog = Join-Path $LauncherRoot 'logs\proof.engine.log'
    $execCmdValue = "py $($Capture.Replace('\','/'))"
    $execCmdArgument = '-ExecCmds="' + $execCmdValue + '"'
    $arguments = @(
        $Project,
        $MapAsset,
        '-D3D12',
        '-sm6',
        '-RenderOffscreen',
        '-windowed',
        '-ResX=2560',
        '-ResY=1440',
        '-NoVSync',
        '-NoSound',
        '-NoSplash',
        '-unattended',
        '-nop4',
        '-DisablePlugins=Fab,Bridge,EditorTelemetry,RuntimeTelemetry,EOSShared',
        '-csvCategories=Global',
        '-csvGpuStats',
        $execCmdArgument,
        "-abslog=$engineLog"
    )
    $process = Start-Process -FilePath $Editor -ArgumentList $arguments -WorkingDirectory 'D:\SG52T08_ENV01' -PassThru -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError $stderr
    $state.unreal_launch_count = 1
    $state.pid = $process.Id
    $handle = $process.Handle
    if ($null -eq $handle) { throw 'Failed to retain Unreal process handle' }
    $startupDeadline = [DateTime]::UtcNow.AddSeconds($ExecutorStartupTimeoutSeconds)
    $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
    while (-not $process.HasExited -and [DateTime]::UtcNow -lt $deadline) {
        if (-not $state.executor_startup_receipt_observed -and (Test-Path -LiteralPath $StartupReceipt)) {
            $startup = Get-Content -LiteralPath $StartupReceipt -Raw | ConvertFrom-Json
            if ($startup.gate -ne 'EXECUTOR_INVOKED') { throw "Executor startup gate failed: $($startup.gate)" }
            $state.executor_startup_receipt_observed = $true
        }
        if (-not $state.executor_startup_receipt_observed -and [DateTime]::UtcNow -ge $startupDeadline) {
            throw "Executor startup receipt was absent after $ExecutorStartupTimeoutSeconds seconds"
        }
        Start-Sleep -Seconds 2
    }
    if (-not $process.HasExited) {
        $state.timed_out = $true
        Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        throw "Proof exceeded $TimeoutSeconds seconds"
    }
    $process.WaitForExit()
    $state.exit_code = [int]$process.ExitCode
    if (-not $state.executor_startup_receipt_observed) { throw 'Executor never wrote a startup receipt' }
    if (-not [IO.File]::Exists($Receipt)) { throw 'Capture receipt missing' }
    $payload = Get-Content -LiteralPath $Receipt -Raw | ConvertFrom-Json
    $state.classification = [string]$payload.classification
    if ($state.classification -ne 'PASSED_AUTOMATIC_AWAITING_HUMAN_VISUAL_REVIEW') { throw "Proof receipt failed: $($state.classification)" }
    if ((Get-Sha256 $MapFile) -ne $ExpectedMapSha) { throw 'Proof mutated Recovery01 map' }
    $finalExit = 0
}
catch {
    $state.failure = $_.Exception.Message
}
finally {
    $state.completed_at_utc = [DateTime]::UtcNow.ToString('o')
    Write-JsonAtomic $TerminalManifest $state
}
$state | ConvertTo-Json -Depth 8
[Environment]::Exit([int]$finalExit)
