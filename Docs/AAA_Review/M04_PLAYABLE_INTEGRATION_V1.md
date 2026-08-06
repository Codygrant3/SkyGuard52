# Skyguard 52 — Mission 4 Playable Integration v1

The accepted `Lvl_M04_NightBlackout_Assembly_v1` remains intact. The builder
creates the separate `Lvl_M04_NightBlackout_Playable_v1` candidate.

The native scaffold preserves the governed Night Blackout contract:

- three waves containing 2, 3 and 4 threats;
- one protected emergency substation with explicit integrity and terminal
  failure;
- three reacquisition-based searchlight passes, each requiring three
  uninterrupted seconds on Black Kite;
- missed searchlight windows damage the substation rather than silently
  advancing the encounter;
- two physical searchlight components and rear-cockpit audio/radio setup;
- four physical boss weak points: port navigation vane, starboard navigation
  vane, jammer and power bus;
- rifle fire strips both illuminated vanes and the exposed jammer;
- jammer destruction creates the governed Igla lock on the power bus;
- an orbit command can arm the bounded rifle contingency if the Igla path is
  unavailable;
- pilot commands propagate to the Yak-52;
- boss destruction is limited to three preallocated pieces.

The mission completes only after all three searchlight passes, all three
governed waves, Black Kite defeat and survival of the emergency substation.

Run the serialized gate only while Unreal is idle:

```powershell
powershell -ExecutionPolicy Bypass -File `
  D:\Skyguard52\Scripts\run_skyguard_m04_playable_integration_gate.ps1
```

The blackout skyline, searchlight batteries and Black Kite body remain proxy
art. Native tests do not prove player input, rendered darkness, audio
localization, performance, or packaged playability.
