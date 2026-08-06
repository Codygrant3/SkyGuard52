# M01 Hero High-to-Low Corrective 002 Visual Review — 2026-08-02

## Decision

`ARTIFACT_GATE_PASS / FINAL_VISUAL_PROMOTION_REJECTED`

One immutable corrective iteration was completed:

- build: `BLD_M01_HERO_HILO_002`;
- attempt:
  `D:\Skyguard52\Saved\BuildAttempts\M01_HERO_HIGH_TO_LOW_BAKE_CORRECTIVE_002\attempt_20260802T131317486Z`;
- Blender: 5.2.0 LTS, CPU bake;
- generator elapsed time: 61.21 seconds;
- artifact verifier: `PASS`;
- assets: 3;
- maps: 6 at 2048x2048;
- package fingerprint:
  `6ae943bed82d5ef006a4e98e4d5ffd5f7f97b88bd5639f384ab6a3779ee590a4`;
- map visual gate: `FAIL`;
- P3.4: `INCOMPLETE`;
- runtime/Unreal promotion: not authorized.

The rejected build 001 evidence was not overwritten. Build 002 uses separate
mesh, texture, report, and attempt paths.

## Corrections executed

### Pathfinder

- Reduced cage/ray from 18/60 mm to 14/25 mm.
- Reduced wing and hatch fasteners.
- Replaced the filled hatch slab with four narrow outline strips.
- Reduced seam height.
- Remapped AO with minimum `0.42`, strength `0.48`.

### Lighthouse

- Aligned seam rings to the actual tower radii.
- Reduced seam and fastener sizes.
- Expanded the cage from 25 mm to 45 mm to contain the measured detail
  excursion.
- Bounded ray distance at 55 mm.
- Remapped AO with minimum `0.28`, strength `0.62`.

### Radar post

- Removed the incorrectly untilted dish-plane fastener ring.
- Placed its replacement fasteners on the turntable mount.
- Reduced fastener sizes.
- Expanded cage/ray to 32/42 mm.
- Remapped AO with minimum `0.32`, strength `0.60`.

## Artifact verification

The independent verifier passed all governed checks:

- contract, generator, source, native master, low GLB, and texture hashes;
- distinct low/high/cage mesh datablocks;
- exact object and asset scope;
- UV layer and high/low density thresholds;
- bounds alignment;
- selected-to-active projection settings;
- map dimensions, channel contract, non-empty content, and hashes;
- deterministic package fingerprint;
- exact AO remap provenance.

Receipt:
`D:\Skyguard52\Saved\BuildAttempts\M01_HERO_HIGH_TO_LOW_BAKE_CORRECTIVE_002\attempt_20260802T131317486Z\artifact_verification.json`

## Direct inspection of all six maps

All maps were opened directly at original 2048x2048 detail.

| Asset | Map | SHA-256 | Result |
|---|---|---|---|
| Pathfinder | Normal | `7658a0216114bd396b18522346a7636a18d7885d4cf839b3b168eb864a70a3ce` | **FAIL** — colored seam excursions plus large cyan/magenta/olive gradients remain. |
| Pathfinder | AO | `d23117537ad3bafbaefb9fa506dcd289c8af1deceb3652a16008d159fbb8d822` | **FAIL** — clipping is reduced, but hard white rims, gray cleared background, and granular transitions remain. |
| Lighthouse | Normal | `afe96d11b558165d8b41a6cbd7095c6de4ff5ef2434d2c95fd7c989bde58b6ae` | **FAIL** — dense multicolor speckling remains inside multiple circular islands. |
| Lighthouse | AO | `aaecb491dc19bc831abf00e444e1b5479dd1352381e9ac2ae3d55e06e1f4ab7a` | **FAIL** — reduced clipping, but hard gray interiors and radial transitions remain. |
| Radar post | Normal | `8a56dbd3f13855433359d7d8990ac8b75b168925adfe84b8558d5483204547e0` | **FAIL** — a split-color speckled rectangle and small discontinuities remain. |
| Radar post | AO | `e82387225489cfb0415f9044b6c22fb22b133dd5d39f61d38390974bbb4c7804` | **FAIL** — moderated darkening, but hard voids and abrupt transitions remain. |

The AO correction helped, but none of the three map pairs is clean enough to
promote. No mapped-mesh or Unreal substitution is authorized.

## Immutable evidence

The attempt archives:

- Blender stdout/stderr and PID;
- artifact verification;
- native master and low-only GLB;
- six texture maps;
- build manifest and report;
- exact contract, generator, and verifier sources;
- recursive SHA-256 inventory.

Inventory:
`D:\Skyguard52\Saved\BuildAttempts\M01_HERO_HIGH_TO_LOW_BAKE_CORRECTIVE_002\attempt_20260802T131317486Z\SHA256SUMS.json`

## Required next direction

The remaining defects are structural, not a reason to keep changing one
global cage:

1. Split the joined multi-shell heroes into independent bake groups.
2. Give every production low group authored topology, smoothing, and UVs
   instead of relying on the smart-projected joined procedural mesh.
3. Author and inspect a separate cage per bake group.
4. Bake tangent normals per material/smoothing group and composite only after
   every group passes.
5. Render the mapped low mesh from front, rear, profile, top, and two grazing
   angles before another Unreal import.

P3.4 remains `INCOMPLETE`.
