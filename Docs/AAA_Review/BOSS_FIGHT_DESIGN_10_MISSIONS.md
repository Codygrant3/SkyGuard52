# Skyguard 52 — Ten-Mission Boss Encounter Plan

Updated: 2026-08-01  
Target runtime: Unreal Engine 5.8  
Player role: rear-seat soldier/gunner in the Yak-52  
Status: gameplay and asset design; not yet implemented

## Design goal

Each mission ends with a distinct aerial threat that tests what the player
learned in that level. Bosses are not large health bars. They are physical,
multi-stage machines with readable components, changing flight behavior and
mission-specific objectives. The player defeats them by combining:

- precise rifle fire through physical iron sights;
- limited Igla missiles with a real lock-on window;
- pilot maneuver commands;
- target prioritization while defending a ground or maritime objective;
- visible mechanical damage rather than abstract damage numbers.

The encounters are fictionalized for gameplay. They should feel mechanically
credible without presenting themselves as exact simulations of real weapons or
aircraft.

## Shared boss interaction framework

### Player verbs

1. **Observe**
   - identify the boss by silhouette, engine sound, navigation lights, exhaust
     and radio callouts;
   - read armor, moving panels, sensors, control surfaces and heat sources;
   - no permanent floating reticle or glowing weak-point icon.
2. **Position**
   - command the pilot to `Pursuit`, `Break`, `Orbit Left`, `Orbit Right` or
     `Extend`;
   - pilot callouts announce when the rear gunner has a stable firing arc;
   - unsafe arcs through the pilot/cockpit remain blocked.
3. **Disarm with the rifle**
   - shoot exposed sensors, antennae, decoy pods, armor latches, control
     surfaces or payload mechanisms;
   - successful hits cause physical animation, sparks, smoke, changed sound
     and altered boss behavior.
4. **Create the lock window**
   - rifle damage exposes or overheats an engine section;
   - a maneuver places the player inside the Igla seeker cone;
   - decoys or jamming must be disabled before lock can complete.
5. **Commit the Igla**
   - lock progress is conveyed through the seeker audio and physical sight;
   - firing too early wastes a scarce missile;
   - a successful hit advances the boss to a damaged phase rather than always
     ending the fight immediately.
6. **Finish**
   - use rifle fire on the final exposed component or a second missile on late
     campaign bosses;
   - the boss enters a pre-authored breakup/crash sequence away from protected
     civilians and mission-critical structures.

### Pilot commands

| Command | Gameplay use | Tradeoff |
|---|---|---|
| Pursuit | Closes distance and stabilizes rifle shots | Boss can attack the Yak-52 more easily |
| Break | Evades a telegraphed pass or debris field | Loses lock progress |
| Orbit Left/Right | Changes which boss components are visible | Temporarily masks the opposite side |
| Extend | Creates separation for an Igla shot | Gives the boss time to attack the defended objective |

Commands should use short radio phrases and one input each. They do not turn
the game into a full flight simulator.

### Fairness rules

- Every dangerous boss attack has an animation, sound and radio telegraph.
- Weak components are recognizable through form and behavior, not neon paint.
- Difficulty changes timing, accuracy, escort count and lock-window duration;
  it does not merely multiply health.
- The player cannot be punished by an attack originating outside the possible
  look/fire arc without an advance warning.
- Bosses cannot clip through scenery, the Yak-52, friendly aircraft or ships.
- A missed Igla must not make the mission mathematically unwinnable; an
  emergency rifle-only finish remains possible but harder.

## Mission 1 — Coastal Intercept

### Boss: `Pathfinder`

A larger reconnaissance/strike Shahed coordinating the remaining low-altitude
contacts along the beach.

### Encounter

1. Pathfinder flies extremely low over the water with two light escorts.
2. The player uses rifle fire to break its dorsal command antenna and nose
   camera.
3. With coordination disabled, the escorts lose formation and become ordinary
   threats.
4. Pathfinder climbs to reacquire the coast, exposing its hot rear engine.
5. The player orders `Extend`, obtains the first campaign Igla lock and fires.
6. A damaged engine forces Pathfinder into a final broad turn; rifle fire on
   the exposed control linkage finishes it before it crosses the beach.

