# Phase 1 Performance and Stability Gate

Updated: 2026-08-01  
Authority: Unreal Engine 5.8 Windows Development runtime

## Purpose

This gate prevents a normal process exit or a short rendered launch from being
misreported as combat-performance acceptance. It produces immutable,
attempt-specific logs, an Unreal Insights trace, an Unreal CSV capture, and a
machine-readable verdict.

The default run:

1. refuses to start while another Unreal or Skyguard process is active;
2. rebuilds `Skyguard52 Win64 Development`;
3. runs both native Pathfinder combat/destruction automation tests;
4. launches the freshest Development runtime on the Mission 1 `_v3` map using
   D3D12, SM6, 1920 x 1080, and a bounded benchmark window;
5. captures CPU/GPU/frame/load/asset Unreal Insights channels;
6. captures Unreal CSV frame and GPU statistics;
7. terminates only the exact supervised PID tree if a hard timeout expires;
8. independently parses raw artifacts and logs rather than trusting exit codes.

An explicit nonzero exit code always fails its stage. If Windows PowerShell
cannot recover an exit code from a redirected process after observing its
bounded exit, the report leaves the code `null` and requires the stronger
stage-specific semantic completion markers (exact automation queue or
benchmark-driven engine exit). It never invents an exit code.

## Canonical command

Close visible Unreal editors and run:

```powershell
powershell -ExecutionPolicy Bypass -File `
  D:\Skyguard52\Scripts\run_skyguard_phase1_performance_gate.ps1
```

Fast harness validation without launching Unreal:

```powershell
powershell -ExecutionPolicy Bypass -File `
  D:\Skyguard52\Scripts\run_skyguard_phase1_performance_gate.ps1 `
  -ValidateOnly
```

Short diagnostic profile:

```powershell
powershell -ExecutionPolicy Bypass -File `
  D:\Skyguard52\Scripts\run_skyguard_phase1_performance_gate.ps1 `
  -DurationSeconds 20 -ResolutionX 1280 -ResolutionY 720
```

Do not use a short diagnostic run for release promotion.

The verifier labels a successful shortened, reduced-resolution, build-skipped,
or automation-skipped run `DIAGNOSTIC_PASS_NOT_PROMOTABLE`. Only a run that
rebuilds, retains automation, captures at least 60 seconds, and runs at no less
than 1920 x 1080 can return the promotion verdict `PASS`.

## Evidence layout

Each attempt is preserved under:

`D:\Skyguard52\Saved\Profiling\Phase1\attempt_<UTC timestamp>\`

It contains:

- `run_manifest.json`: commands, exact PIDs, deadlines, exit codes, and runtime
  selection;
- `logs\`: separate stdout and stderr for every stage;
- `artifacts\phase1_runtime.utrace`: Unreal Insights capture;
- `gate_report.json`: independent verifier output;
- the Unreal-generated CSV path recorded in both JSON files.

Unreal 5.8 may write editor-game CSV captures below
`%LOCALAPPDATA%\UnrealEngine\5.8\Saved\Profiling\CSV`. The runner snapshots that
location as well as the project profiling directory, and the verifier also
extracts the authoritative `Writing CSV to file` path from the raw runtime log.

The most recent verdict is copied to:

`D:\Skyguard52\Saved\Reports\PHASE1_PERFORMANCE_GATE_LATEST.json`

Attempts are never overwritten or renamed.

## Gates

### Stability smoke

PASS requires all of the following:

- no process timeout;
- Development build success, unless explicitly skipped;
- both exact Pathfinder tests complete with `Result={Success}`;
- the automation queue reports exactly two completed tests;
- D3D12/SM6 runtime initialization;
- requested map load and world play startup;
- benchmark-driven exit;
- no fatal error, assertion, GPU crash, OOM, access violation, Blueprint error,
  property error, linker error, or class error;
- nontrivial `.utrace` and CSV artifacts.

### Performance

The initial Mission 1 target is:

- mean frame time at or below 16.7 ms;
- p95 frame time at or below 22.2 ms;
- maximum hitch at or below 100 ms;
- zero frames above 100 ms.

The verifier discards the first 120 numeric CSV frames as a bounded shader,
streaming, and map-start warm-up interval. It records the discarded count and
does not discard later combat or destruction hitches.

If the CSV cannot be parsed, the verifier returns
`SMOKE_PASS_PERFORMANCE_UNVERIFIED`; it does not infer frame performance from
the process exit or trace size.

## Current automation boundary

The native Pathfinder tests exercise:

- rifle rejection against protected weak points;
- command antenna and nose-camera rifle destruction;
- Igla lock eligibility and engine strike;
- rifle finishing shot;
- all five pilot commands and authored route behavior;
- fixed three-piece breakup;
- bounded attack telegraphs and route/altitude safety.

They run in an editor-context game world under NullRHI. They do not yet drive
mouse ADS, a visible gunner pawn, live projectiles, Niagara appearance, audio,
or a full packaged mission. A later Gauntlet/input soak must add those behaviors
without weakening this deterministic native gate.

## Promotion rule

Phase 1 is not green until:

1. this harness returns `PASS` on repeated full-resolution runs;
2. Unreal Insights review confirms the CSV result and identifies no hidden
   load, streaming, shader, Niagara, or memory spike;
3. a 20-minute input-driven combat soak completes with stable memory and no
   visible ADS/destruction hitch.

## Executed diagnostic evidence

The corrected end-to-end diagnostic is:

`Saved/Profiling/Phase1/attempt_20260802T012344774Z/`

Its independently reverified verdict is
`DIAGNOSTIC_PASS_NOT_PROMOTABLE`, with:

- both exact Pathfinder tests completing with `Result={Success}`;
- D3D12 and SM6 initialization on an NVIDIA GeForce RTX 3090;
- `_v3` map load and benchmark-driven exit;
- zero fatal, assertion, GPU-crash, OOM, Blueprint/property/linker/class, or
  unhandled-exception signatures;
- a 27 MB-class Unreal Insights trace;
- 480 analyzed CSV frames after discarding 120 warm-up frames;
- 10.7414 ms mean and 13.4781 ms p95 frame time;
- 18.5894 ms maximum analyzed frame time;
- zero frames above 50 ms or 100 ms;
- 5.2304 ms mean and 7.9597 ms p95 GPU time.

This result is intentionally not a Phase 1 promotion because it skipped the
Game-target rebuild and used a 10-second, 1280 x 720 EditorGame diagnostic.
The canonical full run remains the command in the first section.

### First canonical attempt retained as a failed receipt

`Saved/Profiling/Phase1/attempt_20260802T012639559Z/` completed the 60-second
1920 x 1080 automation/runtime profile, but the overall gate is correctly
`FAIL`. The first build command was over-quoted, and `cmd.exe` reported that
the literal quoted batch path was not recognized. Although that shell returned
zero, the verifier rejected the build because the raw log lacked
`Result: Succeeded` or `Target is up to date`.

The non-build evidence from that failed attempt is still useful and preserved:

- both Pathfinder automation tests passed;
- D3D12 runtime, requested map load, and benchmark exit passed;
- 129,287,115-byte Insights trace;
- 3,480 analyzed frames after the bounded 120-frame warm-up;
- 11.2091 ms mean, 14.3441 ms p95, 16.1340 ms p99, and 19.6175 ms maximum
  frame time;
- 7.0211 ms mean and 10.7168 ms p95 GPU time;
- zero frames above 50 ms or 100 ms;
- zero critical signatures in build, automation, or runtime logs.

The runner now constructs the single `/c` payload without pre-quoting its
space-free batch and project paths. A new complete attempt is required before
Phase 1 can be promoted.
