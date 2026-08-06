[CmdletBinding()]
param(
    [switch]$AuthorizeOfflineFreeze
)

$ErrorActionPreference = 'Stop'
$root = 'D:\Skyguard52'
$gate = 'PHASE4_M01_RECOVERY05_ENVIRONMENT_SOURCE_RECOVERY01_VALIDATION_RECOVERY01'
$attemptRoot = [System.IO.Path]::Combine(
    $root,
    'Saved',
    'BuildAttempts',
    $gate,
    'validation_attempt_01'
)
$reports = [System.IO.Path]::Combine($root, 'Saved', 'Reports')
$docs = [System.IO.Path]::Combine($root, 'Docs', 'AAA_Review')
$inventoryPath = [System.IO.Path]::Combine(
    $reports,
    $gate + '_ARTIFACT_INVENTORY.json'
)
$freezePath = [System.IO.Path]::Combine(
    $docs,
    $gate + '_FREEZE.json'
)
$sourcePath = [System.IO.Path]::Combine(
    $root,
    'Source',
    'Skyguard52',
    'SkyguardMission01EnvironmentDirector.cpp'
)

function Get-Sha256([string]$Path) {
    if (-not [System.IO.File]::Exists($Path)) {
        throw "Missing file: $Path"
    }
    $stream = $null
    $algorithm = $null
    try {
        $stream = New-Object System.IO.FileStream(
            $Path,
            [System.IO.FileMode]::Open,
            [System.IO.FileAccess]::Read,
            [System.IO.FileShare]::Read
        )
        $algorithm = [System.Security.Cryptography.SHA256]::Create()
        $digest = $algorithm.ComputeHash($stream)
        $builder = New-Object System.Text.StringBuilder
        foreach ($value in $digest) {
            [void]$builder.Append($value.ToString('x2'))
        }
        return $builder.ToString()
    } finally {
        if ($null -ne $algorithm) {
            $algorithm.Dispose()
        }
        if ($null -ne $stream) {
            $stream.Dispose()
        }
    }
}

