[CmdletBinding()]
param(
    [string]$ProjectRoot = "D:\Skyguard52",
    [string]$UnrealRoot = "D:\UE_5.8",
    [ValidateRange(60, 1800)]
    [int]$StageTimeoutSeconds = 600
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$project = Join-Path $ProjectRoot "Skyguard52.uproject"
$buildTool = Join-Path $UnrealRoot "Engine\Build\BatchFiles\Build.bat"
$unrealCmd = Join-Path $UnrealRoot "Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
$builder = Join-Path $ProjectRoot "Scripts\build_skyguard_phase7_wave3_mission_maps.py"
$verifier = Join-Path $ProjectRoot "Scripts\verify_skyguard_phase7_wave3_mission_maps.py"
$reports = Join-Path $ProjectRoot "Saved\Reports"
$attempt = Join-Path $reports (
    "Phase7_Wave3\attempt_" +
    [DateTime]::UtcNow.ToString("yyyyMMddTHHmmssfffZ")
)
New-Item -ItemType Directory -Force -Path $attempt, $reports | Out-Null

foreach ($required in @($project, $buildTool, $unrealCmd, $builder, $verifier)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
        throw "Required Wave 3 input is missing: $required"
    }
}

$active = @(
    Get-CimInstance Win32_Process |
        Where-Object {
            $_.Name -in @(
                "UnrealEditor.exe", "UnrealEditor-Cmd.exe",
                "UnrealBuildTool.exe", "AutomationTool.exe",
                "ShaderCompileWorker.exe", "UbaAgent.exe", "UbaServer.exe"
            ) -or (
                $_.Name -eq "dotnet.exe" -and
                $_.CommandLine -match "UnrealBuildTool|AutomationTool"
            )
        }
)
if ($active.Count -gt 0) {
    $summary = $active |
        ForEach-Object { "$($_.Name) PID=$($_.ProcessId)" } |
        Sort-Object
    throw "Shared Unreal lane active; no duplicate launched: $($summary -join ', ')"
}

function ConvertTo-Argument {
    param([Parameter(Mandatory = $true)][string]$Value)
    if ($Value -notmatch '[\s"]') { return $Value }
    return '"' + ($Value -replace '(\\*)"', '$1$1\"' -replace '(\\+)$', '$1$1') + '"'
}

function Get-DescendantProcessIds {
    param([Parameter(Mandatory = $true)][int]$RootProcessId)
    $all = @(Get-CimInstance Win32_Process | Select-Object ProcessId, ParentProcessId)
    $result = [System.Collections.Generic.List[int]]::new()
    $queue = [System.Collections.Generic.Queue[int]]::new()
    $queue.Enqueue($RootProcessId)
    while ($queue.Count -gt 0) {
        $parent = $queue.Dequeue()
        foreach ($candidate in $all) {
            if ([int]$candidate.ParentProcessId -eq $parent) {
                $child = [int]$candidate.ProcessId
                $result.Add($child)
                $queue.Enqueue($child)
            }
        }
    }
    return @($result)
}

function Stop-ExactProcessTree {
    param([Parameter(Mandatory = $true)][int]$RootProcessId)
    $children = @(Get-DescendantProcessIds -RootProcessId $RootProcessId)
    [array]::Reverse($children)
    foreach ($child in $children) {
        Stop-Process -Id $child -Force -ErrorAction SilentlyContinue
    }
    Stop-Process -Id $RootProcessId -Force -ErrorAction SilentlyContinue
}

function Get-Sha256Hex {
    param([Parameter(Mandatory = $true)][string]$LiteralPath)
    $stream = [System.IO.File]::OpenRead($LiteralPath)
    try {
        $sha = [System.Security.Cryptography.SHA256]::Create()
        try {
            return ([System.BitConverter]::ToString(
                $sha.ComputeHash($stream)
            )).Replace("-", "").ToLowerInvariant()
        }
        finally { $sha.Dispose() }
    }
    finally { $stream.Dispose() }
}

