[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$root = 'D:\Skyguard52'
$attemptRoot = Join-Path $root 'Saved\BuildAttempts\PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY03_NATIVE_BUILD_RECOVERY01\build_attempt_01'
$packageRoot = 'D:\SG52R03B02'
$pluginRoot = Join-Path $root 'Plugins\SkyguardRecovery03NativeRecovery01'
$plugin = Join-Path $pluginRoot 'SkyguardRecovery03NativeRecovery01.uplugin'
$automationTool = 'D:\UE_5.8\Engine\Binaries\DotNET\AutomationTool\AutomationTool.exe'
$automationToolDirectory = Split-Path -Parent $automationTool
$logsRoot = Join-Path $attemptRoot 'logs'
$stdoutPath = Join-Path $logsRoot 'build.stdout.log'
$stderrPath = Join-Path $logsRoot 'build.stderr.log'
$treePath = Join-Path $attemptRoot 'process_tree_samples.jsonl'
$manifestPath = Join-Path $attemptRoot 'build_manifest.json'
$timeoutSeconds = 1200

if (Test-Path -LiteralPath $attemptRoot) { throw "Build namespace exists: $attemptRoot" }
if (Test-Path -LiteralPath $packageRoot) { throw "Short package root exists: $packageRoot" }
foreach ($reserved in @(
    (Join-Path $root 'Saved\BuildAttempts\PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY03_NATIVE_BUILD_RECOVERY01\runtime_attempt_01'),
    (Join-Path $root 'Saved\BuildAttempts\PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY03_NATIVE_BUILD_RECOVERY01\launcher_attempt_01')
)) {
    if (Test-Path -LiteralPath $reserved) { throw "Runtime namespace exists: $reserved" }
}
$heavyNames = @('UnrealEditor', 'UnrealEditor-Cmd', 'ShaderCompileWorker', 'blender', 'AutomationTool', 'UnrealBuildTool')
$heavy = @(Get-Process -ErrorAction SilentlyContinue | Where-Object { $heavyNames -contains $_.ProcessName })
if ($heavy.Count -ne 0) { throw "Heavy process preflight failed: $($heavy.ProcessName -join ', ')" }
foreach ($required in @($plugin, $automationTool)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) { throw "Missing authority: $required" }
}

New-Item -ItemType Directory -Path $logsRoot -Force | Out-Null
$arguments = @(
    'BuildPlugin',
    "-Plugin=$plugin",
    "-Package=$packageRoot",
    '-TargetPlatforms=Win64',
    '-Rocket',
    '-StrictIncludes',
    '-NoP4'
)
$startedUtc = [DateTime]::UtcNow.ToString('o')
$process = $null
$timedOut = $false
$exitCode = $null
$issue = $null
try {
    $process = Start-Process -FilePath $automationTool -WorkingDirectory $automationToolDirectory -ArgumentList $arguments -PassThru -WindowStyle Hidden -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath
    $deadline = [DateTime]::UtcNow.AddSeconds($timeoutSeconds)
    while (-not $process.HasExited -and [DateTime]::UtcNow -lt $deadline) {
        $all = @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue)
        $known = @($process.Id)
        $changed = $true
        while ($changed) {
            $changed = $false
            foreach ($candidate in $all) {
                if ($known -contains [int]$candidate.ParentProcessId -and $known -notcontains [int]$candidate.ProcessId) {
                    $known += [int]$candidate.ProcessId
                    $changed = $true
                }
            }
        }
        [ordered]@{
            utc = [DateTime]::UtcNow.ToString('o')
            root_pid = $process.Id
            processes = @($all | Where-Object { $known -contains [int]$_.ProcessId } | ForEach-Object {
                [ordered]@{
                    pid = [int]$_.ProcessId
                    parent_pid = [int]$_.ParentProcessId
                    name = [string]$_.Name
                    command_line = [string]$_.CommandLine
                }
            })
        } | ConvertTo-Json -Depth 7 -Compress | Add-Content -LiteralPath $treePath -Encoding utf8
        Start-Sleep -Seconds 2
        $process.Refresh()
    }
    if (-not $process.HasExited) {
        $timedOut = $true
        Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
    }
    $process.WaitForExit()
    $process.Refresh()
    if ($null -eq $process.ExitCode -or $process.ExitCode -isnot [int]) {
        $issue = 'Direct AutomationTool process returned a null or nonnumeric exit code.'
    } else {
        $exitCode = [int]$process.ExitCode
        if ($exitCode -ne 0) { $issue = "AutomationTool returned exit code $exitCode." }
    }
    if ($null -eq $issue) {
        $builtPlugin = Join-Path $packageRoot 'HostProject\Plugins\SkyguardRecovery03NativeRecovery01'
        $builtBinaries = Join-Path $builtPlugin 'Binaries'
        if (-not (Test-Path -LiteralPath $builtBinaries -PathType Container)) {
            $issue = 'Build reported success without plugin binaries.'
        } else {
            Copy-Item -LiteralPath $builtBinaries -Destination $pluginRoot -Recurse -Force
        }
    }
} catch {
    $issue = $_.Exception.Message
} finally {
    $produced = @()
    foreach ($scanRoot in @($packageRoot, (Join-Path $pluginRoot 'Binaries'))) {
        if (Test-Path -LiteralPath $scanRoot) {
            $produced += @(Get-ChildItem -LiteralPath $scanRoot -Recurse -File | ForEach-Object {
                [ordered]@{
                    file = $_.FullName
                    bytes = $_.Length
                    sha256 = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
                }
            })
        }
    }
    [ordered]@{
        schema = 'skyguard.recovery03-native-build-recovery01-attempt.v1'
        contract_id = 'P4.6-M01-REPRESENTATIVE-VISUAL-008-RECOVERY-03-NATIVE-BUILD-RECOVERY-01'
        executable = $automationTool
        arguments = $arguments
        working_directory = $automationToolDirectory
        started_utc = $startedUtc
        ended_utc = [DateTime]::UtcNow.ToString('o')
        process_id = if ($null -eq $process) { $null } else { $process.Id }
        timed_out = $timedOut
        actual_exit_code = $exitCode
        actual_exit_code_type = if ($null -eq $exitCode) { $null } else { $exitCode.GetType().FullName }
        issue = $issue
        launch_count = if ($null -eq $process) { 0 } else { 1 }
        automatic_retry = $false
        unreal_editor_launched = false
        package_root = $packageRoot
        produced_files = $produced
    } | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $manifestPath -Encoding utf8
}
if ($null -ne $issue) { throw "$issue Evidence: $manifestPath" }

