# Skyguard 52 — Mission 5 Playable Integration v1

The accepted `Lvl_M05_StormFront_Assembly_v1` remains intact. The builder
creates the separate `Lvl_M05_StormFront_Playable_v1` candidate.

The native scaffold preserves the governed Storm Front contract while making
the weather mechanically relevant:

- three waves containing 2, 3 and 4 threats;
- independently damageable offshore-platform and distressed-trawler targets;
- loss of either protected target fails `ProtectOffshoreCrew`;
- bounded lightning windows expose Tempest's two static-discharge booms;
- turbulence from zero to one directly slows Igla-lock stabilization;
- rifle fire removes both booms and jams the exposed control servo;
- `Extend` is required to stabilize the governed Igla lock on the engine
  intake;
- `Break` can arm a bounded rifle contingency if the Igla route is
  unavailable;
- pilot commands propagate to the Yak-52;
- boss destruction is limited to three preallocated panel pieces.

The mission completes only after the three governed waves, both boom
objectives, Tempest defeat, and survival of both protected offshore targets.

Run the serialized gate only while Unreal is idle:

```powershell
powershell -ExecutionPolicy Bypass -File `
  D:\Skyguard52\Scripts\run_skyguard_m05_playable_integration_gate.ps1
```

The storm environment, offshore platform, trawler and Tempest body remain
proxy art. Native tests do not prove player input, rendered lightning,
turbulence feel, audio mix, performance, or packaged playability.
