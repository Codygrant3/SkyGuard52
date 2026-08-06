# Phase 4 — Mission 1 Production Environment

## Architecture

Mission 1 uses a separate map revision:

`/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_ProductionEnvironment_v4_attempt02`

The unsuffixed `_v4` package is preserved as the immutable failed first
attempt: its commandlet stopped before saving actor assembly when UE 5.8
rejected an obsolete reflected fog property. It is not an accepted candidate.

`ASkyguardMission01EnvironmentDirector` owns the stable coastline:

- six contiguous 75-metre ocean districts;
- six matching beach districts;
- six matching inland terrain districts;
- one HISM draw family for each material zone;
- explicit flight-route exclusion bounds;
- explicit inland PCG inclusion bounds;
- deterministic point acceptance suitable for an authored PCG graph;
- stable ordinary static meshes and materials only.

The actor intentionally has no dependency on Water, WaterAdvanced, Landmass or Volumetrics. SkyAtmosphere, the engine VolumetricCloud actor, ExponentialHeightFog, directional wind, sun and skylight remain part of the supported atmosphere stack.

The map builder reconstructs the level from the governed 20-asset refinement manifest rather than duplicating an already-loaded external-actor world. This preserves the approved landmarks and Pathfinder bindings without reviving the prior UWorld ownership hazard.

## Route safety

The protected route runs from 0–450 metres along local X with a 28-metre half-width exclusion corridor. The shoreline begins 52 metres landward and the 18-metre beach remains excluded from vegetation. PCG scatter is accepted only inland, inside mission length and outside the route corridor.

## Performance contract

- HISM tiles replace separate repeating slab actors.
- The default route produces only 18 terrain instances across three components.
- No runtime tick is enabled.
- Point inclusion is constant-time and allocation-free.
- Automation performs 100,000 PCG inclusion queries with a broad 100 ms CPU guard.

## Verification artifacts

- `D:\Skyguard52\Saved\Reports\PHASE4_M01_PRODUCTION_ENVIRONMENT_BUILD.json`
- `D:\Skyguard52\Saved\Reports\PHASE4_M01_PRODUCTION_ENVIRONMENT_AUDIT.json`
- `D:\Skyguard52\Saved\Logs\Phase4M01Automation.stdout.log`

Focused automation:

- `Skyguard52.Environment.Mission01Production.StructureAndRouteExclusion`
- `Skyguard52.Environment.Mission01Production.BoundedScatterQueryCost`

## Honest visual boundary

NullRHI proves structure, persistence, route exclusion and bounded CPU behavior. It does not prove that the ocean, shoreline, fog, cloud, lighting or horizon look final. A visible GPU review must still evaluate:

- ocean wave scale and temporal stability;
- foam, wakes, depth color and wet shoreline blending;
- visible district seams or tiling;
- beach-to-terrain material transition;
- vegetation species, density and wind response;
- skyline composition and landmark readability;
- GPU frame time, overdraw, shadows and texture streaming.

The final PCG graph and licensed Fab/Quixel vegetation remain content work. They must consume the native inclusion/exclusion contract rather than introducing a parallel route definition.

## P4.4 authored PCG/Landscape handoff — 2026-08-02

The source boundary is now executable and fail-closed rather than implicit:

- `ASkyguardMission01EnvironmentDirector` owns a real `UPCGComponent`;
- `LandScatterBounds` carries `Skyguard.PCG.Inclusion`;
- `RouteExclusion` carries `Skyguard.PCG.Exclusion`;
- `ProductionLandscape` binds the imported `ALandscapeProxy`;
- `AuthoredPCGGraph` binds the governed graph asset;
- the PCG component uses `GenerateOnDemand` and remains inactive until a
  valid Landscape GUID, at least one Landscape component, the authored graph,
  exact bounds, coastline continuity, and route exclusion all validate.

The deterministic source heightfield is:

`Content/Skyguard/Environment/Source/Mission01/HM_M01_CoastalProduction_505x127.r16`

It is an 8×2 component, 1-section, 63-quads-per-section Landscape source with
64,135 little-endian 16-bit samples. Its current SHA-256 is
`636044a61065e72ea18defad4e6893150c3cf9c274c6aa6b06584675f4db7b26`.

Governance and gates:

- `Docs/AAA_Review/PHASE4_M01_PCG_LANDSCAPE_AUTHORING_CONTRACT.json`
- `Saved/Reports/PHASE4_M01_LANDSCAPE_SOURCE_MANIFEST.json`
- `Saved/Reports/PHASE4_M01_PCG_LANDSCAPE_READINESS_AUDIT.json`
- `Scripts/verify_skyguard_phase4_m01_pcg_landscape_assets.py`

The offline readiness gate is **PASS** and the source compiles against UE
5.8's real `Landscape` and `PCG` modules. This paragraph records the historical
pre-authoring state. It is superseded for P4.4 by
`PHASE4_M01_PCG_LANDSCAPE_SERIALIZED_ACCEPTANCE_2026-08-02.md`: the immutable
v5 `attempt03` Landscape and PCG graph now exist, round-trip in a fresh editor
process, and pass the post-authoring native regression. PCG output has still
not been generated or baked, licensed vegetation slots intentionally remain
empty, and visible GPU/AAA acceptance remains pending.

## Verification — 2026-08-01 CDT

Accepted map candidate:

`/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_ProductionEnvironment_v4_attempt02`

Fresh-process results:

- native editor target: **PASS**;
- governed map build: **PASS**, 20 governed assets and 10 non-boss placements;
- map round-trip persistence audit: **PASS**, 19 revision actors;
- six ocean, six beach and six land districts persisted;
- coastline continuity and route exclusion persisted;
- no WaterBody, WaterZone or Landmass brush actor persisted;
- both focused native automation tests: **Success**;
- 100,000 PCG exclusion queries: **1.608 ms**, 41,031 accepted inland samples;
- zero fatal, ensure or Python error markers across the accepted build, map-build, audit and automation logs.

The first unsuffixed `_v4` attempt remains a failed, non-accepted package. It stopped when UE 5.8 rejected the obsolete `volumetric_fog` reflected Python property. The accepted attempt omits that obsolete assignment because the project rendering configuration already owns the volumetric-fog CVar.

Structural Phase 4 is green. Rendered visual review remains pending and is not implied by the NullRHI evidence.
