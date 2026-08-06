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
$builder = Join-Path $ProjectRoot "Scripts\build_skyguard_m02_playable_integration.py"
$verifier = Join-Path $ProjectRoot "Scripts\verify_skyguard_m02_playable_integration.py"
$reports = Join-Path $ProjectRoot "Saved\Reports"
$stamp = [DateTime]::UtcNow.ToString("yyyyMMddTHHmmssfffZ")
$attempt = Join-Path $reports "M02_Playable\attempt_$stamp"
New-Item -ItemType Directory -Force -Path $attempt, $reports | Out-Null

foreach ($required in @($project, $buildTool, $unrealCmd, $builder, $verifier)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
        throw "Required M02 playable input is missing: $required"
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
    throw "Shared Unreal lane is active; no duplicate launched: $($summary -join ', ')"
}

function ConvertTo-Argument {
    param([Parameter(Mandatory = $true)][string]$Value)
    if ($Value -notmatch '[\s"]') { return $Value }
    return '"' + ($Value -replace '(\\*)"', '$1$1\"' -replace '(\\+)$', '$1$1') + '"'
}

function Stop-ExactProcessTree {
    param([Parameter(Mandatory = $true)][int]$RootProcessId)
    $all = @(Get-CimInstance Win32_Process | Select-Object ProcessId, ParentProcessId)
    $descendants = [System.Collections.Generic.List[int]]::new()
    $queue = [System.Collections.Generic.Queue[int]]::new()
    $queue.Enqueue($RootProcessId)
    while ($queue.Count -gt 0) {
        $parentId = $queue.Dequeue()
        foreach ($candidate in $all) {
            if ([int]$candidate.ParentProcessId -eq $parentId) {
                $childId = [int]$candidate.ProcessId
                $descendants.Add($childId)
                $queue.Enqueue($childId)
            }
        }
    }
    $orderedDescendants = @($descendants)
    [array]::Reverse($orderedDescendants)
    foreach ($child in $orderedDescendants) {
        Stop-Process -Id $child -Force -ErrorAction SilentlyContinue
    }
    Stop-Process -Id $RootProcessId -Force -ErrorAction SilentlyContinue
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
    $failureMarkers = @(
        @(
            "Fatal error", "Assertion failed", "Ensure condition failed",
            "Unhandled Exception", "LogPython: Error:",
            "Python script executed with errors", "Traceback (most recent call last)"
        ) | Where-Object { $text -match [regex]::Escape($_) }
    )
    $observedExitCode = $null
    try { $observedExitCode = [int]$process.ExitCode } catch { $observedExitCode = $null }
    $nonZeroExit = $null -ne $observedExitCode -and $observedExitCode -ne 0
    $semanticSuccess = switch ($Name) {
        "build" {
            $text -match "Result: Succeeded|Target is up to date"
            break
        }
        "compose" {
            $text -match "\[SkyguardM02PlayableBuild\]"
            break
        }
        "fresh_audit" {
            $text -match "\[SkyguardM02PlayableAudit\]"
            break
        }
        "automation" {
            $text -match "Automation Test Queue Empty"
            break
        }
        default { $true }
    }
    if ($nonZeroExit -or $failureMarkers.Count -gt 0 -or -not $semanticSuccess) {
        throw "$Name failed: exit=$observedExitCode; semantic_success=$semanticSuccess; markers=$($failureMarkers -join ', ')"
    }
    return [ordered]@{
        name = $Name
        exit_code = $observedExitCode
        process_exit_observed = [bool]$process.HasExited
        semantic_success = [bool]$semanticSuccess
        stdout = $stdout
        stderr = $stderr
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
$stages += Invoke-GovernedStage -Name "automation" -FilePath $unrealCmd -Arguments @(
    $project,
    "-ExecCmds=Automation RunTests Skyguard52.Mission02",
    "-TestExit=Automation Test Queue Empty",
    "-unattended", "-nop4", "-nosplash", "-NullRHI",
    "-stdout", "-FullStdOutLogOutput"
)

$automationLog = Join-Path $attempt "automation.stdout.log"
$automationText = Get-Content -LiteralPath $automationLog -Raw
$found = [regex]::Match(
    $automationText,
    "Found ([0-9]+) automation tests based on 'Skyguard52\.Mission02'"
)
$discovered = if ($found.Success) { [int]$found.Groups[1].Value } else { 0 }
$success = ([regex]::Matches(
    $automationText, "Test Completed\. Result=\{Success\}"
)).Count
$failure = ([regex]::Matches(
    $automationText, "Test Completed\. Result=\{Fail\}"
)).Count
$requiredTests = @(
    "Skyguard52.Mission02.Breakwater.SequenceIglaAndBoundedDestruction",
    "Skyguard52.Mission02.Integration.GovernedContractAndWaveProgression",
    "Skyguard52.Mission02.Integration.PlayableCompositionIglaAndObjectives",
    "Skyguard52.Mission02.Integration.EmergencyRifleOnlyAndTerminalFailure"
)
$missing = @(
    $requiredTests |
        Where-Object {
            $automationText -notmatch (
                "Test Completed\. Result=\{Success\}.*Path=\{" +
                [regex]::Escape($_) + "\}"
            )
        }
)
$audit = Get-Content -LiteralPath (
    Join-Path $reports "M02_PLAYABLE_INTEGRATION_AUDIT.json"
) -Raw | ConvertFrom-Json
$gate = if (
    $audit.gate -eq "PASS" -and
    $discovered -eq 4 -and $success -eq 4 -and
    $failure -eq 0 -and $missing.Count -eq 0
) { "PASS" } else { "FAIL" }

$receipt = [ordered]@{
    schema = "skyguard.m02-playable-supervisor.v1"
    gate = $gate
    generated_at_utc = [DateTime]::UtcNow.ToString("o")
    attempt = $attempt
    stages = $stages
    automation = [ordered]@{
        discovered = $discovered
        success = $success
        failure = $failure
        required = $requiredTests
        missing = $missing
    }
    persistence_audit = $audit
    packaging_performed = $false
}
$json = $receipt | ConvertTo-Json -Depth 12
$json | Set-Content -LiteralPath (
    Join-Path $attempt "gate_receipt.json"
) -Encoding utf8
$json | Set-Content -LiteralPath (
    Join-Path $reports "M02_PLAYABLE_INTEGRATION_GATE_LATEST.json"
) -Encoding utf8
if ($gate -ne "PASS") {
    throw "Mission 2 playable integration gate failed"
}
Write-Output "M02_PLAYABLE_INTEGRATION_GATE=PASS"
