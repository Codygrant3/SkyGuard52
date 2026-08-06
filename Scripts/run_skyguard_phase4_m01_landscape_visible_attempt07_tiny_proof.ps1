[CmdletBinding()]
param(
    [string]$ProjectRoot = "D:\Skyguard52",
    [string]$UnrealRoot = "D:\UE_5.8",
    [switch]$AuthorizeSingleTinyProof
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

if (-not $AuthorizeSingleTinyProof) {
    throw "Attempt07 requires explicit -AuthorizeSingleTinyProof"
}

$Supervisor = Join-Path $ProjectRoot `
    "Scripts\supervise_skyguard_phase4_m01_landscape_visible_attempt07_tiny_proof.py"
if (-not (Test-Path -LiteralPath $Supervisor -PathType Leaf)) {
    throw "Attempt07 supervisor missing: $Supervisor"
}

& python $Supervisor `
    --project-root $ProjectRoot `
    --unreal-root $UnrealRoot `
    --authorize-single-tiny-proof
if ($LASTEXITCODE -ne 0) {
    throw "Attempt07 tiny proof failed with exit code $LASTEXITCODE"
}
