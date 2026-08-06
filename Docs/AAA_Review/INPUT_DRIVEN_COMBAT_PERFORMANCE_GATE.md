# Input-driven combat performance gate

## Scope

This gate is the missing evidence path for P1.4, P1.5, P8.10, P8.11, and
P8.12. It does not replace the accepted fixed-route Phase 1 baseline.

The governed matrix requires:

- three 120-second, 1920x1080 input-driven combat profiles;
- one 20-minute input-driven combat soak;
- D3D12/SM6, 60 fps target, CSV and Unreal Insights;
- `memory` in the trace channel list;
- process-relative `GPUUsage/Memory`, texture-streaming, Nanite-streaming,
  level-streaming, and physical-memory CSV counters;
- one-second global adapter samples from `nvidia-smi`;
- five runtime-authored contextual windows: ADS+rifle, Igla, drone breakup,
  boss destruction, and weather plus fast camera movement.

## Current validate-only command

```powershell
Set-Location D:\Skyguard52
.\Scripts\run_skyguard_input_combat_performance_gate.ps1 -ValidateOnly
```

This command never launches Unreal. It writes a fail-closed receipt to:

`Saved/Reports/INPUT_COMBAT_PERFORMANCE_GATE_LATEST.json`

## Runtime instrumentation

The runtime now wraps the actual player-triggered path with:

- a trace region named exactly as the contract's `region`;
- a begin bookmark named exactly as `begin_bookmark`;
- an end bookmark named exactly as `end_bookmark`.

The begin marker precedes the first player-triggered work. Each end marker is
tied to a real lifecycle event:

- ADS release;
- Igla impact;
- drone breakup lifespan cleanup;
- bounded boss-debris cleanup;
- completion of the coastal haze transition.

The boss destruction window begins at the first destroyed weak point. Every
trace window has a 30-second-or-smaller fail-safe bound, but a capture cannot
pass unless the corresponding lifecycle completion event is present.

The source scanner now finds all 15 required literals. Latest validate-only
attempt:

`Saved/Profiling/InputCombat/attempt_20260802T115603268Z`

Result:
`VALIDATED_CONTRACT_BLOCKED_PREREQUISITE`, with runtime marker coverage
`15/15`. Literal presence is only a preflight; the later trace review must prove
each region occurred exactly in the player-driven run and had a valid duration.

## Telemetry interpretation

- `memory` trace data supports Memory Insights allocation analysis.
- `GPUUsage/Memory` is the engine's process-relative GPU-memory fraction when
  the active RHI reports it.
- `TextureStreaming/StreamingPool`, wanted/non-streaming mip counters, Nanite,
  and level-streaming counters provide workload context.
- `nvidia-smi` provides global adapter used/total memory and GPU utilization.
  It cannot replace the process-relative counter.

The gate fails closed when either GPU-memory path is missing.

## Acceptance boundary

Raw capture completion is not acceptance. Promotion requires:

1. all three combat profiles pass mean, p95, and >100 ms hitch thresholds;
2. all five windows are present and contextually reviewed in every profile;
3. no player-triggered first-use shader/PSO hitch;
4. the 20-minute soak stays within the governed memory-growth threshold and
   has no visible ADS/destruction pause;
5. memory, VRAM, texture/Nanite/level streaming, and critical logs are clean;
6. hashes bind every trace, CSV, GPU sample file, command contract, and report.

Every executed profile or soak also captures a bounded
`windows_machine_events.json` covering the run. It records NVIDIA
`nvlddmkm`/Display errors, WHEA hardware errors, Kernel-Power critical events,
Skyguard/Unreal application faults, and Nahimic service faults. This prevents a
driver or audio-service reset from being misclassified as a game-only hitch.

The latest exact-package preflight proves Entry and M01 both render visibly,
write `COMPLETE` D3D12/SM6 receipts, exit naturally with code zero, and emit no
GPU or critical device signatures. Authorization remains fail-closed on two
exact inbound firewall Block rules and the injected NVIDIA App
`nvspcap64.dll` hook. Until those machine-policy findings pass and the measured
runs are captured and reviewed, all five requirements remain incomplete or
insufficiently evidenced.
