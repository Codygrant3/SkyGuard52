[CmdletBinding()]
param(
    [switch]$AuthorizeSingleBlender,
    [switch]$OfflineContractTest
)

$ErrorActionPreference = 'Stop'
$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$ContractPath = Join-Path $ScriptRoot 'production_refinement01_recovery01_contract.json'
$FrozenContractPath = 'D:\Skyguard52\Scripts\Production\m01_lighthouse_production_refinement01\production_refinement01_contract.json'
$WrapperPath = Join-Path $ScriptRoot 'build_m01_lighthouse_production_refinement01_recovery01.py'
$AttemptPath = 'D:\Skyguard52\Saved\BuildAttempts\M01_LIGHTHOUSE_PRODUCTION_REFINEMENT01_RECOVERY01\attempt_01'
$TerminalPath = 'D:\Skyguard52\Saved\Reports\M01_LIGHTHOUSE_PRODUCTION_REFINEMENT01_RECOVERY01_TERMINAL_MANIFEST.json'
$EmergencyPath = 'D:\Skyguard52\Saved\Reports\M01_LIGHTHOUSE_PRODUCTION_REFINEMENT01_RECOVERY01_EMERGENCY_RECEIPT.jsonl'
$BlenderPath = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
$state = [ordered]@{
    schema = 'skyguard.m01-lighthouse-production-refinement01-recovery01.terminal-supervisor.v1'
    created_at_utc = [DateTime]::UtcNow.ToString('o')
    classification = 'FAILED_WITH_EVIDENCE'
    authorized = [bool]$AuthorizeSingleBlender
    offline_contract_test = [bool]$OfflineContractTest
    preflight_passed = $false
    blender_launch_count = 0
    automatic_retry_count = 0
    unreal_launch_count = 0
    timed_out = $false
    process_id = $null
    exit_code = $null
    exit_code_type = $null
    receipt = $null
    final_inventory = $null
    error = $null
}

function Get-Sha256([string]$Path) {
    $stream = [System.IO.File]::Open($Path, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::Read)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($sha.ComputeHash($stream))).Replace('-', '').ToLowerInvariant() }
    finally { $sha.Dispose(); $stream.Dispose() }
}

function Verify-Record([object]$Entry) {
    if (-not (Test-Path -LiteralPath $Entry.path -PathType Leaf)) { throw "Authority missing: $($Entry.path)" }
    $item = Get-Item -LiteralPath $Entry.path
    if ($item.Length -ne [int64]$Entry.bytes) { throw "Authority byte mismatch: $($Entry.path)" }
    if ((Get-Sha256 $Entry.path) -ne [string]$Entry.sha256) { throw "Authority hash mismatch: $($Entry.path)" }
}

function Write-JsonAtomic([string]$Path, [object]$Value) {
    $parent = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $parent)) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }
    $temporary = "$Path.tmp"
    $Value | ConvertTo-Json -Depth 50 | Set-Content -LiteralPath $temporary -Encoding UTF8
    Move-Item -LiteralPath $temporary -Destination $Path -Force
}

function Assert-NoHeavyProcess {
    $heavy = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {
        $_.Name -match '^(UnrealEditor|UnrealEditor-Cmd|Blender|ShaderCompileWorker|AutomationTool|UnrealBuildTool|cl|link|dotnet)(\.exe)?$'
    }
    if ($heavy) { throw "Heavy process active: $($heavy.Name -join ', ')" }
}

function Write-FinalInventory {
    $rows = @()
    Get-ChildItem -LiteralPath $AttemptPath -Recurse -File | Where-Object {
        $_.Name -ne 'final_artifact_inventory.json'
    } | Sort-Object FullName | ForEach-Object {
        $rows += [ordered]@{
            path = $_.FullName
            bytes = $_.Length
            sha256 = Get-Sha256 $_.FullName
        }
    }
    $value = [ordered]@{
        schema = 'skyguard.m01-lighthouse-production-refinement01-recovery01.final-artifact-inventory.v1'
        created_at_utc = [DateTime]::UtcNow.ToString('o')
        classification = $state.classification
        artifacts = $rows
    }
    $path = Join-Path $AttemptPath 'final_artifact_inventory.json'
    Write-JsonAtomic $path $value
    return [ordered]@{
        path = $path
        bytes = (Get-Item -LiteralPath $path).Length
        sha256 = Get-Sha256 $path
    }
}

