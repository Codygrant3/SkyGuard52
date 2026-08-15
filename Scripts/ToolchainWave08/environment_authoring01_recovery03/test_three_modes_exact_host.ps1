param()

$ErrorActionPreference = 'Stop'
$Target = 'D:\Skyguard52\Scripts\ToolchainWave08\environment_authoring01_recovery03\invoke_dependency_probe_once.ps1'
$ResultPath = 'D:\Skyguard52\Saved\Reports\ToolchainWave08\EnvironmentAuthoring01Recovery03OfflineDesign\exact_host_test_result.json'
$FuturePaths = @(
    'D:\Skyguard52\Saved\BuildAttempts\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY03_DEPENDENCY_PROBE\attempt_01',
    'D:\Skyguard52\Saved\Reports\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY03_DEPENDENCY_PROBE_TERMINAL_MANIFEST.json',
    'D:\Skyguard52\Saved\Reports\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY03_DEPENDENCY_PROBE_EMERGENCY_RECEIPT.jsonl',
    'D:\Skyguard52\Saved\BuildAttempts\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY03\attempt_01',
    'D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentAuthoring01_Recovery03.umap'
)

function Write-JsonAtomic([string]$Path, $Value) {
    $parent = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $parent)) { [System.IO.Directory]::CreateDirectory($parent) | Out-Null }
    $temporary = "$Path.tmp"
    $Value | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $temporary -Encoding UTF8
    Move-Item -LiteralPath $temporary -Destination $Path -Force
}

function Invoke-TestProcess([string[]]$ModeArguments) {
    $info = [System.Diagnostics.ProcessStartInfo]::new()
    $info.FileName = 'powershell.exe'
    $all = @('-NoProfile','-ExecutionPolicy','Bypass','-File',('"'+$Target+'"')) + $ModeArguments
    $info.Arguments = $all -join ' '
    $info.UseShellExecute = $false
    $info.CreateNoWindow = $true
    $info.RedirectStandardOutput = $true
    $info.RedirectStandardError = $true
    $process = [System.Diagnostics.Process]::new()
    $process.StartInfo = $info
    $started = [DateTime]::UtcNow
    if (-not $process.Start()) { throw 'Exact-host test child failed to start' }
    $stdoutTask = $process.StandardOutput.ReadToEndAsync()
    $stderrTask = $process.StandardError.ReadToEndAsync()
    $process.WaitForExit()
    $process.Refresh()
    $stdout = $stdoutTask.GetAwaiter().GetResult()
    $stderr = $stderrTask.GetAwaiter().GetResult()
    $code = $process.ExitCode
    $record = [ordered]@{
        arguments = $ModeArguments
        pid = $process.Id
        started_at_utc = $started.ToString('o')
        completed_at_utc = [DateTime]::UtcNow.ToString('o')
        exit_code = $code
        exit_code_type = $code.GetType().FullName
        stdout = $stdout
        stderr = $stderr
    }
    $process.Dispose()
    return $record
}

if (Test-Path -LiteralPath $ResultPath) { throw "Exact-host result already exists: $ResultPath" }
$existingBefore = @($FuturePaths | Where-Object { Test-Path -LiteralPath $_ })
if ($existingBefore.Count -ne 0) { throw "Governed namespace existed before exact-host tests: $($existingBefore -join ', ')" }
$heavyBefore = @(Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -match '^(UnrealEditor|UnrealEditor-Cmd|Blender|ShaderCompileWorker|AutomationTool|UnrealBuildTool|cl|link)$' })
if ($heavyBefore.Count -ne 0) { throw 'Heavy process existed before exact-host tests' }

$offline = Invoke-TestProcess @('-OfflineContractTest')
$refusal = Invoke-TestProcess @()
$conflict = Invoke-TestProcess @('-OfflineContractTest','-AuthorizeSingleDependencyProbe')
$failures = @()

