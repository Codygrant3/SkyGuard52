from __future__ import annotations

import hashlib
import json
import os
import re
import traceback
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
ISOLATED = Path(r"D:\SG52T08_ENV01")
INPUT_ASSET = "/Game/M01/Lvl_M01_PhotorealFoundation_NonVegetation01"
OUTPUT_ASSET = "/Game/M01/Lvl_M01_PhotorealFoundation_LightingRoadsWaterline02"
INPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_PhotorealFoundation_NonVegetation01.umap"
OUTPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_PhotorealFoundation_LightingRoadsWaterline02.umap"
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_PHOTOREAL_FOUNDATION_WAVE01_LIGHTING_ROADS_WATERLINE02_AUTHORING/attempt_01"
RECEIPT = ATTEMPT / "authoring_receipt.json"

EXPECTED_INPUT_BYTES = 736476
EXPECTED_INPUT_SHA256 = "618a260a905680cf5b17c1ac82a114a69f93f947334f45701cd1a8daa2b1f2a1"
EXPECTED_ACTOR_COUNT = 120

CROSS_STREET_PATTERN = re.compile(r"^M01_RS01_CrossStreet_\d{2}_\d{2}$")
CROSS_STREET_COUNT = 15
CONCRETE_LIGHT = (
    "/Game/Skyguard/Meshes/Mission01/Wave1Refinement/"
    "m01_wave1_aaa_refinement/Materials/M_M01_ConcreteLight.M_M01_ConcreteLight"
)
CONCRETE_DARK_ASSET = (
    "/Game/Skyguard/Meshes/Mission01/Wave1Refinement/"
    "m01_wave1_aaa_refinement/Materials/M_M01_ConcreteDark"
)
SAND_ASSET = "/Game/M01/EnvKit02/M01_COASTAL_DISTRICT_A/Materials/M_ENV_Sand_Coast_2K"

TARGET_FILL_INTENSITY = 4.25
TARGET_SKYLIGHT_INTENSITY = 4.75
TARGET_EXPOSURE_BIAS = 0.85
TARGET_FILM_TOE = 0.42
TARGET_OCEAN_Z_CM = -80.0
TARGET_FAR_WATER_EXTENT_CM = 4_000_000.0


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


def vector(value: object) -> list[float]:
    return [float(value.x), float(value.y), float(value.z)]


def vector2(value: object) -> list[float]:
    return [float(value.x), float(value.y)]


def actor_transform(actor: object) -> dict[str, list[float]]:
    rotation = actor.get_actor_rotation()
    return {
        "location_cm": vector(actor.get_actor_location()),
        "rotation_degrees": [float(rotation.pitch), float(rotation.yaw), float(rotation.roll)],
        "scale": vector(actor.get_actor_scale3d()),
    }


def find_exact(actors: list[object], label: str):
    matches = [actor for actor in actors if actor.get_actor_label() == label]
    require(len(matches) == 1, f"Expected exactly one {label}; found {len(matches)}")
    return matches[0]


def static_mesh_component(actor: object):
    component = actor.get_component_by_class(unreal.StaticMeshComponent)
    require(component is not None, f"StaticMeshComponent missing: {actor.get_actor_label()}")
    require(component.get_editor_property("static_mesh") is not None, f"Static mesh missing: {actor.get_actor_label()}")
    return component


def material_path(component: object, slot: int) -> str:
    material = component.get_material(slot)
    require(material is not None, f"Material slot {slot} is empty")
    return str(material.get_path_name())


result: dict[str, object] = {
    "schema": "skyguard.m01-photoreal-foundation.lighting-roads-waterline02.authoring.v1",
    "classification": "FAILED_WITH_EVIDENCE",
    "input_asset": INPUT_ASSET,
    "output_asset": OUTPUT_ASSET,
    "input_sha256_before": None,
    "input_sha256_after": None,
    "output_sha256": None,
    "actor_count_before": None,
    "actor_count_after": None,
    "cross_street_overrides": [],
    "lighting": {},
    "post_process": {},
    "water": {},
    "terrain_materials": [],
    "quality_metrics": {},
    "errors": [],
}

