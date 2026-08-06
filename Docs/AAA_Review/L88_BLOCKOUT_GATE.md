# L88 Yak-52 Blockout Gate

Updated: 2026-08-01
Gate scope: primary shape and physical envelope only
Overall AAA status: FAIL / active (blockout and source-import gates passed; AAA promotion remains blocked)

## Result

**PASS — Yak-52 primary-shape blockout gate only.**

The first authored blockout failed visual review because of twin hemispherical
canopies, a tube-like fuselage, an abrupt cowl collar, slab wings, and crude
empennage. Those five faults were corrected and the second harsh review passed.

**PASS — rear-gunner subject-presence sub-gate.**

The rear cockpit hero now contains a readable side-mounted rifle with a
wood-tone stock/receiver, forward barrel, mount, sleeve, and glove silhouette.
An independent harsh review accepted the weapon arc as sufficient to identify
the station as a gunner position rather than a generic cockpit. This remains a
procedural blockout check; the sight/muzzle contrast and final weapon model are
still production work.

## Dimensions

| Axis | Target | Measured | Error |
|---|---:|---:|---:|
| Length | 7.680 m | 7.675 m | -0.07% |
| Span | 9.300 m | 9.300 m | ~0.00% |
| Height | 2.700 m | 2.6915 m | -0.32% |

All axes are within the <=2.5% L88 gate.

## Passing evidence

- `Saved/Screenshots/AAA_L88_Blockout/AAA_Cam_L88_SideOrtho_FINAL.png`
- `Saved/Screenshots/AAA_L88_Blockout/AAA_Cam_L88_FrontOrtho_FINAL.png`
- `Saved/Screenshots/AAA_L88_Blockout/AAA_Cam_L88_TopOrtho_FINAL.png`
- `Saved/Screenshots/AAA_L88_Blockout/AAA_Cam_L88_Beauty_FINAL.png`
- `Saved/Screenshots/AAA_L88_Blockout/AAA_Cam_L88_RearCockpitHero_FINAL.png`
- `Saved/Screenshots/AAA_L88_Blockout/AAA_Cam_L88_RearGunnerWeaponHero_FINAL.png`
- `Saved/Screenshots/AAA_L88_Blockout/L88_SILHOUETTE_REPORT.json`
- `Saved/Reports/L88_VALIDATION_IMPORT.json` (Unreal map import audit)

## Unreal validation import

The isolated `/Game/Skyguard/Maps/Lvl_Yak52_L88_Validation_v2` map imports 219
static-mesh assets and places all 219 aircraft pieces, plus a neutral floor,
three cameras, and three lights. The audit found no `AAA_`, `L52_`, `L86_`,
`L87_`, or `WebGame_` legacy labels. This proves import and map isolation only;
it does not promote the blockout to production art.

## Non-blocking high-poly corrections

The candidate source now uses smooth/weighted normals, radial-engine face
hardware, canopy hinges, fuselage fasteners, and restrained
procedural micro-surface breakup for the Blender proofs. These improve the
candidate read but are not a substitute for authored UVs and baked 4K PBR
sets in the production pass.

1. Shorten/soften the cowl transition and taper sooner behind the radial cowl.
2. Refine outer-wing taper and round the remaining clipped-looking tips.
3. Broaden/smooth the vertical fin, swept leading edge, and crown.
4. Reduce the horizontal tail's slab breadth and round its tips.
5. Bring the main landing gear modestly inboard.
6. Replace the procedural rifle/glove cue with the production rifle and
   physically articulated rear-gunner hand/arm after the Unreal import gate.

## Explicit non-approval

This pass does not approve final topology, cockpit, canopy mechanics, UVs,
materials, textures, LODs, collision, Unreal import, gameplay integration, or
AAA visual promotion.

## Latest high-poly candidate review

The 160-mesh source pass is a **candidate PASS only**, not a final-art
promotion. It materially improves canopy shaping, livery read, wing leading
edges, panel scale cues, navigation markers, and gear hardware. Independent
reviews still reject AAA promotion for these evidence-backed blockers:

