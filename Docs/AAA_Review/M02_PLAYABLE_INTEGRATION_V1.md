# Skyguard 52 — Mission 2 Playable Integration v1

## Scope

This gate promotes the accepted proxy assembly
`/Game/Skyguard/Maps/Campaign_v1/Lvl_M02_HarborShield_Assembly_v1`
into the separately governed candidate
`/Game/Skyguard/Maps/Campaign_v1/Lvl_M02_HarborShield_Playable_v1`.
The source map is preserved.

## Deterministic gameplay contract

- Three governed waves contain exactly 2, 3 and 4 threats.
- Clearing the last wave opens the Breakwater encounter.
- Fuel-terminal integrity reaches a terminal failure at zero.
- Port latch exposes starboard latch; starboard latch exposes decoys.
- Destroying decoys creates the Igla engine-lock window.
- Normal route: Igla engine strike, then rifle elevator-linkage finish.
- Emergency route: after an orbit command, the player may expose and sever
  the elevator linkage using the rifle without expending an Igla.
- Both routes complete four governed boss-progress steps.
- Two latch destructions complete `StripArmorPanels`.
- Pilot commands propagate to the Yak-52 runtime.
- Breakwater defeat uses exactly three preallocated debris components.

## Offline implementation

- `SkyguardBreakwaterBoss.h/.cpp`
- `SkyguardBreakwaterBossTests.cpp`
- `SkyguardMission02IntegrationDirector.h/.cpp`
- `SkyguardMission02IntegrationTests.cpp`
- `build_skyguard_m02_playable_integration.py`
- `verify_skyguard_m02_playable_integration.py`
- `run_skyguard_m02_playable_integration_gate.ps1`

## Heavy validation command

Run only while the shared Unreal lane is idle:

```powershell
powershell -ExecutionPolicy Bypass -File `
  D:\Skyguard52\Scripts\run_skyguard_m02_playable_integration_gate.ps1
```

The supervisor compiles the editor target, duplicates/composes the playable
candidate, performs a separate-process persistence audit, then requires four
focused native automation tests.

## Honest limitations

- The harbor environment remains proxy art.
- Breakwater currently uses native placeholder geometry. Its production
  Blender body, armor panels, decoy pods, engine and breakup parts remain an
  art-production task.
- The native tests prove deterministic state and objective behavior, not
  player possession, input, rendered fidelity, audio mix, performance or
  packaged playability.
- No packaging is performed by this gate.
