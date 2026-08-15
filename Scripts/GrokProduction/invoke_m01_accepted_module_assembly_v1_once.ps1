param(
    [switch]$AuthorizeSingleUnreal,
    [switch]$OfflineContractTest
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Root = 'D:\Skyguard52'
$Project = 'D:\Skyguard52\Skyguard52.uproject'
$Editor = 'D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$Author = Join-Path $Root 'Scripts\GrokProduction\author_m01_accepted_module_assembly_v1.py'
$Verifier = Join-Path $Root 'Scripts\GrokProduction\verify_m01_accepted_module_assembly_v1_offline.py'
$Contract = Join-Path $Root 'Docs\Toolchain\M01_ACCEPTED_MODULE_ASSEMBLY_REVERSIBLE_CONTRACT.json'
$Authorization = Join-Path $Root 'Production\standing_heavy_process_authorization.json'
$Playable = Join-Path $Root 'Content\Skyguard\Maps\Lvl_M01_CoastalIntercept_Playable_v1.umap'
$PriorFailedAttempt = Join-Path $Root 'Saved\BuildAttempts\M01_ACCEPTED_MODULE_ASSEMBLY_v1\attempt_01'
$Attempt = Join-Path $Root 'Saved\BuildAttempts\M01_ACCEPTED_MODULE_ASSEMBLY_v1_RECOVERY01\attempt_01'
$MapFile = Join-Path $Root 'Content\Skyguard\Maps\Assembly\Lvl_M01_AcceptedModuleAssembly_v1.umap'
$Receipt = Join-Path $Attempt 'assembly_receipt.json'
$Terminal = Join-Path $Root 'Saved\Reports\M01_ACCEPTED_MODULE_ASSEMBLY_V1_RECOVERY01_TERMINAL_SUPERVISOR.json'
$Emergency = Join-Path $Root 'Saved\Reports\M01_ACCEPTED_MODULE_ASSEMBLY_V1_RECOVERY01_EMERGENCY_RECEIPT.jsonl'
$PriorTerminal = Join-Path $Root 'Saved\Reports\M01_ACCEPTED_MODULE_ASSEMBLY_V1_TERMINAL_SUPERVISOR.json'
$TimeoutSeconds = 1800
$ExpectedPlayableBytes = 70545
$ExpectedPlayableSha256 = '9d2ca2e50b446f488926bdd8a29eca9fe33d62ec25656fc77ca55997f5a08afa'

function Get-Sha256([string]$Path) {
    $stream = $null
    $hasher = $null
    try {
        $stream = [IO.File]::Open($Path, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::Read)
        $hasher = [Security.Cryptography.SHA256]::Create()
        return ([BitConverter]::ToString($hasher.ComputeHash($stream))).Replace('-', '').ToLowerInvariant()
    }
    finally {
        if ($null -ne $hasher) { $hasher.Dispose() }
        if ($null -ne $stream) { $stream.Dispose() }
    }
}

function Get-Record([string]$Path) {
    $item = Get-Item -LiteralPath $Path -ErrorAction Stop
    [ordered]@{ path = $item.FullName; bytes = [int64]$item.Length; sha256 = Get-Sha256 $item.FullName }
}

function Write-JsonAtomic([string]$Path, [object]$Value) {
    $parent = Split-Path -Parent $Path
    [IO.Directory]::CreateDirectory($parent) | Out-Null
    $temporary = $Path + '.tmp.' + [Diagnostics.Process]::GetCurrentProcess().Id
    [IO.File]::WriteAllText($temporary, (($Value | ConvertTo-Json -Depth 40) + [Environment]::NewLine), [Text.UTF8Encoding]::new($false))
    if (Test-Path -LiteralPath $Path) { throw "Refusing to overwrite terminal evidence: $Path" }
    [IO.File]::Move($temporary, $Path)
}

function Get-HeavyProcesses {
    $exact = @('Blender', 'UnrealEditor', 'UnrealEditor-Cmd', 'ShaderCompileWorker', 'AutomationTool', 'UnrealBuildTool', 'cl', 'link', 'dotnet')
    @(Get-Process -ErrorAction SilentlyContinue | Where-Object {
            $exact -contains $_.ProcessName -or $_.ProcessName -like 'UnrealEditor*' -or $_.ProcessName -like 'ShaderCompileWorker*'
        } | Select-Object ProcessName, Id, StartTime, CPU, WorkingSet64)
}

$State = [ordered]@{
    schema = 'skyguard.m01-accepted-module-assembly.v1.supervisor.v1'
    classification = 'FAILED_WITH_EVIDENCE'
    started_utc = [DateTime]::UtcNow.ToString('o')
    ended_utc = $null
    failure_stage = 'initialization'
    failure_message = $null
    supervisor_launch_count = 1
    unreal_launch_count = 0
    retry_count = 0
    timed_out = $false
    actual_exit_code = $null
    actual_exit_code_type = $null
    unreal_pid = $null
    process_handle_retained = $false
    offline_contract_test = [bool]$OfflineContractTest
    exact_executable = $Editor
    exact_arguments = @()
    authorities = @()
    heavy_processes_before = @()
    process_samples = @()
    receipt = $null
    map = $null
    playable_before = $null
    playable_after = $null
    runtime_promotion_performed = $false
    blender_used = $false
}

$Exit = 1
try {
    $State.failure_stage = 'preflight'
    foreach ($path in @($Author, $Verifier, $Contract, $Authorization, $Project, $Editor, $Playable)) {
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Missing authority: $path" }
        $State.authorities += Get-Record $path
    }
    $State.playable_before = Get-Record $Playable
    if ([int64]$State.playable_before.bytes -ne $ExpectedPlayableBytes) {
        throw "Playable map bytes changed: $($State.playable_before.bytes)"
    }
    if ([string]$State.playable_before.sha256 -ne $ExpectedPlayableSha256) {
        throw "Playable map hash changed: $($State.playable_before.sha256)"
    }

    $standing = Get-Content -LiteralPath $Authorization -Raw | ConvertFrom-Json
    if ($standing.status -ne 'ACTIVE' -or $standing.execution_policy.per_run_user_authorization_required -ne $false) {
        throw 'Standing heavy-process authorization is not active.'
    }
    if ($standing.execution_policy.one_heavy_process_at_a_time -ne $true) {
        throw 'Standing authorization one_heavy_process_at_a_time is not true.'
    }
    if ([int]$standing.execution_policy.automatic_retry_count -ne 0) {
        throw 'Standing authorization automatic_retry_count is not zero.'
    }

    if (-not (Test-Path -LiteralPath $PriorFailedAttempt -PathType Container)) {
        throw "Prior failed attempt_01 evidence missing: $PriorFailedAttempt"
    }
    if (-not (Test-Path -LiteralPath $PriorTerminal -PathType Leaf)) {
        throw "Prior failed terminal evidence missing: $PriorTerminal"
    }
    if (Test-Path -LiteralPath $Attempt) { throw "Fresh Recovery01 attempt exists: $Attempt" }
    if (Test-Path -LiteralPath $Terminal) { throw "Fresh Recovery01 terminal exists: $Terminal" }
    if (Test-Path -LiteralPath $MapFile) { throw "Fresh assembly map exists: $MapFile" }

    $verify = & python $Verifier 2>&1
    if ($LASTEXITCODE -ne 0 -or ($verify -join "`n") -notmatch 'PASS_M01_ACCEPTED_MODULE_ASSEMBLY_V1_OFFLINE') {
        throw "Offline verifier failed: $($verify -join ' ')"
    }
    $syntax = & python -c "from pathlib import Path; p=Path(r'$Author'); compile(p.read_text(encoding='utf-8'), str(p), 'exec'); print('PASS')" 2>&1
    if ($LASTEXITCODE -ne 0 -or ($syntax -join "`n") -notmatch 'PASS') {
        throw "Author syntax failed: $($syntax -join ' ')"
    }
    $script = Get-Content -LiteralPath $PSCommandPath -Raw
    if ([regex]::Matches($script, 'Start-Process -FilePath \$Editor').Count -ne 1) {
        throw 'Supervisor does not contain exactly one Unreal launch path'
    }

    if ($OfflineContractTest) {
        $State.classification = 'PASS_OFFLINE_CONTRACT'
        $State.failure_stage = $null
        $State.ended_utc = [DateTime]::UtcNow.ToString('o')
        $offlineTerminal = Join-Path $Root 'Saved\Reports\M01_ACCEPTED_MODULE_ASSEMBLY_V1_RECOVERY01_OFFLINE_CONTRACT_TERMINAL.json'
        if (-not (Test-Path -LiteralPath $offlineTerminal)) {
            Write-JsonAtomic $offlineTerminal $State
        }
        Write-Output ($State | ConvertTo-Json -Depth 40)
        [Environment]::Exit([int]0)
    }

    if (-not $AuthorizeSingleUnreal) {
        $State.classification = 'REFUSED_MISSING_MECHANICAL_GUARD'
        $State.failure_stage = 'authorization'
        $Exit = 2
        return
    }

    $State.heavy_processes_before = @(Get-HeavyProcesses)
    if ($State.heavy_processes_before.Count -ne 0) {
        throw "Heavy process gate failed: $($State.heavy_processes_before.ProcessName -join ', ')"
    }

    # Quarantine Candidates folders before Unreal (Phase A also ensures them).
    foreach ($dir in @(
            (Join-Path $Root 'Content\Skyguard\Candidates\M01\WindowBayR06\StaticMeshes'),
            (Join-Path $Root 'Content\Skyguard\Candidates\M01\WindowBayR06\Materials'),
            (Join-Path $Root 'Content\Skyguard\Candidates\M01\CoastalCorridorC06R01\StaticMeshes'),
            (Join-Path $Root 'Content\Skyguard\Maps\Assembly')
        )) {
        [IO.Directory]::CreateDirectory($dir) | Out-Null
    }

    [IO.Directory]::CreateDirectory($Attempt) | Out-Null
    $stdout = Join-Path $Attempt 'unreal.stdout.log'
    $stderr = Join-Path $Attempt 'unreal.stderr.log'
    $engineLog = Join-Path $Attempt 'unreal.engine.log'
    $samples = Join-Path $Attempt 'process_tree_samples.jsonl'
    $arguments = @(
        $Project,
        '-Unattended',
        '-NoSplash',
        '-NoSound',
        '-NullRHI',
        '-stdout',
        '-FullStdOutLogOutput',
        '-nop4',
        '-DisablePlugins=Fab,Bridge,EditorTelemetry,RuntimeTelemetry,EOSShared',
        '-ini:EditorSettings:[/Script/UnrealEd.AnalyticsPrivacySettings]:bSendUsageData=False',
        "-ExecutePythonScript=$Author",
        '-ScriptErrorsAreFatal',
        "-abslog=$engineLog"
    )
    $State.exact_arguments = $arguments
    $State.failure_stage = 'launch'
    $process = Start-Process -FilePath $Editor -ArgumentList $arguments -WorkingDirectory $Root -RedirectStandardOutput $stdout -RedirectStandardError $stderr -WindowStyle Hidden -PassThru
    $State.unreal_launch_count = 1
    $State.unreal_pid = [int]$process.Id
    $null = $process.Handle
    $State.process_handle_retained = $true
    $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
    $State.failure_stage = 'wait'
    while (-not $process.HasExited) {
        $process.Refresh()
        $sample = [ordered]@{
            utc = [DateTime]::UtcNow.ToString('o')
            pid = [int]$process.Id
            working_set = [int64]$process.WorkingSet64
            cpu_seconds = [double]$process.TotalProcessorTime.TotalSeconds
        }
        $State.process_samples += $sample
        [IO.File]::AppendAllText($samples, (($sample | ConvertTo-Json -Compress) + [Environment]::NewLine), [Text.UTF8Encoding]::new($false))
        if ([DateTime]::UtcNow -ge $deadline) {
            $State.timed_out = $true
            try { $process.Kill() } catch {}
            throw "Accepted module assembly exceeded $TimeoutSeconds seconds."
        }
        Start-Sleep -Seconds 2
    }
    $process.WaitForExit()
    $process.Refresh()
    $State.actual_exit_code = [int]$process.ExitCode
    $State.actual_exit_code_type = $process.ExitCode.GetType().FullName
    $State.failure_stage = 'postflight'

    $State.playable_after = Get-Record $Playable
    if ([string]$State.playable_after.sha256 -ne $ExpectedPlayableSha256) {
        throw "Playable map was mutated during assembly: $($State.playable_after.sha256)"
    }

    if (-not (Test-Path -LiteralPath $Receipt -PathType Leaf)) {
        throw "Assembly receipt missing: $Receipt"
    }
    $State.receipt = Get-Record $Receipt
    $payload = Get-Content -LiteralPath $Receipt -Raw | ConvertFrom-Json
    if (Test-Path -LiteralPath $MapFile -PathType Leaf) {
        $State.map = Get-Record $MapFile
    }

    $classification = [string]$payload.classification
    if ($classification -like 'PASSED_*') {
        $State.classification = $classification
        $State.failure_stage = $null
        $Exit = 0
    }
    else {
        $State.classification = $classification
        $State.failure_message = [string]$payload.blocker
        if ([string]::IsNullOrWhiteSpace($State.failure_message)) {
            $State.failure_message = [string]$payload.error
        }
        $Exit = 1
    }
}
catch {
    $State.failure_message = "$_"
    try {
        [IO.File]::AppendAllText(
            $Emergency,
            (([ordered]@{ utc = [DateTime]::UtcNow.ToString('o'); error = "$_"; state = $State } | ConvertTo-Json -Compress -Depth 20) + [Environment]::NewLine),
            [Text.UTF8Encoding]::new($false)
        )
    }
    catch {}
    $Exit = 1
}
finally {
    $State.ended_utc = [DateTime]::UtcNow.ToString('o')
    try {
        if (-not (Test-Path -LiteralPath $Terminal)) {
            Write-JsonAtomic $Terminal $State
        }
    }
    catch {
        try {
            [IO.File]::AppendAllText(
                $Emergency,
                (([ordered]@{ utc = [DateTime]::UtcNow.ToString('o'); terminal_write_error = "$_"; state = $State } | ConvertTo-Json -Compress -Depth 20) + [Environment]::NewLine),
                [Text.UTF8Encoding]::new($false)
            )
        }
        catch {}
    }
}

Write-Output ($State | ConvertTo-Json -Depth 40)
[Environment]::Exit($Exit)
