[CmdletBinding()]
param(
    [switch]$AuthorizeSingleUnreal,
    [switch]$OfflineContractTest
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Root = 'D:\Skyguard52'
$Project = Join-Path $Root 'Skyguard52.uproject'
$Editor = 'D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$Author = Join-Path $Root 'Scripts\GrokProduction\polish_hero_proxy_materials.py'
$Authorization = Join-Path $Root 'Production\standing_heavy_process_authorization.json'
$HeroRoot = Join-Path $Root 'Content\Skyguard\Meshes\Hero'
$Attempt = Join-Path $Root 'Saved\BuildAttempts\HERO_PROXY_MATERIAL_POLISH01\attempt_01'
$Receipt = Join-Path $Attempt 'material_polish_receipt.json'
$Terminal = Join-Path $Root 'Saved\Reports\HERO_PROXY_MATERIAL_POLISH01_TERMINAL_SUPERVISOR.json'
$Emergency = Join-Path $Root 'Saved\Reports\HERO_PROXY_MATERIAL_POLISH01_EMERGENCY_RECEIPT.jsonl'
$TimeoutSeconds = 1800

function Get-Sha256([string]$Path) {
    $stream = $null; $hasher = $null
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
    [IO.Directory]::CreateDirectory((Split-Path -Parent $Path)) | Out-Null
    $temporary = $Path + '.tmp.' + [Diagnostics.Process]::GetCurrentProcess().Id
    [IO.File]::WriteAllText($temporary, (($Value | ConvertTo-Json -Depth 50) + [Environment]::NewLine), [Text.UTF8Encoding]::new($false))
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
    schema = 'skyguard.hero-proxy-material-polish01.supervisor.v1'
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
    material_inventory = @()
}

$Exit = 1
$AttemptStarted = $false
try {
    $State.failure_stage = 'preflight'
    foreach ($path in @($Project, $Editor, $Author, $Authorization)) {
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Missing authority: $path" }
        $State.authorities += Get-Record $path
    }
    if (-not (Test-Path -LiteralPath $HeroRoot -PathType Container)) { throw "Hero mesh root missing: $HeroRoot" }
    $standing = Get-Content -LiteralPath $Authorization -Raw | ConvertFrom-Json
    if ($standing.status -ne 'ACTIVE' -or $standing.execution_policy.per_run_user_authorization_required -ne $false) {
        throw 'Standing heavy-process authorization is not active.'
    }
    if ($standing.execution_policy.one_heavy_process_at_a_time -ne $true -or [int]$standing.execution_policy.automatic_retry_count -ne 0) {
        throw 'Standing authorization process/retry policy is invalid.'
    }
    if (Test-Path -LiteralPath $Attempt) { throw "Fresh attempt namespace exists: $Attempt" }
    if (Test-Path -LiteralPath $Terminal) { throw "Fresh terminal namespace exists: $Terminal" }

    $offlineOutput = & py -3 $Author --offline-contract-test 2>&1
    if ($LASTEXITCODE -ne 0 -or ($offlineOutput -join "`n") -notmatch 'PASS_HERO_PROXY_MATERIAL_POLISH01_OFFLINE_CONTRACT') {
        throw "Author offline contract failed: $($offlineOutput -join ' ')"
    }
    if ($OfflineContractTest) {
        $State.classification = 'PASS_OFFLINE_CONTRACT'
        $State.failure_stage = $null
        $State.ended_utc = [DateTime]::UtcNow.ToString('o')
        $Exit = 0
        $State | ConvertTo-Json -Depth 50 | Write-Output
        [Environment]::Exit([int]0)
    }
    if (-not $AuthorizeSingleUnreal) {
        $State.classification = 'REFUSED_MISSING_MECHANICAL_GUARD'
        $State.failure_stage = 'authorization'
        $State.failure_message = 'Supply -AuthorizeSingleUnreal after readiness passes.'
        $State.ended_utc = [DateTime]::UtcNow.ToString('o')
        $Exit = 2
        $State | ConvertTo-Json -Depth 50 | Write-Output
        [Environment]::Exit([int]2)
    }
    $State.heavy_processes_before = @(Get-HeavyProcesses)
    if ($State.heavy_processes_before.Count -ne 0) {
        throw "Heavy process gate failed: $($State.heavy_processes_before.ProcessName -join ', ')"
    }

    [IO.Directory]::CreateDirectory($Attempt) | Out-Null
    $AttemptStarted = $true
    $stdout = Join-Path $Attempt 'unreal.stdout.log'
    $stderr = Join-Path $Attempt 'unreal.stderr.log'
    $engineLog = Join-Path $Attempt 'unreal.engine.log'
    $samples = Join-Path $Attempt 'process_tree_samples.jsonl'
    $arguments = @(
        $Project, '-Unattended', '-NoSplash', '-NoSound', '-NullRHI', '-stdout',
        '-FullStdOutLogOutput', '-nop4',
        '-DisablePlugins=Fab,Bridge,EditorTelemetry,RuntimeTelemetry,EOSShared',
        '-ini:EditorSettings:[/Script/UnrealEd.AnalyticsPrivacySettings]:bSendUsageData=False',
        "-ExecutePythonScript=$Author", '-ScriptErrorsAreFatal', "-abslog=$engineLog"
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
        $sample = [ordered]@{ utc = [DateTime]::UtcNow.ToString('o'); pid = [int]$process.Id; working_set = [int64]$process.WorkingSet64; cpu_seconds = [double]$process.TotalProcessorTime.TotalSeconds }
        $State.process_samples += $sample
        [IO.File]::AppendAllText($samples, (($sample | ConvertTo-Json -Compress) + [Environment]::NewLine), [Text.UTF8Encoding]::new($false))
        if ([DateTime]::UtcNow -ge $deadline) {
            $State.timed_out = $true
            try { $process.Kill() } catch {}
            throw "Unreal Hero proxy material polish exceeded $TimeoutSeconds seconds."
        }
        Start-Sleep -Seconds 2
    }
    $process.WaitForExit(); $process.Refresh()
    $State.actual_exit_code = [int]$process.ExitCode
    $State.actual_exit_code_type = $process.ExitCode.GetType().FullName
    if ($State.actual_exit_code -ne 0) { throw "Unreal returned exit code $($State.actual_exit_code)." }

    $State.failure_stage = 'postflight'
    if (-not (Test-Path -LiteralPath $Receipt -PathType Leaf)) { throw "Hero proxy material receipt missing: $Receipt" }
    $payload = Get-Content -LiteralPath $Receipt -Raw | ConvertFrom-Json
    $State.receipt = Get-Record $Receipt
    if ($payload.classification -ne 'PASSED_HERO_PROXY_MATERIAL_POLISH01_AWAITING_REVIEW') {
        throw "Unexpected proxy material classification: $($payload.classification) error=$($payload.error)"
    }
    if ([int]$payload.matched_mesh_count -lt 1 -or @($payload.assignments).Count -ne [int]$payload.matched_mesh_count) {
        throw 'Hero proxy material assignment count failed postflight.'
    }
    $materialRootDisk = Join-Path $HeroRoot 'Materials'
    if (-not (Test-Path -LiteralPath $materialRootDisk -PathType Container)) { throw 'Hero proxy material directory missing after authoring.' }
    $State.material_inventory = @(Get-ChildItem -LiteralPath $materialRootDisk -File | Sort-Object Name | ForEach-Object { Get-Record $_.FullName })
    $State.classification = [string]$payload.classification
    $State.failure_stage = $null
    $Exit = 0
}
catch {
    $State.failure_message = $_.Exception.Message
    $Exit = 1
}
finally {
    $State.ended_utc = [DateTime]::UtcNow.ToString('o')
    if (-not $OfflineContractTest) {
        try {
            Write-JsonAtomic $Terminal $State
            if ($AttemptStarted) { Write-JsonAtomic (Join-Path $Attempt 'terminal_supervisor.json') $State }
        }
        catch {
            try {
                [IO.Directory]::CreateDirectory((Split-Path -Parent $Emergency)) | Out-Null
                [IO.File]::AppendAllText($Emergency, (([ordered]@{ utc = [DateTime]::UtcNow.ToString('o'); error = $_.Exception.Message; state = $State } | ConvertTo-Json -Compress -Depth 20) + [Environment]::NewLine), [Text.UTF8Encoding]::new($false))
            } catch {}
            $Exit = 1
        }
    }
}

$State | ConvertTo-Json -Depth 50
[Environment]::Exit([int]$Exit)
