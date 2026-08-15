[CmdletBinding()]
param(
    [switch]$OfflineContractTest
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$BlockedNames = @(
    'UnrealEditor',
    'UnrealEditor-Cmd',
    'Blender',
    'ShaderCompileWorker',
    'AutomationTool',
    'UnrealBuildTool',
    'dotnet',
    'MSBuild',
    'cl',
    'link'
)

function Get-BlockedRows($Rows) {
    return @(
        $Rows | Where-Object { $BlockedNames -contains [string]$_.ProcessName }
    )
}

function Write-Result($Value) {
    [Console]::Out.WriteLine(($Value | ConvertTo-Json -Depth 8 -Compress))
}

if ($OfflineContractTest) {
    $clearFixture = @(
        [pscustomobject]@{ ProcessName = 'codex'; Id = 101 },
        [pscustomobject]@{ ProcessName = 'blender-mcp'; Id = 102 }
    )
    if (@(Get-BlockedRows $clearFixture).Count -ne 0) {
        throw 'The clear fixture was incorrectly classified as busy.'
    }
    foreach ($requiredName in $BlockedNames) {
        $fixture = @([pscustomobject]@{ ProcessName = $requiredName; Id = 200 })
        $blocked = @(Get-BlockedRows $fixture)
        if ($blocked.Count -ne 1 -or [string]$blocked[0].ProcessName -cne $requiredName) {
            throw "Required heavy process was not blocked: $requiredName"
        }
    }
    Write-Result ([ordered]@{
        schema = 'skyguard.shared-heavy-process-quiescence01.offline-contract.v1'
        classification = 'PASS_OFFLINE_CONTRACT_TEST'
        blocked_name_count = $BlockedNames.Count
        required_names = $BlockedNames
        blender_mcp_blocked = $false
        child_process_launch_count = 0
        filesystem_write_count = 0
    })
    [Environment]::Exit([int]0)
}

$processRows = @(
    Get-Process -ErrorAction SilentlyContinue | ForEach-Object {
        $startTime = $null
        $cpuSeconds = $null
        $workingSet = $null
        try { $startTime = $_.StartTime.ToUniversalTime().ToString('o') } catch {}
        try { $cpuSeconds = [double]$_.CPU } catch {}
        try { $workingSet = [int64]$_.WorkingSet64 } catch {}
        [pscustomobject]@{
            ProcessName = [string]$_.ProcessName
            Id = [int]$_.Id
            StartTime = $startTime
            CPU = $cpuSeconds
            WorkingSet64 = $workingSet
        }
    }
)
$blockedRows = @(Get-BlockedRows $processRows)
$clear = $blockedRows.Count -eq 0
Write-Result ([ordered]@{
    schema = 'skyguard.shared-heavy-process-quiescence01.live-result.v1'
    classification = if ($clear) { 'PASS_HEAVY_PROCESS_GATE_CLEAR' } else { 'FAILED_HEAVY_PROCESS_GATE_BUSY' }
    at_utc = [DateTime]::UtcNow.ToString('o')
    blocked_name_count = $BlockedNames.Count
    active_heavy_process_count = $blockedRows.Count
    active_heavy_processes = $blockedRows
    blender_mcp_is_not_a_governed_heavy_process = $true
    read_only = $true
})

if ($clear) {
    [Environment]::Exit([int]0)
}
[Environment]::Exit([int]4)
