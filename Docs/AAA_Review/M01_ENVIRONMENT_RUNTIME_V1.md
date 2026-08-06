# Mission 1 Environment Runtime v1

## Status

**STRUCTURAL PASS — native code linked, the isolated map was saved and reopened,
and environment plus Pathfinder automation passed. Rendered/GPU acceptance is
still pending.**

`Lvl_SkyguardCoast` was never targeted. The environment builder writes only:

`/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_Environment_Runtime_v3`

## Native runtime implementation

`ASkyguardCoastalEnvironmentDirector` provides:

- deterministic HISM trees and shrubs;
- a route-exclusion corridor and landward-only vegetation rules;
- Low, Medium, High, and Epic density budgets;
- hard tree/shrub caps and distance culling;
- an actual directional wind component;
- discovery of Water, Landmass, PCG, atmosphere, cloud, fog, and wind actors by
  explicit capability tags.

`USkyguardEnvironmentVFXPoolComponent` provides:

- a fixed pool of Niagara components;
- smoke, fire, sparks, and explosion hooks using existing project systems;
- round-robin reuse with no per-effect actor or component spawning;
- activation telemetry and a hard pool cap.

## Isolated map builder

The map script reconstructs the governed 20-mesh Mission 1 refinement set in a
fresh map and adds:

- a stable existing-material visible ocean surface that does not depend on the
  experimental Water/Landmass implementation;
- a tagged Landmass deferred-integration marker that does not load the broken
  experimental UE 5.8 brush Blueprint;
- a PCG volume;
- `SkyAtmosphere`;
- `VolumetricCloud`;
- volumetric `ExponentialHeightFog`;
- `WindDirectionalSource`;
- the native coastal environment director.

## Honest capability boundaries

Executable now:

- deterministic route-safe vegetation;
- quality and culling budgets;
- fixed-capacity Niagara reuse;
- atmosphere, cloud, fog, wind, and stable material-ocean integration;
- separate-map round-trip structural audit.

Still requiring authored content or rendered validation:

- the PCG volume has no authored PCG graph yet; native HISM placement is the
  executable fallback;
- the bundled experimental UE 5.8 `CustomBrush_Landmass` Blueprint is excluded
  because a rendered launch exposed internal compiler incompatibilities; a
  production Landscape edit-layer implementation is still required;
- explicit Water, WaterAdvanced, Volumetrics, and Landmass project enablement
  is disabled; saved Water actors can still resolve through Unreal's transitive
  plugin loading, but the stable material/mesh ocean is the authoritative
  fallback and production Volumetrics content remains excluded;
- NullRHI cannot judge water, cloud, fog, vegetation, or Niagara appearance;
- GPU time and visual frame pacing require a visible-editor or packaged
  Development profile.

## Verified gate result

The guarded gate was executed after the reboot confirmed no visible editor was
holding canonical project assets:

`powershell -ExecutionPolicy Bypass -File D:\Skyguard52\Scripts\run_skyguard_m01_environment_runtime_v1_gate.ps1`

Verified evidence:

1. map build PASS:
   `Saved/Reports/M01_ENVIRONMENT_RUNTIME_V1_BUILD.json`;
2. fresh-process persistence PASS:
   `Saved/Reports/M01_ENVIRONMENT_RUNTIME_V1_AUDIT.json`;
3. environment structure/budget automation PASS:
   `Saved/Logs/M01EnvironmentAutomation11.stdout.log`;
4. Pathfinder encounter and bounded-destruction automation PASS:
   `Saved/Logs/M01PathfinderAutomation11.stdout.log`;
5. 720 deterministic vegetation instances rebuilt in 0.233 ms;
6. one hundred pooled Niagara activations completed in 0.264 ms with a fixed
   pool of 12.

These CPU timings were captured under NullRHI. They do not replace visible
water/cloud/fog/Niagara review or standalone GPU/frame-time profiling.

A bounded 1280 x 720 D3D12 game launch also loaded `_v3`, brought the world up
for play, ran for 20 benchmark seconds, and exited normally with zero Blueprint
errors, property errors, fatal errors, GPU crashes, or out-of-memory events:

`Saved/Logs/M01EnvironmentRenderedBenchmark04.stdout.log`
