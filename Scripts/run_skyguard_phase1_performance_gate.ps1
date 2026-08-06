[CmdletBinding()]
param(
    [string]$ProjectRoot = "D:\Skyguard52",
    [string]$UnrealRoot = "D:\UE_5.8",
    [string]$Map = "/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_Environment_Runtime_v3",
    [ValidateRange(10, 3600)]
    [int]$DurationSeconds = 60,
    [ValidateRange(640, 7680)]
    [int]$ResolutionX = 1920,
    [ValidateRange(360, 4320)]
    [int]$ResolutionY = 1080,
    [ValidateRange(1, 240)]
    [int]$TargetFps = 60,
    [ValidateRange(60, 3600)]
    [int]$BuildTimeoutSeconds = 900,
    [ValidateRange(60, 1800)]
    [int]$AutomationTimeoutSeconds = 600,
    [ValidateRange(60, 7200)]
    [int]$RuntimeTimeoutSeconds = 300,
    [switch]$SkipBuild,
    [switch]$SkipAutomation,
    [switch]$UseEditorGame,
    [switch]$ValidateOnly
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$ProjectFile = Join-Path $ProjectRoot "Skyguard52.uproject"
$BuildTool = Join-Path $UnrealRoot "Engine\Build\BatchFiles\Build.bat"
$EditorCmd = Join-Path $UnrealRoot "Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
$EditorExe = Join-Path $UnrealRoot "Engine\Binaries\Win64\UnrealEditor.exe"
$GameExe = Join-Path $ProjectRoot "Binaries\Win64\Skyguard52.exe"
$Verifier = Join-Path $ProjectRoot "Scripts\verify_skyguard_phase1_performance_gate.py"
$Phase1Root = Join-Path $ProjectRoot "Saved\Profiling\Phase1"
$ReportsRoot = Join-Path $ProjectRoot "Saved\Reports"

function ConvertTo-CommandLineArgument {
    param([Parameter(Mandatory = $true)][string]$Value)
    if ($Value -notmatch '[\s"]') {
        return $Value
    }
    return '"' + ($Value -replace '(\\*)"', '$1$1\"' -replace '(\\+)$', '$1$1') + '"'
}

function Join-CommandLine {
    param([Parameter(Mandatory = $true)][string[]]$Arguments)
    return (($Arguments | ForEach-Object { ConvertTo-CommandLineArgument $_ }) -join " ")
}

function Get-DescendantProcessIds {
    param([Parameter(Mandatory = $true)][int]$RootProcessId)
    $allProcesses = @(Get-CimInstance Win32_Process | Select-Object ProcessId, ParentProcessId)
    $descendants = [System.Collections.Generic.List[int]]::new()
    $frontier = [System.Collections.Generic.Queue[int]]::new()
    $frontier.Enqueue($RootProcessId)
    while ($frontier.Count -gt 0) {
        $parentId = $frontier.Dequeue()
        foreach ($candidate in $allProcesses) {
            if ([int]$candidate.ParentProcessId -eq $parentId) {
                $childId = [int]$candidate.ProcessId
                $descendants.Add($childId)
                $frontier.Enqueue($childId)
            }
        }
    }
    return @($descendants)
}

function Stop-ExactProcessTree {
    param([Parameter(Mandatory = $true)][int]$RootProcessId)
    $descendants = @(Get-DescendantProcessIds -RootProcessId $RootProcessId)
    [array]::Reverse($descendants)
    foreach ($processId in $descendants) {
        Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
    }
    Stop-Process -Id $RootProcessId -Force -ErrorAction SilentlyContinue
    return @($descendants)
}

function Invoke-BoundedProcess {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$FilePath,
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [Parameter(Mandatory = $true)][string]$StdoutPath,
        [Parameter(Mandatory = $true)][string]$StderrPath,
        [Parameter(Mandatory = $true)][int]$TimeoutSeconds,
        [string]$WorkingDirectory = $ProjectRoot
    )

    $startedAt = [DateTime]::UtcNow
    $argumentString = Join-CommandLine -Arguments $Arguments
    $process = Start-Process -FilePath $FilePath `
        -ArgumentList $argumentString `
        -WorkingDirectory $WorkingDirectory `
        -RedirectStandardOutput $StdoutPath `
        -RedirectStandardError $StderrPath `
        -PassThru -WindowStyle Hidden

    $timedOut = -not $process.WaitForExit($TimeoutSeconds * 1000)
    $terminatedDescendants = @()
    if ($timedOut) {
        $terminatedDescendants = @(Stop-ExactProcessTree -RootProcessId $process.Id)
        $process.WaitForExit()
    }
    else {
        # A second parameterless wait is required when stdout/stderr are
        # redirected; it drains the asynchronous readers and makes ExitCode
        # reliably available on Windows PowerShell 5.1.
        $process.WaitForExit()
    }
    $process.Refresh()
    $exitCode = $null
    $exitCodeAvailable = $false
    if (-not $timedOut -and $process.HasExited) {
        try {
            $exitCode = [int]$process.ExitCode
            $exitCodeAvailable = $null -ne $exitCode
        }
        catch {
            $exitCode = $null
            $exitCodeAvailable = $false
        }
    }

    return [ordered]@{
        name = $Name
        file_path = $FilePath
        arguments = $Arguments
        command_line = "$FilePath $argumentString"
        pid = $process.Id
        started_at_utc = $startedAt.ToString("o")
        finished_at_utc = [DateTime]::UtcNow.ToString("o")
        duration_seconds = [Math]::Round(([DateTime]::UtcNow - $startedAt).TotalSeconds, 3)
        timeout_seconds = $TimeoutSeconds
        timed_out = $timedOut
        process_exit_observed = [bool]$process.HasExited
        terminated_descendant_pids = $terminatedDescendants
        exit_code = $exitCode
        exit_code_available = $exitCodeAvailable
        stdout = $StdoutPath
        stderr = $StderrPath
    }
}

function Save-Json {
    param(
        [Parameter(Mandatory = $true)]$Value,
        [Parameter(Mandatory = $true)][string]$Path
    )
    $Value | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $Path -Encoding UTF8
}

foreach ($requiredPath in @($ProjectFile, $BuildTool, $EditorCmd, $EditorExe, $Verifier)) {
    if (-not (Test-Path -LiteralPath $requiredPath -PathType Leaf)) {
        throw "Required file is missing: $requiredPath"
    }
}

New-Item -ItemType Directory -Force -Path $Phase1Root, $ReportsRoot | Out-Null
$attemptStamp = [DateTime]::UtcNow.ToString("yyyyMMddTHHmmssfffZ")
$AttemptRoot = Join-Path $Phase1Root "attempt_$attemptStamp"
$LogsRoot = Join-Path $AttemptRoot "logs"
$ArtifactsRoot = Join-Path $AttemptRoot "artifacts"
New-Item -ItemType Directory -Force -Path $AttemptRoot, $LogsRoot, $ArtifactsRoot | Out-Null

$ManifestPath = Join-Path $AttemptRoot "run_manifest.json"
$GatePath = Join-Path $AttemptRoot "gate_report.json"
$LatestGatePath = Join-Path $ReportsRoot "PHASE1_PERFORMANCE_GATE_LATEST.json"
$TracePath = Join-Path $ArtifactsRoot "phase1_runtime.utrace"
$EngineCsvRoot = Join-Path $env:LOCALAPPDATA "UnrealEngine\5.8\Saved\Profiling\CSV"
$CsvSearchRoots = @(
    (Join-Path $ProjectRoot "Saved\Profiling"),
    $EngineCsvRoot
)
$CsvSnapshotBefore = @(
    Get-ChildItem -LiteralPath $CsvSearchRoots -File -Recurse -ErrorAction SilentlyContinue |
        Where-Object { $_.Extension -in @(".csv", ".gz") } |
        ForEach-Object { $_.FullName }
)

$manifest = [ordered]@{
    schema = "skyguard.phase1.performance-run.v1"
    attempt_id = "attempt_$attemptStamp"
    created_at_utc = [DateTime]::UtcNow.ToString("o")
    project_root = $ProjectRoot
    project_file = $ProjectFile
    unreal_root = $UnrealRoot
    map = $Map
    requested_profile = [ordered]@{
        duration_seconds = $DurationSeconds
        resolution_x = $ResolutionX
        resolution_y = $ResolutionY
        target_fps = $TargetFps
        graphics_api = "D3D12"
        csv_capture_frames = $DurationSeconds * $TargetFps
        insights_channels = "cpu,gpu,frame,bookmark,loadtime,file,assetload"
    }
    controls = [ordered]@{
        build_timeout_seconds = $BuildTimeoutSeconds
        automation_timeout_seconds = $AutomationTimeoutSeconds
        runtime_timeout_seconds = $RuntimeTimeoutSeconds
        skip_build = [bool]$SkipBuild
        skip_automation = [bool]$SkipAutomation
        use_editor_game = [bool]$UseEditorGame
        validate_only = [bool]$ValidateOnly
    }
    automation_filter = "Skyguard52.Boss.Pathfinder"
    stages = @()
    artifacts = [ordered]@{
        attempt_root = $AttemptRoot
        trace = $TracePath
        csv_files = @()
        gate_report = $GatePath
        latest_gate_report = $LatestGatePath
    }
    terminal_state = "CREATED"
}
Save-Json -Value $manifest -Path $ManifestPath

$activeUnreal = @(
    Get-CimInstance Win32_Process |
        Where-Object {
            $_.Name -in @("UnrealEditor.exe", "UnrealEditor-Cmd.exe", "Skyguard52.exe")
        } |
        Select-Object ProcessId, Name, CommandLine
)
if ($activeUnreal.Count -gt 0) {
    $manifest.terminal_state = "BLOCKED_ACTIVE_UNREAL_PROCESS"
    $manifest.active_processes = $activeUnreal
    Save-Json -Value $manifest -Path $ManifestPath
    & py -3 $Verifier --manifest $ManifestPath --output $GatePath --latest-output $LatestGatePath
    exit 2
}

if ($ValidateOnly) {
    $manifest.terminal_state = "VALIDATED_NOT_EXECUTED"
    Save-Json -Value $manifest -Path $ManifestPath
    & py -3 $Verifier --manifest $ManifestPath --output $GatePath --latest-output $LatestGatePath
    exit 0
}

if (-not $SkipBuild) {
    $buildStdout = Join-Path $LogsRoot "build.stdout.log"
    $buildStderr = Join-Path $LogsRoot "build.stderr.log"
    # Both canonical paths are deliberately space-free. Do not pre-quote the
    # batch path inside this single /c payload: Join-CommandLine owns the one
    # required outer quote. Pre-quoting caused cmd.exe to receive a literal
    # leading quote/backslash sequence while still returning zero.
    $buildCommand = "$BuildTool Skyguard52 Win64 Development -Project=$ProjectFile -WaitMutex -NoHotReloadFromIDE"
    $buildStage = Invoke-BoundedProcess `
        -Name "build_development_game" `
        -FilePath $env:ComSpec `
        -Arguments @("/d", "/s", "/c", $buildCommand) `
        -StdoutPath $buildStdout `
        -StderrPath $buildStderr `
        -TimeoutSeconds $BuildTimeoutSeconds
    $manifest.stages += $buildStage
    Save-Json -Value $manifest -Path $ManifestPath
    if ($buildStage.timed_out -or $buildStage.exit_code -ne 0 -or -not (Test-Path -LiteralPath $GameExe)) {
        $manifest.terminal_state = "BUILD_FAILED"
        Save-Json -Value $manifest -Path $ManifestPath
        & py -3 $Verifier --manifest $ManifestPath --output $GatePath --latest-output $LatestGatePath
        exit 1
    }
}

if (-not $SkipAutomation) {
    $automationStdout = Join-Path $LogsRoot "automation.stdout.log"
    $automationStderr = Join-Path $LogsRoot "automation.stderr.log"
    $automationStage = Invoke-BoundedProcess `
        -Name "pathfinder_combat_destruction_automation" `
        -FilePath $EditorCmd `
        -Arguments @(
            $ProjectFile,
            "-ExecCmds=Automation RunTests Skyguard52.Boss.Pathfinder",
            "-TestExit=Automation Test Queue Empty",
            "-unattended",
            "-nop4",
            "-nosplash",
            "-NullRHI",
            "-stdout",
            "-FullStdOutLogOutput",
            "-NoAssetRegistryCache"
        ) `
        -StdoutPath $automationStdout `
        -StderrPath $automationStderr `
        -TimeoutSeconds $AutomationTimeoutSeconds
    $manifest.stages += $automationStage
    Save-Json -Value $manifest -Path $ManifestPath
    if ($automationStage.timed_out) {
        $manifest.terminal_state = "AUTOMATION_TIMEOUT"
        Save-Json -Value $manifest -Path $ManifestPath
        & py -3 $Verifier --manifest $ManifestPath --output $GatePath --latest-output $LatestGatePath
        exit 1
    }
}

$editorModule = Join-Path $ProjectRoot "Binaries\Win64\UnrealEditor-Skyguard52.dll"
$runtimeExecutable = $GameExe
$runtimeArguments = @(
    $Map,
    "-windowed",
    "-ResX=$ResolutionX",
    "-ResY=$ResolutionY",
    "-d3d12",
    "-sm6",
    "-NoVSync",
    "-benchmark",
    "-benchmarkseconds=$DurationSeconds",
    "-fps=$TargetFps",
    "-unattended",
    "-nop4",
    "-nosplash",
    "-stdout",
    "-FullStdOutLogOutput",
    "-trace=cpu,gpu,frame,bookmark,loadtime,file,assetload",
    "-tracefile=$TracePath",
    "-tracefiletrunc",
    "-traceautostart=1",
    "-csvCaptureFrames=$($DurationSeconds * $TargetFps)",
    "-csvCategories=Global",
    "-csvGpuStats",
    "-csvNamedEvents",
    "-csvMetadata=phase=phase1,attempt=$($manifest.attempt_id),map=M01_CoastalIntercept"
)

$gameIsFresh = (Test-Path -LiteralPath $GameExe) -and (
    -not (Test-Path -LiteralPath $editorModule) -or
    (Get-Item -LiteralPath $GameExe).LastWriteTimeUtc -ge (Get-Item -LiteralPath $editorModule).LastWriteTimeUtc
)
if ($UseEditorGame -or (-not $gameIsFresh)) {
    $runtimeExecutable = $EditorExe
    $runtimeArguments = @($ProjectFile) + $runtimeArguments + @("-game")
    $manifest.runtime_selection = [ordered]@{
        mode = "EditorGame"
        reason = if ($UseEditorGame) { "Explicit request" } else { "Development game executable is older than the current editor module" }
    }
}
else {
    $manifest.runtime_selection = [ordered]@{
        mode = "DevelopmentGame"
        reason = "Current Development game executable is available and not older than the editor module"
    }
}

$runtimeStdout = Join-Path $LogsRoot "runtime.stdout.log"
$runtimeStderr = Join-Path $LogsRoot "runtime.stderr.log"
$runtimeStage = Invoke-BoundedProcess `
    -Name "d3d12_runtime_profile" `
    -FilePath $runtimeExecutable `
    -Arguments $runtimeArguments `
    -StdoutPath $runtimeStdout `
    -StderrPath $runtimeStderr `
    -TimeoutSeconds $RuntimeTimeoutSeconds
$manifest.stages += $runtimeStage

$CsvSnapshotAfter = @(
    Get-ChildItem -LiteralPath $CsvSearchRoots -File -Recurse -ErrorAction SilentlyContinue |
        Where-Object { $_.Extension -in @(".csv", ".gz") } |
        ForEach-Object { $_.FullName }
)
$newCsvFiles = @($CsvSnapshotAfter | Where-Object { $_ -notin $CsvSnapshotBefore })
$manifest.artifacts.csv_files = $newCsvFiles
$manifest.terminal_state = if ($runtimeStage.timed_out) { "RUNTIME_TIMEOUT" } else { "EXECUTION_COMPLETE" }
Save-Json -Value $manifest -Path $ManifestPath

& py -3 $Verifier --manifest $ManifestPath --output $GatePath --latest-output $LatestGatePath
exit $LASTEXITCODE
