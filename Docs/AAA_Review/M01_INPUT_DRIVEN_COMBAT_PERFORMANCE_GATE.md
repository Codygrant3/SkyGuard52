# Skyguard 52 — M01 Input-Driven Combat Performance Gate

Updated: 2026-08-02  
Runtime target: packaged Unreal Engine 5.8 Windows Development  
Status: supervisor/verifier/native telemetry hook and offline tests complete;
fresh Unreal compile/package/runtime proof pending  
Map:
`/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_Playable_v1`

## Purpose

This gate closes the explicit Phase 1/Phase 8 evidence gap. It cannot pass from
a benchmark route, native automation, static bindings, a process exit, or a
human assertion that combat occurred. It requires exactly:

1. three 180-second, 1920×1080 input-driven packaged combat captures; and
2. one 1,200-second input-driven packaged combat/memory soak.

Every measured window must contain real player-input evidence for:

- player aiming input;
- ADS start;
- ADS held concurrently with left fire;
- at least five rifle shots;
- a weapon switch;
- Igla lock acquisition;
- Igla launch;
- drone breakup;
- boss destruction; and
- one weather or visibility transition.

## Implemented offline tooling

- supervisor:
  `D:\Skyguard52\Scripts\run_skyguard_m01_input_combat_performance_gate.ps1`;
- independent verifier:
  `D:\Skyguard52\Scripts\verify_skyguard_m01_input_combat_performance_gate.py`;
- verifier tests:
  `D:\Skyguard52\Scripts\tests\test_verify_skyguard_m01_input_combat_performance_gate.py`.

The supervisor:

- refuses any map other than exact M01;
- refuses an occupied Unreal/Skyguard build lane;
- uses a packaged Development executable, never the uncooked local binary;
- binds the attempt to SHA-256 hashes for the executable, source map,
  `.uproject`, three runtime configs, and packaged SM6 PSO cache;
- creates an immutable
  `Saved\Profiling\M01InputCombat\attempt_<UTC>` directory;
- launches the four stages sequentially at 1920×1080, D3D12/SM6, with VSync
  disabled;
- captures separate stdout/stderr, CSV, `.utrace`, runtime receipt, and
  one-second process-memory samples for every stage;
- supervises the exact PID and terminates only its process tree after a hard
  timeout;
- writes `FAILED_HARNESS` on orchestration failure;
- hands the raw manifest to the independent verifier;
- publishes a latest report only after an attempt-specific report exists.

The verifier:

- treats the manifest and every runtime receipt as untrusted;
- re-hashes every executable/map/config/PSO binding;
- requires the exact ordered stage set
  `combat_01`, `combat_02`, `combat_03`, `soak_01`;
- requires runtime receipt schema, exact map, 1920×1080, D3D12/SM6,
  `input_source=PlayerInput|EnhancedInput`, and
  `automation_injected=false`;
- derives required event counts from timestamped events rather than trusting a
  summary counter;
- rejects events outside the measurement window or out of timestamp order;
- parses Unreal CSV through the existing Phase 1 analyzer;
- requires mean ≤16.7 ms, p95 ≤22.2 ms, max ≤100 ms, and zero frames >100 ms;
- requires enough frames to cover each window;
- analyzes working-set samples after a bounded startup discard;
- for the soak, requires slope ≤8 MiB/minute and first-to-last-quarter median
  growth ≤256 MiB;
- scans for fatal, assertion, GPU crash/device removal, OOM, access violation,
  unhandled exception, Blueprint/property/linker/class errors;
- requires the bundled cache-open marker, completed PSO precompile marker,
  `0 had missing shaders`, and no cache/shader failure;
- requires a nontrivial trace and hashes every stage artifact.

## Native runtime hook

The project now contains:

- `Source\Skyguard52\SkyguardInputCombatPerformanceCapture.h`
- `Source\Skyguard52\SkyguardInputCombatPerformanceCapture.cpp`

The hook parses:

- `SkyguardCombatPerfRunId`
- `SkyguardCombatPerfKind`
- `SkyguardCombatPerfDurationSeconds`
- `SkyguardCombatPerfReceipt`
- `SkyguardCombatPerfExpectedMap`

It does not generate combat events or invoke gameplay functions. It is an
inert-by-default observer and bounded lifecycle controller. It starts only
after the exact expected world begins play, starts/stops Unreal CSV capture,
writes the receipt, and requests a clean exit after the requested duration.

### Required instrumentation

Actual gameplay paths are instrumented as follows:

