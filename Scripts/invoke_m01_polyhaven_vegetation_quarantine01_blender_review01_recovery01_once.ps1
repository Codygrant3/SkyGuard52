param([switch]$AuthorizeSingleBlender)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

if (-not $AuthorizeSingleBlender) {
    [Console]::Error.WriteLine('Refusing Blender launch without -AuthorizeSingleBlender.')
    exit 2
}

$Blender = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
$Worker = 'D:\Skyguard52\Scripts\Workers\review_m01_polyhaven_vegetation_quarantine01.py'
$Attempt = 'D:\Skyguard52\Saved\BuildAttempts\M01_POLYHAVEN_VEGETATION_QUARANTINE01_BLENDER_REVIEW01_RECOVERY01\attempt_01'
$Output = 'D:\Skyguard52\Blender\M01_POLYHAVEN_VEGETATION_QUARANTINE01_BLENDER_REVIEW01_RECOVERY01_ATTEMPT01'
if ((Test-Path -LiteralPath $Attempt) -or (Test-Path -LiteralPath $Output)) {
    throw 'Fresh governed Recovery01 attempt or output namespace already exists.'
}
New-Item -ItemType Directory -Path $Attempt | Out-Null
$Stdout = Join-Path $Attempt 'stdout.log'
$Stderr = Join-Path $Attempt 'stderr.log'
$Started = [DateTime]::UtcNow.ToString('o')
$Process = $null
$ExitCode = $null
$TimedOut = $false
$Validated = $false
$FailureMessage = $null
try {
    $Args = @('--background', '--factory-startup', '--python-exit-code', '7', '--python', $Worker, '--', '--output', $Output)
    $Process = Start-Process -FilePath $Blender -ArgumentList $Args -PassThru -RedirectStandardOutput $Stdout -RedirectStandardError $Stderr
    if (-not $Process.WaitForExit(900000)) {
        $TimedOut = $true
        $Process.Kill()
        $Process.WaitForExit()
    }
    $Process.Refresh()
    $ExitCode = [int]$Process.ExitCode
    if ($TimedOut -or $ExitCode -ne 0) {
        throw "Blender review failed. timeout=$TimedOut exit=$ExitCode"
    }
    $Receipt = Join-Path $Output 'review_receipt.json'
    $Blend = Join-Path $Output 'M01_PolyHaven_Vegetation_Quarantine01_Review01.blend'
    $Renders = @(Get-ChildItem -LiteralPath (Join-Path $Output 'renders') -Filter '*.png' -File)
    if (-not (Test-Path -LiteralPath $Receipt) -or -not (Test-Path -LiteralPath $Blend) -or $Renders.Count -ne 5) {
        throw "Required output validation failed: receipt=$([bool](Test-Path $Receipt)) blend=$([bool](Test-Path $Blend)) renders=$($Renders.Count)"
    }
    $ReceiptData = Get-Content -LiteralPath $Receipt -Raw | ConvertFrom-Json
    if ($ReceiptData.classification -ne 'PASSED_AUTOMATIC_AWAITING_DIRECT_VISUAL_REVIEW') {
        throw "Unexpected receipt classification: $($ReceiptData.classification)"
    }
    $Validated = $true
}
catch {
    $FailureMessage = $_.Exception.Message
    throw
}
finally {
    $Files = @()
    if (Test-Path -LiteralPath $Output) {
        $Files = @(Get-ChildItem -LiteralPath $Output -Recurse -File | ForEach-Object {
            [ordered]@{ path = $_.FullName; bytes = $_.Length; sha256 = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant() }
        })
    }
    $Terminal = [ordered]@{
        schema = 'skyguard.m01-polyhaven-vegetation-quarantine01-blender-review01-recovery01-terminal.v1'
        created_at_utc = [DateTime]::UtcNow.ToString('o')
        started_at_utc = $Started
        classification = if ($Validated) { 'PASSED_AUTOMATIC_AWAITING_DIRECT_VISUAL_REVIEW' } else { 'FAILED_WITH_EVIDENCE' }
        failure_message = $FailureMessage
        executable = $Blender
        worker = $Worker
        process_id = if ($null -ne $Process) { $Process.Id } else { $null }
        exit_code = $ExitCode
        exit_code_type = if ($null -ne $ExitCode) { $ExitCode.GetType().FullName } else { $null }
        timed_out = $TimedOut
        required_outputs_validated = $Validated
        launch_count = if ($null -ne $Process) { 1 } else { 0 }
        retry_count = 0
        stdout = $Stdout
        stderr = $Stderr
        output = $Output
        files = $Files
        unreal_launched = $false
        runtime_promoted = $false
    }
    $Terminal | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath (Join-Path $Attempt 'terminal.json') -Encoding utf8
}

exit $ExitCode
