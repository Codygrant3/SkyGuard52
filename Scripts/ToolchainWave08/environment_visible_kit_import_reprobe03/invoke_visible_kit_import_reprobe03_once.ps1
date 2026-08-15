param(
    [switch]$AuthorizeSingleUnreal,
    [switch]$OfflineContractTest
)

$ErrorActionPreference = 'Stop'
$Root = 'D:\Skyguard52'
$Project = 'D:\SG52T08_ENV01\Skyguard52.uproject'
$Map = 'D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentRealismStack03.umap'
$Editor = 'D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$Probe = Join-Path $Root 'Scripts\ToolchainWave08\environment_visible_kit_import_reprobe03\probe_visible_kit_import_reprobe03.py'
$Verifier = Join-Path $Root 'Scripts\ToolchainWave08\environment_visible_kit_import_reprobe03\verify_visible_kit_import_reprobe03_offline.py'
$Contract = Join-Path $Root 'Docs\Toolchain\ToolchainWave08\M01VisibleEnvironmentKitImportReprobe03\execution_contract.json'
$Acceptance = Join-Path $Root 'Docs\AAA_Review\M01_VISIBLE_ENVIRONMENT_UNREAL_READY02_ACCEPTANCE_FREEZE.json'
$PriorProbe = Join-Path $Root 'Docs\AAA_Review\M01_VISIBLE_ENVIRONMENT_KIT_IMPORT_REPROBE02_ACCEPTANCE_FREEZE.json'
$Authorization = Join-Path $Root 'Production\standing_heavy_process_authorization.json'
$Source = Join-Path $Root 'Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentProductionReset01_UnrealReady02\exports\SM_M01_Apartment_Production_A_CONSOLIDATED.glb'
$Attempt = Join-Path $Root 'Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_KIT_IMPORT_REPROBE03\attempt_01'
$Terminal = Join-Path $Root 'Saved\Reports\M01_VISIBLE_ENVIRONMENT_KIT_IMPORT_REPROBE03_TERMINAL_SUPERVISOR.json'
$Emergency = Join-Path $Root 'Saved\Reports\M01_VISIBLE_ENVIRONMENT_KIT_IMPORT_REPROBE03_EMERGENCY_RECEIPT.jsonl'
$Destination = 'D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\VisibleKitImportReprobe03'
$Receipt = Join-Path $Attempt 'import_probe_receipt.json'
$TimeoutSeconds = 1800

$Expected = [ordered]@{
    $Probe = '31cc367550e26054908bb45435145efde80c989201ae7bd7a8ad4dc580d68bc9'
    $Verifier = '7fc5385d082ddcca91146b5595fdf01bb550d51844ca32de75d69b38d4731acd'
    $Contract = 'ea35e1db00a1c84d48681a3c9c921040c8fe4831e6a949b448cdf3edb9f3805f'
    $Acceptance = '9f0bce85b5011ca8b002e52fdb651fffe6adcb10f541c74583cc13599199dc20'
    $PriorProbe = '88b2ac171f48bca55b0643599c7e17137f740b3db15d4c708c42b7838916b202'
    $Authorization = '48277d7edd869cc2b841c3993e8f7599bec5291ddf23e9c442b33e09b870c089'
    $Source = '77b04f21f75f97b337eb89d142b5d672d9be5eaaa79184ee9f44421d35e51080'
    $Project = '7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a'
    $Map = 'c68de75000c25569f38b9307fd8760cce85236e2f3166785350ea0c641de81e8'
    $Editor = '0fb325cf215cc800ce260a1890af3f3dc314b8cc6331061d4e7e7246489af2e0'
}

