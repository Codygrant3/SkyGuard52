# Selected Luna proposals for Loop55
Base freeze: **L54** densify+thin-art (11/11). L52 densify recipe; L53 rejected.
Wave: wave02
Model: gpt-5.6-luna
Usable gate required: **11/11**

## Implement list (A-band capped, non-duplicate vs L54)
1. `MAT-019` - Behind-wall oxidized fastener patch
   - pillar: materials | score: 93.5 | risk: low | placement: behind_wall | stages: Combat
   - change: Add one compact oxidized-fastener patch to a background metal panel.
   - notes: Use a small cluster of rust spots with a brighter metal center and place the panel beyond x>=bx+3.
   - acceptance: Capture Combat; verify the patch reads as a small material story without competing with the rifle or reducing target contrast.

2. `AIR-011` - Instrument cluster bezel separators
   - pillar: aircraft | score: 93.5 | risk: low | placement: behind_wall | stages: Cockpit|ADS
   - change: Add three thin bright bezel separator bars between the main instrument groups.
   - notes: Keep bars at x>=bx+3, use light neutral unlit HF values, and preserve all existing instrument faces and panel fill.
   - acceptance: Cockpit and ADS remain usable; separators clarify three groups without reducing gauge readability or creating glare.

3. `MAT-006` - Airframe paint scuff accents
   - pillar: materials | score: 92.5 | risk: low | placement: additive_emissive | stages: PropNose|YakBeauty
   - change: Add two or three small pale scuff patches to high-contact airframe zones.
   - notes: Use tiny additive masks with subdued neutral-white response; place only on already bright panel edges.
   - acceptance: Capture PropNose and YakBeauty; confirm scuffs improve authored wear readability without visible glow or camera usability loss.

4. `AIR-013` - Instrument switch-cap highlights
   - pillar: aircraft | score: 92.5 | risk: low | placement: additive_emissive | stages: Cockpit
   - change: Add five tiny bright shell caps to the visible instrument toggle switches.
   - notes: Limit caps to existing switch locations, keep each below pixel-cluster scale where possible, and use restrained additive intensity without bloom.
   - acceptance: Cockpit remains usable; at least three switch caps are distinguishable and no cap blooms into neighboring gauges.

5. `VFX-015` - Thin ocean spray fan
   - pillar: vfx | score: 92.5 | risk: low | placement: additive_emissive | stages: Ocean|Harbor
   - change: Add a three-particle additive emissive spray fan to NS_OceanSpray at the principal wave break.
   - notes: Use tiny cool-white droplets with narrow spread, low count, and no opaque foam sheet.
   - acceptance: Ocean and Harbor remain usable; spray is confined to the selected wave break.

6. `CO-001` - Bright brick tower vertical strip
   - pillar: city_ocean | score: 91.0 | risk: low | placement: behind_wall | stages: City|Wide
   - change: Add one narrow warm-brick vertical facade strip to facade_tower_proxy behind the primary wall.
   - notes: Place at x>=bx+3 with a single narrow strip, restrained roughness variation, and no dark-only facade material.
   - acceptance: Loop52 recipe remains 11/11 usable; City and Wide show one readable brick plane without black-pixel growth.

7. `CO-002` - Apartment bright plaster panel
   - pillar: city_ocean | score: 91.0 | risk: low | placement: behind_wall | stages: City|Wide
   - change: Add one pale plaster infill panel to apartment_midrise_proxy behind the wall.
   - notes: Use a thin rectangular panel at x>=bx+3 with warm ivory albedo and soft value variation.
   - acceptance: City and Wide retain usable framing and the panel reads as bright plaster rather than a washout patch.
