# Selected Luna proposals for next densify loop
Base freeze: **L56** densify+thin-art (11/11). L52 densify recipe; L53 rejected; L54/L55/L56 kept.
Wave: wave04
Model: gpt-5.6-luna
Generated: 2026-08-01T00:27:55
Usable gate required: **11/11**

## Job summary
- materials: status=ok count=20 exit=EXIT=0
- aircraft: status=ok count=20 exit=EXIT=0
- city_ocean: status=ok count=20 exit=EXIT=0
- weapon_ads: status=ok count=20 exit=EXIT=0
- vfx: status=ok count=20 exit=EXIT=0

## Keep rules
- Preserve L52 HF densify exactly
- Prefer additive_emissive or tiny behind_wall accents
- No large multi-stage hero stacks (L53 failure mode)
- Protect Prop/PropNose/YakBeauty/City/Ocean/Wide

## Implement list (A-band capped)
1. MAT-040 - Behind-wall salt-streak roughness - stages=Combat|Harbor - score=93.5 - risk=low - placement=behind_wall
2. AIR-024 - Cowling inspection-plate gap - stages=YakBeauty - score=93.5 - risk=low - placement=behind_wall
3. MAT-036 - Behind-wall vertical oxidation variation - stages=Combat - score=93.5 - risk=low - placement=behind_wall
4. VFX-021 - Ocean spray pinpoint droplets - stages=Ocean|Harbor - score=92.5 - risk=low - placement=additive_emissive
5. VFX-003 - Muzzle flash twin filament streaks - stages=Cockpit|ADS - score=92.5 - risk=low - placement=additive_emissive
6. CO-022 - Submarine Hull Panel Highlight - stages=Ocean|Harbor - score=91.0 - risk=low - placement=behind_wall
7. CO-023 - Coast Block Utility Boxes - stages=City|Wide - score=91.0 - risk=low - placement=behind_wall

## Artifacts
- Combined: D:\Skyguard52\Docs\AAA_Review\luna_farm\wave04\wave04_all_proposals.json
- Ranked: D:\Skyguard52\Docs\AAA_Review\luna_farm\wave04\wave04_ranked.csv
- Summary: D:\Skyguard52\Docs\AAA_Review\luna_farm\wave04\wave04_job_summary.json

## Acceptance
- host usable 11/11
- no camera falls to Partial/No vs L52
- critic notes any pillar movement; overall may still FAIL
