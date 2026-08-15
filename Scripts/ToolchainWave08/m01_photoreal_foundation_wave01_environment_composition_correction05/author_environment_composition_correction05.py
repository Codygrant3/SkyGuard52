"""Author a fresh geometry-first Mission 1 environment correction.

The previous D3D12 proof was runtime-stable but visually rejected.  This pass
addresses only measured causes: UV-less beach slabs, over-thick cross streets,
rigid building repetition, mismatched near/far water, and crushed shadow tone.
The accepted input map is cloned and never modified.
"""

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
INPUT_ASSET = "/Game/M01/Lvl_M01_PhotorealFoundation_GroundLightingCorrection04Recovery01"
OUTPUT_ASSET = "/Game/M01/Lvl_M01_PhotorealFoundation_EnvironmentCompositionCorrection05"
INPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_PhotorealFoundation_GroundLightingCorrection04Recovery01.umap"
OUTPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_PhotorealFoundation_EnvironmentCompositionCorrection05.umap"
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_PHOTOREAL_FOUNDATION_WAVE01_ENVIRONMENT_COMPOSITION_CORRECTION05_AUTHORING/attempt_01"
RECEIPT = ATTEMPT / "authoring_receipt.json"

EXPECTED_INPUT_BYTES = 743809
EXPECTED_INPUT_SHA256 = "97902b7dd39556d4409adcdd87a8c995cfef1322a8e827c52cae7a84020093cf"
EXPECTED_ACTOR_COUNT = 120
EXPECTED_REMOVED_TERRAIN = 4
EXPECTED_BEACH_MODULES = 24
EXPECTED_CROSS_STREETS = 15
EXPECTED_BUILDING_GROUPS = 81
EXPECTED_BUILDINGS = 27
EXPECTED_FINAL_ACTOR_COUNT = 140

TERRAIN_PATTERN = re.compile(r"^M01_VEK02_District_\d{2}_TERRAIN$")
CROSS_STREET_PATTERN = re.compile(r"^M01_RS01_CrossStreet_\d{2}_\d{2}$")
BUILDING_PATTERN = re.compile(
    r"^(?P<instance>M01_VEK02_City_R(?P<row>\d{2})_C(?P<column>\d{2})_[A-Za-z]+)_(?P<group>DETAILS|GLAZING|STRUCTURAL)$"
)

BEACH_MESH_PATH = "/Game/Skyguard/Meshes/Mission01/Wave1Refinement/m01_wave1_aaa_refinement/StaticMeshes/SM_M01_Coast_Beach_Detailed_A"
SAND_MATERIAL_PATH = "/Game/M01/GroundLightingCorrection04Recovery01/Materials/MI_M01_BeachSand_Tiled"
OCEAN_MATERIAL_PATH = "/Water/Materials/WaterSurface/Water_Material_Ocean"
FAR_WATER_MATERIAL_PATH = "/Water/Materials/WaterSurface/Water_FarMesh"
OCEAN_WAVES_PATH = "/Water/Waves/GerstnerWaves_Ocean"

EXPECTED_PREVIOUS_OCEAN_MATERIAL = "/Game/Skyguard/Materials/Generated/M_L23_Ocean.M_L23_Ocean"
EXPECTED_PREVIOUS_FAR_MATERIAL = "/Game/M01/GroundLightingCorrection04Recovery01/Materials/MI_M01_OceanFar_Cohesive.MI_M01_OceanFar_Cohesive"
EXPECTED_PREVIOUS_SKYLIGHT = 9.0
EXPECTED_PREVIOUS_EXPOSURE = 1.10
EXPECTED_PREVIOUS_FILM_TOE = 0.62

TARGET_ROAD_Z_SCALE = 0.12
TARGET_SKYLIGHT = 10.5
TARGET_EXPOSURE = 1.14
TARGET_FILM_TOE = 0.40
TARGET_LOWER_HEMISPHERE = (0.13, 0.16, 0.20, 1.0)

