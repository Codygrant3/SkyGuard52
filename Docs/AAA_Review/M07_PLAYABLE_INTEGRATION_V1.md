# Skyguard 52 — Mission 7 Playable Integration v1

The accepted `Lvl_M07_SearchIntercept_Assembly_v1` remains intact. The builder
creates the separate `Lvl_M07_SearchIntercept_Playable_v1` candidate.

This mission is deliberately structured around search and identification
before weapons release:

- the route retains four separated island points, radar and lighthouse
  references, and three fishing vessels as identification traffic;
- three false contacts must be classified across two search sectors;
- Radar Ghost cannot be confirmed until the player observes exhaust
  distortion, a physical shadow and engine sound;
- waves cannot begin before hostile identification;
- the island navigation station and fishing fleet have independent integrity,
  and loss of either fails `ProtectRadarChain`;
- after the third wave, a bounded reinforcement timer pressures the player to
  finish the command drone before the radar station is disabled;
- the governed weak-point chain remains signature modulator, radar receiver,
  cooling door and engine;
- left orbit exposes the signature modulator and right orbit exposes the radar
  receiver;
- rifle fire opens the cooling system, then a pursuit/rear-aspect command
  enables the Igla engine shot;
- `Break` supports a bounded rifle fallback;
- pilot commands propagate to the Yak-52;
- defeat destruction is limited to three preallocated pieces.

Run the serialized gate only while Unreal is idle:

```powershell
powershell -ExecutionPolicy Bypass -File `
  D:\Skyguard52\Scripts\run_skyguard_m07_playable_integration_gate.ps1
```

The islands, radar installation, fishing fleet and Radar Ghost remain proxy
art. Native tests do not prove rendered identification cues, player input,
performance, audio mix, packaging, or final playability.
