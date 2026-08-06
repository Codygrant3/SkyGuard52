# M01 Fab/Quixel Acquired-Kit Technical Evaluation

Status: `SOURCE_ONLY_FAIL_CLOSED`

This is the companion gate after
`M01_FAB_QUARANTINE_INTAKE_RUNBOOK.md`. It evaluates exactly one manually
acquired city kit and one manually acquired beach/coast kit. It never browses,
purchases, downloads, extracts, imports, launches Unreal, or promotes content.

Coast 001 remains the accepted dimension, snapping, collision-intent, and
composition scaffold. Its diagnostic surfaces and box-like buildings remain
rejected as visible AAA art.

## Current catalog evidence and limits

The current product-page inspection indicates:

- the nominated city listing advertises Unreal Engine 5.0–5.8, Windows,
  Standard License, and Unreal/Unity/Blender formats, but no interiors;
- the nominated beach listing advertises Unreal 4.24–4.27 and 5.0–5.8,
  Windows, up-to-8K textures, 1k–80k-vertex meshes, five authored LODs, and
  DX12, mesh-distance-field, and virtual-texturing requirements;
- the beach demo references third-party plugins that are not included;
- the beach listing notes a public-domain boat scan.

These observations do **not** prove acquisition, selected license tier,
receipt, installed contents, immutable hashes, installed size, Nanite,
collision, included dependencies, cooked-Windows redistribution rights, or
technical acceptance. Do not mark the intake complete from catalog text.

## Exact staging layout

After the user manually acquires the two selected kits, place their untouched
or extracted payloads in exactly:

```text
Saved/FabQuarantine/M01_FAB_QUARANTINE_INTAKE_001/
├── intake_record.json
├── staging/
│   ├── CITY_KIT/payload/
│   └── BEACH_COAST_KIT/payload/
└── manifests/
```

License snapshots, receipts, compatibility proof, dependency notes, and other
evidence remain beneath the same intake root. Do not stage anything in
`Content`, `Plugins`, `/Game/Skyguard`, or an engine directory.

Executable payloads and symbolic links fail closed for this first environment
wave. The inventory generator reads files and hashes them; it does not modify
payloads:

```powershell
python .\Scripts\build_m01_fab_staging_inventory.py --slot CITY_KIT
python .\Scripts\build_m01_fab_staging_inventory.py --slot BEACH_COAST_KIT
```

Each manifest records every relative path, byte count, SHA-256, aggregate tree
hash, symlink finding, and executable finding. Any later file mutation makes
the technical record fail.

## Provenance handoff

First complete the v1 intake record with real evidence. It must independently
pass:

```powershell
python .\Scripts\verify_m01_fab_quarantine_intake.py `
  --record .\Saved\FabQuarantine\M01_FAB_QUARANTINE_INTAKE_001\intake_record.json `
  --require-ready
```

The technical record hash-binds that exact intake file and re-runs its
license, receipt, compatibility, storage, texture, feature, dependency, and
immutable-artifact checks. A missing or altered license record therefore
relocks this gate.

## Dependency contract

Create one hash-bound dependency report per kit. An empty list is valid only
when the report explicitly proves there are no dependencies.

Every dependency must be individually classified and approved. Allowed object
roots are limited to:

```text
/Engine/
/Game/Skyguard/Quarantine/M01/
/Game/Skyguard/Shared/Materials/
```

Untracked vendor roots, production-map references, missing demo plugins, and
undeclared external content fail closed. The beach listing’s non-included
demo plugins must be explicitly resolved as unnecessary or separately
licensed; silence is not approval.

## Unreal quarantine contract

No script in this lane imports content. If the provenance and staging gate
passes, a separately authorized operator may manually import to:

```text
/Game/Skyguard/Quarantine/M01/CityKit
/Game/Skyguard/Quarantine/M01/BeachCoastKit
```

Required prefixes are:

| Asset type | City | Beach/coast |
|---|---|---|
| Static mesh | `SM_M01Q_CITY_` | `SM_M01Q_COAST_` |
| Master material | `M_M01Q_CITY_` | `M_M01Q_COAST_` |
| Material instance | `MI_M01Q_CITY_` | `MI_M01Q_COAST_` |
| Texture | `T_M01Q_CITY_` | `T_M01Q_COAST_` |
| Blueprint | `BP_M01Q_CITY_` | `BP_M01Q_COAST_` |

After a manual quarantine import, export a hash-bound Asset Registry inventory
and record every inspected mesh and material:

- every mesh must use Nanite or at least two authored LODs;
- every mesh needs simple, custom UCX, or explicitly reviewed
  complex-as-simple collision;
- foreground meshes may not use complex-as-simple collision;
- every mesh material slot must resolve to the declared slot inventory;
- material variants require governed material instances;
- master/instance names, instance parents, texture references, blend modes,
  and shader-complexity dispositions must pass;
- textures may reference only the kit destination or approved shared
  materials;
- production references remain forbidden.

`READY_FOR_VISUAL_REVIEW` is still quarantine-only. It is not runtime
promotion, a Coast 001 replacement, performance acceptance, or an AAA claim.

## Gate commands

The untouched template must fail closed:

```powershell
python .\Scripts\verify_m01_fab_technical_evaluation.py
```

After filling a separate technical record:

```powershell
python .\Scripts\verify_m01_fab_technical_evaluation.py `
  --record .\Saved\FabQuarantine\M01_FAB_QUARANTINE_INTAKE_001\technical_evaluation.json
```

Only after a separately authorized quarantine import and complete technical
results:

```powershell
python .\Scripts\verify_m01_fab_technical_evaluation.py `
  --record .\Saved\FabQuarantine\M01_FAB_QUARANTINE_INTAKE_001\technical_evaluation.json `
  --require-visual-ready
```

Offline source tests:

```powershell
python -m unittest .\Scripts\test_m01_fab_technical_evaluation.py
```

## Evidence still required from the user

For each of the two kits:

1. Manually choose the exact tier and acquire it in the signed-in Fab UI.
2. Save the receipt/free-acquisition record and exact license-tier text.
3. Save product and compatibility snapshots proving the selected entitlement,
   UE 5.8 support, platform restrictions, and cooked-Windows redistribution.
4. Place the acquired payload only in its exact staging directory.
5. Identify download and installed sizes, textures, dependencies, and any
   excluded demo/plugin content.
6. Run both staging inventories and populate the hash-bound intake and
   technical records.
7. Decide whether to authorize a later manual import into the two quarantine
   destinations.

Until those actions occur, the correct disposition is
`HOLD_NO_IMPORT_NO_PROMOTION`.
