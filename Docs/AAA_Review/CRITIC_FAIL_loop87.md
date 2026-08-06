# Loop87 Aircraft Truth Verdict — FAIL

Updated: 2026-08-01

## What was proven

- Blender 5.2 imported the original 70 MB
  `yak52-detail-kit-blender.glb` directly.
- The source hierarchy assembles coherently as 30 meshes with 17 materials.
- Deterministic 1920x1080 beauty/cockpit probes render without crushed blacks or
  clipped whites after the lighting correction.
- A normalized assembled GLB was exported to
  `Content/Skyguard/Meshes/Source/processed/yak52_assembled_l87.glb`.
- All three local variants (`yak52-detail-kit.glb`, `-raw.glb`, and
  `-blender.glb`) were independently imported and rendered. They share the
  same 30 meshes, 17 materials, 23.4375 x 36.0 x 5.1796875 bounds, and
  effectively identical pixels. There is no better hidden local variant.

## Objective exposure metrics

| Capture | Black < 8 | Dark < 25 | Clipped > 247 |
|---|---:|---:|---:|
| CockpitProbe | 1.25% | 4.61% | 0.00% |
| FrontThreeQuarter | 0.19% | 5.44% | 0.00% |
| RearThreeQuarter | 0.08% | 4.07% | 0.00% |
| Side | 0.78% | 2.40% | 0.00% |

Lighting is no longer the explanation for the failure.

## Visual verdict

**REJECT THE SOURCE AIRCRAFT AS A YAK-52 HERO ASSET.**

The bright renders expose a stretched narrow fuselage, fighter/jet-like wing and
tail proportions, an incorrect nose/propeller region, a largely empty low-detail
cockpit, crude geometry, and flat low-resolution material language. It does not
match the compact radial-engine Yak-52 reference silhouette and is not
salvageable through texture polish alone.

## Evidence

- `Saved/Screenshots/AAA_L87_Blender/AAA_Cam_L87_YakSide_FINAL.png`
- `Saved/Screenshots/AAA_L87_Blender/AAA_Cam_L87_YakFrontThreeQuarter_FINAL.png`
- `Saved/Screenshots/AAA_L87_Blender/AAA_Cam_L87_YakRearThreeQuarter_FINAL.png`
- `Saved/Screenshots/AAA_L87_Blender/AAA_Cam_L87_CockpitProbe_FINAL.png`
- `Saved/Screenshots/AAA_L87_Blender/BLENDER_L87_REPORT.json`

## Required next slice

L88 is asset replacement, not polish:

1. Source or author a dimensionally accurate two-seat Yak-52 exterior.
2. Build the rear cockpit as a separate first-person hero asset.
3. Validate side/front/rear silhouettes against reference before Unreal import.
4. Import one normalized parent hierarchy with preserved PBR materials.
5. Only then rebuild the Unreal validation map and capture the three visual gates.
