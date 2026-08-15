"""Corrected reversible UE import for the accepted Mission 1 window bay.

Recovery01 uses a short package namespace to avoid UE 5.8 Interchange name
budgeting, applies a verified +90 degree roll import offset, removes the unused
collision-review material slot, and creates three canonical StaticMesh sockets.
No map or production runtime asset is modified.
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
ACCEPTANCE_FREEZE = ROOT / r"Docs\AAA_Review\M01_HERO_PREWAR_WINDOW_BAY_A01_RECOVERY06_UNREALREADY01_GROK_MCP_ATTEMPT01_ACCEPTANCE_FREEZE.json"
ACCEPTANCE_FREEZE_BYTES = 5_741
ACCEPTANCE_FREEZE_SHA256 = "fc406a78a464cb1a418baf479047ac04ea9e5df850f3f986ccc41c1d537be154"
FAILED_IMPORT_FREEZE = ROOT / r"Docs\AAA_Review\M01_WINDOW_RECOVERY06_UNREALREADY01_REVERSIBLE_UNREAL_IMPORT01_ATTEMPT01_TERMINAL_FREEZE.json"
FAILED_IMPORT_FREEZE_SHA256 = "0217140083c4440ac5e902e39f09f41bcb1414cbc00ae92593db5b88aa6d6719"
PIPELINE_PROBE = ROOT / r"Saved\BuildAttempts\M01_WINDOW_INTERCHANGE_PIPELINE_PROBE01\attempt_01\probe_receipt.json"
PIPELINE_PROBE_BYTES = 923
PIPELINE_PROBE_SHA256 = "3e8f99b1a6b962e445463ad2bdd316c81a36b343fdefc865c17d75af984f75aa"
PROJECT = ISOLATED / "Skyguard52.uproject"
PROJECT_BYTES = 3_703
PROJECT_SHA256 = "7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a"

DESTINATION = "/Game/T08/GW01"
DESTINATION_DISK = ISOLATED / "Content/T08/GW01"
ATTEMPT = ROOT / r"Saved\BuildAttempts\M01_WINDOW_RECOVERY06_UNREALREADY01_REVERSIBLE_UNREAL_IMPORT01_RECOVERY01\attempt_01"
RECEIPT = ATTEMPT / "import_receipt.json"

FRAME = "SM_M01_PrewarWindowBay_A01_FrameFacadeHardware"
GLASS = "SM_M01_PrewarWindowBay_A01_Glass"
INTERIOR = "SM_M01_PrewarWindowBay_A01_Interior"
EXPECTED_RENDER_MESHES = {FRAME: 5, GLASS: 1, INTERIOR: 9}
EXPECTED_COLLISION = {
    "UCX_SM_M01_PrewarWindowBay_A01_FrameFacadeHardware_00",
    "UCX_SM_M01_PrewarWindowBay_A01_FrameFacadeHardware_01",
    "UCX_SM_M01_PrewarWindowBay_A01_FrameFacadeHardware_02",
    "UCX_SM_M01_PrewarWindowBay_A01_FrameFacadeHardware_03",
}
EXPECTED_SOURCE_SOCKETS = {
    "SOCKET_M01_PrewarWindowR03_Center",
    "SOCKET_M01_PrewarWindowR03_Latch",
    "SOCKET_M01_PrewarWindowR03_Origin",
}
EXPECTED_UE_SOCKETS = {
    "M01_Window_Origin": (0.0, 0.0, 0.0),
    "M01_Window_Center": (0.0, 0.0, 212.0),
    "M01_Window_Latch": (5.0, 5.2, 200.0),
}


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
        require(magic == b"glTF" and version == 2 and total == path.stat().st_size, "Invalid source GLB header")
        json_length, json_type = struct.unpack("<II", stream.read(8))
        require(json_type == 0x4E4F534A, "Source GLB JSON chunk is absent")
        return json.loads(stream.read(json_length).decode("utf-8").rstrip("\x00 \t\r\n"))


def validate_source_contract() -> dict[str, object]:
    require(SOURCE.is_file() and SOURCE.stat().st_size == SOURCE_BYTES, "Accepted source GLB is missing or changed")
    require(sha256(SOURCE) == SOURCE_SHA256, "Accepted source GLB hash changed")
    require(ACCEPTANCE_FREEZE.is_file() and ACCEPTANCE_FREEZE.stat().st_size == ACCEPTANCE_FREEZE_BYTES, "Acceptance freeze is missing or changed")
    require(sha256(ACCEPTANCE_FREEZE) == ACCEPTANCE_FREEZE_SHA256, "Acceptance freeze hash changed")
    require(FAILED_IMPORT_FREEZE.is_file(), "Failed Attempt01 terminal freeze is missing")
    require(sha256(FAILED_IMPORT_FREEZE) == FAILED_IMPORT_FREEZE_SHA256, "Failed Attempt01 terminal freeze changed")
    require(PIPELINE_PROBE.is_file() and PIPELINE_PROBE.stat().st_size == PIPELINE_PROBE_BYTES, "Pipeline probe is missing or changed")
    require(sha256(PIPELINE_PROBE) == PIPELINE_PROBE_SHA256, "Pipeline probe hash changed")
    probe = json.loads(PIPELINE_PROBE.read_text(encoding="utf-8"))
    require(probe.get("classification") == "PASSED_INTERCHANGE_PIPELINE_REFLECTION_READY_FOR_RECOVERY01_IMPORT", "Pipeline probe was not accepted")
    require(probe.get("import_rotation_roundtrip", {}).get("roll") == 90.0, "Pipeline roll authority changed")

    document = read_glb_document(SOURCE)
    render_meshes: dict[str, int] = {}
    collision: set[str] = set()
    for mesh in document.get("meshes", []):
        name = str(mesh.get("name", ""))
        primitives = list(mesh.get("primitives", []))
        if name.startswith("UCX_"):
            collision.add(name)
        else:
            render_meshes[name] = len(primitives)
    node_names = {str(row.get("name", "")) for row in document.get("nodes", [])}
    require(render_meshes == EXPECTED_RENDER_MESHES, f"Renderable source contract changed: {render_meshes}")
    require(collision == EXPECTED_COLLISION, f"Collision source contract changed: {sorted(collision)}")
    require(EXPECTED_SOURCE_SOCKETS.issubset(node_names), "Source socket contract changed")
    return {
        "source": record(SOURCE),
        "acceptance_freeze": record(ACCEPTANCE_FREEZE),
        "failed_import_freeze": record(FAILED_IMPORT_FREEZE),
        "pipeline_probe": record(PIPELINE_PROBE),
        "render_meshes": render_meshes,
        "collision_nodes": sorted(collision),
        "source_socket_nodes": sorted(EXPECTED_SOURCE_SOCKETS),
    }


def run_offline_contract_test() -> int:
    validate_source_contract()
    require(PROJECT.is_file() and PROJECT.stat().st_size == PROJECT_BYTES and sha256(PROJECT) == PROJECT_SHA256, "Isolated project authority changed")
    require(not DESTINATION_DISK.exists(), "Fresh Recovery01 import namespace exists")
    require(not ATTEMPT.exists(), "Fresh Recovery01 attempt namespace exists")
    compile(Path(__file__).read_text(encoding="utf-8"), __file__, "exec")
    print("PASS_M01_WINDOW_REVERSIBLE_UNREAL_IMPORT01_RECOVERY01_CONTRACT")
    return 0


def collision_summary(mesh: object) -> dict[str, object]:
    body_setup = mesh.get_editor_property("body_setup")
    require(body_setup is not None, "StaticMesh BodySetup is missing")
    aggregate = body_setup.get_editor_property("agg_geom")
    convex = aggregate.get_editor_property("convex_elems")
    return {"body_setup_present": True, "convex_element_count": len(convex)}


def slot_material_name(slot: object) -> str | None:
    interface = slot.get_editor_property("material_interface")
    return None if interface is None else str(interface.get_name())


def normalize_frame_materials(frame: object) -> dict[str, object]:
    before = list(frame.get_editor_property("static_materials"))
    names_before = [slot_material_name(slot) for slot in before]
    review_indices = [index for index, name in enumerate(names_before) if name == "M_REVIEW_Collision"]
    require(review_indices == [len(before) - 1], f"Collision-review material is not the single final slot: {names_before}")
    after = before[:-1]
    frame.modify()
    frame.set_editor_property("static_materials", after)
    frame.post_edit_change()
    names_after = [slot_material_name(slot) for slot in frame.get_editor_property("static_materials")]
    require(len(names_after) == 5 and "M_REVIEW_Collision" not in names_after, f"Frame material cleanup failed: {names_after}")
    return {"before": names_before, "removed_index": review_indices[0], "after": names_after}


def add_canonical_sockets(frame: object, unreal: object) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for name, location in EXPECTED_UE_SOCKETS.items():
        require(frame.find_socket(name) is None, f"Socket already exists before normalization: {name}")
        socket = unreal.StaticMeshSocket(outer=frame)
        socket.set_editor_property("socket_name", name)
        socket.set_editor_property("relative_location", unreal.Vector(*location))
        frame.add_socket(socket)
        observed = frame.find_socket(name)
        require(observed is not None, f"Failed to add canonical socket: {name}")
        actual = vector(observed.get_editor_property("relative_location"))
        require(all(abs(actual[index] - location[index]) <= 0.01 for index in range(3)), f"Socket transform changed: {name} -> {actual}")
        rows.append({"name": name, "relative_location_cm": actual})
    frame.post_edit_change()
    return rows


def validate_bounds(name: str, extent: list[float]) -> None:
    ranges = {
        FRAME: ((160.0, 200.0), (30.0, 55.0), (180.0, 220.0)),
        GLASS: ((50.0, 75.0), (0.1, 10.0), (85.0, 110.0)),
        INTERIOR: ((115.0, 155.0), (105.0, 145.0), (130.0, 165.0)),
    }
    for axis, (low, high) in enumerate(ranges[name]):
        require(low <= extent[axis] <= high, f"Corrected bounds failed for {name} axis {axis}: {extent}")


def run_unreal() -> None:
    import unreal

    result: dict[str, object] = {
        "schema": "skyguard.m01-window.reversible-unreal-import01-recovery01.v1",
        "classification": "FAILED_WITH_EVIDENCE",
        "destination": DESTINATION,
        "source_contract": None,
        "pipeline": {},
        "task_imported_object_paths": [],
        "imported_assets": [],
        "production_static_meshes": {},
        "frame_material_normalization": None,
        "canonical_sockets": [],
        "map_mutations": 0,
        "runtime_promotion_performed": False,
        "project_before": None,
        "project_after": None,
        "error": None,
        "traceback": None,
    }
    try:
        result["source_contract"] = validate_source_contract()
        require(PROJECT.is_file() and PROJECT.stat().st_size == PROJECT_BYTES, "Isolated project authority changed")
        result["project_before"] = record(PROJECT)
        require(result["project_before"]["sha256"] == PROJECT_SHA256, "Isolated project hash changed")
        require(not DESTINATION_DISK.exists(), f"Fresh Recovery01 destination exists: {DESTINATION_DISK}")
        require(not unreal.EditorAssetLibrary.does_directory_exist(DESTINATION), f"Fresh Recovery01 destination exists: {DESTINATION}")

        pipeline = unreal.InterchangeGenericAssetsPipeline()
        rotation = unreal.Rotator()
        rotation.roll = 90.0
        rotation.pitch = 0.0
        rotation.yaw = 0.0
        pipeline.set_editor_property("import_offset_rotation", rotation)
        pipeline.set_editor_property("scene_name_sub_folder", False)
        pipeline.set_editor_property("asset_type_sub_folders", True)
        pipeline.set_editor_property("use_source_name_for_asset", False)
        common = pipeline.get_editor_property("common_meshes_properties")
        common.set_editor_property("import_sockets", True)
        common.set_editor_property("bake_meshes", True)
        stack = unreal.InterchangePipelineStackOverride()
        stack.add_pipeline(pipeline)
        observed_rotation = pipeline.get_editor_property("import_offset_rotation")
        result["pipeline"] = {
            "class": pipeline.get_class().get_name(),
            "stack_class": stack.get_class().get_name(),
            "import_offset_rotation": {"roll": float(observed_rotation.roll), "pitch": float(observed_rotation.pitch), "yaw": float(observed_rotation.yaw)},
            "scene_name_sub_folder": bool(pipeline.get_editor_property("scene_name_sub_folder")),
            "asset_type_sub_folders": bool(pipeline.get_editor_property("asset_type_sub_folders")),
            "import_sockets": bool(common.get_editor_property("import_sockets")),
        }

        require(unreal.EditorAssetLibrary.make_directory(DESTINATION), "Failed to create fresh Recovery01 destination")
        task = unreal.AssetImportTask()
        task.filename = str(SOURCE)
        task.destination_path = DESTINATION
        task.destination_name = ""
        task.automated = True
        task.replace_existing = False
        task.save = True
        task.options = stack
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
        result["task_imported_object_paths"] = sorted(str(path) for path in (task.imported_object_paths or []))

        registry = unreal.AssetRegistryHelpers.get_asset_registry()
        registry.scan_paths_synchronous([DESTINATION], True, False)
        imported_paths = sorted(unreal.EditorAssetLibrary.list_assets(DESTINATION, recursive=True, include_folder=False))
        require(imported_paths, "Recovery01 import produced no assets")
        meshes: dict[str, object] = {}
        for asset_path in imported_paths:
            asset = unreal.EditorAssetLibrary.load_asset(asset_path)
            require(asset is not None, f"Imported asset failed to load: {asset_path}")
            row: dict[str, object] = {"path": asset_path, "class": asset.get_class().get_name(), "name": asset.get_name()}
            if isinstance(asset, unreal.StaticMesh):
                bounds = asset.get_bounds()
                extent = vector(bounds.box_extent)
                slots = list(asset.get_editor_property("static_materials"))
                row.update({
                    "bounds_origin_cm": vector(bounds.origin),
                    "bounds_extent_cm": extent,
                    "material_slot_count": len(slots),
                    "material_names": [slot_material_name(slot) for slot in slots],
                    "lod_count": int(asset.get_num_lods()),
                    "collision": collision_summary(asset),
                })
                if asset.get_name() in EXPECTED_RENDER_MESHES:
                    meshes[asset.get_name()] = asset
            result["imported_assets"].append(row)

        require(set(meshes) == set(EXPECTED_RENDER_MESHES), f"Short-path name preservation failed: {sorted(meshes)}")
        for name, mesh in meshes.items():
            validate_bounds(name, vector(mesh.get_bounds().box_extent))
            require(int(mesh.get_num_lods()) >= 1, f"StaticMesh has no LOD: {name}")

        frame = meshes[FRAME]
        require(collision_summary(frame)["convex_element_count"] == 4, f"UCX collision hull count changed: {collision_summary(frame)}")
        result["frame_material_normalization"] = normalize_frame_materials(frame)
        result["canonical_sockets"] = add_canonical_sockets(frame, unreal)
        require(len(frame.get_editor_property("static_materials")) == EXPECTED_RENDER_MESHES[FRAME], "Frame material-slot count remains incorrect")
        require(len(meshes[GLASS].get_editor_property("static_materials")) == EXPECTED_RENDER_MESHES[GLASS], "Glass material-slot count changed")
        require(len(meshes[INTERIOR].get_editor_property("static_materials")) == EXPECTED_RENDER_MESHES[INTERIOR], "Interior material-slot count changed")
        result["production_static_meshes"] = {name: mesh.get_path_name() for name, mesh in sorted(meshes.items())}

        try:
            unreal.EditorAssetLibrary.save_directory(DESTINATION, only_if_is_dirty=False, recursive=True)
        except TypeError:
            unreal.EditorAssetLibrary.save_directory(DESTINATION)
        require(DESTINATION_DISK.is_dir(), "Recovery01 imported namespace was not saved")

        result["project_after"] = record(PROJECT)
        require(result["project_after"]["sha256"] == PROJECT_SHA256, "Project descriptor changed")
        require(sha256(SOURCE) == SOURCE_SHA256, "Accepted source GLB changed")
        require(sha256(ACCEPTANCE_FREEZE) == ACCEPTANCE_FREEZE_SHA256, "Acceptance freeze changed")
        require(sha256(FAILED_IMPORT_FREEZE) == FAILED_IMPORT_FREEZE_SHA256, "Failed Attempt01 freeze changed")
        result["classification"] = "PASSED_M01_WINDOW_RECOVERY06_UNREALREADY01_REVERSIBLE_IMPORT_RECOVERY01_READY_FOR_MAPPED_PREVIEW"
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        result["traceback"] = traceback.format_exc()
    finally:
        write_json_atomic(RECEIPT, result)

    if result["classification"].startswith("PASSED_"):
        unreal.SystemLibrary.quit_editor()
    else:
        raise RuntimeError(result["error"] or "Recovery01 window import failed")


if "--offline-contract-test" in sys.argv:
    raise SystemExit(run_offline_contract_test())

run_unreal()
