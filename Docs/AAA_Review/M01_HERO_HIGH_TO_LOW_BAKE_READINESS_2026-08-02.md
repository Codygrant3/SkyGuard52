# Mission 01 Hero High-to-Low Bake Readiness — 2026-08-02

## Outcome

The previous Mission 01 hero bake remains valid as a deterministic
same-mesh texture candidate, but it is not reclassified. A new isolated build,
`BLD_M01_HERO_HILO_001`, now defines a real high-to-low path for Pathfinder,
lighthouse, and radar-post geometric detail.

Current state:

- source gate: `PASS`;
- Blender artifact gate: `NOT_RUN`;
- overall readiness gate: `PASS_WITH_GAPS`;
- P3.4: `INCOMPLETE`;
- promotion: candidate only.

No Blender or Unreal process was launched in this stability-safe authoring
pass.

## What is now governed

For every scoped hero, the contract requires:

1. the accepted Wave 1 object copied to a distinct low mesh datablock;
2. a separate high mesh with an applied bevel and asset-specific geometric
   detail;
3. a separate named cage inflated from the low target;
4. the existing `UV_M01_AAA_0` layer on the low target;
5. Cycles CPU projection with `selected_to_active=true`;
6. a named explicit cage, bounded extrusion, and bounded ray distance;
7. 2048x2048 tangent-space Normal and AO maps with 32-pixel padding;
8. minimum high/low vertex ratios and maximum bounds drift;
9. byte counts and SHA-256 for source, native master, low-only GLB, and every
   map;
10. an order-independent package fingerprint.

The three high sources use different geometric-detail recipes:

- Pathfinder: wing and service-hatch fasteners plus raised panel seams;
- lighthouse: tower seams, gallery fasteners, and access-panel fasteners;
- radar post: bunker, dish-mount, and mast-joint fasteners.

## Files

- Contract:
  `D:\Skyguard52\Docs\AAA_Review\M01_HERO_HIGH_TO_LOW_BAKE_CONTRACT.json`
- Generator:
  `D:\Skyguard52\Scripts\blender_m01_hero_high_to_low_bake.py`
- Offline/artifact verifier:
  `D:\Skyguard52\Scripts\verify_skyguard_m01_hero_high_to_low_bake.py`
- Manifest schema:
  `D:\Skyguard52\Scripts\skyguard_m01_hero_high_to_low_bake_v1.schema.json`
- Serialized supervisor:
  `D:\Skyguard52\Scripts\run_m01_hero_high_to_low_bake.ps1`
- Current readiness receipt:
  `D:\Skyguard52\Saved\Reports\M01_HERO_HIGH_TO_LOW_BAKE_READINESS.json`

## Safe commands

Offline validation only:

```powershell
Set-Location D:\Skyguard52
.\Scripts\run_m01_hero_high_to_low_bake.ps1 -ValidateOnly
```

The eventual serialized build, after the machine is stable and no other
Blender process is active:

```powershell
Set-Location D:\Skyguard52
.\Scripts\run_m01_hero_high_to_low_bake.ps1
```

The supervisor refuses overlapping Blender jobs, redirects stdout/stderr to a
unique attempt directory, allows up to 30 minutes, requires a zero Blender
exit code, then runs the artifact verifier with `--require-artifacts`.

## What still blocks P3.4

This source readiness does not prove:

- successful Blender execution;
- clean cage projection at tight concavities or grazing angles;
- acceptable skew, waviness, seam, or gradient behavior;
- correct Unreal green-channel handling;
- final master-material response under daylight, overcast, night, wet, and
  storm lighting;
- visible or human art acceptance.

After the serialized build passes, inspect each Normal and AO map plus the
mapped low mesh from front, rear, profile, top, and grazing-angle views. Only
then can the result move to Unreal import and multi-lighting review. P3.4
must remain incomplete until that evidence exists.
