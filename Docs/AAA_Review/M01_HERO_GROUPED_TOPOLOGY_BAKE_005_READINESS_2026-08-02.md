# M01 Hero Grouped Topology Bake 005 Readiness — 2026-08-02

## Decision

`SOURCE_READY / HEAVY_LANE_NOT_GRANTED`

Build `BLD_M01_HERO_GROUPED_TOPOLOGY_005` is an offline-only correction to
the immutable failed build 004. No Blender process was launched while Phase 5
owned the exclusive heavy lane.

Static evidence:

- effective contract and base-contract hashes: `PASS`;
- all source checks: `PASS`;
- Python parse/compile: `PASS`;
- supervisor PowerShell parse: `PASS`;
- grouped topology tests: 17/17 `PASS`;
- Blender artifacts: `NOT_RUN`;
- direct original-resolution map review: `NOT_RUN`;
- promotion: not authorized;
- P3.4: `INCOMPLETE`.

## Material change from 004

Build 005 keeps the exact disjoint four-group partition for Pathfinder,
lighthouse, and radar post but removes the strategies disproven by build 004:

1. It retains connected `UV_M01_AAA_0` charts as seeds, isolates them by
   semantic group, normalizes island scale, and repacks them without merging
   overlap.
2. It derives actual mesh seam flags from UV discontinuities after packing.
3. It no longer forces every polygon into a separate tangent domain.
4. Tangent Normal remains selected-to-active with the group's explicit
   normal-offset cage.
5. AO is baked directly on the isolated production low with
   selected-to-active and the cage disabled.
6. A high mesh that receives no density from angle beveling is linearly
   subdivided before baking.
7. Smooth groups may correctly record zero hard edges; the authored angle and
   polygon-smoothing state remain explicit.
8. Normal and AO now carry separate black-pixel limits in the contract and
   author/verifier gates.

## Governed source

- Effective overlay contract:
  `D:\Skyguard52\Docs\AAA_Review\M01_HERO_GROUPED_TOPOLOGY_BAKE_005_CONTRACT.json`
- Hash-bound base contract:
  `D:\Skyguard52\Docs\AAA_Review\M01_HERO_GROUPED_TOPOLOGY_BAKE_003_CONTRACT.json`
- Generator:
  `D:\Skyguard52\Scripts\blender_m01_hero_grouped_topology_bake.py`
- Verifier:
  `D:\Skyguard52\Scripts\verify_skyguard_m01_hero_grouped_topology_bake.py`
- Serialized supervisor:
  `D:\Skyguard52\Scripts\run_m01_hero_grouped_topology_bake_003.ps1`
- Tests:
  `D:\Skyguard52\Scripts\tests\test_m01_hero_grouped_topology_bake.py`
- Readiness receipt:
  `D:\Skyguard52\Saved\Reports\M01_HERO_GROUPED_TOPOLOGY_BAKE_READINESS_005.json`

## Next gate

When the root agent explicitly grants the exclusive Blender lane, invoke the
single governed supervisor with the 005 contract. The supervisor must create
one new attempt, reject traceback text regardless of Blender's exit code,
verify all hashes, and stop at the direct 2048×2048 review boundary.

No 005 artifact or quality claim exists yet.
