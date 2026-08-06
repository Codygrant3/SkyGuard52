# AAA Critic Report — Loop 48

## Verdict: FAIL vs AAA (authoritative)
Loop48 uses yaw=0 (+X) cameras aimed into high-frequency checker boards and radial prop proxies with alternating unlit/PBR mats, plus triple-source capture (BASE/FINAL/SCENE when available).
Host Pillow RGB is authoritative. Even if Prop/Yak capture recovers, content remains densified kit/proxy — not MSFS / BF-COD class materials or authored Niagara beauty.
Updated: 2026-07-31T22:40:33-05:00

## Host Pillow RGB audit (best source per cam)
| Camera | Best src | black% | white% | uniq | edge | Usable |
|---|---|---|---|---|---|---|
| ADS | BASE | 0.0% | 0.0% | ~3 | 0.0 | **No** (low unique) |
| City | BASE | 14.5% | 0.0% | ~76 | 14.4 | **Partial** (partial) |
| Cockpit | BASE | 0.0% | 0.0% | ~2 | 0.0 | **No** (low unique) |
| Combat | BASE | 14.9% | 0.0% | ~67 | 11.6 | **Partial** (partial) |
| Harbor | BASE | 8.2% | 0.0% | ~98 | 16.0 | **Yes** (ok) |
| Ocean | BASE | 8.4% | 0.0% | ~82 | 6.6 | **Yes** (ok) |
| Prop | BASE | 0.0% | 0.0% | ~3 | 0.0 | **No** (low unique) |
| PropHub | BASE | 0.0% | 0.0% | ~3 | 0.0 | **No** (low unique) |
| PropNose | BASE | 0.0% | 0.0% | ~5 | 0.0 | **No** (low unique) |
| Wide | FINAL | 34.6% | 10.1% | ~267 | 0.5 | **Yes** (strong) |
| YakBeauty | BASE | 11.1% | 0.0% | ~65 | 10.5 | **Partial** (partial) |

## Densify verified
- Map size: **12822003** (12.8 MB)
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
- Usable: 3  Partial: 3  Failed: 5
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
