param([switch]$OfflineContractTest)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$OriginalSupervisor = 'D:\Skyguard52\Scripts\ToolchainWave08\m01_photoreal_foundation_wave01_ground_lighting_correction04\invoke_authoring_once.ps1'
$OriginalAuthor = 'D:\Skyguard52\Scripts\ToolchainWave08\m01_photoreal_foundation_wave01_ground_lighting_correction04\author_ground_lighting_correction04.py'
$Binder = 'D:\Skyguard52\Scripts\ToolchainWave08\m01_photoreal_foundation_wave01_ground_lighting_correction04_recovery01\author_ground_lighting_correction04_recovery01.py'
$Verifier = 'D:\Skyguard52\Scripts\ToolchainWave08\m01_photoreal_foundation_wave01_ground_lighting_correction04_recovery01\verify_authoring_offline.py'
$Contract = 'D:\Skyguard52\Docs\Toolchain\ToolchainWave08\M01PhotorealFoundationGroundLightingCorrection04Recovery01\quality_contract.json'
$FailedFreeze = 'D:\Skyguard52\Docs\AAA_Review\M01_PHOTOREAL_FOUNDATION_WAVE01_GROUND_LIGHTING_CORRECTION04_AUTHORING_ATTEMPT01_TERMINAL_FREEZE.json'
$EngineAuthority = 'D:\Skyguard52\Docs\AAA_Review\M01_PHOTOREAL_FOUNDATION_WAVE01_GROUND_LIGHTING_CORRECTION04_ATTEMPT01_ENGINE_AUTHORITY_REPORT.json'
$EngineImplementation = 'D:\UE_5.8\Engine\Source\Editor\MaterialEditor\Private\MaterialEditingLibrary.cpp'
$TerminalManifest = 'D:\Skyguard52\Saved\Reports\M01_PHOTOREAL_FOUNDATION_WAVE01_GROUND_LIGHTING_CORRECTION04_RECOVERY01_AUTHORING_TERMINAL_MANIFEST.json'
$EmergencyReceipt = 'D:\Skyguard52\Saved\Reports\M01_PHOTOREAL_FOUNDATION_WAVE01_GROUND_LIGHTING_CORRECTION04_RECOVERY01_AUTHORING_EMERGENCY_RECEIPT.jsonl'

