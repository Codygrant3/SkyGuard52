param(
    [Parameter(Mandatory = $true)]
    [string]$OutputPath
)

$ErrorActionPreference = 'Stop'

function Test-CapturedExitCode($Value) {
    if ($null -eq $Value) { throw 'Captured exit code is null.' }
    if ($Value -isnot [System.Int32]) { throw "Captured exit-code type is invalid: $($Value.GetType().FullName)" }
    return [ordered]@{ exit_code = [System.Int32]$Value; exit_code_type = $Value.GetType().FullName }
}

function Invoke-ExitProbe([int]$RequestedExitCode, [string]$Root) {
    $stdout = Join-Path $Root "exit_$RequestedExitCode.stdout.log"
    $stderr = Join-Path $Root "exit_$RequestedExitCode.stderr.log"
    $arguments = @('-NoProfile', '-Command', "Start-Sleep -Milliseconds 250; exit $RequestedExitCode")
    $process = Start-Process -FilePath 'powershell.exe' -ArgumentList $arguments -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru
    $nativeHandle = $process.Handle
    if ($nativeHandle -eq [IntPtr]::Zero) { throw "Native handle was not retained for exit $RequestedExitCode probe." }
    $process.WaitForExit()
    $process.Refresh()
    $capturedExitCode = $process.ExitCode
    $validated = Test-CapturedExitCode $capturedExitCode
    return [ordered]@{
        requested_exit_code = $RequestedExitCode
        captured_exit_code = $validated.exit_code
        exit_code_type = $validated.exit_code_type
        native_handle_retained = $true
        native_handle_nonzero = $true
        launch_count = 1
        retry_count = 0
        stdout = $stdout
        stderr = $stderr
    }
}

$root = Split-Path -Parent $OutputPath
if (-not (Test-Path -LiteralPath $root)) { New-Item -ItemType Directory -Path $root | Out-Null }
$result = [ordered]@{
    classification = 'FAIL'
    host = 'powershell.exe -NoProfile -ExecutionPolicy Bypass'
    success_probe = $null
    failure_probe = $null
    null_probe = [ordered]@{
        rejected = $false
        get_type_called_on_null = $false
        coerced_to_zero = $false
        terminal_evidence = $false
    }
    child_launch_count = 0
    retry_count = 0
    blender_launch_count = 0
    unreal_launch_count = 0
    error = $null
}

try {
    $result.success_probe = Invoke-ExitProbe 0 $root
    $result.child_launch_count++
    $result.failure_probe = Invoke-ExitProbe 7 $root
    $result.child_launch_count++
    try {
        $null = Test-CapturedExitCode $null
    }
    catch {
        $result.null_probe.rejected = $true
        $result.null_probe.terminal_evidence = -not [string]::IsNullOrWhiteSpace($_.Exception.Message)
    }
    if ($result.success_probe.captured_exit_code -ne 0) { throw 'Success probe did not capture exit code 0.' }
    if ($result.failure_probe.captured_exit_code -ne 7) { throw 'Failure probe did not capture exit code 7.' }
    if ($result.success_probe.exit_code_type -ne 'System.Int32' -or $result.failure_probe.exit_code_type -ne 'System.Int32') {
        throw 'Probe exit-code type was not System.Int32.'
    }
    if (-not $result.null_probe.rejected) { throw 'Null exit-code probe was not rejected.' }
    $result.classification = 'PASS'
}
catch {
    $result.error = $_.Exception.Message
}
finally {
    [System.IO.File]::WriteAllText(
        $OutputPath,
        ($result | ConvertTo-Json -Depth 12) + [Environment]::NewLine,
        [System.Text.UTF8Encoding]::new($false)
    )
}

if ($result.classification -eq 'PASS') { exit 0 }
exit 91
