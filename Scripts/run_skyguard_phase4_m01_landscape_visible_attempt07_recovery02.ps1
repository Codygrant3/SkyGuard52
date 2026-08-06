[CmdletBinding()]
param(
    [switch]$AuthorizeSingleRecovery02TinyProof,
    [int]$BuildTimeoutSeconds = 900,
    [int]$ProofTimeoutSeconds = 180
)

$ErrorActionPreference = "Stop"
$root = "D:\Skyguard52"
$supervisor = Join-Path $root (
    "Scripts\supervise_skyguard_phase4_m01_landscape_visible_" +
    "attempt07_recovery02.py"
)

if (-not $AuthorizeSingleRecovery02TinyProof) {
    throw (
        "Attempt07 Recovery02 is offline-only until the exact " +
        "-AuthorizeSingleRecovery02TinyProof switch is supplied."
    )
}

if (-not (Test-Path -LiteralPath $supervisor -PathType Leaf)) {
    throw "Recovery02 supervisor is missing: $supervisor"
}

$heavy = Get-Process -ErrorAction SilentlyContinue | Where-Object {
    $_.ProcessName -in @(
        "UnrealEditor",
        "UnrealEditor-Cmd",
        "UnrealBuildTool",
        "blender"
    )
}
if ($heavy) {
    throw (
        "Exclusive heavy lane is occupied: " +
        (($heavy | Select-Object -ExpandProperty ProcessName) -join ", ")
    )
}

& python $supervisor `
    --authorize-single-recovery02-tiny-proof `
    --build-timeout $BuildTimeoutSeconds `
    --proof-timeout $ProofTimeoutSeconds
if ($LASTEXITCODE -ne 0) {
    throw "Attempt07 Recovery02 supervisor failed with $LASTEXITCODE"
}
