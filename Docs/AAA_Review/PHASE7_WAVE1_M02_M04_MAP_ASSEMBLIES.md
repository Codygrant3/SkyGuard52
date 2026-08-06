# Skyguard 52 — Campaign Map Wave 1: M02–M04

Updated: 2026-08-01  
Runtime target: Unreal Engine 5.8  
Status: offline implementation ready; Unreal execution pending explicit shared
lane release

## Accepted target paths

- `/Game/Skyguard/Maps/Campaign_v1/Lvl_M02_HarborShield_Assembly_v1`
- `/Game/Skyguard/Maps/Campaign_v1/Lvl_M03_ConvoyEscort_Assembly_v1`
- `/Game/Skyguard/Maps/Campaign_v1/Lvl_M04_NightBlackout_Assembly_v1`

These are spatial/gameplay assemblies with placeholder art. They are not final
environment maps.

## Native assembly boundary

`ASkyguardMissionMapAssemblyDirector` binds each map to its validated
`USkyguardMissionDefinition`. A map passes only when:

- its mission id matches the referenced DataAsset;
- its route reproduces the DataAsset route exactly;
- the route contains at least four points and spans at least 300 metres;
- every required objective has one valid map anchor;
- landmark ids are unique;
- at least three landmark roles are present;
- at least two landmarks are mission-exclusive.

It also provides a segment-based flight-clearance query so hero placeholders
and later PCG/scenery passes can remain outside the aircraft corridor.

## Map identities

### M02 — Harbor Shield

- industrial harbor skyline;
- four-crane corridor set away from the authored flight route;
- three piers, fuel terminal, container ship and offshore submarine silhouette;
- port aprons rather than a coastal highway/grid;
- defended fuel-terminal and Breakwater objective anchors.

### M03 — Convoy Escort

- diagonal coastal-highway route;
- relief convoy with command truck, buses and cars;
- bridge crossing and tunnel destination silhouettes;
- ridge settlement skyline;
- moving convoy-core and Road Hunter objective anchors.

### M04 — Night Blackout

- dense blackout urban skyline;
- emergency substation;
- paired searchlight-battery placeholders;
- waterfront radar bearing reference;
- street-lamp corridor and damaged/vertical tower silhouettes;
- substation and Black Kite objective anchors;
- low-intensity night directional-light profile.

All three reuse the coastal apartment/block kit and simple coast/ocean surfaces,
but their route coordinates, skyline style, placement signature, objective
positions and exclusive landmarks are different. The verifier rejects cloned
layout signatures.

## Offline deliverables

- native director:
  `Source/Skyguard52/SkyguardMissionMapAssemblyDirector.*`;
- native automation:
  `SkyguardMissionMapAssemblyDirectorTests.cpp`;
- idempotent builder:
  `Scripts/build_skyguard_phase7_wave1_mission_maps.py`;
- fresh-process verifier:
  `Scripts/verify_skyguard_phase7_wave1_mission_maps.py`;
- guarded supervisor:
  `Scripts/run_skyguard_phase7_wave1_mission_map_gate.ps1`.

The supervisor rejects an occupied Unreal/build lane, scans Python logs rather
than trusting process exit alone, and runs builder, separate-process verifier,
then focused native automation.

## Honest limitations

- Existing proxy meshes and engine primitives remain clearly visible.
- Terrain surfaces are simple assembly geometry, not sculpted production
  landscapes.
- Roads, port aprons, bridge and tunnel are spatial placeholders.
- Cranes, convoy vehicles, searchlights and environmental actors are not yet
  connected to mission behavior.
- Boss actors, weak points, waves, objectives, weather application, audio and
  cinematics are not yet integrated into these maps.
- No visual-quality, collision, streaming, GPU, packaged-runtime or playability
  claim is made at this stage.

The purpose of this wave is to establish genuinely different, DataAsset-driven
map spaces that later art and gameplay work can refine without rebuilding the
campaign structure.
