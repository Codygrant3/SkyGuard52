# BLD-M01-YAK-PROD-001 Runbook

Purpose: author a new production-direction Yak-52 exterior and rear-cockpit
master without promoting or copying L88 geometry.

## Current state

The generator, contract, verifier, and tests are source-only. Blender has not
been launched and the `.blend`, `.glb`, and artifact manifest do not exist until
the root build supervisor deliberately runs the serialized Blender step.

## Authority and isolation

- Blender authority: 5.2 only.
- Coordinate system: metres, `+X` forward, `+Y` right, `+Z` up.
- L88 use: hash-bound coordinate/datum lineage only.
- L88 geometry import, link, append, datablock copy, material reuse, or topology
  promotion is forbidden.
- The generator resets to a clean factory scene.
- Outputs use a new `Yak52_Production` source directory and never overwrite L88.
- This source build is a candidate. It cannot claim Unreal, rendered, packaged,
  performance, or final AAA acceptance.

## Files

- Contract:
  `Docs/AAA_Review/BLD_M01_YAK_PROD_001_CONTRACT.json`
- Blender generator:
  `Scripts/blender_bld_m01_yak_prod_001.py`
- Offline verifier:
  `Scripts/verify_bld_m01_yak_prod_001.py`
- Tests:
  `Scripts/tests/test_bld_m01_yak_prod_001.py`

Later Blender outputs:

- `Content/Skyguard/Meshes/Source/Mission01/Yak52_Production/BLD_M01_YAK_PROD_001_MASTER.blend`
- `Content/Skyguard/Meshes/Source/Mission01/Yak52_Production/bld_m01_yak_prod_001.glb`
- `Saved/Reports/BLD_M01_YAK_PROD_001_MANIFEST.json`

## Safe preflight

Run the offline checks before starting Blender:

```powershell
Set-Location D:\Skyguard52
py -3 Scripts\verify_bld_m01_yak_prod_001.py
py -3 -m unittest Scripts.tests.test_bld_m01_yak_prod_001
```

Expected source-only result:

- verifier `gate=PASS`;
- `artifact_gate=NOT_RUN`;
- all tests pass.

This proves source syntax/contract structure and import isolation. It does not
prove that Blender can execute the generator.

## Serialized Blender execution

Only the root supervisor may run this after confirming no Unreal, UAT,
ShaderCompileWorker, packaging, Blender, or other heavyweight process owns the
workstation.

Use an attempt-specific directory with direct stdout/stderr, PID tracking, a
hard deadline, and bounded cleanup of only that process tree. The intended
command shape is:

```powershell
& '<BLENDER_5_2_EXE>' `
  --background `
  --factory-startup `
  --python D:\Skyguard52\Scripts\blender_bld_m01_yak_prod_001.py
```

Do not substitute another Blender version. Do not open the L88 `.blend`.

## Artifact verification

After Blender exits successfully:

```powershell
py -3 Scripts\verify_bld_m01_yak_prod_001.py `
  --artifact-manifest Saved\Reports\BLD_M01_YAK_PROD_001_MANIFEST.json
```

The artifact verifier rejects:

- wrong Blender version;
- L88 reference drift;
- missing or tampered `.blend`/GLB;
- missing separated aircraft, propeller, canopy, cockpit, or control surfaces;
- missing named sockets/datums;
- absent `UV0` or material slots;
- insufficient governed topology thresholds;
- names containing `blockout`, `proxy`, `placeholder`, `temp`, `default`,
  or `cube`;
- real-world dimension drift beyond contract tolerances;
- a false final-production claim.

## Manual source review before Unreal

Even with verifier `PASS`, stop before Unreal import until a reviewer confirms:

1. Yak-52 silhouette and dimensions against the reference board.
2. Smooth shading and production-direction topology with no obvious primitive
   intersections at first-person or exterior hero distance.
3. Correct hinge pivots for ailerons, elevators, rudder, controls, propeller,
   and sliding rear canopy.
4. Rear-cockpit clearances and canopy travel.
5. Pilot, rear-gunner, ADS-eye, rifle, and Igla socket positions.
6. Material separation, UV density, bake route, glass thickness, and scale.
7. No blockout topology or legacy web asset in the saved source.

Only after this manual source gate should root schedule a separate Unreal import
and visible/performance acceptance task.
