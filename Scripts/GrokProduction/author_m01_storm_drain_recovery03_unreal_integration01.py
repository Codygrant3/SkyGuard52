"""Import the accepted storm drain without GLB materials and place grounded instances in a fresh M01 map."""

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
SOURCE = ROOT / r"Production\Attempts\m01-storm-drain-deterministic-recovery03\attempt_20260811T104500000000Z\output\exports\M01_Promenade_StormDrain_Recovery03.glb"
SOURCE_BYTES = 149_996
SOURCE_SHA256 = "e5eac4d8040703eeb7abf056711b525a709113c1538a6ebf08ae5369ff78cf4c"
ACCEPTANCE_FREEZE = ROOT / r"Docs\AAA_Review\M01_STORM_DRAIN_DETERMINISTIC_RECOVERY03_ACCEPTANCE_FREEZE.json"
ACCEPTANCE_FREEZE_BYTES = 3_212
ACCEPTANCE_FREEZE_SHA256 = "1c1944a5a194ca8ca20e0cba1a842fd23f2d56dfcc5c3eae9d3ad81ce12a1574"
PROJECT = ISOLATED / "Skyguard52.uproject"
PROJECT_BYTES = 3_703
PROJECT_SHA256 = "7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a"
INPUT_ASSET = "/Game/M01/Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01Recovery01_PromenadeBollards01_BicycleRacks01_UtilityCabinets01Recovery01"
OUTPUT_ASSET = "/Game/M01/Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01Recovery01_PromenadeBollards01_BicycleRacks01_UtilityCabinets01Recovery01_StormDrains01"
INPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01Recovery01_PromenadeBollards01_BicycleRacks01_UtilityCabinets01Recovery01.umap"
OUTPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01Recovery01_PromenadeBollards01_BicycleRacks01_UtilityCabinets01Recovery01_StormDrains01.umap"
INPUT_BYTES = 767_680
INPUT_SHA256 = "529894f4e025e80781c3e5901e7fd59aa38448db4c6cf850cc3a1855e075c7e3"
DESTINATION = "/Game/M01/PromenadeStormDrainRecovery03"
DESTINATION_DISK = ISOLATED / "Content/M01/PromenadeStormDrainRecovery03"
ATTEMPT = ROOT / r"Saved\BuildAttempts\M01_STORM_DRAIN_RECOVERY03_UNREAL_INTEGRATION01\attempt_01"
RECEIPT = ATTEMPT / "integration_receipt.json"
MESH_NAME = "SM_M01_Promenade_StormDrain_A"
SOCKET_NODE = "SOCKET_StormDrain_Origin"
COLLISION_NODE = "UCX_SM_M01_Promenade_StormDrain_A_00"
CANONICAL_SOCKET = "M01_StormDrain_Origin"
RUNTIME_MATERIAL_ASSET = "/Game/Skyguard/Materials/M_MetalRust"
RUNTIME_MATERIAL_FILE = ISOLATED / "Content/Skyguard/Materials/M_MetalRust.uasset"
RUNTIME_MATERIAL_BYTES = 11_482
RUNTIME_MATERIAL_SHA256 = "2aad50bf560d653e8df430473619de370c52920a0f97c190bca7115a915df9ad"
PLACEMENT_COUNT = 12
EXPECTED_ACTORS_BEFORE = 126


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
    require(SOURCE.is_file() and SOURCE.stat().st_size == SOURCE_BYTES and sha256(SOURCE) == SOURCE_SHA256, "Accepted storm-drain GLB is missing or changed")
    require(ACCEPTANCE_FREEZE.is_file() and ACCEPTANCE_FREEZE.stat().st_size == ACCEPTANCE_FREEZE_BYTES and sha256(ACCEPTANCE_FREEZE) == ACCEPTANCE_FREEZE_SHA256, "Storm-drain acceptance freeze is missing or changed")
    freeze = json.loads(ACCEPTANCE_FREEZE.read_text(encoding="utf-8"))
    require(freeze.get("classification") == "PASSED_PROVISIONAL_MID_DISTANCE_RUNTIME_CANDIDATE", "Unexpected storm-drain acceptance classification")
    require(freeze.get("unreal_staging_authorized") is True, "Acceptance freeze does not authorize Unreal staging")

    document = read_glb_document(SOURCE)
    meshes = [str(row.get("name", "")) for row in document.get("meshes", [])]
    nodes = {str(row.get("name", "")) for row in document.get("nodes", [])}
    materials = [str(row.get("name", "")) for row in document.get("materials", [])]
    require({MESH_NAME, SOCKET_NODE, COLLISION_NODE}.issubset(nodes), f"Accepted GLB node contract changed: {sorted(nodes)}")
    require(len(meshes) == 2 and any(MESH_NAME in name for name in meshes), f"Accepted GLB mesh contract changed: {meshes}")
    require(materials == ["M_M01_StormDrain_CastIron", "M_M01_StormDrain_DarkRecess", "M_M01_StormDrain_EdgeWear"], f"Accepted material identity changed: {materials}")
    return {
        "source": record(SOURCE),
        "acceptance_freeze": record(ACCEPTANCE_FREEZE),
        "meshes": meshes,
        "nodes": sorted(nodes),
        "source_materials": materials,
        "material_import_policy": "disabled_to_avoid_ue58_interchange_specular_color_factor_failure",
    }


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
    require(RUNTIME_MATERIAL_FILE.is_file() and RUNTIME_MATERIAL_FILE.stat().st_size == RUNTIME_MATERIAL_BYTES and sha256(RUNTIME_MATERIAL_FILE) == RUNTIME_MATERIAL_SHA256, "Runtime metal material authority changed")
    require(not DESTINATION_DISK.exists(), "Fresh storm-drain import namespace already exists")
    require(not OUTPUT_FILE.exists(), "Fresh storm-drain output map already exists")
    require(not ATTEMPT.exists(), "Fresh storm-drain attempt namespace already exists")
    compile(Path(__file__).read_text(encoding="utf-8"), __file__, "exec")
    print("PASS_M01_STORM_DRAIN_RECOVERY03_UNREAL_INTEGRATION01_CONTRACT")
    return 0


