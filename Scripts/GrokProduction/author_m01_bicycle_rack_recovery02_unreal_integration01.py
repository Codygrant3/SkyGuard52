"""Import the accepted bicycle rack and place grounded instances in a fresh M01 map."""

from __future__ import annotations

import hashlib
import json
import math
import os
import struct
import sys
import traceback
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
ISOLATED = Path(r"D:\SG52T08_ENV01")
SOURCE = ROOT / r"Production\Attempts\m01-bicycle-rack-grok-mcp-recovery02\attempt_20260811T073000000000Z\output\exports\M01_Promenade_BicycleRack_Recovery02.glb"
SOURCE_BYTES = 422_412
SOURCE_SHA256 = "edf7e9a2e9a67a6ac9132900dc176a0e39d2eaf4e7c249e36a6de92a9c03651c"
ACCEPTANCE_FREEZE = ROOT / r"Docs\AAA_Review\M01_BICYCLE_RACK_GROK_MCP_RECOVERY02_ACCEPTANCE_FREEZE.json"
ACCEPTANCE_FREEZE_BYTES = 2_605
ACCEPTANCE_FREEZE_SHA256 = "68ca8f16d4c3ea5886ee1b75c6040703102c720fefdbe62896fcf4581f495f05"
PROJECT = ISOLATED / "Skyguard52.uproject"
PROJECT_BYTES = 3_703
PROJECT_SHA256 = "7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a"
INPUT_ASSET = "/Game/M01/Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01Recovery01_PromenadeBollards01"
OUTPUT_ASSET = "/Game/M01/Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01Recovery01_PromenadeBollards01_BicycleRacks01"
INPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01Recovery01_PromenadeBollards01.umap"
OUTPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01Recovery01_PromenadeBollards01_BicycleRacks01.umap"
INPUT_BYTES = 734_014
INPUT_SHA256 = "d4659a61c3f20abdb060f07d9d6e2b3ca713487f7ee0295b5afd8d27320cc54c"
DESTINATION = "/Game/M01/PromenadeBicycleRackRecovery02"
DESTINATION_DISK = ISOLATED / "Content/M01/PromenadeBicycleRackRecovery02"
ATTEMPT = ROOT / r"Saved\BuildAttempts\M01_BICYCLE_RACK_RECOVERY02_UNREAL_INTEGRATION01\attempt_01"
RECEIPT = ATTEMPT / "integration_receipt.json"
MESH_NAME = "SM_M01_Promenade_BicycleRack_A"
SOCKET_NODE = "SOCKET_BicycleRack_Origin"
CANONICAL_SOCKET = "M01_BicycleRack_Origin"
PLACEMENT_COUNT = 8
EXPECTED_ACTORS_BEFORE = 113


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


def inventory(path: Path) -> list[dict[str, object]]:
    return [record(item) for item in sorted(path.rglob("*")) if item.is_file()]


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
        require(magic == b"glTF" and version == 2 and total == path.stat().st_size, "Invalid accepted GLB header")
        json_length, json_type = struct.unpack("<II", stream.read(8))
        require(json_type == 0x4E4F534A, "Accepted GLB JSON chunk is absent")
        return json.loads(stream.read(json_length).decode("utf-8").rstrip("\x00 \t\r\n"))


def validate_source_contract() -> dict[str, object]:
    require(SOURCE.is_file() and SOURCE.stat().st_size == SOURCE_BYTES, "Accepted bicycle-rack GLB is missing or changed")
    require(sha256(SOURCE) == SOURCE_SHA256, "Accepted bicycle-rack GLB hash changed")
    require(ACCEPTANCE_FREEZE.is_file() and ACCEPTANCE_FREEZE.stat().st_size == ACCEPTANCE_FREEZE_BYTES, "Acceptance freeze is missing or changed")
    require(sha256(ACCEPTANCE_FREEZE) == ACCEPTANCE_FREEZE_SHA256, "Acceptance freeze hash changed")
    freeze = json.loads(ACCEPTANCE_FREEZE.read_text(encoding="utf-8"))
    require(freeze.get("classification") == "PASSED_DIRECT_VISUAL_REVIEW_FOR_MID_DISTANCE_ENVIRONMENT_USE", "Unexpected acceptance classification")
    require(freeze.get("glb", {}).get("sha256") == SOURCE_SHA256, "Accepted GLB is not bound by the freeze")

    document = read_glb_document(SOURCE)
    meshes = [str(row.get("name", "")) for row in document.get("meshes", [])]
    nodes = {str(row.get("name", "")) for row in document.get("nodes", [])}
    materials = [str(row.get("name", "")) for row in document.get("materials", [])]
    require(len(meshes) == 1, f"Accepted GLB mesh count changed: {meshes}")
    require(MESH_NAME in nodes and SOCKET_NODE in nodes, f"Accepted node contract changed: {sorted(nodes)}")
    require(materials == ["M_M01_Promenade_GalvanizedSteel_Rack"], f"Accepted material contract changed: {materials}")
    return {"source": record(SOURCE), "acceptance_freeze": record(ACCEPTANCE_FREEZE), "meshes": meshes, "nodes": sorted(nodes), "materials": materials}


