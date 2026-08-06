[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$CompileActivationPath,

    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[0-9A-Fa-f]{64}$')]
    [string]$CompileActivationSha256,

    [switch]$AuthorizeSingleRecovery03TinyProof,

    [ValidateRange(120, 300)]
    [int]$ProofTimeoutSeconds = 180
)

$ErrorActionPreference = 'Stop'
$projectRoot = 'D:\Skyguard52'
$supervisor = Join-Path $projectRoot 'Scripts\supervise_skyguard_phase4_m01_landscape_visible_attempt07_recovery03.py'

if (-not $AuthorizeSingleRecovery03TinyProof) {
    throw 'Recovery03 requires -AuthorizeSingleRecovery03TinyProof.'
}

$activation = (Resolve-Path -LiteralPath $CompileActivationPath).Path
$observedHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $activation).Hash.ToLowerInvariant()
$expectedHash = $CompileActivationSha256.ToLowerInvariant()
if ($observedHash -ne $expectedHash) {
    throw "Compile activation SHA256 mismatch. Expected $expectedHash, observed $observedHash."
}

$heavyNames = @(
    'UnrealEditor',
    'UnrealEditor-Cmd',
    'UnrealBuildTool',
    'blender'
)
$activeHeavy = Get-Process -ErrorAction SilentlyContinue |
    Where-Object { $heavyNames -contains $_.ProcessName }
if ($activeHeavy) {
    $descriptions = $activeHeavy |
        ForEach-Object { '{0}({1})' -f $_.ProcessName, $_.Id }
    throw ('Exclusive heavy lane is not free: ' + ($descriptions -join ', '))
}

& python $supervisor `
    --project-root $projectRoot `
    --unreal-root 'D:\UE_5.8' `
    --compile-activation $activation `
    --compile-activation-sha256 $expectedHash `
    --proof-timeout $ProofTimeoutSeconds `
    --authorize-single-recovery03-tiny-proof

if ($LASTEXITCODE -ne 0) {
    throw "Recovery03 proof-only supervisor failed with exit code $LASTEXITCODE."
}
