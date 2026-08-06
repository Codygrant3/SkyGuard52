$ErrorActionPreference = "Stop"

$ProjectRoot = "D:\Skyguard52"
$ProjectFile = Join-Path $ProjectRoot "Skyguard52.uproject"
$UnrealRoot = "D:\UE_5.8"
$BuildTool = Join-Path $UnrealRoot "Engine\Build\BatchFiles\Build.bat"
$UnrealCmd = Join-Path $UnrealRoot "Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
$BuildScript = Join-Path $ProjectRoot "Scripts\build_skyguard_phase7_wave2_mission_maps.py"
$AuditScript = Join-Path $ProjectRoot "Scripts\verify_skyguard_phase7_wave2_mission_maps.py"
$LogDirectory = Join-Path $ProjectRoot "Saved\Logs"
$ReportDirectory = Join-Path $ProjectRoot "Saved\Reports"

$ActiveLane = @(
    Get-CimInstance Win32_Process |
        Where-Object {
            $_.Name -in @(
                "UnrealEditor.exe", "UnrealEditor-Cmd.exe",
                "ShaderCompileWorker.exe", "UnrealBuildTool.exe",
                "AutomationTool.exe", "UbaAgent.exe", "UbaServer.exe"
            ) -or (
                $_.Name -eq "dotnet.exe" -and
                $_.CommandLine -match "UnrealBuildTool|AutomationTool"
            )
        }
)
if ($ActiveLane.Count -gt 0) {
    $Summary = $ActiveLane |
        ForEach-Object { "$($_.Name) PID=$($_.ProcessId)" } |
        Sort-Object
    Write-Error (
        "READY_TO_RUN: shared Unreal lane is active. No process was terminated " +
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

function Invoke-PythonGate {
    param([string]$Script, [string]$Log, [string]$Label)
    & $UnrealCmd $ProjectFile "-ExecutePythonScript=$Script" `
        -unattended -nop4 -nosplash -NullRHI "-abslog=$Log"
    if ($LASTEXITCODE -ne 0) {
        throw "$Label process failed with exit code $LASTEXITCODE"
    }
    $Text = Get-Content -LiteralPath $Log -Raw
    if (
        $Text -match "LogPython: Error:|Python script executed with errors|Traceback \(most recent call last\)"
    ) {
        throw "$Label logged a Python failure despite its process exit code"
    }
}

$BuildLog = Join-Path $LogDirectory "Phase7Wave2MissionMapBuild01.log"
Invoke-PythonGate -Script $BuildScript -Log $BuildLog -Label "Wave 2 map builder"
if (@(Get-Process "UnrealEditor-Cmd" -ErrorAction SilentlyContinue).Count -gt 0) {
    throw "Builder process has not exited; refusing to launch fresh verifier"
}

$AuditLog = Join-Path $LogDirectory "Phase7Wave2MissionMapPersistence01.log"
Invoke-PythonGate -Script $AuditScript -Log $AuditLog -Label "Wave 2 map verifier"

$AuditReport = Join-Path $ReportDirectory "PHASE7_WAVE2_MISSION_MAP_PERSISTENCE_AUDIT.json"
if (-not (Test-Path -LiteralPath $AuditReport)) {
    throw "Wave 2 map persistence report was not created"
}
$Audit = Get-Content -LiteralPath $AuditReport -Raw | ConvertFrom-Json
if ($Audit.gate -ne "PASS") {
    throw "Wave 2 map persistence report did not pass"
}

$AutomationLog = Join-Path $LogDirectory "Phase7Wave2MissionMapAutomation01.log"
& $UnrealCmd $ProjectFile `
    "-ExecCmds=Automation RunTests Skyguard52.CampaignMaps.Assembly" `
    "-TestExit=Automation Test Queue Empty" `
    -unattended -nop4 -nosplash -NullRHI "-abslog=$AutomationLog"
if ($LASTEXITCODE -ne 0) {
    throw "Wave 2 native automation failed with exit code $LASTEXITCODE"
}
$Text = Get-Content -LiteralPath $AutomationLog -Raw
$Found = [regex]::Match(
    $Text,
    "Found ([0-9]+) automation tests based on 'Skyguard52\.CampaignMaps\.Assembly'"
)
$Discovered = if ($Found.Success) { [int]$Found.Groups[1].Value } else { 0 }
$Success = ([regex]::Matches($Text, "Test Completed\. Result=\{Success\}")).Count
$Failure = ([regex]::Matches($Text, "Test Completed\. Result=\{Fail\}")).Count
$Fatal = (
    [regex]::Matches($Text, "Fatal error|Assertion failed|Ensure condition failed")
).Count
if ($Discovered -lt 1 -or $Success -ne $Discovered -or $Failure -ne 0 -or $Fatal -ne 0) {
    throw (
        "Unexpected native evidence: discovered=$Discovered success=$Success " +
        "fail=$Failure fatal=$Fatal"
    )
}

Write-Output (
    "PASS: M05-M07 distinct campaign assembly maps persisted and native " +
    "integrity automation passed. Proxy-art limitation remains."
)
