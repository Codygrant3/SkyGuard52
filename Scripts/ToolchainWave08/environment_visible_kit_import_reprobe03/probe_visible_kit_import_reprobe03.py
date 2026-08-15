"""Import one material-preserving apartment GLB into the isolated UE 5.8 project.

This probe validates semantic mesh and material-slot preservation before the
full environment kit may enter Mission 1. It never loads or saves a map.
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
SOURCE = ROOT / r"Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentProductionReset01_UnrealReady02\exports\SM_M01_Apartment_Production_A_CONSOLIDATED.glb"
DESTINATION = "/Game/ToolchainWave08/Environment/VisibleKitImportReprobe03"
DESTINATION_DISK = ISOLATED / r"Content\ToolchainWave08\Environment\VisibleKitImportReprobe03"
ATTEMPT = ROOT / r"Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_KIT_IMPORT_REPROBE03\attempt_01"
RECEIPT = ATTEMPT / "import_probe_receipt.json"
UPROJECT = ISOLATED / "Skyguard52.uproject"
MAP = ISOLATED / r"Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentRealismStack03.umap"
SOURCE_BYTES = 45826976
SOURCE_SHA256 = "77b04f21f75f97b337eb89d142b5d672d9be5eaaa79184ee9f44421d35e51080"
UPROJECT_SHA256 = "7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a"
MAP_SHA256 = "c68de75000c25569f38b9307fd8760cce85236e2f3166785350ea0c641de81e8"
EXPECTED_MATERIAL_SLOTS = {
    "SM_M01_Apartment_Production_A_DETAILS": 6,
    "SM_M01_Apartment_Production_A_GLAZING": 3,
    "SM_M01_Apartment_Production_A_STRUCTURAL": 4,
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
        require(magic == b"glTF" and version == 2 and total_length == path.stat().st_size, "Invalid GLB header")
        json_length, json_type = struct.unpack("<II", stream.read(8))
        require(json_type == 0x4E4F534A, "First GLB chunk is not JSON")
        return json.loads(stream.read(json_length).decode("utf-8").rstrip("\x00 \t\r\n"))


def validate_glb_contract() -> None:
    require(SOURCE.is_file(), "Material-preserving apartment GLB is missing")
    require(SOURCE.stat().st_size == SOURCE_BYTES and sha256(SOURCE) == SOURCE_SHA256, "Material-preserving apartment GLB authority changed")
    document = read_glb_json(SOURCE)
    meshes = {row["name"]: row for row in document.get("meshes", [])}
    require(set(EXPECTED_MATERIAL_SLOTS).issubset(meshes), "Expected semantic render meshes are absent from GLB")
    for name, expected in EXPECTED_MATERIAL_SLOTS.items():
        primitives = meshes[name].get("primitives", [])
        material_indices = [row.get("material") for row in primitives]
        require(len(primitives) == expected, f"Unexpected primitive/material-slot count in {name}: {len(primitives)}")
        require(None not in material_indices, f"Unmaterialed render primitive in {name}")
        require(len(set(material_indices)) == expected, f"Collapsed source material assignments in {name}")
    require(len(document.get("materials", [])) == 11, "Apartment GLB material authority changed")
    node_names = {row.get("name") for row in document.get("nodes", [])}
    require("SOCKET_SM_M01_Apartment_Production_A_Origin" in node_names, "Placement socket missing")


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def vector(value) -> list[float]:
    return [float(value.x), float(value.y), float(value.z)]


def offline_contract_test() -> int:
    validate_glb_contract()
    compile(Path(__file__).read_text(encoding="utf-8"), __file__, "exec")
    print("PASS_GLTF_MATERIAL_CONTRACT")
    return 0


def run_unreal() -> None:
    import unreal

    result = {
        "schema": "skyguard.m01-visible-environment-kit-import-reprobe03.receipt.v1",
        "classification": "FAILED_WITH_EVIDENCE",
        "source": str(SOURCE),
        "destination": DESTINATION,
        "source_bytes": None,
        "source_sha256": None,
        "uproj_sha256_before": None,
        "uproj_sha256_after": None,
        "map_sha256_before": None,
        "map_sha256_after": None,
        "task_imported_object_paths": [],
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
        validate_glb_contract()
        require(UPROJECT.is_file() and sha256(UPROJECT) == UPROJECT_SHA256, "Isolated uproject authority changed")
        require(MAP.is_file() and sha256(MAP) == MAP_SHA256, "Accepted Stack03 map authority changed")
        require(not DESTINATION_DISK.exists(), "Fresh material-slot re-probe disk namespace exists")
        require(not unreal.EditorAssetLibrary.does_directory_exist(DESTINATION), "Fresh material-slot re-probe asset namespace exists")
        result["source_bytes"] = SOURCE.stat().st_size
        result["source_sha256"] = sha256(SOURCE)
        result["uproj_sha256_before"] = sha256(UPROJECT)
        result["map_sha256_before"] = sha256(MAP)

        require(unreal.EditorAssetLibrary.make_directory(DESTINATION), "Failed to create material-slot re-probe asset directory")
        task = unreal.AssetImportTask()
        task.filename = str(SOURCE)
        task.destination_path = DESTINATION
        task.destination_name = ""
        task.automated = True
        task.replace_existing = False
        task.save = True
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
        result["task_imported_object_paths"] = sorted(str(path) for path in (task.imported_object_paths or []))

        registry = unreal.AssetRegistryHelpers.get_asset_registry()
        registry.scan_paths_synchronous([DESTINATION], True, False)
        paths = sorted(unreal.EditorAssetLibrary.list_assets(DESTINATION, recursive=True, include_folder=False))
        result["asset_registry_paths"] = paths
        require(paths, "Interchange import produced no visible assets")
        observed_slots = {}
        for asset_path in paths:
            asset = unreal.EditorAssetLibrary.load_asset(asset_path)
            require(asset is not None, f"Imported asset failed to load: {asset_path}")
            row = {"path": asset_path, "class": asset.get_class().get_name()}
            if isinstance(asset, unreal.StaticMesh):
                bounds = asset.get_bounds()
                name = asset.get_name()
                materials = asset.get_editor_property("static_materials")
                observed_slots[name] = len(materials)
                row.update({
                    "bounds_origin_cm": vector(bounds.origin),
                    "bounds_extent_cm": vector(bounds.box_extent),
                    "material_slot_count": len(materials),
                    "lod_count": int(asset.get_num_lods()),
                })
            result["assets"].append(row)
        result["static_mesh_count"] = len(observed_slots)
        result["material_slot_counts"] = observed_slots
        result["material_slot_total"] = sum(observed_slots.values())
        require(result["static_mesh_count"] == 3, f"Expected exactly three semantic StaticMeshes; found {result['static_mesh_count']}")
        require(set(observed_slots) == set(EXPECTED_MATERIAL_SLOTS), f"Unexpected StaticMesh names: {sorted(observed_slots)}")
        require(observed_slots == EXPECTED_MATERIAL_SLOTS, f"Material-slot preservation failed: expected {EXPECTED_MATERIAL_SLOTS}, observed {observed_slots}")
        require(result["material_slot_total"] == 13, f"Expected thirteen per-mesh material slots; found {result['material_slot_total']}")
        try:
            unreal.EditorAssetLibrary.save_directory(DESTINATION, only_if_is_dirty=False, recursive=True)
        except TypeError:
            unreal.EditorAssetLibrary.save_directory(DESTINATION)
        result["uproj_sha256_after"] = sha256(UPROJECT)
        result["map_sha256_after"] = sha256(MAP)
        require(result["uproj_sha256_after"] == UPROJECT_SHA256, "Isolated uproject mutated")
        require(result["map_sha256_after"] == MAP_SHA256, "Accepted Stack03 map mutated")
        result["classification"] = "PASSED_MATERIAL_SLOT_IMPORT_REPROBE_READY_FOR_FULL_KIT_IMPORT"
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        write_json(RECEIPT, result)

    if result["classification"].startswith("PASSED_"):
        unreal.SystemLibrary.quit_editor()
    else:
        raise RuntimeError(result["error"] or "Material-slot import re-probe failed")


if "--offline-contract-test" in sys.argv:
    raise SystemExit(offline_contract_test())

run_unreal()
