from __future__ import annotations

import hashlib
import json
import os
import re
import traceback
from collections import Counter

import unreal


MAP_ASSET = "/Game/M01/Lvl_M01_VisibleEnvironmentKit02_PresentationRefinement01_Recovery01"
MAP_FILE = r"D:\SG52T08_ENV01\Content\M01\Lvl_M01_VisibleEnvironmentKit02_PresentationRefinement01_Recovery01.umap"
EXPECTED_MAP_BYTES = 845823
EXPECTED_MAP_SHA256 = "7ff5370b03b090c1111395e7873da9d8333c1063d3492d30c4e6e7a7006a3430"
ATTEMPT_ROOT = r"D:\Skyguard52\Saved\BuildAttempts\M01_PHOTOREAL_FOUNDATION_WAVE01_NONVEGETATION01_PROBE\attempt_01"
RECEIPT_PATH = os.path.join(ATTEMPT_ROOT, "probe_receipt.json")

CANDIDATE_MATERIALS = (
    "/Game/Skyguard/Materials/M_CityGlass",
    "/Game/Skyguard/Materials/M_Road",
    "/Game/Skyguard/Materials/M_Beach",
    "/Game/Skyguard/Materials/M_WetSand",
    "/Game/Skyguard/Meshes/Mission01/Wave1Refinement/m01_wave1_aaa_refinement/Materials/M_M01_Window",
    "/Game/Skyguard/Meshes/Mission01/Wave1Refinement/m01_wave1_aaa_refinement/Materials/M_M01_Glass",
)

CITY_PATTERN = re.compile(
    r"^M01_VEK02_City_R(?P<row>\d{2})_C(?P<column>\d{2})_"
    r"(?P<family>ApartmentA|MidriseB|CornerC)_(?P<group>STRUCTURAL|GLAZING|DETAILS)$"
)
PROXY_TOKENS = ("TREE", "FOLIAGE", "SHRUB", "PLANT", "VEGETATION")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


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


def object_path(value: object) -> str | None:
    if value is None:
        return None
    try:
        return str(value.get_path_name())
    except Exception:
        return None


def vector3(value: object) -> list[float]:
    return [float(value.x), float(value.y), float(value.z)]


def actor_snapshot(actor: object) -> dict[str, object]:
    label = actor.get_actor_label()
    location = actor.get_actor_location()
    rotation = actor.get_actor_rotation()
    scale = actor.get_actor_scale3d()
    record: dict[str, object] = {
        "label": label,
        "class": actor.get_class().get_path_name(),
        "location_cm": vector3(location),
        "rotation_deg": [float(rotation.pitch), float(rotation.yaw), float(rotation.roll)],
        "scale": vector3(scale),
        "folder": str(actor.get_folder_path()),
        "static_mesh": None,
        "materials": [],
        "material_slot_names": [],
    }
    component = actor.get_component_by_class(unreal.StaticMeshComponent)
    if component is not None:
        mesh = component.get_editor_property("static_mesh")
        record["static_mesh"] = object_path(mesh)
        count = int(component.get_num_materials())
        record["materials"] = [object_path(component.get_material(index)) for index in range(count)]
        if mesh is not None:
            slots = list(mesh.get_editor_property("static_materials"))
            record["material_slot_names"] = [
                str(slot.get_editor_property("material_slot_name")) for slot in slots
            ]
    return record


def material_record(path: str) -> dict[str, object]:
    record: dict[str, object] = {
        "asset_path": path,
        "exists": False,
        "loaded": False,
        "class": None,
        "name": None,
    }
    record["exists"] = bool(unreal.EditorAssetLibrary.does_asset_exist(path))
    value = unreal.EditorAssetLibrary.load_asset(path)
    record["loaded"] = value is not None
    if value is not None:
        record["class"] = str(value.get_class().get_name())
        record["name"] = str(value.get_name())
    return record


result: dict[str, object] = {
    "schema": "skyguard.m01-photoreal-foundation.nonvegetation01.probe.v1",
    "classification": "FAILED_WITH_EVIDENCE",
    "read_only": True,
    "world_saved": False,
    "map_asset": MAP_ASSET,
    "map_sha256_before": None,
    "map_sha256_after": None,
    "map_unchanged": False,
    "actor_count": 0,
    "visible_kit_actors": [],
    "city_groups": [],
    "proxy_vegetation_actors": [],
    "district_actors": [],
    "lighthouse_actors": [],
    "material_usage": {},
    "candidate_materials": [],
    "quality_facts": {},
    "errors": [],
}

