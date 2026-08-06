"""Create the canonical Mission 01 texture/material provenance ledger.

Read-only audit.  It never downloads, imports, edits Unreal assets, or opens a
legacy web runtime.  Web output paths found in the old surface manifest are
retained only as historical lineage.
"""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
POLY_ROOT = ROOT / "Content" / "Skyguard" / "Textures" / "PolyHaven"
MANIFEST = POLY_ROOT / "surface-build-manifest.json"
PROVENANCE_MANIFEST = POLY_ROOT / "polyhaven-provenance-manifest.json"
README = POLY_ROOT / "README.md"
DOWNLOADER = ROOT / "Scripts" / "download_polyhaven_textures.py"
MATERIAL_ROOT = ROOT / "Content" / "Skyguard" / "Materials"
IMPORTED_TEXTURE_ROOT = ROOT / "Content" / "Skyguard" / "Textures" / "Imported"
OUTPUT = ROOT / "Saved" / "Reports" / "M01_TEXTURE_MATERIAL_PROVENANCE_LEDGER.json"


MISSION1_ROLE = {
    "aerial_beach_01": ["beach_macro", "dune_transition"],
    "aerial_grass_rock": ["coastal_ground_blend"],
    "aerial_rocks_02": ["groyne_rock", "shore_rock"],
    "asphalt_02": ["coastal_road"],
    "blue_metal_plate": ["pathfinder_painted_panel", "radar_metal"],
    "blue_plaster_weathered": ["coastal_apartment_facade"],
    "brick_wall_006": ["urban_facade_variant"],
    "coast_sand_01": ["beach_base", "wet_dry_sand_blend"],
    "concrete_floor_painted": ["radar_bunker_floor", "service_area"],
    "concrete_floor_worn_001": ["promenade_wear", "damage_debris"],
    "concrete_wall_006": ["seawall", "radar_bunker", "urban_concrete"],
    "concrete_wall_008": ["seawall_variant", "urban_concrete_variant"],
    "corrugated_iron_02": ["radar_service_panels", "roof_detail"],
    "fabric_leather_01": ["cockpit_and_gunner_only"],
    "green_metal_rust": ["weathered_metal", "radar_service_detail"],
    "metal_plate": ["pathfinder_structure", "street_and_radar_metal"],
    "metal_plate_02": ["pathfinder_panel_variant"],
    "metal_walkway_01": ["lighthouse_gallery", "radar_access"],
    "painted_metal_02": ["lighthouse_painted_metal", "radar_painted_metal"],
    "painted_plaster_wall": ["apartment_facade"],
    "roof_07": ["urban_roof"],
    "rusty_metal_02": ["coastal_corrosion_detail"],
    "ship_hull": ["marine_prop_surface"],
    "wood_cabinet_worn_long": ["coastal_service_prop", "interior_only"],
}

IMPORTED_FAMILY_BINDING = {
    "airframe_metal": "blue_metal_plate",
    "brick": "brick_wall_006",
    "concrete": "concrete_wall_006",
    "leather": "fabric_leather_01",
    "metal": "green_metal_rust",
    "plaster": "blue_plaster_weathered",
    "L3_asphalt2": "asphalt_02",
    "L3_floor": "concrete_floor_painted",
    "L3_plate": "metal_plate",
    "L3_rock": "aerial_rocks_02",
    "L3_roof": "roof_07",
    "L3_sand": "coast_sand_01",
    "L3_wood2": "wood_cabinet_worn_long",
    "L4_concrete8": "concrete_wall_008",
    "L4_grassrock": "aerial_grass_rock",
    "L4_rust": "rusty_metal_02",
    "L7_beach2": "aerial_beach_01",
    "L7_corrugated": "corrugated_iron_02",
    "L7_floorworn": "concrete_floor_worn_001",
    "L7_plaster2": "painted_plaster_wall",
    "L8_beach2": "aerial_beach_01",
    "L8_corrugated": "corrugated_iron_02",
    "L8_floorworn": "concrete_floor_worn_001",
    "L8_plaster2": "painted_plaster_wall",
    "L8_plate2": "metal_plate_02",
}

