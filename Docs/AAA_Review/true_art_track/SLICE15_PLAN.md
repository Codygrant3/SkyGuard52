# True-Art Slice15 - L72 (on L71 freeze)
Updated: 2026-08-01
Goal: formal Niagara shell/emitter author pass + denser capture-safe VFX language; no FOV point lights.

## Hard rules
1. No extra PointLight FOV stacks (L66 reject)
2. Keep L52 HF densify core in FOV
3. Behind-wall hero content only
4. Single small bounded Niagara + emissive cards/cores
5. Host 11/11 absolute else REJECT to L71

## Content
- ensure_slice15_vfx_library() creates/loads NS shells + NS_L72_*Auth variants + emitter shells when API allows
- denser prop concentric discs/blades/streaks
- combat emissive cards + cores/filaments/shells/debris
- city windows + ocean foam cards
- note: empty Niagara shells alone are not AAA; denser authored mesh VFX language is the capture-visible progress
