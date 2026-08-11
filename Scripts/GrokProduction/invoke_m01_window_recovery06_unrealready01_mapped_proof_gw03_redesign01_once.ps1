param(
    [switch]$AuthorizeSingleUnreal,
    [switch]$OfflineContractTest
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$Root = 'D:\Skyguard52'
$Project = 'D:\SG52T08_ENV01\Skyguard52.uproject'
$Editor = 'D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$Executor = Join-Path $Root 'Scripts\GrokProduction\author_and_capture_m01_window_recovery06_unrealready01_mapped_proof_gw03_redesign01.py'
$Contract = Join-Path $Root 'Docs\GrokProduction\Wave02\M01_WINDOW_RECOVERY06_UNREALREADY01_MAPPED_PROOF_GW03_REDESIGN01_CONTRACT.json'
$ImportFreeze = Join-Path $Root 'Docs\AAA_Review\M01_WINDOW_RECOVERY06_UNREALREADY01_REVERSIBLE_UNREAL_IMPORT01_RECOVERY02_ACCEPTANCE_FREEZE.json'
$Authorization = Join-Path $Root 'Production\standing_heavy_process_authorization.json'
$Attempt = Join-Path $Root 'Saved\BuildAttempts\M01_WINDOW_RECOVERY06_UNREALREADY01_MAPPED_PROOF_GW03_REDESIGN01\attempt_01'
$Receipt = Join-Path $Attempt 'mapped_proof_receipt.json'
$MapFile = 'D:\SG52T08_ENV01\Content\T08\GW03MappedProof01\Lvl_GW03_WindowMappedProof01.umap'
$Terminal = Join-Path $Root 'Saved\Reports\M01_WINDOW_RECOVERY06_UNREALREADY01_MAPPED_PROOF_GW03_REDESIGN01_TERMINAL_SUPERVISOR.json'
$Emergency = Join-Path $Root 'Saved\Reports\M01_WINDOW_RECOVERY06_UNREALREADY01_MAPPED_PROOF_GW03_REDESIGN01_EMERGENCY_RECEIPT.jsonl'
$TimeoutSeconds = 1200

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
    schema = 'skyguard.m01-window-recovery06-unrealready01.mapped-proof-gw03-redesign01.supervisor.v1'
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
    capture_inventory = @()
    runtime_promotion_performed = $false
    scene_capture_exposure_sweep_used = $false
    failed_harness_reused = $false
}
$Exit = 1

