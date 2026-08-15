param([switch]$AuthorizeSingleUnreal)

$ErrorActionPreference='Stop'
$Root='D:\Skyguard52'
$Editor='D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$Project='D:\SG52T08_ENV01\Skyguard52.uproject'
$Script=Join-Path $Root 'Scripts\ToolchainWave08\environment_realism_stack_pivot01\runtime_probe_recovery01\probe_landscape_grounding_runtime_recovery01.py'
$Attempt=Join-Path $Root 'Saved\BuildAttempts\M01_LANDSCAPE_GROUNDING_BRIDGE01_RUNTIME_PROBE_RECOVERY01\attempt_01'
$Receipt=Join-Path $Attempt 'runtime_probe_receipt.json'
$Terminal=Join-Path $Root 'Saved\Reports\M01_LANDSCAPE_GROUNDING_BRIDGE01_RUNTIME_PROBE_RECOVERY01_TERMINAL_MANIFEST.json'

function Get-Hash([string]$Path){$s=$null;$h=$null;try{$s=[IO.File]::Open($Path,'Open','Read','Read');$h=[Security.Cryptography.SHA256]::Create();return([BitConverter]::ToString($h.ComputeHash($s))).Replace('-','').ToLowerInvariant()}finally{if($null-ne$h){$h.Dispose()};if($null-ne$s){$s.Dispose()}}}
function Assert-File([string]$Path,[int64]$Bytes,[string]$Hash){if(-not[IO.File]::Exists($Path)){throw"Missing authority: $Path"};$i=Get-Item -LiteralPath $Path;if($i.Length-ne$Bytes-or(Get-Hash $Path)-ne$Hash){throw"Authority mismatch: $Path"}}
function Write-Json([string]$Path,[object]$Value){$parent=Split-Path -Parent $Path;if(-not[IO.Directory]::Exists($parent)){[IO.Directory]::CreateDirectory($parent)|Out-Null};$tmp=$Path+'.tmp';[IO.File]::WriteAllText($tmp,($Value|ConvertTo-Json -Depth 12)+[Environment]::NewLine,[Text.UTF8Encoding]::new($false));[IO.File]::Move($tmp,$Path)}

