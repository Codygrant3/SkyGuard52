param(
    [switch]$AuthorizeSingleBlender,
    [switch]$OfflineContractTest
)

$ErrorActionPreference = 'Stop'
$Root = 'D:\Skyguard52'
$AssetId = 'm01-coastal-corridor-correction06-recovery01-unrealready01'
$CyclePath = Join-Path $Root 'Scripts\skyguard_production_cycle.py'
$StandingAuthority = Join-Path $Root 'Production\standing_heavy_process_authorization.json'

if ($AuthorizeSingleBlender -and $OfflineContractTest) {
    [Console]::Error.WriteLine('Authorized and offline modes are mutually exclusive.')
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
    $authority.execution_policy.per_run_user_authorization_required -ne $false -or
    $authority.execution_policy.one_heavy_process_at_a_time -ne $true -or
    [int]$authority.execution_policy.automatic_retry_count -ne 0) {
    [Console]::Error.WriteLine('Standing authorization policy is not valid for governed execution.')
    [Environment]::Exit([int]6)
}

if ($OfflineContractTest) {
    & python $CyclePath audit $AssetId
    [Environment]::Exit([int]$LASTEXITCODE)
}

if (-not $AuthorizeSingleBlender) {
    [Console]::Error.WriteLine('Mechanical -AuthorizeSingleBlender guard is required; standing user authorization supplies authority.')
    [Environment]::Exit([int]2)
}

& python $CyclePath run $AssetId
[Environment]::Exit([int]$LASTEXITCODE)
