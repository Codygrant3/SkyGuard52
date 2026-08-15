from __future__ import annotations

import hashlib
import json
import os
import traceback

import unreal


MAP_ASSET = "/Game/ToolchainWave08/Environment/Lvl_M01_T08_EnvironmentAuthoring01_Recovery07"
MAP_FILE = r"D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentAuthoring01_Recovery07.umap"
EXPECTED_MAP_BYTES = 625041
EXPECTED_MAP_SHA256 = "401fb7a86321c05f977347185e41fd0ea0436ef7ec3d06d635935ad5f4ce702f"
ATTEMPT_ROOT = r"D:\Skyguard52\Saved\BuildAttempts\M01_ENVIRONMENT_REALISM_STACK_PIVOT01_ASSET_PROBE\attempt_01"
RECEIPT_PATH = os.path.join(ATTEMPT_ROOT, "asset_map_probe_receipt.json")

REFINEMENT_ROOT = (
    "/Game/Skyguard/Meshes/Mission01/Wave1Refinement/"
    "m01_wave1_aaa_refinement/StaticMeshes/"
)

STATIC_MESH_ASSETS = (
    REFINEMENT_ROOT + "SM_M01_Coast_Beach_Detailed_A",
    REFINEMENT_ROOT + "SM_M01_Coast_Promenade_Detailed_A",
    REFINEMENT_ROOT + "SM_M01_Coast_Seawall_Detailed_A",
    REFINEMENT_ROOT + "SM_M01_Road_CoastalTransition_Detailed_A",
    REFINEMENT_ROOT + "SM_M01_Urban_Apartment_Detailed_A",
    REFINEMENT_ROOT + "SM_M01_Urban_Apartment_Detailed_B",
    REFINEMENT_ROOT + "SM_M01_Urban_Midrise_Detailed_A",
    REFINEMENT_ROOT + "SM_M01_Urban_Midrise_Damaged_A",
    REFINEMENT_ROOT + "SM_M01_Landmark_Lighthouse_Hero_A",
    REFINEMENT_ROOT + "SM_M01_Landmark_RadarPost_Hero_A",
)

MATERIAL_ASSETS = (
    "/Game/Skyguard/Materials/M_CityConcrete",
    "/Game/Skyguard/Materials/M_CityGlass",
    "/Game/Skyguard/Materials/M_Road",
    "/Game/Skyguard/Materials/M_Beach",
    "/Game/Skyguard/Materials/M_WetSand",
)


def sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json_atomic(path: str, payload: object) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    temporary = path + ".tmp"
    with open(temporary, "w", encoding="utf-8", newline="\n") as stream:
        json.dump(payload, stream, indent=2, sort_keys=True)
        stream.write("\n")
    os.replace(temporary, path)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def object_path(asset: object) -> str | None:
    if asset is None:
        return None
    try:
        return str(asset.get_path_name())
    except Exception:
        return None


def vector3(value: object) -> list[float]:
    return [float(value.x), float(value.y), float(value.z)]


def static_materials(mesh: object) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    try:
        values = list(mesh.get_editor_property("static_materials"))
    except Exception as exc:
        return [{"error": f"{type(exc).__name__}: {exc}"}]
    for index, value in enumerate(values):
        material = None
        slot_name = None
        imported_slot_name = None
        try:
            material = value.get_editor_property("material_interface")
        except Exception:
            pass
        try:
            slot_name = str(value.get_editor_property("material_slot_name"))
        except Exception:
            pass
        try:
            imported_slot_name = str(value.get_editor_property("imported_material_slot_name"))
        except Exception:
            pass
        records.append(
            {
                "index": index,
                "slot_name": slot_name,
                "imported_slot_name": imported_slot_name,
                "material": object_path(material),
            }
        )
    return records


def static_mesh_record(path: str) -> dict[str, object]:
    record: dict[str, object] = {
        "asset_path": path,
        "exists": False,
        "loaded": False,
        "class": None,
        "bounds_origin_cm": None,
        "bounds_extent_cm": None,
        "materials": [],
        "nanite_enabled": None,
        "lod_count": None,
        "errors": [],
        "passed": False,
    }
    try:
        record["exists"] = bool(unreal.EditorAssetLibrary.does_asset_exist(path))
        mesh = unreal.EditorAssetLibrary.load_asset(path)
        record["loaded"] = mesh is not None
        if mesh is None:
            raise RuntimeError("asset failed to load")
        record["class"] = str(mesh.get_class().get_name())
        bounds = mesh.get_bounds()
        record["bounds_origin_cm"] = vector3(bounds.origin)
        record["bounds_extent_cm"] = vector3(bounds.box_extent)
        record["materials"] = static_materials(mesh)
        try:
            nanite = mesh.get_editor_property("nanite_settings")
            record["nanite_enabled"] = bool(nanite.get_editor_property("enabled"))
        except Exception as exc:
            record["errors"].append(f"nanite_settings: {type(exc).__name__}: {exc}")
        try:
            record["lod_count"] = int(unreal.EditorStaticMeshLibrary.get_lod_count(mesh))
        except Exception as exc:
            record["errors"].append(f"lod_count: {type(exc).__name__}: {exc}")
        record["passed"] = bool(
            record["exists"]
            and record["loaded"]
            and record["class"] == "StaticMesh"
            and all(value > 0.0 for value in record["bounds_extent_cm"])
        )
    except Exception as exc:
        record["errors"].append(f"{type(exc).__name__}: {exc}")
    return record


