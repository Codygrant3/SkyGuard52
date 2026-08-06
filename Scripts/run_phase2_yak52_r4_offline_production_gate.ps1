[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$ReportRoot = Join-Path $ProjectRoot "Saved\Reports"
$ReceiptPath = Join-Path $ReportRoot "PHASE2_YAK52_R4_OFFLINE_PRODUCTION_GATE.json"
$StartedAt = [DateTime]::UtcNow

New-Item -ItemType Directory -Path $ReportRoot -Force | Out-Null

$Verifier = Join-Path $PSScriptRoot "verify_phase2_yak52_r4_offline_production_contract.py"
$Tests = Join-Path $PSScriptRoot "tests\test_phase2_yak52_r4_offline_production_contract.py"
$Commands = @(
    @{
        Name = "python_compile"
        Executable = "python"
        Arguments = @("-m", "py_compile", $Verifier, $Tests)
    },
    @{
        Name = "r4_offline_contract"
        Executable = "python"
        Arguments = @($Verifier, "--no-write")
    },
    @{
        Name = "mutation_tests"
        Executable = "python"
        Arguments = @("-m", "unittest", $Tests)
    }
)

$Results = @()
foreach ($Command in $Commands) {
    $PreviousErrorPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $Executable = [string]$Command.Executable
    $Output = & $Executable @($Command.Arguments) 2>&1
    $ExitCode = $LASTEXITCODE
    $ErrorActionPreference = $PreviousErrorPreference
    $Results += [ordered]@{
        name = $Command.Name
        exit_code = $ExitCode
        passed = ($ExitCode -eq 0)
        output = @(
            $Output |
                ForEach-Object {
                    $Line = "$_"
                    if ($Line -ne "System.Management.Automation.RemoteException") {
                        $Line
                    }
                }
        )
    }
}

$Passed = ($Results | Where-Object { -not $_.passed }).Count -eq 0
$Receipt = [ordered]@{
    schema = "skyguard.phase2.yak52-r4-offline-production-gate.v1"
    status = if ($Passed) {
        "PASS_R4_OFFLINE_CONTRACT_PRODUCTION_NOT_STARTED"
    } else {
        "FAIL_R4_OFFLINE_CONTRACT"
    }
    started_at_utc = $StartedAt.ToString("o")
    completed_at_utc = [DateTime]::UtcNow.ToString("o")
    project_root = $ProjectRoot
    blender_process_launched = $false
    unreal_process_launched = $false
    accepted_assets_modified = $false
    r4_source_created = $false
    r4_export_created = $false
    r4_imported = $false
    runtime_replaced = $false
    final = $false
    aaa = $false
    production_ready = $false
    shipping_allowed = $false
    checks = $Results
}

$Receipt | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $ReceiptPath -Encoding utf8
$Receipt | ConvertTo-Json -Depth 8

if (-not $Passed) {
    exit 2
}
