# M01 Hero Grouped Topology Bake 007 Visual Review — 2026-08-02

## Decision

`ARTIFACT_INTEGRITY_CONFIRMED / AUTHOR_GATE_PASS / DIRECT_MAP_GATE_FAIL`

Build `BLD_M01_HERO_GROUPED_TOPOLOGY_007` completed once through the serialized
Blender supervisor. Artifact verification and the authored topology gate both
passed, but six of the twenty-four required original-resolution maps failed
direct visual inspection. The build is rejected for mapped-mesh review, Unreal
import, promotion, and P3.4 closure.

No Blender or Unreal process remained active after the governed attempt, and
no further heavy process was launched during this review.

## Governed attempt

- Attempt:
  `Saved/BuildAttempts/M01_HERO_GROUPED_TOPOLOGY_007/attempt_20260802T153804154Z`
- Blender version: `5.2.0 LTS`
- Blender exit code: zero
- Supervisor decision:
  `ARTIFACTS_VERIFIED_AWAITING_DIRECT_ORIGINAL_RESOLUTION_MAP_REVIEW`
- Package fingerprint:
  `b554cb542d493310f61f27bfa1c8e20711ea1959a4674cd210aad74fbc9a750d`
- Contract:
  `Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_BAKE_007_CONTRACT.json`
- Direct-review receipt:
  `Saved/BuildAttempts/M01_HERO_GROUPED_TOPOLOGY_007/attempt_20260802T153804154Z/direct_original_resolution_map_review_receipt.json`

## Original-resolution review

Every map was opened directly at its original 2048×2048 resolution. Contact
sheets and thumbnails were not used as acceptance evidence.

