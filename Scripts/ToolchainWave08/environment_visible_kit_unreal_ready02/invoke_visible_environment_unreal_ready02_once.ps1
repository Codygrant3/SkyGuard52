param(
    [switch]$AuthorizeSingleBlender,
    [switch]$OfflineContractTest
)

$ErrorActionPreference = 'Stop'
$Root = 'D:\Skyguard52'
$Blender = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
$SourceBlend = Join-Path $Root 'Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentProductionReset01_Checkpoint02\M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_CHECKPOINT02.blend'
$Generator = Join-Path $Root 'Scripts\ToolchainWave08\environment_visible_kit_unreal_ready02\build_visible_environment_unreal_ready02.py'
$Adjudicator = Join-Path $Root 'Scripts\ToolchainWave08\environment_visible_kit_unreal_ready02\adjudicate_visible_environment_unreal_ready02.py'
$Verifier = Join-Path $Root 'Scripts\ToolchainWave08\environment_visible_kit_unreal_ready02\verify_visible_environment_unreal_ready02_offline.py'
$Contract = Join-Path $Root 'Docs\Toolchain\ToolchainWave08\M01VisibleEnvironmentUnrealReady02\execution_contract.json'
$CheckpointFreeze = Join-Path $Root 'Docs\AAA_Review\M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_CHECKPOINT02_ACCEPTANCE_FREEZE.json'
$ProbeFreeze = Join-Path $Root 'Docs\AAA_Review\M01_VISIBLE_ENVIRONMENT_KIT_IMPORT_REPROBE02_ACCEPTANCE_FREEZE.json'
$Authorization = Join-Path $Root 'Production\standing_heavy_process_authorization.json'
$OutputRoot = Join-Path $Root 'Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentProductionReset01_UnrealReady02'
$AttemptRoot = Join-Path $Root 'Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_UNREAL_READY02\attempt_01'
$TerminalManifest = Join-Path $Root 'Saved\Reports\M01_VISIBLE_ENVIRONMENT_UNREAL_READY02_TERMINAL_SUPERVISOR.json'
$EmergencyReceipt = Join-Path $Root 'Saved\Reports\M01_VISIBLE_ENVIRONMENT_UNREAL_READY02_EMERGENCY_RECEIPT.jsonl'
$Postflight = Join-Path $Root 'Saved\Reports\M01_VISIBLE_ENVIRONMENT_UNREAL_READY02_POSTFLIGHT.json'
$TimeoutSeconds = 1800

$Expected = [ordered]@{
    $SourceBlend = '0ef89cd08cb224f1d21015cfb1c968c1b66d8916c29c4702e129766a215093eb'
    $Generator = '4a2c33e2e1ab656343996b0d17e17a3eb50058c0c8621c927916fc3320d1d158'
    $Adjudicator = 'a09eb76c72481b2bb74ff2006ee453c555198fb138bc6ca3d39abcc1398e6233'
    $Verifier = 'f6df9778e04b24ee9988e06706ca25494003f30a4a038f18d67a3344dd26888c'
    $Contract = '0dee50e3e3eedc992f2ef89bf3d75469f38ba169f8def1878791f411898b3866'
    $CheckpointFreeze = 'efc54d13040f45efbabcb9e55d99754be161c15fc80804e5ea30440deb368284'
    $ProbeFreeze = '88b2ac171f48bca55b0643599c7e17137f740b3db15d4c708c42b7838916b202'
    $Authorization = '48277d7edd869cc2b841c3993e8f7599bec5291ddf23e9c442b33e09b870c089'
    $Blender = 'e27fbfea8564aa645d4463cb0949695fd85562b9de6df9561b06859a1074adf7'
}

function Get-Sha256([string]$Path) {
    $stream = $null
    $algorithm = $null
    try {
        $stream = [System.IO.File]::Open($Path, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::Read)
        $algorithm = [System.Security.Cryptography.SHA256]::Create()
        return ([System.BitConverter]::ToString($algorithm.ComputeHash($stream))).Replace('-', '').ToLowerInvariant()
    }
    finally {
        if ($null -ne $algorithm) { $algorithm.Dispose() }
        if ($null -ne $stream) { $stream.Dispose() }
    }
}

