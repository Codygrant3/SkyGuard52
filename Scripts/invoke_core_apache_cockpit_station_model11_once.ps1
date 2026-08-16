param(
    [switch]$ExecuteOnce,
    [switch]$OfflineContractTest
)

$ErrorActionPreference = 'Stop'
$Root = 'D:\Skyguard52'
$AssetId = 'core-apache-cockpit-station-model11'
$CyclePath = Join-Path $Root 'Scripts\skyguard_production_cycle.py'
$StandingAuthority = Join-Path $Root 'Production\standing_heavy_process_authorization.json'

if ($ExecuteOnce -and $OfflineContractTest) {
    [Console]::Error.WriteLine('Execution and offline modes are mutually exclusive.')
    [Environment]::Exit([int]3)
}
if (-not (Test-Path -LiteralPath $CyclePath -PathType Leaf)) {
    [Console]::Error.WriteLine('Production cycle controller is missing.')
    [Environment]::Exit([int]4)
}
if (-not (Test-Path -LiteralPath $StandingAuthority -PathType Leaf)) {
    [Console]::Error.WriteLine('Standing Blender and Unreal authorization is missing.')
    [Environment]::Exit([int]5)
}
$authority = Get-Content -Raw -LiteralPath $StandingAuthority | ConvertFrom-Json
if ($authority.status -ne 'ACTIVE' -or
    $authority.canonical_project_root -ne $Root -or
    $authority.scope.blender -ne $true -or
    $authority.execution_policy.per_run_user_authorization_required -ne $false -or
    $authority.execution_policy.one_heavy_process_at_a_time -ne $true -or
    [int]$authority.execution_policy.automatic_retry_count -ne 0 -or
    $authority.execution_policy.failed_namespace_reuse -ne $false) {
    [Console]::Error.WriteLine('Standing authorization policy is not valid for governed execution.')
    [Environment]::Exit([int]6)
}
if ($OfflineContractTest) {
    & python $CyclePath audit $AssetId
    [Environment]::Exit([int]$LASTEXITCODE)
}
if (-not $ExecuteOnce) {
    [Console]::Error.WriteLine('Mechanical -ExecuteOnce guard is required; standing authorization supplies user consent.')
    [Environment]::Exit([int]2)
}
& python $CyclePath run $AssetId
[Environment]::Exit([int]$LASTEXITCODE)
