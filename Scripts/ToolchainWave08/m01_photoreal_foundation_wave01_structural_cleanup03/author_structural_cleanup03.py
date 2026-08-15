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
INPUT_ASSET = "/Game/M01/Lvl_M01_PhotorealFoundation_LightingRoadsWaterline02"
OUTPUT_ASSET = "/Game/M01/Lvl_M01_PhotorealFoundation_StructuralCleanup03"
INPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_PhotorealFoundation_LightingRoadsWaterline02.umap"
OUTPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_PhotorealFoundation_StructuralCleanup03.umap"
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_PHOTOREAL_FOUNDATION_WAVE01_STRUCTURAL_CLEANUP03_AUTHORING/attempt_01"
RECEIPT = ATTEMPT / "authoring_receipt.json"

EXPECTED_INPUT_BYTES = 739952
EXPECTED_INPUT_SHA256 = "34b93c53b208fa061538674a36f1aef2a087376ec66a5254465fdafbd8488149"
EXPECTED_ACTOR_COUNT = 120

CROSS_STREET_PATTERN = re.compile(r"^M01_RS01_CrossStreet_\d{2}_\d{2}$")
CROSS_STREET_COUNT = 15
TERRAIN_PATTERN = re.compile(r"^M01_VEK02_District_\d{2}_TERRAIN$")
TERRAIN_COUNT = 4

WAVE1_MATERIAL_ROOT = (
    "/Game/Skyguard/Meshes/Mission01/Wave1Refinement/"
    "m01_wave1_aaa_refinement/Materials"
)
OLD_ASPHALT = WAVE1_MATERIAL_ROOT + "/M_M01_Asphalt.M_M01_Asphalt"
DARK_CONCRETE = WAVE1_MATERIAL_ROOT + "/M_M01_ConcreteDark.M_M01_ConcreteDark"
ROAD_MARK = WAVE1_MATERIAL_ROOT + "/M_M01_RoadMark.M_M01_RoadMark"
SAND = "/Game/M01/EnvKit02/M01_COASTAL_DISTRICT_A/Materials/M_ENV_Sand_Coast_2K.M_ENV_Sand_Coast_2K"

ASPHALT_ASSET = "/Game/M01/EnvKit02/M01_COASTAL_DISTRICT_A/Materials/M_ENV_Asphalt_2K"
PAVERS_ASSET = "/Game/M01/EnvKit02/M01_COASTAL_DISTRICT_A/Materials/M_ENV_Concrete_Pavers_2K"
FAR_WATER_ASSET = "/Water/Materials/WaterSurface/Water_FarMesh"

TARGET_SUN_INTENSITY = 8.0
TARGET_FILL_INTENSITY = 5.5
TARGET_SKYLIGHT_INTENSITY = 6.25
TARGET_EXPOSURE_BIAS = 0.95
TARGET_FILM_TOE = 0.55
TARGET_OCEAN_Z_CM = -80.0
TARGET_ZONE_EXTENT_CM = 800_000.0
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
    "schema": "skyguard.m01-photoreal-foundation.structural-cleanup03.authoring.v1",
    "classification": "FAILED_WITH_EVIDENCE",
    "input_asset": INPUT_ASSET,
    "output_asset": OUTPUT_ASSET,
    "input_sha256_before": None,
    "input_sha256_after": None,
    "output_sha256": None,
    "actor_count_before": None,
    "actor_count_after": None,
    "road_material_corrections": [],
    "terrain_material_corrections": [],
    "lighting": {},
    "post_process": {},
    "water": {},
    "quality_metrics": {},
    "errors": [],
}

