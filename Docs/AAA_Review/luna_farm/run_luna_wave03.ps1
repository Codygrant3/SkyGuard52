param(
  [string]$FarmDir = "D:\Skyguard52\Docs\AAA_Review\luna_farm",
  [string]$WaveId = "wave03",
  [string]$Model = "gpt-5.6-luna",
  [int]$TimeoutSec = 900
)

$ErrorActionPreference = "Stop"
$wave = Join-Path $FarmDir $WaveId
$rawDir = Join-Path $wave "raw"
$canDir = Join-Path $wave "canonical"
$logDir = Join-Path $wave "logs"
$schema = Join-Path $FarmDir "proposal_wave_schema.json"
$ranker = Join-Path $FarmDir "rank_luna_proposals.py"
New-Item -ItemType Directory -Force -Path $rawDir, $canDir, $logDir | Out-Null

$jobs = @(
  @{ Id = "materials"; Prompt = "P01_materials.txt" },
  @{ Id = "aircraft"; Prompt = "P02_aircraft.txt" },
  @{ Id = "city_ocean"; Prompt = "P03_city_ocean.txt" },
  @{ Id = "weapon_ads"; Prompt = "P04_weapon_ads.txt" },
  @{ Id = "vfx"; Prompt = "P05_vfx.txt" }
)