function Get-Record([string]$Path) {
    $info = New-Object System.IO.FileInfo($Path)
    if (-not $info.Exists) {
        throw "Missing artifact: $Path"
    }
    return [ordered]@{
        file = $Path.Substring($root.Length + 1).Replace('\', '/')
        bytes = [long]$info.Length
        sha256 = Get-Sha256 $Path
    }
}

function Write-Json([string]$Path, $Value) {
    $encoding = New-Object System.Text.UTF8Encoding($false)
    $json = $Value | ConvertTo-Json -Depth 30
    [System.IO.File]::WriteAllText(
        $Path,
        $json + [Environment]::NewLine,
        $encoding
    )
}

function Get-HeavyProcesses {
    $names = @(
        'UnrealEditor',
        'UnrealEditor-Cmd',
        'ShaderCompileWorker',
        'blender',
        'AutomationTool',
        'UnrealBuildTool',
        'cl',
        'link',
        'dotnet'
    )
    $found = @()
    foreach ($process in [System.Diagnostics.Process]::GetProcesses()) {
        try {
            if ($names -contains $process.ProcessName) {
                $found += [ordered]@{
                    pid = [int]$process.Id
                    name = [string]$process.ProcessName
                }
            }
        } finally {
            $process.Dispose()
        }
    }
    return @($found)
}

if (-not $AuthorizeOfflineFreeze) {
    throw 'Offline freeze finalization requires -AuthorizeOfflineFreeze.'
}
if (
    [System.IO.File]::Exists($inventoryPath) -or
    [System.IO.File]::Exists($freezePath)
) {
    throw 'Freeze output namespace already exists.'
}
$heavy = @(Get-HeavyProcesses)
if ($heavy.Count -ne 0) {
    throw 'Heavy process detected during offline freeze finalization.'
}

$terminalPath = [System.IO.Path]::Combine(
    $reports,
    $gate + '_TERMINAL_EVIDENCE.json'
)
$readinessPath = [System.IO.Path]::Combine(
    $reports,
    $gate + '_READINESS.json'
)
$validationPath = [System.IO.Path]::Combine(
    $reports,
    $gate + '_VALIDATION_RESULT.json'
)
$terminal = Get-Content -LiteralPath $terminalPath -Raw | ConvertFrom-Json
$readiness = Get-Content -LiteralPath $readinessPath -Raw | ConvertFrom-Json
$validation = Get-Content -LiteralPath $validationPath -Raw | ConvertFrom-Json
$pass = 'PASSED_READY_FOR_EXPLICIT_M01_ENVIRONMENT_NATIVE_BUILD_AUTHORIZATION'
foreach ($classification in @(
    $terminal.classification,
    $readiness.classification,
    $validation.classification
)) {
    if ([string]$classification -cne $pass) {
        throw "Gate classification is not accepted: $classification"
    }
}
$source = Get-Record $sourcePath
if (
    $source.bytes -ne 15032 -or
    $source.sha256 -cne
        '73e736b088dd77dfaed42081bd988094d6743057175626db01a1fb9a92ceec44'
) {
    throw 'Current source no longer matches the accepted validation authority.'
}

$artifactPaths = @(
    [System.IO.Path]::Combine(
        $docs,
        $gate + '_CONTRACT.json'
    ),
    [System.IO.Path]::Combine(
        $root,
        'Scripts',
        'validate_phase4_m01_recovery05_environment_source_recovery01_validation_recovery01.ps1'
    ),
    [System.IO.Path]::Combine(
        $root,
        'Scripts',
        'finalize_phase4_m01_recovery05_environment_source_validation_recovery01.ps1'
    ),
    [System.IO.Path]::Combine(
        $docs,
        'PHASE1_8_COMPLETION_AUDIT_ADDENDUM_PHASE4_RECOVERY05_ENVIRONMENT_SOURCE_VALIDATION_RECOVERY01_2026-08-04.md'
    ),
    [System.IO.Path]::Combine(
        $docs,
        'M01_PRODUCTION_VERTICAL_SLICE_ACCEPTANCE_MATRIX_ADDENDUM_PHASE4_RECOVERY05_ENVIRONMENT_SOURCE_VALIDATION_RECOVERY01_2026-08-04.md'
    ),
    [System.IO.Path]::Combine(
        $docs,
        'SKYGUARD52_AAA_PRODUCTION_DASHBOARD_GATE1_2026-08-04.md'
    ),
    $sourcePath
)
$artifactPaths += @(
    [System.IO.Directory]::EnumerateFiles(
        $attemptRoot,
        '*',
        [System.IO.SearchOption]::AllDirectories
    )
)
$artifactPaths += @(
    [System.IO.Directory]::EnumerateFiles(
        $reports,
        $gate + '_*.json',
        [System.IO.SearchOption]::TopDirectoryOnly
    )
)
$uniquePaths = @($artifactPaths | Sort-Object -Unique)
$records = @()
foreach ($path in $uniquePaths) {
    $records += Get-Record $path
}
$inventory = [ordered]@{
    schema = 'skyguard.phase4.m01-recovery05-environment-source-validation-recovery01-artifact-inventory.v1'
    created_utc = [DateTime]::UtcNow.ToString('o')
    classification = $pass
    artifact_count = $records.Count
    artifacts = @($records)
    source_mutation_performed = $false
    compile_launched = $false
    unreal_launched = $false
    blender_launched = $false
    retry_count = 0
}
Write-Json $inventoryPath $inventory

$records += Get-Record $inventoryPath
$freeze = [ordered]@{
    schema = 'skyguard.phase4.m01-recovery05-environment-source-recovery01-validation-recovery01-freeze.v1'
    created_utc = [DateTime]::UtcNow.ToString('o')
    classification = $pass
    summary = 'The current Mission 1 environment source is byte-identical to the preserved validated candidate and differs from the immutable base by exactly one authorized mobility line. Prior freezes are preserved. No source mutation, build, Unreal, Blender, or retry occurred.'
    source = $source
    comparison = [ordered]@{
        sha256_and_byte_count = 'PASS'
        structural_equality_comparer = 'PASS'
        unsupported_sequence_equal_used = $false
        exact_added_lines = 1
        exact_removed_lines = 0
        exact_other_changed_lines = 0
    }
    failed_namespace_reused = $false
    source_mutation_performed = $false
    compile_launched = $false
    unreal_launched = $false
    blender_launched = $false
    automatic_retry = $false
    frozen_files = @($records)
    next_gate = 'EXPLICIT_M01_ENVIRONMENT_NATIVE_BUILD_AUTHORIZATION_REQUIRED'
}
Write-Json $freezePath $freeze

[ordered]@{
    classification = $pass
    inventory = Get-Record $inventoryPath
    freeze = Get-Record $freezePath
    artifact_count = $records.Count
    heavy_processes = @($heavy)
} | ConvertTo-Json -Depth 6
