param([switch]$OfflineContractTest)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Project = 'D:\SG52T08_ENV01\Skyguard52.uproject'
$Editor = 'D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$InputMap = 'D:\SG52T08_ENV01\Content\M01\Lvl_M01_PhotorealFoundation_LightingRoadsWaterline02.umap'
$OutputMap = 'D:\SG52T08_ENV01\Content\M01\Lvl_M01_PhotorealFoundation_StructuralCleanup03.umap'
$StandingAuthorization = 'D:\Skyguard52\Production\standing_heavy_process_authorization.json'
$FailedProofFreeze = 'D:\Skyguard52\Docs\AAA_Review\M01_PHOTOREAL_FOUNDATION_WAVE01_LIGHTING_ROADS_WATERLINE02_VISUAL_PROOF01_ATTEMPT01_TERMINAL_FREEZE.json'
$DirectVisualReview = 'D:\Skyguard52\Docs\AAA_Review\M01_PHOTOREAL_FOUNDATION_WAVE01_LIGHTING_ROADS_WATERLINE02_VISUAL_PROOF01_DIRECT_VISUAL_REVIEW.json'
$Author = 'D:\Skyguard52\Scripts\ToolchainWave08\m01_photoreal_foundation_wave01_structural_cleanup03\author_structural_cleanup03.py'
$Verifier = 'D:\Skyguard52\Scripts\ToolchainWave08\m01_photoreal_foundation_wave01_structural_cleanup03\verify_authoring_offline.py'
$Contract = 'D:\Skyguard52\Docs\Toolchain\ToolchainWave08\M01PhotorealFoundationStructuralCleanup03\quality_contract.json'
$AttemptRoot = 'D:\Skyguard52\Saved\BuildAttempts\M01_PHOTOREAL_FOUNDATION_WAVE01_STRUCTURAL_CLEANUP03_AUTHORING\attempt_01'
$Receipt = Join-Path $AttemptRoot 'authoring_receipt.json'
$TerminalManifest = 'D:\Skyguard52\Saved\Reports\M01_PHOTOREAL_FOUNDATION_WAVE01_STRUCTURAL_CLEANUP03_AUTHORING_TERMINAL_MANIFEST.json'
$EmergencyReceipt = 'D:\Skyguard52\Saved\Reports\M01_PHOTOREAL_FOUNDATION_WAVE01_STRUCTURAL_CLEANUP03_AUTHORING_EMERGENCY_RECEIPT.jsonl'
$TimeoutSeconds = 1800

$Expected = @{
    Project = @{ Bytes = 3703; Sha256 = '7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a' }
    Editor = @{ Bytes = 512952; Sha256 = '0fb325cf215cc800ce260a1890af3f3dc314b8cc6331061d4e7e7246489af2e0' }
    InputMap = @{ Bytes = 739952; Sha256 = '34b93c53b208fa061538674a36f1aef2a087376ec66a5254465fdafbd8488149' }
    StandingAuthorization = @{ Bytes = 2146; Sha256 = '48277d7edd869cc2b841c3993e8f7599bec5291ddf23e9c442b33e09b870c089' }
    FailedProofFreeze = @{ Bytes = 4569; Sha256 = '11be3f5cc60d51b7791650f5b84a068d0f2152308c943fd38d31f5c6bfa9d38b' }
    DirectVisualReview = @{ Bytes = 4503; Sha256 = '71d810c207285a83233e437f89dcfb74314753bd6ba784249076b08ada1f03e8' }
    Author = @{ Bytes = 17167; Sha256 = '2db3a7c85270decbf363d4449c6795ead5c35b3d60ab50e0cca841606f2a1a47' }
    Verifier = @{ Bytes = 2512; Sha256 = '8efcaf1697b73916e4103416a7dc60e95deb11ffb00b63396a7db9f1286d81cd' }
    Contract = @{ Bytes = 2658; Sha256 = '8de8c90cba1a6779d7922a9515ad83037971d39ed0943ace48033a4ce32d85c3' }
}

function Get-Sha256([string]$Path) {
    $stream = [System.IO.File]::Open($Path, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::Read)
    $hasher = [System.Security.Cryptography.SHA256]::Create()
    try { return ([System.BitConverter]::ToString($hasher.ComputeHash($stream))).Replace('-', '').ToLowerInvariant() }
    finally { $hasher.Dispose(); $stream.Dispose() }
}

function Assert-File([string]$Path, [int64]$Bytes, [string]$Sha256, [string]$Label) {
    if (-not [System.IO.File]::Exists($Path)) { throw "$Label missing: $Path" }
    $info = [System.IO.FileInfo]::new($Path)
    if ($info.Length -ne $Bytes) { throw "$Label byte mismatch: $($info.Length) != $Bytes" }
    $actual = Get-Sha256 $Path
    if ($actual -ne $Sha256) { throw "$Label hash mismatch: $actual != $Sha256" }
}

