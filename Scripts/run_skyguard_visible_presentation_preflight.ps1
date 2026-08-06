[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$PackageAttemptRoot,
    [string]$ProjectRoot = "D:\Skyguard52",
    [ValidateRange(100, 1000)]
    [int]$ModuleSampleMilliseconds = 250
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$reportSchema = "skyguard.visible-presentation-preflight.report.v1"
$entryMap = "/Engine/Maps/Entry"
$m01Map = "/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_Playable_v1"
$smokeSeconds = 10
$stageTimeoutSeconds = 35
$resolutionX = 1280
$resolutionY = 720
$verifier = Join-Path $ProjectRoot "Scripts\verify_skyguard_visible_presentation_preflight.py"
$schemaPath = Join-Path $ProjectRoot "Scripts\skyguard_visible_presentation_preflight_report_v1.schema.json"

function Get-PortableSha256 {
    param([Parameter(Mandatory = $true)][string]$LiteralPath)
    $algorithm = [System.Security.Cryptography.SHA256]::Create()
    try {
        $stream = [System.IO.File]::OpenRead($LiteralPath)
        try {
            return ([System.BitConverter]::ToString(
                $algorithm.ComputeHash($stream))).Replace("-", "").ToLowerInvariant()
        }
        finally {
            $stream.Dispose()
        }
    }
    finally {
        $algorithm.Dispose()
    }
}

function New-FileRecord {
    param(
        [Parameter(Mandatory = $true)][string]$Label,
        [Parameter(Mandatory = $true)][string]$LiteralPath
    )
    $item = Get-Item -LiteralPath $LiteralPath -ErrorAction Stop
    if ($item.PSIsContainer) {
        throw "Bound artifact is a directory: $LiteralPath"
    }
    return [ordered]@{
        label = $Label
        path = $item.FullName
        bytes = [int64]$item.Length
        sha256 = Get-PortableSha256 -LiteralPath $item.FullName
    }
}

function New-OptionalFileRecord {
    param([Parameter(Mandatory = $true)][string]$LiteralPath)
    if (-not (Test-Path -LiteralPath $LiteralPath -PathType Leaf)) {
        return [ordered]@{
            path = $LiteralPath
            exists = $false
            bytes = $null
            sha256 = $null
        }
    }
    $item = Get-Item -LiteralPath $LiteralPath
    return [ordered]@{
        path = $item.FullName
        exists = $true
        bytes = [int64]$item.Length
        sha256 = Get-PortableSha256 -LiteralPath $item.FullName
    }
}

function ConvertTo-Argument {
    param([Parameter(Mandatory = $true)][string]$Value)
    if ($Value -notmatch '[\s"]') { return $Value }
    return '"' + ($Value -replace '(\\*)"', '$1$1\"' -replace '(\\+)$', '$1$1') + '"'
}

function Get-DriverEvidence {
    $result = [ordered]@{
        query_complete = $false
        query_error = $null
        selected_adapter = $null
        adapters = @()
    }
    try {
        $adapters = @(
            Get-CimInstance -ClassName Win32_VideoController -ErrorAction Stop |
                ForEach-Object {
                    [ordered]@{
                        name = [string]$_.Name
                        pnp_device_id = [string]$_.PNPDeviceID
                        driver_version = [string]$_.DriverVersion
                        driver_date = if ($_.DriverDate) {
                            ([DateTime]$_.DriverDate).ToUniversalTime().ToString("o")
                        } else { $null }
                        adapter_ram_bytes = if ($null -ne $_.AdapterRAM) {
                            [uint64]$_.AdapterRAM
                        } else { $null }
                        status = [string]$_.Status
                        video_processor = [string]$_.VideoProcessor
                    }
                }
        )
        $result.adapters = $adapters
        $result.selected_adapter = @(
            $adapters | Where-Object { $_.name -match '(?i)nvidia' }
        ) | Select-Object -First 1
        if ($null -eq $result.selected_adapter -and $adapters.Count -gt 0) {
            $result.selected_adapter = $adapters[0]
        }
        $result.query_complete = $true
    }
    catch {
        $result.query_error = $_.Exception.Message
    }
    return $result
}

function Get-FirewallEvidence {
    param([Parameter(Mandatory = $true)][string]$Program)

    $result = [ordered]@{
        operation = "READ_ONLY_INSPECTION"
        mutation_attempted = $false
        target_program = $Program
        queried_at_utc = [DateTime]::UtcNow.ToString("o")
        query_complete = $false
        query_error = $null
        action_summary = "QUERY_FAILED"
        rules = @()
    }
    try {
        if (-not (Get-Command Get-NetFirewallApplicationFilter -ErrorAction SilentlyContinue)) {
            throw "Get-NetFirewallApplicationFilter is unavailable."
        }
        $filters = @(
            Get-NetFirewallApplicationFilter -PolicyStore ActiveStore -ErrorAction Stop |
                Where-Object {
                    [string]::Equals(
                        [string]$_.Program,
                        $Program,
                        [System.StringComparison]::OrdinalIgnoreCase
                    )
                }
        )
        $rulesByName = @{}
        foreach ($filter in $filters) {
            $associatedRules = @(
                Get-NetFirewallRule `
                    -AssociatedNetFirewallApplicationFilter $filter `
                    -ErrorAction Stop
            )
            foreach ($rule in $associatedRules) {
                if ($rulesByName.ContainsKey([string]$rule.Name)) { continue }
                $rulesByName[[string]$rule.Name] = [ordered]@{
                    name = [string]$rule.Name
                    display_name = [string]$rule.DisplayName
                    enabled = ([string]$rule.Enabled -eq "True")
                    direction = [string]$rule.Direction
                    action = [string]$rule.Action
                    profile = [string]$rule.Profile
                    policy_store_source = [string]$rule.PolicyStoreSource
                    policy_store_source_type = [string]$rule.PolicyStoreSourceType
                    program = [string]$filter.Program
                }
            }
        }
        $result.rules = @($rulesByName.Values | Sort-Object name)
        $enabledActions = @(
            $result.rules |
                Where-Object { $_.enabled } |
                ForEach-Object { ([string]$_.action).ToUpperInvariant() } |
                Select-Object -Unique
        )
        if ($enabledActions.Count -eq 0) {
            $result.action_summary = "NO_ENABLED_RULES"
        }
        elseif ($enabledActions.Count -gt 1) {
            $result.action_summary = "MIXED"
        }
        elseif ($enabledActions[0] -eq "ALLOW") {
            $result.action_summary = "ALLOW"
        }
        else {
            $result.action_summary = "BLOCK"
        }
        $result.query_complete = $true
    }
    catch {
        $result.query_error = $_.Exception.Message
    }
    return $result
}

function Get-OverlayModuleSample {
    param([Parameter(Mandatory = $true)][int]$ProcessId)

    # Do not name this variable `$matches`: PowerShell's case-insensitive
    # automatic `$Matches` hash is overwritten by every `-match` expression.
    $overlayMatches = @()
    $moduleCount = 0
    try {
        $process = Get-Process -Id $ProcessId -ErrorAction Stop
        $modules = @($process.Modules)
        $moduleCount = $modules.Count
        foreach ($module in $modules) {
            $identity = "$($module.ModuleName)|$($module.FileName)"
            if (
                $identity -match
                '(?i)(nvspcap|gamebarpresencewriter|gameoverlayrenderer|discordhook|rtsshooks|graphics-hook|obs-|overwolf|reshade|specialk|amdihk)'
            ) {
                $overlayMatches += [pscustomobject][ordered]@{
                    module_name = [string]$module.ModuleName
                    path = [string]$module.FileName
                    file_version = [string]$module.FileVersionInfo.FileVersion
                    product_name = [string]$module.FileVersionInfo.ProductName
                }
            }
        }
        return [ordered]@{
            success = $true
            error = $null
            module_count = $moduleCount
            overlay_modules = $overlayMatches
        }
    }
    catch {
        return [ordered]@{
            success = $false
            error = $_.Exception.Message
            module_count = $moduleCount
            overlay_modules = @()
        }
    }
}

function Get-LogSignatureEvidence {
    param([Parameter(Mandatory = $true)][string[]]$Paths)

    $gpuTimeoutCount = 0
    $criticalCount = 0
    # Keep this separate from PowerShell's automatic `$Matches` hash.
    $signatureMatches = @()
    foreach ($path in $Paths) {
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { continue }
        $reader = $null
        $lastOpenError = $null
        for ($openAttempt = 1; $openAttempt -le 10; $openAttempt++) {
            try {
                $stream = [System.IO.FileStream]::new(
                    $path,
                    [System.IO.FileMode]::Open,
                    [System.IO.FileAccess]::Read,
                    [System.IO.FileShare]::ReadWrite
                )
                $reader = [System.IO.StreamReader]::new($stream)
                break
            }
            catch [System.IO.IOException] {
                $lastOpenError = $_.Exception
                Start-Sleep -Milliseconds 100
            }
            catch [System.UnauthorizedAccessException] {
                $lastOpenError = $_.Exception
                Start-Sleep -Milliseconds 100
            }
        }
        if ($null -eq $reader) {
            throw "Unable to read supervised log '$path' after 10 attempts: $($lastOpenError.Message)"
        }
        try {
            $lineNumber = 0
            while ($null -ne ($line = $reader.ReadLine())) {
                $lineNumber++
                $isGpuTimeout = $line -match '(?i)GPU timeout:'
                $isCritical = $line -match (
                    '(?i)(GPU timeout:|DXGI_ERROR_DEVICE_(HUNG|REMOVED)|' +
                    'GPU Crashed or D3D Device Removed|Fatal error:)'
                )
                if ($isGpuTimeout) { $gpuTimeoutCount++ }
                if ($isCritical) { $criticalCount++ }
                if (
                    ($isGpuTimeout -or $isCritical) -and
                    $signatureMatches.Count -lt 100
                ) {
                    $signatureMatches += [pscustomobject][ordered]@{
                        path = $path
                        line = $lineNumber
                        text = $line
                    }
                }
            }
        }
        finally {
            $reader.Dispose()
        }
    }
    return [ordered]@{
        gpu_timeout_count = $gpuTimeoutCount
        critical_signature_count = $criticalCount
        captured_match_limit = 100
        matches = @($signatureMatches)
    }
}

function Read-SmokeReceipt {
    param(
        [Parameter(Mandatory = $true)][string]$LiteralPath,
        [Parameter(Mandatory = $true)][string]$ExpectedMap
    )
    $record = New-OptionalFileRecord -LiteralPath $LiteralPath
    $record.schema = $null
    $record.state = $null
    $record.map = $null
    $record.rhi = $null
    $record.parse_error = $null
    if ($record.exists) {
        try {
            $receipt = Get-Content -LiteralPath $LiteralPath -Raw |
                ConvertFrom-Json -ErrorAction Stop
            $record.schema = [string]$receipt.schema
            $record.state = [string]$receipt.state
            $record.map = [string]$receipt.map
            $record.rhi = [string]$receipt.rhi
        }
        catch {
            $record.parse_error = $_.Exception.Message
        }
    }
    return $record
}

function New-NotRunStage {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$Map,
        [Parameter(Mandatory = $true)]
        [ValidateSet("FAILED", "SKIPPED_ENTRY_FAILED")]
        [string]$Status,
        [Parameter(Mandatory = $true)][string]$Reason
    )
    return [ordered]@{
        name = $Name
        map = $Map
        status = $Status
        visible = $true
        rhi = "D3D12"
        feature_level = "SM6"
        resolution = [ordered]@{ x = $resolutionX; y = $resolutionY }
        smoke_seconds = $smokeSeconds
        supervisor_seconds = $stageTimeoutSeconds
        pid = $null
        command_line = $null
        started_at_utc = $null
        finished_at_utc = $null
        elapsed_seconds = 0.0
        timed_out = $false
        natural_exit = $false
        exit_code = $null
        receipt = [ordered]@{
            path = $null
            exists = $false
            bytes = $null
            sha256 = $null
            schema = $null
            state = $null
            map = $null
            rhi = $null
            parse_error = $Reason
        }
        logs = [ordered]@{ stdout = $null; stderr = $null }
        signatures = [ordered]@{
            gpu_timeout_count = 0
            critical_signature_count = 0
            captured_match_limit = 100
            matches = @()
        }
        module_scan = [ordered]@{
            query_complete = $false
            samples = 0
            errors = @($Reason)
            overlay_modules = @()
        }
        cleanup = [ordered]@{
            needed = $false
            attempted = $false
            command = $null
            exit_code = $null
            post_cleanup_process_exists = $false
            success = $true
        }
    }
}

