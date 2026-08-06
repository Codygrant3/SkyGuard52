# Yak-52 L88 Reference and Provenance Notes

Updated: 2026-08-01 (pass22)
Asset stage: dimension-locked silhouette blockout
Production approval: NO

## Authorship and rights

This blockout was authored procedurally for the Skyguard52 project by Codex
using `D:\Skyguard52\Scripts\blender_l88_yak52_blockout.py`. It does not contain
geometry, UVs, textures, or materials copied from the rejected
`yak52-detail-kit` GLBs. It is project-owned working source, subject to the
project owner's normal rights and distribution decisions.

The rear-gunner rifle/gameplay layer is Skyguard fiction and is not represented
as historical Yak-52 factory equipment.

## Reference contract

- Variant target: Yak-52 tandem-seat radial-engine trainer
- Target length: 7.68 m
- Target wingspan: 9.30 m
- Target height: 2.70 m
- Coordinate contract: +X forward, +Z up
- Current measured envelope: 7.6750 x 9.3000 x 2.6915 m
- Current errors: -0.065%, ~0.00%, -0.315%

Dimensions are inside the L88 <=2.5% numeric gate. The current Blender
validation set also includes a rear-gunner cockpit hero still; that still is a
blockout subject-presence check, not a final-art approval.

## Artifact hashes

```text
18B88B5DFD4CDD9FB44E83F775DC9474C6146F417B455B6BC7605A07CB39E993  1276202  YAK52_L88_MASTER_BLOCKOUT.blend
85F7C3D5164BA1FB9056DD206FF8BE29716C6DB81F152E045DD31EC051E418FB  8721608  yak52_l88_silhouette_blockout.glb
8A8D37611ACFD544B2681DD6C3C3A98123562B8C265F20CE41D4F95C2DF9856C  72840    D:\Skyguard52\Scripts\blender_l88_yak52_blockout.py
DD5C381FC686B8D359D977BDFDFB05BC510E20B402C4CC9CDDB7E919D3180028  854      D:\Skyguard52\Saved\Reports\L88_MARKERS.json
AF99DDC08828AF4EB96805BE05EB647317DD632221A2234C366C051673B15F9C  2823     D:\Skyguard52\Saved\Screenshots\AAA_L88_Blockout\L88_SILHOUETTE_REPORT.json
92FFB0EAD91D7F3A1EE7ED4F9862AE0234D496A7AFE1EF6D39195E7A1E22BB51  5098     D:\Skyguard52\Scripts\audit_l88_import_delta.py
8A0665D81443F43510C09FE70D0B52A3943A10863F6524833E7F81ABE3424FE0  448      D:\Skyguard52\Saved\Reports\L88_BASELINE_PASS14.json
87A0B3A5BFDBBD4DE5623B597B1FF0541305D2F434DE6EC8098A8E4BDFB67EB3  448      D:\Skyguard52\Saved\Reports\L88_BASELINE_PASS15.json
502F83F9A03104F66EB4B09A933FB1C8EF4A1A5B1A6961239E045E1139FE74C1  1444     D:\Skyguard52\Saved\Reports\L88_IMPORT_DELTA_PASS16.json
3947190C7BFDC71B7C1619DF36E61D22D2CC0AAFC60A8C1A7C72FB32B62B8406  449      D:\Skyguard52\Saved\Reports\L88_BASELINE_PASS16.json
8140928A9E101A1B79E697B29B9B0B935A40A85C4C56B4529CDCDA8CF2E4E42E  1460     D:\Skyguard52\Saved\Reports\L88_IMPORT_DELTA_PASS17.json
367E17FF21B206D7695269FC77AB56164EA2E6BAD1E96EAE04D328B24F701327  1506     D:\Skyguard52\Saved\Reports\L88_IMPORT_DELTA_PASS19.json
7675EAE8C884F8EBDB0B6765887B700E369F6698D674EC0721F442CE2BC8697F  1487     D:\Skyguard52\Saved\Reports\L88_IMPORT_DELTA_PASS20.json
6B30213F44009CA48578D8908389311D3F19E07F15336D132BBD2E400E15B711  1433     D:\Skyguard52\Saved\Reports\L88_IMPORT_DELTA_PASS21.json
ACE3065A939D816D109C07672E68F3F2D113EBACAC1E155F3F62E9E26476D94F  1499     D:\Skyguard52\Saved\Reports\L88_IMPORT_DELTA_PASS22.json
```

Regeneration changes these hashes and requires the manifest to be refreshed.

## Pass14 readiness slice

Pass14 preserves the dimension envelope and the 160/160 Unreal import gate while
adding deterministic `UV_L88_0` coverage and semantic material-family metadata
to all 160 hero meshes. The Blender source also carries exactly three
non-render socket markers (`SO_RearWeaponMount`, `SO_ADSEye`, `SO_RearEye`),
recorded in `Saved/Reports/L88_MARKERS.json`. The GLB grew to 6,041,948 bytes
because the UV channel is now serialized. This is import/readiness evidence
only; it is not approval of production topology, baked PBR, or AAA promotion.

## Pass15 canopy/fairing slice

Pass15 replaces the rectangular bow/rail cage with two continuous curved bows,
keeps the rear sliding shell stowed, and replaces both spherical wing-root
fillets with tapered lofted fairings. Eight small sill/root fasteners preserve
the 160-mesh import contract without restoring the old cage silhouette. The
envelope remains 7.6750 x 9.3000 x 2.6915 m; the read-only pass14-to-pass15
delta gate is `PASS` in `Saved/Reports/L88_IMPORT_DELTA_PASS15.json`.
This remains a candidate blockout improvement, not final topology, baked PBR,
collision/LOD, gameplay, or AAA acceptance.

