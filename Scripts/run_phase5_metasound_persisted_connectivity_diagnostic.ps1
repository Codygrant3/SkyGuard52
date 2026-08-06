param(
    [string]$UnrealRoot = "D:\UE_5.8",
    [int]$TimeoutSeconds = 240
)

$ErrorActionPreference = "Stop"
$ProjectRoot = "D:\Skyguard52"
$ProjectFile = Join-Path $ProjectRoot "Skyguard52.uproject"
$UnrealCmd = Join-Path (
    Join-Path $UnrealRoot "Engine\Binaries\Win64"
) "UnrealEditor-Cmd.exe"
$Author = Join-Path (
    Join-Path $ProjectRoot "Scripts"
) "diagnose_phase5_metasound_persisted_connectivity_author.py"
$Fresh = Join-Path (
    Join-Path $ProjectRoot "Scripts"
) "diagnose_phase5_metasound_persisted_connectivity_fresh.py"
$AttemptId = "attempt_{0}_{1}" -f (
    (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssfffZ")
), ([guid]::NewGuid().ToString("N").Substring(0, 8))
$AttemptDirectory = Join-Path (
    Join-Path $ProjectRoot "Saved\Reports\Phase5MetaSoundConnectivity"
) $AttemptId
$TempAssetDirectory = Join-Path (
    Join-Path $ProjectRoot "Content\Skyguard\Diagnostics"
) "Temporary"
$TempAssetPattern = "MS_P5ConnectivityProbe.*"

function Get-ActiveHeavyLane {
    @(
        Get-CimInstance Win32_Process | Where-Object {
            $_.Name -in @(
                "UnrealEditor.exe", "UnrealEditor-Cmd.exe",
                "ShaderCompileWorker.exe", "UnrealBuildTool.exe",
                "AutomationTool.exe", "UbaAgent.exe", "UbaServer.exe",
                "blender.exe"
            ) -or (
                $_.Name -eq "dotnet.exe" -and
                $_.CommandLine -match "UnrealBuildTool|AutomationTool"
            )
        }
    )
}

function Get-TemporaryAssetFiles {
    @(
        Get-ChildItem -LiteralPath $TempAssetDirectory `
            -Filter $TempAssetPattern -File -ErrorAction SilentlyContinue
    )
}

function Quarantine-TemporaryAssetFiles {
    $Files = @(Get-TemporaryAssetFiles)
    if ($Files.Count -eq 0) {
        return
    }
    if ((Get-ActiveHeavyLane).Count -gt 0) {
        throw "Cannot quarantine temporary probe while heavy lane is active"
    }
    $Quarantine = Join-Path $AttemptDirectory "quarantine"
    New-Item -ItemType Directory -Force -Path $Quarantine | Out-Null
    foreach ($File in $Files) {
        Move-Item -LiteralPath $File.FullName -Destination (
            Join-Path $Quarantine $File.Name
        )
    }
}

function Invoke-ProbeProcess {
    param([string]$Label, [string]$Script)
    if ((Get-ActiveHeavyLane).Count -gt 0) {
        throw "Heavy lane active before $Label"
    }
    $Stdout = Join-Path $AttemptDirectory "$Label.stdout.log"
    $Stderr = Join-Path $AttemptDirectory "$Label.stderr.log"
    $Process = Start-Process -FilePath $UnrealCmd -ArgumentList @(
        $ProjectFile,
        "-ExecutePythonScript=$Script",
        "-unattended", "-nop4", "-nosplash", "-NullRHI", "-stdout",
        "-FullStdOutLogOutput"
    ) -RedirectStandardOutput $Stdout -RedirectStandardError $Stderr `
        -PassThru -WindowStyle Hidden
    [ordered]@{
        schema = "skyguard.phase5.metasound-connectivity-process.v1"
        attempt_id = $AttemptId
        label = $Label
        pid = $Process.Id
        script = $Script
        stdout = $Stdout
        stderr = $Stderr
        started_utc = (Get-Date).ToUniversalTime().ToString("o")
    } | ConvertTo-Json | Set-Content (
        Join-Path $AttemptDirectory "$Label.process.json"
    ) -Encoding utf8
    $Deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while (-not $Process.HasExited -and (Get-Date) -lt $Deadline) {
        Start-Sleep -Seconds 2
        $Process.Refresh()
    }
    if (-not $Process.HasExited) {
        throw "$Label remains active after timeout; never duplicate"
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
        $Text -notmatch "LogExit:\s+Exiting\." -or
        $Text -match (
            "Fatal error|Ensure condition failed|LogPython: Error:|" +
            "Traceback \(most recent call last\)|GPU Crash|DXGI_ERROR"
        )
    ) {
        throw "$Label failed closed"
    }
}

foreach ($Path in @($ProjectFile, $UnrealCmd, $Author, $Fresh)) {
    if (-not (Test-Path -LiteralPath $Path)) {
        throw "Required path missing: $Path"
    }
}
if ((Get-ActiveHeavyLane).Count -gt 0) {
    throw "Heavy lane active; diagnostic refused"
}
if ((Get-TemporaryAssetFiles).Count -gt 0) {
    throw "Preexisting temporary connectivity asset refused"
}
New-Item -ItemType Directory -Force -Path $AttemptDirectory | Out-Null
$env:SKYGUARD_PHASE5_CONNECTIVITY_ATTEMPT_DIR = $AttemptDirectory
try {
    Invoke-ProbeProcess "01_author" $Author
    if (-not (Test-Path -LiteralPath (
        Join-Path $AttemptDirectory "author_connectivity.json"
    ))) {
        throw "Connectivity author report missing"
    }
    Invoke-ProbeProcess "02_fresh_and_delete" $Fresh
    $FreshPath = Join-Path $AttemptDirectory "fresh_connectivity.json"
    if (-not (Test-Path -LiteralPath $FreshPath)) {
        throw "Fresh connectivity report missing"
    }
    $Result = Get-Content $FreshPath -Raw | ConvertFrom-Json
    if (
        $Result.status -ne "PASS_FRESH_CONNECTIVITY_CAPTURED" -or
        $Result.temporary_asset_deleted -ne $true -or
        $Result.production_path -ne $false -or
        @($Result.fresh.PSObject.Properties).Count -ne 4
    ) {
        throw "Fresh connectivity evidence incomplete or unsafe"
    }
    if ((Get-TemporaryAssetFiles).Count -gt 0) {
        throw "Temporary connectivity asset remains after fresh probe"
    }
    [ordered]@{
        schema = "skyguard.phase5.metasound-connectivity-status.v1"
        attempt_id = $AttemptId
        state = "PASS_DIAGNOSTIC_ONLY"
        temporary_asset_deleted = $true
        production_content_modified = $false
        unreal_fully_exited = $true
        completed_utc = (Get-Date).ToUniversalTime().ToString("o")
    } | ConvertTo-Json | Set-Content (
        Join-Path $AttemptDirectory "status.json"
    ) -Encoding utf8
    Write-Output $AttemptDirectory
}
catch {
    $QuarantineError = $null
    try {
        Quarantine-TemporaryAssetFiles
    }
    catch {
        $QuarantineError = $_.Exception.Message
    }
    [ordered]@{
        schema = "skyguard.phase5.metasound-connectivity-status.v1"
        attempt_id = $AttemptId
        state = "FAIL_CLOSED"
        detail = $_.Exception.Message
        quarantine_error = $QuarantineError
        production_content_modified = $false
        completed_utc = (Get-Date).ToUniversalTime().ToString("o")
    } | ConvertTo-Json | Set-Content (
        Join-Path $AttemptDirectory "status.json"
    ) -Encoding utf8
    Write-Error $_
    exit 1
}
finally {
    Remove-Item Env:SKYGUARD_PHASE5_CONNECTIVITY_ATTEMPT_DIR `
        -ErrorAction SilentlyContinue
}
