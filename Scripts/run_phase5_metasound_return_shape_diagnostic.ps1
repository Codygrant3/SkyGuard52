param(
    [string]$UnrealRoot = "D:\UE_5.8",
    [int]$TimeoutSeconds = 180
)

$ErrorActionPreference = "Stop"
$ProjectRoot = "D:\Skyguard52"
$ProjectFile = Join-Path $ProjectRoot "Skyguard52.uproject"
$UnrealCmd = Join-Path (
    Join-Path $UnrealRoot "Engine\Binaries\Win64"
) "UnrealEditor-Cmd.exe"
$Probe = Join-Path (
    Join-Path $ProjectRoot "Scripts"
) "diagnose_phase5_metasound_ue58_return_shapes.py"
$AttemptId = "attempt_{0}_{1}" -f (
    (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssfffZ")
), ([guid]::NewGuid().ToString("N").Substring(0, 8))
$AttemptDirectory = Join-Path (
    Join-Path $ProjectRoot "Saved\Reports\Phase5MetaSoundReturnShape"
) $AttemptId
$Stdout = Join-Path $AttemptDirectory "diagnostic.stdout.log"
$Stderr = Join-Path $AttemptDirectory "diagnostic.stderr.log"
$Report = Join-Path $AttemptDirectory "return_shape.json"

function Get-ActiveUnrealLane {
    @(
        Get-CimInstance Win32_Process | Where-Object {
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
}

$Active = Get-ActiveUnrealLane
if ($Active.Count -gt 0) {
    throw "Shared Unreal lane active; diagnostic duplicate refused"
}
foreach ($Path in @($ProjectFile, $UnrealCmd, $Probe)) {
    if (-not (Test-Path -LiteralPath $Path)) {
        throw "Required path missing: $Path"
    }
}
New-Item -ItemType Directory -Force -Path $AttemptDirectory | Out-Null
$env:SKYGUARD_PHASE5_METASOUND_DIAGNOSTIC_REPORT = $Report
$Arguments = @(
    $ProjectFile,
    "-ExecutePythonScript=$Probe",
    "-unattended", "-nop4", "-nosplash", "-NullRHI", "-stdout",
    "-FullStdOutLogOutput"
)
$Process = Start-Process -FilePath $UnrealCmd -ArgumentList $Arguments `
    -RedirectStandardOutput $Stdout -RedirectStandardError $Stderr `
    -PassThru -WindowStyle Hidden
[ordered]@{
    schema = "skyguard.phase5.metasound-return-shape-process.v1"
    attempt_id = $AttemptId
    pid = $Process.Id
    started_utc = (Get-Date).ToUniversalTime().ToString("o")
    stdout = $Stdout
    stderr = $Stderr
    report = $Report
    transient_only = $true
    production_content_modified = $false
} | ConvertTo-Json | Set-Content (
    Join-Path $AttemptDirectory "process.json"
) -Encoding utf8
$Deadline = (Get-Date).AddSeconds($TimeoutSeconds)
while (-not $Process.HasExited -and (Get-Date) -lt $Deadline) {
    Start-Sleep -Seconds 2
    $Process.Refresh()
}
if (-not $Process.HasExited) {
    throw "Diagnostic PID $($Process.Id) remains active after timeout"
}
$Process.WaitForExit()
$Process.Refresh()
$Text = (
    (Get-Content $Stdout -Raw -ErrorAction SilentlyContinue) + "`n" +
    (Get-Content $Stderr -Raw -ErrorAction SilentlyContinue)
)
$ExitCode = $Process.ExitCode
if ($null -eq $ExitCode -and $Text -match "LogExit:\s+Exiting\.") {
    $ExitCode = 0
}
if (
    $ExitCode -ne 0 -or
    $Text -notmatch "PHASE5_RETURN_SHAPE_PROBE_COMPLETE" -or
    $Text -notmatch "LogExit:\s+Exiting\." -or
    $Text -match (
        "Fatal error|Ensure condition failed|LogPython: Error:|" +
        "Traceback \(most recent call last\)|GPU Crash|DXGI_ERROR"
    )
) {
    throw "Transient return-shape diagnostic failed closed"
}
if (-not (Test-Path -LiteralPath $Report)) {
    throw "Transient return-shape diagnostic report missing"
}
$Evidence = Get-Content $Report -Raw | ConvertFrom-Json
if (
    $Evidence.status -ne "PASS_TRANSIENT_RETURN_SHAPE_CAPTURED" -or
    $Evidence.asset_written -ne $false
) {
    throw "Transient diagnostic evidence violated truth boundary"
}
Start-Sleep -Seconds 1
if ((Get-ActiveUnrealLane).Count -gt 0) {
    throw "Unreal lane still active after diagnostic exit"
}
[ordered]@{
    schema = "skyguard.phase5.metasound-return-shape-status.v1"
    attempt_id = $AttemptId
    state = "PASS_TRANSIENT_DIAGNOSTIC_ONLY"
    report = $Report
    asset_written = $false
    production_content_modified = $false
    unreal_fully_exited = $true
    completed_utc = (Get-Date).ToUniversalTime().ToString("o")
} | ConvertTo-Json | Set-Content (
    Join-Path $AttemptDirectory "status.json"
) -Encoding utf8
Write-Output $AttemptDirectory
