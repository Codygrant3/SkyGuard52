[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

$projectRoot = 'D:\Skyguard52'
$standingAuthority = 'D:\Skyguard52\Production\standing_heavy_process_authorization.json'
$standingAuthorityHash = '48277d7edd869cc2b841c3993e8f7599bec5291ddf23e9c442b33e09b870c089'
$sourceBlend = 'D:\Skyguard52\Content\Skyguard\Meshes\Source\Mission01\HeroGroupedTopology_008\BLD_M01_HERO_GROUPED_TOPOLOGY_008_MASTER.blend'
$sourceBlendBytes = 2979460
$sourceBlendHash = 'a45905e8c21557cbaf974df6dd6d5495d071c497207c3c3b00181e1d5ad833a7'
$gameplayCpp = 'D:\Skyguard52\Source\Skyguard52\SkyguardPathfinderBoss.cpp'
$gameplayCppBytes = 6437
$gameplayCppHash = 'd13ebf43fb7716d1e72625395a29305c7558cd9b6529b309f3a7841c20ea047c'
$gameplayHeader = 'D:\Skyguard52\Source\Skyguard52\SkyguardPathfinderBoss.h'
$gameplayHeaderBytes = 1748
$gameplayHeaderHash = '40f23efc4c594b4b40187ff1cd5659a80b45796438ac085fba85d64afb264b2c'
$sourceInspection = 'D:\Skyguard52\Saved\Reports\M01_PATHFINDER_SOURCE_INSPECTION_STDOUT.log'
$sourceInspectionBytes = 24393
$sourceInspectionHash = '78630cc416b037b74ae1f96a551f2172453dac34923bbda51288efd52e76cdb3'
$radarLearningFreeze = 'D:\Skyguard52\Docs\AAA_Review\M01_RADAR_POST_GROK_MCP_PRODUCTION_CORRECTION02_POSTREVIEW_TERMINAL_FREEZE.json'
$radarLearningFreezeBytes = 4710
$radarLearningFreezeHash = '3f6acfb5d7c6e321098ef7eb9868e80b9308d78d41fd2159ba6302156184bd25'
$promptPath = 'D:\Skyguard52\Production\Prompts\M01_PATHFINDER_BOSS_GROK_MCP_PRODUCTION_ATTEMPT01.md'
$attemptRoot = 'D:\Skyguard52\Production\Attempts\m01-pathfinder-boss-grok-mcp\attempt_20260811T052000000000Z'
$outputRoot = Join-Path $attemptRoot 'output'
$terminalPath = Join-Path $attemptRoot 'terminal_manifest.json'
$blenderPath = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
$nodePath = 'C:\Program Files\nodejs\node.exe'
$codexPath = 'C:\Users\chris\AppData\Roaming\npm\node_modules\@openai\codex\bin\codex.js'
$routerSecretPath = 'C:\Users\chris\.codex\codex-router\caller-secret'
$mcpClient = 'D:\Skyguard52\Tools\BlenderMCP\skyguard_blender_mcp_client.py'
$shutdownScript = 'D:\Skyguard52\Scripts\GrokProduction\shutdown_blender_mcp.py'
$finalizeScript = 'D:\Skyguard52\Scripts\GrokProduction\finalize_m01_pathfinder_boss_scene.py'
$renderVerifier = 'D:\Skyguard52\Scripts\GrokProduction\verify_m01_pathfinder_render_suite.py'
$expectedBlend = Join-Path $outputRoot 'M01_PathfinderBoss_GrokMCP_Production_A.blend'
$expectedGlb = Join-Path $outputRoot 'exports\M01_PathfinderBoss_GrokMCP_Production_A.glb'
$expectedFbx = Join-Path $outputRoot 'exports\M01_PathfinderBoss_GrokMCP_Production_A.fbx'
$expectedReport = Join-Path $outputRoot 'implementation_report.json'
$expectedBuildReport = Join-Path $outputRoot 'grok_build_report.json'
$expectedCheckpointReceipt = Join-Path $outputRoot 'receipts\checkpoint_review.json'
$expectedSerializationReceipt = Join-Path $outputRoot 'receipts\scene_serialization_receipt.json'
$expectedCameraReceipt = Join-Path $outputRoot 'receipts\camera_framing_receipt.json'
$renderReviewPath = Join-Path $outputRoot 'receipts\render_suite_automatic_review.json'
$finalizerLogPath = Join-Path $attemptRoot 'deterministic_scene_serialization.log'
$renderVerifierLogPath = Join-Path $attemptRoot 'render_suite_verifier.log'
$eventsPath = Join-Path $attemptRoot 'grok_events.jsonl'
$grokErrorPath = Join-Path $attemptRoot 'grok_stderr.log'
$grokFinalPath = Join-Path $attemptRoot 'grok_final.md'
$grokExitPath = Join-Path $attemptRoot 'grok_process_exit.json'
$blenderStdoutPath = Join-Path $attemptRoot 'blender_stdout.log'
$blenderStderrPath = Join-Path $attemptRoot 'blender_stderr.log'
$processSamplesPath = Join-Path $attemptRoot 'process_tree_samples.jsonl'
$startedUtc = [DateTime]::UtcNow.ToString('o')

$blenderProcess = $null
$grokProcess = $null
$blenderLaunchCount = 0
$grokLaunchCount = 0
$retryCount = 0
$timedOut = $false
$failureStage = $null
$failureMessage = $null
$grokExitCode = $null
$grokExitCodeType = $null
$sourceHashAfter = $null
$sourceBytesAfter = $null
$tokenUsage = $null
$finalizerExitCode = $null
$finalizerPassed = $false
$renderVerifierExitCode = $null
$renderVerifierPassed = $false
$classification = 'FAILED_WITH_EVIDENCE'
$secret = $null

function Get-Sha256Lower([string]$Path) {
    $stream = $null
    $sha = $null
    try {
        $stream = [System.IO.FileStream]::new($Path, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::Read)
        $sha = [System.Security.Cryptography.SHA256]::Create()
        $digest = $sha.ComputeHash($stream)
        return (($digest | ForEach-Object { $_.ToString('x2') }) -join '')
    } finally {
        if ($sha) { $sha.Dispose() }
        if ($stream) { $stream.Dispose() }
    }
}

function Assert-FileAuthority([string]$Path, [long]$Bytes, [string]$Sha256) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw "Missing authority: $Path" }
    $item = Get-Item -LiteralPath $Path
    if ($item.Length -ne $Bytes) { throw "Authority byte mismatch: $Path" }
    if ((Get-Sha256Lower $Path) -ne $Sha256) { throw "Authority SHA-256 mismatch: $Path" }
}

