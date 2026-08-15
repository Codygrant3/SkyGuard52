[CmdletBinding()]
param(
    [switch]$AuthorizeSingleUnrealProof,
    [switch]$OfflineContractTest,
    [string]$OfflineEvidenceRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$source = 'D:\Skyguard52\Scripts\ToolchainWave08\environment_realism_stack_visual_proof01\invoke_m01_environment_realism_stack_visual_proof01_once.ps1'
$expectedBytes = 4773
$expectedSha256 = '21fc39e3db4a9dd97ab8a21ed5677d9d690d8ab2134556d1dee1436bdd241970'

function Get-LowerSha256([string]$Path) {
    $stream = $null; $algorithm = $null
    try {
        $stream = [System.IO.File]::Open($Path, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::Read)
        $algorithm = [System.Security.Cryptography.SHA256]::Create()
        return ([System.BitConverter]::ToString($algorithm.ComputeHash($stream))).Replace('-', '').ToLowerInvariant()
    }
    finally {
        if ($null -ne $algorithm) { $algorithm.Dispose() }
        if ($null -ne $stream) { $stream.Dispose() }
    }
}

if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { throw "Frozen Visual Proof01 supervisor wrapper is missing: $source" }
$item = Get-Item -LiteralPath $source
if ($item.Length -ne $expectedBytes -or (Get-LowerSha256 $source) -ne $expectedSha256) { throw 'Frozen Visual Proof01 supervisor wrapper changed' }

$transformed = Get-Content -LiteralPath $source -Raw
$replacements = @(
    @('PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_ENVIRONMENT_REALISM_STACK_VISUAL_PROOF01_EXECUTION', 'PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_VISIBLE_ENVIRONMENT_KIT_MAP_VISUAL_REMEDIATION01_RECOVERY01_VISUAL_PROOF01_EXECUTION'),
    @('M01_ENVIRONMENT_REALISM_STACK_VISUAL_PROOF01', 'M01_VISIBLE_ENVIRONMENT_KIT_MAP_VISUAL_REMEDIATION01_RECOVERY01_VISUAL_PROOF01'),
    @('M01-ENVIRONMENT-REALISM-STACK-VISUAL-PROOF01', 'M01-VISIBLE-ENVIRONMENT-KIT-MAP-VISUAL-REMEDIATION01-RECOVERY01-VISUAL-PROOF01'),
    @('Lvl_M01_T08_EnvironmentRealismStack01_Recovery02', 'Lvl_M01_VisibleEnvironmentKit02_VisualRemediation01_Recovery01'),
    @('M01EnvironmentRealismStackVisualProof01.csv', 'M01VisibleEnvironmentKitMapVisualRemediation01Recovery01VisualProof01.csv'),
    @('capture_m01_environment_realism_stack_visual_proof01.py', 'capture_m01_visible_environment_kit_map_visual_remediation01_recovery01_visual_proof01.py'),
    @('adjudicate_m01_environment_realism_stack_visual_proof01_once.py', 'adjudicate_m01_visible_environment_kit_map_visual_remediation01_recovery01_visual_proof01_once.py'),
    @('m01_environment_realism_stack_visual_proof01', 'm01_visible_environment_kit_map_visual_remediation01_recovery01_visual_proof01'),
    @('environment_realism_stack_visual_proof01', 'environment_visible_kit_map_visual_remediation01_recovery01_visual_proof01'),
    @('visual-proof01', 'visible-environment-kit-map-visual-remediation01-recovery01-visual-proof01')
)
foreach ($pair in $replacements) {
    if (-not $transformed.Contains($pair[0])) { throw "Remediated-map supervisor binding token is absent: $($pair[0])" }
    $transformed = $transformed.Replace($pair[0], $pair[1])
}

$mapReplaceNeedle = '$transformed = $transformed.Replace($oldMap, $newMap)'
$mapReplaceValue = $mapReplaceNeedle + [Environment]::NewLine + '$transformed = $transformed.Replace(''/Game/ToolchainWave08/Environment/'', ''/Game/M01/'')' + [Environment]::NewLine + '$transformed = $transformed.Replace(''$timeoutSeconds = 900'', ''$timeoutSeconds = 1200'')' + [Environment]::NewLine + '$transformed = $transformed.Replace(''if ($timeoutSeconds -ne 900)'', ''if ($timeoutSeconds -ne 1200)'')'
if (-not $transformed.Contains($mapReplaceNeedle)) { throw 'Map-directory transformation insertion point is missing' }
$transformed = $transformed.Replace($mapReplaceNeedle, $mapReplaceValue)

$badAtomic = "if (Test-Path -LiteralPath ```$Path) { [System.IO.File]::Replace(```$temporary, ```$Path, ```$null) } else { [System.IO.File]::Move(```$temporary, ```$Path) }"
$goodAtomic = "if (Test-Path -LiteralPath ```$Path) { ```$backup = ```$Path + '.atomic-backup'; if (Test-Path -LiteralPath ```$backup) { throw ('Atomic backup exists: ' + ```$backup) }; [System.IO.File]::Replace(```$temporary, ```$Path, ```$backup); [System.IO.File]::Delete(```$backup) } else { [System.IO.File]::Move(```$temporary, ```$Path) }"
if (-not $transformed.Contains($badAtomic)) { throw 'Known null-backup atomic writer target is missing' }
$transformed = $transformed.Replace($badAtomic, $goodAtomic)
foreach ($pair in $replacements) {
    if ($pair[0] -ne 'visual-proof01' -and $transformed.Contains($pair[0])) { throw "Remediated-map supervisor retained stale token: $($pair[0])" }
}
foreach ($required in @(
    'M01_VISIBLE_ENVIRONMENT_KIT_MAP_VISUAL_REMEDIATION01_RECOVERY01_VISUAL_PROOF01',
    'M01-VISIBLE-ENVIRONMENT-KIT-MAP-VISUAL-REMEDIATION01-RECOVERY01-VISUAL-PROOF01',
    'Lvl_M01_VisibleEnvironmentKit02_VisualRemediation01_Recovery01',
    'M01VisibleEnvironmentKitMapVisualRemediation01Recovery01VisualProof01.csv',
    'environment_visible_kit_map_visual_remediation01_recovery01_visual_proof01',
    '/Game/M01/',
    '$timeoutSeconds = 1200'
)) {
    if (-not $transformed.Contains($required)) { throw "Remediated-map supervisor output binding is missing: $required" }
}
if ($transformed.Contains('[System.IO.File]::Replace(`$temporary, `$Path, `$null)')) { throw 'Null-backup File.Replace survived correction' }
if ([regex]::Matches($transformed, [regex]::Escape('Start-Process -FilePath $editor')).Count -ne 1) { throw 'Transformed supervisor must contain exactly one Unreal launch path' }

$global:SkyguardTransformedSupervisorSource = $transformed
$scriptBlock = [ScriptBlock]::Create($transformed)
$arguments = @{}
if ($AuthorizeSingleUnrealProof) { $arguments['AuthorizeSingleUnrealProof'] = $true }
if ($OfflineContractTest) { $arguments['OfflineContractTest'] = $true }
if ($OfflineEvidenceRoot) { $arguments['OfflineEvidenceRoot'] = $OfflineEvidenceRoot }
& $scriptBlock @arguments
