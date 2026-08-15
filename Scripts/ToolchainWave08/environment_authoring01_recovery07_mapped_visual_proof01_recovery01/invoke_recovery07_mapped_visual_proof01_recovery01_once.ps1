[CmdletBinding()]
param(
    [switch]$AuthorizeSingleUnrealProof,
    [switch]$OfflineContractTest,
    [string]$OfflineEvidenceRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$root = 'D:\Skyguard52'
$isolatedRoot = 'D:\SG52T08_ENV01'
$editor = 'D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe'
$uproject = Join-Path $isolatedRoot 'Skyguard52.uproject'
$mapAsset = '/Game/ToolchainWave08/Environment/Lvl_M01_T08_EnvironmentAuthoring01_Recovery07'
$contractId = 'T08-M01-ENV-AUTH01-RECOVERY07-MAPPED-VISUAL-PROOF01-RECOVERY01'
$scriptRoot = Join-Path $root 'Scripts\ToolchainWave08\environment_authoring01_recovery07_mapped_visual_proof01_recovery01'
$executor = Join-Path $scriptRoot 'capture_recovery07_mapped_visual_proof01_recovery01.py'
$adjudicator = Join-Path $scriptRoot 'adjudicate_recovery07_mapped_visual_proof01_recovery01_once.py'
$contract = Join-Path $root 'Docs\AAA_Review\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY07_MAPPED_VISUAL_PROOF01_RECOVERY01_CONTRACT.json'
$offlineFreeze = Join-Path $root 'Docs\AAA_Review\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY07_MAPPED_VISUAL_PROOF01_RECOVERY01_OFFLINE_DESIGN_FREEZE.json'
$bindingFreeze = Join-Path $root 'Docs\AAA_Review\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY07_MAPPED_VISUAL_PROOF01_RECOVERY01_EXECUTION_PROMPT_BINDING_FREEZE.json'
$attemptRoot = Join-Path $root 'Saved\BuildAttempts\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY07_MAPPED_VISUAL_PROOF01_RECOVERY01\attempt_01'
$launcherRoot = Join-Path $root 'Saved\BuildAttempts\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY07_MAPPED_VISUAL_PROOF01_RECOVERY01\launcher_attempt_01'
$preflightReceipt = Join-Path $root 'Saved\Reports\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY07_MAPPED_VISUAL_PROOF01_RECOVERY01_EXECUTION_PREFLIGHT.json'
$terminalSupervisor = Join-Path $root 'Saved\Reports\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY07_MAPPED_VISUAL_PROOF01_RECOVERY01_TERMINAL_SUPERVISOR.json'
$emergencyReceipt = Join-Path $root 'Saved\Reports\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY07_MAPPED_VISUAL_PROOF01_RECOVERY01_EMERGENCY_RECEIPT.jsonl'
$postflightReport = Join-Path $root 'Saved\Reports\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY07_MAPPED_VISUAL_PROOF01_RECOVERY01_POSTFLIGHT.json'
$profileFile = Join-Path $isolatedRoot 'Saved\Profiling\CSV\Recovery07MappedVisualProof01Recovery01.csv'
$timeoutSeconds = 540

$state = [ordered]@{
    schema = 'skyguard.t08.m01.recovery07-mapped-proof01-supervisor.v1'
    contract_id = $contractId
    gate = 'FAILED_WITH_EVIDENCE'
    started_utc = [DateTime]::UtcNow.ToString('o')
    ended_utc = $null
    failure_stage = $null
    failure_message = $null
    supervisor_launch_count = 1
    unreal_launch_count = 0
    adjudicator_launch_count = 0
    retry_count = 0
    unreal_started = $false
    unreal_pid = $null
    process_handle_retained = $false
    timed_out = $false
    actual_exit_code = $null
    actual_exit_code_type = $null
    postflight_exit_code = $null
    postflight_exit_code_type = $null
    peak_working_set_bytes = 0
    profile_files_before = @()
    profile_files_after = @()
    heavy_processes_before = @()
    world_save_requested = $false
    automatic_retry = $false
}
$exitCode = 1
$stage = 'initialize'
$process = $null

function Get-LowerSha256([string]$Path) {
    $stream = $null
    $algorithm = $null
    try {
        $stream = [System.IO.File]::Open($Path, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::Read)
        $algorithm = [System.Security.Cryptography.SHA256]::Create()
        $bytes = $algorithm.ComputeHash($stream)
        return ([System.BitConverter]::ToString($bytes)).Replace('-', '').ToLowerInvariant()
    }
    finally {
        if ($null -ne $algorithm) { $algorithm.Dispose() }
        if ($null -ne $stream) { $stream.Dispose() }
    }
}

function Write-JsonAtomic([string]$Path, $Value) {
    $parent = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $parent)) {
        [System.IO.Directory]::CreateDirectory($parent) | Out-Null
    }
    $temporary = "$Path.tmp.$PID"
    [System.IO.File]::WriteAllText(
        $temporary,
        (($Value | ConvertTo-Json -Depth 30) + [Environment]::NewLine),
        [System.Text.UTF8Encoding]::new($false)
    )
    [System.IO.File]::Move($temporary, $Path)
}

