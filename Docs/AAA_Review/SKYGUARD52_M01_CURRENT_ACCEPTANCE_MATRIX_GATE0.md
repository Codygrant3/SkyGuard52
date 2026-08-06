# Skyguard 52 — Mission 1 Current Acceptance Matrix

Generated: 2026-08-04  
Mission: M01 — Coastal Intercept  
Production classification: `AWAITING_NEXT_EXPLICIT_GATE`

The accepted Phase 8 package proves an engineering integration candidate. It does not prove the current Mission 1 candidate is production quality.

| Domain | Existing evidence | Current classification | Remaining acceptance work |
|---|---|---|---|
| Playable map exists | `Lvl_M01_CoastalIntercept_Playable_v1.umap`, SHA-256 `9d2ca2e5…a08afa` | `PASSED` for presence and Phase 8 cook | Repackage current candidate after all production assets integrate |
| Five-minute fixed-route soak | Phase 8 baseline | `PASSED` engineering baseline | Repeat on final content with input-driven combat and streaming |
| Environment source correction | Current source SHA-256 `73e736b0…ec44` and Gate 1 freeze | `PASSED` offline | Gate 2 must compile and test it |
| Environment native project build | Not run for current source | `AWAITING_NEXT_EXPLICIT_GATE` | Run frozen one-shot build prompt |
| Recovery05 proof plugin | Unique source exists; offline design passed | `AWAITING_NEXT_EXPLICIT_GATE` | Build after Gate 2 passes |
| Runtime binding | No accepted Recovery05 binding | `AWAITING_NEXT_EXPLICIT_GATE` | Freeze accepted binary, map, material, cameras, metrics and namespaces |
| Representative visual proof | Recovery04 timed out without captures; Recovery05 not run | `FAILED_WITH_EVIDENCE` / awaiting new gate | One governed Recovery05 UE proof and eight full-resolution visual reviews |
| Ocean and shoreline | Proxy/current content exists | `UNVERIFIED` | Convincing waterline, beach/terrain transition, temporal stability and performance |
| Terrain and city grounding | Prior web and Unreal issues recorded | `UNVERIFIED` | No floating terrain/buildings, seams, slab gaps, or camera-coupled motion |
| Roads, promenade, vegetation and traffic | Assets/source present in varying states | `UNVERIFIED` | Final layout, density, grounded placement, LOD/Nanite and visual acceptance |
| Lighthouse and radar hero assets | Recovery12 generated mapped proof | `FAILED_WITH_EVIDENCE` | Replace overexposed disconnected proxy forms; pass close/grazing review |
| Pathfinder boss art | Gameplay class and integration source exist | `FAILED_WITH_EVIDENCE` visually | Production silhouette, materials, weak points, phases, destruction and aftermath |
| Yak-52 exterior | R5 publication succeeded | `FAILED_WITH_EVIDENCE` | R6 reference-locked production asset and accepted Unreal import |
| Cockpit and rear-gunner station | Partial/proxy assets exist | `UNVERIFIED` | Production canopy, bows, glazing, pilot compartment, open rear station and no clipping |
| Pilot and rear gunner | Gameplay context exists | `UNVERIFIED` | Production characters, anatomy, harnesses, gloves, pose and animation |
| Rifle and ADS | Phase 8 input round trip proves bindings | `PASSED` engineering baseline / art unverified | Production model, physical iron-sight alignment, animation, packaged combat evidence |
| Igla | Phase 8 binding and runtime checks exist | `PASSED` engineering baseline / art unverified | Production model, correct launch point/orientation, lock feedback, tracking and reload |
| Shahed/heavy drones | Gameplay classes/assets exist | `UNVERIFIED` | Production variants, damage states, breakup, fire/smoke/debris and visual acceptance |
| Pilot/airframe firing protection | Phase 8 runtime validation passed | `PASSED` engineering baseline | Repeat in final packaged build across rifle and Igla states |
| Destruction performance | Current input-combat gate is blocked | `AWAITING_NEXT_EXPLICIT_GATE` | No ADS/fire freezes or drone-breakup stalls; three combat captures and 20-minute soak |
| Audio | Audio source/assets exist | `UNVERIFIED` | Realistic spatial engine, wind, rifle, Igla, impact, explosion, debris, radio, city and ocean mix |
| Briefing and warmup | Design intent established | `UNVERIFIED` | Dense mission briefing that masks asset/shader warmup and passes packaged flow |
| Input/settings/save | Phase 8 packaged round trip passed | `PASSED` engineering baseline | Validate current Development and Shipping candidates, including rebinding/accessibility |
| Visual performance | Frozen 1440p rubric exists | `AWAITING_NEXT_EXPLICIT_GATE` | Meet absolute frame, hitch, GPU, memory, VRAM and shader bounds with final content |
| Packaged Development candidate | Phase 8 old candidate exists | `ACCEPTED_ENGINEERING_BASELINE` only | Fresh package after accepted integration |
| Packaged Shipping candidate | Phase 8 old candidate exists | `ACCEPTED_ENGINEERING_BASELINE` only | Fresh release candidate after all gates |
| Asset provenance | Detailed M01 ledger exists with backlog | `PARTIAL` | Resolve 15 unmanifested families, 3 empty placeholders, Fab/Bridge receipts and all used-asset licenses |
| Clean-machine release validation | Missing | `MISSING` | Install, launch, progression, shutdown, crash recovery and uninstall |

## Immediate critical path

1. Explicitly authorize and run Gate 2, the frozen one-shot Mission 1 native project build.
2. Build and accept the unique Recovery05 proof plugin.
3. Freeze Recovery05 runtime binding.
4. Execute and visually inspect one representative Mission 1 Unreal proof.
5. In parallel through offline work, complete Yak R6 reference intake.
6. Produce Yak R6 and close-view combat art only through separately authorized Blender/Unreal gates.
7. Integrate the first production-quality Mission 1 vertical slice.
8. Package and validate Mission 1 before propagating its approved language to the campaign.

## Mission 1 acceptance rule

Mission 1 remains unaccepted until its current packaged build passes presentation, input, combat, art, environment, audio, performance, stability, restart, soak, provenance and release-readiness checks. No editor capture or old package may stand in for that evidence.
