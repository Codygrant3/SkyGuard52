[CmdletBinding()]
param(
    [switch]$AuthorizeSingleRecoveryTinyProof,
    [int]$BuildTimeoutSeconds = 900,
    [int]$AuthorTimeoutSeconds = 240,
    [int]$ProofTimeoutSeconds = 240
)

$ErrorActionPreference = "Stop"
$root = "D:\Skyguard52"
$supervisor = Join-Path $root (
    "Scripts\supervise_skyguard_phase4_m01_landscape_visible_" +
    "attempt07_recovery01.py"
)

if (-not $AuthorizeSingleRecoveryTinyProof) {
    throw (
        "Attempt07 Recovery01 is offline-only until the exact " +
        "-AuthorizeSingleRecoveryTinyProof switch is supplied."
    )
}

if (-not (Test-Path -LiteralPath $supervisor -PathType Leaf)) {
    throw "Recovery01 supervisor is missing: $supervisor"
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
    --authorize-single-recovery-tiny-proof `
    --build-timeout $BuildTimeoutSeconds `
    --author-timeout $AuthorTimeoutSeconds `
    --proof-timeout $ProofTimeoutSeconds
if ($LASTEXITCODE -ne 0) {
    throw "Attempt07 Recovery01 supervisor failed with $LASTEXITCODE"
}