function Test-FrozenRecord($Record) {
    $absoluteProperty = $Record.PSObject.Properties['absolute_path']
    $fileProperty = $Record.PSObject.Properties['file']
    $path = if ($null -ne $absoluteProperty -and $absoluteProperty.Value) {
        [string]$absoluteProperty.Value
    }
    elseif ($null -ne $fileProperty -and $fileProperty.Value) {
        Join-Path $root ([string]$fileProperty.Value)
    }
    else { return $false }
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { return $false }
    $item = Get-Item -LiteralPath $path
    return ($item.Length -eq [long]$Record.bytes) -and ((Get-LowerSha256 $path) -eq [string]$Record.sha256)
}

function Get-HeavyProcesses {
    $names = @(
        'UnrealEditor', 'UnrealEditor-Cmd', 'ShaderCompileWorker', 'Blender',
        'AutomationTool', 'UnrealBuildTool', 'cl', 'link', 'msbuild'
    )
    return @(
        Get-Process -ErrorAction SilentlyContinue |
            Where-Object { $names -contains $_.ProcessName } |
            ForEach-Object {
                [ordered]@{ id = $_.Id; name = $_.ProcessName; start_time = if ($_.StartTime) { $_.StartTime.ToUniversalTime().ToString('o') } else { $null } }
            }
    )
}

function Get-ProfileInventory {
    $rootPath = Join-Path $isolatedRoot 'Saved\Profiling'
    if (-not (Test-Path -LiteralPath $rootPath)) { return @() }
    return @(
        Get-ChildItem -LiteralPath $rootPath -File -Recurse -ErrorAction SilentlyContinue |
            Sort-Object FullName |
            ForEach-Object {
                [ordered]@{
                    path = $_.FullName
                    bytes = $_.Length
                    sha256 = Get-LowerSha256 $_.FullName
                    last_write_utc = $_.LastWriteTimeUtc.ToString('o')
                }
            }
    )
}

function Assert-JsonObject([string]$Path) {
    $value = Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
    if ($null -eq $value) { throw "JSON did not parse as an object: $Path" }
    return $value
}

function Test-OfflineContract {
    foreach ($required in @($editor, $uproject, $executor, $adjudicator, $contract, $offlineFreeze, $bindingFreeze)) {
        if (-not (Test-Path -LiteralPath $required -PathType Leaf)) { throw "Missing offline authority: $required" }
    }
    $freeze = Assert-JsonObject $offlineFreeze
    $binding = Assert-JsonObject $bindingFreeze
    if ($freeze.classification -ne 'PASSED_READY_FOR_EXPLICIT_SINGLE_RECOVERY07_MAPPED_VISUAL_PROOF01_RECOVERY01_AUTHORIZATION') { throw 'Offline freeze classification mismatch' }
    if ($binding.classification -ne 'PASSED_READY_FOR_EXPLICIT_SINGLE_RECOVERY07_MAPPED_VISUAL_PROOF01_RECOVERY01_AUTHORIZATION') { throw 'Binding freeze classification mismatch' }
    foreach ($record in @($freeze.members) + @($binding.members)) {
        if (-not (Test-FrozenRecord $record)) {
            $identity = $record | ConvertTo-Json -Compress
            throw "Frozen member mismatch: $identity"
        }
    }
    foreach ($future in @($attemptRoot, $launcherRoot, $preflightReceipt, $terminalSupervisor, $emergencyReceipt, $postflightReport, $profileFile)) {
        if (Test-Path -LiteralPath $future) { throw "Future namespace exists: $future" }
    }
    $script = Get-Content -LiteralPath $PSCommandPath -Raw
    $startProcessNeedle = 'Start-Process -FilePath $' + 'editor'
    if ([regex]::Matches($script, [regex]::Escape($startProcessNeedle)).Count -ne 1) { throw 'Supervisor does not contain exactly one Unreal Start-Process path' }
    if ($script -notmatch '-ExecCmds=py') { throw 'Deferred Python ExecCmds path is absent' }
    $forbiddenPythonLifecycle = '-ExecutePython' + 'Script'
    if ($script -match [regex]::Escape($forbiddenPythonLifecycle)) { throw 'Forbidden commandlet Python lifecycle detected' }
    return [ordered]@{
        schema = 'skyguard.t08.m01.recovery07-mapped-proof01-offline-contract-test.v1'
        gate = 'PASS'
        contract_id = $contractId
        future_namespaces_absent = $true
        unreal_launch_count = 0
        retry_count = 0
    }
}

