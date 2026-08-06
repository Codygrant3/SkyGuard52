# Mission 01 Hero Grouped Topology Bake 008 — Offline Readiness

Status: **PASS — ready for the exclusive Blender lane, not yet authored**

Build 008 is the isolated corrective successor to the immutable Build 007 candidate. No Blender or Unreal process was launched during this readiness pass.

## Corrective scope

- Rebake exactly six maps rejected by Build 007 direct original-resolution review.
- Reuse the other eighteen accepted Build 007 maps only through byte-for-byte SHA-256 identity.
- Use component-exploded, bake-only duplicates for the six corrective projections.
- Never translate the production-low geometry.
- Use a dedicated bounded AO occluder for `Pathfinder/PaintShell` and `Lighthouse/WhiteTower`.
- Keep promotion fail-closed after authoring until the six new maps pass direct original-resolution review, followed by mapped-mesh grazing-angle review and Unreal acceptance.

The six rebake targets are:

1. `Pathfinder/PaintShell/Normal`
2. `Pathfinder/PaintShell/AO`
3. `Pathfinder/EdgeHardware/Normal`
4. `Lighthouse/WhiteTower/Normal`
5. `Lighthouse/WhiteTower/AO`
6. `RadarPost/MastDrive/Normal`

## Offline verification

- Source verifier: PASS, all checks.
- Dedicated unit suite: 16 passed, 0 failed, 0 errors.
- Python parsing and bytecode compilation: PASS.
- PowerShell parser: PASS.
- Offline classification semantic reproduction: PASS.
- Corrective partition: 6 rebake + 18 reuse = 24 maps.
- Build 008 canonical outputs: absent.
- Active Blender/Unreal processes at readiness check: none.

The supervisor is serialized, refuses an overlapping Blender process, refuses canonical overwrite, archives the correction basis and immutable Build 007 evidence, and creates a review queue with only the six new maps pending. The eighteen reused maps inherit their Build 007 PASS status only after hash identity verification.

## Governed evidence

- Contract SHA-256: `a107e6e9ab398ec42de4c0114585ae7ddbd47185d10597068577fdae5aea3eff`
- Generator SHA-256: `6c547078cb31f9f3f940c468c80e4a6392ba715ab9dd3e7e26b059fd80cd18bf`
- Verifier SHA-256: `1b43c517bc6593db6a64cd7669c24445d958b6920582fc215f4db59d94a3510e`
- Supervisor SHA-256: `370e2fac677c6912705ec050f61780e516ac4e38b6a9b259eb2a1b346c1bbb19`
- Test suite SHA-256: `b616784a8abcca4da8c76105ecfff784fcf61262ab85ffd9df2edbd78b9c4e5e`
- Classification SHA-256: `77b1471029f1d7c29249ca0f98a7bfd768f2f3cab6dcf2253ab043d9735285b5`
- Build 007 manifest SHA-256: `1ac5f4881f2eede51626d9cede40b420df7fc165bb9378bc30909a7c85c1d8c0`
- Build 007 direct-review receipt SHA-256: `ed118ed9c98dcb44e50227481a69f94ec8391d67f8d88b5ce39776df7341f5fe`

Machine-readable readiness receipt:
`D:\Skyguard52\Saved\Reports\M01_HERO_GROUPED_TOPOLOGY_BAKE_READINESS_008.json`

## Remaining gates

1. Run the serialized Build 008 supervisor in the exclusive Blender lane.
2. Verify the authored manifest and all output hashes.
3. Inspect the six corrective maps directly at original 2048×2048 resolution.
4. Run the mapped-mesh grazing-angle review.
5. Only after those pass, proceed to Unreal acceptance.

Build 008 is source-ready; it is not promoted and P3.4 remains open.
