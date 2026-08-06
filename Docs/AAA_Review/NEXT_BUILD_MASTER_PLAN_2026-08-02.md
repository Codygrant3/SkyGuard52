# Skyguard 52 — Next Build Master Plan

Updated: 2026-08-02  
Runtime authority: Unreal Engine 5.8  
Hero-asset authority: Blender 5.2  
Status: ten-mission Windows release gate and refreshed PSO workflow green

## North star

Ship a stable, downloadable Windows game in which the player is the rear-seat
gunner of a Yak-52, uses a rifle and limited Igla missiles, protects believable
Ukrainian coastal objectives, and completes ten mechanically and visually
distinct missions.

The build is not complete when ten maps merely open. It is complete when every
mission is playable from briefing to debrief, has a unique route and encounter,
meets visual and performance gates, persists campaign progress, and survives a
cooked Windows soak.

## Current evidence-backed baseline

| Area | Current state | Promotion status |
|---|---|---|
| Missions 1–3 | Separate playable-integration maps with governed routes, waves, objectives, pilot commands, rifle/Igla paths and bosses | Promoted into the cook contract |
| Mission 4 | Night Blackout playable integration with searchlight, jammer, darkness and Black Kite encounter logic | Promoted into the cook contract |
| Mission 5 | Storm Front playable integration with storm route, protected platform/trawler and Tempest encounter logic | Promoted into the cook contract |
| Mission 6 | Airfield Defense playable integration; multiple protected targets, payload windows, Runway Breaker boss, Igla and orbit-gated rifle finish | Promoted into the cook contract |
| Mission 7 | Search and Intercept playable integration with two-sector identification, false tracks, protected targets and Radar Ghost encounter logic | Promoted into the cook contract |
| Mission 8 | Rescue Cover playable integration with friendly-safety corridors, hoist windows, Lifeline Hunter sensors and safe wreck redirection | Promoted into the cook contract |
| Mission 9 | Saturation Attack playable integration with bounded high-density waves, metropolitan route and Iron Rain multi-pass encounter | Promoted into the cook contract |
| Mission 10 | Evacuation Finale playable integration with highway, terminal and ship phases plus Last Flight encounter | Promoted into the cook contract |
| Campaign | Ten mission definitions, routes, objectives and boss weak-point data | Native/data foundation complete |
| Performance | Current ten-mission packaged baseline: worst mean 8.08 ms (M07), worst p95 9.88 ms (M07), worst maximum hitch 20.82 ms (M03), zero hitches over 100 ms | Baseline and current campaign stability green; input-driven ADS/fire/destruction stress profiling remains a later quality gate |
| Packaging | Development and Shipping attempt `attempt_20260802T092516016Z` contains the exact ten-map cook set, complete rehashable inventories and the accepted 97-PSO cache | Current ten-mission release gate green |
| Runtime acceptance | Same-build Shipping startup, ten mission soaks, input/ADS/fire safety, campaign save/relaunch/delete and settings persistence all pass | Current governed release evidence green |
| Audio | Seven production routing assets persist through a fresh Unreal audit | Five identity-bed sources and the remaining production categories still require approved sources |
| Art | L88 remains the most complete Yak/cockpit/crew/weapon baseline; Yak 001/002 and Coast 001 passed artifact gates but failed visible AAA replacement review | Versioned L88 component uplift and quarantined Fab visible-art inspection are in production |
| Provenance | Audio and Fab/Quixel acquisition gates now fail closed until evidence is complete | Source/license gaps still block final art and audio promotion |

## Execution rule

Only one heavyweight Unreal, UAT, shader-compilation, Blender export, or
packaged-soak process may run at a time on this workstation. Every long process
must have:

- an attempt-specific directory;
- direct stdout and stderr files;
- an exact PID and descendant list;
- a hard deadline;
- a machine-readable terminal state;
- bounded cleanup of only its own process tree;
- immutable hashes for accepted outputs.

Blender modeling, documentation, source acquisition review and code authoring
may proceed in parallel only when they do not start heavy render/build jobs.

## Gate 0 — Recover the release spine

This gate comes before additional art production because it proves that every
later milestone can become a real executable.

1. Replace `Get-FileHash` in
   `Scripts/run_skyguard_phase8_release_gate.ps1` with the project's portable
   .NET SHA-256 implementation.
