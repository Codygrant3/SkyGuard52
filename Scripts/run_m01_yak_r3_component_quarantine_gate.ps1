[CmdletBinding()]
param(
    [string]$ProjectRoot = "D:\Skyguard52",
    [string]$UnrealRoot = "D:\UE_5.8",
    [ValidateRange(120, 1800)][int]$StageTimeoutSeconds = 900
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$Project = Join-Path $ProjectRoot "Skyguard52.uproject"
$UnrealCmd = Join-Path $UnrealRoot "Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
$OfflineAudit = Join-Path $ProjectRoot "Scripts\audit_m01_yak_r3_component_import_source.py"
$Builder = Join-Path $ProjectRoot "Scripts\build_m01_yak_r3_component_quarantine.py"
$Verifier = Join-Path $ProjectRoot "Scripts\verify_m01_yak_r3_component_quarantine.py"
$AuditReport = Join-Path $ProjectRoot "Saved\Reports\M01_YAK_R3_COMPONENT_QUARANTINE_AUDIT.json"
$Stamp = [DateTime]::UtcNow.ToString("yyyyMMddTHHmmssfffZ")
$Attempt = Join-Path $ProjectRoot "Saved\BuildAttempts\M01_YAK_R3_COMPONENT_QUARANTINE\attempt_$Stamp"
New-Item -ItemType Directory -Force -Path $Attempt | Out-Null

foreach ($Required in @($Project, $UnrealCmd, $OfflineAudit, $Builder, $Verifier)) {
    if (-not (Test-Path -LiteralPath $Required -PathType Leaf)) {
        throw "Missing required input: $Required"
    }
}

$OfflineOutput = & python $OfflineAudit 2>&1
$OfflineExit = $LASTEXITCODE
$OfflineOutput | Set-Content -LiteralPath (Join-Path $Attempt "offline_source_audit.log") -Encoding utf8
if ($OfflineExit -ne 0) {
    throw "Offline source audit failed; Unreal was not launched."
}

$Active = @(
    Get-CimInstance Win32_Process |
        Where-Object {
            $_.Name -in @(
                "UnrealEditor.exe", "UnrealEditor-Cmd.exe",
                "UnrealBuildTool.exe", "AutomationTool.exe",
                "ShaderCompileWorker.exe", "UbaAgent.exe", "UbaServer.exe",
                "blender.exe"
            ) -or (
                $_.Name -eq "dotnet.exe" -and
                $_.CommandLine -match "UnrealBuildTool|AutomationTool"
            )
        }
)
if ($Active.Count -gt 0) {
    $Summary = $Active | ForEach-Object { "$($_.Name) PID=$($_.ProcessId)" }
    throw "Heavyweight lane is active; no duplicate launched: $($Summary -join ', ')"
}

function Invoke-IsolatedUnrealStage {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$Script,
        [Parameter(Mandatory = $true)][string]$ExpectedSuccessMarker
    )
    $Stdout = Join-Path $Attempt "$Name.stdout.log"
    $Stderr = Join-Path $Attempt "$Name.stderr.log"
    $Arguments = @(
        "`"$Project`"",
        "-run=pythonscript",
        "-script=`"$Script`"",
        "-unattended", "-nop4", "-nosplash", "-NullRHI",
        "-stdout", "-FullStdOutLogOutput", "-NoAssetRegistryCache"
    )
    $Process = Start-Process -FilePath $UnrealCmd -ArgumentList $Arguments `
        -RedirectStandardOutput $Stdout -RedirectStandardError $Stderr `
        -PassThru -WindowStyle Hidden
    if (-not $Process.WaitForExit($StageTimeoutSeconds * 1000)) {
        [ordered]@{
            schema = "skyguard.m01.yak-r3-component-stage.v1"
            stage = $Name
            terminal_state = "ACTIVE_TIMEOUT_WAIT_NEVER_DUPLICATE"
            pid = $Process.Id
            recorded_at_utc = [DateTime]::UtcNow.ToString("o")
        } | ConvertTo-Json | Set-Content -LiteralPath (
            Join-Path $Attempt "$Name.terminal.json"
        ) -Encoding utf8
        throw "$Name PID $($Process.Id) is still active. Wait; never launch a duplicate."
    }
    $Process.WaitForExit()
    $Process.Refresh()
    $Text = (
        Get-Content -LiteralPath $Stdout -Raw -ErrorAction SilentlyContinue
    ) + (
        Get-Content -LiteralPath $Stderr -Raw -ErrorAction SilentlyContinue
    )
    $Markers = @(
        @(
            "Fatal error", "Unhandled Exception", "LogPython: Error:",
            "Python script executed with errors", "Traceback (most recent call last)"
        ) | Where-Object { $Text -match [regex]::Escape($_) }
    )
    $SuccessMarkerPresent = $Text -match [regex]::Escape($ExpectedSuccessMarker)
    $ExitCode = $null
    try {
        $ExitCode = [int]$Process.ExitCode
    }
    catch {
        # Windows PowerShell 5 can expose a null ExitCode for a completed
        # redirected process. In that case the stage remains fail-closed unless
        # its exact success marker is present and no error marker was emitted.
    }
    if ($Markers.Count -gt 0 -or -not $SuccessMarkerPresent -or
        ($null -ne $ExitCode -and $ExitCode -ne 0)) {
        throw "$Name failed: exit=$ExitCode; success_marker=$SuccessMarkerPresent; markers=$($Markers -join ', ')"
    }
    return [ordered]@{
        stage = $Name
        pid = $Process.Id
        exit_code = $ExitCode
        exit_code_available = $null -ne $ExitCode
        success_marker = $ExpectedSuccessMarker
        success_marker_present = $SuccessMarkerPresent
        stdout = $Stdout
        stderr = $Stderr
    }
}

$Stages = @()
$Stages += Invoke-IsolatedUnrealStage `
    -Name "quarantine_import" `
    -Script $Builder `
    -ExpectedSuccessMarker "PASS_QUARANTINE_IMPORT_REQUIRES_FRESH_PROCESS_AUDIT"
$Stages += Invoke-IsolatedUnrealStage `
    -Name "fresh_process_audit" `
    -Script $Verifier `
    -ExpectedSuccessMarker "PASS_QUARANTINE_IMPORT_PERSISTED_NOT_PROMOTABLE"

if (-not (Test-Path -LiteralPath $AuditReport -PathType Leaf)) {
    throw "Fresh-process audit did not emit its report."
}
$Audit = Get-Content -LiteralPath $AuditReport -Raw | ConvertFrom-Json
if ($Audit.gate -ne "PASS_QUARANTINE_IMPORT_PERSISTED_NOT_PROMOTABLE" -or
    $Audit.promotion_allowed -ne $false) {
    throw "Persistence audit did not return the required non-promotable gate."
}

$Receipt = [ordered]@{
    schema = "skyguard.m01.yak-r3-component-quarantine-gate.v1"
    gate = "PASS_QUARANTINE_IMPORT_PERSISTED_NOT_PROMOTABLE"
    completed_at_utc = [DateTime]::UtcNow.ToString("o")
    attempt = $Attempt
    stages = $Stages
    runtime_map_changed = $false
    config_changed = $false
    promotion_allowed = $false
    next_gate = "manual per-component pivot/material/collision/camera/safety evidence"
}
$Receipt | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (
    Join-Path $Attempt "receipt.json"
) -Encoding utf8
$Receipt | ConvertTo-Json -Depth 6
