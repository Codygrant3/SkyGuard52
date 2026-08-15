"""Import the complete material-preserving Mission 1 visible-environment kit.

The run is isolated, NullRHI, and map-independent. It validates exact semantic
StaticMesh names and material-slot counts for all five governed GLBs.
"""

from __future__ import annotations

import hashlib
import json
import os
import struct
import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
ISOLATED = Path(r"D:\SG52T08_ENV01")
EXPORT_ROOT = ROOT / r"Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentProductionReset01_UnrealReady02\exports"
DESTINATION = "/Game/ToolchainWave08/Environment/VisibleEnvironmentKit01"
DESTINATION_DISK = ISOLATED / r"Content\ToolchainWave08\Environment\VisibleEnvironmentKit01"
ATTEMPT = ROOT / r"Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_KIT_FULL_IMPORT01\attempt_01"
RECEIPT = ATTEMPT / "full_kit_import_receipt.json"
UPROJECT = ISOLATED / "Skyguard52.uproject"
MAP = ISOLATED / r"Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentRealismStack03.umap"
UPROJECT_SHA256 = "7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a"
MAP_SHA256 = "c68de75000c25569f38b9307fd8760cce85236e2f3166785350ea0c641de81e8"

SOURCES = {
    "SM_M01_Apartment_Production_A_CONSOLIDATED.glb": (45826976, "77b04f21f75f97b337eb89d142b5d672d9be5eaaa79184ee9f44421d35e51080"),
    "SM_M01_CoastalDistrict_Production_A_CONSOLIDATED.glb": (57221668, "7c76f069a0f72592b4cdf0928529c1fc35405fa175cea27f5697124313f85c0a"),
    "SM_M01_CornerResidence_Production_C_CONSOLIDATED.glb": (61796036, "6c5fe2a8ce70a4dbf0d0bec910261e7eef68183ca6103f3b756c4f0f0065cdb8"),
    "SM_M01_Lighthouse_Production_A_CONSOLIDATED.glb": (35550616, "50e38c728d2497a6689bd352dcc8c4cb3de0e9ab8f2dfb50b5d518680d608301"),
    "SM_M01_Midrise_Production_B_CONSOLIDATED.glb": (62233232, "6c4b22ab84b79510345215772da2649b0cb101089d87336b4604944a74ca3155"),
}

