# True-Art Slice16 - L73 (on L72 freeze)
Updated: 2026-08-01
Goal: deepen Niagara emitter authoring + denser capture-visible particle language; no FOV point lights.

## Hard rules
1. No extra PointLight FOV stacks (L66 reject)
2. Keep L52 HF densify core in FOV
3. Behind-wall hero content only
4. Bounded Niagara + denser visible particle fields/rings
5. Host 11/11 absolute else REJECT to L72

## Content
- deepen ensure_authored_ns (attach emitter when API allows, fixed bounds/warmup)
- new NS_L73_*Auth variants (MuzzleBurst/SparkRing/ExplPlume/FoamBurst/ContrailDense)
- spawn_particle_field + spawn_burst_ring for still-readable pseudo-particles
- denser prop discs/blades + combat explosion fields
