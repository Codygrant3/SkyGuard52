# True-Art Slice29 — L86 Truth-Capture Reset

Updated: 2026-08-01

## Why this slice exists

L85 passed an exact structural capture gate but failed direct visual review. Its checker walls and proxy clusters optimized pixel statistics while hiding the aircraft, cockpit, weapon, world, and combat subjects. Structural readability is no longer allowed to stand in for art quality.

## Implementation

- Delete only owned `AAA_L*` and `AAA_Cam_L*` loop actors from the loaded map
- Reassemble the 19 imported `production-yak52*` and `production-rear*` meshes at one aircraft origin using their imported PBR materials
- Place the production rifle, glove, sleeve, and Shahed assemblies
- Add bounded hero harbor/city/coast anchors using the existing imported/proxy library
- Use target-derived camera rotations for all 11 views
- Capture BASE, FINAL, and SCENE for each camera at 1920×1080
- Emit exactly 33 SHA-256 manifest entries
- Use no checker walls, scoring boards, or color-card grids

## Acceptance gates

1. Exact 11 named cameras
2. Exact 3 sources per camera
3. All 33 PNGs readable at 1920×1080
4. All 33 sizes and SHA-256 values match the manifest
5. Each intended subject is visually recognizable in its named frame
6. No camera intersects or sits behind a dominant occluder
7. The harsh critic still returns FAIL until Skyguard beats the reference in blind comparison

## Expected outcome

This slice is allowed to score worse on the old pixel-diversity heuristic. It succeeds only if the captures become truthful, compositionally readable evidence of the actual Unreal art.
