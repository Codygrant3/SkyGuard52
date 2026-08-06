# Skyguard 52 — Phase 6 Data-Driven Campaign Foundation

Updated: 2026-08-01  
Runtime target: Unreal Engine 5.8  
Scope: Phase 6 and the reusable structural foundation for Phase 7  
Status: native implementation, shared editor link and focused automation PASS

## Outcome

Skyguard 52 now has a native, data-driven campaign layer that separates
authored mission content from map actors and combat implementations. Designers
can describe a mission without copying a Level Blueprint. Runtime state,
scoring, unlock rules and save data are deterministic C++ contracts.

The implementation deliberately does not replace the existing Pathfinder boss,
coastal environment or aircraft systems. It supplies the stable data and
progression boundary those systems can consume.

## Native architecture

### Authored primary assets

`USkyguardMissionDefinition` is a `UPrimaryDataAsset` with the stable primary
asset type `SkyguardMission`. It owns:

- mission identity, display name and campaign order;
- a soft map reference;
- a dimensioned flight route and combat-orbit permissions;
- required and optional objectives, failure behavior and score rewards;
- timed enemy waves and formation composition;
- boss identity, weak-point graph, weapon requirements and bounded breakup
  budget;
- weather, time of day, wind, precipitation and cloud coverage;
- briefing, radio chatter, success/failure debrief and minimum warm-up time;
- completion, accuracy, damage and medal score thresholds;
- prerequisite mission ids and campaign-medal requirements.

`USkyguardCampaignDefinition` is a `UPrimaryDataAsset` with the stable primary
asset type `SkyguardCampaign`. It owns the ordered mission catalog and validates
mission identity, order and dependency integrity as one graph.

### Runtime services

`USkyguardCampaignSubsystem` is a `UGameInstanceSubsystem`, making campaign
progress independent of map travel. It:

- configures only from a valid campaign;
- determines mission availability from completed prerequisites and best earned
  medals;
- starts a mission by constructing objective and route runtimes;
- accepts objective progress/failure events;
- refuses mission completion after a terminal failure or before every required
  objective completes;
- calculates objective, perfect-accuracy and no-damage score contributions;
- deduplicates objective ids before applying score rewards;
- retains best score, medal and completion time;
- exports and imports a versioned campaign save contract;
- rejects saves for another campaign or schema version.

`USkyguardObjectiveRuntime` owns objective state transitions. Progress is
clamped, completed objectives reject duplicate progress, and authored
failure-ending objectives become terminal.

`USkyguardRouteRuntime` converts authored points into a deterministic,
distance-sampled polyline. It clamps before the start and after the end and is a
safe source for a future spline-driven pilot controller.

`USkyguardCampaignSaveGame` is the version-one persistence contract. It stores
campaign identity and per-mission best records rather than transient actors,
enemy pointers or map state. Imported scores and completion times are clamped
non-negative, medal tiers are clamped to zero-through-three, and records for
unknown missions are discarded.

## Validation rules

The native definitions reject:

- missing or duplicate mission, route-point, objective, wave, formation and
  boss weak-point ids;
- routes with fewer than two points or non-positive airspeeds;
- missions without a required success objective;
- wave and boss references to missing objectives;
- boss weak-point exposure links that do not resolve;
- formations outside the one-to-thirty-two unit bound;
- boss breakup budgets outside zero-to-twelve pieces;
- invalid weather ranges or non-monotonic medal thresholds;
- null/duplicate campaign missions and duplicate order values;
- unknown prerequisites and forward/cyclic dependencies.

This turns authoring mistakes into deterministic validation failures rather
than late mission soft-locks.

## Phase 7 authoring matrix

Create one `DA_Mission_*` asset per row and add it to
`DA_Campaign_Skyguard52`.

| Order | Mission asset | Boss id | Exclusive mechanic | Required data emphasis |
|---:|---|---|---|---|
| 1 | `DA_Mission_CoastalIntercept` | `Pathfinder` | Component disarm and first Igla lock | Beach route, city protection, antenna-camera-engine-linkage graph |
| 2 | `DA_Mission_HarborShield` | `Breakwater` | Crane occlusion, armor and decoys | Harbor route, fuel-terminal protection, latch-panel-decoy graph |
| 3 | `DA_Mission_ConvoyEscort` | `RoadHunter` | Crossing attacks and moving objective | Highway route, convoy survival threshold, camera-actuator graph |
| 4 | `DA_Mission_NightBlackout` | `BlackKite` | Audio search and searchlight exposure | Night profile, grid protection, vane-jammer-power graph |
| 5 | `DA_Mission_StormFront` | `Tempest` | Turbulence and short visibility windows | Storm profile, offshore objective, boom-servo-engine graph |
| 6 | `DA_Mission_AirfieldDefense` | `RunwayBreaker` | Independently threatened airfield assets | Runway route, three protection objectives, payload-engine graph |
| 7 | `DA_Mission_SearchIntercept` | `RadarGhost` | Search sectors and identification | Island route, radar objectives and signature-control graph |
| 8 | `DA_Mission_RescueCover` | `LifelineHunter` | Timed rescue/hoist protection | Rescue orbit, survivor objectives and attack-inhibitor graph |
| 9 | `DA_Mission_SaturationAttack` | `IronRain` | Simultaneous waves and prioritization | Metropolitan route, infrastructure objectives and multi-node boss graph |
| 10 | `DA_Mission_EvacuationFinale` | `LastFlight` | Branching finale under evacuation pressure | Ferry route, civilian convoy objectives and final multi-phase graph |

