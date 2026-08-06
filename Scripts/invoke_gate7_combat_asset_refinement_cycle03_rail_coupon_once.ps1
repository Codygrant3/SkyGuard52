param(
    [switch]$AuthorizeSingleBlender
)

$ErrorActionPreference = 'Stop'

$Gate = 'GATE7_COMBAT_ASSET_REFINEMENT_CYCLE03_RAIL_COUPON_ATTEMPT01'
$ProjectRoot = 'D:\Skyguard52'
$AttemptRoot = 'D:\Skyguard52\Saved\BuildAttempts\GATE7_COMBAT_ASSET_REFINEMENT_CYCLE03_RAIL_COUPON\attempt_01'
$OutputRoot = 'D:\Skyguard52\Blender\GATE7_COMBAT_ASSET_REFINEMENT_CYCLE03_RAIL_COUPON_ATTEMPT01'
$ExternalManifest = 'D:\Skyguard52\Saved\Reports\GATE7_COMBAT_ASSET_REFINEMENT_CYCLE03_RAIL_COUPON_TERMINAL_SUPERVISOR_MANIFEST.json'
$EmergencyReceipt = 'D:\Skyguard52\Saved\Reports\GATE7_COMBAT_ASSET_REFINEMENT_CYCLE03_RAIL_COUPON_EMERGENCY_RECEIPT.jsonl'
$BlenderExecutable = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
$SourceAuthority = 'D:\Skyguard52\References\CombatAssets\CombatAsset_Refinement_Cycle03_Execution\source\blender_gate7_combat_asset_refinement_cycle03_rail_coupon_attempt01.py'
$TimeoutSeconds = 1200

$State = [ordered]@{
    gate = $Gate
    classification = 'FAILED_WITH_EVIDENCE'
    terminal = $false
    supervisor_launch_count = 1
    blender_launch_count = 0
    retry_count = 0
    unreal_launch_count = 0
    preflight_passed = $false
    governed_attempt_namespace_created = $false
    output_namespace_created = $false
    blender_pid = $null
    native_handle_retained = $false
    start_utc = [DateTime]::UtcNow.ToString('o')
    end_utc = $null
    timeout = $false
    exit_code = $null
    exit_code_type = $null
    failure_stage = $null
    failure_message = $null
    output_counts = [ordered]@{ blend = 0; glb = 0; png = 0 }
    dimension_receipt_state = 'NOT_EVALUATED'
    glb_structure_state = 'NOT_EVALUATED'
    terminal_receipt_state = 'NOT_EVALUATED'
    produced_files = @()
    process_tree_samples = @()
}
$ScriptExitCode = 1

function Get-Sha256Lower([string]$Path) {
    $stream = $null
    $sha = $null
    try {
        if ([string]::IsNullOrWhiteSpace($Path)) { throw 'Hash path is null or empty.' }
        $stream = [System.IO.File]::Open($Path, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::ReadWrite)
        $sha = [System.Security.Cryptography.SHA256]::Create()
        $digest = $sha.ComputeHash($stream)
        if ($null -eq $digest -or $digest.Length -ne 32) { throw 'SHA-256 returned a null or invalid digest.' }
        return ([System.BitConverter]::ToString($digest)).Replace('-', '').ToLowerInvariant()
    }
    finally {
        if ($sha) { $sha.Dispose() }
        if ($stream) { $stream.Dispose() }
    }
}

function Verify-FileAuthority([string]$Path, [long]$ExpectedBytes, [string]$ExpectedHash) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw "Missing authority: $Path" }
    $item = Get-Item -LiteralPath $Path
    if ($item.Length -ne $ExpectedBytes) { throw "Byte-count mismatch for $Path. Expected $ExpectedBytes, received $($item.Length)." }
    $actual = Get-Sha256Lower $Path
    if ($actual -ne $ExpectedHash.ToLowerInvariant()) { throw "SHA-256 mismatch for $Path" }
    return [ordered]@{ path = $Path; bytes = $item.Length; sha256 = $actual }
}