$packageAttempt = (Resolve-Path -LiteralPath $PackageAttemptRoot).Path
$packageRoot = Join-Path $packageAttempt "packages\Development\Windows"
$launcher = Join-Path $packageRoot "Skyguard52.exe"
$runtime = Join-Path $packageRoot "Skyguard52\Binaries\Win64\Skyguard52.exe"
foreach ($required in @($launcher, $runtime, $verifier, $schemaPath)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
        throw "Required visible-presentation preflight file is missing: $required"
    }
}

$busy = @(
    Get-Process -ErrorAction SilentlyContinue |
        Where-Object {
            $_.ProcessName -match
            '^(UnrealEditor|UnrealEditor-Cmd|ShaderCompileWorker|Skyguard52|UnrealBuildTool|AutomationTool)$'
        }
)
if ($busy.Count -gt 0) {
    throw "Unreal/Skyguard lane is occupied: $($busy.ProcessName -join ', ')"
}

$stamp = [DateTime]::UtcNow.ToString("yyyyMMddTHHmmssfffZ")
$attemptRoot = Join-Path $ProjectRoot (
    "Saved\BuildAttempts\VISIBLE_PRESENTATION_PREFLIGHT\attempt_$stamp"
)
$logsRoot = Join-Path $attemptRoot "logs"
$receiptsRoot = Join-Path $attemptRoot "receipts"
New-Item -ItemType Directory -Force -Path $attemptRoot, $logsRoot, $receiptsRoot |
    Out-Null
