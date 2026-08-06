[CmdletBinding()]
param(
    [string]$ProjectRoot = "D:\Skyguard52",
    [string]$BlenderExe = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe",
    [string]$ContractPath = "",
    [ValidateRange(60, 7200)]
    [int]$TimeoutSeconds = 3600
)

$ErrorActionPreference = "Stop"
$contract = if ($ContractPath) {
    [System.IO.Path]::GetFullPath($ContractPath)
}
else {
    Join-Path $ProjectRoot "Docs\AAA_Review\M01_HERO_GROUPED_TOPOLOGY_BAKE_003_CONTRACT.json"
}
$contractData = Get-Content -LiteralPath $contract -Raw | ConvertFrom-Json
$buildId = [string]$contractData.build_id
if (-not $buildId) {
    throw "Contract does not declare build_id: $contract"
}
function Resolve-ProjectPath([string]$RawPath) {
    if ([System.IO.Path]::IsPathRooted($RawPath)) {
        return [System.IO.Path]::GetFullPath($RawPath)
    }
    return Join-Path $ProjectRoot $RawPath
}
$generator = Join-Path $ProjectRoot "Scripts\blender_m01_hero_grouped_topology_bake.py"
$verifier = Join-Path $ProjectRoot "Scripts\verify_skyguard_m01_hero_grouped_topology_bake.py"
$supervisorSource = $MyInvocation.MyCommand.Path
$manifest = Resolve-ProjectPath ([string]$contractData.outputs.manifest)
$authorReport = Resolve-ProjectPath ([string]$contractData.outputs.report)
$masterBlend = Resolve-ProjectPath ([string]$contractData.outputs.master_blend)
$lowGlb = Resolve-ProjectPath ([string]$contractData.outputs.low_glb)
$textureRoot = Resolve-ProjectPath ([string]$contractData.outputs.texture_root)
$canonicalOutputs = @($manifest, $authorReport, $masterBlend, $lowGlb, $textureRoot)

$attemptSlug = $buildId -replace '^BLD_', ''
$attemptBase = Join-Path $ProjectRoot "Saved\BuildAttempts\$attemptSlug"
$stamp = [DateTime]::UtcNow.ToString("yyyyMMddTHHmmssfffZ")
$attemptRoot = Join-Path $attemptBase "attempt_$stamp"
$inputArchive = Join-Path $attemptRoot "inputs"
$artifactArchive = Join-Path $attemptRoot "artifacts"
New-Item -ItemType Directory -Path $inputArchive -Force | Out-Null
New-Item -ItemType Directory -Path $artifactArchive -Force | Out-Null

$startedAtUtc = [DateTime]::UtcNow
$stage = "PREFLIGHT"
$process = $null
$exitCode = $null
$terminalState = "SUPERVISOR_FAILED"
$failure = $null
$sourceVerification = Join-Path $attemptRoot "source_verification.json"
$artifactVerification = Join-Path $attemptRoot "artifact_verification.json"
$stdoutPath = Join-Path $attemptRoot "blender.stdout.log"
$stderrPath = Join-Path $attemptRoot "blender.stderr.log"
$pidPath = Join-Path $attemptRoot "blender.pid"

$inputFiles = @($contract, $generator, $verifier, $supervisorSource)
if ($contractData.extends_contract) {
    $inputFiles += Resolve-ProjectPath ([string]$contractData.extends_contract)
}
if ($contractData.classification_report) {
    $inputFiles += Resolve-ProjectPath ([string]$contractData.classification_report)
}
foreach ($inputFile in $inputFiles) {
    Copy-Item -LiteralPath $inputFile -Destination $inputArchive
}