if ($offline.exit_code -ne 0 -or $offline.exit_code_type -ne 'System.Int32') { $failures += 'Offline contract mode exit contract failed' }
if ($refusal.exit_code -ne 2 -or $refusal.exit_code_type -ne 'System.Int32') { $failures += 'Authorization-refusal exit contract failed' }
if ($conflict.exit_code -ne 3 -or $conflict.exit_code_type -ne 'System.Int32') { $failures += 'Conflicting-switch exit contract failed' }

$offlineSummaryMatch = [regex]::Match($offline.stdout, '(?m)^OFFLINE_TEST_SUMMARY=(.+)$')
if (-not $offlineSummaryMatch.Success) { $failures += 'Offline test summary path was not emitted' }
$offlineSummaryPath = if ($offlineSummaryMatch.Success) { $offlineSummaryMatch.Groups[1].Value.Trim() } else { $null }
if ($offlineSummaryPath -and (Test-Path -LiteralPath $offlineSummaryPath -PathType Leaf)) {
    $summary = Get-Content -Raw -LiteralPath $offlineSummaryPath | ConvertFrom-Json
    if ($summary.classification -ne 'PASS' -or $summary.unreal_launch_count -ne 0 -or $summary.retry_count -ne 0) { $failures += 'Offline temporary summary validation failed' }
    foreach($path in @($summary.success_terminal,$summary.failure_terminal,$summary.emergency_receipt)) { if (-not(Test-Path -LiteralPath $path -PathType Leaf)) { $failures += "Offline evidence missing: $path" } }
} elseif ($offlineSummaryPath) { $failures += "Offline summary does not exist: $offlineSummaryPath" }

$refusalMatch = [regex]::Match($refusal.stdout, '(?m)^AUTHORIZATION_REFUSAL_RECEIPT=(.+)$')
if (-not $refusalMatch.Success) { $failures += 'Authorization-refusal receipt path was not emitted' }
$refusalPath = if ($refusalMatch.Success) { $refusalMatch.Groups[1].Value.Trim() } else { $null }
if ($refusalPath -and (Test-Path -LiteralPath $refusalPath -PathType Leaf)) {
    $refusalReceipt = Get-Content -Raw -LiteralPath $refusalPath | ConvertFrom-Json
    if ($refusalReceipt.classification -ne 'AUTHORIZATION_REQUIRED' -or $refusalReceipt.unreal_launch_count -ne 0) { $failures += 'Authorization-refusal receipt validation failed' }
} elseif ($refusalPath) { $failures += "Authorization-refusal receipt does not exist: $refusalPath" }

$existingAfter = @($FuturePaths | Where-Object { Test-Path -LiteralPath $_ })
if ($existingAfter.Count -ne 0) { $failures += "Exact-host tests created governed namespace: $($existingAfter -join ', ')" }
$heavyAfter = @(Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -match '^(UnrealEditor|UnrealEditor-Cmd|Blender|ShaderCompileWorker|AutomationTool|UnrealBuildTool|cl|link)$' })
if ($heavyAfter.Count -ne 0) { $failures += 'Heavy process exists after exact-host tests' }

$result = [ordered]@{
    schema = 'skyguard.toolchain-wave08.m01-authoring01-recovery03.three-mode-exact-host-test.v1'
    classification = if ($failures.Count -eq 0) { 'PASS' } else { 'FAIL' }
    offline_contract = $offline
    authorization_refusal = $refusal
    conflicting_switches = $conflict
    offline_summary_path = $offlineSummaryPath
    authorization_refusal_receipt = $refusalPath
    governed_before = $existingBefore
    governed_after = $existingAfter
    unreal_launch_count = 0
    retry_count = 0
    failures = $failures
}
Write-JsonAtomic $ResultPath $result
Write-Host "EXACT_HOST_RESULT=$ResultPath"
Write-Host "CLASSIFICATION=$($result.classification)"
if ($failures.Count -ne 0) { [Environment]::Exit([int]1) }
[Environment]::Exit([int]0)
