# Mission 01 Build 008 Unreal candidate acceptance

## Purpose

Import the exact hash-bound Build 008 low GLB and its 24 Normal/AO maps into
an isolated Unreal candidate namespace. This lane evaluates import fidelity,
texture interpretation, material binding, scale, collision, Nanite policy,
fresh-process persistence, and mapped-view agreement. It never changes a
runtime map, project config, or promoted asset.

## Preconditions

- The offline readiness report must be
  `PASS_OFFLINE_READY_AWAITING_SEPARATE_UNREAL_AUTHORIZATION`.
- The Unreal candidate root must not exist:
  `/Game/Skyguard/Candidates/Mission01/HeroGroupedTopology_008`.
- Unreal Editor, UnrealEditor-Cmd, UBT, UAT, ShaderCompileWorker, UBA, and
  Blender must all be inactive.
- A root operator must separately authorize the Unreal launch. The Blender
  review receipts recommend the next gate but do not authorize an engine run.

## Serialized gate

After authorization:

```powershell
powershell -ExecutionPolicy Bypass -File D:\Skyguard52\Scripts\run_m01_hero_grouped_topology_unreal_acceptance_008.ps1
```

The runner performs the offline audit first, then uses one hidden
`UnrealEditor-Cmd` process for candidate import/staging and a distinct fresh
process for persistence verification. A still-active PID is waited on and is
never duplicated.

## Import contract

- The 12 GLB low objects are renamed to the exact contracted `SM_M01C008_*`
  assets.
- The 24 source maps are derived only from the bound Build 008 manifest.
- Normal maps are non-sRGB, `TC_NORMALMAP`, and have green flipped because the
  bake is OpenGL tangent-space.
- AO maps are non-sRGB `TC_MASKS`; red feeds Ambient Occlusion.
- Each semantic group receives one neutral candidate material with its own
  Normal and AO pair. All mesh slots are bound.
- Mesh dimensions must agree with Blender meters converted to Unreal
  centimeters within two percent.
- Only `RadarPost/DishFeed` enables Nanite; all other groups remain classic
  because they are small, transparent, dynamic, or below the density floor.
- Collision is explicit per group; lantern glass intentionally has none.

## Review and rollback

The candidate review map is isolated under the same candidate root. Capture
three-quarter, port-grazing, and starboard-grazing views for Pathfinder,
Lighthouse, and RadarPost, then compare at original resolution to the bound
mapped-Blender receipt.

Failure never promotes or silently deletes evidence. Preserve the complete
attempt directory. Rollback may remove only the candidate root after the
failed attempt has been reviewed. It must never delete or overwrite runtime
assets, the canonical Build 008 Blender package, or any review receipt.

Even a complete pass means `PASS_CANDIDATE_PERSISTED_AWAITING_MAPPED_VIEW_REVIEW`
or `READY_FOR_SEPARATE_MANUAL_PROMOTION_REVIEW`; it does not authorize
promotion or close P3.4.
