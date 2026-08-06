[CmdletBinding()]
param(
    [switch]$AuthorizeSingleUnrealProof
)

$ErrorActionPreference = 'Stop'
$root = 'D:\Skyguard52'
$bindingId = 'P4.6-M01-RECOVERY04-BINDING-01'
$bindingFreeze = Join-Path $root 'Docs\AAA_Review\PHASE4_M01_RECOVERY04_RUNTIME_BINDING_FREEZE.json'
$bindingContract = Join-Path $root 'Docs\AAA_Review\PHASE4_M01_RECOVERY04_RUNTIME_BINDING_CONTRACT.json'
$preflightSchema = Join-Path $root 'Saved\Reports\PHASE4_M01_RECOVERY04_EXECUTION_PREFLIGHT_SCHEMA.json'
$terminalSchema = Join-Path $root 'Saved\Reports\PHASE4_M01_RECOVERY04_TERMINAL_SUPERVISOR_SCHEMA.json'
$postflightVerifier = Join-Path $root 'Scripts\verify_skyguard_phase4_m01_representative_visual_attempt08_recovery04_postflight.py'
$editor = 'D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$uproject = Join-Path $root 'Skyguard52.uproject'
$pluginRoot = Join-Path $root 'Plugins\SkyguardRecovery03NativeRecovery04'
$pluginDescriptor = Join-Path $pluginRoot 'SkyguardRecovery03NativeRecovery04.uplugin'
$pluginBinary = Join-Path $pluginRoot 'Binaries\Win64\UnrealEditor-SkyguardRecovery03NativeRecovery01.dll'
$runtimeAttempt = Join-Path $root 'Saved\BuildAttempts\PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY03_NATIVE_BUILD_RECOVERY01\runtime_attempt_01'
$proofRoot = Join-Path $runtimeAttempt 'proof'
$launcherAttempt = Join-Path $root 'Saved\BuildAttempts\PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY04_BINDING01\launcher_attempt_01'
$preflightReceipt = Join-Path $root 'Saved\Reports\PHASE4_M01_RECOVERY04_BINDING01_EXECUTION_PREFLIGHT.json'
$terminalReceipt = Join-Path $root 'Saved\Reports\PHASE4_M01_RECOVERY04_BINDING01_TERMINAL_SUPERVISOR.json'
$timeoutSeconds = 540
$checks = [ordered]@{}
$process = $null
$nativeHandle = $null
$startedUtc = [DateTime]::UtcNow.ToString('o')
$timedOut = $false
$numericExit = $null
$failureIssue = $null
$launchCount = 0
$unrealStarted = $false
$terminalWritten = $false

function Get-LowerSha256([string]$Path) {
    $stream = $null
    $hasher = $null
    try {
        $stream = [System.IO.File]::Open(
            $Path,
            [System.IO.FileMode]::Open,
            [System.IO.FileAccess]::Read,
            [System.IO.FileShare]::Read)
        $hasher = [System.Security.Cryptography.SHA256]::Create()
        return -join ($hasher.ComputeHash($stream) | ForEach-Object { $_.ToString('x2') })
    } finally {
        if ($null -ne $stream) { $stream.Dispose() }
        if ($null -ne $hasher) { $hasher.Dispose() }
    }
}