Each definition must have a different route polyline, weather/presentation
profile, objective set, wave/formation slate and boss weak-point graph. Shared
geometry does not imply duplicated mission data.

## Integration contracts for other phases

### Flight and pilot

The aircraft/pilot layer should sample `USkyguardRouteRuntime` by traveled
distance, apply each point's target airspeed, and enable orbit commands only
when `bAllowCombatOrbit` is true. It should never own campaign unlock state.

### Enemy director

The wave director should consume `FSkyguardEnemyWaveDefinition`, instantiate
formations through the existing pool/spawner, and report completion through
`AddObjectiveProgress`. Runtime actors must not mutate the primary asset.

### Bosses

Boss actors should bind physical components to authored `WeakPointId` values.
Destruction of a component reports boss-objective progress. The existing
Pathfinder remains the Mission 1 reference implementation; the data definition
does not simulate weapon damage or replace physical boss behavior.

### Briefing and loading

The briefing screen should render `Presentation.Briefing`,
`Presentation.RadioChatter` and threat/objective data while requesting the
mission map and asset bundles. `MinimumBriefingWarmupSeconds` is a presentation
floor, not permission to hide an unbounded load.

### Environment

The environment director should consume `FSkyguardWeatherProfile` after map
load. Weather stays world-space; it must not be parented to aircraft attitude.

### Debrief and persistence

The debrief screen consumes `FSkyguardMissionResult`. After displaying the
score breakdown, the game instance persists `BuildSaveGame()` using Unreal's
save-slot API. Disk I/O is intentionally outside the subsystem so platform slot
policy remains a presentation/platform concern.

## Native automation coverage

`SkyguardCampaignTests.cpp` adds three focused tests:

1. `Skyguard52.Campaign.Definition.ValidationRejectsBrokenReferences`
   - validates a complete authored mission and campaign;
   - verifies stable primary asset identity;
   - proves missing objective/weak-point references and forward/cyclic
     prerequisites are rejected.
2. `Skyguard52.Campaign.Runtime.ObjectivesAndRouteAreDeterministic`
   - proves route length, interpolation and endpoint clamping;
   - proves required progress, duplicate rejection and terminal objective
     failure behavior.
3. `Skyguard52.Campaign.Runtime.ScoringUnlocksAndSaveRoundTrip`
   - proves deterministic scoring and silver-medal classification;
   - proves combined prerequisite/medal unlock behavior;
   - proves matching save data restores unlocks and cross-campaign data is
     rejected.

## Current build evidence

Unreal Header Tool accepted every new reflected type. The native build produced
fresh object files for:

- `SkyguardCampaignDefinition.cpp`
- `SkyguardCampaignSaveGame.cpp`
- `SkyguardCampaignSubsystem.cpp`
- `SkyguardCampaignTests.cpp`
- `SkyguardMissionDefinition.cpp`
- `SkyguardObjectiveRuntime.cpp`
- `SkyguardRouteRuntime.cpp`

After the independently owned concurrent Igla compile errors were repaired, the
shared `Skyguard52Editor Win64 Development` target compiled and linked
successfully.

Final focused automation log:
`D:\Skyguard52\Saved\Logs\Phase6CampaignAutomation03.log`

- test filter: `Skyguard52.Campaign`;
- discovered tests: 3;
- successful tests: 3;
- failed tests: 0;
- fatal errors/assertions/ensures: 0;
- queue completion: `Automation Test Queue Empty 3 tests performed`;
- UnrealEditor-Cmd exit status: 0;
- no editor or shader-worker process remained after shutdown.

The earlier `Phase6CampaignAutomation01.log` is retained as diagnostic evidence.
It caught an invalid test fixture that constructed a
`UGameInstanceSubsystem` outside a `UGameInstance`. The fixture was corrected
to reproduce runtime ownership. The final third run also covers duplicate score
reward suppression and save-value sanitization.

## Remaining integration gates

Phase 6's native foundation is present, but campaign production is not complete
until all of the following are proven:

1. Create `DA_Campaign_Skyguard52` and ten mission primary data assets in
   Content.
2. Populate and validate every mission against the matrix above.
3. Register/load the campaign asset at game-instance startup.
4. Connect map travel, wave spawning, boss events, environment profiles,
   briefing/debrief screens and save-slot I/O to the native contracts.
5. Run a packaged-build campaign traversal proving unlocks and save persistence
   across process restart.

These are integration and authored-content gates, not missing definitions in
the native foundation.
