# True-Art Slice17 - L74 (on L73 freeze)
Updated: 2026-08-01
Goal: thin true-art on L73 KEEP — prioritize **visible** VFX beauty and prop/airframe response without capture regression.

## Hard rules
1. No extra PointLight FOV stacks (L66 reject)
2. Keep L52 HF densify core in FOV
3. Behind-wall hero content only (x >= bx+3) or tiny additive/Niagara
4. No L53 multi-stage hero stacks
5. Host 11/11 absolute else REJECT to L73
6. Author materials once and cache; prefer load-existing Generated mats

## Multi-model sequence (required for Slice17)
1. **Luna high farm** — capture-safe densify proposals focused on:
   - VFX visible particle language (muzzle/spark/explosion/prop-wash/foam)
   - Prop/airframe lighting response under baseline exposure
   - ADS/cockpit thin HF (no solid fills)
2. **Luna max refine** — shortlist 5-8 recipes that cannot violate capture law
3. **Terra high architecture** — order materials → Niagara → densify stages; one thin compound wave only
4. **Grok 4.5 challenge** — reject L53/L66-class risks before implement
5. **Sol** — only if Terra vs Grok conflict
6. **Codex implement** — single L74 script + capture
7. **Host Pillow 11/11** gate
8. **Harsh critic** still FAIL until blind flips pillars
9. **Opus 5 acceptance** — non-implementing, on receipts only

## Content targets (thin)
- Deepen real Niagara emitter graphs where UE Python API allows; keep bounded scales
- Keep/extend spawn_particle_field + spawn_burst_ring only as secondary still-readable language
- Prop motion disc PBR response without washing FOV
- Airframe ANR accents behind wall only
- Combat explosion field readability without layered FOV light

## Out of scope this slice
- FOV point lights
- Hero stack densify gambles
- Claiming AAA complete
- Replacing L52 HF core wholesale

## Success criteria
- Host: usable 11 / partial 0 / failed 0
- Map size stays capture-stable (~20-25 MB class)
- Prop/Yak/Cockpit/City remain strong or improve
- Critic may still FAIL (expected) until blind prefers Skyguard on materials/aircraft/city-ocean/weapon/VFX
