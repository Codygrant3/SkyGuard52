# Mission 01 Landscape Visible GPU Review

Status: `READY_FOR_AUTHORIZED_GPU_AUTHORING`

This is the first bounded visible review of the real 505×127 Landscape in the
accepted v5 `attempt03` environment. It deliberately does not authorize Fab,
Quixel, vegetation, PCG generation, or a broad environment art pass.

The governing machine-readable contract is
`Docs/AAA_Review/PHASE4_M01_LANDSCAPE_VISIBLE_GPU_REVIEW_CONTRACT.json`.

## Material audit outcome

The allowed external surface inputs are only:

- `coast_sand_01` for the first 14 m of Landscape inland from the beach;
- `aerial_grass_rock` for the inland surface.

Both are local Poly Haven CC0 families. Their six source files have canonical
download URLs, local byte counts, and SHA-256 hashes verified in
`Content/Skyguard/Textures/PolyHaven/polyhaven-provenance-manifest.json`. The
six imported Unreal textures are hash-locked in the contract.

The existing `M_L23_Ocean` and `M_L23_Beach` are project-authored materials,
created by `Scripts/build_skyguard_aaa_loop23_beauty_capture.py`; their binary
hashes are also locked. They remain only so this pass can judge the relationship
between the new Landscape, the existing beach, and the existing water.

Excluded from this pass:

- all Fab and Quixel catalog items;
- all vegetation;
- the empty `metal_walkway_01`, `painted_metal_02`, and `ship_hull` folders;
- materials not enumerated in the contract;
- decals, wetness, RVT, displacement, tessellation, and material-layer expansion.

## Immutable authoring rule

Do not edit v5 `attempt03`. Create the contract's new validation map from the
governed scene manifest and deterministic R16 height source. Do not duplicate a
loaded `UWorld`, and never overwrite an existing attempt.

The candidate must expose the real Landscape. The director's legacy `LandTiles`
surface must be non-rendering in the candidate only; otherwise it overlaps and
conceals the Landscape, invalidating every visual conclusion. Ocean and beach
tiles remain present for the relationship review.

Bind one new Landscape material using six samplers:

- sand BaseColor, OpenGL Normal, and Roughness;
- grass/rock BaseColor, OpenGL Normal, and Roughness.

Blend in world space from Y=7000 cm to Y=8400 cm. Use a 3 m sand scale and a
5 m inland scale. Imported OpenGL normals must have green-channel flipping
enabled. Do not add displacement, tessellation, RVT, decals, wetness, foliage,
or PCG output.

## Heavy-lane sequence

Run only after root grants exclusive Unreal/UBT ownership.

1. Prove no Unreal, UBT, UBA, ShaderCompileWorker, CrashReportClient, or game
   process is active.
2. Compile once if the candidate-only `LandTiles` visibility switch requires a
   native change.
3. Author the immutable candidate with D3D12/SM6 or NullRHI as appropriate, but
   do not claim visible acceptance from NullRHI.
4. Start a fresh D3D12/SM6 process and perform the five fixed camera captures.
5. Capture the three candidate diagnostics.
6. Profile one baseline and one candidate run: 30 s warm-up plus 60 s measured,
   with a 180 s hard process timeout.
7. Verify the exact image count/dimensions, parse cost evidence, scan logs, and
   record a separate human visual decision against every rubric item.
8. Stop and verify that the heavy process set is empty.

Never run a second supervisor while the first is active.

## Required visual decision

The pass is conjunctive. All of the following must pass:

- the Landscape reads as shaped terrain rather than an infinite slab;
- all 16 components are present and grounded;
- there are zero visible component cracks, black seam lines, district gaps, or
  post-warm-up z-fighting frames;
- beach, Landscape, and water meet continuously, with no dry gap or water over
  land;
- the water stays 40–140 cm below the land/beach relationship and remains world
  fixed;
- the world-space sand-to-inland blend has no hard border or obvious scale
  mismatch;
- the exact performance and delta limits in the JSON contract pass.

If any required capture, trace, CSV, hash, or human judgment is absent, the gate
is `INCOMPLETE`, not PASS.

## Claim boundary

An offline readiness pass proves only that the baseline and approved material
inputs are present, hash-bound, and ready for a bounded GPU authoring lane.

A completed visible gate may accept Landscape material, shoreline relationship,
and Landscape cost for this M01 slice. It does not approve vegetation, the
broader environment, Mission 01 AAA completion, or gold master.