function Test-FrozenRecord($Record) {
    $path = if ($Record.path) {
        [string]$Record.path
    } elseif ($Record.file) {
        Join-Path $root ([string]$Record.file)
    } else {
        return $false
    }
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { return $false }
    $item = Get-Item -LiteralPath $path
    return $item.Length -eq [long]$Record.bytes `
        -and (Get-LowerSha256 $path) -eq ([string]$Record.sha256).ToLowerInvariant()
}

function Write-JsonFile([string]$Path, $Value) {
    $parent = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent | Out-Null
    }
    $Value | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $Path -Encoding utf8
}

function Write-ExecutionPreflight([string]$Gate, [string]$Issue) {
    Write-JsonFile $preflightReceipt ([ordered]@{
        schema = 'skyguard.phase4.m01-recovery04-binding01-execution-preflight.v1'
        binding_id = $bindingId
        created_utc = [DateTime]::UtcNow.ToString('o')
        gate = $Gate
        error = $Issue
        checks = $checks
        runtime_namespace_created = (Test-Path -LiteralPath $runtimeAttempt)
        launcher_namespace_created = (Test-Path -LiteralPath $launcherAttempt)
        unreal_started = $unrealStarted
        launch_count = $launchCount
        retry_count = 0
    })
}

function Write-TerminalSupervisor([string]$Gate, [string]$Issue) {
    $exitType = if ($null -eq $numericExit) { $null } else { $numericExit.GetType().FullName }
    Write-JsonFile $terminalReceipt ([ordered]@{
        schema = 'skyguard.phase4.m01-recovery04-binding01-terminal-supervisor.v1'
        binding_id = $bindingId
        gate = $Gate
        issue = $Issue
        started_utc = $startedUtc
        ended_utc = [DateTime]::UtcNow.ToString('o')
        process_id = if ($null -eq $process) { $null } else { $process.Id }
        process_handle_retained = $null -ne $nativeHandle
        timed_out = $timedOut
        actual_exit_code = $numericExit
        actual_exit_code_type = $exitType
        launch_count = $launchCount
        retry_count = 0
        unreal_started = $unrealStarted
        runtime_attempt = $runtimeAttempt
        launcher_attempt = $launcherAttempt
    })
    $script:terminalWritten = $true
}

try {
    if (-not $AuthorizeSingleUnrealProof) {
        throw 'Exact -AuthorizeSingleUnrealProof switch is required.'
    }
    if (Test-Path -LiteralPath $preflightReceipt) {
        throw "Execution preflight namespace already exists: $preflightReceipt"
    }
    if (Test-Path -LiteralPath $terminalReceipt) {
        throw "Terminal supervisor namespace already exists: $terminalReceipt"
    }
    foreach ($required in @(
        $bindingFreeze,
        $bindingContract,
        $preflightSchema,
        $terminalSchema,
        $postflightVerifier,
        $editor,
        $uproject,
        $pluginDescriptor,
        $pluginBinary
    )) {
        if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
            throw "Missing required authority: $required"
        }
    }

    $freeze = Get-Content -LiteralPath $bindingFreeze -Raw | ConvertFrom-Json
    if ($freeze.classification -ne 'PASSED_READY_FOR_EXPLICIT_SINGLE_RECOVERY04_UNREAL_AUTHORIZATION') {
        throw 'Recovery04 runtime-binding freeze is not execution-ready.'
    }
    $allFrozenRecords = @($freeze.authorities) + @($freeze.frozen_files)
    $badFrozen = @($allFrozenRecords | Where-Object { -not (Test-FrozenRecord $_) })
    $checks.frozen_record_count = $allFrozenRecords.Count
    $checks.frozen_hashes = $badFrozen.Count -eq 0
    if ($badFrozen.Count -ne 0) {
        throw "Frozen binding mismatch: $($badFrozen.path -join ', ')"
    }

    $editorItem = Get-Item -LiteralPath $editor
    $checks.editor_bytes = $editorItem.Length -eq 512952
    $checks.editor_version = $editorItem.VersionInfo.FileVersion -eq '++UE5+Release-5.8-CL-56057345'
    $checks.editor_sha256 = (Get-LowerSha256 $editor) -eq '0fb325cf215cc800ce260a1890af3f3dc314b8cc6331061d4e7e7246489af2e0'
    if (-not ($checks.editor_bytes -and $checks.editor_version -and $checks.editor_sha256)) {
        throw 'Installed UE 5.8 editor authority mismatch.'
    }

    $checks.plugin_binary_sha256 = (Get-LowerSha256 $pluginBinary) -eq '2070765a5d44199f7116c2038c97d866b91a509706de73953ead1cad057cb6e3'
    $descriptor = Get-Content -LiteralPath $pluginDescriptor -Raw | ConvertFrom-Json
    $checks.plugin_disabled_by_default = $descriptor.EnabledByDefault -eq $false
    $checks.module_identity = @($descriptor.Modules).Count -eq 1 `
        -and $descriptor.Modules[0].Name -eq 'SkyguardRecovery03NativeRecovery01'
    if (-not ($checks.plugin_binary_sha256 -and $checks.plugin_disabled_by_default -and $checks.module_identity)) {
        throw 'Accepted Recovery04 plugin authority mismatch.'
    }

    $checks.runtime_absent = -not (Test-Path -LiteralPath $runtimeAttempt)
    $checks.proof_absent = -not (Test-Path -LiteralPath $proofRoot)
    $checks.launcher_absent = -not (Test-Path -LiteralPath $launcherAttempt)
    if (-not ($checks.runtime_absent -and $checks.proof_absent -and $checks.launcher_absent)) {
        throw 'A governed Recovery04 execution namespace already exists; reuse is forbidden.'
    }

    $heavyNames = @(
        'UnrealEditor',
        'UnrealEditor-Cmd',
        'ShaderCompileWorker',
        'blender',
        'AutomationTool',
        'UnrealBuildTool',
        'cl',
        'link'
    )
    $heavy = @(Get-Process -ErrorAction SilentlyContinue | Where-Object {
        $heavyNames -contains $_.ProcessName
    })
    $checks.heavy_process_count = $heavy.Count
    if ($heavy.Count -ne 0) {
        throw "Heavy process preflight failed: $($heavy.ProcessName -join ', ')"
    }

    Write-ExecutionPreflight 'PASS_READY_TO_START_SINGLE_UNREAL_PROCESS' $null

    New-Item -ItemType Directory -Path $launcherAttempt | Out-Null
    $logs = Join-Path $launcherAttempt 'logs'
    New-Item -ItemType Directory -Path $logs | Out-Null
    $stdout = Join-Path $logs 'recovery04.stdout.log'
    $stderr = Join-Path $logs 'recovery04.stderr.log'
    $engineLog = Join-Path $logs 'recovery04.engine.log'
    $processTree = Join-Path $launcherAttempt 'process_tree_samples.jsonl'

    $arguments = @(
        "`"$uproject`"",
        '/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_ProductionEnvironment_v5_attempt03',
        '-dx12',
        '-sm6',
        '-unattended',
        '-nosplash',
        '-NoSound',
        '-NoVSync',
        '-ExecCmds="r.ScreenPercentage 100,sg.ViewDistanceQuality 3,sg.AntiAliasingQuality 3,sg.ShadowQuality 3,sg.GlobalIlluminationQuality 3,sg.ReflectionQuality 3,sg.PostProcessQuality 3,sg.TextureQuality 3,sg.EffectsQuality 3,sg.FoliageQuality 3,sg.ShadingQuality 3"',
        '-EnablePlugins=SkyguardRecovery03NativeRecovery04',
        '-DisablePlugins=SkyguardRecovery03NativeRecovery01,Fab,Bridge,EditorTelemetry,RuntimeTelemetry,EOSShared',
        '-ini:EditorSettings:[/Script/UnrealEd.AnalyticsPrivacySettings]:bSendUsageData=False',
        '-SkyguardRecovery01ContractId=P4.6-M01-REPRESENTATIVE-VISUAL-008-RECOVERY-03-NATIVE-BUILD-RECOVERY-01',
        '-SkyguardRecovery01Authorization=P4.6-M01-REPRESENTATIVE-VISUAL-008-RECOVERY-03-NATIVE-BUILD-RECOVERY-01-ONE-SHOT',
        '-SkyguardRecovery01ExpectedMap=/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_ProductionEnvironment_v5_attempt03',
        "-SkyguardRecovery01AttemptRoot=`"$runtimeAttempt`"",
        "-abslog=`"$engineLog`""
    )

    $process = Start-Process -FilePath $editor -ArgumentList $arguments -PassThru -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError $stderr
    $launchCount = 1
    $unrealStarted = $true
    $nativeHandle = $process.Handle
    $deadline = [DateTime]::UtcNow.AddSeconds($timeoutSeconds)
    while (-not $process.HasExited -and [DateTime]::UtcNow -lt $deadline) {
        $sample = [ordered]@{
            sampled_utc = [DateTime]::UtcNow.ToString('o')
            supervisor_process_id = $PID
            unreal_process_id = $process.Id
            unreal_has_exited = $process.HasExited
            unreal_working_set_bytes = if ($process.HasExited) { $null } else { $process.WorkingSet64 }
        }
        ($sample | ConvertTo-Json -Compress) | Add-Content -LiteralPath $processTree -Encoding utf8
        $process.WaitForExit(5000) | Out-Null
        $process.Refresh()
    }
    if (-not $process.HasExited) {
        $timedOut = $true
        Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
    }
    $process.WaitForExit()
    $process.Refresh()
    if ($null -eq $process.ExitCode -or $process.ExitCode -isnot [int]) {
        throw 'Unreal exit code was null or nonnumeric.'
    }
    $numericExit = [int]$process.ExitCode
    if ($timedOut -or $numericExit -ne 0) {
        throw "Unreal failed: exit_code=$numericExit timed_out=$timedOut"
    }
    Write-TerminalSupervisor 'UNREAL_EXITED_AWAITING_POSTFLIGHT' $null
} catch {
    $failureIssue = $_.Exception.Message
    if (-not (Test-Path -LiteralPath $preflightReceipt)) {
        Write-ExecutionPreflight 'FAILED_WITH_EVIDENCE' $failureIssue
    }
    if (-not (Test-Path -LiteralPath $terminalReceipt)) {
        Write-TerminalSupervisor 'FAILED_WITH_EVIDENCE' $failureIssue
    }
    throw
} finally {
    if (-not $terminalWritten -and -not (Test-Path -LiteralPath $terminalReceipt)) {
        Write-TerminalSupervisor 'FAILED_WITH_EVIDENCE' $(if ($failureIssue) { $failureIssue } else { 'Supervisor ended without terminal classification.' })
    }
}