def promenade_surface_z_cm(x_cm: float, y_cm: float) -> float:
    x = x_cm / 100.0
    y = y_cm / 100.0
    long_wave = 0.045 * math.sin(x / 72.0) + 0.025 * math.sin(x / 19.0 + 0.7)
    shore = 38.0 + 2.45 * math.sin(x / 47.0) + 0.82 * math.sin(x / 13.0 + 0.4)
    boundaries = [
        (18.0, -1.25),
        (shore, -0.54 + long_wave),
        (shore + 10.0 + 0.65 * math.sin(x / 23.0), -0.10 + long_wave),
        (shore + 29.0 + 1.35 * math.sin(x / 39.0 + 0.8), 0.42 + long_wave),
        (78.0 + 0.62 * math.sin(x / 61.0), 0.70 + long_wave * 0.35),
        (86.0, 0.72 + long_wave * 0.20),
        (100.0, 0.56 + long_wave * 0.15),
        (104.0, 0.72 + long_wave * 0.15),
    ]
    if y >= 104.0:
        return (0.76 + 0.025 * math.sin(x / 31.0)) * 100.0
    for (left_y, left_z), (right_y, right_z) in zip(boundaries, boundaries[1:]):
        if left_y <= y <= right_y:
            alpha = 0.0 if right_y == left_y else (y - left_y) / (right_y - left_y)
            return (left_z + (right_z - left_z) * alpha) * 100.0
    return boundaries[0][1] * 100.0


def run_offline_contract_test() -> int:
    validate_source_contract()
    require(PROJECT.is_file() and PROJECT.stat().st_size == PROJECT_BYTES and sha256(PROJECT) == PROJECT_SHA256, "Isolated project authority changed")
    require(INPUT_FILE.is_file() and INPUT_FILE.stat().st_size == INPUT_BYTES and sha256(INPUT_FILE) == INPUT_SHA256, "Accepted input map authority changed")
    require(not DESTINATION_DISK.exists(), "Fresh bicycle-rack import namespace already exists")
    require(not OUTPUT_FILE.exists(), "Fresh bicycle-rack output map already exists")
    require(not ATTEMPT.exists(), "Fresh bicycle-rack attempt namespace already exists")
    compile(Path(__file__).read_text(encoding="utf-8"), __file__, "exec")
    print("PASS_M01_BICYCLE_RACK_RECOVERY02_UNREAL_INTEGRATION01_CONTRACT")
    return 0


