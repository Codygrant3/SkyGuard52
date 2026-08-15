<#
.SYNOPSIS
Creates an M01 soak-scaffold receipt and optionally launches an existing Development package.

.DESCRIPTION
Defaults to validation-only behavior. The script reads M01 from the Phase 8 mission
soak matrix, discovers the newest Skyguard52.exe below the Phase 8 Development
archive layout, and always writes JSON evidence under Saved\Reports\SoakScaffold.
It does not require a packaged executable to exist.

Use -Launch together with -AuthorizeSinglePackagedGame to explicitly request one
bounded packaged-game launch. No Unreal Editor, packaging, compiler, or build tool
is invoked by this script.

.PARAMETER ProjectRoot
Canonical Skyguard52 project root. Defaults to D:\Skyguard52.

.PARAMETER MissionMatrix
Phase 8 mission soak matrix JSON. M01 is selected from this file.

.PARAMETER Executable
Optional explicit packaged Skyguard52.exe. When omitted, the newest Development
executable under Saved\Releases\Phase8 is discovered.

.PARAMETER BenchmarkSeconds
Packaged-game benchmark duration passed as -benchmarkseconds. Defaults to 60.

.PARAMETER Launch
Explicitly requests the short packaged-game scaffold. Without this switch the
script performs validation only, even when an executable is present.

.PARAMETER AuthorizeSinglePackagedGame
Mechanical one-shot guard required with -Launch after standing-authorization and
one-heavy-process readiness checks pass.

.EXAMPLE
.\Scripts\run_skyguard_m01_soak_scaffold.ps1

