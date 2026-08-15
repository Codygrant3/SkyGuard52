param([switch]$AuthorizeSingleUnrealPreview, [switch]$OfflineContractTest)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$Root = 'D:\Skyguard52'
$Project = 'D:\SG52T08_ENV01\Skyguard52.uproject'
$MapAsset = '/Game/T08/GW02PreviewR02/Lvl_GW02_WindowPreview01_Recovery02'
$MapFile = 'D:\SG52T08_ENV01\Content\T08\GW02PreviewR02\Lvl_GW02_WindowPreview01_Recovery02.umap'
$Editor = 'D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe'
$Executor = Join-Path $Root 'Scripts\GrokProduction\capture_m01_window_recovery06_unrealready01_mapped_preview01_recovery04.py'
$PriorFreeze = Join-Path $Root 'Docs\AAA_Review\M01_WINDOW_RECOVERY06_UNREALREADY01_MAPPED_PREVIEW01_RECOVERY03_ATTEMPT01_TERMINAL_FREEZE.json'
$ImportFreeze = Join-Path $Root 'Docs\AAA_Review\M01_WINDOW_RECOVERY06_UNREALREADY01_REVERSIBLE_UNREAL_IMPORT01_RECOVERY02_ACCEPTANCE_FREEZE.json'
$Authorization = Join-Path $Root 'Production\standing_heavy_process_authorization.json'
$Attempt = Join-Path $Root 'Saved\BuildAttempts\M01_WINDOW_RECOVERY06_UNREALREADY01_MAPPED_PREVIEW01_RECOVERY04\attempt_01'
$Receipt = Join-Path $Attempt 'mapped_preview_receipt.json'
$Terminal = Join-Path $Root 'Saved\Reports\M01_WINDOW_RECOVERY06_UNREALREADY01_MAPPED_PREVIEW01_RECOVERY04_TERMINAL_SUPERVISOR.json'
$Emergency = Join-Path $Root 'Saved\Reports\M01_WINDOW_RECOVERY06_UNREALREADY01_MAPPED_PREVIEW01_RECOVERY04_EMERGENCY_RECEIPT.jsonl'
$TimeoutSeconds = 1800
$Expected = [ordered]@{
    $Executor = '92c4e8b1f6368b21d38bf8201592ecf417b332d523a3253fa29ef4499ad6f5c9'
    $PriorFreeze = 'a6a5b98dbb69825d33f6aa179820a4dbd830dc16b8cf8f568c5343b6c74f6d05'
    $ImportFreeze = '362579881b7df83bf32ce48a50e104f51149c08e3a1949b1894fad57a413b58c'
    $Authorization = '48277d7edd869cc2b841c3993e8f7599bec5291ddf23e9c442b33e09b870c089'
    $Project = '7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a'
    $MapFile = 'd83666579f4ef49b30daaed27fc8ba80ffec7af4b924b655998b440e56742c71'
    $Editor = 'de28527cc2dae4c235a0cea01a182913862c9dcd10c08b36dc8be342a7f62311'
}

