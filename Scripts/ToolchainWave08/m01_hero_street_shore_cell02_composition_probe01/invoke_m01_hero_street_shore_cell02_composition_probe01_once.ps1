param(
    [switch]$AuthorizeSingleUnreal,
    [switch]$OfflineContractTest
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Project = 'D:\SG52T08_ENV01\Skyguard52.uproject'
$Editor = 'D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$Probe = 'D:\Skyguard52\Scripts\ToolchainWave08\m01_hero_street_shore_cell02_composition_probe01\probe_m01_hero_street_shore_cell02_composition_probe01.py'
$MapFile = 'D:\SG52T08_ENV01\Content\M01\Lvl_M01_HeroStreetShoreCell01_Recovery01.umap'
$StandingAuthorization = 'D:\Skyguard52\Production\standing_heavy_process_authorization.json'
$Cell01Freeze = 'D:\Skyguard52\Docs\AAA_Review\M01_HERO_STREET_SHORE_CELL01_RECOVERY01_VISUAL_PROOF01_ATTEMPT01_TERMINAL_FREEZE.json'
$FullKitReceipt = 'D:\Skyguard52\Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_KIT_FULL_IMPORT01_RECOVERY01\attempt_01\full_kit_import_receipt.json'
$FullKitTerminal = 'D:\Skyguard52\Saved\Reports\M01_VISIBLE_ENVIRONMENT_KIT_FULL_IMPORT01_RECOVERY01_TERMINAL_SUPERVISOR.json'
$Contract = 'D:\Skyguard52\Docs\AAA_Review\M01_HERO_STREET_SHORE_CELL02_COMPOSITION_PROBE01_CONTRACT.json'
$Inventory = 'D:\Skyguard52\Saved\Reports\M01_HERO_STREET_SHORE_CELL02_COMPOSITION_PROBE01_SOURCE_INVENTORY.json'
$AttemptRoot = 'D:\Skyguard52\Saved\BuildAttempts\M01_HERO_STREET_SHORE_CELL02_COMPOSITION_PROBE01\attempt_01'
$Receipt = Join-Path $AttemptRoot 'composition_probe_receipt.json'
$TerminalManifest = 'D:\Skyguard52\Saved\Reports\M01_HERO_STREET_SHORE_CELL02_COMPOSITION_PROBE01_TERMINAL_SUPERVISOR.json'
$EmergencyReceipt = 'D:\Skyguard52\Saved\Reports\M01_HERO_STREET_SHORE_CELL02_COMPOSITION_PROBE01_EMERGENCY_RECEIPT.jsonl'
$TimeoutSeconds = 1200

$Expected = @{
    Project = @{ Path = $Project; Bytes = 3703; Sha256 = '7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a' }
    Editor = @{ Path = $Editor; Bytes = 512952; Sha256 = '0fb325cf215cc800ce260a1890af3f3dc314b8cc6331061d4e7e7246489af2e0' }
    Probe = @{ Path = $Probe; Bytes = 10838; Sha256 = 'e8ff932ab82a67a4ef8c831965fe2345f60b676066ce367195369e2c1e989564' }
    Map = @{ Path = $MapFile; Bytes = 746684; Sha256 = '449c4d1153da7a149375f8b288c0908401ffe1db21104f83088039ed9b3656f2' }
    StandingAuthorization = @{ Path = $StandingAuthorization; Bytes = 2146; Sha256 = '48277d7edd869cc2b841c3993e8f7599bec5291ddf23e9c442b33e09b870c089' }
    Cell01Freeze = @{ Path = $Cell01Freeze; Bytes = 5278; Sha256 = 'c1c13e4a30366ff5fde357ec969b8418928e7a53d62ee098a0b6673c0ca65094' }
    FullKitReceipt = @{ Path = $FullKitReceipt; Bytes = 58338; Sha256 = '04895051591b7df6dfa39f87d1afa9f6bb72944c3cdde80e950d7cdcd35cad63' }
    FullKitTerminal = @{ Path = $FullKitTerminal; Bytes = 70113; Sha256 = '33fc9da97245b084ae821f4252d3409c003f210da9110bfbab801d862fcc77e0' }
    Contract = @{ Path = $Contract; Bytes = 1584; Sha256 = '791c8ac371b80575df11f4d4a1c318cf9876742c45a0da61d19b90c66dd2064a' }
    Inventory = @{ Path = $Inventory; Bytes = 5419; Sha256 = 'dd4a03c2204befb4f2d7f9ea7c8b2fa4b375099dd3f65afb3e70ac2ee9cb47ea' }
}

function Get-Sha256([string]$Path) {
    $stream = [System.IO.File]::Open($Path, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::Read)
    $hasher = [System.Security.Cryptography.SHA256]::Create()
    try { return ([System.BitConverter]::ToString($hasher.ComputeHash($stream))).Replace('-', '').ToLowerInvariant() }
    finally { $hasher.Dispose(); $stream.Dispose() }
}

function Assert-FileRecord([string]$Path, [int64]$Bytes, [string]$Sha256, [string]$Label) {
    if (-not [System.IO.File]::Exists($Path)) { throw "$Label is missing: $Path" }
    $info = [System.IO.FileInfo]::new($Path)
    if ($info.Length -ne $Bytes) { throw "$Label byte count mismatch: $($info.Length) != $Bytes" }
    $actual = Get-Sha256 $Path
    if ($actual -ne $Sha256) { throw "$Label SHA-256 mismatch: $actual != $Sha256" }
}

function Write-JsonAtomic([string]$Path, [object]$Payload) {
    $parent = [System.IO.Path]::GetDirectoryName($Path)
    [System.IO.Directory]::CreateDirectory($parent) | Out-Null
    $temporary = "$Path.tmp"
    [System.IO.File]::WriteAllText($temporary, (($Payload | ConvertTo-Json -Depth 30) + [Environment]::NewLine), [System.Text.UTF8Encoding]::new($false))
    [System.IO.File]::Move($temporary, $Path)
}

function Get-HeavyProcesses {
    return @(Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -match '^(UnrealEditor|UnrealEditor-Cmd|Blender|ShaderCompileWorker|AutomationTool|UnrealBuildTool|cl|link)$' } | Select-Object Id, ProcessName)
}

