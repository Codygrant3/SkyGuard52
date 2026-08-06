# AAA Critic Report — Loop 20

## Verdict: FAIL vs AAA (authoritative)
Frustum densify improved **City / Cockpit / Combat** RGB usability. YakBeauty, Ocean, Wide remain pure black. Usable frames still read as densified proxy geometry under flat lighting — not MSFS / modern BF-COD class. Blind pick remains references.

Updated: 2026-08-01T00:01:00-05:00

## Pillow RGB audit (authoritative)
| Still | black% | uniq | edge | Usable |
|---|---|---|---|---|
| City | 11.8% | ~3546 | 22.3 | **Yes** |
| Cockpit | 15.7% | ~4373 | 21.3 | **Yes** |
| Combat | 28.7% | ~514 | 11.6 | **Yes** |
| Prop | 68.0% | ~370 | 0.3 | No |
| Harbor | 98.4% | ~246 | 3.6 | No |
| Ocean / Wide / YakBeauty | ~100% | ~2 | 0 | No |

In-engine gate still said valid=0 (zlib edge proxy broken when PIL edge not available in UE Python). Critic uses host Pillow RGB.

## Map / densify
- Map size: **15108278** (~15.1 MB)
- Added frustum content: Yak continuous silhouette, ocean planes, harbor cranes/ships/containers, skyline, lights, prop spinner reseed
- Prior systems retained: combat VFX helper, prop spinner C++, WaterBodyOcean, generated mats

## Harsh blind pillar judgment
| Pillar | Winner | Why |
|---|---|---|
| Materials | Reference | No Megascans/Fab hero weathering |
| City/Ocean | Reference | City usable but proxy; ocean capture failed |
| Aircraft | Reference | Cockpit brighter; beauty exterior still black / not MSFS |
| Weapon/ADS | Reference | No true iron-sight AAA still |
| VFX | Reference | No authored Niagara beauty |
| Capture | Partial | 3 usable stills of 8 |
| Overall | **Reference** | Blind A/B still prefers AAA refs |

## Blind call
City/Cockpit/Combat would still lose to MSFS cockpit/coast and BF coastal combat. Progress is densify + capture usability, **not** AAA win.

## Next
1. Force content into YakBeauty/Ocean camera near-plane with unlit+lit dual markers and BaseColor capture only for those cams
2. Movie Render Queue / interactive HighResShot path for beauty
3. Fab/Megascans environment if available on disk
4. Keep FAIL until blind prefers Skyguard on all pillars

## Goal
NOT COMPLETE.