2. Make supervisor exceptions write `terminal_state=FAILED_HARNESS`; no dead
   process may leave an attempt in `CREATED`.
3. Hash every file in both Development and Shipping archives.
4. Fix the malformed `SmoothedFrameRateRange` in `Config/DefaultEngine.ini`.
   Because smoothing is disabled, the cleanest option is to remove the unused
   override. If retained, use Unreal's full `FFloatRange` bound structure.
5. Re-run Shipping packaging and the bounded M01 startup smoke in a fresh
   attempt. Preserve the prior attempt as failed harness evidence.

Acceptance:

- known-file SHA-256 agrees with Python `hashlib`;
- both package inventories contain path, size and SHA-256 for every file;
- deliberate hash mismatch is rejected;
- zero `FloatRange` import warnings;
- Shipping loads the exact M01 playable map and exits by benchmark;
- no fatal, assert, GPU crash, OOM, unhandled exception or new crash receipt;
- terminal state is explicit and the independent gate report exists.

## Gate 1 — Freeze the gold gameplay template

M01 becomes the implementation template for the remaining campaign before its
art is polished.

Required template bundle:

- mission-definition and campaign binding;
- briefing preload and start transition;
- route spline and pilot maneuver commands;
- wave/objective state machine;
- physical rifle, ADS and cockpit safety arcs;
- Igla acquisition, lock loss, launch and hit path;
- boss weak-point graph;
- successful Igla path and emergency rifle-only completion path;
- protected-objective failure state;
- bounded, pre-authored boss breakup;
- scoring, medal, unlock and save update;
- debrief and return-to-campaign flow;
- telemetry and deterministic automation hooks.

Acceptance:

- two consecutive native automation passes;
- two clean packaged launches;
- at least eight packaged input cases, including fire while holding ADS;
- save, relaunch and verified score/medal/unlock round trip;
- settings change, relaunch and verified persistence;
- no dynamic high-complexity fracture or synchronous asset load during combat.

## Gate 2 — Mission 1 gold vertical slice

This is the quality bar for every later mission.

### Yak-52 and first-person station

- replace the L88 silhouette/blockout with production exterior topology;
- model the rear cockpit, open sliding canopy, bows, instrument panel, seat,
  harness, padding, trim, rivets and safety geometry;
- build the pilot and rear gunner as rigged skeletal characters;
- build anatomically credible sleeves, arms, gloves and weapon grips;
- finalize propeller hub, blades, spinner, motion-blur representation and RPM
  response;
- provide firearm/Igla sockets, ADS eye, muzzle, projectile, occupant and
  cockpit-safety sockets;
- author appropriate LODs, collision and material slots.

### Weapons and target

- production rifle with aligned physical iron sights and complete animations;
- production Igla launcher and missile with correct front/rear orientation;
- final Pathfinder boss with named antenna, camera, engine, control linkage,
  damage states and bounded breakup pieces;
- standard and heavy Shahed variants with internal damage detail visible only
  where the camera can resolve it.

### Environment

- final beach, dunes, seawall, promenade, city transition, lighthouse and
  coastal radar;
- provenance-recorded Fab/Quixel terrain, surfaces, vegetation and background
  architecture;
- Blender-authored landmarks and foreground interactive geometry;
- physically plausible water, clouds, fog, wetness and lighting in Unreal;
- no foreground proxy meshes, floating districts or scenery attached to the
  aircraft route.

### Visual gate

- correct real-world scale and silhouette;
- high-poly source or justified Nanite source;
- production topology, UVs and bake maps;
- calibrated PBR response under daylight, overcast, night, wet and storm test
  lighting;
- pivots, sockets, UCX collision and destruction states pass;
- first-person hero textures receive 4K-class detail only where screen coverage
  justifies it; shared trims/decals cover modular environment assets;
- independent blind review cannot identify a foreground blockout or legacy web
  asset.

### Performance gate

- three packaged 1920x1080 combat runs;
- mean frame time at or below 16.7 ms;
- p95 at or below 22.2 ms;
- maximum hitch at or below 100 ms;
- zero frames above 100 ms;
- ADS, rifle fire, Igla launch, drone breakup and boss destruction all occur
  inside the measured window;
- a 20-minute input-driven combat soak has stable memory.

## Gate 3 — Production asset library

Build one shared coastal library rather than ten isolated worlds:

1. beach, dunes, rocks, cliffs, seawalls and shoreline transitions;
2. roads, bridges, tunnels, rail, barriers and utilities;
3. Ukrainian low-rise, apartment, civic, midrise and industrial modules;
4. port, quay, warehouse, fuel, pipe, crane and container modules;
5. civilian, emergency, relief and support vehicles;
6. fishing, cargo, ferry, rescue and workboat families;
7. runway, taxiway, hangar, shelter and airfield-support modules;
8. radar, searchlight, checkpoint and emergency-position modules;
9. vegetation, debris, rubble and damage-state families;
10. shared drone weak-point, damage and bounded-breakup families.

Fab/Quixel supplies provenance-recorded terrain, surfaces, vegetation,
background architecture and common props. Blender supplies the Yak-52, crew,
weapons, bosses, landmarks, moving objectives, named weak points and
destruction pieces. Unreal owns assembly, PCG, Nanite, HLOD, materials,
lighting, weather, water, VFX and gameplay.

Every imported asset must record source, creator, license, version, acquisition
date, intended use and file hash before it is accepted.

## Gate 4 — Campaign production order

Do not expand all nine proxy maps simultaneously. Promote them in dependency
order so each mission proves a new reusable system.

### Wave A — M02 Harbor Shield

Make this the second production vertical slice and the generic mission-feature
bundle test. It adds crane occlusion, armor panels, decoy suppression, a fuel
terminal and a harbor-safe crash route.

### Wave B — M03 Convoy Escort, then M06 Airfield Defense

Build moving-objective and multi-target defense systems:

- M03: convoy, bridge/tunnel route, fast crossing boss and vehicle survival;
- M06: payload-release mechanisms, runway/hangar objectives and multiple
  protected targets.

### Wave C — M04 Night Blackout, M05 Storm Front, M07 Search and Intercept

Build perception and weather systems:

- M04: searchlights, darkness, audio localization and jammer exposure;
- M05: turbulence, lightning, offshore platform, trawler and storm visibility;
- M07: radar identification, decoys, two-sector patrol and reinforcement timer.

### Wave D — M08 Rescue Cover

Build animated-friendly safety:

- rescue helicopter, hoist, survivors, rafts and rescue vessel;
- friendly exclusion zones and crash-diversion logic.

### Wave E — M09 Saturation Attack

Prove high-density combat, skyline/HLOD, dispenser bays, multi-pass boss logic
and the campaign's heaviest performance case.

### Wave F — M10 Evacuation Finale

Combine validated systems into a city-port-highway finale with ferry terminal,
evacuation ship, buses, ambulances and staged Last Flight boss phases. M10
starts only after M02–M09 have passed their individual gates.

## Per-mission definition of done

Each mission must satisfy all of the following:

- exact mission, route, objective, weather and campaign binding;
- three objectives complete and fail deterministically;
- four named boss weak points map to physical damageable components;
- rifle action creates an Igla window;
- Igla path and emergency rifle-only finish both work;
- final crash path avoids the protected objective;
- at least three mission-exclusive production hero assets are visible from the
  normal route;
- no foreground `*_proxy` reference remains;
- unique route, skyline, defended objective, boss silhouette and phase order;
- asset scale, UV/PBR, pivots, sockets, collision and Nanite/LOD gates pass;
- two repeat automation passes;
- a 300-second full-combat cooked Development soak;
- the standard frame-time and critical-log gates pass;
- briefing, radio, scoring, debrief and save progression work.

## Gate 5 — Production audio

Audio acquisition runs in parallel with visual production, but cannot be called
complete until audible packaged acceptance.

1. Lock rifle platform, animation timing, listener perspectives and ten mission
   radio scripts.
2. Secure interactive-game and redistribution rights for authentic Yak-52
   engine/load, propeller, open-cockpit wind, rifle, Igla, piston-UAV,
   explosion and radio sources.
3. Audition every candidate for semantic fit, perspective, clipping, noise,
   duration and loopability.
4. Archive immutable originals and license evidence; hash immediately.
5. Produce phase-stable loops, transitions and layered weapon/explosion
   derivatives.
6. Populate all 25 production-bank categories and seven routing assets.
7. Mix cockpit/exterior transitions, localization, radio intelligibility,
   suppression and combat density.

Acceptance:

