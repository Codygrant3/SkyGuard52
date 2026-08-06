# Mission 01 Texture and Material Provenance

Status: **PASS WITH PROVENANCE GAPS**

Runtime contract: **Unreal Engine and Blender only.** Any WebP or `public/`
output recorded by the historical surface manifest is lineage evidence, not a
runtime dependency or promotion target.

## Canonical ledger

- Audit script:
  `D:\Skyguard52\Scripts\audit_m01_texture_material_provenance.py`
- Machine-readable ledger:
  `D:\Skyguard52\Saved\Reports\M01_TEXTURE_MATERIAL_PROVENANCE_LEDGER.json`
- Poly Haven declaration:
  `D:\Skyguard52\Content\Skyguard\Textures\PolyHaven\README.md`
- Original surface manifest:
  `D:\Skyguard52\Content\Skyguard\Textures\PolyHaven\surface-build-manifest.json`

The ledger records every source-file, Unreal texture, and relevant material
binary with its current size and SHA-256.

## Verified local inventory

| Classification | Families | Files | Production meaning |
| --- | ---: | ---: | --- |
| Manifest-verified Poly Haven CC0 | 6 | 18 | Source URL, byte count and SHA-256 all match the retained manifest. |
| CC0-root documented, locally unmanifested | 15 | 46 | Located under the declared Poly Haven root, but lacks canonical per-file acquisition receipt/hash provenance. |
| Empty unverified placeholders | 3 | 0 | Not usable assets. |

All 18 manifest-declared source files match. There are no hash or byte-count
mismatches.

### Manifest-verified CC0 families

- `blue_metal_plate`
- `blue_plaster_weathered`
- `brick_wall_006`
- `concrete_wall_006`
- `fabric_leather_01`
- `green_metal_rust`

These are the safest existing sources for immediate Mission 1 reuse.

### Locally present but provenance-pending families

- `aerial_beach_01`
- `aerial_grass_rock`
- `aerial_rocks_02`
- `asphalt_02`
- `coast_sand_01`
- `concrete_floor_painted`
- `concrete_floor_worn_001`
- `concrete_wall_008`
- `corrugated_iron_02`
- `metal_plate`
- `metal_plate_02`
- `painted_plaster_wall`
- `roof_07`
- `rusty_metal_02`
- `wood_cabinet_worn_long`

The root README identifies the directory as Poly Haven CC0, and several
families also have official URL construction documented in the retained
download script. That is useful evidence, but it is not equivalent to the
immutable per-file source URL and provider hash receipt retained for the six
verified families. These assets may be evaluated locally but should not be
called fully provenance-bound until a canonical receipt is added.

### Empty placeholders

- `metal_walkway_01`
- `painted_metal_02`
- `ship_hull`

`painted_metal_02` is also missing all three files expected by the retained
download script.

## Unreal inventory

- Mission 1 material candidates: 38.
- Imported Unreal texture binaries: 75.
- Generated/experimental material history: 87.

The 38 current candidates include coastal road, beach, sand, wetness, ocean,
urban concrete/glass, metal/rust and the textured L3/L4/L7/L8 source variants.
The exact paths and hashes are in the ledger.

The 87 assets under `Materials\Generated` are retained as historical or
experimental variants. Their presence does not prove visual approval,
provenance, correct texture binding, or production suitability. Promote one
only after an in-engine material review and explicit canonical designation.

Imported `.uasset` textures and materials currently have local binary hashes,
but no import receipts that bind each Unreal package hash to exact importer
settings. The ledger therefore labels them `local_unmanifested_unreal_binary`
or `local_unmanifested_unreal_import_binary` even when their inferred source
family is manifest verified.

## Canonical reuse policy

1. Prefer the six manifest-verified families for immediate reuse.
2. Keep source maps under the Poly Haven tree; create Unreal-native materials
   without depending on historical browser output paths.
3. Treat all OpenGL normal maps as requiring Unreal green-channel conversion.
4. Do not infer a license from a folder name alone.
5. Before promoting a provenance-pending family, record official source URL,
   asset identifier, license/version, source-file sizes and SHA-256 hashes.
6. Bind each promoted Unreal texture/material package to its source record and
   import settings.
7. Avoid duplicating L7/L8 material variants when one parameterized master
   material can cover the same surface family.

## Fab acquisition gaps

### P0

- Ukrainian coastal apartment/midrise modular kit with intact and authored
  damage variants.
- Dune grass, coastal shrubs, wind-shaped trees and ground scatter.
- Lighthouse Fresnel lens, lamp, access stair and maintenance detail.
- Radar motor, feed/waveguide, generator, cable trays and service equipment.

### P1

- Region-appropriate cars, utility poles, lamps, benches, bins, signs and
  barriers.
- Fishing boats, navigation buoys, breakwater blocks and mooring hardware.
- Salt, rust, soot, cracks, leaks, chipped paint, tide-mark and wetness decals.
- Verified replacements for the empty painted-metal, metal-walkway and
  ship-hull surface placeholders.

For every Fab acquisition, retain the product ID, creator, license, version,
acquisition date, original filenames and hashes before import. Avoid visible
brand or protected insignia unless licensing explicitly permits their use.

## Promotion boundary

This audit authorizes reuse decisions; it does not import, download, modify
maps, or approve visual quality. Fab acquisition and Unreal material promotion
remain separate, reviewable gates.
