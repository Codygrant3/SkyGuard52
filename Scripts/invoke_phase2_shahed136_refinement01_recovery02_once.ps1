param(
    [switch]$OfflineContractTest,
    [switch]$AuthorizeSingleBlender
)

$ErrorActionPreference = 'Stop'
$Root = 'D:\Skyguard52'
$AssetId = 'core-shahed136'
$CyclePath = Join-Path $Root 'Scripts\skyguard_production_cycle.py'
$WorkerPath = Join-Path $Root 'Scripts\Workers\worker_core_shahed136_refinement01_recovery02.py'

if ($OfflineContractTest -and $AuthorizeSingleBlender) {
    [Console]::Error.WriteLine('Offline and authorized modes are mutually exclusive.')
    [Environment]::Exit([int]3)
}

if ($OfflineContractTest) {
    & python -m py_compile $WorkerPath $CyclePath
    if ($LASTEXITCODE -ne 0) { [Environment]::Exit([int]$LASTEXITCODE) }
    & python $CyclePath audit $AssetId
    [Environment]::Exit([int]$LASTEXITCODE)
}

if (-not $AuthorizeSingleBlender) {
    [Console]::Error.WriteLine('Mechanical one-shot guard was not supplied.')
    [Environment]::Exit([int]2)
}

& python $CyclePath run $AssetId
[Environment]::Exit([int]$LASTEXITCODE)
