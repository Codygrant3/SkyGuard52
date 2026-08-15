param([switch]$AuthorizeSingleUnrealPreview, [switch]$OfflineContractTest)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$Root = 'D:\Skyguard52'
$Project = 'D:\SG52T08_ENV01\Skyguard52.uproject'
$Editor = 'D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe'
$Executor = Join-Path $Root 'Scripts\GrokProduction\author_and_capture_m01_window_recovery06_unrealready01_mapped_preview01.py'
$ImportFreeze = Join-Path $Root 'Docs\AAA_Review\M01_WINDOW_RECOVERY06_UNREALREADY01_REVERSIBLE_UNREAL_IMPORT01_RECOVERY02_ACCEPTANCE_FREEZE.json'
$Authorization = Join-Path $Root 'Production\standing_heavy_process_authorization.json'
$Attempt = Join-Path $Root 'Saved\BuildAttempts\M01_WINDOW_RECOVERY06_UNREALREADY01_MAPPED_PREVIEW01\attempt_01'
$Receipt = Join-Path $Attempt 'mapped_preview_receipt.json'
$MapFile = 'D:\SG52T08_ENV01\Content\T08\GW02Preview\Lvl_GW02_WindowPreview01.umap'
$Terminal = Join-Path $Root 'Saved\Reports\M01_WINDOW_RECOVERY06_UNREALREADY01_MAPPED_PREVIEW01_TERMINAL_SUPERVISOR.json'
$Emergency = Join-Path $Root 'Saved\Reports\M01_WINDOW_RECOVERY06_UNREALREADY01_MAPPED_PREVIEW01_EMERGENCY_RECEIPT.jsonl'
$TimeoutSeconds = 600
$Expected = [ordered]@{
    $Executor = 'bf114b348475ff29bee80c7ec7c15e1c0d73a567422a38690639cb9df25ea893'
    $ImportFreeze = '362579881b7df83bf32ce48a50e104f51149c08e3a1949b1894fad57a413b58c'
    $Authorization = '48277d7edd869cc2b841c3993e8f7599bec5291ddf23e9c442b33e09b870c089'
    $Project = '7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a'
    $Editor = 'de28527cc2dae4c235a0cea01a182913862c9dcd10c08b36dc8be342a7f62311'
}

function Get-Sha256([string]$Path){$stream=$null;$hasher=$null;try{$stream=[IO.File]::Open($Path,[IO.FileMode]::Open,[IO.FileAccess]::Read,[IO.FileShare]::Read);$hasher=[Security.Cryptography.SHA256]::Create();return([BitConverter]::ToString($hasher.ComputeHash($stream))).Replace('-','').ToLowerInvariant()}finally{if($null-ne$hasher){$hasher.Dispose()};if($null-ne$stream){$stream.Dispose()}}}
function Get-Record([string]$Path){$item=Get-Item -LiteralPath $Path -ErrorAction Stop;[ordered]@{path=$item.FullName;bytes=[int64]$item.Length;sha256=Get-Sha256 $item.FullName}}
function Write-JsonAtomic([string]$Path,[object]$Value){$parent=Split-Path -Parent $Path;[IO.Directory]::CreateDirectory($parent)|Out-Null;$temporary=$Path+'.tmp.'+[Diagnostics.Process]::GetCurrentProcess().Id;[IO.File]::WriteAllText($temporary,(($Value|ConvertTo-Json -Depth 40)+[Environment]::NewLine),[Text.UTF8Encoding]::new($false));if(Test-Path -LiteralPath $Path){throw "Refusing to overwrite terminal evidence: $Path"};[IO.File]::Move($temporary,$Path)}
function Get-HeavyProcesses{$exact=@('Blender','UnrealEditor','UnrealEditor-Cmd','ShaderCompileWorker','AutomationTool','UnrealBuildTool','cl','link','dotnet');@(Get-Process -ErrorAction SilentlyContinue|Where-Object{$exact-contains$_.ProcessName-or$_.ProcessName-like'UnrealEditor*'-or$_.ProcessName-like'ShaderCompileWorker*'}|Select-Object ProcessName,Id,StartTime,CPU,WorkingSet64)}