try {
    if ($OfflineContractTest -and $AuthorizeSingleUnrealProof) {
        [Console]::Error.WriteLine('Offline and authorized modes are mutually exclusive')
        $exitCode = 3
    }
    elseif ($OfflineContractTest) {
        $stage = 'offline_contract_test'
        $result = Test-OfflineContract
        if ($OfflineEvidenceRoot) {
            if (-not (Test-Path -LiteralPath $OfflineEvidenceRoot)) { [System.IO.Directory]::CreateDirectory($OfflineEvidenceRoot) | Out-Null }
            Write-JsonAtomic (Join-Path $OfflineEvidenceRoot 'offline_contract_test.json') $result
        }
        $result | ConvertTo-Json -Depth 10
        $state.gate = 'PASS_OFFLINE_CONTRACT_TEST'
        $exitCode = 0
    }
    elseif (-not $AuthorizeSingleUnrealProof) {
        [Console]::Error.WriteLine('Normal mode requires -AuthorizeSingleUnrealProof')
        $exitCode = 2
    }
    else {
        $stage = 'preflight_authority'
        $offlineResult = Test-OfflineContract
        $state.heavy_processes_before = @(Get-HeavyProcesses)
        if ($state.heavy_processes_before.Count -ne 0) {
            throw "Heavy processes are active: $($state.heavy_processes_before.name -join ', ')"
        }
        $state.profile_files_before = @(Get-ProfileInventory)
        $preflight = [ordered]@{
            schema = 'skyguard.t08.m01.recovery07-mapped-proof01-execution-preflight.v1'
            gate = 'PASS_READY_FOR_SINGLE_UNREAL_LAUNCH'
            created_utc = [DateTime]::UtcNow.ToString('o')
            contract_id = $contractId
            offline_contract = $offlineResult
            heavy_process_count = 0
            attempt_absent = -not (Test-Path -LiteralPath $attemptRoot)
            launcher_absent = -not (Test-Path -LiteralPath $launcherRoot)
            profile_target_absent = -not (Test-Path -LiteralPath $profileFile)
            unreal_launch_count = 0
            retry_count = 0
        }
        Write-JsonAtomic $preflightReceipt $preflight

        $stage = 'launcher_namespace'
        [System.IO.Directory]::CreateDirectory((Join-Path $launcherRoot 'logs')) | Out-Null
        $stdout = Join-Path $launcherRoot 'logs\recovery07_mapped_visual_proof01_recovery01.stdout.log'
        $stderr = Join-Path $launcherRoot 'logs\recovery07_mapped_visual_proof01_recovery01.stderr.log'
        $engineLog = Join-Path $launcherRoot 'logs\recovery07_mapped_visual_proof01_recovery01.engine.log'
        $processTree = Join-Path $launcherRoot 'process_tree_samples.jsonl'
        $postflightLog = Join-Path $launcherRoot 'logs\recovery07_mapped_visual_proof01_recovery01.postflight.log'
        $arguments = @(
            $uproject,
            $mapAsset,
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
            '-DisablePlugins=Fab,Bridge,EditorTelemetry,RuntimeTelemetry,EOSShared,SkyguardRecovery03,SkyguardRecovery03NativeRecovery01,SkyguardRecovery03NativeRecovery04,SkyguardRecovery03NativeRecovery05',
            '-ini:EditorSettings:[/Script/UnrealEd.AnalyticsPrivacySettings]:bSendUsageData=False',
            '-csvCategories=Global',
            '-csvGpuStats',
            '-csvNamedEvents',
            '-csvCompression=0',
            "-SkyguardRecovery07ProofContract=$contractId",
            "-SkyguardRecovery07ProofAttemptRoot=$($attemptRoot.Replace('\','/'))",
            "-ExecCmds=py $($executor.Replace('\','/'))",
            "-abslog=$engineLog"
        )

        $stage = 'unreal_launch'
        $process = Start-Process -FilePath $editor -ArgumentList $arguments -PassThru -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError $stderr
        $state.unreal_launch_count = 1
        $state.unreal_started = $true
        $state.unreal_pid = $process.Id
        $handle = $process.Handle
        $state.process_handle_retained = $null -ne $handle
        $deadline = [DateTime]::UtcNow.AddSeconds($timeoutSeconds)
        while (-not $process.HasExited -and [DateTime]::UtcNow -lt $deadline) {
            $process.Refresh()
            if (-not $process.HasExited -and $process.WorkingSet64 -gt $state.peak_working_set_bytes) {
                $state.peak_working_set_bytes = [long]$process.WorkingSet64
            }
            $children = @(
                Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
                    Where-Object { $_.ParentProcessId -eq $process.Id } |
                    Select-Object ProcessId, ParentProcessId, Name, CommandLine
            )
            $sample = [ordered]@{
                sampled_utc = [DateTime]::UtcNow.ToString('o')
                unreal_process_id = $process.Id
                unreal_has_exited = $process.HasExited
                working_set_bytes = if ($process.HasExited) { $null } else { $process.WorkingSet64 }
                children = $children
            }
            [System.IO.File]::AppendAllText($processTree, (($sample | ConvertTo-Json -Depth 8 -Compress) + [Environment]::NewLine), [System.Text.UTF8Encoding]::new($false))
            Start-Sleep -Seconds 2
        }
        if (-not $process.HasExited) {
            $state.timed_out = $true
            Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
            throw "Unreal proof exceeded the $timeoutSeconds-second supervisor timeout"
        }
        $process.WaitForExit()
        $process.Refresh()
        $childCode = $process.ExitCode
        if ($null -eq $childCode -or -not ($childCode -is [int])) { throw 'Unreal exit code is null or nonnumeric' }
        $state.actual_exit_code = [int]$childCode
        $state.actual_exit_code_type = $childCode.GetType().FullName
        if ($childCode -ne 0) { throw "Unreal proof returned exit code $childCode" }
        $terminalReceipt = Join-Path $attemptRoot 'terminal_receipt.json'
        if (-not (Test-Path -LiteralPath $terminalReceipt -PathType Leaf)) { throw 'Executor terminal receipt is absent' }
        $terminal = Assert-JsonObject $terminalReceipt
        if ($terminal.gate -ne 'PASS_CAPTURE_COMPLETE_PENDING_OFFLINE_ADJUDICATION') { throw "Executor terminal gate failed: $($terminal.gate)" }

        $stage = 'postflight_prewrite'
        $state.profile_files_after = @(Get-ProfileInventory)
        $state.gate = 'UNREAL_EXITED_AWAITING_POSTFLIGHT'
        $state.ended_utc = [DateTime]::UtcNow.ToString('o')
        Write-JsonAtomic $terminalSupervisor $state

        $stage = 'mandatory_postflight_adjudicator'
        $python = (Get-Command python -ErrorAction Stop).Source
        $state.adjudicator_launch_count = 1
        & $python $adjudicator --output $postflightReport *> $postflightLog
        $postflightCode = $LASTEXITCODE
        if ($null -eq $postflightCode -or -not ($postflightCode -is [int])) { throw 'Postflight exit code is null or nonnumeric' }
        $state.postflight_exit_code = [int]$postflightCode
        $state.postflight_exit_code_type = $postflightCode.GetType().FullName
        if ($postflightCode -ne 0) { throw "Mandatory postflight adjudicator returned exit code $postflightCode" }
        $postflight = Assert-JsonObject $postflightReport
        if ($postflight.classification -ne 'PASSED_AUTOMATIC_AWAITING_HUMAN_VISUAL_REVIEW') { throw "Postflight classification failed: $($postflight.classification)" }
        $state.gate = 'PASSED_AUTOMATIC_AWAITING_HUMAN_VISUAL_REVIEW'
        $exitCode = 0
    }
}
catch {
    $state.gate = 'FAILED_WITH_EVIDENCE'
    $state.failure_stage = $stage
    $state.failure_message = $_.Exception.Message
    if ($OfflineContractTest) {
        [Console]::Error.WriteLine("$stage`: $($_.Exception.Message)")
    }
    $exitCode = 1
}
finally {
    $state.ended_utc = [DateTime]::UtcNow.ToString('o')
    if (-not $OfflineContractTest -and $AuthorizeSingleUnrealProof) {
        try {
            Write-JsonAtomic $terminalSupervisor $state
        }
        catch {
            try {
                $parent = Split-Path -Parent $emergencyReceipt
                if (-not (Test-Path -LiteralPath $parent)) { [System.IO.Directory]::CreateDirectory($parent) | Out-Null }
                $emergency = [ordered]@{
                    schema = 'skyguard.t08.m01.recovery07-mapped-proof01-emergency.v1'
                    gate = 'FAILED_WITH_EVIDENCE'
                    created_utc = [DateTime]::UtcNow.ToString('o')
                    failure_stage = $stage
                    supervisor_failure = $state.failure_message
                    manifest_failure = $_.Exception.Message
                }
                [System.IO.File]::AppendAllText($emergencyReceipt, (($emergency | ConvertTo-Json -Compress) + [Environment]::NewLine), [System.Text.UTF8Encoding]::new($false))
            }
            catch {}
            $exitCode = 1
        }
    }
}

exit ([int]$exitCode)
