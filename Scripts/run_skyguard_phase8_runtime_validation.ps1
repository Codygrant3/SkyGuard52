[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$PackageAttemptRoot,
    [string]$ProjectRoot = "D:\Skyguard52",
    [ValidateRange(30, 600)]
    [int]$LaunchTimeoutSeconds = 180
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$packageAttempt = (Resolve-Path -LiteralPath $PackageAttemptRoot).Path
$attemptId = Split-Path $packageAttempt -Leaf
$packageRoot = Join-Path $packageAttempt "packages\Development\Windows"
$executable = Join-Path $packageRoot "Skyguard52.exe"
$verifier = Join-Path $ProjectRoot "Scripts\verify_skyguard_phase8_runtime_receipt.py"
foreach ($required in @($executable, $verifier)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
        throw "Required packaged-runtime validation input is missing: $required"
    }
}

$stamp = [DateTime]::UtcNow.ToString("yyyyMMddTHHmmssfffZ")
$attemptRoot = Join-Path $packageAttempt "artifacts\runtime_validation_$stamp"
New-Item -ItemType Directory -Force -Path $attemptRoot | Out-Null

function Get-PortableSha256 {
    param([Parameter(Mandatory = $true)][string]$LiteralPath)
    $algorithm = [System.Security.Cryptography.SHA256]::Create()
    try {
        $stream = [System.IO.File]::OpenRead($LiteralPath)
        try {
            return ([System.BitConverter]::ToString(
                $algorithm.ComputeHash($stream))).Replace("-", "").ToLowerInvariant()
        } finally {
            $stream.Dispose()
        }
    } finally {
        $algorithm.Dispose()
    }
}

function ConvertTo-Argument {
    param([Parameter(Mandatory = $true)][string]$Value)
    if ($Value -notmatch '[\s"]') { return $Value }
    return '"' + ($Value -replace '(\\*)"', '$1$1\"' -replace '(\\+)$', '$1$1') + '"'
}

function Stop-ExactProcessTree {
    param([Parameter(Mandatory = $true)][int]$RootProcessId)
    & taskkill.exe /PID $RootProcessId /T /F | Out-Null
}

function Invoke-ValidationLaunch {
    param([Parameter(Mandatory = $true)][int]$Phase)
    $artifact = Join-Path $attemptRoot "phase_$Phase.json"
    $stdout = Join-Path $attemptRoot "phase_$Phase.stdout.log"
    $stderr = Join-Path $attemptRoot "phase_$Phase.stderr.log"
    $arguments = @(
        "/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_Playable_v1",
        "-RenderOffscreen", "-ResX=1280", "-ResY=720",
        "-d3d12", "-sm6", "-NoVSync",
        "-SkyguardRuntimeValidationPhase=$Phase",
        "-SkyguardRuntimeValidationArtifact=$artifact",
        "-unattended", "-nosplash", "-stdout", "-FullStdOutLogOutput"
    )
    $argumentLine = ($arguments | ForEach-Object { ConvertTo-Argument $_ }) -join " "
    $process = Start-Process -FilePath $executable -ArgumentList $argumentLine `
        -WorkingDirectory $packageRoot -WindowStyle Hidden -PassThru `
        -RedirectStandardOutput $stdout -RedirectStandardError $stderr
    $deadline = (Get-Date).AddSeconds($LaunchTimeoutSeconds)
    while (-not $process.HasExited -and (Get-Date) -lt $deadline) {
        Start-Sleep -Milliseconds 500
        $process.Refresh()
    }
    $timedOut = -not $process.HasExited
    if ($timedOut) {
        Stop-ExactProcessTree -RootProcessId $process.Id
    }
    $process.WaitForExit()
    $process.Refresh()
    $exitCode = $null
    try { $exitCode = [int]$process.ExitCode } catch { $exitCode = $null }
    if ($timedOut) {
        throw "Packaged runtime phase $Phase timed out; exact PID tree $($process.Id) terminated."
    }
    if (-not (Test-Path -LiteralPath $artifact -PathType Leaf)) {
        throw "Packaged runtime phase $Phase produced no artifact: $artifact"
    }
    $result = Get-Content -LiteralPath $artifact -Raw | ConvertFrom-Json
    if ($result.schema -ne "skyguard.packaged-runtime-validation-launch.v1" -or
        [int]$result.phase -ne $Phase -or $result.gate -ne "PASS") {
        throw "Packaged runtime phase $Phase artifact is not PASS."
    }
    return [ordered]@{
        phase = $Phase
        pid = $process.Id
        exit_code = $exitCode
        timed_out = $false
        log = $stdout
        stderr = $stderr
        artifact = $artifact
        result = $result
    }
}

function Convert-Cases {
    param(
        [Parameter(Mandatory = $true)]$Cases,
        [Parameter(Mandatory = $true)][string]$Artifact
    )
    return @(
        $Cases | ForEach-Object {
            [ordered]@{
                name = [string]$_.name
                result = [string]$_.result
                detail = [string]$_.detail
                artifact = $Artifact
            }
        }
    )
}

$phaseOne = Invoke-ValidationLaunch -Phase 1
$phaseTwo = Invoke-ValidationLaunch -Phase 2

$receiptPath = Join-Path $attemptRoot "runtime_validation_receipt.json"
$verificationPath = Join-Path $attemptRoot "runtime_validation_verification.json"
$receipt = [ordered]@{
    schema = "skyguard.phase8.runtime-validation-receipt.v1"
    gate = "PASS"
    package_attempt_id = $attemptId
    package_configuration = "Development"
    package_executable_sha256 = Get-PortableSha256 -LiteralPath $executable
    input = "PASS"
    save_round_trip = "PASS"
    settings_round_trip = "PASS"
    evidence = [ordered]@{
        input_cases = Convert-Cases `
            -Cases $phaseTwo.result.input_cases -Artifact $phaseTwo.artifact
        save_cases = Convert-Cases `
            -Cases $phaseTwo.result.save_cases -Artifact $phaseTwo.artifact
        settings_cases = Convert-Cases `
            -Cases $phaseTwo.result.settings_cases -Artifact $phaseTwo.artifact
        launches = @(
            [ordered]@{
                pid = $phaseOne.pid
                exit_code = $phaseOne.exit_code
                timed_out = $phaseOne.timed_out
                log = $phaseOne.log
            },
            [ordered]@{
                pid = $phaseTwo.pid
                exit_code = $phaseTwo.exit_code
                timed_out = $phaseTwo.timed_out
                log = $phaseTwo.log
            }
        )
    }
}
$receipt | ConvertTo-Json -Depth 14 |
    Set-Content -LiteralPath $receiptPath -Encoding utf8

& py -3 $verifier `
    --receipt $receiptPath `
    --package-executable $executable `
    --expected-attempt-id $attemptId `
    --report $verificationPath
if ($LASTEXITCODE -ne 0) {
    throw "Independent packaged runtime receipt verification failed."
}
$verification = Get-Content -LiteralPath $verificationPath -Raw | ConvertFrom-Json
if ($verification.gate -ne "PASS") {
    throw "Packaged runtime validation is not PASS."
}

$latest = Join-Path $ProjectRoot "Saved\Reports\PHASE8_RUNTIME_VALIDATION_LATEST.json"
Copy-Item -LiteralPath $verificationPath -Destination $latest -Force
Write-Output "PHASE8_RUNTIME_VALIDATION=PASS"
Write-Output "RECEIPT=$receiptPath"
Write-Output "VERIFICATION=$verificationPath"
