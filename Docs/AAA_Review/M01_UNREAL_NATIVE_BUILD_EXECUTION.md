# Mission 1 Unreal-Native Build Execution

Updated: 2026-08-01  
Pipeline: Blender 5.2 -> Unreal Engine 5.8  
Runtime authority: Unreal Engine only

## Outcome

The first campaign vertical slice has advanced from a proxy-only concept into
a governed production candidate with:

- a refined Mission 1 coastal/urban/landmark Blender library;
- a live native Pathfinder boss with physical rifle and Igla weak points;
- deterministic boss flight phases and all five pilot commands;
- bounded, preallocated breakup and VFX presentation;
- hero PBR texture packages;
- selective Nanite and collision contracts;
- an isolated refined validation map with fresh-editor persistence evidence;
- a canonical texture/provenance inventory;
- persisted Unreal material families and bindings;
- a saved Unreal-native coastal environment revision;
- green environment and Pathfinder native automation.

This is not final AAA visual acceptance. Rendered material review, Water and
volumetric validation, GPU/frame-time profiling, and the remaining Fab gap
acquisitions are still required.

## Green gates

| Gate | Result | Evidence |
|---|---|---|
| Blender Wave 1 refinement | PASS | `Saved/Reports/M01_WAVE1_AAA_REFINEMENT_REPORT.json` |
| GLB round trip | PASS | `Saved/Reports/M01_WAVE1_AAA_REFINEMENT_ROUNDTRIP_AUDIT.json` |
| Refined Unreal import | PASS | `Saved/Reports/M01_WAVE1_REFINEMENT_UNREAL_AUDIT.json` |
| Fresh-editor persistence | PASS | `Saved/Reports/M01_WAVE1_REFINEMENT_PERSISTENCE_AUDIT.json` |
| Performance readiness | READY_FOR_RUNTIME_PROFILE | `Saved/Reports/M01_WAVE1_REFINEMENT_PERFORMANCE_READINESS.json` |
| Hero PBR bake | PASS | `Saved/Reports/M01_HERO_PBR_BAKE_REPORT.json` |
| Material build/bind | PASS | `Saved/Reports/M01_REFINEMENT_MATERIAL_UNREAL_AUDIT.json` |
| Material fresh-process persistence | PASS | `Saved/Reports/M01_REFINEMENT_MATERIAL_PERSISTENCE_AUDIT.json` |
| Texture memory estimate | READY_FOR_RUNTIME_PROFILE | `Saved/Reports/M01_REFINEMENT_TEXTURE_BUDGET.json` |
| Environment map build | PASS | `Saved/Reports/M01_ENVIRONMENT_RUNTIME_V1_BUILD.json` |
| Environment fresh-process persistence | PASS | `Saved/Reports/M01_ENVIRONMENT_RUNTIME_V1_AUDIT.json` |
| Environment structure/budget automation | PASS | `Saved/Logs/M01EnvironmentAutomation11.stdout.log` |
| Bounded D3D12 rendered startup smoke | PASS | `Saved/Logs/M01EnvironmentRenderedBenchmark04.stdout.log` |
| Pathfinder destruction sequence | PASS | `Saved/Logs/M01PathfinderAutomation11.stdout.log` |
| Pathfinder flight/controller | PASS | `Saved/Logs/M01PathfinderAutomation11.stdout.log` |
| Texture provenance | PASS_WITH_PROVENANCE_GAPS | `Saved/Reports/M01_TEXTURE_MATERIAL_PROVENANCE_LEDGER.json` |

## Produced candidate

- 20 refined meshes.
- 45,844 triangles.
- 20/20 clean GLB round-trip assets.
- Four physical weak-point meshes.
- Four authored breakup meshes; the live boss uses a hard-bounded three-piece
  pool.
- Five dense static environment assets use selective Nanite.
- Twelve deterministic 1024 x 1024 hero textures:
  BaseColor, tangent Normal, packed ORM, and Material ID for Pathfinder,
  lighthouse, and radar.
- Seven persisted material families, 24 governed textures, and 18 persisted
  refined-component bindings.
- Estimated compressed full texture mip chain of 68,506,965 bytes
  (approximately 65.3 MiB), below the 80 MiB candidate ceiling.
