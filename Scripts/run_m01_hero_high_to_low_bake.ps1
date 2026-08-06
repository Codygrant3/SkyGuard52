[CmdletBinding()]
param(
    [string]$ProjectRoot = "D:\Skyguard52",
    [string]$BlenderExe = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe",
    [ValidateRange(60, 3600)]
    [int]$TimeoutSeconds = 1800,
    [switch]$ValidateOnly
)

$ErrorActionPreference = "Stop"
$generator = Join-Path $ProjectRoot "Scripts\blender_m01_hero_high_to_low_bake.py"
$verifier = Join-Path $ProjectRoot "Scripts\verify_skyguard_m01_hero_high_to_low_bake.py"
$reportRoot = Join-Path $ProjectRoot "Saved\BuildAttempts\M01_HERO_HIGH_TO_LOW_BAKE"
$stamp = [DateTime]::UtcNow.ToString("yyyyMMddTHHmmssfffZ")
$attemptRoot = Join-Path $reportRoot "attempt_$stamp"
New-Item -ItemType Directory -Path $attemptRoot -Force | Out-Null

$preflightPath = Join-Path $attemptRoot "source_readiness.json"
& python $verifier --root $ProjectRoot --output $preflightPath
if ($LASTEXITCODE -ne 0) {
    throw "High-to-low source readiness failed. See $preflightPath"
}

if ($ValidateOnly) {
    Write-Host "SOURCE_READY_ARTIFACTS_NOT_RUN: $preflightPath"
    exit 0
}

if (-not (Test-Path -LiteralPath $BlenderExe -PathType Leaf)) {
    throw "Blender executable not found: $BlenderExe"
}
if (-not (Test-Path -LiteralPath $generator -PathType Leaf)) {
    throw "Generator not found: $generator"
}

$activeBlender = Get-Process -Name "blender" -ErrorAction SilentlyContinue
if ($activeBlender) {
    throw "A Blender process is already active. Refusing to overlap serialized asset builds."
}

$stdoutPath = Join-Path $attemptRoot "blender.stdout.log"
$stderrPath = Join-Path $attemptRoot "blender.stderr.log"
$pidPath = Join-Path $attemptRoot "blender.pid"
$startedAtUtc = [DateTime]::UtcNow
$process = Start-Process `
    -FilePath $BlenderExe `
    -ArgumentList @("--background", "--factory-startup", "--python", $generator) `
    -WorkingDirectory $ProjectRoot `
    -RedirectStandardOutput $stdoutPath `
    -RedirectStandardError $stderrPath `
    -WindowStyle Hidden `
    -PassThru
Set-Content -LiteralPath $pidPath -Value ([string]$process.Id) -Encoding ascii

$completed = $process.WaitForExit($TimeoutSeconds * 1000)
if (-not $completed) {
    Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
    $process.WaitForExit()
    throw "Blender build exceeded ${TimeoutSeconds}s and its child process was terminated. See $attemptRoot"
}
$process.WaitForExit()
if ($process.ExitCode -ne 0) {
    throw "Blender build exited $($process.ExitCode). See $attemptRoot"
}

$postflightPath = Join-Path $attemptRoot "artifact_verification.json"
& python $verifier `
    --root $ProjectRoot `
    --output $postflightPath `
    --require-artifacts
if ($LASTEXITCODE -ne 0) {
    throw "High-to-low artifact verification failed. See $postflightPath"
}

$summary = [ordered]@{
    schema = "skyguard.m01.hero-high-to-low-bake.supervisor.v1"
    build_id = "BLD_M01_HERO_HILO_001"
    gate = "PASS"
    terminal_state = "ARTIFACTS_VERIFIED_CANDIDATE_ONLY"
    started_at_utc = $startedAtUtc.ToString("o")
    finished_at_utc = [DateTime]::UtcNow.ToString("o")
    blender_exit_code = $process.ExitCode
    attempt_root = $attemptRoot
    source_readiness = $preflightPath
    artifact_verification = $postflightPath
    stdout = $stdoutPath
    stderr = $stderrPath
    promotion = "high_to_low_bake_candidate_requires_blender_execution_artifact_verification_and_unreal_visual_acceptance"
}
$summaryPath = Join-Path $attemptRoot "supervisor_summary.json"
$summary | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $summaryPath -Encoding utf8
Write-Host "ARTIFACTS_VERIFIED_CANDIDATE_ONLY: $summaryPath"
