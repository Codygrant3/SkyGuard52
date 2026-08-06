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
$OfflineAudit = Join-Path $ProjectRoot "Scripts\audit_m01_hero_grouped_topology_unreal_acceptance_008.py"
$Builder = Join-Path $ProjectRoot "Scripts\build_m01_hero_grouped_topology_unreal_candidate_008.py"
$Verifier = Join-Path $ProjectRoot "Scripts\verify_m01_hero_grouped_topology_unreal_candidate_008.py"
$PersistenceReport = Join-Path $ProjectRoot "Saved\Reports\M01_HERO_GROUPED_TOPOLOGY_UNREAL_CANDIDATE_008_PERSISTENCE.json"
$CandidateRoot = "/Game/Skyguard/Candidates/Mission01/HeroGroupedTopology_008"
$Stamp = [DateTime]::UtcNow.ToString("yyyyMMddTHHmmssfffZ")
$Attempt = Join-Path $ProjectRoot "Saved\BuildAttempts\M01_HERO_GROUPED_TOPOLOGY_UNREAL_008\attempt_$Stamp"
New-Item -ItemType Directory -Force -Path $Attempt | Out-Null

foreach ($Required in @($Project, $UnrealCmd, $OfflineAudit, $Builder, $Verifier)) {
    if (-not (Test-Path -LiteralPath $Required -PathType Leaf)) {
        throw "Missing required input: $Required"
    }
}

$OfflineOutput = & python $OfflineAudit 2>&1
$OfflineExit = $LASTEXITCODE
$OfflineOutput | Set-Content -LiteralPath (Join-Path $Attempt "offline_readiness.log") -Encoding utf8
if ($OfflineExit -ne 0) {
    throw "Offline readiness failed; Unreal was not launched."
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
    throw "Exclusive lane active; no duplicate launched: $($Summary -join ', ')"
}

function Invoke-IsolatedStage {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$Script,
        [Parameter(Mandatory = $true)][string]$SuccessMarker
    )
    $Stdout = Join-Path $Attempt "$Name.stdout.log"
    $Stderr = Join-Path $Attempt "$Name.stderr.log"
    $Arguments = @(
        "`"$Project`"", "-run=pythonscript", "-script=`"$Script`"",
        "-unattended", "-nop4", "-nosplash", "-NullRHI",
        "-stdout", "-FullStdOutLogOutput", "-NoAssetRegistryCache"
    )
    $Process = Start-Process -FilePath $UnrealCmd -ArgumentList $Arguments `
        -RedirectStandardOutput $Stdout -RedirectStandardError $Stderr `
        -PassThru -WindowStyle Hidden
    if (-not $Process.WaitForExit($StageTimeoutSeconds * 1000)) {
        [ordered]@{
            schema = "skyguard.m01.grouped008.unreal-stage.v1"
            stage = $Name
            terminal_state = "ACTIVE_TIMEOUT_WAIT_NEVER_DUPLICATE"
            pid = $Process.Id
            recorded_at_utc = [DateTime]::UtcNow.ToString("o")
        } | ConvertTo-Json | Set-Content -LiteralPath (
            Join-Path $Attempt "$Name.terminal.json"
        ) -Encoding utf8
        throw "$Name PID $($Process.Id) remains active. Wait; never duplicate."
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
    $Success = $Text -match [regex]::Escape($SuccessMarker)
    $ExitCode = $null
    try { $ExitCode = [int]$Process.ExitCode } catch {}
    if ($Markers.Count -gt 0 -or -not $Success -or
        ($null -ne $ExitCode -and $ExitCode -ne 0)) {
        throw "$Name failed: exit=$ExitCode marker=$Success errors=$($Markers -join ', ')"
    }
    return [ordered]@{
        stage = $Name
        pid = $Process.Id
        exit_code = $ExitCode
        success_marker = $SuccessMarker
        stdout = $Stdout
        stderr = $Stderr
    }
}

$Stages = @()
$Stages += Invoke-IsolatedStage -Name "candidate_build" -Script $Builder `
    -SuccessMarker "PASS_CANDIDATE_BUILD_REQUIRES_FRESH_PROCESS_AUDIT"
$Stages += Invoke-IsolatedStage -Name "fresh_persistence" -Script $Verifier `
    -SuccessMarker "PASS_CANDIDATE_PERSISTED_AWAITING_MAPPED_VIEW_REVIEW"

if (-not (Test-Path -LiteralPath $PersistenceReport -PathType Leaf)) {
    throw "Fresh-process persistence report was not emitted."
}
$Audit = Get-Content -LiteralPath $PersistenceReport -Raw | ConvertFrom-Json
if ($Audit.gate -ne "PASS_CANDIDATE_PERSISTED_AWAITING_MAPPED_VIEW_REVIEW" -or
    $Audit.promotion_allowed -ne $false) {
    throw "Candidate persistence did not return the required non-promotable gate."
}

$Receipt = [ordered]@{
    schema = "skyguard.m01.hero-grouped-topology-unreal-gate.v1"
    gate = "PASS_CANDIDATE_PERSISTED_AWAITING_MAPPED_VIEW_REVIEW"
    completed_at_utc = [DateTime]::UtcNow.ToString("o")
    attempt = $Attempt
    candidate_root = $CandidateRoot
    stages = $Stages
    runtime_map_changed = $false
    config_changed = $false
    promotion_allowed = $false
    p3_4_closed = $false
    next_gate = "original-resolution Unreal versus bound Blender mapped-view comparison"
}
$Receipt | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (
    Join-Path $Attempt "receipt.json"
) -Encoding utf8
$Receipt | ConvertTo-Json -Depth 6