function Invoke-LunaPillar {
  param($Job)
  $promptPath = Join-Path $FarmDir $Job.Prompt
  $rawPath = Join-Path $rawDir ($Job.Id + ".jsonl")
  $canPath = Join-Path $canDir ($Job.Id + ".json")
  $logPath = Join-Path $logDir ($Job.Id + ".log")
  $exitPath = Join-Path $logDir ($Job.Id + ".exit.txt")
  foreach ($p in @($rawPath, $canPath, $logPath, $exitPath)) {
    if (Test-Path -LiteralPath $p) { Remove-Item -LiteralPath $p -Force -ErrorAction SilentlyContinue }
  }

  $bat = Join-Path $logDir ("run_" + $Job.Id + ".bat")
  $batLines = @(
    "@echo off",
    "setlocal EnableDelayedExpansion",
    "type `"$promptPath`" | codex -a never exec -m $Model -s read-only --json --ephemeral --skip-git-repo-check --output-schema `"$schema`" -o `"$canPath`" - > `"$rawPath`" 2> `"$logPath`"",
    "set ERR=!ERRORLEVEL!",
    "echo EXIT=!ERR!> `"$exitPath`""
  )
  $batLines | Set-Content -LiteralPath $bat -Encoding ascii
  $proc = Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "`"$bat`"" -WorkingDirectory $FarmDir -WindowStyle Hidden -PassThru
  return [pscustomobject]@{
    Id = $Job.Id
    Pid = $proc.Id
    Process = $proc
    Raw = $rawPath
    Canonical = $canPath
    Log = $logPath
    ExitFile = $exitPath
    Started = Get-Date
  }
}

Write-Host ("Launching 5 Luna jobs model={0} wave={1}" -f $Model, $WaveId)
$running = @()
foreach ($j in $jobs) {
  $running += Invoke-LunaPillar -Job $j
  Start-Sleep -Milliseconds 500
}

$deadline = (Get-Date).AddSeconds($TimeoutSec)
while ((Get-Date) -lt $deadline) {
  $alive = @($running | Where-Object { -not $_.Process.HasExited })
  $done = @($running | Where-Object { $_.Process.HasExited })
  Write-Host ("{0:HH:mm:ss} running={1} done={2}" -f (Get-Date), $alive.Count, $done.Count)
  if ($alive.Count -eq 0) { break }
  Start-Sleep -Seconds 12
}

foreach ($r in $running) {
  if (-not $r.Process.HasExited) {
    try { Stop-Process -Id $r.Pid -Force -ErrorAction SilentlyContinue } catch {}
    "TIMEOUT" | Set-Content -LiteralPath $r.ExitFile -Encoding ascii
  }
}

$all = New-Object System.Collections.Generic.List[object]
$summary = @()
foreach ($r in $running) {
  $status = "missing"
  $count = 0
  $err = ""
  try {
    if (Test-Path -LiteralPath $r.Canonical) {
      $obj = Get-Content -LiteralPath $r.Canonical -Raw | ConvertFrom-Json
      $props = @()
      if ($null -ne $obj.proposals) { $props = @($obj.proposals) }
      elseif ($obj -is [System.Array]) { $props = @($obj) }
      $count = $props.Count
      if ($count -gt 0) {
        foreach ($pp in $props) { [void]$all.Add($pp) }
        $status = "ok"
      } else {
        $status = "empty"
      }
    } elseif (Test-Path -LiteralPath $r.Raw) {
      $status = "no_canonical"
    }
  } catch {
    $status = "parse_error"
    $err = $_.Exception.Message
  }
  $exitTxt = if (Test-Path -LiteralPath $r.ExitFile) { (Get-Content -LiteralPath $r.ExitFile -Raw).Trim() } else { "n/a" }
  $summary += [pscustomobject]@{ pillar=$r.Id; status=$status; count=$count; exit=$exitTxt; error=$err; canonical=$r.Canonical; raw=$r.Raw }
}

$combined = Join-Path $wave "wave03_all_proposals.json"
$payload = [ordered]@{
  wave = $WaveId
  model = $Model
  generated_at = (Get-Date).ToString("s")
  freeze = "L55"
  proposal_count = $all.Count
  proposals = $all
}
$payload | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $combined -Encoding utf8
$summaryPath = Join-Path $wave "wave03_job_summary.json"
$summary | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $summaryPath -Encoding utf8

$listPath = Join-Path $wave "wave03_proposals_list.json"
if ($all.Count -eq 0) { "[]" | Set-Content -LiteralPath $listPath -Encoding utf8 } else { (@($all.ToArray()) | ConvertTo-Json -Depth 12) | Set-Content -LiteralPath $listPath -Encoding utf8 }
$rankedCsv = Join-Path $wave "wave03_ranked.csv"
& python $ranker $listPath $rankedCsv
$rankExit = $LASTEXITCODE

$selected = Join-Path $wave "selected_next_loop.md"
$aRows = @()
if (Test-Path -LiteralPath $rankedCsv) {
  $aRows = @(Import-Csv -LiteralPath $rankedCsv | Where-Object { $_.band -eq "A" -and $_.status -eq "candidate" } | Sort-Object { [double]$_.score } -Descending)
}
$picked = @()
$perPillar = @{}
foreach ($row in $aRows) {
  $pillar = [string]$row.pillar
  if (-not $perPillar.ContainsKey($pillar)) { $perPillar[$pillar] = 0 }
  if ($perPillar[$pillar] -ge 2) { continue }
  if ($picked.Count -ge 7) { break }
  if ([string]$row.risk -eq "high") { continue }
  $picked += $row
  $perPillar[$pillar] = $perPillar[$pillar] + 1
}

$lines = New-Object System.Collections.Generic.List[string]
[void]$lines.Add("# Selected Luna proposals for next densify loop")
[void]$lines.Add("Base freeze: **L55** densify+thin-art (11/11). L52 densify recipe; L53 rejected; L54/L55 kept.")
[void]$lines.Add("Wave: $WaveId")
[void]$lines.Add("Model: $Model")
[void]$lines.Add("Generated: $((Get-Date).ToString('s'))")
[void]$lines.Add("Usable gate required: **11/11**")
[void]$lines.Add("")
[void]$lines.Add("## Job summary")
foreach ($s in $summary) {
  [void]$lines.Add(("- {0}: status={1} count={2} exit={3}" -f $s.pillar, $s.status, $s.count, $s.exit))
}
[void]$lines.Add("")
[void]$lines.Add("## Keep rules")
[void]$lines.Add("- Preserve L52 HF densify exactly")
[void]$lines.Add("- Prefer additive_emissive or tiny behind_wall accents")
[void]$lines.Add("- No large multi-stage hero stacks (L53 failure mode)")
[void]$lines.Add("- Protect Prop/PropNose/YakBeauty/City/Ocean/Wide")
[void]$lines.Add("")
[void]$lines.Add("## Implement list (A-band capped)")
if ($picked.Count -eq 0) {
  [void]$lines.Add("- None selected. Inspect ranked CSV and raw pillar outputs.")
} else {
  $i = 1
  foreach ($p in $picked) {
    [void]$lines.Add(("{0}. `{1}` - {2} - stages={3} - score={4} - risk={5} - placement={6}" -f $i, $p.id, $p.title, $p.stage_targets, $p.score, $p.risk, $p.placement))
    $i++
  }
}
[void]$lines.Add("")
[void]$lines.Add("## Artifacts")
[void]$lines.Add("- Combined: $combined")
[void]$lines.Add("- Ranked: $rankedCsv")
[void]$lines.Add("- Summary: $summaryPath")
[void]$lines.Add("")
[void]$lines.Add("## Acceptance")
[void]$lines.Add("- host usable 11/11")
[void]$lines.Add("- no camera falls to Partial/No vs L52")
[void]$lines.Add("- critic notes any pillar movement; overall may still FAIL")
($lines -join "`r`n") | Set-Content -LiteralPath $selected -Encoding utf8

Write-Host ("WAVE_DONE proposals={0} rank_exit={1} selected={2}" -f $all.Count, $rankExit, $picked.Count)
Write-Host ("selected_md={0}" -f $selected)
Write-Host ("ranked_csv={0}" -f $rankedCsv)
exit 0