EXPECTED_MATERIAL_SLOTS = {
    "SM_M01_Apartment_Production_A_DETAILS": 6,
    "SM_M01_Apartment_Production_A_GLAZING": 3,
    "SM_M01_Apartment_Production_A_STRUCTURAL": 4,
    "SM_M01_CoastalDistrict_Production_A_HARDSCAPE": 6,
    "SM_M01_CoastalDistrict_Production_A_TERRAIN": 1,
    "SM_M01_CornerResidence_Production_C_DETAILS": 6,
    "SM_M01_CornerResidence_Production_C_GLAZING": 3,
    "SM_M01_CornerResidence_Production_C_STRUCTURAL": 5,
    "SM_M01_Lighthouse_Production_A_DETAILS": 1,
    "SM_M01_Lighthouse_Production_A_GLAZING": 1,
    "SM_M01_Lighthouse_Production_A_STRUCTURAL": 4,
    "SM_M01_Midrise_Production_B_DETAILS": 6,
    "SM_M01_Midrise_Production_B_GLAZING": 3,
    "SM_M01_Midrise_Production_B_STRUCTURAL": 5,
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def read_glb_json(path: Path) -> dict:
    with path.open("rb") as stream:
        magic, version, total_length = struct.unpack("<4sII", stream.read(12))
        require(magic == b"glTF" and version == 2 and total_length == path.stat().st_size, f"Invalid GLB header: {path}")
        json_length, json_type = struct.unpack("<II", stream.read(8))
        require(json_type == 0x4E4F534A, f"First GLB chunk is not JSON: {path}")
        return json.loads(stream.read(json_length).decode("utf-8").rstrip("\x00 \t\r\n"))


def validate_source_contract() -> list[dict]:
    observed_meshes = {}
    source_records = []
    socket_count = 0
    for filename, (expected_bytes, expected_hash) in SOURCES.items():
        path = EXPORT_ROOT / filename
        require(path.is_file(), f"Missing governed GLB: {path}")
        actual_hash = sha256(path)
        require(path.stat().st_size == expected_bytes and actual_hash == expected_hash, f"GLB authority changed: {path}")
        document = read_glb_json(path)
        render_meshes = [row for row in document.get("meshes", []) if not row.get("name", "").startswith("UCX_")]
        for mesh in render_meshes:
            name = mesh["name"]
            require(name not in observed_meshes, f"Duplicate semantic mesh name across GLBs: {name}")
            primitives = mesh.get("primitives", [])
            material_indices = [row.get("material") for row in primitives]
            require(None not in material_indices, f"Unmaterialed render primitive in {name}")
            require(len(set(material_indices)) == len(primitives), f"Collapsed material assignments in {name}")
            observed_meshes[name] = len(primitives)
        sockets = [row.get("name") for row in document.get("nodes", []) if str(row.get("name", "")).startswith("SOCKET_")]
        require(len(sockets) == 1, f"Expected one placement socket in {path.name}; found {sockets}")
        socket_count += 1
        source_records.append({"path": str(path), "bytes": path.stat().st_size, "sha256": actual_hash, "render_meshes": len(render_meshes), "materials": len(document.get("materials", [])), "socket": sockets[0]})
    require(observed_meshes == EXPECTED_MATERIAL_SLOTS, f"Full-kit semantic/material contract changed: {observed_meshes}")
    require(len(observed_meshes) == 14 and sum(observed_meshes.values()) == 54, "Full-kit aggregate mesh/material contract changed")
    require(socket_count == 5, "Full-kit socket count changed")
    return source_records


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def vector(value) -> list[float]:
    return [float(value.x), float(value.y), float(value.z)]


def offline_contract_test() -> int:
    records = validate_source_contract()
    require(len(records) == 5, "Expected five source records")
    compile(Path(__file__).read_text(encoding="utf-8"), __file__, "exec")
    print("PASS_FULL_KIT_GLTF_CONTRACT")
    return 0


def run_unreal() -> None:
    import unreal

    result = {
        "schema": "skyguard.m01-visible-environment-kit-full-import01.receipt.v1",
        "classification": "FAILED_WITH_EVIDENCE",
        "destination": DESTINATION,
        "sources": [],
        "uproj_sha256_before": None,
        "uproj_sha256_after": None,
        "map_sha256_before": None,
        "map_sha256_after": None,
        "task_imported_object_paths": {},
        "asset_registry_paths": [],
        "assets": [],
        "static_mesh_count": 0,
        "material_slot_counts": {},
        "material_slot_total": 0,
        "map_loaded": False,
        "map_saved": False,
        "error": None,
    }

    try:
        result["sources"] = validate_source_contract()
        require(UPROJECT.is_file() and sha256(UPROJECT) == UPROJECT_SHA256, "Isolated uproject authority changed")
        require(MAP.is_file() and sha256(MAP) == MAP_SHA256, "Accepted Stack03 map authority changed")
        require(not DESTINATION_DISK.exists(), "Fresh full-kit disk namespace exists")
        require(not unreal.EditorAssetLibrary.does_directory_exist(DESTINATION), "Fresh full-kit asset namespace exists")
        result["uproj_sha256_before"] = sha256(UPROJECT)
        result["map_sha256_before"] = sha256(MAP)
        require(unreal.EditorAssetLibrary.make_directory(DESTINATION), "Failed to create full-kit asset directory")

        tasks = []
        for filename in SOURCES:
            task = unreal.AssetImportTask()
            task.filename = str(EXPORT_ROOT / filename)
            task.destination_path = DESTINATION
            task.destination_name = ""
            task.automated = True
            task.replace_existing = False
            task.save = True
            tasks.append(task)
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
        for task in tasks:
            result["task_imported_object_paths"][Path(task.filename).name] = sorted(str(path) for path in (task.imported_object_paths or []))

        registry = unreal.AssetRegistryHelpers.get_asset_registry()
        registry.scan_paths_synchronous([DESTINATION], True, False)
        paths = sorted(unreal.EditorAssetLibrary.list_assets(DESTINATION, recursive=True, include_folder=False))
        result["asset_registry_paths"] = paths
        require(paths, "Full-kit import produced no visible assets")
        observed_slots = {}
        for asset_path in paths:
            asset = unreal.EditorAssetLibrary.load_asset(asset_path)
            require(asset is not None, f"Imported asset failed to load: {asset_path}")
            row = {"path": asset_path, "class": asset.get_class().get_name()}
            if isinstance(asset, unreal.StaticMesh):
                bounds = asset.get_bounds()
                name = asset.get_name()
                materials = asset.get_editor_property("static_materials")
                require(name not in observed_slots, f"Duplicate imported StaticMesh identity: {name}")
                observed_slots[name] = len(materials)
                row.update({"bounds_origin_cm": vector(bounds.origin), "bounds_extent_cm": vector(bounds.box_extent), "material_slot_count": len(materials), "lod_count": int(asset.get_num_lods())})
            result["assets"].append(row)
        result["static_mesh_count"] = len(observed_slots)
        result["material_slot_counts"] = observed_slots
        result["material_slot_total"] = sum(observed_slots.values())
        require(observed_slots == EXPECTED_MATERIAL_SLOTS, f"Full-kit material-slot preservation failed: {observed_slots}")
        require(result["static_mesh_count"] == 14 and result["material_slot_total"] == 54, "Full-kit aggregate import contract failed")
        try:
            unreal.EditorAssetLibrary.save_directory(DESTINATION, only_if_is_dirty=False, recursive=True)
        except TypeError:
            unreal.EditorAssetLibrary.save_directory(DESTINATION)
        result["uproj_sha256_after"] = sha256(UPROJECT)
        result["map_sha256_after"] = sha256(MAP)
        require(result["uproj_sha256_after"] == UPROJECT_SHA256, "Isolated uproject mutated")
        require(result["map_sha256_after"] == MAP_SHA256, "Accepted Stack03 map mutated")
        result["classification"] = "PASSED_FULL_VISIBLE_ENVIRONMENT_KIT_IMPORT_READY_FOR_REVERSIBLE_MAP_ASSEMBLY_DESIGN"
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        write_json(RECEIPT, result)

    if result["classification"].startswith("PASSED_"):
        unreal.SystemLibrary.quit_editor()
    else:
        raise RuntimeError(result["error"] or "Full visible-environment kit import failed")


if "--offline-contract-test" in sys.argv:
    raise SystemExit(offline_contract_test())

run_unreal()
