# Skyguard 52 Project Instructions

## Canonical project

- Work only in `D:\Skyguard52`.
- This is the Unreal Engine 5.8 and Blender 5.2 AAA project.
- The retired Three.js project under `Shoot down the drones` is not a source,
  asset, build, or deployment authority.
- Read `D:\Skyguard52\Production\production_manifest.json` before planning or
  changing production work.

## Production workflow

- Use `D:\Skyguard52\Scripts\skyguard_production.py` for queue state,
  preflight, attempts, evidence, and acceptance.
- Run at most one heavy Blender, Unreal, shader compiler, compiler, build, or
  packaging process at a time.
- Do not start a second attempt while a first attempt is active.
- Do not automatically retry a failed asset. Preserve the failed attempt and
  continue with an independent queue item or make one bounded correction.
- Existing `Docs\AAA_Review`, `Saved\Reports`, and `Saved\BuildAttempts`
  artifacts are historical evidence. Do not rewrite or delete them.

## Evidence rules

- Do not create circular hashes or hash mutable files into one another.
- Attempt receipts may hash immutable inputs and produced outputs.
- A release snapshot may hash the finalized manifest; the mutable manifest
  must never contain its own hash.
- One attempt gets one directory, one terminal receipt, and one artifact
  inventory. Do not create a new prompt/freeze package for every normal step.
- States are explicit: `queued`, `blocked_reference`, `source_candidate`,
  `provisional_blockout`, `ready`, `running`, `awaiting_review`, `accepted`,
  `failed`, or `deferred`.
- Names such as `final`, `production`, `AAA`, or `accepted` do not establish
  quality. Only registry state plus visual and Unreal-readiness review does.

## Asset and engine boundaries

- Blender owns hero geometry, UVs, bake sources, rigs, pivots, sockets, and
  export-ready source files.
- Unreal owns materials, Fab/Quixel assembly, terrain, water, foliage, PCG,
  lighting, weather, Niagara, gameplay integration, performance, and packaging.
- Do not import a Blender candidate into accepted runtime content until it is
  marked `accepted`.
- Do not replace accepted runtime assets without a reversible integration
  manifest.
- Preserve reference provenance and licenses. Do not invent unsupported weapon,
  aircraft, or drone details.

## Quality gates

- Hero assets require reviewed proportions, clean silhouette, UV coverage,
  calibrated PBR materials, required sockets/pivots, collision, and fixed-camera
  renders.
- Skeletal assets require an armature and deformation review.
- Mission maps require grounded geometry, shoreline contact, temporal stability,
  no camera clipping, and measured traversal performance.
- The project is not production complete until a packaged clean-machine build
  passes gameplay, presentation, input, combat, performance, soak, and stability
  validation.
