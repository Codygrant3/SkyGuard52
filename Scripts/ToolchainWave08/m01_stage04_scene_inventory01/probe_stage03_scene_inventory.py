"""Read-only UE 5.8 scene inventory for Mission 1 Stage04 placement planning.

The script loads the immutable Stage03 map, records every actor's transform and
bounds plus static-mesh identity, and never saves a world or asset.
"""

from __future__ import annotations

import hashlib
import json
import os
import traceback
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
PROJECT = Path(r"D:\SG52T08_ENV01")
MAP_ASSET = "/Game/M01/Lvl_M01_VisibleEnvironmentStage03"
MAP_FILE = PROJECT / "Content/M01/Lvl_M01_VisibleEnvironmentStage03.umap"
EXPECTED_MAP_BYTES = 911233
EXPECTED_MAP_SHA256 = "28c3462ffe39b6fe753e2ba96761aa0e54d3aa947b41c1c9be4c760202980cad"
EXPECTED_ACTOR_COUNT = 195
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_STAGE04_SCENE_INVENTORY01/attempt_01"
RECEIPT = ATTEMPT / "scene_inventory.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json_atomic(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def object_path(value: object) -> str | None:
    if value is None:
        return None
    try:
        return str(value.get_path_name())
    except Exception:
        return str(value)


def vector(value: object) -> list[float]:
    return [float(value.x), float(value.y), float(value.z)]


def bounds(actor: object) -> dict[str, list[float]]:
    origin, extent = actor.get_actor_bounds(False)
    return {
        "origin_cm": vector(origin),
        "extent_cm": vector(extent),
        "minimum_cm": [float(origin.x - extent.x), float(origin.y - extent.y), float(origin.z - extent.z)],
        "maximum_cm": [float(origin.x + extent.x), float(origin.y + extent.y), float(origin.z + extent.z)],
    }


def folder_path(actor: object) -> str:
    try:
        return str(actor.get_folder_path())
    except Exception:
        return ""


def actor_record(actor: object) -> dict[str, object]:
    rotation = actor.get_actor_rotation()
    row: dict[str, object] = {
        "label": actor.get_actor_label(),
        "class": actor.get_class().get_path_name(),
        "folder": folder_path(actor),
        "location_cm": vector(actor.get_actor_location()),
        "rotation_degrees": {
            "pitch": float(rotation.pitch),
            "yaw": float(rotation.yaw),
            "roll": float(rotation.roll),
        },
        "scale": vector(actor.get_actor_scale3d()),
        "bounds": bounds(actor),
    }
    try:
        row["hidden_in_editor"] = bool(actor.is_hidden_ed())
    except Exception:
        row["hidden_in_editor"] = None
    component = actor.get_component_by_class(unreal.StaticMeshComponent)
    if component is not None:
        mesh = component.get_editor_property("static_mesh")
        row["static_mesh"] = object_path(mesh)
        row["material_slots"] = [object_path(component.get_material(index)) for index in range(component.get_num_materials())]
    return row


def role(record: dict[str, object]) -> str:
    label = str(record["label"])
    mesh = str(record.get("static_mesh") or "")
    folded = (label + " " + mesh).lower()
    if "lighthouse" in folded:
        return "lighthouse"
    if "vegetation" in folded or label.startswith("M01_PHV02_") or any(token in folded for token in ("fir_", "pine_", "shrub", "grass")):
        return "vegetation"
    if any(token in folded for token in ("bicycle", "bollard", "litter", "stormdrain", "storm_drain", "utilitycabinet", "utility_cabinet")):
        return "promenade_prop"
    if any(token in folded for token in ("apartment", "midrise", "corner", "building", "facade")):
        return "architecture"
    if any(token in folded for token in ("terrain", "hardscape", "road", "sidewalk", "promenade", "beach")):
        return "surface_or_route"
    if any(token in folded for token in ("water", "ocean", "shore")):
        return "water_or_shore"
    if any(token in folded for token in ("light", "sky", "fog", "postprocess")):
        return "lighting_atmosphere"
    return "other"


result: dict[str, object] = {
    "schema": "skyguard.m01-stage04.scene-inventory01.v1",
    "classification": "FAILED_WITH_EVIDENCE",
    "read_only": True,
    "world_saved": False,
    "map_asset": MAP_ASSET,
    "map_sha256_before": None,
    "map_sha256_after": None,
    "map_unchanged": False,
    "actor_count": 0,
    "role_counts": {},
    "actors": [],
    "errors": [],
}

try:
    require(MAP_FILE.is_file(), "Stage03 map is missing")
    require(MAP_FILE.stat().st_size == EXPECTED_MAP_BYTES, "Stage03 map byte count changed")
    result["map_sha256_before"] = sha256(MAP_FILE)
    require(result["map_sha256_before"] == EXPECTED_MAP_SHA256, "Stage03 map hash changed")

    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    actors_api = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    require(levels is not None and actors_api is not None, "Required editor subsystems unavailable")
    require(bool(levels.load_level(MAP_ASSET)), "Stage03 map failed to load")

    rows = [actor_record(actor) for actor in actors_api.get_all_level_actors()]
    rows.sort(key=lambda item: str(item["label"]))
    for row in rows:
        row["stage04_role"] = role(row)
    result["actors"] = rows
    result["actor_count"] = len(rows)
    require(len(rows) == EXPECTED_ACTOR_COUNT, f"Stage03 actor count changed: {len(rows)}")

    counts: dict[str, int] = {}
    for row in rows:
        key = str(row["stage04_role"])
        counts[key] = counts.get(key, 0) + 1
    result["role_counts"] = counts
    require(counts.get("architecture", 0) > 0, "Architecture inventory is empty")
    require(counts.get("lighthouse", 0) == 3, "Expected three legacy lighthouse group actors")
    require(counts.get("vegetation", 0) == 28, "Expected twenty-eight vegetation actors")

    result["map_sha256_after"] = sha256(MAP_FILE)
    result["map_unchanged"] = result["map_sha256_after"] == result["map_sha256_before"]
    require(bool(result["map_unchanged"]), "Read-only scene inventory changed Stage03 map")
    result["classification"] = "PASSED_STAGE04_SCENE_INVENTORY_READY_FOR_FRESH_AUTHORING"
except Exception as exc:
    result["errors"].append({"type": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()})
finally:
    if result["map_sha256_after"] is None and MAP_FILE.is_file():
        result["map_sha256_after"] = sha256(MAP_FILE)
        result["map_unchanged"] = result["map_sha256_after"] == result["map_sha256_before"]
    write_json_atomic(RECEIPT, result)

print("SKYGUARD_M01_STAGE04_SCENE_INVENTORY=" + str(result["classification"]))
if result["classification"] != "PASSED_STAGE04_SCENE_INVENTORY_READY_FOR_FRESH_AUTHORING":
    raise RuntimeError(str(result["errors"][-1]["message"]) if result["errors"] else "Stage04 scene inventory failed")
