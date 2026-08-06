# Mission 1 Pathfinder Gameplay QA

## Gate result

**PASS — deterministic native Unreal automation**

Tests:

`Skyguard52.Boss.Pathfinder.SequenceAndBoundedDestruction`

`Skyguard52.Boss.Pathfinder.EncounterFlightAndAttackController`

Verified sequence:

1. Pathfinder starts in `Approach`; engine and control linkage are protected.
2. Rifle fire destroys the command antenna and nose camera.
3. The engine becomes exposed and the boss enters `LockWindow`.
4. Igla lock becomes eligible only during that window.
5. An Igla strike destroys the engine and advances the boss to `Critical`.
6. Igla lock closes and the control linkage becomes exposed.
7. Rifle fire destroys the linkage and advances the boss to `Defeated`.
8. Further damage and lock attempts are rejected.

Additional verified contracts:

- Rejected weapon/component combinations do not increment accepted-hit telemetry.
- Pilot commands update the current command and deterministic telemetry.
- Exactly four weak points register at begin play.
- Exactly three breakup pieces are preallocated.
- Breakup pieces cannot exceed the hard per-boss budget.
- Defeat removes the intact body from collision.

## Encounter flight and attack controller

The Pathfinder now owns a lightweight, tunable encounter controller rather than
a full flight simulator:

- `Approach` / `Disarm`: low-water ingress with bounded lateral drift.
- `LockWindow`: slower disrupted climb that exposes the engine.
- `Critical`: damaged broad turn with a bounded radius.
- `Defeated`: authored flight movement and attack telegraphs stop.

All five pilot commands have deterministic effects:

- `Pursuit` slows objective progress and presents a steadier approach.
- `Break` adds a bounded evasive weave and climb.
- `Orbit Left` and `Orbit Right` create opposite lateral firing presentations.
- `Extend` increases separation pressure by allowing faster objective progress.

The controller exposes route length, three phase speeds, ingress sway, climb
timing, critical-turn radius/timing, safety envelopes, command offsets, attack
intervals, telegraph lead time, simulation-step limits, and a hard telegraph
budget. It emits a bounded attack-commit event for a mission-owned pooled attack
presentation; it never spawns projectiles or effects itself.

The encounter automation verifies:

- command-specific movement effects;
- low-water, climb, broad-turn, and defeated phase behavior;
- rotated-route local-space correctness;
- lateral, altitude, finite-value, and route-progress safety invariants;
- hard route-end clamping;
- bounded telegraph/attack commits;
- no movement or attack telegraph after defeat.

## Evidence

- Editor build: `Result: Succeeded`
- Automation log: `D:\Skyguard52\Saved\Logs\PathfinderAutomation.log`
- Automation result: `Result={Success}`
- Tests performed: `2`

## Scope boundary

This validates combat sequencing, pilot-command hooks, and bounded breakup behavior.
It does not yet validate final imported meshes, audiovisual presentation, flight-path
AI, or frame-time behavior in the Mission 1 assembled map. Those remain map/import
and performance gates.
