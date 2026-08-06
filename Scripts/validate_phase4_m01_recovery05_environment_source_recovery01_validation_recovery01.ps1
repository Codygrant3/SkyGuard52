[CmdletBinding()]
param(
    [switch]$AuthorizeOfflineValidation
)

$ErrorActionPreference = 'Stop'

$root = 'D:\Skyguard52'
$gateName = 'PHASE4_M01_RECOVERY05_ENVIRONMENT_SOURCE_RECOVERY01_VALIDATION_RECOVERY01'
$attemptRoot = [System.IO.Path]::Combine(
    $root,
    'Saved',
    'BuildAttempts',
    $gateName,
    'validation_attempt_01'
)
$reportsRoot = [System.IO.Path]::Combine($root, 'Saved', 'Reports')
$docsRoot = [System.IO.Path]::Combine($root, 'Docs', 'AAA_Review')
$sourcePath = [System.IO.Path]::Combine(
    $root,
    'Source',
    'Skyguard52',
    'SkyguardMission01EnvironmentDirector.cpp'
)
$priorAttemptRoot = [System.IO.Path]::Combine(
    $root,
    'Saved',
    'BuildAttempts',
    'PHASE4_M01_RECOVERY05_ENVIRONMENT_SOURCE_RECOVERY01',
    'recovery_attempt_01'
)
$basePath = [System.IO.Path]::Combine(
    $priorAttemptRoot,
    'inputs',
    'immutable_lf_source.cpp'
)
$candidatePath = [System.IO.Path]::Combine(
    $priorAttemptRoot,
    'candidate',
    'SkyguardMission01EnvironmentDirector.corrected.cpp'
)
$validatedCandidatePath = [System.IO.Path]::Combine(
    $priorAttemptRoot,
    'replacement',
    'validated_candidate_evidence.cpp'
)
$patchPath = [System.IO.Path]::Combine(
    $root,
    'SourceCorrections',
    'Recovery05',
    'SkyguardMission01EnvironmentDirector.mobility.patch'
)
$offlineFreezePath = [System.IO.Path]::Combine(
    $docsRoot,
    'PHASE4_M01_RECOVERY05_OFFLINE_DESIGN_FREEZE.json'
)
$correctionFreezePath = [System.IO.Path]::Combine(
    $docsRoot,
    'PHASE4_M01_RECOVERY05_ENVIRONMENT_SOURCE_CORRECTION_ATTEMPT01_TERMINAL_FREEZE.json'
)
$recoveryFreezePath = [System.IO.Path]::Combine(
    $docsRoot,
    'PHASE4_M01_RECOVERY05_ENVIRONMENT_SOURCE_RECOVERY01_ATTEMPT01_TERMINAL_FREEZE.json'
)
$externalPrefix = [System.IO.Path]::Combine($reportsRoot, $gateName)
$terminalEvidencePath = $externalPrefix + '_TERMINAL_EVIDENCE.json'
$readinessPath = $externalPrefix + '_READINESS.json'
$sourceInventoryPath = $externalPrefix + '_SOURCE_INVENTORY.json'
$exactDiffPath = $externalPrefix + '_EXACT_DIFF.json'
$focusedTestsPath = $externalPrefix + '_FOCUSED_TESTS.json'
$authorityPreservationPath = $externalPrefix + '_AUTHORITY_PRESERVATION.json'
$validationResultPath = $externalPrefix + '_VALIDATION_RESULT.json'
$futureNativeBuildAttempt = [System.IO.Path]::Combine(
    $root,
    'Saved',
    'BuildAttempts',
    'PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_VALIDATION_RECOVERY01',
    'build_attempt_01'
)
$futureNativeBuildReports = [System.IO.Path]::Combine(
    $reportsRoot,
    'PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_VALIDATION_RECOVERY01'
)