function Write-JsonAtomic([string]$Path, [object]$Payload) {
    [System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName($Path)) | Out-Null
    $temporary = "$Path.tmp"
    [System.IO.File]::WriteAllText($temporary, ($Payload | ConvertTo-Json -Depth 40) + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
    [System.IO.File]::Move($temporary, $Path)
}

function Get-HeavyProcesses {
    return @(Get-Process -ErrorAction SilentlyContinue | Where-Object {
        $_.ProcessName -match '^(UnrealEditor|UnrealEditor-Cmd|Blender|ShaderCompileWorker|AutomationTool|UnrealBuildTool|cl|link)$'
    } | Select-Object Id, ProcessName)
}

function Assert-Authorities {
    Assert-File $Project $Expected.Project.Bytes $Expected.Project.Sha256 'Isolated project'
    Assert-File $Editor $Expected.Editor.Bytes $Expected.Editor.Sha256 'UE 5.8 editor'
    Assert-File $InputMap $Expected.InputMap.Bytes $Expected.InputMap.Sha256 'Accepted input map'
    Assert-File $StandingAuthorization $Expected.StandingAuthorization.Bytes $Expected.StandingAuthorization.Sha256 'Standing authorization'
    Assert-File $FailedProofFreeze $Expected.FailedProofFreeze.Bytes $Expected.FailedProofFreeze.Sha256 'Failed-proof freeze'
    Assert-File $DirectVisualReview $Expected.DirectVisualReview.Bytes $Expected.DirectVisualReview.Sha256 'Direct visual review'
    Assert-File $Author $Expected.Author.Bytes $Expected.Author.Sha256 'Authoring script'
    Assert-File $Verifier $Expected.Verifier.Bytes $Expected.Verifier.Sha256 'Offline verifier'
    Assert-File $Contract $Expected.Contract.Bytes $Expected.Contract.Sha256 'Quality contract'
    $authorization = Get-Content -LiteralPath $StandingAuthorization -Raw | ConvertFrom-Json
    if ($authorization.status -ne 'ACTIVE' -or [bool]$authorization.execution_policy.per_run_user_authorization_required) { throw 'Standing heavy-process authorization is inactive' }
    $failed = Get-Content -LiteralPath $FailedProofFreeze -Raw | ConvertFrom-Json
    if ($failed.classification -ne 'FAILED_WITH_EVIDENCE' -or $failed.next_gate -ne 'M01_PHOTOREAL_FOUNDATION_WAVE01_STRUCTURAL_CLEANUP03_AUTHORING') { throw 'Failed-proof authority does not route to StructuralCleanup03' }
}

if ($OfflineContractTest) {
    Assert-Authorities
    if ([System.IO.Directory]::Exists($AttemptRoot)) { throw "Future attempt exists: $AttemptRoot" }
    if ([System.IO.File]::Exists($OutputMap)) { throw "Future output exists: $OutputMap" }
    if ([System.IO.File]::Exists($TerminalManifest)) { throw "Future terminal exists: $TerminalManifest" }
    if ([System.IO.File]::Exists($EmergencyReceipt)) { throw "Future emergency receipt exists: $EmergencyReceipt" }
    if (@(Get-HeavyProcesses).Count -ne 0) { throw 'Heavy process active during offline contract test' }
    $verifyOutput = & python $Verifier 2>&1
    if ($LASTEXITCODE -ne 0 -or ($verifyOutput -join "`n") -notmatch 'PASS') { throw "Offline verifier failed: $($verifyOutput -join ' ')" }
    [pscustomobject]@{ classification = 'PASSED_OFFLINE_CONTRACT'; unreal_launch_count = 0; retry_count = 0; governed_namespaces_created = 0 } | ConvertTo-Json
    [Environment]::Exit([int]0)
}

$state = [ordered]@{
    schema = 'skyguard.m01-photoreal-foundation.structural-cleanup03.authoring-supervisor.v1'
    classification = 'FAILED_WITH_EVIDENCE'
    started_utc = [DateTime]::UtcNow.ToString('o')
    ended_utc = $null
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
    output_map = $OutputMap
    output_bytes = $null
    output_sha256 = $null
    quality_metrics = $null
    input_unchanged = $false
    failure = $null
}

$finalExit = 1
try {
    $state.stage = 'preflight'
    Assert-Authorities
    if ([System.IO.Directory]::Exists($AttemptRoot)) { throw "Attempt exists: $AttemptRoot" }
    if ([System.IO.File]::Exists($OutputMap)) { throw "Output map exists: $OutputMap" }
    if ([System.IO.File]::Exists($TerminalManifest)) { throw "Terminal exists: $TerminalManifest" }
    if ([System.IO.File]::Exists($EmergencyReceipt)) { throw "Emergency receipt exists: $EmergencyReceipt" }
    $heavy = @(Get-HeavyProcesses)
    if ($heavy.Count -ne 0) { throw "Heavy process active: $($heavy | ConvertTo-Json -Compress)" }

    [System.IO.Directory]::CreateDirectory($AttemptRoot) | Out-Null
    $stdout = Join-Path $AttemptRoot 'unreal.stdout.log'
    $stderr = Join-Path $AttemptRoot 'unreal.stderr.log'
    $engineLog = Join-Path $AttemptRoot 'unreal.engine.log'
    $arguments = @(
        $Project, '-Unattended', '-NoSplash', '-NoSound', '-NullRHI', '-NoSaveOnExit',
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
    if ($null -eq $handle) { throw 'Failed to retain native process handle' }
    $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
    while (-not $process.HasExited -and [DateTime]::UtcNow -lt $deadline) {
        $process.Refresh()
        if ($process.WorkingSet64 -gt $state.peak_working_set_bytes) { $state.peak_working_set_bytes = [int64]$process.WorkingSet64 }
        $state.process_samples += [ordered]@{ at_utc = [DateTime]::UtcNow.ToString('o'); pid = $process.Id; working_set_bytes = [int64]$process.WorkingSet64 }
        Start-Sleep -Seconds 2
    }
    if (-not $process.HasExited) {
        $state.timeout = $true
        Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        throw "Unreal authoring exceeded $TimeoutSeconds seconds"
    }
    $process.WaitForExit(); $process.Refresh()
    $state.exit_code = [int]$process.ExitCode
    $state.exit_code_type = $process.ExitCode.GetType().FullName
    if ($state.exit_code -ne 0) { throw "Unreal authoring returned $($state.exit_code)" }
    if ($state.exit_code_type -ne 'System.Int32') { throw "Unexpected exit-code type: $($state.exit_code_type)" }
    if (-not [System.IO.File]::Exists($Receipt)) { throw "Authoring receipt missing: $Receipt" }

    $state.stage = 'postflight'
    $payload = Get-Content -LiteralPath $Receipt -Raw | ConvertFrom-Json
    $state.receipt_classification = [string]$payload.classification
    $state.quality_metrics = $payload.quality_metrics
    if ($state.receipt_classification -ne 'PASSED_M01_PHOTOREAL_FOUNDATION_STRUCTURAL_CLEANUP03_AUTOMATIC') { throw "Authoring receipt failed: $($state.receipt_classification)" }
    if (-not [System.IO.File]::Exists($OutputMap)) { throw "Output map missing: $OutputMap" }
    Assert-File $InputMap $Expected.InputMap.Bytes $Expected.InputMap.Sha256 'Accepted input map after authoring'
    $state.input_unchanged = $true
    $state.output_bytes = ([System.IO.FileInfo]::new($OutputMap)).Length
    $state.output_sha256 = Get-Sha256 $OutputMap
    if ($payload.output_sha256 -ne $state.output_sha256) { throw 'Output-map hash does not match receipt' }
    if ([int]$payload.actor_count_after -ne 120) { throw 'Output actor count is not 120' }
    if ([int]$payload.quality_metrics.cross_street_actor_count -ne 15) { throw 'CrossStreet actor count is not 15' }
    if ([int]$payload.quality_metrics.cross_street_corrected_surface_count -ne 30) { throw 'CrossStreet corrected-surface count is not 30' }
    if ([int]$payload.quality_metrics.district_urban_paver_bindings -ne 4) { throw 'Urban-paver binding count is not four' }
    if ([int]$payload.quality_metrics.proxy_tree_count -ne 0) { throw 'Rejected proxy trees returned' }
    $state.classification = 'PASSED_M01_PHOTOREAL_FOUNDATION_STRUCTURAL_CLEANUP03_AUTOMATIC'
    $state.stage = 'complete'
    $finalExit = 0
}
catch {
    $state.stage = 'failed'
    $state.failure = [ordered]@{ type = $_.Exception.GetType().FullName; message = $_.Exception.Message; script_stack_trace = $_.ScriptStackTrace }
}
finally {
    $state.ended_utc = [DateTime]::UtcNow.ToString('o')
    try {
        Write-JsonAtomic $TerminalManifest $state
        if ([System.IO.Directory]::Exists($AttemptRoot)) { Write-JsonAtomic (Join-Path $AttemptRoot 'terminal.json') $state }
    }
    catch {
        try {
            $line = ([ordered]@{ at_utc = [DateTime]::UtcNow.ToString('o'); classification = 'FAILED_WITH_EVIDENCE'; error = $_.Exception.Message } | ConvertTo-Json -Compress)
            [System.IO.File]::AppendAllText($EmergencyReceipt, $line + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
        } catch {}
        $finalExit = 1
    }
}

$state | ConvertTo-Json -Depth 40
[Environment]::Exit([int]$finalExit)