try {
    if (-not (Test-Path -LiteralPath $BlenderExe -PathType Leaf)) {
        throw "Blender executable not found: $BlenderExe"
    }
    if (Get-Process -Name "blender" -ErrorAction SilentlyContinue) {
        throw "A Blender process is already active. Refusing to overlap the exclusive heavy lane."
    }
    $existing = @($canonicalOutputs | Where-Object { Test-Path -LiteralPath $_ })
    if ($existing.Count -gt 0) {
        throw "$buildId is immutable and already has canonical output(s): $($existing -join ', '). Author a new build id instead of overwriting."
    }

    & python $verifier `
        --root $ProjectRoot `
        --contract $contract `
        --generator $generator `
        --manifest $manifest `
        --output $sourceVerification
    if ($LASTEXITCODE -ne 0) {
        throw "$buildId source verification failed. See $sourceVerification"
    }

    $stage = "BLENDER_AUTHORING"
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
        throw "$buildId Blender build exceeded ${TimeoutSeconds}s."
    }
    $process.WaitForExit()
    $exitCode = $process.ExitCode
    if ($exitCode -ne 0) {
        throw "$buildId Blender build exited $exitCode."
    }
    $stderrText = if (Test-Path -LiteralPath $stderrPath) {
        Get-Content -LiteralPath $stderrPath -Raw
    }
    else {
        ""
    }
    if ($stderrText -match '(?m)^Traceback \(most recent call last\):') {
        throw "$buildId emitted a Python traceback despite Blender exit 0."
    }

    $stage = "ARTIFACT_VERIFICATION"
    & python $verifier `
        --root $ProjectRoot `
        --contract $contract `
        --generator $generator `
        --manifest $manifest `
        --output $artifactVerification `
        --require-artifacts
    if ($LASTEXITCODE -ne 0) {
        throw "$buildId artifact verification failed. See $artifactVerification"
    }

    $stage = "IMMUTABLE_ARCHIVE"
    $textureArchive = Join-Path $artifactArchive "textures"
    Copy-Item -LiteralPath $textureRoot -Destination $textureArchive -Recurse
    foreach ($file in @(
        $masterBlend,
        $lowGlb,
        $manifest,
        $authorReport,
        $contract,
        $generator,
        $verifier,
        $supervisorSource
    )) {
        Copy-Item -LiteralPath $file -Destination $artifactArchive
    }

    $manifestData = Get-Content -LiteralPath $manifest -Raw | ConvertFrom-Json
    $reviewQueue = @()
    foreach ($asset in $manifestData.assets) {
        foreach ($group in $asset.groups) {
            foreach ($map in $group.maps) {
                $reviewQueue += [ordered]@{
                    asset = $asset.id
                    group = $group.id
                    map_type = $map.type
                    source_path = $map.path
                    sha256 = $map.sha256
                    width = $map.width
                    height = $map.height
                    review_mode = "DIRECT_ORIGINAL_RESOLUTION"
                    review_status = "PENDING"
                }
            }
        }
    }
    $reviewQueuePath = Join-Path $attemptRoot "direct_map_review_queue.json"
    [ordered]@{
        schema = "skyguard.m01.hero-grouped-topology-bake.map-review-queue.v1"
        build_id = $buildId
        required_map_count = 24
        reviewed_map_count = 0
        overall_gate = "NOT_REVIEWED"
        maps = $reviewQueue
    } | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $reviewQueuePath -Encoding utf8

    $hashes = Get-ChildItem -LiteralPath $artifactArchive -File -Recurse |
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
    $terminalState = "ARTIFACTS_VERIFIED_AWAITING_DIRECT_ORIGINAL_RESOLUTION_MAP_REVIEW"
    $stage = "COMPLETE"
}
catch {
    $failure = $_.Exception.Message
    throw
}
finally {
    $summary = [ordered]@{
        schema = "skyguard.m01.hero-grouped-topology-bake.supervisor.v1"
        build_id = $buildId
        gate = if ($terminalState -like "ARTIFACTS_VERIFIED*") { "PASS" } else { "FAIL" }
        terminal_state = $terminalState
        final_stage = $stage
        started_at_utc = $startedAtUtc.ToString("o")
        finished_at_utc = [DateTime]::UtcNow.ToString("o")
        blender_exit_code = $exitCode
        attempt_root = $attemptRoot
        source_verification = $sourceVerification
        artifact_verification = $artifactVerification
        stdout = $stdoutPath
        stderr = $stderrPath
        direct_map_review_queue = Join-Path $attemptRoot "direct_map_review_queue.json"
        direct_original_resolution_map_review = "NOT_REVIEWED"
        mapped_mesh_grazing_angle_review = "NOT_RUN"
        unreal_acceptance = "NOT_RUN"
        promotion_authorized = $false
        p3_4_closed = $false
        failure = $failure
    }
    $summaryPath = Join-Path $attemptRoot "supervisor_summary.json"
    $summary | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $summaryPath -Encoding utf8
}

Write-Host (Join-Path $attemptRoot "supervisor_summary.json")