### Skill taught

Basic component damage, first pilot command and first missile lock.

### Failure pressure

Pathfinder reaching the city triggers a heavy shield penalty; escort breaches
remain normal damage.

### Blender assets

- Pathfinder high/low/damaged meshes;
- detachable antenna, camera and control-linkage parts;
- two engine-damage states and bounded breakup chunks.

## Mission 2 — Harbor Shield

### Boss: `Breakwater`

An armored maritime strike drone using cranes and container stacks to interrupt
line of sight while approaching the fuel terminal.

### Encounter

1. Breakwater makes crossing runs between crane silhouettes.
2. Three armored side panels cover its engine and control bay.
3. During each bank, mechanical latches become visible for precise rifle fire.
4. Destroying two latches causes a panel to tear away; the third panel remains
   as optional bonus damage.
5. Breakwater ejects hot decoys until the player destroys both decoy pods.
6. The pilot exits the crane corridor, the player locks the exposed engine and
   fires the Igla.
7. The damaged drone attempts a final fuel-terminal dive; rifle fire severs its
   remaining elevator linkage and diverts the crash into the harbor.

### Skill tested

Occluded sightlines, armor removal and decoy suppression.

### Blender assets

- heavy armored drone;
- animated armor panels/latches and decoy pods;
- damaged engine, elevator and harbor-safe crash chunks.

## Mission 3 — Convoy Escort

### Boss: `Road Hunter`

A fast attack drone that predicts the convoy route and performs repeated
crossing attacks rather than flying straight at the objective.

### Encounter

1. Road Hunter alternates between ridge cover and fast highway crossings.
2. The player must choose an orbit direction that reveals its targeting camera.
3. Rifle hits blind the camera and make the next attack less accurate.
4. Shooting either wing actuator forces a longer recovery climb.
5. The recovery climb creates the short Igla lock window.
6. After the missile hit, Road Hunter attempts to strike the convoy's lead
   vehicle; the player destroys its remaining actuator with the rifle.

### Skill tested

Leading a fast crossing target and choosing which side of the aircraft to
engage.

### Failure pressure

Individual convoy vehicles can be damaged or lost; the mission only fails when
the convoy's protected core falls below its survival threshold.

### Blender assets

- swept fast-drone body;
- nose camera gimbal and two animated wing actuators;
- three damage configurations and lightweight debris set.

## Mission 4 — Night Blackout

### Boss: `Black Kite`

A low-observable night drone that is difficult to see outside searchlight and
muzzle-flash illumination.

### Encounter

1. Searchlight crews sweep the waterfront while the boss uses the dark sea as
   cover.
2. Radio bearing and engine sound guide the player before visual acquisition.
3. A searchlight pass reveals reflective navigation vanes for rifle fire.
4. Destroying both vanes prevents Black Kite from timing its light-avoidance
   maneuver.
5. The boss is illuminated continuously for several seconds, allowing the
   player to destroy its jammer blister.
6. Jammer loss enables the Igla seeker; the player locks and fires.
7. A short rifle finish destroys the exposed power bus during the burning glide.

### Skill tested

Audio localization, target reacquisition and firing without a HUD crosshair.

### Blender assets

- night-drone silhouette with controlled reflective materials;
- navigation vanes, jammer blister and exposed power bus;
- emissive failure states visible under night lighting.

## Mission 5 — Storm Front

### Boss: `Tempest`

A weather-hardened heavy drone that emerges intermittently from cloud and rain.

### Encounter

1. Tempest uses squalls to conceal attack runs.
2. Lightning and radio calls briefly reveal its silhouette.
3. The player shoots two static-discharge booms; until removed, they confuse
   the seeker during lightning.
4. Strong gusts force the boss into a corrective bank, exposing the engine
   intake and a control servo.
5. Rifle damage jams the servo and lengthens the exposure.
6. The pilot stabilizes with `Extend`; the player holds a difficult Igla lock
   through turbulence and fires.
7. Tempest sheds damaged panels; the player must `Break` to avoid debris before
   finishing the smoking engine.

### Skill tested

Short visibility windows, aim stabilization and deliberate evade commands.

### Blender assets

