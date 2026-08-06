# Skyguard 52 — Ten-Mission Blender Asset, Boss and AAA Art Plan

Updated: 2026-08-01  
Target pipeline: Blender 5.2 → Unreal Engine 5.8  
Runtime authority: Unreal Engine only  
Status: Mission 1 vertical-slice execution in progress; refined geometry,
gameplay and PBR gates green, Unreal material/environment runtime gates prepared

## Goal

Build ten visually distinct, believable Ukrainian coastal-defense missions
without creating ten unrelated asset libraries. Approximately 65–70% of the
environment vocabulary should come from shared modular kits. Each mission must
then add a unique skyline, route profile, landmark family, moving objective,
boss encounter, and hero set pieces so that it cannot be mistaken for another
mission in a blind gameplay screenshot or playtest.

The former browser campaign definitions are used only as mission-design canon:

`C:\Users\chris\OneDrive\Documents\Shoot down the drones\src\campaign.ts`

No browser geometry, Three.js runtime code, or legacy web map is an input to
the new production build.

## Current truth

- The new L88 Yak-52 candidate exists in native Blender and imports into Unreal.
- The isolated L88 validation map passes at 240/240 meshes.
- The main world currently has one coastal map and mostly proxy hero meshes.
- Only three Unreal maps currently exist; there are not yet ten production
  mission maps.
- Existing `*_proxy` assets are reference/blockout placeholders, not approved
  production art.

## Production architecture

### Shared asset library

Build these once and reuse them across missions through instancing, material
variants, decals, damage states, and HLOD:

1. **Coastal terrain kit**
   - sand beach segments, dunes, rock shelves, cliffs, seawalls, breakwaters
   - shoreline transitions, drainage outlets, concrete revetments
   - road-to-beach and city-to-shore transition meshes
2. **Road and infrastructure kit**
   - highway, boulevard, local road, bridge, tunnel, rail, sidewalks
   - barriers, guardrails, utility poles, signs, lighting, power lines
3. **Urban modular kit**
   - low-rise residential, Soviet-era apartment, modern midrise, civic,
     industrial, damaged and abandoned variants
   - modular walls, corners, roofs, balconies, windows, storefronts, entrances
4. **Port and industrial kit**
   - pier sections, quay walls, warehouses, tanks, pipe racks, gantries,
     container stacks, cranes and dock furniture
5. **Vehicle and traffic kit**
   - civilian cars, buses, trucks, ambulances, fuelers, relief vehicles,
     forklifts and trailers
6. **Maritime kit**
   - fishing boats, tug, workboat, ferry, cargo ship, patrol/rescue craft,
     life rafts and navigation buoys
7. **Airfield kit**
   - runway/taxiway modules, lights, hangars, shelters, ground-support
     equipment, parked aircraft and revetments
8. **Military and emergency kit**
   - radar vehicles, searchlights, AA positions, checkpoints, sandbags,
     emergency staging, fire/rescue equipment
9. **Vegetation and debris kit**
   - coastal trees, scrub, grass clusters, wind-shaped vegetation, rubble,
     broken masonry, wreckage and litter
10. **Combat target kit**
    - Shahed standard/heavy variants, detachable damage pieces, engine and
      control-surface internals, debris and collision proxies
11. **Shared boss kit**
    - reusable engine, sensor, antenna, jammer, decoy, armor-panel, actuator,
      payload-bay and control-surface weak-point families
    - common skeletal/control rig, damage-state conventions, heat-lock sockets,
      attack telegraph parts and bounded breakup/debris components
    - common rifle-hit, Igla-hit, smoke, fire and disabled-flight material
      states, authored once and specialized per boss

### Mission-exclusive rule

Every level must have:

- one unique macro landform or route profile;
- one unique skyline silhouette;
- one unique moving or defended objective;
- at least three mission-exclusive hero assets;
- one unique boss silhouette and combat behavior;
- at least three boss-specific destructible components or weak points;
- a rifle interaction, an Igla lock-window interaction and an emergency
  rifle-only completion route;
- at least two unique close/mid-distance prop families;
- its own destruction/damage state;
- a distinct lighting/weather treatment authored in Unreal, not baked into
  duplicate Blender geometry.

## Ten mission packs

