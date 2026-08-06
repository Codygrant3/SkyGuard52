param(
    [string]$UnrealRoot = "D:\UE_5.8",
    [int]$TimeoutSeconds = 900
)

$ErrorActionPreference = "Stop"
$ProjectRoot = "D:\Skyguard52"
$ProjectFile = Join-Path $ProjectRoot "Skyguard52.uproject"
$UnrealCmd = Join-Path $UnrealRoot "Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
$Contract = Join-Path $ProjectRoot "Docs\AAA_Review\PHASE5_METASOUND_TOPOLOGY_CONTRACT.json"
$ContractAudit = Join-Path $ProjectRoot "Scripts\verify_phase5_metasound_topology_contract.py"
$Builder = Join-Path $ProjectRoot "Scripts\build_skyguard_phase5_metasound_topology.py"
$FreshAudit = Join-Path $ProjectRoot "Scripts\verify_skyguard_phase5_metasound_topology.py"
$StaticTests = Join-Path $ProjectRoot "Scripts\test_phase5_metasound_topology_authoring.py"
$RuntimeAudit = Join-Path $ProjectRoot "Scripts\verify_phase5_audio_runtime_routing_readiness.py"
$ShippingAudit = Join-Path $ProjectRoot "Scripts\verify_phase5_audio_shipping_boundary.py"
$AttemptRoot = Join-Path $ProjectRoot "Saved\Reports\Phase5MetaSoundTopology"
$AttemptId = "attempt_{0}_{1}" -f (
    (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssfffZ")
), ([guid]::NewGuid().ToString("N").Substring(0, 8))
$AttemptDirectory = Join-Path $AttemptRoot $AttemptId
$ExpectedBundleSha256 = (
    "296f1ce6cfff00b949d8ae8e83461eedf73f56321dc34c0d27a9fbb4cc9afcfd"
)
$GraphNames = @(
    "MS_Yak52IdentityBed", "MS_RifleShot", "MS_IglaWeapon",
    "MS_DronePropulsion", "MS_ExplosionSmall", "MS_ExplosionHeavy"
)
$GraphAssetDirectory = Join-Path (
    Join-Path $ProjectRoot "Content\Skyguard\Audio\Production"
) "MetaSounds"
$RollbackDirectory = Join-Path $AttemptDirectory "preexisting_graph_backup"
$PreexistingGraphFiles = @{}

function Write-Status {
    param([string]$State, [string]$Detail)
    [ordered]@{
        schema = "skyguard.phase5.metasound-topology-supervisor.v1"
        attempt_id = $AttemptId
        state = $State
        detail = $Detail
        graph_count = 6
        primitive_count = 29
        authentic_source_count = 0
        expected_missing_source_count = 25
        production_ready = $false
        shipping_allowed = $false
        updated_utc = (Get-Date).ToUniversalTime().ToString("o")
    } | ConvertTo-Json -Depth 8 | Set-Content (
        Join-Path $AttemptDirectory "status.json"
    ) -Encoding utf8
}

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

function Assert-NoActiveUnrealLane {
    $Active = @(Get-ActiveUnrealLane)
    if ($Active.Count -gt 0) {
        $Summary = $Active | ForEach-Object {
            "$($_.Name) PID=$($_.ProcessId)"
        }
        throw "Shared Unreal lane active; duplicate refused: $($Summary -join ', ')"
    }
}

function Save-GraphRollbackState {
    New-Item -ItemType Directory -Force -Path $RollbackDirectory | Out-Null
    foreach ($Name in $GraphNames) {
        $Matches = @(
            Get-ChildItem -LiteralPath $GraphAssetDirectory `
                -Filter "$Name.*" -File -ErrorAction SilentlyContinue
        )
        $PreexistingGraphFiles[$Name] = @(
            $Matches | ForEach-Object { $_.Name }
        )
        foreach ($File in $Matches) {
            Copy-Item -LiteralPath $File.FullName -Destination (
                Join-Path $RollbackDirectory $File.Name
            )
        }
    }
    $PreexistingGraphFiles | ConvertTo-Json -Depth 5 | Set-Content (
        Join-Path $AttemptDirectory "preexisting_graph_files.json"
    ) -Encoding utf8
}

function Restore-GraphRollbackState {
    if ((Get-ActiveUnrealLane).Count -gt 0) {
        throw "Cannot restore graph rollback state while Unreal lane is active"
    }
    foreach ($Name in $GraphNames) {
        $Current = @(
            Get-ChildItem -LiteralPath $GraphAssetDirectory `
                -Filter "$Name.*" -File -ErrorAction SilentlyContinue
        )
        foreach ($File in $Current) {
            Remove-Item -LiteralPath $File.FullName -Force
        }
        foreach ($FileName in @($PreexistingGraphFiles[$Name])) {
            Copy-Item -LiteralPath (
                Join-Path $RollbackDirectory $FileName
            ) -Destination (
                Join-Path $GraphAssetDirectory $FileName
            ) -Force
        }
    }
    [ordered]@{
        schema = "skyguard.phase5.metasound-topology-rollback.v1"
        restored = $true
        partial_promotion_retained = $false
        completed_utc = (Get-Date).ToUniversalTime().ToString("o")
    } | ConvertTo-Json | Set-Content (
        Join-Path $AttemptDirectory "rollback.json"
    ) -Encoding utf8
}

function Invoke-SupervisedUnreal {
    param(
        [string]$Label,
        [string]$PythonScript
    )
    $Stdout = Join-Path $AttemptDirectory "$Label.stdout.log"
    $Stderr = Join-Path $AttemptDirectory "$Label.stderr.log"
    $Arguments = @(
        $ProjectFile,
        "-ExecutePythonScript=$PythonScript",
        "-unattended", "-nop4", "-nosplash", "-NullRHI", "-stdout",
        "-FullStdOutLogOutput"
    )
    $Process = Start-Process -FilePath $UnrealCmd -ArgumentList $Arguments `
        -RedirectStandardOutput $Stdout -RedirectStandardError $Stderr `
        -PassThru -WindowStyle Hidden
    [ordered]@{
        label = $Label
        pid = $Process.Id
        started_utc = (Get-Date).ToUniversalTime().ToString("o")
        stdout = $Stdout
        stderr = $Stderr
        python_script = $PythonScript
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
    if ($null -eq $ExitCode -and $Text -match "LogExit:\s+Exiting\.") {
        $ExitCode = 0
    }
    if ($null -eq $ExitCode) {
        throw "$Label completed without readable exit code or exit marker"
    }
    if ($ExitCode -ne 0) {
        throw "$Label failed with exit code $ExitCode"
    }
    if ($Text -notmatch "LogExit:\s+Exiting\.") {
        throw "$Label missed clean Unreal exit marker"
    }
    if ($Text -match (
        "Fatal error|Ensure condition failed|LogPython: Error:|" +
        "Traceback \(most recent call last\)|GPU Crash|DXGI_ERROR"
    )) {
        throw "$Label emitted a fatal, ensure, Python, or GPU failure marker"
    }
}

New-Item -ItemType Directory -Force -Path $AttemptDirectory | Out-Null
Write-Status "PRECHECK" "MetaSound topology attempt created."
$env:SKYGUARD_PHASE5_METASOUND_ATTEMPT_DIR = $AttemptDirectory
try {
    foreach ($Path in @(
        $ProjectFile, $UnrealCmd, $Contract, $ContractAudit, $Builder,
        $FreshAudit, $StaticTests, $RuntimeAudit, $ShippingAudit
    )) {
        if (-not (Test-Path -LiteralPath $Path)) {
            throw "Required path missing: $Path"
        }
    }
    Assert-NoActiveUnrealLane
    & python -m py_compile $ContractAudit $Builder $FreshAudit $StaticTests
    if ($LASTEXITCODE -ne 0) {
        throw "Python compile preflight failed"
    }
    & python -m unittest $StaticTests | Set-Content (
        Join-Path $AttemptDirectory "static_tests.log"
    ) -Encoding utf8
    if ($LASTEXITCODE -ne 0) {
        throw "MetaSound topology static tests failed"
    }
    & python $ContractAudit --output (
        Join-Path $AttemptDirectory "contract_audit.json"
    ) | Set-Content (
        Join-Path $AttemptDirectory "contract_audit.stdout.log"
    ) -Encoding utf8
    if ($LASTEXITCODE -ne 0) {
        throw "MetaSound topology contract audit failed"
    }
    $ContractReport = Get-Content (
        Join-Path $AttemptDirectory "contract_audit.json"
    ) -Raw | ConvertFrom-Json
    if (
        $ContractReport.status -ne (
            "PASS_GOVERNED_SILENT_UNTIL_SOURCED_TOPOLOGY_CONTRACT"
        ) -or
        $ContractReport.graph_count -ne 6 -or
        $ContractReport.category_count -ne 25 -or
        $ContractReport.wave_asset_input_count -ne 25 -or
        $ContractReport.authentic_source_count -ne 0 -or
        $ContractReport.production_ready -ne $false -or
        $ContractReport.shipping_allowed -ne $false -or
        $ContractReport.contract_bundle.bundle_sha256 -ne (
            $ExpectedBundleSha256
        )
    ) {
        throw "Offline contract report does not prove exact safe topology"
    }

    Write-Status "AUTHORING" (
        "Serializing six connected silent-until-sourced MetaSound graphs."
    )
    Save-GraphRollbackState
    Invoke-SupervisedUnreal "01_topology_builder" $Builder
    Assert-NoActiveUnrealLane
    $BuildReceipt = Join-Path $AttemptDirectory "build_topology_manifest.json"
    if (-not (Test-Path -LiteralPath $BuildReceipt)) {
        throw "MetaSound topology build manifest missing"
    }
    $Build = Get-Content $BuildReceipt -Raw | ConvertFrom-Json
    if (
        $Build.status -ne (
            "BUILT_SILENT_GOVERNED_TOPOLOGY_REQUIRES_FRESH_AUDIT"
        ) -or
        $Build.graph_count -ne 6 -or
        $Build.primitive_count -ne 29 -or
        $Build.governed_asset_count -ne 35 -or
        $Build.authentic_source_count -ne 0 -or
        $Build.metasound_soundwave_binding_count -ne 0 -or
        $Build.procedural_generator_count -ne 0 -or
        $Build.production_bank.explicit_missing_source_count -ne 25 -or
        $Build.production_bank.bound_production_source_count -ne 0 -or
        $Build.production_ready -ne $false -or
        $Build.shipping_allowed -ne $false -or
        $Build.contract_bundle.bundle_sha256 -ne $ExpectedBundleSha256 -or
        @($Build.serialized_asset_sha256.PSObject.Properties).Count -ne 35
    ) {
        throw "Build manifest crossed the Phase 5 truth boundary"
    }

    Write-Status "FRESH_SERIALIZED_AUDIT" (
        "Reopening all six graphs and 29 primitive hashes independently."
    )
    Invoke-SupervisedUnreal "02_fresh_topology_audit" $FreshAudit
    Assert-NoActiveUnrealLane
    $FreshPath = Join-Path $AttemptDirectory "fresh_topology_audit.json"
    if (-not (Test-Path -LiteralPath $FreshPath)) {
        throw "Fresh MetaSound topology audit receipt missing"
    }
    $Fresh = Get-Content $FreshPath -Raw | ConvertFrom-Json
    if (
        $Fresh.status -ne (
            "PASS_FRESH_GOVERNED_METASOUND_TOPOLOGY_SOURCES_MISSING"
        ) -or
        $Fresh.graph_count -ne 6 -or
        $Fresh.primitive_count -ne 29 -or
        $Fresh.governed_asset_count -ne 35 -or
        $Fresh.authentic_source_count -ne 0 -or
        $Fresh.metasound_soundwave_binding_count -ne 0 -or
        $Fresh.procedural_generator_count -ne 0 -or
        $Fresh.fresh_for_current_contract -ne $true -or
        $Fresh.production_bank.explicit_missing_source_count -ne 25 -or
        $Fresh.production_bank.bound_production_source_count -ne 0 -or
        $Fresh.production_ready -ne $false -or
        $Fresh.shipping_allowed -ne $false -or
        $Fresh.contract_bundle.bundle_sha256 -ne $ExpectedBundleSha256 -or
        @($Fresh.serialized_asset_sha256.PSObject.Properties).Count -ne 35 -or
        @($Fresh.errors).Count -ne 0
    ) {
        throw "Fresh audit did not prove exact governed topology state"
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
        $Runtime.assets.metasounds.present_count -ne 6 -or
        $Runtime.assets.attenuation.present_count -ne 15 -or
        $Runtime.assets.concurrency.present_count -ne 14 -or
        $Runtime.serialized_unreal_audit.fresh_for_current_contract -ne $true -or
        $Runtime.runtime_routing_ready -ne $false
    ) {
        throw "Runtime readiness does not recognize fresh topology safely"
    }

    $ShippingText = & python $ShippingAudit
    $ShippingCode = $LASTEXITCODE
    $ShippingText | Set-Content (
        Join-Path $AttemptDirectory "shipping_boundary.json"
    ) -Encoding utf8
    if ($ShippingCode -ne 3) {
        throw "Shipping boundary must remain fail-closed with exit 3"
    }

    Write-Status "PASS_TOPOLOGY_ONLY_SOURCES_MISSING" (
        "Six graphs and 29 primitives are hash-bound and freshly audited; " +
        "25 authentic sources and audible acceptance remain blocked."
    )
    Write-Output (
        "PHASE5_METASOUND_TOPOLOGY_GATE=" +
        "PASS_TOPOLOGY_ONLY_SOURCES_MISSING"
    )
    Write-Output "ATTEMPT_DIRECTORY=$AttemptDirectory"
}
catch {
    $RollbackError = $null
    if (Test-Path -LiteralPath (
        Join-Path $AttemptDirectory "preexisting_graph_files.json"
    )) {
        try {
            Restore-GraphRollbackState
        }
        catch {
            $RollbackError = $_.Exception.Message
        }
    }
    $StatusText = Get-Content (
        Join-Path $AttemptDirectory "status.json"
    ) -Raw -ErrorAction SilentlyContinue
    if ($StatusText -notmatch "ACTIVE_PROCESS_TIMEOUT") {
        $Detail = $_.Exception.Message
        if ($RollbackError) {
            $Detail += "; rollback error: $RollbackError"
        }
        Write-Status "FAIL_CLOSED" $Detail
    }
    Write-Error $_
    exit 1
}
finally {
    Remove-Item Env:SKYGUARD_PHASE5_METASOUND_ATTEMPT_DIR `
        -ErrorAction SilentlyContinue
}
