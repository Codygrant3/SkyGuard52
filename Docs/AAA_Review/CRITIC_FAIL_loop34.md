# AAA Critic Report — Loop 34

## Verdict: FAIL vs AAA (authoritative)
Loop34 uses yaw=0 (+X) cameras aimed into high-frequency checker boards and radial prop proxies with alternating unlit/PBR mats, plus triple-source capture (BASE/FINAL/SCENE when available).
Host Pillow RGB is authoritative. Even if Prop/Yak capture recovers, content remains densified kit/proxy — not MSFS / BF-COD class materials or authored Niagara beauty.
Updated: 2026-07-31T20:33:04-05:00

## Host Pillow RGB audit (best source per cam)
| Camera | Best src | black% | white% | uniq | edge | Usable |
|---|---|---|---|---|---|---|
| ADS | FINAL | 70.9% | 0.0% | ~87 | 0.4 | **Partial** (too black) |
| City | FINAL | 0.0% | 0.0% | ~14 | 0.0 | **No** (low unique) |
| Cockpit | BASE | 0.0% | 0.0% | ~2 | 0.0 | **No** (low unique) |
| Combat | FINAL | 0.6% | 61.3% | ~685 | 0.4 | **Yes** (strong) |
| Harbor | FINAL | 12.0% | 0.8% | ~227 | 0.4 | **Yes** (strong) |
| Ocean | FINAL | 15.8% | 6.1% | ~586 | 0.8 | **Yes** (strong) |
| Prop | FINAL | 5.2% | 0.0% | ~348 | 1.1 | **Yes** (strong) |
| PropHub | FINAL | 13.1% | 0.9% | ~513 | 0.6 | **Yes** (strong) |
| PropNose | FINAL | 10.6% | 2.0% | ~541 | 0.9 | **Yes** (strong) |
| Wide | FINAL | 36.6% | 8.2% | ~697 | 1.0 | **Yes** (strong) |
| YakBeauty | FINAL | 9.9% | 18.9% | ~1679 | 1.3 | **Yes** (strong) |

## Densify verified
- Map size: **13687275** (13.7 MB)
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
- Usable: 8  Partial: 1  Failed: 2
- Prop recoverable: True
- YakBeauty strong: True
- Cockpit strong: False
- City strong: False

## Next
1. If Prop now Yes: replace HF boards with hero prop PBR + motion disc while keeping capture locked
2. Authored airframe materials (normal/roughness/AO dirt)
3. Niagara muzzle/explosion/prop wash
4. Keep FAIL until blind prefers Skyguard on all pillars

## Goal
NOT COMPLETE.