function Get-Sha256([string]$Path) {
    $stream = $null
    $algorithm = $null
    try {
        $stream = [IO.File]::OpenRead($Path)
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
    return [ordered]@{ path = $item.FullName; bytes = [int64]$item.Length; sha256 = Get-Sha256 $item.FullName }
}

function Write-JsonAtomic([string]$Path, [object]$Value) {
    $parent = Split-Path -Parent $Path
    [IO.Directory]::CreateDirectory($parent) | Out-Null
    $temporary = $Path + '.tmp.' + [Diagnostics.Process]::GetCurrentProcess().Id
    [IO.File]::WriteAllText($temporary, (($Value | ConvertTo-Json -Depth 20) + [Environment]::NewLine), [Text.UTF8Encoding]::new($false))
    if (Test-Path -LiteralPath $Path) { throw "Terminal namespace already exists: $Path" }
    [IO.File]::Move($temporary, $Path)
}

function Get-HeavyProcesses {
    $exact = @('Blender','UnrealEditor','UnrealEditor-Cmd','ShaderCompileWorker','AutomationTool','UnrealBuildTool','cl','link','dotnet')
    return @(Get-Process -ErrorAction SilentlyContinue | Where-Object {
        $exact -contains $_.ProcessName -or $_.ProcessName -like 'UnrealEditor*' -or $_.ProcessName -like 'ShaderCompileWorker*'
    } | Select-Object ProcessName, Id, StartTime, CPU, WorkingSet64)
}

$State = [ordered]@{
    schema = 'skyguard.m01-visible-environment-kit-import-reprobe03.supervisor.v1'
    classification = 'FAILED_WITH_EVIDENCE'
    started_utc = [DateTime]::UtcNow.ToString('o')
    ended_utc = $null
    failure_stage = $null
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
    working_directory = $Root
    authorities = @()
    heavy_processes_before = @()
    process_samples = @()
    produced_files = @()
    receipt = $null
}

$Exit = 1
try {
    $State.failure_stage = 'preflight'
    foreach ($entry in $Expected.GetEnumerator()) {
        if (-not (Test-Path -LiteralPath $entry.Key -PathType Leaf)) { throw "Missing authority: $($entry.Key)" }
        $actual = Get-Sha256 $entry.Key
        if ($actual -ne $entry.Value) { throw "Authority hash mismatch: $($entry.Key) expected=$($entry.Value) actual=$actual" }
        $State.authorities += Get-Record $entry.Key
    }
    $authorizationObject = Get-Content -LiteralPath $Authorization -Raw | ConvertFrom-Json
    if ($authorizationObject.status -ne 'ACTIVE' -or $authorizationObject.execution_policy.per_run_user_authorization_required -ne $false) { throw 'Standing authorization is not active.' }
    if (Test-Path -LiteralPath $Attempt) { throw "Fresh attempt namespace exists: $Attempt" }
    if (Test-Path -LiteralPath $Terminal) { throw "Fresh terminal namespace exists: $Terminal" }
    if (Test-Path -LiteralPath $Destination) { throw "Fresh import destination exists: $Destination" }

    if ($OfflineContractTest) {
        $State.classification = 'PASS_OFFLINE_CONTRACT'
        $Exit = 0
        return
    }
    if (-not $AuthorizeSingleUnreal) {
        $State.classification = 'REFUSED_MISSING_MECHANICAL_GUARD'
        $Exit = 2
        return
    }

    $State.heavy_processes_before = @(Get-HeavyProcesses)
    if ($State.heavy_processes_before.Count -ne 0) { throw "Heavy process gate failed: $($State.heavy_processes_before.ProcessName -join ', ')" }
    [IO.Directory]::CreateDirectory($Attempt) | Out-Null
    $stdout = Join-Path $Attempt 'unreal.stdout.log'
    $stderr = Join-Path $Attempt 'unreal.stderr.log'
    $engineLog = Join-Path $Attempt 'unreal-engine.log'
    $samples = Join-Path $Attempt 'process_tree_samples.jsonl'
    $arguments = @(
        $Project,
        '-run=pythonscript',
        ('-script=' + $Probe),
        '-unattended',
        '-nop4',
        '-nosplash',
        '-nullrhi',
        '-NoSound',
        '-stdout',
        '-FullStdOutLogOutput',
        ('-abslog=' + $engineLog),
        '-DisablePlugins=Fab,Bridge,EditorTelemetry,RuntimeTelemetry,EOSShared',
        '-ini:EditorSettings:[/Script/UnrealEd.AnalyticsPrivacySettings]:bSendUsageData=False'
    )
    $State.exact_arguments = $arguments
    $State.failure_stage = 'launch'
    $process = Start-Process -FilePath $Editor -ArgumentList $arguments -WorkingDirectory $Root -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru
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
            try { $process.Kill() } catch { }
            throw "Unreal material-slot import re-probe exceeded $TimeoutSeconds seconds."
        }
        Start-Sleep -Seconds 2
    }
    $process.WaitForExit()
    $process.Refresh()
    $State.actual_exit_code = [int]$process.ExitCode
    $State.actual_exit_code_type = $process.ExitCode.GetType().FullName
    if ($process.ExitCode -ne 0) { throw "Unreal returned exit code $($process.ExitCode)." }

    $State.failure_stage = 'postflight'
    if (-not (Test-Path -LiteralPath $Receipt -PathType Leaf)) { throw 'Import re-probe receipt missing.' }
    $receiptObject = Get-Content -LiteralPath $Receipt -Raw | ConvertFrom-Json
    $State.receipt = Get-Record $Receipt
    if ($receiptObject.classification -ne 'PASSED_MATERIAL_SLOT_IMPORT_REPROBE_READY_FOR_FULL_KIT_IMPORT') { throw "Unexpected receipt classification: $($receiptObject.classification)" }
    if ([int]$receiptObject.static_mesh_count -ne 3) { throw "Unexpected StaticMesh count: $($receiptObject.static_mesh_count)" }
    if ([int]$receiptObject.material_slot_total -ne 13) { throw "Unexpected material-slot total: $($receiptObject.material_slot_total)" }
    if (-not (Test-Path -LiteralPath $Destination -PathType Container)) { throw 'Import destination was not created.' }
    $assets = @(Get-ChildItem -LiteralPath $Destination -Recurse -File -Filter '*.uasset')
    if ($assets.Count -lt 3) { throw 'Import destination contains too few uassets.' }
    $State.produced_files = @(Get-ChildItem -LiteralPath $Destination -Recurse -File | Sort-Object FullName | ForEach-Object { Get-Record $_.FullName })
    $State.classification = 'PASSED_MATERIAL_SLOT_IMPORT_REPROBE_READY_FOR_FULL_KIT_IMPORT'
    $State.failure_stage = $null
    $Exit = 0
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
        try { Write-JsonAtomic $Terminal $State }
        catch {
            $emergencyObject = [ordered]@{ utc = [DateTime]::UtcNow.ToString('o'); classification = $State.classification; stage = 'terminal_manifest_write'; message = $_.Exception.Message }
            [IO.Directory]::CreateDirectory((Split-Path -Parent $Emergency)) | Out-Null
            [IO.File]::AppendAllText($Emergency, (($emergencyObject | ConvertTo-Json -Compress) + [Environment]::NewLine), [Text.UTF8Encoding]::new($false))
            $Exit = 1
        }
    }
}

[Environment]::Exit([int]$Exit)