| # | Mission and environment identity | Boss and engagement identity |
|---|---|---|
| 1 | **Coastal Intercept:** beach, dunes, promenade, lighthouse, beachfront hotel and coastal radar; low beach-parallel route | **Pathfinder:** rifle destroys command antenna/camera and exposes control linkage; first Igla lock occurs during its climb; rifle finish diverts it before the beach |
| 2 | **Harbor Shield:** cranes, fuel terminal, container ship, pipe racks, warehouses and industrial port; occluded crane corridor | **Breakwater:** shoot armor latches and decoy pods, then lock the exposed engine; sever the remaining elevator linkage to redirect the final dive into open harbor |
| 3 | **Convoy Escort:** coastal highway, bridge, tunnel, retaining walls and relief vehicles; fast crossing route | **Road Hunter:** blind its targeting camera and damage a wing actuator; use the forced recovery climb for an Igla shot, then prevent its final convoy attack |
| 4 | **Night Blackout:** substation, damaged grid, searchlights and burned waterfront states; minimal ambient illumination | **Black Kite:** use sound/searchlights to reveal navigation vanes and jammer blister; destroy the jammer for Igla lock and finish its exposed power bus |
| 5 | **Storm Front:** offshore platform, sea stacks, storm buoys, wreckage and distressed trawler; turbulent open-water route | **Tempest:** shoot discharge booms and jam its control servo during a gust-induced bank; hold lock through turbulence, evade debris and finish the smoking engine |
| 6 | **Airfield Defense:** runway, hangars, control tower, hardened shelters, fuelers and parked aircraft; inland low pass | **Runway Breaker:** disable three payload release mechanisms before separate objectives are struck; lock the exposed heat manifold and finish its remaining engine |
| 7 | **Search and Intercept:** radar installation, islands, fishing fleet and navigation stations; broad two-sector patrol | **Radar Ghost:** identify the real contact, destroy jammer pods from both orbit directions, then use the exposed heat vent for an Igla shot and stop reinforcement transmission |
| 8 | **Rescue Cover:** animated rescue helicopter/hoist, survivors, rafts and rescue vessel; orbiting extraction route | **Lifeline Hunter:** remove primary and secondary tracking sensors, create safe separation from friendlies, fire the Igla and redirect the disabled drone away from survivors |
| 9 | **Saturation Attack:** metropolitan skyline, power station, bridge, civic tower and rooftop infrastructure; dense approach canyons | **Iron Rain:** destroy three dispenser bays, command antennae and decoy controller; attack upper engine pods across multiple passes with missiles or difficult rifle fuel-control shots |
| 10 | **Evacuation Finale:** ferry terminal, evacuation ship, buses, ambulances and civilian convoy hub; three-stage city-port-highway corridor | **Last Flight:** combined highway, terminal and ship phases; destroy guidance arrays, strike bays, cooling systems and jammer, then use the final Igla/rifle sequence to divert the wreck |

## Variety without waste

Mission variation must come from composition and state, not recoloring the same
layout:

- Recombine modular buildings into different block shapes and street widths.
- Change terrain elevation, shoreline curvature, approach direction and flight
  altitude between missions.
- Use intact, damaged, wet, burned, blackout and evacuation material/decal
  states from shared geometry.
- Swap vegetation density, prop populations, traffic state and dock activity.
- Use Unreal lighting, fog, clouds, rain, wetness, wave state and time of day
  for atmospheric variation.
- Keep mission-exclusive landmarks visible from the aircraft's normal route,
  not hidden outside the gameplay camera envelope.
- Reuse the common boss rig and weak-point framework, but never reuse an
  identical boss silhouette, phase order or lock-window behavior.
- Tie each boss's attack pattern to the mission route and defended objective so
  it cannot be detached and dropped unchanged into another level.

## AAA asset construction standard

### 1. Reference and scale

- Assemble a reference board for every asset family with known dimensions.
- Model at real-world scale in meters, +X forward and +Z up.
- Freeze a metric blockout and approve silhouette before surface detail.
- Record source/license provenance for Fab, Quixel and any external reference.

### 2. High-poly source

- Build primary and secondary forms with clean curvature and believable
  structural load paths.
- Add actual thickness, seams, fasteners, welds, access panels, hinges,
  louvers, gutters, flashing and construction joints where visible.
- Use Blender modifiers and Geometry Nodes for nondestructive repeating detail.
- Sculpt damage and organic breakup on duplicate high-poly states rather than
  painting fake silhouettes into textures.

### 3. Game mesh

- Retopologize silhouettes and deformation areas deliberately.
- Use Nanite for appropriate opaque static architecture, rocks, ships and
  large props.
- Use conventional LODs for skeletal, animated, translucent, masked and
  gameplay-critical moving objects.
