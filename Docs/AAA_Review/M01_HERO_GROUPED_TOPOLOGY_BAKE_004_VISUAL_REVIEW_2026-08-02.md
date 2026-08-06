# M01 Hero Grouped Topology Bake 004 Visual Review — 2026-08-02

## Decision

`ARTIFACT_INTEGRITY_CONFIRMED / AUTHOR_GATE_FAIL / DIRECT_MAP_GATE_FAIL`

Build `BLD_M01_HERO_GROUPED_TOPOLOGY_004` was executed once through the
serialized Blender supervisor:

- attempt:
  `D:\Skyguard52\Saved\BuildAttempts\M01_HERO_GROUPED_TOPOLOGY_004\attempt_20260802T141049059Z`;
- Blender 5.2.0 LTS, one process, CPU bake;
- elapsed Blender authoring time: 282.17 seconds;
- Blender exit: `0`, but stderr contained an authored `RuntimeError`;
- group count: 12;
- map count: 24 at 2048×2048;
- package fingerprint:
  `d09352561906e2d9495c08bb56ddbfd2112d4d016c61d9500739c0a4cf7221cd`;
- supervisor gate: `FAIL`;
- direct map gate: `FAIL`;
- promotion: not authorized;
- P3.4: `INCOMPLETE`.

The traceback-aware supervisor correctly rejected Blender's false-zero exit.
No second process was launched and Blender was fully exited.

## Independent artifact postmortem

The postmortem verifier independently confirmed:

- source, extended base contract, active contract, and generator hashes;
- master `.blend` and low-only GLB hashes;
- all 24 PNG hashes and headers;
- exact 12-group and 24-map scope;
- map projection metadata;
- complete source-face coverage;
- cage topology for every group; and
- the deterministic package fingerprint.

It rejected exactly:

1. Pathfinder/PaintShell high-to-low density stayed `1.0000`;
2. RadarPost/ConcreteBunker recorded zero angle-derived sharp edges;
3. RadarPost/DishFeed recorded zero angle-derived sharp edges; and
4. the aggregate author-validation gate.

Receipt:
`D:\Skyguard52\Saved\BuildAttempts\M01_HERO_GROUPED_TOPOLOGY_004\attempt_20260802T141049059Z\artifact_verification_postmortem.json`

## Original-resolution visual review

The first eight queue items were opened directly at their original
2048×2048 resolution. The review stopped fail-fast after all eight failed;
the remaining sixteen maps were not reclassified because the overall visual
gate was already irrecoverably failed.

| Asset/group | Map | SHA-256 | Result |
|---|---|---|---|
| Pathfinder/PaintShell | Normal | `bfc696763f83f3a130afed75d5db57057462667d97e946dbbd63374a3e61d1a6` | **FAIL** — broad olive edge bands and dense granular tangent noise remain. |
| Pathfinder/PaintShell | AO | `3bbdefa0ea8d7293b30e4997f05405d7c40e7542c6942bb3bbe7208d3e2ea46c` | **FAIL** — large faces are clipped to solid black rather than carrying bounded contact occlusion. |
| Pathfinder/EdgeHardware | Normal | `5f2c30fa3c1158fcad330c712877c962f42e24e84ec504d769a11c5421fca899` | **FAIL** — dense multicolor block, stripe, and speckle fields dominate the atlas. |
| Pathfinder/EdgeHardware | AO | `466e1d0be290c65725c28d48ab2623036bb3fdec0036dcfe873bb9d092fb0241` | **FAIL** — approximately half the atlas is hard black with abrupt boundaries. |
| Pathfinder/AccessPanels | Normal | `7587c8a9f2f1f6c011eb9c05233cadaf13dfb4003ae24d84c7b462c4adee98a4` | **FAIL** — long cyan/green/red bars, speckled patches, and hard tangent discontinuities remain. |
| Pathfinder/AccessPanels | AO | `23a68c5ae9e82f2b9c17e90e1a012565fd7048e788dcdf45a52216620532edd3` | **FAIL** — multiple large islands are near-solid black with hard striping. |
| Pathfinder/ThermalHardware | Normal | `7a60e3ec73ea3083b0f70d032c711481dfecc6f9fbc7cd4b9900fd4f4505dda3` | **FAIL** — repeated cyan/magenta ring bands and granular interior fields remain. |
| Pathfinder/ThermalHardware | AO | `55d95c30733fbd28e367a410f50a507fd5583260853756c055879c871b40cfbe` | **FAIL** — cylinder islands are dominated by solid black wedges and fields. |

The unreviewed sixteen maps retain their original hashes and remain
`NOT_REVIEWED`; they are not implicitly passed.

## Root cause and required Build 005 direction

Semantic group isolation removed cross-asset rays but did not make the
per-face-atlas strategy production-ready:

- marking every face as a UV island fragmented tangent domains;
- selected-to-active AO with an offset cage produced hard black regions;
- a beveled duplicate is not a defensible high source for every group; and
- a universal nonzero sharp-edge count is not valid for fully smooth groups.

Build 005 must therefore:

1. preserve connected source UV charts and repack them per semantic group
   instead of forcing every face into a new island;
2. derive authored seam flags from actual UV discontinuities;
3. bake Tangent Normal selected-to-active with a dedicated cage;
4. bake AO directly on the isolated production low, without a projection
   cage;
5. linearly subdivide a high source when beveling produces no density change;
6. permit zero hard edges when a group is intentionally fully smooth; and
7. enforce map-specific black-pixel limits before artifact acceptance.

Build 004 is immutable failed evidence and is not an Unreal import candidate.
