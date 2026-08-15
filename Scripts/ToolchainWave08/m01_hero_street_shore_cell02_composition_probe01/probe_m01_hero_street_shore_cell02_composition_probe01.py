"""Read-only composition probe for Mission 1 Hero Street/Shore Cell02.

The probe measures the accepted Cell01 map and the accepted textured coastal
district/building assets.  It does not save a level or mutate an asset.
"""

from __future__ import annotations

import hashlib
import json
import os
import traceback
from pathlib import Path

import unreal


MAP_ASSET = "/Game/M01/Lvl_M01_HeroStreetShoreCell01_Recovery01"
MAP_FILE = Path(r"D:\SG52T08_ENV01\Content\M01\Lvl_M01_HeroStreetShoreCell01_Recovery01.umap")
MAP_BYTES = 746_684
MAP_SHA256 = "449c4d1153da7a149375f8b288c0908401ffe1db21104f83088039ed9b3656f2"
ATTEMPT = Path(
    r"D:\Skyguard52\Saved\BuildAttempts\M01_HERO_STREET_SHORE_CELL02_COMPOSITION_PROBE01\attempt_01"
)
RECEIPT = ATTEMPT / "composition_probe_receipt.json"

ASSETS = (
    "/Game/M01/EnvKit02/M01_COASTAL_DISTRICT_A/StaticMeshes/SM_M01_CoastalA_HARDSCAPE",
    "/Game/M01/EnvKit02/M01_COASTAL_DISTRICT_A/StaticMeshes/SM_M01_CoastalA_TERRAIN",
    "/Game/M01/EnvKit02/M01_APARTMENT_A/StaticMeshes/SM_M01_ApartmentA_STRUCTURAL",
    "/Game/M01/EnvKit02/M01_APARTMENT_A/StaticMeshes/SM_M01_ApartmentA_GLAZING",
    "/Game/M01/EnvKit02/M01_APARTMENT_A/StaticMeshes/SM_M01_ApartmentA_DETAILS",
    "/Game/M01/EnvKit02/M01_MIDRISE_B/StaticMeshes/SM_M01_MidriseB_STRUCTURAL",
    "/Game/M01/EnvKit02/M01_MIDRISE_B/StaticMeshes/SM_M01_MidriseB_GLAZING",
    "/Game/M01/EnvKit02/M01_MIDRISE_B/StaticMeshes/SM_M01_MidriseB_DETAILS",
    "/Game/M01/EnvKit02/M01_CORNER_RESIDENCE_C/StaticMeshes/SM_M01_CornerC_STRUCTURAL",
    "/Game/M01/EnvKit02/M01_CORNER_RESIDENCE_C/StaticMeshes/SM_M01_CornerC_GLAZING",
    "/Game/M01/EnvKit02/M01_CORNER_RESIDENCE_C/StaticMeshes/SM_M01_CornerC_DETAILS",
    "/Game/T08/GW02/StaticMeshes/SM_M01_PrewarWindowBay_A01_FrameFacadeHardware",
    "/Game/T08/GW02/StaticMeshes/SM_M01_PrewarWindowBay_A01_Glass",
    "/Game/T08/GW02/StaticMeshes/SM_M01_PrewarWindowBay_A01_Interior",
)

