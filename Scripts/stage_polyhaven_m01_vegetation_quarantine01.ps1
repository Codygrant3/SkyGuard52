param(
    [switch]$AuthorizeSingleDownload
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

if (-not $AuthorizeSingleDownload) {
    [Console]::Error.WriteLine('Refusing download without -AuthorizeSingleDownload.')
    exit 2
}

$ProjectRoot = 'D:\Skyguard52'
$OutputRoot = Join-Path $ProjectRoot 'Saved\SourceQuarantine\M01_POLYHAVEN_VEGETATION_QUARANTINE01'
if (Test-Path -LiteralPath $OutputRoot) {
    throw "Fresh quarantine namespace already exists: $OutputRoot"
}

$Assets = @(
    'tree_small_02',
    'fir_sapling',
    'pine_sapling_small',
    'shrub_02',
    'shrub_04',
    'grass_medium_02'
)

function Get-FileSha256([string]$Path) {
    $Stream = [System.IO.File]::OpenRead($Path)
    $Sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $Bytes = $Sha.ComputeHash($Stream)
        return ([System.BitConverter]::ToString($Bytes)).Replace('-', '').ToLowerInvariant()
    }
    finally {
        $Sha.Dispose()
        $Stream.Dispose()
    }
}

function Get-FileMd5([string]$Path) {
    $Stream = [System.IO.File]::OpenRead($Path)
    $Md5 = [System.Security.Cryptography.MD5]::Create()
    try {
        $Bytes = $Md5.ComputeHash($Stream)
        return ([System.BitConverter]::ToString($Bytes)).Replace('-', '').ToLowerInvariant()
    }
    finally {
        $Md5.Dispose()
        $Stream.Dispose()
    }
}

function Download-GovernedFile([string]$Url, [string]$Path, [string]$ExpectedMd5, [long]$ExpectedBytes) {
    $Parent = Split-Path -Parent $Path
    New-Item -ItemType Directory -Path $Parent -Force | Out-Null
    Invoke-WebRequest -Uri $Url -OutFile $Path -UseBasicParsing
    $Item = Get-Item -LiteralPath $Path
    $ActualMd5 = Get-FileMd5 $Path
    if ($Item.Length -ne $ExpectedBytes) {
        throw "Byte mismatch for $Path. Expected $ExpectedBytes, got $($Item.Length)."
    }
    if ($ActualMd5 -ne $ExpectedMd5.ToLowerInvariant()) {
        throw "MD5 mismatch for $Path. Expected $ExpectedMd5, got $ActualMd5."
    }
    return [ordered]@{
        path = $Path
        source_url = $Url
        bytes = $Item.Length
        md5 = $ActualMd5
        sha256 = Get-FileSha256 $Path
    }
}

New-Item -ItemType Directory -Path $OutputRoot | Out-Null
$Started = [DateTime]::UtcNow.ToString('o')
$Records = @()

try {
    foreach ($AssetId in $Assets) {
        $AssetRoot = Join-Path $OutputRoot $AssetId
        New-Item -ItemType Directory -Path $AssetRoot | Out-Null
        $InfoUrl = "https://api.polyhaven.com/info/$AssetId"
        $FilesUrl = "https://api.polyhaven.com/files/$AssetId"
        $Info = Invoke-RestMethod -Uri $InfoUrl -Method Get
        $Files = Invoke-RestMethod -Uri $FilesUrl -Method Get
        $InfoPath = Join-Path $AssetRoot 'polyhaven_info.json'
        $FilesPath = Join-Path $AssetRoot 'polyhaven_files.json'
        $Info | ConvertTo-Json -Depth 100 | Set-Content -LiteralPath $InfoPath -Encoding utf8
        $Files | ConvertTo-Json -Depth 100 | Set-Content -LiteralPath $FilesPath -Encoding utf8

        $GltfRecord = $Files.gltf.'2k'.gltf
        if ($null -eq $GltfRecord) {
            throw "No 2K glTF package for $AssetId."
        }
        $Downloads = @()
        $Downloads += Download-GovernedFile $GltfRecord.url (Join-Path $AssetRoot ([System.IO.Path]::GetFileName([uri]$GltfRecord.url))) $GltfRecord.md5 ([long]$GltfRecord.size)
        foreach ($Include in $GltfRecord.include.PSObject.Properties) {
            $IncludePath = Join-Path $AssetRoot ($Include.Name -replace '/', '\')
            $Downloads += Download-GovernedFile $Include.Value.url $IncludePath $Include.Value.md5 ([long]$Include.Value.size)
        }
        $Records += [ordered]@{
            asset_id = $AssetId
            name = $Info.name
            categories = @($Info.categories)
            authors = @($Info.authors.PSObject.Properties.Name)
            dimensions_mm = @($Info.dimensions)
            source_info_url = $InfoUrl
            source_files_url = $FilesUrl
            source_page = "https://polyhaven.com/a/$AssetId"
            license = 'CC0-1.0'
            license_url = 'https://polyhaven.com/license'
            metadata = @(
                [ordered]@{ path = $InfoPath; bytes = (Get-Item $InfoPath).Length; sha256 = Get-FileSha256 $InfoPath },
                [ordered]@{ path = $FilesPath; bytes = (Get-Item $FilesPath).Length; sha256 = Get-FileSha256 $FilesPath }
            )
            downloads = $Downloads
        }
    }

    $Manifest = [ordered]@{
        schema = 'skyguard.m01-polyhaven-vegetation-quarantine01-manifest.v1'
        created_at_utc = [DateTime]::UtcNow.ToString('o')
        started_at_utc = $Started
        classification = 'PASSED_SOURCE_DOWNLOAD_AWAITING_TECHNICAL_AND_VISUAL_EVALUATION'
        source = 'Poly Haven official API and download host'
        source_url = 'https://polyhaven.com/'
        license = 'CC0-1.0'
        license_url = 'https://polyhaven.com/license'
        asset_count = $Records.Count
        assets = $Records
        side_effects = [ordered]@{
            unreal_launched = $false
            blender_launched = $false
            content_imported = $false
            runtime_promotion_performed = $false
        }
        next_gate = 'M01_POLYHAVEN_VEGETATION_QUARANTINE01_TECHNICAL_VISUAL_EVALUATION'
    }
    $ManifestPath = Join-Path $OutputRoot 'quarantine_manifest.json'
    $Manifest | ConvertTo-Json -Depth 100 | Set-Content -LiteralPath $ManifestPath -Encoding utf8
    Write-Output ($Manifest | ConvertTo-Json -Depth 8 -Compress)
    exit 0
}
catch {
    $Failure = [ordered]@{
        schema = 'skyguard.m01-polyhaven-vegetation-quarantine01-failure.v1'
        created_at_utc = [DateTime]::UtcNow.ToString('o')
        classification = 'FAILED_WITH_EVIDENCE'
        message = $_.Exception.Message
        unreal_launched = $false
        blender_launched = $false
        content_imported = $false
        runtime_promotion_performed = $false
    }
    $Failure | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $OutputRoot 'failure.json') -Encoding utf8
    [Console]::Error.WriteLine($_.Exception.ToString())
    exit 1
}
