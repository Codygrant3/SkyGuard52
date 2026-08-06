# Skyguard 52 — Release Definition of Done

Generated: 2026-08-04  
Project: `D:\Skyguard52`  
Target: Windows production release built with Unreal Engine 5.8 and Blender-authored hero assets

The release is done only when every item below is supported by immutable current-candidate evidence. File presence, an editor prototype, an exit code, an offline contract, or the old Phase 8 engineering baseline cannot substitute for a required packaged result.

## 1. Campaign

- [ ] Ten missions are present, distinct, playable and finishable.
- [ ] Each mission has a unique flight route, briefing, objective structure, skyline, landmarks, weather, lighting, pacing, threats and boss.
- [ ] Mission geometry reuse is approximately 65–70% modular without duplicated layouts.
- [ ] Every mission has three to ten exclusive hero assets.
- [ ] Every boss has an introduction, readable telegraphs, weak points, multiple phases, destruction and aftermath.
- [ ] Campaign progression, mission unlocks, scoring, debriefing and save/load survive relaunch.
- [ ] The full campaign passes on a clean machine.

## 2. Yak-52 and cockpit

- [ ] Verified dimensions and silhouettes pass.
- [ ] Fuselage, wings, wing roots, cowling, radial opening, propeller, spinner, tail and landing gear pass direct art review.
- [ ] Canopy proportions, bows, glazing, front pilot compartment and open rear-gunner arrangement pass.
- [ ] Instrument panels, controls, seats, harnesses, padding, interior panels and cockpit equipment pass.
- [ ] Exterior panels, rivets, fasteners, seams, vents, hatches, decals, wear, oil, grime, soot, salt and wetness pass.
- [ ] Pivots, collision, sockets, hierarchy, animation and damage states are correct.
- [ ] Pilot, gunner, rifle and Igla do not clip through each other, the canopy, fuselage or wings during supported gameplay.

## 3. Player and weapons

- [ ] Pilot and rear-gunner characters are production quality.
- [ ] Arms, hands and leather gloves are anatomically convincing in every gameplay view.
- [ ] Rifle model, iron sights, ADS alignment, recoil, reload, muzzle, projectiles, impacts and animations pass.
- [ ] Right mouse holds ADS while left mouse continues to fire.
- [ ] No artificial firearm reticle or crosshair appears during normal play.
- [ ] Firing arcs prevent the rifle or Igla from harming the pilot or aircraft.
- [ ] Igla model, missile orientation, launch point, lock feedback, launch, tracking, impact and reload pass.
- [ ] Input is remappable and mouse sensitivity, ADS sensitivity and invert options persist.
- [ ] Supported controller flows pass if controller support is advertised.

## 4. Enemies, bosses and destruction

- [ ] Shahed and heavy-drone variants pass production-art review.
- [ ] Bosses are production quality and visually distinct.
- [ ] Weak points, damage feedback, detached components and phase transitions are readable.
- [ ] Fire, smoke, debris, sparks and explosions are physically coherent and appropriately scaled.
- [ ] No explosion uses an arcade placeholder or “pew” sound.
- [ ] Debris, particles, audio and destruction assets are pooled/prewarmed/bounded.
- [ ] Drone and boss destruction never causes a multi-second stall.

## 5. Environments and visual quality

- [ ] Ocean, waterline, beach, dunes and terrain transitions are convincing.
- [ ] Buildings, roads, trees, cars, cranes, ships, landmarks and district terrain remain fixed to the world and grounded.
- [ ] No floating, disconnected, repeating-placeholder, long-slab, low-poly hero or diagnostic geometry is visible.
- [ ] Water, clouds, foliage and world geometry are temporally stable as the plane banks or the camera moves.
- [ ] Every mission's atmosphere, fog, clouds, exposure, shadow detail and lighting pass.
- [ ] Camera and weapon views do not clip.
- [ ] Nanite/LOD/HLOD, PCG, streaming and texture strategies preserve quality at rear-gunner flight speed.
- [ ] All representative captures are inspected at original resolution.

## 6. Presentation and audio