- reinforced storm-drone shell;
- discharge booms, intake shutters, servo and water-shedding panels;
- authored panel debris with fixed performance bounds.

## Mission 6 — Airfield Defense

### Boss: `Runway Breaker`

A heavy bomber drone carrying three separate payload modules for runway,
hangars and parked aircraft.

### Encounter

1. Each payload module announces its target through door animation and radio
   warning.
2. The player shoots the opening rack or release mechanism before the drop.
3. Saved objectives improve the final mission rating; losing all three fails
   the sortie.
4. Destroying two release mechanisms exposes an internal heat manifold.
5. The player obtains an Igla lock during the boss's turn over the runway.
6. The missile disables one engine, but the boss continues on asymmetric power.
7. Rifle fire destroys the opposite engine's oil/cooling housing to force a
   crash outside the runway complex.

### Skill tested

Component prioritization under multiple simultaneous objective threats.

### Blender assets

- twin-engine bomber boss;
- three animated payload bays/modules and release racks;
- internal heat manifold and two progressive engine-damage states.

## Mission 7 — Search and Intercept

### Boss: `Radar Ghost`

An electronic-warfare command drone generating false contacts and splitting the
player's attention across the patrol box.

### Encounter

1. The radar shows several false returns, but only the real drone has physical
   exhaust distortion, shadow and engine sound.
2. The player visually identifies it and orders the pilot toward the correct
   sector.
3. Radar Ghost carries two jammer pods on opposite sides, requiring both orbit
   directions.
4. Rifle fire destroys each pod; every destroyed pod removes part of the false
   contact field.
5. The center antenna retracts after the second pod fails, exposing a heat vent.
6. A narrow rear-aspect Igla shot damages the boss.
7. The player destroys its command antenna during the retreat to prevent a
   reinforcement wave and finish the encounter.

### Skill tested

Visual identification, bilateral positioning and resisting false HUD data.

### Blender assets

- electronic-warfare drone;
- left/right jammer pods, retracting antenna and heat vent;
- radar false-contact effects remain Unreal UI/VFX assets.

## Mission 8 — Rescue Cover

### Boss: `Lifeline Hunter`

A precision strike drone focused on the rescue helicopter and survivors rather
than the city.

### Encounter

1. Lifeline Hunter alternates between tracking the rescue helicopter and
   repositioning behind the Yak-52.
2. The player shoots its tracking optic to break each attack solution.
3. The optic rotates behind armor after taking damage; the player must change
   orbit direction to reach its secondary sensor.
4. Destroying both sensors forces the boss into a broad visual-search pattern.
5. The pilot creates separation from the rescue helicopter before an Igla can
   be fired safely.
6. The missile disables the boss, but it begins an uncontrolled descent toward
   the extraction lane.
7. Rifle fire removes the remaining control surface, turning the crash away
   from the helicopter and survivors.

### Skill tested

Fire discipline, friendly separation and defending a fragile moving objective.

### Blender assets

- precision-strike drone;
- rotating primary optic, secondary sensor and armored covers;
- rescue-safe redirected crash state.

## Mission 9 — Saturation Attack

### Boss: `Iron Rain`

A command-and-carrier drone coordinating the campaign's largest swarm and
releasing replacement contacts during the fight.

### Encounter

1. Three dispenser bays periodically release small drones.
2. The player can shoot a bay door while open to destroy that dispenser and
   reduce later waves.
3. Two command antennae buff the remaining swarm's coordination; rifle fire
   removes them.
4. Iron Rain then deploys decoys and turns its armored belly toward the player.
5. The pilot must climb and cross above the boss to expose the upper engines.
6. The player destroys a decoy controller, locks the first engine and fires an
   Igla.
7. The boss enters a second attack phase on two remaining engine pods.
8. A second missile or a difficult rifle attack on both fuel-control units ends
   the fight.

### Skill tested

Crowd control, resource management and multi-pass component destruction.

### Blender assets

- large carrier drone;
- three animated dispenser bays, drone racks and two antennae;
- decoy controller, three engine pods and multiple damage states.

## Mission 10 — Evacuation Finale

### Boss: `Last Flight`

A three-phase heavy command drone attacking the highway convoy, ferry terminal
and evacuation ship in sequence.

