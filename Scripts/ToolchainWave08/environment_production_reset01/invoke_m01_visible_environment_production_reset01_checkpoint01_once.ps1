param(
    [switch]$AuthorizeSingleBlender,
    [switch]$OfflineContractTest
)

$ErrorActionPreference = 'Stop'
$Root = 'D:\Skyguard52'
$Blender = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
$Generator = Join-Path $Root 'Scripts\ToolchainWave08\environment_production_reset01\build_m01_visible_environment_production_reset01_checkpoint01.py'
$Adjudicator = Join-Path $Root 'Scripts\ToolchainWave08\environment_production_reset01\adjudicate_m01_visible_environment_production_reset01_checkpoint01.py'
$Verifier = Join-Path $Root 'Scripts\ToolchainWave08\environment_production_reset01\verify_m01_visible_environment_production_reset01_checkpoint01_offline.py'
$Contract = Join-Path $Root 'Docs\Toolchain\ToolchainWave08\M01VisibleEnvironmentProductionReset01Checkpoint01\execution_contract.json'
$Authorization = Join-Path $Root 'Production\standing_heavy_process_authorization.json'
$OutputRoot = Join-Path $Root 'Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentProductionReset01_Checkpoint01'
$AttemptRoot = Join-Path $Root 'Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_CHECKPOINT01\attempt_01'
$TerminalManifest = Join-Path $Root 'Saved\Reports\M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_CHECKPOINT01_TERMINAL_SUPERVISOR.json'
$EmergencyReceipt = Join-Path $Root 'Saved\Reports\M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_CHECKPOINT01_EMERGENCY_RECEIPT.jsonl'
$TimeoutSeconds = 1200

$Expected = [ordered]@{
    $Generator = 'fefa08e50cb9e78d8d5a3965635d8f065df251d8861c777821c2a88d64eaf891'
    $Adjudicator = '7b74c7d08a0918172b064553865dbd9d1868fca4e56f38be5f2e659c4046b440'
    $Verifier = 'f81dad2cc122d2708023882701360f0fa9fdcdf1577b57470e690a18e55235db'
    $Contract = '31a497e335fa3ec75de9ad6b0f62dbf6ea61c3fbcf910d08f645c8544e7d351c'
    $Authorization = '48277d7edd869cc2b841c3993e8f7599bec5291ddf23e9c442b33e09b870c089'
    $Blender = 'e27fbfea8564aa645d4463cb0949695fd85562b9de6df9561b06859a1074adf7'
}

function Get-Sha256([string]$Path) {
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

function Get-FileRecord([string]$Path) {
    $item = Get-Item -LiteralPath $Path -ErrorAction Stop
    return [ordered]@{ path = $item.FullName; bytes = [int64]$item.Length; sha256 = Get-Sha256 $item.FullName }
}

function Write-JsonAtomic([string]$Path, $Payload) {
    $parent = Split-Path -Parent $Path
    [System.IO.Directory]::CreateDirectory($parent) | Out-Null
    $temp = $Path + '.tmp.' + [System.Diagnostics.Process]::GetCurrentProcess().Id
    $backup = $Path + '.atomic-backup'
    $json = $Payload | ConvertTo-Json -Depth 20
    [System.IO.File]::WriteAllText($temp, $json + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
    if ([System.IO.File]::Exists($Path)) {
        [System.IO.File]::Replace($temp, $Path, $backup)
        if ([System.IO.File]::Exists($backup)) { [System.IO.File]::Delete($backup) }
    }
    else {
        [System.IO.File]::Move($temp, $Path)
    }
}

function Assert-Authority([string]$Path, [string]$Hash) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw "Missing authority: $Path" }
    $actual = Get-Sha256 $Path
    if ($actual -ne $Hash) { throw "Authority hash mismatch: $Path expected=$Hash actual=$actual" }
}

function Get-HeavyProcesses {
    $exact = @('Blender','UnrealEditor','UnrealEditor-Cmd','ShaderCompileWorker','AutomationTool','UnrealBuildTool','cl','link')
    return @(Get-Process -ErrorAction SilentlyContinue | Where-Object {
        $exact -contains $_.ProcessName -or $_.ProcessName -like 'UnrealEditor*' -or $_.ProcessName -like 'ShaderCompileWorker*'
    } | Select-Object ProcessName, Id, StartTime, CPU, WorkingSet64)
}

