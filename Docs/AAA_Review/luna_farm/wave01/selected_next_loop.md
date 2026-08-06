# Selected Luna proposals for next densify loop
Base freeze: **L52** (11/11 usable). L53 rejected.
Wave: wave01
Model: gpt-5.6-luna
Generated: 2026-07-31T23:33:00
Usable gate required: **11/11**

## Job summary
- materials: status=ok count=20 exit=EXIT=0
- aircraft: status=ok count=20 exit=EXIT=0
- city_ocean: status=ok count=20 exit=EXIT=0
- weapon_ads: status=ok count=20 exit=EXIT=0
- vfx: status=ok count=20 exit=EXIT=0

## Keep rules
- Preserve L52 HF densify exactly
- Prefer additive_emissive or tiny behind_wall accents
- No large multi-stage hero stacks (L53 failure mode)
- Protect Prop/PropNose/YakBeauty/City/Ocean/Wide

## Implement list (A-band capped)
1. `MAT-018` - Behind-wall painted metal chips
   - pillar: materials | score: 93.5 | risk: low | placement: behind_wall | stages: Harbor
   - change: Add a small cluster of pale paint chips over muted rust on one rear metal panel.
   - notes: Use a single compact mask at x>=bx+3; keep chips off the ground plane and use pale gray edges so the panel does not become a dark mass.
   - acceptance: Harbor remains Usable; the rear panel gains readable paint loss without any new foreground or ocean contrast issue.
   - capture_safe: The weathering is rear-only, small in area, and value-balanced toward pale chipped paint.

2. `AIR-003` - Fuselage access-panel offset
   - pillar: aircraft | score: 93.5 | risk: low | placement: behind_wall | stages: YakBeauty
   - change: Add one shallow offset border around an existing fuselage access panel behind the wall.
   - notes: Use a 1-2 pixel projected border in warm gray; keep the panel face mid-value and avoid adding a full hero decal.
   - acceptance: Panel border must be legible in YakBeauty and absent from the frozen foreground overlap; all 11 cameras remain usable.
   - capture_safe: Only a small existing-surface border is added beyond x>=bx+3, with no new dark or reflective material.

3. `AIR-018` - Gunner station trim notch
   - pillar: aircraft | score: 93.5 | risk: low | placement: behind_wall | stages: Cockpit
   - change: Add one small bright trim notch to the gunner station side panel.
   - notes: Use a single trapezoid accent with restrained contrast and no additional panel volume.
   - acceptance: The notch is readable as a manufactured trim cue in Cockpit with no new black block or loss of usability.
   - capture_safe: A single behind-wall trim notch is a controlled local detail and does not affect canopy, aircraft exterior, or exposure.

4. `VFX-001` - Compact twin-lobed muzzle flash
   - pillar: vfx | score: 92.5 | risk: low | placement: additive_emissive | stages: Combat|ADS
   - change: Add a short-duration, camera-facing twin-lobed muzzle flash proxy to the primary aircraft gun firing point.
   - notes: Use a small additive sprite or card, warm white core with restrained amber edge, 0.05-0.09 second lifetime, and bounded size relative to the weapon muzzle.
   - acceptance: Capture Combat and ADS; muzzle flash is readable for one burst, occupies less than 3 percent of frame area, and all 11 cameras remain Usable.
   - capture_safe: Small additive emissive content stays in the muzzle region and cannot create a dark FOV wall or sun-washout field.

5. `VFX-006` - Single impact ember core
   - pillar: vfx | score: 92.5 | risk: low | placement: additive_emissive | stages: PropNose|Combat
   - change: Add one compact orange-white emissive ember core at the first hit location.
   - notes: Use a small billboard with a brief brightness peak and fast fade; keep the radius below the local panel feature scale.
   - acceptance: The ember is visible in PropNose and Combat, remains under 1 percent of frame area, and does not alter silhouette readability.
   - capture_safe: A single tiny emissive point provides a stable focal cue and cannot obscure the nose or create a smoke wall.

6. `MAT-013` - Behind-wall rust tile
   - pillar: materials | score: 90.5 | risk: low | placement: behind_wall | stages: City
   - change: Add one small rust tile decal/material variation behind the wall on a visible city-side construction surface.
   - notes: Place at x>=bx+3 on an existing wall or utility surface; use a compact orange-brown rust mask with a light base and no foreground overlap.
   - acceptance: City remains Usable; the rust tile is visible only on the intended rear surface and does not affect Prop, YakBeauty, Ocean, or Wide.
   - capture_safe: The authored weathering is explicitly behind the wall and outside the frozen foreground densify band.

7. `CO-001` - Warm brick bay bands on facade tower
   - pillar: city_ocean | score: 90.0 | risk: low | placement: additive_emissive | stages: City|Wide
   - change: Add two narrow warm-brick vertical bay bands to facade_tower_proxy with bright unlit height-field breakup.
   - notes: Use a small additive proxy offset from the tower face; keep intensity restrained and preserve the existing HF-lit silhouette.
   - acceptance: Loop52 capture remains 11/11 usable; City and Wide show two readable brick bands without clipping or black patches.
   - capture_safe: Small bright facade accents preserve the frozen FOV density and avoid dark sole-material coverage.

## Ranking snapshot
- Total proposals: 100
- A-band: 68
- Selected for next loop: 7

## Artifacts
- Combined: D:\Skyguard52\Docs\AAA_Review\luna_farm\wave01\wave01_all_proposals.json
- Ranked: D:\Skyguard52\Docs\AAA_Review\luna_farm\wave01\wave01_ranked.csv
- Summary: D:\Skyguard52\Docs\AAA_Review\luna_farm\wave01\wave01_job_summary.json

## Acceptance
- host usable 11/11
- no camera falls to Partial/No vs L52
- critic notes any pillar movement; overall may still FAIL