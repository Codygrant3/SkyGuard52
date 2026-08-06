# BLD-M01-YAK-UPLIFT-003-R3 Runbook

## Purpose

R3 is an immutable Blender 5.2 compatibility repair derived from R2.

The serialized R2 attempt opened and saved its isolated L88 blend, then stopped
at render setup because installed Blender 5.2 exposes `BLENDER_EEVEE`, not
`BLENDER_EEVEE_NEXT`.

R3 changes only that verified compatibility boundary:

```text
R2: scene.render.engine = "BLENDER_EEVEE_NEXT"
R3: scene.render.engine = "BLENDER_EEVEE"
```

Required version rebinding creates new R3 build IDs, Blender object names,
output paths, manifest path, comparison paths, and attempt namespace. The
component strategy, geometry construction, camera and clearance definitions,
donor selection, comparison cameras, and 232+8 accounting remain unchanged.

## Immutable prior evidence

Do not edit, delete, rename, or overwrite:

- `Saved/BuildAttempts/BLD_M01_YAK_UPLIFT_003_R2/attempt_01`
- `Content/Skyguard/Meshes/Source/Mission01/Yak52_Uplift_003_R2`
- any R1 or original Uplift 003 source or attempt evidence

The R3 contract hash-binds the R2 generator, contract, ledger, source audit,
attempt stdout/stderr/terminal record, and isolated partial blend.

## Preserved component accounting

R3 retains:

`232 exact required L88 objects + 8 source_absent_hold exceptions = 240 governed components`

The eight absent underscore-spelled canopy hinge/seal names:

- are explicitly classified `source_absent_hold`;
- count toward the 240 governed total;
- are not required as Blender objects;
- cannot be synthesized, renamed, aliased, or promoted;
- do not silently resolve to the actual dotted source names.

## Source gate

Run:

```powershell
Set-Location 'D:\Skyguard52'
python .\Scripts\verify_bld_m01_yak_uplift_003_r3.py
python -m unittest Scripts.tests.test_bld_m01_yak_uplift_003_r3 -v
```

Expected:

- `PASS`
- 240 governed components
- 232 exact object requirements
- 8 `source_absent_hold` exceptions
- five matched comparison slots
- all sixteen tests passing
- explicit regression coverage rejecting `BLENDER_EEVEE_NEXT`

Do not launch Blender if this gate fails.

## Exact serialized Blender command

After the source gate passes:

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' `
  --background `
  --factory-startup `
  --python 'D:\Skyguard52\Scripts\blender_bld_m01_yak_uplift_003_r3.py'
```

This source-only repair task does not execute that command.

## R3-only outputs

The generator may create only:

- `Content/Skyguard/Meshes/Source/Mission01/Yak52_Uplift_003_R3/BLD_M01_YAK_UPLIFT_003_R3_MASTER.blend`
- `Content/Skyguard/Meshes/Source/Mission01/Yak52_Uplift_003_R3/bld_m01_yak_uplift_003_r3.glb`
- `Saved/Reports/BLD_M01_YAK_UPLIFT_003_R3_MANIFEST.json`
- `Saved/Screenshots/BLD_M01_YAK_UPLIFT_003_R3/UPLIFT003R3_Beauty.png`
- `Saved/Screenshots/BLD_M01_YAK_UPLIFT_003_R3/UPLIFT003R3_SideOrtho.png`
- `Saved/Screenshots/BLD_M01_YAK_UPLIFT_003_R3/UPLIFT003R3_TopOrtho.png`
- `Saved/Screenshots/BLD_M01_YAK_UPLIFT_003_R3/UPLIFT003R3_RearCockpit.png`
- `Saved/Screenshots/BLD_M01_YAK_UPLIFT_003_R3/UPLIFT003R3_RearGunnerEye.png`

The generator refuses to overwrite an existing R3 blend, GLB, manifest, or
non-empty R3 comparison directory.

## Artifact gate

After Blender exits:

```powershell
Set-Location 'D:\Skyguard52'
python .\Scripts\verify_bld_m01_yak_uplift_003_r3.py --artifacts
```

The gate rejects:

- drift in any immutable R1/R2/L88 source or attempt evidence;
- R1/R2 output overlap;
- incomplete 232+8 component accounting;
- synthesized or promoted source-absent names;
- missing inherited objects, donors, camera, or safety/clearance volumes;
- missing or hash-drifted blend, GLB, or matched comparison;
- final, AAA, visual-review, or Unreal-acceptance claims.

## Visual disposition

After a passing artifact gate, compare the five R3 images to their hash-bound
L88 baselines and record one:

- `REJECTED`
- `REVISE_IN_NEW_VERSIONED_NAMESPACE`
- `ACCEPTED_FOR_UNREAL_IMPORT_EVALUATION`

The last disposition authorizes only later Unreal import evaluation. It does
not promote a component and is not final or AAA acceptance.
