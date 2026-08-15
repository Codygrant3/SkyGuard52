"""Reversibly import the accepted promenade bollard and place it in a fresh M01 map."""

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
SOURCE = ROOT / (
    r"Production\Attempts\m01-promenade-prop-kit-grok-mcp-recovery01"
    r"\attempt_20260811T063000000000Z\output\exports\M01_Promenade_Bollard_A.glb"
)
SOURCE_BYTES = 239_084
SOURCE_SHA256 = "585c830686015d9733640dbbc6d4785d1f23c3fad043a8317642dec1b3ad550f"
ACCEPTANCE_FREEZE = ROOT / r"Docs\AAA_Review\M01_PROMENADE_PROP_KIT_GROK_MCP_PRODUCTION_RECOVERY01_POSTREVIEW_TERMINAL_FREEZE.json"
ACCEPTANCE_FREEZE_BYTES = 2_888
ACCEPTANCE_FREEZE_SHA256 = "99aa93fb74dff633d472144b44c524b69b43af07453f15092db3583f776484dd"
PROJECT = ISOLATED / "Skyguard52.uproject"
PROJECT_BYTES = 3_703
PROJECT_SHA256 = "7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a"
INPUT_ASSET = "/Game/M01/Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01Recovery01"
OUTPUT_ASSET = "/Game/M01/Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01Recovery01_PromenadeBollards01"
INPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01Recovery01.umap"
OUTPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01Recovery01_PromenadeBollards01.umap"
INPUT_BYTES = 707_628
INPUT_SHA256 = "a2ccdbe88a77821acb3e601cc129af932f9061f8def90af452d620895ed6a1aa"
DESTINATION = "/Game/M01/PromenadeBollardRecovery01"
DESTINATION_DISK = ISOLATED / "Content/M01/PromenadeBollardRecovery01"
ATTEMPT = ROOT / r"Saved\BuildAttempts\M01_PROMENADE_BOLLARD_RECOVERY01_UNREAL_INTEGRATION01\attempt_01"
RECEIPT = ATTEMPT / "integration_receipt.json"
MESH_NAME = "SM_M01_Promenade_Bollard_A"
COLLISION_NAME = "UCX_SM_M01_Promenade_Bollard_A_00"
SOCKET_NAME = "SOCKET_Bollard_Origin"
PLACEMENT_COUNT = 13
EXPECTED_ACTORS_BEFORE = 100


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
    require(SOURCE.is_file() and SOURCE.stat().st_size == SOURCE_BYTES, "Accepted bollard GLB is missing or changed")
    require(sha256(SOURCE) == SOURCE_SHA256, "Accepted bollard GLB hash changed")
    require(ACCEPTANCE_FREEZE.is_file() and ACCEPTANCE_FREEZE.stat().st_size == ACCEPTANCE_FREEZE_BYTES, "Accepted postreview freeze is missing or changed")
    require(sha256(ACCEPTANCE_FREEZE) == ACCEPTANCE_FREEZE_SHA256, "Accepted postreview freeze hash changed")
    freeze = json.loads(ACCEPTANCE_FREEZE.read_text(encoding="utf-8"))
    require(freeze.get("classification") == "PARTIAL_ACCEPTANCE_WITH_EXPLICIT_REJECTIONS", "Unexpected postreview classification")
    accepted = {row.get("asset"): row for row in freeze.get("accepted_subset", [])}
    require(MESH_NAME in accepted and accepted[MESH_NAME].get("sha256") == SOURCE_SHA256, "Bollard is not the frozen accepted subset")

    document = read_glb_document(SOURCE)
    meshes = {str(row.get("name", "")): len(row.get("primitives", [])) for row in document.get("meshes", [])}
    nodes = {str(row.get("name", "")) for row in document.get("nodes", [])}
    materials = [str(row.get("name", "")) for row in document.get("materials", [])]
    require(set(meshes) == {MESH_NAME, COLLISION_NAME}, f"Accepted mesh contract changed: {meshes}")
    require(MESH_NAME in nodes and COLLISION_NAME in nodes and SOCKET_NAME in nodes, f"Accepted node contract changed: {sorted(nodes)}")
    require(len(materials) == 5 and len(set(materials)) == 5, f"Accepted material contract changed: {materials}")
    return {
        "source": record(SOURCE),
        "acceptance_freeze": record(ACCEPTANCE_FREEZE),
        "meshes": meshes,
        "nodes": sorted(nodes),
        "materials": materials,
    }