CANDIDATE_TRANSFORM = {
    "location_cm": [5500.0, 13500.0, -29.0],
    "rotation_deg": [0.0, 0.0, 0.0],
    "scale": [1.0, 1.0, 1.0],
    "rationale": (
        "At yaw zero the 140 m district spans X=5500..19500; terrain spans "
        "Y=10000..13500 and hardscape spans Y=7805..9935.  Z=-29 aligns "
        "the hardscape minimum with the accepted promenade datum near Z=71."
    ),
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


def write_json_atomic(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(payload, stream, indent=2, sort_keys=True)
        stream.write("\n")
    os.replace(temporary, path)


def object_path(value: object) -> str | None:
    if value is None:
        return None
    try:
        return str(value.get_path_name())
    except Exception:
        return None


def vector3(value: object) -> list[float]:
    return [float(value.x), float(value.y), float(value.z)]


def mesh_materials(mesh: object) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    for index, slot in enumerate(list(mesh.get_editor_property("static_materials"))):
        material = slot.get_editor_property("material_interface")
        result.append(
            {
                "index": index,
                "slot_name": str(slot.get_editor_property("material_slot_name")),
                "material": object_path(material),
            }
        )
    return result


def asset_record(asset_path: str) -> dict[str, object]:
    mesh = unreal.EditorAssetLibrary.load_asset(asset_path)
    require(mesh is not None, f"Asset failed to load: {asset_path}")
    require(mesh.get_class().get_name() == "StaticMesh", f"Not a StaticMesh: {asset_path}")
    bounds = mesh.get_bounds()
    return {
        "asset_path": asset_path,
        "class": str(mesh.get_class().get_name()),
        "bounds_origin_cm": vector3(bounds.origin),
        "bounds_extent_cm": vector3(bounds.box_extent),
        "material_slots": mesh_materials(mesh),
        "lod_count": int(unreal.EditorStaticMeshLibrary.get_lod_count(mesh)),
    }


def actor_record(actor: object) -> dict[str, object]:
    location = actor.get_actor_location()
    rotation = actor.get_actor_rotation()
    scale = actor.get_actor_scale3d()
    record: dict[str, object] = {
        "label": actor.get_actor_label(),
        "class": actor.get_class().get_path_name(),
        "location_cm": vector3(location),
        "rotation_deg": [float(rotation.roll), float(rotation.pitch), float(rotation.yaw)],
        "scale": vector3(scale),
        "bounds_origin_cm": None,
        "bounds_extent_cm": None,
        "static_mesh": None,
        "materials": [],
    }
    try:
        origin, extent = actor.get_actor_bounds(False)
        record["bounds_origin_cm"] = vector3(origin)
        record["bounds_extent_cm"] = vector3(extent)
    except Exception:
        pass
    component = actor.get_component_by_class(unreal.StaticMeshComponent)
    if component is not None:
        record["static_mesh"] = object_path(component.get_editor_property("static_mesh"))
        record["materials"] = [
            object_path(component.get_material(index))
            for index in range(int(component.get_num_materials()))
        ]
    return record


def world_bounds(asset: dict[str, object], location: list[float]) -> dict[str, list[float]]:
    origin = [
        float(asset["bounds_origin_cm"][index]) + location[index] for index in range(3)
    ]
    extent = [float(value) for value in asset["bounds_extent_cm"]]
    return {
        "origin_cm": origin,
        "extent_cm": extent,
        "minimum_cm": [origin[index] - extent[index] for index in range(3)],
        "maximum_cm": [origin[index] + extent[index] for index in range(3)],
    }


def intersects(left: dict[str, object], right: dict[str, list[float]]) -> bool:
    if left["bounds_origin_cm"] is None or left["bounds_extent_cm"] is None:
        return False
    left_min = [
        float(left["bounds_origin_cm"][index]) - float(left["bounds_extent_cm"][index])
        for index in range(3)
    ]
    left_max = [
        float(left["bounds_origin_cm"][index]) + float(left["bounds_extent_cm"][index])
        for index in range(3)
    ]
    return all(
        left_max[index] >= right["minimum_cm"][index]
        and left_min[index] <= right["maximum_cm"][index]
        for index in range(3)
    )


result: dict[str, object] = {
    "schema": "skyguard.m01-hero-street-shore-cell02.composition-probe01.v1",
    "classification": "FAILED_WITH_EVIDENCE",
    "read_only": True,
    "world_saved": False,
    "map_asset": MAP_ASSET,
    "map_sha256_before": None,
    "map_sha256_after": None,
    "map_unchanged": False,
    "asset_records": [],
    "actor_count": 0,
    "actors": [],
    "candidate_transform": CANDIDATE_TRANSFORM,
    "candidate_world_bounds": {},
    "candidate_intersections": [],
    "required_removals_or_replacements": [],
    "errors": [],
}

try:
    require(MAP_FILE.is_file(), "Accepted Cell01 map is missing")
    require(MAP_FILE.stat().st_size == MAP_BYTES, "Accepted Cell01 map byte count changed")
    result["map_sha256_before"] = sha256(MAP_FILE)
    require(result["map_sha256_before"] == MAP_SHA256, "Accepted Cell01 map hash changed")

    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    actors_api = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    require(levels is not None and actors_api is not None, "Required editor subsystems unavailable")
    require(bool(levels.load_level(MAP_ASSET)), "Accepted Cell01 map failed to load")

    actors = [actor_record(actor) for actor in actors_api.get_all_level_actors()]
    result["actor_count"] = len(actors)
    result["actors"] = sorted(actors, key=lambda row: str(row["label"]))
    require(len(actors) == 121, f"Expected 121 Cell01 actors; found {len(actors)}")

    assets = [asset_record(path) for path in ASSETS]
    result["asset_records"] = assets
    by_name = {str(row["asset_path"]).rsplit("/", 1)[-1]: row for row in assets}
    hardscape = by_name["SM_M01_CoastalA_HARDSCAPE"]
    terrain = by_name["SM_M01_CoastalA_TERRAIN"]
    placement = list(CANDIDATE_TRANSFORM["location_cm"])
    hardscape_world = world_bounds(hardscape, placement)
    terrain_world = world_bounds(terrain, placement)
    result["candidate_world_bounds"] = {
        "hardscape": hardscape_world,
        "terrain": terrain_world,
    }

    combined = {
        "minimum_cm": [
            min(hardscape_world["minimum_cm"][index], terrain_world["minimum_cm"][index])
            for index in range(3)
        ],
        "maximum_cm": [
            max(hardscape_world["maximum_cm"][index], terrain_world["maximum_cm"][index])
            for index in range(3)
        ],
    }
    result["candidate_intersections"] = [
        row
        for row in result["actors"]
        if intersects(row, combined)
        and (
            row["static_mesh"] is not None
            or "Landscape" in str(row["class"])
            or "WaterBody" in str(row["class"])
        )
    ]
    result["required_removals_or_replacements"] = [
        {
            "label": row["label"],
            "reason": "Candidate Coastal District overlaps this bounded Cell01 actor; Cell02 authoring must explicitly retain, reposition, or remove it in the derived map.",
        }
        for row in result["candidate_intersections"]
    ]

    result["map_sha256_after"] = sha256(MAP_FILE)
    result["map_unchanged"] = result["map_sha256_after"] == result["map_sha256_before"]
    require(result["map_unchanged"], "Read-only composition probe changed Cell01 map")
    result["classification"] = "PASSED_M01_HERO_STREET_SHORE_CELL02_COMPOSITION_PROBE_READY_FOR_AUTHORING_DESIGN"
except Exception as exc:
    result["errors"].append(f"{type(exc).__name__}: {exc}")
    result["errors"].append(traceback.format_exc())
finally:
    if result["map_sha256_after"] is None and MAP_FILE.is_file():
        result["map_sha256_after"] = sha256(MAP_FILE)
        result["map_unchanged"] = result["map_sha256_after"] == result["map_sha256_before"]
    write_json_atomic(RECEIPT, result)
    print("SKYGUARD_M01_CELL02_COMPOSITION_PROBE=" + str(result["classification"]))

if result["classification"] != "PASSED_M01_HERO_STREET_SHORE_CELL02_COMPOSITION_PROBE_READY_FOR_AUTHORING_DESIGN":
    raise RuntimeError(str(result["errors"][0] if result["errors"] else "composition probe failed"))