function Get-FileRecord([string]$Path) {
    $item = Get-Item -LiteralPath $Path
    return [ordered]@{ path = $item.FullName; bytes = $item.Length; sha256 = Get-Sha256Lower $item.FullName }
}

function Write-JsonAtomic([string]$Path, $Value) {
    $parent = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $parent)) { New-Item -ItemType Directory -Path $parent | Out-Null }
    $temporary = "$Path.tmp.$([Guid]::NewGuid().ToString('N'))"
    $json = $Value | ConvertTo-Json -Depth 20
    [System.IO.File]::WriteAllText($temporary, $json + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
    [System.IO.File]::Move($temporary, $Path)
}

function Write-EmergencyLine([string]$Path, $Value) {
    $parent = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $parent)) { New-Item -ItemType Directory -Path $parent | Out-Null }
    $line = ($Value | ConvertTo-Json -Depth 8 -Compress) + [Environment]::NewLine
    [System.IO.File]::AppendAllText($Path, $line, [System.Text.UTF8Encoding]::new($false))
}

function Write-TerminalEvidence([string]$ManifestPath, [string]$EmergencyPath, $Value) {
    try {
        Write-JsonAtomic $ManifestPath $Value
        return 'manifest'
    }
    catch {
        $emergency = [ordered]@{
            gate = $Value.gate
            classification = $Value.classification
            terminal = $true
            timestamp_utc = [DateTime]::UtcNow.ToString('o')
            manifest_error = $_.Exception.Message
            failure_stage = $Value.failure_stage
        }
        Write-EmergencyLine $EmergencyPath $emergency
        return 'emergency'
    }
}

function Get-FrozenAuthorities {
    $cycleFreezePath = 'D:\Skyguard52\Docs\AAA_Review\GATE7_COMBAT_ASSET_REFINEMENT_CYCLE03_OFFLINE_DESIGN_FREEZE.json'
    $cycleFreeze = [System.IO.File]::ReadAllText($cycleFreezePath) | ConvertFrom-Json
    $authorities = @(
        [ordered]@{
            path = $cycleFreezePath
            bytes = 4857
            sha256 = '6c2b75200e09e8189bbd203e8a2c0f6c9271a938e14a564502770e7dd3fe2f02'
        },
        [ordered]@{
            path = 'D:\Skyguard52\Docs\AAA_Review\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY03_ATTEMPT01_ACCEPTANCE_FREEZE.json'
            bytes = 9362
            sha256 = 'a59af7eb4c185b44f824d3933a4cf05e3715654d34af260e93b0911a04b2e228'
        }
    )
    foreach ($member in $cycleFreeze.members) {
        $authorities += [ordered]@{
            path = [string]$member.path
            bytes = [long]$member.bytes
            sha256 = [string]$member.sha256
        }
    }
    return $authorities
}

