# BLD-M01-YAK-UPLIFT-003-R2 Runbook

## Why R2 exists

The first Uplift 003 Blender attempt opened its isolated L88 copy and then
stopped before donor construction. The runtime contract requested eight canopy
hinge/seal object names that do not exist with those exact spellings in the L88
Blender source.

The governed runtime names use underscores:

- `GEO_CanopyHinge_0_18_L`
- `GEO_CanopyHinge_0_18_R`
- `GEO_CanopyHinge_0_76_L`
- `GEO_CanopyHinge_0_76_R`
- `GEO_CanopySeal_0_18_L`
- `GEO_CanopySeal_0_18_R`
- `GEO_CanopySeal_0_76_L`
- `GEO_CanopySeal_0_76_R`

The immutable L88 source inventory instead contains the corresponding dotted
names, such as `GEO_CanopyHinge_0.18_L` and
`GEO_CanopySeal_0.76_R`.

R2 does not rename, alias, or synthesize the absent underscore names. Each is
explicitly classified as `source_absent_hold`, is not required as a Blender
object, cannot promote, and remains counted in the governed ledger:

`232 exact required objects + 8 source_absent_hold exceptions = 240 components`

The complete reconciliation evidence is in
`BLD_M01_YAK_UPLIFT_003_R2_SOURCE_AUDIT.json`.

## Preserved strategy

R2 retains the component-by-component uplift strategy:

- preserve the richer L88 cockpit, pilot, rear gunner, rifle, and Igla;
- correct the rear-gunner camera and stage explicit camera, pilot-safety,
  rifle-muzzle, and Igla-backblast volumes before donor geometry;
- use Production 002 only for selected cowl, propeller, wheel-well, and pivot
  construction;
- keep every inherited and donor component non-promotable;
- produce five matched comparison views against hash-bound L88 baselines;
- require separate visual and later Unreal import review.

R2 is not final, AAA, production, or Unreal accepted.

## Source-only validation

Run:

```powershell
Set-Location 'D:\Skyguard52'
python .\Scripts\verify_bld_m01_yak_uplift_003_r2.py
python -m unittest Scripts.tests.test_bld_m01_yak_uplift_003_r2 -v
```

Expected:

- source gate `PASS`;
- 240 governed components;
- 232 exact Blender-object requirements;
- 8 `source_absent_hold` exceptions;
- classification counts of 155 provisional inherited, 26 rebuild candidates,
  6 Production 002 donors, 45 held, and 8 source-absent held;
- five matched comparison slots;
- all R2 tests passing.

Do not run Blender if the source gate fails.

## Exact offline Blender command

Only after the source gate passes:

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' `
  --background `
  --factory-startup `
  --python 'D:\Skyguard52\Scripts\blender_bld_m01_yak_uplift_003_r2.py'
```

This source-only repair task does not execute that command.

## Immutable R2 outputs

The command may create only:

- `Content/Skyguard/Meshes/Source/Mission01/Yak52_Uplift_003_R2/BLD_M01_YAK_UPLIFT_003_R2_MASTER.blend`
- `Content/Skyguard/Meshes/Source/Mission01/Yak52_Uplift_003_R2/bld_m01_yak_uplift_003_r2.glb`
- `Saved/Reports/BLD_M01_YAK_UPLIFT_003_R2_MANIFEST.json`
- `Saved/Screenshots/BLD_M01_YAK_UPLIFT_003_R2/UPLIFT003R2_Beauty.png`
- `Saved/Screenshots/BLD_M01_YAK_UPLIFT_003_R2/UPLIFT003R2_SideOrtho.png`
- `Saved/Screenshots/BLD_M01_YAK_UPLIFT_003_R2/UPLIFT003R2_TopOrtho.png`
- `Saved/Screenshots/BLD_M01_YAK_UPLIFT_003_R2/UPLIFT003R2_RearCockpit.png`
- `Saved/Screenshots/BLD_M01_YAK_UPLIFT_003_R2/UPLIFT003R2_RearGunnerEye.png`

The generator refuses to overwrite existing R2 outputs. Preserve all original
Uplift 003 files and `attempt_01` logs as immutable failure evidence.

## Post-run artifact validation

After Blender exits:

```powershell
Set-Location 'D:\Skyguard52'
python .\Scripts\verify_bld_m01_yak_uplift_003_r2.py --artifacts
```

The artifact gate rejects:

- any changed immutable source or attempt evidence;
- any output outside the R2 namespace;
- anything other than 232 exact objects plus 8 exception records;
- an absent underscore canopy name synthesized as an object;
- an exception marked required, synthesized, or promotable;
- a missing inherited component, donor, safety volume, or corrected camera;
- a missing or hash-drifted blend, GLB, or comparison image;
- a missing matched comparison slot;
- a final, AAA, production, visual-acceptance, or Unreal-acceptance claim.

## Visual disposition

After a passing artifact gate, compare all five R2 images with their L88
baselines and record exactly one:

- `REJECTED`
- `REVISE_IN_NEW_VERSIONED_NAMESPACE`
- `ACCEPTED_FOR_UNREAL_IMPORT_EVALUATION`

The last disposition authorizes only a later Unreal import evaluation. It does
not promote any component and does not constitute final or AAA acceptance.
