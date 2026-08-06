[CmdletBinding()]
param(
    [string]$ProjectRoot = "D:\Skyguard52",
    [string]$BlenderExe = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe",
    [ValidateRange(60, 3600)]
    [int]$TimeoutSeconds = 1800
)

$ErrorActionPreference = "Stop"
$contract = Join-Path $ProjectRoot "Docs\AAA_Review\M01_HERO_HIGH_TO_LOW_BAKE_CORRECTIVE_002_CONTRACT.json"
$generator = Join-Path $ProjectRoot "Scripts\blender_m01_hero_high_to_low_bake.py"
$verifier = Join-Path $ProjectRoot "Scripts\verify_skyguard_m01_hero_high_to_low_corrective_002.py"
$attemptRootBase = Join-Path $ProjectRoot "Saved\BuildAttempts\M01_HERO_HIGH_TO_LOW_BAKE_CORRECTIVE_002"
$stamp = [DateTime]::UtcNow.ToString("yyyyMMddTHHmmssfffZ")
$attemptRoot = Join-Path $attemptRootBase "attempt_$stamp"
New-Item -ItemType Directory -Path $attemptRoot -Force | Out-Null

if (-not (Test-Path -LiteralPath $BlenderExe -PathType Leaf)) {
    throw "Blender executable not found: $BlenderExe"
}
if (Get-Process -Name "blender" -ErrorAction SilentlyContinue) {
    throw "A Blender process is already active. Refusing to overlap serialized asset builds."
}

$stdoutPath = Join-Path $attemptRoot "blender.stdout.log"
$stderrPath = Join-Path $attemptRoot "blender.stderr.log"
$pidPath = Join-Path $attemptRoot "blender.pid"
$startedAtUtc = [DateTime]::UtcNow
$arguments = @(
    "--background",
    "--factory-startup",
    "--python",
    $generator,
    "--",
    "--contract",
    $contract
)
$process = Start-Process `
    -FilePath $BlenderExe `
    -ArgumentList $arguments `
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
    throw "Corrective Blender build exceeded ${TimeoutSeconds}s. See $attemptRoot"
}
$process.WaitForExit()
if ($process.ExitCode -ne 0) {
    throw "Corrective Blender build exited $($process.ExitCode). See $attemptRoot"
}

$manifest = Join-Path $ProjectRoot "Saved\Reports\M01_HERO_HIGH_TO_LOW_BAKE_MANIFEST_002.json"
$verificationPath = Join-Path $attemptRoot "artifact_verification.json"
& python $verifier `
    --root $ProjectRoot `
    --contract $contract `
    --generator $generator `
    --manifest $manifest `
    --output $verificationPath
if ($LASTEXITCODE -ne 0) {
    throw "Corrective artifact verification failed. See $verificationPath"
}

$artifactRoot = Join-Path $attemptRoot "artifacts"
$textureArchive = Join-Path $artifactRoot "textures"
New-Item -ItemType Directory -Path $textureArchive -Force | Out-Null
$sourceTextureRoot = Join-Path $ProjectRoot "Content\Skyguard\Textures\Source\Mission01\HeroHighToLow_002"
Copy-Item -LiteralPath $sourceTextureRoot -Destination $textureArchive -Recurse

$archiveFiles = @(
    (Join-Path $ProjectRoot "Content\Skyguard\Meshes\Source\Mission01\HeroHighToLow_002\BLD_M01_HERO_HILO_002_MASTER.blend"),
    (Join-Path $ProjectRoot "Content\Skyguard\Meshes\Source\Mission01\HeroHighToLow_002\bld_m01_hero_hilo_002_low.glb"),
    $manifest,
    (Join-Path $ProjectRoot "Saved\Reports\M01_HERO_HIGH_TO_LOW_BAKE_REPORT_002.json"),
    $contract,
    $generator,
    $verifier
)
foreach ($file in $archiveFiles) {
    Copy-Item -LiteralPath $file -Destination $artifactRoot
}

$hashes = Get-ChildItem -LiteralPath $artifactRoot -File -Recurse |
    Sort-Object FullName |
    ForEach-Object {
        $hash = Get-FileHash -Algorithm SHA256 -LiteralPath $_.FullName
        [ordered]@{
            relative_path = [System.IO.Path]::GetRelativePath($attemptRoot, $_.FullName)
            bytes = $_.Length
            sha256 = $hash.Hash.ToLower()
        }
    }
$hashPath = Join-Path $attemptRoot "SHA256SUMS.json"
$hashes | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $hashPath -Encoding utf8

$summary = [ordered]@{
    schema = "skyguard.m01.hero-high-to-low-bake.corrective-supervisor.v1"
    build_id = "BLD_M01_HERO_HILO_002"
    gate = "PASS"
    terminal_state = "ARTIFACTS_VERIFIED_AWAITING_MAP_VISUAL_REVIEW"
    started_at_utc = $startedAtUtc.ToString("o")
    finished_at_utc = [DateTime]::UtcNow.ToString("o")
    blender_exit_code = $process.ExitCode
    attempt_root = $attemptRoot
    artifact_verification = $verificationPath
    immutable_hashes = $hashPath
    stdout = $stdoutPath
    stderr = $stderrPath
    map_visual_gate = "NOT_REVIEWED"
    p3_4_closed = $false
}
$summaryPath = Join-Path $attemptRoot "supervisor_summary.json"
$summary | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $summaryPath -Encoding utf8
Write-Host $summaryPath
