# P0 Cockpit Combat Asset Wave 01 — Terminal Report

Date: 2026-08-06  
Project: `D:\Skyguard52`  
Classification: `PARTIAL_WITH_ACCEPTED_ASSETS_AND_EXPLICIT_BLOCKERS`

## Outcome

The canonical production controller, manifest, Blender 5.2 worker SDK, single-process lock, artifact validation, GLB export, render capture, visual-review recording, and audit all functioned correctly.

No asset in this wave passed the production-candidate visual gate. This is not a shared production-system failure: all nine governed Blender attempts completed with one launch, numeric exit code `0`, zero retries, complete required outputs, and valid receipts. Direct full-resolution review rejected the final result for each asset because the procedural geometry remained visibly primitive at its intended first-person viewing distance.

No generated Blender output is accepted for Unreal import.

## Asset results

### `core-yak52-cockpit`

- Final state: `failed`
- Attempts: 3
- Latest attempt: `D:\Skyguard52\Production\Attempts\core-yak52-cockpit\attempt_20260806T143613845680Z`
- Terminal SHA-256: `352780715ee916570957318fa6429693cb1c3c91d18b31cf6731cb65d875f908`
- Visual-review SHA-256: `010fea974eee5f99f9c502a0cf1b61d800e836bde3f5ccd584b911a17a5909ba`
- Governed `.blend` SHA-256: `a22728451d798f36d398377190147cb7cdda7e136120fdd67ab7bf401177db7f`
- GLB SHA-256: `706f1367bfcc58599c20f42d26114d8743d22eb876c0e5990734533cca768a8e`
- Corrected during wave: camera occlusion, review framing, instrument-marking geometry, switchgear density, upholstery seams, canopy rig/export evidence.
- Terminal blocker: blank-disc instrument appearance, slab-like upholstery/panels, and an unconvincing rear-gunner cockpit composition remain visible at cockpit distance.

### `core-hand-forearm`

- Final state: `failed`
- Attempts: 3
- Latest attempt: `D:\Skyguard52\Production\Attempts\core-hand-forearm\attempt_20260806T144106414958Z`
- Terminal SHA-256: `3e76da89d91ae5720c3b6bce6fdec2b14720c96f4122ebe60aab523bb1ea35c8`
- Visual-review SHA-256: `16c13c5262b92e2675584fc43006b6848f46d7e58f56358dbbdc9181def0d802`
- Governed `.blend` SHA-256: `9469aab89d5dfabe9863ede879b30d8d6df394546ed9464d380e699dbe99b3aa`
- GLB SHA-256: `62dea7fa646d2158e3728b52b02d7b54aba9f28a5fabf878dbea5ebd2bb75c98`
- Corrected during wave: review exposure, camera framing, joint continuity, thumb web, knuckle volumes, dark leather/olive material readability, and a curled grip silhouette.
- Terminal blocker: segmented construction still reads as a mannequin and does not meet credible human anatomy, leather deformation, or first-person hand quality.

### `core-rifle`

- Final state: `failed`
- Attempts: 3
- Latest attempt: `D:\Skyguard52\Production\Attempts\core-rifle\attempt_20260806T144616145298Z`
- Terminal SHA-256: `6716011ae51d711c085bbef4dfb4f617d0154bb1464ea511e8167d7a759bfd21`
- Visual-review SHA-256: `e3544e10896ebda01d90c24cbbf5145f4efd97bcefbe6fc03094397d9a4a4aaf`
- Governed `.blend` SHA-256: `f2d749a5b5a984e6dcd2ba9e026895c6381e0c74072d998355fa1da6a85f5653`
- GLB SHA-256: `32ab48bf3669b5d87d0a2a54535531db216ad383767fc1c3ed3b3d7d4ffb3ccf`
- Corrected during wave: full-weapon framing, dark-material exposure, stock support silhouette, aligned iron-sight evidence, ADS and socket/export receipts.
- Terminal blocker: receiver, grip, magazine, stock, and handguard remain visibly primitive for a first-person hero weapon, with insufficient material separation.

## Final validation

- Production validation: `PASS`
- Manifest assets: 56
- Executable workers: 4
- Accepted assets: 0
- Production audit: `PASS`
- Heavy processes after wave: 0
- Production lock after wave: absent
- Wave state changes: three source/provisional candidates transitioned through governed attempts to terminal `failed`.

## Root cause and production correction

The shared pipeline is operational. The failure is the chosen art-generation method: assembling hero assets from simple procedural boxes, cylinders, and spheres cannot meet the close-up AAA bar, especially for organic anatomy and a reference-specific cockpit.

Do not authorize more parameter-only refinements of these workers. Their attempts are useful dimensional, socket, rig-contract, camera-contract, and export evidence, but not acceptable art.

The next production wave should use artist-grade source construction:

1. `core-yak52-airframe` remains the manifest’s first item but is `blocked_reference`; acquire or create an authoritative dimensioned three-view/station package before modeling.
2. In parallel independent work, replace `core-hand-forearm` with a sculpt/retopology/skin-weight workflow based on an anatomically credible licensed or original human base mesh.
3. Rebuild `core-rifle` with reference-backed hard-surface subdivision/booleans and baked normal detail, preserving its generic AR/M4-family identity and the validated sight/socket contract.
4. Rebuild `core-yak52-cockpit` from dimensioned panel/canopy references using proper high-poly, retopology, UV, texture-bake, and decal workflows.

The immediate executable queue reported by the manifest starts with:

- `core-yak52-airframe` — `blocked_reference`
- `core-pilot` — `queued`
- `core-rear-gunner` — `queued`
- `core-igla-launcher` — `queued`
- `core-igla-missile` — `provisional_blockout`
- `core-shahed136` — `provisional_blockout`

Do not start Unreal integration for these three rejected assets.
