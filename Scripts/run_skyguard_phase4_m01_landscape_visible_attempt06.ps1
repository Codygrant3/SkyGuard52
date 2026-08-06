[CmdletBinding()]
param(
    [string]$ProjectRoot = "D:\Skyguard52",
    [string]$UnrealRoot = "D:\UE_5.8",
    [switch]$AuthorizeSingleRun
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

if (-not $AuthorizeSingleRun) {
    throw "Attempt06 requires explicit -AuthorizeSingleRun"
}

$Supervisor = Join-Path $ProjectRoot `
    "Scripts\supervise_skyguard_phase4_m01_landscape_visible_attempt06.py"
if (-not (Test-Path -LiteralPath $Supervisor -PathType Leaf)) {
    throw "Attempt06 supervisor missing: $Supervisor"
}

$Arguments = @(
    $Supervisor,
    "--project-root", $ProjectRoot,
    "--unreal-root", $UnrealRoot,
    "--authorize-single-run"
)
& python @Arguments
if ($LASTEXITCODE -ne 0) {
    throw "Attempt06 supervisor failed with exit code $LASTEXITCODE"
}
