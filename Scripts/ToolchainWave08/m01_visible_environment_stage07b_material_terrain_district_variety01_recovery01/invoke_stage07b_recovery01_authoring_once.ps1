param(
    [switch]$OfflineContractTest,
    [switch]$AuthorizeSingleUnrealAuthoring
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Root = 'D:\Skyguard52'
$Project = 'D:\SG52T08_ENV01\Skyguard52.uproject'
$Editor = 'D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$InputMap = 'D:\SG52T08_ENV01\Content\M01\Lvl_M01_VisibleEnvironmentStage07AHeroCorridor01Correction01.umap'
$OutputMap = 'D:\SG52T08_ENV01\Content\M01\Lvl_M01_VisibleEnvironmentStage07BMaterialTerrainDistrictVariety01Recovery01.umap'
$Destination = 'D:\SG52T08_ENV01\Content\M01\VisibleEnvironmentStage07BMaterialTerrainDistrictVariety01Recovery01'
$StandingAuthorization = Join-Path $Root 'Production\standing_heavy_process_authorization.json'
$Author = Join-Path $Root 'Scripts\ToolchainWave08\m01_visible_environment_stage07b_material_terrain_district_variety01_recovery01\author_m01_visible_environment_stage07b_material_terrain_district_variety01_recovery01.py'
$Contract = Join-Path $Root 'Scripts\ToolchainWave08\m01_visible_environment_stage07b_material_terrain_district_variety01_recovery01\stage07b_recovery01_contract.json'
$AttemptRoot = Join-Path $Root 'Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_STAGE07B_MATERIAL_TERRAIN_DISTRICT_VARIETY01_RECOVERY01_AUTHORING01\attempt_01'
$Receipt = Join-Path $AttemptRoot 'authoring_receipt.json'
$TerminalManifest = Join-Path $Root 'Saved\Reports\M01_VISIBLE_ENVIRONMENT_STAGE07B_MATERIAL_TERRAIN_DISTRICT_VARIETY01_RECOVERY01_AUTHORING01_TERMINAL_MANIFEST.json'
$EmergencyReceipt = Join-Path $Root 'Saved\Reports\M01_VISIBLE_ENVIRONMENT_STAGE07B_MATERIAL_TERRAIN_DISTRICT_VARIETY01_RECOVERY01_AUTHORING01_EMERGENCY_RECEIPT.jsonl'
$TimeoutSeconds = 1800

function Get-Sha256([string]$Path) {
    $stream = [System.IO.File]::Open($Path, 'Open', 'Read', 'Read')
    $hasher = [System.Security.Cryptography.SHA256]::Create()
    try {
        return ([BitConverter]::ToString($hasher.ComputeHash($stream))).Replace('-', '').ToLowerInvariant()
    }
    finally {
        $hasher.Dispose()
        $stream.Dispose()
    }
}

function Get-FileRecord([string]$Path) {
    $item = [IO.FileInfo]::new($Path)
    return [ordered]@{ path = $Path; bytes = [int64]$item.Length; sha256 = Get-Sha256 $Path }
}

function Assert-FileRecord([object]$Spec, [string]$Label) {
    $pathProperty = $Spec.PSObject.Properties['path']
    $fileProperty = $Spec.PSObject.Properties['file']
    if ($null -ne $pathProperty) { $path = [string]$pathProperty.Value }
    elseif ($null -ne $fileProperty) { $path = [string]$fileProperty.Value }
    else { throw "$Label record contains neither path nor file" }
    if (-not [IO.File]::Exists($path)) { throw "$Label missing: $path" }
    $item = [IO.FileInfo]::new($path)
    if ($item.Length -ne [int64]$Spec.bytes) { throw "$Label byte mismatch: $path" }
    $actual = Get-Sha256 $path
    if ($actual -ne [string]$Spec.sha256) { throw "$Label hash mismatch: $path" }
}

function Write-JsonAtomic([string]$Path, [object]$Payload) {
    [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($Path)) | Out-Null
    $temporary = "$Path.tmp"
    [IO.File]::WriteAllText($temporary, ($Payload | ConvertTo-Json -Depth 64) + [Environment]::NewLine, [Text.UTF8Encoding]::new($false))
    [IO.File]::Move($temporary, $Path)
}

function Get-HeavyProcesses {
    return @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {
        $_.Name -match '^(UnrealEditor(-Cmd)?|Blender|ShaderCompileWorker|AutomationTool|UnrealBuildTool|cl|link|dotnet)(\.exe)?$'
    } | Select-Object ProcessId, Name, CommandLine)
}

