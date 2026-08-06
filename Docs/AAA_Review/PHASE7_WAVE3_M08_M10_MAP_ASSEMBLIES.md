# Skyguard 52 Campaign Map Wave 3: M08-M10

Runtime target: Unreal Engine 5.8  
Status: offline implementation ready; global compile and governed execution
pending

## Accepted target paths

- `/Game/Skyguard/Maps/Campaign_v1/Lvl_M08_RescueCover_Assembly_v1`
- `/Game/Skyguard/Maps/Campaign_v1/Lvl_M09_SaturationAttack_Assembly_v1`
- `/Game/Skyguard/Maps/Campaign_v1/Lvl_M10_EvacuationFinale_Assembly_v1`

These are distinct spatial/gameplay assemblies with proxy art. They are not
finished AAA maps.

## Mission identities

### M08 Rescue Cover

- island/coastal rescue route from the governed Mission 8 DataAsset;
- rescue-helicopter proxy at the hoist orbit;
- three survivor-raft proxies and one rescue-vessel proxy;
- rescue cove, pier and navigation/radar landmarks;
- protected rescue-flight and Lifeline Hunter objective anchors;
- heavy-drone proxy marking the governed boss placement.

### M09 Saturation Attack

- metropolitan defense route and dense skyline family;
- three differently scaled tower proxies and a wider urban block field;
- coastal power-station proxy compound;
- major bridge proxy crossing;
- three rooftop swarm-relay proxies;
- protected infrastructure and Iron Rain objective anchors;
- heavy-drone proxy marking the governed boss placement.

### M10 Evacuation Finale

- dawn harbor/evacuation route;
- ferry-terminal proxy complex and two piers;
- large evacuation-ship proxy;
- buses and ambulance-labeled vehicle proxies at the civilian convoy hub;
- departure breakwater and crane skyline;
- protected evacuation hub and Last Flight objective anchors;
- heavy-drone proxy marking the governed boss placement.

## Differentiation and governance

Each map persists:

- its exact four-point DataAsset route;
- its mission weather profile id;
- two required-objective anchors;
- four unique landmark ids and at least three mission-exclusive landmarks;
- a different skyline family;
- a different objective-placement and proxy-layout signature;
- a saved Mission DataAsset reference back to its governed map.

The builder owns only actors prefixed `P7W3_M08_`, `P7W3_M09_`, or
`P7W3_M10_`. Re-running it removes and deterministically replaces those actors
without touching another wave's map content.

## Gate

After the shared Unreal lane is released:

```powershell
& D:\Skyguard52\Scripts\run_skyguard_phase7_wave3_mission_map_gate.ps1
```

The supervisor performs one editor build, idempotent composition, a
fresh-process persistence/differentiation audit, and the generic native
campaign-map assembly automation. Attempts and hashed logs are immutable.
Packaging is not performed.

## Honest limitations

- Rescue helicopter, rafts, rescue vessel, towers, power station, bridge,
  ferry terminal, evacuation ship, civilian vehicles and all three bosses use
  existing proxy meshes or scaled reusable kit pieces.
- The helicopter has no rotor/hoist animation; survivors and rafts have no
  skeletal or water interaction.
- The bridge, terminal, power station and metropolitan skyline are spatial
  silhouettes rather than final modular environment art.
- `AmbulanceProxy` labels currently reuse the city-car proxy.
- Distinct mission boss classes, weak points and encounter behavior do not yet
  exist for Lifeline Hunter, Iron Rain or Last Flight.
- Environment lighting actors are foundational only; no final weather,
  volumetrics, water, cinematics, audio, streaming, collision, navigation, GPU
  quality or packaged playability claim is made.
