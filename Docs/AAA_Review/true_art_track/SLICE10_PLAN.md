# True-Art Slice10 - L67 (on L65 freeze)
Updated: 2026-08-01
Goal: thin capture-safe art after L66 lighting reject. Tiny emissive accents + single bounded Niagara only. No FOV point-light stacks. No layered multi-Niagara near boards.

## Hard rules (from L66 reject)
1. No extra PointLight actors near FOV boards
2. No layered multi-spawn Niagara stacks
3. Keep L52 HF densify core in FOV
4. Behind-wall accents only (x >= bx+3.4), small scales
5. Author/load existing L63/L64 mats; no dark PBR as sole FOV material

## Gate
- host usable 11/11 required else REJECT to L65
- critic may still FAIL

