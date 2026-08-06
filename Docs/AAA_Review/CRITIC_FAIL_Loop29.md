# AAA Critic Report — Loop 29

## Verdict: FAIL vs AAA (authoritative)
Loop29 uses yaw=0 (+X) cameras aimed into high-frequency checker boards and radial prop proxies with alternating unlit/PBR mats, plus triple-source capture (BASE/FINAL/SCENE when available).
Host Pillow RGB is authoritative. Even if Prop/Yak capture recovers, content remains densified kit/proxy — not MSFS / BF-COD class materials or authored Niagara beauty.
Updated: 2026-07-31T20:01:42-05:00

## Host Pillow RGB audit (best source per cam)
| Camera | Best src | black% | white% | uniq | edge | Usable |
|---|---|---|---|---|---|---|
| ADS | FINAL | 55.3% | 0.0% | ~120 | 0.4 | **Partial** (too black) |
| City | BASE | 12.7% | 0.0% | ~59 | 2.0 | **Partial** (partial) |
| Cockpit | BASE | 0.0% | 0.0% | ~2 | 0.0 | **No** (low unique) |
| Combat | FINAL | 24.1% | 8.4% | ~578 | 0.9 | **Yes** (strong) |
| Harbor | FINAL | 21.3% | 40.2% | ~238 | 1.5 | **Yes** (strong) |
| Ocean | FINAL | 23.4% | 48.5% | ~506 | 0.5 | **Yes** (strong) |
| Prop | FINAL | 3.9% | 0.0% | ~81 | 0.3 | **Yes** (ok) |
| PropHub | FINAL | 0.0% | 0.0% | ~17 | 0.0 | **No** (low unique) |
| PropNose | FINAL | 0.0% | 0.0% | ~17 | 0.0 | **No** (low unique) |
| Wide | FINAL | 52.0% | 0.7% | ~567 | 1.7 | **Yes** (strong) |
| YakBeauty | FINAL | 37.5% | 0.6% | ~476 | 1.3 | **Yes** (strong) |

## Densify verified
- Map size: **8945406** (8.9 MB)
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
- Usable: 6  Partial: 2  Failed: 3
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
