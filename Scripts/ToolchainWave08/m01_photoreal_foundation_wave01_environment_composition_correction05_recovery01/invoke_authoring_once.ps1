param(
    [switch]$OfflineContractTest,
    [switch]$AuthorizeSingleUnreal
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$OriginalSupervisor = 'D:\Skyguard52\Scripts\ToolchainWave08\m01_photoreal_foundation_wave01_environment_composition_correction05\invoke_authoring_once.ps1'
$OriginalAuthor = 'D:\Skyguard52\Scripts\ToolchainWave08\m01_photoreal_foundation_wave01_environment_composition_correction05\author_environment_composition_correction05.py'
$Binder = 'D:\Skyguard52\Scripts\ToolchainWave08\m01_photoreal_foundation_wave01_environment_composition_correction05_recovery01\author_environment_composition_correction05_recovery01.py'
$Verifier = 'D:\Skyguard52\Scripts\ToolchainWave08\m01_photoreal_foundation_wave01_environment_composition_correction05_recovery01\verify_authoring_offline.py'
$Contract = 'D:\Skyguard52\Docs\Toolchain\ToolchainWave08\M01PhotorealFoundationEnvironmentCompositionCorrection05Recovery01\quality_contract.json'
$FailedFreeze = 'D:\Skyguard52\Docs\AAA_Review\M01_PHOTOREAL_FOUNDATION_WAVE01_ENVIRONMENT_COMPOSITION_CORRECTION05_AUTHORING_ATTEMPT01_TERMINAL_FREEZE.json'
$TerminalManifest = 'D:\Skyguard52\Saved\Reports\M01_PHOTOREAL_FOUNDATION_WAVE01_ENVIRONMENT_COMPOSITION_CORRECTION05_RECOVERY01_AUTHORING_TERMINAL_MANIFEST.json'
$EmergencyReceipt = 'D:\Skyguard52\Saved\Reports\M01_PHOTOREAL_FOUNDATION_WAVE01_ENVIRONMENT_COMPOSITION_CORRECTION05_RECOVERY01_AUTHORING_EMERGENCY_RECEIPT.jsonl'

$Expected = @(
    @{ Path = $OriginalSupervisor; Bytes = 15495; Sha256 = 'eb7f4dfb94ea868974b59e9b8f386a76cf621437d82e41f3d5e9718f25d25156'; Label = 'Frozen Correction05 supervisor' },
    @{ Path = $OriginalAuthor; Bytes = 22628; Sha256 = '250c91c8facdea46ce1e5602eeb47e90cefd609c6b9f908f9f19c67eb5e2c294'; Label = 'Frozen Correction05 author' },
    @{ Path = $Binder; Bytes = 3681; Sha256 = 'ce3349f4eafc4b4d21bdeac0d6da7ac7b4ea8fc89f1ca8488f2ff623b43b5708'; Label = 'Recovery01 author binder' },
    @{ Path = $Verifier; Bytes = 4841; Sha256 = '55616efdae46d4f4f876c170b7ef36068db5ae1b182d9f6236239b6bd1da237d'; Label = 'Recovery01 verifier' },
    @{ Path = $Contract; Bytes = 1718; Sha256 = 'b22103202523aa27e275072f2a0dd216e80ab38876efc0d2e5587018a4726a8d'; Label = 'Recovery01 contract' },
    @{ Path = $FailedFreeze; Bytes = 4119; Sha256 = '57d5f609719f47089a779af59e670c249cf408d2b45a903e4a4b64bd5c04494f'; Label = 'Failed Attempt01 freeze' }
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
    if ($failed.classification -ne 'FAILED_WITH_EVIDENCE' -or $failed.next_gate -ne 'M01_PHOTOREAL_FOUNDATION_WAVE01_ENVIRONMENT_COMPOSITION_CORRECTION05_RECOVERY01_AUTHORING') { throw 'Failed attempt does not authorize Recovery01' }

    $source = [System.IO.File]::ReadAllText($OriginalSupervisor, [System.Text.Encoding]::UTF8)
    $source = Replace-Exact $source 'EnvironmentCompositionCorrection05' 'EnvironmentCompositionCorrection05Recovery01' 2
    $source = Replace-Exact $source 'ENVIRONMENT_COMPOSITION_CORRECTION05' 'ENVIRONMENT_COMPOSITION_CORRECTION05_RECOVERY01' 5
    $source = Replace-Exact $source 'environment-composition-correction05' 'environment-composition-correction05-recovery01' 1
    $source = Replace-Exact $source 'm01_photoreal_foundation_wave01_environment_composition_correction05\author_environment_composition_correction05.py' 'm01_photoreal_foundation_wave01_environment_composition_correction05_recovery01\author_environment_composition_correction05_recovery01.py' 1
    $source = Replace-Exact $source 'm01_photoreal_foundation_wave01_environment_composition_correction05\verify_authoring_offline.py' 'm01_photoreal_foundation_wave01_environment_composition_correction05_recovery01\verify_authoring_offline.py' 1
    $source = Replace-Exact $source "Bytes = 22628; Sha256 = '250c91c8facdea46ce1e5602eeb47e90cefd609c6b9f908f9f19c67eb5e2c294'" "Bytes = 3681; Sha256 = 'ce3349f4eafc4b4d21bdeac0d6da7ac7b4ea8fc89f1ca8488f2ff623b43b5708'" 1
    $source = Replace-Exact $source "Bytes = 5241; Sha256 = 'a032dd95a4712ac213da622bce2239b88f49f3ae83125ac5f297c3942d7cba0a'" "Bytes = 4841; Sha256 = '55616efdae46d4f4f876c170b7ef36068db5ae1b182d9f6236239b6bd1da237d'" 1
    $source = Replace-Exact $source "Bytes = 2934; Sha256 = '6ef70fce7fd71eb0a1b0b652e323774f9411ef14554033a49e7861da333dcfc6'" "Bytes = 1718; Sha256 = 'b22103202523aa27e275072f2a0dd216e80ab38876efc0d2e5587018a4726a8d'" 1

    $launchToken = 'Start-' + 'Process'
    if (([regex]::Matches($source, $launchToken)).Count -ne 1) { throw 'Bound supervisor launch count is not one' }
    if ($source -match 'EnvironmentCompositionCorrection05\.umap') { throw 'Failed output map remains in bound supervisor' }
    if ($source -match 'ENVIRONMENT_COMPOSITION_CORRECTION05_AUTHORING') { throw 'Failed attempt namespace remains in bound supervisor' }
    if (-not $source.Contains($Binder) -or -not $source.Contains($Verifier) -or -not $source.Contains($Contract)) { throw 'Recovery01 authorities are not fully bound' }

    $bound = [scriptblock]::Create($source)
    & $bound -OfflineContractTest:$OfflineContractTest -AuthorizeSingleUnreal:$AuthorizeSingleUnreal
}
catch {
    if (-not $OfflineContractTest) {
        $failure = [ordered]@{
            schema = 'skyguard.m01-photoreal-foundation.environment-composition-correction05-recovery01.binding-failure.v1'
            classification = 'FAILED_WITH_EVIDENCE'
            at_utc = [DateTime]::UtcNow.ToString('o')
            unreal_launch_count = 0
            retry_count = 0
            failure = $_.Exception.Message
        }
        try { Write-JsonAtomic $TerminalManifest $failure }
        catch {
            try { [System.IO.File]::AppendAllText($EmergencyReceipt, (($failure | ConvertTo-Json -Compress) + [Environment]::NewLine), [System.Text.UTF8Encoding]::new($false)) } catch {}
        }
    }
    [Console]::Error.WriteLine($_.Exception.Message)
    [Environment]::Exit([int]1)
}