function Assert-Authorities {
    if (-not [IO.File]::Exists($Contract)) { throw "Contract missing: $Contract" }
    $contractObject = Get-Content -LiteralPath $Contract -Raw | ConvertFrom-Json
    Assert-FileRecord $contractObject.input 'Stage 7A Correction01 map'
    foreach ($spec in $contractObject.authorities) { Assert-FileRecord $spec 'Stage7B authority' }
    foreach ($path in @($Project, $Editor, $StandingAuthorization, $Author, $Contract, $InputMap)) {
        if (-not [IO.File]::Exists($path)) { throw "Required Stage7B file missing: $path" }
    }
    $standing = Get-Content -LiteralPath $StandingAuthorization -Raw | ConvertFrom-Json
    if ($standing.status -ne 'ACTIVE' -or $standing.execution_policy.per_run_user_authorization_required -ne $false) {
        throw 'Standing heavy-process authorization is inactive'
    }
}

function Assert-Fresh {
    foreach ($path in @($OutputMap, $Destination, $AttemptRoot, $TerminalManifest, $EmergencyReceipt)) {
        if (Test-Path -LiteralPath $path) { throw "Fresh namespace already exists: $path" }
    }
}

if ($OfflineContractTest) {
    Assert-Authorities
    Assert-Fresh
    if (@(Get-HeavyProcesses).Count -ne 0) { throw 'Heavy process active during offline test' }
    & python $Author --offline-contract-test
    if ($LASTEXITCODE -ne 0) { throw "Python offline contract failed: $LASTEXITCODE" }
    [ordered]@{
        classification = 'PASSED_OFFLINE_READY_FOR_SINGLE_STAGE07B_RECOVERY01_AUTHORING'
        unreal_launch_count = 0
        governed_namespaces_created = 0
    } | ConvertTo-Json
    [Environment]::Exit([int]0)
}

$state = [ordered]@{
    schema = 'skyguard.m01-visible-environment-stage07b-material-terrain-district-variety01.recovery01-authoring01.supervisor.v1'
    classification = 'FAILED_WITH_EVIDENCE'
    started_at_utc = [DateTime]::UtcNow.ToString('o')
    completed_at_utc = $null
    stage = 'initialization'
    executable = $Editor
    arguments = @()
    working_directory = 'D:\SG52T08_ENV01'
    supervisor_launch_count = 1
    unreal_launch_count = 0
    retry_count = 0
    pid = $null
    exit_code = $null
    exit_code_type = $null
    timeout = $false
    peak_working_set_bytes = [int64]0
    process_samples = @()
    receipt_path = $Receipt
    receipt_classification = $null
    input_map_unchanged = $false
    output_map = $null
    author_source = $null
    contract = $null
    failure = $null
}

