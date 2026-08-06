# True-Art Slice09 — L66 (on L65 freeze)
Updated: 2026-08-01
Goal: stronger lighting-response materials + layered Niagara language + local rim/fill lights without L53 regression.

## Material system
- Reuse L63 HF + L64 AO/detail + L65 multi-slot once-cached materials
- Add once-authored lighting-response variants: M_L66_*Lit / M_L66_MuzzleHot (load-existing preferred)
- No dark PBR as sole FOV material; hero lit panels stay behind wall (x >= bx+3)

## Content densify
- Aircraft: lit airframe/plate/rust panels + rim/fill lights on Yak/Prop/Cockpit/ADS
- City/Harbor/Wide: lit brick/concrete panels + warm city lamps
- Combat/ADS/Wide: layered NS_MuzzleFlash/GunSmoke/HitSparks/DroneExplosion + hot muzzle core light
- Ocean/Harbor/Wide: layered NS_OceanSpray + CloudWisps
- Prop/Yak: layered PropWash + ContrailRibbon

## Gate
- host usable 11/11 required
- critic may still FAIL (stub Niagara still not AAA beauty)

## Capture law
- Keep L52 HF densify core in FOV
- Author materials once and cache
- No extreme sun/sky washout
