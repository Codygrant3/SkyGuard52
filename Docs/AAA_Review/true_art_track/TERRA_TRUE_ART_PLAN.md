# Terra True-Art Plan — L58 Slice 01

Phase: L58 first true-art slice: preserve the L52 high-frequency unlit-board foreground while adding a single rear-layer material/readability cluster and tiny, bounded combat/ocean VFX accents.
Freeze: Keep the L52 HF unlit boards unchanged and in FOV at x=bx+1/+2. All opaque authored meshes/material applications remain at x>=bx+3; only the listed tiny additive/emissive and Niagara elements may sit forward of that wall.

## First slice
- Name: Rear material anchor plus micro-VFX readability accents
- Loop: L58

### Materials
- **MAT-01-aircraft-metal-anchor** `/Game/Skyguard/Materials/M_Tex_airframe_metal` → One existing rear aircraft or aircraft-silhouette mesh; assign only its primary fuselage material slot. (hero_mesh_slot)
- **MAT-02-city-concrete-anchor** `/Game/Skyguard/Materials/M_Tex_concrete` → One existing rear coastal building facade or simple existing rear block mesh, facing camera at a shallow readable angle. (behind_wall)
- **MAT-03-city-brick-breakup** `/Game/Skyguard/Materials/M_Tex_brick` → One adjacent, smaller existing rear facade or wall segment. (behind_wall)
- **MAT-04-engine-emissive-pin** `/Game/Skyguard/Materials/M_ExhaustGlow` → One tiny existing engine-nozzle or exhaust-card slot on the MAT-01 aircraft. (additive_emissive)

### Niagara
- **VFX-01-muzzle-readability** `/Game/Skyguard/VFX/NS_MuzzleFlash` stages=['Stage 3: attach one system to the existing weapon muzzle only after the L52/rear-material composition is locked.', 'Stage 4: capture a single 0.05-0.10 s burst frame; disable for all non-burst validation frames.'] budget=1 concurrent system; 1 burst; <=0.10 s visible; <=1% image width; no persistent light.
- **VFX-02-ocean-contact-accent** `/Game/Skyguard/VFX/NS_OceanSpray` stages=['Stage 3: place one emitter at a distant waterline/contact point behind the wall.', 'Stage 4: capture only if the particle cluster remains separated from the horizon and does not veil the ocean.'] budget=1 concurrent system; <=24 visible particles; <=0.75 s lifetime; <=2% image width; no screen-space fog.
- **VFX-03-impact-event** `/Game/Skyguard/VFX/NS_HitSparks` stages=['Stage 3: stage one rear impact point on the MAT-02 concrete anchor or a nearby existing rear hard-surface target.', 'Stage 4: capture one short event frame only; disable for baseline and all clean-material frames.'] budget=1 concurrent system; 1 event; <=12 visible sparks; <=0.20 s lifetime; <=1% image width.

### Acceptance
- 11/11 L58 captures are usable, with no composition regression versus L57 and no modification to L52 board placement/material behavior.
- Primary clean frame visibly distinguishes textured aircraft metal, concrete, and brick at normal review scale; materials do not read as a single dark PBR mass.
- Aircraft remains a single readable rear silhouette with a restrained exhaust pin and no rear-stack collapse.
- City reads as two restrained material classes while remaining behind the wall and below 15% combined frame coverage.
- Ocean/horizon remains legible without global spray, fog, heavy bloom, or extreme sky/sun washout.
- At least one event frame has a localized muzzle flash and one has localized impact/ocean energy; both remain small enough that the clean frame is still the hero evidence.
- No new asset lookup, shader fallback, missing reference, spawn error, or Niagara persistence warning is present in the L58 capture log.

### Do not
- Do not repeat L53 hero-mesh stacks, foreground PBR replacements, or multi-layer aircraft assemblies.
- Do not add new Megascans, unavailable paths, landscapes, ocean replacements, weapon meshes, ADS camera changes, or large city kits.
- Do not use dark PBR as the only visible FOV surface.
- Do not move, delete, rescale, or materially alter the L52 HF boards.
- Do not add persistent smoke, full-frame particles, broad emissive cards, or more than one concurrent instance of each listed Niagara system.
- Do not tune sun, sky, auto-exposure, or post-process to hide material shortcomings.
