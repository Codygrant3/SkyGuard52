# Poly Haven CC0 surface sources

The runtime cockpit and city surface atlases in this project use selected
Poly Haven photogrammetry as micro-surface source material.

- Source: https://polyhaven.com/
- License: CC0 1.0 Universal
- License text: https://polyhaven.com/license
- Rebuild: `node tools/build-photoreal-surface-atlases.mjs`

The build script downloads the published 2K diffuse, OpenGL normal, and
roughness JPG maps, verifies the provider MD5 when available, retains the
source files here, and writes optimized WebP runtime outputs. The generated
`surface-build-manifest.json` records the exact source URLs, hashes, atlas
layout, and generated output hashes.

The city atlas layout is contract-bound:

1. aged concrete
2. warm brick
3. weathered plaster
4. modern metal panel

These sources supply material response and photographic micro-detail. All
model geometry, UV layout, runtime material binding, weather response, and
game-specific art direction remain authored by the Skyguard 52 project.
