param([switch]$AuthorizeSingleReadOnlyProbe)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Project = 'D:\SG52T08_ENV01\Skyguard52.uproject'
$Editor = 'D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$Probe = 'D:\Skyguard52\Scripts\ToolchainWave08\m01_visible_environment_stage04_recovery01\probe_failed_stage04_import_slots.py'
$Attempt = 'D:\Skyguard52\Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_STAGE04_RECOVERY01_IMPORT_PROBE01\attempt_01'
$Terminal = 'D:\Skyguard52\Saved\Reports\M01_VISIBLE_ENVIRONMENT_STAGE04_RECOVERY01_IMPORT_PROBE01_TERMINAL.json'

function Get-Heavy {
    @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {
        $_.Name -match '^(UnrealEditor(-Cmd)?|Blender|ShaderCompileWorker|AutomationTool|UnrealBuildTool|cl|link)(\.exe)?$'
    } | Select-Object ProcessId,Name,CommandLine)
}

if (-not $AuthorizeSingleReadOnlyProbe) { throw 'Mechanical authorization guard missing' }
if ((Test-Path -LiteralPath $Attempt) -or (Test-Path -LiteralPath $Terminal)) { throw 'Fresh probe namespace exists' }
if (@(Get-Heavy).Count -ne 0) { throw 'Heavy process active' }
New-Item -ItemType Directory -Path $Attempt | Out-Null
$stdout=Join-Path $Attempt 'unreal.stdout.log'; $stderr=Join-Path $Attempt 'unreal.stderr.log'; $engine=Join-Path $Attempt 'unreal.engine.log'
$args=@($Project,'-Unattended','-NoSplash','-NoSound','-NullRHI','-NoSaveOnExit','-stdout','-FullStdOutLogOutput','-nop4','-DisablePlugins=Fab,Bridge,EditorTelemetry,RuntimeTelemetry,EOSShared',"-ExecutePythonScript=$Probe",'-ScriptErrorsAreFatal',"-abslog=$engine")
$state=[ordered]@{classification='FAILED_WITH_EVIDENCE';unreal_launch_count=0;retry_count=0;pid=$null;exit_code=$null;exit_code_type=$null;receipt=$null;failure=$null}
try {
    $p=Start-Process -FilePath $Editor -ArgumentList $args -WorkingDirectory 'D:\SG52T08_ENV01' -PassThru -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError $stderr
    $state.unreal_launch_count=1; $state.pid=$p.Id; $handle=$p.Handle
    if($null -eq $handle){throw 'Native process handle missing'}
    if(-not $p.WaitForExit(1200000)){Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue;throw 'Probe timed out'}
    $p.Refresh(); $state.exit_code=[int]$p.ExitCode; $state.exit_code_type=$p.ExitCode.GetType().FullName
    if($state.exit_code -ne 0){throw "Probe failed: $($state.exit_code)"}
    $receipt=Join-Path $Attempt 'import_slot_probe.json'; if(-not (Test-Path -LiteralPath $receipt)){throw 'Receipt missing'}
    $payload=Get-Content -LiteralPath $receipt -Raw | ConvertFrom-Json
    if($payload.classification -ne 'PASSED_FAILED_IMPORT_SLOT_EVIDENCE_READY_FOR_STAGE04_RECOVERY01'){throw "Receipt failed: $($payload.classification)"}
    $state.receipt=$receipt; $state.classification=$payload.classification
} catch {$state.failure=$_.Exception.Message}
finally {
    [System.IO.File]::WriteAllText($Terminal,($state|ConvertTo-Json -Depth 16)+[Environment]::NewLine,[System.Text.UTF8Encoding]::new($false))
}
$state|ConvertTo-Json -Depth 16
if($state.classification -notlike 'PASSED_*'){[Environment]::Exit([int]1)}
[Environment]::Exit([int]0)
