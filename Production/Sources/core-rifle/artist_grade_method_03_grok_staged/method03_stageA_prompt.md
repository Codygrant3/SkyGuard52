# Skyguard 52 Core Rifle — Artist-Grade Method 03, Stage A

You are the production artist for one bounded Blender task in the canonical Unreal Engine 5.8 / Blender 5.2 project at `D:\Skyguard52`.

This is not a generic gun-generation exercise. Method 02 failed because it built a toy-like primitive M4 with slab receivers, attached rail blocks, a box magazine, disconnected sights, a faceted muzzle, and non-credible ADS. Do not read, import, copy, resume, or modify any Method 01 or Method 02 geometry, scripts, `.blend`, GLB, or scene. Their renders may be used only as negative examples.

## Scope: Stage A only

Build and render only the reference-supported forward assembly:

- long tan/FDE ventilated free-float handguard;
- continuous integrated top Picatinny rail;
- dark barrel visible through actual openings;
- project-provisional open-tine muzzle silhouette;
- the visible circular side socket / attachment detail where supported by the footage.

Do **not** build the receiver, stock, magazine, pistol grip, sights, hands, arms, ammunition, markings, optics, or a complete weapon in this stage.

## Governing reference boundary

Read these files before modeling:

- `D:\Skyguard52\References\CombatAssets\TechnicalIntake_Cycle02\reports\GATE7_COMBAT_ASSET_REFERENCE_RESOLUTION_CYCLE02_REPORT.md`
- `D:\Skyguard52\References\CombatAssets\TechnicalIntake_Cycle02\reports\GATE7_COMBAT_ASSET_REFERENCE_RESOLUTION_CYCLE02_RIFLE_IDENTITY_DECISION.json`
- `D:\Skyguard52\References\CombatAssets\TechnicalIntake_Cycle02\rifle_crop_manifest.json`

Inspect these governed image crops directly with your image-reading capability before touching Blender:

- `D:\Skyguard52\References\CombatAssets\TechnicalIntake_Cycle02\rifle_crops\frame_0435_0014.500s_rifle_crop.png`
- `D:\Skyguard52\References\CombatAssets\TechnicalIntake_Cycle02\rifle_crops\frame_0450_0015.000s_rifle_crop.png`
- `D:\Skyguard52\References\CombatAssets\TechnicalIntake_Cycle02\rifle_crops\frame_0510_0017.000s_rifle_crop.png`
- `D:\Skyguard52\References\CombatAssets\TechnicalIntake_Cycle02\rifle_crops\frame_0675_0022.500s_rifle_crop.png`

The footage proves an AR/M4-pattern family, continuous top rail, long ventilated free-float handguard, and open-tine muzzle silhouette. It does not prove the exact manufacturer, receiver controls, magazine, stock, sights, ammunition, or markings. Do not invent or claim those identities.

## Visual target

The handguard is the hero object. Match the footage's observable language:

- long, slim, mechanically plausible tan/FDE aluminum body;
- chamfered / softly faceted cross-section, not a plain cylinder or box;
- large elongated rounded-rectangle side windows with real negative space and believable wall thickness;
- smaller elongated slots where visible;
- continuous top rail with a proper supporting rail body and clean tooth spacing, not floating or individually attached cubes;
- dark barrel and internal shadow visible through the windows;
- controlled edge bevels and weighted normals so highlights roll like machined metal;
- no intersections, floating parts, paper-thin surfaces, coplanar flicker, non-manifold booleans, or obvious primitive artifacts;
- realistic scale and proportions suitable for a close first-person cockpit view.

The muzzle remains explicitly `PROJECT_PROVISIONAL_OPEN_TINE_MUZZLE`. Reproduce only the supported open-tine silhouette; do not claim an exact device.

## Production method

Use Blender MCP against the single live Blender 5.2 session. Create original geometry only. No external models, asset downloads, web search, Poly Haven, Hyper3D, or other external asset sources.

