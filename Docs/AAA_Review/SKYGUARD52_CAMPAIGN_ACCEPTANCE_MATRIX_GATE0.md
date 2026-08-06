# Skyguard 52 — Ten-Mission Campaign Acceptance Matrix

Generated: 2026-08-04  
Campaign classification: `AWAITING_NEXT_EXPLICIT_GATE`

All ten playable map files and mission integration directors exist. The accepted Phase 8 engineering baseline cooked the exact ten maps and completed a five-minute fixed-route soak for each. None of the ten missions has current production-art, route-distinction, input-driven combat, audio, or final packaged acceptance.

| Mission | Current map SHA-256 | Phase 8 state | Boss source | Required production identity | Current production acceptance |
|---|---|---|---|---|---|
| M01 Coastal Intercept | `9d2ca2e5…a08afa` | Playable integration candidate; soak passed | Pathfinder | Beach, dunes, promenade, lighthouse, radar, coastal route and interception boss | `UNVERIFIED`; vertical slice critical path active |
| M02 Harbor Shield | `f07a2238…f4f4bbc` | Playable integration candidate; soak passed | Breakwater | Working harbor, fixed cranes, fuel terminal, container ship, realistic naval target and port boss | `UNVERIFIED` |
| M03 Convoy Escort | `31f781e5…164059` | Playable integration candidate; soak passed | RoadHunter | Coastal highway, bridge, tunnel, relief convoy, safe opening route and ambush boss | `UNVERIFIED` |
| M04 Night Blackout | `08307029…a0858d` | Playable integration candidate; soak passed | BlackKite | Substation, damaged grid, searchlights, blackout navigation and electronic-warfare boss | `UNVERIFIED` |
| M05 Storm Front | `c8ab1601…dbf017` | Proxy assembly candidate; soak passed | Tempest | Offshore platform, sea stacks, storm buoys, trawler, severe weather and storm boss | `UNVERIFIED`; proxy baseline |
| M06 Airfield Defense | `e8302c72…aa81f` | Playable integration candidate; soak passed | RunwayBreaker | Runway, hangars, control tower, hardened shelters, ground-defense activity and airfield boss | `UNVERIFIED` |
| M07 Search and Intercept | `9ac99384…b553d` | Proxy assembly candidate; soak passed | RadarGhost | Radar installation, islands, fishing fleet, navigation stations, search mechanics and decoy/stealth boss | `UNVERIFIED`; proxy baseline |
| M08 Rescue Cover | `26e7a3a8…73736` | Playable integration candidate; soak passed | LifelineHunter | Animated rescue helicopter, hoist, survivors, rafts, rescue vessel and extraction boss | `UNVERIFIED` |
| M09 Saturation Attack | `6f037ee4…8eb4` | Playable integration candidate; soak passed | IronRain | Metropolitan skyline, power station, major bridge, rooftops, large waves and command-drone boss | `UNVERIFIED` |
| M10 Evacuation Finale | `b859a3dd…3f9669` | Playable integration candidate; soak passed | LastFlight | Ferry terminal, evacuation ship, buses, ambulances, convoy hub and multi-phase finale boss | `UNVERIFIED` |

## Per-mission production gate

Every mission must independently pass all of the following:

- Unique route and rear-gunner composition.
- Unique briefing, objective flow, escalation, recovery and debrief.
- Distinct skyline, landmark set, weather, lighting and soundscape.
- Three to ten exclusive hero assets.
- Boss introduction, readable telegraphs, weak points, phases, destruction and aftermath.
- No floating, disconnected, repetitive or visibly placeholder geometry.
- Grounded terrain/shore/road/building transitions.
- Rifle and Igla engagement opportunities with pilot/airframe protection.
- Input-driven combat validation including ADS, firing, lock, launch, impact and reload.
- Destruction without multi-second stalls.
- Packaged audio, input, save, progression, success and failure validation.
- Absolute frame-time, hitch, GPU, memory, VRAM and shader-readiness budgets.
- Repeated restart/transition and extended soak checks.
- Complete source/license receipts for every used third-party asset.

## Campaign-level gates

The campaign cannot pass until:

1. Mission 1 establishes an accepted production-quality vertical-slice standard.
2. Modular geometry reuse remains approximately 65–70% without duplicated layouts.
3. All ten missions are present, distinct, playable and finishable in the current packaged candidate.
4. Progression and mission unlocks survive relaunch.
5. A full-campaign clean-machine run completes without red gates.
6. Development and Shipping packages have complete immutable inventories.
7. No mission is represented only by editor, proxy, offline-contract or old-baseline evidence.
