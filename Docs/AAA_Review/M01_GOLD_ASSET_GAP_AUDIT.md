# Mission 01 Gold-Slice Asset Gap Audit

Updated: 2026-08-02  
Method: offline file, source, and receipt inspection only  
Manifest: `Docs/AAA_Review/M01_GOLD_ASSET_GAP_MANIFEST.json`

## Result

The audit contract passes when its manifest and evidence remain hash-valid, but
Mission 01 art remains `PASS_WITH_GAPS`. A verifier `PASS` means the
classifications are internally consistent; it does not mean the assets are
production accepted.

| Asset family | Current classification | Reason |
|---|---|---|
| Yak-52 exterior | `blockout_proxy` | Governed source and runtime binding exist, but the source and receipts explicitly identify a silhouette blockout/readiness candidate. |
| Rear cockpit | `blockout_proxy` | L88 contains a substantial cockpit bundle, but final topology, PBR, collision, sockets, and rendered acceptance remain open. |
| Crew arms and gloves | `blockout_proxy` | Static first/third-person staging exists; production skeletal crew, anatomy, deformation, and animations do not. |
| Rifle | `blockout_proxy` | An 18-part L88 bundle exists, but no final hero-weapon geometry, bake, ADS, or packaged acceptance exists. |
| Igla | `blockout_proxy` | An eight-part staged assembly exists, but final launcher/missile detail, orientation contract, animation, and acceptance remain open. |
| Pathfinder | `unverified` | Refined geometry, four weak points, bounded breakup, textures, import, and runtime binding exist; final bake justification, visible review, and packaged destruction performance remain open. |
| Lighthouse | `unverified` | Refined Blender/PBR/import candidates exist; visible multi-lighting and route-performance acceptance remain open. |
| Radar post | `unverified` | Refined Blender/PBR/import candidates exist; visible, animation/pivot, and objective-combat performance acceptance remain open. |
| Coast | `unverified` | Refined coast and persisted environment assembly exist; final material/provenance, visible GPU, HLOD/streaming, and packaged performance acceptance remain open. |

Counts:

- production: 0
- blockout/proxy: 5
- missing: 0
- unverified: 4
- scoped families: 9

## Highest-value next serialized Blender build

Build `BLD-M01-YAK-PROD-001`: the production Yak-52 exterior and rear-cockpit
master.

This is upstream of the crew, rifle, and Igla. Freezing the real airframe,
cockpit dimensions, canopy envelope, occupant datums, ADS eye, weapon sockets,
launch axis, and safety volumes prevents later hero assets from being authored
against disposable blockout coordinates.

The offline source gate must pass before Unreal import:

1. real-world silhouette and dimensions;
2. separated exterior, propeller, canopy, cockpit, controls, seat, harness,
   trim, and glass;
3. named pivots and machine-readable crew/weapon/socket datums;
4. production topology or justified Nanite route;
5. UV/material/bake-source validation;
6. transform, naming, non-manifold, and blockout-name rejection checks.

## Verification

Run only the lightweight verifier and tests:

```powershell
py -3 Scripts\verify_skyguard_m01_gold_asset_gap.py
py -3 -m unittest Scripts.tests.test_verify_skyguard_m01_gold_asset_gap
```

These commands do not launch Unreal, Blender, UAT, shader compilation,
packaging, or rendering.
