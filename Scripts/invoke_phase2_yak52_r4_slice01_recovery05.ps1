[CmdletBinding()]
param(
    [string]$ProjectRoot = "D:\Skyguard52",
    [string]$BlenderExe = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe",
    [switch]$AuthorizeProduction
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

if (-not $AuthorizeProduction) {
    throw "Recovery05 requires explicit -AuthorizeProduction."
}

$root = (Resolve-Path -LiteralPath $ProjectRoot).Path
$blender = (Resolve-Path -LiteralPath $BlenderExe).Path
$script = Join-Path $root "Scripts\blender_phase2_yak52_r4_slice01_recovery05.py"
$contract = Join-Path $root "Docs\AAA_Review\PHASE2_YAK52_R4_SLICE01_RECOVERY05_OUTPUT_CONTRACT.json"
$verifier = Join-Path $root "Scripts\verify_phase2_yak52_r4_slice01_recovery05.py"

if (Get-Process -Name "blender" -ErrorAction SilentlyContinue) {
    throw "An active Blender process exists; duplicate Recovery05 launch refused."
}

& python $verifier --root $root
if ($LASTEXITCODE -ne 0) {
    throw "Recovery05 readiness failed; Blender was not launched."
}

$contractHash = (Get-FileHash -LiteralPath $contract -Algorithm SHA256).Hash.ToLowerInvariant()
$attemptId = "attempt_{0}_{1}_{2:x8}" -f [DateTime]::UtcNow.ToString("yyyyMMddTHHmmssfffffffZ"), $contractHash.Substring(0, 8), $PID
$attemptRoot = Join-Path $root "Saved\Reports\Phase2Yak52R4Slice01Recovery05Production"
$attemptDir = Join-Path $attemptRoot $attemptId
if (Test-Path -LiteralPath $attemptDir) {
    throw "Recovery05 attempt collision: $attemptDir"
}
New-Item -ItemType Directory -Path $attemptDir | Out-Null

$stdout = Join-Path $attemptDir "blender.stdout.log"
$stderr = Join-Path $attemptDir "blender.stderr.log"
$receiptPath = Join-Path $attemptDir "launch_receipt.json"
$startedUtc = [DateTime]::UtcNow.ToString("o")

$process = Start-Process -FilePath $blender `
    -ArgumentList @("--background", "--factory-startup", "--python", $script) `
    -RedirectStandardOutput $stdout `
    -RedirectStandardError $stderr `
    -WindowStyle Hidden `
    -Wait `
    -PassThru

$contractData = Get-Content -Raw -LiteralPath $contract | ConvertFrom-Json
$outputState = [ordered]@{}
foreach ($entry in $contractData.outputs.PSObject.Properties) {
    $absolute = Join-Path $root $entry.Value
    $exists = Test-Path -LiteralPath $absolute
    $item = [ordered]@{
        path = $entry.Value
        exists = [bool]$exists
    }
    if ($exists -and (Test-Path -LiteralPath $absolute -PathType Leaf)) {
        $file = Get-Item -LiteralPath $absolute
        $item["bytes"] = [int64]$file.Length
        $item["sha256"] = (Get-FileHash -LiteralPath $absolute -Algorithm SHA256).Hash.ToLowerInvariant()
    }
    $outputState[$entry.Name] = $item
}

$allOutputsExist = (
    $outputState.blend.exists -and
    $outputState.glb.exists -and
    $outputState.manifest.exists -and
    $outputState.comparison_directory.exists
)
$status = if ($process.ExitCode -eq 0 -and $allOutputsExist) {
    "PASS_DRAFT_REFERENCE_PACKAGE_MISSING"
} else {
    "FAILED_RECOVERY05_REQUIRED_OUTPUTS_MISSING"
}

$receipt = [ordered]@{
    schema = "skyguard.phase2.slice01.recovery05.launch.v1"
    attempt_id = $attemptId
    status = $status
    started_utc = $startedUtc
    finished_utc = [DateTime]::UtcNow.ToString("o")
    exit_code = $process.ExitCode
    contract_sha256 = $contractHash
    authoring_source_sha256 = (Get-FileHash -LiteralPath $script -Algorithm SHA256).Hash.ToLowerInvariant()
    outputs = $outputState
    classification = "DRAFT_REFERENCE_PACKAGE_MISSING"
    unreal_launched = $false
    promotion_allowed = $false
}
[IO.File]::WriteAllText(
    $receiptPath,
    (($receipt | ConvertTo-Json -Depth 8) + [Environment]::NewLine),
    [Text.UTF8Encoding]::new($false)
)

$sumLines = [System.Collections.Generic.List[string]]::new()
$sumLines.Add(((Get-FileHash -LiteralPath $stdout -Algorithm SHA256).Hash.ToLowerInvariant() + "  blender.stdout.log"))
$sumLines.Add(((Get-FileHash -LiteralPath $stderr -Algorithm SHA256).Hash.ToLowerInvariant() + "  blender.stderr.log"))
$sumLines.Add(((Get-FileHash -LiteralPath $receiptPath -Algorithm SHA256).Hash.ToLowerInvariant() + "  launch_receipt.json"))
[IO.File]::WriteAllLines(
    (Join-Path $attemptDir "SHA256SUMS.txt"),
    $sumLines,
    [Text.UTF8Encoding]::new($false)
)

if ($status -ne "PASS_DRAFT_REFERENCE_PACKAGE_MISSING") {
    exit 1
}
