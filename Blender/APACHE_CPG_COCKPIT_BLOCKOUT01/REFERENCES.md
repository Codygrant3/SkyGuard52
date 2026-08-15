# AH-64 CPG cockpit — public reference notes

Built 2026-08-14 for Skyguard first-person gunner view.

This is a **public-layout blockout**, not a classified reproduction.
No switch labels, no proprietary bezel art, no unpublished dimensions.

## What is public and used

| Fact | Source |
| --- | --- |
| Tandem crew. Pilot in the **rear** seat. Co-pilot/gunner (CPG) in the **front**. | U.S. Army, AH-64E article, 2014 |
| CPG uses TADS imagery; TADS can be slaved to helmet look. ORT/DVO removed on later D models and replaced by a third MPD. | Wikipedia, TADS/PNVS |
| TEDAC is the modern CPG sight display: **5" × 5"** AMLCD replacing the Optical Relay Tube, with left/right handgrips. | Lockheed Martin TEDAC product page |
| Both crew stations fly the aircraft (HOCAS: cyclic + collective). CPG is the primary TADS / missile designator. | Army + public DCS/quick-start overviews (layout only) |

## CPG station — side photo (user-supplied 2026-08-14)

Public hangar photo of a front-seater at the TEDAC (Alamy G9N5DH). Layout only.
Do not copy the photograph, watermarks, faces, or any readable switch labels.

Visible public layout from the gunner's left/aft-left:

1. Armored seat and harness **behind** the CPG. Never in front of the eye.
2. Square **TEDAC** is the hero: dark bezel, green TADS picture, center reticle.
3. **Left and right TEDAC handgrips** — the CPG works the sensor with both hands.
4. **Right side console** drops beside the right thigh (button slab, no labels).
5. Greenhouse canopy frames the world above the dash. Not a closed cabin.
6. The gunner looks *over* the TEDAC at the world, or *into* TEDAC for the sensor.

## CPG Play view — runway through the greenhouse (user-supplied)

First-person, not through the sight. This is the composition to match in Play.

| Band | What belongs there |
| --- | --- |
| Upper ~45% | World (runway/coast) through the greenhouse. Top canopy bow. |
| Left / right | Thick canopy frames. |
| Center-lower | Hooded **TEDAC** between the knees: black box, circular optic on top, green face. |
| Flanks | Green **MPDs**. |
| Bottom | Gunner knees / legs. Seat stays behind. |

TEDAC sits *between the knees* and *below the horizon*. Never a bar across the world.

## Sight picture (Grok Imagine concept, user-supplied)

Looking *through* the targeting device, not over the greenhouse.

- World fills a framed window. Green overlay: weapon, range, crosshair, heading.
- No 3D TEDAC box in this mode. Hold **RMB** (ADS). **T** is thermal on that sight.
- Concept art only. Not a classified TADS format.

## TEDAC unit (Jessica Ament render, user-supplied)

Public 3D study of the **TEDAC box + left/right handgrips**. Shape only.

- Square ~5×5 display, dark face, thick bezel.
- Chunky pistol grips on the left and right of the box.
- Face shows a monochrome sensor picture, a heading tape, a target gate, and range.
- Do **not** copy TAD/FCR/PNV/G/S, LMC, CAGE, or any switch labels.

## CPG unsighted greenhouse (user-supplied 2026-08-14)

First-person gunner view **not** through the sight. Public game screenshot used for composition only.

| Band | What belongs there |
| --- | --- |
| Upper ~55% | World through the greenhouse. Thin heading tape. No cabin. |
| Left / right edges | Thick canopy frames only. |
| Lower center | Hooded **TEDAC** (black shade, dark optic, green symbology). |
| Lower left / right | Green **MPD** faces. |
| Bottom | TEDAC handgrips. Seat never in front of the eye. |

Look *over* TEDAC at the world. TEDAC is a sensor box, not a lime bar.

## CPG station — left/aft hangar photo (Gary Stedman, user-supplied)

Layout only. Do not copy labels, "DO NOT GRAB", or switch engravings.

| Piece | Where it sits |
| --- | --- |
| TEDAC | Center, hooded, on a stalk, **two chunky handgrips**. |
| Left MPD | Smaller, a bit higher than TEDAC. |
| Right MPD | Larger square with a thick bezel. |
| Cyclic | Separate stick, low, between the knees / left of TEDAC. |
| Right console | Knob slab by the right thigh. |
| Greenhouse | Glass above the dash. Seat behind the eye. |

Everything is matte black housings and green faces.

## First-person composition we are building

From the CPG eye, looking forward:

1. Narrow greenhouse canopy rails left/right (high visibility, not a fighter HUD bubble).
2. Center-right **TEDAC** square (green sensor picture + reticle).
3. TEDAC **handgrips** left and right of the screen.
4. **MPD** rectangles as secondary tapes (weapon / threat).
5. Thin **EUFD**-style strip above TEDAC.
6. Right **side console**. Cyclic implied at the grip, collective off-frame left.
7. Armored seat stays behind the eye.

## Units

Blender meters. Eye empty at origin-relative `(0, 0, 1.18)`. Forward `+X` to match Unreal.

## External airframe — public parts only

HowStuffWorks AH-64 diagram (2002, user-supplied 2026-08-14). Unclassified external labels:

| Part | How we use it |
| --- | --- |
| Gunner (front seat) | Live CPG. Player sits here. |
| Pilot (rear seat) | AI / player collective. Aft of the CPG. |
| Pilot's Night Vision | Small nose turret (PNVS). Public shape only. |
| Gunner's Sensor Turret | TADS ball under the nose. Feeds TEDAC. |
| M230 30mm Automatic Cannon | Chin gun. Station `1`. HUD tape `M230`. |
| Landing Gear | Tricycle proxy. |
| Hellfire Missiles | Inboard pylon rails. Station `3`. HUD tape `HLF`. |
| Hydra Rocket Launcher | Outboard pods. Station `2`. HUD tape `HYDRA`. |
| Pylons / Wings | Stub wings. Stores hang from here. |
| Twin Turboshaft Engines | Aft of the stub wings. |
| Main Rotor / Tail Rotor | Spinning silhouette. |
| Radar Dome | Mast-mounted Longbow-style dome. Public shape only. |

Do **not** invent classified internals, switch labels, or unpublished dimensions.

## Exterior side — CPG, TADS, M230 (user-supplied)

Side of the front seat in flight. Public silhouette only.

- Front greenhouse, crew in the CPG. "DO NOT GRAB" is a stencil, not a feature we copy.
- **TADS** ball under the nose, just forward of the CPG, with a lens snout.
- **M230** hangs well below the chin, receiver + barrel.
- Dark olive-drab airframe, side exhaust, landing gear.

## Not in this pass

- Accepted hero airframe (this is still a proxy silhouette)
- Classified panel engravings
