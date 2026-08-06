# AAA Critic Report — Loop 66

## Verdict: FAIL vs AAA (authoritative)
Loop66 uses yaw=0 (+X) cameras aimed into high-frequency checker boards and radial prop proxies with alternating unlit/PBR mats, plus triple-source capture (BASE/FINAL/SCENE when available).
Host Pillow RGB is authoritative. Even if Prop/Yak capture recovers, content remains densified kit/proxy — not MSFS / BF-COD class materials or authored Niagara beauty.
Updated: 2026-08-01T02:39:44-05:00

## Host Pillow RGB audit (best source per cam)
| Camera | Best src | black% | white% | uniq | edge | Usable |
|---|---|---|---|---|---|---|
| ADS | BASE | 11.2% | 0.0% | ~59 | 2.7 | **Partial** (partial) |
| City | FINAL | 19.9% | 8.8% | ~676 | 0.9 | **Yes** (strong) |
| Cockpit | FINAL | 0.0% | 67.3% | ~138 | 0.2 | **Partial** (partial) |
| Combat | BASE | 30.2% | 0.0% | ~124 | 14.0 | **Yes** (ok) |
| Harbor | BASE | 26.9% | 0.0% | ~84 | 16.1 | **Yes** (ok) |
| Ocean | BASE | 21.9% | 0.0% | ~82 | 14.4 | **Yes** (ok) |
| Prop | FINAL | 0.0% | 26.6% | ~108 | 0.2 | **Partial** (partial) |
| PropHub | FINAL | 0.2% | 16.5% | ~1006 | 1.0 | **Yes** (strong) |
| PropNose | FINAL | 0.0% | 0.5% | ~61 | 0.3 | **Partial** (partial) |
| Wide | FINAL | 4.0% | 35.7% | ~1057 | 0.4 | **Yes** (strong) |
| YakBeauty | BASE | 42.2% | 0.0% | ~67 | 10.7 | **Partial** (partial) |

## Densify verified
- Map size: **20208642** (20.2 MB)
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
- Usable: 6  Partial: 5  Failed: 0
- Prop recoverable: True
- YakBeauty strong: False
- Cockpit strong: False
- City strong: True

## Next
1. If Prop now Yes: replace HF boards with hero prop PBR + motion disc while keeping capture locked
2. Authored airframe materials (normal/roughness/AO dirt)
3. Niagara muzzle/explosion/prop wash
4. Keep FAIL until blind prefers Skyguard on all pillars

## Goal
NOT COMPLETE.

## Decision
**REJECT L66** — host usable 6/11 with 5 partial (ADS/Cockpit/Prop/PropNose/YakBeauty). Fall back freeze remains **L65 (11/11)**.
Likely regression: slice09 rim/fill/muzzle point lights + layered Niagara raised washout/low structure on FOV-critical cams.
Do not promote L66 materials/lights as freeze baseline.
