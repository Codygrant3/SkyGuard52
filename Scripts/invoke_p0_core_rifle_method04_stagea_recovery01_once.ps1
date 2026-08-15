param(
    [switch]$AuthorizeSingleProduction,
    [switch]$OfflineContractTest
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Project = "D:\Skyguard52"
$SourceDir = Join-Path $Project "Production\Sources\core-rifle\artist_grade_method_04_grok_blender"
$AttemptDir = Join-Path $Project "Production\Attempts\core-rifle-artist-grade-method04\stage_A_attempt_01"
$OutputDir = Join-Path $Project "Blender\P0_CORE_RIFLE_ARTIST_GRADE_METHOD04\stage_A"
$PromptTemplate = Join-Path $Project "Docs\AAA_Review\NEXT_PROMPT_P0_CORE_RIFLE_ARTIST_GRADE_METHOD04_STAGEA.md"
$StartupTemplate = Join-Path $Project "Scripts\Templates\method04_blender_mcp_startup.py"
$BlenderExe = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
$GrokExe = "C:\Users\chris\.grok\bin\grok.exe"
$PromptPath = Join-Path $SourceDir "method04_stageA_prompt.md"
$StartupPath = Join-Path $SourceDir "blender_mcp_startup.py"
$TerminalPath = Join-Path $Project "Saved\Reports\P0_CORE_RIFLE_METHOD04_STAGEA_RECOVERY01_TERMINAL_SUPERVISOR_MANIFEST.json"
$EmergencyPath = Join-Path $Project "Saved\Reports\P0_CORE_RIFLE_METHOD04_STAGEA_RECOVERY01_EMERGENCY_RECEIPT.jsonl"
$MaxSeconds = 3600

$Authorities = @(
    @{ Path = Join-Path $Project "Production\Attempts\support-rail-coupon\attempt_20260807T221818127741Z\output\exports\PROVISIONAL_MIL_STD_1913_VALIDATION_COUPON.glb"; Hash = "811905a5ce8f44d3430e2537e1089223a5c7f0455a7cb5ec3fa7c6d2345294a6" },
    @{ Path = Join-Path $Project "Production\Attempts\support-rail-coupon\attempt_20260807T221818127741Z\output\GATE7_COMBAT_ASSET_REFINEMENT_CYCLE03_RAIL_COUPON_RECOVERY05_ATTEMPT01.blend"; Hash = "7e930ae4dcebfc74e6038667cc1230b087f428547e8e553ff738d1728538643f" },
    @{ Path = Join-Path $Project "Production\Attempts\support-rail-coupon\attempt_20260807T221818127741Z\output\dimension_receipt.json"; Hash = "1095eb6e6ec4501fdf1c3add839a5cb6fcd6749052318c3d89130fe55bc6a4ba" },
    @{ Path = Join-Path $Project "Docs\AAA_Review\GATE7_RAIL_COUPON_RECOVERY05_ACCEPTANCE_ADDENDUM_2026-08-07.md"; Hash = "bbe566e4417b8108749adf4f4f40561ba57dd801975dbcebb99bed75b875c963" },
    @{ Path = Join-Path $Project "Docs\AAA_Review\P0_CORE_RIFLE_BODY_CAP_USER_CHANGE_RECONCILIATION_2026-08-07.json"; Hash = "387392d25e180dce52ea79b297f98dc2eae669742311ecb9911ee7758c557af5" }
)

$State = [ordered]@{
    schema = "skyguard.method04-stagea-supervisor-recovery01.v1"
    gate = "P0_CORE_RIFLE_ARTIST_GRADE_METHOD04_STAGEA_TOPOLOGY_DRIVEN_FOREEND"
    started_at_utc = [DateTime]::UtcNow.ToString("o")
    ended_at_utc = $null
    classification = "FAILED_WITH_EVIDENCE"
    failure_stage = $null
    failure_message = $null
    preflight_passed = $false
    authentication_category = $null
    authentication_probe = $null
    xai_api_key_removed_from_grok_child_only = $false
    blender_launch_count = 0
    grok_session_launch_count = 0
    retry_count = 0
    blender_pid = $null
    grok_pid = $null
    blender_exit_code = $null
    blender_exit_code_type = $null
    grok_exit_code = $null
    grok_exit_code_type = $null
    timeout = $false
    process_samples = @()
    source_inventory = @()
    attempt_inventory = @()
    output_inventory = @()
}

$BlenderProcess = $null
$GrokProcess = $null

function Get-Sha256([string]$Path) {
    $stream = $null
    $sha = $null
    try {
        $stream = [System.IO.File]::Open($Path, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::Read)
        $sha = [System.Security.Cryptography.SHA256]::Create()
        return ([System.BitConverter]::ToString($sha.ComputeHash($stream))).Replace("-", "").ToLowerInvariant()
    }
    finally {
        if ($null -ne $sha) { $sha.Dispose() }
        if ($null -ne $stream) { $stream.Dispose() }
    }
}

function Get-Inventory([string]$Root) {
    if (-not (Test-Path -LiteralPath $Root)) { return @() }
    return @(Get-ChildItem -LiteralPath $Root -Recurse -File | Sort-Object FullName | ForEach-Object {
        [ordered]@{
            relative_path = $_.FullName.Substring($Root.Length).TrimStart("\")
            bytes = [int64]$_.Length
            sha256 = Get-Sha256 $_.FullName
        }
    })
}

function ConvertTo-PlainJsonData($InputObject, [int]$Depth = 0) {
    if ($Depth -gt 12) { throw "JSON data exceeded the maximum supported depth." }
    if ($null -eq $InputObject) { return $null }
    $baseObject = $InputObject.PSObject.BaseObject
    if ($baseObject -is [System.Collections.IDictionary]) {
        $plain = @{}
        foreach ($key in $baseObject.Keys) {
            $plain[[string]$key] = ConvertTo-PlainJsonData $baseObject[$key] ($Depth + 1)
        }
        return $plain
    }
    if ($baseObject -is [System.Collections.IEnumerable] -and $baseObject -isnot [string]) {
        $items = New-Object System.Collections.ArrayList
        foreach ($item in $baseObject) {
            [void]$items.Add((ConvertTo-PlainJsonData $item ($Depth + 1)))
        }
        return ,$items.ToArray()
    }
    if ($baseObject -is [string] -or $baseObject -is [bool] -or $baseObject -is [byte] -or
        $baseObject -is [int16] -or $baseObject -is [int32] -or $baseObject -is [int64] -or
        $baseObject -is [uint16] -or $baseObject -is [uint32] -or $baseObject -is [uint64] -or
        $baseObject -is [single] -or $baseObject -is [double] -or $baseObject -is [decimal]) {
        return $baseObject
    }
    if ($baseObject -is [datetime]) { return $baseObject.ToString("o") }
    throw "Unsupported JSON receipt value type: $($baseObject.GetType().FullName)"
}

function Write-JsonAtomic([string]$Path, $Value) {
    $parent = Split-Path -Parent $Path
    [System.IO.Directory]::CreateDirectory($parent) | Out-Null
    $temp = "$Path.tmp"
    Add-Type -AssemblyName System.Web.Extensions
    $serializer = New-Object System.Web.Script.Serialization.JavaScriptSerializer
    $serializer.MaxJsonLength = 10485760
    $plainValue = ConvertTo-PlainJsonData $Value
    $json = $serializer.Serialize($plainValue)
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($temp, $json, $utf8NoBom)
    Move-Item -LiteralPath $temp -Destination $Path -Force
}

function Add-ProcessSample([string]$Stage) {
    $items = @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {
        $_.Name -match '^(blender|blender-mcp|grok|UnrealEditor|ShaderCompileWorker|AutomationTool|UnrealBuildTool|cl|link|dotnet)\.exe$'
    } | Select-Object ProcessId, ParentProcessId, Name, ExecutablePath, CommandLine)
    $State.process_samples += [ordered]@{ at_utc = [DateTime]::UtcNow.ToString("o"); stage = $Stage; processes = $items }
}

function Invoke-GrokAuthenticationProbe([string]$EvidenceRoot) {
    [System.IO.Directory]::CreateDirectory($EvidenceRoot) | Out-Null
    $stdoutPath = Join-Path $EvidenceRoot "grok-models.stdout.log"
    $stderrPath = Join-Path $EvidenceRoot "grok-models.stderr.log"
    $started = [DateTime]::UtcNow
    $hadXai = Test-Path Env:XAI_API_KEY
    $originalXai = if ($hadXai) { $env:XAI_API_KEY } else { $null }
    $hadGrokHome = Test-Path Env:GROK_HOME
    $originalGrokHome = if ($hadGrokHome) { $env:GROK_HOME } else { $null }
    $originalHome = $env:HOME
    $process = $null
    $exitCode = $null
    try {
        Remove-Item Env:XAI_API_KEY -ErrorAction SilentlyContinue
        $env:GROK_HOME = "C:\Users\chris\.grok"
        $process = Start-Process -FilePath $GrokExe -ArgumentList @("models") -WorkingDirectory $Project -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath -NoNewWindow -PassThru
        $null = $process.Handle
    }
    finally {
        if ($hadXai) { $env:XAI_API_KEY = $originalXai } else { Remove-Item Env:XAI_API_KEY -ErrorAction SilentlyContinue }
        if ($hadGrokHome) { $env:GROK_HOME = $originalGrokHome } else { Remove-Item Env:GROK_HOME -ErrorAction SilentlyContinue }
        if ($env:HOME -ne $originalHome) {
            throw "Authentication probe modified HOME."
        }
    }
    if ($null -eq $process) { throw "Authentication probe did not return a process object." }
    if (-not $process.WaitForExit(30000)) {
        Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        throw "Authentication probe exceeded its 30-second timeout."
    }
    $process.WaitForExit()
    $process.Refresh()
    $exitCode = $process.ExitCode
    if ($null -eq $exitCode) { throw "Authentication probe returned a null exit code." }
    $stdout = if (Test-Path -LiteralPath $stdoutPath) { Get-Content -LiteralPath $stdoutPath -Raw } else { $null }
    $stderr = if (Test-Path -LiteralPath $stderrPath) { Get-Content -LiteralPath $stderrPath -Raw } else { $null }
    $record = [ordered]@{
        executable = $GrokExe
        arguments = @("models")
        pid = [int]$process.Id
        started_at_utc = $started.ToString("o")
        ended_at_utc = [DateTime]::UtcNow.ToString("o")
        exit_code = [int]$exitCode
        exit_code_type = $exitCode.GetType().FullName
        stdout_path = $stdoutPath
        stderr_path = $stderrPath
        stdout = $stdout
        stderr = $stderr
        xai_api_key_removed_from_child = $true
        grok_home_for_child = "C:\Users\chris\.grok"
        home_modified = $false
        parent_xai_restored = ((Test-Path Env:XAI_API_KEY) -eq $hadXai) -and ((-not $hadXai) -or ($env:XAI_API_KEY -eq $originalXai))
        parent_grok_home_restored = ((Test-Path Env:GROK_HOME) -eq $hadGrokHome) -and ((-not $hadGrokHome) -or ($env:GROK_HOME -eq $originalGrokHome))
    }
    $process.Dispose()
    return $record
}

function Test-GrokAuthenticationRecord($Record) {
    if ($null -eq $Record) { throw "Authentication record is null." }
    if ($Record.exit_code -isnot [int]) { throw "Authentication exit code is not System.Int32." }
    if ($Record.exit_code -ne 0) { throw "Authentication probe returned nonzero exit code." }
    if ([string]::IsNullOrWhiteSpace([string]$Record.stdout)) { throw "Authentication stdout is missing." }
    if ($Record.stdout -notmatch "logged in with grok\.com") { throw "OAuth confirmation is missing." }
    if ($Record.stdout -match "You are not authenticated") { throw "Authentication probe reports unauthenticated." }
    if ($Record.stdout -match "using XAI_API_KEY") { throw "Authentication probe used XAI_API_KEY." }
    if (-not $Record.parent_xai_restored -or -not $Record.parent_grok_home_restored -or $Record.home_modified) {
        throw "Authentication probe did not restore the parent environment."
    }
    return $true
}

if ($OfflineContractTest) {
    $testRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("SkyguardM04Recovery01Auth_" + [Guid]::NewGuid().ToString("N"))
    $receiptPath = Join-Path $testRoot "offline-contract-test.json"
    $result = [ordered]@{
        schema = "skyguard.method04-stagea-recovery01-offline-test.v1"
        started_at_utc = [DateTime]::UtcNow.ToString("o")
        classification = "FAILED_WITH_EVIDENCE"
        authentication_probe = $null
        synthetic_acceptances = [ordered]@{}
        synthetic_rejections = [ordered]@{}
        blender_launch_count = 0
        grok_model_session_launch_count = 0
        retry_count = 0
        governed_namespaces_created = $false
    }
    try {
        foreach ($governed in @($SourceDir, $AttemptDir, $OutputDir)) {
            if (Test-Path -LiteralPath $governed) { throw "Governed namespace already exists: $governed" }
        }
        $result.authentication_probe = Invoke-GrokAuthenticationProbe $testRoot
        Test-GrokAuthenticationRecord $result.authentication_probe | Out-Null

        $warningRecord = [ordered]@{
            exit_code = 0
            stdout = "You are logged in with grok.com."
            stderr = "auto worktree gc failed: neither GROK_HOME nor HOME is set"
            parent_xai_restored = $true
            parent_grok_home_restored = $true
            home_modified = $false
        }
        Test-GrokAuthenticationRecord $warningRecord | Out-Null
        $result.synthetic_acceptances.warning_only_stderr = $true

        $valid = $result.authentication_probe
        $cases = [ordered]@{
            unauthenticated = [ordered]@{ exit_code = 0; stdout = "You are not authenticated."; parent_xai_restored = $true; parent_grok_home_restored = $true; home_modified = $false }
            api_key = [ordered]@{ exit_code = 0; stdout = "You are using XAI_API_KEY."; parent_xai_restored = $true; parent_grok_home_restored = $true; home_modified = $false }
            nonzero = [ordered]@{ exit_code = 7; stdout = "You are logged in with grok.com."; parent_xai_restored = $true; parent_grok_home_restored = $true; home_modified = $false }
            nonnumeric = [ordered]@{ exit_code = "0"; stdout = "You are logged in with grok.com."; parent_xai_restored = $true; parent_grok_home_restored = $true; home_modified = $false }
            missing_stdout = [ordered]@{ exit_code = 0; stdout = ""; parent_xai_restored = $true; parent_grok_home_restored = $true; home_modified = $false }
            missing_oauth = [ordered]@{ exit_code = 0; stdout = "Default model: grok-4.5"; parent_xai_restored = $true; parent_grok_home_restored = $true; home_modified = $false }
        }
        foreach ($entry in $cases.GetEnumerator()) {
            $rejected = $false
            try { Test-GrokAuthenticationRecord $entry.Value | Out-Null } catch { $rejected = $true }
            if (-not $rejected) { throw "Synthetic case was not rejected: $($entry.Key)" }
            $result.synthetic_rejections[$entry.Key] = $true
        }
        $nullCodeRejected = $false
        try {
            $nullRecord = [ordered]@{ exit_code = $null; stdout = "You are logged in with grok.com."; parent_xai_restored = $true; parent_grok_home_restored = $true; home_modified = $false }
            Test-GrokAuthenticationRecord $nullRecord | Out-Null
        } catch { $nullCodeRejected = $true }
        if (-not $nullCodeRejected) { throw "Null exit code was not rejected." }
        $result.synthetic_rejections.null_exit_code = $true

        foreach ($governed in @($SourceDir, $AttemptDir, $OutputDir)) {
            if (Test-Path -LiteralPath $governed) { $result.governed_namespaces_created = $true; throw "Offline test created a governed namespace." }
        }
        $result.classification = "PASS"
    }
    catch {
        $result.failure = $_.Exception.Message
    }
    finally {
        $result.ended_at_utc = [DateTime]::UtcNow.ToString("o")
        Write-JsonAtomic $receiptPath $result
    Write-Output (Get-Content -LiteralPath $receiptPath -Raw)
        Write-Output "OFFLINE_RECEIPT=$receiptPath"
    }
    if ($result.classification -eq "PASS") { exit 0 }
    exit 1
}

try {
    if (-not $AuthorizeSingleProduction) { throw "Explicit -AuthorizeSingleProduction is required." }

    foreach ($authority in $Authorities) {
        if (-not (Test-Path -LiteralPath $authority.Path -PathType Leaf)) { throw "Missing authority: $($authority.Path)" }
        if ((Get-Sha256 $authority.Path) -ne $authority.Hash) { throw "Authority hash mismatch: $($authority.Path)" }
    }
    foreach ($required in @($PromptTemplate, $StartupTemplate, $BlenderExe, $GrokExe)) {
        if (-not (Test-Path -LiteralPath $required -PathType Leaf)) { throw "Missing required file: $required" }
    }
    foreach ($future in @($SourceDir, $AttemptDir, $OutputDir, $TerminalPath, $EmergencyPath)) {
        if (Test-Path -LiteralPath $future) { throw "Fresh namespace already exists: $future" }
    }

    $heavy = @(Get-Process -ErrorAction SilentlyContinue | Where-Object {
        $_.ProcessName -match '^(UnrealEditor|UnrealEditor-Cmd|ShaderCompileWorker|Blender|blender-mcp|grok|AutomationTool|UnrealBuildTool|cl|link|dotnet)$'
    })
    if ($heavy.Count -gt 0) { throw "Heavy process conflict: $($heavy.ProcessName -join ', ')" }
    $listener = @(Get-NetTCPConnection -LocalPort 9876 -State Listen -ErrorAction SilentlyContinue)
    if ($listener.Count -gt 0) { throw "Port 9876 already has a listener." }

    $authRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("SkyguardM04Recovery01Auth_" + [Guid]::NewGuid().ToString("N"))
    $State.authentication_probe = Invoke-GrokAuthenticationProbe $authRoot
    Test-GrokAuthenticationRecord $State.authentication_probe | Out-Null
    $State.authentication_category = "grok.com OAuth account session"

    [System.IO.Directory]::CreateDirectory($SourceDir) | Out-Null
    [System.IO.Directory]::CreateDirectory($AttemptDir) | Out-Null
    [System.IO.Directory]::CreateDirectory($OutputDir) | Out-Null
    Copy-Item -LiteralPath $PromptTemplate -Destination $PromptPath
    Copy-Item -LiteralPath $StartupTemplate -Destination $StartupPath

    $bodySearch = Join-Path $Project "Docs\AAA_Review\P0_CORE_RIFLE_METHOD04_BODY_CAP_SEARCH_2026-08-07.json"
    Copy-Item -LiteralPath $bodySearch -Destination (Join-Path $AttemptDir "body_cap_search_evidence.json")

    $BlenderStdout = Join-Path $AttemptDir "blender.stdout.log"
    $BlenderStderr = Join-Path $AttemptDir "blender.stderr.log"
    $BlenderProcess = Start-Process -FilePath $BlenderExe -ArgumentList @("--background", "--factory-startup", "--python", $StartupPath) -WorkingDirectory $Project -RedirectStandardOutput $BlenderStdout -RedirectStandardError $BlenderStderr -PassThru
    $State.blender_launch_count = 1
    $State.blender_pid = [int]$BlenderProcess.Id

    $ready = $false
    $deadline = [DateTime]::UtcNow.AddSeconds(90)
    while ([DateTime]::UtcNow -lt $deadline) {
        $BlenderProcess.Refresh()
        if ($BlenderProcess.HasExited) { throw "Blender exited before MCP readiness." }
        if (@(Get-NetTCPConnection -LocalPort 9876 -State Listen -ErrorAction SilentlyContinue).Count -gt 0) { $ready = $true; break }
        Start-Sleep -Milliseconds 500
    }
    if (-not $ready) { throw "Blender MCP listener did not become ready within 90 seconds." }

    $GrokStdout = Join-Path $AttemptDir "grok.stdout.json"
    $GrokStderr = Join-Path $AttemptDir "grok.stderr.log"
    $GrokArguments = @(
        "--prompt-file", $PromptPath,
        "--cwd", $Project,
        "--model", "grok-4.5",
        "--reasoning-effort", "high",
        "--max-turns", "20",
        "--output-format", "json",
        "--permission-mode", "bypassPermissions",
        "--no-subagents",
        "--no-memory",
        "--disable-web-search"
    )

    $originalXai = [Environment]::GetEnvironmentVariable("XAI_API_KEY", "Process")
    try {
        [Environment]::SetEnvironmentVariable("XAI_API_KEY", $null, "Process")
        $GrokProcess = Start-Process -FilePath $GrokExe -ArgumentList $GrokArguments -WorkingDirectory $Project -RedirectStandardOutput $GrokStdout -RedirectStandardError $GrokStderr -PassThru
        $State.xai_api_key_removed_from_grok_child_only = $true
    }
    finally {
        [Environment]::SetEnvironmentVariable("XAI_API_KEY", $originalXai, "Process")
    }
    $State.grok_session_launch_count = 1
    $State.grok_pid = [int]$GrokProcess.Id
    Add-ProcessSample "grok_started"

    $deadline = [DateTime]::UtcNow.AddSeconds($MaxSeconds)
    while ([DateTime]::UtcNow -lt $deadline) {
        $GrokProcess.Refresh()
        if ($GrokProcess.HasExited) { break }
        Start-Sleep -Seconds 2
    }
    $GrokProcess.Refresh()
    if (-not $GrokProcess.HasExited) {
        $State.timeout = $true
        Stop-Process -Id $GrokProcess.Id -Force -ErrorAction SilentlyContinue
        throw "Grok session exceeded $MaxSeconds seconds."
    }
    $GrokProcess.WaitForExit()
    $GrokProcess.Refresh()
    $State.grok_exit_code = [int]$GrokProcess.ExitCode
    $State.grok_exit_code_type = $GrokProcess.ExitCode.GetType().FullName
    if ($GrokProcess.ExitCode -ne 0) { throw "Grok exited with code $($GrokProcess.ExitCode)." }

    $handoff = Join-Path $AttemptDir "grok_method04_stageA_handoff.json"
    if (-not (Test-Path -LiteralPath $handoff -PathType Leaf)) { throw "Grok did not produce the required handoff." }
    $handoffData = Get-Content -LiteralPath $handoff -Raw | ConvertFrom-Json
    if ($handoffData.classification -notin @("PASSED_METHOD04_STAGEA_AWAITING_CODEX_VISUAL_REVIEW", "FAILED_METHOD04_STAGEA_WITH_EVIDENCE")) {
        throw "Invalid Grok handoff classification."
    }

    $State.classification = if ($handoffData.classification -eq "PASSED_METHOD04_STAGEA_AWAITING_CODEX_VISUAL_REVIEW") { "COMPLETED_AWAITING_CODEX_VISUAL_REVIEW" } else { "FAILED_WITH_EVIDENCE" }
    $State.preflight_passed = $true
}
catch {
    $State.failure_stage = if (-not $State.preflight_passed -and $State.grok_session_launch_count -eq 0) { "preflight_or_bridge" } else { "production" }
    $State.failure_message = $_.Exception.Message
    $State.classification = "FAILED_WITH_EVIDENCE"
}
finally {
    try {
        Add-ProcessSample "terminal"
        if ($null -ne $GrokProcess) {
            $GrokProcess.Refresh()
            if (-not $GrokProcess.HasExited) { Stop-Process -Id $GrokProcess.Id -Force -ErrorAction SilentlyContinue }
        }
        if ($null -ne $BlenderProcess) {
            $BlenderProcess.Refresh()
            if (-not $BlenderProcess.HasExited) { Stop-Process -Id $BlenderProcess.Id -Force -ErrorAction SilentlyContinue }
            Start-Sleep -Milliseconds 500
            $BlenderProcess.Refresh()
            if ($BlenderProcess.HasExited) {
                $BlenderProcess.WaitForExit()
                $BlenderProcess.Refresh()
                $State.blender_exit_code = [int]$BlenderProcess.ExitCode
                $State.blender_exit_code_type = $BlenderProcess.ExitCode.GetType().FullName
            }
        }
        $State.source_inventory = Get-Inventory $SourceDir
        $State.attempt_inventory = Get-Inventory $AttemptDir
        $State.output_inventory = Get-Inventory $OutputDir
        $State.ended_at_utc = [DateTime]::UtcNow.ToString("o")
        Write-JsonAtomic $TerminalPath $State
    }
    catch {
        try {
            $emergency = [ordered]@{ at_utc = [DateTime]::UtcNow.ToString("o"); gate = $State.gate; error = $_.Exception.Message }
            [System.IO.Directory]::CreateDirectory((Split-Path -Parent $EmergencyPath)) | Out-Null
            [System.IO.File]::AppendAllText($EmergencyPath, (($emergency | ConvertTo-Json -Compress) + [Environment]::NewLine), [System.Text.UTF8Encoding]::new($false))
        } catch {}
    }
}

if ($State.classification -eq "COMPLETED_AWAITING_CODEX_VISUAL_REVIEW") { exit 0 }
exit 1
