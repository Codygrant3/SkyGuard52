"""Import the accepted Igla missile candidate into a fresh Unreal staging namespace.

This is deliberately not a gameplay binding.  The accepted asset is a
mid-distance visual candidate, so the authoring pass creates a dedicated audit
map and leaves every existing runtime proxy untouched.
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
SOURCE = ROOT / r"Production\Attempts\core-igla-missile-grok-mcp-refinement01\attempt_20260811T0737000000000Z\output\exports\CORE_IglaMissile_Refinement01.glb"
SOURCE_BYTES = 1_079_028
SOURCE_SHA256 = "f17b665bd8f7a88fc05d9a925e910c0a74fa43b5c4f3a87c28446f7a581ea497"
ACCEPTANCE_FREEZE = ROOT / r"Docs\AAA_Review\CORE_IGLA_MISSILE_GROK_MCP_REFINEMENT01_ACCEPTANCE_FREEZE.json"
ACCEPTANCE_FREEZE_BYTES = 2_952
ACCEPTANCE_FREEZE_SHA256 = "9c9cc2a4b48522fe3dd5fc0cbe5421047c4e209982f2e9c2a50700b2c390adcc"
PROJECT = ISOLATED / "Skyguard52.uproject"
PROJECT_BYTES = 3_703
PROJECT_SHA256 = "7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a"
DESTINATION = "/Game/Skyguard/Combat/Weapons/IglaMissileRefinement01"
DESTINATION_DISK = ISOLATED / "Content/Skyguard/Combat/Weapons/IglaMissileRefinement01"
MAP_ASSET = DESTINATION + "/Lvl_CORE_IglaMissile_Refinement01_ImportAudit"
MAP_FILE = DESTINATION_DISK / "Lvl_CORE_IglaMissile_Refinement01_ImportAudit.umap"
ATTEMPT = ROOT / r"Saved\BuildAttempts\CORE_IGLA_MISSILE_REFINEMENT01_UNREAL_INTEGRATION01\attempt_01"
RECEIPT = ATTEMPT / "integration_receipt.json"
MESH_NAME = "SM_CORE_IglaMissile_Provisional_A"
AUTHORITY_NODE = "AUTH_IglaMissile_Body_1574x0072"
COLLISION_NODE = "UCX_SM_CORE_IglaMissile_Provisional_A_Body"
SOCKETS = (
    "SOCKET_IglaMissile_ForwardOrigin_PROVISIONAL",
    "SOCKET_IglaMissile_RearAxis_PROVISIONAL",
    "SOCKET_IglaMissile_Exhaust_PROVISIONAL",
)
MATERIALS = (
    "M_IglaMissile_BodyPaint_Provisional",
    "M_IglaMissile_NoseBlueGrey_Provisional",
    "M_IglaMissile_BandCharcoal_Provisional",
    "M_IglaMissile_TailMetalPaint_Provisional",
)


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
    if not path.exists():
        return []
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
    require(SOURCE.is_file() and SOURCE.stat().st_size == SOURCE_BYTES, "Accepted Igla GLB is missing or changed")
    require(sha256(SOURCE) == SOURCE_SHA256, "Accepted Igla GLB hash changed")
    require(
        ACCEPTANCE_FREEZE.is_file() and ACCEPTANCE_FREEZE.stat().st_size == ACCEPTANCE_FREEZE_BYTES,
        "Igla acceptance freeze is missing or changed",
    )
    require(sha256(ACCEPTANCE_FREEZE) == ACCEPTANCE_FREEZE_SHA256, "Igla acceptance freeze hash changed")
    freeze = json.loads(ACCEPTANCE_FREEZE.read_text(encoding="utf-8"))
    require(
        freeze.get("classification") == "PASSED_PROVISIONAL_MID_DISTANCE_RUNTIME_CANDIDATE",
        "Unexpected Igla acceptance classification",
    )
    members = {str(row.get("path")): row for row in freeze.get("members", [])}
    require(str(SOURCE) in members and members[str(SOURCE)].get("sha256") == SOURCE_SHA256, "Accepted GLB is not bound by the freeze")

    document = read_glb_document(SOURCE)
    nodes = {str(row.get("name", "")) for row in document.get("nodes", [])}
    materials = tuple(str(row.get("name", "")) for row in document.get("materials", []))
    required_nodes = {MESH_NAME, AUTHORITY_NODE, COLLISION_NODE, *SOCKETS}
    require(required_nodes.issubset(nodes), f"Accepted GLB node contract changed: {sorted(nodes)}")
    require(materials == MATERIALS, f"Accepted GLB material contract changed: {materials}")
    return {
        "source": record(SOURCE),
        "acceptance_freeze": record(ACCEPTANCE_FREEZE),
        "nodes": sorted(nodes),
        "materials": list(materials),
    }


def run_offline_contract_test() -> int:
    validate_source_contract()
    require(PROJECT.is_file() and PROJECT.stat().st_size == PROJECT_BYTES and sha256(PROJECT) == PROJECT_SHA256, "Isolated project authority changed")
    require(not DESTINATION_DISK.exists(), "Fresh Igla import namespace already exists")
    require(not MAP_FILE.exists(), "Fresh Igla audit map already exists")
    require(not ATTEMPT.exists(), "Fresh Igla attempt namespace already exists")
    compile(Path(__file__).read_text(encoding="utf-8"), __file__, "exec")
    print("PASS_CORE_IGLA_MISSILE_REFINEMENT01_UNREAL_INTEGRATION01_CONTRACT")
    return 0


def run_unreal() -> None:
    import unreal

    result: dict[str, object] = {
        "schema": "skyguard.core-igla-missile-refinement01.unreal-integration01.v1",
        "classification": "FAILED_WITH_EVIDENCE",
        "accepted_scope": "mid-distance visual candidate only; no gameplay binding or runtime replacement",
        "source_contract": None,
        "destination": DESTINATION,
        "map_asset": MAP_ASSET,
        "imported_assets": [],
        "render_mesh": None,
        "placements": [],
        "output_map": None,
        "asset_inventory": [],
        "rollback_manifest": {
            "created_asset_namespace": DESTINATION,
            "created_map": MAP_ASSET,
            "existing_runtime_proxy_replaced": False,
            "accepted_inputs_mutated": False,
        },
        "error": None,
        "traceback": None,
    }

    try:
        result["source_contract"] = validate_source_contract()
        require(PROJECT.is_file() and PROJECT.stat().st_size == PROJECT_BYTES and sha256(PROJECT) == PROJECT_SHA256, "Isolated project authority changed")
        require(not DESTINATION_DISK.exists(), f"Fresh import namespace exists: {DESTINATION_DISK}")
        require(not unreal.EditorAssetLibrary.does_directory_exist(DESTINATION), f"Fresh import namespace exists: {DESTINATION}")
        require(not MAP_FILE.exists() and not unreal.EditorAssetLibrary.does_asset_exist(MAP_ASSET), "Fresh audit map exists")

        pipeline = unreal.InterchangeGenericAssetsPipeline()
        pipeline.set_editor_property("scene_name_sub_folder", False)
        pipeline.set_editor_property("asset_type_sub_folders", True)
        pipeline.set_editor_property("use_source_name_for_asset", False)
        common = pipeline.get_editor_property("common_meshes_properties")
        common.set_editor_property("import_sockets", True)
        common.set_editor_property("bake_meshes", True)
        stack = unreal.InterchangePipelineStackOverride()
        stack.add_pipeline(pipeline)

        require(unreal.EditorAssetLibrary.make_directory(DESTINATION), "Failed to create Igla staging namespace")
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
        require(imported_paths, "Igla Interchange import produced no assets")
        render_mesh = None
        for asset_path in imported_paths:
            asset = unreal.EditorAssetLibrary.load_asset(asset_path)
            require(asset is not None, f"Imported asset failed to load: {asset_path}")
            row: dict[str, object] = {"path": asset_path, "class": asset.get_class().get_name(), "name": asset.get_name()}
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
        require(render_mesh is not None, f"Accepted Igla StaticMesh not imported: {MESH_NAME}")

        bounds = render_mesh.get_bounds()
        extent = vector(bounds.box_extent)
        full = [value * 2.0 for value in extent]
        require(156.5 <= full[0] <= 158.3, f"Igla length authority changed in Unreal: {full}")
        require(17.0 <= full[1] <= 19.5 and 17.0 <= full[2] <= 19.5, f"Igla fin envelope changed in Unreal: {full}")
        require(int(render_mesh.get_num_lods()) >= 1, "Imported Igla has no LOD")
        materials = list(render_mesh.get_editor_property("static_materials"))
        require(len(materials) == 4, f"Igla material-slot count changed: {len(materials)}")
        body_setup = render_mesh.get_editor_property("body_setup")
        require(body_setup is not None, "Imported Igla has no BodySetup")
        for socket_name in SOCKETS:
            require(render_mesh.find_socket(socket_name) is not None, f"Imported Igla socket missing: {socket_name}")

        try:
            unreal.EditorAssetLibrary.save_loaded_asset(render_mesh, only_if_is_dirty=False)
            unreal.EditorAssetLibrary.save_directory(DESTINATION, only_if_is_dirty=False, recursive=True)
        except TypeError:
            unreal.EditorAssetLibrary.save_loaded_asset(render_mesh)
            unreal.EditorAssetLibrary.save_directory(DESTINATION)

        result["render_mesh"] = {
            "path": render_mesh.get_path_name(),
            "bounds_origin_cm": vector(bounds.origin),
            "bounds_extent_cm": extent,
            "full_dimensions_cm": full,
            "material_slot_count": len(materials),
            "lod_count": int(render_mesh.get_num_lods()),
            "body_setup_present": True,
            "sockets": list(SOCKETS),
        }

        require(unreal.EditorLevelLibrary.new_level(MAP_ASSET), "Failed to create fresh Igla import-audit level")
        actors_api = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        require(actors_api is not None, "EditorActorSubsystem is unavailable")
        transforms = (
            ("Side_A", unreal.Vector(-190.0, 0.0, 125.0), unreal.Rotator(0.0, 0.0, 0.0)),
            ("Side_B", unreal.Vector(190.0, 0.0, 125.0), unreal.Rotator(0.0, 180.0, 0.0)),
            ("Oblique", unreal.Vector(0.0, 230.0, 150.0), unreal.Rotator(-18.0, 35.0, 0.0)),
        )
        for suffix, location, rotation in transforms:
            actor = actors_api.spawn_actor_from_class(unreal.StaticMeshActor, location, rotation, False)
            require(actor is not None, f"Failed to spawn Igla audit actor: {suffix}")
            actor.set_actor_label(f"AUDIT_CORE_IglaMissile_{suffix}")
            actor.set_folder_path("Audit/Combat/IglaMissileRefinement01")
            component = actor.get_component_by_class(unreal.StaticMeshComponent)
            require(component is not None, f"Igla audit StaticMeshComponent missing: {suffix}")
            component.set_static_mesh(render_mesh)
            component.set_mobility(unreal.ComponentMobility.STATIC)
            component.set_collision_profile_name("BlockAll")
            result["placements"].append(
                {
                    "label": actor.get_actor_label(),
                    "location_cm": vector(actor.get_actor_location()),
                    "rotation_deg": [
                        float(actor.get_actor_rotation().roll),
                        float(actor.get_actor_rotation().pitch),
                        float(actor.get_actor_rotation().yaw),
                    ],
                }
            )

        require(len(result["placements"]) == 3, "Igla audit placement count changed")
        require(unreal.EditorLevelLibrary.save_current_level(), "Failed to save fresh Igla import-audit level")
        require(MAP_FILE.is_file(), "Fresh Igla import-audit map was not created")
        require(sha256(SOURCE) == SOURCE_SHA256, "Accepted source GLB changed")
        require(sha256(ACCEPTANCE_FREEZE) == ACCEPTANCE_FREEZE_SHA256, "Acceptance freeze changed")
        require(PROJECT.stat().st_size == PROJECT_BYTES and sha256(PROJECT) == PROJECT_SHA256, "Isolated project authority changed during import")
        result["output_map"] = record(MAP_FILE)
        result["asset_inventory"] = inventory(DESTINATION_DISK)
        require(result["asset_inventory"], "Saved Igla staging inventory is empty")
        result["classification"] = "PASSED_CORE_IGLA_MISSILE_REFINEMENT01_UNREAL_STAGING_READY_FOR_D3D12_VISUAL_PROOF"
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        result["traceback"] = traceback.format_exc()
    finally:
        write_json_atomic(RECEIPT, result)

    if result["classification"].startswith("PASSED_"):
        unreal.SystemLibrary.quit_editor()
    else:
        raise RuntimeError(result["error"] or "Igla Unreal staging import failed")


if "--offline-contract-test" in sys.argv:
    raise SystemExit(run_offline_contract_test())

run_unreal()