try {
    if (-not $AuthorizeSingleBlender) { throw 'Explicit -AuthorizeSingleBlender is required.' }

    $State.failure_stage = 'AUTHORITY_PREFLIGHT'
    foreach ($authority in Get-FrozenAuthorities) {
        $null = Verify-FileAuthority $authority.path $authority.bytes $authority.sha256
    }
    $sourceRecord = Get-FileRecord $SourceAuthority
    $blenderRecord = Verify-FileAuthority $BlenderExecutable 112975320 'e27fbfea8564aa645d4463cb0949695fd85562b9de6df9561b06859a1074adf7'

    foreach ($namespace in @($AttemptRoot, $OutputRoot, $ExternalManifest, $EmergencyReceipt)) {
        if (Test-Path -LiteralPath $namespace) { throw "Governed future namespace already exists: $namespace" }
    }
    $heavy = @(Get-CimInstance Win32_Process -ErrorAction Stop | Where-Object {
        $_.Name -match '^(blender|UnrealEditor|ShaderCompileWorker|AutomationTool|UnrealBuildTool|cl|link)(\.exe)?$'
    })
    if ($heavy.Count -gt 0) { throw "Heavy process detected: $($heavy.Name -join ', ')" }

    $State.preflight_passed = $true
    $State.failure_stage = 'ATTEMPT_NAMESPACE_CREATION'
    $sourceDirectory = Join-Path $AttemptRoot 'source'
    New-Item -ItemType Directory -Path $sourceDirectory | Out-Null
    $State.governed_attempt_namespace_created = $true
    $sourceCopy = Join-Path $sourceDirectory 'blender_gate7_combat_asset_refinement_cycle03_rail_coupon_attempt01.py'
    Copy-Item -LiteralPath $SourceAuthority -Destination $sourceCopy
    $copiedSourceRecord = Get-FileRecord $sourceCopy
    if ($copiedSourceRecord.sha256 -ne $sourceRecord.sha256 -or $copiedSourceRecord.bytes -ne $sourceRecord.bytes) {
        throw 'Attempt source copy does not match source authority.'
    }

    $preflightReceipt = [ordered]@{
        gate = $Gate
        classification = 'PASSED_SINGLE_EXECUTION_PREFLIGHT'
        timestamp_utc = [DateTime]::UtcNow.ToString('o')
        cycle03_freeze = (Get-FileRecord 'D:\Skyguard52\Docs\AAA_Review\GATE7_COMBAT_ASSET_REFINEMENT_CYCLE03_OFFLINE_DESIGN_FREEZE.json')
        recovery03_freeze = (Get-FileRecord 'D:\Skyguard52\Docs\AAA_Review\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY03_ATTEMPT01_ACCEPTANCE_FREEZE.json')
        source = $copiedSourceRecord
        blender = $blenderRecord
        blender_launch_count = 0
        retry_count = 0
        unreal_launch_count = 0
        resident_blender_mcp_count = @(Get-Process -Name 'blender-mcp' -ErrorAction SilentlyContinue).Count
        note = 'Idle bridge servers are not Blender production executables and were not launched or used.'
    }
    Write-JsonAtomic (Join-Path $AttemptRoot 'preflight_receipt.json') $preflightReceipt

    $stdoutPath = Join-Path $AttemptRoot 'blender.stdout.log'
    $stderrPath = Join-Path $AttemptRoot 'blender.stderr.log'
    $arguments = @('--background', '--factory-startup', '--python', $sourceCopy, '--', '--output', $OutputRoot)
    $State.failure_stage = 'BLENDER_LAUNCH'
    $process = Start-Process -FilePath $BlenderExecutable -ArgumentList $arguments -WorkingDirectory $AttemptRoot -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath -PassThru
    $nativeHandle = $process.Handle
    if ($nativeHandle -eq [IntPtr]::Zero) { throw 'Blender native process handle was not retained.' }
    $State.native_handle_retained = $true
    $State.blender_launch_count = 1
    $State.blender_pid = $process.Id
    $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
    while (-not $process.HasExited -and [DateTime]::UtcNow -lt $deadline) {
        $sample = @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {
            $_.ProcessId -eq $process.Id -or $_.ParentProcessId -eq $process.Id
        } | Select-Object Name, ProcessId, ParentProcessId, CommandLine)
        $State.process_tree_samples += [ordered]@{
            timestamp_utc = [DateTime]::UtcNow.ToString('o')
            processes = $sample
        }
        Start-Sleep -Seconds 2
        $process.Refresh()
    }
    if (-not $process.HasExited) {
        $State.timeout = $true
        try { $process.Kill() } catch {}
        $process.WaitForExit()
        throw "Blender exceeded the $TimeoutSeconds-second timeout."
    }
    $process.WaitForExit()
    $process.Refresh()
    $capturedExitCode = $process.ExitCode
    if ($null -eq $capturedExitCode) { throw 'Blender exit code is null.' }
    if ($capturedExitCode -isnot [System.Int32]) { throw "Invalid Blender exit-code type: $($capturedExitCode.GetType().FullName)" }
    $State.exit_code = [System.Int32]$capturedExitCode
    $State.exit_code_type = $capturedExitCode.GetType().FullName
    if ($State.exit_code -ne 0) { throw "Blender returned nonzero exit code: $($State.exit_code)" }

    $State.failure_stage = 'OUTPUT_VALIDATION'
    $State.output_namespace_created = Test-Path -LiteralPath $OutputRoot
    if (-not $State.output_namespace_created) { throw 'Blender did not create the governed output namespace.' }
    $stderrText = if (Test-Path -LiteralPath $stderrPath) { [System.IO.File]::ReadAllText($stderrPath) } else { '' }
    if ($stderrText -match '(?i)traceback|error:') { throw 'Blender stderr contains a traceback or error.' }

    $blendFiles = @(Get-ChildItem -LiteralPath $OutputRoot -Filter '*.blend' -File)
    $glbFiles = @(Get-ChildItem -LiteralPath (Join-Path $OutputRoot 'exports') -Filter '*.glb' -File)
    $pngFiles = @(Get-ChildItem -LiteralPath (Join-Path $OutputRoot 'renders') -Filter '*.png' -File)
    $State.output_counts = [ordered]@{ blend = $blendFiles.Count; glb = $glbFiles.Count; png = $pngFiles.Count }
    if ($blendFiles.Count -ne 1 -or $glbFiles.Count -ne 1 -or $pngFiles.Count -ne 11) {
        throw 'Blender output counts do not match the frozen Cycle03 execution contract.'
    }

    $dimensionReceiptPath = Join-Path $OutputRoot 'dimension_receipt.json'
    $glbReceiptPath = Join-Path $OutputRoot 'glb_structure_receipt.json'
    $inventoryPath = Join-Path $OutputRoot 'artifact_inventory.json'
    $terminalReceiptPath = Join-Path $OutputRoot 'terminal_receipt.json'
    foreach ($required in @($dimensionReceiptPath, $glbReceiptPath, $inventoryPath, $terminalReceiptPath)) {
        if (-not (Test-Path -LiteralPath $required -PathType Leaf)) { throw "Required output receipt is missing: $required" }
    }
    $dimensionReceipt = [System.IO.File]::ReadAllText($dimensionReceiptPath) | ConvertFrom-Json
    $glbReceipt = [System.IO.File]::ReadAllText($glbReceiptPath) | ConvertFrom-Json
    $terminalReceipt = [System.IO.File]::ReadAllText($terminalReceiptPath) | ConvertFrom-Json
    if (-not [bool]$dimensionReceipt.dimension_validation.all_passed) { throw 'Dimension receipt did not pass.' }
    if (-not [bool]$glbReceipt.structure.socket_present -or -not [bool]$glbReceipt.structure.collision_present) {
        throw 'GLB structure receipt is missing the socket or collision.'
    }
    if ($terminalReceipt.gate -ne $Gate -or $terminalReceipt.status -ne 'BLENDER_COMPLETED_AWAITING_EXTERNAL_VISUAL_REVIEW') {
        throw 'Terminal receipt identity or status is invalid.'
    }
    $State.dimension_receipt_state = 'PASSED'
    $State.glb_structure_state = 'PASSED'
    $State.terminal_receipt_state = 'PASSED'

    $State.produced_files = @(Get-ChildItem -LiteralPath $OutputRoot -File -Recurse | ForEach-Object {
        Get-FileRecord $_.FullName
    })
    $State.classification = 'PASSED_AUTOMATIC_AWAITING_EXTERNAL_VISUAL_REVIEW'
    $State.failure_stage = $null
    $State.failure_message = $null
    $ScriptExitCode = 0
}
catch {
    $State.classification = 'FAILED_WITH_EVIDENCE'
    if (-not $State.failure_stage) { $State.failure_stage = 'SUPERVISOR' }
    $State.failure_message = $_.Exception.Message
    try {
        [ordered]@{
            gate = $Gate
            timestamp_utc = [DateTime]::UtcNow.ToString('o')
            failure_stage = $State.failure_stage
            failure_message = $State.failure_message
        } | ConvertTo-Json -Depth 6
    }
    catch {}
    $ScriptExitCode = 91
}
finally {
    $State.terminal = $true
    $State.end_utc = [DateTime]::UtcNow.ToString('o')
    $State.output_namespace_created = Test-Path -LiteralPath $OutputRoot
    $null = Write-TerminalEvidence $ExternalManifest $EmergencyReceipt $State
}

exit $ScriptExitCode
