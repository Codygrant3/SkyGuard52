# Skyguard 52 — Mission 6 Playable Integration v1

The accepted `Lvl_M06_AirfieldDefense_Assembly_v1` remains intact. The builder
creates `Lvl_M06_AirfieldDefense_Playable_v1`.

The native scaffold provides three independently damageable targets—runway,
hangars and parked aircraft—plus visible timed payload windows. At least two
targets must survive. Runway and hangar rack destruction cancels the matching
payload and advances `JamPayloadRacks`; the heat manifold can cancel the final
parked-aircraft run and exposes the engine. Runway Breaker supports the normal
Igla engine strike and an orbit-gated rifle fallback. Three governed waves use
2, 3 and 4 threats. Pilot commands propagate to the Yak-52 and destruction is
limited to three preallocated pieces.

Run the serialized gate only while Unreal is idle:

```powershell
powershell -ExecutionPolicy Bypass -File `
  D:\Skyguard52\Scripts\run_skyguard_m06_playable_integration_gate.ps1
```

The airfield, protected assets and payload-carrier body remain proxy art.
Native tests do not prove player input, rendered fidelity, audio mix,
performance or packaged playability.