try:
    require(os.path.isfile(MAP_FILE), "Accepted presentation map is missing")
    require(os.path.getsize(MAP_FILE) == EXPECTED_MAP_BYTES, "Accepted presentation map byte count changed")
    result["map_sha256_before"] = sha256(MAP_FILE)
    require(result["map_sha256_before"] == EXPECTED_MAP_SHA256, "Accepted presentation map hash changed")

    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    actors_api = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    require(levels is not None and actors_api is not None, "Required editor subsystems are unavailable")
    require(bool(levels.load_level(MAP_ASSET)), "Accepted presentation map failed to load")
    actors = list(actors_api.get_all_level_actors())
    result["actor_count"] = len(actors)
    require(len(actors) == 180, f"Expected 180 actors; found {len(actors)}")

    snapshots = [actor_snapshot(actor) for actor in actors]
    visible = sorted(
        (row for row in snapshots if str(row["label"]).startswith("M01_VEK02_")),
        key=lambda row: str(row["label"]),
    )
    result["visible_kit_actors"] = visible
    require(len(visible) == 92, f"Expected 92 visible-kit actors; found {len(visible)}")

    city_groups: dict[str, dict[str, object]] = {}
    for row in visible:
        match = CITY_PATTERN.match(str(row["label"]))
        if not match:
            continue
        key = f"R{match.group('row')}_C{match.group('column')}"
        entry = city_groups.setdefault(
            key,
            {
                "key": key,
                "row": int(match.group("row")),
                "column": int(match.group("column")),
                "family": match.group("family"),
                "actors": [],
            },
        )
        entry["actors"].append(row)
    result["city_groups"] = sorted(city_groups.values(), key=lambda row: (row["row"], row["column"]))
    require(len(result["city_groups"]) == 27, f"Expected 27 city groups; found {len(result['city_groups'])}")
    require(all(len(row["actors"]) == 3 for row in result["city_groups"]), "A city group is not a complete triplet")

    result["district_actors"] = [row for row in visible if "_District_" in str(row["label"])]
    result["lighthouse_actors"] = [row for row in visible if "Lighthouse_Hero" in str(row["label"])]
    result["proxy_vegetation_actors"] = sorted(
        (
            row
            for row in snapshots
            if any(token in str(row["label"]).upper() for token in PROXY_TOKENS)
            or any(token in str(row["static_mesh"]).upper() for token in PROXY_TOKENS)
        ),
        key=lambda row: str(row["label"]),
    )

    material_usage: Counter[str] = Counter()
    for row in visible:
        for material in row["materials"]:
            material_usage[str(material)] += 1
    result["material_usage"] = dict(sorted(material_usage.items()))
    result["candidate_materials"] = [material_record(path) for path in CANDIDATE_MATERIALS]

    structural = [
        actor
        for group in result["city_groups"]
        for actor in group["actors"]
        if str(actor["label"]).endswith("_STRUCTURAL")
    ]
    exact_yaw_counts = Counter(round(float(row["rotation_deg"][1]), 3) for row in structural)
    exact_scale_counts = Counter(tuple(round(float(v), 3) for v in row["scale"]) for row in structural)
    result["quality_facts"] = {
        "city_group_count": len(result["city_groups"]),
        "structural_actor_count": len(structural),
        "distinct_structural_yaws": len(exact_yaw_counts),
        "structural_yaw_counts": {str(key): value for key, value in sorted(exact_yaw_counts.items())},
        "distinct_structural_scales": len(exact_scale_counts),
        "proxy_vegetation_count": len(result["proxy_vegetation_actors"]),
        "glass_dark_usage_count": sum(
            count for path, count in material_usage.items() if "M_ENV_Glass_Dark" in path
        ),
        "road_marking_usage_count": sum(
            count for path, count in material_usage.items() if "Road_Marking" in path
        ),
    }

    result["map_sha256_after"] = sha256(MAP_FILE)
    result["map_unchanged"] = result["map_sha256_after"] == result["map_sha256_before"]
    require(result["map_unchanged"], "Read-only probe changed the accepted map")
    result["classification"] = "PASSED_READY_FOR_M01_NONVEGETATION01_AUTHORING"
except Exception as exc:
    result["errors"].append(f"{type(exc).__name__}: {exc}")
    result["errors"].append(traceback.format_exc())
finally:
    if result["map_sha256_after"] is None and os.path.isfile(MAP_FILE):
        result["map_sha256_after"] = sha256(MAP_FILE)
        result["map_unchanged"] = result["map_sha256_after"] == result["map_sha256_before"]
    write_json_atomic(RECEIPT_PATH, result)
    print("SKYGUARD_M01_NONVEGETATION01_PROBE=" + str(result["classification"]))

if result["classification"] != "PASSED_READY_FOR_M01_NONVEGETATION01_AUTHORING":
    raise RuntimeError(str(result["errors"][0] if result["errors"] else "probe failed"))
