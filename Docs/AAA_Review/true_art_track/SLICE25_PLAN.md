# True-Art Slice25 - L82 (on L81 freeze)
Updated: 2026-08-01
Goal: thin true-art on L81 KEEP — make combat/prop/ocean particle language more capture-visible and strengthen prop/airframe material response without host regression.

## Hard rules
1. No extra PointLight FOV stacks (L66 reject)
2. Keep L52 HF densify core in FOV
3. Behind-wall hero content only (x >= bx+3)
4. No L53 multi-stage hero stacks
5. Host 11/11 absolute else REJECT to L81
6. Author materials once and cache

## Multi-model sequence
1. Luna high farm (capture-safe densify proposals)
2. Luna max refine (shortlist)
3. Terra high architecture (materials/Niagara order)
4. Grok 4.5 challenge (L53/L66 risk audit)
5. Sol only on conflict
6. Codex implement L82 + capture
7. Host Pillow 11/11
8. Harsh critic FAIL until blind flips pillars
9. Opus 5 acceptance on receipts only

## Content targets (thin / capture-safe)
- New NS_L82_* systems: MuzzleCone, SparkSheet, ExplCore, PropDiscWash, FoamCrestLite, TracerRibbon, GunSmokeSheet, FlakBurst, CityGlow, ContrailRibbon, ShellEject, HitSpark, DebrisLite, ExhaustRibbon, MuzzleSpark, OceanCrest
- Combat: slightly denser muzzle/tracer/shell/debris fields + thin spark sheet (behind wall)
- Prop/Yak: denser motion-disc / wash bloom / exhaust ribbon (no FOV light)
- City: thin window/asphalt material response + CityGlow behind wall
- Ocean/Harbor: foam crest + spray sheet bounded
- ADS/Cockpit: thin HF only; no solid fills; optional tiny HitSpark additive

## Reject risks
- L53: multi-stage hero stacks behind wall
- L66: FOV point-light stacks
- Empty Niagara shells without capture-visible fallbacks (keep particle_field/burst_ring)

## Success criteria
- Host 11/11
- Prop/Yak/Cockpit/City remain strong
- Map growth modest vs L81
- Critic may still FAIL until blind prefers Skyguard

## Implement notes
- Base script: build_skyguard_aaa_loop81_true_art_slice24_capture.py
- Retarget PREFIX/OUT_DIR/RT/cam labels to L82
- Append ensure_slice25_vfx_library + thin densify block after Slice24 chain
- Host audit glob must match AAA_Cam_L82_*
