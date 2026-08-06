[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$root = 'D:\Skyguard52'
$attemptRoot = Join-Path $root 'Saved\BuildAttempts\PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY03_NATIVE_BUILD_RECOVERY02\build_attempt_01'
$packageRoot = 'D:\SG52R03B03'
$pluginRoot = Join-Path $root 'Plugins\SkyguardRecovery03NativeRecovery01'
$plugin = Join-Path $pluginRoot 'SkyguardRecovery03NativeRecovery01.uplugin'
$terminalFreeze = Join-Path $root 'Docs\AAA_Review\PHASE4_M01_RECOVERY03_NATIVE_BUILD_RECOVERY01_ATTEMPT01_TERMINAL_FREEZE.json'
$sourceFreeze = Join-Path $root 'Docs\AAA_Review\PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY03_NATIVE_BUILD_RECOVERY01_FREEZE.json'
$runtimeRoot = Join-Path $root 'Saved\BuildAttempts\PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY03_NATIVE_BUILD_RECOVERY02\runtime_attempt_01'
$dotnet = 'D:\UE_5.8\Engine\Binaries\ThirdParty\DotNet\10.0\win-x64\dotnet.exe'
$automationAssembly = 'D:\UE_5.8\Engine\Binaries\DotNET\AutomationTool\AutomationTool.dll'
$workingDirectory = Split-Path -Parent $automationAssembly
$logsRoot = Join-Path $attemptRoot 'logs'
$stdoutPath = Join-Path $logsRoot 'build.stdout.log'
$stderrPath = Join-Path $logsRoot 'build.stderr.log'
$treePath = Join-Path $attemptRoot 'process_tree_samples.jsonl'
$manifestPath = Join-Path $attemptRoot 'terminal_supervisor_manifest.json'
$emergencyPath = Join-Path $attemptRoot 'emergency_receipt.jsonl'
$timeoutSeconds = 1200
$arguments = @(
    $automationAssembly,
    'BuildPlugin',
    "-Plugin=$plugin",
    "-Package=$packageRoot",
    '-TargetPlatforms=Win64',
    '-Rocket',
    '-StrictIncludes',
    '-NoP4'
)

function Get-LowerSha256([string]$Path) {
    (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}
function Assert-File([string]$Path, [long]$Bytes, [string]$Sha256) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw "Missing authority: $Path" }
    $item = Get-Item -LiteralPath $Path
    if ($item.Length -ne $Bytes -or (Get-LowerSha256 $Path) -ne $Sha256) {
        throw "Authority mismatch: $Path"
    }
}
function Write-Emergency([string]$Stage, [string]$Issue) {
    try {
        New-Item -ItemType Directory -Path $attemptRoot -Force | Out-Null
        ([ordered]@{
            utc = [DateTime]::UtcNow.ToString('o')
            stage = $Stage
            issue = $Issue
            contract_id = 'P4.6-M01-RECOVERY03-NATIVE-BUILD-RECOVERY02'
        } | ConvertTo-Json -Compress) | Add-Content -LiteralPath $emergencyPath -Encoding utf8
    } catch {}
}

