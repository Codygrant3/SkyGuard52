# Skyguard 52 Project Instructions

## Current product direction

As of 2026-08-14 the live goal is a **tactical arcade gunship campaign**:
Apache CPG, AI pilot, sensors, weapons as decisions, threat
prioritization. Not a Yak-52/Igla intercept and not BF6/COD photoreal
parity. Read `Docs/SKYGUARD_OWN_THING.md` and
`Docs/SKYGUARD_APACHE_GUNSHIP_PIVOT.md` before planning weapons, missions,
or aircraft work. Historical AAA evidence stays immutable. Do not reopen
Stage 7B / hero photoreal acceptance loops unless the user explicitly
restores that bar.

## Cursor Cloud

Cloud agents cannot compile Unreal or hit Play. They edit C++/config/tests
only. Before any Cloud gameplay work, read `Docs/SKYGUARD_OWN_THING.md` and
`Docs/SKYGUARD_APACHE_GUNSHIP_PIVOT.md`. Stay on Apache CPG: 30 mm / Hydra /
Hellfire. Do not restore Yak rifle or player Igla.

`.cursor/environment.json` is the Cloud Build install (Git LFS pull). Enable
Builds for this environment in the Cloud Agents dashboard so new agents start
from a verified snapshot instead of just-in-time clone.

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
- The user granted standing authorization on 2026-08-09 for governed Blender
  and Unreal utilization within this canonical project. Do not pause to request
  a new user authorization for each Blender, UnrealEditor, UnrealEditor-Cmd,
  ShaderCompileWorker, UnrealBuildTool, AutomationTool, compiler, renderer,
  capture, profiling, integration, or packaging gate. Existing
  `-AuthorizeSingle*` switches remain mechanical one-shot safety guards and may
  be supplied autonomously after the applicable readiness checks pass.
- Apply `D:\Skyguard52\Production\standing_heavy_process_authorization.json`.
  A historical prompt's per-run user-authorization clause is prospectively
  superseded by this standing authority; its hash, evidence, fresh-namespace,
  one-launch, review, and acceptance requirements remain in force.
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
