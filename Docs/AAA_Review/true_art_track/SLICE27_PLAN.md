# True-Art Slice27 - L84 (on L83 freeze)
Updated: 2026-08-01
Goal: thin true-art on L83 KEEP — deepen capture-visible combat/prop/ocean particle language and airframe material response without host regression.

## Hard rules
1. No extra PointLight FOV stacks (L66 reject)
2. Keep L52 HF densify core in FOV
3. Behind-wall hero content only (x >= bx+3)
4. No L53 multi-stage hero stacks
5. Host 11/11 absolute else REJECT to L83
6. Author materials once and cache
7. Host audit glob AAA_Cam_L84_*

## Multi-model sequence
1. Luna high farm
2. Luna max refine
3. Terra high architecture
4. Grok 4.5 challenge
5. Sol only on conflict
6. Codex implement L84 + capture
7. Host Pillow 11/11
8. Harsh critic FAIL until blind flips pillars
9. Opus 5 acceptance on receipts only

## Content targets (thin / capture-safe)
- New NS_L84_* systems: MuzzleBloomLite, SparkFilament, ExplHalo, PropDiscGlow, FoamSheetLite, TracerBloom, GunSmokeWisp, FlakCoreLite, CityEmberLite, ContrailMist, ShellFlash, HitCoreLite, DebrisMist, ExhaustMist, MuzzleCoreSoft, OceanMist
- Combat: thin muzzle/tracer/shell/debris + spark filament (behind wall)
- Prop/Yak: motion-disc glow + exhaust mist
- City: CityEmberLite + window response behind wall
- Ocean/Harbor: foam sheet lite + ocean mist bounded
- ADS/Cockpit: thin HF only + optional tiny HitCoreLite

## Success criteria
- Host 11/11
- Prop/Yak/Cockpit/City remain strong
- Map growth modest vs L83
- Critic may still FAIL until blind prefers Skyguard

## Implement notes
- Base script: build_skyguard_aaa_loop83_true_art_slice26_capture.py
- Retarget PREFIX/OUT_DIR/RT/cam labels to L84
- Append ensure_slice27_vfx_library + thin densify after Slice26 chain
- Host audit must use AAA_Cam_L84_* (not previous loop)
