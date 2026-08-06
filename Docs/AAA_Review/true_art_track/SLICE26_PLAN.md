# True-Art Slice26 - L83 (on L82 freeze)
Updated: 2026-08-01
Goal: thin true-art on L82 KEEP — deepen capture-visible combat/prop/ocean particle language and airframe material response without host regression.

## Hard rules
1. No extra PointLight FOV stacks (L66 reject)
2. Keep L52 HF densify core in FOV
3. Behind-wall hero content only (x >= bx+3)
4. No L53 multi-stage hero stacks
5. Host 11/11 absolute else REJECT to L82
6. Author materials once and cache

## Multi-model sequence
1. Luna high farm
2. Luna max refine
3. Terra high architecture
4. Grok 4.5 challenge
5. Sol only on conflict
6. Codex implement L83 + capture
7. Host Pillow 11/11
8. Harsh critic FAIL until blind flips pillars
9. Opus 5 acceptance on receipts only

## Content targets (thin / capture-safe)
- New NS_L83_* systems: MuzzlePetal, SparkArc, ExplShock, PropWashDisc, FoamRibbon, TracerCoreLite, GunSmokeRibbon, FlakPetal, CitySparkLite, ContrailSoft, ShellSpark, HitFlash, DebrisSpark, ExhaustSoft, MuzzleHalo, OceanRibbon
- Combat: thin muzzle/tracer/shell/debris fields + spark arc (behind wall)
- Prop/Yak: motion-disc wash + exhaust soft ribbon
- City: CitySparkLite + window material response behind wall
- Ocean/Harbor: foam ribbon + spray bounded
- ADS/Cockpit: thin HF only + optional tiny HitFlash

## Success criteria
- Host 11/11
- Prop/Yak/Cockpit/City remain strong
- Map growth modest vs L82
- Critic may still FAIL until blind prefers Skyguard

## Implement notes
- Base script: build_skyguard_aaa_loop82_true_art_slice25_capture.py
- Retarget PREFIX/OUT_DIR/RT/cam labels to L83
- Append ensure_slice26_vfx_library + thin densify after Slice25 chain
- Host audit glob must match AAA_Cam_L83_*
