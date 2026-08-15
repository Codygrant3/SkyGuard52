"""Extend the accepted M01 realism landscape inland, re-ground it, and rebalance daylight."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
ISOLATED = Path(r"D:\SG52T08_ENV01")
INPUT_ASSET = "/Game/ToolchainWave08/Environment/Lvl_M01_T08_EnvironmentRealismStack01_Recovery02"
OUTPUT_ASSET = "/Game/ToolchainWave08/Environment/Lvl_M01_T08_EnvironmentRealismStack02"
INPUT_FILE = ISOLATED / "Content/ToolchainWave08/Environment/Lvl_M01_T08_EnvironmentRealismStack01_Recovery02.umap"
OUTPUT_FILE = ISOLATED / "Content/ToolchainWave08/Environment/Lvl_M01_T08_EnvironmentRealismStack02.umap"
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_ENVIRONMENT_REALISM_STACK_AUTHORING02/attempt_01"
RECEIPT = ATTEMPT / "authoring_receipt.json"
EXPECTED_INPUT_BYTES = 860203
EXPECTED_INPUT_SHA256 = "46a8ad9187c836329554d29716bd61ca4a2bc0f8bad7d64f66addc108e93e9d2"
TARGET_LANDSCAPE_SCALE = (100.0, 150.0, 100.0)
TARGET_SUN_ROTATION = (-35.0, 75.0, 0.0)
TARGET_SUN_INTENSITY = 10.0
TARGET_SKYLIGHT_INTENSITY = 2.0


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def prop(value, *names):
    for name in names:
        try:
            return value.get_editor_property(name)
        except Exception:
            if hasattr(value, name):
                return getattr(value, name)
    raise RuntimeError(f"Missing property {names} on {type(value).__name__}")


def vector(value):
    return [float(value.x), float(value.y), float(value.z)]


def rotator(value):
    return [float(value.pitch), float(value.yaw), float(value.roll)]


def find_exact(actors, label):
    matches = [actor for actor in actors if actor.get_actor_label() == label]
    require(len(matches) == 1, f"Expected exactly one {label}; found {len(matches)}")
    return matches[0]


def footprint_points(origin, extent, count):
    cx, cy = float(origin.x), float(origin.y)
    ex = max(1.0, float(extent.x) * 0.98)
    ey = max(1.0, float(extent.y) * 0.98)
    xy = [(cx, cy), (cx - ex, cy - ey), (cx + ex, cy - ey), (cx - ex, cy + ey), (cx + ex, cy + ey)]
    if count >= 9:
        xy += [(cx - ex, cy), (cx + ex, cy), (cx, cy - ey), (cx, cy + ey)]
    if count == 13:
        xy += [(cx - ex * 0.5, cy - ey), (cx + ex * 0.5, cy - ey), (cx - ex * 0.5, cy + ey), (cx + ex * 0.5, cy + ey)]
    require(len(xy) == count, f"Footprint sample count mismatch: {len(xy)} != {count}")
    return [unreal.Vector(x, y, 100000.0) for x, y in xy]


def sample_summary(sampled, label):
    return {
        "name": label,
        "success": bool(prop(sampled, "success", "b_success")),
        "required_sample_count": int(prop(sampled, "required_sample_count")),
        "valid_sample_count": int(prop(sampled, "valid_sample_count")),
        "supported_fraction": float(prop(sampled, "supported_fraction")),
        "minimum_height_cm": float(prop(sampled, "minimum_height_centimeters")),
        "maximum_height_cm": float(prop(sampled, "maximum_height_centimeters")),
        "mean_height_cm": float(prop(sampled, "mean_height_centimeters")),
        "height_delta_cm": float(prop(sampled, "height_delta_centimeters")),
        "error": str(prop(sampled, "error")),
    }


def align_bottom(actor, target_z):
    origin, extent = actor.get_actor_bounds(False)
    bottom_before = float(origin.z - extent.z)
    location = actor.get_actor_location()
    actor.set_actor_location(unreal.Vector(location.x, location.y, location.z + float(target_z) - bottom_before), False, False)
    after_origin, after_extent = actor.get_actor_bounds(False)
    bottom_after = float(after_origin.z - after_extent.z)
    gap = bottom_after - float(target_z)
    require(abs(gap) <= 1.0, f"Grounding gap exceeded for {actor.get_actor_label()}: {gap} cm")
    return {"bottom_before_cm": bottom_before, "bottom_after_cm": bottom_after, "target_ground_z_cm": float(target_z), "gap_cm": gap}


def ground_footprint(library, landscape, actor, count, maximum_delta, category):
    origin, extent = actor.get_actor_bounds(False)
    summary = sample_summary(library.sample_landscape_footprint(landscape, footprint_points(origin, extent, count)), actor.get_actor_label())
    require(summary["success"], f"Unsupported footprint for {actor.get_actor_label()}: {summary['error']}")
    require(summary["supported_fraction"] == 1.0, f"Incomplete footprint support for {actor.get_actor_label()}")
    require(summary["height_delta_cm"] <= maximum_delta, f"Terrain delta too large for {actor.get_actor_label()}: {summary['height_delta_cm']} cm")
    summary.update(align_bottom(actor, summary["mean_height_cm"]))
    summary.update({"category": category, "actor_bounds_origin_cm": vector(origin), "actor_bounds_extent_cm": vector(extent)})
    return summary


def ground_point(library, landscape, actor):
    location = actor.get_actor_location()
    sampled = library.sample_landscape_height(landscape, unreal.Vector(location.x, location.y, 100000.0))
    require(bool(prop(sampled, "valid", "b_valid")), f"Unsupported point for {actor.get_actor_label()}: {prop(sampled, 'error')}")
    target = float(prop(sampled, "height_centimeters"))
    row = {"name": actor.get_actor_label(), "success": True, "supported_fraction": 1.0, "height_delta_cm": 0.0, "category": "tree"}
    row.update(align_bottom(actor, target))
    return row


def category_for(label):
    if label.startswith("M01_RS01_Seawall_"):
        return "seawall", 13, 225.0
    if label.startswith("M01_RS01_Promenade_"):
        return "promenade", 13, 225.0
    if label.startswith("M01_RS01_CoastalRoad_") or label.startswith("M01_RS01_CrossStreet_"):
        return "road", 13, 225.0
    if label.startswith("M01_RS01_City_"):
        return "building", 9, 175.0
    if label in {"M01_RS01_Lighthouse_Hero", "M01_RS01_Radar_Hero"}:
        return "landmark", 9, 175.0
    return None


result = {
    "schema": "skyguard.m01-environment-realism-stack-authoring02.receipt.v1",
    "classification": "FAILED_WITH_EVIDENCE",
    "input_asset": INPUT_ASSET,
    "output_asset": OUTPUT_ASSET,
    "input_sha256_before": None,
    "input_sha256_after": None,
    "output_sha256": None,
    "actor_count": 0,
    "landscape_scale_before": None,
    "landscape_scale_after": None,
    "regrounding_records": [],
    "waterline_records": [],
    "lighting_before": {},
    "lighting_after": {},
    "saved_assets": [],
    "error": None,
}

try:
    require(INPUT_FILE.is_file() and INPUT_FILE.stat().st_size == EXPECTED_INPUT_BYTES and sha256(INPUT_FILE) == EXPECTED_INPUT_SHA256, "Accepted RealismStack01 map authority changed")
    require(not OUTPUT_FILE.exists() and not unreal.EditorAssetLibrary.does_asset_exist(OUTPUT_ASSET), "Authoring02 output namespace exists")
    result["input_sha256_before"] = sha256(INPUT_FILE)
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    actors_api = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    require(levels is not None and actors_api is not None, "Editor subsystems are unavailable")
    require(levels.new_level_from_template(OUTPUT_ASSET, INPUT_ASSET), "Failed to clone RealismStack01")
    actors = list(actors_api.get_all_level_actors())
    result["actor_count"] = len(actors)
    require(len(actors) == 186, f"Expected 186 governed actors; found {len(actors)}")

    landscape = find_exact(actors, "M01_A01_Landscape_Production")
    ocean = find_exact(actors, "M01_A01_WaterBodyOcean")
    sun = find_exact(actors, "M01_RS01_Sun")
    sky = find_exact(actors, "M01_RS01_SkyLight")
    old_scale = landscape.get_actor_scale3d()
    result["landscape_scale_before"] = vector(old_scale)
    landscape.set_actor_scale3d(unreal.Vector(*TARGET_LANDSCAPE_SCALE))
    result["landscape_scale_after"] = vector(landscape.get_actor_scale3d())
    require(all(abs(a - b) <= 0.001 for a, b in zip(result["landscape_scale_after"], TARGET_LANDSCAPE_SCALE)), "Landscape scale did not update")

    library = unreal.SkyguardMission01LandscapeGroundingLibrary
    require(library is not None, "Landscape grounding library is unavailable")
    ocean_z = float(ocean.get_actor_location().z)
    for actor in actors:
        label = actor.get_actor_label()
        if label.startswith("M01_RS01_Beach_"):
            origin, extent = actor.get_actor_bounds(False)
            result["waterline_records"].append({"name": label, "bottom_cm": float(origin.z - extent.z), "target_cm": ocean_z + 65.0, "gap_cm": float(origin.z - extent.z) - (ocean_z + 65.0)})
        elif label.startswith("M01_RS01_Tree_"):
            result["regrounding_records"].append(ground_point(library, landscape, actor))
        else:
            category = category_for(label)
            if category:
                result["regrounding_records"].append(ground_footprint(library, landscape, actor, category[1], category[2], category[0]))

    require(len(result["regrounding_records"]) == 165, f"Expected 165 re-grounded actors; found {len(result['regrounding_records'])}")
    require(len(result["waterline_records"]) == 10, "Expected ten governed waterline records")
    require(max(abs(row["gap_cm"]) for row in result["waterline_records"]) <= 1.0, "Beach waterline authority changed")

    sun_component = sun.get_component_by_class(unreal.DirectionalLightComponent)
    sky_component = sky.get_component_by_class(unreal.SkyLightComponent)
    require(sun_component is not None and sky_component is not None, "Lighting components are missing")
    result["lighting_before"] = {"sun_rotation": rotator(sun.get_actor_rotation()), "sun_intensity": float(sun_component.get_editor_property("intensity")), "skylight_intensity": float(sky_component.get_editor_property("intensity"))}
    sun.set_actor_rotation(unreal.Rotator(*TARGET_SUN_ROTATION), False)
    sun_component.set_editor_property("intensity", TARGET_SUN_INTENSITY)
    sky_component.set_editor_property("intensity", TARGET_SKYLIGHT_INTENSITY)
    result["lighting_after"] = {"sun_rotation": rotator(sun.get_actor_rotation()), "sun_intensity": float(sun_component.get_editor_property("intensity")), "skylight_intensity": float(sky_component.get_editor_property("intensity"))}

    require(levels.save_current_level(), "Failed to save Authoring02 map")
    require(OUTPUT_FILE.is_file(), "Authoring02 map file was not created")
    result["saved_assets"] = [OUTPUT_ASSET]
    result["output_sha256"] = sha256(OUTPUT_FILE)
    result["input_sha256_after"] = sha256(INPUT_FILE)
    require(result["input_sha256_after"] == EXPECTED_INPUT_SHA256, "Accepted input map changed")
    result["classification"] = "PASSED_M01_ENVIRONMENT_REALISM_STACK_AUTHORING02_AUTOMATIC"
except Exception as exc:
    result["error"] = f"{type(exc).__name__}: {exc}"
finally:
    write_json(RECEIPT, result)

if result["classification"].startswith("PASSED_"):
    unreal.SystemLibrary.quit_editor()
else:
    raise RuntimeError(result["error"] or "Authoring02 failed")