def run_unreal() -> None:
    import unreal

    result: dict[str, object] = {
        "schema": "skyguard.m01-storm-drain-recovery03.unreal-integration01.v1",
        "classification": "FAILED_WITH_EVIDENCE",
        "source_contract": None,
        "input_asset": INPUT_ASSET,
        "output_asset": OUTPUT_ASSET,
        "destination": DESTINATION,
        "input_map_before": None,
        "input_map_after": None,
        "imported_assets": [],
        "storm_drain_mesh": None,
        "runtime_material": None,
        "placements": [],
        "actor_count_before": None,
        "actor_count_after": None,
        "output_map": None,
        "asset_inventory": [],
        "rollback_manifest": {
            "created_asset_namespace": DESTINATION,
            "created_map": OUTPUT_ASSET,
            "accepted_inputs_mutated": False,
        },
        "error": None,
        "traceback": None,
    }

    try:
        result["source_contract"] = validate_source_contract()
        require(PROJECT.is_file() and PROJECT.stat().st_size == PROJECT_BYTES and sha256(PROJECT) == PROJECT_SHA256, "Isolated project authority changed")
        require(RUNTIME_MATERIAL_FILE.is_file() and RUNTIME_MATERIAL_FILE.stat().st_size == RUNTIME_MATERIAL_BYTES and sha256(RUNTIME_MATERIAL_FILE) == RUNTIME_MATERIAL_SHA256, "Runtime metal material authority changed")
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
        mesh_pipeline = pipeline.get_editor_property("mesh_pipeline")
        mesh_pipeline.set_editor_property("collision", True)
        mesh_pipeline.set_editor_property("import_collision_according_to_mesh_name", True)
        mesh_pipeline.set_editor_property("one_convex_hull_per_ucx", True)
        material_pipeline = pipeline.get_editor_property("material_pipeline")
        material_pipeline.set_editor_property("import_materials", False)
        texture_pipeline = material_pipeline.get_editor_property("texture_pipeline")
        texture_pipeline.set_editor_property("import_textures", False)
        stack = unreal.InterchangePipelineStackOverride()
        stack.add_pipeline(pipeline)

        require(unreal.EditorAssetLibrary.make_directory(DESTINATION), "Failed to create storm-drain import namespace")
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
        require(imported_paths, "Storm-drain Interchange import produced no assets")
        render_mesh = None
        for asset_path in imported_paths:
            asset = unreal.EditorAssetLibrary.load_asset(asset_path)
            require(asset is not None, f"Imported asset failed to load: {asset_path}")
            row: dict[str, object] = {
                "path": asset_path,
                "class": asset.get_class().get_name(),
                "name": asset.get_name(),
            }
            require(row["class"] not in {"Material", "MaterialInstanceConstant", "Texture2D"}, f"Material/texture import was not disabled: {row}")
            if isinstance(asset, unreal.StaticMesh):
                bounds = asset.get_bounds()
                row.update(
                    {
                        "bounds_origin_cm": vector(bounds.origin),
                        "bounds_extent_cm": vector(bounds.box_extent),
                        "material_slot_count": len(list(asset.get_editor_property("static_materials"))),
                        "lod_count": int(asset.get_num_lods()),
                    }
                )
                if asset.get_name() == MESH_NAME:
                    render_mesh = asset
            result["imported_assets"].append(row)
        require(render_mesh is not None, f"Accepted storm-drain StaticMesh not imported: {MESH_NAME}")

        extent = vector(render_mesh.get_bounds().box_extent)
        require(32.0 <= extent[0] <= 36.0 and 22.0 <= extent[1] <= 26.0 and 4.0 <= extent[2] <= 6.0, f"Storm-drain bounds changed: {extent}")
        require(int(render_mesh.get_num_lods()) >= 1, "Imported storm drain has no LOD")
        materials = list(render_mesh.get_editor_property("static_materials"))
        require(len(materials) >= 1, "Imported storm drain has no material slots")
        runtime_material = unreal.EditorAssetLibrary.load_asset(RUNTIME_MATERIAL_ASSET)
        require(runtime_material is not None, f"Runtime metal material failed to load: {RUNTIME_MATERIAL_ASSET}")
        for index in range(len(materials)):
            render_mesh.set_material(index, runtime_material)
        assigned_materials = [render_mesh.get_material(index) for index in range(len(materials))]
        require(all(material is not None and material.get_path_name().startswith(RUNTIME_MATERIAL_ASSET) for material in assigned_materials), "Runtime metal material assignment failed")

        body_setup = render_mesh.get_editor_property("body_setup")
        require(body_setup is not None, "Imported storm drain has no BodySetup")
        body_setup.set_editor_property("collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
        socket = render_mesh.find_socket(CANONICAL_SOCKET)
        if socket is None:
            socket = unreal.StaticMeshSocket(outer=render_mesh)
            socket.set_editor_property("socket_name", CANONICAL_SOCKET)
            socket.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 0.0))
            render_mesh.add_socket(socket)
        require(render_mesh.find_socket(CANONICAL_SOCKET) is not None, "Canonical storm-drain origin socket is missing")
        try:
            unreal.EditorAssetLibrary.save_loaded_asset(render_mesh, only_if_is_dirty=False)
            unreal.EditorAssetLibrary.save_directory(DESTINATION, only_if_is_dirty=False, recursive=True)
        except TypeError:
            unreal.EditorAssetLibrary.save_loaded_asset(render_mesh)
            unreal.EditorAssetLibrary.save_directory(DESTINATION)

        result["runtime_material"] = record(RUNTIME_MATERIAL_FILE)
        result["storm_drain_mesh"] = {
            "path": render_mesh.get_path_name(),
            "bounds_origin_cm": vector(render_mesh.get_bounds().origin),
            "bounds_extent_cm": extent,
            "material_slot_count": len(materials),
            "assigned_material": RUNTIME_MATERIAL_ASSET,
            "collision": "CTF_USE_COMPLEX_AS_SIMPLE",
            "canonical_socket": CANONICAL_SOCKET,
        }

        levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        actors_api = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        require(levels is not None and actors_api is not None, "Required editor subsystems are unavailable")
        require(levels.new_level_from_template(OUTPUT_ASSET, INPUT_ASSET), "Failed to duplicate accepted corridor map")
        before = list(actors_api.get_all_level_actors())
        result["actor_count_before"] = len(before)
        require(len(before) == EXPECTED_ACTORS_BEFORE, f"Accepted corridor actor count changed: {len(before)}")
        require(not any(actor.get_actor_label().startswith("M01_Promenade_StormDrain_") for actor in before), "Storm-drain labels already exist in accepted input map")

        x_positions = [4000.0 + 5000.0 * index for index in range(PLACEMENT_COUNT)]
        y_offsets = (-35.0, 20.0, -10.0, 30.0)
        yaw_offsets = (0.0, 0.8, -0.6, 0.4)
        for index, x_cm in enumerate(x_positions):
            y_cm = 7350.0 + y_offsets[index % len(y_offsets)]
            yaw = yaw_offsets[index % len(yaw_offsets)]
            actor = actors_api.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x_cm, y_cm, 0.0), unreal.Rotator(0.0, yaw, 0.0), False)
            require(actor is not None, f"Failed to spawn storm drain {index + 1:02d}")
            actor.set_actor_label(f"M01_Promenade_StormDrain_{index + 1:02d}")
            actor.set_folder_path("M01/PromenadeProps/StormDrains")
            component = actor.get_component_by_class(unreal.StaticMeshComponent)
            require(component is not None, f"StaticMeshComponent missing for storm drain {index + 1:02d}")
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
            require(abs(bottom_after - target_z) <= 1.0, f"Storm-drain grounding failed: {index + 1:02d}")
            result["placements"].append(
                {
                    "label": actor.get_actor_label(),
                    "location_cm": vector(actor.get_actor_location()),
                    "rotation_deg": [float(actor.get_actor_rotation().roll), float(actor.get_actor_rotation().pitch), float(actor.get_actor_rotation().yaw)],
                    "surface_target_z_cm": target_z,
                    "bottom_after_cm": bottom_after,
                    "bounds_extent_cm": vector(extent_after),
                }
            )

        after = list(actors_api.get_all_level_actors())
        result["actor_count_after"] = len(after)
        require(len(result["placements"]) == PLACEMENT_COUNT, "Storm-drain placement count changed")
        require(len(after) == EXPECTED_ACTORS_BEFORE + PLACEMENT_COUNT, f"Final actor count changed: {len(after)}")
        require(levels.save_current_level(), "Failed to save fresh storm-drain map")
        require(OUTPUT_FILE.is_file(), "Fresh storm-drain map was not created")

        result["input_map_after"] = record(INPUT_FILE)
        require(result["input_map_after"]["sha256"] == INPUT_SHA256, "Accepted input map changed")
        require(sha256(SOURCE) == SOURCE_SHA256, "Accepted source GLB changed")
        require(sha256(ACCEPTANCE_FREEZE) == ACCEPTANCE_FREEZE_SHA256, "Acceptance freeze changed")
        require(sha256(RUNTIME_MATERIAL_FILE) == RUNTIME_MATERIAL_SHA256, "Runtime material changed")
        result["output_map"] = record(OUTPUT_FILE)
        result["asset_inventory"] = inventory(DESTINATION_DISK)
        require(result["asset_inventory"], "Saved storm-drain asset inventory is empty")
        result["classification"] = "PASSED_M01_STORM_DRAIN_RECOVERY03_UNREAL_INTEGRATION01_READY_FOR_D3D12_VISUAL_PROOF"
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        result["traceback"] = traceback.format_exc()
    finally:
        write_json_atomic(RECEIPT, result)

    if result["classification"].startswith("PASSED_"):
        unreal.SystemLibrary.quit_editor()
        return
    raise RuntimeError(result["error"] or "Storm-drain Unreal integration failed")


if "--offline-contract-test" in sys.argv:
    raise SystemExit(run_offline_contract_test())

run_unreal()
