[CmdletBinding()]
param(
    [string]$ProjectRoot = "D:\Skyguard52",
    [ValidateRange(60, 1800)][int]$TimeoutSeconds = 900
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$blender = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
$generator = Join-Path $ProjectRoot "Scripts\blender_bld_m01_yak_uplift_003_r3.py"
$verifier = Join-Path $ProjectRoot "Scripts\verify_bld_m01_yak_uplift_003_r3.py"
$stamp = [DateTime]::UtcNow.ToString("yyyyMMddTHHmmssfffZ")
$attempt = Join-Path $ProjectRoot (
    "Saved\BuildAttempts\BLD_M01_YAK_UPLIFT_003_R3\attempt_$stamp"
)
New-Item -ItemType Directory -Force -Path $attempt | Out-Null

foreach ($file in @($blender, $generator, $verifier)) {
    if (-not (Test-Path -LiteralPath $file -PathType Leaf)) {
        throw "Missing required file: $file"
    }
}

$active = @(Get-CimInstance Win32_Process | Where-Object {
    $_.Name -in @(
        "UnrealEditor.exe",
        "UnrealEditor-Cmd.exe",
        "UnrealBuildTool.exe",
        "AutomationTool.exe",
        "ShaderCompileWorker.exe",
        "UbaAgent.exe",
        "UbaServer.exe",
        "blender.exe"
    ) -or
    ($_.Name -eq "dotnet.exe" -and
        $_.CommandLine -match "UnrealBuildTool|AutomationTool")
})
if ($active.Count) {
    throw "Shared heavyweight lane is active; refusing duplicate launch."
}

$stdout = Join-Path $attempt "blender.stdout.log"
$stderr = Join-Path $attempt "blender.stderr.log"
$process = Start-Process -FilePath $blender `
    -ArgumentList @(
        "--background",
        "--factory-startup",
        "--python",
        $generator
    ) `
    -RedirectStandardOutput $stdout `
    -RedirectStandardError $stderr `
    -PassThru `
    -WindowStyle Hidden

[ordered]@{
    schema = "skyguard.blender-supervisor.v1"
    build_id = "BLD-M01-YAK-UPLIFT-003-R3"
    pid = $process.Id
    started_utc = [DateTime]::UtcNow.ToString("o")
    stdout = $stdout
    stderr = $stderr
} | ConvertTo-Json |
    Set-Content -LiteralPath (Join-Path $attempt "process.json") -Encoding utf8

if (-not $process.WaitForExit($TimeoutSeconds * 1000)) {
    [ordered]@{
        terminal_state = "ACTIVE_TIMEOUT_WAIT_NEVER_DUPLICATE"
        pid = $process.Id
        recorded_utc = [DateTime]::UtcNow.ToString("o")
    } | ConvertTo-Json |
        Set-Content -LiteralPath (Join-Path $attempt "terminal.json") -Encoding utf8
    throw "Blender PID $($process.Id) is still active after the supervisor window."
}

$process.WaitForExit()
$process.Refresh()
$combined = (
    Get-Content -LiteralPath $stdout -Raw -ErrorAction SilentlyContinue
) + (
    Get-Content -LiteralPath $stderr -Raw -ErrorAction SilentlyContinue
)
$bad = @(
    "Traceback (most recent call last)",
    "TypeError:",
    "RuntimeError:",
    "Blender quit"
) | Where-Object {
    $_ -ne "Blender quit" -and
    $combined -match [regex]::Escape($_)
}

$exitCode = $process.ExitCode
if ($null -eq $exitCode -and
    $combined -match [regex]::Escape(
        "[BLD-M01-YAK-UPLIFT-003-R3] provisional R3 comparison candidate emitted"
    )) {
    $exitCode = 0
}

if ($null -eq $exitCode -or $exitCode -ne 0 -or $bad.Count) {
    [ordered]@{
        terminal_state = "FAILED_GENERATOR"
        pid = $process.Id
        exit_code = $exitCode
        markers = $bad
        completed_utc = [DateTime]::UtcNow.ToString("o")
    } | ConvertTo-Json -Depth 4 |
        Set-Content -LiteralPath (Join-Path $attempt "terminal.json") -Encoding utf8
    throw "R3 Blender generator failed. Preserve this attempt and never overwrite."
}

$artifactStdout = Join-Path $attempt "artifact.stdout.log"
$artifactStderr = Join-Path $attempt "artifact.stderr.log"
& py -3 $verifier --artifacts 1> $artifactStdout 2> $artifactStderr
$artifactExit = $LASTEXITCODE
if ($artifactExit -ne 0) {
    [ordered]@{
        terminal_state = "FAILED_ARTIFACT_GATE"
        pid = $process.Id
        blender_exit_code = $exitCode
        artifact_exit_code = $artifactExit
        completed_utc = [DateTime]::UtcNow.ToString("o")
    } | ConvertTo-Json |
        Set-Content -LiteralPath (Join-Path $attempt "terminal.json") -Encoding utf8
    throw "R3 artifact gate failed. Preserve this attempt and never overwrite."
}

[ordered]@{
    terminal_state = "PASS_ARTIFACT_GATE_REQUIRES_VISUAL_REVIEW"
    pid = $process.Id
    blender_exit_code = $exitCode
    artifact_exit_code = $artifactExit
    completed_utc = [DateTime]::UtcNow.ToString("o")
} | ConvertTo-Json |
    Set-Content -LiteralPath (Join-Path $attempt "terminal.json") -Encoding utf8

Write-Output $attempt