- the open rail cage dominates the rear station and occludes the seated eye
  point; it needs a finished bubble/fairing, seals, thickness, and clean sightline;
- the wing edge strip is an add-on and the airfoil, tips, and control-surface
  hinges remain slab-like;
- the gray procedural material still lacks a panel-value hierarchy, authored
  paint wear, decals, and distinct metal/fabric/leather treatment;
- seam rings and fasteners remain shallow graphic cues rather than recessed
  overlapping skins and access panels;
- gear, wheel, brake, oleo, doors, and contact detail remain primitive;
- the rear weapon view is readable as a station, but rails occlude the rifle
  and the glove/hand contact is not clear from the seated eye point;
- the overall barrel fuselage and flat tail still read generic rather than a
  reference-accurate Yak-52.

## Pass13 cockpit/ADS review

The pass13 candidate earns a **conditional PASS for the procedural blockout
sub-gate only**: the port-side `RearCockpitHero` now shows the rifle,
forearm/glove cluster, rear aperture, and open station, while
`RearGunnerADS` shows the front post through an unobstructed aperture. The
independent cockpit review still blocks visual promotion because the hero eye
view loses most instrument-panel context, the peripheral rails remain crowded,
the glove is an abstract blockout silhouette, and the ADS proof is isolated
from a target/sweep and gameplay validation. Production topology, UV/PBR,
collision, LODs, and final canopy/fairing remain open.

## Pass14 readiness slice

The pass14 export keeps the numeric envelope and the 160/160 Unreal import gate
green while adding deterministic `UV_L88_0` and semantic family metadata to all
160 hero meshes. The master Blender source carries exactly three non-render
markers (`SO_RearWeaponMount`, `SO_ADSEye`, `SO_RearEye`), recorded in
`Saved/Reports/L88_MARKERS.json`. The GLB is 6,041,948 bytes after serializing
the UV channel. This is a readiness result only; it does not approve final
topology, baked PBR, collision, LODs, or AAA visual promotion.

The read-only pass13-to-pass14 contract also passes: mesh/actor counts and the
measured envelope are unchanged, forbidden labels remain empty, the imported
GLB hash matches the Unreal audit, all 160 meshes carry `UV_L88_0`, and the
three expected non-render socket markers are present. Evidence is in
`Saved/Reports/L88_IMPORT_DELTA_PASS14.json` and the script/hash record in
`Content/Skyguard/Meshes/Source/L88/REFERENCE_NOTES.md`.

## Pass15 canopy/fairing candidate

Pass15 replaces the rectangular canopy bow/rail cage with two continuous curved
bows, retains the open rear station with its sliding shell stowed, and replaces
the two detached wing-root UV-sphere pods with tapered lofted fairings. The
dimension envelope remains 7.6750 x 9.3000 x 2.6915 m; Blender and Unreal both
report 160 meshes, and the import audit remains `PASS` with no forbidden
labels. The read-only pass14-to-pass15 delta is recorded in
`Saved/Reports/L88_IMPORT_DELTA_PASS15.json`.

This is still a **candidate PASS only**. The visual critic must confirm that
the canopy reads as a real Yak-52 frame and that the fairings no longer read as
pods before this slice can move toward production art.

## Pass16b cockpit/ADS correction

Pass16b is a bounded correction slice, not an AAA promotion. The continuous
canopy sections and wing-root fairings were smoothed, the stowed shell was
lowered, the canopy bows were narrowed, and the rear-gunner ADS camera/sight
picture was brought onto the camera centerline. Blender remains at
160/160 hero meshes and 7.6750 x 9.3000 x 2.6915 m; the isolated Unreal audit
remains `PASS` at 160/160 with no forbidden labels. The read-only pass15-to-
pass16 contract is recorded in `Saved/Reports/L88_IMPORT_DELTA_PASS16.json`.