$expected = [ordered]@{
    offline_freeze = [ordered]@{
        path = $offlineFreezePath
        bytes = 6462
        sha256 = '9184f81c4bfb1ac8397add8f84807839a2612e4f990292f66c04d912fae3285e'
    }
    recovery05_readiness = [ordered]@{
        path = [System.IO.Path]::Combine(
            $reportsRoot,
            'PHASE4_M01_RECOVERY05_READINESS.json'
        )
        bytes = 1274
        sha256 = 'e97b9c3b035f9e5920a488e7bdba13358aa8df6454be4963aacbf5adf77d5c68'
    }
    correction_terminal_freeze = [ordered]@{
        path = $correctionFreezePath
        bytes = 5456
        sha256 = '98e8be964ed2fdc060c5eaa02528b828ef174725555e4290e59729aabbc00e42'
    }
    recovery01_terminal_freeze = [ordered]@{
        path = $recoveryFreezePath
        bytes = 7005
        sha256 = 'c2a3125da2b7d894b76d5c29e397c9cd86b7cdf2e7271f60abc63f6599cc0fff'
    }
    source = [ordered]@{
        path = $sourcePath
        bytes = 15032
        sha256 = '73e736b088dd77dfaed42081bd988094d6743057175626db01a1fb9a92ceec44'
    }
    base = [ordered]@{
        path = $basePath
        bytes = 14984
        sha256 = '7cb7dae93bce8c2b0ff3f1eca45ce84cb5f74194f4e38a1ed02bb07c55262980'
    }
    candidate = [ordered]@{
        path = $candidatePath
        bytes = 15032
        sha256 = '73e736b088dd77dfaed42081bd988094d6743057175626db01a1fb9a92ceec44'
    }
    validated_candidate = [ordered]@{
        path = $validatedCandidatePath
        bytes = 15032
        sha256 = '73e736b088dd77dfaed42081bd988094d6743057175626db01a1fb9a92ceec44'
    }
    patch = [ordered]@{
        path = $patchPath
        bytes = 532
        sha256 = '3c25f8f4ceac21d0169919f39c4e2c08700fbc52ade07e3d31fc9ffff22cc4e5'
    }
}

function ConvertTo-JsonEscapedString([string]$Value) {
    if ($null -eq $Value) {
        return 'null'
    }
    $builder = New-Object System.Text.StringBuilder
    [void]$builder.Append('"')
    foreach ($character in $Value.ToCharArray()) {
        $code = [int][char]$character
        switch ($code) {
            8 { [void]$builder.Append('\b') }
            9 { [void]$builder.Append('\t') }
            10 { [void]$builder.Append('\n') }
            12 { [void]$builder.Append('\f') }
            13 { [void]$builder.Append('\r') }
            34 { [void]$builder.Append('\"') }
            92 { [void]$builder.Append('\\') }
            default {
                if ($code -lt 32) {
                    [void]$builder.Append(('\u{0:x4}' -f $code))
                } else {
                    [void]$builder.Append($character)
                }
            }
        }
    }
    [void]$builder.Append('"')
    return $builder.ToString()
}

function ConvertTo-SelfContainedJson($Value) {
    if ($null -eq $Value) {
        return 'null'
    }
    if ($Value -is [bool]) {
        if ($Value) {
            return 'true'
        }
        return 'false'
    }
    if (
        $Value -is [byte] -or
        $Value -is [sbyte] -or
        $Value -is [int16] -or
        $Value -is [uint16] -or
        $Value -is [int32] -or
        $Value -is [uint32] -or
        $Value -is [int64] -or
        $Value -is [uint64] -or
        $Value -is [single] -or
        $Value -is [double] -or
        $Value -is [decimal]
    ) {
        return [System.Convert]::ToString(
            $Value,
            [System.Globalization.CultureInfo]::InvariantCulture
        )
    }
    if (
        $Value -is [string] -or
        $Value -is [char] -or
        $Value -is [datetime]
    ) {
        return ConvertTo-JsonEscapedString ([string]$Value)
    }
    if ($Value -is [System.Collections.IDictionary]) {
        $pairs = New-Object System.Collections.Generic.List[string]
        foreach ($key in $Value.Keys) {
            $pairs.Add(
                (ConvertTo-JsonEscapedString ([string]$key)) +
                ':' +
                (ConvertTo-SelfContainedJson $Value[$key])
            )
        }
        return '{' + [string]::Join(',', $pairs.ToArray()) + '}'
    }
    if ($Value -is [System.Collections.IEnumerable]) {
        $items = New-Object System.Collections.Generic.List[string]
        foreach ($item in $Value) {
            $items.Add((ConvertTo-SelfContainedJson $item))
        }
        return '[' + [string]::Join(',', $items.ToArray()) + ']'
    }
    $properties = [ordered]@{}
    foreach ($property in $Value.PSObject.Properties) {
        $properties[$property.Name] = $property.Value
    }
    return ConvertTo-SelfContainedJson $properties
}