function Get-HeavyProcesses {
    $names = @('blender', 'UnrealEditor', 'UnrealEditor-Cmd', 'ShaderCompileWorker', 'AutomationTool', 'UnrealBuildTool', 'cl', 'link')
    return @(Get-Process -ErrorAction SilentlyContinue | Where-Object { $names -contains $_.ProcessName })
}

function Test-McpListener([int]$ExpectedPid) {
    $listeners = @(Get-NetTCPConnection -State Listen -LocalPort 9876 -ErrorAction SilentlyContinue)
    return [bool]($listeners | Where-Object { $_.OwningProcess -eq $ExpectedPid })
}

function Write-JsonFile([string]$Path, $Value, [int]$Depth = 12) {
    $parent = Split-Path -Parent $Path
    if ($parent -and -not (Test-Path -LiteralPath $parent)) { [void](New-Item -ItemType Directory -Path $parent -Force) }
    $json = $Value | ConvertTo-Json -Depth $Depth
    [System.IO.File]::WriteAllText($Path, $json + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
}

function Add-ProcessSample {
    $ids = @()
    if ($blenderProcess) { $ids += $blenderProcess.Id }
    if ($grokProcess) { $ids += $grokProcess.Id }
    $rows = @()
    foreach ($id in $ids) {
        $process = Get-CimInstance Win32_Process -Filter "ProcessId=$id" -ErrorAction SilentlyContinue
        if ($process) {
            $safeCommandLine = $process.CommandLine
            if ($secret) { $safeCommandLine = $safeCommandLine.Replace($secret, '[REDACTED]') }
            $rows += [ordered]@{ pid = [int]$process.ProcessId; parent_pid = [int]$process.ParentProcessId; name = $process.Name; command_line = $safeCommandLine }
        }
        foreach ($child in @(Get-CimInstance Win32_Process -Filter "ParentProcessId=$id" -ErrorAction SilentlyContinue)) {
            $safeChildCommandLine = $child.CommandLine
            if ($secret) { $safeChildCommandLine = $safeChildCommandLine.Replace($secret, '[REDACTED]') }
            $rows += [ordered]@{ pid = [int]$child.ProcessId; parent_pid = [int]$child.ParentProcessId; name = $child.Name; command_line = $safeChildCommandLine }
        }
    }
    $sample = [ordered]@{ at_utc = [DateTime]::UtcNow.ToString('o'); processes = $rows }
    [System.IO.File]::AppendAllText($processSamplesPath, (($sample | ConvertTo-Json -Depth 6 -Compress) + [Environment]::NewLine), [System.Text.UTF8Encoding]::new($false))
}

function Redact-AttemptTextEvidence {
    if (-not $secret -or -not (Test-Path -LiteralPath $attemptRoot)) { return }
    $extensions = @('.json', '.jsonl', '.log', '.md', '.txt', '.py', '.ps1')
    foreach ($file in @(Get-ChildItem -LiteralPath $attemptRoot -Recurse -File | Where-Object { $extensions -contains $_.Extension.ToLowerInvariant() })) {
        try {
            $content = [System.IO.File]::ReadAllText($file.FullName)
            if ($content.Contains($secret)) {
                [System.IO.File]::WriteAllText($file.FullName, $content.Replace($secret, '[REDACTED]'), [System.Text.UTF8Encoding]::new($false))
            }
        } catch {
        }
    }
}

try {
    $failureStage = 'preflight'
    Assert-FileAuthority $standingAuthority 2146 $standingAuthorityHash
    Assert-FileAuthority $sourceBlend $sourceBlendBytes $sourceBlendHash
    Assert-FileAuthority $gameplayCpp $gameplayCppBytes $gameplayCppHash
    Assert-FileAuthority $gameplayHeader $gameplayHeaderBytes $gameplayHeaderHash
    Assert-FileAuthority $sourceInspection $sourceInspectionBytes $sourceInspectionHash
    Assert-FileAuthority $radarLearningFreeze $radarLearningFreezeBytes $radarLearningFreezeHash
    foreach ($requiredPath in @($promptPath, $blenderPath, $nodePath, $codexPath, $routerSecretPath, $mcpClient, $shutdownScript, $finalizeScript, $renderVerifier)) {
        if (-not (Test-Path -LiteralPath $requiredPath -PathType Leaf)) { throw "Required file is absent: $requiredPath" }
    }
    if (Test-Path -LiteralPath $attemptRoot) { throw "Fresh attempt namespace already exists: $attemptRoot" }
    if (@(Get-HeavyProcesses).Count -ne 0) { throw 'A governed heavy process is already active.' }
    if (@(Get-NetTCPConnection -State Listen -LocalPort 9876 -ErrorAction SilentlyContinue).Count -ne 0) { throw 'Port 9876 already has a live listener.' }

    [void](New-Item -ItemType Directory -Path $attemptRoot)
    foreach ($relative in @('output', 'output\scripts', 'output\checkpoint', 'output\checkpoint_renders', 'output\renders', 'output\textures', 'output\exports', 'output\receipts')) {
        [void](New-Item -ItemType Directory -Path (Join-Path $attemptRoot $relative))
    }

    $failureStage = 'blender_launch'
    $blenderProcess = Start-Process -FilePath $blenderPath -ArgumentList @($sourceBlend) -WorkingDirectory $projectRoot -WindowStyle Hidden -RedirectStandardOutput $blenderStdoutPath -RedirectStandardError $blenderStderrPath -PassThru
    $blenderLaunchCount = 1
    $listenerDeadline = [DateTime]::UtcNow.AddSeconds(120)
    while ([DateTime]::UtcNow -lt $listenerDeadline) {
        if ($blenderProcess.HasExited) { throw "Blender exited before MCP readiness with code $($blenderProcess.ExitCode)." }
        if (Test-McpListener $blenderProcess.Id) { break }
        Start-Sleep -Milliseconds 750
    }
    if (-not (Test-McpListener $blenderProcess.Id)) { throw 'Blender MCP did not bind port 9876 within 120 seconds.' }

    $failureStage = 'grok_launch'
    $secret = (Get-Content -LiteralPath $routerSecretPath -Raw).Trim()
    if ($secret.Length -lt 32) { throw 'Router caller capability is invalid.' }
    $baseUrl = "http://127.0.0.1:4102/_codex-router/$secret/v1"
    $startInfo = [System.Diagnostics.ProcessStartInfo]::new()
    $startInfo.FileName = $nodePath
    $startInfo.WorkingDirectory = $projectRoot
    $startInfo.UseShellExecute = $false
    $startInfo.RedirectStandardInput = $true
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    $arguments = @(
        $codexPath, 'exec', '--ephemeral', '--ignore-user-config', '--dangerously-bypass-approvals-and-sandbox', '--json', '--color', 'never',
        '--output-last-message', $grokFinalPath, '-m', 'grok-oauth/grok-4.5', '-C', $projectRoot,
        '-c', 'model_provider="skyguard_router"', '-c', 'model_reasoning_effort="high"',
        '-c', 'model_providers.skyguard_router.name="Skyguard Router"',
        '-c', "model_providers.skyguard_router.base_url=`"$baseUrl`"",
        '-c', 'model_providers.skyguard_router.env_key="SKYGUARD_ROUTER_SECRET"',
        '-c', 'model_providers.skyguard_router.wire_api="responses"'
    )
    foreach ($argument in $arguments) { [void]$startInfo.ArgumentList.Add($argument) }
    $startInfo.Environment['SKYGUARD_ROUTER_SECRET'] = $secret
    [void]$startInfo.Environment.Remove('XAI_API_KEY')

    $grokProcess = [System.Diagnostics.Process]::Start($startInfo)
    $grokLaunchCount = 1
    $stdoutTask = $grokProcess.StandardOutput.ReadToEndAsync()
    $stderrTask = $grokProcess.StandardError.ReadToEndAsync()
    $prompt = Get-Content -LiteralPath $promptPath -Raw
    $grokProcess.StandardInput.Write($prompt)
    $grokProcess.StandardInput.Close()

    $failureStage = 'grok_execution'
    $deadline = [DateTime]::UtcNow.AddMinutes(60)
    $nextSample = [DateTime]::MinValue
    while (-not $grokProcess.HasExited) {
        if ([DateTime]::UtcNow -ge $nextSample) { Add-ProcessSample; $nextSample = [DateTime]::UtcNow.AddSeconds(10) }
        if ([DateTime]::UtcNow -ge $deadline) { $timedOut = $true; Stop-Process -Id $grokProcess.Id -Force -ErrorAction SilentlyContinue; break }
        Start-Sleep -Milliseconds 1000
    }
    $grokProcess.WaitForExit()
    $grokProcess.Refresh()
    if ($null -eq $grokProcess.ExitCode) { throw 'The completed Grok process did not expose a numeric exit code.' }
    $grokExitCode = [int]$grokProcess.ExitCode
    $grokExitCodeType = $grokExitCode.GetType().FullName
    $stdoutRaw = $stdoutTask.GetAwaiter().GetResult()
    $stderrRaw = $stderrTask.GetAwaiter().GetResult()
    if ($null -eq $stdoutRaw) { $stdoutRaw = '' }
    if ($null -eq $stderrRaw) { $stderrRaw = '' }
    $stdout = $stdoutRaw.Replace($secret, '[REDACTED]')
    $stderr = $stderrRaw.Replace($secret, '[REDACTED]')
    [System.IO.File]::WriteAllText($eventsPath, $stdout, [System.Text.UTF8Encoding]::new($false))
    [System.IO.File]::WriteAllText($grokErrorPath, $stderr, [System.Text.UTF8Encoding]::new($false))
    Write-JsonFile $grokExitPath ([ordered]@{ exit_code = $grokExitCode; exit_code_type = $grokExitCodeType; completed_utc = [DateTime]::UtcNow.ToString('o'); timed_out = $timedOut })
    foreach ($line in ($stdout -split "`r?`n")) {
        if (-not $line.Trim()) { continue }
        try { $event = $line | ConvertFrom-Json -ErrorAction Stop; if ($event.type -eq 'turn.completed' -and $event.usage) { $tokenUsage = $event.usage } } catch { continue }
    }

    $failureStage = 'deterministic_scene_serialization'
    if ($timedOut -or $grokExitCode -ne 0) { throw 'Grok did not complete successfully; deterministic scene serialization is prohibited.' }
    $finalizerOutput = (& python $mcpClient --timeout 420 execute-file --file $finalizeScript 2>&1 | Out-String)
    $finalizerExitCode = [int]$LASTEXITCODE
    [System.IO.File]::WriteAllText($finalizerLogPath, $finalizerOutput, [System.Text.UTF8Encoding]::new($false))
    $finalizerPassed = [bool]($finalizerExitCode -eq 0 -and $finalizerOutput.Contains('SKYGUARD_PATHFINDER_FINALIZE_PASS') -and (Test-Path -LiteralPath $expectedSerializationReceipt -PathType Leaf))
    if (-not $finalizerPassed) { throw 'Deterministic scene serialization did not produce its required PASS marker and receipt.' }

    $failureStage = 'automatic_render_review'
    $renderVerifierOutput = (& python $renderVerifier --renders (Join-Path $outputRoot 'renders') --output $renderReviewPath 2>&1 | Out-String)
    $renderVerifierExitCode = [int]$LASTEXITCODE
    [System.IO.File]::WriteAllText($renderVerifierLogPath, $renderVerifierOutput, [System.Text.UTF8Encoding]::new($false))
    $renderVerifierPassed = [bool]($renderVerifierExitCode -eq 0 -and $renderVerifierOutput.Contains('PASS_AUTOMATIC_AWAITING_DIRECT_VISUAL_REVIEW'))
    if (-not $renderVerifierPassed) { throw 'Automatic render-suite review failed.' }

    $failureStage = 'automatic_postflight'
    $renderFiles = @(Get-ChildItem -LiteralPath (Join-Path $outputRoot 'renders') -Filter '*.png' -File)
    $checkpointFiles = @(Get-ChildItem -LiteralPath (Join-Path $outputRoot 'checkpoint_renders') -Filter '*.png' -File)
    $sourceBytesAfter = (Get-Item -LiteralPath $sourceBlend).Length
    $sourceHashAfter = Get-Sha256Lower $sourceBlend
    $passed = (
        -not $timedOut -and $grokExitCode -eq 0 -and $finalizerPassed -and $renderVerifierPassed -and
        (Test-Path -LiteralPath $expectedBlend -PathType Leaf) -and
        (Test-Path -LiteralPath $expectedGlb -PathType Leaf) -and
        (Test-Path -LiteralPath $expectedFbx -PathType Leaf) -and
        (Test-Path -LiteralPath $expectedReport -PathType Leaf) -and
        (Test-Path -LiteralPath $expectedBuildReport -PathType Leaf) -and
        (Test-Path -LiteralPath $expectedCheckpointReceipt -PathType Leaf) -and
        (Test-Path -LiteralPath $expectedSerializationReceipt -PathType Leaf) -and
        (Test-Path -LiteralPath $expectedCameraReceipt -PathType Leaf) -and
        $renderFiles.Count -eq 8 -and $checkpointFiles.Count -eq 3 -and
        $sourceBytesAfter -eq $sourceBlendBytes -and $sourceHashAfter -eq $sourceBlendHash
    )
    if ($passed) { $classification = 'PASSED_AUTOMATIC_AWAITING_DIRECT_VISUAL_REVIEW'; $failureStage = $null; $failureMessage = $null }
    else { $failureMessage = 'Output did not meet the automatic file, checkpoint, render, structure, framing, image-statistics, or source-integrity contract.' }
} catch {
    $failureMessage = $_.Exception.Message
    [Console]::Error.WriteLine("SKYGUARD_SUPERVISOR_FAILURE_STAGE=$failureStage")
    [Console]::Error.WriteLine("SKYGUARD_SUPERVISOR_FAILURE_MESSAGE=$failureMessage")
} finally {
    if ($blenderProcess -and -not $blenderProcess.HasExited) {
        try { & python $mcpClient --timeout 30 execute-file --file $shutdownScript *> $null } catch {}
        $quitDeadline = [DateTime]::UtcNow.AddSeconds(20)
        while (-not $blenderProcess.HasExited -and [DateTime]::UtcNow -lt $quitDeadline) { Start-Sleep -Milliseconds 500 }
        if (-not $blenderProcess.HasExited) { Stop-Process -Id $blenderProcess.Id -Force -ErrorAction SilentlyContinue }
    }
    if (Test-Path -LiteralPath $attemptRoot) {
        Redact-AttemptTextEvidence
        if ($null -eq $sourceHashAfter -and (Test-Path -LiteralPath $sourceBlend)) { $sourceBytesAfter = (Get-Item -LiteralPath $sourceBlend).Length; $sourceHashAfter = Get-Sha256Lower $sourceBlend }
        $inventory = @()
        foreach ($file in @(Get-ChildItem -LiteralPath $attemptRoot -Recurse -File | Where-Object FullName -ne $terminalPath)) {
            $inventory += [ordered]@{ path = $file.FullName; bytes = [long]$file.Length; sha256 = Get-Sha256Lower $file.FullName }
        }
        $terminal = [ordered]@{
            schema = 'skyguard.m01-pathfinder.grok-mcp.production-attempt01.terminal.v1'
            created_at_utc = [DateTime]::UtcNow.ToString('o')
            started_at_utc = $startedUtc
            classification = $classification
            failure_stage = $failureStage
            failure_message = $failureMessage
            model = 'grok-oauth/grok-4.5'
            provider = 'local Codex router authenticated Grok OAuth caller-capability route'
            xai_api_key_removed_from_child = $true
            attempt_root = $attemptRoot
            prompt = [ordered]@{ path = $promptPath; bytes = if (Test-Path $promptPath) { (Get-Item $promptPath).Length } else { $null }; sha256 = if (Test-Path $promptPath) { Get-Sha256Lower $promptPath } else { $null } }
            execution = [ordered]@{
                blender_launches = $blenderLaunchCount; grok_launches = $grokLaunchCount; unreal_launches = 0; retries = $retryCount; timed_out = $timedOut
                blender_pid = if ($blenderProcess) { $blenderProcess.Id } else { $null }; grok_pid = if ($grokProcess) { $grokProcess.Id } else { $null }
                grok_exit_code = $grokExitCode; grok_exit_code_type = $grokExitCodeType; token_usage = $tokenUsage
                deterministic_scene_serialization_exit_code = $finalizerExitCode; deterministic_scene_serialization_passed = $finalizerPassed
                render_verifier_exit_code = $renderVerifierExitCode; render_verifier_passed = $renderVerifierPassed
            }
            source_authority = [ordered]@{ path = $sourceBlend; expected_bytes = $sourceBlendBytes; expected_sha256 = $sourceBlendHash; bytes_after = $sourceBytesAfter; sha256_after = $sourceHashAfter; unchanged = [bool]($sourceBytesAfter -eq $sourceBlendBytes -and $sourceHashAfter -eq $sourceBlendHash) }
            expected_outputs = [ordered]@{
                blend = $expectedBlend; glb = $expectedGlb; fbx = $expectedFbx; implementation_report = $expectedReport; grok_build_report = $expectedBuildReport
                checkpoint_review = $expectedCheckpointReceipt; scene_serialization_receipt = $expectedSerializationReceipt; camera_framing_receipt = $expectedCameraReceipt
                render_automatic_review = $renderReviewPath
                render_count = if (Test-Path (Join-Path $outputRoot 'renders')) { @(Get-ChildItem -LiteralPath (Join-Path $outputRoot 'renders') -Filter '*.png' -File).Count } else { 0 }
                checkpoint_render_count = if (Test-Path (Join-Path $outputRoot 'checkpoint_renders')) { @(Get-ChildItem -LiteralPath (Join-Path $outputRoot 'checkpoint_renders') -Filter '*.png' -File).Count } else { 0 }
            }
            artifacts = $inventory
            runtime_promotion_performed = $false
            next_gate = if ($classification -eq 'PASSED_AUTOMATIC_AWAITING_DIRECT_VISUAL_REVIEW') { 'Independent full-resolution review of all eight original renders and structural receipts; only accepted output may enter a fresh reversible Unreal import namespace.' } else { 'Preserve failure evidence; do not retry this namespace.' }
        }
        Write-JsonFile $terminalPath $terminal 24
    }
}

Write-Output $classification
if ($classification -ne 'PASSED_AUTOMATIC_AWAITING_DIRECT_VISUAL_REVIEW') { exit 1 }
exit 0

