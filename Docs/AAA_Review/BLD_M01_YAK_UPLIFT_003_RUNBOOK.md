# BLD-M01-YAK-UPLIFT-003 Runbook

## Purpose and decision

Uplift 003 preserves the richer L88 Yak-52 scene and selectively stages the
strongest construction work from Production 002. It is not a wholesale
replacement and it is not an AAA, final, production, or Unreal-accepted asset.

The governing visual review rejected Production 002 as a full L88 replacement.
Its cowl, propeller, wheel-well construction and pivot metadata remain useful,
but its sparse cockpit, missing crew and weapons, generic proportions, and
occluded rear-gunner-eye render would regress the playable aircraft.

Uplift 003 therefore:

1. Byte-copies the original L88 `.blend` into an isolated namespace.
2. Opens only the isolated copy.
3. Fixes the rear-gunner-eye camera and creates explicit camera, pilot-safety,
   rifle-muzzle, and Igla-backblast clearance volumes before geometry work.
4. Classifies and tags every one of the 240 governed L88 components.
5. Preserves L88 cockpit, pilot, rear gunner, rifle, and Igla content.
6. Stages only the 002 cowl, propeller, wheel wells, canopy-travel datum, and
   gear-pivot datums as separately named, non-promotable donors.
7. Emits five matched L88-versus-uplift comparison views.

The original L88, Production 001, and Production 002 namespaces are immutable.

## Source gate

Run this before Blender:

```powershell
Set-Location 'D:\Skyguard52'
python .\Scripts\verify_bld_m01_yak_uplift_003.py
python -m unittest Scripts.tests.test_bld_m01_yak_uplift_003 -v
```

Expected source result:

- `PASS`
- 240 governed components
- 163 `provisional_inherited`
- 26 `rebuild_candidate`
- 6 `donor_from_002`
- 45 `hold`
- five matched comparison slots
- thirteen negative/positive verifier tests passing

Do not continue if the source gate fails.

## Exact governed Blender command

Close any interactive Blender session using these assets. Run exactly:

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' `
  --background `
  --factory-startup `
  --python 'D:\Skyguard52\Scripts\blender_bld_m01_yak_uplift_003.py'
```

The generator refuses to overwrite any existing Uplift 003 blend, GLB,
manifest, or non-empty comparison directory. If an earlier attempt emitted
partial artifacts, preserve them as attempt evidence and investigate rather
than deleting or overwriting them.

The command is intentionally not executed by the source-only build task.

## Governed outputs

- `Content/Skyguard/Meshes/Source/Mission01/Yak52_Uplift_003/BLD_M01_YAK_UPLIFT_003_MASTER.blend`
- `Content/Skyguard/Meshes/Source/Mission01/Yak52_Uplift_003/bld_m01_yak_uplift_003.glb`
- `Saved/Reports/BLD_M01_YAK_UPLIFT_003_MANIFEST.json`
- `Saved/Screenshots/BLD_M01_YAK_UPLIFT_003/UPLIFT003_Beauty.png`
- `Saved/Screenshots/BLD_M01_YAK_UPLIFT_003/UPLIFT003_SideOrtho.png`
- `Saved/Screenshots/BLD_M01_YAK_UPLIFT_003/UPLIFT003_TopOrtho.png`
- `Saved/Screenshots/BLD_M01_YAK_UPLIFT_003/UPLIFT003_RearCockpit.png`
- `Saved/Screenshots/BLD_M01_YAK_UPLIFT_003/UPLIFT003_RearGunnerEye.png`

## Artifact gate

After the Blender process exits successfully, run:

```powershell
Set-Location 'D:\Skyguard52'
python .\Scripts\verify_bld_m01_yak_uplift_003.py --artifacts
```

The artifact gate rejects:

- a changed original L88 source hash;
- output outside the isolated Uplift 003 namespace;
- missing or hash-drifted blend/GLB;
- incomplete 240-component classification;
- any inherited or donor component with promotion enabled;
- missing rear-gunner camera or clearance/safety volume;
- missing selective donor;
- missing or unmatched comparison slot;
- a final, AAA, production, Unreal, or visual-review acceptance claim.

## Required visual review

The artifact verifier proves lineage and completeness, not visual quality.
Review all five candidate images next to their contract-bound L88 baselines.

The reviewer must explicitly answer:

1. Is the rear-gunner-eye view unobstructed and usable without clipping?
2. Are the pilot safety, rifle sweep, and Igla backblast concepts credible?
3. Does the L88 cockpit, crew, rifle, and Igla richness remain visible?
4. Do the donor cowl and propeller improve silhouette and construction without
   creating a coordinate or scale mismatch?
5. Do the wheel-well donors improve the underside without adopting the
   inaccurate Production 002 landing-gear stance?
6. Do side and top views show any regression in Yak-52 proportions?
7. Does the beauty view improve the aircraft rather than merely changing it?

Record one of these dispositions:

- `REJECTED`
- `REVISE_IN_ISOLATED_UPLIFT_004`
- `ACCEPTED_FOR_UNREAL_IMPORT_EVALUATION`

Acceptance for Unreal import evaluation is still not final or AAA acceptance.
Never silently promote component classes. Any approved component promotion must
be explicit, reviewer-attributed, and recorded in a later immutable contract.

## Recovery rules

- Never open or save over the original L88 blend.
- Never overwrite Uplift 003 outputs.
- Never import or append Production 001/002 blend or GLB files.
- Never discard L88 cockpit, crew, rifle, or Igla work to make a donor fit.
- If the camera remains occluded, stop geometry replacement and correct the
  camera/clearance stage in a new isolated uplift attempt.
- If Blender exits without the manifest and all five comparisons, the artifact
  run is incomplete even if the process exit code was zero.
