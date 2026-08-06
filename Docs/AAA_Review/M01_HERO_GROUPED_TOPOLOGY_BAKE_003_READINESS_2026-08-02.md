# M01 Hero Grouped Topology Bake 003 Readiness — 2026-08-02

## Decision

`SOURCE_READY / EXCLUSIVE_BLENDER_EXECUTION_NOT_YET_RUN`

Build `BLD_M01_HERO_GROUPED_TOPOLOGY_003` replaces the rejected whole-asset
projection design used by builds 001 and 002. It does not overwrite either
candidate or reinterpret their failed visual reviews.

Static source verification currently passes. P3.4 remains `INCOMPLETE`.

## Structural correction

The 002 visual gate established that cage tuning alone could not correct:

- cross-shell normal projection;
- multicolor speckling inside circular islands;
- abrupt AO voids;
- filled or hard-edged island backgrounds; and
- tangent discontinuities inherited from one joined smart-projected mesh.

Build 003 divides each hero into four exact, disjoint source-material groups:

| Asset | Isolated bake groups |
|---|---|
| Pathfinder | PaintShell, EdgeHardware, AccessPanels, ThermalHardware |
| Lighthouse | WhiteTower, RedBandsRoof, SteelGallery, LanternGlass |
| RadarPost | ConcreteBunker, BlastDoor, MastDrive, DishFeed |

Every source face must occur in exactly one group. The generator fails if a
source material is missing, duplicated across groups, or newly appears outside
the contract.

## Production-art contract

Every one of the twelve groups receives:

1. an independent low mesh containing only its governed material faces;
2. orphan-free topology and retained source-face accounting;
3. a new `UV_M01_GROUPED_0` layer;
4. explicit face-island seams, angle-based unwrap, normalized island scale,
   and packed 0–1 UVs;
5. smooth polygons with hard edges governed by the group angle;
6. a separate three-segment beveled high mesh;
7. a separate cage with topology identical to the low and vertices moved only
   along their normals;
8. isolated selected-to-active Tangent Normal and AO bakes; and
9. one Normal and one AO map at 2048×2048.

This produces 12 lows, 12 highs, 12 cages, and 24 governed maps. Unoccupied
Normal pixels stay neutral `(0.5, 0.5, 1.0)` and AO pixels stay white instead
of being cleared to black.

## Fail-closed execution

Supervisor:

`D:\Skyguard52\Scripts\run_m01_hero_grouped_topology_bake_003.ps1`

The supervisor:

- refuses to overlap any active Blender process;
- source-verifies before Blender starts;
- refuses to overwrite any canonical 003 output;
- redirects stdout/stderr directly to an attempt-specific directory;
- records the Blender PID;
- waits up to one hour;
- independently verifies all artifacts and hashes;
- archives exact inputs, native master, GLB, maps, reports, and recursive
  hashes; and
- emits a 24-entry direct-map review queue with every item initially
  `PENDING`.

An artifact PASS ends at:

`ARTIFACTS_VERIFIED_AWAITING_DIRECT_ORIGINAL_RESOLUTION_MAP_REVIEW`

It does not promote the assets.

## Direct visual gate

All 24 PNG files must be opened at original 2048×2048 resolution. A group
fails if either map contains:

- black unoccupied Normal pixels;
- cyan/magenta/olive projection blocks unrelated to a real surface turn;
- salt-and-pepper speckling;
- rays from another semantic group;
- discontinuities not aligned to an authored UV/tangent seam;
- hard AO voids caused by an unrelated shell; or
- obvious margin dilation leaking into a neighboring island.

Every queue row must record `PASS` or `FAIL`, a concise observation, reviewer,
review time, and the exact reviewed SHA-256. Any failed or unreviewed row keeps
the overall gate failed.

Even a 24/24 direct map pass only authorizes mapped-low validation from front,
rear, profile, top, and two grazing angles. Unreal substitution still requires
separate lighting and material acceptance.

## Current evidence

- Contract:
  `D:\Skyguard52\Docs\AAA_Review\M01_HERO_GROUPED_TOPOLOGY_BAKE_003_CONTRACT.json`
- Blender generator:
  `D:\Skyguard52\Scripts\blender_m01_hero_grouped_topology_bake.py`
- Independent verifier:
  `D:\Skyguard52\Scripts\verify_skyguard_m01_hero_grouped_topology_bake.py`
- Static tests:
  `D:\Skyguard52\Scripts\tests\test_m01_hero_grouped_topology_bake.py`
- Readiness report:
  `D:\Skyguard52\Saved\Reports\M01_HERO_GROUPED_TOPOLOGY_BAKE_READINESS_003.json`

No Blender execution or visual acceptance is claimed by this readiness record.
