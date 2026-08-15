param(
    [switch]$AuthorizeSingleUnreal,
    [switch]$OfflineContractTest
)

$ErrorActionPreference = 'Stop'
$ProjectRoot = 'D:\Skyguard52'
$Editor = 'D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$UProject = 'D:\SG52T08_ENV01\Skyguard52.uproject'
$PythonScript = Join-Path $ProjectRoot 'Scripts\ToolchainWave08\environment_realism_stack_pivot01\probe_landscape_grounding_runtime.py'
$AttemptRoot = Join-Path $ProjectRoot 'Saved\BuildAttempts\M01_LANDSCAPE_GROUNDING_BRIDGE01_RUNTIME_PROBE\attempt_01'
$ReceiptPath = Join-Path $AttemptRoot 'runtime_probe_receipt.json'
$TerminalPath = Join-Path $ProjectRoot 'Saved\Reports\M01_LANDSCAPE_GROUNDING_BRIDGE01_RUNTIME_PROBE_TERMINAL_MANIFEST.json'
$StandingPath = Join-Path $ProjectRoot 'Production\standing_heavy_process_authorization.json'
$BindingFreeze = Join-Path $ProjectRoot 'Docs\AAA_Review\M01_LANDSCAPE_GROUNDING_BRIDGE01_RUNTIME_BINDING_RECOVERY01_TERMINAL_FREEZE.json'
$MapFile = 'D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentAuthoring01_Recovery07.umap'
$BoundDll = 'D:\SG52T08_ENV01\Binaries\Win64\UnrealEditor-Skyguard52.dll'

$Authorities = @(
    @{Path=$PythonScript;Bytes=7826;Sha256='c5364f5655089b717a93b5a30a74f0fbe12f36e3051cac7762d746987dc7d059'},
    @{Path=$BindingFreeze;Bytes=2006;Sha256='3c722e2bcbfe42ce28712524287bc41ba4f2d683e31f174550e6e5a26d97d717'},
    @{Path=$MapFile;Bytes=625041;Sha256='401fb7a86321c05f977347185e41fd0ea0436ef7ec3d06d635935ad5f4ce702f'},
    @{Path=$BoundDll;Bytes=2937344;Sha256='2fdc9a755051df3472b409bab58eb5b152625ff9c1394d4c79c5701832529aa1'},
    @{Path=$Editor;Bytes=512952;Sha256='0fb325cf215cc800ce260a1890af3f3dc314b8cc6331061d4e7e7246489af2e0'}
)

function Get-Sha256([string]$Path) {
    $stream=$null;$sha=$null
    try {$stream=[IO.File]::Open($Path,'Open','Read','Read');$sha=[Security.Cryptography.SHA256]::Create();return([BitConverter]::ToString($sha.ComputeHash($stream))).Replace('-','').ToLowerInvariant()}
    finally {if($null-ne$sha){$sha.Dispose()};if($null-ne$stream){$stream.Dispose()}}
}

function Assert-Authority([object]$Record) {
    if(-not[IO.File]::Exists($Record.Path)){throw "Missing authority: $($Record.Path)"}
    $item=Get-Item -LiteralPath $Record.Path
    if($item.Length-ne[int64]$Record.Bytes){throw "Byte mismatch: $($Record.Path)"}
    if((Get-Sha256 $Record.Path)-ne$Record.Sha256){throw "Hash mismatch: $($Record.Path)"}
}

function Assert-NoHeavyProcess {
    $heavy=@(Get-Process -ErrorAction SilentlyContinue|Where-Object{$_.ProcessName-match'^(UnrealEditor|UnrealEditor-Cmd|ShaderCompileWorker|AutomationTool|UnrealBuildTool|blender|cl|link)$'})
    if($heavy.Count-ne0){throw "Heavy process active: $($heavy.ProcessName -join ', ')"}
}

function Write-Json([string]$Path,[object]$Value) {
    $parent=Split-Path -Parent $Path
    if(-not[IO.Directory]::Exists($parent)){[IO.Directory]::CreateDirectory($parent)|Out-Null}
    $temp=$Path+'.tmp'
    [IO.File]::WriteAllText($temp,($Value|ConvertTo-Json -Depth 12)+[Environment]::NewLine,[Text.UTF8Encoding]::new($false))
    [IO.File]::Move($temp,$Path)
}

$State=[ordered]@{
    schema='skyguard.m01-landscape-grounding-bridge01.runtime-probe-supervisor.v1'
    classification='FAILED_WITH_EVIDENCE'
    started_utc=[DateTime]::UtcNow.ToString('o')
    ended_utc=$null
    stage='initializing'
    authorization_present=[bool]$AuthorizeSingleUnreal
    offline_contract_test=[bool]$OfflineContractTest
    preflight_passed=$false
    supervisor_launch_count=1
    unreal_launch_count=0
    retry_count=0
    pid=$null
    exit_code=$null
    exit_code_type=$null
    timeout=$false
    crash=$false
    peak_working_set_bytes=0
    receipt_path=$ReceiptPath
    receipt_classification=$null
    map_unchanged=$false
    world_saved=$null
    failure=$null
}

