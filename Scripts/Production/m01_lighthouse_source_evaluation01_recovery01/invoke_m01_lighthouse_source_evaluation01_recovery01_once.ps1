[CmdletBinding()]
param([switch]$AuthorizeSingleBlender, [switch]$OfflineContractTest)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$ContractPath = Join-Path $Root 'source_evaluation_recovery01_contract.json'
$SourceContract = 'D:\Skyguard52\Scripts\Production\m01_lighthouse_source_evaluation01\source_evaluation_contract.json'
$Wrapper = Join-Path $Root 'evaluate_m01_lighthouse_sources_recovery01.py'
$Attempt = 'D:\Skyguard52\Saved\BuildAttempts\M01_LIGHTHOUSE_SOURCE_EVALUATION01_RECOVERY01\attempt_01'
$Terminal = 'D:\Skyguard52\Saved\Reports\M01_LIGHTHOUSE_SOURCE_EVALUATION01_RECOVERY01_TERMINAL_MANIFEST.json'
$Emergency = 'D:\Skyguard52\Saved\Reports\M01_LIGHTHOUSE_SOURCE_EVALUATION01_RECOVERY01_EMERGENCY_RECEIPT.jsonl'
$Blender = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
$state = [ordered]@{schema='skyguard.m01-lighthouse-source-evaluation01-recovery01.terminal-supervisor.v1';created_at_utc=[DateTime]::UtcNow.ToString('o');classification='FAILED_WITH_EVIDENCE';authorized=[bool]$AuthorizeSingleBlender;offline_contract_test=[bool]$OfflineContractTest;preflight_passed=$false;blender_launch_count=0;automatic_retry_count=0;unreal_launch_count=0;timed_out=$false;process_id=$null;exit_code=$null;exit_code_type=$null;receipt=$null;final_inventory=$null;error=$null}

function Get-Sha256([string]$Path){$s=[System.IO.File]::Open($Path,'Open','Read','Read');$h=[System.Security.Cryptography.SHA256]::Create();try{return([BitConverter]::ToString($h.ComputeHash($s))).Replace('-','').ToLowerInvariant()}finally{$h.Dispose();$s.Dispose()}}
function Verify([object]$E){if(-not(Test-Path -LiteralPath $E.path -PathType Leaf)){throw "Missing: $($E.path)"};$i=Get-Item -LiteralPath $E.path;if($i.Length-ne[int64]$E.bytes-or(Get-Sha256 $E.path)-ne[string]$E.sha256){throw "Hash or byte mismatch: $($E.path)"}}
function Write-Atomic([string]$Path,[object]$Value){$parent=Split-Path -Parent $Path;if(-not(Test-Path -LiteralPath $parent)){New-Item -ItemType Directory -Path $parent -Force|Out-Null};$tmp="$Path.tmp";$Value|ConvertTo-Json -Depth 40|Set-Content -LiteralPath $tmp -Encoding UTF8;Move-Item -LiteralPath $tmp -Destination $Path -Force}
function Assert-Quiet{$heavy=Get-CimInstance Win32_Process -ErrorAction SilentlyContinue|Where-Object{$_.Name-match'^(UnrealEditor|UnrealEditor-Cmd|Blender|ShaderCompileWorker|AutomationTool|UnrealBuildTool|cl|link|dotnet)(\.exe)?$'};if($heavy){throw "Heavy process active: $($heavy.Name -join ', ')"}}
function Final-Inventory{
    $rows=@();Get-ChildItem -LiteralPath $Attempt -Recurse -File|Where-Object{$_.Name-ne'final_artifact_inventory.json'}|Sort-Object FullName|ForEach-Object{$rows+=[ordered]@{path=$_.FullName;bytes=$_.Length;sha256=Get-Sha256 $_.FullName}}
    $value=[ordered]@{schema='skyguard.m01-lighthouse-source-evaluation01-recovery01.final-artifact-inventory.v1';created_at_utc=[DateTime]::UtcNow.ToString('o');classification=$state.classification;artifacts=$rows}
    $path=Join-Path $Attempt 'final_artifact_inventory.json';Write-Atomic $path $value;return[ordered]@{path=$path;bytes=(Get-Item -LiteralPath $path).Length;sha256=Get-Sha256 $path}
}

