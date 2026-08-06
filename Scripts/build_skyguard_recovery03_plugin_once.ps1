[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$root = 'D:\Skyguard52'
$attemptRoot = Join-Path $root 'Saved\BuildAttempts\PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY03_NATIVE_BUILD\build_attempt_01'
$packageRoot = Join-Path $attemptRoot 'package'
$logsRoot = Join-Path $attemptRoot 'logs'
$stdoutPath = Join-Path $logsRoot 'build.stdout.log'
$stderrPath = Join-Path $logsRoot 'build.stderr.log'
$treePath = Join-Path $attemptRoot 'process_tree_samples.jsonl'
$manifestPath = Join-Path $attemptRoot 'build_manifest.json'
$uat = 'D:\UE_5.8\Engine\Build\BatchFiles\RunUAT.bat'
$plugin = Join-Path $root 'Plugins\SkyguardRecovery03\SkyguardRecovery03.uplugin'
$timeoutSeconds = 1200

if (Test-Path -LiteralPath $attemptRoot) {
    throw "Immutable build attempt namespace already exists: $attemptRoot"
}
foreach ($reserved in @(
    (Join-Path $root 'Saved\BuildAttempts\PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY03\attempt_01'),
    (Join-Path $root 'Saved\BuildAttempts\PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY03\launcher_attempt_01'),
    (Join-Path $root 'Saved\Reports\PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY03_EXECUTION_PREFLIGHT.json')
)) {
    if (Test-Path -LiteralPath $reserved) {
        throw "Governed execution namespace is no longer fresh: $reserved"
    }
}
$heavyNames = @('UnrealEditor', 'UnrealEditor-Cmd', 'ShaderCompileWorker', 'blender', 'AutomationTool', 'UnrealBuildTool')
$heavy = @(Get-Process -ErrorAction SilentlyContinue | Where-Object { $heavyNames -contains $_.ProcessName })
if ($heavy.Count -ne 0) {
    throw "Heavy process preflight failed: $($heavy.ProcessName -join ', ')"
}
if (-not (Test-Path -LiteralPath $uat -PathType Leaf)) {
    throw "RunUAT authority is absent: $uat"
}

New-Item -ItemType Directory -Path $logsRoot -Force | Out-Null
$commandLine = "`"$uat`" BuildPlugin -Plugin=`"$plugin`" -Package=`"$packageRoot`" -TargetPlatforms=Win64 -Rocket -StrictIncludes"
$startedUtc = [DateTime]::UtcNow.ToString('o')
$process = $null
$timedOut = $false
$exitCode = $null
$issue = $null

try {
    $process = Start-Process -FilePath 'cmd.exe' -ArgumentList @('/d', '/s', '/c', "`"$commandLine`"") -PassThru -WindowStyle Hidden -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath
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
        $sample = [ordered]@{
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
        }
        ($sample | ConvertTo-Json -Depth 7 -Compress) | Add-Content -LiteralPath $treePath -Encoding utf8
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
        $issue = 'Null or nonnumeric build-process exit code.'
    } else {
        $exitCode = [int]$process.ExitCode
        if ($exitCode -ne 0) {
            $issue = "Build process returned exit code $exitCode."
        }
    }
} catch {
    $issue = $_.Exception.Message
} finally {
    $produced = @()
    if (Test-Path -LiteralPath $packageRoot) {
        $produced = @(Get-ChildItem -LiteralPath $packageRoot -Recurse -File | ForEach-Object {
            [ordered]@{
                file = $_.FullName.Substring($attemptRoot.Length + 1).Replace('\', '/')
                bytes = $_.Length
                sha256 = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
            }
        })
    }
    $manifest = [ordered]@{
        schema = 'skyguard.recovery03.native-build-attempt.v1'
        contract_id = 'P4.6-M01-REPRESENTATIVE-VISUAL-008-RECOVERY-03'
        command = $commandLine
        started_utc = $startedUtc
        ended_utc = [DateTime]::UtcNow.ToString('o')
        process_id = if ($null -eq $process) { $null } else { $process.Id }
        timed_out = $timedOut
        actual_exit_code = $exitCode
        actual_exit_code_type = if ($null -eq $exitCode) { $null } else { $exitCode.GetType().FullName }
        issue = $issue
        launch_count = if ($null -eq $process) { 0 } else { 1 }
        automatic_retry = $false
        unreal_editor_launched = $false
        package_root = $packageRoot
        produced_files = $produced
    }
    $manifest | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $manifestPath -Encoding utf8
}

if ($null -ne $issue) {
    throw "$issue Evidence: $manifestPath"
}