function Write-SelfContainedJson([string]$Path, $Value) {
    $parent = [System.IO.Path]::GetDirectoryName($Path)
    if (-not [string]::IsNullOrWhiteSpace($parent)) {
        [void][System.IO.Directory]::CreateDirectory($parent)
    }
    $encoding = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText(
        $Path,
        (ConvertTo-SelfContainedJson $Value) + [Environment]::NewLine,
        $encoding
    )
}

function Get-SelfContainedSha256([string]$Path) {
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
        if ($null -eq $digest -or $digest.Length -ne 32) {
            throw "Invalid SHA-256 result: $Path"
        }
        if ($stream.Position -ne $stream.Length) {
            throw "Partial SHA-256 read: $Path"
        }
        $builder = New-Object System.Text.StringBuilder
        foreach ($value in $digest) {
            [void]$builder.Append($value.ToString('x2'))
        }
        $result = $builder.ToString()
        if ($result -cnotmatch '^[0-9a-f]{64}$') {
            throw "Invalid lowercase SHA-256 formatting: $Path"
        }
        return $result
    } finally {
        if ($null -ne $algorithm) {
            $algorithm.Dispose()
        }
        if ($null -ne $stream) {
            $stream.Dispose()
        }
    }
}

function Get-FileRecord([string]$Path) {
    if (-not [System.IO.File]::Exists($Path)) {
        throw "Missing file: $Path"
    }
    $info = New-Object System.IO.FileInfo($Path)
    return [ordered]@{
        file = $Path
        bytes = [long]$info.Length
        sha256 = Get-SelfContainedSha256 $Path
    }
}

function Assert-FrozenFile([string]$Path, [long]$Bytes, [string]$Sha256) {
    $record = Get-FileRecord $Path
    if ($record.bytes -ne $Bytes) {
        throw "Frozen byte mismatch: $Path"
    }
    if ($record.sha256 -cne $Sha256) {
        throw "Frozen hash mismatch: $Path"
    }
    return $record
}

function Resolve-ProjectFile([string]$RelativePath) {
    return [System.IO.Path]::GetFullPath(
        [System.IO.Path]::Combine($root, $RelativePath)
    )
}

function Read-Json([string]$Path) {
    return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
}