try:
    require(INPUT_FILE.is_file(), "Accepted NonVegetation01 map is missing")
    require(INPUT_FILE.stat().st_size == EXPECTED_INPUT_BYTES, "Accepted input map byte count changed")
    result["input_sha256_before"] = sha256(INPUT_FILE)
    require(result["input_sha256_before"] == EXPECTED_INPUT_SHA256, "Accepted input map hash changed")
    require(not OUTPUT_FILE.exists(), f"Fresh output file exists: {OUTPUT_FILE}")
    require(not unreal.EditorAssetLibrary.does_asset_exist(OUTPUT_ASSET), f"Fresh output asset exists: {OUTPUT_ASSET}")

    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    actors_api = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    require(levels is not None and actors_api is not None, "Required editor subsystems unavailable")
    require(levels.new_level_from_template(OUTPUT_ASSET, INPUT_ASSET), "Failed to clone NonVegetation01")

    actors = list(actors_api.get_all_level_actors())
    result["actor_count_before"] = len(actors)
    require(len(actors) == EXPECTED_ACTOR_COUNT, f"Expected {EXPECTED_ACTOR_COUNT} actors; found {len(actors)}")

    concrete_dark = unreal.load_asset(CONCRETE_DARK_ASSET)
    sand = unreal.load_asset(SAND_ASSET)
    require(concrete_dark is not None and sand is not None, "Required local PBR materials failed to load")

    cross_streets = sorted(
        (actor for actor in actors if CROSS_STREET_PATTERN.match(actor.get_actor_label())),
        key=lambda actor: actor.get_actor_label(),
    )
    require(len(cross_streets) == CROSS_STREET_COUNT, f"Expected {CROSS_STREET_COUNT} CrossStreet actors")
    for actor in cross_streets:
        before_transform = actor_transform(actor)
        component = static_mesh_component(actor)
        require(component.get_num_materials() == 3, f"Unexpected CrossStreet slot count: {actor.get_actor_label()}")
        before = material_path(component, 1)
        require(before == CONCRETE_LIGHT, f"Unexpected CrossStreet slot-1 material: {actor.get_actor_label()} -> {before}")
        component.set_material(1, concrete_dark)
        after = material_path(component, 1)
        require(after == concrete_dark.get_path_name(), f"CrossStreet material override failed: {actor.get_actor_label()}")
        require(actor_transform(actor) == before_transform, f"CrossStreet transform drift: {actor.get_actor_label()}")
        result["cross_street_overrides"].append({"label": actor.get_actor_label(), "slot": 1, "before": before, "after": after})

    terrain_actors = sorted(
        (actor for actor in actors if re.match(r"^M01_VEK02_District_\d{2}_TERRAIN$", actor.get_actor_label())),
        key=lambda actor: actor.get_actor_label(),
    )
    require(len(terrain_actors) == 4, "Expected four district terrain actors")
    for actor in terrain_actors:
        component = static_mesh_component(actor)
        require(component.get_num_materials() == 1, f"Unexpected terrain slot count: {actor.get_actor_label()}")
        before = material_path(component, 0)
        component.set_material(0, sand)
        after = material_path(component, 0)
        require(after == sand.get_path_name(), f"Sand material binding failed: {actor.get_actor_label()}")
        result["terrain_materials"].append({"label": actor.get_actor_label(), "before": before, "after": after})

    fill = find_exact(actors, "M01_PR01_FillSun")
    fill_component = fill.get_component_by_class(unreal.DirectionalLightComponent)
    require(fill_component is not None, "Fill DirectionalLightComponent missing")
    fill_before = float(fill_component.get_editor_property("intensity"))
    require(abs(fill_before - 2.75) <= 0.001, f"Fill intensity authority changed: {fill_before}")
    fill_component.set_editor_property("intensity", TARGET_FILL_INTENSITY)
    fill_component.set_editor_property("cast_shadows", False)

    sun = find_exact(actors, "M01_RS01_Sun")
    sun_component = sun.get_component_by_class(unreal.DirectionalLightComponent)
    require(sun_component is not None, "Sun DirectionalLightComponent missing")
    sun_intensity = float(sun_component.get_editor_property("intensity"))
    require(abs(sun_intensity - 10.0) <= 0.001, f"Sun intensity authority changed: {sun_intensity}")

    sky = find_exact(actors, "M01_RS01_SkyLight")
    sky_component = sky.get_component_by_class(unreal.SkyLightComponent)
    require(sky_component is not None, "SkyLightComponent missing")
    sky_before = float(sky_component.get_editor_property("intensity"))
    require(abs(sky_before - 3.25) <= 0.001, f"Skylight intensity authority changed: {sky_before}")
    sky_component.set_editor_property("intensity", TARGET_SKYLIGHT_INTENSITY)
    sky_component.set_editor_property("real_time_capture", True)
    sky_component.set_editor_property("lower_hemisphere_is_black", False)
    result["lighting"] = {
        "fill_before": fill_before,
        "fill_after": float(fill_component.get_editor_property("intensity")),
        "fill_cast_shadows": bool(fill_component.get_editor_property("cast_shadows")),
        "sun_preserved": sun_intensity,
        "skylight_before": sky_before,
        "skylight_after": float(sky_component.get_editor_property("intensity")),
        "skylight_real_time_capture": bool(sky_component.get_editor_property("real_time_capture")),
        "skylight_lower_hemisphere_is_black": bool(sky_component.get_editor_property("lower_hemisphere_is_black")),
    }

    post = find_exact(actors, "M01_RS01_PostProcess")
    settings = post.get_editor_property("settings")
    bias_before = float(settings.get_editor_property("auto_exposure_bias"))
    toe_before = float(settings.get_editor_property("film_toe"))
    require(abs(bias_before - 0.5) <= 0.001, f"Exposure authority changed: {bias_before}")
    require(abs(toe_before - 0.55) <= 0.001, f"Film toe authority changed: {toe_before}")
    settings.set_editor_property("override_auto_exposure_bias", True)
    settings.set_editor_property("auto_exposure_bias", TARGET_EXPOSURE_BIAS)
    settings.set_editor_property("override_film_toe", True)
    settings.set_editor_property("film_toe", TARGET_FILM_TOE)
    post.set_editor_property("settings", settings)
    verified_settings = post.get_editor_property("settings")
    result["post_process"] = {
        "auto_exposure_bias_before": bias_before,
        "auto_exposure_bias_after": float(verified_settings.get_editor_property("auto_exposure_bias")),
        "film_toe_before": toe_before,
        "film_toe_after": float(verified_settings.get_editor_property("film_toe")),
    }

    ocean = find_exact(actors, "M01_A01_WaterBodyOcean")
    water_zone = find_exact(actors, "M01_A01_WaterZone")
    ocean_component_class = unreal.load_class(None, "/Script/Water.WaterBodyOceanComponent")
    water_mesh_class = unreal.load_class(None, "/Script/Water.WaterMeshComponent")
    require(ocean_component_class is not None and water_mesh_class is not None, "Water component classes failed to resolve")
    ocean_component = ocean.get_component_by_class(ocean_component_class)
    water_mesh = water_zone.get_component_by_class(water_mesh_class)
    require(ocean_component is not None and water_mesh is not None, "Water components are missing")
    water_material = ocean_component.get_editor_property("water_material")
    require(water_material is not None, "Ocean water material is missing")
    ocean_before = actor_transform(ocean)
    far_material_before = water_mesh.get_editor_property("far_distance_material")
    far_extent_before = float(water_mesh.get_editor_property("far_distance_mesh_extent"))
    location = ocean.get_actor_location()
    ocean.set_actor_location(unreal.Vector(float(location.x), float(location.y), TARGET_OCEAN_Z_CM), False, False)
    water_mesh.set_editor_property("far_distance_material", water_material)
    water_mesh.set_editor_property("far_distance_mesh_extent", TARGET_FAR_WATER_EXTENT_CM)
    if hasattr(ocean_component, "fill_water_zone_with_ocean"):
        ocean_component.fill_water_zone_with_ocean()
    result["water"] = {
        "ocean_before": ocean_before,
        "ocean_after": actor_transform(ocean),
        "water_material": water_material.get_path_name(),
        "far_distance_material_before": None if far_material_before is None else far_material_before.get_path_name(),
        "far_distance_material_after": water_mesh.get_editor_property("far_distance_material").get_path_name(),
        "far_distance_mesh_extent_before_cm": far_extent_before,
        "far_distance_mesh_extent_after_cm": float(water_mesh.get_editor_property("far_distance_mesh_extent")),
    }

    require(abs(result["lighting"]["fill_after"] - TARGET_FILL_INTENSITY) <= 0.001, "Fill target mismatch")
    require(abs(result["lighting"]["skylight_after"] - TARGET_SKYLIGHT_INTENSITY) <= 0.001, "Skylight target mismatch")
    require(result["lighting"]["fill_cast_shadows"] is False, "Fill light must not cast shadows")
    require(result["lighting"]["skylight_lower_hemisphere_is_black"] is False, "Skylight lower hemisphere must remain open")
    require(abs(result["post_process"]["auto_exposure_bias_after"] - TARGET_EXPOSURE_BIAS) <= 0.001, "Exposure target mismatch")
    require(abs(result["post_process"]["film_toe_after"] - TARGET_FILM_TOE) <= 0.001, "Film-toe target mismatch")
    require(abs(result["water"]["ocean_after"]["location_cm"][2] - TARGET_OCEAN_Z_CM) <= 0.01, "Ocean height target mismatch")
    require(result["water"]["far_distance_material_after"] == water_material.get_path_name(), "Far-water material mismatch")
    require(abs(result["water"]["far_distance_mesh_extent_after_cm"] - TARGET_FAR_WATER_EXTENT_CM) <= 1.0, "Far-water extent mismatch")

    actors_after = list(actors_api.get_all_level_actors())
    result["actor_count_after"] = len(actors_after)
    require(len(actors_after) == EXPECTED_ACTOR_COUNT, "Actor count changed")
    require(len([a for a in actors_after if a.get_actor_label().startswith("M01_RS01_Tree_")]) == 0, "Rejected proxy tree returned")
    require(levels.save_current_level(), "Failed to save LightingRoadsWaterline02")
    require(OUTPUT_FILE.is_file(), "LightingRoadsWaterline02 map file was not created")
    result["input_sha256_after"] = sha256(INPUT_FILE)
    require(result["input_sha256_after"] == EXPECTED_INPUT_SHA256, "Accepted input map changed")
    result["output_sha256"] = sha256(OUTPUT_FILE)
    result["quality_metrics"] = {
        "cross_street_dark_concrete_overrides": len(result["cross_street_overrides"]),
        "district_sand_bindings": len(result["terrain_materials"]),
        "proxy_tree_count": 0,
        "actor_count": len(actors_after),
        "far_water_extent_cm": TARGET_FAR_WATER_EXTENT_CM,
        "shore_overlap_cm": TARGET_OCEAN_Z_CM - (-95.0),
    }
    result["classification"] = "PASSED_M01_PHOTOREAL_FOUNDATION_LIGHTING_ROADS_WATERLINE02_AUTOMATIC"
except Exception as exc:
    result["errors"].append({"type": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()})
finally:
    write_json_atomic(RECEIPT, result)

print("SKYGUARD_M01_LIGHTING_ROADS_WATERLINE02=" + str(result["classification"]))
if result["classification"] != "PASSED_M01_PHOTOREAL_FOUNDATION_LIGHTING_ROADS_WATERLINE02_AUTOMATIC":
    raise RuntimeError(result["errors"][-1]["message"] if result["errors"] else "Authoring failed")
