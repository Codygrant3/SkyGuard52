[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

function Invoke-LightweightExitProbe([int]$RequestedExitCode) {
    $process = Start-Process -FilePath 'powershell.exe' -ArgumentList @(
        '-NoProfile',
        '-NonInteractive',
        '-Command',
        "exit $RequestedExitCode"
    ) -PassThru -WindowStyle Hidden
    $process.WaitForExit()
    $process.Refresh()
    if ($null -eq $process.ExitCode) {
        throw "Null exit code for requested code $RequestedExitCode"
    }
    if ($process.ExitCode -isnot [int]) {
        throw "Nonnumeric exit code type: $($process.ExitCode.GetType().FullName)"
    }
    return [ordered]@{
        requested = $RequestedExitCode
        actual = [int]$process.ExitCode
        type = $process.ExitCode.GetType().FullName
        pid = $process.Id
    }
}

$success = Invoke-LightweightExitProbe 0
$failure = Invoke-LightweightExitProbe 7
if ($success.actual -ne 0 -or $failure.actual -ne 7) {
    throw 'PowerShell exit-code retention probe failed.'
}
$nullRejected = $false
try {
    $value = $null
    if ($null -eq $value) { throw 'expected-null-rejection' }
} catch {
    $nullRejected = $_.Exception.Message -eq 'expected-null-rejection'
}
if (-not $nullRejected) {
    throw 'Null exit-code rejection probe failed.'
}
[ordered]@{
    schema = 'skyguard.recovery03.process-exit-offline-test.v1'
    success = $success
    failure = $failure
    null_rejected = $nullRejected
    gate = 'PASS'
} | ConvertTo-Json -Depth 6

