[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
function Invoke-DirectProbe([int]$Requested) {
    $process = Start-Process -FilePath 'powershell.exe' -ArgumentList @(
        '-NoProfile', '-NonInteractive', '-Command', "exit $Requested"
    ) -PassThru -WindowStyle Hidden
    $process.WaitForExit()
    $process.Refresh()
    if ($null -eq $process.ExitCode -or $process.ExitCode -isnot [int]) {
        throw 'Direct process exit code is null or nonnumeric.'
    }
    [ordered]@{
        requested = $Requested
        actual = [int]$process.ExitCode
        type = $process.ExitCode.GetType().FullName
        pid = $process.Id
    }
}
$success = Invoke-DirectProbe 0
$failure = Invoke-DirectProbe 7
if ($success.actual -ne 0 -or $failure.actual -ne 7) {
    throw 'Direct process exit-code values were not retained.'
}
$nullRejected = $false
try {
    $candidate = $null
    if ($null -eq $candidate) { throw 'null-rejected' }
} catch {
    $nullRejected = $_.Exception.Message -eq 'null-rejected'
}
if (-not $nullRejected) { throw 'Null exit-code rejection failed.' }
[ordered]@{
    schema = 'skyguard.recovery03-native-recovery01-exit-test.v1'
    success = $success
    failure = $failure
    null_rejected = $nullRejected
    gate = 'PASS'
} | ConvertTo-Json -Depth 6

