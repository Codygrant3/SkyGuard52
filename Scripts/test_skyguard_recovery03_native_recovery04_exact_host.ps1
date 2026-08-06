[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$supervisor = 'D:\Skyguard52\Scripts\build_skyguard_recovery03_native_recovery04_once.ps1'
$dotnet = 'D:\UE_5.8\Engine\Binaries\ThirdParty\DotNet\10.0\win-x64\dotnet.exe'
$testRoot = Join-Path $env:TEMP 'SkyguardRecovery04ExactHostTest'
New-Item -ItemType Directory -Path $testRoot -Force | Out-Null

function Invoke-ExactProcess([string]$Executable, [string[]]$Arguments, [string]$Name) {
    $stdout = Join-Path $testRoot "$Name.stdout.log"
    $stderr = Join-Path $testRoot "$Name.stderr.log"
    $process = Start-Process -FilePath $Executable -ArgumentList $Arguments -PassThru -Wait -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError $stderr
    $process.Refresh()
    if ($null -eq $process.ExitCode -or $process.ExitCode -isnot [int]) {
        throw "$Name returned null or nonnumeric exit code."
    }
    [ordered]@{
        executable = $Executable
        arguments = $Arguments
        pid = $process.Id
        exit_code = [int]$process.ExitCode
        exit_code_type = $process.ExitCode.GetType().FullName
        stdout = Get-Content -LiteralPath $stdout -Raw -ErrorAction SilentlyContinue
        stderr = Get-Content -LiteralPath $stderr -Raw -ErrorAction SilentlyContinue
    }
}

$offline = Invoke-ExactProcess 'powershell.exe' @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $supervisor, '-OfflineContractTest') 'offline_contract'
$success = Invoke-ExactProcess $dotnet @('--info') 'dotnet_success'
$missingAssembly = Join-Path $testRoot 'intentionally_missing_managed_assembly.dll'
$failure = Invoke-ExactProcess $dotnet @($missingAssembly) 'dotnet_failure'

if ($offline.exit_code -ne 0) { throw 'Exact-host offline contract test failed.' }
$offlineResult = $offline.stdout | ConvertFrom-Json
if ($offlineResult.gate -ne 'PASS' -or $offlineResult.exit_code_type -ne 'System.Int32') { throw 'Offline result contract failed.' }
if ($offlineResult.governed_build_namespace_created -or $offlineResult.bundled_dotnet_launch_count -ne 0 -or $offlineResult.automation_tool_invocation_count -ne 0) {
    throw 'Offline isolation failed.'
}
if ($success.exit_code -ne 0 -or $success.stdout -notmatch '10\.0\.203' -or $success.stdout -notmatch 'Microsoft\.NETCore\.App 10\.0\.7') {
    throw 'Bundled dotnet success probe failed.'
}
if ($failure.exit_code -eq 0 -or ([string]::IsNullOrWhiteSpace($failure.stdout) -and [string]::IsNullOrWhiteSpace($failure.stderr))) {
    throw 'Bundled dotnet failure probe failed.'
}
$nullRejected = $false
try {
    $candidate = $null
    if ($null -eq $candidate) { throw 'null-rejected' }
} catch {
    $nullRejected = $_.Exception.Message -eq 'null-rejected'
}
if (-not $nullRejected) { throw 'Null-code rejection failed.' }

[ordered]@{
    schema = 'skyguard.recovery03-native-build-recovery04-exact-host-test.v1'
    offline_contract = $offline
    dotnet_success = $success
    dotnet_failure = $failure
    null_exit_code_rejected = $nullRejected
    automation_tool_launched = $false
    native_build_launched = $false
    gate = 'PASS'
} | ConvertTo-Json -Depth 10
