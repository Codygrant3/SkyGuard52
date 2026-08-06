param(
    [string]$UnrealRoot = "D:\UE_5.8",
    [int]$TimeoutSeconds = 900
)

$ErrorActionPreference = "Stop"
$ProjectRoot = "D:\Skyguard52"
$ProjectFile = Join-Path $ProjectRoot "Skyguard52.uproject"
$UnrealCmd = Join-Path $UnrealRoot "Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
$BuildTool = Join-Path $UnrealRoot "Engine\Build\BatchFiles\Build.bat"
$Builder = Join-Path $ProjectRoot "Scripts\build_skyguard_phase5_routing_primitives.py"
$FreshAudit = Join-Path $ProjectRoot "Scripts\verify_skyguard_phase5_routing_primitives.py"
$RuntimeAudit = Join-Path $ProjectRoot "Scripts\verify_phase5_audio_runtime_routing_readiness.py"
$OfflineGate = Join-Path $ProjectRoot "Scripts\run_phase5_audio_offline_readiness_gate.ps1"
$ShippingAudit = Join-Path $ProjectRoot "Scripts\verify_phase5_audio_shipping_boundary.py"
$StaticTests = Join-Path $ProjectRoot "Scripts\test_phase5_routing_primitive_authoring.py"
$AttemptRoot = Join-Path $ProjectRoot "Saved\Reports\Phase5RoutingPrimitives"
$AttemptId = "attempt_{0}_{1}" -f (
    (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssfffZ")
), ([guid]::NewGuid().ToString("N").Substring(0, 8))
$AttemptDirectory = Join-Path $AttemptRoot $AttemptId

function Write-Status {
    param([string]$State, [string]$Detail)
    [ordered]@{
        schema = "skyguard.phase5.routing-primitives-supervisor.v1"
        attempt_id = $AttemptId
        state = $State
        detail = $Detail
        attenuation_asset_count = 15
        concurrency_asset_count = 14
        metasound_shell_count = 0
        authentic_source_count = 0
        production_ready = $false
        updated_utc = (Get-Date).ToUniversalTime().ToString("o")
    } | ConvertTo-Json -Depth 6 | Set-Content (
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
        throw "Shared Unreal lane active; duplicate refused: $($Summary -join ', ')"
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
    [ordered]@{
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
        throw "$Label exceeded $TimeoutSeconds seconds; process not terminated"
    }
    $Process.WaitForExit()
    $Process.Refresh()
    $Text = (
        (Get-Content $Stdout -Raw -ErrorAction SilentlyContinue) + "`n" +
        (Get-Content $Stderr -Raw -ErrorAction SilentlyContinue)
    )
    $ExitCode = $Process.ExitCode
    if ($null -eq $ExitCode -and $SuccessPattern -and $Text -match $SuccessPattern) {
        $ExitCode = 0
    }
    if ($null -eq $ExitCode) {
        throw "$Label completed without a readable exit code or accepted success marker"
    }
    if ($ExitCode -ne 0) {
        throw "$Label failed with exit code $ExitCode"
    }
    if ($SuccessPattern -and $Text -notmatch $SuccessPattern) {
        throw "$Label missed success marker: $SuccessPattern"
    }
    if ($Text -match "Fatal error|Ensure condition failed|LogPython: Error:|Traceback \(most recent call last\)|Result=\{Fail\}") {
        throw "$Label emitted a fatal, ensure, Python, or test failure marker"
    }
}

New-Item -ItemType Directory -Force -Path $AttemptDirectory | Out-Null
Write-Status "PRECHECK" "Routing-only authoring attempt created."
$env:SKYGUARD_PHASE5_PRIMITIVES_ATTEMPT_DIR = $AttemptDirectory
try {
    foreach ($Path in @(
        $ProjectFile, $UnrealCmd, $BuildTool, $Builder, $FreshAudit,
        $RuntimeAudit, $OfflineGate, $ShippingAudit, $StaticTests
    )) {
        if (-not (Test-Path -LiteralPath $Path)) {
            throw "Required path missing: $Path"
        }
    }
    Assert-NoActiveUnrealLane
    & python -m py_compile $Builder $FreshAudit $StaticTests
    if ($LASTEXITCODE -ne 0) {
        throw "Python compile preflight failed"
    }
    & python -m unittest $StaticTests
    if ($LASTEXITCODE -ne 0) {
        throw "Routing primitive static tests failed"
    }

    Write-Status "BUILDING_EDITOR" "Compiling current native audio source."
    Invoke-Supervised "01_editor_build" $BuildTool @(
        "Skyguard52Editor", "Win64", "Development", $ProjectFile,
        "-WaitMutex", "-NoHotReloadFromIDE"
    ) "Result:\s+Succeeded"
    Assert-NoActiveUnrealLane

    Write-Status "AUTHORING_PRIMITIVES" "Serializing 15 ATT and 14 CON assets."
    Invoke-Supervised "02_primitive_builder" $UnrealCmd @(
        $ProjectFile, "-ExecutePythonScript=$Builder",
        "-unattended", "-nop4", "-nosplash", "-NullRHI", "-stdout",
        "-FullStdOutLogOutput"
    ) "LogExit:\s+Exiting\."
    Assert-NoActiveUnrealLane
    if (-not (Test-Path (Join-Path $AttemptDirectory "build_receipt.json"))) {
        throw "Routing primitive builder receipt missing"
    }

    Write-Status "FRESH_SERIALIZED_AUDIT" "Reopening assets in an independent process."
    Invoke-Supervised "03_fresh_audit" $UnrealCmd @(
        $ProjectFile, "-ExecutePythonScript=$FreshAudit",
        "-unattended", "-nop4", "-nosplash", "-NullRHI", "-stdout",
        "-FullStdOutLogOutput"
    ) "LogExit:\s+Exiting\."
    Assert-NoActiveUnrealLane
    $FreshPath = Join-Path $AttemptDirectory "fresh_audit.json"
    if (-not (Test-Path $FreshPath)) {
        throw "Fresh serialized audit receipt missing"
    }
    $Fresh = Get-Content $FreshPath -Raw | ConvertFrom-Json
    if (
        $Fresh.status -ne "PASS_ROUTING_PRIMITIVES_SOURCES_AND_METASOUNDS_MISSING" -or
        $Fresh.attenuation_asset_count -ne 15 -or
        $Fresh.concurrency_asset_count -ne 14 -or
        $Fresh.bank_routing_binding_count -ne 25 -or
        $Fresh.explicit_missing_source_count -ne 25 -or
        $Fresh.metasound_shell_count -ne 0 -or
        $Fresh.production_ready -ne $false
    ) {
        throw "Fresh audit did not prove exact routing-only state"
    }

    Write-Status "NATIVE_AUDIO_TESTS" "Running five focused native tests under NullRHI."
    Invoke-Supervised "04_native_audio_tests" $UnrealCmd @(
        $ProjectFile,
        "-ExecCmds=`"Automation RunTests Skyguard52.Audio`"",
        "-TestExit=`"Automation Test Queue Empty`"",
        "-unattended", "-nop4", "-nosplash", "-NullRHI", "-stdout",
        "-FullStdOutLogOutput"
    ) "Automation Test Queue Empty 5 tests performed"
    Assert-NoActiveUnrealLane

    & powershell -NoProfile -ExecutionPolicy Bypass -File $OfflineGate | Set-Content (
        Join-Path $AttemptDirectory "offline_gate.log"
    ) -Encoding utf8
    if ($LASTEXITCODE -ne 0) {
        throw "Phase 5 offline gate failed after authoring"
    }
    $RuntimeText = & python $RuntimeAudit
    $RuntimeCode = $LASTEXITCODE
    $RuntimeText | Set-Content (
        Join-Path $AttemptDirectory "runtime_readiness.json"
    ) -Encoding utf8
    if ($RuntimeCode -ne 0) {
        throw "Runtime routing structural audit failed"
    }
    $Runtime = $RuntimeText | ConvertFrom-Json
    if (
        $Runtime.structural_contract_valid -ne $true -or
        $Runtime.assets.attenuation.present_count -ne 15 -or
        $Runtime.assets.concurrency.present_count -ne 14 -or
        $Runtime.assets.metasounds.present_count -ne 0 -or
        $Runtime.runtime_routing_ready -ne $false
    ) {
        throw "Offline runtime report does not match serialized routing-only state"
    }
    $ShippingText = & python $ShippingAudit
    $ShippingCode = $LASTEXITCODE
    $ShippingText | Set-Content (
        Join-Path $AttemptDirectory "shipping_boundary.json"
    ) -Encoding utf8
    if ($ShippingCode -ne 3) {
        throw "Shipping boundary must remain blocked with exit 3"
    }

    Write-Status "PASS_ROUTING_PRIMITIVES_ONLY" (
        "15 attenuation and 14 concurrency assets serialized and fresh-audited; sources and MetaSounds remain missing."
    )
    Write-Output "PHASE5_ROUTING_PRIMITIVES_GATE=PASS_ROUTING_PRIMITIVES_ONLY"
    Write-Output "ATTEMPT_DIRECTORY=$AttemptDirectory"
}
catch {
    $StatusText = Get-Content (
        Join-Path $AttemptDirectory "status.json"
    ) -Raw -ErrorAction SilentlyContinue
    if ($StatusText -notmatch "ACTIVE_PROCESS_TIMEOUT") {
        Write-Status "FAIL_CLOSED" $_.Exception.Message
    }
    Write-Error $_
    exit 1
}
finally {
    Remove-Item Env:SKYGUARD_PHASE5_PRIMITIVES_ATTEMPT_DIR `
        -ErrorAction SilentlyContinue
}
