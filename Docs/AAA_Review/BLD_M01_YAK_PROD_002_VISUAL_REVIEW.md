# BLD-M01-YAK-PROD-002 Visual Review

Status: `REJECTED_AS_FULL_L88_REPLACEMENT`

The source and artifact gates pass. The candidate is a useful governed
construction study, but it is not visually acceptable as the new runtime
aircraft.

Review images:

- `Saved/Screenshots/BLD_M01_YAK_PROD_002/yak52_three_quarter.png`
- `Saved/Screenshots/BLD_M01_YAK_PROD_002/yak52_side.png`
- `Saved/Screenshots/BLD_M01_YAK_PROD_002/yak52_top.png`
- `Saved/Screenshots/BLD_M01_YAK_PROD_002/yak52_underside.png`
- `Saved/Screenshots/BLD_M01_YAK_PROD_002/yak52_rear_cockpit_oblique.png`
- `Saved/Screenshots/BLD_M01_YAK_PROD_002/yak52_rear_gunner_eye.png`

## Improvements over 001

- Radial inlet face and shutters are visible.
- Propeller blades, spinner, wheels, struts and wells now exist as separated
  parts.
- Fuselage taper, cockpit sidewalls, controls, seats, canopy rails and movable
  metadata are materially more complete.
- UV, material, dimension, pivot, socket and file-integrity contracts pass.

## Blocking findings

1. The airframe remains a generic procedural approximation rather than a
   reference-faithful Yak-52 silhouette.
2. Tail, rudder, wing planform, wing-root fairings, gear stance and canopy
   proportions remain visibly inaccurate or underdeveloped.
3. Surface language is not production-ready: no convincing fasteners, access
   panels, rivet rows, seams, national markings, weathering or calibrated PBR.
4. The rear cockpit is still sparse and box-driven compared with the existing
   L88 cockpit bundle.
5. The exact rear-gunner-eye render is occluded/dark, so camera clearance and
   first-person visibility fail manual review.
6. The existing L88 build already preserves more cockpit, crew, rifle, Igla,
   airframe-detail and presentation work. Replacing it wholesale with 002
   would regress visible scope.

## Production direction

Do not import 002 as a replacement for L88.

Use L88 as the preserved working baseline in a new, isolated production uplift
branch. Track every inherited component as `provisional_inherited`, then
replace or refine it component by component. Use 002 only as a donor reference
for contract ideas and for individually reviewed parts such as cowling
shutters, propeller construction, gear pivots, wheel wells and cockpit
metadata. The original L88 and both 001/002 candidates remain immutable.

The next source contract must:

- open or copy L88 only into a new output namespace;
- produce an inherited/rebuilt/accepted component ledger;
- forbid silent promotion of inherited blockout parts;
- correct the rear-gunner camera and weapon-clearance volumes first;
- preserve cockpit, crew, rifle and Igla work while replacing the airframe,
  gear and canopy pieces in bounded stages;
- require matched visual comparisons before any Unreal runtime replacement.
