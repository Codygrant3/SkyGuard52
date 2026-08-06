# AAA Critic Report — Loop 45

## Verdict: FAIL vs AAA (authoritative)
Loop45 uses yaw=0 (+X) cameras aimed into high-frequency checker boards and radial prop proxies with alternating unlit/PBR mats, plus triple-source capture (BASE/FINAL/SCENE when available).
Host Pillow RGB is authoritative. Even if Prop/Yak capture recovers, content remains densified kit/proxy — not MSFS / BF-COD class materials or authored Niagara beauty.
Updated: 2026-07-31T22:34:39-05:00

## Host Pillow RGB audit (best source per cam)
| Camera | Best src | black% | white% | uniq | edge | Usable |
|---|---|---|---|---|---|---|
| ADS | BASE | 2.8% | 0.0% | ~41 | 21.7 | **Partial** (partial) |
| City | BASE | 31.7% | 0.0% | ~73 | 14.3 | **Partial** (partial) |
| Cockpit | BASE | 21.4% | 0.0% | ~39 | 14.6 | **No** (low unique) |
| Combat | BASE | 34.6% | 0.0% | ~67 | 15.0 | **Partial** (partial) |
| Harbor | BASE | 28.2% | 0.0% | ~83 | 15.8 | **Yes** (ok) |
| Ocean | BASE | 21.9% | 0.0% | ~82 | 14.4 | **Yes** (ok) |
| Prop | FINAL | 7.3% | 0.0% | ~274 | 0.9 | **Yes** (strong) |
| PropHub | FINAL | 6.3% | 0.0% | ~195 | 0.8 | **Yes** (ok) |
| PropNose | FINAL | 0.0% | 0.0% | ~105 | 0.4 | **Yes** (ok) |
| Wide | FINAL | 47.8% | 0.5% | ~209 | 0.7 | **Yes** (strong) |
| YakBeauty | FINAL | 47.7% | 0.0% | ~432 | 1.0 | **Yes** (strong) |

## Densify verified
- Map size: **11833877** (11.8 MB)
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
- Usable: 7  Partial: 3  Failed: 1
- Prop recoverable: True
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
