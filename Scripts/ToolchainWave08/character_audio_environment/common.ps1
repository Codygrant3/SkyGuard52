Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-Sha256Lower {
    param([Parameter(Mandatory = $true)][string]$Path)
    $stream = $null
    $sha = $null
    try {
        $stream = [System.IO.File]::Open($Path, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::Read)
        $sha = [System.Security.Cryptography.SHA256]::Create()
        return ([System.BitConverter]::ToString($sha.ComputeHash($stream))).Replace('-', '').ToLowerInvariant()
    }
    finally {
        if ($null -ne $sha) { $sha.Dispose() }
        if ($null -ne $stream) { $stream.Dispose() }
    }
}

function Assert-Authority {
    param([Parameter(Mandatory = $true)]$Authority)
    $path = [string]$Authority.path
    if (-not [System.IO.File]::Exists($path)) { throw "Missing authority: $path" }
    $item = Get-Item -LiteralPath $path
    if ([int64]$item.Length -ne [int64]$Authority.bytes) { throw "Byte mismatch: $path" }
    $actual = Get-Sha256Lower -Path $path
    if ($actual -ne [string]$Authority.sha256) { throw "SHA-256 mismatch: $path" }
}

function Assert-NoHeavyProcess {
    $names = @('UnrealEditor', 'UnrealEditor-Cmd', 'Blender', 'ShaderCompileWorker', 'AutomationTool', 'UnrealBuildTool', 'cl', 'link')
    $active = @(Get-Process -ErrorAction SilentlyContinue | Where-Object { $names -contains $_.ProcessName })
    if ($active.Count -gt 0) {
        $summary = ($active | ForEach-Object { "$($_.ProcessName):$($_.Id)" }) -join ', '
        throw "Heavy process gate failed: $summary"
    }
}

function Set-PluginState {
    param(
        [Parameter(Mandatory = $true)]$Project,
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][bool]$Enabled
    )
    $plugins = @($Project.Plugins)
    $found = $false
    foreach ($entry in $plugins) {
        if ([string]$entry.Name -eq $Name) {
            $entry.Enabled = $Enabled
            $found = $true
        }
    }
    if (-not $found) {
        $Project.Plugins += [pscustomobject]@{ Name = $Name; Enabled = $Enabled }
    }
}

