param([switch]$OfflineContractTest, [switch]$AuthorizeSingleReadOnlyPostflight)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$Root = 'D:\Skyguard52'
$Project = 'D:\SG52T08_ENV01\Skyguard52.uproject'
$Editor = 'D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$Map = 'D:\SG52T08_ENV01\Content\M01\Lvl_M01_VisibleEnvironmentStage04Recovery03.umap'
$InputMap = 'D:\SG52T08_ENV01\Content\M01\Lvl_M01_VisibleEnvironmentStage03.umap'
$AuthoringReceipt = Join-Path $Root 'Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_STAGE04_AUTHORING01_RECOVERY03\attempt_01\authoring_receipt.json'
$AuthoringTerminal = Join-Path $Root 'Saved\Reports\M01_VISIBLE_ENVIRONMENT_STAGE04_AUTHORING01_RECOVERY03_TERMINAL_MANIFEST.json'
$Probe = Join-Path $Root 'Scripts\ToolchainWave08\m01_visible_environment_stage04_recovery03_postflight\verify_stage04_recovery03_saved_map.py'
$Attempt = Join-Path $Root 'Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_STAGE04_RECOVERY03_POSTFLIGHT01\attempt_01'
$Receipt = Join-Path $Attempt 'postflight_receipt.json'
$Terminal = Join-Path $Root 'Saved\Reports\M01_VISIBLE_ENVIRONMENT_STAGE04_RECOVERY03_POSTFLIGHT01_TERMINAL.json'
$TimeoutSeconds = 600

$Expected = @{
    Project = @{Bytes=3703;Sha='7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a'}
    Editor = @{Bytes=512952;Sha='0fb325cf215cc800ce260a1890af3f3dc314b8cc6331061d4e7e7246489af2e0'}
    Map = @{Bytes=978545;Sha='70b0929008acafcd4d2c943e9eba6de02d0533752081e6794494b872966a5c18'}
    InputMap = @{Bytes=911233;Sha='28c3462ffe39b6fe753e2ba96761aa0e54d3aa947b41c1c9be4c760202980cad'}
    AuthoringReceipt = @{Bytes=63288;Sha='30b2a0a90cf88811990a27aeb49c5e554093bbe65f6089d106650e351db58c2f'}
    AuthoringTerminal = @{Bytes=8241;Sha='9893e4c6a8ab1fd0f34db61fd8b9268e23e45fdac080398973fd2c7be8d62192'}
    Probe = @{Bytes=10096;Sha='9ae0fc9b68c0abc06c67b3d259121e4b2d4d345acf7f9cedd75bc70064e12acd'}
}
function Get-Sha([string]$Path){$s=[IO.File]::OpenRead($Path);$h=[Security.Cryptography.SHA256]::Create();try{return([BitConverter]::ToString($h.ComputeHash($s))).Replace('-','').ToLowerInvariant()}finally{$h.Dispose();$s.Dispose()}}
function Assert-File([string]$Path,[int64]$Bytes,[string]$Sha,[string]$Label){if(-not[IO.File]::Exists($Path)){throw"$Label missing"};$i=[IO.FileInfo]::new($Path);if($i.Length-ne$Bytes){throw"$Label bytes changed"};if((Get-Sha $Path)-ne$Sha){throw"$Label hash changed"}}
function Assert-Authorities {
    Assert-File $Project $Expected.Project.Bytes $Expected.Project.Sha 'Project'
    Assert-File $Editor $Expected.Editor.Bytes $Expected.Editor.Sha 'Editor'
    Assert-File $Map $Expected.Map.Bytes $Expected.Map.Sha 'Recovery03 map'
    Assert-File $InputMap $Expected.InputMap.Bytes $Expected.InputMap.Sha 'Stage03 map'
    Assert-File $AuthoringReceipt $Expected.AuthoringReceipt.Bytes $Expected.AuthoringReceipt.Sha 'Authoring receipt'
    Assert-File $AuthoringTerminal $Expected.AuthoringTerminal.Bytes $Expected.AuthoringTerminal.Sha 'Authoring terminal'
    Assert-File $Probe $Expected.Probe.Bytes $Expected.Probe.Sha 'Postflight probe'
}
function Heavy { @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue|Where-Object{$_.Name-match'^(UnrealEditor(-Cmd)?|Blender|ShaderCompileWorker|AutomationTool|UnrealBuildTool|cl|link)(\.exe)?$'}) }
if($OfflineContractTest){Assert-Authorities;if(Test-Path $Attempt){throw'Fresh attempt exists'};if(Test-Path $Terminal){throw'Fresh terminal exists'};if(@(Heavy).Count){throw'Heavy process active'};python -m py_compile $Probe;if($LASTEXITCODE-ne0){throw'Probe parse failed'};[ordered]@{classification='PASSED_OFFLINE_READY_FOR_SINGLE_READ_ONLY_POSTFLIGHT';unreal_launch_count=0}|ConvertTo-Json;exit 0}

