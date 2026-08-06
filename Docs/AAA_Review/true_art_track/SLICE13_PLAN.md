# True-Art Slice13 - L70 (on L69 freeze)
Updated: 2026-08-01
Goal: VFX core language + stronger airframe/city material response; no FOV point lights.

## Hard rules
1. No extra PointLight FOV stacks (L66 reject)
2. Keep L52 HF densify core in FOV
3. Behind-wall hero content only (x >= bx+3)
4. Single small bounded Niagara + readable mesh VFX cores
5. Host 11/11 absolute else REJECT to L69

## Content
- Airframe response mats M_L70_*Resp (fallback L68 ANR)
- Prop disc/blades + yak multi-slot + exhaust pin
- Combat/ADS: rifle multi-slot + muzzle/smoke/sparks + cores/filaments/shells
- City/ocean: brick/concrete response + windows + foam + bounded spray
