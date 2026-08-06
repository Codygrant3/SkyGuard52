# Mission 01 Wave 1 Blender Refinement

Status: **Blender candidate gate PASS; Unreal visual/performance acceptance still required.**

## What this candidate adds

- Sculpted beach surface, detailed seawall, promenade and road-transition modules.
- Four Ukrainian coastal residential/midrise modules with recessed window banks,
  balconies, parapets, roof plant and an authored damage variant.
- Compound lighthouse with tapered tower, gallery, railing, lantern and roof.
- Compound radar post with bunker, blast door, mast structure, turntable, dish
  frame, feed arm and receiver.
- Mechanically readable Pathfinder airframe with panel seams, service hatch,
  exhausts, elevons, canted tails and leading-edge structure.
- Four independently named gameplay weak points:
  Command Antenna, Nose Camera, Engine and Control Linkage.
- Four bounded breakup pieces. Runtime fracture is explicitly out of contract.

## Generated artifacts

- Native source:
  `D:\Skyguard52\Content\Skyguard\Meshes\Source\Mission01\Wave1_Refinement\M01_WAVE1_AAA_REFINEMENT_MASTER.blend`
- Unreal-importable GLB:
  `D:\Skyguard52\Content\Skyguard\Meshes\Source\Mission01\Wave1_Refinement\m01_wave1_aaa_refinement.glb`
- Manifest:
  `D:\Skyguard52\Saved\Reports\M01_WAVE1_AAA_REFINEMENT_MANIFEST.json`
- Blender gate:
  `D:\Skyguard52\Saved\Reports\M01_WAVE1_AAA_REFINEMENT_REPORT.json`
- GLB round-trip gate:
  `D:\Skyguard52\Saved\Reports\M01_WAVE1_AAA_REFINEMENT_ROUNDTRIP_AUDIT.json`
- Proof renders:
  `D:\Skyguard52\Saved\Screenshots\Mission01_Wave1_Refinement`

## Verified evidence

- Blender asset gate: PASS.
- GLB round-trip gate: PASS.
- Exported assets: 20.
- Imported assets after round trip: 20.
- Missing or unexpected asset names: 0.
- UV omissions: 0.
- Invalid local transforms: 0.
- Geometry: 23,777 vertices / 45,844 triangles.
- GLB size: 3,159,664 bytes.
- SHA-256:
  `d12c4509f7234a3fc6fe16917db431a6b5146a6ddcd34264e7885a82c6284a99`.

## Unreal handoff

1. Import into a Mission 01 refinement folder without replacing the original
   Wave 1 blockout.
2. Bind stable semantic mesh names from the manifest.
3. Generate or assign collision from each `SKG_CollisionContract`.
4. Enable Nanite only where `SKG_NaniteCandidate` is true.
5. Replace or bake Blender procedural microdetail into Unreal master materials.
6. Exercise the Pathfinder sequence:
   rifle antenna/camera, Igla engine, rifle linkage.
7. Profile the intact/damaged swap and four-piece debris pool. Do not enable
   runtime fracture.

## Remaining limitations

- Procedural Blender microdetail is an art-direction source, not the final
  authored Unreal texture set.
- UCX collision must still be generated and validated in Unreal.
- This candidate is production-ready geometry direction, not final AAA
  photogrammetry or material acceptance.
