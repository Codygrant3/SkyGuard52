param(
    [switch]$AuthorizeSingleUnreal,
    [switch]$OfflineContractTest
)

$ErrorActionPreference = 'Stop'
$Root = 'D:\Skyguard52'
$Project = 'D:\SG52T08_ENV01\Skyguard52.uproject'
$InputMap = 'D:\SG52T08_ENV01\Content\M01\Lvl_M01_VisibleEnvironmentKit02_VisualRemediation01_Recovery01.umap'
$OutputMap = 'D:\SG52T08_ENV01\Content\M01\Lvl_M01_VisibleEnvironmentKit02_PresentationRefinement01.umap'
$BlueMaterial = 'D:\SG52T08_ENV01\Content\M01\EnvKit02\M01_APARTMENT_A\Materials\M_ENV_Plaster_Blue_Weathered_2K.uasset'
$WarmMaterial = 'D:\SG52T08_ENV01\Content\M01\EnvKit02\M01_MIDRISE_B\Materials\M_ENV_Plaster_Warm_2K.uasset'
$Editor = 'D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$Author = Join-Path $Root 'Scripts\ToolchainWave08\environment_visible_kit_presentation_refinement01\author_m01_visible_environment_kit_presentation_refinement01.py'
$Verifier = Join-Path $Root 'Scripts\ToolchainWave08\environment_visible_kit_presentation_refinement01\verify_m01_visible_environment_kit_presentation_refinement01_offline.py'
$Contract = Join-Path $Root 'Docs\Toolchain\ToolchainWave08\M01VisibleEnvironmentPresentationRefinement01\execution_contract.json'
$MapAcceptance = Join-Path $Root 'Docs\AAA_Review\M01_VISIBLE_ENVIRONMENT_KIT_MAP_VISUAL_REMEDIATION01_RECOVERY01_ACCEPTANCE_FREEZE.json'
$FailedVisualFreeze = Join-Path $Root 'Docs\AAA_Review\M01_VISIBLE_ENVIRONMENT_KIT_MAP_VISUAL_REMEDIATION01_RECOVERY01_VISUAL_PROOF01_ATTEMPT01_TERMINAL_FREEZE.json'
$Authorization = Join-Path $Root 'Production\standing_heavy_process_authorization.json'
$Attempt = Join-Path $Root 'Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_PRESENTATION_REFINEMENT01\attempt_01'
$Receipt = Join-Path $Attempt 'authoring_receipt.json'
$Terminal = Join-Path $Root 'Saved\Reports\M01_VISIBLE_ENVIRONMENT_PRESENTATION_REFINEMENT01_TERMINAL_SUPERVISOR.json'
$Emergency = Join-Path $Root 'Saved\Reports\M01_VISIBLE_ENVIRONMENT_PRESENTATION_REFINEMENT01_EMERGENCY_RECEIPT.jsonl'
$TimeoutSeconds = 900

$Expected = [ordered]@{
    $Author = '2899658124ce2dbf66d6ac15551b6213745184df02958e835e5bc208d3785d7c'
    $Verifier = 'bb0dd6f908706465dcd815764bfabce31fcf60b7a62c95cb97595377d8e6bc51'
    $Contract = '5c4de841e32ff2dc974f10ec1872e266e0e5f9527c74ce7f71de62b3d38fdc91'
    $MapAcceptance = '5fd40cf5a17d2cefd4ae31416cd7ccf7280ac5e113f74323270cef6fda699028'
    $FailedVisualFreeze = '95b2185422c8744dba1ec6ed463b11d436c2b2783677459b13bd9a8f1bf0f8c4'
    $Authorization = '48277d7edd869cc2b841c3993e8f7599bec5291ddf23e9c442b33e09b870c089'
    $Project = '7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a'
    $InputMap = 'd5a134978dec578f2833647d95545d228928cd6d30aee86f69e51e69506c8669'
    $BlueMaterial = '8e42160fb7f272a53a73b14a2a6815287b4367fe64922ea958ff5a34fec3b865'
    $WarmMaterial = '2c5ff6e097120a278f3062f97bd61b80d9720c38f66959a92cb23e0ce80fefcf'
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
    return [ordered]@{
        path = $item.FullName
        bytes = [int64]$item.Length
        sha256 = Get-Sha256 $item.FullName
    }
}