BEACH_X_CENTERS = tuple(-1600.0 + 4800.0 * index for index in range(12))
BEACH_ROWS = (
    ("SEAWARD", 4700.0, -95.0),
    ("INLAND", 6500.0, -65.0),
)

X_OFFSETS = (-180.0, 90.0, 210.0, -120.0, 150.0, -220.0, 60.0, 190.0, -80.0)
Y_OFFSETS = (
    (0.0, 120.0, -80.0, 160.0, -120.0, 60.0, -160.0, 80.0, -40.0),
    (-100.0, 60.0, 140.0, -60.0, 110.0, -140.0, 40.0, 150.0, -90.0),
    (120.0, -120.0, 40.0, 90.0, -160.0, 130.0, -50.0, 70.0, -110.0),
)
YAW_OFFSETS = (-2.0, 1.5, 2.5, -1.25, 0.75, -2.5, 1.25, 2.0, -0.75)
Z_SCALES = (0.96, 1.04, 1.08, 0.94, 1.02, 1.06, 0.98, 1.07, 0.95)


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


def rgba(value: object) -> list[float]:
    return [float(value.r), float(value.g), float(value.b), float(value.a)]


def actor_transform(actor: object) -> dict[str, list[float]]:
    location = actor.get_actor_location()
    rotation = actor.get_actor_rotation()
    scale = actor.get_actor_scale3d()
    return {
        "location_cm": vector(location),
        "rotation_degrees": [float(rotation.pitch), float(rotation.yaw), float(rotation.roll)],
        "scale": vector(scale),
    }


def same_transform(left: dict[str, list[float]], right: dict[str, list[float]], tolerance: float = 0.01) -> bool:
    for key in ("location_cm", "rotation_degrees", "scale"):
        if any(abs(a - b) > tolerance for a, b in zip(left[key], right[key])):
            return False
    return True


def find_exact(actors: list[object], label: str):
    matches = [actor for actor in actors if actor.get_actor_label() == label]
    require(len(matches) == 1, f"Expected exactly one {label}; found {len(matches)}")
    return matches[0]


def load_required(path: str, expected_type: object):
    asset = unreal.load_asset(path)
    require(asset is not None and isinstance(asset, expected_type), f"Required asset unavailable or wrong type: {path}")
    return asset


def static_mesh_component(actor: object):
    component = actor.get_component_by_class(unreal.StaticMeshComponent)
    require(component is not None, f"StaticMeshComponent missing: {actor.get_actor_label()}")
    require(component.get_editor_property("static_mesh") is not None, f"Static mesh missing: {actor.get_actor_label()}")
    return component


def object_path(value: object) -> str:
    require(value is not None, "Expected non-null object")
    return str(value.get_path_name())


def spawn_beach_module(actors_api: object, mesh: object, material: object, row_name: str, row_index: int, column: int, center_x: float, center_y: float, target_bottom: float):
    yaw = 180.0 if (row_index + column) % 2 else 0.0
    bounds = mesh.get_bounds()
    local_bottom = float(bounds.origin.z - bounds.box_extent.z)
    location = unreal.Vector(center_x, center_y, target_bottom - local_bottom)
    actor = actors_api.spawn_actor_from_class(
        unreal.StaticMeshActor,
        location,
        unreal.Rotator(roll=0.0, pitch=0.0, yaw=yaw),
        False,
    )
    require(actor is not None, f"Failed to spawn beach module {row_name}/{column}")
    label = f"M01_ECC05_Beach_{row_name}_{column:02d}"
    actor.set_actor_label(label)
    actor.set_folder_path("M01/EnvironmentCompositionCorrection05/Beach")
    component = actor.static_mesh_component
    require(component is not None, f"Beach component missing: {label}")
    component.set_static_mesh(mesh)
    component.set_mobility(unreal.ComponentMobility.STATIC)
    component.set_editor_property("cast_shadow", True)
    require(component.get_num_materials() == 2, f"Beach mesh slot count changed: {component.get_num_materials()}")
    component.set_material(0, material)
    component.set_material(1, material)
    origin, extent = actor.get_actor_bounds(False)
    bottom = float(origin.z - extent.z)
    require(abs(bottom - target_bottom) <= 1.0, f"Beach grounding gap exceeded 1 cm: {label} -> {bottom - target_bottom}")
    return {
        "label": label,
        "row": row_name,
        "column": column,
        "yaw_degrees": yaw,
        "location_cm": vector(actor.get_actor_location()),
        "bounds_origin_cm": vector(origin),
        "bounds_extent_cm": vector(extent),
        "bounds_min_z_cm": bottom,
        "target_bottom_cm": target_bottom,
        "material_slots": [object_path(component.get_material(slot)) for slot in range(2)],
    }