function Assert-FrozenAuthorities {
    foreach ($entry in $Expected.GetEnumerator()) {
        Assert-FileRecord $entry.Value.Path $entry.Value.Bytes $entry.Value.Sha256 $entry.Key
    }
    $inventoryPayload = Get-Content -LiteralPath $Inventory -Raw | ConvertFrom-Json
    foreach ($member in $inventoryPayload.members) {
        Assert-FileRecord ([string]$member.path) ([int64]$member.bytes) ([string]$member.sha256) ([string]$member.label)
    }
}

if ($AuthorizeSingleUnreal -and $OfflineContractTest) { [Console]::Error.WriteLine('Offline and authorized modes are mutually exclusive'); [Environment]::Exit([int]3) }

if ($OfflineContractTest) {
    Assert-FrozenAuthorities
    if ([System.IO.Directory]::Exists($AttemptRoot)) { throw "Future attempt already exists: $AttemptRoot" }
    if ([System.IO.File]::Exists($TerminalManifest)) { throw "Future terminal manifest already exists: $TerminalManifest" }
    if ([System.IO.File]::Exists($EmergencyReceipt)) { throw "Future emergency receipt already exists: $EmergencyReceipt" }
    $heavy = @(Get-HeavyProcesses)
    if ($heavy.Count -ne 0) { throw "Heavy process active during offline test: $($heavy | ConvertTo-Json -Compress)" }
    $source = [System.IO.File]::ReadAllText($Probe)
    foreach ($required in @('world_saved', 'map_unchanged', 'candidate_intersections', 'get_all_level_actors', 'SM_M01_CoastalA_HARDSCAPE', 'SM_M01_CoastalA_TERRAIN')) {
        if (-not $source.Contains($required)) { throw "Probe contract token missing: $required" }
    }
    [pscustomobject]@{ classification = 'PASSED_M01_HERO_STREET_SHORE_CELL02_COMPOSITION_PROBE01_OFFLINE_CONTRACT'; attempt_absent = $true; terminal_absent = $true; heavy_process_count = 0; unreal_launch_count = 0 } | ConvertTo-Json -Depth 4
    [Environment]::Exit([int]0)
}

if (-not $AuthorizeSingleUnreal) { [Console]::Error.WriteLine('Single Unreal composition-probe authorization guard was not supplied'); [Environment]::Exit([int]2) }

$state = [ordered]@{
    schema = 'skyguard.m01-hero-street-shore-cell02.composition-probe01.supervisor.v1'
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
    crash = $false
    peak_working_set_bytes = [int64]0
    process_samples = @()
    receipt_path = $Receipt
    receipt_classification = $null
    map_unchanged = $false
    world_saved = $null
    failure = $null
}