function Invoke-GovernedStage {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$FilePath,
        [Parameter(Mandatory = $true)][string[]]$Arguments
    )
    $stdout = Join-Path $attempt "$Name.stdout.log"
    $stderr = Join-Path $attempt "$Name.stderr.log"
    $argumentLine = ($Arguments | ForEach-Object { ConvertTo-Argument $_ }) -join " "
    $process = Start-Process -FilePath $FilePath -ArgumentList $argumentLine `
        -RedirectStandardOutput $stdout -RedirectStandardError $stderr `
        -PassThru -WindowStyle Hidden
    $deadline = (Get-Date).AddSeconds($StageTimeoutSeconds)
    while (-not $process.HasExited -and (Get-Date) -lt $deadline) {
        Start-Sleep -Seconds 2
        $process.Refresh()
    }
    if (-not $process.HasExited) {
        Stop-ExactProcessTree -RootProcessId $process.Id
        throw "$Name exceeded $StageTimeoutSeconds seconds"
    }
    $process.WaitForExit()
    $process.Refresh()
    $text = (Get-Content -LiteralPath $stdout -Raw -ErrorAction SilentlyContinue) +
        (Get-Content -LiteralPath $stderr -Raw -ErrorAction SilentlyContinue)
    $markers = @(
        @(
            "Fatal error", "Assertion failed", "Ensure condition failed",
            "Unhandled Exception", "LogPython: Error:",
            "Python script executed with errors", "Traceback (most recent call last)"
        ) | Where-Object { $text -match [regex]::Escape($_) }
    )
    $observedExitCode = $null
    try { $observedExitCode = [int]$process.ExitCode } catch { $observedExitCode = $null }
    $nonZeroExit = $null -ne $observedExitCode -and $observedExitCode -ne 0
    if ($nonZeroExit -or $markers.Count -gt 0) {
        throw "$Name failed: exit=$observedExitCode; markers=$($markers -join ', ')"
    }
    return [ordered]@{
        name = $Name
        exit_code = $observedExitCode
        stdout = $stdout
        stderr = $stderr
        stdout_sha256 = Get-Sha256Hex -LiteralPath $stdout
        stderr_sha256 = Get-Sha256Hex -LiteralPath $stderr
    }
}

$stages = @()
$stages += Invoke-GovernedStage -Name "build" -FilePath $buildTool -Arguments @(
    "Skyguard52Editor", "Win64", "Development", $project,
    "-WaitMutex", "-NoHotReloadFromIDE"
)
$stages += Invoke-GovernedStage -Name "compose" -FilePath $unrealCmd -Arguments @(
    $project, "-run=pythonscript", "-script=$builder",
    "-unattended", "-nop4", "-nosplash", "-NullRHI",
    "-stdout", "-FullStdOutLogOutput"
)
$stages += Invoke-GovernedStage -Name "fresh_audit" -FilePath $unrealCmd -Arguments @(
    $project, "-run=pythonscript", "-script=$verifier",
    "-unattended", "-nop4", "-nosplash", "-NullRHI",
    "-stdout", "-FullStdOutLogOutput"
)
$stages += Invoke-GovernedStage -Name "native_automation" -FilePath $unrealCmd -Arguments @(
    $project,
    "-ExecCmds=Automation RunTests Skyguard52.CampaignMaps.Assembly",
    "-TestExit=Automation Test Queue Empty",
    "-unattended", "-nop4", "-nosplash", "-NullRHI",
    "-stdout", "-FullStdOutLogOutput"
)

$auditPath = Join-Path $reports "PHASE7_WAVE3_MISSION_MAP_PERSISTENCE_AUDIT.json"
$audit = Get-Content -LiteralPath $auditPath -Raw | ConvertFrom-Json
$automationText = Get-Content -LiteralPath (
    Join-Path $attempt "native_automation.stdout.log"
) -Raw
$found = [regex]::Match(
    $automationText,
    "Found ([0-9]+) automation tests based on 'Skyguard52\.CampaignMaps\.Assembly'"
)
$discovered = if ($found.Success) { [int]$found.Groups[1].Value } else { 0 }
$success = ([regex]::Matches(
    $automationText, "Test Completed\. Result=\{Success\}"
)).Count
$failure = ([regex]::Matches(
    $automationText, "Test Completed\. Result=\{Fail\}"
)).Count
$fatal = ([regex]::Matches(
    $automationText, "Fatal error|Assertion failed|Ensure condition failed"
)).Count
$gate = if (
    $audit.gate -eq "PASS" -and $discovered -ge 1 -and
    $success -eq $discovered -and $failure -eq 0 -and $fatal -eq 0
) { "PASS" } else { "FAIL" }

$receipt = [ordered]@{
    schema = "skyguard.phase7.wave3-map-gate.v1"
    gate = $gate
    generated_at_utc = [DateTime]::UtcNow.ToString("o")
    attempt = $attempt
    stages = $stages
    automation = [ordered]@{
        discovered = $discovered
        success = $success
        failure = $failure
        fatal_markers = $fatal
    }
    audit = $audit
    packaged = $false
}
$json = $receipt | ConvertTo-Json -Depth 15
$json | Set-Content -LiteralPath (Join-Path $attempt "gate_receipt.json") -Encoding utf8
$json | Set-Content -LiteralPath (
    Join-Path $reports "PHASE7_WAVE3_MISSION_MAP_GATE_LATEST.json"
) -Encoding utf8
if ($gate -ne "PASS") {
    throw "Phase 7 Wave 3 map gate failed"
}
Write-Output "PHASE7_WAVE3_MISSION_MAP_GATE=PASS"
