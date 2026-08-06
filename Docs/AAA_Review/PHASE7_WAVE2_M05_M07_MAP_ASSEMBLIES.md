# Skyguard 52 — Campaign Map Wave 2: M05–M07

Updated: 2026-08-01  
Runtime target: Unreal Engine 5.8  
Status: offline implementation ready for the parent-owned global compile

## Accepted target paths

- `/Game/Skyguard/Maps/Campaign_v1/Lvl_M05_StormFront_Assembly_v1`
- `/Game/Skyguard/Maps/Campaign_v1/Lvl_M06_AirfieldDefense_Assembly_v1`
- `/Game/Skyguard/Maps/Campaign_v1/Lvl_M07_SearchIntercept_Assembly_v1`

These are governed spatial/gameplay assemblies with placeholder art—not final
environment maps.

## Shared native extension

The reusable `ASkyguardMissionMapAssemblyDirector` now supports:

- `OffshoreStorm`, `AirfieldMilitary`, and `IslandSearch` skyline identities;
- an authored `WeatherProfileId`;
- native enforcement that the map weather identity matches its validated
  mission DataAsset.

The earlier Wave 1 builder was updated to populate the new weather field, so
the shared contract remains coherent across M02–M07.

## M05 — Storm Front

- SevereSquall weather identity;
- open-ocean route;
- distressed trawler;
- offshore platform/deck/crane silhouette;
- authored sea-stack gate;
- ten storm-buoy navigation markers;
- dedicated Tempest spawn;
- three objective anchors, including the discharge-boom mechanic.

Exclusive landmarks: distressed trawler, offshore platform, sea-stack gate.

## M06 — Airfield Defense

- AirfieldHaze weather identity;
- primary runway and separate taxiway;
- control-tower silhouette;
- six-hangar line;
- paired hardened shelters;
- two air-defense positions;
- parked-aircraft proxy line;
- dedicated Runway Breaker spawn;
- three objective anchors covering protected assets, payload racks and boss.

Exclusive landmarks: runway, control tower and hardened shelters.

## M07 — Search and Intercept

- IslandMist weather identity;
- four separated islands rather than a continuous coast;
- governed radar and lighthouse hero proxies;
- three-vessel fishing fleet used as identification traffic;
- outer-island radar truck/search boundary;
- island-specific vegetation clusters;
- dedicated Radar Ghost spawn;
- three objective anchors covering radar protection, classification and boss.

Exclusive landmarks: island radar, lighthouse and fishing fleet.

## Differentiation gate

The fresh-process verifier requires:

- three unique route signatures;
- three unique skyline styles;
- three unique weather profiles;
- three unique objective layouts;
- three unique boss-spawn positions;
- three non-cloned placeholder placement signatures;
- at least four landmark roles and two exclusive landmarks per map;
- exact mission DataAsset references;
- native definition, route, objective, landmark and weather readiness;
- all landmark anchors outside the flight-clearance corridor.

## Offline deliverables

- `Scripts/build_skyguard_phase7_wave2_mission_maps.py`
- `Scripts/verify_skyguard_phase7_wave2_mission_maps.py`
- `Scripts/run_skyguard_phase7_wave2_mission_map_gate.ps1`

The supervisor refuses an occupied Unreal lane, scans logs for Python failures
even after exit code zero, uses a separate verifier process, and runs focused
native assembly automation.

## Honest limitations

- Existing proxy meshes and engine primitives remain visible.
- Storm water, rain, lightning, runway markings, hangars, shelters, islands and
  vegetation are layout placeholders.
- Persisted weather identity is not a completed weather presentation.
- Convincing terrain, Quixel/Fab art, lighting, collision, PCG, streaming and
  Nanite treatment remain future passes.
- Boss actors, waves, objective behavior, audio and cinematics are not yet
  connected.
- No packaged playability, visual-quality or performance claim is made.
