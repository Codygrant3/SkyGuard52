# Phase 8 — Windows Packaging and Final Acceptance

Updated: 2026-08-01  
Authority: cooked Unreal Engine 5.8 Windows packages

## Release boundary

`D:\Skyguard52\Binaries\Win64\Skyguard52.exe` is an uncooked local Development
binary. It is never a distributable package and can never satisfy Phase 8.

Final acceptance requires two attempt-scoped UAT archives:

- Windows Development for profiling and mission soaks;
- Windows Shipping for the friend-facing release candidate.

Both must contain `Skyguard52.exe` and cooked `.pak` or IoStore `.utoc/.ucas`
containers. Shipping promotion additionally rehashes every archived file.

## Release tiers and authentic audio

The release-tier contract is:

`D:\Skyguard52\Docs\AAA_Review\PHASE8_RELEASE_TIER_CONTRACT.json`

- `Engineering` preserves internal baselines with an explicit, receipt-bound
  audio exception. It forbids external distribution and Shipping promotion.
- `AAA` requires the Phase 5 audio Shipping boundary to pass.
- `FriendFacing` requires the same production-audio pass before a package may
  be built for friends or any external recipient.

The tier preflight executes before UAT or packaging. Current AAA and
FriendFacing preflights correctly stop with exit code `3`.

Full command guidance:

`D:\Skyguard52\Docs\AAA_Review\PHASE8_RELEASE_TIER_AUDIO_INTEGRATION.md`

## Guarded execution

Offline validation:

```powershell
powershell -ExecutionPolicy Bypass -File `
  D:\Skyguard52\Scripts\run_skyguard_phase8_release_gate.ps1 `
  -ValidateOnly
```

Canonical release candidate:

```powershell
powershell -ExecutionPolicy Bypass -File `
  D:\Skyguard52\Scripts\run_skyguard_phase8_release_gate.ps1
```

The unqualified command remains an Engineering baseline for backward
compatibility. It is not a friend-facing release command.

The runner refuses to launch beside active Unreal, Skyguard, UBT, Automation
Tool, or shader-worker processes. UAT and every packaged runtime have a hard
deadline, exact PID, preserved stdout/stderr, and exact descendant termination
only after timeout.

Attempts are immutable:

`D:\Skyguard52\Saved\Releases\Phase8\attempt_<UTC timestamp>\`

Latest report:

`D:\Skyguard52\Saved\Reports\PHASE8_RELEASE_GATE_LATEST.json`

## Required gates

### Packaging

- UAT `BuildCookRun` success for Development and Shipping;
- Win64 build, cook, stage, pak, IoStore, archive, and prerequisites;
- packaged executable plus cooked containers;
- no fatal, assertion, GPU crash, OOM, access violation, Blueprint/property,
  linker, or class errors;
- SHA-256 verification of every Shipping archive file.

### Input

Static bindings must exist for:

- mouse turn/look;
- left-click fire;
- right-click ADS press and release;
- rifle/Igla switch;
- Igla launch.

A packaged runtime receipt must also prove fire-while-ADS, weapon switching,
Igla launch/lock loss, pilot safety blocking, focus loss/recovery, and
mouse/controller settings behavior.

The receipt contract is:

`D:\Skyguard52\Docs\AAA_Review\PHASE8_RUNTIME_VALIDATION_RECEIPT_SCHEMA.json`

### Save and settings

Static types are insufficient. Packaged runtime validation must:

1. write campaign state to a named save slot;
2. terminate the process;
3. reload and verify mission score, medal, and unlock state;
4. reject or migrate an incompatible save version;
5. change resolution/fullscreen/scalability/audio/input settings;
6. apply and persist them;
7. relaunch and verify their round trip;
8. restore a controlled test profile afterward.

### Shader and PSO

- capture PSOs from representative combat across all missions;
- merge and stabilize the cache against the exact Shipping build;
- enable `ShaderPipelineCache` runtime consumption;
- package the matching `.upipelinecache`/stable cache;
- warm critical mission assets during the briefing;
- verify zero critical PSO misses during ADS, rifle fire, Igla launch, drone
  breakup, boss destruction, weather transitions, and first mission camera
  movement.

### Mission soak

`PHASE8_MISSION_SOAK_MATRIX.json` is the canonical campaign list. Every mission
needs a unique cooked map and a bounded Development-package soak. The present
file deliberately records Missions 2-10 as `NOT_AUTHORED`; they are blockers,
not skipped tests.

Each soak requires:

- D3D12/SM6 initialization;
- exact map load;
- at least five minutes;
- benchmark-driven bounded exit;
- no crash receipt or critical log signature;
- stable memory and frame pacing reviewed through CSV/Insights;
- input-driven combat coverage added before final acceptance.

The Shipping package then receives a separate startup smoke.

### Crash and logs

The runner snapshots project and CrashReportClient crash directories before and
after execution. Any new crash artifact fails acceptance. Absence of a crash
folder does not override fatal log evidence.

### Provenance

Every third-party file must have source, publisher/creator, license, version,
acquisition date, intended use, and hash. `PASS_WITH_PROVENANCE_GAPS` is not a
release pass.

## Current honest blockers

Offline inspection currently shows:

- Mission 1 has a vertical-slice map; Missions 2-10 do not have authored maps;
- versioned campaign `SaveGameToSlot`/`LoadGameFromSlot` integration is now
  implemented with slot validation, campaign binding, value sanitization, disk
  round-trip automation, and incompatible-version rejection. The focused native
  disk-slot test passed on 2026-08-02 with exactly one discovered test, one
  success, zero failures, and no fatal/assert/ensure markers;
- `USkyguardGameUserSettings` now applies and saves clamped master-volume,
  sensitivity, look-inversion, camera-shake, VSync, frame-limit, scalability,
  resolution and window-mode preferences. Both focused settings tests passed on
  2026-08-02 with exactly two discovered tests, two successes, zero failures,
  and no fatal/assert/ensure markers;
- PSO consumption and component precaching are enabled in background mode, but
  no stabilized `.upipelinecache` has been captured or packaged;
- the Mission 1 provenance ledger is `PASS_WITH_PROVENANCE_GAPS`;
- there is no packaged runtime input/save/settings round-trip receipt.

Therefore Phase 8 cannot pass yet, even if UAT packaging itself succeeds.

The immutable focused-test evidence is:

- `Saved/Releases/Phase8/native_verification_20260802T015928126Z/`
- `Saved/Reports/PHASE8_NATIVE_VERIFICATION_LATEST.json`

The receipt is bound to the native module, relevant source/configuration files,
and exact automation logs with SHA-256 hashes. A superseded launcher attempt at
`native_verification_20260802T015840202Z` is retained separately; it failed in
Windows command quoting before Unreal Build Tool started and is not counted.

## Acceptance authority

The independent verifier—not UAT exit code—decides the gate. It returns `PASS`
only when every package, mission, runtime validation, PSO, crash, hash, and
provenance requirement is supported by current attempt evidence.
