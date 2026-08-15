Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
. (Join-Path (Split-Path -Parent $PSScriptRoot) 'common.ps1')

$testRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("SkyguardT08OfflineTest_" + [Guid]::NewGuid().ToString('N'))
try {
    $canonical = Join-Path $testRoot 'canonical'
    $target = Join-Path $testRoot 'target'
    $attempt = Join-Path $testRoot 'attempt'
    $reports = Join-Path $testRoot 'reports'
    [System.IO.Directory]::CreateDirectory((Join-Path $canonical 'Config')) | Out-Null
    [System.IO.File]::WriteAllText((Join-Path $canonical 'Config\DefaultEngine.ini'), "[OfflineTest]`nValue=True`n", [System.Text.UTF8Encoding]::new($false))
    $projectPath = Join-Path $canonical 'Skyguard52.uproject'
    $project = [ordered]@{
        FileVersion = 3
        Plugins = @([ordered]@{ Name = 'PythonScriptPlugin'; Enabled = $false })
        Modules = @([ordered]@{ Name = 'Skyguard52'; Type = 'Runtime'; LoadingPhase = 'Default' })
    }
    Write-JsonAtomic -Value $project -Path $projectPath
    $projectItem = Get-Item -LiteralPath $projectPath
    $contractPath = Join-Path $testRoot 'contract.json'
    $contract = [ordered]@{
        schema = 'skyguard.toolchain-wave08.isolated-view-contract.v1'
        lane = 'offline_fixture'
        canonical_root = $canonical
        canonical_uproject = $projectPath
        target_root = $target
        attempt_root = $attempt
        evidence_root = $reports
        terminal_report_path = (Join-Path $reports 'terminal.json')
        copy_content = $false
        copy_source = $false
        copy_plugins = $false
        copy_binaries = $false
        drop_runtime_modules = $true
        success_classification = 'PASSED_ISOLATED_OFFLINE_FIXTURE'
        plugin_states = [ordered]@{ PythonScriptPlugin = $true; Water = $false }
        authorities = @([ordered]@{ path = $projectPath; bytes = [int64]$projectItem.Length; sha256 = (Get-Sha256Lower -Path $projectPath) })
    }
    Write-JsonAtomic -Value $contract -Path $contractPath
    $before = Get-Sha256Lower -Path $projectPath
    $code = Invoke-IsolatedViewPreparation -ContractPath $contractPath -Authorized $true -OfflineContractTest $false
    if ($code -ne 0) { throw "Unexpected result: $code" }
    $after = Get-Sha256Lower -Path $projectPath
    if ($before -ne $after) { throw 'Fixture canonical project changed.' }
    $clone = Get-Content -LiteralPath (Join-Path $target 'Skyguard52.uproject') -Raw | ConvertFrom-Json
    if (@($clone.Modules).Count -ne 0) { throw 'Runtime modules were not dropped.' }
    $python = @($clone.Plugins | Where-Object { $_.Name -eq 'PythonScriptPlugin' })
    $water = @($clone.Plugins | Where-Object { $_.Name -eq 'Water' })
    if ($python.Count -ne 1 -or -not [bool]$python[0].Enabled) { throw 'Python state failed.' }
    if ($water.Count -ne 1 -or [bool]$water[0].Enabled) { throw 'Water state failed.' }
    $terminal = Get-Content -LiteralPath (Join-Path $reports 'terminal.json') -Raw | ConvertFrom-Json
    if ($terminal.classification -ne 'PASSED_ISOLATED_OFFLINE_FIXTURE') { throw 'Terminal classification failed.' }
    if ([int]$terminal.child_process_launches -ne 0 -or [int]$terminal.retry_count -ne 0) { throw 'Execution counters failed.' }
    'OFFLINE_COMMON_CONTRACT_TEST_PASS'
}
finally {
    $tempRoot = [System.IO.Path]::GetFullPath([System.IO.Path]::GetTempPath())
    $resolvedTest = [System.IO.Path]::GetFullPath($testRoot)
    if ($resolvedTest.StartsWith($tempRoot, [System.StringComparison]::OrdinalIgnoreCase) -and [System.IO.Directory]::Exists($resolvedTest)) {
        Remove-Item -LiteralPath $resolvedTest -Recurse -Force
    }
}
