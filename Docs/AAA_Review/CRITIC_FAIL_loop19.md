# AAA Critic Report — Loop 19

## Verdict: FAIL vs AAA (authoritative)
Lit densify + dual capture improved frame usefulness vs Loop16–18. Pillow RGB audit shows **City** and **Cockpit** are no longer pure black, but content is still not MSFS / BF-class. Overall blind pick remains reference games.

Updated: 2026-07-31T19:00:00-05:00

## Capture evidence (Pillow RGB)
| Still | black% | uniq | size | Notes |
|---|---|---|---|---|
| City_FINAL | 16.7% | ~2414 | 2.24MB | First city frame with real brightness diversity |
| Cockpit_FINAL | 15.9% | ~3527 | 1.62MB | First cockpit frame with non-black structure |
| ADS_FINAL | 0.0% | ~275 | 2.24MB | Over-bright flat orange/yellow (proof-like wash) |
| Combat_FINAL | 50.1% | ~595 | 1.17MB | Mixed; not readable combat readability |
| Prop_FINAL | 68.7% | ~583 | 0.85MB | Partial |
| Ocean/YakBeauty/Wide | ~100% | low | ~0.44MB | Still failed |

In-engine gate reported valid=0 because zlib-byte black proxy is harsher than RGB audit. Critic uses Pillow RGB as authoritative.

## Map / systems
- Map size after Loop19: **14145262** (~14.1 MB)
- Continuous Yak proxy silhouette densify (fuselage/wings/tail/prop)
- City skyline blocks + roads + ocean/beach + harbor
- Lights: key/fill/sky/point + atmosphere/fog/PP
- Dual capture BASE+FINAL

## Harsh blind pillar judgment
| Pillar | Winner | Why |
|---|---|---|
| Materials | Reference | Generated mats, not Megascans/Fab hero weathering |
| City/Ocean | Reference | City frame exists but proxy blocks; ocean still black |
| Aircraft | Reference | Cockpit brighter but not MSFS-grade interior/exterior |
| Weapon/ADS | Reference | ADS wash not iron-sight realism |
| VFX | Reference | No authored Niagara beauty |
| Capture | Partial | Some usable RGB stills finally |
| Overall | **Reference** | Blind A/B still prefers AAA refs |

## Blind call
Even best Loop19 City/Cockpit stills would lose to MSFS cockpit/coast and modern coastal combat stills. Progress is capture usability, not AAA win.

## Next (Loop20)
1. Beauty-pass densify focused on **YakBeauty + Ocean + Harbor** camera frustums (currently black)
2. Recalibrate validity gate to Pillow-equivalent RGB stats
3. Replace orange proof dominance in ADS with lit rifle/Yak interior
4. Fab/Megascans if available; else higher-fidelity procedural facade/ocean
5. Keep FAIL until blind prefers Skyguard on all pillars

## Goal
NOT COMPLETE.
