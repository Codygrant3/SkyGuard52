"""Recovery01: import the accepted Igla and materialize GLB locators as sockets."""

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
SOURCE_SHA = "f17b665bd8f7a88fc05d9a925e910c0a74fa43b5c4f3a87c28446f7a581ea497"
ACCEPTANCE = ROOT / r"Docs\AAA_Review\CORE_IGLA_MISSILE_GROK_MCP_REFINEMENT01_ACCEPTANCE_FREEZE.json"
ACCEPTANCE_BYTES = 2_952
ACCEPTANCE_SHA = "9c9cc2a4b48522fe3dd5fc0cbe5421047c4e209982f2e9c2a50700b2c390adcc"
FAILED_FREEZE = ROOT / r"Docs\AAA_Review\CORE_IGLA_MISSILE_REFINEMENT01_UNREAL_INTEGRATION01_ATTEMPT01_TERMINAL_FREEZE.json"
FAILED_FREEZE_BYTES = 2_252
FAILED_FREEZE_SHA = "6a97a54c9f8799b84d43bcbc1b56251b9ba06a8c1ff298f18198b34adbbbb760"
PROJECT = ISOLATED / "Skyguard52.uproject"
PROJECT_BYTES = 3_703
PROJECT_SHA = "7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a"
FAILED_DESTINATION = ISOLATED / "Content/Skyguard/Combat/Weapons/IglaMissileRefinement01"
DESTINATION = "/Game/Skyguard/Combat/Weapons/IglaMissileRefinement01Recovery01"
DESTINATION_DISK = ISOLATED / "Content/Skyguard/Combat/Weapons/IglaMissileRefinement01Recovery01"
MAP_ASSET = DESTINATION + "/Lvl_CORE_IglaMissile_Refinement01_Recovery01_ImportAudit"
MAP_FILE = DESTINATION_DISK / "Lvl_CORE_IglaMissile_Refinement01_Recovery01_ImportAudit.umap"
ATTEMPT = ROOT / r"Saved\BuildAttempts\CORE_IGLA_MISSILE_REFINEMENT01_UNREAL_INTEGRATION01_RECOVERY01\attempt_01"
RECEIPT = ATTEMPT / "integration_receipt.json"
MESH_NAME = "SM_CORE_IglaMissile_Provisional_A"
SOCKET_NAMES = (
    "SOCKET_IglaMissile_ForwardOrigin_PROVISIONAL",
    "SOCKET_IglaMissile_RearAxis_PROVISIONAL",
    "SOCKET_IglaMissile_Exhaust_PROVISIONAL",
)
MATERIAL_NAMES = (
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
    return [record(item) for item in sorted(path.rglob("*")) if item.is_file()] if path.exists() else []


def write_json_atomic(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def vec(value: object) -> list[float]:
    return [float(value.x), float(value.y), float(value.z)]


def glb_document() -> dict[str, object]:
    with SOURCE.open("rb") as stream:
        magic, version, total = struct.unpack("<4sII", stream.read(12))
        require(magic == b"glTF" and version == 2 and total == SOURCE.stat().st_size, "Invalid accepted GLB")
        length, kind = struct.unpack("<II", stream.read(8))
        require(kind == 0x4E4F534A, "GLB JSON chunk missing")
        return json.loads(stream.read(length).decode("utf-8").rstrip("\x00 \t\r\n"))


def source_contract() -> dict[str, object]:
    for path, size, digest in (
        (SOURCE, SOURCE_BYTES, SOURCE_SHA),
        (ACCEPTANCE, ACCEPTANCE_BYTES, ACCEPTANCE_SHA),
        (FAILED_FREEZE, FAILED_FREEZE_BYTES, FAILED_FREEZE_SHA),
        (PROJECT, PROJECT_BYTES, PROJECT_SHA),
    ):
        require(path.is_file() and path.stat().st_size == size and sha256(path) == digest, f"Authority mismatch: {path}")
    document = glb_document()
    nodes = {str(node.get("name", "")): node for node in document.get("nodes", [])}
    require(MESH_NAME in nodes, "Accepted render-mesh node is missing")
    require(set(SOCKET_NAMES).issubset(nodes), "Accepted socket-locator nodes are missing")
    materials = tuple(str(item.get("name", "")) for item in document.get("materials", []))
    require(materials == MATERIAL_NAMES, f"Accepted material contract changed: {materials}")
    socket_locations_cm: dict[str, list[float]] = {}
    for name in SOCKET_NAMES:
        translation = nodes[name].get("translation", [0.0, 0.0, 0.0])
        require(len(translation) == 3, f"Invalid GLB socket translation: {name}")
        socket_locations_cm[name] = [float(value) * 100.0 for value in translation]
    require(abs(socket_locations_cm[SOCKET_NAMES[0]][0] - 78.7) < 0.01, "Forward locator authority changed")
    require(abs(socket_locations_cm[SOCKET_NAMES[1]][0] + 78.7) < 0.01, "Rear locator authority changed")
    require(abs(socket_locations_cm[SOCKET_NAMES[2]][0] + 78.7) < 0.01, "Exhaust locator authority changed")
    return {
        "source": record(SOURCE),
        "acceptance": record(ACCEPTANCE),
        "failed_attempt_freeze": record(FAILED_FREEZE),
        "project": record(PROJECT),
        "socket_locations_cm": socket_locations_cm,
    }


def offline_contract_test() -> int:
    source_contract()
    require(FAILED_DESTINATION.is_dir(), "Failed Attempt01 namespace is missing")
    require(not DESTINATION_DISK.exists(), "Fresh Recovery01 destination exists")
    require(not MAP_FILE.exists(), "Fresh Recovery01 map exists")
    require(not ATTEMPT.exists(), "Fresh Recovery01 attempt exists")
    compile(Path(__file__).read_text(encoding="utf-8"), __file__, "exec")
    print("PASS_CORE_IGLA_MISSILE_REFINEMENT01_UNREAL_INTEGRATION01_CONTRACT")
    return 0


def run_unreal() -> None:
    import unreal

    result: dict[str, object] = {
        "schema": "skyguard.core-igla-missile-refinement01.unreal-integration01.recovery01.v1",
        "classification": "FAILED_WITH_EVIDENCE",
        "scope": "mid-distance staging only; no gameplay binding or runtime replacement",
        "source_contract": None,
        "imported_assets": [],
        "mesh": None,
        "placements": [],
        "output_map": None,
        "asset_inventory": [],
        "rollback_manifest": {
            "created_asset_namespace": DESTINATION,
            "created_map": MAP_ASSET,
            "failed_attempt_mutated": False,
            "runtime_proxy_replaced": False,
        },
        "error": None,
        "traceback": None,
    }
    try:
        contract = source_contract()
        result["source_contract"] = contract
        require(FAILED_DESTINATION.is_dir(), "Failed Attempt01 namespace is missing")
        require(not DESTINATION_DISK.exists() and not unreal.EditorAssetLibrary.does_directory_exist(DESTINATION), "Fresh Recovery01 destination exists")
        require(not MAP_FILE.exists() and not unreal.EditorAssetLibrary.does_asset_exist(MAP_ASSET), "Fresh Recovery01 map exists")

        pipeline = unreal.InterchangeGenericAssetsPipeline()
        pipeline.set_editor_property("scene_name_sub_folder", False)
        pipeline.set_editor_property("asset_type_sub_folders", True)
        pipeline.set_editor_property("use_source_name_for_asset", False)
        common = pipeline.get_editor_property("common_meshes_properties")
        common.set_editor_property("import_sockets", True)
        common.set_editor_property("bake_meshes", True)
        stack = unreal.InterchangePipelineStackOverride()
        stack.add_pipeline(pipeline)
        require(unreal.EditorAssetLibrary.make_directory(DESTINATION), "Failed to create Recovery01 destination")
        task = unreal.AssetImportTask()
        task.filename = str(SOURCE)
        task.destination_path = DESTINATION
        task.automated = True
        task.replace_existing = False
        task.save = True
        task.options = stack
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])

        unreal.AssetRegistryHelpers.get_asset_registry().scan_paths_synchronous([DESTINATION], True, False)
        imported = sorted(unreal.EditorAssetLibrary.list_assets(DESTINATION, recursive=True, include_folder=False))
        require(imported, "Recovery01 import produced no assets")
        render_mesh = None
        for asset_path in imported:
            asset = unreal.EditorAssetLibrary.load_asset(asset_path)
            require(asset is not None, f"Imported asset failed to load: {asset_path}")
            row: dict[str, object] = {"path": asset_path, "class": asset.get_class().get_name(), "name": asset.get_name()}
            if isinstance(asset, unreal.StaticMesh):
                bounds = asset.get_bounds()
                row["bounds_extent_cm"] = vec(bounds.box_extent)
                row["material_slot_count"] = len(list(asset.get_editor_property("static_materials")))
                if asset.get_name() == MESH_NAME:
                    render_mesh = asset
            result["imported_assets"].append(row)
        require(render_mesh is not None, "Accepted Igla render mesh was not imported")

        full = [value * 2.0 for value in vec(render_mesh.get_bounds().box_extent)]
        require(156.5 <= full[0] <= 158.3, f"Unreal length authority changed: {full}")
        require(17.0 <= full[1] <= 19.5 and 17.0 <= full[2] <= 19.5, f"Unreal fin envelope changed: {full}")
        require(len(list(render_mesh.get_editor_property("static_materials"))) == 4, "Igla material-slot count changed")
        require(render_mesh.get_editor_property("body_setup") is not None, "Igla BodySetup is missing")

        created_sockets = []
        for name, location in contract["socket_locations_cm"].items():
            socket = render_mesh.find_socket(name)
            if socket is None:
                socket = unreal.StaticMeshSocket(outer=render_mesh)
                socket.set_editor_property("socket_name", name)
                socket.set_editor_property("relative_location", unreal.Vector(*location))
                socket.set_editor_property("relative_rotation", unreal.Rotator(0.0, 0.0, 0.0))
                render_mesh.add_socket(socket)
                created_sockets.append(name)
            verified = render_mesh.find_socket(name)
            require(verified is not None, f"Recovery01 socket creation failed: {name}")
            actual = vec(verified.get_editor_property("relative_location"))
            require(max(abs(actual[index] - location[index]) for index in range(3)) <= 0.01, f"Recovery01 socket location changed: {name} {actual}")

        try:
            unreal.EditorAssetLibrary.save_loaded_asset(render_mesh, only_if_is_dirty=False)
            unreal.EditorAssetLibrary.save_directory(DESTINATION, only_if_is_dirty=False, recursive=True)
        except TypeError:
            unreal.EditorAssetLibrary.save_loaded_asset(render_mesh)
            unreal.EditorAssetLibrary.save_directory(DESTINATION)
        result["mesh"] = {
            "path": render_mesh.get_path_name(),
            "full_dimensions_cm": full,
            "material_slot_count": 4,
            "body_setup_present": True,
            "created_sockets": created_sockets,
            "verified_sockets": contract["socket_locations_cm"],
        }

        require(unreal.EditorLevelLibrary.new_level(MAP_ASSET), "Failed to create Recovery01 audit level")
        actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        require(actors is not None, "EditorActorSubsystem unavailable")
        poses = (
            ("Side_A", unreal.Vector(-190.0, 0.0, 125.0), unreal.Rotator(0.0, 0.0, 0.0)),
            ("Side_B", unreal.Vector(190.0, 0.0, 125.0), unreal.Rotator(0.0, 180.0, 0.0)),
            ("Oblique", unreal.Vector(0.0, 230.0, 150.0), unreal.Rotator(-18.0, 35.0, 0.0)),
        )
        for suffix, location, rotation in poses:
            actor = actors.spawn_actor_from_class(unreal.StaticMeshActor, location, rotation, False)
            require(actor is not None, f"Failed to spawn Recovery01 audit actor: {suffix}")
            actor.set_actor_label(f"AUDIT_CORE_IglaMissile_Recovery01_{suffix}")
            actor.set_folder_path("Audit/Combat/IglaMissileRefinement01Recovery01")
            component = actor.get_component_by_class(unreal.StaticMeshComponent)
            require(component is not None, "Audit actor StaticMeshComponent missing")
            component.set_static_mesh(render_mesh)
            component.set_mobility(unreal.ComponentMobility.STATIC)
            component.set_collision_profile_name("BlockAll")
            result["placements"].append({"label": actor.get_actor_label(), "location_cm": vec(actor.get_actor_location())})
        require(len(result["placements"]) == 3, "Recovery01 placement count changed")
        require(unreal.EditorLevelLibrary.save_current_level(), "Failed to save Recovery01 audit level")
        require(MAP_FILE.is_file(), "Recovery01 audit map was not created")

        for path, size, digest in (
            (SOURCE, SOURCE_BYTES, SOURCE_SHA),
            (ACCEPTANCE, ACCEPTANCE_BYTES, ACCEPTANCE_SHA),
            (FAILED_FREEZE, FAILED_FREEZE_BYTES, FAILED_FREEZE_SHA),
            (PROJECT, PROJECT_BYTES, PROJECT_SHA),
        ):
            require(path.stat().st_size == size and sha256(path) == digest, f"Authority changed during Recovery01: {path}")
        result["output_map"] = record(MAP_FILE)
        result["asset_inventory"] = inventory(DESTINATION_DISK)
        require(result["asset_inventory"], "Recovery01 destination inventory is empty")
        result["classification"] = "PASSED_CORE_IGLA_MISSILE_REFINEMENT01_UNREAL_STAGING_READY_FOR_D3D12_VISUAL_PROOF"
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        result["traceback"] = traceback.format_exc()
    finally:
        write_json_atomic(RECEIPT, result)

    if result["classification"].startswith("PASSED_"):
        unreal.SystemLibrary.quit_editor()
    else:
        raise RuntimeError(result["error"] or "Igla Recovery01 staging failed")


if "--offline-contract-test" in sys.argv:
    raise SystemExit(offline_contract_test())

run_unreal()