def material_record(path: str) -> dict[str, object]:
    record: dict[str, object] = {
        "asset_path": path,
        "exists": False,
        "loaded": False,
        "class": None,
        "passed": False,
        "errors": [],
    }
    try:
        record["exists"] = bool(unreal.EditorAssetLibrary.does_asset_exist(path))
        material = unreal.EditorAssetLibrary.load_asset(path)
        record["loaded"] = material is not None
        if material is None:
            raise RuntimeError("asset failed to load")
        record["class"] = str(material.get_class().get_name())
        record["passed"] = bool(record["exists"] and record["loaded"])
    except Exception as exc:
        record["errors"].append(f"{type(exc).__name__}: {exc}")
    return record


def actor_snapshot(actor: object) -> dict[str, object]:
    location = actor.get_actor_location()
    rotation = actor.get_actor_rotation()
    scale = actor.get_actor_scale3d()
    record: dict[str, object] = {
        "label": actor.get_actor_label(),
        "class": actor.get_class().get_path_name(),
        "location_cm": vector3(location),
        "rotation_deg": [float(rotation.roll), float(rotation.pitch), float(rotation.yaw)],
        "scale": vector3(scale),
        "tags": sorted(str(tag) for tag in actor.tags),
        "bounds_origin_cm": None,
        "bounds_extent_cm": None,
        "static_mesh": None,
        "component_materials": [],
    }
    try:
        origin, extent = actor.get_actor_bounds(False)
        record["bounds_origin_cm"] = vector3(origin)
        record["bounds_extent_cm"] = vector3(extent)
    except Exception:
        pass
    try:
        component = actor.get_component_by_class(unreal.StaticMeshComponent)
        if component is not None:
            mesh = component.get_editor_property("static_mesh")
            record["static_mesh"] = object_path(mesh)
            material_count = int(component.get_num_materials())
            record["component_materials"] = [
                object_path(component.get_material(index)) for index in range(material_count)
            ]
    except Exception:
        pass
    return record


result: dict[str, object] = {
    "schema": "skyguard.m01-environment-realism-stack-pivot01.asset-map-probe.v1",
    "classification": "FAILED_WITH_EVIDENCE",
    "read_only": True,
    "world_saved": False,
    "map_asset": MAP_ASSET,
    "map_sha256_before": None,
    "map_sha256_after": None,
    "map_unchanged": False,
    "static_mesh_assets": [],
    "material_assets": [],
    "actor_inventory": [],
    "governed_actor_count": 0,
    "errors": [],
}

try:
    require(os.path.isfile(MAP_FILE), "Recovery07 map file is missing")
    require(os.path.getsize(MAP_FILE) == EXPECTED_MAP_BYTES, "Recovery07 map byte count mismatch")
    result["map_sha256_before"] = sha256(MAP_FILE)
    require(result["map_sha256_before"] == EXPECTED_MAP_SHA256, "Recovery07 map hash mismatch")

    level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    require(level_subsystem is not None, "LevelEditorSubsystem is unavailable")
    require(bool(level_subsystem.load_level(MAP_ASSET)), "Recovery07 map failed to load")

    actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    require(actor_subsystem is not None, "EditorActorSubsystem is unavailable")
    actors = list(actor_subsystem.get_all_level_actors())
    result["actor_inventory"] = sorted(
        (actor_snapshot(actor) for actor in actors), key=lambda row: str(row["label"])
    )
    result["governed_actor_count"] = sum(
        1 for row in result["actor_inventory"] if str(row["label"]).startswith("M01_A01_")
    )

    result["static_mesh_assets"] = [static_mesh_record(path) for path in STATIC_MESH_ASSETS]
    result["material_assets"] = [material_record(path) for path in MATERIAL_ASSETS]
    require(all(row["passed"] for row in result["static_mesh_assets"]), "A candidate static mesh failed validation")
    require(all(row["passed"] for row in result["material_assets"]), "A candidate material failed validation")
    require(result["governed_actor_count"] > 0, "Recovery07 map has no governed environment actors")

    result["map_sha256_after"] = sha256(MAP_FILE)
    result["map_unchanged"] = result["map_sha256_after"] == result["map_sha256_before"]
    require(result["map_unchanged"], "Read-only probe changed the Recovery07 map")
    result["classification"] = "PASSED_READY_FOR_ENVIRONMENT_REALISM_STACK_PIVOT01_AUTHORING_DESIGN"
except Exception as exc:
    result["errors"].append(f"{type(exc).__name__}: {exc}")
    result["errors"].append(traceback.format_exc())
finally:
    if result["map_sha256_after"] is None and os.path.isfile(MAP_FILE):
        result["map_sha256_after"] = sha256(MAP_FILE)
        result["map_unchanged"] = result["map_sha256_after"] == result["map_sha256_before"]
    write_json_atomic(RECEIPT_PATH, result)
    print("SKYGUARD_M01_REALISM_STACK_PIVOT01_PROBE=" + str(result["classification"]))

if result["classification"] != "PASSED_READY_FOR_ENVIRONMENT_REALISM_STACK_PIVOT01_AUTHORING_DESIGN":
    raise RuntimeError(str(result["errors"][0] if result["errors"] else "probe failed"))
