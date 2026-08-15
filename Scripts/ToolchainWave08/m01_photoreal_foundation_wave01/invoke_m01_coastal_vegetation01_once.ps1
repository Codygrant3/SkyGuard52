param(
    [switch]$AuthorizeSingleBlender,
    [switch]$OfflineContractTest
)

$ErrorActionPreference = 'Stop'

$Root = 'D:\Skyguard52'
$Blender = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
$Worker = 'D:\Skyguard52\Scripts\ToolchainWave08\m01_photoreal_foundation_wave01\worker_m01_coastal_vegetation01.py'
$Attempt = 'D:\Skyguard52\Saved\BuildAttempts\M01_PHOTOREAL_FOUNDATION_WAVE01_COASTAL_VEGETATION01\attempt_01'
$Output = Join-Path $Attempt 'output'
$Stdout = Join-Path $Attempt 'blender.stdout.log'
$Stderr = Join-Path $Attempt 'blender.stderr.log'
$Terminal = if ($OfflineContractTest) {
    Join-Path ([System.IO.Path]::GetTempPath()) ('skyguard_m01_coastal_vegetation01_offline_' + [guid]::NewGuid().ToString('N') + '.json')
} else {
    'D:\Skyguard52\Saved\Reports\M01_PHOTOREAL_FOUNDATION_WAVE01_COASTAL_VEGETATION01_TERMINAL_SUPERVISOR.json'
}
$ExpectedWorkerBytes = 26824
$ExpectedWorkerSha256 = 'dd623a698979b6740f4e9ecbd08caab0d43f8552102253e753d774899b923b60'
$ExpectedBlenderBytes = 112975320
$ExpectedBlenderSha256 = 'e27fbfea8564aa645d4463cb0949695fd85562b9de6df9561b06859a1074adf7'
$TimeoutSeconds = 1800

function Get-Sha256Hex([string]$Path) {
    $stream = $null
    $algorithm = $null
    try {
        $stream = [System.IO.File]::Open($Path, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::Read)
        $algorithm = [System.Security.Cryptography.SHA256]::Create()
        return ([System.BitConverter]::ToString($algorithm.ComputeHash($stream))).Replace('-', '').ToLowerInvariant()
    }
    finally {
        if ($null -ne $algorithm) { $algorithm.Dispose() }
        if ($null -ne $stream) { $stream.Dispose() }
    }
}

function Assert-Authority([string]$Path, [long]$Bytes, [string]$Sha256) {
    if (-not [System.IO.File]::Exists($Path)) { throw "Missing frozen authority: $Path" }
    $item = [System.IO.FileInfo]::new($Path)
    if ($item.Length -ne $Bytes) { throw "Authority byte-count mismatch: $Path" }
    $actual = Get-Sha256Hex $Path
    if ($actual -ne $Sha256) { throw "Authority SHA-256 mismatch: $Path" }
}