function Copy-TreeDeterministic {
    param(
        [Parameter(Mandatory = $true)][string]$Source,
        [Parameter(Mandatory = $true)][string]$Destination
    )
    if (-not [System.IO.Directory]::Exists($Source)) { return }
    [System.IO.Directory]::CreateDirectory($Destination) | Out-Null
    foreach ($directory in [System.IO.Directory]::EnumerateDirectories($Source, '*', [System.IO.SearchOption]::AllDirectories)) {
        $relative = $directory.Substring($Source.Length).TrimStart('\')
        [System.IO.Directory]::CreateDirectory((Join-Path $Destination $relative)) | Out-Null
    }
    foreach ($file in [System.IO.Directory]::EnumerateFiles($Source, '*', [System.IO.SearchOption]::AllDirectories)) {
        $relative = $file.Substring($Source.Length).TrimStart('\')
        $target = Join-Path $Destination $relative
        [System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName($target)) | Out-Null
        [System.IO.File]::Copy($file, $target, $false)
    }
}

function Get-FileInventory {
    param([Parameter(Mandatory = $true)][string]$Root)
    $records = @()
    if (-not [System.IO.Directory]::Exists($Root)) { return $records }
    foreach ($file in [System.IO.Directory]::EnumerateFiles($Root, '*', [System.IO.SearchOption]::AllDirectories)) {
        $item = Get-Item -LiteralPath $file
        $records += [ordered]@{
            relative_path = $file.Substring($Root.Length).TrimStart('\')
            bytes = [int64]$item.Length
            sha256 = Get-Sha256Lower -Path $file
        }
    }
    return $records
}

function Write-JsonAtomic {
    param([Parameter(Mandatory = $true)]$Value, [Parameter(Mandatory = $true)][string]$Path)
    $parent = [System.IO.Path]::GetDirectoryName($Path)
    [System.IO.Directory]::CreateDirectory($parent) | Out-Null
    $temporary = "$Path.tmp"
    $json = $Value | ConvertTo-Json -Depth 32
    [System.IO.File]::WriteAllText($temporary, $json + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
    Move-Item -LiteralPath $temporary -Destination $Path -Force
}

function Invoke-IsolatedViewPreparation {
    param(
        [Parameter(Mandatory = $true)][string]$ContractPath,
        [Parameter(Mandatory = $true)][bool]$Authorized,
        [Parameter(Mandatory = $true)][bool]$OfflineContractTest
    )
    $contract = Get-Content -LiteralPath $ContractPath -Raw | ConvertFrom-Json
    if ($OfflineContractTest) {
        foreach ($authority in $contract.authorities) { Assert-Authority -Authority $authority }
        if ([System.IO.Directory]::Exists([string]$contract.target_root)) { throw 'Governed target already exists.' }
        if ([System.IO.Directory]::Exists([string]$contract.attempt_root)) { throw 'Governed attempt already exists.' }
        return 0
    }
    if (-not $Authorized) { throw 'Explicit -AuthorizeSinglePrepare is required.' }

    $state = [ordered]@{
        schema = 'skyguard.toolchain-wave08.prepare-terminal.v1'
        lane = [string]$contract.lane
        started_at_utc = [DateTime]::UtcNow.ToString('o')
        completed_at_utc = $null
        classification = 'FAILED_WITH_EVIDENCE'
        target_created = $false
        attempt_created = $false
        unreal_launched = $false
        blender_launched = $false
        child_process_launches = 0
        retry_count = 0
        failure_stage = $null
        failure_message = $null
        canonical_uproject_pre_sha256 = $null
        canonical_uproject_post_sha256 = $null
        output_inventory = @()
    }
    $attemptRoot = [string]$contract.attempt_root
    $terminalPath = Join-Path $attemptRoot 'terminal_manifest.json'
    $externalTerminalPath = [string]$contract.terminal_report_path
    try {
        $state.failure_stage = 'preflight'
        foreach ($authority in $contract.authorities) { Assert-Authority -Authority $authority }
        Assert-NoHeavyProcess
        if ([System.IO.Directory]::Exists([string]$contract.target_root)) { throw 'Target root already exists.' }
        if ([System.IO.Directory]::Exists($attemptRoot)) { throw 'Attempt root already exists.' }
        if ([System.IO.File]::Exists($externalTerminalPath)) { throw 'Terminal report path already exists.' }

        [System.IO.Directory]::CreateDirectory($attemptRoot) | Out-Null
        $state.attempt_created = $true
        [System.IO.Directory]::CreateDirectory([string]$contract.target_root) | Out-Null
        $state.target_created = $true

        $canonicalProject = [string]$contract.canonical_uproject
        $state.canonical_uproject_pre_sha256 = Get-Sha256Lower -Path $canonicalProject
        $targetProject = Join-Path ([string]$contract.target_root) 'Skyguard52.uproject'
        $project = Get-Content -LiteralPath $canonicalProject -Raw | ConvertFrom-Json
        if ([bool]$contract.drop_runtime_modules) { $project.Modules = @() }
        foreach ($plugin in $contract.plugin_states.psobject.Properties) {
            Set-PluginState -Project $project -Name $plugin.Name -Enabled ([bool]$plugin.Value)
        }
        Write-JsonAtomic -Value $project -Path $targetProject

        Copy-TreeDeterministic -Source (Join-Path ([string]$contract.canonical_root) 'Config') -Destination (Join-Path ([string]$contract.target_root) 'Config')
        if ([bool]$contract.copy_source) { Copy-TreeDeterministic -Source (Join-Path ([string]$contract.canonical_root) 'Source') -Destination (Join-Path ([string]$contract.target_root) 'Source') }
        if ([bool]$contract.copy_plugins) { Copy-TreeDeterministic -Source (Join-Path ([string]$contract.canonical_root) 'Plugins') -Destination (Join-Path ([string]$contract.target_root) 'Plugins') }
        if ([bool]$contract.copy_binaries) { Copy-TreeDeterministic -Source (Join-Path ([string]$contract.canonical_root) 'Binaries') -Destination (Join-Path ([string]$contract.target_root) 'Binaries') }
        if ([bool]$contract.copy_content) {
            Copy-TreeDeterministic -Source (Join-Path ([string]$contract.canonical_root) 'Content') -Destination (Join-Path ([string]$contract.target_root) 'Content')
        }
        else {
            [System.IO.Directory]::CreateDirectory((Join-Path ([string]$contract.target_root) 'Content')) | Out-Null
        }

        $clone = Get-Content -LiteralPath $targetProject -Raw | ConvertFrom-Json
        foreach ($plugin in $contract.plugin_states.psobject.Properties) {
            $matches = @($clone.Plugins | Where-Object { [string]$_.Name -eq $plugin.Name })
            if ($matches.Count -ne 1 -or [bool]$matches[0].Enabled -ne [bool]$plugin.Value) {
                throw "Clone plugin state mismatch: $($plugin.Name)"
            }
        }
        $state.canonical_uproject_post_sha256 = Get-Sha256Lower -Path $canonicalProject
        if ($state.canonical_uproject_pre_sha256 -ne $state.canonical_uproject_post_sha256) { throw 'Canonical project descriptor changed.' }
        $state.output_inventory = @(Get-FileInventory -Root ([string]$contract.target_root))
        $state.classification = [string]$contract.success_classification
        $state.failure_stage = $null
    }
    catch {
        $state.failure_message = $_.Exception.Message
        throw
    }
    finally {
        $state.completed_at_utc = [DateTime]::UtcNow.ToString('o')
        try {
            Write-JsonAtomic -Value $state -Path $externalTerminalPath
            if ($state.attempt_created) { Write-JsonAtomic -Value $state -Path $terminalPath }
        }
        catch {
            $emergency = Join-Path ([string]$contract.evidence_root) "$($contract.lane)_prepare_emergency.jsonl"
            $entry = [ordered]@{ timestamp_utc = [DateTime]::UtcNow.ToString('o'); lane = $contract.lane; message = $_.Exception.Message }
            [System.IO.File]::AppendAllText($emergency, (($entry | ConvertTo-Json -Compress) + [Environment]::NewLine), [System.Text.UTF8Encoding]::new($false))
        }
    }
    return 0
}
