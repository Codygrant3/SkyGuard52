param([switch]$OfflineContractTest, [switch]$AuthorizeSingleUnreal)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$OriginalSupervisor = 'D:\Skyguard52\Scripts\ToolchainWave08\m01_photoreal_foundation_wave01_environment_composition_correction05\invoke_authoring_once.ps1'
$OriginalAuthor = 'D:\Skyguard52\Scripts\ToolchainWave08\m01_photoreal_foundation_wave01_environment_composition_correction05\author_environment_composition_correction05.py'
$Binder = 'D:\Skyguard52\Scripts\ToolchainWave08\m01_photoreal_foundation_wave01_environment_composition_correction05_recovery02\author_environment_composition_correction05_recovery02.py'
$Verifier = 'D:\Skyguard52\Scripts\ToolchainWave08\m01_photoreal_foundation_wave01_environment_composition_correction05_recovery02\verify_authoring_offline.py'
$Contract = 'D:\Skyguard52\Docs\Toolchain\ToolchainWave08\M01PhotorealFoundationEnvironmentCompositionCorrection05Recovery02\quality_contract.json'
$FailedFreeze = 'D:\Skyguard52\Docs\AAA_Review\M01_PHOTOREAL_FOUNDATION_WAVE01_ENVIRONMENT_COMPOSITION_CORRECTION05_RECOVERY01_AUTHORING_ATTEMPT01_TERMINAL_FREEZE.json'
$TerminalManifest = 'D:\Skyguard52\Saved\Reports\M01_PHOTOREAL_FOUNDATION_WAVE01_ENVIRONMENT_COMPOSITION_CORRECTION05_RECOVERY02_AUTHORING_TERMINAL_MANIFEST.json'
$EmergencyReceipt = 'D:\Skyguard52\Saved\Reports\M01_PHOTOREAL_FOUNDATION_WAVE01_ENVIRONMENT_COMPOSITION_CORRECTION05_RECOVERY02_AUTHORING_EMERGENCY_RECEIPT.jsonl'

$Expected = @(
    @{ Path = $OriginalSupervisor; Bytes = 15495; Sha256 = 'eb7f4dfb94ea868974b59e9b8f386a76cf621437d82e41f3d5e9718f25d25156'; Label = 'Frozen Correction05 supervisor' },
    @{ Path = $OriginalAuthor; Bytes = 22628; Sha256 = '250c91c8facdea46ce1e5602eeb47e90cefd609c6b9f908f9f19c67eb5e2c294'; Label = 'Frozen Correction05 author' },
    @{ Path = $Binder; Bytes = 3730; Sha256 = '2b0fd42562dfb0a03c0e2b96c22d7e31b94e66156e1b60db475c2a941057ba44'; Label = 'Recovery02 author binder' },
    @{ Path = $Verifier; Bytes = 4521; Sha256 = 'f6a6afee751c878853f0f7fa758c5f94d9e62414165f3058fabdee585b6de30d'; Label = 'Recovery02 verifier' },
    @{ Path = $Contract; Bytes = 1670; Sha256 = 'deeece68b488de9357a9d4e1d90c0f63d702180ff455218f7db965a469ea2558'; Label = 'Recovery02 contract' },
    @{ Path = $FailedFreeze; Bytes = 3541; Sha256 = '512c8431ed4faad150ebf7991b9418fded102e0df51c6ee9854c7c7d9f4fbd05'; Label = 'Recovery01 failure freeze' }
)

function Get-Sha256([string]$Path) {
    $stream = [System.IO.File]::Open($Path, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::Read)
    $hasher = [System.Security.Cryptography.SHA256]::Create()
    try { return ([System.BitConverter]::ToString($hasher.ComputeHash($stream))).Replace('-', '').ToLowerInvariant() }
    finally { $hasher.Dispose(); $stream.Dispose() }
}

function Assert-File([hashtable]$Row) {
    if (-not [System.IO.File]::Exists($Row.Path)) { throw "$($Row.Label) missing: $($Row.Path)" }
    $info = [System.IO.FileInfo]::new($Row.Path)
    if ($info.Length -ne [int64]$Row.Bytes) { throw "$($Row.Label) byte mismatch" }
    if ((Get-Sha256 $Row.Path) -ne [string]$Row.Sha256) { throw "$($Row.Label) hash mismatch" }
}

