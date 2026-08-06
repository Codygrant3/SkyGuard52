# AAA Critic Report — Loop 18

## Verdict: FAIL vs AAA (authoritative)
Capture is partially unblocked (non-black frames exist), but content is **not AAA**. Usable frames are dominated by unlit orange/yellow proof slabs and black voids. A blind A/B against MSFS prop-plane or modern BF/COD coastal combat stills would pick the reference every time.

Updated: 2026-07-31T18:55:00-05:00

## Pixel / content audit (Pillow)
| Still | black% | uniq | edge | Usable? | Visual read |
|---|---|---|---|---|---|
| ADS | 0.0% | ~281 | 5.9 | Yes | Flat yellow/orange unlit fields — proof geometry only |
| Proof | 0.0% | ~74 | 1.2 | No | Near-solid orange emissive wash |
| Combat | 51% | ~1898 | 15.9 | Yes | Orange slabs + black half-frame; no readable aircraft/city |
| Prop | 48.5% | ~1643 | 11.2 | Yes | Mixed black/white/orange; no Yak silhouette fidelity |
| Ocean | 86.7% | ~357 | 9.1 | No | Mostly black with sparse highlights |
| City/Harbor/Cockpit/YakBeauty | 93–100% | low | low | No | Black / failed |

## Systems present (not visual AAA)
- Map ~13.7 MB after Loop18 densify
- Prop spinner C++ class
- Runtime combat VFX helper
- WaterBodyOcean (Loop14)
- Generated PBR mats + unlit proof mats
- Capture writes SHA256 manifests

## Harsh blind pillar judgment
| Pillar | Winner | Why |
|---|---|---|
| Materials | Reference | Unlit proof colors ≠ weathered PBR hero stacks |
| City/Ocean | Reference | Still proxy/black; no MSFS coastline fidelity |
| Aircraft | Reference | No readable Yak beauty/cockpit stills |
| Weapon/ADS | Reference | ADS still is proof wash, not iron sights |
| VFX | Reference | No authored Niagara; combat frame not VFX-readable |
| Capture | Partial | Non-black possible, but not production beauty stills |
| Overall | **Reference** | Blind pick: AAA refs |

## Blind call
If shown ADS/Combat/Prop stills next to MSFS Yak-class exterior/cockpit or BF coastal combat frames, critic picks references immediately. Skyguard frames look like debug unlit markers, not a shipped AAA game.

## Next required (Loop19+)
1. Fix lit path: movable key/fill/sky intensities via light components; exposure lock
2. Dual capture: BaseColor + FinalColor; reject stills with edge energy < 8 or dominated by single hue
3. Hero densify: continuous Yak assembly silhouette, ocean water material response, city blocks with real facade textures
4. Only claim pillar progress from stills that pass usability gates AND look like the pillar
5. Keep overall FAIL until blind A/B prefers Skyguard on every pillar

## Goal
NOT COMPLETE.