function Get-FileRecord([string]$Path) {
    $item = Get-Item -LiteralPath $Path -ErrorAction Stop
    return [ordered]@{ path = $item.FullName; bytes = [int64]$item.Length; sha256 = Get-Sha256 $item.FullName }
}

function Write-JsonAtomic([string]$Path, $Payload) {
    $parent = Split-Path -Parent $Path
    [System.IO.Directory]::CreateDirectory($parent) | Out-Null
    $temp = $Path + '.tmp.' + [System.Diagnostics.Process]::GetCurrentProcess().Id
    $json = $Payload | ConvertTo-Json -Depth 30
    [System.IO.File]::WriteAllText($temp, $json + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
    if ([System.IO.File]::Exists($Path)) { throw "Terminal namespace already exists: $Path" }
    [System.IO.File]::Move($temp, $Path)
}

function Assert-Authority([string]$Path, [string]$Hash) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw "Missing authority: $Path" }
    $actual = Get-Sha256 $Path
    if ($actual -ne $Hash) { throw "Authority hash mismatch: $Path expected=$Hash actual=$actual" }
}

function Get-HeavyProcesses {
    $exact = @('Blender','UnrealEditor','UnrealEditor-Cmd','ShaderCompileWorker','AutomationTool','UnrealBuildTool','cl','link','dotnet')
    return @(Get-Process -ErrorAction SilentlyContinue | Where-Object {
        $exact -contains $_.ProcessName -or $_.ProcessName -like 'UnrealEditor*' -or $_.ProcessName -like 'ShaderCompileWorker*'
    } | Select-Object ProcessName, Id, StartTime, CPU, WorkingSet64)
}

$State = [ordered]@{
    schema = 'skyguard.m01-visible-environment-unreal-ready02-supervisor.v1'
    gate = 'RUNNING'
    started_utc = [DateTime]::UtcNow.ToString('o')
    ended_utc = $null
    failure_stage = $null
    failure_message = $null
    supervisor_launch_count = 1
    blender_launch_count = 0
    postflight_launch_count = 0
    retry_count = 0
    timed_out = $false
    actual_exit_code = $null
    actual_exit_code_type = $null
    postflight_exit_code = $null
    postflight_exit_code_type = $null
    blender_pid = $null
    process_handle_retained = $false
    offline_contract_test = [bool]$OfflineContractTest
    exact_executable = $Blender
    exact_arguments = @('--background',$SourceBlend,'--python',$Generator)
    working_directory = $Root
    authorities = @()
    heavy_processes_before = @()
    process_samples = @()
    produced_files = @()
    postflight_report = $null
}

