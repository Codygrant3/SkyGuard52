[CmdletBinding()]
param(
    [switch]$OfflineContractTest,
    [switch]$AuthorizeSingleUnrealAuthoring
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Root = 'D:\Skyguard52'
$Project = 'D:\SG52T08_ENV01\Skyguard52.uproject'
$Editor = 'D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$InputMap = 'D:\SG52T08_ENV01\Content\M01\Lvl_M01_VisibleEnvironmentStage07AHeroCorridor01.umap'
$OutputMap = 'D:\SG52T08_ENV01\Content\M01\Lvl_M01_VisibleEnvironmentStage07AHeroCorridor01Correction01.umap'
$StandingAuthorization = Join-Path $Root 'Production\standing_heavy_process_authorization.json'
$Author = Join-Path $Root 'Scripts\ToolchainWave08\m01_visible_environment_stage07a_hero_corridor01_correction01\author_m01_visible_environment_stage07a_hero_corridor01_correction01.py'
$Contract = Join-Path $Root 'Scripts\ToolchainWave08\m01_visible_environment_stage07a_hero_corridor01_correction01\stage07a_hero_corridor01_correction01_contract.json'
$AttemptRoot = Join-Path $Root 'Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_STAGE07A_HERO_CORRIDOR01_CORRECTION01_AUTHORING01\attempt_01'
$Receipt = Join-Path $AttemptRoot 'authoring_receipt.json'
$TerminalManifest = Join-Path $Root 'Saved\Reports\M01_VISIBLE_ENVIRONMENT_STAGE07A_HERO_CORRIDOR01_CORRECTION01_AUTHORING01_TERMINAL_MANIFEST.json'
$EmergencyReceipt = Join-Path $Root 'Saved\Reports\M01_VISIBLE_ENVIRONMENT_STAGE07A_HERO_CORRIDOR01_CORRECTION01_AUTHORING01_EMERGENCY_RECEIPT.jsonl'
$TimeoutSeconds = 900

function Get-LowerSha256([string]$Path) {
    $stream = $null; $hasher = $null
    try {
        $stream = [IO.File]::Open($Path, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::Read)
        $hasher = [Security.Cryptography.SHA256]::Create()
        return ([BitConverter]::ToString($hasher.ComputeHash($stream))).Replace('-', '').ToLowerInvariant()
    }
    finally { if ($null -ne $hasher) { $hasher.Dispose() }; if ($null -ne $stream) { $stream.Dispose() } }
}

function Get-FileRecord([string]$Path) {
    $item = Get-Item -LiteralPath $Path
    return [ordered]@{ path = $item.FullName; bytes = [int64]$item.Length; sha256 = Get-LowerSha256 $item.FullName }
}

function Write-JsonAtomic([string]$Path, $Value) {
    $parent = Split-Path -Parent $Path
    if (-not [IO.Directory]::Exists($parent)) { [IO.Directory]::CreateDirectory($parent) | Out-Null }
    $temporary = $Path + '.tmp'
    [IO.File]::WriteAllText($temporary, (($Value | ConvertTo-Json -Depth 20) + [Environment]::NewLine), [Text.UTF8Encoding]::new($false))
    Move-Item -LiteralPath $temporary -Destination $Path -Force
}

function Assert-FileRecord($Spec, [string]$Label) {
    $path = [string]$Spec.path
    if (-not [IO.File]::Exists($path)) { throw "$Label missing: $path" }
    $actual = Get-FileRecord $path
    if ($actual.bytes -ne [int64]$Spec.bytes -or $actual.sha256 -ne [string]$Spec.sha256) { throw "$Label changed: $path" }
}

function Get-HeavyProcesses {
    return @(Get-Process -ErrorAction SilentlyContinue | Where-Object {
        $_.Name -match '^(UnrealEditor(-Cmd)?|Blender|ShaderCompileWorker|AutomationTool|UnrealBuildTool|cl|link|dotnet)(\.exe)?$'
    })
}

function Invoke-Preflight {
    foreach ($path in @($Project, $Editor, $StandingAuthorization, $Author, $Contract, $InputMap)) {
        if (-not [IO.File]::Exists($path)) { throw "Required file missing: $path" }
    }
    $contractObject = Get-Content -LiteralPath $Contract -Raw | ConvertFrom-Json
    $inputSpec = [pscustomobject]@{
        path = [string]$contractObject.input.file
        bytes = [int64]$contractObject.input.bytes
        sha256 = [string]$contractObject.input.sha256
    }
    Assert-FileRecord $inputSpec 'Stage07A map'
    foreach ($spec in $contractObject.authorities) { Assert-FileRecord $spec 'Correction authority' }
    $standing = Get-Content -LiteralPath $StandingAuthorization -Raw | ConvertFrom-Json
    if ($standing.status -ne 'ACTIVE' -or $standing.execution_policy.per_run_user_authorization_required -ne $false) { throw 'Standing heavy-process authorization is inactive' }
    $heavy = @(Get-HeavyProcesses)
    if ($heavy.Count -ne 0) { throw "Heavy-process gate blocked: $($heavy.Name -join ', ')" }
    foreach ($path in @($OutputMap, $AttemptRoot, $TerminalManifest, $EmergencyReceipt)) {
        if (Test-Path -LiteralPath $path) { throw "Fresh namespace exists: $path" }
    }
}

if ($OfflineContractTest) {
    Invoke-Preflight
    & python $Author --offline-contract-test
    exit [int]$LASTEXITCODE
}

$state = [ordered]@{
    schema = 'skyguard.m01-visible-environment-stage07a-hero-corridor01-correction01.authoring01.supervisor.v1'
    classification = 'FAILED_WITH_EVIDENCE'
    stage = 'initialization'
    started_utc = [DateTime]::UtcNow.ToString('o')
    ended_utc = $null
    launch_count = 0
    retry_count = 0
    pid = $null
    exit_code = $null
    exit_code_type = $null
    timed_out = $false
    executable = $Editor
    arguments = @()
    working_directory = 'D:\SG52T08_ENV01'
    process_samples = @()
    author_source = $null
    contract = $null
    receipt = $null
    output_map = $null
    error = $null
}

try {
    if (-not $AuthorizeSingleUnrealAuthoring) { throw 'Mechanical -AuthorizeSingleUnrealAuthoring guard is required' }
    $state.stage = 'preflight'
    Invoke-Preflight
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
        $Project, '-nullrhi', '-unattended', '-nosplash', '-NoSound', '-NoTextureStreaming', '-NoAssetRegistryCache',
        '-stdout', '-FullStdOutLogOutput', '-nop4', "-abslog=$engineLog",
        '-ini:EditorSettings:[/Script/UnrealEd.AnalyticsPrivacySettings]:bSendUsageData=False',
        '-DisablePlugins=Fab,Bridge,EditorTelemetry,RuntimeTelemetry,EOSShared',
        "-ExecutePythonScript=$attemptAuthor"
    )
    $state.arguments = $arguments
    $state.stage = 'launch'
    $process = Start-Process -FilePath $Editor -ArgumentList $arguments -WorkingDirectory $state.working_directory -PassThru -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError $stderr
    $handle = $process.Handle
    if ($null -eq $handle) { throw 'Failed to retain native Unreal process handle' }
    $state.launch_count = 1
    $state.pid = [int]$process.Id
    $state.stage = 'wait'
    $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
    while (-not $process.HasExited -and [DateTime]::UtcNow -lt $deadline) {
        $process.Refresh()
        $state.process_samples += [ordered]@{ utc = [DateTime]::UtcNow.ToString('o'); working_set_bytes = [int64]$process.WorkingSet64; processor_time_seconds = [double]$process.TotalProcessorTime.TotalSeconds }
        Start-Sleep -Seconds 1
    }
    if (-not $process.HasExited) { $state.timed_out = $true; try { $process.Kill() } catch {}; throw "Correction authoring exceeded $TimeoutSeconds seconds" }
    $process.WaitForExit(); $process.Refresh()
    $state.exit_code = [int]$process.ExitCode
    $state.exit_code_type = $process.ExitCode.GetType().FullName
    if ($state.exit_code -ne 0) { throw "Correction authoring returned $($state.exit_code) $($state.exit_code_type)" }
    $state.stage = 'validation'
    if (-not [IO.File]::Exists($Receipt)) { throw 'Correction authoring receipt missing' }
    $receiptObject = Get-Content -LiteralPath $Receipt -Raw | ConvertFrom-Json
    $expected = 'PASSED_STAGE07A_HERO_CORRIDOR01_CORRECTION01_AUTHORING_AWAITING_FINAL_VISUAL'
    if ($receiptObject.classification -ne $expected) { throw "Correction receipt failed: $($receiptObject.classification)" }
    if (-not [IO.File]::Exists($OutputMap)) { throw 'Correction output map missing' }
    $contractObject = Get-Content -LiteralPath $Contract -Raw | ConvertFrom-Json
    $inputSpec = [pscustomobject]@{
        path = [string]$contractObject.input.file
        bytes = [int64]$contractObject.input.bytes
        sha256 = [string]$contractObject.input.sha256
    }
    Assert-FileRecord $inputSpec 'Immutable Stage07A map after correction'
    $state.receipt = Get-FileRecord $Receipt
    $state.output_map = Get-FileRecord $OutputMap
    $state.classification = $expected
    $state.stage = 'complete'
}
catch {
    $state.error = $_.Exception.Message
}
finally {
    $state.ended_utc = [DateTime]::UtcNow.ToString('o')
    try {
        Write-JsonAtomic $TerminalManifest $state
        if ([IO.Directory]::Exists($AttemptRoot)) { Write-JsonAtomic (Join-Path $AttemptRoot 'terminal.json') $state }
    }
    catch {
        try { Add-Content -LiteralPath $EmergencyReceipt -Value (([ordered]@{ utc = [DateTime]::UtcNow.ToString('o'); error = $_.Exception.Message; state = $state } | ConvertTo-Json -Compress -Depth 20)) -Encoding UTF8 } catch {}
    }
}

if ($state.classification -eq 'FAILED_WITH_EVIDENCE') { exit [int]1 }
exit [int]0
