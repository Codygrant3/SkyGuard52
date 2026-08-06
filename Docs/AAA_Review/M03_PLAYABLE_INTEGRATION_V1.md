# Skyguard 52 — Mission 3 Playable Integration v1

## Scope

This gate preserves
`/Game/Skyguard/Maps/Campaign_v1/Lvl_M03_ConvoyEscort_Assembly_v1`
and promotes a separate candidate:
`/Game/Skyguard/Maps/Campaign_v1/Lvl_M03_ConvoyEscort_Playable_v1`.

## Deterministic contract

- Three governed waves contain 2, 3 and 4 threats.
- The first wave releases the convoy from holding state.
- A native convoy anchor moves along the accepted map's route spline.
- The convoy must reach the tunnel with integrity above zero.
- Convoy integrity reaching zero fails `ProtectConvoyCore` and the mission.
- Rifle fire destroys Road Hunter's targeting camera and exposes both wing
  actuators.
- Destroying both actuators creates the engine lock window.
- The normal finish uses an Igla against the exposed engine.
- An orbit-left or orbit-right command may instead arm a harder rifle engine
  finish.
- The camera advances `BlindTargetingCamera`; four physical components advance
  `DefeatRoadHunter`.
- Pilot commands propagate to the Yak-52.
- Final breakup uses exactly three preallocated debris components.

## Files and gate

- `SkyguardRoadHunterBoss.h/.cpp`
- `SkyguardRoadHunterBossTests.cpp`
- `SkyguardMission03IntegrationDirector.h/.cpp`
- `SkyguardMission03IntegrationTests.cpp`
- `build_skyguard_m03_playable_integration.py`
- `verify_skyguard_m03_playable_integration.py`
- `run_skyguard_m03_playable_integration_gate.ps1`

Run only while the shared Unreal lane is idle:

```powershell
powershell -ExecutionPolicy Bypass -File `
  D:\Skyguard52\Scripts\run_skyguard_m03_playable_integration_gate.ps1
```

## Honest limitations

- Highway, bridge, tunnel and convoy visuals remain proxy art.
- The native convoy anchor is the movement authority, but final vehicle meshes,
  wheel animation and formation following are not yet attached.
- Road Hunter uses placeholder geometry pending its Blender hero build.
- Native tests do not prove player possession, rendered fidelity, audio mix,
  performance, or packaged playability.
- This gate does not package the game.
