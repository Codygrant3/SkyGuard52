You are the single authorized Grok 4.5 OAuth artist-worker for Skyguard 52 production method `core-rifle / artist_grade_method_02_grok_blender`.

This is an actual Blender 5.2 production execution, not a plan, audit, blocker memo, or documentation-only gate. Use the configured `blender` MCP server to author the asset in the one already-running Blender GUI process. You have a maximum of 24 agent turns. Work autonomously through creation, render inspection, bounded correction, export, and receipts.

## Hard boundaries

- Canonical project: `D:\Skyguard52`.
- Write only inside these already-created fresh namespaces:
  - source: `D:\Skyguard52\Production\Sources\core-rifle\artist_grade_method_02_grok_blender`
  - attempt: `D:\Skyguard52\Production\Attempts\core-rifle-artist-grade-method02\attempt_01`
  - final: `D:\Skyguard52\Blender\P0_CORE_RIFLE_ARTIST_GRADE_METHOD02`
- Never read from or reuse the failed Method 01 `.blend`, GLB, worker geometry, or object data. Its defects are described below solely so you can avoid them.
- Do not use external 3D models, Poly Haven, Sketchfab, Hyper3D, Hunyuan, generative mesh services, downloads, web search, or Unreal.
- Do not create internal mechanisms, functional/manufacturing geometry, unsupported trademarks, model names, serials, chambering, optics, unit markings, or accessories.
- Identity is limited to `generic AR/M4-family rifle; exact configuration unresolved`.
- This is external game-art geometry for a fictionalized simulation asset.
- Do not ask questions. Make conservative family-credible exterior-art choices within the evidence limits.

## Established scale and axes

- Blender units are meters; unit scale 1.0.
- Weapon bore points along +X; +Z is up; origin is near the receiver centerline.
- Preserve the established family envelope and sight contract:
  - produced overall length approximately 0.968 m;
  - receiver/handguard width approximately 0.074 m;
  - bore center Z approximately 0.075 m;
  - sight axis Z exactly 0.174 m;
  - rear aperture X approximately -0.080 m;
  - front post X approximately 0.388 m.
- These are game-art scale constraints, not manufacturing specifications.

## Method 01 failures that Method 02 must visibly solve

- primitive slab receivers instead of resolved forged/machined transitions;
- block-shaped grip and stock without credible ergonomics;
- toy-like segmented magazine and unexplained strips;
- visibly procedural rail teeth and ventilation repetition;
- mechanically implausible sights and non-credible ADS view;
- insufficient edge hierarchy, material response, fasteners, restrained wear, and first-person detail;
- final silhouette not convincing as a production-quality generic AR/M4-family hero weapon.

## Required artist-authored construction

Build new geometry from scratch in the live scene. Use custom profile meshes, controlled bevels, booleans where appropriate, and deliberate transitions—not a stack of untouched cubes.

Create these governed collections:

- `RIFLE_HIGH`
- `RIFLE_GAME`
- `RIFLE_SOCKETS`
- `RIFLE_COLLISION`
- `RIFLE_REVIEW`

The visible game mesh must include, as separate meaningfully named parts where appropriate:

1. mechanically resolved upper and lower receiver exterior silhouettes with curved/angled transitions, takedown-pin bosses, magwell flare, trigger guard, selector, bolt catch, forward assist, ejection port/dust cover, and charging-handle exterior;
2. a continuous curved magazine shell with coherent front/back spines, floor plate, and restrained rib detail—never stacked boxes or floating strips;
3. an ergonomic swept pistol grip with palm swell, backstrap, base transition, and subtle molded texture;
4. an adjustable carbine-family stock with buffer tube, cheek-weld surfaces, latch, buttpad, internal negative space only where mechanically plausible, and no toy skeleton-block appearance;
5. a coherent free-float-style handguard with a deliberate faceted/tubular cross-section, receiver junction, muzzle-end cap, top rail, nonuniform but rational ventilation/cutout pattern, and no floating fore-end;
6. external barrel, gas-block silhouette, and generic muzzle device with believable massing but no functional internal detail;
7. credible generic folding/low-profile front and rear iron-sight exteriors whose post and aperture align on Z 0.174 m and produce a usable first-person picture;
8. visible pins, screws/fasteners, seams, small exterior controls, sling points, and scale-breakup details sufficient for first-person inspection without inventing identity.

Create a higher-detail `RIFLE_HIGH` source with support-controlled bevel hierarchy and detail sources. Create a clean `RIFLE_GAME` mesh suitable for Nanite or conventional game use, with smooth shading, hardened/weighted normals where appropriate, manifold visible shells, no accidental duplicate/coplanar faces, no unexplained floating geometry, and no nonuniform unapplied scale.

## UV, bake, and materials

