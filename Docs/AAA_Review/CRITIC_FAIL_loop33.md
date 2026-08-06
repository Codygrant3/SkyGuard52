# AAA Critic Report — Loop 33

## Verdict: FAIL vs AAA (authoritative)
Loop33 uses yaw=0 (+X) cameras aimed into high-frequency checker boards and radial prop proxies with alternating unlit/PBR mats, plus triple-source capture (BASE/FINAL/SCENE when available).
Host Pillow RGB is authoritative. Even if Prop/Yak capture recovers, content remains densified kit/proxy — not MSFS / BF-COD class materials or authored Niagara beauty.
Updated: 2026-07-31T20:26:32-05:00

## Host Pillow RGB audit (best source per cam)
| Camera | Best src | black% | white% | uniq | edge | Usable |
|---|---|---|---|---|---|---|
| ADS | FINAL | 51.0% | 0.0% | ~92 | 0.4 | **Yes** (ok) |
| City | BASE | 100.0% | 0.0% | ~1 | 0.0 | **No** (too black) |
| Cockpit | BASE | 0.0% | 0.0% | ~3 | 0.0 | **No** (low unique) |
| Combat | FINAL | 0.0% | 0.0% | ~13 | 0.0 | **No** (low unique) |
| Harbor | BASE | 14.4% | 0.0% | ~59 | 1.4 | **Partial** (partial) |
| Ocean | FINAL | 87.1% | 2.0% | ~1009 | 2.5 | **Partial** (too black) |
| Prop | FINAL | 5.2% | 0.0% | ~355 | 1.3 | **Yes** (strong) |
| PropHub | FINAL | 13.1% | 0.9% | ~521 | 0.6 | **Yes** (strong) |
| PropNose | FINAL | 16.4% | 0.2% | ~457 | 0.7 | **Yes** (strong) |
| Wide | BASE | 53.4% | 0.0% | ~62 | 1.4 | **Partial** (partial) |
| YakBeauty | FINAL | 35.7% | 6.2% | ~679 | 1.7 | **Yes** (strong) |

## Densify verified
- Map size: **8546293** (8.5 MB)
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
- Usable: 5  Partial: 3  Failed: 3
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