$state=[ordered]@{schema='skyguard.m01-visible-environment-stage04-recovery03.postflight01.supervisor.v1';classification='FAILED_WITH_EVIDENCE';started_at_utc=[DateTime]::UtcNow.ToString('o');completed_at_utc=$null;unreal_launch_count=0;retry_count=0;pid=$null;exit_code=$null;exit_code_type=$null;timeout=$false;receipt_classification=$null;map_unchanged=$false;input_map_unchanged=$false;failure=$null}
$code=1
try{
    if(-not$AuthorizeSingleReadOnlyPostflight){throw'Mechanical authorization guard required'}
    Assert-Authorities
    if(Test-Path $Attempt){throw'Fresh attempt exists'};if(Test-Path $Terminal){throw'Fresh terminal exists'};if(@(Heavy).Count){throw'Heavy process active'}
    [IO.Directory]::CreateDirectory($Attempt)|Out-Null
    Copy-Item $Probe (Join-Path $Attempt 'verify_stage04_recovery03_saved_map.py')
    $out=Join-Path $Attempt 'unreal.stdout.log';$err=Join-Path $Attempt 'unreal.stderr.log';$log=Join-Path $Attempt 'unreal.engine.log'
    $args=@($Project,'-Unattended','-NoSplash','-NoSound','-NullRHI','-NoSaveOnExit','-stdout','-FullStdOutLogOutput','-nop4','-DisablePlugins=Fab,Bridge,EditorTelemetry,RuntimeTelemetry,EOSShared','-ini:EditorSettings:[/Script/UnrealEd.AnalyticsPrivacySettings]:bSendUsageData=False',"-ExecutePythonScript=$Probe",'-ScriptErrorsAreFatal',"-abslog=$log")
    $p=Start-Process $Editor -ArgumentList $args -WorkingDirectory 'D:\SG52T08_ENV01' -PassThru -WindowStyle Hidden -RedirectStandardOutput $out -RedirectStandardError $err
    $state.unreal_launch_count=1;$state.pid=$p.Id;$null=$p.Handle;$deadline=[DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
    while(-not$p.HasExited-and[DateTime]::UtcNow-lt$deadline){Start-Sleep 2;$p.Refresh()}
    if(-not$p.HasExited){$state.timeout=$true;Stop-Process $p.Id -Force -ErrorAction SilentlyContinue;throw'Postflight timed out'}
    $p.WaitForExit();$p.Refresh();$state.exit_code=[int]$p.ExitCode;$state.exit_code_type=$p.ExitCode.GetType().FullName
    if($state.exit_code-ne0){throw"Postflight Unreal returned $($state.exit_code)"};if(-not(Test-Path $Receipt)){throw'Receipt missing'}
    $payload=Get-Content $Receipt -Raw|ConvertFrom-Json;$state.receipt_classification=$payload.classification
    if($payload.classification-ne'PASSED_STAGE04_RECOVERY03_SAVED_MAP_READY_FOR_GOVERNED_D3D12_VISUAL_PROOF'){throw"Receipt failed: $($payload.classification)"}
    Assert-File $Map $Expected.Map.Bytes $Expected.Map.Sha 'Recovery03 map after postflight';Assert-File $InputMap $Expected.InputMap.Bytes $Expected.InputMap.Sha 'Stage03 map after postflight'
    $state.map_unchanged=$true;$state.input_map_unchanged=$true;$state.classification=$payload.classification;$code=0
}catch{$state.failure=[ordered]@{type=$_.Exception.GetType().FullName;message=$_.Exception.Message;stack=$_.ScriptStackTrace}}
finally{$state.completed_at_utc=[DateTime]::UtcNow.ToString('o');[IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($Terminal))|Out-Null;[IO.File]::WriteAllText($Terminal,($state|ConvertTo-Json -Depth 32)+[Environment]::NewLine,[Text.UTF8Encoding]::new($false));if(Test-Path $Attempt){[IO.File]::WriteAllText((Join-Path $Attempt 'terminal.json'),($state|ConvertTo-Json -Depth 32)+[Environment]::NewLine,[Text.UTF8Encoding]::new($false))}}
$state|ConvertTo-Json -Depth 32
exit $code