- Do not chase one universal triangle limit; allocate geometry by screen size,
  motion and silhouette importance.

### 4. UV and baking

- Use consistent texel-density tiers:
  - first-person/hero: 4K-class unique sets where justified;
  - large mission landmarks: 2K–4K plus trim sheets/tiling surfaces;
  - midground modular pieces: 2K shared trims and atlases;
  - background/HLOD: 1K or baked atlas as measured on screen.
- Provide non-overlapping bake UVs for unique assets and a separate lightmap UV
  where Unreal requires it.
- Bake tangent-space normal, ambient occlusion, curvature, thickness,
  position and material-ID maps from the high-poly source.
- Inspect cages and every bake at grazing angles; visible projection errors
  fail the asset.

### 5. PBR material detail

- Use calibrated base color, roughness, metallic and normal response.
- Build shared Unreal master materials for painted metal, bare metal, concrete,
  plaster, asphalt, glass, fabric, rubber, vegetation and water-adjacent grime.
- Add macro variation, micro normals, edge wear, decals, leaks, salt,
  soot, tire marks, chipped paint and wetness as separate controllable layers.
- Prefer trim sheets, decals and material instances over unique materials for
  every mesh.
- Use Fab/Quixel surfaces where their provenance and license are recorded, but
  reshape and art-direct them to match the Ukrainian coastal setting.

### 6. Animation-ready construction

- Place pivots at doors, cranes, radar dishes, wheels, rotors, hinges, hoists
  and control surfaces.
- Separate moving parts with stable semantic names.
- Use skeletal meshes for crew, rescue personnel, helicopter rotors/hoist,
  flexible weapon handling and destructible drone states.
- Author sockets for occupants, weapon grips, muzzle, ADS eye, Igla,
  projectiles, debris, rescue hoist and vehicle cargo.
- Bosses additionally require sockets for sensors, jammer/decoy modules,
  payload bays, heat-lock targets, weak points, damaged engines and controlled
  breakup pieces.
- Every boss weak point must be a distinct named component with intact, damaged
  and destroyed behavior rather than a painted target on one fused mesh.

### 7. Collision and destruction

- Author simple `UCX_` collision for buildings, bridges, ships, cranes and
  gameplay obstacles.
- Keep visual detail out of collision unless a gameplay raycast needs it.
- Supply intact, damaged and destroyed states for defended objectives.
- Pre-fracture only mission-critical destruction; use bounded debris pools
  instead of runtime fracturing everything.
- Boss final destruction uses pre-authored major break pieces, pooled debris
  and staged events over multiple frames; live high-complexity fracture is
  prohibited because it previously caused multi-second combat freezes.

### 8. Unreal integration

- Import into a validation map before mission placement.
- Check scale, orientation, material slots, pivots, sockets, Nanite/LOD,
  collision, light response and shadow behavior.
- Assemble missions as Unreal Level Instances/Data Layers using World
  Partition, HLOD and instancing.
- Weather, Lumen, Virtual Shadow Maps, volumetric clouds, Niagara, water and
  mission logic remain Unreal responsibilities.

## Asset naming and hierarchy

```text
SKG_<Family>_<Asset>_ROOT
├─ SM_<Family>_<Asset>_A
├─ SM_<Family>_<Asset>_B
├─ SK_<CharacterOrVehicle>
├─ UCX_<Asset>_00
├─ SO_<GameplaySocket>
└─ LOD_<n> or Nanite source
```

Examples:

- `SM_Harbor_STSCrane_A`
- `SM_Airfield_Hangar_Hardened_A`
- `SK_Rescue_Mi8_Crewed`
- `SM_Evac_Ferry_A`
- `UCX_Convoy_Viaduct_00`
- `SO_RescueHoist`

## Acceptance gates

An asset is not production-ready until it passes:

1. **Provenance:** source and license are recorded.
2. **Reference:** dimensions and silhouette match the approved board.
3. **DCC health:** transforms applied, normals correct, no accidental
   non-manifold geometry, stable names and clean hierarchy.
4. **UV/bake:** expected UV channels exist and bake artifacts are absent.
5. **Material:** physically plausible response under neutral, sun, overcast,
   night and wet lighting probes.
6. **Pivot/socket:** every animated or interactive part moves around the
   correct origin.
7. **Collision:** navigation, aircraft clearance and projectile traces behave
   correctly.
8. **LOD/Nanite:** no visible popping or silhouette collapse on the mission
   flight path.
9. **Performance:** mission frame-time, draw-call, memory and streaming traces
   remain inside the agreed target on the actual test PC.
