# Skyguard 52 — Mission 10 Playable Integration v1

The accepted `Lvl_M10_EvacuationFinale_Assembly_v1` remains intact. The
builder creates the separate `Lvl_M10_EvacuationFinale_Playable_v1`
candidate.

## Finale route and protected evacuation

Mission 10 combines established systems without copying a prior mission
layout:

- wave one follows the moving highway convoy with three threats;
- wave two shifts four threats to the ferry terminal;
- wave three covers the departing evacuation ship against five threats;
- the convoy group includes two bus and two ambulance runtime anchors;
- convoy, ferry terminal, and evacuation ship integrity are tracked
  independently;
- loss of any protected group deterministically fails
  `ProtectEvacuationHub`;
- weapon release is rejected inside the civilian corridor or below the
  configured separation distance;
- the fourth evacuation-lane step is the safe diversion of the final wreck.

## Last Flight

Last Flight expands the governed four-milestone objective into ten physical
mechanisms:

1. left and right orbit passes expose two guidance arrays;
2. rifle fire opens both armored strike-bay mechanisms and their cooling
   systems;
3. an `Extend` command and safe separation permit the first Igla engine hit;
4. a climb pass exposes the jammer;
5. after jammer destruction, another `Extend` permits the second engine hit;
6. pursuit exposes the command core to rifle fire;
7. command-core destruction starts a disabled descent but does not award
   victory;
8. `Break` diverts the wreck away from civilians and completes the boss.

The governed DataAsset's four boss points remain the acceptance boundary.
Runtime objective progress is emitted only at four deterministic milestones,
not once per physical component. Breakup is limited to six pre-authored
pieces.

Run the serialized gate only while Unreal is idle:

```powershell
powershell -ExecutionPolicy Bypass -File `
  D:\Skyguard52\Scripts\run_skyguard_m10_playable_integration_gate.ps1
```

The buses, ambulances, terminal, ship, civilians, and Last Flight remain
proxy presentation. Native tests do not prove rendered animation, player
input, performance, audio mix, packaging, or final playability.
