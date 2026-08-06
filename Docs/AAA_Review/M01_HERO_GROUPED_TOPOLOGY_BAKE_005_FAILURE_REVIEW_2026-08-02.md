# Mission 01 Hero Grouped Topology Bake 005 Failure Review

## Decision

`BLD_M01_HERO_GROUPED_TOPOLOGY_005` is rejected and immutable. It is not
authorized for direct-map acceptance, mapped-mesh review, Unreal import, or
promotion.

## Governed attempt

- Attempt:
  `Saved/BuildAttempts/M01_HERO_GROUPED_TOPOLOGY_005/attempt_20260802T143629697Z`
- Supervisor result: failed safely after Blender emitted a Python traceback
  despite process exit code zero.
- Blender process: fully exited.
- Author report:
  `Saved/Reports/M01_HERO_GROUPED_TOPOLOGY_BAKE_REPORT_005.json`
- Package fingerprint:
  `d4c8fd58efc2640fadff6867075153688647cc1fc1291e9040864da4d03e57dc`

## Evidence

All twelve semantic groups and all twenty-four maps were authored, but eight AO
maps exceeded the maximum black-pixel fraction:

- Pathfinder/PaintShell: 0.413657
- Pathfinder/EdgeHardware: 0.456448
- Pathfinder/ThermalHardware: 0.523800
- Lighthouse/SteelGallery: 0.476879
- RadarPost/ConcreteBunker: 0.381505
- RadarPost/BlastDoor: 0.381405
- RadarPost/MastDrive: 0.827800
- RadarPost/DishFeed: 0.421236

Direct original-resolution inspection of representative failed maps confirmed
that the statistic reflected a real defect: entire UV islands were pure black,
with only narrow noisy edge gradients. The gate must not be weakened.

## Root cause and corrective action

Material partitioning preserved inherited face winding on disconnected shells.
Some partitioned components therefore baked AO while facing inward, producing
fully occluded islands. The next isolated build must recalculate consistent
face normals on every partitioned low mesh before smoothing, UV validation,
high-source construction, cage generation, or baking. The derived high mesh
must also recalculate consistent face normals after bevel/subdivision.

## Non-claims

- Build 005 did not pass author validation.
- The remaining maps were not accepted merely because their numeric thresholds
  passed.
- No Unreal/runtime asset was replaced.
- Build 006 must pass fresh source, artifact, original-resolution map, mapped
  mesh, and Unreal gates independently.
