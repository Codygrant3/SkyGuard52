# Skyguard 52 — Phase 7 Governed Campaign Content

Updated: 2026-08-01  
Runtime target: Unreal Engine 5.8  
Governed root: `/Game/Skyguard/Data/Campaign_v1`  
Status: generated, fresh-process persisted and native automation PASS

## Scope

Phase 7 instantiates the Phase 6 native framework as one campaign definition
and ten mission definitions. The assets govern identity, progression and
runtime inputs.

They are explicitly **not completed maps or art**. They do not claim finished
geometry, lighting, audio, animation, cinematics, Blueprint hookups or packaged
playability. Each asset carries `Skyguard.ContentState` metadata with the value
`DefinitionOnly_NoFinishedMapOrArt`.

## Governed asset set

The folder must contain exactly:

- `DA_Campaign_Skyguard52`
- `DA_Mission_M01_CoastalIntercept`
- `DA_Mission_M02_HarborShield`
- `DA_Mission_M03_ConvoyEscort`
- `DA_Mission_M04_NightBlackout`
- `DA_Mission_M05_StormFront`
- `DA_Mission_M06_AirfieldDefense`
- `DA_Mission_M07_SearchIntercept`
- `DA_Mission_M08_RescueCover`
- `DA_Mission_M09_SaturationAttack`
- `DA_Mission_M10_EvacuationFinale`

No unrelated asset is permitted under the governed root.

## Mission differentiation

Every mission has:

- a unique four-point flight route and route id;
- a unique boss and four-node weak-point graph;
- a required protected objective;
- a unique mission-mechanic objective;
- a required boss-defeat objective;
- three authored waves with explicit formations;
- a unique weather profile and time/wind/precipitation values;
- mission-specific briefing, three radio lines and two debriefs;
- score and medal thresholds;
- a prerequisite link to the immediately preceding mission;
- a rising campaign-medal requirement.

| Order | Identity | Boss | Protected objective | Exclusive interaction |
|---:|---|---|---|---|
| 1 | Coastal Intercept | Pathfinder | Coastal radar | Disable command network |
| 2 | Harbor Shield | Breakwater | Fuel terminal | Strip armor panels |
| 3 | Convoy Escort | RoadHunter | Convoy core | Blind targeting camera |
| 4 | Night Blackout | BlackKite | Emergency substation | Hold searchlight track |
| 5 | Storm Front | Tempest | Distressed trawler | Disable discharge booms |
| 6 | Airfield Defense | RunwayBreaker | Airfield targets | Jam payload racks |
| 7 | Search and Intercept | RadarGhost | Island radar chain | Classify false tracks |
| 8 | Rescue Cover | LifelineHunter | Rescue flight/survivors | Complete hoist windows |
| 9 | Saturation Attack | IronRain | City infrastructure | Break swarm relays |
| 10 | Evacuation Finale | LastFlight | Evacuation hub | Clear evacuation lanes |

## Governance and generation

`build_skyguard_phase7_campaign_v1.py` is idempotent within the governed root:

- it creates missing native DataAssets;
- it updates existing assets only when they are the correct native class;
- it refuses to overwrite a wrong-class asset;
- it authors all reflected structures from one canonical specification;
- it saves every mission before the campaign;
- it writes a SHA-256-bound build report;
- it labels content honestly as definition-only.

The build report is:
`D:\Skyguard52\Saved\Reports\PHASE7_CAMPAIGN_V1_BUILD.json`.

## Fresh-process acceptance

`run_skyguard_phase7_campaign_v1_gate.ps1`:

1. refuses to run if an editor, commandlet, shader worker or Unreal build tool
   is active;
2. compiles the shared editor target;
3. runs the generator and waits for clean process exit;
4. starts a separate UnrealEditor-Cmd process;
5. reloads every saved asset from disk;
6. runs an exact persistence/content audit;
7. runs the complete `Skyguard52.Campaign` native automation namespace and
   asserts the three foundation tests are present;
8. rejects unexpected test counts, failures, fatal errors, assertions or
   ensures.

The persistence audit proves:

- the governed folder contains exactly eleven assets;
- all ten native mission assets load;
- campaign order and hard mission references persist;
- routes match the canonical coordinates and are mutually distinct;
- objectives, waves, formation counts and weak-point order persist;
- bosses, exclusive objectives and weather profiles are mutually distinct;
- prerequisite and medal progression persists;
- briefing/radio/debrief content persists;
- governance metadata persists;
- every mission and the full campaign pass native validation.

The audit report is:
`D:\Skyguard52\Saved\Reports\PHASE7_CAMPAIGN_V1_PERSISTENCE_AUDIT.json`.

## Acceptance evidence

Final supervisor result: PASS

- shared `Skyguard52Editor Win64 Development` target: up to date/success;
- governed assets persisted: 11;
- mission definitions persisted: 10;
- exact governed asset set: PASS;
- distinct routes: 10/10;
- distinct weather profiles: 10/10;
- distinct bosses: 10/10;
- distinct exclusive objectives: 10/10;
- mission native validation: 10/10;
- campaign native validation: PASS;
- audit failures: 0;
- automation discovered: 4;
- automation success: 4;
- automation failures: 0;
- fatal errors/assertions/ensures: 0;
- canonical specification SHA-256:
  `e31204d57f50a4bb4f1e03bd2910c52a04fe7e9106f0c7250ead2932298d64a0`;
- no Unreal editor, commandlet or shader-worker process remained after the
  final gate.

Evidence paths:

- build report:
  `D:\Skyguard52\Saved\Reports\PHASE7_CAMPAIGN_V1_BUILD.json`;
- fresh-process persistence report:
  `D:\Skyguard52\Saved\Reports\PHASE7_CAMPAIGN_V1_PERSISTENCE_AUDIT.json`;
- generator log:
  `D:\Skyguard52\Saved\Logs\Phase7CampaignBuild01.log`;
- persistence log:
  `D:\Skyguard52\Saved\Logs\Phase7CampaignPersistence01.log`;
- native automation log:
  `D:\Skyguard52\Saved\Logs\Phase7CampaignAutomation01.log`.

The native automation namespace currently contains:

1. definition/reference validation;
2. disk-slot save round trip and sanitization;
3. deterministic objectives and routes;
4. scoring, unlock and in-memory save round trip.

The first audit correctly caught an unresolved Breakwater exposure link:
`PortLatch -> ArmorPanel`, where `ArmorPanel` was absent from the governed
four-node graph. The final governed chain is fully resolvable:
`PortLatch -> StarboardLatch -> DecoyPods -> Engine`.

The supervisor was also hardened after UnrealEditor-Cmd returned zero despite a
Python exception during one retry. It now scans builder and verifier logs for
Python tracebacks and script errors instead of treating process exit alone as
proof.

## Intentionally deferred integrations

- Mission map references remain empty until each governed map package exists.
- Route definitions are not yet connected to the aircraft pilot controller.
- Wave definitions are not yet connected to the enemy director/pools.
- Objective events are not yet connected to map actors and bosses.
- Weather profiles are not yet applied to world environment directors.
- Briefing/debrief content is not yet displayed by UI.
- Save-slot I/O and packaged process-restart traversal are not yet connected.
- The mission environments, hero assets, boss art and destruction states remain
  separate production work.

These are declared integration gates. They must not be inferred from green data
definition persistence.