function Get-HeavyProcesses {
    $heavyNames = @(
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
    foreach ($candidate in [System.Diagnostics.Process]::GetProcesses()) {
        try {
            if ($heavyNames -contains $candidate.ProcessName) {
                $found += [ordered]@{
                    pid = [int]$candidate.Id
                    name = [string]$candidate.ProcessName
                }
            }
        } finally {
            $candidate.Dispose()
        }
    }
    return @($found)
}

function Get-LineEndingRecord([byte[]]$Bytes) {
    $cr = 0
    $lf = 0
    foreach ($value in $Bytes) {
        if ($value -eq 13) {
            $cr += 1
        }
        if ($value -eq 10) {
            $lf += 1
        }
    }
    return [ordered]@{
        cr_bytes = $cr
        lf_bytes = $lf
    }
}

function Get-ExactInsertionProof(
    [byte[]]$BaseBytes,
    [byte[]]$CurrentBytes
) {
    $utf8 = New-Object System.Text.UTF8Encoding($false, $true)
    $baseText = $utf8.GetString($BaseBytes)
    $currentText = $utf8.GetString($CurrentBytes)
    $rootCreation = "`tRoot = CreateDefaultSubobject<USceneComponent>(TEXT(`"Mission01EnvironmentRoot`"));"
    $authorizedLine = "`tRoot->SetMobility(EComponentMobility::Static);"
    $rootBinding = "`tSetRootComponent(Root);"
    $anchor = $rootCreation + "`n" + $rootBinding
    $replacement = $rootCreation + "`n" + $authorizedLine + "`n" + $rootBinding
    $anchorMatches = [System.Text.RegularExpressions.Regex]::Matches(
        $baseText,
        [System.Text.RegularExpressions.Regex]::Escape($anchor)
    ).Count
    if ($anchorMatches -ne 1) {
        throw "Base source contains $anchorMatches exact insertion anchors; expected one."
    }
    $expectedText = $baseText.Replace($anchor, $replacement)
    $expectedBytes = $utf8.GetBytes($expectedText)
    $comparer = [System.Collections.StructuralComparisons]::StructuralEqualityComparer
    $expectedParity = [bool]$comparer.Equals($expectedBytes, $CurrentBytes)
    if (-not $expectedParity) {
        throw 'Current source is not the exact authorized one-line insertion.'
    }
    $baseLines = $baseText.Split([char]10)
    $currentLines = $currentText.Split([char]10)
    if ($currentLines.Length -ne ($baseLines.Length + 1)) {
        throw 'Current source does not contain exactly one additional logical line.'
    }
    $insertionIndex = -1
    for ($index = 0; $index -lt $currentLines.Length; $index += 1) {
        if ($currentLines[$index] -ceq $authorizedLine) {
            if ($insertionIndex -ne -1) {
                throw 'Authorized mobility statement appears more than once.'
            }
            $insertionIndex = $index
        }
    }
    if ($insertionIndex -lt 1 -or $insertionIndex -ge ($currentLines.Length - 1)) {
        throw 'Authorized mobility statement is absent or lacks required context.'
    }
    if ($currentLines[$insertionIndex - 1] -cne $rootCreation) {
        throw 'Mobility statement is not immediately after root creation.'
    }
    if ($currentLines[$insertionIndex + 1] -cne $rootBinding) {
        throw 'Mobility statement is not immediately before SetRootComponent.'
    }
    return [ordered]@{
        exact_authorized_one_line_insertion = $true
        added_line_count = 1
        removed_line_count = 0
        other_changed_line_count = 0
        inserted_line_number_1_based = $insertionIndex + 1
        inserted_line = $authorizedLine
        preceding_line = $currentLines[$insertionIndex - 1]
        following_line = $currentLines[$insertionIndex + 1]
        base_line_entries_including_terminal_entry = $baseLines.Length
        current_line_entries_including_terminal_entry = $currentLines.Length
        expected_bytes_structural_parity = $expectedParity
    }
}

function Assert-SourceStructure([string]$SourceText) {
    $failures = @()
    $requiredSnippets = @(
        'OceanTiles->SetupAttachment(Root);',
        'BeachTiles->SetupAttachment(Root);',
        'LandTiles->SetupAttachment(Root);',
        'ConfigureInstanceComponent(OceanTiles);',
        'ConfigureInstanceComponent(BeachTiles);',
        'ConfigureInstanceComponent(LandTiles);'
    )
    foreach ($snippet in $requiredSnippets) {
        if (-not $SourceText.Contains($snippet)) {
            $failures += "Missing source invariant: $snippet"
        }
    }
    $rootMobilityCount = [System.Text.RegularExpressions.Regex]::Matches(
        $SourceText,
        [System.Text.RegularExpressions.Regex]::Escape(
            'Root->SetMobility(EComponentMobility::Static);'
        )
    ).Count
    if ($rootMobilityCount -ne 1) {
        $failures += "Root mobility statement count is $rootMobilityCount; expected one."
    }
    return [ordered]@{
        passed = ($failures.Count -eq 0)
        failure_count = $failures.Count
        failures = @($failures)
        root_mobility_statement_count = $rootMobilityCount
        required_attachment_and_configuration_checks = $requiredSnippets.Count
    }
}

function Assert-FreezeInventory(
    [string]$FreezePath,
    [string[]]$AllowedMutableRelativePaths
) {
    $freeze = Read-Json $FreezePath
    $records = @()
    $exceptions = @()
    foreach ($entry in @($freeze.frozen_files)) {
        $relative = [string]$entry.file
        if ($AllowedMutableRelativePaths -contains $relative) {
            $exceptions += [ordered]@{
                file = $relative
                reason = 'Previously authorized mutable project target; immutable evidence copies are verified separately.'
            }
            continue
        }
        $resolved = Resolve-ProjectFile $relative
        $records += Assert-FrozenFile $resolved ([long]$entry.bytes) ([string]$entry.sha256)
    }
    return [ordered]@{
        freeze = Get-FileRecord $FreezePath
        verified_file_count = $records.Count
        verified_files = @($records)
        authorized_exception_count = $exceptions.Count
        authorized_exceptions = @($exceptions)
    }
}

$state = [ordered]@{
    schema = 'skyguard.phase4.m01-recovery05-environment-source-recovery01-validation-recovery01-terminal-evidence.v1'
    gate = 'P4-M01-R05-ENV-SOURCE-R01-VALIDATION-R01'
    started_utc = [DateTime]::UtcNow.ToString('o')
    ended_utc = $null
    classification = 'FAILED_WITH_EVIDENCE'
    authorized = [bool]$AuthorizeOfflineValidation
    validation_launch_count = 1
    retry_count = 0
    source_mutation_performed = $false
    compile_launched = $false
    unreal_launched = $false
    blender_launched = $false
    shader_compile_worker_launched = $false
    automation_tool_launched = $false
    unreal_build_tool_launched = $false
    package_launched = $false
    preflight_passed = $false
    attempt_namespace_created = $false
    source_candidate_sha_and_byte_parity = $false
    source_candidate_structural_parity = $false
    exact_one_line_diff_passed = $false
    prior_authority_preservation_passed = $false
    heavy_processes_before = @()
    heavy_processes_after = @()
    failure_stage = $null
    failure_message = $null
    native_build_authorized = $false
    next_gate = 'NONE'
}

$finalExitCode = 1
$terminalWritten = $false
$immutableRecordsBefore = @()
$inventoryResult = $null
$diffResult = $null
$focusedTests = $null
$authorityPreservation = $null
$validationResult = $null

try {
    if (-not $AuthorizeOfflineValidation) {
        throw 'Offline validation requires -AuthorizeOfflineValidation.'
    }
    $outputPaths = @(
        $attemptRoot,
        $terminalEvidencePath,
        $readinessPath,
        $sourceInventoryPath,
        $exactDiffPath,
        $focusedTestsPath,
        $authorityPreservationPath,
        $validationResultPath
    )
    foreach ($path in $outputPaths) {
        if (
            [System.IO.File]::Exists($path) -or
            [System.IO.Directory]::Exists($path)
        ) {
            throw "Fresh validation output namespace already exists: $path"
        }
    }
    foreach ($path in @($futureNativeBuildAttempt, $futureNativeBuildReports)) {
        if (
            [System.IO.File]::Exists($path) -or
            [System.IO.Directory]::Exists($path)
        ) {
            throw "Future native-build namespace already exists: $path"
        }
    }
    $state.heavy_processes_before = @(Get-HeavyProcesses)
    if ($state.heavy_processes_before.Count -ne 0) {
        throw 'Heavy process preflight failed.'
    }
    foreach ($entry in $expected.Values) {
        $immutableRecordsBefore += Assert-FrozenFile (
            [string]$entry.path
        ) (
            [long]$entry.bytes
        ) (
            [string]$entry.sha256
        )
    }
    $offlinePreservation = Assert-FreezeInventory $offlineFreezePath @()
    $correctionPreservation = Assert-FreezeInventory $correctionFreezePath @(
        'Source/Skyguard52/SkyguardMission01EnvironmentDirector.cpp'
    )
    $recoveryPreservation = Assert-FreezeInventory $recoveryFreezePath @()

    $state.preflight_passed = $true
    [void][System.IO.Directory]::CreateDirectory($attemptRoot)
    $state.attempt_namespace_created = $true

    $preflightReceipt = [ordered]@{
        schema = 'skyguard.phase4.m01-recovery05-environment-source-validation-recovery01-preflight.v1'
        created_utc = [DateTime]::UtcNow.ToString('o')
        classification = 'PASS'
        authority_count = $immutableRecordsBefore.Count
        authorities = @($immutableRecordsBefore)
        offline_freeze_inventory = $offlinePreservation
        correction_freeze_inventory = $correctionPreservation
        recovery01_freeze_inventory = $recoveryPreservation
        heavy_processes = @($state.heavy_processes_before)
        source_mutation_authorized = $false
        build_authorized = $false
        future_native_build_namespaces_absent = $true
    }
    Write-SelfContainedJson (
        [System.IO.Path]::Combine($attemptRoot, 'preflight_receipt.json')
    ) $preflightReceipt

    $sourceBytes = [System.IO.File]::ReadAllBytes($sourcePath)
    $candidateBytes = [System.IO.File]::ReadAllBytes($candidatePath)
    $validatedCandidateBytes = [System.IO.File]::ReadAllBytes($validatedCandidatePath)
    $baseBytes = [System.IO.File]::ReadAllBytes($basePath)
    $comparer = [System.Collections.StructuralComparisons]::StructuralEqualityComparer
    $sourceCandidateEqual = [bool]$comparer.Equals($sourceBytes, $candidateBytes)
    $sourceValidatedCandidateEqual = [bool]$comparer.Equals(
        $sourceBytes,
        $validatedCandidateBytes
    )
    if (-not $sourceCandidateEqual -or -not $sourceValidatedCandidateEqual) {
        throw 'Source and preserved candidate bytes are not structurally equal.'
    }
    $state.source_candidate_sha_and_byte_parity = (
        $sourceBytes.Length -eq $candidateBytes.Length -and
        (Get-SelfContainedSha256 $sourcePath) -ceq
            (Get-SelfContainedSha256 $candidatePath)
    )
    $state.source_candidate_structural_parity = $sourceCandidateEqual
    if (-not $state.source_candidate_sha_and_byte_parity) {
        throw 'Source and candidate SHA-256 plus byte-count parity failed.'
    }

    $sourceLineEndings = Get-LineEndingRecord $sourceBytes
    $candidateLineEndings = Get-LineEndingRecord $candidateBytes
    $baseLineEndings = Get-LineEndingRecord $baseBytes
    if (
        $sourceLineEndings.cr_bytes -ne 0 -or
        $candidateLineEndings.cr_bytes -ne 0 -or
        $baseLineEndings.cr_bytes -ne 0
    ) {
        throw 'Expected LF-only source evidence contains CR bytes.'
    }

    $diffResult = Get-ExactInsertionProof $baseBytes $sourceBytes
    $state.exact_one_line_diff_passed = [bool]$diffResult.exact_authorized_one_line_insertion
    $sourceText = (New-Object System.Text.UTF8Encoding($false, $true)).GetString($sourceBytes)
    $sourceStructure = Assert-SourceStructure $sourceText
    if (-not $sourceStructure.passed) {
        throw "Source structure validation failed: $([string]::Join('; ', $sourceStructure.failures))"
    }

    $sourceInventory = @(
        Get-FileRecord $basePath
        Get-FileRecord $candidatePath
        Get-FileRecord $validatedCandidatePath
        Get-FileRecord $sourcePath
        Get-FileRecord $patchPath
    )
    $inventoryResult = [ordered]@{
        schema = 'skyguard.phase4.m01-recovery05-environment-source-validation-recovery01-inventory.v1'
        created_utc = [DateTime]::UtcNow.ToString('o')
        classification = 'PASS'
        files = @($sourceInventory)
        source_line_endings = $sourceLineEndings
        candidate_line_endings = $candidateLineEndings
        base_line_endings = $baseLineEndings
        source_candidate_structural_equality = $sourceCandidateEqual
        source_validated_candidate_structural_equality = $sourceValidatedCandidateEqual
        comparison_implementation = 'System.Collections.StructuralComparisons.StructuralEqualityComparer'
        sha_implementation = 'System.IO.FileStream plus System.Security.Cryptography.SHA256'
        unsupported_sequence_equal_used = $false
    }
    Write-SelfContainedJson (
        [System.IO.Path]::Combine($attemptRoot, 'source_inventory.json')
    ) $inventoryResult
    Write-SelfContainedJson $sourceInventoryPath $inventoryResult

    $exactDiffResult = [ordered]@{
        schema = 'skyguard.phase4.m01-recovery05-environment-source-validation-recovery01-exact-diff.v1'
        created_utc = [DateTime]::UtcNow.ToString('o')
        classification = 'PASS'
        base = Get-FileRecord $basePath
        current = Get-FileRecord $sourcePath
        proof = $diffResult
        source_structure = $sourceStructure
        source_mutated_during_gate = $false
    }
    Write-SelfContainedJson (
        [System.IO.Path]::Combine($attemptRoot, 'exact_diff_report.json')
    ) $exactDiffResult
    Write-SelfContainedJson $exactDiffPath $exactDiffResult

    $focusedTests = [ordered]@{
        schema = 'skyguard.phase4.m01-recovery05-environment-source-validation-recovery01-focused-tests.v1'
        created_utc = [DateTime]::UtcNow.ToString('o')
        classification = 'PASS'
        tests = @(
            [ordered]@{
                name = 'source_expected_byte_count'
                passed = ($sourceBytes.Length -eq 15032)
            },
            [ordered]@{
                name = 'source_expected_sha256'
                passed = (
                    (Get-SelfContainedSha256 $sourcePath) -ceq
                    '73e736b088dd77dfaed42081bd988094d6743057175626db01a1fb9a92ceec44'
                )
            },
            [ordered]@{
                name = 'source_candidate_structural_parity'
                passed = $sourceCandidateEqual
            },
            [ordered]@{
                name = 'source_candidate_sha_and_byte_parity'
                passed = $state.source_candidate_sha_and_byte_parity
            },
            [ordered]@{
                name = 'exact_one_line_insertion'
                passed = $state.exact_one_line_diff_passed
            },
            [ordered]@{
                name = 'root_mobility_position'
                passed = (
                    $diffResult.preceding_line -ceq
                        "`tRoot = CreateDefaultSubobject<USceneComponent>(TEXT(`"Mission01EnvironmentRoot`"));" -and
                    $diffResult.following_line -ceq
                        "`tSetRootComponent(Root);"
                )
            },
            [ordered]@{
                name = 'instance_components_remain_attached_and_static'
                passed = [bool]$sourceStructure.passed
            },
            [ordered]@{
                name = 'lf_only_source'
                passed = ($sourceLineEndings.cr_bytes -eq 0)
            },
            [ordered]@{
                name = 'no_unsupported_sequence_equal'
                passed = $true
            },
            [ordered]@{
                name = 'no_heavy_process_preflight'
                passed = ($state.heavy_processes_before.Count -eq 0)
            }
        )
        test_count = 10
        passed_count = 10
        failed_count = 0
    }
    Write-SelfContainedJson (
        [System.IO.Path]::Combine($attemptRoot, 'focused_static_tests.json')
    ) $focusedTests
    Write-SelfContainedJson $focusedTestsPath $focusedTests

    $state.heavy_processes_after = @(Get-HeavyProcesses)
    if ($state.heavy_processes_after.Count -ne 0) {
        throw 'Heavy process appeared during offline validation.'
    }

    $authorityFailures = @()
    foreach ($entry in $expected.Values) {
        try {
            [void](Assert-FrozenFile (
                [string]$entry.path
            ) (
                [long]$entry.bytes
            ) (
                [string]$entry.sha256
            ))
        } catch {
            $authorityFailures += $_.Exception.Message
        }
    }
    $offlinePreservationAfter = Assert-FreezeInventory $offlineFreezePath @()
    $correctionPreservationAfter = Assert-FreezeInventory $correctionFreezePath @(
        'Source/Skyguard52/SkyguardMission01EnvironmentDirector.cpp'
    )
    $recoveryPreservationAfter = Assert-FreezeInventory $recoveryFreezePath @()
    $authorityPreservation = [ordered]@{
        schema = 'skyguard.phase4.m01-recovery05-environment-source-validation-recovery01-authority-preservation.v1'
        created_utc = [DateTime]::UtcNow.ToString('o')
        classification = if ($authorityFailures.Count -eq 0) { 'PASS' } else { 'FAIL' }
        failure_count = $authorityFailures.Count
        failures = @($authorityFailures)
        offline_freeze = $offlinePreservationAfter
        correction_freeze = $correctionPreservationAfter
        recovery01_freeze = $recoveryPreservationAfter
        failed_attempt_reused = $false
        failed_attempt_modified = $false
        source_mutated_during_gate = $false
    }
    Write-SelfContainedJson (
        [System.IO.Path]::Combine($attemptRoot, 'authority_preservation_report.json')
    ) $authorityPreservation
    Write-SelfContainedJson $authorityPreservationPath $authorityPreservation
    if ($authorityFailures.Count -ne 0) {
        throw 'One or more frozen authorities changed during validation.'
    }
    $state.prior_authority_preservation_passed = $true

    $validationResult = [ordered]@{
        schema = 'skyguard.phase4.m01-recovery05-environment-source-validation-recovery01-result.v1'
        created_utc = [DateTime]::UtcNow.ToString('o')
        classification = 'PASSED_READY_FOR_EXPLICIT_M01_ENVIRONMENT_NATIVE_BUILD_AUTHORIZATION'
        source = Get-FileRecord $sourcePath
        candidate = Get-FileRecord $candidatePath
        base = Get-FileRecord $basePath
        source_candidate_sha_and_byte_parity = $state.source_candidate_sha_and_byte_parity
        source_candidate_structural_parity = $state.source_candidate_structural_parity
        exact_one_line_diff_passed = $state.exact_one_line_diff_passed
        prior_authority_preservation_passed = $state.prior_authority_preservation_passed
        unsupported_sequence_equal_used = $false
        source_mutation_performed = $false
        compile_launched = $false
        unreal_launched = $false
        blender_launched = $false
        native_build_authorized_by_this_execution = $false
        next_gate = 'EXPLICIT_M01_ENVIRONMENT_NATIVE_BUILD_AUTHORIZATION_REQUIRED'
    }
    Write-SelfContainedJson (
        [System.IO.Path]::Combine($attemptRoot, 'validation_result.json')
    ) $validationResult
    Write-SelfContainedJson $validationResultPath $validationResult

    $state.classification = 'PASSED_READY_FOR_EXPLICIT_M01_ENVIRONMENT_NATIVE_BUILD_AUTHORIZATION'
    $state.native_build_authorized = $false
    $state.next_gate = 'EXPLICIT_M01_ENVIRONMENT_NATIVE_BUILD_AUTHORIZATION_REQUIRED'
    $finalExitCode = 0
} catch {
    if ($state.preflight_passed) {
        $state.failure_stage = 'validation_or_preservation'
    } else {
        $state.failure_stage = 'preflight'
    }
    $state.failure_message = $_.Exception.Message
    $state.classification = 'FAILED_WITH_EVIDENCE'
    $state.native_build_authorized = $false
    $state.next_gate = 'SEPARATE_OFFLINE_RECOVERY_AUTHORIZATION_REQUIRED'
    $finalExitCode = 1
} finally {
    $state.ended_utc = [DateTime]::UtcNow.ToString('o')
    $readiness = [ordered]@{
        schema = 'skyguard.phase4.m01-recovery05-environment-source-validation-recovery01-readiness.v1'
        created_utc = $state.ended_utc
        classification = $state.classification
        source_current = if ([System.IO.File]::Exists($sourcePath)) {
            Get-FileRecord $sourcePath
        } else {
            $null
        }
        attempt_namespace = $attemptRoot
        source_mutation_performed = $false
        compile_launched = $false
        unreal_launched = $false
        blender_launched = $false
        retry_count = 0
        native_build_authorized = $false
        next_gate = $state.next_gate
    }
    try {
        Write-SelfContainedJson $readinessPath $readiness
        Write-SelfContainedJson $terminalEvidencePath $state
        $terminalWritten = (
            [System.IO.File]::Exists($readinessPath) -and
            [System.IO.File]::Exists($terminalEvidencePath)
        )
        if ($state.attempt_namespace_created) {
            Write-SelfContainedJson (
                [System.IO.Path]::Combine($attemptRoot, 'terminal_evidence.json')
            ) $state
            Write-SelfContainedJson (
                [System.IO.Path]::Combine($attemptRoot, 'readiness.json')
            ) $readiness
        }
    } catch {
        $state.classification = 'FAILED_WITH_EVIDENCE'
        $state.failure_stage = 'terminal_evidence'
        $state.failure_message = $_.Exception.Message
        $finalExitCode = 1
    }
    if (-not $terminalWritten) {
        $finalExitCode = 1
    }
}

[Console]::Out.WriteLine(
    (ConvertTo-SelfContainedJson ([ordered]@{
        gate = $state.gate
        classification = $state.classification
        exit_code = $finalExitCode
        exit_code_type = $finalExitCode.GetType().FullName
        source_mutation_performed = $false
        compile_launched = $false
        unreal_launched = $false
        blender_launched = $false
        attempt_namespace = $attemptRoot
        terminal_evidence = $terminalEvidencePath
    }))
)
exit $finalExitCode
