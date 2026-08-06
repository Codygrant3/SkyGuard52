[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$root = 'D:\Skyguard52'
$editor = 'D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$uproject = Join-Path $root 'Skyguard52.uproject'
$attemptRoot = Join-Path $root 'Saved\BuildAttempts\PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY03\attempt_01'
$proofRoot = Join-Path $attemptRoot 'proof'
$launcherRoot = Join-Path $root 'Saved\BuildAttempts\PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY03\launcher_attempt_01'
$preflightReceipt = Join-Path $root 'Saved\Reports\PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY03_EXECUTION_PREFLIGHT.json'
$pluginBinary = Join-Path $root 'Plugins\SkyguardRecovery03\Binaries\Win64\UnrealEditor-SkyguardRecovery03.dll'
$terminalSupervisorReceipt = Join-Path $launcherRoot 'terminal_supervisor_receipt.json'
$timeoutSeconds = 540

function Write-TerminalSupervisorReceipt {
    param(
        [string]$Gate,
        [object]$ProcessObject,
        [Nullable[int]]$ExitCode,
        [bool]$TimedOut,
        [string]$Issue,
        [string]$StartedUtc
    )
    New-Item -ItemType Directory -Path $launcherRoot -Force | Out-Null
    $exitType = if ($null -eq $ExitCode) { $null } else { $ExitCode.GetType().FullName }
    [ordered]@{
        schema = 'skyguard.recovery03.supervisor-terminal.v1'
        contract_id = 'P4.6-M01-REPRESENTATIVE-VISUAL-008-RECOVERY-03'
        gate = $Gate
        issue = $Issue
        process_id = if ($null -eq $ProcessObject) { $null } else { $ProcessObject.Id }
        started_utc = $StartedUtc
        ended_utc = [DateTime]::UtcNow.ToString('o')
        timed_out = $TimedOut
        actual_exit_code = $ExitCode
        actual_exit_code_type = $exitType
        process_handle_retained = $null -ne $ProcessObject
        automatic_retry = $false
        launch_count = if ($null -eq $ProcessObject) { 0 } else { 1 }
    } | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $terminalSupervisorReceipt -Encoding utf8
}

# This script is intentionally fail-closed until the separate native
# build/rebind gate freezes a compiled Recovery03 plugin binary.
if (-not (Test-Path -LiteralPath $pluginBinary -PathType Leaf)) {
    throw "Recovery03 native plugin binary is absent. Unreal execution is unauthorized until a separate native build/rebind freeze: $pluginBinary"
}
foreach ($reserved in @($attemptRoot, $proofRoot, $launcherRoot, $preflightReceipt)) {
    if (Test-Path -LiteralPath $reserved) {
        throw "Recovery03 namespace is not fresh: $reserved"
    }
}

$heavyNames = @('UnrealEditor', 'UnrealEditor-Cmd', 'ShaderCompileWorker', 'blender', 'AutomationTool', 'UnrealBuildTool')
$heavy = @(Get-Process -ErrorAction SilentlyContinue | Where-Object { $heavyNames -contains $_.ProcessName })
if ($heavy.Count -ne 0) {
    throw "Heavy process preflight failed: $($heavy.ProcessName -join ', ')"
}

New-Item -ItemType Directory -Path $launcherRoot | Out-Null
$logs = Join-Path $launcherRoot 'logs'
New-Item -ItemType Directory -Path $logs | Out-Null
$stdout = Join-Path $logs 'recovery03.stdout.log'
$stderr = Join-Path $logs 'recovery03.stderr.log'
$engineLog = Join-Path $logs 'recovery03.engine.log'
$arguments = @(
    "`"$uproject`"",
    '/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_ProductionEnvironment_v5_attempt03',
    '-dx12',
    '-sm6',
    '-unattended',
    '-nosplash',
    '-NoSound',
    '-NoVSync',
    '-EnablePlugins=SkyguardRecovery03',
    '-DisablePlugins=Fab,Bridge,EditorTelemetry,RuntimeTelemetry,EOSShared',
    '-ini:EditorSettings:[/Script/UnrealEd.AnalyticsPrivacySettings]:bSendUsageData=False',
    '-SkyguardRecovery03ContractId=P4.6-M01-REPRESENTATIVE-VISUAL-008-RECOVERY-03',
    '-SkyguardRecovery03Authorization=P4.6-M01-REPRESENTATIVE-VISUAL-008-RECOVERY-03-ONE-SHOT',
    "-SkyguardRecovery03AttemptRoot=`"$attemptRoot`"",
    '-SkyguardRecovery03ExpectedMap=/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_ProductionEnvironment_v5_attempt03',
    "-abslog=`"$engineLog`""
)

$process = $null
$startedUtc = [DateTime]::UtcNow.ToString('o')
try {
    $process = Start-Process -FilePath $editor -ArgumentList $arguments -PassThru -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError $stderr
    $timedOut = -not $process.WaitForExit($timeoutSeconds * 1000)
    if ($timedOut) {
        Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        $process.WaitForExit()
    }
    $process.Refresh()
    if ($null -eq $process.ExitCode -or $process.ExitCode -isnot [int]) {
        Write-TerminalSupervisorReceipt 'FAILED_WITH_EVIDENCE' $process $null $timedOut 'Null or nonnumeric process exit code.' $startedUtc
        throw 'Recovery03 process exit code was null or nonnumeric.'
    }
    $numericExit = [int]$process.ExitCode
    Write-TerminalSupervisorReceipt $(if ($timedOut -or $numericExit -ne 0) { 'FAILED_WITH_EVIDENCE' } else { 'UNREAL_EXITED_AWAITING_POSTFLIGHT' }) $process $numericExit $timedOut $null $startedUtc
    if ($timedOut -or $numericExit -ne 0) {
        throw "Recovery03 failed with numeric exit code $numericExit (timed_out=$timedOut)."
    }
} catch {
    if (-not (Test-Path -LiteralPath $terminalSupervisorReceipt)) {
        Write-TerminalSupervisorReceipt 'FAILED_WITH_EVIDENCE' $process $null $false $_.Exception.Message $startedUtc
    }
    throw
}

