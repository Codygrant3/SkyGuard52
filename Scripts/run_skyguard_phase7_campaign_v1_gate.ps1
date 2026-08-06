$ErrorActionPreference = "Stop"

$ProjectRoot = "D:\Skyguard52"
$ProjectFile = Join-Path $ProjectRoot "Skyguard52.uproject"
$UnrealRoot = "D:\UE_5.8"
$BuildTool = Join-Path $UnrealRoot "Engine\Build\BatchFiles\Build.bat"
$UnrealCmd = Join-Path $UnrealRoot "Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
$BuildScript = Join-Path $ProjectRoot "Scripts\build_skyguard_phase7_campaign_v1.py"
$AuditScript = Join-Path $ProjectRoot "Scripts\verify_skyguard_phase7_campaign_v1.py"
$LogDirectory = Join-Path $ProjectRoot "Saved\Logs"
$ReportDirectory = Join-Path $ProjectRoot "Saved\Reports"

$ActiveUnreal = @(
    Get-CimInstance Win32_Process |
        Where-Object {
            $_.Name -in @(
                "UnrealEditor.exe",
                "UnrealEditor-Cmd.exe",
                "ShaderCompileWorker.exe",
                "UnrealBuildTool.exe",
                "AutomationTool.exe",
                "UbaAgent.exe",
                "UbaServer.exe"
            ) -or (
                $_.Name -eq "dotnet.exe" -and
                $_.CommandLine -match "UnrealBuildTool|AutomationTool"
            )
        }
)
if ($ActiveUnreal.Count -gt 0) {
    $Summary = $ActiveUnreal |
        ForEach-Object { "$($_.Name) PID=$($_.ProcessId)" } |
        Sort-Object
    Write-Error (
        "READY_TO_RUN: Unreal/build lane is active. No process was terminated " +
        "and no duplicate was launched. Active: " + ($Summary -join ", ")
    )
    exit 2
}

New-Item -ItemType Directory -Force -Path $LogDirectory | Out-Null
New-Item -ItemType Directory -Force -Path $ReportDirectory | Out-Null

& $BuildTool Skyguard52Editor Win64 Development $ProjectFile -WaitMutex -NoHotReloadFromIDE
if ($LASTEXITCODE -ne 0) {
    throw "Skyguard52Editor build failed with exit code $LASTEXITCODE"
}

$BuildLog = Join-Path $LogDirectory "Phase7CampaignBuild01.log"
& $UnrealCmd $ProjectFile "-ExecutePythonScript=$BuildScript" -unattended -nop4 -nosplash -NullRHI "-abslog=$BuildLog"
if ($LASTEXITCODE -ne 0) {
    throw "Phase 7 campaign asset build failed with exit code $LASTEXITCODE"
}
$BuildText = Get-Content -LiteralPath $BuildLog -Raw
if (
    $BuildText -match "LogPython: Error:|Python script executed with errors|Traceback \(most recent call last\)"
) {
    throw "Phase 7 builder logged a Python failure despite its process exit code"
}

$StillRunning = @(Get-Process "UnrealEditor-Cmd" -ErrorAction SilentlyContinue)
if ($StillRunning.Count -gt 0) {
    throw "Builder process has not exited; refusing to start persistence verifier"
}

$AuditLog = Join-Path $LogDirectory "Phase7CampaignPersistence01.log"
& $UnrealCmd $ProjectFile "-ExecutePythonScript=$AuditScript" -unattended -nop4 -nosplash -NullRHI "-abslog=$AuditLog"
if ($LASTEXITCODE -ne 0) {
    throw "Phase 7 fresh-process persistence audit failed with exit code $LASTEXITCODE"
}
$AuditText = Get-Content -LiteralPath $AuditLog -Raw
if (
    $AuditText -match "LogPython: Error:|Python script executed with errors|Traceback \(most recent call last\)"
) {
    throw "Phase 7 persistence verifier logged a Python failure despite its process exit code"
}

$AuditReport = Join-Path $ReportDirectory "PHASE7_CAMPAIGN_V1_PERSISTENCE_AUDIT.json"
if (-not (Test-Path -LiteralPath $AuditReport)) {
    throw "Phase 7 persistence audit report was not created"
}
$Audit = Get-Content -LiteralPath $AuditReport -Raw | ConvertFrom-Json
if ($Audit.gate -ne "PASS") {
    throw "Phase 7 persistence report did not pass"
}

$AutomationLog = Join-Path $LogDirectory "Phase7CampaignAutomation01.log"
& $UnrealCmd $ProjectFile `
    "-ExecCmds=Automation RunTests Skyguard52.Campaign" `
    "-TestExit=Automation Test Queue Empty" `
    -unattended -nop4 -nosplash -NullRHI `
    "-abslog=$AutomationLog"
if ($LASTEXITCODE -ne 0) {
    throw "Phase 7 native campaign automation failed with exit code $LASTEXITCODE"
}

$AutomationText = Get-Content -LiteralPath $AutomationLog -Raw
$SuccessCount = (
    [regex]::Matches($AutomationText, "Test Completed\. Result=\{Success\}")
).Count
$FailureCount = (
    [regex]::Matches($AutomationText, "Test Completed\. Result=\{Fail\}")
).Count
$FatalCount = (
    [regex]::Matches(
        $AutomationText,
        "Fatal error|Assertion failed|Ensure condition failed"
    )
).Count
$FoundMatch = [regex]::Match(
    $AutomationText,
    "Found ([0-9]+) automation tests based on 'Skyguard52\.Campaign'"
)
$DiscoveredCount = if ($FoundMatch.Success) {
    [int]$FoundMatch.Groups[1].Value
}
else {
    0
}
$RequiredTests = @(
    "Skyguard52.Campaign.Definition.ValidationRejectsBrokenReferences",
    "Skyguard52.Campaign.Runtime.ObjectivesAndRouteAreDeterministic",
    "Skyguard52.Campaign.Runtime.ScoringUnlocksAndSaveRoundTrip"
)
$MissingRequiredTests = @(
    $RequiredTests |
        Where-Object {
            $AutomationText -notmatch (
                "Test Completed\. Result=\{Success\}.*Path=\{" +
                [regex]::Escape($_) +
                "\}"
            )
        }
)
if (
    $DiscoveredCount -lt 3 -or
    $SuccessCount -ne $DiscoveredCount -or
    $FailureCount -ne 0 -or
    $FatalCount -ne 0 -or
    $MissingRequiredTests.Count -ne 0
) {
    throw (
        "Unexpected campaign automation evidence: discovered=$DiscoveredCount " +
        "success=$SuccessCount fail=$FailureCount fatal=$FatalCount " +
        "missingRequired=$($MissingRequiredTests -join ',')"
    )
}

Write-Output (
    "PASS: Phase 7 generated 10 governed mission definitions plus one campaign, " +
    "passed fresh-process persistence, and passed $SuccessCount/$DiscoveredCount " +
    "native campaign tests. " +
    "Definitions are not completed maps or art."
)
