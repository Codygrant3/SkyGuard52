[CmdletBinding()]
param(
    [string]$ProjectRoot = "D:\Skyguard52",
    [string]$UnrealRoot = "D:\UE_5.8",
    [switch]$AuthorizeSingleRecoveryRun
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

if (-not $AuthorizeSingleRecoveryRun) {
    throw "Recovery01 requires explicit -AuthorizeSingleRecoveryRun"
}

$Supervisor = Join-Path $ProjectRoot `
    "Scripts\supervise_skyguard_phase4_m01_landscape_visible_attempt06_recovery01.py"
if (-not (Test-Path -LiteralPath $Supervisor -PathType Leaf)) {
    throw "Recovery01 supervisor missing: $Supervisor"
}

& python $Supervisor `
    --project-root $ProjectRoot `
    --unreal-root $UnrealRoot `
    --authorize-single-recovery-run
if ($LASTEXITCODE -ne 0) {
    throw "Recovery01 supervisor failed with exit code $LASTEXITCODE"
}
