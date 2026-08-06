# True-Art Slice08 — L65 (on L64 freeze)
Updated: 2026-08-01
Goal: multi-slot hero material overrides + denser multi-mat panelization + multi-Niagara event language without L53 regression.

## Material system
- Reuse L63 HF + L64 AO/detail once-cached materials
- spawn_sm now supports mats=[slot0, slot1, ...] multi-slot assignment on hero proxies

## Content densify
- Aircraft multi-slot yak + denser plates/AO seams/rivets
- City multi-slot tower/apartment + denser facade language + harbor crane/ship/sub
- Combat multi-slot rifle/igla + densest multi-Niagara set yet (muzzle/smoke/tracer/shells/missile/igla/drone trail/explosion)
- Ocean denser foam/mist
- Impact denser spark/debris

## Gate
- host usable 11/11 required
- critic may still FAIL
