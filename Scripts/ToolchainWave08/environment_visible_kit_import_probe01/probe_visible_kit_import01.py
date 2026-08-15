"""Import one accepted Checkpoint02 GLB into the isolated UE 5.8 project.

The probe records the actual Interchange decomposition before full-kit placement.
It never loads, duplicates, or saves a map.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
ISOLATED = Path(r"D:\SG52T08_ENV01")
SOURCE = ROOT / r"Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentProductionReset01_Checkpoint02\exports\SM_M01_Apartment_Production_A.glb"
DESTINATION = "/Game/ToolchainWave08/Environment/VisibleKitImportProbe01"
DESTINATION_DISK = ISOLATED / r"Content\ToolchainWave08\Environment\VisibleKitImportProbe01"
ATTEMPT = ROOT / r"Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_KIT_IMPORT_PROBE01\attempt_01"
RECEIPT = ATTEMPT / "import_probe_receipt.json"
UPROJECT = ISOLATED / "Skyguard52.uproject"
MAP = ISOLATED / r"Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentRealismStack03.umap"
SOURCE_BYTES = 45451472
SOURCE_SHA256 = "5c09c9eb7bf17057ec277b958165005e71e3ecac6a9430df47eddeceab9a7849"
UPROJECT_SHA256 = "7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a"
MAP_SHA256 = "c68de75000c25569f38b9307fd8760cce85236e2f3166785350ea0c641de81e8"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def vector(value) -> list[float]:
    return [float(value.x), float(value.y), float(value.z)]


result = {
    "schema": "skyguard.m01-visible-environment-kit-import-probe01.receipt.v1",
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
    "map_loaded": False,
    "map_saved": False,
    "error": None,
}

try:
    require(SOURCE.is_file() and SOURCE.stat().st_size == SOURCE_BYTES and sha256(SOURCE) == SOURCE_SHA256, "Accepted apartment GLB authority changed")
    require(UPROJECT.is_file() and sha256(UPROJECT) == UPROJECT_SHA256, "Isolated uproject authority changed")
    require(MAP.is_file() and sha256(MAP) == MAP_SHA256, "Accepted Stack03 map authority changed")
    require(not DESTINATION_DISK.exists(), "Fresh import-probe disk namespace exists")
    require(not unreal.EditorAssetLibrary.does_directory_exist(DESTINATION), "Fresh import-probe asset namespace exists")
    result["source_bytes"] = SOURCE.stat().st_size
    result["source_sha256"] = sha256(SOURCE)
    result["uproj_sha256_before"] = sha256(UPROJECT)
    result["map_sha256_before"] = sha256(MAP)

    require(unreal.EditorAssetLibrary.make_directory(DESTINATION), "Failed to create import-probe asset directory")
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
    static_mesh_count = 0
    for asset_path in paths:
        asset = unreal.EditorAssetLibrary.load_asset(asset_path)
        require(asset is not None, f"Imported asset failed to load: {asset_path}")
        row = {"path": asset_path, "class": asset.get_class().get_name()}
        if isinstance(asset, unreal.StaticMesh):
            static_mesh_count += 1
            bounds = asset.get_bounds()
            row.update({
                "bounds_origin_cm": vector(bounds.origin),
                "bounds_extent_cm": vector(bounds.box_extent),
                "material_slot_count": len(asset.get_editor_property("static_materials")),
                "lod_count": int(asset.get_num_lods()),
            })
        result["assets"].append(row)
    result["static_mesh_count"] = static_mesh_count
    require(static_mesh_count >= 1, "Interchange import produced no StaticMesh assets")
    try:
        unreal.EditorAssetLibrary.save_directory(DESTINATION, only_if_is_dirty=False, recursive=True)
    except TypeError:
        unreal.EditorAssetLibrary.save_directory(DESTINATION)
    result["uproj_sha256_after"] = sha256(UPROJECT)
    result["map_sha256_after"] = sha256(MAP)
    require(result["uproj_sha256_after"] == UPROJECT_SHA256, "Isolated uproject mutated")
    require(result["map_sha256_after"] == MAP_SHA256, "Accepted Stack03 map mutated")
    result["classification"] = "PASSED_VISIBLE_KIT_IMPORT_PROBE_READY_FOR_FULL_INTEGRATION_DESIGN"
except Exception as exc:
    result["error"] = f"{type(exc).__name__}: {exc}"
finally:
    write_json(RECEIPT, result)

if result["classification"].startswith("PASSED_"):
    unreal.SystemLibrary.quit_editor()
else:
    raise RuntimeError(result["error"] or "Visible-kit import probe failed")