try {
    $State.failure_stage = 'preflight'
    foreach ($path in @($Executor, $Contract, $ImportFreeze, $Authorization, $Project, $Editor)) {
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Missing authority: $path" }
        $State.authorities += Get-Record $path
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
    if (Test-Path -LiteralPath $Attempt) { throw "Fresh GW03 attempt exists: $Attempt" }
    if (Test-Path -LiteralPath $Terminal) { throw "Fresh GW03 terminal exists: $Terminal" }
    if (Test-Path -LiteralPath $MapFile) { throw "Fresh GW03 map exists: $MapFile" }
    $syntax = & python -c "from pathlib import Path; p=Path(r'$Executor'); compile(p.read_text(encoding='utf-8'), str(p), 'exec'); print('PASS')" 2>&1
    if ($LASTEXITCODE -ne 0 -or ($syntax -join "`n") -notmatch 'PASS') {
        throw "GW03 Python syntax failed: $($syntax -join ' ')"
    }
    $script = Get-Content -LiteralPath $PSCommandPath -Raw
    if ([regex]::Matches($script, 'Start-Process -FilePath \$Editor').Count -ne 1) {
        throw 'Supervisor does not contain exactly one Unreal launch path'
    }
    if ($OfflineContractTest) {
        $State.classification = 'PASS_OFFLINE_CONTRACT'
        $State.failure_stage = $null
        $Exit = 0
        return
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

    [IO.Directory]::CreateDirectory($Attempt) | Out-Null
    $stdout = Join-Path $Attempt 'unreal.stdout.log'
    $stderr = Join-Path $Attempt 'unreal.stderr.log'
    $engineLog = Join-Path $Attempt 'unreal.engine.log'
    $samples = Join-Path $Attempt 'process_tree_samples.jsonl'
    $execCmdValue = "py $($Executor.Replace('\', '/'))"
    $execCmdArgument = '-ExecCmds="' + $execCmdValue + '"'
    $arguments = @(
        $Project,
        '-D3D12',
        '-sm6',
        '-RenderOffscreen',
        '-windowed',
        '-ResX=1920',
        '-ResY=1080',
        '-NoVSync',
        '-NoSound',
        '-NoSplash',
        '-unattended',
        '-nop4',
        '-DisablePlugins=Fab,Bridge,EditorTelemetry,RuntimeTelemetry,EOSShared',
        '-ini:EditorSettings:[/Script/UnrealEd.AnalyticsPrivacySettings]:bSendUsageData=False',
        $execCmdArgument,
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
            throw "GW03 mapped proof exceeded $TimeoutSeconds seconds."
        }
        Start-Sleep -Seconds 2
    }
    $process.WaitForExit()
    $process.Refresh()
    $State.actual_exit_code = [int]$process.ExitCode
    $State.actual_exit_code_type = $process.ExitCode.GetType().FullName

    $State.failure_stage = 'postflight'
    if (-not (Test-Path -LiteralPath $Receipt -PathType Leaf)) { throw 'GW03 mapped-proof receipt missing.' }
    $payload = Get-Content -LiteralPath $Receipt -Raw | ConvertFrom-Json
    $State.receipt = Get-Record $Receipt
    $classification = [string]$payload.classification
    if ($classification -eq 'PASSED_GW03_AUTOMATIC_AWAITING_DIRECT_D3D12_VISUAL_REVIEW') {
        if ([int]$payload.capture_count -lt 6) { throw 'GW03 capture count below contract minimum.' }
        if (-not (Test-Path -LiteralPath $MapFile -PathType Leaf)) { throw 'GW03 map is absent.' }
        if (-not [bool]$payload.accepted_source_tree_unchanged -or [bool]$payload.runtime_promotion_performed) {
            throw 'GW03 exceeded its isolated boundary.'
        }
        if ([bool]$payload.scene_capture_exposure_sweep_used -or [bool]$payload.failed_harness_reused) {
            throw 'GW03 reused a forbidden exposure-sweep harness.'
        }
        $State.map = Get-Record $MapFile
        $State.capture_inventory = @($payload.captures | ForEach-Object { Get-Record $_.path })
        $State.classification = $classification
        $State.failure_stage = $null
        $Exit = 0
    }
    elseif ($classification -eq 'STRUCTURAL_MAP_CREATED_VISUAL_GATE_BLOCKED') {
        if (-not (Test-Path -LiteralPath $MapFile -PathType Leaf)) { throw 'Structural classification without map file.' }
        $State.map = Get-Record $MapFile
        $State.classification = $classification
        $State.failure_message = [string]$payload.visual_gate_blocker
        $State.failure_stage = 'visual_gate'
        $Exit = 3
    }
    else {
        throw "Unexpected receipt classification: $classification"
    }
}
catch {
    $State.classification = 'FAILED_WITH_EVIDENCE'
    if ($null -eq $State.failure_stage) { $State.failure_stage = 'supervisor' }
    $State.failure_message = $_.Exception.Message
    $Exit = 1
}
finally {
    $State.ended_utc = [DateTime]::UtcNow.ToString('o')
    if (-not $OfflineContractTest) {
        try {
            Write-JsonAtomic $Terminal $State
        }
        catch {
            $emergencyObject = [ordered]@{
                utc = [DateTime]::UtcNow.ToString('o')
                classification = $State.classification
                stage = 'terminal_manifest_write'
                message = $_.Exception.Message
            }
            [IO.Directory]::CreateDirectory((Split-Path -Parent $Emergency)) | Out-Null
            [IO.File]::AppendAllText($Emergency, (($emergencyObject | ConvertTo-Json -Compress) + [Environment]::NewLine), [Text.UTF8Encoding]::new($false))
            $Exit = 1
        }
    }
}

[Environment]::Exit([int]$Exit)