$State = [ordered]@{
    schema = 'skyguard.m01-visible-environment-production-reset01.checkpoint01-supervisor.v1'
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
    output_root_created = $false
    governed_attempt_created = $false
    offline_contract_test = [bool]$OfflineContractTest
    exact_executable = $Blender
    exact_arguments = @('--background','--factory-startup','--python',$Generator)
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
    if ($auth.status -ne 'ACTIVE' -or $auth.execution_policy.per_run_user_authorization_required -ne $false) {
        throw 'Standing heavy-process authorization is not active.'
    }

    if ($OfflineContractTest) {
        if (Test-Path -LiteralPath $OutputRoot) { throw "Output namespace exists during offline test: $OutputRoot" }
        if (Test-Path -LiteralPath $AttemptRoot) { throw "Attempt namespace exists during offline test: $AttemptRoot" }
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
    if (Test-Path -LiteralPath $OutputRoot) { throw "Fresh output namespace already exists: $OutputRoot" }
    if (Test-Path -LiteralPath $AttemptRoot) { throw "Fresh attempt namespace already exists: $AttemptRoot" }
    if (Test-Path -LiteralPath $TerminalManifest) { throw "Fresh terminal manifest already exists: $TerminalManifest" }
    $State.heavy_processes_before = @(Get-HeavyProcesses)
    if ($State.heavy_processes_before.Count -ne 0) { throw "Heavy process conflict: $($State.heavy_processes_before | ConvertTo-Json -Compress)" }

    [System.IO.Directory]::CreateDirectory($AttemptRoot) | Out-Null
    $State.governed_attempt_created = $true
    $stdout = Join-Path $AttemptRoot 'blender.stdout.log'
    $stderr = Join-Path $AttemptRoot 'blender.stderr.log'
    $samples = Join-Path $AttemptRoot 'process_tree_samples.jsonl'

    $State.failure_stage = 'blender_launch'
    $arguments = @('--background','--factory-startup','--python',$Generator)
    $process = Start-Process -FilePath $Blender -ArgumentList $arguments -WorkingDirectory $Root -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru
    $State.blender_launch_count = 1
    $State.blender_pid = [int]$process.Id
    $null = $process.Handle
    $State.process_handle_retained = $true
    $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
    while (-not $process.HasExited) {
        $sample = [ordered]@{ utc = [DateTime]::UtcNow.ToString('o'); pid = [int]$process.Id; working_set = [int64]$process.WorkingSet64; cpu_seconds = [double]$process.TotalProcessorTime.TotalSeconds }
        $State.process_samples += $sample
        [System.IO.File]::AppendAllText($samples, ($sample | ConvertTo-Json -Compress) + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
        if ([DateTime]::UtcNow -gt $deadline) {
            $State.timed_out = $true
            try { $process.Kill() } catch { }
            throw "Blender exceeded timeout of $TimeoutSeconds seconds."
        }
        Start-Sleep -Milliseconds 1000
        $process.Refresh()
    }
    $process.WaitForExit()
    $process.Refresh()
    $State.actual_exit_code = [int]$process.ExitCode
    $State.actual_exit_code_type = $process.ExitCode.GetType().FullName
    if ($process.ExitCode -ne 0) { throw "Blender returned exit code $($process.ExitCode)." }
    $State.output_root_created = Test-Path -LiteralPath $OutputRoot -PathType Container
    if (-not $State.output_root_created) { throw 'Blender exited zero without creating the output namespace.' }

    $required = @(
        (Join-Path $OutputRoot 'M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_CHECKPOINT01.blend'),
        (Join-Path $OutputRoot 'production_checkpoint_receipt.json'),
        (Join-Path $OutputRoot 'artifact_inventory.json')
    )
    $required += @(Get-ChildItem -LiteralPath (Join-Path $OutputRoot 'exports') -Filter '*.glb' -File -ErrorAction Stop | Select-Object -ExpandProperty FullName)
    $required += @(Get-ChildItem -LiteralPath (Join-Path $OutputRoot 'renders') -Filter '*.png' -File -ErrorAction Stop | Select-Object -ExpandProperty FullName)
    if (@($required | Where-Object { -not (Test-Path -LiteralPath $_ -PathType Leaf) }).Count -ne 0) { throw 'One or more required outputs are missing.' }
    if (@($required | Where-Object { $_ -like '*.glb' }).Count -ne 5) { throw 'Expected exactly five GLB exports.' }
    if (@($required | Where-Object { $_ -like '*.png' }).Count -ne 4) { throw 'Expected exactly four review renders.' }

    $State.failure_stage = 'mandatory_postflight_adjudicator'
    $python = (Get-Command python -ErrorAction Stop).Source
    $State.postflight_launch_count = 1
    & $python $Adjudicator
    $postflightCode = [int]$LASTEXITCODE
    $State.postflight_exit_code = $postflightCode
    $State.postflight_exit_code_type = $postflightCode.GetType().FullName
    if ($postflightCode -ne 0) { throw "Mandatory postflight returned exit code $postflightCode." }
    $postflight = Join-Path $Root 'Saved\Reports\M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_CHECKPOINT01_POSTFLIGHT.json'
    if (-not (Test-Path -LiteralPath $postflight -PathType Leaf)) { throw 'Postflight report missing.' }
    $State.postflight_report = Get-FileRecord $postflight
    $State.produced_files = @(Get-ChildItem -LiteralPath $OutputRoot -Recurse -File | Sort-Object FullName | ForEach-Object { Get-FileRecord $_.FullName })
    $State.gate = 'PASSED_AUTOMATIC_AWAITING_DIRECT_FULL_RESOLUTION_VISUAL_REVIEW'
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
        try {
            Write-JsonAtomic $TerminalManifest $State
        }
        catch {
            $emergency = [ordered]@{ utc = [DateTime]::UtcNow.ToString('o'); gate = $State.gate; failure_stage = 'terminal_manifest_write'; message = $_.Exception.Message }
            [System.IO.Directory]::CreateDirectory((Split-Path -Parent $EmergencyReceipt)) | Out-Null
            [System.IO.File]::AppendAllText($EmergencyReceipt, ($emergency | ConvertTo-Json -Compress) + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
            $Exit = 1
        }
    }
}

[Environment]::Exit([int]$Exit)
