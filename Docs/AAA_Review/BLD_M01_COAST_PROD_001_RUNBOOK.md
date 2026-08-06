# BLD-M01-COAST-PROD-001 Source-Only Runbook

## Current state

This package is a source-only production-direction candidate. Blender and Unreal
have not been launched for this build ID. No artifact, visual-fidelity, gameplay,
performance, or AAA claim is made.

The Wave1 screenshot is hash-bound rejection evidence only. It must never be
loaded as geometry, traced, sampled for materials, or used as image-to-mesh input.
All generated geometry starts from Blender factory state and is written to the
isolated `Coastal_Production_001` namespace.

## Offline preflight

From `D:\Skyguard52`:

```powershell
python .\Scripts\verify_bld_m01_coast_prod_001.py
python -m unittest .\Scripts\test_bld_m01_coast_prod_001.py
python -m py_compile .\Scripts\blender_bld_m01_coast_prod_001.py .\Scripts\verify_bld_m01_coast_prod_001.py .\Scripts\test_bld_m01_coast_prod_001.py
```

The source gate must report `PASS`. `artifact_status: NOT_RUN` is expected until
the serialized Blender job completes.

## Exact serialized Blender command

Run this only after the shared heavy-process lane is confirmed free:

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --factory-startup --python 'D:\Skyguard52\Scripts\blender_bld_m01_coast_prod_001.py'
```

Do not run this concurrently with Unreal, another Blender generator, shader
compilation, asset import, or cooking.

## Artifact gate

After Blender exits successfully:

```powershell
python .\Scripts\verify_bld_m01_coast_prod_001.py --require-artifacts
```

The artifact gate validates the master `.blend`, 38 per-asset GLB exports,
hashes, exact dimensions, UV0/UV1 presence, snap/collision metadata, Nanite/LOD
intent, and isolated output paths.

## Mandatory manual and Unreal review

1. Inspect all four 100 m by 80 m terrain variants side by side and in repeated
   sequences. Reject exposed thin edges, vertical discontinuities, or 100 m seams.
2. Validate the full beach, dune, seawall, sidewalk, curb, drainage, crowned-road,
   and inland transition under grazing daylight.
3. Assemble straight, corner, and end midrise shells with roof, balcony, and
   window variants. Reject repetitive silhouettes, floating modules, bad pivots,
   or visible facade gaps.
4. Confirm UV0 real-world material scale and inspect UV1 overlap/padding in
   Blender and Unreal. Regenerate or repack any invalid lightmap charts.
5. Import into a quarantined Unreal test path. Validate centimeters, +X coast,
   +Y inland, +Z up, pivots, sockets, materials, collision, Nanite eligibility,
   fallback/LOD behavior, and streaming.
6. Perform collision, seam, route readability, memory, draw-call, and frame-time
   tests before promotion.

Only after these gates may the package advance beyond
`production_direction_candidate_not_aaa`. Existing Wave1 files are not modified
or replaced by this process.
