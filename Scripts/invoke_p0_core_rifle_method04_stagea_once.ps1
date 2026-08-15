param(
    [switch]$AuthorizeSingleProduction
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
$TerminalPath = Join-Path $Project "Saved\Reports\P0_CORE_RIFLE_METHOD04_STAGEA_TERMINAL_SUPERVISOR_MANIFEST.json"
$EmergencyPath = Join-Path $Project "Saved\Reports\P0_CORE_RIFLE_METHOD04_STAGEA_EMERGENCY_RECEIPT.jsonl"
$MaxSeconds = 3600

$Authorities = @(
    @{ Path = Join-Path $Project "Production\Attempts\support-rail-coupon\attempt_20260807T221818127741Z\output\exports\PROVISIONAL_MIL_STD_1913_VALIDATION_COUPON.glb"; Hash = "811905a5ce8f44d3430e2537e1089223a5c7f0455a7cb5ec3fa7c6d2345294a6" },
    @{ Path = Join-Path $Project "Production\Attempts\support-rail-coupon\attempt_20260807T221818127741Z\output\GATE7_COMBAT_ASSET_REFINEMENT_CYCLE03_RAIL_COUPON_RECOVERY05_ATTEMPT01.blend"; Hash = "7e930ae4dcebfc74e6038667cc1230b087f428547e8e553ff738d1728538643f" },
    @{ Path = Join-Path $Project "Production\Attempts\support-rail-coupon\attempt_20260807T221818127741Z\output\dimension_receipt.json"; Hash = "1095eb6e6ec4501fdf1c3add839a5cb6fcd6749052318c3d89130fe55bc6a4ba" },
    @{ Path = Join-Path $Project "Docs\AAA_Review\GATE7_RAIL_COUPON_RECOVERY05_ACCEPTANCE_ADDENDUM_2026-08-07.md"; Hash = "bbe566e4417b8108749adf4f4f40561ba57dd801975dbcebb99bed75b875c963" },
    @{ Path = Join-Path $Project "Docs\AAA_Review\P0_CORE_RIFLE_BODY_CAP_USER_CHANGE_RECONCILIATION_2026-08-07.json"; Hash = "387392d25e180dce52ea79b297f98dc2eae669742311ecb9911ee7758c557af5" }
)

$State = [ordered]@{
    schema = "skyguard.method04-stagea-supervisor.v1"
    gate = "P0_CORE_RIFLE_ARTIST_GRADE_METHOD04_STAGEA_TOPOLOGY_DRIVEN_FOREEND"
    started_at_utc = [DateTime]::UtcNow.ToString("o")
    ended_at_utc = $null
    classification = "FAILED_WITH_EVIDENCE"
    failure_stage = $null
    failure_message = $null
    preflight_passed = $false
    authentication_category = $null
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

function Write-JsonAtomic([string]$Path, $Value) {
    $parent = Split-Path -Parent $Path
    [System.IO.Directory]::CreateDirectory($parent) | Out-Null
    $temp = "$Path.tmp"
    [System.IO.File]::WriteAllText($temp, ($Value | ConvertTo-Json -Depth 12), [System.Text.UTF8Encoding]::new($false))
    Move-Item -LiteralPath $temp -Destination $Path -Force
}

function Add-ProcessSample([string]$Stage) {
    $items = @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {
        $_.Name -match '^(blender|blender-mcp|grok|UnrealEditor|ShaderCompileWorker|AutomationTool|UnrealBuildTool|cl|link|dotnet)\.exe$'
    } | Select-Object ProcessId, ParentProcessId, Name, ExecutablePath, CommandLine)
    $State.process_samples += [ordered]@{ at_utc = [DateTime]::UtcNow.ToString("o"); stage = $Stage; processes = $items }
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

    $originalXai = [Environment]::GetEnvironmentVariable("XAI_API_KEY", "Process")
    try {
        [Environment]::SetEnvironmentVariable("XAI_API_KEY", $null, "Process")
        $authOutput = (& $GrokExe models 2>&1 | Out-String)
    }
    finally {
        [Environment]::SetEnvironmentVariable("XAI_API_KEY", $originalXai, "Process")
    }
    if ($authOutput -match "You are not authenticated" -or $authOutput -match "using XAI_API_KEY") {
        throw "Grok OAuth account session is not authenticated."
    }
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