- [ ] Briefing screens contain mission-specific intelligence, radio chatter, threat pictograms and a concise flight card.
- [ ] Briefings hide required shader and asset warmup without extending total mission-start time.
- [ ] UI uses a coherent military-aviation visual language and remains readable.
- [ ] HUD avoids unnecessary arcade elements and supports diegetic cues where feasible.
- [ ] Engine, propeller, wind, canopy, rifle, missile, impacts, explosions, debris, radio, city, ocean and weather audio are realistic and spatially coherent.
- [ ] Occlusion, attenuation, concurrency, mix states and first-use preload pass.
- [ ] Subtitles, master/effects/dialogue/music sliders and accessibility options pass.
- [ ] Tutorial and onboarding teach looking, firing, ADS, weapon switching, Igla locking and objectives.

## 7. Gameplay and mission flow

- [ ] Startup, title/menu, settings, mission select, briefing, warmup, gameplay, pause, success/failure, debrief and progression work in packaged builds.
- [ ] Rifle hip fire and ADS fire work throughout every mission.
- [ ] Igla select, lock, launch, tracking, impact and reload work against intended targets.
- [ ] Boss encounters can be completed through intended mechanics.
- [ ] Objectives, scoring, success and failure conditions cannot soft-lock.
- [ ] Mission restarts, transitions and consecutive mission loads work repeatedly.
- [ ] Save data handles first run, normal relaunch, version migration and corrupted/missing data safely.

## 8. Performance and stability

- [ ] The frozen 2560×1440 Epic D3D12 SM6 primary profile passes the absolute budget.
- [ ] Mean frame time is at most 16.7 ms.
- [ ] P95 frame time is at most 22.2 ms.
- [ ] P99 frame time is at most 33.3 ms.
- [ ] No measured gameplay frame exceeds 50 ms.
- [ ] No five-second destruction, ADS/fire, streaming or audio stall occurs.
- [ ] Mean GPU time is at most 14 ms and P95 GPU time at most 20 ms in the representative proof.
- [ ] Peak working set is at most 12,288 MiB and peak GPU memory at most 10,240 MiB in the representative proof.
- [ ] Shader compilation and texture-pool over-budget frames are zero during measured gameplay.
- [ ] Three packaged input-driven combat captures pass.
- [ ] A 20-minute input-driven combat soak passes.
- [ ] Each mission passes at least a five-minute current-candidate soak.
- [ ] Repeated restarts and at least 30 repeated destruction sequences pass.
- [ ] Full-campaign soak and clean shutdown pass without crash, fatal, ensure, device removal, OOM or unbounded memory growth.

## 9. Packaging and installation

- [ ] Fresh Development and Shipping packages are produced from the accepted source and assets.
- [ ] Every archive file has an immutable byte count and SHA-256 inventory.
- [ ] Exactly the ten accepted mission maps are cooked.
- [ ] Stable PSO/shader caches and required runtime dependencies ship.
- [ ] A clean Windows machine installs, launches, plays, saves, progresses and uninstalls successfully.
- [ ] Resolution, display mode, fullscreen/windowed behavior and graphics presets pass.
- [ ] Crash logs and recovery behavior are verified.
- [ ] No editor-only asset, module or dependency is required by Shipping.

## 10. Provenance, configuration and release governance

- [ ] Every third-party asset has a source, ID, creator, license, version, acquisition receipt, file hash, mission usage and modification record.
- [ ] Fab, Bridge/Quixel, Poly Haven and any other external sources are fully reconciled.
- [ ] Required notices and attributions ship.
- [ ] No reference-only media is redistributed without rights.
- [ ] Privacy, analytics, network, telemetry and configuration behavior are reviewed and documented.
- [ ] Failed namespaces and accepted baselines remain immutable.
- [ ] The release candidate has a complete source, binary, content, configuration, package and evidence manifest.
- [ ] Every required gate is green; none is provisional, missing, unverified, editor-only or represented only by the Phase 8 proxy baseline.

## Final acceptance

The release classification may become `PRODUCTION_RELEASE_CANDIDATE_ACCEPTED` only after independent review verifies every checked item against the exact final Shipping package. Until then, the project remains `AWAITING_NEXT_EXPLICIT_GATE`.