PREFERRED_M01_MATERIALS = {
    "M_Asphalt", "M_Beach", "M_CityConcrete", "M_CityGlass", "M_L5_SeaFoam",
    "M_L5_WetAsphalt", "M_L5_WetMetal", "M_Metal", "M_MetalRust",
    "M_Ocean", "M_OceanDeep", "M_Road", "M_Sand", "M_ShahedDrone",
    "M_Terrain", "M_Tex_brick", "M_Tex_concrete", "M_Tex_L3_asphalt2",
    "M_Tex_L3_floor", "M_Tex_L3_plate", "M_Tex_L3_rock", "M_Tex_L3_roof",
    "M_Tex_L3_sand", "M_Tex_L4_concrete8", "M_Tex_L4_grassrock",
    "M_Tex_L4_rust", "M_Tex_L7_beach2", "M_Tex_L7_corrugated",
    "M_Tex_L7_floorworn", "M_Tex_L7_plaster2", "M_Tex_L8_beach2",
    "M_Tex_L8_corrugated", "M_Tex_L8_floorworn", "M_Tex_L8_plaster2",
    "M_Tex_L8_plate2", "M_Tex_metal", "M_Tex_plaster", "M_WetSand",
}

FAB_GAPS = [
    {
        "priority": "P0",
        "category": "modular_architecture",
        "need": "Ukrainian coastal apartment and midrise kit with intact and authored damage variants",
        "local_coverage": "Procedural Blender geometry and facade textures exist; no photoreal hero-grade modular building pack is provenance-bound.",
        "acquisition": "Fab/Quixel candidate; capture product ID, creator, license, version and downloaded file hashes before use.",
    },
    {
        "priority": "P0",
        "category": "coastal_vegetation",
        "need": "Dune grass, salt-tolerant shrubs, wind-shaped coastal trees and ground scatter",
        "local_coverage": "Ground textures exist; no verified vegetation geometry/material family in this ledger.",
        "acquisition": "Fab foliage collection with Nanite/LODs and wind support; record license and source receipt.",
    },
    {
        "priority": "P0",
        "category": "hero_landmark_detail",
        "need": "Lighthouse Fresnel lens, lamp, access stair, door hardware and maintenance props",
        "local_coverage": "Refined lighthouse geometry exists, but optical/interior hero detail is absent.",
        "acquisition": "Fab industrial/maritime prop kit or authored Blender supplement.",
    },
    {
        "priority": "P0",
        "category": "radar_site_detail",
        "need": "Radar drive motor, waveguide/feed detail, generator, cable trays, junction boxes and perimeter equipment",
        "local_coverage": "Refined radar silhouette exists; secondary mechanical storytelling is incomplete.",
        "acquisition": "Fab military/industrial utility kit with explicit commercial-use provenance.",
    },
    {
        "priority": "P1",
        "category": "street_dressing",
        "need": "Region-appropriate cars, utility poles, lamps, benches, bins, signs and barriers",
        "local_coverage": "No canonical Mission 01 street-prop asset family identified.",
        "acquisition": "Fab urban prop packs; avoid visible brand/IP marks unless licensed.",
    },
    {
        "priority": "P1",
        "category": "marine_dressing",
        "need": "Fishing boats, navigation buoys, breakwater blocks, mooring hardware and rescue equipment",
        "local_coverage": "Ship-hull texture placeholder is empty and there is no provenance-bound geometry pack.",
        "acquisition": "Fab maritime pack; record creator, license and exact asset hashes.",
    },
    {
        "priority": "P1",
        "category": "surface_decals",
        "need": "Salt streaks, rust runs, soot, cracks, leaks, chipped paint, tide marks and wetness breakup",
        "local_coverage": "Base PBR families exist, but no canonical decal atlas is present.",
        "acquisition": "Fab/Quixel decal pack or project-authored atlas with source ledger.",
    },
    {
        "priority": "P1",
        "category": "missing_local_surface_receipts",
        "need": "Verified painted metal, metal walkway and ship-hull surface families",
        "local_coverage": "The corresponding PolyHaven folders are empty placeholders.",
        "acquisition": "Prefer completing verified CC0 acquisition from official source or substitute Fab assets; create immutable manifest before import.",
    },
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_downloader_sets():
    tree = ast.parse(DOWNLOADER.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            if any(isinstance(target, ast.Name) and target.id == "sets" for target in node.targets):
                return ast.literal_eval(node.value)
    return {}


def map_kind(filename: str):
    lower = filename.lower()
    if "nor_gl" in lower:
        return "Normal_OpenGL"
    if "rough" in lower:
        return "Roughness"
    if "metal" in lower and ("_metal_" in lower or "-metal-" in lower):
        return "Metallic"
    if "diff" in lower or "albedo" in lower:
        return "BaseColor"
    return "Unknown"


def main():
    original = json.loads(MANIFEST.read_text(encoding="utf-8"))
    provenance_manifest = json.loads(
        PROVENANCE_MANIFEST.read_text(encoding="utf-8")
    )
    downloader_sets = parse_downloader_sets()
    manifest_by_family = {}
    for entry in original["sources"]:
        manifest_by_family.setdefault(entry["asset"], []).append(entry)

    families = []
    verified_file_count = 0
    mismatch_count = 0
    unmanifested_nonempty = 0
    empty_count = 0
    for directory in sorted((path for path in POLY_ROOT.iterdir() if path.is_dir()), key=lambda p: p.name):
        files = sorted(path for path in directory.iterdir() if path.is_file())
        manifest_entries = manifest_by_family.get(directory.name, [])
        checks = []
        for entry in manifest_entries:
            expected_name = Path(entry["cached_path"]).name
            local = directory / expected_name
            exists = local.exists()
            actual_hash = sha256(local) if exists else None
            actual_bytes = local.stat().st_size if exists else None
            match = exists and actual_hash == entry["sha256"] and actual_bytes == entry["bytes"]
            checks.append({
                "file": str(local),
                "exists": exists,
                "expected_bytes": entry["bytes"],
                "actual_bytes": actual_bytes,
                "expected_sha256": entry["sha256"],
                "actual_sha256": actual_hash,
                "source_url": entry["source_url"],
                "match": match,
            })
            verified_file_count += int(match)
            mismatch_count += int(not match)

        file_records = [{
            "name": file.name,
            "path": str(file),
            "map": map_kind(file.name),
            "bytes": file.stat().st_size,
            "sha256": sha256(file),
        } for file in files]

        if manifest_entries and all(check["match"] for check in checks):
            status = "manifest_verified_cc0"
            license_evidence = [str(README), str(MANIFEST)]
        elif files:
            unmanifested_nonempty += 1
            status = (
                "cc0_root_documented_download_script_unmanifested"
                if directory.name in downloader_sets
                else "cc0_root_claim_unmanifested"
            )
            license_evidence = [str(README)]
            if directory.name in downloader_sets:
                license_evidence.append(str(DOWNLOADER))
        else:
            empty_count += 1
            status = "empty_unverified_placeholder"
            license_evidence = []

        expected_from_downloader = downloader_sets.get(directory.name, [])
        missing_expected = [
            name for name in expected_from_downloader if not (directory / name).exists()
        ]
        families.append({
            "family": directory.name,
            "directory": str(directory),
            "status": status,
            "license": original["license"] if status != "empty_unverified_placeholder" else "unverified",
            "license_evidence": license_evidence,
            "mission1_roles": MISSION1_ROLE.get(directory.name, []),
            "files": file_records,
            "manifest_checks": checks,
            "download_script_expected_files": expected_from_downloader,
            "missing_expected_files": missing_expected,
        })

    all_materials = sorted(MATERIAL_ROOT.rglob("*.uasset"))
    relevant_materials = []
    generated_history = []
    for path in all_materials:
        record = {
            "name": path.stem,
            "path": str(path),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
            "provenance": "local_unmanifested_unreal_binary",
        }
        if path.parent.name == "Generated":
            generated_history.append(record)
        elif path.stem in PREFERRED_M01_MATERIALS:
            relevant_materials.append(record)

    imported_textures = []
    if IMPORTED_TEXTURE_ROOT.exists():
        for path in sorted(IMPORTED_TEXTURE_ROOT.glob("*.uasset")):
            stem = path.stem.removeprefix("T_")
            base = stem.rsplit("_", 1)[0]
            family = IMPORTED_FAMILY_BINDING.get(base)
            imported_textures.append({
                "name": path.stem,
                "path": str(path),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
                "inferred_source_family": family,
                "source_binding_status": (
                    "manifest_verified_source_family"
                    if family in manifest_by_family
                    else "unmanifested_source_family" if family else "unresolved"
                ),
                "provenance": "local_unmanifested_unreal_import_binary",
            })

    ledger = {
        "schema": "skyguard.m01.texture-material-provenance.v1",
        "runtime_pipeline": "Unreal Engine + Blender only",
        "legacy_web_outputs": {
            "status": "historical_lineage_only_not_runtime",
            "entries": original.get("outputs", []),
        },
        "polyhaven_root": str(POLY_ROOT),
        "license_declaration": {
            "source": original["source"],
            "source_url": original["source_url"],
            "license": original["license"],
            "license_url": original["license_url"],
            "readme": str(README),
            "readme_sha256": sha256(README),
            "manifest": str(MANIFEST),
            "manifest_sha256": sha256(MANIFEST),
            "expanded_provenance_manifest": str(PROVENANCE_MANIFEST),
            "expanded_provenance_manifest_sha256": sha256(PROVENANCE_MANIFEST),
            "expanded_provenance_gate": provenance_manifest.get("gate"),
            "expanded_provenance_record_count": provenance_manifest.get(
                "record_count", 0
            ),
            "expanded_provenance_verified_record_count": provenance_manifest.get(
                "verified_record_count", 0
            ),
        },
        "summary": {
            "family_count": len(families),
            "manifest_verified_family_count": sum(1 for family in families if family["status"] == "manifest_verified_cc0"),
            "manifest_verified_file_count": verified_file_count,
            "manifest_mismatch_or_missing_count": mismatch_count,
            "unmanifested_nonempty_family_count": unmanifested_nonempty,
            "empty_placeholder_family_count": empty_count,
            "mission1_relevant_material_count": len(relevant_materials),
            "imported_unreal_texture_count": len(imported_textures),
            "generated_material_history_count": len(generated_history),
        },
        "polyhaven_families": families,
        "mission1_relevant_unreal_materials": relevant_materials,
        "imported_unreal_textures": imported_textures,
        "generated_material_history": {
            "status": "historical_or_experimental_do_not_promote_without_in_engine_review",
            "assets": generated_history,
        },
        "fab_acquisition_gaps": FAB_GAPS,
        "gate": (
            "PASS_USED_ASSETS_WITH_ART_BACKLOG"
            if (
                mismatch_count == 0
                and verified_file_count == len(original["sources"])
                and provenance_manifest.get("gate") == "PASS"
                and provenance_manifest.get("record_count", 0)
                == provenance_manifest.get("verified_record_count", -1)
            )
            else "FAIL_MANIFEST_MISMATCH_OR_UNVERIFIED_SOURCE"
        ),
    }
    OUTPUT.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(OUTPUT),
        "summary": ledger["summary"],
        "gate": ledger["gate"],
    }))


if __name__ == "__main__":
    main()
