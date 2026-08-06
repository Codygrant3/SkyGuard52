# Skyguard 52 Gate 7 Combat-Art Production Backlog

Classification: `AWAITING_GATE6_AND_EXPLICIT_PRODUCTION_AUTHORIZATION`

This backlog covers the shared close-view combat art needed for the first
production Mission 1 vertical slice. It does not claim Gate 7 acceptance and
does not authorize Blender, Unreal, a native build, import, integration,
capture, profiling or packaging.

## What is genuinely complete

- The ten mission integration architecture is an accepted engineering
  baseline.
- The Phase 7 second-pass receipt passed all 39 expected unique automation
  tests for Missions 1 through 10, with no fatal, assert, ensure or GPU-timeout
  signatures.
- Routes, objective placements, skyline families and boss mechanics are
  structurally distinct.
- Rifle/ADS, Igla, input, save/settings and pilot-protection behavior have
  earlier engineering evidence.
- All 15 combat performance bookmark literals exist in source.

Those results prove gameplay structure. They do not prove production art,
animation, packaged combat performance or release quality.

## Current production blockers

1. Yak-52 R5 failed. R6 is still awaiting sufficient reference input, so the
   final cockpit, canopy, seat, camera, protection volume, skeleton and weapon
   socket contract does not exist.
2. Current gunner code prefers retired WebGame rifle, glove, sleeve and Igla
   meshes, then explicit `*_proxy` assets, then engine primitives.
3. Current drone code prefers retired WebGame meshes and selects explicit
   Shahed proxies or primitives.
4. The current Igla missile is an engine cylinder pending a governed Blender
   asset.
5. The current aircraft loads the L88 silhouette blockout root.
6. The Pathfinder Recovery12 visual proof is terminally rejected: clipping was
   roughly 18–40% against a 2% maximum, and the model presented disconnected
   slabs, floating members and featureless overexposure.
7. The combat-performance contract exists, but its execution is blocked. Three
   1080p combat captures, a 20-minute soak and contextual first-use shader/PSO
   evidence are missing.

No asset under `Meshes/WebGame`, `Meshes/Hero`, the L88 blockout root or
`/Engine/BasicShapes` can qualify as Gate 7 production authority.

## Ordered production plan

| Order | Lane | Output | Entry gate | Acceptance gate |
|---:|---|---|---|---|
| 1 | G7.1 Pilot and rear gunner | Production characters, skeleton, harnesses, sockets and seated poses | Accepted Yak R6 cockpit/socket contract | Anatomy, posture, no clipping, pilot protection and canopy-state review |
| 2 | G7.2 Arms, sleeves and gloves | Anatomical first-person limbs, articulated hands, leather gloves and IK | G7.1 skeleton/socket freeze | Hip, ADS, fire and reload views pass with credible contact and no primitive forms |
| 3 | G7.3 Rifle and physical ADS | Production rifle, iron sights, sockets, animation, muzzle/impact/audio | G7.1–G7.2 | RMB ADS + LMB fire, physical sight alignment, no HUD reticle and safe firing arcs |
| 4 | G7.4 Igla and missile | Production launcher/missile, lock states, launch/reload presentation | G7.1–G7.2 | Forward-end launch, correct orientation, lock acquire/decay, safe arcs and no first-use stall |
| 5 | G7.5 Drone families | Standard/heavy Shaheds, damage states, breakup and wrecks | Dimensioned drone reference freeze | Readable silhouettes/damage, pooled breakup, realistic explosions and no stalls |
| 6 | G7.6 Pathfinder boss | Continuous boss silhouette, weak points, phases, destruction and aftermath | G7.5 + accepted M1 environment | No Recovery12 defects, gameplay-aligned weak points and bounded destruction |
| 7 | G7.7 VFX/audio/destruction | Pooled Niagara, realistic spatial audio, budgets and PSO prewarm | G7.3–G7.6 | No placeholder pew explosions, no sight washout, no runtime compilation or allocation spike |
| 8 | G7.8 Packaged combat proof | Fresh package, 3 captures, 20-minute soak and traces | G7.1–G7.7 + accepted M1 environment/Yak | Frozen performance, stability, protection and full-resolution visual rubrics pass |

## Per-lane execution pattern

Every lane follows the same immutable sequence:

1. Freeze a dimensioned, source-cited reference and interface contract.
2. Verify the fresh output namespace is absent and no heavy process is active.
3. Author the Blender source and export contract offline.
4. Request one explicit Blender authorization.
5. Preserve stdout, stderr, PID, actual exit code, manifests, exports, renders
   and hashes.
6. Validate geometry, scale, UVs, materials, sockets, collision and original
   resolution renders.
7. Inspect every governed render directly.
8. If accepted, freeze a separate one-shot Unreal import prompt.
9. Validate imported scale, shading, materials, animation, collision, sockets,
   Asset Registry and dependency closure.
10. Integrate only accepted outputs in a fresh namespace.
11. Capture and profile only after a separate explicit authorization.
12. Classify `PASSED`, `FAILED_WITH_EVIDENCE` or
    `AWAITING_NEXT_EXPLICIT_GATE`; never merely “in progress.”

## AAA visual requirements

- Continuous, proportionally correct close-view silhouettes.
- High-poly/subdivision or equivalent sources with deliberate bevels and
  manufactured transitions.
- Production retopology, Nanite or skeletal topology chosen from measured use.
- Clean UVs and physically calibrated base color, normal and ORM materials.
- Macro and micro detail, seams, fasteners, decals and controlled wear that
  remain credible in daylight, overcast, night, wet and storm conditions.
- Fixed close, grazing and gameplay cameras plus temporal review.
- No floating parts, clipping, overexposure, crushed shadows, unstable LOD,
  camera-coupled motion or proxy read.
- Every third-party final-use dependency has a passing provenance receipt.

## Performance and stability requirements

- No synchronous load, runtime mesh construction, shader compilation or
  unbounded allocation in ADS, fire, impact, damage or breakup paths.
- Effects, audio voices, debris and breakup actors are pooled and prewarmed.
- The existing ADS rifle, Igla, drone breakup, boss destruction and
  weather-fast-camera bookmarks are exercised in the packaged game.
- Three accepted 1920×1080 input-driven combat captures are required.
- One accepted 20-minute input-driven combat soak is required.
- The frozen frame, hitch, GPU, memory, VRAM, shader and stability limits must
  pass.
- A Shipping candidate must repeat the accepted input, combat, save/settings
  and stability gates.

## Next executable gate

Gate 2 remains the next heavy gate:

`D:\Skyguard52\Docs\AAA_Review\NEXT_PROMPT_PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_VALIDATION_RECOVERY01.md`

It is not authorized by this offline Gate 7 audit. Gate 7 production also
remains unauthorized until Gate 6 and the Mission 1 environment prerequisites
pass.
