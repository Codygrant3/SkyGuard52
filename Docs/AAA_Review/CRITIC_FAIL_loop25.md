# AAA Critic Report — Loop 25

## Verdict: FAIL vs AAA (authoritative)
ADS/Prop/Yak-edge densify + dual-source host selection recovered **ADS** (previously pure black) and kept City/Combat/Ocean usable. Prop remains failed; YakBeauty still low-edge; Cockpit regressed to low-structure BASE. Frames are densified kit/proxy with improved capture coverage, not MSFS / BF-COD class. Blind pick remains reference games.

Updated: 2026-07-31T19:26:00-05:00

## Host Pillow RGB audit (best BASE/FINAL per cam)
| Camera | Best src | black% | white% | uniq | edge | Usable |
|---|---|---|---|---|---|---|
| ADS | FINAL | 42.2% | 14.2% | ~1716 | 11.0 | **Yes** (recovered) |
| City | FINAL | 13.4% | 27.3% | ~6038 | 35.7 | **Yes** |
| Combat | FINAL | 0.0% | 0.2% | ~1083 | 10.3 | **Yes** |
| Ocean | FINAL | 0.0% | 0.0% | ~247 | 8.3 | **Yes** |
| Cockpit | BASE | 0.0% | 0.0% | ~84 | 4.6 | No (low structure) |
| Harbor | FINAL | 0.0% | 0.0% | ~176 | 4.3 | Partial |
| Wide | FINAL | 0.0% | 65.2% | ~1718 | 3.8 | Partial (over-bright) |
| YakBeauty | FINAL | 0.0% | 0.0% | ~105 | 1.9 | Partial (flat) |
| Prop | BASE | 0.0% | 0.0% | ~3 | 0.0 | No |

## Densify verified
- Map size: **23154170** (~23.2 MB)
- Yak production meshes: **20** @ scale ~0.292
- ADS near-field rifle/iron-sights/glove/forearm densify
- Prop near-field blades/cowling densify
- Yak rivet/panel/canopy edge densify + high-contrast city windows
- Dual BASE/FINAL capture; host selects best non-black source

## Harsh blind pillar judgment
| Pillar | Winner | Why |
|---|---|---|
| Materials | Reference | Generated mats; no Megascans hero weathering |
| City/Ocean | Partial | City/Ocean usable; still proxy coastline fidelity |
| Aircraft | Partial | Yak densified; beauty still flat vs MSFS |
| Weapon/ADS | Partial | ADS recovered with structure; not AAA iron-sight fidelity |
| VFX | Reference | Burst markers / no authored Niagara beauty |
| Capture | Improved | ADS recovered; Prop still broken |
| Overall | **Reference** | Blind A/B still prefers AAA refs |

## Blind call
Best Loop25 ADS/City/Combat/Ocean stills would still lose to MSFS cockpit/exterior and modern combat stills. Capture recovery is meaningful; AAA win is not.

## Next
1. Prop frustum overhaul (camera looks into solid black void)
2. YakBeauty material microdetail + sharper lighting for edge energy
3. Stabilize cockpit FINAL (avoid near-black FINAL)
4. Fab/Megascans if available
5. Keep FAIL until blind prefers Skyguard on all pillars

## Goal
NOT COMPLETE.