$State=[ordered]@{schema='skyguard.m01-landscape-grounding-bridge01.runtime-probe-recovery01-supervisor.v1';classification='FAILED_WITH_EVIDENCE';started_utc=[DateTime]::UtcNow.ToString('o');ended_utc=$null;stage='initializing';authorization_present=[bool]$AuthorizeSingleUnreal;preflight_passed=$false;supervisor_launch_count=1;unreal_launch_count=0;retry_count=0;pid=$null;exit_code=$null;exit_code_type=$null;timeout=$false;crash=$false;peak_working_set_bytes=0;receipt_classification=$null;map_unchanged=$false;world_saved=$null;failure=$null}
try{
    if(-not$AuthorizeSingleUnreal){throw'Mechanical -AuthorizeSingleUnreal guard is required.'}
    $standing=Get-Content -LiteralPath (Join-Path $Root 'Production\standing_heavy_process_authorization.json') -Raw|ConvertFrom-Json
    if($standing.status-ne'ACTIVE'-or$standing.execution_policy.per_run_user_authorization_required-ne$false){throw'Standing authorization is inactive.'}
    Assert-File $Script 7274 'dbe56b2ef7894889d7423da4a61a7de1393883f152a3f83a3a4996a2575e13a4'
    Assert-File (Join-Path $Root 'Docs\AAA_Review\M01_LANDSCAPE_GROUNDING_BRIDGE01_RUNTIME_PROBE_ATTEMPT01_TERMINAL_FREEZE.json') 1859 '6b8ce5081f7570b36319b3801cce7a3f48fa0ffa95d17ab4394fd772c3c6f691'
    Assert-File 'D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentAuthoring01_Recovery07.umap' 625041 '401fb7a86321c05f977347185e41fd0ea0436ef7ec3d06d635935ad5f4ce702f'
    Assert-File 'D:\SG52T08_ENV01\Binaries\Win64\UnrealEditor-Skyguard52.dll' 2937344 '2fdc9a755051df3472b409bab58eb5b152625ff9c1394d4c79c5701832529aa1'
    $heavy=@(Get-Process -ErrorAction SilentlyContinue|Where-Object{$_.ProcessName-match'^(UnrealEditor|UnrealEditor-Cmd|ShaderCompileWorker|AutomationTool|UnrealBuildTool|blender|cl|link)$'})
    if($heavy.Count-ne0){throw'Governed heavy process is active.'}
    if([IO.Directory]::Exists($Attempt)-or[IO.File]::Exists($Terminal)){throw'Recovery01 namespace is not fresh.'}
    $State.preflight_passed=$true
    [IO.Directory]::CreateDirectory($Attempt)|Out-Null
    $stdout=Join-Path $Attempt 'unreal.stdout.log';$stderr=Join-Path $Attempt 'unreal.stderr.log';$engineLog=Join-Path $Attempt 'unreal.engine.log'
    $args=@($Project,'-Unattended','-NoSplash','-NoSound','-NullRHI','-NoSaveOnExit','-stdout','-FullStdOutLogOutput','-nop4','-DisablePlugins=Fab,Bridge,EditorTelemetry,RuntimeTelemetry,EOSShared','-ini:EditorSettings:[/Script/UnrealEd.AnalyticsPrivacySettings]:bSendUsageData=False',"-ExecutePythonScript=$Script",'-ScriptErrorsAreFatal',"-abslog=$engineLog")
    $State.executable=$Editor;$State.arguments=$args;$State.stage='running';$State.unreal_launch_count=1
    $p=Start-Process -FilePath $Editor -ArgumentList $args -WorkingDirectory 'D:\SG52T08_ENV01' -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru
    $State.pid=$p.Id;$deadline=[DateTime]::UtcNow.AddSeconds(600)
    while(-not$p.HasExited){$p.Refresh();if($p.WorkingSet64-gt$State.peak_working_set_bytes){$State.peak_working_set_bytes=$p.WorkingSet64};if([DateTime]::UtcNow-ge$deadline){$State.timeout=$true;Stop-Process -Id $p.Id -Force;break};Start-Sleep -Seconds 2}
    $p.WaitForExit();$p.Refresh();$code=$p.ExitCode;$State.exit_code=$code;if($null-ne$code){$State.exit_code_type=$code.GetType().FullName}
    if($State.timeout){throw'Runtime probe timed out.'};if($null-eq$code){throw'Runtime probe returned a null exit code.'};if($code-ne0){throw"Runtime probe exit code $code."}
    if(-not[IO.File]::Exists($Receipt)){throw'Runtime probe receipt is missing.'}
    $r=Get-Content -LiteralPath $Receipt -Raw|ConvertFrom-Json;$State.receipt_classification=$r.classification;$State.map_unchanged=[bool]$r.map_unchanged;$State.world_saved=[bool]$r.world_saved
    if($r.classification-ne'PASSED_GROUNDING_BRIDGE_RUNTIME_READY_FOR_MEASURED_AUTHORING'){throw"Unexpected receipt: $($r.classification)"};if(-not$r.map_unchanged-or$r.world_saved){throw'Read-only invariant failed.'}
    $State.stage='complete';$State.classification='PASSED_GROUNDING_BRIDGE_RUNTIME_READY_FOR_MEASURED_AUTHORING'
}catch{$State.failure=[ordered]@{stage=$State.stage;message=$_.Exception.Message;type=$_.Exception.GetType().FullName}}
finally{$State.ended_utc=[DateTime]::UtcNow.ToString('o');Write-Json $Terminal $State;if([IO.Directory]::Exists($Attempt)){Write-Json (Join-Path $Attempt 'terminal.json') $State}}
if($State.classification-eq'PASSED_GROUNDING_BRIDGE_RUNTIME_READY_FOR_MEASURED_AUTHORING'){exit 0};exit 1