- A separate saved coastal environment map:
  `/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_Environment_Runtime_v3`.
- Ten environment integration actors covering stable material-based ocean,
  transitively resolved Water actors, deferred Landmass integration, PCG,
  atmosphere, cloud, fog, directional wind, and the native environment
  director.
- Native environment automation rebuilt 720 deterministic vegetation instances
  in 0.233 ms and performed 100 pooled Niagara activations in 0.264 ms with a
  fixed pool of 12 under NullRHI.
- All Pathfinder automation tests pass.

## Existing environment material library retained

The build reuses the prior local Poly Haven work instead of redownloading it:

- 24 family directories and 64 retained source maps.
- Six fully manifest-verified CC0 families, 18 exact hash matches, zero
  mismatches.
- Fifteen nonempty families that still require per-file provenance completion.
- 75 imported Unreal texture packages.
- 38 Mission 1 material candidates.
- Historical browser/WebP outputs are lineage evidence only and are not part
  of the Unreal runtime.

## Executed guarded gates

The guarded runners were executed after the reboot confirmed no visible Unreal
Editor held canonical assets or the project DLL:

```powershell
& 'D:\Skyguard52\Scripts\run_skyguard_m01_material_gate.ps1'
& 'D:\Skyguard52\Scripts\run_skyguard_m01_environment_runtime_v1_gate.ps1'
```

The first imports and binds governed Poly Haven and HeroPBR textures, creates
seven reusable material families, verifies normal/compression rules, saves an
isolated map revision, and reopens it in a fresh process.

The second builds the Unreal-native coastal runtime: Water, atmosphere, cloud,
fog, wind, route-safe vegetation HISM/PCG-ready rules, hard density budgets,
and fixed-capacity Niagara smoke/fire/sparks/explosion pools. It then runs the
structural/profile audit and all Pathfinder automation.

The material build and fresh-process persistence audits are PASS. The
environment map build and fresh-process persistence audits are PASS. The native
environment automation test and both Pathfinder automation tests are PASS.

The environment target was first advanced to the `_v2` map because loading a
duplicated external-actor world inside the same commandlet retained conflicting
world ownership. The builder now reconstructs the governed 20-mesh validation
set into a fresh target map before adding the ten environment integrations.

A bounded D3D12 launch then showed that the explicitly enabled UE 5.8
Volumetrics/Water/Landmass combination produced hundreds of Blueprint compiler
errors even when no Landmass brush existed in the map. The stable candidate
therefore advances to `_v3`, disables explicit Water, WaterAdvanced,
Volumetrics, and Landmass project enablement, retains native
atmosphere/cloud/fog/wind, and uses the governed material-ocean surface. Saved
Water actors may still resolve through Unreal's transitive plugin loading, but
the clean `_v3` smoke emitted zero Blueprint or property errors.

The old `M01_REFINEMENT_MATERIAL_GATE_STATUS.json` remains a historical
pre-reboot blocked-run receipt. It is superseded by the material build and
persistence audits listed above.

## Fab acquisition policy

Do not download generic assets merely because they are available. Acquire only
the audited gaps and record listing URL, publisher, license, acquisition date,
source version, local destination, intended mission, and package hash.

Mission 1 priorities:

1. Ukrainian coastal apartment and midrise hero modules.
2. Coastal vegetation and wind-shaped scrub.
3. Lighthouse optics, access hardware, and service detail.
4. Radar mechanical/service equipment.
5. Street dressing and marine props.
6. Damage, salt, soot, leak, and wetness decal packs.
7. Verified replacements for the empty metal walkway, painted metal, and ship
   hull placeholders.

Fab/Quixel supplies reusable environment realism. Blender remains authoritative
for the Yak-52, cockpit, weapons, Pathfinder, weak points, damage states, and
mission-exclusive landmarks.

## Promotion boundary

Mission 1 may be propagated into Missions 2-10 only after:

1. rendered daylight, overcast, wet, night, and storm review;
2. real in-editor/standalone CPU and GPU profiling;
3. stable rifle/Igla combat under destruction and VFX load;
4. authored PCG graph, a production Landscape edit-layer implementation that
   replaces the incompatible experimental UE 5.8 Landmass brush, and a verified
   production water implementation;
5. final provenance completion for every shipping third-party asset.