$finalExit = 1
try {
    if (-not $AuthorizeSingleUnrealAuthoring) { throw 'Mechanical -AuthorizeSingleUnrealAuthoring guard is required' }
    $state.stage = 'preflight'
    Assert-Authorities
    Assert-Fresh
    $heavy = @(Get-HeavyProcesses)
    if ($heavy.Count -ne 0) { throw "Heavy process active: $($heavy | ConvertTo-Json -Compress)" }

    [IO.Directory]::CreateDirectory($AttemptRoot) | Out-Null
    $attemptAuthor = Join-Path $AttemptRoot ([IO.Path]::GetFileName($Author))
    $attemptContract = Join-Path $AttemptRoot ([IO.Path]::GetFileName($Contract))
    Copy-Item -LiteralPath $Author -Destination $attemptAuthor
    Copy-Item -LiteralPath $Contract -Destination $attemptContract
    $state.author_source = Get-FileRecord $attemptAuthor
    $state.contract = Get-FileRecord $attemptContract

    $stdout = Join-Path $AttemptRoot 'unreal.stdout.log'
    $stderr = Join-Path $AttemptRoot 'unreal.stderr.log'
    $engineLog = Join-Path $AttemptRoot 'unreal.engine.log'
    $arguments = @(
        $Project,
        '-Unattended', '-NoSplash', '-NoSound', '-NullRHI', '-NoSaveOnExit',
        '-stdout', '-FullStdOutLogOutput', '-nop4',
        '-DisablePlugins=Fab,Bridge,EditorTelemetry,RuntimeTelemetry,EOSShared',
        '-ini:EditorSettings:[/Script/UnrealEd.AnalyticsPrivacySettings]:bSendUsageData=False',
        "-ExecutePythonScript=$Author", '-ScriptErrorsAreFatal', "-abslog=$engineLog"
    )
    $state.arguments = $arguments
    $state.stage = 'unreal_launch'
    $process = Start-Process -FilePath $Editor -ArgumentList $arguments -WorkingDirectory $state.working_directory -PassThru -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError $stderr
    $state.unreal_launch_count = 1
    $state.pid = $process.Id
    $handle = $process.Handle
    if ($null -eq $handle) { throw 'Failed to retain native Unreal process handle' }

    $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
    while (-not $process.HasExited -and [DateTime]::UtcNow -lt $deadline) {
        $process.Refresh()
        if ($process.WorkingSet64 -gt $state.peak_working_set_bytes) { $state.peak_working_set_bytes = [int64]$process.WorkingSet64 }
        $state.process_samples += [ordered]@{
            at_utc = [DateTime]::UtcNow.ToString('o')
            pid = $process.Id
            working_set_bytes = [int64]$process.WorkingSet64
        }
        Start-Sleep -Seconds 2
    }
    if (-not $process.HasExited) {
        $state.timeout = $true
        Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        throw "Stage7B Recovery01 authoring exceeded $TimeoutSeconds seconds"
    }
    $process.WaitForExit()
    $process.Refresh()
    $state.exit_code = [int]$process.ExitCode
    $state.exit_code_type = $process.ExitCode.GetType().FullName
    if ($state.exit_code -ne 0 -or $state.exit_code_type -ne 'System.Int32') {
        throw "Stage7B Recovery01 authoring returned $($state.exit_code) $($state.exit_code_type)"
    }

    if (-not [IO.File]::Exists($Receipt)) { throw 'Stage7B Recovery01 authoring receipt missing' }
    $state.stage = 'receipt_validation'
    $payload = Get-Content -LiteralPath $Receipt -Raw | ConvertFrom-Json
    $state.receipt_classification = [string]$payload.classification
    $expected = 'PASSED_STAGE07B_RECOVERY01_AUTHORING_AWAITING_D3D12_PROOF'
    if ($state.receipt_classification -ne $expected) { throw "Stage7B Recovery01 authoring receipt failed: $($state.receipt_classification)" }
    if (-not [IO.File]::Exists($OutputMap)) { throw 'Stage7B Recovery01 output map missing' }
    $contractObject = Get-Content -LiteralPath $Contract -Raw | ConvertFrom-Json
    Assert-FileRecord $contractObject.input 'Stage 7A Correction01 map after authoring'
    $state.input_map_unchanged = $true
    $state.output_map = Get-FileRecord $OutputMap
    $state.classification = $expected
    $state.stage = 'complete'
    $finalExit = 0
}
catch {
    $state.stage = 'failed'
    $state.failure = [ordered]@{
        type = $_.Exception.GetType().FullName
        message = $_.Exception.Message
        script_stack_trace = $_.ScriptStackTrace
    }
}
finally {
    $state.completed_at_utc = [DateTime]::UtcNow.ToString('o')
    try {
        Write-JsonAtomic $TerminalManifest $state
        if ([IO.Directory]::Exists($AttemptRoot)) { Write-JsonAtomic (Join-Path $AttemptRoot 'terminal.json') $state }
    }
    catch {
        try {
            [IO.File]::AppendAllText(
                $EmergencyReceipt,
                (([ordered]@{ at_utc = [DateTime]::UtcNow.ToString('o'); classification = 'FAILED_WITH_EVIDENCE'; error = $_.Exception.Message } | ConvertTo-Json -Compress) + [Environment]::NewLine),
                [Text.UTF8Encoding]::new($false)
            )
        }
        catch {}
        $finalExit = 1
    }
}

$state | ConvertTo-Json -Depth 64
[Environment]::Exit([int]$finalExit)