function Write-JsonAtomic([string]$Path, [object]$Payload) {
    [System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName($Path)) | Out-Null
    $temporary = "$Path.tmp"
    [System.IO.File]::WriteAllText($temporary, ($Payload | ConvertTo-Json -Depth 40) + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
    if ([System.IO.File]::Exists($Path)) { throw "Refusing to overwrite evidence: $Path" }
    [System.IO.File]::Move($temporary, $Path)
}

function Replace-Exact([string]$Source, [string]$Old, [string]$New, [int]$ExpectedCount) {
    $actual = ([regex]::Matches($Source, [regex]::Escape($Old))).Count
    if ($actual -ne $ExpectedCount) { throw "Supervisor binding count changed for '$Old': $actual != $ExpectedCount" }
    return $Source.Replace($Old, $New)
}

try {
    foreach ($row in $Expected) { Assert-File $row }
    $failed = Get-Content -LiteralPath $FailedFreeze -Raw | ConvertFrom-Json
    if ($failed.classification -ne 'FAILED_WITH_EVIDENCE' -or $failed.next_gate -ne 'M01_PHOTOREAL_FOUNDATION_WAVE01_ENVIRONMENT_COMPOSITION_CORRECTION05_RECOVERY02_AUTHORING') { throw 'Recovery01 failure does not authorize Recovery02' }

    $source = [System.IO.File]::ReadAllText($OriginalSupervisor, [System.Text.Encoding]::UTF8)
    $source = Replace-Exact $source 'EnvironmentCompositionCorrection05' 'EnvironmentCompositionCorrection05Recovery02' 2
    $source = Replace-Exact $source 'ENVIRONMENT_COMPOSITION_CORRECTION05' 'ENVIRONMENT_COMPOSITION_CORRECTION05_RECOVERY02' 5
    $source = Replace-Exact $source 'environment-composition-correction05' 'environment-composition-correction05-recovery02' 1
    $source = Replace-Exact $source 'm01_photoreal_foundation_wave01_environment_composition_correction05\author_environment_composition_correction05.py' 'm01_photoreal_foundation_wave01_environment_composition_correction05_recovery02\author_environment_composition_correction05_recovery02.py' 1
    $source = Replace-Exact $source 'm01_photoreal_foundation_wave01_environment_composition_correction05\verify_authoring_offline.py' 'm01_photoreal_foundation_wave01_environment_composition_correction05_recovery02\verify_authoring_offline.py' 1
    $source = Replace-Exact $source "Bytes = 22628; Sha256 = '250c91c8facdea46ce1e5602eeb47e90cefd609c6b9f908f9f19c67eb5e2c294'" "Bytes = 3730; Sha256 = '2b0fd42562dfb0a03c0e2b96c22d7e31b94e66156e1b60db475c2a941057ba44'" 1
    $source = Replace-Exact $source "Bytes = 5241; Sha256 = 'a032dd95a4712ac213da622bce2239b88f49f3ae83125ac5f297c3942d7cba0a'" "Bytes = 4521; Sha256 = 'f6a6afee751c878853f0f7fa758c5f94d9e62414165f3058fabdee585b6de30d'" 1
    $source = Replace-Exact $source "Bytes = 2934; Sha256 = '6ef70fce7fd71eb0a1b0b652e323774f9411ef14554033a49e7861da333dcfc6'" "Bytes = 1670; Sha256 = 'deeece68b488de9357a9d4e1d90c0f63d702180ff455218f7db965a469ea2558'" 1
    $source = Replace-Exact $source 'ocean_wave_bindings' 'ocean_wave_state_preserved' 1

    $launchToken = 'Start-' + 'Process'
    if (([regex]::Matches($source, $launchToken)).Count -ne 1) { throw 'Bound supervisor launch count is not one' }
    if ($source -match 'EnvironmentCompositionCorrection05\.umap') { throw 'Failed output map remains in bound supervisor' }
    if ($source -match 'ENVIRONMENT_COMPOSITION_CORRECTION05_AUTHORING') { throw 'Failed attempt namespace remains in bound supervisor' }
    if (-not $source.Contains($Binder) -or -not $source.Contains($Verifier) -or -not $source.Contains($Contract)) { throw 'Recovery02 authorities are not fully bound' }
    if ($source -match '\.ocean_wave_bindings') { throw 'Unsupported wave-binding metric remains in bound supervisor' }

    $bound = [scriptblock]::Create($source)
    & $bound -OfflineContractTest:$OfflineContractTest -AuthorizeSingleUnreal:$AuthorizeSingleUnreal
}
catch {
    if (-not $OfflineContractTest) {
        $failure = [ordered]@{ schema = 'skyguard.m01-photoreal-foundation.environment-composition-correction05-recovery02.binding-failure.v1'; classification = 'FAILED_WITH_EVIDENCE'; at_utc = [DateTime]::UtcNow.ToString('o'); unreal_launch_count = 0; retry_count = 0; failure = $_.Exception.Message }
        try { Write-JsonAtomic $TerminalManifest $failure }
        catch { try { [System.IO.File]::AppendAllText($EmergencyReceipt, (($failure | ConvertTo-Json -Compress) + [Environment]::NewLine), [System.Text.UTF8Encoding]::new($false)) } catch {} }
    }
    [Console]::Error.WriteLine($_.Exception.Message)
    [Environment]::Exit([int]1)
}
