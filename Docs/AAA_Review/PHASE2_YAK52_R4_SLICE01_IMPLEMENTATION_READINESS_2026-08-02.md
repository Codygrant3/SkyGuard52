# Phase 2 Yak-52 R4 Slice 01 implementation readiness

## Outcome

`BLD-M01-YAK-FINAL-ART-R4-S01` is ready for a later, explicitly authorized Blender 5.2 draft-authoring run.

This is an offline readiness result only:

- Blender was not launched.
- Unreal was not launched.
- No `.blend`, GLB, render, artifact manifest, import, runtime replacement, promotion, or acceptance was created.
- The accepted R3 and R4 authority files were not changed.
- The primary Yak-52 reference package is still missing.
- The silhouette is not locked and cannot be called reference-faithful, final, or AAA.

## Frozen Slice 01 scope

The future draft contains only the dependency-first primary volumes:

- fuselage and cowling envelopes;
- left/right wing primary planforms;
- left/right horizontal tail and vertical tail planforms;
- front and rear canopy envelopes;
- main and nose landing-gear stance envelopes;
- propeller motion disc;
- four measurement datums;
- neutral diagnostic materials;
- five fixed review cameras.

No R3 donor geometry, external mesh import, surface microdetail, production materials, rigging, collision, Unreal import, or gameplay promotion is permitted in this slice.

## Dimension truth boundary

The immutable ledger governs six inherited project values:

| Measurement | Target | Tolerance |
|---|---:|---:|
| Overall length | 7.745 m | 0.08 m |
| Wingspan | 9.300 m | 0.08 m |
| Overall height | 2.700 m | 0.08 m |
| Propeller diameter | 2.400 m | 0.05 m |
| Rear cockpit clear width | 0.720 m | 0.04 m |
| Rear cockpit rail height | 1.340 m | 0.04 m |

These values came from an internal project contract. They are useful for deterministic draft construction but are not primary technical-source proof. The ledger therefore records the orthographic/dimensioned drawing, cleared multi-angle photographs, and primary dimension source as `MISSING`.

## Deterministic authoring boundary

The future Blender source:

- requires Blender 5.2;
- starts from a factory-empty scene;
- uses random seed `5201`;
- refuses to overwrite any canonical output;
- never opens, appends, links, or imports an accepted `.blend`;
- validates all authority hashes before authoring;
- validates exact collections, objects, cameras, dimensions, symmetry, finite bounds, applied scale, and a 50,000-triangle draft budget;
- writes temporary files before canonical publication;
- labels every future artifact `DRAFT_REFERENCE_PACKAGE_MISSING`;
- keeps all final, AAA, import, runtime, promotion, and silhouette-lock claims false.

## Fixed visual review

The five required 1920×1080 neutral EEVEE Next views are:

1. `R4_CAM_BEAUTY_PORT` → `R4S01_BeautyPort.png`
2. `R4_CAM_SIDE_ORTHO` → `R4S01_SideOrtho.png`
3. `R4_CAM_TOP_ORTHO` → `R4S01_TopOrtho.png`
4. `R4_CAM_REAR_QUARTER` → `R4S01_RearQuarter.png`
5. `R4_CAM_UNDERSIDE_ORTHO` → `R4S01_UndersideOrtho.png`

Cropping, reframing, or camera mutation after authoring begins is forbidden.

## Verification

The offline gate validates:

- eight immutable authority inputs by size and SHA-256;
- the authoring source by size, SHA-256, AST safety, Blender version gate, fixed seed, factory reset, required output operations, and forbidden donor/import/network operations;
- exact namespace and topology rules;
- exact R4 camera agreement;
- exact dimension values and tolerances;
- strictly increasing nine-station fuselage plan;
- all completion claims false;
- all canonical future output paths absent.

Fourteen mutation tests prove the gate fails on false execution status, false silhouette lock, falsified reference availability, changed dimensions or tolerances, station-order drift, camera removal or movement, namespace drift, budget relaxation, donor-policy relaxation, script drift, and pre-existing canonical output.

## Next authorized action

The preferred next action is to obtain a cleared primary reference package with provenance, viewing notes, rights status, and SHA-256 hashes, then revise the dimension ledger under a separately accepted contract.

If the root owner instead explicitly authorizes a provisional draft run before those references arrive, the run must remain isolated and must retain `DRAFT_REFERENCE_PACKAGE_MISSING`. A successful run still will not satisfy the R4 Slice 01 exit gate. Silhouette lock requires the cleared reference package, all fixed renders, measurement conformance, human reference comparison, and explicit separate acceptance.
