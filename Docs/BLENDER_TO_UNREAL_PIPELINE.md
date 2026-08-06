# Blender to Unreal pipeline

The current AAA track is `D:\Skyguard52`. The legacy browser game is not an
input to this pipeline.

## Current asset status

The L88 Yak-52 Blender source exports to:

`Content/Skyguard/Meshes/Source/L88/yak52_l88_silhouette_blockout.glb`

Unreal imports the GLB into `/Game/Skyguard/Meshes/L88` and assembles the
imported static meshes in:

`/Game/Skyguard/Maps/Lvl_Yak52_L88_Validation_v2`

This proves the Blender models can be imported and used in Unreal. The L88
aircraft remains a validation blockout, not accepted final AAA hero art.

## Commands

Run from PowerShell:

```powershell
# Read-only validation of the current source and Unreal receipt
& "D:\Skyguard52\Scripts\run_l88_blender_unreal_pipeline.ps1" -Step Validate

# Rebuild the GLB and native .blend from the canonical Blender script
& "D:\Skyguard52\Scripts\run_l88_blender_unreal_pipeline.ps1" -Step Export

# Import/reimport the GLB and rebuild the isolated validation map
& "D:\Skyguard52\Scripts\run_l88_blender_unreal_pipeline.ps1" -Step Import

# Regenerate the Unreal import audit
& "D:\Skyguard52\Scripts\run_l88_blender_unreal_pipeline.ps1" -Step Audit

# Run export, import, audit, and final receipt validation
& "D:\Skyguard52\Scripts\run_l88_blender_unreal_pipeline.ps1" -Step All
```

The current pass22 contract intentionally contains 80 more meshes than the
pass16 baseline (20 from Pass20, 39 from Pass21, and a net 21 from Pass22).
`ExpectedMeshDelta` defaults to 80 and the auditor requires Blender and Unreal
to agree at 240/240. Future intentional count changes must
update this explicit value; unexpected additions or missing assets fail.

Close the interactive Unreal Editor before Import, Audit, or All. This avoids
two processes writing the same asset packages.

Audit and All also regenerate
`Saved/Reports/L88_IMPORT_DELTA_CURRENT.json`, which verifies that mesh counts,
dimensions, UV coverage, socket markers, forbidden labels, and the current GLB
hash still match the Unreal import.

## Promotion requirements

Before a Blender model replaces production gameplay art:

1. Preserve the native `.blend`, exported GLB, source/license evidence, and
   SHA-256.
2. Apply transforms, correct normals, stable semantic names, Unreal axes, and
   meter-to-centimeter scale.
3. Author semantic material slots, PBR textures, UVs, LODs/Nanite policy, and
   simple collision.
4. Preserve required sockets such as `SO_PropAxis`, `SO_RearEye`,
   `SO_ADSEye`, and `SO_RearWeaponMount`.
5. Pass the isolated import map, interaction, performance, and harsh visual
   gates before production promotion.