| Receipt event | Required source of truth |
|---|---|
| `ads_started` | real ADS input handler after the input event is accepted |
| `ads_left_fire_overlap` | real left-fire input while ADS remains active |
| `rifle_shot` | an accepted rifle discharge, not merely a button press |
| `weapon_switch` | an accepted player weapon-mode change |
| `igla_lock_acquired` | lock progress crossing to acquired on a valid target |
| `igla_launch` | an actual spawned/initialized Igla missile |
| `drone_breakup` | bounded breakup activation on a defeated drone |
| `boss_destroyed` | boss phase entering `Defeated` |
| `weather_visibility_transition` | a real environment visibility/weather state change, not a timer-only synthetic marker |

Implemented integration points:

- `ASkyguardGunner::ADSPressed`, `FirePressed`/accepted rifle discharge,
  `SwitchWeapon`, `UpdateIglaLock`, and `FireIgla`;
- `ASkyguardBossDroneBase::HandleDefeated` after bounded breakup activation;
- `ASkyguardMission01EnvironmentDirector` after the coastal-haze density change
  is applied.

Input bindings now use dedicated wrappers, so the older direct method calls
used by Phase 8 static/runtime contract validation do not create input-combat
events. Rifle telemetry occurs only after the pilot safety arc accepts the
shot. Igla launch telemetry occurs only after a missile actor is spawned and
initialized. Breakup telemetry occurs only after the bounded debris count is
calculated and at least one registered piece is activated.

### Required runtime receipt

The hook must write the path supplied by `SkyguardCombatPerfReceipt`:

```json
{
  "schema": "skyguard.m01.input-combat.runtime-receipt.v1",
  "state": "COMPLETE",
  "gate": "PASS",
  "run_id": "combat_01",
  "map": "/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_Playable_v1",
  "resolution": { "x": 1920, "y": 1080 },
  "rhi": "D3D12 (SM6)",
  "input_source": "PlayerInput",
  "automation_injected": false,
  "measurement_window": {
    "started_at_utc": "ISO-8601 UTC",
    "ended_at_utc": "ISO-8601 UTC",
    "duration_seconds": 180
  },
  "events": [
    {
      "name": "ads_started",
      "seconds_from_measurement_start": 3.25
    }
  ]
}
```

`gate=PASS` is allowed only when the requested duration elapsed and all
required events occurred from actual player input/gameplay during the window.
The hook must write `gate=FAIL` with explicit issues otherwise. It must stop
CSV/trace capture, flush the receipt, and request a clean zero process exit
only when the artifact is safely persisted. A failed evidence run should still
exit cleanly after writing `gate=FAIL`; the independent verifier owns the final
verdict.

## Weather/visibility transition

`ASkyguardMission01EnvironmentDirector` now applies one bounded coastal-haze
cycle during normal M01 play:

- 30-second clear-air lead-in;
- eight-second fade into haze;
- twelve-second hold;
- eight-second recovery to the original fog density.

The environment director owns and applies this actual world-state change. The
telemetry subsystem merely observes the completed fade-in. If no
`AExponentialHeightFog` exists, no transition is recorded and the gate fails
closed.

## Preflight

This command launches no Unreal process:

```powershell
powershell -ExecutionPolicy Bypass -File `
  D:\Skyguard52\Scripts\run_skyguard_m01_input_combat_performance_gate.ps1 `
  -PackageAttemptRoot `
  D:\Skyguard52\Saved\Releases\Phase8\attempt_<fresh-hook-build> `
  -ValidateOnly
```

Expected result against the old accepted attempt:

`status=BLOCKED_RUNTIME_HOOK_MISSING`

The source hook now passes preflight inspection, but the packaged executable
must also contain the receipt-schema marker. Compile and package a fresh
Development/Shipping attempt, then rerun preflight. Do not use the accepted
`attempt_20260802T092516016Z`; its executable predates this telemetry contract.

## Exact later execution command

With Unreal, UAT, shader workers, and Skyguard closed:

```powershell
powershell -ExecutionPolicy Bypass -File `
  D:\Skyguard52\Scripts\run_skyguard_m01_input_combat_performance_gate.ps1 `
  -PackageAttemptRoot `
  D:\Skyguard52\Saved\Releases\Phase8\attempt_<fresh-hook-build>
```

The game window opens four times. Play each window continuously and complete
the full event checklist before its timer ends. The final soak lasts twenty
minutes. Do not switch to another app during a measured run.

## Acceptance

Promotion requires:

- supervisor `terminal_state=EXECUTION_COMPLETE`;
- independent verifier `gate=PASS`;
- exactly four stage reports and no reused artifacts;
- every event requirement in every stage;
- all four frame budgets;
- stable memory checks, including the 20-minute trend;
- clean PSO, shader, crash, and critical-log checks;
- exact binding hashes valid;
- no runtime-hook or verifier bypass.

Passing this gate closes the original ADS/drone-breakup freeze concern for the
tested package. Any later promotion that changes M01 foreground art, combat
VFX, destruction, weather, materials, shader coverage, or streaming must
refresh this evidence and the Phase 8 release gate.
