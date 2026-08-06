# AAA Critic Report — Loop 68

## Verdict: FAIL vs AAA (authoritative)
Loop68 uses yaw=0 (+X) cameras aimed into high-frequency checker boards and radial prop proxies with alternating unlit/PBR mats, plus triple-source capture (BASE/FINAL/SCENE when available).
Host Pillow RGB is authoritative. Even if Prop/Yak capture recovers, content remains densified kit/proxy — not MSFS / BF-COD class materials or authored Niagara beauty.
Updated: 2026-08-01T02:58:46-05:00

## Host Pillow RGB audit (best source per cam)
| Camera | Best src | black% | white% | uniq | edge | Usable |
|---|---|---|---|---|---|---|
| ADS | FINAL | 16.1% | 0.0% | ~255 | 1.0 | **Yes** (strong) |
| City | FINAL | 32.0% | 1.2% | ~409 | 0.8 | **Yes** (strong) |
| Cockpit | FINAL | 2.3% | 0.0% | ~167 | 0.5 | **Yes** (ok) |
| Combat | BASE | 30.2% | 0.0% | ~124 | 14.0 | **Yes** (ok) |
| Harbor | BASE | 27.4% | 0.0% | ~83 | 16.1 | **Yes** (ok) |
| Ocean | BASE | 21.9% | 0.0% | ~82 | 14.4 | **Yes** (ok) |
| Prop | FINAL | 7.3% | 0.0% | ~274 | 0.9 | **Yes** (strong) |
| PropHub | FINAL | 6.3% | 0.0% | ~195 | 0.8 | **Yes** (ok) |
| PropNose | FINAL | 0.0% | 0.0% | ~105 | 0.4 | **Yes** (ok) |
| Wide | FINAL | 47.8% | 0.5% | ~209 | 0.7 | **Yes** (strong) |
| YakBeauty | FINAL | 48.6% | 0.0% | ~413 | 1.0 | **Yes** (strong) |

## Densify verified
- Map size: **20167163** (20.2 MB)
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
- Usable: 11  Partial: 0  Failed: 0
- Prop recoverable: True
- YakBeauty strong: False
- Cockpit strong: True
- City strong: True

## Next
1. If Prop now Yes: replace HF boards with hero prop PBR + motion disc while keeping capture locked
2. Authored airframe materials (normal/roughness/AO dirt)
3. Niagara muzzle/explosion/prop wash
4. Keep FAIL until blind prefers Skyguard on all pillars

## Goal
NOT COMPLETE.