$reportPath = Join-Path $attemptRoot "presentation_preflight_report.json"
$verificationPath = Join-Path $attemptRoot "presentation_preflight_verification.json"

$report = [ordered]@{
    schema = $reportSchema
    attempt_id = "attempt_$stamp"
    generated_at_utc = [DateTime]::UtcNow.ToString("o")
    terminal_state = "RUNNING"
    failure = $null
    package_attempt_root = $packageAttempt
    configuration = [ordered]@{
        visible = $true
        rhi = "D3D12"
        feature_level = "SM6"
        resolution = [ordered]@{ x = $resolutionX; y = $resolutionY }
        smoke_seconds = $smokeSeconds
        stage_timeout_seconds = $stageTimeoutSeconds
        module_sample_milliseconds = $ModuleSampleMilliseconds
    }
    bindings = @(
        New-FileRecord -Label "package_launcher" -LiteralPath $launcher
        New-FileRecord -Label "package_runtime" -LiteralPath $runtime
    )
    driver = Get-DriverEvidence
    firewall = Get-FirewallEvidence -Program $runtime
    stages = @()
}
$report | ConvertTo-Json -Depth 20 |
    Set-Content -LiteralPath $reportPath -Encoding utf8

function Invoke-VisibleStage {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$Map
    )

    $stdout = Join-Path $logsRoot "$Name.stdout.log"
    $stderr = Join-Path $logsRoot "$Name.stderr.log"
    $receiptPath = Join-Path $receiptsRoot "$Name.receipt.json"
    $arguments = @(
        $Map,
        "-windowed",
        "-ResX=$resolutionX",
        "-ResY=$resolutionY",
        "-d3d12",
        "-sm6",
        "-NoVSync",
        "-SkyguardStartupSmokeSeconds=$smokeSeconds",
        "-SkyguardStartupSmokeReceipt=$receiptPath",
        "-nosplash",
        "-stdout",
        "-FullStdOutLogOutput"
    )
    $argumentLine = ($arguments | ForEach-Object { ConvertTo-Argument $_ }) -join " "
    $started = [DateTime]::UtcNow
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    # Launch the bound inner runtime directly so the supervised PID is the game
    # process, not the small bootstrap executable that may create a child.
    $process = Start-Process -FilePath $runtime -ArgumentList $argumentLine `
        -WorkingDirectory $packageRoot -WindowStyle Normal -PassThru `
        -RedirectStandardOutput $stdout -RedirectStandardError $stderr
    $overlayModules = @{}
    $moduleErrors = @()
    $moduleSamples = 0
    $timedOut = $false
    $cleanupNeeded = $false
    $cleanupAttempted = $false
    $cleanupCommand = $null
    $cleanupExitCode = $null
    $monitorFailure = $null
    $naturalExit = $false

    try {
        while (-not $process.HasExited) {
            if ($stopwatch.Elapsed.TotalSeconds -ge $stageTimeoutSeconds) {
                $timedOut = $true
                $cleanupNeeded = $true
                break
            }
            $sample = Get-OverlayModuleSample -ProcessId $process.Id
            $moduleSamples++
            if (-not $sample.success) {
                $process.Refresh()
                if (-not $process.HasExited) {
                    $moduleErrors += [string]$sample.error
                }
            }
            foreach ($module in $sample.overlay_modules) {
                $key = "$($module.module_name)|$($module.path)".ToLowerInvariant()
                $overlayModules[$key] = $module
            }
            Start-Sleep -Milliseconds $ModuleSampleMilliseconds
            $process.Refresh()
        }
    }
    catch {
        $monitorFailure = $_.Exception.Message
        $moduleErrors += "Monitor failure: $monitorFailure"
    }
    finally {
        try { $process.Refresh() } catch { }
        $naturalExit = (
            $process.HasExited -and
            -not $timedOut -and
            $null -eq $monitorFailure
        )
        if (-not $process.HasExited) {
            $cleanupNeeded = $true
            $cleanupAttempted = $true
            $cleanupCommand = "taskkill.exe /PID $($process.Id) /T /F"
            & taskkill.exe /PID $process.Id /T /F | Out-Null
            $cleanupExitCode = $LASTEXITCODE
            [void]$process.WaitForExit(5000)
            $process.Refresh()
        }
        if ($process.HasExited) {
            try {
                # Start-Process owns asynchronous redirection streams. The
                # parameterless overload waits for their final flush after the
                # OS process has exited, preventing a successful stage from
                # racing the subsequent log scan.
                $process.WaitForExit()
            }
            catch {
                $moduleErrors += "Process stream flush failure: $($_.Exception.Message)"
            }
        }
        $stopwatch.Stop()
    }

    $processStillExists = $null -ne (
        Get-Process -Id $process.Id -ErrorAction SilentlyContinue
    )
    $exitCode = $null
    if ($process.HasExited) {
        try { $exitCode = [int]$process.ExitCode } catch { $exitCode = $null }
    }
    $cleanupSuccess = -not $processStillExists
    $receipt = Read-SmokeReceipt -LiteralPath $receiptPath -ExpectedMap $Map
    $signatures = Get-LogSignatureEvidence -Paths @($stdout, $stderr)
    $stdoutRecord = New-OptionalFileRecord -LiteralPath $stdout
    $stderrRecord = New-OptionalFileRecord -LiteralPath $stderr
    $expectedReceiptMap = if ($Map -eq $entryMap) {
        "Entry"
    } else {
        $Map.Substring($Map.LastIndexOf("/") + 1)
    }
    $stagePass = (
        -not $timedOut -and
        $naturalExit -and
        $exitCode -eq 0 -and
        $receipt.exists -and
        $receipt.schema -eq "skyguard.shipping-startup-smoke.v1" -and
        $receipt.state -eq "COMPLETE" -and
        $receipt.map -eq $expectedReceiptMap -and
        $signatures.gpu_timeout_count -eq 0 -and
        $signatures.critical_signature_count -eq 0 -and
        $moduleErrors.Count -eq 0 -and
        $overlayModules.Count -eq 0 -and
        $cleanupSuccess
    )
    return [ordered]@{
        name = $Name
        map = $Map
        status = if ($stagePass) { "COMPLETE" } else { "FAILED" }
        visible = $true
        rhi = "D3D12"
        feature_level = "SM6"
        resolution = [ordered]@{ x = $resolutionX; y = $resolutionY }
        smoke_seconds = $smokeSeconds
        supervisor_seconds = $stageTimeoutSeconds
        pid = [int]$process.Id
        command_line = "$runtime $argumentLine"
        started_at_utc = $started.ToString("o")
        finished_at_utc = [DateTime]::UtcNow.ToString("o")
        elapsed_seconds = [Math]::Round($stopwatch.Elapsed.TotalSeconds, 3)
        timed_out = $timedOut
        natural_exit = $naturalExit
        exit_code = $exitCode
        receipt = $receipt
        logs = [ordered]@{
            stdout = $stdoutRecord
            stderr = $stderrRecord
        }
        signatures = $signatures
        module_scan = [ordered]@{
            query_complete = $moduleErrors.Count -eq 0
            samples = $moduleSamples
            errors = @($moduleErrors)
            overlay_modules = @($overlayModules.Values)
        }
        cleanup = [ordered]@{
            needed = $cleanupNeeded
            attempted = $cleanupAttempted
            command = $cleanupCommand
            exit_code = $cleanupExitCode
            post_cleanup_process_exists = $processStillExists
            success = $cleanupSuccess
        }
    }
}

