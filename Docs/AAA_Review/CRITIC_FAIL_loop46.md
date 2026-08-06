# AAA Critic Report — Loop 46

## Verdict: FAIL vs AAA (authoritative)
Loop46 uses yaw=0 (+X) cameras aimed into high-frequency checker boards and radial prop proxies with alternating unlit/PBR mats, plus triple-source capture (BASE/FINAL/SCENE when available).
Host Pillow RGB is authoritative. Even if Prop/Yak capture recovers, content remains densified kit/proxy — not MSFS / BF-COD class materials or authored Niagara beauty.
Updated: 2026-07-31T22:20:08-05:00

## Host Pillow RGB audit (best source per cam)
| Camera | Best src | black% | white% | uniq | edge | Usable |
|---|---|---|---|---|---|---|
| ADS | FINAL | 47.3% | 0.0% | ~195 | 0.6 | **Yes** (ok) |
| City | BASE | 31.5% | 0.0% | ~73 | 14.3 | **Partial** (partial) |
| Cockpit | BASE | 21.4% | 0.0% | ~54 | 7.9 | **Partial** (partial) |
| Combat | FINAL | 48.9% | 0.0% | ~379 | 0.7 | **Yes** (strong) |
| Harbor | BASE | 11.3% | 0.0% | ~74 | 15.9 | **Partial** (partial) |
| Ocean | BASE | 21.9% | 0.0% | ~82 | 8.2 | **Yes** (ok) |
| Prop | BASE | 0.0% | 0.0% | ~25 | 5.2 | **No** (low unique) |
| PropHub | BASE | 0.1% | 0.0% | ~30 | 5.4 | **No** (low unique) |
| PropNose | FINAL | 54.4% | 0.0% | ~64 | 0.3 | **Partial** (partial) |
| Wide | BASE | 10.7% | 0.0% | ~15 | 0.2 | **No** (low unique) |
| YakBeauty | BASE | 24.6% | 0.0% | ~41 | 4.9 | **Partial** (partial) |

## Densify verified
- Map size: **13150701** (13.2 MB)
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
- Usable: 3  Partial: 5  Failed: 3
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
