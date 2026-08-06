# Skyguard 52 — Mission 8 Playable Integration v1

The accepted `Lvl_M08_RescueCover_Assembly_v1` remains intact. The builder
creates the separate `Lvl_M08_RescueCover_Playable_v1` candidate.

Mission 8 is structured around rescue cover rather than another straight
intercept:

- a four-point coastal rescue orbit separates the sortie from prior routes;
- animated runtime anchors represent the rescue helicopter, oscillating
  hoist, survivors, rafts, and moving rescue vessel;
- three escalating waves contain two, three, and four threats;
- three successful cover windows are required to complete the hoist
  objective;
- the helicopter, survivors/rafts, and rescue vessel are protected
  independently, and loss of any one explicitly fails the mission;
- weapon release is rejected inside the friendly corridor or below the
  configured safe-separation distance;
- Lifeline Hunter exposes its primary tracker on a left orbit and its
  secondary servo on a right orbit;
- the rifle defeats the optical tracker, weapon servo, and countermeasure pod;
- after an `Extend` command and safe separation, the Igla can disable the
  engine;
- `Break` provides a safe rifle fallback and is also required to redirect the
  disabled drone away from survivors;
- destroying the engine alone is not victory—the redirected crash is a
  mandatory safety condition;
- boss destruction is limited to three preallocated pieces;
- mission success requires all hoists, all protected groups, all required
  objectives, and the safe boss redirect.

Run the serialized gate only while Unreal is idle:

```powershell
powershell -ExecutionPolicy Bypass -File `
  D:\Skyguard52\Scripts\run_skyguard_m08_playable_integration_gate.ps1
```

The rescue aircraft, hoist, people, rafts, vessel, and Lifeline Hunter remain
proxy presentation. Native tests do not prove rendered animation, input,
performance, audio mix, packaging, or final playability.