$Exit = 1
try {
    foreach ($entry in $Expected.GetEnumerator()) {
        Assert-Authority $entry.Key $entry.Value
        $State.authorities += Get-FileRecord $entry.Key
    }
    $auth = Get-Content -LiteralPath $Authorization -Raw | ConvertFrom-Json
    if ($auth.status -ne 'ACTIVE' -or $auth.execution_policy.per_run_user_authorization_required -ne $false) { throw 'Standing authorization is not active.' }
    if (Test-Path -LiteralPath $OutputRoot) { throw "Fresh output namespace already exists: $OutputRoot" }
    if (Test-Path -LiteralPath $AttemptRoot) { throw "Fresh attempt namespace already exists: $AttemptRoot" }
    if (Test-Path -LiteralPath $TerminalManifest) { throw "Fresh terminal namespace already exists: $TerminalManifest" }
    if (Test-Path -LiteralPath $Postflight) { throw "Fresh postflight namespace already exists: $Postflight" }

    if ($OfflineContractTest) {
        $State.gate = 'PASS_OFFLINE_CONTRACT'
        $Exit = 0
        return
    }
    if (-not $AuthorizeSingleBlender) {
        $State.gate = 'REFUSED_MISSING_MECHANICAL_GUARD'
        $Exit = 2
        return
    }

    $State.failure_stage = 'preflight'
    $State.heavy_processes_before = @(Get-HeavyProcesses)
    if ($State.heavy_processes_before.Count -ne 0) { throw "Heavy process conflict: $($State.heavy_processes_before | ConvertTo-Json -Compress)" }
    [System.IO.Directory]::CreateDirectory($AttemptRoot) | Out-Null
    $stdout = Join-Path $AttemptRoot 'blender.stdout.log'
    $stderr = Join-Path $AttemptRoot 'blender.stderr.log'
    $samples = Join-Path $AttemptRoot 'process_tree_samples.jsonl'

    $State.failure_stage = 'blender_launch'
    $arguments = @('--background',$SourceBlend,'--python',$Generator)
    $process = Start-Process -FilePath $Blender -ArgumentList $arguments -WorkingDirectory $Root -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru
    $State.blender_launch_count = 1
    $State.blender_pid = [int]$process.Id
    $null = $process.Handle
    $State.process_handle_retained = $true
    $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
    while (-not $process.HasExited) {
        $process.Refresh()
        $sample = [ordered]@{ utc = [DateTime]::UtcNow.ToString('o'); pid = [int]$process.Id; working_set = [int64]$process.WorkingSet64; cpu_seconds = [double]$process.TotalProcessorTime.TotalSeconds }
        $State.process_samples += $sample
        [System.IO.File]::AppendAllText($samples, ($sample | ConvertTo-Json -Compress) + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
        if ([DateTime]::UtcNow -gt $deadline) {
            $State.timed_out = $true
            try { $process.Kill() } catch { }
            throw "Blender exceeded timeout of $TimeoutSeconds seconds."
        }
        Start-Sleep -Seconds 2
    }
    $process.WaitForExit()
    $process.Refresh()
    $State.actual_exit_code = [int]$process.ExitCode
    $State.actual_exit_code_type = $process.ExitCode.GetType().FullName
    if ($process.ExitCode -ne 0) { throw "Blender returned exit code $($process.ExitCode)." }
    if (-not (Test-Path -LiteralPath $OutputRoot -PathType Container)) { throw 'Blender exited zero without output namespace.' }

    $State.failure_stage = 'mandatory_postflight'
    $python = (Get-Command python -ErrorAction Stop).Source
    $State.postflight_launch_count = 1
    & $python $Adjudicator
    $postflightCode = [int]$LASTEXITCODE
    $State.postflight_exit_code = $postflightCode
    $State.postflight_exit_code_type = $postflightCode.GetType().FullName
    if ($postflightCode -ne 0) { throw "Mandatory postflight returned exit code $postflightCode." }
    if (-not (Test-Path -LiteralPath $Postflight -PathType Leaf)) { throw 'Postflight report missing.' }
    $State.postflight_report = Get-FileRecord $Postflight
    $State.produced_files = @(Get-ChildItem -LiteralPath $OutputRoot -Recurse -File | Sort-Object FullName | ForEach-Object { Get-FileRecord $_.FullName })
    $State.gate = 'PASSED_AUTOMATIC_AWAITING_DIRECT_VISUAL_AND_UNREAL_IMPORT_REPROBE'
    $State.failure_stage = $null
    $Exit = 0
}
catch {
    $State.gate = 'FAILED_WITH_EVIDENCE'
    if ($null -eq $State.failure_stage) { $State.failure_stage = 'supervisor' }
    $State.failure_message = $_.Exception.Message
    $Exit = 1
}
finally {
    $State.ended_utc = [DateTime]::UtcNow.ToString('o')
    if (-not $OfflineContractTest) {
        try { Write-JsonAtomic $TerminalManifest $State }
        catch {
            $emergency = [ordered]@{ utc = [DateTime]::UtcNow.ToString('o'); gate = $State.gate; failure_stage = 'terminal_manifest_write'; message = $_.Exception.Message }
            [System.IO.Directory]::CreateDirectory((Split-Path -Parent $EmergencyReceipt)) | Out-Null
            [System.IO.File]::AppendAllText($EmergencyReceipt, ($emergency | ConvertTo-Json -Compress) + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
            $Exit = 1
        }
    }
}

[Environment]::Exit([int]$Exit)
