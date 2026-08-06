param(
    [ValidateSet("Validate", "Export", "Import", "Audit", "All")]
    [string]$Step = "Validate",
    [int]$ExpectedMeshDelta = 80,
    [switch]$AllowConcurrentEditor
)

$ErrorActionPreference = "Stop"

$ProjectRoot = "D:\Skyguard52"
$Project = Join-Path $ProjectRoot "Skyguard52.uproject"
$Blender = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
$UnrealCmd = "D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
$BlenderScript = Join-Path $ProjectRoot "Scripts\blender_l88_yak52_blockout.py"
$ImportScript = Join-Path $ProjectRoot "Scripts\build_skyguard_l88_validation.py"
$AuditScript = Join-Path $ProjectRoot "Scripts\audit_skyguard_l88_validation.py"
$DeltaAuditScript = Join-Path $ProjectRoot "Scripts\audit_l88_import_delta.py"
$DeltaBaseline = Join-Path $ProjectRoot "Saved\Reports\L88_BASELINE_PASS16.json"
$DeltaReport = Join-Path $ProjectRoot "Saved\Reports\L88_IMPORT_DELTA_CURRENT.json"
$SourceGlb = Join-Path $ProjectRoot "Content\Skyguard\Meshes\Source\L88\yak52_l88_silhouette_blockout.glb"
$SourceBlend = Join-Path $ProjectRoot "Content\Skyguard\Meshes\Source\L88\YAK52_L88_MASTER_BLOCKOUT.blend"
$ImportReport = Join-Path $ProjectRoot "Saved\Reports\L88_VALIDATION_IMPORT.json"
$LogRoot = Join-Path $ProjectRoot "Saved\Logs"

function Assert-File {
    param([Parameter(Mandatory = $true)][string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "Required file is missing: $Path"
    }
}

function Get-Sha256 {
    param([Parameter(Mandatory = $true)][string]$Path)
    $stream = [System.IO.File]::OpenRead($Path)
    try {
        $sha = [System.Security.Cryptography.SHA256]::Create()
        try {
            return (([BitConverter]::ToString($sha.ComputeHash($stream))) -replace "-", "").ToLowerInvariant()
        } finally {
            $sha.Dispose()
        }
    } finally {
        $stream.Dispose()
    }
}

function Assert-NoEditorConflict {
    if ($AllowConcurrentEditor) {
        return
    }
    $editors = @(Get-Process -Name "UnrealEditor" -ErrorAction SilentlyContinue)
    if ($editors.Count -gt 0) {
        throw "Unreal Editor is running. Close it before an automated import/audit, or explicitly use -AllowConcurrentEditor."
    }
}

function Invoke-UnrealPython {
    param(
        [Parameter(Mandatory = $true)][string]$Script,
        [Parameter(Mandatory = $true)][string]$Label
    )
    Assert-NoEditorConflict
    New-Item -ItemType Directory -Force -Path $LogRoot | Out-Null
    $stamp = [DateTimeOffset]::Now.ToString("yyyyMMdd-HHmmss")
    $stdout = Join-Path $LogRoot ("l88-{0}-{1}.stdout.log" -f $Label, $stamp)
    $stderr = Join-Path $LogRoot ("l88-{0}-{1}.stderr.log" -f $Label, $stamp)
    $arguments = @(
        $Project,
        "-ExecutePythonScript=$Script",
        "-unattended",
        "-nop4",
        "-nosplash",
        "-NullRHI",
        "-stdout",
        "-FullStdOutLogOutput"
    )
    $process = Start-Process -FilePath $UnrealCmd -ArgumentList $arguments `
        -RedirectStandardOutput $stdout -RedirectStandardError $stderr `
        -WindowStyle Hidden -Wait -PassThru
    if ($process.ExitCode -ne 0) {
        throw "Unreal $Label failed with exit code $($process.ExitCode). Logs: $stdout ; $stderr"
    }
}

function Invoke-DeltaAudit {
    Assert-File $DeltaAuditScript
    Assert-File $DeltaBaseline
    & python $DeltaAuditScript `
        --baseline $DeltaBaseline `
        --output $DeltaReport `
        --expected-mesh-delta $ExpectedMeshDelta `
        --change-reason "current Blender source and synchronized Unreal import"
    if ($LASTEXITCODE -ne 0) {
        throw "L88 import-delta audit failed with exit code $LASTEXITCODE."
    }
}

function Test-CurrentImport {
    Assert-File $SourceGlb
    Assert-File $SourceBlend
    Assert-File $ImportReport
    $report = Get-Content -LiteralPath $ImportReport -Raw | ConvertFrom-Json
    $currentHash = Get-Sha256 $SourceGlb
    if ([string]$report.gate -ne "PASS") {
        throw "Current Unreal import report is not PASS."
    }
    if ([string]$report.source_glb_sha256 -ne $currentHash) {
        throw "Current GLB hash does not match the Unreal import report. Run Import and Audit."
    }
    if (@($report.forbidden_legacy_labels).Count -ne 0) {
        throw "Current validation map contains forbidden legacy labels."
    }
    [ordered]@{
        status = "validated"
        project = $Project
        source_glb = $SourceGlb
        source_glb_sha256 = $currentHash
        imported_static_meshes = @($report.static_mesh_assets).Count
        validation_map = "/Game/Skyguard/Maps/Lvl_Yak52_L88_Validation_v2"
        gate = [string]$report.gate
        promotion = "validation_ready_not_final_aaa_art"
    } | ConvertTo-Json -Depth 10
}

foreach ($required in @($Project, $Blender, $UnrealCmd, $BlenderScript, $ImportScript, $AuditScript)) {
    Assert-File $required
}

if ($Step -in @("Export", "All")) {
    & $Blender --background --python $BlenderScript
    if ($LASTEXITCODE -ne 0) {
        throw "Blender export failed with exit code $LASTEXITCODE."
    }
    Assert-File $SourceGlb
    Assert-File $SourceBlend
}
if ($Step -in @("Import", "All")) {
    Invoke-UnrealPython -Script $ImportScript -Label "import"
}
if ($Step -in @("Audit", "All")) {
    Invoke-UnrealPython -Script $AuditScript -Label "audit"
    Invoke-DeltaAudit
}

if ($Step -in @("Validate", "Audit", "All")) {
    Test-CurrentImport
} else {
    [ordered]@{
        status = if ($Step -eq "Export") { "exported_pending_import" } else { "imported_pending_audit" }
        step = $Step
        source_glb = $SourceGlb
        source_glb_sha256 = Get-Sha256 $SourceGlb
        next_step = if ($Step -eq "Export") { "Import" } else { "Audit" }
    } | ConvertTo-Json -Depth 10
}