- `BoundProductionSourceCount=25`;
- `MISSING_SOURCE=0`;
- routing missing count is zero;
- QA-only procedural sources in Shipping equals zero;
- `bProductionReady=true`;
- no clipping or underruns;
- at most 48 active voices and audio-thread maximum at or below 2 ms;
- true peak at or below -1 dBTP;
- audible packaged acceptance contains at least 600 measured samples and
  hashes of the exact build and evidence.

The first acquisition priority is a controlled Yak-52 recording agreement,
because engine, propeller and open-cockpit wind define the game's identity and
cover five missing production categories.

## Gate 6 — Shader, streaming and final performance

- capture representative rifle, Igla, destruction, weather, water, UI and all
  mission traversal PSOs;
- merge and stabilize against the exact Shipping build;
- package and hash the cache;
- warm critical mission assets during briefing;
- validate M05, M09 and M10 as stress cases;
- run three-repeat packaged performance captures;
- run every mission for 300 seconds;
- run the final 20-minute input-driven campaign combat soak.

Acceptance:

- matching PSO cache is packaged and consumed;
- no first-use shader hitch breaches the frame gate;
- 10/10 exact cooked maps load;
- at least 3,000 mission-soak seconds complete;
- no new crash receipt, timeout or critical log signature;
- stable memory, streaming and frame pacing.

## Gate 7 — Release candidate

1. Close every third-party provenance record.
2. Produce packaged input/save/settings validation tied to the executable hash.
3. Run the complete Development and Shipping release supervisor.
4. Rehash every archived file.
5. Test installation and startup on a clean Windows account or machine.
6. Perform an external playtest of campaign start, one mid-campaign mission and
   M10 completion.

Final acceptance requires the independent Phase 8 verifier to return exactly
`PASS`. Successful UAT packaging alone is not release acceptance.

## Immediate next execution batch

The exact ten-map cook contract, Development and Shipping packages, packaged
runtime receipt, ten mission soaks, Shipping startup smoke, facade repair, all
ten playable mission promotions, seven-asset audio-routing scaffold,
used-asset provenance receipt and refreshed PSO workflow are now green. The
active bounded batch is:

1. preserve `attempt_20260802T092516016Z` and its receipts as the current
   accepted ten-mission engineering release;
2. continue M01 gold art using the accepted L88 baseline plus only individually
   approved R3 Yak uplift components;
3. populate the fail-closed Fab quarantine receipts for exactly one city kit
   and one beach/coast kit before any import;
4. replace visible Coast 001 diagnostic geometry while retaining its governed
   100 m by 80 m layout underlayer;
5. acquire or record the five Yak-52 identity sources without weakening the
   missing-source or provenance gates;
6. run the input-driven combat stress profile after each material art/audio
   promotion;
7. repeat the same-build Phase 8 release gate after the next promoted content
   wave.

No broad Fab import, ten-map art pass, 8K texture sweep or unsupervised
multi-process build begins. Third-party art and audio remain fail-closed until
their source, license, compatibility and immutable hash evidence is complete.

## Post-restart serialized run order

The workstation is clean after restart. No Unreal, UAT or shader-compiler
process was found during the 2026-08-02 planning audit. Heavy work resumes in
this exact order:

### R1 — Cook contract and material preflight

- require 10/10 unique map paths in config, matrix and source content;
- reject missing, duplicate and legacy-only cook sets;
- repair and compile-check `M_Tex_FacadeAtlas`;
- record config, source-map and material hashes before packaging.

Exit evidence: offline preflight `PASS`, 10/10 map equality, no empty texture
sample, and no Unreal process left running.

### R2 — Fresh package proof

- package Development, then Shipping, never concurrently;
- preserve attempt-specific logs, PID tree, deadlines and SHA-256 inventories;
- inspect the cooked registry or IoStore listing for all ten exact long package
  names;
- run a short Development NullRHI M01 load probe before Shipping smoke.

Exit evidence: both UAT exits are zero, inventories rehash, 10/10 maps are
present, and M01 no longer reports `SkipPackage` or `map could not be found`.

### R3 — Packaged behavior proof

- run the bounded D3D12/SM6 Shipping startup smoke;
- generate the executable-hash-bound runtime receipt;
- exercise ADS plus left-fire, weapon switching, Igla launch/orientation,
  cockpit/pilot safety, focus recovery, save/relaunch, incompatible-save
  handling and settings persistence.

Exit evidence: two clean launches; at least eight input, four save and five
settings cases; benchmark exit; exact M01 load; no timeout or critical log
signature.

