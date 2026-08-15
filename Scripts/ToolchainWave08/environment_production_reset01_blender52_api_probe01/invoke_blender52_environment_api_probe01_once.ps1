param([switch]$AuthorizeSingleBlenderProbe)

$ErrorActionPreference = 'Stop'
$Root = 'D:\Skyguard52'
$Blender = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
$Probe = Join-Path $Root 'Scripts\ToolchainWave08\environment_production_reset01_blender52_api_probe01\probe_blender52_environment_api.py'
$Attempt = Join-Path $Root 'Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_BLENDER52_API_PROBE01\attempt_01'
$Result = Join-Path $Root 'Saved\Reports\M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_BLENDER52_API_PROBE01_RESULT.json'
$Terminal = Join-Path $Root 'Saved\Reports\M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_BLENDER52_API_PROBE01_TERMINAL_SUPERVISOR.json'

function Get-Sha256([string]$Path) {
    $stream = $null; $algorithm = $null
    try {
        $stream = [System.IO.File]::OpenRead($Path)
        $algorithm = [System.Security.Cryptography.SHA256]::Create()
        return ([BitConverter]::ToString($algorithm.ComputeHash($stream))).Replace('-','').ToLowerInvariant()
    }
    finally { if($null-ne$algorithm){$algorithm.Dispose()}; if($null-ne$stream){$stream.Dispose()} }
}

function Write-Terminal($Payload) {
    [System.IO.Directory]::CreateDirectory((Split-Path -Parent $Terminal)) | Out-Null
    [System.IO.File]::WriteAllText($Terminal, ($Payload|ConvertTo-Json -Depth 12)+[Environment]::NewLine, [Text.UTF8Encoding]::new($false))
}

$state = [ordered]@{
    schema='skyguard.blender52.environment-api-probe01-supervisor.v1'; gate='RUNNING'; started_utc=[DateTime]::UtcNow.ToString('o'); ended_utc=$null
    failure_stage=$null; failure_message=$null; blender_launch_count=0; retry_count=0; actual_exit_code=$null; actual_exit_code_type=$null
    blender_pid=$null; timed_out=$false; stdout=$null; stderr=$null; result=$null
}
$exit=1
try {
    if(-not$AuthorizeSingleBlenderProbe){throw 'Missing mechanical one-shot guard.'}
    if((Get-Sha256 $Probe)-ne'33f790d11da41792fa6613680ed59570af7b606c44a3b955cc6dbc688d360c0f'){throw 'Probe source hash mismatch.'}
    if((Get-Sha256 $Blender)-ne'e27fbfea8564aa645d4463cb0949695fd85562b9de6df9561b06859a1074adf7'){throw 'Blender hash mismatch.'}
    if(Test-Path $Attempt){throw 'Fresh probe attempt exists.'}; if(Test-Path $Result){throw 'Fresh probe result exists.'}; if(Test-Path $Terminal){throw 'Fresh probe terminal exists.'}
    $heavy=@(Get-Process -ErrorAction SilentlyContinue|Where-Object{$_.ProcessName -eq 'blender' -or $_.ProcessName -like 'UnrealEditor*' -or $_.ProcessName -like 'ShaderCompileWorker*'})
    if($heavy.Count-ne0){throw 'Heavy process conflict.'}
    [IO.Directory]::CreateDirectory($Attempt)|Out-Null
    $stdout=Join-Path $Attempt 'blender.stdout.log'; $stderr=Join-Path $Attempt 'blender.stderr.log'; $state.stdout=$stdout; $state.stderr=$stderr
    $state.failure_stage='blender_api_probe'
    $process=Start-Process -FilePath $Blender -ArgumentList @('--background','--factory-startup','--python',$Probe) -WorkingDirectory $Root -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru
    $state.blender_launch_count=1; $state.blender_pid=[int]$process.Id; $null=$process.Handle
    if(-not$process.WaitForExit(120000)){try{$process.Kill()}catch{};$state.timed_out=$true;throw 'Probe timeout.'}
    $process.Refresh(); $state.actual_exit_code=[int]$process.ExitCode; $state.actual_exit_code_type=$process.ExitCode.GetType().FullName
    if($process.ExitCode-ne0){throw "Probe exit $($process.ExitCode)."}; if(-not(Test-Path $Result -PathType Leaf)){throw 'Probe result missing.'}
    $state.result=[ordered]@{path=$Result;bytes=(Get-Item $Result).Length;sha256=Get-Sha256 $Result}
    $state.gate='PASSED_READ_ONLY_API_CAPABILITY_PROBE';$state.failure_stage=$null;$exit=0
}
catch{$state.gate='FAILED_WITH_EVIDENCE';$state.failure_message=$_.Exception.Message}
finally{$state.ended_utc=[DateTime]::UtcNow.ToString('o');Write-Terminal $state}
[Environment]::Exit([int]$exit)