## Pass16b cockpit/ADS correction slice

Pass16b keeps the same dimension and 160/160 import contract while lowering and
reshaping the stowed shell, smoothing the continuous canopy sections and wing-root
fairings, narrowing the bows, and moving the rear-gunner sight picture onto the
camera centerline. The read-only pass15-to-pass16 delta gate is `PASS` in
`Saved/Reports/L88_IMPORT_DELTA_PASS16.json`; `RearGunnerADS_FINAL.png` is now
centered as a gameplay-readability check. Independent visual review is still
required before any AAA promotion, and the asset remains a blockout candidate
without baked PBR, collision/LOD, or final topology approval.

## Pass17d rear-gunner hand/sleeve slice

Pass17d keeps the 160-mesh and envelope contract while replacing the glove palm
and four finger/thumb spheres with a tapered ring-built palm and bent
capsule-like finger rods. The flight sleeve stops at the wrist and uses a muted
olive fabric value so the dark leather hand reads separately in the weapon hero
still. The read-only pass16b-to-pass17d delta gate is `PASS` in
`Saved/Reports/L88_IMPORT_DELTA_PASS17.json`; Unreal import/audit remains
160/160 with no forbidden labels. This improves hand readability but is still
procedural blockout geometry, not a production hand rig, baked leather PBR, or
AAA acceptance.

## Pass19 propeller and landing-gear topology slice

Pass19 replaces the full-span rectangular propeller slab with a tapered,
pitched two-blade mesh and replaces the three box struts with smooth tapered
oleo meshes. The prop origin is authored on the +X shaft axis and each oleo
origin is authored at its airframe attachment point, allowing Unreal animation
without runtime pivot compensation. The envelope remains
7.6750 x 9.3000 x 2.6915 m, Blender and Unreal remain at 160/160 meshes, and the
read-only import delta is `PASS` in
`Saved/Reports/L88_IMPORT_DELTA_PASS19.json`. This is a topology/readability
improvement, not final gear engineering, baked PBR, LOD, collision, or AAA
acceptance.

## Pass22 pilot, rear soldier, and detachable weapon states

Pass22 corrects the gameplay composition using the supplied Yak-52 reference:
a dedicated pilot occupies the front seat and a separate rear soldier occupies
the rear station. The soldier physically shoulders and grips the rifle; the
three former meshes that implied a fixed cockpit mount (`GEO_GunnerRifleMount`,
`GEO_GunnerPivotRing`, and `GEO_GunnerAmmoBox`) are removed. An eight-part Igla
assembly is stowed on the starboard rear side as an alternate weapon state, not
simultaneously posed in the soldier's hands. The pass adds 24 crew/Igla meshes
and removes three fixed-mount meshes for a net +21, bringing the dimension-
locked candidate to exactly 240 UV-complete meshes. Unreal imports 240/240,
all 24 crew/Igla names are present, none of the three removed mount names are
present, and `Saved/Reports/L88_IMPORT_DELTA_PASS22.json` is `PASS` at
cumulative Pass16-relative `expected_mesh_delta` 80. Crew geometry remains
blocking for later skeletal replacements; it is not a final character rig or
animation acceptance.

## Pass20 rear-cockpit controls and hardware kit

Pass20 intentionally adds 20 named meshes for a rear throttle quadrant and
hinged lever, trim wheel, six-switch bank, radio/intercom box and knobs,
canopy latches, harness buckle, port/starboard wiring, and map light. The
throttle lever origin is authored at its hinge for later Unreal animation.
The candidate expands from 160 to exactly 180 meshes while preserving the
7.6750 x 9.3000 x 2.6915 m envelope, all three gameplay markers, and full
`UV_L88_0` coverage. Unreal imports 180/180 assets with no forbidden labels,
and `Saved/Reports/L88_IMPORT_DELTA_PASS20.json` is `PASS` with an explicitly
authorized `expected_mesh_delta` of 20. This is a cockpit-context improvement,
not final instrument typography, quilted sidewall upholstery, baked PBR,
interaction logic, LOD/collision, or AAA acceptance.

## Pass21 ten-subsystem asset wave

Pass21 adds exactly 39 stable, semantically named meshes across the ten planned
subsystems: rear sidewalls, instrument-panel hardware, sliding-canopy hardware,
seat/restraint hardware, rifle furniture, first-person glove details, fuselage
skin/service detail, wing/tail hinges, radial-engine plumbing, and complete
main/nose-gear fork and door assemblies. Canopy-lock and gear-door origins are
authored at their intended hinges for later Unreal animation. The candidate
expands from 180 to exactly 219 meshes while preserving the
7.6750 x 9.3000 x 2.6915 m envelope, all three gameplay markers, and complete
`UV_L88_0` coverage. Unreal imports and places 219/219 assets; all 39 Pass21
names are present and `Saved/Reports/L88_IMPORT_DELTA_PASS21.json` is `PASS`
with cumulative `expected_mesh_delta` 59 relative to the frozen Pass16
baseline. This is a production-candidate structure pass, not final sculpted
topology, baked PBR, LOD/collision, rigging, performance approval, or Opus 5
acceptance.