function Get-Sha256([string]$Path) {
    $stream = $null
    $algorithm = $null
    try {
        $stream = [IO.File]::Open($Path, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::Read)
        $algorithm = [Security.Cryptography.SHA256]::Create()
        return ([BitConverter]::ToString($algorithm.ComputeHash($stream))).Replace('-', '').ToLowerInvariant()
    }
    finally {
        if ($null -ne $algorithm) { $algorithm.Dispose() }
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
    $names = @('Blender', 'UnrealEditor', 'UnrealEditor-Cmd', 'ShaderCompileWorker', 'AutomationTool', 'UnrealBuildTool', 'cl', 'link', 'dotnet')
    @(
        Get-Process -ErrorAction SilentlyContinue |
            Where-Object { $names -contains $_.ProcessName } |
            Select-Object ProcessName, Id, StartTime, CPU, WorkingSet64
    )
}

$State = [ordered]@{
    schema = 'skyguard.m01-window-recovery06-unrealready01.mapped-preview01-recovery04.supervisor.v1'
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
    exact_executable = $Editor
    exact_arguments = @()
    authorities = @()
    heavy_processes_before = @()
    process_samples = @()
    receipt = $null
    map = $null
    capture_inventory = @()
    runtime_promotion_performed = $false
}
$Exit = 1
$Process = $null

try {
    $State.failure_stage = 'preflight'
    foreach ($entry in $Expected.GetEnumerator()) {
        if (-not (Test-Path -LiteralPath $entry.Key -PathType Leaf)) { throw "Missing authority: $($entry.Key)" }
        if ((Get-Sha256 $entry.Key) -ne $entry.Value) { throw "Authority mismatch: $($entry.Key)" }
        $State.authorities += Get-Record $entry.Key
    }
    $standing = Get-Content -LiteralPath $Authorization -Raw | ConvertFrom-Json
    if ($standing.status -ne 'ACTIVE' -or $standing.execution_policy.per_run_user_authorization_required -ne $false) {
        throw 'Standing heavy-process authorization is inactive'
    }
    foreach ($future in @($Attempt, $Terminal, $Emergency)) {
        if (Test-Path -LiteralPath $future) { throw "Fresh Recovery04 namespace exists: $future" }
    }
    $syntax = & python -c "from pathlib import Path;p=Path(r'$Executor');compile(p.read_text(encoding='utf-8'),str(p),'exec');print('PASS')" 2>&1
    if ($LASTEXITCODE -ne 0 -or ($syntax -join "`n") -notmatch 'PASS') { throw "Executor syntax failed: $($syntax -join ' ')" }
    $script = Get-Content -LiteralPath $PSCommandPath -Raw
    if ([regex]::Matches($script, 'Start-Process -FilePath \$Editor').Count -ne 1) { throw 'Supervisor launch count contract changed' }
    if ($OfflineContractTest) {
        $State.classification = 'PASS_OFFLINE_CONTRACT'
        $State.failure_stage = $null
        $Exit = 0
        return
    }
    if (-not $AuthorizeSingleUnrealPreview) {
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
    $execCmd = '-ExecCmds="py ' + $Executor.Replace('\', '/') + '"'
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
        '-ini:EditorSettings:[/Script/UnrealEd.AnalyticsPrivacySettings]:bSendUsageData=False',
        $execCmd,
        "-abslog=$engineLog"
    )
    $State.exact_arguments = $arguments
    $State.failure_stage = 'launch'
    $Process = Start-Process -FilePath $Editor -ArgumentList $arguments -WorkingDirectory $Root -RedirectStandardOutput $stdout -RedirectStandardError $stderr -WindowStyle Hidden -PassThru
    $State.unreal_launch_count = 1
    $State.unreal_pid = [int]$Process.Id
    $null = $Process.Handle
    $State.process_handle_retained = $true
    $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
    $State.failure_stage = 'wait'
    while (-not $Process.HasExited) {
        $Process.Refresh()
        $sample = [ordered]@{
            utc = [DateTime]::UtcNow.ToString('o')
            pid = [int]$Process.Id
            working_set = [int64]$Process.WorkingSet64
            cpu_seconds = [double]$Process.TotalProcessorTime.TotalSeconds
        }
        $State.process_samples += $sample
        [IO.File]::AppendAllText($samples, (($sample | ConvertTo-Json -Compress) + [Environment]::NewLine), [Text.UTF8Encoding]::new($false))
        if ([DateTime]::UtcNow -ge $deadline) {
            $State.timed_out = $true
            try { $Process.Kill() } catch {}
            throw "Recovery04 preview exceeded $TimeoutSeconds seconds"
        }
        Start-Sleep -Seconds 2
    }
    $Process.WaitForExit()
    $Process.Refresh()
    $State.actual_exit_code = [int]$Process.ExitCode
    $State.actual_exit_code_type = $Process.ExitCode.GetType().FullName
    if ($Process.ExitCode -ne 0) { throw "Unreal returned exit code $($Process.ExitCode)" }

    $State.failure_stage = 'postflight'
    if (-not (Test-Path -LiteralPath $Receipt -PathType Leaf)) { throw 'Recovery04 preview receipt missing' }
    $payload = Get-Content -LiteralPath $Receipt -Raw | ConvertFrom-Json
    $State.receipt = Get-Record $Receipt
    if ($payload.classification -ne 'PASSED_RECOVERY04_AUTOMATIC_AWAITING_DIRECT_VISUAL_REVIEW') {
        throw "Unexpected receipt classification: $($payload.classification)"
    }
    if ([int]$payload.capture_count -ne 6) { throw 'Capture count changed' }
    if (-not [bool]$payload.map_unchanged -or -not [bool]$payload.accepted_source_tree_unchanged) {
        throw 'Accepted review authorities changed during capture'
    }
    $State.map = Get-Record $MapFile
    $State.capture_inventory = @($payload.captures | ForEach-Object { Get-Record $_.path })
    if ($State.capture_inventory.Count -ne 6) { throw 'PNG inventory changed' }
    if ([bool]$payload.runtime_promotion_performed -or [bool]$payload.world_saved) {
        throw 'Recovery04 preview exceeded its reversible boundary'
    }
    $State.classification = 'PASSED_RECOVERY04_AUTOMATIC_AWAITING_DIRECT_VISUAL_REVIEW'
    $State.failure_stage = $null
    $Exit = 0
}
catch {
    $State.classification = 'FAILED_WITH_EVIDENCE'
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
            [IO.Directory]::CreateDirectory((Split-Path -Parent $Emergency)) | Out-Null
            [IO.File]::AppendAllText(
                $Emergency,
                (([ordered]@{ utc = [DateTime]::UtcNow.ToString('o'); classification = $State.classification; message = $_.Exception.Message } | ConvertTo-Json -Compress) + [Environment]::NewLine),
                [Text.UTF8Encoding]::new($false)
            )
            $Exit = 1
        }
    }
}
[Environment]::Exit([int]$Exit)