try:
    require(INPUT_FILE.is_file(), "Accepted LightingRoadsWaterline02 map is missing")
    require(INPUT_FILE.stat().st_size == EXPECTED_INPUT_BYTES, "Accepted input map byte count changed")
    result["input_sha256_before"] = sha256(INPUT_FILE)
    require(result["input_sha256_before"] == EXPECTED_INPUT_SHA256, "Accepted input map hash changed")
    require(not OUTPUT_FILE.exists(), f"Fresh output file exists: {OUTPUT_FILE}")
    require(not unreal.EditorAssetLibrary.does_asset_exist(OUTPUT_ASSET), f"Fresh output asset exists: {OUTPUT_ASSET}")

    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    actors_api = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    require(levels is not None and actors_api is not None, "Required editor subsystems unavailable")
    require(levels.new_level_from_template(OUTPUT_ASSET, INPUT_ASSET), "Failed to clone LightingRoadsWaterline02")

    actors = list(actors_api.get_all_level_actors())
    result["actor_count_before"] = len(actors)
    require(len(actors) == EXPECTED_ACTOR_COUNT, f"Expected {EXPECTED_ACTOR_COUNT} actors; found {len(actors)}")

    asphalt = unreal.load_asset(ASPHALT_ASSET)
    pavers = unreal.load_asset(PAVERS_ASSET)
    far_water = unreal.load_asset(FAR_WATER_ASSET)
    require(asphalt is not None and pavers is not None and far_water is not None, "Required local materials failed to load")

    cross_streets = sorted(
        (actor for actor in actors if CROSS_STREET_PATTERN.match(actor.get_actor_label())),
        key=lambda actor: actor.get_actor_label(),
    )
    require(len(cross_streets) == CROSS_STREET_COUNT, f"Expected {CROSS_STREET_COUNT} CrossStreet actors")
    for actor in cross_streets:
        before_transform = actor_transform(actor)
        component = static_mesh_component(actor)
        require(component.get_num_materials() == 3, f"Unexpected CrossStreet slot count: {actor.get_actor_label()}")
        before = [material_path(component, slot) for slot in range(3)]
        require(before == [OLD_ASPHALT, DARK_CONCRETE, ROAD_MARK], f"Unexpected CrossStreet materials: {actor.get_actor_label()} -> {before}")
        component.set_material(0, asphalt)
        component.set_material(2, asphalt)
        after = [material_path(component, slot) for slot in range(3)]
        require(after[0] == asphalt.get_path_name(), f"CrossStreet base-asphalt correction failed: {actor.get_actor_label()}")
        require(after[1] == DARK_CONCRETE, f"CrossStreet dark-concrete slot drifted: {actor.get_actor_label()}")
        require(after[2] == asphalt.get_path_name(), f"CrossStreet malformed road-mark surface correction failed: {actor.get_actor_label()}")
        require(actor_transform(actor) == before_transform, f"CrossStreet transform drift: {actor.get_actor_label()}")
        result["road_material_corrections"].append({
            "label": actor.get_actor_label(),
            "before": before,
            "after": after,
            "corrected_slots": [0, 2],
        })

    terrain_actors = sorted(
        (actor for actor in actors if TERRAIN_PATTERN.match(actor.get_actor_label())),
        key=lambda actor: actor.get_actor_label(),
    )
    require(len(terrain_actors) == TERRAIN_COUNT, f"Expected {TERRAIN_COUNT} district terrain actors")
    for actor in terrain_actors:
        before_transform = actor_transform(actor)
        component = static_mesh_component(actor)
        require(component.get_num_materials() == 1, f"Unexpected terrain slot count: {actor.get_actor_label()}")
        before = material_path(component, 0)
        require(before == SAND, f"Unexpected district terrain material: {actor.get_actor_label()} -> {before}")
        component.set_material(0, pavers)
        after = material_path(component, 0)
        require(after == pavers.get_path_name(), f"Urban paver material binding failed: {actor.get_actor_label()}")
        require(actor_transform(actor) == before_transform, f"District terrain transform drift: {actor.get_actor_label()}")
        result["terrain_material_corrections"].append({"label": actor.get_actor_label(), "before": before, "after": after})

    fill = find_exact(actors, "M01_PR01_FillSun")
    fill_component = fill.get_component_by_class(unreal.DirectionalLightComponent)
    require(fill_component is not None, "Fill DirectionalLightComponent missing")
    fill_before = float(fill_component.get_editor_property("intensity"))
    require(abs(fill_before - 4.25) <= 0.001, f"Fill intensity authority changed: {fill_before}")
    fill_component.set_editor_property("intensity", TARGET_FILL_INTENSITY)
    fill_component.set_editor_property("cast_shadows", False)

    sun = find_exact(actors, "M01_RS01_Sun")
    sun_component = sun.get_component_by_class(unreal.DirectionalLightComponent)
    require(sun_component is not None, "Sun DirectionalLightComponent missing")
    sun_before = float(sun_component.get_editor_property("intensity"))
    require(abs(sun_before - 10.0) <= 0.001, f"Sun intensity authority changed: {sun_before}")
    sun_component.set_editor_property("intensity", TARGET_SUN_INTENSITY)

    sky = find_exact(actors, "M01_RS01_SkyLight")
    sky_component = sky.get_component_by_class(unreal.SkyLightComponent)
    require(sky_component is not None, "SkyLightComponent missing")
    sky_before = float(sky_component.get_editor_property("intensity"))
    require(abs(sky_before - 4.75) <= 0.001, f"Skylight intensity authority changed: {sky_before}")
    sky_component.set_editor_property("intensity", TARGET_SKYLIGHT_INTENSITY)
    sky_component.set_editor_property("real_time_capture", True)
    sky_component.set_editor_property("lower_hemisphere_is_black", False)
    result["lighting"] = {
        "sun_before": sun_before,
        "sun_after": float(sun_component.get_editor_property("intensity")),
        "fill_before": fill_before,
        "fill_after": float(fill_component.get_editor_property("intensity")),
        "fill_cast_shadows": bool(fill_component.get_editor_property("cast_shadows")),
        "skylight_before": sky_before,
        "skylight_after": float(sky_component.get_editor_property("intensity")),
        "skylight_real_time_capture": bool(sky_component.get_editor_property("real_time_capture")),
        "skylight_lower_hemisphere_is_black": bool(sky_component.get_editor_property("lower_hemisphere_is_black")),
    }

    post = find_exact(actors, "M01_RS01_PostProcess")
    settings = post.get_editor_property("settings")
    bias_before = float(settings.get_editor_property("auto_exposure_bias"))
    toe_before = float(settings.get_editor_property("film_toe"))
    require(abs(bias_before - 0.85) <= 0.001, f"Exposure authority changed: {bias_before}")
    require(abs(toe_before - 0.42) <= 0.001, f"Film-toe authority changed: {toe_before}")
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
    ocean_before = actor_transform(ocean)
    require(abs(ocean_before["location_cm"][2] - TARGET_OCEAN_Z_CM) <= 0.01, "Ocean height authority changed")
    zone_before = vector2(water_zone.get_editor_property("zone_extent"))
    require(abs(zone_before[0] - 180_000.0) <= 1.0 and abs(zone_before[1] - 180_000.0) <= 1.0, f"WaterZone extent authority changed: {zone_before}")
    far_material_before = water_mesh.get_editor_property("far_distance_material")
    far_extent_before = float(water_mesh.get_editor_property("far_distance_mesh_extent"))
    require(far_material_before is not None, "Far-water material authority is missing")
    require(abs(far_extent_before - TARGET_FAR_WATER_EXTENT_CM) <= 1.0, "Far-water extent authority changed")
    water_zone.set_editor_property("zone_extent", unreal.Vector2D(TARGET_ZONE_EXTENT_CM, TARGET_ZONE_EXTENT_CM))
    water_mesh.set_editor_property("far_distance_material", far_water)
    water_mesh.set_editor_property("far_distance_mesh_extent", TARGET_FAR_WATER_EXTENT_CM)
    if hasattr(ocean_component, "fill_water_zone_with_ocean"):
        ocean_component.fill_water_zone_with_ocean()
    zone_after = vector2(water_zone.get_editor_property("zone_extent"))
    result["water"] = {
        "ocean_transform_preserved": actor_transform(ocean),
        "zone_extent_before_cm": zone_before,
        "zone_extent_after_cm": zone_after,
        "far_distance_material_before": far_material_before.get_path_name(),
        "far_distance_material_after": water_mesh.get_editor_property("far_distance_material").get_path_name(),
        "far_distance_mesh_extent_before_cm": far_extent_before,
        "far_distance_mesh_extent_after_cm": float(water_mesh.get_editor_property("far_distance_mesh_extent")),
    }

    require(abs(result["lighting"]["sun_after"] - TARGET_SUN_INTENSITY) <= 0.001, "Sun target mismatch")
    require(abs(result["lighting"]["fill_after"] - TARGET_FILL_INTENSITY) <= 0.001, "Fill target mismatch")
    require(abs(result["lighting"]["skylight_after"] - TARGET_SKYLIGHT_INTENSITY) <= 0.001, "Skylight target mismatch")
    require(result["lighting"]["fill_cast_shadows"] is False, "Fill light must not cast shadows")
    require(result["lighting"]["skylight_lower_hemisphere_is_black"] is False, "Skylight lower hemisphere must remain open")
    require(abs(result["post_process"]["auto_exposure_bias_after"] - TARGET_EXPOSURE_BIAS) <= 0.001, "Exposure target mismatch")
    require(abs(result["post_process"]["film_toe_after"] - TARGET_FILM_TOE) <= 0.001, "Film-toe target mismatch")
    require(all(abs(value - TARGET_ZONE_EXTENT_CM) <= 1.0 for value in zone_after), "WaterZone target mismatch")
    require(result["water"]["far_distance_material_after"] == far_water.get_path_name(), "Far-water material mismatch")

    actors_after = list(actors_api.get_all_level_actors())
    result["actor_count_after"] = len(actors_after)
    require(len(actors_after) == EXPECTED_ACTOR_COUNT, "Actor count changed")
    require(len([a for a in actors_after if a.get_actor_label().startswith("M01_RS01_Tree_")]) == 0, "Rejected proxy tree returned")
    require(levels.save_current_level(), "Failed to save StructuralCleanup03")
    require(OUTPUT_FILE.is_file(), "StructuralCleanup03 map file was not created")
    result["input_sha256_after"] = sha256(INPUT_FILE)
    require(result["input_sha256_after"] == EXPECTED_INPUT_SHA256, "Accepted input map changed")
    result["output_sha256"] = sha256(OUTPUT_FILE)
    result["quality_metrics"] = {
        "cross_street_actor_count": len(result["road_material_corrections"]),
        "cross_street_corrected_surface_count": len(result["road_material_corrections"]) * 2,
        "district_urban_paver_bindings": len(result["terrain_material_corrections"]),
        "proxy_tree_count": 0,
        "actor_count": len(actors_after),
        "water_zone_extent_cm": TARGET_ZONE_EXTENT_CM,
        "far_water_extent_cm": TARGET_FAR_WATER_EXTENT_CM,
    }
    result["classification"] = "PASSED_M01_PHOTOREAL_FOUNDATION_STRUCTURAL_CLEANUP03_AUTOMATIC"
except Exception as exc:
    result["errors"].append({"type": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()})
finally:
    write_json_atomic(RECEIPT, result)

print("SKYGUARD_M01_STRUCTURAL_CLEANUP03=" + str(result["classification"]))
if result["classification"] != "PASSED_M01_PHOTOREAL_FOUNDATION_STRUCTURAL_CLEANUP03_AUTOMATIC":
    raise RuntimeError(result["errors"][-1]["message"] if result["errors"] else "Authoring failed")
