# L88 — Yak-52 Hero Asset Replacement

Updated: 2026-08-01
Status: ACTIVE NEXT SLICE
Promotion state: BLOCKED until source/license and silhouette gates pass

## Decision

Replace the current 70 MB `yak52-detail-kit` wholesale. L87 proved its
hierarchy can assemble and light correctly, but the aircraft is dimensionally
and visually not a Yak-52. No current shell, wing, tail, nose, canopy, cockpit,
or marking geometry is approved for the player-visible hero aircraft.

## Reference contract

- Target exterior dimensions: 7.68 m length, 9.30 m span, 2.70 m height
- Unreal target bounds: 768 x 930 x 270 cm
- Unreal coordinate contract: +X forward, +Z up
- Silhouette tolerance: <= 2.5% on length/span/height
- Required landmarks:
  - blunt circular radial-engine cowl
  - compact trainer fuselage
  - broad low wing with correct planform
  - tandem two-seat cockpit/canopy
  - correct vertical/horizontal tail mass
  - tricycle landing-gear placement

Unknown commercial rights, opaque web GLBs, missing native masters, and
unverifiable aircraft variants are automatic rejection conditions.

## Canonical Blender hierarchy

```text
YAK52_L88_ROOT
├─ GEO_Airframe
├─ GEO_EngineCowling
├─ GEO_PropHub
├─ GEO_PropBlade_A
├─ GEO_PropBlade_B
├─ GEO_Gear
├─ GEO_CanopyExterior
├─ GEO_RearCockpitHero
├─ GEO_RearCockpitGlass
├─ COL_Airframe_*
├─ SO_PropAxis
├─ SO_RearGunnerSeat
├─ SO_RearEye
├─ SO_RearWeaponMount
├─ SO_FrontSeat
└─ SO_LandingGear_L / R / N
```

The exterior and rear cockpit are separate hero assets under one normalized
root. The rifle, hands, and ADS components remain a detachable gameplay overlay.

## Smallest shippable vertical slice

1. Dimensionally accurate, material-complete exterior with radial cowl/prop,
   fuselage, wings, tail, visual gear, and canopy.
2. Rear first-person cockpit shell containing the rim, rear seat/harness,
   side consoles, footwell, stick, instrument panel, cables, fasteners, canopy
   rails, and painted-metal/leather/fabric material separation.
3. One `BP_Yak52_L88` hierarchy with correct sockets, prop binding, LODs,
   simple collision, and rear-seat player mount.
 4. A new `Lvl_Yak52_L88_Validation_v2` map containing no L52 boards, legacy proxy
   art, city, harbor, ocean, or combat clutter.

## Art and technical budgets

| Asset | LOD0 target | LOD1 | LOD2 | LOD3 |
|---|---:|---:|---:|---:|
| Exterior opaque | 150–220k tris | 45–55% | 15–25% | 6–10% |
| Rear cockpit hero | 90–140k tris | 50% | 20% | 8% |
| Prop / gear / glass | authored hero | 50% | 20% | 8–10% |

- Exterior: up to four authored 4K BaseColor/Normal/ORM sets
- Rear cockpit: up to two dedicated authored 4K sets
- Semantic material slots only; no generated `production-*` material sprawl
- Nanite for compatible opaque static detail; conventional meshes for glass,
  prop, animated, or masked pieces
- 6–10 simple convex airframe collision hulls; no per-poly simulation
- Hero hierarchy does not simulate physics in this slice

## Gates

1. **Source/license:** native `.blend` or clean editable FBX, commercial game
   rights, retained receipt/license, source SHA-256.
2. **Silhouette:** side/front/rear orthographic overlays within 2.5%; radial
   cowl, canopy, wing, tail, and gear landmarks correct before detail work.
3. **Rear cockpit:** `SO_RearEye` capture visibly includes the cockpit rim,
    instrument panel, seat-side structure, and clear weapon arc. The current
    procedural blockout passes this subject-presence sub-gate with a visible
    side-mounted rifle, mount, sleeve, and glove.
4. **Source hygiene:** applied transforms, scale 1/1/1, correct normals, no
   non-manifold hero geometry, no hidden rejected-source objects, no missing
   maps or duplicate material slots.
5. **Unreal import:** one Blueprint parent, correct axes/sockets/materials,
   proxy fallbacks removed, prop spins about `SO_PropAxis`.
6. **Interaction:** rear-seat mount, camera sweep, ADS, shot trace, self-hit
   prevention, and canopy/airframe collision all pass.
7. **Visual:** beauty, rear cockpit, and ADS are immediately recognizable at
   thumbnail size and pass a harsh reference comparison.

## Deferred

Forward-cockpit heroization, animated landing gear, full flight model,
destruction breakup, alternate liveries, city/ocean/harbor rebuild, and broad
combat VFX remain deferred until this aircraft gate passes.

## Panel receipts

- Terra architecture: completed; wholesale replacement and separate cockpit
  hero shell recommended.
- Harsh visual critic: completed; source not salvageable.
- Grok 4.5 challenger: not counted; OAuth proxy returned HTTP 402/502.
- Sol escalation: skipped because completed reviewers do not conflict.
- Opus 5 acceptance: deferred until a candidate source passes L88 gates.

## Current implementation evidence

- Script: `Scripts/blender_l88_yak52_blockout.py`
- Export: `Content/Skyguard/Meshes/Source/L88/yak52_l88_silhouette_blockout.glb`
- Renders: `Saved/Screenshots/AAA_L88_Blockout`
- Measured dimensions: 7.6750 m length, 9.3000 m span, 2.6915 m height
- Error vs contract: -0.065%, ~0.00%, -0.315%
- Numeric dimension gate: **PASS**
- Visual silhouette gate: **PASS after one reject/rebuild loop**
- Rear-gunner subject-presence gate: **PASS after rifle-cue revision**
- Unreal validation import: **PASS** — isolated v2 map contains 240 imported
  aircraft meshes, three cameras, three lights, and no legacy labels.
- Unreal import audit: `Saved/Reports/L88_VALIDATION_IMPORT.json`
- Current synchronized source/import hash:
  `85f7c3d5164ba1fb9056dd206ff8be29716c6db81f152e045dd31ec051e418fb`
- Current read-only import delta:
  `Saved/Reports/L88_IMPORT_DELTA_PASS22.json` — **PASS**
- Current candidate inventory: 240 meshes, including the complete 39-mesh
  Pass21 wave across all ten requested rear-cockpit, weapon, exterior, engine,
  control-surface, and landing-gear subsystems.
- Crew arrangement: dedicated front pilot plus rear soldier holding the rifle;
  an eight-part Igla is stowed as an alternate rear-station weapon state. The
  three former fixed-rifle-mount implication meshes are absent.
- Source shading/detail pass: **PASS for candidate review** — weighted normals,
  restrained micro-surface breakup, radial-engine face hardware, canopy hinges,
  and fuselage fasteners are now authored on the Blender source; baked 4K
  texture sets remain required for production promotion.
- Gate report: `Docs/AAA_Review/L88_BLOCKOUT_GATE.md`
- Blockout remains unapproved as final art and must not be imported as the
  production hero.
