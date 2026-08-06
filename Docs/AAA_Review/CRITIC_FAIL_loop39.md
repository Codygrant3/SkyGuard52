# AAA Critic Report — Loop 39

## Verdict: FAIL vs AAA (authoritative)
Loop39 uses yaw=0 (+X) cameras aimed into high-frequency checker boards and radial prop proxies with alternating unlit/PBR mats, plus triple-source capture (BASE/FINAL/SCENE when available).
Host Pillow RGB is authoritative. Even if Prop/Yak capture recovers, content remains densified kit/proxy — not MSFS / BF-COD class materials or authored Niagara beauty.
Updated: 2026-07-31T21:02:42-05:00

## Host Pillow RGB audit (best source per cam)
| Camera | Best src | black% | white% | uniq | edge | Usable |
|---|---|---|---|---|---|---|
| ADS | FINAL | 6.1% | 0.0% | ~178 | 0.4 | **Yes** (ok) |
| City | FINAL | 0.0% | 0.0% | ~13 | 0.0 | **No** (low unique) |
| Cockpit | FINAL | 2.0% | 0.0% | ~84 | 0.3 | **Yes** (ok) |
| Combat | FINAL | 24.7% | 0.0% | ~238 | 1.1 | **Yes** (strong) |
| Harbor | FINAL | 19.7% | 0.0% | ~87 | 0.4 | **Yes** (ok) |
| Ocean | FINAL | 12.3% | 0.0% | ~83 | 0.3 | **Yes** (ok) |
| Prop | FINAL | 0.0% | 0.0% | ~13 | 0.0 | **No** (low unique) |
| PropHub | FINAL | 0.0% | 0.0% | ~13 | 0.0 | **No** (low unique) |
| PropNose | FINAL | 0.0% | 0.0% | ~33 | 0.2 | **No** (low unique) |
| Wide | FINAL | 28.8% | 0.1% | ~82 | 0.5 | **Yes** (ok) |
| YakBeauty | FINAL | 17.1% | 0.0% | ~232 | 0.6 | **Yes** (strong) |

## Densify verified
- Map size: **6750737** (6.8 MB)
- HF frustum boards for Prop/PropHub/PropNose/YakBeauty/Cockpit/ADS
- Yak production kit at beauty board
- Triple-source capture when engine supports it

## Harsh blind pillar judgment
| Pillar | Winner | Why |
|---|---|---|
| Materials | Reference | Unlit/debug + generated mats; no Megascans hero weathering |
| City/Ocean | Partial/Reference | Proxy coastline fidelity |
| Aircraft | Partial/Reference | Beauty depends on capture structure; not MSFS panel fidelity |
| Weapon/ADS | Partial | Sight densify only |
| VFX | Reference | Burst markers / no authored Niagara beauty |
| Capture | Improved if Prop/Yak recoverable | Host-gated |
| Overall | **Reference** | Blind A/B still prefers AAA refs |

## Blind call
High-frequency boards are an engineering capture fix, not AAA art direction. Keep FAIL until side-by-side stills would pick Skyguard for materials, aircraft, city/ocean, weapon, and VFX.

## Capture summary
- Usable: 7  Partial: 0  Failed: 4
- Prop recoverable: False
- YakBeauty strong: False
- Cockpit strong: False
- City strong: False

## Next
1. If Prop now Yes: replace HF boards with hero prop PBR + motion disc while keeping capture locked
2. Authored airframe materials (normal/roughness/AO dirt)
3. Niagara muzzle/explosion/prop wash
4. Keep FAIL until blind prefers Skyguard on all pillars

## Goal
NOT COMPLETE.
