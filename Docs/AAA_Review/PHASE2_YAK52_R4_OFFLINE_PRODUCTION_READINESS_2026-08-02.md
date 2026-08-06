# Phase 2 Yak-52 R4 offline production readiness

## Outcome

The next Yak-52 art pass is now defined as a bounded, fail-closed R4 production
program rather than another whole-aircraft procedural replacement.

- Contract:
  `Docs/AAA_Review/PHASE2_YAK52_R4_OFFLINE_PRODUCTION_CONTRACT.json`
- Verifier:
  `Scripts/verify_phase2_yak52_r4_offline_production_contract.py`
- Mutation tests:
  `Scripts/tests/test_phase2_yak52_r4_offline_production_contract.py`
- Offline runner:
  `Scripts/run_phase2_yak52_r4_offline_production_gate.ps1`

This work does not create the R4 Blender source, launch Blender or Unreal,
modify accepted assets, import media, promote donors, replace the runtime Yak,
or establish final, AAA, production-ready, or shipping acceptance.

## Evidence-derived boundary

R3 remains useful but provisional:

- 240 governed component identities;
- 232 exact-object requirements;
- 8 source-absent holds;
- 155 provisional inherited parts;
- 26 rebuild candidates;
- 6 donor-classified inherited parts;
- 45 holds;
- 8 source-absent holds.

The ten quarantined R3 donor meshes have useful automated compatibility
evidence:

- exact assets persisted;
- pivots match their governed datums;
- each asset has a material slot;
- each asset has simple collision;
- donor bounds preserve camera, pilot, rifle, and Igla clearance;
- rear-gunner sightline remains level and unobstructed.

That evidence does not prove visual quality, material calibration, motion,
gameplay behavior, performance, packaged persistence, or human promotion. All
ten donors remain unpromoted.

R3 is still rejected as visible final art because the main airframe/canopy
silhouettes remain blockout-grade, crew anatomy and hands are simplified,
weapons are not first-person quality, cockpit detail is sparse, materials lack
calibrated surface language, and no final set has passed complete Unreal
gameplay and performance validation.

## Ordered R4 production slices

1. Reference board, dimensions, and silhouette lock.
2. Production exterior surfaces and control breaks.
3. Cowling, radial face, propeller, and landing-gear integration.
4. Front canopy and opening rear-gunner canopy system.
5. Front and rear cockpit production interiors.
6. Rigged pilot and rear-gunner crew.
7. First-person rifle and Igla interaction set.
8. UV, bake, calibrated PBR, livery, and weathering.
9. Production grouping, pivots, sockets, rigs, and collision.
10. Isolated export, matched visual review, and Unreal performance acceptance.

The final slice depends on all prior slices. No later material or detail pass
may disguise a rejected silhouette.

## Visual acceptance

Thirteen frozen cameras cover:

- port beauty;
- side orthographic;
- top orthographic;
- rear quarter;
- underside orthographic;
- nose/propeller close-up;
- canopy closed;
- canopy open;
- rear cockpit hero;
- rear-gunner eye;
- rear-gunner ADS;
- pilot safety;
- crew port close-up.

Matched renders use 1920×1080 output, the compatible
`BLENDER_EEVEE` engine, fixed neutral lighting/color management, and no
post-render cropping or reframing. Additional daylight, overcast, night, wet,
and storm material reviews supplement but cannot replace the neutral views.

## Production requirements

### Canopy

- Correct front/rear glazing thickness and frames.
- Complete rear bow, rails, rollers, seals, hinges, latches, handles, and rim.
- Pilot remains enclosed while the rear gunner's canopy slides open.
- Closed, transit, open, and stowed states clear crew, weapons, camera, and
  airframe.
- Glass remains optically credible and cockpit-readable.

### Cockpit

- Physical panels, gauges, needles, glass, lamps, placards, switches, guards,
  throttles, trim, sticks, pedals, radios, wiring, padding, seats, harnesses,
  fasteners, and wear.
- Rear-eye visibility is the priority; repeated sub-pixel detail uses atlases,
  trims, decals, and normal detail.

### Crew and weapons

- Rigged pilot, first-person gunner arms/hands, and third-person gunner.
- Maximum 128 bones per skeletal asset and 8 vertex influences.
- Anatomical limbs, individual finger/thumb silhouettes, stable wrists, proper
  seated contact, and no block arms or glove mitts.
- Rifle sights physically align in ADS.
- Rifle muzzle, sight, Igla launch, and Igla backblast axes are explicit.
- Pilot no-fire, canopy sweep, recoil, reload, and Igla shoulder/launch poses
  require clearance evidence.

### Materials

- Maximum 4K authored runtime textures; no 8K exception in this contract.
- 512 px/m exterior/gear/engine targets and 1024 px/m first-person
  cockpit/crew/weapon targets.
- Normal, AO, curvature, thickness, position, and material-ID bakes.
- Calibrated paint, metal, engine, glass, rubber, cockpit, instrument, leather,
  fabric, skin, rifle, Igla, decal, grime, oil, soot, salt, and wetness
  families.

### Collision and gameplay interfaces

- No complex-as-simple collision.
- Maximum 40 simple primitives and 24 physics bodies.
- Cosmetic microdetail never participates in gameplay collision.
- Dedicated camera, pilot, rifle, and Igla safety volumes are preserved.
- Required propeller, canopy, control-surface, gear, rifle, Igla, eye, and pilot
  pivots/sockets are named explicitly.

## Performance gate

At the fixed future 2560×1440 High target profile:

- 60 FPS / 16.67 ms frame target;
- maximum 40 runtime render components;
- maximum 500k visible triangles from the rear-gunner view;
- maximum 350k / 160k / 60k exterior triangles at 15 m / 50 m / 150 m;
- maximum 85 rear-view and 70 exterior Yak draw calls;
- maximum 24 material instances;
- maximum 256 MiB resident Yak texture memory;
- maximum 3 visible skeletal assets;
- Yak delta budgets of 1.0 ms game thread, 1.5 ms render thread, and 2.0 ms GPU.

Median and worst one-percent frame times must pass. Downloadable packaging is
not a budget waiver. ADS/fire, canopy, Igla, impact, and destruction soaks must
show no multi-second stalls, and first-use compilation/warm-up hitches must be
reported separately from steady-state performance.

## Current truthful state

- R4 production started: **false**
- R4 Blender source created: **false**
- R4 export created: **false**
- R4 Unreal import: **false**
- R3 donor promotion: **0 of 10**
- Runtime replacement: **false**
- Human visual acceptance: **false**
- Performance acceptance: **false**
- Final / AAA / production-ready / shipping: **false**