10. **Visual:** close, gameplay and aerial evidence frames survive independent
    harsh review against the approved references.
11. **Gameplay:** defended objectives, weapon traces, drone approaches and
    destruction states work in the assembled mission.
12. **Boss encounter:** weak points, attack telegraphs, pilot commands, Igla
    eligibility, rifle-only emergency completion and final crash direction all
    pass a deterministic full-encounter test.
13. **Acceptance:** Opus 5 reviews the complete evidence package only after
    Codex verifies the measurable gates.

## Production waves

### Wave 0 — lock the factory

- Create Blender scene templates, unit/orientation preset, naming validator,
  UV/texel validator, pivot/socket validator and Unreal import receipt.
- Create the asset registry with owner, source, license, mission use, status,
  triangle/texture tier and latest hashes.
- Establish neutral material/light turntables and aerial/gameplay review
  cameras.
- Create `BP_BossDroneBase`, the weak-point component contract, pilot-command
  hooks, lock-window interface and boss evidence/telemetry schema in Unreal.

### Wave 1 — shared coast plus Mission 1

- Build the coastal terrain, roads, urban shell, vegetation and shoreline kits.
- Complete Coastal Intercept as the vertical-slice quality bar.
- Build Pathfinder as the boss-system vertical slice with physical rifle weak
  points, one Igla lock window, a rifle-only fallback and pooled breakup.
- Do not propagate assets to the other nine missions until Mission 1 passes the
  full environment, boss, visual, collision, streaming and performance gates.

### Wave 2 — industrial and moving-ground objectives

- Build Harbor Shield and Convoy Escort.
- Finish port/ship/crane kits, highway infrastructure and convoy vehicles.
- Build Breakwater and Road Hunter from the approved boss base, proving armor,
  decoy and crossing-target variants.
- Prove moving-object pivots and wing-clearance collision.

### Wave 3 — environmental variants

- Build Night Blackout and Storm Front using the approved shared coast.
- Add electrical, searchlight, offshore and storm-hazard hero assets.
- Build Black Kite and Tempest, proving night/searchlight and turbulence lock
  mechanics.
- Prove wetness, night readability and lightning/rain performance in Unreal.

### Wave 4 — inland and patrol missions

- Build Airfield Defense and Search and Intercept.
- Finish airfield, radar, island and navigation kits.
- Build Runway Breaker and Radar Ghost, proving multi-objective payload defense,
  bilateral weak points and false-contact counterplay.
- Prove route silhouettes differ materially from the coastal/harbor missions.

### Wave 5 — rescue gameplay

- Build Rescue Cover with a production rescue helicopter, hoist, raft,
  survivors and rescue vessel.
- Build Lifeline Hunter and prove friendly separation, sensor suppression and
  safe crash redirection.
- Complete skeletal animation, attachment sockets and moving-object collision.

### Wave 6 — metropolitan climax

- Build Saturation Attack and Evacuation Finale.
- Finish metropolitan skyline, power/bridge landmarks, evacuation ferry,
  terminal and civilian convoy assets.
- Build Iron Rain and Last Flight only after the shared boss framework has
  passed performance and full-encounter regression tests.
- Assemble the finale from city, harbor and highway kits without copying any
  prior mission layout.

### Wave 7 — campaign-wide polish

- Replace remaining proxies, finish damage states and decals, generate
  HLOD/streaming data, tune Nanite/LOD/collision and profile every mission.
- Capture identical environment and complete boss-encounter evidence sets for
  all ten missions.
- Run independent harsh visual challenge, regression audit and Opus 5 final
  acceptance.

## Immediate next build gate

Build Wave 0 and the first three shared hero families:

1. modular beach/seawall/road transition kit;
2. Ukrainian coastal apartment/midrise kit;
3. lighthouse plus coastal radar-post landmarks;
4. Pathfinder high/low/damaged Blender asset with separable antenna, camera,
   control linkage, engine damage states and bounded breakup pieces;
5. Unreal `BP_BossDroneBase`, weak-point components, pilot maneuver commands,
   rifle/Igla gating and deterministic encounter telemetry.

Then assemble a greybox-to-final Mission 1 slice, including its complete
Pathfinder encounter, and prove that both the environment and boss meet the AAA
visual, gameplay and performance gates before scaling production to Missions
2–10.

The corresponding ten-mission boss mechanics, weak-point assets and engagement
rules are defined in:

`Docs/AAA_Review/BOSS_FIGHT_DESIGN_10_MISSIONS.md`