def run_unreal() -> None:
    import unreal

    result: dict[str, object] = {
        "schema": "skyguard.m01-bicycle-rack-recovery02.unreal-integration01.v1",
        "classification": "FAILED_WITH_EVIDENCE",
        "source_contract": None,
        "input_asset": INPUT_ASSET,
        "output_asset": OUTPUT_ASSET,
        "destination": DESTINATION,
        "input_map_before": None,
        "input_map_after": None,
        "imported_assets": [],
        "rack_mesh": None,
        "placements": [],
        "actor_count_before": None,
        "actor_count_after": None,
        "output_map": None,
        "asset_inventory": [],
        "rollback_manifest": {"created_asset_namespace": DESTINATION, "created_map": OUTPUT_ASSET, "accepted_inputs_mutated": False},
        "error": None,
        "traceback": None,
    }

    try:
        result["source_contract"] = validate_source_contract()
        require(PROJECT.is_file() and PROJECT.stat().st_size == PROJECT_BYTES and sha256(PROJECT) == PROJECT_SHA256, "Isolated project authority changed")
        result["input_map_before"] = record(INPUT_FILE)
        require(result["input_map_before"]["bytes"] == INPUT_BYTES and result["input_map_before"]["sha256"] == INPUT_SHA256, "Accepted input map changed")
        require(not DESTINATION_DISK.exists(), f"Fresh import namespace exists: {DESTINATION_DISK}")
        require(not unreal.EditorAssetLibrary.does_directory_exist(DESTINATION), f"Fresh import namespace exists: {DESTINATION}")
        require(not OUTPUT_FILE.exists() and not unreal.EditorAssetLibrary.does_asset_exist(OUTPUT_ASSET), "Fresh output map exists")

        pipeline = unreal.InterchangeGenericAssetsPipeline()
        pipeline.set_editor_property("scene_name_sub_folder", False)
        pipeline.set_editor_property("asset_type_sub_folders", True)
        pipeline.set_editor_property("use_source_name_for_asset", False)
        common = pipeline.get_editor_property("common_meshes_properties")
        common.set_editor_property("import_sockets", True)
        common.set_editor_property("bake_meshes", True)
        stack = unreal.InterchangePipelineStackOverride()
        stack.add_pipeline(pipeline)

        require(unreal.EditorAssetLibrary.make_directory(DESTINATION), "Failed to create bicycle-rack import namespace")
        task = unreal.AssetImportTask()
        task.filename = str(SOURCE)
        task.destination_path = DESTINATION
        task.destination_name = ""
        task.automated = True
        task.replace_existing = False
        task.save = True
        task.options = stack
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])

        registry = unreal.AssetRegistryHelpers.get_asset_registry()
        registry.scan_paths_synchronous([DESTINATION], True, False)
        imported_paths = sorted(unreal.EditorAssetLibrary.list_assets(DESTINATION, recursive=True, include_folder=False))
        require(imported_paths, "Bicycle-rack Interchange import produced no assets")
        render_mesh = None
        for asset_path in imported_paths:
            asset = unreal.EditorAssetLibrary.load_asset(asset_path)
            require(asset is not None, f"Imported asset failed to load: {asset_path}")
            row: dict[str, object] = {"path": asset_path, "class": asset.get_class().get_name(), "name": asset.get_name()}
            if isinstance(asset, unreal.StaticMesh):
                bounds = asset.get_bounds()
                row.update({"bounds_origin_cm": vector(bounds.origin), "bounds_extent_cm": vector(bounds.box_extent), "material_slot_count": len(list(asset.get_editor_property("static_materials"))), "lod_count": int(asset.get_num_lods())})
                if asset.get_name() == MESH_NAME:
                    render_mesh = asset
            result["imported_assets"].append(row)
        require(render_mesh is not None, f"Accepted bicycle-rack StaticMesh not imported: {MESH_NAME}")

        extent = vector(render_mesh.get_bounds().box_extent)
        require(85.0 <= extent[0] <= 100.0 and 25.0 <= extent[1] <= 35.0 and 35.0 <= extent[2] <= 45.0, f"Bicycle-rack bounds changed: {extent}")
        require(int(render_mesh.get_num_lods()) >= 1, "Imported bicycle rack has no LOD")
        materials = list(render_mesh.get_editor_property("static_materials"))
        require(len(materials) == 1, f"Bicycle-rack material-slot count changed: {len(materials)}")
        body_setup = render_mesh.get_editor_property("body_setup")
        require(body_setup is not None, "Imported bicycle rack has no BodySetup")
        body_setup.set_editor_property("collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)

        socket = render_mesh.find_socket(CANONICAL_SOCKET)
        if socket is None:
            socket = unreal.StaticMeshSocket(outer=render_mesh)
            socket.set_editor_property("socket_name", CANONICAL_SOCKET)
            socket.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 0.0))
            render_mesh.add_socket(socket)
        require(render_mesh.find_socket(CANONICAL_SOCKET) is not None, "Canonical bicycle-rack origin socket is missing")
        try:
            unreal.EditorAssetLibrary.save_loaded_asset(render_mesh, only_if_is_dirty=False)
            unreal.EditorAssetLibrary.save_directory(DESTINATION, only_if_is_dirty=False, recursive=True)
        except TypeError:
            unreal.EditorAssetLibrary.save_loaded_asset(render_mesh)
            unreal.EditorAssetLibrary.save_directory(DESTINATION)

        result["rack_mesh"] = {"path": render_mesh.get_path_name(), "bounds_origin_cm": vector(render_mesh.get_bounds().origin), "bounds_extent_cm": extent, "material_slot_count": len(materials), "collision": "CTF_USE_COMPLEX_AS_SIMPLE", "canonical_socket": CANONICAL_SOCKET}

        levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        actors_api = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        require(levels is not None and actors_api is not None, "Required editor subsystems are unavailable")
        require(levels.new_level_from_template(OUTPUT_ASSET, INPUT_ASSET), "Failed to duplicate accepted corridor map")
        before = list(actors_api.get_all_level_actors())
        result["actor_count_before"] = len(before)
        require(len(before) == EXPECTED_ACTORS_BEFORE, f"Accepted corridor actor count changed: {len(before)}")
        require(not any(actor.get_actor_label().startswith("M01_Promenade_BicycleRack_") for actor in before), "Bicycle-rack labels already exist in accepted input map")

        x_positions = [6500.0 + 7500.0 * index for index in range(PLACEMENT_COUNT)]
        y_offsets = (-120.0, 40.0, 130.0, -35.0)
        yaw_offsets = (0.0, 1.5, -1.0, 0.5)
        scale_values = (0.98, 1.00, 1.02, 0.99)
        for index, x_cm in enumerate(x_positions):
            y_cm = 8000.0 + y_offsets[index % len(y_offsets)]
            scale = scale_values[index % len(scale_values)]
            yaw = yaw_offsets[index % len(yaw_offsets)]
            actor = actors_api.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x_cm, y_cm, 0.0), unreal.Rotator(0.0, yaw, 0.0), False)
            require(actor is not None, f"Failed to spawn bicycle rack {index + 1:02d}")
            actor.set_actor_label(f"M01_Promenade_BicycleRack_{index + 1:02d}")
            actor.set_folder_path("M01/PromenadeProps/BicycleRacks")
            actor.set_actor_scale3d(unreal.Vector(scale, scale, scale))
            component = actor.get_component_by_class(unreal.StaticMeshComponent)
            require(component is not None, f"StaticMeshComponent missing for bicycle rack {index + 1:02d}")
            component.set_static_mesh(render_mesh)
            component.set_mobility(unreal.ComponentMobility.STATIC)
            component.set_editor_property("cast_shadow", True)
            component.set_collision_profile_name("BlockAll")
            origin_before, extent_before = actor.get_actor_bounds(False)
            bottom_before = float(origin_before.z - extent_before.z)
            target_z = promenade_surface_z_cm(x_cm, y_cm)
            location = actor.get_actor_location()
            actor.set_actor_location(unreal.Vector(location.x, location.y, location.z + target_z - bottom_before), False, True)
            origin_after, extent_after = actor.get_actor_bounds(False)
            bottom_after = float(origin_after.z - extent_after.z)
            require(abs(bottom_after - target_z) <= 1.0, f"Bicycle-rack grounding failed: {index + 1:02d}")
            result["placements"].append({"label": actor.get_actor_label(), "location_cm": vector(actor.get_actor_location()), "rotation_deg": [float(actor.get_actor_rotation().roll), float(actor.get_actor_rotation().pitch), float(actor.get_actor_rotation().yaw)], "scale": vector(actor.get_actor_scale3d()), "surface_target_z_cm": target_z, "bottom_after_cm": bottom_after, "bounds_extent_cm": vector(extent_after)})

        after = list(actors_api.get_all_level_actors())
        result["actor_count_after"] = len(after)
        require(len(result["placements"]) == PLACEMENT_COUNT, "Bicycle-rack placement count changed")
        require(len(after) == EXPECTED_ACTORS_BEFORE + PLACEMENT_COUNT, f"Final actor count changed: {len(after)}")
        require(levels.save_current_level(), "Failed to save fresh bicycle-rack map")
        require(OUTPUT_FILE.is_file(), "Fresh bicycle-rack map was not created")

        result["input_map_after"] = record(INPUT_FILE)
        require(result["input_map_after"]["sha256"] == INPUT_SHA256, "Accepted input map changed")
        require(sha256(SOURCE) == SOURCE_SHA256, "Accepted source GLB changed")
        require(sha256(ACCEPTANCE_FREEZE) == ACCEPTANCE_FREEZE_SHA256, "Acceptance freeze changed")
        result["output_map"] = record(OUTPUT_FILE)
        result["asset_inventory"] = inventory(DESTINATION_DISK)
        require(result["asset_inventory"], "Saved bicycle-rack asset inventory is empty")
        result["classification"] = "PASSED_M01_BICYCLE_RACK_RECOVERY02_UNREAL_INTEGRATION01_READY_FOR_D3D12_VISUAL_PROOF"
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        result["traceback"] = traceback.format_exc()
    finally:
        write_json_atomic(RECEIPT, result)

    if result["classification"].startswith("PASSED_"):
        unreal.SystemLibrary.quit_editor()
    else:
        raise RuntimeError(result["error"] or "Bicycle-rack Unreal integration failed")


if "--offline-contract-test" in sys.argv:
    raise SystemExit(run_offline_contract_test())

run_unreal()