### R4 — Gold slice and shared-runtime freeze

- remove runtime synchronous loads and dynamic complex fracture from combat;
- finalize briefing warm-up, scoring, debrief and campaign round trip;
- promote M01 art to the Yak-52/rear-cockpit/crew/weapon/environment gold bar;
- preserve the now-green M01, M02, M03 and M06 gameplay integrations;
- extract reusable systems from their proven shared shapes without regressing
  mission-specific mechanics.

Exit evidence: repeatable native and packaged tests, three 1080p combat runs,
mean frame time at or below 16.7 ms, p95 at or below 22.2 ms, maximum hitch at
or below 100 ms, and zero frames above 100 ms.

### R5 — Campaign promotion order

1. M04 Night Blackout — searchlights, localization and blackout rules.
2. M05 Storm Front — turbulence and intermittent visibility.
3. M07 Search and Intercept — identification, decoys and EW presentation.
4. M08 Rescue Cover — friendly exclusion and timed hoist windows.
5. M09 Saturation Attack — dense scheduling, skyline streaming and HLOD.
6. M10 Evacuation Finale — integration of proven systems, with no new
   foundational technology.

Each mission preserves its assembly source, creates a separate playable map,
passes deterministic complete/fail tests, supports Igla and governed rifle-only
resolution, includes at least three route-visible exclusive hero assets, and
completes a 300-second cooked combat soak.

### R6 — Audio wave P5-A

The first executable production-audio wave is limited to:

- EngineIdle;
- EngineCruise;
- EnginePower;
- Propeller;
- OpenCockpitWind.

Use a controlled, project-owned Yak-52 recording session with releases, metadata
and immutable hashes. Create the seven routing assets in the same wave:
MasterSubmix, CockpitSubmix, ExteriorSubmix, WeaponsSubmix, ExplosionsSubmix,
RadioSubmix and CockpitSoundMix.

P5-A acceptance is 5/5 provenance-complete sources, 7/7 routing assets, no
underruns, at most 48 packaged voices, audio-thread maximum at or below 2 ms,
true peak at or below -1 dBTP, and a hash-bound audible Development capture.
This is not full Phase 5 completion; that still requires all 25 categories.

### R7 — PSO, soak and release

- capture combat, weather, water, UI, traversal and destruction PSOs;
- stabilize and package the cache against the exact Shipping build;
- prove runtime cache consumption;
- run 10 five-minute mission soaks, then the 20-minute input-driven combat soak;
- close every third-party provenance gap;
- run the independent Phase 8 verifier.

Final exit evidence is exactly `gate=PASS`; successful packaging alone is not
release acceptance.

### R7 accepted evidence — 2026-08-02

- Release attempt:
  `Saved/Releases/Phase8/attempt_20260802T092516016Z`
- Independent release result:
  `Saved/Reports/PHASE8_RELEASE_GATE_LATEST.json`, `gate=PASS`
- Exact cook set: ten unique current mission maps, M01 through M10
- Packages: Development and Shipping UAT exits zero, cooked inventories and
  hashes valid
- Runtime: ten mission soaks pass; Shipping loads exact M01 under D3D12/SM6;
  input/save/settings two-launch round trip passes
- Performance receipt:
  `Saved/Reports/PHASE8_SOAK_PERFORMANCE_BASELINE_20260802T092516016Z.json`,
  `gate=PASS_BASELINE`; worst mean 8.0796 ms, worst p95 9.8811 ms,
  worst maximum hitch 20.8179 ms and zero hitches over 100 ms
- Crashes: no new crash receipts
- PSO workflow:
  `Saved/Profiling/Phase8PSO/attempt_20260802T090444632Z`
- Accepted cache:
  `Build/Windows/PipelineCaches/Skyguard52_PCD3D_SM6.stable.upipelinecache`
- Accepted cache SHA-256:
  `40008ba1fd540fca9fa5bfbda1468cf90cdf85616e2c6819a53ef0c60d7c498a`
- Cache coverage: 97 recorded PSOs, up from the preserved 92-PSO seed
- Consumption receipt:
  `verify_consumed_consume_final_m08_m10_v1.json`, `gate=PASS`

This is an accepted engineering release, not final visual/audio content
completion. Fab/Quixel visible-art imports and authentic production audio remain
blocked until their fail-closed provenance records are complete.
