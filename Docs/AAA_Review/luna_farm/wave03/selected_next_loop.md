# Selected Luna proposals for Loop56
Base freeze: **L55** densify+thin-art (11/11).
Wave: wave03
Model: gpt-5.6-luna
Usable gate required: **11/11**

## Implement list (A-band capped, non-duplicate vs L54/L55)
1. `MAT-016` - Behind-wall dirt runoff stripe
   - pillar: materials | score: 93.5 | risk: low | placement: behind_wall | stages: Harbor
   - change: Add one short vertical dirt-runoff stripe to an occluded wall-back panel.
   - notes: Use a sparse opacity mask with a soft termination; keep width narrow and avoid repeating bands.
   - acceptance: Only the intended occluded inspection angle reveals the runoff stripe; Harbor remains usable at 11/11 capture positions.

2. `MAT-020` - Behind-wall layered dirt patch
   - pillar: materials | score: 93.5 | risk: low | placement: behind_wall | stages: City|Harbor
   - change: Add a single small layered rust-and-dirt patch behind the wall using existing imported texture channels.
   - notes: Keep the patch compact, desaturated, and fully occluded until x>=bx+3; use roughness variation as the primary signal.
   - acceptance: The patch reads as layered weathering only in the intended behind-wall position and all frozen cameras remain usable.

3. `AIR-002` - Fuselage inspection hatch rim
   - pillar: aircraft | score: 93.5 | risk: low | placement: behind_wall | stages: YakBeauty|Prop
   - change: Add one shallow offset inspection-hatch rim with a deliberately interrupted lower edge on the fuselage.
   - notes: Use a small rectangular rim at x>=bx+3 with two missing corner segments; keep the base panel bright enough for unlit HF separation.
   - acceptance: Verify hatch rim reads as a distinct local feature in YakBeauty while Prop remains usable and bright.

4. `AIR-004` - Cowling louver break pair
   - pillar: aircraft | score: 93.5 | risk: low | placement: behind_wall | stages: YakBeauty|PropNose
   - change: Add two short offset louver strips on the cowling with unequal spacing and a visible center gap.
   - notes: Keep each louver narrow and shallow at x>=bx+3; use bright-to-mid unlit contrast and no black cavity material.
   - acceptance: Check two readable louver clusters in YakBeauty and no uniqueness or black collapse in PropNose.

5. `VFX-006` - Ricochet spark streak
   - pillar: vfx | score: 92.5 | risk: low | placement: additive_emissive | stages: Combat|ADS
   - change: Add one short directional ricochet streak leaving each metallic impact point.
   - notes: Orient the streak along the impact normal, use a 0.06 second lifetime, and clamp length to a few pixels in the final capture.
   - acceptance: The streak is visible only at impact locations and does not become a continuous line or screen-space artifact.

6. `VFX-016` - Water splash crown tips
   - pillar: vfx | score: 92.5 | risk: low | placement: additive_emissive | stages: Ocean|Harbor
   - change: Add five tiny additive crown tips at the outer edge of a water splash impact.
   - notes: Use a low-opacity pale foam tint, 0.14 second lifetime, and keep all tips inside the existing splash footprint.
   - acceptance: Splash edges become legible at capture resolution while horizon and water values remain stable.

7. `CO-003` - Corrugated facade rib cadence
   - pillar: city_ocean | score: 91.0 | risk: low | placement: behind_wall | stages: City
   - change: Add three bright corrugated vertical ribs to one apartment or industrial facade section.
   - notes: Use sparse, light-gray ribs with alternating roughness; keep the section behind wall at x>=bx+3 and avoid full-facade repetition.
   - acceptance: Capture City and check that ribs read as three separate facade edges without clipping, aliasing, or uniqueness collapse.