$Expected = @(
    @{ Path = $OriginalSupervisor; Bytes = 14589; Sha256 = '3a278c5d94063651c8da7ce581db95818218fd63e1dd307f062fdca275140e42'; Label = 'Frozen Correction04 supervisor' },
    @{ Path = $OriginalAuthor; Bytes = 20684; Sha256 = 'eba032612dd1ee9de55560b1fef1ec8f88fdf608d96121ef3d1c08132ce818b3'; Label = 'Frozen Correction04 author' },
    @{ Path = $Binder; Bytes = 2960; Sha256 = '29de31f880045f0d8d9e0a3fbaf8a8e63e1f3983d2854feca620489d2a0ad7a0'; Label = 'Recovery01 compatibility binder' },
    @{ Path = $Verifier; Bytes = 3776; Sha256 = '9a804e38304df3d4557c764c8f331b3ba22a5c291ff6a98c8727e3ef586ce9a7'; Label = 'Recovery01 verifier' },
    @{ Path = $Contract; Bytes = 1460; Sha256 = '8477fb30469cfd68d2011962d01ec700c3b107340a6fc1a6d8be00d09153e0e2'; Label = 'Recovery01 contract' },
    @{ Path = $FailedFreeze; Bytes = 3140; Sha256 = '9ca747e3af985f782359a3cf6f8c5f48a7ce70defab2e9238b393c71f761bea2'; Label = 'Failed Attempt01 freeze' },
    @{ Path = $EngineAuthority; Bytes = 1758; Sha256 = '00c83de19d34d724dc58334e121ed2c29cac29eec92bfb0d10ee4b5d51f4b6d3'; Label = 'UE 5.8 authority report' },
    @{ Path = $EngineImplementation; Bytes = 71759; Sha256 = '96051980458dad86719f195072da4bd34eebd07a80d647ebb50bbbb0626e5565'; Label = 'UE 5.8 MaterialEditingLibrary implementation' }
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
    [System.IO.File]::WriteAllText($temporary, ($Payload | ConvertTo-Json -Depth 30) + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
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
    if ($failed.classification -ne 'FAILED_WITH_EVIDENCE' -or $failed.next_gate -ne 'M01_PHOTOREAL_FOUNDATION_WAVE01_GROUND_LIGHTING_CORRECTION04_RECOVERY01_OFFLINE_CORRECTION') { throw 'Failed attempt does not route to Recovery01' }
    $engine = Get-Content -LiteralPath $EngineAuthority -Raw | ConvertFrom-Json
    if ($engine.classification -ne 'PASSED_BOUNDED_UE58_TOOLING_DEFECT_IDENTIFIED') { throw 'UE 5.8 tooling defect authority is not accepted' }

    $source = [System.IO.File]::ReadAllText($OriginalSupervisor, [System.Text.Encoding]::UTF8)
    $source = Replace-Exact $source 'm01_photoreal_foundation_wave01_ground_lighting_correction04\author_ground_lighting_correction04.py' 'm01_photoreal_foundation_wave01_ground_lighting_correction04_recovery01\author_ground_lighting_correction04_recovery01.py' 1
    $source = Replace-Exact $source 'm01_photoreal_foundation_wave01_ground_lighting_correction04\verify_authoring_offline.py' 'm01_photoreal_foundation_wave01_ground_lighting_correction04_recovery01\verify_authoring_offline.py' 1
    $source = Replace-Exact $source "Bytes = 20684; Sha256 = 'eba032612dd1ee9de55560b1fef1ec8f88fdf608d96121ef3d1c08132ce818b3'" "Bytes = 2960; Sha256 = '29de31f880045f0d8d9e0a3fbaf8a8e63e1f3983d2854feca620489d2a0ad7a0'" 1
    $source = Replace-Exact $source "Bytes = 3211; Sha256 = 'd3d84f7022d5e1ccc1b24b42eb268f12f1103660daf9140d21878acf95177b5b'" "Bytes = 3776; Sha256 = '9a804e38304df3d4557c764c8f331b3ba22a5c291ff6a98c8727e3ef586ce9a7'" 1
    $source = Replace-Exact $source "Bytes = 2359; Sha256 = '29910c55f5922c03bfcc59165b53c64e206047e5479fd2364be9a89751a04a1c'" "Bytes = 1460; Sha256 = '8477fb30469cfd68d2011962d01ec700c3b107340a6fc1a6d8be00d09153e0e2'" 1
    $source = Replace-Exact $source 'GroundLightingCorrection04' 'GroundLightingCorrection04Recovery01' 4
    $source = Replace-Exact $source 'M01_PHOTOREAL_FOUNDATION_WAVE01_GROUND_LIGHTING_CORRECTION04_AUTHORING' 'M01_PHOTOREAL_FOUNDATION_WAVE01_GROUND_LIGHTING_CORRECTION04_RECOVERY01_AUTHORING' 3
    $source = Replace-Exact $source 'PASSED_M01_PHOTOREAL_FOUNDATION_GROUND_LIGHTING_CORRECTION04_AUTOMATIC' 'PASSED_M01_PHOTOREAL_FOUNDATION_GROUND_LIGHTING_CORRECTION04_RECOVERY01_AUTOMATIC' 1
    $source = Replace-Exact $source 'PASSED_READY_FOR_GROUND_LIGHTING_CORRECTION04_D3D12_VISUAL_PROOF' 'PASSED_READY_FOR_GROUND_LIGHTING_CORRECTION04_RECOVERY01_D3D12_VISUAL_PROOF' 1
    $source = Replace-Exact $source 'ground-lighting-correction04' 'ground-lighting-correction04-recovery01' 1

    $launchToken = 'Start-' + 'Process'
    if (([regex]::Matches($source, $launchToken)).Count -ne 1) { throw 'Bound supervisor launch count is not one' }
    if ($source -match 'GroundLightingCorrection04\\Materials') { throw 'Failed material namespace remains in bound supervisor' }
    if ($source -match 'GROUND_LIGHTING_CORRECTION04_AUTHORING') { throw 'Failed attempt namespace remains in bound supervisor' }
    if (-not $source.Contains($Binder)) { throw 'Bound supervisor does not reference Recovery01 binder' }
    if (-not $source.Contains($Verifier)) { throw 'Bound supervisor does not reference Recovery01 verifier' }

    $bound = [scriptblock]::Create($source)
    & $bound -OfflineContractTest:$OfflineContractTest
}
catch {
    if (-not $OfflineContractTest) {
        $failure = [ordered]@{
            schema = 'skyguard.m01-photoreal-foundation.ground-lighting-correction04-recovery01.binding-failure.v1'
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