result: dict[str, object] = {
    "schema": "skyguard.m01-photoreal-foundation.environment-composition-correction05.authoring.v1",
    "classification": "FAILED_WITH_EVIDENCE",
    "input_asset": INPUT_ASSET,
    "output_asset": OUTPUT_ASSET,
    "input_sha256_before": None,
    "input_sha256_after": None,
    "output_sha256": None,
    "actor_count_before": None,
    "actor_count_after": None,
    "removed_terrain": [],
    "beach_modules": [],
    "road_corrections": [],
    "building_variation": [],
    "water": {},
    "lighting": {},
    "quality_metrics": {},
    "errors": [],
}

try:
    require(INPUT_FILE.is_file(), "Accepted GroundLightingCorrection04Recovery01 map is missing")
    require(INPUT_FILE.stat().st_size == EXPECTED_INPUT_BYTES, "Accepted input-map byte count changed")
    result["input_sha256_before"] = sha256(INPUT_FILE)
    require(result["input_sha256_before"] == EXPECTED_INPUT_SHA256, "Accepted input-map hash changed")
    require(not OUTPUT_FILE.exists(), f"Fresh output map exists: {OUTPUT_FILE}")
    require(not unreal.EditorAssetLibrary.does_asset_exist(OUTPUT_ASSET), f"Fresh output asset exists: {OUTPUT_ASSET}")

    beach_mesh = load_required(BEACH_MESH_PATH, unreal.StaticMesh)
    sand_material = load_required(SAND_MATERIAL_PATH, unreal.MaterialInterface)
    ocean_material = load_required(OCEAN_MATERIAL_PATH, unreal.MaterialInterface)
    far_water_material = load_required(FAR_WATER_MATERIAL_PATH, unreal.MaterialInterface)
    ocean_waves = unreal.load_asset(OCEAN_WAVES_PATH)
    require(ocean_waves is not None, f"Ocean waves unavailable: {OCEAN_WAVES_PATH}")

    beach_bounds = beach_mesh.get_bounds()
    require(abs(float(beach_bounds.box_extent.x) - 2400.0) <= 1.0, "Beach mesh X extent changed")
    require(abs(float(beach_bounds.box_extent.y) - 1000.0) <= 1.0, "Beach mesh Y extent changed")

    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    actors_api = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    require(levels is not None and actors_api is not None, "Required editor subsystems unavailable")
    require(levels.new_level_from_template(OUTPUT_ASSET, INPUT_ASSET), "Failed to clone accepted input map")

    actors = list(actors_api.get_all_level_actors())
    result["actor_count_before"] = len(actors)
    require(len(actors) == EXPECTED_ACTOR_COUNT, f"Expected {EXPECTED_ACTOR_COUNT} actors; found {len(actors)}")

    terrain_actors = sorted(
        (actor for actor in actors if TERRAIN_PATTERN.match(actor.get_actor_label())),
        key=lambda actor: actor.get_actor_label(),
    )
    require(len(terrain_actors) == EXPECTED_REMOVED_TERRAIN, f"Expected four UV-less terrain slabs; found {len(terrain_actors)}")
    for actor in terrain_actors:
        component = static_mesh_component(actor)
        origin, extent = actor.get_actor_bounds(False)
        record = {
            "label": actor.get_actor_label(),
            "mesh": object_path(component.get_editor_property("static_mesh")),
            "bounds_origin_cm": vector(origin),
            "bounds_extent_cm": vector(extent),
        }
        require(actors_api.destroy_actor(actor), f"Failed to remove UV-less terrain slab: {actor.get_actor_label()}")
        result["removed_terrain"].append(record)

    for row_index, (row_name, center_y, target_bottom) in enumerate(BEACH_ROWS):
        for column, center_x in enumerate(BEACH_X_CENTERS):
            result["beach_modules"].append(
                spawn_beach_module(actors_api, beach_mesh, sand_material, row_name, row_index, column, center_x, center_y, target_bottom)
            )
    require(len(result["beach_modules"]) == EXPECTED_BEACH_MODULES, "Beach module count changed")

    current = list(actors_api.get_all_level_actors())
    cross_streets = sorted(
        (actor for actor in current if CROSS_STREET_PATTERN.match(actor.get_actor_label())),
        key=lambda actor: actor.get_actor_label(),
    )
    require(len(cross_streets) == EXPECTED_CROSS_STREETS, f"Expected fifteen cross streets; found {len(cross_streets)}")
    for actor in cross_streets:
        before = actor_transform(actor)
        require(all(abs(value - 1.0) <= 0.001 for value in before["scale"]), f"Cross-street scale authority changed: {actor.get_actor_label()}")
        before_origin, before_extent = actor.get_actor_bounds(False)
        before_min_z = float(before_origin.z - before_extent.z)
        actor.set_actor_scale3d(unreal.Vector(1.0, 1.0, TARGET_ROAD_Z_SCALE))
        after = actor_transform(actor)
        after_origin, after_extent = actor.get_actor_bounds(False)
        after_min_z = float(after_origin.z - after_extent.z)
        require(abs(after["scale"][2] - TARGET_ROAD_Z_SCALE) <= 0.001, f"Cross-street Z scale failed: {actor.get_actor_label()}")
        require(float(after_extent.z) <= 3.0, f"Cross-street remains excessively thick: {actor.get_actor_label()}")
        require(abs(after_min_z - before_min_z) <= 0.25, f"Cross-street grounded pivot moved: {actor.get_actor_label()}")
        result["road_corrections"].append(
            {
                "label": actor.get_actor_label(),
                "before": before,
                "after": after,
                "before_extent_z_cm": float(before_extent.z),
                "after_extent_z_cm": float(after_extent.z),
                "before_min_z_cm": before_min_z,
                "after_min_z_cm": after_min_z,
            }
        )

    groups: dict[str, dict[str, object]] = {}
    for actor in list(actors_api.get_all_level_actors()):
        match = BUILDING_PATTERN.match(actor.get_actor_label())
        if match:
            groups.setdefault(match.group("instance"), {})[match.group("group")] = actor
    require(sum(len(members) for members in groups.values()) == EXPECTED_BUILDING_GROUPS, "Building group actor count changed")
    require(len(groups) == EXPECTED_BUILDINGS, f"Expected twenty-seven building instances; found {len(groups)}")
    for instance in sorted(groups):
        members = groups[instance]
        require(set(members) == {"DETAILS", "GLAZING", "STRUCTURAL"}, f"Building group incomplete: {instance}")
        match = BUILDING_PATTERN.match(members["STRUCTURAL"].get_actor_label())
        require(match is not None, f"Failed to parse building instance: {instance}")
        row = int(match.group("row"))
        column = int(match.group("column"))
        require(0 <= row < 3 and 0 <= column < 9, f"Unexpected building grid index: {instance}")
        authority = actor_transform(members["STRUCTURAL"])
        for member in members.values():
            require(same_transform(actor_transform(member), authority), f"Building group transform mismatch before correction: {instance}")
        variant_index = (column + row * 3) % 9
        target_location = unreal.Vector(
            authority["location_cm"][0] + X_OFFSETS[variant_index],
            authority["location_cm"][1] + Y_OFFSETS[row][column],
            authority["location_cm"][2],
        )
        target_rotation = unreal.Rotator(
            roll=authority["rotation_degrees"][2],
            pitch=authority["rotation_degrees"][0],
            yaw=authority["rotation_degrees"][1] + YAW_OFFSETS[variant_index],
        )
        target_scale = unreal.Vector(1.0, 1.0, Z_SCALES[variant_index])
        for member in members.values():
            member.set_actor_location(target_location, False, True)
            member.set_actor_rotation(target_rotation, False)
            member.set_actor_scale3d(target_scale)
        corrected = actor_transform(members["STRUCTURAL"])
        for member in members.values():
            require(same_transform(actor_transform(member), corrected), f"Building group transform mismatch after correction: {instance}")
        result["building_variation"].append({"instance": instance, "before": authority, "after": corrected})

    current = list(actors_api.get_all_level_actors())
    ocean = find_exact(current, "M01_A01_WaterBodyOcean")
    water_component = ocean.get_water_body_component()
    require(water_component is not None, "WaterBodyOceanComponent unavailable")
    near_before = object_path(water_component.get_water_material())
    require(near_before == EXPECTED_PREVIOUS_OCEAN_MATERIAL, f"Near-water authority changed: {near_before}")
    water_component.set_water_material(ocean_material)
    near_after = object_path(water_component.get_water_material())
    require(near_after == object_path(ocean_material), "Near-water material correction failed")
    waves_before_value = ocean.get_editor_property("water_waves")
    waves_before = object_path(waves_before_value) if waves_before_value is not None else None
    ocean.set_water_waves(ocean_waves)
    waves_after = object_path(ocean.get_editor_property("water_waves"))
    require(waves_after == object_path(ocean_waves), "Ocean wave binding failed")

    water_zone = find_exact(current, "M01_A01_WaterZone")
    water_mesh_class = unreal.load_class(None, "/Script/Water.WaterMeshComponent")
    require(water_mesh_class is not None, "WaterMeshComponent class unavailable")
    water_mesh = water_zone.get_component_by_class(water_mesh_class)
    require(water_mesh is not None, "WaterMeshComponent unavailable")
    far_before = object_path(water_mesh.get_editor_property("far_distance_material"))
    require(far_before == EXPECTED_PREVIOUS_FAR_MATERIAL, f"Far-water authority changed: {far_before}")
    far_extent_before = float(water_mesh.get_editor_property("far_distance_mesh_extent"))
    water_mesh.set_editor_property("far_distance_material", far_water_material)
    far_after = object_path(water_mesh.get_editor_property("far_distance_material"))
    require(far_after == object_path(far_water_material), "Far-water material correction failed")
    require(abs(float(water_mesh.get_editor_property("far_distance_mesh_extent")) - far_extent_before) <= 0.1, "Far-water extent changed")
    result["water"] = {
        "near_material_before": near_before,
        "near_material_after": near_after,
        "far_material_before": far_before,
        "far_material_after": far_after,
        "waves_before": waves_before,
        "waves_after": waves_after,
        "far_extent_cm": far_extent_before,
    }

    sky = find_exact(current, "M01_RS01_SkyLight")
    sky_component = sky.get_component_by_class(unreal.SkyLightComponent)
    require(sky_component is not None, "SkyLightComponent unavailable")
    post = find_exact(current, "M01_RS01_PostProcess")
    settings = post.get_editor_property("settings")
    lighting_before = {
        "skylight_intensity": float(sky_component.get_editor_property("intensity")),
        "lower_hemisphere_color": rgba(sky_component.get_editor_property("lower_hemisphere_color")),
        "auto_exposure_bias": float(settings.get_editor_property("auto_exposure_bias")),
        "film_toe": float(settings.get_editor_property("film_toe")),
    }
    require(abs(lighting_before["skylight_intensity"] - EXPECTED_PREVIOUS_SKYLIGHT) <= 0.001, "Skylight authority changed")
    require(abs(lighting_before["auto_exposure_bias"] - EXPECTED_PREVIOUS_EXPOSURE) <= 0.001, "Exposure authority changed")
    require(abs(lighting_before["film_toe"] - EXPECTED_PREVIOUS_FILM_TOE) <= 0.001, "Film-toe authority changed")
    sky_component.set_editor_property("intensity", TARGET_SKYLIGHT)
    sky_component.set_editor_property("lower_hemisphere_is_black", False)
    sky_component.set_editor_property("lower_hemisphere_color", unreal.LinearColor(*TARGET_LOWER_HEMISPHERE))
    settings.set_editor_property("override_auto_exposure_bias", True)
    settings.set_editor_property("auto_exposure_bias", TARGET_EXPOSURE)
    settings.set_editor_property("override_film_toe", True)
    settings.set_editor_property("film_toe", TARGET_FILM_TOE)
    post.set_editor_property("settings", settings)
    checked = post.get_editor_property("settings")
    result["lighting"] = {
        "before": lighting_before,
        "after": {
            "skylight_intensity": float(sky_component.get_editor_property("intensity")),
            "lower_hemisphere_color": rgba(sky_component.get_editor_property("lower_hemisphere_color")),
            "auto_exposure_bias": float(checked.get_editor_property("auto_exposure_bias")),
            "film_toe": float(checked.get_editor_property("film_toe")),
        },
    }

    actors_after = list(actors_api.get_all_level_actors())
    result["actor_count_after"] = len(actors_after)
    require(len(actors_after) == EXPECTED_FINAL_ACTOR_COUNT, f"Expected {EXPECTED_FINAL_ACTOR_COUNT} final actors; found {len(actors_after)}")
    require(not any(TERRAIN_PATTERN.match(actor.get_actor_label()) for actor in actors_after), "UV-less terrain slab remains")
    require(len([actor for actor in actors_after if actor.get_actor_label().startswith("M01_ECC05_Beach_")]) == EXPECTED_BEACH_MODULES, "Beach label count changed")
    require(len([actor for actor in actors_after if actor.get_actor_label().startswith("M01_RS01_Tree_")]) == 0, "Rejected proxy tree returned")

    require(levels.save_current_level(), "Failed to save EnvironmentCompositionCorrection05")
    require(OUTPUT_FILE.is_file(), "EnvironmentCompositionCorrection05 map file was not created")
    result["input_sha256_after"] = sha256(INPUT_FILE)
    require(result["input_sha256_after"] == EXPECTED_INPUT_SHA256, "Accepted input map changed")
    result["output_sha256"] = sha256(OUTPUT_FILE)
    result["quality_metrics"] = {
        "actor_count": len(actors_after),
        "uv_less_terrain_removed": len(result["removed_terrain"]),
        "uv_mapped_beach_modules": len(result["beach_modules"]),
        "grounded_cross_streets": len(result["road_corrections"]),
        "varied_building_instances": len(result["building_variation"]),
        "matched_water_material_pair": 1,
        "ocean_wave_bindings": 1,
        "proxy_tree_count": 0,
    }
    require(
        result["quality_metrics"]
        == {
            "actor_count": 140,
            "uv_less_terrain_removed": 4,
            "uv_mapped_beach_modules": 24,
            "grounded_cross_streets": 15,
            "varied_building_instances": 27,
            "matched_water_material_pair": 1,
            "ocean_wave_bindings": 1,
            "proxy_tree_count": 0,
        },
        "Quality metric contract failed",
    )
    result["classification"] = "PASSED_M01_PHOTOREAL_FOUNDATION_ENVIRONMENT_COMPOSITION_CORRECTION05_AUTOMATIC"
except Exception as exc:
    result["errors"].append(
        {
            "type": type(exc).__name__,
            "message": str(exc),
            "traceback": traceback.format_exc(),
        }
    )
finally:
    write_json_atomic(RECEIPT, result)

if result["classification"].startswith("PASSED_"):
    unreal.SystemLibrary.quit_editor()
else:
    raise RuntimeError(result["errors"][-1]["message"] if result["errors"] else "EnvironmentCompositionCorrection05 failed")
