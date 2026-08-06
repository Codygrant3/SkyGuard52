[CmdletBinding()]
param(
    [switch]$AuthorizeSingleRecovery04OfflineAudit
)

$ErrorActionPreference = 'Stop'
$projectRoot = 'D:\Skyguard52'
$audit = Join-Path $projectRoot 'Scripts\audit_skyguard_phase4_m01_landscape_attempt07_recovery04.py'

if (-not $AuthorizeSingleRecovery04OfflineAudit) {
    throw 'Recovery04 requires -AuthorizeSingleRecovery04OfflineAudit.'
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

& python $audit --authorize-single-recovery04-offline-audit
if ($LASTEXITCODE -ne 0) {
    throw "Recovery04 offline audit failed with exit code $LASTEXITCODE."
}
