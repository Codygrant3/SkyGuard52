[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$dotnet = 'D:\UE_5.8\Engine\Binaries\ThirdParty\DotNet\10.0\win-x64\dotnet.exe'
$testRoot = Join-Path $env:TEMP 'SkyguardRecovery02BundledHostTest'
New-Item -ItemType Directory -Path $testRoot -Force | Out-Null

function Invoke-Probe([string[]]$Arguments, [string]$Name) {
    $stdout = Join-Path $testRoot "$Name.stdout.log"
    $stderr = Join-Path $testRoot "$Name.stderr.log"
    $process = Start-Process -FilePath $dotnet -ArgumentList $Arguments -PassThru -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError $stderr
    # Force the native process handle to be retained before a fast child exits.
    $processHandle = $process.Handle
    $process.WaitForExit()
    $process.Refresh()
    if ($null -eq $process.ExitCode -or $process.ExitCode -isnot [int]) {
        throw "$Name returned null or nonnumeric exit code."
    }
    [ordered]@{
        arguments = $Arguments
        pid = $process.Id
        process_handle_retained = ($processHandle -ne [IntPtr]::Zero)
        exit_code = [int]$process.ExitCode
        exit_code_type = $process.ExitCode.GetType().FullName
        stdout = Get-Content -LiteralPath $stdout -Raw -ErrorAction SilentlyContinue
        stderr = Get-Content -LiteralPath $stderr -Raw -ErrorAction SilentlyContinue
    }
}

$success = Invoke-Probe @('--info') 'success'
$missing = Join-Path $testRoot 'intentionally_missing_managed_assembly.dll'
$failure = Invoke-Probe @($missing) 'failure'
if ($success.exit_code -ne 0 -or $success.stdout -notmatch '10\.0') {
    throw 'Bundled .NET 10 success probe failed.'
}
if ($failure.exit_code -eq 0 -or ([string]::IsNullOrWhiteSpace($failure.stdout) -and [string]::IsNullOrWhiteSpace($failure.stderr))) {
    throw 'Bundled .NET failure probe failed.'
}
$nullRejected = $false
try {
    $candidate = $null
    if ($null -eq $candidate) { throw 'null-rejected' }
} catch {
    $nullRejected = $_.Exception.Message -eq 'null-rejected'
}
if (-not $nullRejected) { throw 'Null rejection failed.' }
[ordered]@{
    schema = 'skyguard.recovery03-native-recovery02-bundled-host-test.v1'
    dotnet = $dotnet
    success = $success
    failure = $failure
    null_rejected = $nullRejected
    automation_tool_launched = $false
    gate = 'PASS'
} | ConvertTo-Json -Depth 8