$State=[ordered]@{schema='skyguard.m01-window-recovery06-unrealready01.mapped-preview01.supervisor.v1';classification='FAILED_WITH_EVIDENCE';started_utc=[DateTime]::UtcNow.ToString('o');ended_utc=$null;failure_stage='initialization';failure_message=$null;supervisor_launch_count=1;unreal_launch_count=0;retry_count=0;timed_out=$false;actual_exit_code=$null;actual_exit_code_type=$null;unreal_pid=$null;process_handle_retained=$false;offline_contract_test=[bool]$OfflineContractTest;exact_executable=$Editor;exact_arguments=@();authorities=@();heavy_processes_before=@();process_samples=@();receipt=$null;map=$null;capture_inventory=@();runtime_promotion_performed=$false}
$Exit=1
try{
    $State.failure_stage='preflight'
    foreach($entry in $Expected.GetEnumerator()){if(-not(Test-Path -LiteralPath $entry.Key -PathType Leaf)){throw "Missing authority: $($entry.Key)"};$actual=Get-Sha256 $entry.Key;if($actual-ne$entry.Value){throw "Authority hash mismatch: $($entry.Key) expected=$($entry.Value) actual=$actual"};$State.authorities+=Get-Record $entry.Key}
    $standing=Get-Content -LiteralPath $Authorization -Raw|ConvertFrom-Json
    if($standing.status-ne'ACTIVE'-or$standing.execution_policy.per_run_user_authorization_required-ne$false){throw 'Standing heavy-process authorization is not active.'}
    if(Test-Path -LiteralPath $Attempt){throw "Fresh mapped-preview attempt exists: $Attempt"}
    if(Test-Path -LiteralPath $Terminal){throw "Fresh mapped-preview terminal exists: $Terminal"}
    if(Test-Path -LiteralPath $MapFile){throw "Fresh mapped-preview map exists: $MapFile"}
    $syntax=& python -c "from pathlib import Path; p=Path(r'$Executor'); compile(p.read_text(encoding='utf-8'),str(p),'exec'); print('PASS')" 2>&1
    if($LASTEXITCODE-ne0-or($syntax-join"`n")-notmatch'PASS'){throw "Mapped-preview Python syntax failed: $($syntax-join' ')"}
    $script=Get-Content -LiteralPath $PSCommandPath -Raw
    $needle='Start-Process -FilePath $'+'Editor'
    if([regex]::Matches($script,[regex]::Escape($needle)).Count-ne1){throw 'Supervisor does not contain exactly one Unreal launch path'}
    if($OfflineContractTest){$State.classification='PASS_OFFLINE_CONTRACT';$State.failure_stage=$null;$Exit=0;return}
    if(-not$AuthorizeSingleUnrealPreview){$State.classification='REFUSED_MISSING_MECHANICAL_GUARD';$State.failure_stage='authorization';$Exit=2;return}
    $State.heavy_processes_before=@(Get-HeavyProcesses)
    if($State.heavy_processes_before.Count-ne0){throw "Heavy process gate failed: $($State.heavy_processes_before.ProcessName -join ', ')"}

    [IO.Directory]::CreateDirectory($Attempt)|Out-Null
    $stdout=Join-Path $Attempt 'unreal.stdout.log';$stderr=Join-Path $Attempt 'unreal.stderr.log';$engineLog=Join-Path $Attempt 'unreal.engine.log';$samples=Join-Path $Attempt 'process_tree_samples.jsonl'
    $execCmdValue="py $($Executor.Replace('\','/'))";$execCmdArgument='-ExecCmds="'+$execCmdValue+'"'
    $arguments=@($Project,'-D3D12','-sm6','-RenderOffscreen','-windowed','-ResX=2560','-ResY=1440','-NoVSync','-NoSound','-NoSplash','-unattended','-nop4','-DisablePlugins=Fab,Bridge,EditorTelemetry,RuntimeTelemetry,EOSShared','-ini:EditorSettings:[/Script/UnrealEd.AnalyticsPrivacySettings]:bSendUsageData=False',$execCmdArgument,"-abslog=$engineLog")
    $State.exact_arguments=$arguments;$State.failure_stage='launch'
    $process=Start-Process -FilePath $Editor -ArgumentList $arguments -WorkingDirectory $Root -RedirectStandardOutput $stdout -RedirectStandardError $stderr -WindowStyle Hidden -PassThru
    $State.unreal_launch_count=1;$State.unreal_pid=[int]$process.Id;$null=$process.Handle;$State.process_handle_retained=$true;$deadline=[DateTime]::UtcNow.AddSeconds($TimeoutSeconds);$State.failure_stage='wait'
    while(-not$process.HasExited){$process.Refresh();$sample=[ordered]@{utc=[DateTime]::UtcNow.ToString('o');pid=[int]$process.Id;working_set=[int64]$process.WorkingSet64;cpu_seconds=[double]$process.TotalProcessorTime.TotalSeconds};$State.process_samples+=$sample;[IO.File]::AppendAllText($samples,(($sample|ConvertTo-Json -Compress)+[Environment]::NewLine),[Text.UTF8Encoding]::new($false));if([DateTime]::UtcNow-ge$deadline){$State.timed_out=$true;try{$process.Kill()}catch{};throw "Mapped preview exceeded $TimeoutSeconds seconds."};Start-Sleep -Seconds 2}
    $process.WaitForExit();$process.Refresh();$State.actual_exit_code=[int]$process.ExitCode;$State.actual_exit_code_type=$process.ExitCode.GetType().FullName
    if($process.ExitCode-ne0){throw "Unreal returned exit code $($process.ExitCode)."}
    $State.failure_stage='postflight'
    if(-not(Test-Path -LiteralPath $Receipt -PathType Leaf)){throw 'Mapped-preview receipt missing.'}
    $payload=Get-Content -LiteralPath $Receipt -Raw|ConvertFrom-Json;$State.receipt=Get-Record $Receipt
    if($payload.classification-ne'PASSED_AUTOMATIC_AWAITING_DIRECT_VISUAL_REVIEW'){throw "Unexpected receipt classification: $($payload.classification)"}
    if([int]$payload.capture_count-ne6){throw 'Mapped-preview capture count changed.'}
    if(-not(Test-Path -LiteralPath $MapFile -PathType Leaf)){throw 'Mapped-preview map is absent.'}
    $State.map=Get-Record $MapFile
    $State.capture_inventory=@($payload.captures|ForEach-Object{Get-Record $_.path})
    if($State.capture_inventory.Count-ne6){throw 'Mapped-preview PNG inventory changed.'}
    if(-not[bool]$payload.accepted_source_tree_unchanged-or[bool]$payload.runtime_promotion_performed){throw 'Mapped preview exceeded its isolated boundary.'}
    $State.classification='PASSED_AUTOMATIC_AWAITING_DIRECT_VISUAL_REVIEW';$State.failure_stage=$null;$Exit=0
}catch{$State.classification='FAILED_WITH_EVIDENCE';if($null-eq$State.failure_stage){$State.failure_stage='supervisor'};$State.failure_message=$_.Exception.Message;$Exit=1}finally{$State.ended_utc=[DateTime]::UtcNow.ToString('o');if(-not$OfflineContractTest){try{Write-JsonAtomic $Terminal $State}catch{$emergencyObject=[ordered]@{utc=[DateTime]::UtcNow.ToString('o');classification=$State.classification;stage='terminal_manifest_write';message=$_.Exception.Message};[IO.Directory]::CreateDirectory((Split-Path -Parent $Emergency))|Out-Null;[IO.File]::AppendAllText($Emergency,(($emergencyObject|ConvertTo-Json -Compress)+[Environment]::NewLine),[Text.UTF8Encoding]::new($false));$Exit=1}}}
[Environment]::Exit([int]$Exit)
