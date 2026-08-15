param(
    [switch]$AuthorizeSingleUnreal,
    [switch]$OfflineContractTest
)

$ErrorActionPreference = 'Stop'
$Original = 'D:\Skyguard52\Scripts\ToolchainWave08\environment_visible_kit_presentation_refinement01\invoke_m01_visible_environment_kit_presentation_refinement01_once.ps1'
$ExpectedOriginal = 'aec13f7119f8567b4712c42bad72ba0e69f949c87995f838aebf15f65fae94ad'

function Get-Sha256([string]$Path) {
    $stream = $null
    $algorithm = $null
    try {
        $stream = [IO.File]::OpenRead($Path)
        $algorithm = [Security.Cryptography.SHA256]::Create()
        return ([BitConverter]::ToString($algorithm.ComputeHash($stream))).Replace('-', '').ToLowerInvariant()
    }
    finally {
        if ($null -ne $algorithm) { $algorithm.Dispose() }
        if ($null -ne $stream) { $stream.Dispose() }
    }
}

if ((Get-Sha256 $Original) -ne $ExpectedOriginal) {
    throw 'Frozen PresentationRefinement01 supervisor hash mismatch.'
}

$Source = [IO.File]::ReadAllText($Original)
$ParameterPattern = '(?s)^param\(.*?\)\r?\n'
if ([regex]::Matches($Source, $ParameterPattern).Count -ne 1) {
    throw 'Expected one leading param block.'
}
$Source = [regex]::Replace($Source, $ParameterPattern, '', 1)

$Replacements = @(
    @('environment_visible_kit_presentation_refinement01\author_m01_visible_environment_kit_presentation_refinement01.py', 'environment_visible_kit_presentation_refinement01_recovery01\author_m01_visible_environment_kit_presentation_refinement01_recovery01.py'),
    @('environment_visible_kit_presentation_refinement01\verify_m01_visible_environment_kit_presentation_refinement01_offline.py', 'environment_visible_kit_presentation_refinement01_recovery01\verify_m01_visible_environment_kit_presentation_refinement01_recovery01_offline.py'),
    @('M01VisibleEnvironmentPresentationRefinement01\execution_contract.json', 'M01VisibleEnvironmentPresentationRefinement01Recovery01\execution_contract.json'),
    @('Lvl_M01_VisibleEnvironmentKit02_PresentationRefinement01.umap', 'Lvl_M01_VisibleEnvironmentKit02_PresentationRefinement01_Recovery01.umap'),
    @('M01_VISIBLE_ENVIRONMENT_PRESENTATION_REFINEMENT01\attempt_01', 'M01_VISIBLE_ENVIRONMENT_PRESENTATION_REFINEMENT01_RECOVERY01\attempt_01'),
    @('M01_VISIBLE_ENVIRONMENT_PRESENTATION_REFINEMENT01_TERMINAL_SUPERVISOR', 'M01_VISIBLE_ENVIRONMENT_PRESENTATION_REFINEMENT01_RECOVERY01_TERMINAL_SUPERVISOR'),
    @('M01_VISIBLE_ENVIRONMENT_PRESENTATION_REFINEMENT01_EMERGENCY_RECEIPT', 'M01_VISIBLE_ENVIRONMENT_PRESENTATION_REFINEMENT01_RECOVERY01_EMERGENCY_RECEIPT'),
    @('2899658124ce2dbf66d6ac15551b6213745184df02958e835e5bc208d3785d7c', 'f72af25ed538ca68d61abffc529e96f553fd41db296806cb3dc01c7b018a95ce'),
    @('bb0dd6f908706465dcd815764bfabce31fcf60b7a62c95cb97595377d8e6bc51', 'cdcea81dceb51608e832a560a35e80b0f71c08e0a598794317d09ffe8612641f'),
    @('5c4de841e32ff2dc974f10ec1872e266e0e5f9527c74ce7f71de62b3d38fdc91', '35aae2550bc37807fa1ab5c50eb10c12877d16e86cf798596455471bb7943c0d'),
    @('PASSED_M01_VISIBLE_ENVIRONMENT_PRESENTATION_REFINEMENT01_AUTOMATIC', 'PASSED_M01_VISIBLE_ENVIRONMENT_PRESENTATION_REFINEMENT01_RECOVERY01_AUTOMATIC'),
    @('PASSED_M01_VISIBLE_ENVIRONMENT_PRESENTATION_REFINEMENT01_READY_FOR_MAPPED_VISUAL_PROOF', 'PASSED_M01_VISIBLE_ENVIRONMENT_PRESENTATION_REFINEMENT01_RECOVERY01_READY_FOR_MAPPED_VISUAL_PROOF'),
    @('presentation-refinement01.supervisor.v1', 'presentation-refinement01-recovery01.supervisor.v1')
)

foreach ($pair in $Replacements) {
    $old = [string]$pair[0]
    $new = [string]$pair[1]
    if ([regex]::Matches($Source, [regex]::Escape($old)).Count -ne 1) {
        throw "Recovery01 supervisor binding count changed: $old"
    }
    $Source = $Source.Replace($old, $new)
}

$FailureVariable = "`$FailedPresentationFreeze = Join-Path `$Root 'Docs\AAA_Review\M01_VISIBLE_ENVIRONMENT_PRESENTATION_REFINEMENT01_ATTEMPT01_TERMINAL_FREEZE.json'`n"
$VariableAnchor = "`$FailedVisualFreeze = Join-Path `$Root 'Docs\AAA_Review\M01_VISIBLE_ENVIRONMENT_KIT_MAP_VISUAL_REMEDIATION01_RECOVERY01_VISUAL_PROOF01_ATTEMPT01_TERMINAL_FREEZE.json'`n"
if (-not $Source.Contains($VariableAnchor)) { throw 'Failed-attempt variable anchor absent.' }
$Source = $Source.Replace($VariableAnchor, $VariableAnchor + $FailureVariable)

$ExpectedAnchor = "`$Expected = [ordered]@{`n"
$FailureEntry = "    `$FailedPresentationFreeze = 'aceb486483b51a0a41347ad1fe0b8753f5df61fcf6173dc856821ca7a41115a2'`n"
if (-not $Source.Contains($ExpectedAnchor)) { throw 'Expected-authority anchor absent.' }
$Source = $Source.Replace($ExpectedAnchor, $ExpectedAnchor + $FailureEntry)

if ($Source.Contains('M01_VISIBLE_ENVIRONMENT_PRESENTATION_REFINEMENT01\attempt_01')) {
    throw 'Recovery01 supervisor retains failed attempt namespace.'
}
if ($Source.Contains('Lvl_M01_VisibleEnvironmentKit02_PresentationRefinement01.umap')) {
    throw 'Recovery01 supervisor retains failed output-map namespace.'
}

Invoke-Expression $Source
