[CmdletBinding()]
param([string]$ProjectRoot="D:\Skyguard52",[string]$BlenderExe="C:\Program Files\Blender Foundation\Blender 5.2\blender.exe",[switch]$AuthorizeProduction)
$ErrorActionPreference="Stop"
if(-not $AuthorizeProduction){throw "Recovery03 requires -AuthorizeProduction."}
$root=(Resolve-Path $ProjectRoot).Path
if(Get-Process blender -ErrorAction SilentlyContinue){throw "Active Blender process; duplicate refused."}
$script=Join-Path $root "Scripts\blender_phase2_yak52_r4_slice01_recovery03.py"
$contract=Join-Path $root "Docs\AAA_Review\PHASE2_YAK52_R4_SLICE01_RECOVERY03_OUTPUT_CONTRACT.json"
$hash=(Get-FileHash $contract -Algorithm SHA256).Hash.ToLowerInvariant()
$id="attempt_{0}_{1}_{2:x8}"-f [DateTime]::UtcNow.ToString("yyyyMMddTHHmmssfffffffZ"),$hash.Substring(0,8),$PID
$dir=Join-Path $root "Saved\Reports\Phase2Yak52R4Slice01Recovery03Production\$id"
New-Item -ItemType Directory $dir|Out-Null
$out=Join-Path $dir "blender.stdout.log";$err=Join-Path $dir "blender.stderr.log"
$p=Start-Process $BlenderExe -ArgumentList @("--background","--factory-startup","--python",$script) -RedirectStandardOutput $out -RedirectStandardError $err -WindowStyle Hidden -Wait -PassThru
$c=Get-Content $contract -Raw|ConvertFrom-Json
$state=[ordered]@{};foreach($x in $c.outputs.psobject.Properties){$state[$x.Name]=[ordered]@{path=$x.Value;exists=[bool](Test-Path (Join-Path $root $x.Value))}}
$receipt=[ordered]@{schema="skyguard.phase2.slice01.recovery03.launch.v1";attempt_id=$id;exit_code=$p.ExitCode;contract_sha256=$hash;stdout_sha256=(Get-FileHash $out -Algorithm SHA256).Hash.ToLowerInvariant();stderr_sha256=(Get-FileHash $err -Algorithm SHA256).Hash.ToLowerInvariant();outputs=$state;unreal_launched=$false;promotion_allowed=$false}
$rp=Join-Path $dir "launch_receipt.json";[IO.File]::WriteAllText($rp,(($receipt|ConvertTo-Json -Depth 6)+[Environment]::NewLine),[Text.UTF8Encoding]::new($false))
$s=@((Get-FileHash $out -Algorithm SHA256).Hash.ToLowerInvariant()+"  blender.stdout.log",(Get-FileHash $err -Algorithm SHA256).Hash.ToLowerInvariant()+"  blender.stderr.log",(Get-FileHash $rp -Algorithm SHA256).Hash.ToLowerInvariant()+"  launch_receipt.json")
[IO.File]::WriteAllText((Join-Path $dir "SHA256SUMS.txt"),(($s-join [Environment]::NewLine)+[Environment]::NewLine),[Text.UTF8Encoding]::new($false))
if($p.ExitCode -ne 0 -or -not($state.blend.exists -and $state.glb.exists -and $state.manifest.exists -and $state.comparison_directory.exists)){exit 1}
