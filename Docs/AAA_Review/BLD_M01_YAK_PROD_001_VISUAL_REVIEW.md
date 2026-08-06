# BLD-M01-YAK-PROD-001 Visual Review

Status: `REJECTED_FOR_UNREAL_PROMOTION`

The governed source and artifact verifiers pass. That proves file integrity,
dimensions, naming, separation, UV presence, materials, sockets and minimum
topology. It does not prove Yak-52 likeness or AAA visual quality.

Review images:

- `Saved/Screenshots/BLD_M01_YAK_PROD_001/yak52_three_quarter.png`
- `Saved/Screenshots/BLD_M01_YAK_PROD_001/yak52_side.png`
- `Saved/Screenshots/BLD_M01_YAK_PROD_001/yak52_rear_cockpit.png`

## Rejection findings

1. The fuselage reads as a generic smooth capsule rather than a Yak-52. The
   upper spine, rear taper, wing-root fairings and lower fuselage transitions
   require reference-driven profiles.
2. The radial-engine cowling is an oversized plain cylinder. It lacks the
   intake face, radial-engine depth cues, cowl-panel breaks, exhaust outlets,
   fasteners and a believable spinner/hub transition.
3. The two propeller blades are visually underdeveloped and nearly disappear
   in side view. Blade twist, chord taper, hub hardware and a governed rotation
   pivot are required.
4. Main and nose landing gear, wheels, struts, doors, wheel wells and brake
   details are absent.
5. The vertical tail and rudder silhouette are too angular and do not match
   the Yak-52 reference profile. Tailplane roots and control-surface gaps also
   read as intersecting slabs.
6. Wing roots, flaps and ailerons do not yet have production junctions,
   thickness transitions, hinge gaps or convincing trailing edges.
7. Canopy glass and bows exist but the rails, forward/rear sections and
   fuselage opening do not form a convincing pressure canopy. The rear opening
   state is not visually demonstrated.
8. The rear cockpit is not reviewable as a gunner station. The close view is
   dominated by glass and rails, while the seat, panel, sidewalls, stick,
   throttle and pedals read as sparse rounded boxes.
9. No production surface language is visible: panel lines, rivet rows,
   fasteners, inspection covers, paint masks, national markings, wear zones
   and decal-ready material IDs are missing.
10. The model has no visual evidence yet for first-person weapon clearances,
    canopy collision/safety arcs, pilot/gunner body fit, or ADS/Igla poses.

## Requirements for BLD-M01-YAK-PROD-002

- Preserve the dimension, coordinate, socket and L88 non-import contracts.
- Add reference-driven fuselage, cowl, tail, wing-root and canopy profiles.
- Add complete separated landing gear and wheel-well assemblies.
- Replace primitive propeller geometry with a twisted tapered two-blade unit
  and mechanically credible hub.
- Rebuild rear-cockpit visible geometry around the rear-gunner eye position.
- Provide separate movable surfaces with correct hinge/slide pivots.
- Provide panel/rivet/decal-ready material IDs and UV strategy.
- Render exterior three-quarter, side, top, underside and rear-gunner-eye
  review views before any Unreal import.

BLD-M01-YAK-PROD-001 remains an immutable source-pipeline proof and must not
replace the accepted runtime Yak assets.
