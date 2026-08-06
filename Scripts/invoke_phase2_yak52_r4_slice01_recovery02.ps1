[CmdletBinding()]
param(
    [string]$ProjectRoot = "D:\Skyguard52",
    [string]$BlenderExe = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe",
    [switch]$AuthorizeProduction
)
$ErrorActionPreference = "Stop"
if (-not $AuthorizeProduction) { throw "Recovery02 is not authorized. Supply -AuthorizeProduction explicitly." }
$root = (Resolve-Path -LiteralPath $ProjectRoot).Path
$blender = (Resolve-Path -LiteralPath $BlenderExe).Path
$contractPath = Join-Path $root "Docs\AAA_Review\PHASE2_YAK52_R4_SLICE01_RECOVERY02_OUTPUT_CONTRACT.json"
$scriptPath = Join-Path $root "Scripts\blender_phase2_yak52_r4_slice01_recovery02.py"
$verifier = Join-Path $root "Scripts\verify_phase2_yak52_r4_slice01_recovery02_readiness.py"
if (Get-Process -Name blender -ErrorAction SilentlyContinue) { throw "Blender is already active; duplicate launch refused." }
python $verifier --root $root --no-write
if ($LASTEXITCODE -ne 0) { throw "Recovery02 readiness failed; Blender was not launched." }

$contractHash = (Get-FileHash $contractPath -Algorithm SHA256).Hash.ToLowerInvariant()
$attemptId = "attempt_{0}_{1}_{2:x8}" -f [DateTime]::UtcNow.ToString("yyyyMMddTHHmmssfffffffZ"),$contractHash.Substring(0,8),$PID
$attemptDir = Join-Path $root "Saved\Reports\Phase2Yak52R4Slice01Recovery02Production\$attemptId"
if (Test-Path $attemptDir) { throw "Attempt collision: $attemptDir" }
New-Item -ItemType Directory -Path $attemptDir | Out-Null
$stdout = Join-Path $attemptDir "blender.stdout.log"
$stderr = Join-Path $attemptDir "blender.stderr.log"
$receiptPath = Join-Path $attemptDir "launch_receipt.json"
$started = [DateTime]::UtcNow
$exitCode = -1
$launchError = $null
$processId = $null
$arguments = @("--background","--factory-startup","--python",$scriptPath)
try {
    $process = Start-Process -FilePath $blender -ArgumentList $arguments -RedirectStandardOutput $stdout -RedirectStandardError $stderr -WindowStyle Hidden -Wait -PassThru
    $processId = $process.Id
    $exitCode = $process.ExitCode
} catch { $launchError = $_.Exception.Message }
if (-not (Test-Path $stdout)) { [IO.File]::WriteAllText($stdout,"",[Text.UTF8Encoding]::new($false)) }
if (-not (Test-Path $stderr)) { [IO.File]::WriteAllText($stderr,"",[Text.UTF8Encoding]::new($false)) }
$contract = Get-Content $contractPath -Raw | ConvertFrom-Json
$outputState = [ordered]@{}
foreach($name in @("blend","glb","manifest","screenshot_directory")){
    $rel=$contract.output_policy.paths.$name
    $outputState[$name]=[ordered]@{path=$rel;exists=[bool](Test-Path (Join-Path $root $rel))}
}
$allPresent=$outputState.blend.exists -and $outputState.glb.exists -and $outputState.manifest.exists -and $outputState.screenshot_directory.exists
$status=if($exitCode -eq 0 -and $allPresent){"BLENDER_EXITED_ZERO_RECOVERY02_DRAFT_OUTPUTS_PRESENT_REVIEW_REQUIRED"}elseif($exitCode -eq 0){"FAILED_BLENDER_EXITED_ZERO_REQUIRED_OUTPUTS_MISSING"}else{"FAILED_BLENDER_NONZERO_OR_LAUNCH_ERROR"}
$receipt=[ordered]@{
    schema="skyguard.phase2.yak52-r4-slice01-recovery02-launch-receipt.v1"
    attempt_id=$attemptId;status=$status;started_utc=$started.ToString("o");finished_utc=[DateTime]::UtcNow.ToString("o")
    blender_executable=$blender;arguments=$arguments;process_id=$processId;exit_code=$exitCode;launch_error=$launchError
    contract=[ordered]@{path="Docs/AAA_Review/PHASE2_YAK52_R4_SLICE01_RECOVERY02_OUTPUT_CONTRACT.json";sha256=$contractHash}
    authoring_script=[ordered]@{path="Scripts/blender_phase2_yak52_r4_slice01_recovery02.py";sha256=(Get-FileHash $scriptPath -Algorithm SHA256).Hash.ToLowerInvariant()}
    stdout=[ordered]@{path="blender.stdout.log";bytes=(Get-Item $stdout).Length;sha256=(Get-FileHash $stdout -Algorithm SHA256).Hash.ToLowerInvariant()}
    stderr=[ordered]@{path="blender.stderr.log";bytes=(Get-Item $stderr).Length;sha256=(Get-FileHash $stderr -Algorithm SHA256).Hash.ToLowerInvariant()}
    outputs=$outputState;unreal_launched_by_wrapper=$false;automatic_promotion_allowed=$false;human_review_required=$true
}
[IO.File]::WriteAllText($receiptPath,(($receipt|ConvertTo-Json -Depth 8)+[Environment]::NewLine),[Text.UTF8Encoding]::new($false))
$sums=@(
"{0}  blender.stdout.log" -f (Get-FileHash $stdout -Algorithm SHA256).Hash.ToLowerInvariant()
"{0}  blender.stderr.log" -f (Get-FileHash $stderr -Algorithm SHA256).Hash.ToLowerInvariant()
"{0}  launch_receipt.json" -f (Get-FileHash $receiptPath -Algorithm SHA256).Hash.ToLowerInvariant()
)
[IO.File]::WriteAllText((Join-Path $attemptDir "SHA256SUMS.txt"),(($sums-join [Environment]::NewLine)+[Environment]::NewLine),[Text.UTF8Encoding]::new($false))
$receipt|ConvertTo-Json -Depth 8
if($status -notlike "BLENDER_EXITED_ZERO_RECOVERY02_DRAFT_OUTPUTS_PRESENT*"){exit 1}
