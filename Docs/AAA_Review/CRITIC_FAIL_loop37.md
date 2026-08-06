# AAA Critic Report — Loop 37

## Verdict: FAIL vs AAA (authoritative)
Loop37 uses yaw=0 (+X) cameras aimed into high-frequency checker boards and radial prop proxies with alternating unlit/PBR mats, plus triple-source capture (BASE/FINAL/SCENE when available).
Host Pillow RGB is authoritative. Even if Prop/Yak capture recovers, content remains densified kit/proxy — not MSFS / BF-COD class materials or authored Niagara beauty.
Updated: 2026-07-31T20:53:53-05:00

## Host Pillow RGB audit (best source per cam)
| Camera | Best src | black% | white% | uniq | edge | Usable |
|---|---|---|---|---|---|---|
| ADS | FINAL | 6.8% | 0.0% | ~182 | 0.4 | **Yes** (ok) |
| City | FINAL | 0.0% | 0.0% | ~14 | 0.0 | **No** (low unique) |
| Cockpit | FINAL | 0.0% | 0.0% | ~57 | 0.2 | **Partial** (low structure) |
| Combat | FINAL | 0.0% | 0.0% | ~14 | 0.0 | **No** (low unique) |
| Harbor | FINAL | 0.0% | 0.0% | ~43 | 0.3 | **Partial** (partial) |
| Ocean | FINAL | 0.0% | 0.0% | ~45 | 0.3 | **Partial** (partial) |
| Prop | FINAL | 0.0% | 0.0% | ~41 | 0.1 | **Partial** (low structure) |
| PropHub | FINAL | 0.0% | 0.0% | ~57 | 0.2 | **Partial** (low structure) |
| PropNose | FINAL | 0.0% | 0.0% | ~53 | 0.2 | **Partial** (low structure) |
| Wide | FINAL | 7.9% | 0.0% | ~29 | 0.4 | **No** (low unique) |
| YakBeauty | FINAL | 0.0% | 0.0% | ~15 | 0.0 | **No** (low unique) |

## Densify verified
- Map size: **10265187** (10.3 MB)
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
- Usable: 1  Partial: 6  Failed: 4
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
