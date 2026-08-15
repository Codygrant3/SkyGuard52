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
INPUT_ASSET = "/Game/M01/Lvl_M01_PhotorealFoundation_StructuralCleanup03"
OUTPUT_ASSET = "/Game/M01/Lvl_M01_PhotorealFoundation_GroundLightingCorrection04"
INPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_PhotorealFoundation_StructuralCleanup03.umap"
OUTPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_PhotorealFoundation_GroundLightingCorrection04.umap"
MATERIAL_ROOT = "/Game/M01/GroundLightingCorrection04/Materials"
MATERIAL_DIRECTORY = ISOLATED / "Content/M01/GroundLightingCorrection04"
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_PHOTOREAL_FOUNDATION_WAVE01_GROUND_LIGHTING_CORRECTION04_AUTHORING/attempt_01"
RECEIPT = ATTEMPT / "authoring_receipt.json"

EXPECTED_INPUT_BYTES = 738931
EXPECTED_INPUT_SHA256 = "142222c49c2ac232c301d14717a61c7a49c104df94ffeaa0e8ad21194184e08d"
EXPECTED_ACTOR_COUNT = 120

TERRAIN_PATTERN = re.compile(r"^M01_VEK02_District_\d{2}_TERRAIN$")
GLAZING_PATTERN = re.compile(r"^M01_VEK02_City_R\d{2}_C\d{2}_[A-Za-z]+_GLAZING$")
EXPECTED_TERRAIN_COUNT = 4
EXPECTED_GLAZING_COUNT = 27

SOURCE_SAND = "/Game/M01/EnvKit02/M01_COASTAL_DISTRICT_A/Materials/M_ENV_Sand_Coast_2K"
SOURCE_PAVERS = "/Game/M01/EnvKit02/M01_COASTAL_DISTRICT_A/Materials/M_ENV_Concrete_Pavers_2K"
SOURCE_FAR_WATER = "/Water/Materials/WaterSurface/Water_FarMesh"
SOURCE_WINDOW = "/Game/Skyguard/Meshes/Mission01/Wave1Refinement/m01_wave1_aaa_refinement/Materials/M_M01_Window"
SOURCE_GLASS = "/Game/Skyguard/Meshes/Mission01/Wave1Refinement/m01_wave1_aaa_refinement/Materials/M_M01_Glass"
SOURCE_TERRAIN = "/Game/Skyguard/Materials/M_Terrain.M_Terrain"

DEST_SAND = MATERIAL_ROOT + "/MI_M01_BeachSand_Tiled"
DEST_PAVERS = MATERIAL_ROOT + "/MI_M01_UrbanGround_Tiled"
DEST_FAR_WATER = MATERIAL_ROOT + "/MI_M01_OceanFar_Cohesive"
DEST_WINDOW = MATERIAL_ROOT + "/MI_M01_Window_Lifted"
DEST_GLASS = MATERIAL_ROOT + "/MI_M01_Glass_Lifted"

WINDOW_OBJECT = SOURCE_WINDOW + ".M_M01_Window"
GLASS_OBJECT = SOURCE_GLASS + ".M_M01_Glass"
PAVERS_OBJECT = SOURCE_PAVERS + ".M_ENV_Concrete_Pavers_2K"

TEXTURE_OFFSET_PARAMETERS = (
    "BaseColorTexture_OffsetScale",
    "MetallicRoughnessTexture_OffsetScale",
    "NormalTexture_OffsetScale",
)

TARGET_SAND_TILING = (0.0, 0.0, 70.0, 18.0)
TARGET_URBAN_TILING = (0.0, 0.0, 126.0, 47.0)
TARGET_FAR_ALBEDO = (0.018, 0.055, 0.085, 0.5)
TARGET_FAR_SCATTERING = (0.045, 0.14, 0.22, 0.5)
TARGET_WINDOW_COLOR = (0.08, 0.22, 0.30, 1.0)
TARGET_GLASS_COLOR = (0.07, 0.20, 0.28, 1.0)
TARGET_SUN_INTENSITY = 6.5
TARGET_FILL_INTENSITY = 8.0
TARGET_SKYLIGHT_INTENSITY = 9.0
TARGET_LOWER_HEMISPHERE = (0.08, 0.11, 0.15, 1.0)
TARGET_EXPOSURE_BIAS = 1.10
TARGET_FILM_TOE = 0.62


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


