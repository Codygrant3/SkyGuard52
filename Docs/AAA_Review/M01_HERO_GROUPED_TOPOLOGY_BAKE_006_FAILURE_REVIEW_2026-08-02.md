# Mission 01 Hero Grouped Topology Bake 006 Failure Review

## Decision

`BLD_M01_HERO_GROUPED_TOPOLOGY_006` is rejected and immutable. It is not
authorized for direct-map acceptance, mapped-mesh review, Unreal import, or
promotion. No further heavy process was launched after this governed attempt.

## Governed attempt

- Attempt:
  `Saved/BuildAttempts/M01_HERO_GROUPED_TOPOLOGY_006/attempt_20260802T144812205Z`
- Start: `2026-08-02T14:48:12.2117730Z`
- Finish: `2026-08-02T14:54:56.5726914Z`
- Blender process exit code: zero
- Supervisor decision: fail, because stderr contained the author-validation
  traceback
- Blender process after supervision: none
- Artifact postmortem:
  `Saved/BuildAttempts/M01_HERO_GROUPED_TOPOLOGY_006/attempt_20260802T144812205Z/artifact_verification_postmortem.json`
- Package fingerprint:
  `8beb2a7bc2175a7ec8974b801c898e2a3fd1ef5340fa9142536aa19f44114cfb`

## Persisted output evidence

- Master blend: 2,091,258 bytes,
  SHA-256 `ebd3370417e573367b858a7e4849c23daa15e0fdcd47defa029e492e8fb571bb`
- Low GLB: 356,076 bytes,
  SHA-256 `fa56ebac5c8ef5acd96e699dc8d5e1dcced9b7d9bbb17ce075a03ad351f518e7`
- Manifest: 94,872 bytes,
  SHA-256 `180672e284c4314dc71ac30f6474cd9076c709a5094e62742f45b40a4974cbf5`
- Author report: 1,304 bytes,
  SHA-256 `ea250134c1b7d61cb2076db7e39f820e34dc6c708c7003f54948f5de5c31b79b`
- Manifest verifies twelve groups, twenty-four map files, output integrity,
  contract/source/generator integrity, and the deterministic package
  fingerprint. Author validation remains false.

## Results

The face-normal correction had one measurable success: Pathfinder/PaintShell
AO black coverage fell from 0.413657 in build 005 to 0.280799 in build 006
after nine faces were reoriented.

Seven AO groups remained above the unchanged 0.35 limit:

- Pathfinder/EdgeHardware: 0.456448
- Pathfinder/ThermalHardware: 0.523800
- Lighthouse/SteelGallery: 0.476879
- RadarPost/ConcreteBunker: 0.381505
- RadarPost/BlastDoor: 0.381405
- RadarPost/MastDrive: 0.827800
- RadarPost/DishFeed: 0.421236

Pathfinder/AccessPanels also contains degenerate geometry: twelve low faces and
ninety-four derived high faces still have zero-length normals after
recalculation. Its AO statistic passed, but its topology did not.

## Diagnosis

Face winding was only one cause. Most remaining black islands did not flip
during consistent-normal authoring and retained exactly the build 005 AO
fractions. They are therefore governed geometry/occlusion problems rather than
threshold noise. The large black areas must not be accepted or hidden by
raising the limit.

The next isolated source revision should be a topology-repair pass, not another
blind bake:

1. Remove or rebuild zero-area AccessPanels faces before high generation.
2. Classify closed, open, double-sided, and interior shell components per
   semantic group.
3. Remove duplicate/copied interior surfaces from the production-low AO target
   while preserving source-face evidence separately.
4. Author AO-only occluder geometry or a bounded selected-to-active AO source
   for legitimate cavities; do not use infinite self-occlusion on open or
   nested shells.
5. Run a cheap geometry diagnostic receipt before reserving another Blender
   bake lane.

## Gate state

- Source gate: PASS
- Artifact integrity: structurally present but FAIL
- Author validation: FAIL
- Direct original-resolution review: NOT RUN
- Mapped-mesh grazing-angle review: NOT RUN
- Unreal acceptance: NOT RUN
- Promotion authorized: false
- P3.4 closed: false