function Write-JsonAtomic([string]$Path, $Payload) {
    $directory = [System.IO.Path]::GetDirectoryName($Path)
    [System.IO.Directory]::CreateDirectory($directory) | Out-Null
    $temporary = $Path + '.tmp'
    $json = $Payload | ConvertTo-Json -Depth 16
    [System.IO.File]::WriteAllText($temporary, $json + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
    [System.IO.File]::Move($temporary, $Path)
}

function Get-ArtifactInventory([string]$Directory) {
    if (-not [System.IO.Directory]::Exists($Directory)) { return @() }
    return @(
        Get-ChildItem -LiteralPath $Directory -Recurse -File | Sort-Object FullName | ForEach-Object {
            [ordered]@{
                relative_path = $_.FullName.Substring($Directory.Length).TrimStart('\')
                bytes = [long]$_.Length
                sha256 = Get-Sha256Hex $_.FullName
            }
        }
    )
}

$state = [ordered]@{
    schema = 'skyguard.m01-coastal-vegetation01-terminal-supervisor.v1'
    asset_id = 'm01-photoreal-foundation-wave01-coastal-vegetation01'
    classification = 'FAILED_WITH_EVIDENCE'
    failure_stage = $null
    failure_message = $null
    supervisor_launch_count = 1
    blender_launch_count = 0
    retry_count = 0
    start_utc = [DateTime]::UtcNow.ToString('o')
    end_utc = $null
    executable = $Blender
    arguments = @('--background', '--factory-startup', '--python', $Worker, '--', '--output', $Output)
    working_directory = $Root
    attempt = $Attempt
    output = $Output
    pid = $null
    process_handle_retained = $false
    process_samples = @()
    timed_out = $false
    exit_code = $null
    exit_code_type = $null
    preflight = [ordered]@{}
    artifact_inventory = @()
    governed_namespace_created = $false
    unreal_launched = $false
    external_ai_used = $false
}
$process = $null
$terminalExit = 1

try {
    Assert-Authority $Worker $ExpectedWorkerBytes $ExpectedWorkerSha256
    Assert-Authority $Blender $ExpectedBlenderBytes $ExpectedBlenderSha256
    $state.preflight.authorities_verified = $true

    if ($OfflineContractTest) {
        if ([System.IO.Directory]::Exists($Attempt)) { throw 'Future attempt namespace already exists.' }
        if ([System.IO.Directory]::Exists($Output)) { throw 'Future output namespace already exists.' }
        $state.preflight.future_namespaces_absent = $true
        $state.classification = 'PASSED_OFFLINE_CONTRACT_NO_HEAVY_PROCESS_LAUNCHED'
        $terminalExit = 0
    }
    else {
        if (-not $AuthorizeSingleBlender) {
            $state.failure_stage = 'authorization'
            throw 'Missing mechanical -AuthorizeSingleBlender guard.'
        }
        if ([System.IO.Directory]::Exists($Attempt)) { throw 'Fresh attempt namespace already exists.' }
        if ([System.IO.Directory]::Exists($Output)) { throw 'Fresh output namespace already exists.' }
        if ([System.IO.File]::Exists($Terminal)) { throw 'Fresh terminal-report namespace already exists.' }
        $state.preflight.future_namespaces_absent = $true

        $heavyNames = @('UnrealEditor', 'UnrealEditor-Cmd', 'ShaderCompileWorker', 'AutomationTool', 'UnrealBuildTool', 'blender', 'cl', 'link')
        $heavy = @(Get-Process -ErrorAction SilentlyContinue | Where-Object { $heavyNames -contains $_.ProcessName } | Select-Object Id, ProcessName, StartTime)
        if ($heavy.Count -ne 0) { throw ('Heavy process gate failed: ' + (($heavy | ConvertTo-Json -Compress))) }
        $state.preflight.heavy_process_count = 0

        $drive = Get-PSDrive -Name D
        $freeDiskGb = [math]::Round($drive.Free / 1GB, 2)
        $os = Get-CimInstance Win32_OperatingSystem
        $freeMemoryGb = [math]::Round(($os.FreePhysicalMemory * 1KB) / 1GB, 2)
        if ($freeDiskGb -lt 100) { throw "Free D: disk below 100 GB: $freeDiskGb" }
        if ($freeMemoryGb -lt 12) { throw "Free physical memory below 12 GB: $freeMemoryGb" }
        $state.preflight.free_disk_gb = $freeDiskGb
        $state.preflight.free_memory_gb = $freeMemoryGb

        [System.IO.Directory]::CreateDirectory($Attempt) | Out-Null
        $state.governed_namespace_created = $true
        $state.failure_stage = 'blender_launch'
        $process = Start-Process -FilePath $Blender -ArgumentList $state.arguments -WorkingDirectory $Root -RedirectStandardOutput $Stdout -RedirectStandardError $Stderr -PassThru
        $state.blender_launch_count = 1
        $state.pid = [int]$process.Id
        $null = $process.Handle
        $state.process_handle_retained = $true
        $timer = [System.Diagnostics.Stopwatch]::StartNew()
        while (-not $process.WaitForExit(2000)) {
            $children = @(
                Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
                    Where-Object { $_.ParentProcessId -eq $process.Id } |
                    Select-Object ProcessId, ParentProcessId, Name
            )
            if ($state.process_samples.Count -lt 60) {
                $state.process_samples += [ordered]@{
                    elapsed_seconds = [math]::Round($timer.Elapsed.TotalSeconds, 2)
                    parent_has_exited = [bool]$process.HasExited
                    children = $children
                }
            }
            if ($timer.Elapsed.TotalSeconds -gt $TimeoutSeconds) {
                $state.timed_out = $true
                Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
                throw "Blender timed out after $TimeoutSeconds seconds."
            }
        }
        $process.WaitForExit()
        $process.Refresh()
        $state.exit_code = [int]$process.ExitCode
        $state.exit_code_type = $process.ExitCode.GetType().FullName
        if ($state.exit_code -ne 0) {
            $state.failure_stage = 'blender_execution'
            throw "Blender returned exit code $($state.exit_code)."
        }

        $state.failure_stage = 'artifact_validation'
        $required = @(
            (Join-Path $Output 'SKG_M01_CoastalVegetation01.blend'),
            (Join-Path $Output 'SKG_M01_CoastalVegetation01.glb'),
            (Join-Path $Output 'dimension_receipt.json'),
            (Join-Path $Output 'production_receipt.json')
        )
        foreach ($path in $required) {
            if (-not [System.IO.File]::Exists($path)) { throw "Required output missing: $path" }
        }
        $renders = @(Get-ChildItem -LiteralPath (Join-Path $Output 'renders') -Filter '*.png' -File)
        if ($renders.Count -ne 11) { throw "Expected exactly 11 renders; found $($renders.Count)." }
        foreach ($render in $renders) {
            if ($render.Length -le 1024) { throw "Truncated render: $($render.FullName)" }
        }
        $receipt = Get-Content -LiteralPath (Join-Path $Output 'production_receipt.json') -Raw | ConvertFrom-Json
        if ($receipt.classification -ne 'PASSED_AUTOMATIC_AWAITING_FULL_RESOLUTION_VISUAL_REVIEW') { throw 'Production receipt did not reach automatic pass.' }
        if ($receipt.external_models_used -ne $false -or $receipt.external_ai_used -ne $false -or $receipt.failed_geometry_reused -ne $false) { throw 'Production provenance contract failed.' }
        $state.artifact_inventory = Get-ArtifactInventory $Output
        $state.classification = 'PASSED_AUTOMATIC_AWAITING_FULL_RESOLUTION_VISUAL_REVIEW'
        $state.failure_stage = $null
        $terminalExit = 0
    }
}
catch {
    if ($null -eq $state.failure_stage) { $state.failure_stage = 'preflight' }
    $state.failure_message = $_.Exception.GetType().FullName + ': ' + $_.Exception.Message
    if ([System.IO.Directory]::Exists($Output)) { $state.artifact_inventory = Get-ArtifactInventory $Output }
    $state.classification = 'FAILED_WITH_EVIDENCE'
    $terminalExit = 1
}
finally {
    $state.end_utc = [DateTime]::UtcNow.ToString('o')
    Write-JsonAtomic $Terminal $state
    if ($OfflineContractTest) {
        $payload = Get-Content -LiteralPath $Terminal -Raw | ConvertFrom-Json
        if ($payload.classification -ne 'PASSED_OFFLINE_CONTRACT_NO_HEAVY_PROCESS_LAUNCHED' -or $payload.blender_launch_count -ne 0) {
            $terminalExit = 1
        }
        Remove-Item -LiteralPath $Terminal -Force -ErrorAction SilentlyContinue
    }
}

exit ([int]$terminalExit)
