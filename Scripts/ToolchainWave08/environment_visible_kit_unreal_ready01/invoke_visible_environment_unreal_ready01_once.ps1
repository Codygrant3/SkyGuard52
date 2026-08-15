param(
    [switch]$AuthorizeSingleBlender,
    [switch]$OfflineContractTest
)

$ErrorActionPreference = 'Stop'
$Root = 'D:\Skyguard52'
$Blender = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
$SourceBlend = Join-Path $Root 'Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentProductionReset01_Checkpoint02\M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_CHECKPOINT02.blend'
$Generator = Join-Path $Root 'Scripts\ToolchainWave08\environment_visible_kit_unreal_ready01\build_visible_environment_unreal_ready01.py'
$Adjudicator = Join-Path $Root 'Scripts\ToolchainWave08\environment_visible_kit_unreal_ready01\adjudicate_visible_environment_unreal_ready01.py'
$Verifier = Join-Path $Root 'Scripts\ToolchainWave08\environment_visible_kit_unreal_ready01\verify_visible_environment_unreal_ready01_offline.py'
$Contract = Join-Path $Root 'Docs\Toolchain\ToolchainWave08\M01VisibleEnvironmentUnrealReady01\execution_contract.json'
$CheckpointFreeze = Join-Path $Root 'Docs\AAA_Review\M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_CHECKPOINT02_ACCEPTANCE_FREEZE.json'
$ProbeFreeze = Join-Path $Root 'Docs\AAA_Review\M01_VISIBLE_ENVIRONMENT_KIT_IMPORT_PROBE01_ACCEPTANCE_FREEZE.json'
$Authorization = Join-Path $Root 'Production\standing_heavy_process_authorization.json'
$OutputRoot = Join-Path $Root 'Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentProductionReset01_UnrealReady01'
$AttemptRoot = Join-Path $Root 'Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_UNREAL_READY01\attempt_01'
$TerminalManifest = Join-Path $Root 'Saved\Reports\M01_VISIBLE_ENVIRONMENT_UNREAL_READY01_TERMINAL_SUPERVISOR.json'
$EmergencyReceipt = Join-Path $Root 'Saved\Reports\M01_VISIBLE_ENVIRONMENT_UNREAL_READY01_EMERGENCY_RECEIPT.jsonl'
$Postflight = Join-Path $Root 'Saved\Reports\M01_VISIBLE_ENVIRONMENT_UNREAL_READY01_POSTFLIGHT.json'
$TimeoutSeconds = 1800

$Expected = [ordered]@{
    $SourceBlend = '0ef89cd08cb224f1d21015cfb1c968c1b66d8916c29c4702e129766a215093eb'
    $Generator = '9dc543d6443e35f12cb9d50e7d577f58d869447f7bdcdcd907389d94599eb21b'
    $Adjudicator = '8285d3e8640ed286618f2b37241e56445949b836c1d6dac9c5873e6269876262'
    $Verifier = '36c8450b348e9fa7729ab843cbac30f3890f809b3d33dec4bf67e6a9e821cdea'
    $Contract = 'a1a792b0fc567ca6b6c38d224839840ef61d202f3ee204ee3c0bf4dc2cd713c5'
    $CheckpointFreeze = 'efc54d13040f45efbabcb9e55d99754be161c15fc80804e5ea30440deb368284'
    $ProbeFreeze = '892a29460ca6e0872eca4bc58dbbd483bf619f0bf863a3ecad05b5e78e7a098a'
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
    schema = 'skyguard.m01-visible-environment-unreal-ready01-supervisor.v1'
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
