param(
    [string]$UnrealRoot = "D:\UE_5.8",
    [int]$TimeoutSeconds = 900
)

$ErrorActionPreference = "Stop"
$ProjectRoot = "D:\Skyguard52"
$ProjectFile = Join-Path $ProjectRoot "Skyguard52.uproject"
$UnrealCmd = Join-Path $UnrealRoot "Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
$BuildTool = Join-Path $UnrealRoot "Engine\Build\BatchFiles\Build.bat"
$Builder = Join-Path $ProjectRoot "Scripts\build_skyguard_phase5_p5a_audio_routing.py"
$FreshAudit = Join-Path $ProjectRoot "Scripts\verify_skyguard_phase5_p5a_audio_routing.py"
$OfflineAudit = Join-Path $ProjectRoot "Scripts\verify_phase5_p5a_audio_routing_contract.py"
$AcquisitionAudit = Join-Path $ProjectRoot "Scripts\verify_phase5_audio_acquisition_contract.py"
$AttemptRoot = Join-Path $ProjectRoot "Saved\Reports\Phase5P5A"
$AttemptId = "attempt_{0}_{1}" -f (
    (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssfffZ")
), ([guid]::NewGuid().ToString("N").Substring(0, 8))
$AttemptDirectory = Join-Path $AttemptRoot $AttemptId

function Write-Status {
    param([string]$State, [string]$Detail)
    @{
        schema = "skyguard.phase5.p5a-supervisor-status.v1"
        attempt_id = $AttemptId
        state = $State
        detail = $Detail
        production_ready = $false
        identity_sources_missing = 5
        updated_utc = (Get-Date).ToUniversalTime().ToString("o")
    } | ConvertTo-Json -Depth 5 | Set-Content (
        Join-Path $AttemptDirectory "status.json"
    ) -Encoding utf8
}

function Assert-NoActiveUnrealLane {
    $Active = @(
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
    if ($Active.Count -gt 0) {
        $Summary = $Active | ForEach-Object {
            "$($_.Name) PID=$($_.ProcessId)"
        }
        throw "Shared Unreal lane active; no duplicate launched: $($Summary -join ', ')"
    }
}

function Invoke-Supervised {
    param(
        [string]$Label,
        [string]$FilePath,
        [string[]]$Arguments,
        [string]$SuccessPattern = ""
    )
    $Stdout = Join-Path $AttemptDirectory "$Label.stdout.log"
    $Stderr = Join-Path $AttemptDirectory "$Label.stderr.log"
    $Process = Start-Process -FilePath $FilePath -ArgumentList $Arguments `
        -RedirectStandardOutput $Stdout -RedirectStandardError $Stderr `
        -PassThru -WindowStyle Hidden
    @{
        label = $Label
        pid = $Process.Id
        started_utc = (Get-Date).ToUniversalTime().ToString("o")
        stdout = $Stdout
        stderr = $Stderr
    } | ConvertTo-Json | Set-Content (
        Join-Path $AttemptDirectory "$Label.process.json"
    ) -Encoding utf8
    $Deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while (-not $Process.HasExited -and (Get-Date) -lt $Deadline) {
        Start-Sleep -Seconds 2
        $Process.Refresh()
    }
    if (-not $Process.HasExited) {
        Write-Status "ACTIVE_PROCESS_TIMEOUT" (
            "$Label PID $($Process.Id) remains authoritative; wait, never duplicate."
        )
        throw "$Label exceeded $TimeoutSeconds seconds; process was not terminated"
    }
    $Process.WaitForExit()
    $Process.Refresh()
    $ExitCode = $Process.ExitCode
    $Text = (
        (Get-Content $Stdout -Raw -ErrorAction SilentlyContinue) + "`n" +
        (Get-Content $Stderr -Raw -ErrorAction SilentlyContinue)
    )
    if ($null -eq $ExitCode -and $SuccessPattern -and $Text -match $SuccessPattern) {
        $ExitCode = 0
    }
    if ($null -eq $ExitCode) {
        throw "$Label completed without a readable exit code or accepted success marker"
    }
    if ($ExitCode -ne 0) {
        throw "$Label failed with exit code $ExitCode"
    }
    if ($Text -match "Fatal error|Ensure condition failed|LogPython: Error:|Traceback \(most recent call last\)") {
        throw "$Label emitted a fatal, ensure, or Python error marker"
    }
}

New-Item -ItemType Directory -Force -Path $AttemptDirectory | Out-Null
Write-Status "PRECHECK" "Fail-closed routing-only attempt created."
$env:SKYGUARD_P5A_ATTEMPT_DIR = $AttemptDirectory
try {
    foreach ($Path in @(
        $ProjectFile, $UnrealCmd, $BuildTool, $Builder, $FreshAudit,
        $OfflineAudit, $AcquisitionAudit
    )) {
        if (-not (Test-Path -LiteralPath $Path)) {
            throw "Required path missing: $Path"
        }
    }
    Assert-NoActiveUnrealLane

    & python $OfflineAudit
    if ($LASTEXITCODE -ne 0) {
        throw "Offline P5-A contract preflight failed"
    }
    $AcquisitionPreflightText = & python $AcquisitionAudit
    $AcquisitionPreflightText | Set-Content (
        Join-Path $AttemptDirectory "acquisition_preflight.json"
    ) -Encoding utf8
    $AcquisitionPreflight = $AcquisitionPreflightText | ConvertFrom-Json
    if ($AcquisitionPreflight.contract_valid -ne $true) {
        throw "Phase 5 acquisition contract preflight is invalid"
    }

    Write-Status "BUILDING_EDITOR" "Compiling the exact editor target."
    Invoke-Supervised "01_editor_build" $BuildTool @(
        "Skyguard52Editor",
        "Win64",
        "Development",
        $ProjectFile,
        "-WaitMutex",
        "-NoHotReloadFromIDE"
    ) "Result:\s+Succeeded"
    Assert-NoActiveUnrealLane

    Write-Status "BUILDING_ROUTING" "Creating or reusing seven governed assets."
    Invoke-Supervised "02_routing_builder" $UnrealCmd @(
        $ProjectFile, "-ExecutePythonScript=$Builder",
        "-unattended", "-nop4", "-nosplash", "-NullRHI", "-stdout",
        "-FullStdOutLogOutput"
    ) "LogExit:\s+Exiting\."
    Assert-NoActiveUnrealLane
    $BuildReceipt = Join-Path $AttemptDirectory "build_receipt.json"
    if (-not (Test-Path $BuildReceipt)) {
        throw "Builder did not produce its attempt receipt"
    }

    Write-Status "FRESH_AUDIT" "Opening a new Unreal process for persistence audit."
    Invoke-Supervised "03_fresh_audit" $UnrealCmd @(
        $ProjectFile, "-ExecutePythonScript=$FreshAudit",
        "-unattended", "-nop4", "-nosplash", "-NullRHI", "-stdout",
        "-FullStdOutLogOutput"
    ) "LogExit:\s+Exiting\."
    Assert-NoActiveUnrealLane
    $FreshReceipt = Join-Path $AttemptDirectory "fresh_audit.json"
    if (-not (Test-Path $FreshReceipt)) {
        throw "Fresh verifier did not produce its attempt receipt"
    }
    $Fresh = Get-Content $FreshReceipt -Raw | ConvertFrom-Json
    if (
        $Fresh.status -ne "P5A_ROUTING_FRESH_AUDIT_PASS_SOURCES_MISSING" -or
        $Fresh.routing_asset_count -ne 7 -or
        $Fresh.identity_missing_source_count -ne 5 -or
        $Fresh.production_ready -ne $false
    ) {
        throw "Fresh audit did not prove seven routes and five missing identity sources"
    }

    & python $OfflineAudit --receipt $BuildReceipt --require-built
    if ($LASTEXITCODE -ne 0) {
        throw "Offline post-build receipt audit failed"
    }
    $AcquisitionPostText = & python $AcquisitionAudit
    $AcquisitionPostText | Set-Content (
        Join-Path $AttemptDirectory "acquisition_postbuild.json"
    ) -Encoding utf8
    $AcquisitionPost = $AcquisitionPostText | ConvertFrom-Json
    if ($AcquisitionPost.contract_valid -ne $true) {
        throw "Post-build acquisition contract is invalid"
    }
    Write-Status "PASS_ROUTING_ONLY" (
        "Seven routing assets fresh-audited; five identity sources remain missing."
    )
    Write-Output "P5A_ROUTING_GATE=PASS_ROUTING_ONLY"
    Write-Output "ATTEMPT_DIRECTORY=$AttemptDirectory"
}
catch {
    if ((Get-Content (Join-Path $AttemptDirectory "status.json") -Raw) -notmatch "ACTIVE_PROCESS_TIMEOUT") {
        Write-Status "FAIL_CLOSED" $_.Exception.Message
    }
    Write-Error $_
    exit 1
}
finally {
    Remove-Item Env:SKYGUARD_P5A_ATTEMPT_DIR -ErrorAction SilentlyContinue
}