if (Test-Path -LiteralPath $attemptRoot) { throw "Build namespace exists: $attemptRoot" }
if (Test-Path -LiteralPath $packageRoot) { throw "Package namespace exists: $packageRoot" }
if (Test-Path -LiteralPath $runtimeRoot) { throw "Runtime namespace exists: $runtimeRoot" }
Assert-File $terminalFreeze 2765 '2fa345942cc9e4e7b91825257b893479372c7d2b8afcdea8d97067a8239bfb4a'
Assert-File $sourceFreeze 3998 '35791f4e8b6557d5c85d354cbb2e0a6ab57933fc9d6942381f462d7077315258'
Assert-File $dotnet 178400 'a8d3105441b568cfd44ac5eab8c0fc190cdefb0047e3e84e49cbce819a197a7a'
Assert-File $automationAssembly 34232 'ff7d013adf719a4e21be224edb70fb97aac78abf9de127ad81afe63b8ee51125'
$immutableFiles = @(
    @((Join-Path $root 'Docs\AAA_Review\PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY03_NATIVE_BUILD_RECOVERY01_CONTRACT.json'), 3016, '3e66b5005d5ca995039fd6d96a3b9553960a91d8b017261f2ecd99d89e85afac'),
    @((Join-Path $root 'Docs\AAA_Review\PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY03_NATIVE_BUILD_RECOVERY01_DECISION_2026-08-03.md'), 874, '18a5c3eb2c31b682d68b05386cb9342721ea515d09679659c0253c2f35fedb82'),
    @($plugin, 452, '4953138e24d76aee6db3636ae1c7a0fe3ed84cf1fabcb746c762d2f5a908963e'),
    @((Join-Path $pluginRoot 'Source\SkyguardRecovery03NativeRecovery01\SkyguardRecovery03NativeRecovery01.Build.cs'), 592, '503a39136a154158474f5d54ad55a00ccaed50c975b008174c3678434d2f1831'),
    @((Join-Path $pluginRoot 'Source\SkyguardRecovery03NativeRecovery01\Public\SkyguardRecovery03NativeRecovery01Module.h'), 3126, '3f1be719e2a33314b2954858521e49955999b547a581c92c27426d647873a9a4'),
    @((Join-Path $pluginRoot 'Source\SkyguardRecovery03NativeRecovery01\Private\SkyguardRecovery03NativeRecovery01Module.cpp'), 26674, '65b9e514819cbd531edcb71fb4d754e5180dde2996bc883125c31c2cd27d73c6'),
    @((Join-Path $root 'Saved\BuildAttempts\PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY03_NATIVE_BUILD_RECOVERY01\build_attempt_01\process_tree_samples.jsonl'), 75, '5edb62d9f46836e924a28a0797e59b7c21361cd3aa0854c5661684346c492c9d'),
    @((Join-Path $root 'Saved\BuildAttempts\PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY03_NATIVE_BUILD_RECOVERY01\build_attempt_01\logs\build.stdout.log'), 0, 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'),
    @((Join-Path $root 'Saved\BuildAttempts\PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY03_NATIVE_BUILD_RECOVERY01\build_attempt_01\logs\build.stderr.log'), 721, '69fbc6bf88422f456085c03d73faf3af1d847cf8a50b889817110e149eec3edb'),
    @((Join-Path $root 'Saved\Reports\PHASE4_M01_RECOVERY03_NATIVE_BUILD_RECOVERY01_ATTEMPT01_TERMINAL_EVIDENCE.json'), 2604, '653c7fea0d1bbdcb2a14977f838f99644b15b63fd6a4b92c2a4ada3839d8ee15'),
    @((Join-Path $root 'Saved\Reports\PHASE4_M01_RECOVERY03_NATIVE_BUILD_RECOVERY01_ATTEMPT01_READINESS.json'), 623, '143c220d8371ca8c239d7a8eba890ec3afd9671331bfebbf0fad7241921c29ca')
)
foreach ($authority in $immutableFiles) {
    Assert-File ([string]$authority[0]) ([long]$authority[1]) ([string]$authority[2])
}
$heavyNames = @('UnrealEditor', 'UnrealEditor-Cmd', 'ShaderCompileWorker', 'blender', 'AutomationTool', 'UnrealBuildTool')
$heavy = @(Get-Process -ErrorAction SilentlyContinue | Where-Object { $heavyNames -contains $_.ProcessName })
if ($heavy.Count -ne 0) { throw "Heavy process preflight failed: $($heavy.ProcessName -join ', ')" }

New-Item -ItemType Directory -Path $logsRoot -Force | Out-Null
$startedUtc = [DateTime]::UtcNow.ToString('o')
$process = $null
$processHandle = $null
$timedOut = $false
$exitCode = $null
$issue = $null
$inventoryIssue = $null
$produced = @()
$rebound = $false
$manifestWritten = $false
try {
    try {
        $process = Start-Process -FilePath $dotnet -WorkingDirectory $workingDirectory -ArgumentList $arguments -PassThru -WindowStyle Hidden -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath
        # Retain the native handle immediately so ExitCode remains readable even
        # when the child exits before the first sampling tick.
        $processHandle = $process.Handle
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
            ([ordered]@{
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
            } | ConvertTo-Json -Depth 7 -Compress) | Add-Content -LiteralPath $treePath -Encoding utf8
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
            $issue = 'Bundled dotnet child returned a null or nonnumeric exit code.'
        } else {
            $exitCode = [int]$process.ExitCode
            if ($exitCode -ne 0) { $issue = "Bundled dotnet child returned exit code $exitCode." }
        }
    } catch {
        $issue = $_.Exception.Message
        Write-Emergency 'child_process' $issue
    }

    try {
        if (Test-Path -LiteralPath $packageRoot) {
            $produced = @(Get-ChildItem -LiteralPath $packageRoot -Recurse -File | ForEach-Object {
                [ordered]@{
                    file = $_.FullName
                    bytes = $_.Length
                    sha256 = Get-LowerSha256 $_.FullName
                }
            })
        }
        if ($null -eq $issue) {
            $binaryRoot = Join-Path $packageRoot 'Binaries\Win64'
            $dll = Join-Path $binaryRoot 'UnrealEditor-SkyguardRecovery03NativeRecovery01.dll'
            $pdb = Join-Path $binaryRoot 'UnrealEditor-SkyguardRecovery03NativeRecovery01.pdb'
            $modules = Join-Path $binaryRoot 'UnrealEditor.modules'
            foreach ($required in @($dll, $pdb, $modules)) {
                if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
                    throw "Missing successful-build artifact: $required"
                }
            }
            $packagedSource = Join-Path $packageRoot 'Source\SkyguardRecovery03NativeRecovery01'
            $sourcePairs = @(
                @((Join-Path $pluginRoot 'Source\SkyguardRecovery03NativeRecovery01\SkyguardRecovery03NativeRecovery01.Build.cs'), (Join-Path $packagedSource 'SkyguardRecovery03NativeRecovery01.Build.cs')),
                @((Join-Path $pluginRoot 'Source\SkyguardRecovery03NativeRecovery01\Public\SkyguardRecovery03NativeRecovery01Module.h'), (Join-Path $packagedSource 'Public\SkyguardRecovery03NativeRecovery01Module.h')),
                @((Join-Path $pluginRoot 'Source\SkyguardRecovery03NativeRecovery01\Private\SkyguardRecovery03NativeRecovery01Module.cpp'), (Join-Path $packagedSource 'Private\SkyguardRecovery03NativeRecovery01Module.cpp'))
            )
            foreach ($pair in $sourcePairs) {
                if ((Get-LowerSha256 $pair[0]) -ne (Get-LowerSha256 $pair[1])) {
                    throw "Packaged source mismatch: $($pair[1])"
                }
            }
            Copy-Item -LiteralPath (Join-Path $packageRoot 'Binaries') -Destination $pluginRoot -Recurse -Force
            $rebound = $true
        }
    } catch {
        $inventoryIssue = $_.Exception.Message
        if ($null -eq $issue) { $issue = $inventoryIssue }
        Write-Emergency 'inventory_or_rebind' $inventoryIssue
    }
} finally {
    try {
        [ordered]@{
            schema = 'skyguard.recovery03-native-build-recovery02-terminal-supervisor.v1'
            contract_id = 'P4.6-M01-RECOVERY03-NATIVE-BUILD-RECOVERY02'
            executable = $dotnet
            arguments = $arguments
            working_directory = $workingDirectory
            started_utc = $startedUtc
            ended_utc = [DateTime]::UtcNow.ToString('o')
            process_id = if ($null -eq $process) { $null } else { $process.Id }
            process_handle_retained = ($null -ne $processHandle -and $processHandle -ne [IntPtr]::Zero)
            timed_out = $timedOut
            actual_exit_code = $exitCode
            actual_exit_code_type = if ($null -eq $exitCode) { $null } else { $exitCode.GetType().FullName }
            issue = $issue
            inventory_issue = $inventoryIssue
            launch_count = if ($null -eq $process) { 0 } else { 1 }
            retry_count = 0
            automatic_retry = $false
            unreal_editor_launched = $false
            rebound = $rebound
            package_root = $packageRoot
            produced_files = $produced
        } | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $manifestPath -Encoding utf8
        $manifestWritten = Test-Path -LiteralPath $manifestPath -PathType Leaf
    } catch {
        Write-Emergency 'terminal_manifest' $_.Exception.Message
    }
    if (-not $manifestWritten) {
        Write-Emergency 'terminal_manifest_confirmation' 'Terminal supervisor manifest was not durable.'
    }
}
if ($null -ne $issue) { throw "$issue Evidence: $manifestPath" }
if (-not $manifestWritten) { throw "Terminal supervisor manifest failed. Evidence: $emergencyPath" }
