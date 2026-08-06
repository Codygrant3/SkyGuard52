# Yak-52 R6 Slice01 Offline Readiness

## Classification

`AWAITING_REFERENCE_INPUT`

The R6 offline design package is internally consistent and passes all eight
focused tests. It is not genuinely ready for a one-shot Blender production
attempt because the supplied references do not include a dimensioned top view,
authoritative three-view/station drawing, canopy travel dimensions, or
cowling/propeller installation drawings.

Launching Blender now would repeat the central R5 mistake: converting
plausible photo inference into apparently authoritative geometry.

## Completed offline gates

- Current audit, Phase 8 baseline, R4 baseline, R5 source, both R5 attempts,
  R5 outputs, visual review, acceptance matrix and Recovery12 evidence were
  hash-reverified.
- Four user references were hash-reverified.
- All R6 source, report, render and attempt paths are absent.
- No Unreal, Blender, ShaderCompileWorker or build process was active.
- R5 failures were mapped to specific governed renders and reference images.
- The coordinate system, dimensional tolerances, 13 fuselage stations,
  cowling/radial construction, airfoil/root approach, canopy motion,
  rear-gunner clearance, materials, topology, hierarchy, namespace, eleven
  cameras and acceptance metrics are defined.
- Camera visibility math passes for all ten bounded subject cameras; the
  rear-gunner view has a separate 9 x 9 ray contract.
- Eight focused tests pass.
- No heavy application was launched.

## Unresolved reference uncertainties

1. No dimensioned top view exists to lock wing and tail planforms.
2. No authoritative station drawing confirms the provisional fuselage
   cross-sections.
3. Cowling diameter, depth, radial-face recess and shutter geometry are
   photo-derived.
4. Propeller blade chord, twist and pitch are unverified.
5. Rear-canopy rail travel and overlap are inferred.
6. Rear-gunner seat and eye datums are ergonomic estimates.

These are documented as inferred values and are forbidden from passing final
silhouette acceptance.

## Objective R6 differences from R5

- exact 7.745 ± 0.04 m station span instead of the 7.96 m R5 result;
- station/guide-curve fuselage cage instead of a rotational tube;
- airfoil wing skins and boundary root fillets instead of prisms and ovals;
- layered cowling/radial/propeller assemblies instead of cylinders and bars;
- continuous sill, real-thickness glazing, seals, rails, latches and governed
  rear-canopy travel instead of disconnected bubbles;
- explicit 81-ray rear-gunner proof instead of a visually blocked camera;
- high-to-low bake and calibrated material policy instead of flat diagnostic
  materials;
- eleven cameras with mathematical coverage limits instead of cropped
  close-ups.

## Required reference input

Provide at least:

- a dimensioned Yak-52 top view or authoritative three-view;
- a fuselage station or maintenance drawing;
- a canopy rail/open-position drawing or measured travel;
- a cowling and propeller installation reference.

The most valuable single item is an authoritative dimensioned Yak-52
three-view showing side, top and front.

## Next gate after reference intake

Hash the new references, revise only the explicitly inferred ledgers, rerun all
focused tests, and issue a new readiness/freeze addendum. Only if that addendum
classifies the package as
`PASSED_READY_FOR_EXPLICIT_R6_BLENDER_AUTHORIZATION` should a separate prompt
authorize one Blender attempt.

