[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$ReportRoot = Join-Path $ProjectRoot "Saved\Reports"
$ReceiptPath = Join-Path $ReportRoot "PHASE5_AUDIO_OFFLINE_READINESS_GATE.json"
$StartedAt = [DateTime]::UtcNow

New-Item -ItemType Directory -Path $ReportRoot -Force | Out-Null

$Commands = @(
    @{
        Name = "host_audio_diagnostic"
        Executable = "powershell"
        Arguments = @(
            "-NoProfile", "-ExecutionPolicy", "Bypass",
            "-File", (Join-Path $PSScriptRoot "collect_phase5_host_audio_diagnostics.ps1")
        )
    },
    @{
        Name = "python_compile"
        Executable = "python"
        Arguments = @(
            "-m", "py_compile",
            (Join-Path $PSScriptRoot "verify_phase5_authentic_source_acquisition_contract.py"),
            (Join-Path $PSScriptRoot "verify_phase5_authentic_audio_acquisition.py"),
            (Join-Path $PSScriptRoot "verify_phase5_audio_acquisition_contract.py"),
            (Join-Path $PSScriptRoot "verify_phase5_audio_production_readiness.py"),
            (Join-Path $PSScriptRoot "verify_phase5_audio_shipping_boundary.py"),
            (Join-Path $PSScriptRoot "verify_phase5_audio_runtime_routing_readiness.py"),
            (Join-Path $PSScriptRoot "verify_phase5_metasound_topology_contract.py"),
            (Join-Path $PSScriptRoot "build_skyguard_phase5_metasound_topology.py"),
            (Join-Path $PSScriptRoot "verify_skyguard_phase5_metasound_topology.py"),
            (Join-Path $PSScriptRoot "test_phase5_authentic_source_acquisition_contract.py"),
            (Join-Path $PSScriptRoot "test_phase5_authentic_audio_acquisition.py"),
            (Join-Path $PSScriptRoot "test_phase5_audio_production_readiness.py"),
            (Join-Path $PSScriptRoot "test_phase5_audio_shipping_boundary.py"),
            (Join-Path $PSScriptRoot "test_phase5_audio_runtime_routing_readiness.py"),
            (Join-Path $PSScriptRoot "test_phase5_routing_primitive_authoring.py"),
            (Join-Path $PSScriptRoot "test_phase5_metasound_topology_authoring.py")
        )
    },
    @{
        Name = "immutable_authentic_source_acquisition_contract"
        Executable = "python"
        Arguments = @(
            (Join-Path $PSScriptRoot "verify_phase5_authentic_source_acquisition_contract.py"),
            "--no-write"
        )
    },
    @{
        Name = "authentic_acquisition_contract"
        Executable = "python"
        Arguments = @(
            (Join-Path $PSScriptRoot "verify_phase5_authentic_audio_acquisition.py")
        )
    },
    @{
        Name = "category_provenance_contract"
        Executable = "python"
        Arguments = @(
            (Join-Path $PSScriptRoot "verify_phase5_audio_acquisition_contract.py")
        )
    },
    @{
        Name = "unified_production_readiness"
        Executable = "python"
        Arguments = @(
            (Join-Path $PSScriptRoot "verify_phase5_audio_production_readiness.py")
        )
    },
    @{
        Name = "shipping_boundary_audit_only"
        Executable = "python"
        Arguments = @(
            (Join-Path $PSScriptRoot "verify_phase5_audio_shipping_boundary.py"),
            "--audit-only"
        )
    },
    @{
        Name = "runtime_routing_readiness_audit"
        Executable = "python"
        Arguments = @(
            (Join-Path $PSScriptRoot "verify_phase5_audio_runtime_routing_readiness.py")
        )
    },
    @{
        Name = "mutation_tests"
        Executable = "python"
        Arguments = @(
            "-m", "unittest",
            (Join-Path $PSScriptRoot "test_phase5_authentic_source_acquisition_contract.py"),
            (Join-Path $PSScriptRoot "test_phase5_authentic_audio_acquisition.py"),
            (Join-Path $PSScriptRoot "test_phase5_audio_production_readiness.py"),
            (Join-Path $PSScriptRoot "test_phase5_audio_shipping_boundary.py"),
            (Join-Path $PSScriptRoot "test_phase5_p5a_audio_routing_contract.py"),
            (Join-Path $PSScriptRoot "test_phase5_p5a_identity_source_evidence.py"),
            (Join-Path $PSScriptRoot "test_phase5_audio_runtime_routing_readiness.py"),
            (Join-Path $PSScriptRoot "test_phase5_routing_primitive_authoring.py"),
            (Join-Path $PSScriptRoot "test_phase5_metasound_topology_authoring.py")
        )
    }
)

$Results = @()
foreach ($Command in $Commands) {
    # Windows PowerShell wraps native stderr as ErrorRecord objects. Unittest
    # writes successful progress to stderr, so capture both streams and judge
    # the native process only by its exit code.
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
    schema = "skyguard.phase5.audio-offline-readiness-gate.v1"
    status = if ($Passed) {
        "PASS_CONTRACT_VALID_AUTHENTIC_SOURCES_AND_AUDIBLE_ACCEPTANCE_REQUIRED"
    } else {
        "FAIL_OFFLINE_CONTRACT"
    }
    started_at_utc = $StartedAt.ToString("o")
    completed_at_utc = [DateTime]::UtcNow.ToString("o")
    project_root = $ProjectRoot
    engine_process_launched = $false
    media_downloaded = $false
    media_imported = $false
    production_ready = $false
    checks = $Results
}

$Receipt | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $ReceiptPath -Encoding utf8
$Receipt | ConvertTo-Json -Depth 8

if (-not $Passed) {
    exit 2
}
