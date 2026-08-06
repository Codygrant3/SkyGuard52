# BLD-M01-YAK-UPLIFT-003-R3 Visual Review

Disposition: `ACCEPTED_FOR_UNREAL_IMPORT_EVALUATION`

This disposition authorizes only a quarantined Unreal import evaluation of
individually governed uplift components. It is not a whole-aircraft runtime
replacement, visual promotion, production acceptance, or AAA claim.

Artifact gate: `PASS`

Reviewed comparisons:

- `Saved/Screenshots/BLD_M01_YAK_UPLIFT_003_R3/UPLIFT003R3_Beauty.png`
- `Saved/Screenshots/BLD_M01_YAK_UPLIFT_003_R3/UPLIFT003R3_SideOrtho.png`
- `Saved/Screenshots/BLD_M01_YAK_UPLIFT_003_R3/UPLIFT003R3_TopOrtho.png`
- `Saved/Screenshots/BLD_M01_YAK_UPLIFT_003_R3/UPLIFT003R3_RearCockpit.png`
- `Saved/Screenshots/BLD_M01_YAK_UPLIFT_003_R3/UPLIFT003R3_RearGunnerEye.png`

## Accepted for evaluation

- L88's more complete cockpit, crew, rifle and Igla staging remains preserved.
- The rear-gunner eye view is no longer the fully occluded/dark failure seen in
  Production 002; the physical rear and front sight relationship is visible.
- Explicit rear-gunner camera, pilot-safety, rifle-muzzle and Igla-backblast
  volumes can now be evaluated against the Unreal gameplay camera and weapon
  traces.
- The 002-derived cowling, radial shutter, propeller, wheel-well and pivot
  donors may be evaluated one component at a time.
- The immutable ledger prevents inherited blockout geometry from silently
  becoming production art.

## Still rejected as visible final art

1. Wing, tail, fuselage and canopy silhouettes remain visibly blockout-grade
   and are not yet reference-faithful Yak-52 production surfaces.
2. Crew anatomy, hands, gloves, sleeves and weapon grips remain simplified and
   need rigged production replacements.
3. Rifle and Igla geometry, sights, controls and material response remain
   insufficient for first-person hero use.
4. The cockpit lacks production instrument, trim, harness, padding, fastener,
   label, wiring and wear detail.
5. Exterior materials lack calibrated paint, bare metal, glass, rubber,
   weathering, livery, panel, seam and rivet treatment.
6. No component has yet passed Unreal scale, socket, collision, ADS, pilot
   safety, Igla launch-axis, animation, Nanite/LOD, material or packaged
   performance validation.

## Quarantined Unreal evaluation rule

Import the R3 candidate into a new evaluation-only path. Do not replace the
current runtime Yak. Evaluate camera and safety volumes first, then cowl,
propeller, wheel-well and pivot donors individually. Each accepted donor must
retain its ledger identity and produce a matched before/after screenshot plus
ADS, rifle-fire, Igla-launch, pilot-safety and frame-time evidence.

Any visible airframe, cockpit, crew or weapon component that remains
blockout-grade must stay provisional and be replaced in a later versioned
production source.
