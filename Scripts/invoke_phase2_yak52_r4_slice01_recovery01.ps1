[CmdletBinding()]
param(
    [string]$ProjectRoot = "D:\Skyguard52",
    [string]$BlenderExe = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe",
    [switch]$AuthorizeProduction
)

$ErrorActionPreference = "Stop"
if (-not $AuthorizeProduction) {
    throw "Recovery01 production is not authorized. Re-run explicitly with -AuthorizeProduction."
}

$root = (Resolve-Path -LiteralPath $ProjectRoot).Path
$blender = (Resolve-Path -LiteralPath $BlenderExe).Path
$contractPath = Join-Path $root "Docs\AAA_Review\PHASE2_YAK52_R4_SLICE01_RECOVERY01_OUTPUT_CONTRACT.json"
$authoringPath = Join-Path $root "Scripts\blender_phase2_yak52_r4_slice01_recovery01.py"
$verifierPath = Join-Path $root "Scripts\verify_phase2_yak52_r4_slice01_recovery01_readiness.py"
$wrapperPath = $MyInvocation.MyCommand.Path

if (Get-Process -Name "blender" -ErrorAction SilentlyContinue) {
    throw "A Blender process is already active; Recovery01 will not duplicate it."
}

python $verifierPath --root $root --no-write
if ($LASTEXITCODE -ne 0) {
    throw "Recovery01 offline readiness failed; Blender was not launched."
}

$contractHash = (Get-FileHash -LiteralPath $contractPath -Algorithm SHA256).Hash.ToLowerInvariant()
$timestamp = [DateTime]::UtcNow.ToString("yyyyMMddTHHmmssfffffffZ")
$attemptId = "attempt_{0}_{1}_{2:x8}" -f $timestamp, $contractHash.Substring(0, 8), $PID
$attemptRoot = Join-Path $root "Saved\Reports\Phase2Yak52R4Slice01Recovery01Production"
$attemptDir = Join-Path $attemptRoot $attemptId
if (Test-Path -LiteralPath $attemptDir) {
    throw "Recovery01 attempt directory already exists: $attemptDir"
}
New-Item -ItemType Directory -Path $attemptDir | Out-Null

$stdoutPath = Join-Path $attemptDir "blender.stdout.log"
$stderrPath = Join-Path $attemptDir "blender.stderr.log"
$receiptPath = Join-Path $attemptDir "launch_receipt.json"
$sumsPath = Join-Path $attemptDir "SHA256SUMS.txt"
$startedUtc = [DateTime]::UtcNow
$exitCode = $null
$launchError = $null
$processId = $null
$arguments = @(
    "--background",
    "--factory-startup",
    "--python",
    $authoringPath
)