try {
    $entryStage = Invoke-VisibleStage -Name "entry_visible" -Map $entryMap
    $report.stages += $entryStage
    $report | ConvertTo-Json -Depth 20 |
        Set-Content -LiteralPath $reportPath -Encoding utf8
    # An injected-but-dormant capture hook is still a fail-closed policy
    # finding, but it is not equivalent to a rendering failure. Continue to
    # the bounded M01 diagnostic only when Entry proved its core render health;
    # the verifier still rejects the overall gate unless both stages also
    # satisfy the zero-overlay policy.
    $entryCoreRenderHealthy = (
        -not $entryStage.timed_out -and
        $entryStage.natural_exit -and
        $entryStage.exit_code -eq 0 -and
        $entryStage.receipt.exists -and
        $entryStage.receipt.schema -eq "skyguard.shipping-startup-smoke.v1" -and
        $entryStage.receipt.state -eq "COMPLETE" -and
        $entryStage.receipt.map -eq "Entry" -and
        $entryStage.signatures.gpu_timeout_count -eq 0 -and
        $entryStage.signatures.critical_signature_count -eq 0 -and
        $entryStage.module_scan.query_complete -and
        $entryStage.cleanup.success
    )
    if ($entryCoreRenderHealthy) {
        $report.stages += Invoke-VisibleStage -Name "m01_visible" -Map $m01Map
    }
    else {
        $report.stages += New-NotRunStage `
            -Name "m01_visible" -Map $m01Map `
            -Status "SKIPPED_ENTRY_FAILED" `
            -Reason "Entry prerequisite failed."
    }
    $report.terminal_state = "EXECUTION_COMPLETE"
}
catch {
    $failureText = "$($_.Exception.Message) | $($_.ScriptStackTrace)"
    $report.failure = $failureText
    $report.terminal_state = "EXECUTION_FAILED"
    if ($report.stages.Count -eq 0) {
        $report.stages += New-NotRunStage `
            -Name "entry_visible" -Map $entryMap -Status "FAILED" `
            -Reason "Supervisor failure: $failureText"
    }
    if ($report.stages.Count -eq 1) {
        $report.stages += New-NotRunStage `
            -Name "m01_visible" -Map $m01Map `
            -Status "SKIPPED_ENTRY_FAILED" `
            -Reason "Entry prerequisite did not pass."
    }
}

$report.generated_at_utc = [DateTime]::UtcNow.ToString("o")
$report | ConvertTo-Json -Depth 20 |
    Set-Content -LiteralPath $reportPath -Encoding utf8

& py -3 $verifier --report $reportPath --output $verificationPath
$verificationExitCode = $LASTEXITCODE
if (Test-Path -LiteralPath $verificationPath -PathType Leaf) {
    Get-Content -LiteralPath $verificationPath -Raw
}
if ($verificationExitCode -ne 0) {
    exit 2
}
exit 0