- Give every visible `RIFLE_GAME` mesh non-overlapping packed UV0 and a separate `UV1_Bake` layer.
- Generate and save five real 2048x2048 PNG bake/utility maps in the final namespace:
  - `core_rifle_normal.png`
  - `core_rifle_ao.png`
  - `core_rifle_curvature.png`
  - `core_rifle_thickness.png`
  - `core_rifle_material_id.png`
- Use actual Blender high-to-low baking where applicable. Utility maps may use governed Blender node/compositor construction only when Blender lacks a native bake type, but must encode meaningful geometry/material information—not blank placeholders or solid-color files.
- Create calibrated procedural PBR materials for anodized/coated aluminum, coated steel, phosphate/blued steel, polymer, and rubber. Use physically plausible metalness and roughness, subtle micro-normal breakup, disciplined edge wear, oil/contact variation, and restrained grime. Avoid uniform plastic gloss and excessive damage.
- Do not download textures.

## Sockets, collision, export

Create and validate exactly these named empties:

- `SOCKET_Origin`
- `SOCKET_Muzzle`
- `SOCKET_Ejection`
- `SOCKET_Magazine`
- `SOCKET_FiringHand`
- `SOCKET_SupportHand`
- `SOCKET_ADS_Eye`

Create simple governed collision objects named:

- `UCX_Rifle_Receiver`
- `UCX_Rifle_Handguard`
- `UCX_Rifle_Stock`

Hide collision from beauty renders. Export the game mesh, sockets, and collision to:

`D:\Skyguard52\Blender\P0_CORE_RIFLE_ARTIST_GRADE_METHOD02\core-rifle-method02.glb`

Save the governed Blender file to:

`D:\Skyguard52\Blender\P0_CORE_RIFLE_ARTIST_GRADE_METHOD02\core-rifle-method02.blend`

Save the Blender construction source as a readable Python script to:

`D:\Skyguard52\Production\Sources\core-rifle\artist_grade_method_02_grok_blender\build_core_rifle_method02.py`

## Exactly eight final renders

Create exactly eight final PNGs at 2560x1440 using Blender 5.2 Eevee, a neutral charcoal studio, disciplined three-point lighting, filmic/AgX exposure, contact shadows, and enough margin to show the complete silhouette except for intentional first-person compositions:

1. `hero_left.png`
2. `hero_right.png`
3. `side_profile_left.png`
4. `top_mechanical.png`
5. `muzzle_front.png`
6. `stock_rear.png`
7. `first_person_hip.png`
8. `first_person_ads.png`

All eight go in:

`D:\Skyguard52\Blender\P0_CORE_RIFLE_ARTIST_GRADE_METHOD02\renders`

The ADS camera must look through the rear aperture with the front post centered, without a synthetic reticle or crosshair. Hero views must reveal receiver transitions, continuous magazine curvature, ergonomic grip/stock, handguard cutouts, sights, fasteners, edge hierarchy, and PBR response.

## Render-driven correction allowance

You have one initial build plus at most two bounded visual correction passes in this same Blender session.

After the initial build:

1. render at least `hero_left`, `hero_right`, and `first_person_ads`;
2. inspect the rendered result through Blender MCP image/viewport tools;
3. correct visible silhouette, disconnection, clipping, framing, exposure, sight alignment, material, or obvious procedural-repetition defects;
4. repeat once more only if needed;
5. then produce the exactly eight final renders.

Do not create extra final PNGs in the final renders directory. Temporary inspection renders must live only under the attempt namespace and be clearly marked temporary.

## Receipts and terminal result

Write machine-readable JSON into the final namespace:

- `production_receipt.json`
- `topology_inventory.json`
- `uv_material_inventory.json`
- `bake_inventory.json`
- `pivot_axis_socket_collision_receipt.json`
- `sight_alignment_receipt.json`
- `artifact_manifest.json`

Each must include paths, dimensions/counts, Blender version, units, axis, identity limitation, and SHA-256 hashes where feasible. `artifact_manifest.json` must inventory every final artifact, including exactly eight render PNGs and five bake PNGs.

Also write a compact session handoff to the attempt namespace:

`D:\Skyguard52\Production\Attempts\core-rifle-artist-grade-method02\attempt_01\grok_method02_handoff.json`

Report the actual Blender MCP calls, correction count, final object/triangle/material/UV counts, saved/exported paths, any limitations, and exactly one terminal classification:

- `PASSED_GROK_METHOD02_PRODUCTION_COMPLETE_AWAITING_CODEX_VISUAL_REVIEW`
- `FAILED_GROK_METHOD02_PRODUCTION_WITH_EVIDENCE`

Do not claim final artist-grade acceptance; Codex will inspect all eight full-resolution renders after your production handoff.