.EXAMPLE
.\Scripts\run_skyguard_m01_soak_scaffold.ps1 -Launch -AuthorizeSinglePackagedGame -BenchmarkSeconds 60
#>
[CmdletBinding()]
param(
    [string]$ProjectRoot = 'D:\Skyguard52',
    [string]$MissionMatrix = 'D:\Skyguard52\Docs\AAA_Review\PHASE8_MISSION_SOAK_MATRIX.json',
    [string]$Executable = '',
    [ValidateRange(10, 600)]
    [int]$BenchmarkSeconds = 60,
    [switch]$Launch,
    [switch]$AuthorizeSinglePackagedGame
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ReportsRoot = Join-Path $ProjectRoot 'Saved\Reports\SoakScaffold'
$Phase8Root = Join-Path $ProjectRoot 'Saved\Releases\Phase8'
$Authorization = Join-Path $ProjectRoot 'Production\standing_heavy_process_authorization.json'
$stamp = [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffZ')
$Receipt = Join-Path $ReportsRoot "M01_SOAK_SCAFFOLD_$stamp.json"

function Write-JsonAtomic([string]$Path, [object]$Value) {
    [IO.Directory]::CreateDirectory((Split-Path -Parent $Path)) | Out-Null
    $temporary = $Path + '.tmp.' + [Diagnostics.Process]::GetCurrentProcess().Id
    [IO.File]::WriteAllText($temporary, (($Value | ConvertTo-Json -Depth 30) + [Environment]::NewLine), [Text.UTF8Encoding]::new($false))
    if (Test-Path -LiteralPath $Path) { throw "Refusing to overwrite soak scaffold evidence: $Path" }
    [IO.File]::Move($temporary, $Path)
}

function Find-DevelopmentExecutable {
    if (-not (Test-Path -LiteralPath $Phase8Root -PathType Container)) { return $null }
    return Get-ChildItem -LiteralPath $Phase8Root -Recurse -File -Filter 'Skyguard52.exe' -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -match '[\\/]packages[\\/]Development[\\/]' -and $_.FullName -match '[\\/]Windows[\\/]' } |
        Sort-Object -Property @{ Expression = 'LastWriteTimeUtc'; Descending = $true }, FullName |
        Select-Object -First 1
}

function Get-HeavyProcesses {
    $names = @('Blender', 'UnrealEditor', 'UnrealEditor-Cmd', 'ShaderCompileWorker', 'AutomationTool', 'UnrealBuildTool', 'Skyguard52', 'cl', 'link', 'dotnet')
    @(Get-Process -ErrorAction SilentlyContinue | Where-Object {
            $names -contains $_.ProcessName -or $_.ProcessName -like 'UnrealEditor*' -or $_.ProcessName -like 'ShaderCompileWorker*'
        } | Select-Object ProcessName, Id, StartTime, CPU, WorkingSet64)
}

$State = [ordered]@{
    schema = 'skyguard.m01.soak-scaffold.v1'
    classification = 'FAILED_WITH_EVIDENCE'
    created_at_utc = [DateTime]::UtcNow.ToString('o')
    completed_at_utc = $null
    validation_only = -not [bool]$Launch
    launch_requested = [bool]$Launch
    mechanical_guard_supplied = [bool]$AuthorizeSinglePackagedGame
    benchmark_seconds = $BenchmarkSeconds
    mission_matrix = $MissionMatrix
    mission = $null
    discovery_root = $Phase8Root
    executable_source = $null
    executable = $null
    executable_present = $false
    arguments = @()
    heavy_processes_before = @()
    packaged_game_launch_count = 0
    retry_count = 0
    pid = $null
    exit_code = $null
    timed_out = $false
    stdout = $null
    stderr = $null
    receipt = $Receipt
    error = $null
}

$Exit = 1
try {
    if (-not (Test-Path -LiteralPath $MissionMatrix -PathType Leaf)) {
        throw "Mission matrix missing: $MissionMatrix"
    }
    $matrix = Get-Content -LiteralPath $MissionMatrix -Raw | ConvertFrom-Json
    $mission = @($matrix.missions | Where-Object { $_.id -eq 'M01' })
    if ($mission.Count -ne 1) { throw "Phase 8 matrix must contain exactly one M01 entry; observed $($mission.Count)." }
    $State.mission = [ordered]@{
        id = [string]$mission[0].id
        name = [string]$mission[0].name
        map = [string]$mission[0].map
        matrix_status = [string]$mission[0].status
        matrix_soak_seconds = [int]$mission[0].soak_seconds
    }

    $exeItem = $null
    if (-not [string]::IsNullOrWhiteSpace($Executable)) {
        $State.executable_source = 'explicit_parameter'
        if (Test-Path -LiteralPath $Executable -PathType Leaf) {
            $exeItem = Get-Item -LiteralPath $Executable
        }
        else {
            $State.executable = $Executable
        }
    }
    else {
        $State.executable_source = 'phase8_development_archive_discovery'
        $exeItem = Find-DevelopmentExecutable
    }
    if ($null -ne $exeItem) {
        $State.executable = $exeItem.FullName
        $State.executable_present = $true
    }

    $State.arguments = @(
        [string]$State.mission.map,
        '-benchmark',
        "-benchmarkseconds=$BenchmarkSeconds",
        '-SkyguardCombatPerf',
        '-unattended',
        '-nosplash',
        '-stdout'
    )

    if (-not $Launch) {
        $State.classification = if ($State.executable_present) {
            'VALIDATED_EXECUTABLE_PRESENT_NOT_LAUNCHED'
        } else {
            'VALIDATED_ABSENT_EXECUTABLE_NOT_LAUNCHED'
        }
        $Exit = 0
        return
    }
    if (-not $State.executable_present) {
        $State.classification = 'VALIDATED_LAUNCH_REQUESTED_BUT_EXECUTABLE_ABSENT'
        $Exit = 0
        return
    }
    if (-not $AuthorizeSinglePackagedGame) {
        $State.classification = 'REFUSED_MISSING_MECHANICAL_GUARD'
        $Exit = 2
        throw 'Supply -AuthorizeSinglePackagedGame with -Launch after readiness passes.'
    }
    if (-not (Test-Path -LiteralPath $Authorization -PathType Leaf)) {
        throw "Standing authorization missing: $Authorization"
    }
    $standing = Get-Content -LiteralPath $Authorization -Raw | ConvertFrom-Json
    if ($standing.status -ne 'ACTIVE' -or $standing.execution_policy.per_run_user_authorization_required -ne $false) {
        throw 'Standing heavy-process authorization is not active.'
    }
    if ($standing.execution_policy.one_heavy_process_at_a_time -ne $true -or [int]$standing.execution_policy.automatic_retry_count -ne 0) {
        throw 'Standing authorization process/retry policy is invalid.'
    }
    $State.heavy_processes_before = @(Get-HeavyProcesses)
    if ($State.heavy_processes_before.Count -ne 0) {
        throw "Heavy process gate failed: $($State.heavy_processes_before.ProcessName -join ', ')"
    }

    $stdout = Join-Path $ReportsRoot "M01_SOAK_SCAFFOLD_$stamp.stdout.log"
    $stderr = Join-Path $ReportsRoot "M01_SOAK_SCAFFOLD_$stamp.stderr.log"
    $State.stdout = $stdout
    $State.stderr = $stderr
    $process = Start-Process -FilePath $State.executable -ArgumentList $State.arguments -WorkingDirectory (Split-Path -Parent $State.executable) -RedirectStandardOutput $stdout -RedirectStandardError $stderr -WindowStyle Hidden -PassThru
    $State.packaged_game_launch_count = 1
    $State.pid = [int]$process.Id
    $null = $process.Handle
    $deadline = [DateTime]::UtcNow.AddSeconds($BenchmarkSeconds + 90)
    while (-not $process.HasExited -and [DateTime]::UtcNow -lt $deadline) {
        Start-Sleep -Seconds 2
        $process.Refresh()
    }
    if (-not $process.HasExited) {
        $State.timed_out = $true
        try { $process.Kill() } catch {}
        throw 'Packaged M01 soak scaffold exceeded its benchmark timeout.'
    }
    $process.WaitForExit(); $process.Refresh()
    $State.exit_code = [int]$process.ExitCode
    if ($State.exit_code -ne 0) { throw "Packaged M01 scaffold returned exit code $($State.exit_code)." }
    $State.classification = 'PASSED_M01_PACKAGED_SOAK_SCAFFOLD'
    $Exit = 0
}
catch {
    $State.error = $_.Exception.Message
    if ($State.classification -ne 'REFUSED_MISSING_MECHANICAL_GUARD') {
        $State.classification = 'FAILED_WITH_EVIDENCE'
        $Exit = 1
    }
}
finally {
    $State.completed_at_utc = [DateTime]::UtcNow.ToString('o')
    Write-JsonAtomic $Receipt $State
}

$State | ConvertTo-Json -Depth 30
[Environment]::Exit([int]$Exit)
