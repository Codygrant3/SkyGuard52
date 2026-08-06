# AAA Critic Report — Loop 21

## Verdict: FAIL vs AAA (authoritative)
Near-plane densify + multi-source capture **fixed previously black beauty frustums**. YakBeauty / Harbor / Wide / Cockpit are now non-black and structurally readable. Content remains densified proxy geometry under flat/bright materials — still loses blind A/B to MSFS prop-plane and modern BF/COD coastal combat.

Updated: 2026-07-31T19:07:00-05:00

## Host Pillow RGB audit (authoritative)
| Still | black% | uniq | edge | Usable |
|---|---|---|---|---|
| YakBeauty_FINAL | 0.0% | ~241 | 6.3 | **Yes** (was 100% black) |
| Harbor_FINAL | 3.8% | ~287 | 8.5 | **Yes** (was ~98% black) |
| Wide_FINAL | 37.1% | ~1332 | 20.3 | **Yes** |
| Cockpit_FINAL | 40.6% | ~4921 | 23.7 | **Yes** |
| City_FINAL | 0.0% | ~223 | 2.4 | Partial (flat/low edge) |
| Ocean_FINAL | 0.0% | ~125 | 1.9 | Partial (low structure) |
| Prop_FINAL | 0.1% | ~228 | 2.6 | Partial |
| Combat_FINAL | 100% | ~2 | 0 | **No** (regressed) |

UE in-process gate reported valid=0 because PIL is unavailable inside Unreal Python; host Pillow is the audit authority.

## Map / densify
- Map size: **15466697** (~15.5 MB)
- Forced ~128 near-plane objects into each camera frustum
- Bright lit materials with mild emissive fallback
- Flood lights + sun/sky/atmosphere
- Combat actors + prop spinner reseeded

## Harsh blind pillar judgment
| Pillar | Winner | Why |
|---|---|---|
| Materials | Reference | Bright procedural blocks ≠ AAA weathering/Megascans |
| City/Ocean | Reference | Harbor/city readable but proxy; ocean low structure |
| Aircraft | Reference | YakBeauty now captures *something*, not MSFS-grade airframe |
| Weapon/ADS | Reference | No iron-sight AAA still |
| VFX | Reference | No authored Niagara beauty |
| Capture | Partial→Improved | Previously black cams now produce content |
| Overall | **Reference** | Blind pick still AAA refs |

## Blind call
Best Loop21 frames (Cockpit/Wide/Harbor/YakBeauty) still lose to MSFS cockpit/exterior and modern coastal combat stills. Capture regression on Combat is noted.

## Next (Loop22)
1. Replace near-plane debug slabs with denser Yak kit web meshes + facade/ocean material response in beauty frustums
2. Restore Combat readability
3. Host-side RGB gate only (don’t trust UE PIL-less gate)
4. Keep FAIL until blind prefers Skyguard on all pillars

## Goal
NOT COMPLETE.
