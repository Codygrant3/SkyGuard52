# Mission 1 Playable Integration v1

## Purpose

This gate composes previously accepted systems into the first playable campaign
map without replacing their owned implementation:

- source environment:
  `/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_ProductionEnvironment_v4_attempt02`
- target:
  `/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_Playable_v1`
- governed Mission 1 DataAsset:
  `/Game/Skyguard/Data/Campaign_v1/DA_Mission_M01_CoastalIntercept`
- native Yak-52 runtime and rear-gunner pawn;
- rifle and Igla combat already owned by `ASkyguardGunner`;
- native Pathfinder weak-point and encounter runtime;
- campaign objectives, route, scoring, and persistence;
- briefing warm-up, radio queue, and audio director.

## Native orchestration

`ASkyguardMission01IntegrationDirector` discovers existing actors before it may
spawn one native Yak, gunner, or Pathfinder. It mounts the gunner at the
validated rear-seat socket, forwards Pathfinder pilot commands to the Yak,
advances the boss and command-network objectives from bounded weak-point
telemetry, records radar survival at victory, and completes the campaign
mission when required objectives are satisfied.

`USkyguardMissionBriefingComponent` requires both the authored minimum reading
time and an explicit asset-readiness signal. UI may acknowledge it manually;
the Mission 1 director can auto-acknowledge after warm-up for the initial
playable slice.

## Idempotent composition

`build_skyguard_m01_playable_integration.py` always duplicates the accepted
source map into the governed target. It only replaces that exact target, keeps
the source intact, removes the static Pathfinder review proxy, places one
native integration director, one native Yak and one native Pathfinder, assigns
`ASkyguardGameMode`, and binds the Mission 1 DataAsset to the target map.

The fresh-process verifier requires exact actor cardinality, all three
presentation components, the accepted environment director, game mode binding,
and persisted DataAsset map binding.

## Execution

After the shared Unreal lane is released:

```powershell
& D:\Skyguard52\Scripts\run_skyguard_m01_playable_integration_gate.ps1
```

The supervisor performs one editor build, composition, a separate-process
persistence audit, and exactly two native tests under
`Skyguard52.Mission01Integration`. It hashes exact logs and never packages.

## Honest limitations

- Offline staging and NullRHI persistence do not prove real-time playability.
- Player possession, mouse look, ADS, rifle fire, Igla lock/launch, boss defeat,
  scoring, save/reload, audio output, and map travel still need an input-driven
  GPU runtime test.
- Radio text is present; this gate does not assert voiced radio assets.
- The native Pathfinder remains gameplay-valid, but this gate does not claim
  that its mesh/material assignment is the final AAA hero-art revision.
- The accepted Phase 4 coastline remains intentionally based on stable native
  primitives rather than the experimental Water/Landmass chain.
- No Shipping cook or Windows package is created by this gate.
