# Mission 01 Hero High-to-Low Map Visual Review — 2026-08-02

## Decision

`ARTIFACT_GATE_PASS / FINAL_VISUAL_PROMOTION_REJECTED`

The serialized Blender 5.2 build and independent artifact verifier pass:

- attempt:
  `D:\Skyguard52\Saved\BuildAttempts\M01_HERO_HIGH_TO_LOW_BAKE\attempt_20260802T125514195Z`;
- terminal state:
  `ARTIFACTS_VERIFIED_CANDIDATE_ONLY`;
- package fingerprint:
  `70b37cdc0aa2294b9a642be44e01056f3392ffdcd02a04f28b86613e3d5de56b`;
- three distinct low/high/cage sets;
- six 2048×2048 Normal/AO maps;
- native master and low-only GLB hashes verified.

This closes Blender execution and artifact-integrity readiness. It does not
close P3.4 or authorize Unreal/runtime replacement.

## Direct map inspection

All six maps were opened directly at high detail.

### Pathfinder

- Normal map is non-empty and preserves the expected UV islands and projected
  edge/detail variation.
- Several thin colored seam excursions and edge gradients require mapped-mesh
  grazing-angle review.
- AO contains very dark large islands and bright hard borders. This may be
  valid for enclosed faces, but it is too aggressive to approve without
  material-response inspection.

### Lighthouse

- Normal and AO maps contain the expected cylindrical, gallery, fastener, and
  seam islands.
- The Normal map contains localized speckled yellow/green regions on circular
  islands. These are candidate cage/ray intersections, overlapping projected
  detail, or tangent discontinuities.
- AO is structurally plausible but still requires mapped-mesh review for
  circular seam gradients and contact-darkening strength.

### Radar post

- Normal and AO maps are non-empty and retain bunker, dish, mast, and fastener
  island structure.
- The Normal map contains multiple localized speckled yellow/green blocks and
  small colored discontinuities. These are not accepted as production-clean
  projection.
- AO has strong black interiors and hard transitions that must be reviewed
  against the low mesh and final material.

## Required correction/acceptance pass

1. Render each mapped low asset from front, rear, profile, top, and at least
   two grazing angles in Blender.
2. Isolate the noisy UV islands and adjust cage extrusion, ray distance,
   high-detail spacing, or UV padding per asset rather than globally.
3. Re-bake and require no speckled tangent regions, skewed detail, gradients,
   seam leaks, or AO clipping in the player-visible range.
4. Import the accepted candidate into an isolated Unreal path.
5. Validate DirectX normal green-channel handling and master-material
   roughness/AO response under daylight, overcast, night, wet, and storm
   lighting.
6. Perform matched before/after review before any runtime substitution.

P3.4 remains `INCOMPLETE`; the current output is a verified engineering
candidate with a documented visual rejection boundary.
