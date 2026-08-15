"""Import the accepted Grok-produced Mission 1 window bay into a fresh UE namespace.

This gate is intentionally limited to source validation, reversible import, and
StaticMesh/material/collision inspection. It does not edit a map or promote an
asset into runtime content.
"""

from __future__ import annotations

import hashlib
import json
import os
import struct
import sys
import traceback
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
ISOLATED = Path(r"D:\SG52T08_ENV01")
SOURCE = ROOT / (
    r"Production\Attempts\m01-hero-prewar-window-bay-a01-recovery06-unrealready01-grok-mcp"
    r"\attempt_20260811T013000000000Z\output"
    r"\M01_Hero_Prewar_Window_Bay_A01_Recovery06_UnrealReady01.glb"
)
SOURCE_BYTES = 18_844_684
SOURCE_SHA256 = "e27b61da25d93fac047c7941b7087325e6500f30790b92b66ac002dc69421805"
ACCEPTANCE_FREEZE = ROOT / (
    r"Docs\AAA_Review"
    r"\M01_HERO_PREWAR_WINDOW_BAY_A01_RECOVERY06_UNREALREADY01_GROK_MCP_ATTEMPT01_ACCEPTANCE_FREEZE.json"
)
ACCEPTANCE_FREEZE_BYTES = 5_741
ACCEPTANCE_FREEZE_SHA256 = "fc406a78a464cb1a418baf479047ac04ea9e5df850f3f986ccc41c1d537be154"
PROJECT = ISOLATED / "Skyguard52.uproject"
PROJECT_BYTES = 3_703
PROJECT_SHA256 = "7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a"

DESTINATION = "/Game/ToolchainWave08/GrokAccepted/M01WindowBayRecovery06UnrealReady01"
DESTINATION_DISK = ISOLATED / "Content/ToolchainWave08/GrokAccepted/M01WindowBayRecovery06UnrealReady01"
ATTEMPT = ROOT / (
    r"Saved\BuildAttempts\M01_WINDOW_RECOVERY06_UNREALREADY01_REVERSIBLE_UNREAL_IMPORT01"
    r"\attempt_01"
)
RECEIPT = ATTEMPT / "import_receipt.json"

EXPECTED_RENDER_MESHES = {
    "SM_M01_PrewarWindowBay_A01_FrameFacadeHardware": 5,
    "SM_M01_PrewarWindowBay_A01_Glass": 1,
    "SM_M01_PrewarWindowBay_A01_Interior": 9,
}
EXPECTED_COLLISION = {
    "UCX_SM_M01_PrewarWindowBay_A01_FrameFacadeHardware_00",
    "UCX_SM_M01_PrewarWindowBay_A01_FrameFacadeHardware_01",
    "UCX_SM_M01_PrewarWindowBay_A01_FrameFacadeHardware_02",
    "UCX_SM_M01_PrewarWindowBay_A01_FrameFacadeHardware_03",
}
EXPECTED_SOCKETS = {
    "SOCKET_M01_PrewarWindowR03_Center",
    "SOCKET_M01_PrewarWindowR03_Latch",
    "SOCKET_M01_PrewarWindowR03_Origin",
}
EXPECTED_MATERIAL_COUNT = 15


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def record(path: Path) -> dict[str, object]:
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)}


