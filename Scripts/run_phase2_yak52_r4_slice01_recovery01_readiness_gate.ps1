[CmdletBinding()]
param(
    [string]$ProjectRoot = "D:\Skyguard52"
)

$ErrorActionPreference = "Stop"
$root = (Resolve-Path -LiteralPath $ProjectRoot).Path
$authoring = Join-Path $root "Scripts\blender_phase2_yak52_r4_slice01_recovery01.py"
$verifier = Join-Path $root "Scripts\verify_phase2_yak52_r4_slice01_recovery01_readiness.py"
$tests = Join-Path $root "Scripts\tests\test_phase2_yak52_r4_slice01_recovery01_readiness.py"

function Get-EngineProcessIds {
    $names = @("blender", "UnrealEditor", "UnrealEditor-Cmd", "UE4Editor", "UE5Editor")
    @(
        Get-Process -ErrorAction SilentlyContinue |
            Where-Object { $names -contains $_.ProcessName } |
            Select-Object -ExpandProperty Id
    )
}

$before = Get-EngineProcessIds

python -m py_compile $authoring $verifier $tests
if ($LASTEXITCODE -ne 0) {
    throw "Recovery01 Python compilation failed."
}

python $verifier --root $root --no-write
if ($LASTEXITCODE -ne 0) {
    throw "Recovery01 offline readiness validation failed."
}

python -m unittest $tests -v
if ($LASTEXITCODE -ne 0) {
    throw "Recovery01 mutation tests failed."
}

python $verifier --root $root
if ($LASTEXITCODE -ne 0) {
    throw "Recovery01 immutable readiness receipt failed."
}

$after = Get-EngineProcessIds
$newEngineProcesses = @($after | Where-Object { $_ -notin $before })
if ($newEngineProcesses.Count -ne 0) {
    throw "An engine process appeared during the offline gate: $($newEngineProcesses -join ', ')"
}

[ordered]@{
    status = "PASS_RECOVERY01_READY_NOT_RUN"
    project_root = $root
    engine_processes_before = @($before)
    engine_processes_after = @($after)
    engine_processes_launched_by_gate = @($newEngineProcesses)
    blender_launched_by_gate = $false
    unreal_launched_by_gate = $false
    production_started = $false
} | ConvertTo-Json -Depth 4