try {
    $process = Start-Process `
        -FilePath $blender `
        -ArgumentList $arguments `
        -RedirectStandardOutput $stdoutPath `
        -RedirectStandardError $stderrPath `
        -WindowStyle Hidden `
        -Wait `
        -PassThru
    $processId = $process.Id
    $exitCode = $process.ExitCode
}
catch {
    $launchError = $_.Exception.Message
    $exitCode = -1
}
finally {
    if (-not (Test-Path -LiteralPath $stdoutPath)) {
        [IO.File]::WriteAllText($stdoutPath, "", [Text.UTF8Encoding]::new($false))
    }
    if (-not (Test-Path -LiteralPath $stderrPath)) {
        [IO.File]::WriteAllText($stderrPath, "", [Text.UTF8Encoding]::new($false))
    }
}

$contract = Get-Content -LiteralPath $contractPath -Raw | ConvertFrom-Json
$outputState = [ordered]@{}
foreach ($name in @("blend", "glb", "manifest", "screenshot_directory")) {
    $relativePath = $contract.output_policy.paths.$name
    $absolutePath = Join-Path $root $relativePath
    $outputState[$name] = [ordered]@{
        path = $relativePath
        exists = [bool](Test-Path -LiteralPath $absolutePath)
    }
}

$allOutputsPresent = (
    $outputState.blend.exists -and
    $outputState.glb.exists -and
    $outputState.manifest.exists -and
    $outputState.screenshot_directory.exists
)
$status = if ($exitCode -eq 0 -and $allOutputsPresent) {
    "BLENDER_EXITED_ZERO_RECOVERY01_DRAFT_OUTPUTS_PRESENT_REVIEW_REQUIRED"
}
elseif ($exitCode -eq 0) {
    "FAILED_BLENDER_EXITED_ZERO_REQUIRED_OUTPUTS_MISSING"
}
else {
    "FAILED_BLENDER_NONZERO_OR_LAUNCH_ERROR"
}

$receipt = [ordered]@{
    schema = "skyguard.phase2.yak52-r4-slice01-recovery01-launch-receipt.v1"
    attempt_id = $attemptId
    status = $status
    started_utc = $startedUtc.ToString("o")
    finished_utc = [DateTime]::UtcNow.ToString("o")
    project_root = $root
    blender_executable = $blender
    blender_file_version = (Get-Item -LiteralPath $blender).VersionInfo.FileVersion
    arguments = $arguments
    process_id = $processId
    exit_code = $exitCode
    launch_error = $launchError
    contract = [ordered]@{
        path = $contractPath.Substring($root.Length + 1).Replace("\", "/")
        sha256 = $contractHash
    }
    authoring_script = [ordered]@{
        path = $authoringPath.Substring($root.Length + 1).Replace("\", "/")
        sha256 = (Get-FileHash -LiteralPath $authoringPath -Algorithm SHA256).Hash.ToLowerInvariant()
    }
    launch_wrapper = [ordered]@{
        path = $wrapperPath.Substring($root.Length + 1).Replace("\", "/")
        sha256 = (Get-FileHash -LiteralPath $wrapperPath -Algorithm SHA256).Hash.ToLowerInvariant()
    }
    stdout = [ordered]@{
        path = "blender.stdout.log"
        bytes = (Get-Item -LiteralPath $stdoutPath).Length
        sha256 = (Get-FileHash -LiteralPath $stdoutPath -Algorithm SHA256).Hash.ToLowerInvariant()
    }
    stderr = [ordered]@{
        path = "blender.stderr.log"
        bytes = (Get-Item -LiteralPath $stderrPath).Length
        sha256 = (Get-FileHash -LiteralPath $stderrPath -Algorithm SHA256).Hash.ToLowerInvariant()
    }
    outputs = $outputState
    unreal_launched_by_wrapper = $false
    automatic_promotion_allowed = $false
    human_review_required = $true
}
$receiptTemp = "$receiptPath.tmp"
[IO.File]::WriteAllText(
    $receiptTemp,
    (($receipt | ConvertTo-Json -Depth 8) + [Environment]::NewLine),
    [Text.UTF8Encoding]::new($false)
)
Move-Item -LiteralPath $receiptTemp -Destination $receiptPath

$sumLines = @(
    "{0}  blender.stdout.log" -f (Get-FileHash -LiteralPath $stdoutPath -Algorithm SHA256).Hash.ToLowerInvariant()
    "{0}  blender.stderr.log" -f (Get-FileHash -LiteralPath $stderrPath -Algorithm SHA256).Hash.ToLowerInvariant()
    "{0}  launch_receipt.json" -f (Get-FileHash -LiteralPath $receiptPath -Algorithm SHA256).Hash.ToLowerInvariant()
)
[IO.File]::WriteAllText(
    $sumsPath,
    (($sumLines -join [Environment]::NewLine) + [Environment]::NewLine),
    [Text.UTF8Encoding]::new($false)
)

$receipt | ConvertTo-Json -Depth 8
if ($status -notlike "BLENDER_EXITED_ZERO_RECOVERY01_DRAFT_OUTPUTS_PRESENT*") {
    exit 1
}
