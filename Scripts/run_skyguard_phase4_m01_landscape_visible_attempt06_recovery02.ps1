[CmdletBinding()]
param(
    [string]$ProjectRoot = "D:\Skyguard52",
    [switch]$AuthorizeOfflineRecoveryRun
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

if (-not $AuthorizeOfflineRecoveryRun) {
    throw "Recovery02 requires explicit -AuthorizeOfflineRecoveryRun"
}

$Supervisor = Join-Path $ProjectRoot `
    "Scripts\supervise_skyguard_phase4_m01_landscape_visible_attempt06_recovery02.py"
if (-not (Test-Path -LiteralPath $Supervisor -PathType Leaf)) {
    throw "Recovery02 supervisor missing: $Supervisor"
}

& python $Supervisor `
    --project-root $ProjectRoot `
    --authorize-offline-recovery-run
if ($LASTEXITCODE -ne 0) {
    throw "Recovery02 offline supervisor failed with exit code $LASTEXITCODE"
}
