param(
    [switch]$OfflineContractTest,
    [switch]$AuthorizeSingleUnrealProof
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Root = 'D:\Skyguard52'
$Project = 'D:\SG52T08_ENV01\Skyguard52.uproject'
$Editor = 'D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe'
$MapAsset = '/Game/M01/Lvl_M01_VisibleEnvironmentStage07BMaterialTerrainDistrictVariety01Recovery01'
$MapFile = 'D:\SG52T08_ENV01\Content\M01\Lvl_M01_VisibleEnvironmentStage07BMaterialTerrainDistrictVariety01Recovery01.umap'
$Capture = Join-Path $Root 'Scripts\ToolchainWave08\m01_visible_environment_stage07b_material_terrain_district_variety01_recovery01_visual_proof01\capture_stage07b_recovery01_visual_proof01.py'
$Contract = Join-Path $Root 'Scripts\ToolchainWave08\m01_visible_environment_stage07b_material_terrain_district_variety01_recovery01_visual_proof01\stage07b_recovery01_visual_proof01_contract.json'
$AttemptRoot = Join-Path $Root 'Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_STAGE07B_MATERIAL_TERRAIN_DISTRICT_VARIETY01_RECOVERY01_VISUAL_PROOF01\attempt_01'
$Receipt = Join-Path $AttemptRoot 'proof\capture_receipt.json'
$TerminalManifest = Join-Path $Root 'Saved\Reports\M01_VISIBLE_ENVIRONMENT_STAGE07B_MATERIAL_TERRAIN_DISTRICT_VARIETY01_RECOVERY01_VISUAL_PROOF01_TERMINAL_SUPERVISOR.json'
$TimeoutSeconds = 1200

function Get-Sha256([string]$Path) {
    $stream = [System.IO.File]::Open($Path, 'Open', 'Read', 'Read')
    $hasher = [System.Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($hasher.ComputeHash($stream))).Replace('-', '').ToLowerInvariant() }
    finally { $hasher.Dispose(); $stream.Dispose() }
}
function Get-FileRecord([string]$Path) {
    $item = [IO.FileInfo]::new($Path)
    return [ordered]@{ path = $Path; bytes = [int64]$item.Length; sha256 = Get-Sha256 $Path }
}
function Write-JsonAtomic([string]$Path, [object]$Payload) {
    [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($Path)) | Out-Null
    $temporary = "$Path.tmp"
    [IO.File]::WriteAllText($temporary, ($Payload | ConvertTo-Json -Depth 32) + [Environment]::NewLine, [Text.UTF8Encoding]::new($false))
    [IO.File]::Move($temporary, $Path)
}

if ($OfflineContractTest) {
    if (-not [IO.File]::Exists($Contract)) { throw "Contract missing: $Contract" }
    $c = Get-Content -LiteralPath $Contract -Raw | ConvertFrom-Json
    if ($c.world.map_sha256 -ne (Get-Sha256 $MapFile)) { throw 'Recovery01 map hash drifted' }
    if (-not [IO.File]::Exists($Capture)) { throw 'Capture script missing' }
    if (Test-Path -LiteralPath $AttemptRoot) { throw "Fresh proof namespace exists: $AttemptRoot" }
    [ordered]@{ classification = 'PASSED_OFFLINE_READY_FOR_SINGLE_STAGE07B_RECOVERY01_VISUAL_PROOF01'; unreal_launch_count = 0 } | ConvertTo-Json
    [Environment]::Exit(0)
}

$state = [ordered]@{
    schema = 'skyguard.m01-visible-environment-stage07b-recovery01.visual-proof01.supervisor.v1'
    classification = 'FAILED_WITH_EVIDENCE'
    started_at_utc = [DateTime]::UtcNow.ToString('o')
    completed_at_utc = $null
    executable = $Editor
    unreal_launch_count = 0
    retry_count = 0
    pid = $null
    exit_code = $null
    timed_out = $false
    failure = $null
}
$finalExit = 1
try {
    if (-not $AuthorizeSingleUnrealProof) { throw 'Mechanical -AuthorizeSingleUnrealProof guard is required' }
    if (Test-Path -LiteralPath $AttemptRoot) { throw "Fresh proof namespace exists: $AttemptRoot" }
    if (Test-Path -LiteralPath $TerminalManifest) { throw "Fresh proof manifest exists: $TerminalManifest" }
    $heavy = @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object { $_.Name -match '^(UnrealEditor(-Cmd)?|Blender|ShaderCompileWorker)(\.exe)?$' })
    if ($heavy.Count -ne 0) { throw "Heavy process active" }
    [IO.Directory]::CreateDirectory($AttemptRoot) | Out-Null
    $stdout = Join-Path $AttemptRoot 'unreal.stdout.log'
    $stderr = Join-Path $AttemptRoot 'unreal.stderr.log'
    $engineLog = Join-Path $AttemptRoot 'unreal.engine.log'
    $py = $Capture.Replace('\', '/')
    $arguments = @(
        $Project, $MapAsset,
        '-game', '-D3D12', '-sm6', '-RenderOffscreen', '-windowed', '-ResX=2560', '-ResY=1440',
        '-NoVSync', '-NoSound', '-NoSplash', '-unattended', '-nop4',
        '-DisablePlugins=Fab,Bridge,EditorTelemetry,RuntimeTelemetry,EOSShared',
        "-ExecCmds=py $py",
        "-abslog=$engineLog"
    )
    $process = Start-Process -FilePath $Editor -ArgumentList $arguments -WorkingDirectory 'D:\SG52T08_ENV01' -PassThru -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError $stderr
    $state.unreal_launch_count = 1
    $state.pid = $process.Id
    $handle = $process.Handle
    if ($null -eq $handle) { throw 'Failed to retain Unreal process handle' }
    $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
    while (-not $process.HasExited -and [DateTime]::UtcNow -lt $deadline) { Start-Sleep -Seconds 2 }
    if (-not $process.HasExited) {
        $state.timed_out = $true
        Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        throw "Proof exceeded $TimeoutSeconds seconds"
    }
    $process.WaitForExit()
    $state.exit_code = [int]$process.ExitCode
    if (-not [IO.File]::Exists($Receipt)) { throw 'Capture receipt missing' }
    $payload = Get-Content -LiteralPath $Receipt -Raw | ConvertFrom-Json
    $state.classification = [string]$payload.classification
    if ($state.classification -ne 'PASSED_AUTOMATIC_AWAITING_HUMAN_VISUAL_REVIEW') { throw "Proof receipt failed: $($state.classification)" }
    if ((Get-Sha256 $MapFile) -ne '531e0d45ecc43d1632ef480e2fbf0116fdfff27425e6dd28703b88a8b95b6bbe') { throw 'Proof mutated Recovery01 map' }
    $finalExit = 0
}
catch {
    $state.failure = $_.Exception.Message
}
finally {
    $state.completed_at_utc = [DateTime]::UtcNow.ToString('o')
    Write-JsonAtomic $TerminalManifest $state
}
$state | ConvertTo-Json -Depth 8
[Environment]::Exit([int]$finalExit)
