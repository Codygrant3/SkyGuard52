[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$Project = 'D:\Skyguard52\Skyguard52.uproject'
$Unreal = 'D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$BuildScript = 'D:\Skyguard52\Scripts\build_skyguard_phase2_yak_runtime_validation.py'
$VerifyScript = 'D:\Skyguard52\Scripts\verify_skyguard_phase2_yak_runtime_persistence.py'
$LogDir = 'D:\Skyguard52\Saved\Logs'

$active = Get-CimInstance Win32_Process |
    Where-Object {
        $_.Name -like 'UnrealEditor*' -and
        $_.CommandLine -like '*Skyguard52*'
    }
if ($active) {
    $ids = ($active.ProcessId | Sort-Object) -join ', '
    throw "Refusing to duplicate an active Skyguard Unreal process: $ids"
}

New-Item -ItemType Directory -Path $LogDir -Force | Out-Null

function Invoke-CheckedUnrealPython {
    param(
        [Parameter(Mandatory = $true)][string]$Script,
        [Parameter(Mandatory = $true)][string]$Stem
    )

    $stdout = Join-Path $LogDir "$Stem.stdout.log"
    $stderr = Join-Path $LogDir "$Stem.stderr.log"
    $arguments = (
        '"' + $Project + '" ' +
        '"-ExecutePythonScript=' + $Script + '" ' +
        '-unattended -nop4 -nosplash -NullRHI -stdout -FullStdOutLogOutput'
    )
    $process = Start-Process -FilePath $Unreal -ArgumentList $arguments `
        -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru
    if (-not $process.WaitForExit(180000)) {
        Stop-Process -Id $process.Id -Force
        throw "$Stem exceeded its 180-second hard timeout"
    }
    # The timed WaitForExit overload can return before redirected stream
    # handlers finish and before ExitCode is populated. Complete the wait
    # before applying semantic exit validation.
    $process.WaitForExit()
    $process.Refresh()
    $pythonErrors = @(
        Select-String -LiteralPath $stdout -Pattern 'LogPython: Error:' -SimpleMatch
    ).Count
    $fatalErrors = @(
        Select-String -LiteralPath $stdout -Pattern 'Fatal error' -SimpleMatch
    ).Count
    $normalExit = @(
        Select-String -LiteralPath $stdout -Pattern 'LogExit: Exiting.' -SimpleMatch
    ).Count -gt 0
    $observedExitCode = $process.ExitCode
    $nonZeroExit = $null -ne $observedExitCode -and $observedExitCode -ne 0
    if ($nonZeroExit -or $pythonErrors -gt 0 -or $fatalErrors -gt 0 -or -not $normalExit) {
        throw "$Stem failed: exit=$observedExitCode, normal_exit=$normalExit, python_errors=$pythonErrors, fatal_errors=$fatalErrors"
    }
}

Invoke-CheckedUnrealPython -Script $BuildScript -Stem 'Phase2YakRuntimeBuild'
Invoke-CheckedUnrealPython -Script $VerifyScript -Stem 'Phase2YakRuntimePersistence'

$build = Get-Content 'D:\Skyguard52\Saved\Reports\PHASE2_YAK_RUNTIME_BUILD.json' -Raw |
    ConvertFrom-Json
$persistence = Get-Content 'D:\Skyguard52\Saved\Reports\PHASE2_YAK_RUNTIME_PERSISTENCE.json' -Raw |
    ConvertFrom-Json
if ($build.gate -ne 'PASS' -or $persistence.gate -ne 'PASS') {
    throw "Phase 2 Yak runtime gate is not green"
}

Write-Output 'PHASE2_YAK_RUNTIME_GATE=PASS'
