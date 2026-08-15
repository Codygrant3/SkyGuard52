[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$OutputRoot,
    [Parameter(Mandatory = $true)]
    [string]$ExecutorPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$captureScript = 'D:\Skyguard52\Scripts\ToolchainWave08\environment_authoring01_recovery07_mapped_visual_proof01_recovery03\capture_native_argv_recovery03.py'
$python = (Get-Command python -ErrorAction Stop).Source
$captureOutput = Join-Path $OutputRoot 'captured_argv.json'
$testResult = Join-Path $OutputRoot 'transport_test_result.json'
$stdout = Join-Path $OutputRoot 'argv_capture.stdout.log'
$stderr = Join-Path $OutputRoot 'argv_capture.stderr.log'
$exitCode = 1

function Write-JsonAtomic([string]$Path, $Value) {
    $temporary = "$Path.tmp.$PID"
    [System.IO.File]::WriteAllText(
        $temporary,
        (($Value | ConvertTo-Json -Depth 10) + [Environment]::NewLine),
        [System.Text.UTF8Encoding]::new($false)
    )
    [System.IO.File]::Move($temporary, $Path)
}

try {
    if (Test-Path -LiteralPath $OutputRoot) { throw "Output root already exists: $OutputRoot" }
    [System.IO.Directory]::CreateDirectory($OutputRoot) | Out-Null
    if (-not (Test-Path -LiteralPath $captureScript -PathType Leaf)) { throw 'Argv capture script is absent' }
    if (-not (Test-Path -LiteralPath $ExecutorPath -PathType Leaf)) { throw 'Executor path is absent' }

    $env:SKYGUARD_RECOVERY03_ARGV_OUTPUT = $captureOutput
    $execCmdValue = "py $($ExecutorPath.Replace('\','/'))"
    $execCmdArgument = '-ExecCmds="' + $execCmdValue + '"'
    $arguments = @($captureScript, $execCmdArgument, '-Sentinel=after')
    $process = Start-Process -FilePath $python -ArgumentList $arguments -PassThru -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError $stderr
    $handle = $process.Handle
    $process.WaitForExit()
    $process.Refresh()
    $childCode = $process.ExitCode
    if ($null -eq $childCode -or -not ($childCode -is [int])) { throw 'Argv fixture exit code is null or nonnumeric' }
    if ($childCode -ne 0) { throw "Argv fixture failed with exit code $childCode" }
    if (-not (Test-Path -LiteralPath $captureOutput -PathType Leaf)) { throw 'Argv capture output is absent' }
    $captured = Get-Content -LiteralPath $captureOutput -Raw | ConvertFrom-Json
    if ($captured.argv.Count -ne 2) { throw "Expected two native arguments after the capture script; got $($captured.argv.Count)" }
    $expectedExecCmd = "-ExecCmds=py $($ExecutorPath.Replace('\','/'))"
    if ($captured.argv[0] -ne $expectedExecCmd) { throw "ExecCmds argument split or changed: $($captured.argv[0])" }
    if ($captured.argv[1] -ne '-Sentinel=after') { throw 'Sentinel argument changed' }
    $result = [ordered]@{
        schema = 'skyguard.t08.m01.recovery07-mapped-proof01-recovery03-transport-test.v1'
        classification = 'PASS'
        executable = $python
        process_handle_retained = $null -ne $handle
        exit_code = [int]$childCode
        exit_code_type = $childCode.GetType().FullName
        captured_argument_count = $captured.argv.Count
        exec_cmd_argument = $captured.argv[0]
        sentinel = $captured.argv[1]
        unreal_launch_count = 0
        retry_count = 0
    }
    Write-JsonAtomic $testResult $result
    $exitCode = 0
}
catch {
    $failure = [ordered]@{
        schema = 'skyguard.t08.m01.recovery07-mapped-proof01-recovery03-transport-test.v1'
        classification = 'FAILED_WITH_EVIDENCE'
        error = $_.Exception.Message
        unreal_launch_count = 0
        retry_count = 0
    }
    if (Test-Path -LiteralPath $OutputRoot) {
        try { Write-JsonAtomic $testResult $failure } catch {}
    }
    [Console]::Error.WriteLine($_.Exception.Message)
    $exitCode = 1
}
finally {
    Remove-Item Env:SKYGUARD_RECOVERY03_ARGV_OUTPUT -ErrorAction SilentlyContinue
}

exit ([int]$exitCode)

