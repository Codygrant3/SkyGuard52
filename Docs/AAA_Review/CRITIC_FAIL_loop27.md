# AAA Critic Report — Loop 27

## Verdict: FAIL vs AAA (authoritative)
Loop27 adds capture-proof high-contrast prop stages (Near/Mid/Nose), unlit radial ticks + checker backdrops, closer YakBeauty, FOV 90 for prop/cockpit/ADS, denser gauges/rivets.
Host Pillow RGB is authoritative. Still densified kit/proxy content, not MSFS / BF-COD class.
Updated: 2026-07-31T19:48:26-05:00

## Host Pillow RGB audit (best BASE/FINAL per cam)
| Camera | Best src | black% | white% | uniq | edge | Usable |
|---|---|---|---|---|---|---|
| ADS | FINAL | 42.7% | 0.3% | ~173 | 0.2 | **Partial** (partial) |
| City | FINAL | 14.9% | 27.5% | ~1639 | 3.1 | **Yes** (strong) |
| Cockpit | FINAL | 22.8% | 1.9% | ~633 | 1.4 | **Yes** (strong) |
| Combat | FINAL | 0.0% | 0.2% | ~594 | 0.3 | **Yes** (ok) |
| Harbor | FINAL | 0.0% | 0.0% | ~44 | 0.4 | **Partial** (partial) |
| Ocean | FINAL | 0.0% | 0.0% | ~74 | 0.3 | **Partial** (partial) |
| Prop | BASE | 30.8% | 0.0% | ~23 | 0.0 | **No** (low unique) |
| PropHub | FINAL | 30.9% | 4.7% | ~152 | 0.1 | **Partial** (weak) |
| PropNose | FINAL | 0.0% | 0.0% | ~23 | 0.0 | **No** (low unique) |
| Wide | FINAL | 0.0% | 76.7% | ~182 | 0.2 | **Partial** (too white) |
| YakBeauty | FINAL | 0.0% | 0.0% | ~12 | 0.0 | **No** (low unique) |

## Densify verified
- Map size: **23643432** (23.6 MB)
- Capture-proof prop stages with unlit blades/ticks/checker BG
- Yak rivets/panel lines + beauty pad
- Cockpit bright gauges + fill spheres
- Dual BASE/FINAL; host selects best

## Harsh blind pillar judgment
| Pillar | Winner | Why |
|---|---|---|
| Materials | Reference | Generated/unlit debug mats for capture proof, not hero weathering |
| City/Ocean | Partial/Reference | Proxy coastline |
| Aircraft | Partial/Reference | Needs readable beauty silhouette + panel materials |
| Weapon/ADS | Partial | Iron-sight densify only |
| VFX | Reference | No authored Niagara beauty |
| Capture | Improved if Prop recoverable | Host-gated |
| Overall | **Reference** | Blind A/B still prefers AAA refs |

## Blind call
Capture-proof unlit prop markers are engineering proof, not AAA art. Keep FAIL until blind prefers Skyguard on materials, aircraft beauty, city/ocean, weapon, VFX.

## Capture summary
- Usable: 3  Partial: 5  Failed: 3
- Prop recoverable: False
- YakBeauty strong: False
- Cockpit strong: True

## Next
1. Convert capture-proof prop success into hero prop materials (metal, oil, motion blur disc)
2. Fab/Megascans or authored PBR for airframe/city
3. Niagara muzzle/explosion/prop disc
4. Keep FAIL until blind prefers Skyguard on all pillars

## Goal
NOT COMPLETE.