def rgba(value: object) -> list[float]:
    return [float(value.r), float(value.g), float(value.b), float(value.a)]


def actor_transform(actor: object) -> dict[str, list[float]]:
    location = actor.get_actor_location()
    rotation = actor.get_actor_rotation()
    scale = actor.get_actor_scale3d()
    return {
        "location_cm": [float(location.x), float(location.y), float(location.z)],
        "rotation_degrees": [float(rotation.pitch), float(rotation.yaw), float(rotation.roll)],
        "scale": [float(scale.x), float(scale.y), float(scale.z)],
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


def asset_file(asset_path: str) -> Path:
    require(asset_path.startswith("/Game/"), f"Only project-local assets can be inventoried: {asset_path}")
    return ISOLATED / "Content" / (asset_path[len("/Game/") :] + ".uasset")


def same_values(actual: list[float], expected: tuple[float, float, float, float], tolerance: float = 0.0005) -> bool:
    return len(actual) == 4 and all(abs(a - b) <= tolerance for a, b in zip(actual, expected))


def duplicate_material(source: str, destination: str):
    require(unreal.EditorAssetLibrary.does_asset_exist(source), f"Source material missing: {source}")
    require(not unreal.EditorAssetLibrary.does_asset_exist(destination), f"Destination material already exists: {destination}")
    created = unreal.EditorAssetLibrary.duplicate_asset(source, destination)
    require(created is not None, f"Failed to duplicate material: {source} -> {destination}")
    loaded = unreal.load_asset(destination)
    require(loaded is not None and isinstance(loaded, unreal.MaterialInstanceConstant), f"Destination is not a material instance: {destination}")
    return loaded


def set_vector(instance: object, parameter: str, values: tuple[float, float, float, float]) -> None:
    success = unreal.MaterialEditingLibrary.set_material_instance_vector_parameter_value(
        instance,
        parameter,
        unreal.LinearColor(*values),
    )
    require(bool(success), f"Failed to set {parameter} on {instance.get_path_name()}")


def verify_vector(instance: object, parameter: str, expected: tuple[float, float, float, float]) -> list[float]:
    value = unreal.MaterialEditingLibrary.get_material_instance_vector_parameter_value(instance, parameter)
    actual = rgba(value)
    require(same_values(actual, expected), f"Parameter mismatch {instance.get_path_name()}::{parameter}: {actual} != {expected}")
    return actual


result: dict[str, object] = {
    "schema": "skyguard.m01-photoreal-foundation.ground-lighting-correction04.authoring.v1",
    "classification": "FAILED_WITH_EVIDENCE",
    "input_asset": INPUT_ASSET,
    "output_asset": OUTPUT_ASSET,
    "input_sha256_before": None,
    "input_sha256_after": None,
    "output_sha256": None,
    "actor_count_before": None,
    "actor_count_after": None,
    "created_materials": [],
    "terrain_bindings": [],
    "landscape": {},
    "glazing_bindings": [],
    "lighting": {},
    "post_process": {},
    "water": {},
    "quality_metrics": {},
    "errors": [],
}

try:
    require(INPUT_FILE.is_file(), "Accepted StructuralCleanup03 map is missing")
    require(INPUT_FILE.stat().st_size == EXPECTED_INPUT_BYTES, "Accepted input map byte count changed")
    result["input_sha256_before"] = sha256(INPUT_FILE)
    require(result["input_sha256_before"] == EXPECTED_INPUT_SHA256, "Accepted input map hash changed")
    require(not OUTPUT_FILE.exists(), f"Fresh output map exists: {OUTPUT_FILE}")
    require(not MATERIAL_DIRECTORY.exists(), f"Fresh material namespace exists: {MATERIAL_DIRECTORY}")
    require(not unreal.EditorAssetLibrary.does_asset_exist(OUTPUT_ASSET), f"Fresh output asset exists: {OUTPUT_ASSET}")

    unreal.EditorAssetLibrary.make_directory(MATERIAL_ROOT)
    sand = duplicate_material(SOURCE_SAND, DEST_SAND)
    pavers = duplicate_material(SOURCE_PAVERS, DEST_PAVERS)
    far_water = duplicate_material(SOURCE_FAR_WATER, DEST_FAR_WATER)
    window = duplicate_material(SOURCE_WINDOW, DEST_WINDOW)
    glass = duplicate_material(SOURCE_GLASS, DEST_GLASS)

    for parameter in TEXTURE_OFFSET_PARAMETERS:
        set_vector(sand, parameter, TARGET_SAND_TILING)
        set_vector(pavers, parameter, TARGET_URBAN_TILING)
    set_vector(far_water, "Water Albedo", TARGET_FAR_ALBEDO)
    set_vector(far_water, "Scattering", TARGET_FAR_SCATTERING)
    set_vector(window, "BaseColorFactor", TARGET_WINDOW_COLOR)
    set_vector(glass, "BaseColorFactor", TARGET_GLASS_COLOR)

    for asset in (sand, pavers, far_water, window, glass):
        unreal.MaterialEditingLibrary.update_material_instance(asset)
        require(unreal.EditorAssetLibrary.save_loaded_asset(asset), f"Failed to save {asset.get_path_name()}")

    for parameter in TEXTURE_OFFSET_PARAMETERS:
        verify_vector(sand, parameter, TARGET_SAND_TILING)
        verify_vector(pavers, parameter, TARGET_URBAN_TILING)
    verify_vector(far_water, "Water Albedo", TARGET_FAR_ALBEDO)
    verify_vector(far_water, "Scattering", TARGET_FAR_SCATTERING)
    verify_vector(window, "BaseColorFactor", TARGET_WINDOW_COLOR)
    verify_vector(glass, "BaseColorFactor", TARGET_GLASS_COLOR)

    for destination, source in (
        (DEST_SAND, SOURCE_SAND),
        (DEST_PAVERS, SOURCE_PAVERS),
        (DEST_FAR_WATER, SOURCE_FAR_WATER),
        (DEST_WINDOW, SOURCE_WINDOW),
        (DEST_GLASS, SOURCE_GLASS),
    ):
        file_path = asset_file(destination)
        require(file_path.is_file(), f"Saved material file missing: {file_path}")
        result["created_materials"].append(
            {
                "asset": destination,
                "source": source,
                "file": str(file_path),
                "bytes": file_path.stat().st_size,
                "sha256": sha256(file_path),
            }
        )

    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    actors_api = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    require(levels is not None and actors_api is not None, "Required editor subsystems unavailable")
    require(levels.new_level_from_template(OUTPUT_ASSET, INPUT_ASSET), "Failed to clone StructuralCleanup03")

    actors = list(actors_api.get_all_level_actors())
    result["actor_count_before"] = len(actors)
    require(len(actors) == EXPECTED_ACTOR_COUNT, f"Expected {EXPECTED_ACTOR_COUNT} actors; found {len(actors)}")
    transforms_before = {actor.get_actor_label(): actor_transform(actor) for actor in actors}

    terrain_actors = sorted(
        (actor for actor in actors if TERRAIN_PATTERN.match(actor.get_actor_label())),
        key=lambda actor: actor.get_actor_label(),
    )
    require(len(terrain_actors) == EXPECTED_TERRAIN_COUNT, f"Expected {EXPECTED_TERRAIN_COUNT} district terrain actors")
    for actor in terrain_actors:
        component = static_mesh_component(actor)
        require(component.get_num_materials() == 1, f"Unexpected terrain slot count: {actor.get_actor_label()}")
        before = material_path(component, 0)
        require(before == PAVERS_OBJECT, f"Unexpected StructuralCleanup03 terrain material: {actor.get_actor_label()} -> {before}")
        component.set_material(0, sand)
        after = material_path(component, 0)
        require(after == sand.get_path_name(), f"Tiled beach-sand binding failed: {actor.get_actor_label()}")
        result["terrain_bindings"].append({"label": actor.get_actor_label(), "before": before, "after": after})

    landscape = find_exact(actors, "M01_A01_Landscape_Production")
    landscape_before = landscape.get_editor_property("landscape_material")
    require(landscape_before is not None and landscape_before.get_path_name() == SOURCE_TERRAIN, "Landscape material authority changed")
    landscape.set_editor_property("landscape_material", pavers)
    landscape_after = landscape.get_editor_property("landscape_material")
    require(landscape_after is not None and landscape_after.get_path_name() == pavers.get_path_name(), "Urban-ground landscape binding failed")
    result["landscape"] = {"before": landscape_before.get_path_name(), "after": landscape_after.get_path_name()}

    glazing_actors = sorted(
        (actor for actor in actors if GLAZING_PATTERN.match(actor.get_actor_label())),
        key=lambda actor: actor.get_actor_label(),
    )
    require(len(glazing_actors) == EXPECTED_GLAZING_COUNT, f"Expected {EXPECTED_GLAZING_COUNT} glazing actors; found {len(glazing_actors)}")
    for actor in glazing_actors:
        component = static_mesh_component(actor)
        require(component.get_num_materials() == 3, f"Unexpected glazing slot count: {actor.get_actor_label()}")
        before = [material_path(component, slot) for slot in range(3)]
        require(before[0] == WINDOW_OBJECT and before[1] == GLASS_OBJECT, f"Unexpected glazing authority: {actor.get_actor_label()} -> {before}")
        curtain = before[2]
        component.set_material(0, window)
        component.set_material(1, glass)
        after = [material_path(component, slot) for slot in range(3)]
        require(after == [window.get_path_name(), glass.get_path_name(), curtain], f"Glazing binding failed: {actor.get_actor_label()}")
        result["glazing_bindings"].append({"label": actor.get_actor_label(), "before": before, "after": after})

    sun = find_exact(actors, "M01_RS01_Sun")
    fill = find_exact(actors, "M01_PR01_FillSun")
    sky = find_exact(actors, "M01_RS01_SkyLight")
    sun_component = sun.get_component_by_class(unreal.DirectionalLightComponent)
    fill_component = fill.get_component_by_class(unreal.DirectionalLightComponent)
    sky_component = sky.get_component_by_class(unreal.SkyLightComponent)
    require(sun_component is not None and fill_component is not None and sky_component is not None, "Lighting components missing")
    lighting_before = {
        "sun_intensity": float(sun_component.get_editor_property("intensity")),
        "fill_intensity": float(fill_component.get_editor_property("intensity")),
        "skylight_intensity": float(sky_component.get_editor_property("intensity")),
        "lower_hemisphere_color": rgba(sky_component.get_editor_property("lower_hemisphere_color")),
    }
    require(abs(lighting_before["sun_intensity"] - 8.0) <= 0.001, "Sun intensity authority changed")
    require(abs(lighting_before["fill_intensity"] - 5.5) <= 0.001, "Fill intensity authority changed")
    require(abs(lighting_before["skylight_intensity"] - 6.25) <= 0.001, "Skylight intensity authority changed")
    sun_component.set_editor_property("intensity", TARGET_SUN_INTENSITY)
    fill_component.set_editor_property("intensity", TARGET_FILL_INTENSITY)
    fill_component.set_editor_property("cast_shadows", False)
    sky_component.set_editor_property("intensity", TARGET_SKYLIGHT_INTENSITY)
    sky_component.set_editor_property("real_time_capture", True)
    sky_component.set_editor_property("lower_hemisphere_is_black", False)
    sky_component.set_editor_property("lower_hemisphere_color", unreal.LinearColor(*TARGET_LOWER_HEMISPHERE))
    result["lighting"] = {
        "before": lighting_before,
        "after": {
            "sun_intensity": float(sun_component.get_editor_property("intensity")),
            "fill_intensity": float(fill_component.get_editor_property("intensity")),
            "fill_cast_shadows": bool(fill_component.get_editor_property("cast_shadows")),
            "skylight_intensity": float(sky_component.get_editor_property("intensity")),
            "lower_hemisphere_is_black": bool(sky_component.get_editor_property("lower_hemisphere_is_black")),
            "lower_hemisphere_color": rgba(sky_component.get_editor_property("lower_hemisphere_color")),
        },
    }

    post = find_exact(actors, "M01_RS01_PostProcess")
    settings = post.get_editor_property("settings")
    bias_before = float(settings.get_editor_property("auto_exposure_bias"))
    toe_before = float(settings.get_editor_property("film_toe"))
    require(abs(bias_before - 0.95) <= 0.001 and abs(toe_before - 0.55) <= 0.001, "Post-process authority changed")
    settings.set_editor_property("override_auto_exposure_bias", True)
    settings.set_editor_property("auto_exposure_bias", TARGET_EXPOSURE_BIAS)
    settings.set_editor_property("override_film_toe", True)
    settings.set_editor_property("film_toe", TARGET_FILM_TOE)
    post.set_editor_property("settings", settings)
    checked_settings = post.get_editor_property("settings")
    result["post_process"] = {
        "auto_exposure_bias_before": bias_before,
        "auto_exposure_bias_after": float(checked_settings.get_editor_property("auto_exposure_bias")),
        "film_toe_before": toe_before,
        "film_toe_after": float(checked_settings.get_editor_property("film_toe")),
    }

    water_zone = find_exact(actors, "M01_A01_WaterZone")
    water_mesh_class = unreal.load_class(None, "/Script/Water.WaterMeshComponent")
    require(water_mesh_class is not None, "WaterMeshComponent class failed to load")
    water_mesh = water_zone.get_component_by_class(water_mesh_class)
    require(water_mesh is not None, "WaterMeshComponent missing")
    far_before = water_mesh.get_editor_property("far_distance_material")
    require(far_before is not None and far_before.get_path_name() == SOURCE_FAR_WATER + ".Water_FarMesh", "Far-water authority changed")
    extent_before = float(water_mesh.get_editor_property("far_distance_mesh_extent"))
    require(abs(extent_before - 4_000_000.0) <= 1.0, "Far-water extent authority changed")
    water_mesh.set_editor_property("far_distance_material", far_water)
    far_after = water_mesh.get_editor_property("far_distance_material")
    require(far_after is not None and far_after.get_path_name() == far_water.get_path_name(), "Cohesive far-water binding failed")
    result["water"] = {
        "far_material_before": far_before.get_path_name(),
        "far_material_after": far_after.get_path_name(),
        "far_extent_cm_before": extent_before,
        "far_extent_cm_after": float(water_mesh.get_editor_property("far_distance_mesh_extent")),
    }

    actors_after = list(actors_api.get_all_level_actors())
    result["actor_count_after"] = len(actors_after)
    require(len(actors_after) == EXPECTED_ACTOR_COUNT, "Actor count changed")
    for actor in actors_after:
        label = actor.get_actor_label()
        require(label in transforms_before, f"Unexpected actor appeared: {label}")
        require(actor_transform(actor) == transforms_before[label], f"Actor transform changed: {label}")
    require(len([actor for actor in actors_after if actor.get_actor_label().startswith("M01_RS01_Tree_")]) == 0, "Rejected proxy tree returned")

    require(levels.save_current_level(), "Failed to save GroundLightingCorrection04")
    require(OUTPUT_FILE.is_file(), "GroundLightingCorrection04 map file was not created")
    result["input_sha256_after"] = sha256(INPUT_FILE)
    require(result["input_sha256_after"] == EXPECTED_INPUT_SHA256, "Accepted source map changed")
    result["output_sha256"] = sha256(OUTPUT_FILE)
    result["quality_metrics"] = {
        "actor_count": len(actors_after),
        "created_material_count": len(result["created_materials"]),
        "tiled_beach_bindings": len(result["terrain_bindings"]),
        "tiled_urban_landscape_bindings": 1,
        "lifted_glazing_actor_count": len(result["glazing_bindings"]),
        "far_water_cohesive_bindings": 1,
        "transforms_preserved": len(actors_after),
        "proxy_tree_count": 0,
    }
    require(result["quality_metrics"] == {
        "actor_count": 120,
        "created_material_count": 5,
        "tiled_beach_bindings": 4,
        "tiled_urban_landscape_bindings": 1,
        "lifted_glazing_actor_count": 27,
        "far_water_cohesive_bindings": 1,
        "transforms_preserved": 120,
        "proxy_tree_count": 0,
    }, "Quality metrics do not match the bounded correction contract")
    result["classification"] = "PASSED_M01_PHOTOREAL_FOUNDATION_GROUND_LIGHTING_CORRECTION04_AUTOMATIC"
except Exception as exc:
    result["errors"].append({"type": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()})
finally:
    write_json_atomic(RECEIPT, result)

print("SKYGUARD_M01_GROUND_LIGHTING_CORRECTION04=" + str(result["classification"]))
if result["classification"] != "PASSED_M01_PHOTOREAL_FOUNDATION_GROUND_LIGHTING_CORRECTION04_AUTOMATIC":
    raise RuntimeError(result["errors"][-1]["message"] if result["errors"] else "Authoring failed")