def promenade_surface_z_cm(x_cm: float, y_cm: float) -> float:
    """Mirror the accepted corridor profile after the positive-Y axis correction."""
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
    require(not DESTINATION_DISK.exists(), "Fresh bollard import namespace already exists")
    require(not OUTPUT_FILE.exists(), "Fresh bollard output map already exists")
    require(not ATTEMPT.exists(), "Fresh bollard attempt namespace already exists")
    compile(Path(__file__).read_text(encoding="utf-8"), __file__, "exec")
    print("PASS_M01_PROMENADE_BOLLARD_RECOVERY01_UNREAL_INTEGRATION01_CONTRACT")
    return 0


def collision_summary(mesh: object) -> dict[str, object]:
    body_setup = mesh.get_editor_property("body_setup")
    require(body_setup is not None, "Imported bollard StaticMesh has no BodySetup")
    aggregate = body_setup.get_editor_property("agg_geom")
    convex = list(aggregate.get_editor_property("convex_elems"))
    return {"body_setup_present": True, "convex_element_count": len(convex)}


def run_unreal() -> None:
    import unreal

    result: dict[str, object] = {
        "schema": "skyguard.m01-promenade-bollard-recovery01.unreal-integration01.v1",
        "classification": "FAILED_WITH_EVIDENCE",
        "source_contract": None,
        "input_asset": INPUT_ASSET,
        "output_asset": OUTPUT_ASSET,
        "destination": DESTINATION,
        "input_map_before": None,
        "input_map_after": None,
        "imported_assets": [],
        "bollard_mesh": None,
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

        require(unreal.EditorAssetLibrary.make_directory(DESTINATION), "Failed to create bollard import namespace")
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
        require(imported_paths, "Bollard Interchange import produced no assets")
        render_mesh = None
        collision_asset_paths: list[str] = []
        for asset_path in imported_paths:
            asset = unreal.EditorAssetLibrary.load_asset(asset_path)
            require(asset is not None, f"Imported asset failed to load: {asset_path}")
            row: dict[str, object] = {"path": asset_path, "class": asset.get_class().get_name(), "name": asset.get_name()}
            if isinstance(asset, unreal.StaticMesh):
                bounds = asset.get_bounds()
                row.update({
                    "bounds_origin_cm": vector(bounds.origin),
                    "bounds_extent_cm": vector(bounds.box_extent),
                    "material_slot_count": len(list(asset.get_editor_property("static_materials"))),
                    "lod_count": int(asset.get_num_lods()),
                })
                if asset.get_name() == MESH_NAME:
                    render_mesh = asset
                elif asset.get_name().startswith("UCX_"):
                    collision_asset_paths.append(asset_path)
            result["imported_assets"].append(row)
        require(render_mesh is not None, f"Accepted bollard StaticMesh not imported: {MESH_NAME}")

        extent = vector(render_mesh.get_bounds().box_extent)
        require(10.0 <= extent[0] <= 18.0 and 10.0 <= extent[1] <= 18.0, f"Bollard horizontal bounds changed: {extent}")
        require(38.0 <= extent[2] <= 48.0, f"Bollard vertical bounds changed: {extent}")
        require(int(render_mesh.get_num_lods()) >= 1, "Imported bollard has no LOD")
        materials = list(render_mesh.get_editor_property("static_materials"))
        require(len(materials) == 5, f"Bollard material-slot count changed: {len(materials)}")
        collision = collision_summary(render_mesh)
        require(collision["convex_element_count"] >= 1 or collision_asset_paths, "Bollard collision contract was not imported")

        socket = render_mesh.find_socket("M01_Bollard_Origin")
        if socket is None:
            socket = unreal.StaticMeshSocket(outer=render_mesh)
            socket.set_editor_property("socket_name", "M01_Bollard_Origin")
            socket.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 0.0))
            render_mesh.add_socket(socket)
        require(render_mesh.find_socket("M01_Bollard_Origin") is not None, "Canonical bollard origin socket is missing")
        try:
            unreal.EditorAssetLibrary.save_loaded_asset(render_mesh, only_if_is_dirty=False)
        except TypeError:
            unreal.EditorAssetLibrary.save_loaded_asset(render_mesh)
        try:
            unreal.EditorAssetLibrary.save_directory(DESTINATION, only_if_is_dirty=False, recursive=True)
        except TypeError:
            unreal.EditorAssetLibrary.save_directory(DESTINATION)

        result["bollard_mesh"] = {
            "path": render_mesh.get_path_name(),
            "bounds_origin_cm": vector(render_mesh.get_bounds().origin),
            "bounds_extent_cm": extent,
            "material_slot_count": len(materials),
            "collision": collision,
            "separate_collision_assets": collision_asset_paths,
            "canonical_socket": "M01_Bollard_Origin",
        }

        levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        actors_api = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        require(levels is not None and actors_api is not None, "Required editor subsystems are unavailable")
        require(levels.new_level_from_template(OUTPUT_ASSET, INPUT_ASSET), "Failed to duplicate accepted corridor map")
        before = list(actors_api.get_all_level_actors())
        result["actor_count_before"] = len(before)
        require(len(before) == EXPECTED_ACTORS_BEFORE, f"Accepted corridor actor count changed: {len(before)}")
        require(not any(actor.get_actor_label().startswith("M01_Promenade_Bollard_") for actor in before), "Bollard labels already exist in accepted input map")

        x_positions = [2500.0 + 4500.0 * index for index in range(PLACEMENT_COUNT)]
        y_offsets = (-90.0, 35.0, 110.0, -25.0)
        scale_values = (0.96, 1.00, 1.04, 0.99, 1.02)
        for index, x_cm in enumerate(x_positions):
            y_cm = 8250.0 + y_offsets[index % len(y_offsets)]
            scale = scale_values[index % len(scale_values)]
            yaw = float((index * 47) % 360)
            actor = actors_api.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x_cm, y_cm, 0.0), unreal.Rotator(0.0, yaw, 0.0), False)
            require(actor is not None, f"Failed to spawn bollard {index + 1:02d}")
            actor.set_actor_label(f"M01_Promenade_Bollard_{index + 1:02d}")
            actor.set_folder_path("M01/PromenadeProps/Bollards")
            actor.set_actor_scale3d(unreal.Vector(scale, scale, scale))
            component = actor.get_component_by_class(unreal.StaticMeshComponent)
            require(component is not None, f"StaticMeshComponent missing for bollard {index + 1:02d}")
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
            require(abs(bottom_after - target_z) <= 1.0, f"Bollard grounding failed: {index + 1:02d}")
            result["placements"].append({
                "label": actor.get_actor_label(),
                "location_cm": vector(actor.get_actor_location()),
                "rotation_deg": [float(actor.get_actor_rotation().roll), float(actor.get_actor_rotation().pitch), float(actor.get_actor_rotation().yaw)],
                "scale": vector(actor.get_actor_scale3d()),
                "surface_target_z_cm": target_z,
                "bottom_after_cm": bottom_after,
                "bounds_extent_cm": vector(extent_after),
            })

        after = list(actors_api.get_all_level_actors())
        result["actor_count_after"] = len(after)
        require(len(result["placements"]) == PLACEMENT_COUNT, "Bollard placement count changed")
        require(len(after) == EXPECTED_ACTORS_BEFORE + PLACEMENT_COUNT, f"Final actor count changed: {len(after)}")
        require(levels.save_current_level(), "Failed to save fresh bollard map")
        require(OUTPUT_FILE.is_file(), "Fresh bollard map was not created")

        result["input_map_after"] = record(INPUT_FILE)
        require(result["input_map_after"]["sha256"] == INPUT_SHA256, "Accepted input map changed")
        require(sha256(SOURCE) == SOURCE_SHA256, "Accepted source GLB changed")
        require(sha256(ACCEPTANCE_FREEZE) == ACCEPTANCE_FREEZE_SHA256, "Accepted postreview freeze changed")
        result["output_map"] = record(OUTPUT_FILE)
        result["asset_inventory"] = inventory(DESTINATION_DISK)
        require(result["asset_inventory"], "Saved bollard asset inventory is empty")
        result["classification"] = "PASSED_M01_PROMENADE_BOLLARD_RECOVERY01_UNREAL_INTEGRATION01_READY_FOR_D3D12_VISUAL_PROOF"
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        result["traceback"] = traceback.format_exc()
    finally:
        write_json_atomic(RECEIPT, result)

    if result["classification"].startswith("PASSED_"):
        unreal.SystemLibrary.quit_editor()
    else:
        raise RuntimeError(result["error"] or "Promenade bollard Unreal integration failed")


if "--offline-contract-test" in sys.argv:
    raise SystemExit(run_offline_contract_test())

run_unreal()