| Asset/group | Map | SHA-256 | Result |
|---|---|---|---|
| Pathfinder/PaintShell | Normal | `1881f8faf4d2150bb424db77963154e2fbae75b8b5a4614f1820aee0926e20fc` | **FAIL** — broad olive/cyan edge bands and dense granular tangent noise remain. |
| Pathfinder/PaintShell | AO | `a787bc879de596aa38680c1c533653afdbdd3d5ce1226be559a432dea8393f90` | **FAIL** — a large populated island is filled near-solid black. |
| Pathfinder/EdgeHardware | Normal | `4eeef4af3f832a290fabaa4e735732a2d83adaa45b756abcbadf5993f9f55946` | **FAIL** — prominent multicolor projection bands contaminate hardware strips. |
| Pathfinder/EdgeHardware | AO | `0254f481680e130c5f8dc6de71d8c9b0cd09d472b29a81d40a99494e9ef1ac32` | **PASS** — localized, geometry-coherent occlusion. |
| Pathfinder/AccessPanels | Normal | `0fd8c00228b138726d218d93de460778118199dae938aa428b096c7e77c3484d` | **PASS** — clean panel gradients after topology repair. |
| Pathfinder/AccessPanels | AO | `87c1ecdf398822bbe742d289e6e6641efda9afd575fc6992a151f1d7cb5bbe22` | **PASS** — subtle bounded occlusion without black contamination. |
| Pathfinder/ThermalHardware | Normal | `77ac1e9c9183a7f0a7bdde0d13302b64fcb244c9be65d99c821a5dc089da314c` | **PASS** — coherent circular and rectangular hardware detail. |
| Pathfinder/ThermalHardware | AO | `002cc78a61ca36d8784e93246532c077d57db0dd860ff5ca914b740212e7d3b8` | **PASS** — bounded subtle hardware occlusion. |
| Lighthouse/WhiteTower | Normal | `70ba16f3ba31a9837bf0327e3d8345fafc454f5d9f853dc704243fcebb8038e6` | **FAIL** — several populated islands contain dense multicolor speckle fields. |
| Lighthouse/WhiteTower | AO | `283140a02e1c3cbbb50f3fd03e41a6abb40fabff1e411de0eb1213d5f5c811b9` | **FAIL** — multiple large populated islands are near-solid black. |
| Lighthouse/RedBandsRoof | Normal | `1d814d8e53767bea12c0c9ba45f53bc9f126ac1b8e7cc206139ad4d869a3003a` | **PASS** — coherent roof gradients and edge transitions. |
| Lighthouse/RedBandsRoof | AO | `e6b99cd21b3de9719e8a94734db377eabdd43117539148d5a902d42a9ff9263d` | **PASS** — bounded direct-low self-occlusion. |
| Lighthouse/SteelGallery | Normal | `c79c49e823fc9de72e237ad66027cef6881b62573229e8b3949f9a9ac5958735` | **PASS** — coherent rings, rails, posts, and fasteners. |
| Lighthouse/SteelGallery | AO | `2eccf7a3d423965be69e5a3c1787a8088e7d246913eeb2b456baf86ba4fad813` | **PASS** — dark values remain localized to legitimate cavities. |
| Lighthouse/LanternGlass | Normal | `a568600b600aea0e96578862ac19bbf183ccc4c92c78fdd9320e7bdf22fa5b6e` | **PASS** — clean low-amplitude glass gradients. |
| Lighthouse/LanternGlass | AO | `78d027cbb31ba9175d5cfe5c632749b95e0291bb09adad261abe138a70db76b5` | **PASS** — near-neutral exposed-glass AO without contamination. |
| RadarPost/ConcreteBunker | Normal | `3bb4ef0372fd0101b396545efdffdb9b6656425407a35c43c58a0575054761e9` | **PASS** — coherent panel and bevel gradients. |
| RadarPost/ConcreteBunker | AO | `242833467da3db78de6cf298f9ee8e971794b11cf9f24ba381de2cffb1631410` | **PASS** — subtle bounded AO for broad exposed panels. |
| RadarPost/BlastDoor | Normal | `aeccce54a6b5ce21584dc5b247df5a65743d3a908df894ba4e815e4f4a13257b` | **PASS** — coherent panel and rib detail. |
| RadarPost/BlastDoor | AO | `f3eec3ab2a3c864d6e036b48e900d44bda540bd0597d6621e159f0873b4cea2b` | **PASS** — bounded low-contrast AO. |
| RadarPost/MastDrive | Normal | `5e5610d53edfed4d047929363d20e7e12bcd9c114c3da4443537638c1e5097a4` | **FAIL** — isolated high-contrast projection ticks cross the mast and drive islands. |
| RadarPost/MastDrive | AO | `f00a6a49c79dd59768c7a7baec9c956a1ecedf81798f6f7ee78247dd272ecad6` | **PASS** — strong values remain aligned to recessed drive geometry. |
| RadarPost/DishFeed | Normal | `d8dfb974606e42402aaf78ae6d40459aa85607effb02979282cf35ee145cec87` | **PASS** — coherent dish, ring, feed, and support detail. |
| RadarPost/DishFeed | AO | `438d58f2efa68fc042990611f142b28a22c95e8b131cd15b55912dd439103bf5` | **PASS** — localized ring, support, and fastener occlusion. |

Result: eighteen maps passed and six failed.

## Diagnosis and next corrective direction

Build 007 successfully repaired the AccessPanels zero-area faces, split the
PaintShell nonmanifold edges, isolated render visibility, and eliminated the
global AO-limit failures that blocked build 006. Those structural corrections
must be retained.

The remaining failures are narrower:

1. Pathfinder/PaintShell and Lighthouse/WhiteTower still contain tangent-normal
   projection contamination on populated islands.
2. Pathfinder/EdgeHardware and RadarPost/MastDrive require tighter normal
   projection control around thin, repeated, or nearby geometry.
3. The dedicated PaintShell AO occluder still produces a large solid-black
   island.
4. WhiteTower direct self-occlusion is not viable for its nested closed
   components and must move to a bounded per-component AO strategy.

The next attempt must be source-bound and diagnose only these four groups. It
must not rebake the eighteen accepted maps blindly, must not modify builds 003
through 007, and must not enter Unreal until every replacement map passes
direct original-resolution review.

## Gate state

- Source gate: PASS
- Artifact integrity: PASS
- Author validation: PASS
- Direct original-resolution review: **FAIL**
- Mapped-mesh grazing-angle review: NOT AUTHORIZED
- Unreal acceptance: NOT AUTHORIZED
- Promotion authorized: false
- P3.4 closed: false