Local still review confirms the ADS alignment is materially improved, but the
asset is still visibly a stylized blockout: the canopy shell/fairings need a
reference-accurate skin and seals, the rear cockpit hero is dominated by the
rail/aperture, and the glove/forearm contact is not yet a convincing human
hand. Keep the overall gate **FAIL/HOLD for AAA** pending a fresh independent
review and a production cockpit/material pass.

## Pass17d rear-gunner hand/sleeve correction

Pass17d keeps the same 160-mesh/envelope/import contract while replacing the
procedural palm and finger spheres with a tapered palm and bent finger/thumb
rods. The sleeve terminates at the wrist and uses a muted olive fabric value so
the dark leather hand separates from the flight suit in the weapon hero still.
The read-only pass16b-to-pass17d contract is `PASS` in
`Saved/Reports/L88_IMPORT_DELTA_PASS17.json`; the Unreal audit is `PASS` at
160/160 with no forbidden labels. This is still a blockout readability gain,
not a production hand rig, leather bake, or AAA acceptance.

## Pass19 propeller and landing-gear correction

Pass19 preserves the 160-mesh and exact exterior-envelope contract while
replacing the old rectangular propeller slab with a tapered/pitched two-blade
mesh and replacing all three box struts with tapered oleo topology. The prop
and strut origins are authored for Unreal animation at the shaft axis and
airframe attachments. Blender export, isolated Unreal reimport, source-hash
match, UV coverage, markers, labels, mesh counts, and envelope checks are all
`PASS` in `Saved/Reports/L88_IMPORT_DELTA_PASS19.json`. The slice remains
validation-ready blockout art rather than final AAA gear/prop art.

## Pass20 rear-cockpit hero controls

Pass20 adds exactly 20 meshes for cockpit context: throttle/trim controls,
switch bank, radio controls, canopy latches, harness buckle, wiring, and a map
light. The throttle is authored with a hinge-correct origin and a dedicated
weapon-free controls camera now proves the installed kit. The dimension
envelope and three gameplay markers are unchanged; Blender and Unreal agree at
180/180 UV-complete meshes with no forbidden labels. The intentional +20 count,
current GLB/import hash, and unchanged envelope are `PASS` in
`Saved/Reports/L88_IMPORT_DELTA_PASS20.json`. This improves cockpit readability
but is not final PBR, typography, upholstery, interaction, collision/LOD, or
AAA promotion.

## Pass21 ten-subsystem candidate structure

Pass21 executes the full ten-item Blender backlog as exactly 39 new meshes:
rear sidewalls, panel details, canopy rollers/lock/handle, lap restraints,
rifle furniture, glove cuff/knuckle detail, fuselage panels/cowl vents,
wing/tail hinges, engine collector/pushrods, and landing-gear forks/doors.
Blender and Unreal agree at 219/219 meshes, all meshes have `UV_L88_0`, the
three gameplay markers remain present, the physical envelope is unchanged, and
the source/import hash matches. The cumulative Pass16-relative count delta is
explicitly authorized as +59 and every check passes in
`Saved/Reports/L88_IMPORT_DELTA_PASS21.json`. The gate remains readiness-only:
production PBR bakes, LOD/Nanite and collision policy, animation/interaction,
performance, independent visual challenge, and Opus 5 acceptance are still
required.

## Pass22 two-seat crew and rear-weapon arrangement

Pass22 establishes the intended gameplay composition from the Yak-52 reference:
one pilot in the front seat and one soldier in the rear. The rear soldier now
shoulders and grips the rifle, while a separate Igla assembly is stowed on the
rear starboard side for later socket-driven weapon swapping. Three meshes that
previously implied a fixed rifle mount are removed. Unreal confirms all 24 new
pilot/soldier/Igla assets, confirms the three fixed-mount assets are absent,
and agrees with Blender at 240/240 UV-complete meshes. Dimensions and gameplay
markers remain unchanged, and the complete contract is `PASS` in
`Saved/Reports/L88_IMPORT_DELTA_PASS22.json`. Final skeletal topology, skinning,
facial/hand detail, animation, weapon-swap logic, and gameplay validation
remain separate production gates.