### Encounter

#### Phase 1 — Highway

- Last Flight deploys escorts and attempts to disable the moving convoy.
- Rifle fire destroys two guidance arrays, weakening escort accuracy.
- The player chooses which convoy section to protect during crossing attacks.

#### Phase 2 — Terminal

- The boss opens two armored strike bays while approaching the ferry terminal.
- The player shoots the bay mechanisms before their attack cycle completes.
- Each destroyed bay exposes one of two cooling systems.
- An Igla hit disables the first main engine.

#### Phase 3 — Evacuation ship

- Last Flight jettisons armor and becomes faster but mechanically exposed.
- The player switches between rifle and remaining Igla while the pilot performs
  pursuit, break and orbit commands learned throughout the campaign.
- Destroying the jammer permits the final lock.
- The final missile tears away the second engine; rifle fire on the command
  core diverts the wreck away from the evacuation ship.

### Skill tested

The complete campaign vocabulary: prioritization, bilateral positioning,
pilot commands, decoy suppression, two weapon types and civilian protection.

### Blender assets

- campaign-final heavy command drone;
- detachable armor shell, guidance arrays, two strike bays, cooling systems,
  jammer, dual engines and exposed command core;
- three major damage configurations and a controlled ocean-impact breakup set.

## Boss feedback without arcade clutter

- **Hit confirmation:** localized metal strike, fragments, component motion and
  sound; no generic hit marker is required.
- **Component destroyed:** distinct mechanical failure animation plus pilot
  callout.
- **Lock state:** authentic escalating seeker tone, sight response and weapon
  vibration; no center-screen lock reticle.
- **Boss phase:** changed silhouette, smoke color, engine sound, flight pattern
  and radio message.
- **Incoming attack:** moving doors/pods, engine spool, navigation-light change
  and directional radio warning.
- **Health communication:** optional compact component diagram on the cockpit
  kneeboard/briefing card, not a giant floating health bar.

## Unreal implementation architecture

### Boss actor

`BP_BossDroneBase` should own:

- a boss state machine;
- physical weak-point components;
- attack telegraphs;
- pilot-maneuver response hooks;
- damage-state mesh/material switching;
- Igla lock eligibility;
- protected-object targeting;
- pooled debris and VFX events;
- encounter telemetry and deterministic test controls.

Each mission creates a child data asset/Blueprint with unique flight behavior,
components and phase rules rather than copying the entire implementation.

### Weak-point component

Each targetable component records:

- weapon eligibility: rifle, Igla or either;
- damage threshold;
- exposed/armored state;
- physical bounds;
- destruction animation;
- gameplay consequence;
- audio/VFX cue;
- replacement mesh or material state.

### Performance rule

Do not perform live high-complexity fracture when a boss dies. Every boss uses:

- pre-authored major break pieces;
- a bounded reusable debris pool;
- capped particles and smoke;
- staged destruction over several frames;
- off-thread asset preloading during the mission briefing.

This specifically protects ADS-and-fire gameplay from the prior multi-second
drone-destruction freezes.

## Blender production order

1. Build Pathfinder as the boss-system vertical slice.
2. Prove component targeting, rifle/Igla gating, pilot commands and pooled
   breakup in Unreal.
3. Build Breakwater and Road Hunter to validate armor and crossing-target
   variants.
4. Build Black Kite and Tempest for lighting/weather mechanics.
5. Build Runway Breaker, Radar Ghost and Lifeline Hunter for defended-object
   and bilateral-component mechanics.
6. Build Iron Rain and Last Flight only after the common boss framework is
   stable and performance-tested.

## Acceptance gates

Every boss must pass:

1. identifiable silhouette at expected combat distance;
2. all phases completable with normal ammunition;
3. rifle-only emergency completion path;
4. readable attack telegraphs without a HUD reticle;
5. correct cockpit/pilot firing obstruction;
6. Igla lock only during intended exposure windows;
7. no scenery, friendly or aircraft clipping;
8. no boss-phase scripting deadlock;
9. deterministic automated phase test;
10. stable frame time during component destruction and final breakup;
11. difficulty variants tested without health inflation;
12. independent full-encounter playtest and visual review.