Work in a fresh scene and write all authored source only under:

- source: `D:\Skyguard52\Production\Sources\core-rifle\artist_grade_method_03_grok_staged`
- attempt: `D:\Skyguard52\Production\Attempts\core-rifle-artist-grade-method03\stage_A_attempt_01`
- output: `D:\Skyguard52\Blender\P0_CORE_RIFLE_ARTIST_GRADE_METHOD03\stage_A`

Do not touch any accepted Unreal runtime asset or any Method 01/02 namespace.

Prefer a clean parametric Blender Python construction script authored into the new Method 03 source namespace and executed through Blender MCP. Use booleans only when they produce stable, inspectable topology. Apply transforms before beveling. Name every production object with `M03A_` and every material with `M03A_MAT_`.

Required top-level collections:

- `M03A_FORWARD_ASSEMBLY`
- `M03A_REVIEW`

Required empties/sockets:

- `SOCKET_M03A_Receiver_Interface`
- `SOCKET_M03A_Muzzle`
- `SOCKET_M03A_TopRail_Origin`

## Materials for this gate

Use only enough calibrated PBR preview material to judge form:

- subdued FDE anodized aluminum for the handguard and rail;
- dark phosphated / nitrided steel for the barrel and provisional muzzle;
- subtle roughness variation and restrained edge wear driven procedurally;
- no bright toy plastic, baked fake shadows, logos, text, or unsupported markings.

Do not spend time on final UVs, UDIMs, texture bakes, LODs, collision, GLB export, or Unreal import yet. Those are forbidden until Stage A passes visual review.

## Required review renders

Render exactly four 2560 x 1440 PNGs into the fresh attempt directory:

1. `stageA_left_oblique.png` — full forward assembly, close three-quarter left.
2. `stageA_right_oblique.png` — full forward assembly, close three-quarter right.
3. `stageA_top_mechanical.png` — top/side mechanical view proving rail continuity and window construction.
4. `stageA_reference_match.png` — perspective intentionally similar to the governed onboard crop, without copying the surrounding cockpit.

Use a neutral studio environment with soft key/fill/rim lighting and a non-distracting mid-gray background. Keep the complete forward assembly in frame with useful margins. No depth of field that hides topology.

## Self-review and bounded correction

After the first renders, inspect all four images directly. You may perform **one** correction pass, limited to Stage A geometry, framing, and preview material.

Reject your own result instead of claiming success if any of these remain:

- the handguard reads as a rounded box, pipe, or primitive shell;
- the large openings are decals, dark plates, or shallow dents instead of real negative space;
- rail teeth float, repeat mechanically without a base, or resemble cubes glued on top;
- the barrel is not credibly visible through the openings;
- the muzzle is a faceted cap rather than an open-tine silhouette;
- silhouette/proportion visibly diverges from the governed crops;
- shading is lumpy, plastic, broken, or visibly boolean-damaged;
- any unsupported receiver, magazine, stock, sight, or marking appears.

## Deliverables and handoff

Produce:

- `core-rifle-method03-stageA.blend` in the Stage A output directory;
- the four renders in the attempt directory;
- the authored Blender Python source in the Method 03 source directory;
- `stageA_artifact_manifest.json` with relative paths, byte counts, SHA-256 hashes, Blender version, object counts, triangle counts, material names, socket names, render dimensions, and reference files used;
- `grok_method03_stageA_handoff.json` in the attempt directory.

The handoff must report exactly one classification:

- `PASSED_STAGE_A_AWAITING_CODEX_VISUAL_REVIEW`
- `FAILED_STAGE_A_WITH_EVIDENCE`

Do not call the asset AAA, final, Unreal-ready, or production-accepted. Stage A success only means the forward assembly is ready for direct Codex visual inspection.

Work efficiently. Do not waste turns narrating a plan. Inspect references, build, render, inspect, use at most one correction, write receipts, and stop.
