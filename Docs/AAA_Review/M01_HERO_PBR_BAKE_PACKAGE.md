# Mission 01 Hero PBR Bake Package

Status: **Blender texture gate PASS; Unreal material and visual validation remain.**

## Scope

The package bakes the refined Mission 01 Pathfinder, lighthouse and radar-post
assets into Unreal-oriented 1024 x 1024 texture sets:

- BaseColor — sRGB RGBA.
- Normal — tangent-space, non-color.
- ORM — non-color; red AO, green roughness, blue metallic.
- MaterialID — non-color, discrete material-slot colors.

All textures are generated from the actual v2 Blender source object, its UV
islands, assigned material slots and procedural source shading.

## Provenance

- Source master:
  `D:\Skyguard52\Content\Skyguard\Meshes\Source\Mission01\Wave1_Refinement\M01_WAVE1_AAA_REFINEMENT_MASTER.blend`
- Source GLB:
  `D:\Skyguard52\Content\Skyguard\Meshes\Source\Mission01\Wave1_Refinement\m01_wave1_aaa_refinement.glb`
- Bake script:
  `D:\Skyguard52\Scripts\blender_m01_hero_pbr_bake.py`
- Texture root:
  `D:\Skyguard52\Content\Skyguard\Textures\Source\Mission01\HeroPBR_v1`
- Manifest:
  `D:\Skyguard52\Saved\Reports\M01_HERO_PBR_BAKE_MANIFEST.json`
- Gate report:
  `D:\Skyguard52\Saved\Reports\M01_HERO_PBR_BAKE_REPORT.json`

The manifest records hashes for both source files and every produced texture.

## Verified evidence

- Hero assets baked: 3.
- Texture maps produced: 12.
- Resolution: 1024 x 1024 RGBA for every map.
- Missing files: 0.
- Empty/invariant maps: 0.
- Every map has measurable RGB channel variation.
- Consecutive identical-source runs produced 12/12 identical texture hashes.
- Package fingerprint:
  `3950bc25a3fb6fa0b1827b0b94a129292141289313f754f3b78f6b6ccbf63687`.

## Normal-map claim

This is a same-mesh tangent-space normal bake that preserves the refined
geometry's authored normals and procedural shader bump. It is **not** claimed
as a high-to-low sculpt bake. The current asset set has no defensible separate
high-poly sculpt and production low-poly pair, so claiming a high-to-low bake
would be false.

The baked normal maps use Blender/OpenGL green-channel convention. In Unreal,
enable **Flip Green Channel** on import or apply the equivalent channel
conversion in the import pipeline.

## Unreal handoff

1. Import each hero folder into a separate Mission 01 texture namespace.
2. Mark BaseColor as sRGB.
3. Disable sRGB for Normal, ORM and MaterialID.
4. Set Normal compression to Normalmap and flip its green channel.
5. Use ORM R/G/B as AO/Roughness/Metallic.
6. Bind MaterialID only through the approved hero master-material layering.
7. Validate mip behavior, UV seams and material response under daylight,
   overcast, night, wet and storm lighting.
8. Profile texture residency before increasing any hero to 2K or 4K.

## Promotion boundary

This is an Unreal-ready texture candidate, not final AAA acceptance. Promotion
requires in-engine shader binding, seam review, lighting review and memory/GPU
profiling.
