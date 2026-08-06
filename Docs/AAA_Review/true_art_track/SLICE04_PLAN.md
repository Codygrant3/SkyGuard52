# True-Art Slice04 — L61 (on L60 freeze)
Updated: 2026-08-01
Goal: author Slice04 material graphs (bright-readable basecolor/rough/metal/spec/emissive) and expand multi-Niagara clusters without L53 stack regression.

## Authored materials (/Game/Skyguard/Materials/Generated)
- M_L61_AirframeBright, M_L61_PlateBright, M_L61_RustWarm
- M_L61_ConcreteLit, M_L61_BrickWarm, M_L61_PlasterLit, M_L61_GlassLit
- M_L61_MuzzleHot, M_L61_FoamLit, M_L61_Waterline

## Niagara expansion
- Prop: NS_PropWash
- Combat/ADS: NS_MuzzleFlash + NS_GunSmoke + NS_TracerBurst
- Ocean: NS_OceanSpray + NS_WaterSplash
- Impact: NS_HitSparks + NS_FlakBurst

## Gate
- host usable 11/11 required
- critic may still FAIL

## L61 result
- Capture stills=33
- Host usable **11/11**
- Decision: **KEEP**
- Authored materials present under Content/Skyguard/Materials/Generated/M_L61_*
- Critic overall still **FAIL vs AAA**
- Perf note: ensure_slice04_materials re-ran per stage; cache next loop