def write_json_atomic(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def vector(value: object) -> list[float]:
    return [float(value.x), float(value.y), float(value.z)]


def read_glb_document(path: Path) -> dict[str, object]:
    with path.open("rb") as stream:
        magic, version, total = struct.unpack("<4sII", stream.read(12))
        require(magic == b"glTF", "Source GLB magic changed")
        require(version == 2, "Source GLB version changed")
        require(total == path.stat().st_size, "Source GLB byte count disagrees with its header")
        json_length, json_type = struct.unpack("<II", stream.read(8))
        require(json_type == 0x4E4F534A, "Source GLB JSON chunk is absent")
        return json.loads(stream.read(json_length).decode("utf-8").rstrip("\x00 \t\r\n"))


def validate_source_contract() -> dict[str, object]:
    require(SOURCE.is_file(), "Accepted source GLB is missing")
    require(SOURCE.stat().st_size == SOURCE_BYTES, "Accepted source GLB byte count changed")
    require(sha256(SOURCE) == SOURCE_SHA256, "Accepted source GLB hash changed")
    require(ACCEPTANCE_FREEZE.is_file(), "Accepted visual-review freeze is missing")
    require(ACCEPTANCE_FREEZE.stat().st_size == ACCEPTANCE_FREEZE_BYTES, "Acceptance freeze byte count changed")
    require(sha256(ACCEPTANCE_FREEZE) == ACCEPTANCE_FREEZE_SHA256, "Acceptance freeze hash changed")

    document = read_glb_document(SOURCE)
    observed_render: dict[str, int] = {}
    observed_collision: set[str] = set()
    for mesh in document.get("meshes", []):
        name = str(mesh.get("name", ""))
        primitives = list(mesh.get("primitives", []))
        require(primitives, f"Mesh has no primitives: {name}")
        require(all(row.get("material") is not None for row in primitives), f"Unmaterialed primitive: {name}")
        if name.startswith("UCX_"):
            observed_collision.add(name)
        else:
            observed_render[name] = len(primitives)

    node_names = {str(row.get("name", "")) for row in document.get("nodes", [])}
    material_names = [str(row.get("name", "")) for row in document.get("materials", [])]
    require(observed_render == EXPECTED_RENDER_MESHES, f"Renderable mesh contract changed: {observed_render}")
    require(observed_collision == EXPECTED_COLLISION, f"UCX collision contract changed: {sorted(observed_collision)}")
    require(EXPECTED_SOCKETS.issubset(node_names), "Socket-node contract changed")
    require(len(material_names) == EXPECTED_MATERIAL_COUNT, f"Material count changed: {len(material_names)}")
    require(len(set(material_names)) == EXPECTED_MATERIAL_COUNT, "Material names are no longer unique")
    return {
        "source": record(SOURCE),
        "acceptance_freeze": record(ACCEPTANCE_FREEZE),
        "render_meshes": observed_render,
        "collision_nodes": sorted(observed_collision),
        "socket_nodes": sorted(EXPECTED_SOCKETS),
        "materials": material_names,
    }


def run_offline_contract_test() -> int:
    validate_source_contract()
    require(PROJECT.is_file(), "Isolated Unreal project is missing")
    require(PROJECT.stat().st_size == PROJECT_BYTES, "Isolated project byte count changed")
    require(sha256(PROJECT) == PROJECT_SHA256, "Isolated project hash changed")
    require(not DESTINATION_DISK.exists(), "Fresh Unreal import namespace already exists")
    require(not ATTEMPT.exists(), "Fresh attempt namespace already exists")
    compile(Path(__file__).read_text(encoding="utf-8"), __file__, "exec")
    print("PASS_M01_WINDOW_RECOVERY06_UNREALREADY01_REVERSIBLE_UNREAL_IMPORT01_CONTRACT")
    return 0


def collision_summary(mesh: object) -> dict[str, object]:
    summary: dict[str, object] = {"body_setup_present": False, "convex_element_count": None, "error": None}
    try:
        body_setup = mesh.get_editor_property("body_setup")
        if body_setup is None:
            return summary
        summary["body_setup_present"] = True
        aggregate = body_setup.get_editor_property("agg_geom")
        convex = aggregate.get_editor_property("convex_elems")
        summary["convex_element_count"] = len(convex)
    except Exception as exc:  # Reflection differs slightly across UE minors; preserve evidence.
        summary["error"] = f"{type(exc).__name__}: {exc}"
    return summary


def validate_mesh_bounds(name: str, extent: list[float]) -> None:
    require(all(value > 0.0 for value in extent), f"Degenerate imported bounds: {name} -> {extent}")
    if name.endswith("FrameFacadeHardware"):
        require(160.0 <= extent[0] <= 200.0, f"Frame width scale/axis mismatch: {extent}")
        require(20.0 <= extent[1] <= 160.0, f"Frame depth scale/axis mismatch: {extent}")
        require(180.0 <= extent[2] <= 220.0, f"Frame height scale/axis mismatch: {extent}")
    elif name.endswith("Glass"):
        require(50.0 <= extent[0] <= 75.0, f"Glass width scale/axis mismatch: {extent}")
        require(0.1 <= extent[1] <= 10.0, f"Glass depth scale/axis mismatch: {extent}")
        require(85.0 <= extent[2] <= 110.0, f"Glass height scale/axis mismatch: {extent}")
    elif name.endswith("Interior"):
        require(115.0 <= extent[0] <= 155.0, f"Interior width scale/axis mismatch: {extent}")
        require(100.0 <= extent[1] <= 160.0, f"Interior depth scale/axis mismatch: {extent}")
        require(125.0 <= extent[2] <= 165.0, f"Interior height scale/axis mismatch: {extent}")


def run_unreal() -> None:
    import unreal

    result: dict[str, object] = {
        "schema": "skyguard.m01-window-recovery06-unrealready01.reversible-unreal-import01.v1",
        "classification": "FAILED_WITH_EVIDENCE",
        "source_contract": None,
        "project_before": None,
        "project_after": None,
        "destination": DESTINATION,
        "task_imported_object_paths": [],
        "imported_assets": [],
        "production_static_meshes": {},
        "source_collision_nodes": sorted(EXPECTED_COLLISION),
        "source_socket_nodes": sorted(EXPECTED_SOCKETS),
        "map_mutations": 0,
        "runtime_promotion_performed": False,
        "rollback_manifest": {"created_asset_namespace": DESTINATION, "map_assets_created": []},
        "error": None,
        "traceback": None,
    }

    try:
        result["source_contract"] = validate_source_contract()
        require(PROJECT.is_file() and PROJECT.stat().st_size == PROJECT_BYTES, "Isolated project authority changed")
        result["project_before"] = record(PROJECT)
        require(result["project_before"]["sha256"] == PROJECT_SHA256, "Isolated project hash changed")
        require(not DESTINATION_DISK.exists(), f"Fresh import namespace exists: {DESTINATION_DISK}")
        require(not unreal.EditorAssetLibrary.does_directory_exist(DESTINATION), f"Fresh import namespace exists: {DESTINATION}")

        require(unreal.EditorAssetLibrary.make_directory(DESTINATION), "Failed to create reversible import namespace")
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
        imported_paths = sorted(unreal.EditorAssetLibrary.list_assets(DESTINATION, recursive=True, include_folder=False))
        require(imported_paths, "Interchange produced no imported assets")

        production_meshes: dict[str, object] = {}
        for asset_path in imported_paths:
            asset = unreal.EditorAssetLibrary.load_asset(asset_path)
            require(asset is not None, f"Imported asset failed to load: {asset_path}")
            name = asset.get_name()
            row: dict[str, object] = {
                "path": asset_path,
                "class": asset.get_class().get_name(),
                "name": name,
            }
            if isinstance(asset, unreal.StaticMesh):
                bounds = asset.get_bounds()
                extent = vector(bounds.box_extent)
                materials = list(asset.get_editor_property("static_materials"))
                row.update(
                    {
                        "bounds_origin_cm": vector(bounds.origin),
                        "bounds_extent_cm": extent,
                        "material_slot_count": len(materials),
                        "lod_count": int(asset.get_num_lods()),
                        "collision": collision_summary(asset),
                    }
                )
                if name in EXPECTED_RENDER_MESHES:
                    require(name not in production_meshes, f"Duplicate production StaticMesh: {name}")
                    require(len(materials) == EXPECTED_RENDER_MESHES[name], f"Material-slot contract changed: {name}")
                    require(int(asset.get_num_lods()) >= 1, f"StaticMesh has no LOD: {name}")
                    validate_mesh_bounds(name, extent)
                    production_meshes[name] = asset
            result["imported_assets"].append(row)

        require(set(production_meshes) == set(EXPECTED_RENDER_MESHES), f"Production StaticMesh set changed: {sorted(production_meshes)}")
        frame = production_meshes["SM_M01_PrewarWindowBay_A01_FrameFacadeHardware"]
        frame_collision = collision_summary(frame)
        if frame_collision["convex_element_count"] is not None:
            require(int(frame_collision["convex_element_count"]) >= 4, f"Expected at least four imported UCX hulls: {frame_collision}")
        result["production_static_meshes"] = {
            name: mesh.get_path_name() for name, mesh in sorted(production_meshes.items())
        }

        try:
            unreal.EditorAssetLibrary.save_directory(DESTINATION, only_if_is_dirty=False, recursive=True)
        except TypeError:
            unreal.EditorAssetLibrary.save_directory(DESTINATION)

        require(DESTINATION_DISK.is_dir(), "Imported namespace was not persisted")
        result["project_after"] = record(PROJECT)
        require(result["project_after"]["sha256"] == PROJECT_SHA256, "Project descriptor changed during import")
        require(sha256(SOURCE) == SOURCE_SHA256, "Accepted GLB changed during import")
        require(sha256(ACCEPTANCE_FREEZE) == ACCEPTANCE_FREEZE_SHA256, "Acceptance freeze changed during import")
        result["classification"] = "PASSED_M01_WINDOW_RECOVERY06_UNREALREADY01_REVERSIBLE_IMPORT_READY_FOR_MAPPED_PREVIEW"
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        result["traceback"] = traceback.format_exc()
    finally:
        write_json_atomic(RECEIPT, result)

    if str(result["classification"]).startswith("PASSED_"):
        unreal.SystemLibrary.quit_editor()
    else:
        raise RuntimeError(result["error"] or "Reversible window import failed")


if "--offline-contract-test" in sys.argv:
    raise SystemExit(run_offline_contract_test())

run_unreal()