try {
    $contract = Get-Content -LiteralPath $ContractPath -Raw | ConvertFrom-Json
    if ($contract.classification -ne 'PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_LIGHTHOUSE_PRODUCTION_REFINEMENT01_RECOVERY01_BLENDER_EXECUTION') {
        throw 'Recovery01 contract classification changed'
    }
    foreach ($entry in $contract.authorities) { Verify-Record $entry }
    $frozenContract = Get-Content -LiteralPath $FrozenContractPath -Raw | ConvertFrom-Json
    foreach ($entry in $frozenContract.authorities) { Verify-Record $entry }
    if (Test-Path -LiteralPath $AttemptPath) { throw "Fresh attempt exists: $AttemptPath" }
    if (Test-Path -LiteralPath $TerminalPath) { throw "Fresh terminal exists: $TerminalPath" }
    if ($OfflineContractTest) {
        Write-Output 'PASS_M01_LIGHTHOUSE_PRODUCTION_REFINEMENT01_RECOVERY01_OFFLINE_CONTRACT'
        [Environment]::Exit([int]0)
    }
    if (-not $AuthorizeSingleBlender) { throw 'Authorization guard missing' }
    Assert-NoHeavyProcess
    New-Item -ItemType Directory -Path $AttemptPath | Out-Null
    $state.preflight_passed = $true
    $stdoutPath = Join-Path $AttemptPath 'blender.stdout.log'
    $stderrPath = Join-Path $AttemptPath 'blender.stderr.log'
    $arguments = @(
        '--background',
        '--factory-startup',
        '--python', $WrapperPath,
        '--',
        '--contract', $FrozenContractPath,
        '--attempt', $AttemptPath
    )
    $state.executable = $BlenderPath
    $state.arguments = $arguments
    $state.working_directory = 'D:\Skyguard52'
    $started = [DateTime]::UtcNow
    $process = Start-Process -FilePath $BlenderPath -ArgumentList $arguments -WorkingDirectory 'D:\Skyguard52' -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath -PassThru
    $state.blender_launch_count = 1
    $state.process_id = [int]$process.Id
    if (-not $process.WaitForExit(1800000)) {
        $state.timed_out = $true
        $process.Kill()
        $process.WaitForExit()
    }
    $process.Refresh()
    $childExitCode = [int]$process.ExitCode
    $childExitCodeType = $childExitCode.GetType().FullName
    $state.exit_code = $childExitCode
    $state.exit_code_type = $childExitCodeType
    $state.elapsed_seconds = ([DateTime]::UtcNow - $started).TotalSeconds
    $receiptPath = Join-Path $AttemptPath 'output\receipts\production_receipt.json'
    if (-not (Test-Path -LiteralPath $receiptPath)) { throw 'Production receipt missing' }
    $receipt = Get-Content -LiteralPath $receiptPath -Raw | ConvertFrom-Json
    $state.receipt = [ordered]@{
        path = $receiptPath
        bytes = (Get-Item -LiteralPath $receiptPath).Length
        sha256 = Get-Sha256 $receiptPath
        classification = $receipt.classification
    }
    if (
        $state.timed_out -or
        $childExitCode -ne 0 -or
        $childExitCodeType -ne 'System.Int32' -or
        $receipt.classification -ne 'PASSED_AUTOMATIC_AWAITING_DIRECT_FULL_RESOLUTION_VISUAL_REVIEW' -or
        [int]$receipt.render_count -ne 12
    ) {
        throw "Child or receipt failure: timeout=$($state.timed_out) code=$childExitCode type=$childExitCodeType class=$($receipt.classification) renders=$($receipt.render_count)"
    }
    $state.classification = 'PASSED_AUTOMATIC_AWAITING_DIRECT_FULL_RESOLUTION_VISUAL_REVIEW'
}
catch {
    $state.error = "$($_.Exception.GetType().Name): $($_.Exception.Message)"
}
finally {
    $state.finished_at_utc = [DateTime]::UtcNow.ToString('o')
    if (Test-Path -LiteralPath $AttemptPath) {
        try { $state.final_inventory = Write-FinalInventory }
        catch { $state.inventory_error = "$($_.Exception.GetType().Name): $($_.Exception.Message)" }
    }
    try { Write-JsonAtomic $TerminalPath $state }
    catch {
        $line = ([ordered]@{
            at_utc = [DateTime]::UtcNow.ToString('o')
            error = "$($_.Exception.GetType().Name): $($_.Exception.Message)"
        } | ConvertTo-Json -Compress)
        Add-Content -LiteralPath $EmergencyPath -Value $line -Encoding UTF8
    }
}

if ($state.classification -eq 'PASSED_AUTOMATIC_AWAITING_DIRECT_FULL_RESOLUTION_VISUAL_REVIEW') {
    [Environment]::Exit([int]0)
}
[Environment]::Exit([int]3)