try {
    if($OfflineContractTest-and$AuthorizeSingleUnreal){throw'Offline and authorized modes are mutually exclusive.'}
    $standing=Get-Content -LiteralPath $StandingPath -Raw|ConvertFrom-Json
    if($standing.status-ne'ACTIVE'-or$standing.execution_policy.per_run_user_authorization_required-ne$false){throw'Standing authorization is inactive.'}
    foreach($record in $Authorities){Assert-Authority $record}
    Assert-NoHeavyProcess
    if([IO.Directory]::Exists($AttemptRoot)-or[IO.File]::Exists($TerminalPath)){throw'Runtime-probe namespace is not fresh.'}
    $State.preflight_passed=$true
    if($OfflineContractTest){$State.stage='offline_complete';$State.classification='PASSED_OFFLINE_CONTRACT_TEST';$State.ended_utc=[DateTime]::UtcNow.ToString('o');$State|ConvertTo-Json -Depth 12;[Environment]::Exit([int]0)}
    if(-not$AuthorizeSingleUnreal){throw'Mechanical -AuthorizeSingleUnreal guard is required.'}
    [IO.Directory]::CreateDirectory($AttemptRoot)|Out-Null
    $stdout=Join-Path $AttemptRoot 'unreal.stdout.log'
    $stderr=Join-Path $AttemptRoot 'unreal.stderr.log'
    $engineLog=Join-Path $AttemptRoot 'unreal.engine.log'
    $args=@(
        $UProject,'-Unattended','-NoSplash','-NoSound','-NullRHI','-NoSaveOnExit','-stdout','-FullStdOutLogOutput','-nop4',
        '-DisablePlugins=Fab,Bridge,EditorTelemetry,RuntimeTelemetry,EOSShared',
        '-ini:EditorSettings:[/Script/UnrealEd.AnalyticsPrivacySettings]:bSendUsageData=False',
        "-ExecutePythonScript=$PythonScript",'-ScriptErrorsAreFatal',"-abslog=$engineLog"
    )
    $State.arguments=$args;$State.executable=$Editor;$State.stage='running';$State.unreal_launch_count=1
    $process=Start-Process -FilePath $Editor -ArgumentList $args -WorkingDirectory 'D:\SG52T08_ENV01' -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru
    $State.pid=$process.Id
    $deadline=[DateTime]::UtcNow.AddSeconds(600)
    while(-not$process.HasExited){
        $process.Refresh();if($process.WorkingSet64-gt$State.peak_working_set_bytes){$State.peak_working_set_bytes=$process.WorkingSet64}
        if([DateTime]::UtcNow-ge$deadline){$State.timeout=$true;Stop-Process -Id $process.Id -Force;break}
        Start-Sleep -Seconds 2
    }
    $process.WaitForExit();$process.Refresh()
    $State.exit_code=$process.ExitCode;$State.exit_code_type=$process.ExitCode.GetType().FullName
    if($State.timeout){throw'Unreal runtime probe timed out.'}
    if($process.ExitCode-ne0){throw"Unreal runtime probe exit code $($process.ExitCode)."}
    if(-not[IO.File]::Exists($ReceiptPath)){throw'Runtime probe receipt is missing.'}
    $receipt=Get-Content -LiteralPath $ReceiptPath -Raw|ConvertFrom-Json
    $State.receipt_classification=$receipt.classification;$State.map_unchanged=[bool]$receipt.map_unchanged;$State.world_saved=[bool]$receipt.world_saved
    if($receipt.classification-ne'PASSED_GROUNDING_BRIDGE_RUNTIME_READY_FOR_MEASURED_AUTHORING'){throw"Unexpected receipt classification: $($receipt.classification)"}
    if(-not$receipt.map_unchanged-or$receipt.world_saved){throw'Read-only map invariant failed.'}
    $State.stage='complete';$State.classification='PASSED_GROUNDING_BRIDGE_RUNTIME_READY_FOR_MEASURED_AUTHORING'
} catch {
    $State.failure=[ordered]@{stage=$State.stage;message=$_.Exception.Message;type=$_.Exception.GetType().FullName}
} finally {
    $State.ended_utc=[DateTime]::UtcNow.ToString('o')
    if(-not$OfflineContractTest){Write-Json $TerminalPath $State;if([IO.Directory]::Exists($AttemptRoot)){Write-Json (Join-Path $AttemptRoot 'terminal.json') $State}}
}

if($State.classification-eq'PASSED_GROUNDING_BRIDGE_RUNTIME_READY_FOR_MEASURED_AUTHORING'){[Environment]::Exit([int]0)}
[Environment]::Exit([int]1)
