[CmdletBinding()]
param(
    [switch]$AuthorizeSingleBlender,
    [switch]$OfflineContractTest
)

$ErrorActionPreference = 'Stop'
$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$ContractPath = Join-Path $ScriptRoot 'source_evaluation_contract.json'
$AttemptPath = 'D:\Skyguard52\Saved\BuildAttempts\M01_LIGHTHOUSE_SOURCE_EVALUATION01\attempt_01'
$TerminalPath = 'D:\Skyguard52\Saved\Reports\M01_LIGHTHOUSE_SOURCE_EVALUATION01_TERMINAL_MANIFEST.json'
$EmergencyPath = 'D:\Skyguard52\Saved\Reports\M01_LIGHTHOUSE_SOURCE_EVALUATION01_EMERGENCY_RECEIPT.jsonl'
$BlenderPath = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
$EvaluatorPath = Join-Path $ScriptRoot 'evaluate_m01_lighthouse_sources.py'
$state = [ordered]@{
    schema = 'skyguard.m01-lighthouse-source-evaluation01.terminal-supervisor.v1'
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
    source_evaluation_receipt = $null
    error = $null
}

function Get-Sha256([string]$Path) {
    $stream = [System.IO.File]::Open($Path, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::Read)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($sha.ComputeHash($stream))).Replace('-', '').ToLowerInvariant() }
    finally { $sha.Dispose(); $stream.Dispose() }
}

function Write-JsonAtomic([string]$Path, [object]$Value) {
    $parent = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $parent)) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }
    $temporary = "$Path.tmp"
    $Value | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath $temporary -Encoding UTF8
    Move-Item -LiteralPath $temporary -Destination $Path -Force
}

function Verify-Record([object]$Entry) {
    if (-not (Test-Path -LiteralPath $Entry.path -PathType Leaf)) { throw "Authority missing: $($Entry.path)" }
    $item = Get-Item -LiteralPath $Entry.path
    if ($item.Length -ne [int64]$Entry.bytes) { throw "Authority byte mismatch: $($Entry.path)" }
    if ((Get-Sha256 $Entry.path) -ne [string]$Entry.sha256) { throw "Authority hash mismatch: $($Entry.path)" }
}

function Assert-NoHeavyProcess {
    $heavy = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object { $_.Name -match '^(UnrealEditor|UnrealEditor-Cmd|Blender|ShaderCompileWorker|AutomationTool|UnrealBuildTool|cl|link|dotnet)(\.exe)?$' }
    if ($heavy) { throw "Heavy process already active: $($heavy.Name -join ', ')" }
}

try {
    $contract = Get-Content -LiteralPath $ContractPath -Raw | ConvertFrom-Json
    if ($contract.classification -ne 'PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_READ_ONLY_BLENDER_SOURCE_EVALUATION') { throw 'Contract classification changed' }
    foreach ($entry in $contract.authorities) { Verify-Record $entry }
    foreach ($entry in $contract.sources) { Verify-Record $entry }
    Verify-Record $contract.evaluator
    Verify-Record $contract.blender
    if ($contract.policies.single_blender_launch -ne $true -or $contract.policies.automatic_retries -ne 0) { throw 'Process policy changed' }
    if (Test-Path -LiteralPath $AttemptPath) { throw "Fresh attempt namespace exists: $AttemptPath" }
    if (Test-Path -LiteralPath $TerminalPath) { throw "Fresh terminal namespace exists: $TerminalPath" }
    if ($OfflineContractTest) {
        Write-Output 'PASS_M01_LIGHTHOUSE_SOURCE_EVALUATION01_OFFLINE_CONTRACT'
        [Environment]::Exit([int]0)
    }
    if (-not $AuthorizeSingleBlender) { throw 'Single Blender authorization guard was not supplied' }
    Assert-NoHeavyProcess
    New-Item -ItemType Directory -Path $AttemptPath | Out-Null
    $state.preflight_passed = $true
    $stdout = Join-Path $AttemptPath 'blender.stdout.log'
    $stderr = Join-Path $AttemptPath 'blender.stderr.log'
    $arguments = @('--background', '--factory-startup', '--python', $EvaluatorPath, '--', '--contract', $ContractPath, '--attempt', $AttemptPath)
    $started = [DateTime]::UtcNow
    $process = Start-Process -FilePath $BlenderPath -ArgumentList $arguments -WorkingDirectory 'D:\Skyguard52' -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru
    $state.blender_launch_count = 1
    $state.process_id = [int]$process.Id
    $process.WaitForExit()
    $process.Refresh()
    $state.exit_code = [int]$process.ExitCode
    $state.exit_code_type = $process.ExitCode.GetType().FullName
    $state.elapsed_seconds = ([DateTime]::UtcNow - $started).TotalSeconds
    $receipt = Join-Path $AttemptPath 'source_evaluation_receipt.json'
    if (Test-Path -LiteralPath $receipt) {
        $state.source_evaluation_receipt = [ordered]@{ path = $receipt; bytes = (Get-Item -LiteralPath $receipt).Length; sha256 = Get-Sha256 $receipt }
        $classification = (Get-Content -LiteralPath $receipt -Raw | ConvertFrom-Json).classification
        if ($process.ExitCode -eq 0 -and $classification -eq 'PASSED_SOURCE_EVALUATION_AWAITING_DIRECT_VISUAL_REVIEW') {
            $state.classification = 'PASSED_SOURCE_EVALUATION_AWAITING_DIRECT_VISUAL_REVIEW'
        } else { throw "Blender or receipt failed: exit=$($process.ExitCode), classification=$classification" }
    } else { throw 'Source evaluation receipt missing' }
}
catch {
    $state.error = "$($_.Exception.GetType().Name): $($_.Exception.Message)"
}
finally {
    $state.finished_at_utc = [DateTime]::UtcNow.ToString('o')
    try { Write-JsonAtomic $TerminalPath $state }
    catch {
        $line = ([ordered]@{at_utc=[DateTime]::UtcNow.ToString('o'); error="$($_.Exception.GetType().Name): $($_.Exception.Message)"} | ConvertTo-Json -Compress)
        Add-Content -LiteralPath $EmergencyPath -Value $line -Encoding UTF8
    }
}

if ($state.classification -eq 'PASSED_SOURCE_EVALUATION_AWAITING_DIRECT_VISUAL_REVIEW') { [Environment]::Exit([int]0) }
[Environment]::Exit([int]3)