function Write-JsonAtomic([string]$Path, [object]$Value) {
    $parent = Split-Path -Parent $Path
    [IO.Directory]::CreateDirectory($parent) | Out-Null
    $temporary = $Path + '.tmp.' + [Diagnostics.Process]::GetCurrentProcess().Id
    [IO.File]::WriteAllText(
        $temporary,
        (($Value | ConvertTo-Json -Depth 32) + [Environment]::NewLine),
        [Text.UTF8Encoding]::new($false)
    )
    if (Test-Path -LiteralPath $Path) { throw "Terminal namespace already exists: $Path" }
    [IO.File]::Move($temporary, $Path)
}

function Get-HeavyProcesses {
    $exact = @(
        'Blender', 'UnrealEditor', 'UnrealEditor-Cmd', 'ShaderCompileWorker',
        'AutomationTool', 'UnrealBuildTool', 'cl', 'link', 'dotnet'
    )
    return @(
        Get-Process -ErrorAction SilentlyContinue |
            Where-Object {
                $exact -contains $_.ProcessName -or
                $_.ProcessName -like 'UnrealEditor*' -or
                $_.ProcessName -like 'ShaderCompileWorker*'
            } |
            Select-Object ProcessName, Id, StartTime, CPU, WorkingSet64
    )
}

function Assert-Authorities {
    foreach ($entry in $Expected.GetEnumerator()) {
        if (-not (Test-Path -LiteralPath $entry.Key -PathType Leaf)) {
            throw "Missing authority: $($entry.Key)"
        }
        $actual = Get-Sha256 $entry.Key
        if ($actual -ne $entry.Value) {
            throw "Authority hash mismatch: $($entry.Key) expected=$($entry.Value) actual=$actual"
        }
    }
    $authorizationPayload = Get-Content -LiteralPath $Authorization -Raw | ConvertFrom-Json
    if ($authorizationPayload.status -ne 'ACTIVE' -or $authorizationPayload.execution_policy.per_run_user_authorization_required -ne $false) {
        throw 'Standing heavy-process authorization is not active.'
    }
}

if ($OfflineContractTest) {
    Assert-Authorities
    if (Test-Path -LiteralPath $OutputMap) { throw "Future output map exists: $OutputMap" }
    if (Test-Path -LiteralPath $Attempt) { throw "Future attempt exists: $Attempt" }
    if (Test-Path -LiteralPath $Terminal) { throw "Future terminal exists: $Terminal" }
    & python $Verifier
    if ($LASTEXITCODE -ne 0) { throw "Offline verifier failed: $LASTEXITCODE" }
    Write-Output 'PASS'
    [Environment]::Exit([int]0)
}

$State = [ordered]@{
    schema = 'skyguard.m01-visible-environment-presentation-refinement01.supervisor.v1'
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
    exact_executable = $Editor
    exact_arguments = @()
    working_directory = $Root
    authorities = @()
    heavy_processes_before = @()
    process_samples = @()
    receipt = $null
    output_map = $null
    input_map_unchanged = $false
}
$Exit = 1