$exitCode = 1
try {
    $state.stage = 'preflight'
    Assert-FrozenAuthorities
    if ([System.IO.Directory]::Exists($AttemptRoot)) { throw "Attempt namespace already exists: $AttemptRoot" }
    if ([System.IO.File]::Exists($TerminalManifest)) { throw "Terminal manifest already exists: $TerminalManifest" }
    if ([System.IO.File]::Exists($EmergencyReceipt)) { throw "Emergency receipt already exists: $EmergencyReceipt" }
    $heavy = @(Get-HeavyProcesses)
    if ($heavy.Count -ne 0) { throw "Heavy process active: $($heavy | ConvertTo-Json -Compress)" }

    [System.IO.Directory]::CreateDirectory($AttemptRoot) | Out-Null
    $stdout = Join-Path $AttemptRoot 'unreal.stdout.log'
    $stderr = Join-Path $AttemptRoot 'unreal.stderr.log'
    $engineLog = Join-Path $AttemptRoot 'unreal.engine.log'
    $arguments = @($Project, '-Unattended', '-NoSplash', '-NoSound', '-NullRHI', '-NoSaveOnExit', '-stdout', '-FullStdOutLogOutput', '-nop4', '-DisablePlugins=Fab,Bridge,EditorTelemetry,RuntimeTelemetry,EOSShared', '-ini:EditorSettings:[/Script/UnrealEd.AnalyticsPrivacySettings]:bSendUsageData=False', "-ExecutePythonScript=$Probe", '-ScriptErrorsAreFatal', "-abslog=$engineLog")
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
    if (-not $process.HasExited) { $state.timeout = $true; Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue; throw "Unreal composition probe exceeded $TimeoutSeconds seconds" }
    $process.WaitForExit(); $process.Refresh()
    $state.exit_code = [int]$process.ExitCode
    $state.exit_code_type = $process.ExitCode.GetType().FullName
    if ($state.exit_code -ne 0) { throw "Unreal composition probe returned exit code $($state.exit_code)" }
    if ($state.exit_code_type -ne 'System.Int32') { throw "Unexpected exit-code type: $($state.exit_code_type)" }
    if (-not [System.IO.File]::Exists($Receipt)) { throw "Probe receipt is missing: $Receipt" }

    $state.stage = 'receipt_validation'
    $receiptPayload = Get-Content -LiteralPath $Receipt -Raw | ConvertFrom-Json
    $state.receipt_classification = [string]$receiptPayload.classification
    $state.map_unchanged = [bool]$receiptPayload.map_unchanged
    $state.world_saved = [bool]$receiptPayload.world_saved
    if ($state.receipt_classification -ne 'PASSED_M01_HERO_STREET_SHORE_CELL02_COMPOSITION_PROBE_READY_FOR_AUTHORING_DESIGN') { throw "Probe receipt classification failed: $($state.receipt_classification)" }
    if (-not $state.map_unchanged) { throw 'Accepted Cell01 map changed during read-only probe' }
    if ($state.world_saved) { throw 'Read-only probe reported a world save' }
    Assert-FileRecord $MapFile $Expected.Map.Bytes $Expected.Map.Sha256 'Cell01 map after probe'
    $state.classification = 'PASSED_M01_HERO_STREET_SHORE_CELL02_COMPOSITION_PROBE_READY_FOR_AUTHORING_DESIGN'
    $state.stage = 'complete'
    $exitCode = 0
}
catch {
    $state.failure = [ordered]@{ type = $_.Exception.GetType().FullName; message = $_.Exception.Message; script_stack_trace = $_.ScriptStackTrace }
    $state.stage = 'failed'
    $exitCode = 1
}
finally {
    $state.ended_utc = [DateTime]::UtcNow.ToString('o')
    try {
        Write-JsonAtomic $TerminalManifest $state
        if ([System.IO.Directory]::Exists($AttemptRoot)) { Write-JsonAtomic (Join-Path $AttemptRoot 'terminal.json') $state }
    }
    catch {
        try { [System.IO.File]::AppendAllText($EmergencyReceipt, (([ordered]@{ at_utc = [DateTime]::UtcNow.ToString('o'); classification = 'FAILED_WITH_EVIDENCE'; terminal_write_error = $_.Exception.Message; stage = $state.stage; pid = $state.pid } | ConvertTo-Json -Compress) + [Environment]::NewLine), [System.Text.UTF8Encoding]::new($false)) } catch {}
        $exitCode = 1
    }
}

$state | ConvertTo-Json -Depth 30
[Environment]::Exit([int]$exitCode)
