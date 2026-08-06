# Mission 01 Hero Grouped Topology Bake 007 Offline Readiness

## Decision

`BLD_M01_HERO_GROUPED_TOPOLOGY_007` is source-ready for one future governed
Blender attempt after the exclusive heavy lane is granted. It has not been
executed in Blender or Unreal, has no canonical Build 007 artifact outputs, and
is not authorized for promotion.

## Offline classification

Build 006 was classified directly from its persisted low GLB without importing
`bpy`, launching Blender, or launching Unreal.

- Classification report:
  `Saved/Reports/M01_HERO_GROUPED_TOPOLOGY_CLASSIFICATION_007.json`
- SHA-256:
  `e575447dc07b8da7bf02f0ecef81f3c9bec3fba1228da21739698b737bd4a30d`
- Groups classified: 12
- Degenerate groups: 1
- Nonmanifold groups: 1
- Open groups after positional weld: 0
- Nested groups: 0
- Inward/interior groups: 0
- AO-failed groups: 7

The classified topology defects are:

- Pathfinder/AccessPanels: twenty-four degenerate exported triangles,
  corresponding to the twelve zero-area source faces reported by Build 006.
- Pathfinder/PaintShell: seven nonmanifold welded edges.

The remaining seven black-AO failures are closed exterior candidates rather
than degenerate, open, nested, or inward shells. Their unchanged Build 005/006
fractions exposed a separate isolation defect: the prior AO path selected only
the target but did not hide the source objects, prior groups, high meshes, or
cages from render visibility.

## Deterministic Build 007 repairs

The contract defines all twelve group policies before execution:

1. Remove zero-area AccessPanels faces, then remove orphan edges and vertices.
2. Split PaintShell edges with more than two linked faces.
3. Require zero remaining zero-area faces and zero remaining nonmanifold edges.
4. Recalculate component-consistent normals after topology repair.
5. Hide every non-participating mesh from render visibility for every bake.
6. Use direct-low AO only for LanternGlass, RedBandsRoof, and WhiteTower.
7. Use nine separately named, separately datablocked high-derived AO occluders
   with the existing bounded group cage and maximum ray distance for all seven
   AO failures plus AccessPanels and PaintShell.
8. Preserve selected-to-active tangent normal baking, neutral backgrounds,
   twenty-four map hashes, and fail-closed visual promotion.

## Source gate

- Unit tests: 22/22 PASS
- Python parse checks: PASS
- Source verifier: PASS
- Readiness terminal state: `GROUPED_SOURCE_READY_BLENDER_NOT_RUN`
- Artifact gate: NOT RUN
- Direct original-resolution map review: NOT RUN
- Mapped-mesh grazing-angle review: NOT RUN
- Unreal acceptance: NOT RUN
- Promotion authorized: false
- P3.4 closed: false

## Evidence hashes

- Build 007 contract:
  `2ce748f9ea34772a9bbb533df5a8a272d179b76ab56cc448dbe9769225f4e0d0`
- Offline classifier:
  `71cccbd93ea3ee5f4328c943c90164c50be582d26067bdba569cc0dc00b008f5`
- Classification report:
  `e575447dc07b8da7bf02f0ecef81f3c9bec3fba1228da21739698b737bd4a30d`
- Blender generator source:
  `ca04ef4aee070d58f66156759582fdf7af3608e09e91d54609b6f7794f65ff76`
- Verifier:
  `eb84d77efe6d29ca774afcb9d1f3df757e4e43f634686f7e01af86c924cae44d`
- Serialized supervisor:
  `7fe6eca8030b728826d83b09634794bab7a20359389e9ea91b56aecff4f4f0f7`
- Unit tests:
  `a1163f8fcae2cace4e22a0a7716fd542b5624c8cef44d7eab5580bee61979e58`
- Readiness receipt:
  `53364883c9b11a79802d3e7cf67fd366c7a33957d601790f94a6479c0da7e5bd`

## Future governed command

The following command is documented only and was not run during offline
preparation:

```powershell
& 'D:\Skyguard52\Scripts\run_m01_hero_grouped_topology_bake_003.ps1' `
  -ProjectRoot 'D:\Skyguard52' `
  -BlenderExe 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' `
  -ContractPath 'D:\Skyguard52\Docs\AAA_Review\M01_HERO_GROUPED_TOPOLOGY_BAKE_007_CONTRACT.json' `
  -TimeoutSeconds 3600
```

The supervisor now archives the hash-bound classification report alongside the
contract, base contract, generator, verifier, and supervisor source.