try{
    $c=Get-Content -LiteralPath $ContractPath -Raw|ConvertFrom-Json
    if($c.classification-ne'PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_READ_ONLY_BLENDER_SOURCE_EVALUATION_RECOVERY01'){throw'Contract classification changed'}
    Verify $c.failure_authority;Verify $c.frozen_evaluator;Verify $c.frozen_source_contract;Verify $c.compatibility_wrapper
    $source=Get-Content -LiteralPath $SourceContract -Raw|ConvertFrom-Json
    foreach($entry in $source.authorities){Verify $entry};foreach($entry in $source.sources){Verify $entry};Verify $source.blender
    if(Test-Path -LiteralPath $Attempt){throw"Fresh attempt exists: $Attempt"};if(Test-Path -LiteralPath $Terminal){throw"Fresh terminal exists: $Terminal"}
    if($OfflineContractTest){Write-Output'PASS_M01_LIGHTHOUSE_SOURCE_EVALUATION01_RECOVERY01_OFFLINE_CONTRACT';[Environment]::Exit([int]0)}
    if(-not$AuthorizeSingleBlender){throw'Authorization guard missing'};Assert-Quiet;New-Item -ItemType Directory -Path $Attempt|Out-Null;$state.preflight_passed=$true
    $stdout=Join-Path $Attempt 'blender.stdout.log';$stderr=Join-Path $Attempt 'blender.stderr.log';$args=@('--background','--factory-startup','--python',$Wrapper,'--','--contract',$SourceContract,'--attempt',$Attempt)
    $started=[DateTime]::UtcNow;$p=Start-Process -FilePath $Blender -ArgumentList $args -WorkingDirectory 'D:\Skyguard52' -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru;$state.blender_launch_count=1;$state.process_id=[int]$p.Id
    $p.WaitForExit();$p.Refresh();$childCode=[int]$p.ExitCode;$childType=$childCode.GetType().FullName;$state.exit_code=$childCode;$state.exit_code_type=$childType;$state.elapsed_seconds=([DateTime]::UtcNow-$started).TotalSeconds
    $receiptPath=Join-Path $Attempt 'source_evaluation_receipt.json';if(-not(Test-Path -LiteralPath $receiptPath)){throw'Receipt missing'};$receiptJson=Get-Content -LiteralPath $receiptPath -Raw|ConvertFrom-Json;$state.receipt=[ordered]@{path=$receiptPath;bytes=(Get-Item -LiteralPath $receiptPath).Length;sha256=Get-Sha256 $receiptPath;classification=$receiptJson.classification}
    if($childCode-ne0-or$childType-ne'System.Int32'-or$receiptJson.classification-ne'PASSED_SOURCE_EVALUATION_AWAITING_DIRECT_VISUAL_REVIEW'-or[int]$receiptJson.render_count-ne8){throw"Child/receipt failure: code=$childCode type=$childType class=$($receiptJson.classification) renders=$($receiptJson.render_count)"}
    $state.classification='PASSED_SOURCE_EVALUATION_AWAITING_DIRECT_VISUAL_REVIEW'
}catch{$state.error="$($_.Exception.GetType().Name): $($_.Exception.Message)"}
finally{$state.finished_at_utc=[DateTime]::UtcNow.ToString('o');if(Test-Path -LiteralPath $Attempt){try{$state.final_inventory=Final-Inventory}catch{$state.inventory_error="$($_.Exception.GetType().Name): $($_.Exception.Message)"}};try{Write-Atomic $Terminal $state}catch{$line=([ordered]@{at_utc=[DateTime]::UtcNow.ToString('o');error="$($_.Exception.GetType().Name): $($_.Exception.Message)"}|ConvertTo-Json -Compress);Add-Content -LiteralPath $Emergency -Value $line -Encoding UTF8}}
if($state.classification-eq'PASSED_SOURCE_EVALUATION_AWAITING_DIRECT_VISUAL_REVIEW'){[Environment]::Exit([int]0)};[Environment]::Exit([int]3)
