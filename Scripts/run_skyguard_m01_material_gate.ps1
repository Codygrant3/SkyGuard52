param(
    [string]$Project = "D:\Skyguard52\Skyguard52.uproject",
    [string]$EditorCmd = "D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
)

$ErrorActionPreference = "Stop"
$root = "D:\Skyguard52"
$script = Join-Path $root "Scripts\build_skyguard_m01_refinement_material_validation.py"
$statusPath = Join-Path $root "Saved\Reports\M01_REFINEMENT_MATERIAL_GATE_STATUS.json"
$gui = @(Get-Process -Name "UnrealEditor" -ErrorAction SilentlyContinue)

if ($gui.Count -gt 0) {
    $status = [ordered]@{
        schema = "skyguard.m01.refinement.material-gate-status.v1"
        gate = "BLOCKED_OPEN_EDITOR"
        checked_at_utc = [DateTime]::UtcNow.ToString("o")
        blocker = "A visible UnrealEditor may own source packages or unsaved user state."
        editor_processes = @($gui | ForEach-Object {
            [ordered]@{
                pid = $_.Id
                start_time = $_.StartTime.ToUniversalTime().ToString("o")
                main_window_title = $_.MainWindowTitle
            }
        })
        preserved_failed_attempt_log = (Join-Path $root "Saved\Logs\M01_REFINEMENT_MATERIAL_BUILD.stdout.log")
        rerun_command = "$PSCommandPath"
    }
    $status | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $statusPath -Encoding UTF8
    Write-Output ($status | ConvertTo-Json -Depth 5)
    exit 2
}

$attempt = 1
do {
    $attemptName = "M01_REFINEMENT_MATERIAL_CLEAN_{0:D2}" -f $attempt
    $stdout = Join-Path $root "Saved\Logs\$attemptName.stdout.log"
    $stderr = Join-Path $root "Saved\Logs\$attemptName.stderr.log"
    $attempt++
} while ((Test-Path -LiteralPath $stdout) -or (Test-Path -LiteralPath $stderr))

$arguments = @(
    $Project,
    "-ExecutePythonScript=$script",
    "-unattended",
    "-nop4",
    "-nosplash",
    "-NullRHI",
    "-stdout",
    "-FullStdOutLogOutput",
    "-NoAssetRegistryCache"
)
$process = Start-Process -FilePath $EditorCmd -ArgumentList $arguments `
    -RedirectStandardOutput $stdout -RedirectStandardError $stderr `
    -PassThru -WindowStyle Hidden
$process.WaitForExit()

$fatalPattern = "LogPython: Error|Traceback|RuntimeError|Fatal error|Error saving"
$fatalLines = @(Select-String -LiteralPath $stdout -Pattern $fatalPattern)
$auditPath = Join-Path $root "Saved\Reports\M01_REFINEMENT_MATERIAL_UNREAL_AUDIT.json"
$budgetPath = Join-Path $root "Saved\Reports\M01_REFINEMENT_TEXTURE_BUDGET.json"
$audit = if (Test-Path -LiteralPath $auditPath) { Get-Content $auditPath -Raw | ConvertFrom-Json } else { $null }
$budget = if (Test-Path -LiteralPath $budgetPath) { Get-Content $budgetPath -Raw | ConvertFrom-Json } else { $null }
$passed = (
    $process.ExitCode -eq 0 -and
    $fatalLines.Count -eq 0 -and
    $null -ne $audit -and $audit.gate -eq "PASS" -and
    $null -ne $budget -and $budget.gate -eq "READY_FOR_RUNTIME_PROFILE"
)

if ($passed) {
    $verifyScript = Join-Path $root "Scripts\verify_skyguard_m01_refinement_material_persistence.py"
    $verifyStdout = $stdout.Replace(".stdout.log", ".persistence.stdout.log")
    $verifyStderr = $stderr.Replace(".stderr.log", ".persistence.stderr.log")
    $verifyArguments = @(
        $Project,
        "-ExecutePythonScript=$verifyScript",
        "-unattended",
        "-nop4",
        "-nosplash",
        "-NullRHI",
        "-stdout",
        "-FullStdOutLogOutput",
        "-NoAssetRegistryCache"
    )
    $verify = Start-Process -FilePath $EditorCmd -ArgumentList $verifyArguments `
        -RedirectStandardOutput $verifyStdout -RedirectStandardError $verifyStderr `
        -PassThru -WindowStyle Hidden
    $verify.WaitForExit()
    $verifyFatalLines = @(Select-String -LiteralPath $verifyStdout -Pattern $fatalPattern)
    $verifyAuditPath = Join-Path $root "Saved\Reports\M01_REFINEMENT_MATERIAL_PERSISTENCE_AUDIT.json"
    $verifyAudit = if (Test-Path -LiteralPath $verifyAuditPath) { Get-Content $verifyAuditPath -Raw | ConvertFrom-Json } else { $null }
    $passed = (
        $verify.ExitCode -eq 0 -and
        $verifyFatalLines.Count -eq 0 -and
        $null -ne $verifyAudit -and $verifyAudit.gate -eq "PASS"
    )
}

$status = [ordered]@{
    schema = "skyguard.m01.refinement.material-gate-status.v1"
    gate = if ($passed) { "PASS" } else { "BUILD_OR_PERSISTENCE_FAIL" }
    checked_at_utc = [DateTime]::UtcNow.ToString("o")
    editor_exit_code = $process.ExitCode
    stdout = $stdout
    stderr = $stderr
    fatal_line_count = $fatalLines.Count
    material_audit = $auditPath
    texture_budget = $budgetPath
    persistence_audit = (Join-Path $root "Saved\Reports\M01_REFINEMENT_MATERIAL_PERSISTENCE_AUDIT.json")
}
$status | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $statusPath -Encoding UTF8
Write-Output ($status | ConvertTo-Json -Depth 5)
if (-not $passed) { exit 1 }