try {
    $State.failure_stage = 'preflight'
    Assert-Authorities
    foreach ($entry in $Expected.GetEnumerator()) { $State.authorities += Get-Record $entry.Key }
    if (-not $AuthorizeSingleUnreal) {
        $State.classification = 'REFUSED_MISSING_MECHANICAL_GUARD'
        $State.failure_stage = 'authorization'
        $Exit = 2
        throw 'Mechanical one-shot guard was not supplied.'
    }
    if (Test-Path -LiteralPath $OutputMap) { throw "Fresh output namespace exists: $OutputMap" }
    if (Test-Path -LiteralPath $Attempt) { throw "Fresh attempt namespace exists: $Attempt" }
    if (Test-Path -LiteralPath $Terminal) { throw "Fresh terminal namespace exists: $Terminal" }
    if (Test-Path -LiteralPath $Emergency) { throw "Fresh emergency namespace exists: $Emergency" }
    $State.heavy_processes_before = @(Get-HeavyProcesses)
    if ($State.heavy_processes_before.Count -ne 0) {
        throw "Heavy process gate failed: $($State.heavy_processes_before.ProcessName -join ', ')"
    }

    [IO.Directory]::CreateDirectory($Attempt) | Out-Null
    $stdout = Join-Path $Attempt 'unreal.stdout.log'
    $stderr = Join-Path $Attempt 'unreal.stderr.log'
    $engineLog = Join-Path $Attempt 'unreal-engine.log'
    $samples = Join-Path $Attempt 'process_tree_samples.jsonl'
    $arguments = @(
        $Project,
        '-run=pythonscript',
        ('-script=' + $Author),
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
        $sample = [ordered]@{
            utc = [DateTime]::UtcNow.ToString('o')
            pid = [int]$process.Id
            working_set = [int64]$process.WorkingSet64
            cpu_seconds = [double]$process.TotalProcessorTime.TotalSeconds
        }
        $State.process_samples += $sample
        [IO.File]::AppendAllText(
            $samples,
            (($sample | ConvertTo-Json -Compress) + [Environment]::NewLine),
            [Text.UTF8Encoding]::new($false)
        )
        if ([DateTime]::UtcNow -ge $deadline) {
            $State.timed_out = $true
            try { $process.Kill() } catch {}
            throw "Unreal presentation refinement exceeded $TimeoutSeconds seconds."
        }
        Start-Sleep -Seconds 2
    }

    $process.WaitForExit()
    $process.Refresh()
    $State.actual_exit_code = [int]$process.ExitCode
    $State.actual_exit_code_type = $process.ExitCode.GetType().FullName
    if ($process.ExitCode -ne 0) { throw "Unreal returned exit code $($process.ExitCode)." }

    $State.failure_stage = 'postflight'
    if (-not (Test-Path -LiteralPath $Receipt -PathType Leaf)) { throw 'Authoring receipt missing.' }
    $payload = Get-Content -LiteralPath $Receipt -Raw | ConvertFrom-Json
    $State.receipt = Get-Record $Receipt
    if ($payload.classification -ne 'PASSED_M01_VISIBLE_ENVIRONMENT_PRESENTATION_REFINEMENT01_AUTOMATIC') {
        throw "Unexpected receipt classification: $($payload.classification)"
    }
    if ([int]$payload.actor_count_before -ne 179 -or [int]$payload.actor_count_after -ne 180) {
        throw 'Actor-count contract failed.'
    }
    if ([int]$payload.material_variation_count -ne 14 -or @($payload.material_variations).Count -ne 14) {
        throw 'Material-variation contract failed.'
    }
    if ($payload.fill_light.label -ne 'M01_PR01_FillSun' -or [Math]::Abs([double]$payload.fill_light.intensity - 2.75) -gt 0.001) {
        throw 'Fill-light contract failed.'
    }
    if ($payload.fill_light.cast_shadows -ne $false -or $payload.fill_light.atmosphere_sun_light -ne $false) {
        throw 'Fill-light shadow or atmosphere contract failed.'
    }
    if (-not (Test-Path -LiteralPath $OutputMap -PathType Leaf)) { throw 'Output map missing.' }
    if ((Get-Sha256 $OutputMap) -ne $payload.output_sha256) { throw 'Output map receipt hash mismatch.' }
    if ((Get-Sha256 $InputMap) -ne $Expected[$InputMap]) { throw 'Accepted input map changed.' }
    $State.output_map = Get-Record $OutputMap
    $State.input_map_unchanged = $true
    $State.classification = 'PASSED_M01_VISIBLE_ENVIRONMENT_PRESENTATION_REFINEMENT01_READY_FOR_MAPPED_VISUAL_PROOF'
    $State.failure_stage = $null
    $Exit = 0
}
catch {
    if ($State.classification -ne 'REFUSED_MISSING_MECHANICAL_GUARD') {
        $State.classification = 'FAILED_WITH_EVIDENCE'
    }
    $State.failure_message = $_.Exception.Message
}
finally {
    $State.ended_utc = [DateTime]::UtcNow.ToString('o')
    try {
        Write-JsonAtomic $Terminal $State
    }
    catch {
        $emergencyPayload = [ordered]@{
            utc = [DateTime]::UtcNow.ToString('o')
            classification = 'FAILED_WITH_EVIDENCE'
            terminal_write_error = $_.Exception.Message
            intended_terminal = $Terminal
            state = $State
        }
        [IO.Directory]::CreateDirectory((Split-Path -Parent $Emergency)) | Out-Null
        [IO.File]::AppendAllText(
            $Emergency,
            (($emergencyPayload | ConvertTo-Json -Depth 32 -Compress) + [Environment]::NewLine),
            [Text.UTF8Encoding]::new($false)
        )
        $Exit = 1
    }
}

[Environment]::Exit([int]$Exit)
