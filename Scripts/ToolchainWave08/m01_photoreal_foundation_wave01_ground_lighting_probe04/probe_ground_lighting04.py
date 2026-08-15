from __future__ import annotations

import hashlib
import json
import os
import traceback
from pathlib import Path
from typing import Any

import unreal


ROOT = Path(r"D:\Skyguard52")
ISOLATED = Path(r"D:\SG52T08_ENV01")
MAP_ASSET = "/Game/M01/Lvl_M01_PhotorealFoundation_StructuralCleanup03"
MAP_FILE = ISOLATED / "Content/M01/Lvl_M01_PhotorealFoundation_StructuralCleanup03.umap"
EXPECTED_MAP_BYTES = 738931
EXPECTED_MAP_SHA256 = "142222c49c2ac232c301d14717a61c7a49c104df94ffeaa0e8ad21194184e08d"
EXPECTED_ACTOR_COUNT = 120
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_PHOTOREAL_FOUNDATION_WAVE01_GROUND_LIGHTING_PROBE04/attempt_01"
RECEIPT = ATTEMPT / "ground_lighting_probe_receipt.json"

LANDSCAPE_LABEL = "M01_A01_Landscape_Production"
TERRAIN_LABELS = tuple(f"M01_VEK02_District_{index:02d}_TERRAIN" for index in range(4))
CROSS_STREET_LABELS = tuple(
    f"M01_RS01_CrossStreet_{district:02d}_{street:02d}"
    for district in range(5)
    for street in range(3)
)
LIGHT_LABELS = (
    "M01_RS01_Sun",
    "M01_PR01_FillSun",
    "M01_RS01_SkyLight",
    "M01_RS01_PostProcess",
)
WATER_LABELS = ("M01_A01_WaterBodyOcean", "M01_A01_WaterZone")
REPRESENTATIVE_BUILDING_LABELS = (
    "M01_VEK02_City_R00_C00_ApartmentA_STRUCTURAL",
    "M01_VEK02_City_R00_C00_ApartmentA_GLAZING",
    "M01_VEK02_City_R00_C00_ApartmentA_DETAILS",
    "M01_VEK02_City_R00_C01_MidriseB_STRUCTURAL",
    "M01_VEK02_City_R00_C02_CornerC_STRUCTURAL",
)
MATERIAL_ASSETS = (
    "/Game/Skyguard/Materials/M_Terrain",
    "/Game/M01/EnvKit02/M01_COASTAL_DISTRICT_A/Materials/M_ENV_Concrete_Pavers_2K",
    "/Game/M01/EnvKit02/M01_COASTAL_DISTRICT_A/Materials/M_ENV_Sand_Coast_2K",
    "/Game/M01/EnvKit02/M01_COASTAL_DISTRICT_A/Materials/M_ENV_Asphalt_2K",
    "/Game/Skyguard/Meshes/Mission01/Wave1Refinement/m01_wave1_aaa_refinement/Materials/M_M01_ConcreteDark",
    "/Game/Skyguard/Materials/M_Beach",
    "/Game/Skyguard/Materials/M_WetSand",
    "/Water/Materials/WaterSurface/Water_FarMesh",
    "/Game/Skyguard/Materials/Generated/M_L23_Ocean",
)


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


def normalize(value: object) -> object:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, (list, tuple)):
        return [normalize(item) for item in value]
    if isinstance(value, dict):
        return {str(key): normalize(item) for key, item in value.items()}
    if all(hasattr(value, key) for key in ("x", "y", "z")):
        return [float(value.x), float(value.y), float(value.z)]
    if all(hasattr(value, key) for key in ("r", "g", "b", "a")):
        return [float(value.r), float(value.g), float(value.b), float(value.a)]
    return object_path(value)


def safe_property(value: object, name: str) -> dict[str, object]:
    try:
        return {"available": True, "value": normalize(value.get_editor_property(name))}
    except Exception as exc:
        return {"available": False, "error": f"{type(exc).__name__}: {exc}"}


def bounds(actor: object) -> dict[str, list[float]]:
    origin, extent = actor.get_actor_bounds(False)
    return {
        "origin_cm": [float(origin.x), float(origin.y), float(origin.z)],
        "extent_cm": [float(extent.x), float(extent.y), float(extent.z)],
        "minimum_cm": [float(origin.x - extent.x), float(origin.y - extent.y), float(origin.z - extent.z)],
        "maximum_cm": [float(origin.x + extent.x), float(origin.y + extent.y), float(origin.z + extent.z)],
    }


def actor_base(actor: object) -> dict[str, object]:
    rotation = actor.get_actor_rotation()
    return {
        "label": actor.get_actor_label(),
        "class": actor.get_class().get_path_name(),
        "location_cm": normalize(actor.get_actor_location()),
        "rotation_degrees": [float(rotation.pitch), float(rotation.yaw), float(rotation.roll)],
        "scale": normalize(actor.get_actor_scale3d()),
        "bounds": bounds(actor),
    }


def texture_record(texture: object) -> dict[str, object] | None:
    if texture is None:
        return None
    record: dict[str, object] = {
        "path": object_path(texture),
        "class": texture.get_class().get_path_name(),
    }
    for name in ("srgb", "compression_settings", "lod_group", "never_stream", "virtual_texture_streaming"):
        record[name] = safe_property(texture, name)
    for name in ("blueprint_get_size_x", "blueprint_get_size_y"):
        try:
            record[name.removeprefix("blueprint_get_")] = int(getattr(texture, name)())
        except Exception as exc:
            record[name.removeprefix("blueprint_get_")] = {"error": f"{type(exc).__name__}: {exc}"}
    return record


def material_record(material: object) -> dict[str, object] | None:
    if material is None:
        return None
    record: dict[str, object] = {
        "path": object_path(material),
        "class": material.get_class().get_path_name(),
        "parent": safe_property(material, "parent"),
        "base_material": None,
        "scalar_parameters": {},
        "vector_parameters": {},
        "texture_parameters": {},
        "static_switch_parameters": {},
    }
    try:
        record["base_material"] = object_path(material.get_base_material())
    except Exception as exc:
        record["base_material"] = {"error": f"{type(exc).__name__}: {exc}"}
    library = unreal.MaterialEditingLibrary
    parameter_specs = (
        ("scalar_parameters", library.get_scalar_parameter_names, library.get_material_instance_scalar_parameter_value),
        ("vector_parameters", library.get_vector_parameter_names, library.get_material_instance_vector_parameter_value),
        ("texture_parameters", library.get_texture_parameter_names, library.get_material_instance_texture_parameter_value),
        ("static_switch_parameters", library.get_static_switch_parameter_names, library.get_material_instance_static_switch_parameter_value),
    )
    for output_key, name_getter, value_getter in parameter_specs:
        try:
            names = [str(name) for name in name_getter(material)]
        except Exception as exc:
            record[output_key] = {"error": f"{type(exc).__name__}: {exc}"}
            continue
        values: dict[str, object] = {}
        for name in names:
            try:
                value = value_getter(material, name)
                values[name] = texture_record(value) if output_key == "texture_parameters" else normalize(value)
            except Exception as exc:
                values[name] = {"error": f"{type(exc).__name__}: {exc}"}
        record[output_key] = values
    return record


def static_mesh_actor_record(actor: object) -> dict[str, object]:
    record = actor_base(actor)
    component = actor.get_component_by_class(unreal.StaticMeshComponent)
    require(component is not None, f"StaticMeshComponent missing: {actor.get_actor_label()}")
    mesh = component.get_editor_property("static_mesh")
    require(mesh is not None, f"Static mesh missing: {actor.get_actor_label()}")
    record["static_mesh"] = object_path(mesh)
    record["component_mobility"] = normalize(component.get_editor_property("mobility"))
    record["materials"] = [material_record(component.get_material(index)) for index in range(component.get_num_materials())]
    return record


def light_record(actor: object) -> dict[str, object]:
    record = actor_base(actor)
    component = actor.get_component_by_class(unreal.LightComponentBase)
    if component is not None:
        record["component"] = {
            name: safe_property(component, name)
            for name in (
                "intensity",
                "light_color",
                "cast_shadows",
                "indirect_lighting_intensity",
                "volumetric_scattering_intensity",
                "temperature",
                "use_temperature",
                "source_angle",
                "source_soft_angle",
            )
        }
    sky_component = actor.get_component_by_class(unreal.SkyLightComponent)
    if sky_component is not None:
        record["component"] = {
            name: safe_property(sky_component, name)
            for name in (
                "intensity",
                "real_time_capture",
                "lower_hemisphere_is_black",
                "lower_hemisphere_color",
                "cast_shadows",
                "indirect_lighting_intensity",
            )
        }
    if actor.get_actor_label() == "M01_RS01_PostProcess":
        settings = actor.get_editor_property("settings")
        record["settings"] = {
            name: safe_property(settings, name)
            for name in (
                "auto_exposure_method",
                "auto_exposure_bias",
                "film_slope",
                "film_toe",
                "film_shoulder",
                "film_black_clip",
                "film_white_clip",
                "color_saturation",
                "color_contrast",
                "color_gamma",
                "color_gain",
                "color_offset",
                "dynamic_global_illumination_method",
                "reflection_method",
            )
        }
    return record


def water_record(actor: object) -> dict[str, object]:
    record = actor_base(actor)
    record["actor_properties"] = {
        name: safe_property(actor, name)
        for name in ("zone_extent", "render_target_resolution", "capture_z_offset")
    }
    record["components"] = []
    for component in actor.get_components_by_class(unreal.ActorComponent):
        class_name = component.get_class().get_name()
        if "Water" not in class_name and "Ocean" not in class_name:
            continue
        item = {
            "class": component.get_class().get_path_name(),
            "path": object_path(component),
            "properties": {
                name: safe_property(component, name)
                for name in (
                    "water_material",
                    "far_distance_material",
                    "far_distance_mesh_extent",
                    "tile_size",
                    "extent_in_tiles",
                    "collision_extents",
                    "shape_dilation",
                    "target_wave_mask_depth",
                    "local_only_tessellation",
                    "tessellation_extent",
                )
            },
        }
        record["components"].append(item)
    return record


result: dict[str, Any] = {
    "schema": "skyguard.m01-photoreal-foundation.ground-lighting-probe04.v1",
    "classification": "FAILED_WITH_EVIDENCE",
    "read_only": True,
    "world_saved": False,
    "map_asset": MAP_ASSET,
    "map_sha256_before": None,
    "map_sha256_after": None,
    "map_unchanged": False,
    "actor_count": 0,
    "landscape": {},
    "district_terrain": [],
    "cross_streets": [],
    "representative_buildings": [],
    "lighting": {},
    "water": {},
    "materials": {},
    "camera_surface_analysis": {},
    "errors": [],
}

try:
    require(MAP_FILE.is_file(), "StructuralCleanup03 map is missing")
    require(MAP_FILE.stat().st_size == EXPECTED_MAP_BYTES, "StructuralCleanup03 map byte count changed")
    result["map_sha256_before"] = sha256(MAP_FILE)
    require(result["map_sha256_before"] == EXPECTED_MAP_SHA256, "StructuralCleanup03 map hash changed")

    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    actors_api = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    require(levels is not None and actors_api is not None, "Required editor subsystems unavailable")
    require(bool(levels.load_level(MAP_ASSET)), "StructuralCleanup03 map failed to load")
    actors = list(actors_api.get_all_level_actors())
    result["actor_count"] = len(actors)
    require(len(actors) == EXPECTED_ACTOR_COUNT, f"Expected {EXPECTED_ACTOR_COUNT} actors; found {len(actors)}")
    by_label = {actor.get_actor_label(): actor for actor in actors}

    landscape = by_label.get(LANDSCAPE_LABEL)
    require(landscape is not None, "Landscape actor is missing")
    result["landscape"] = actor_base(landscape)
    result["landscape"]["landscape_material"] = material_record(landscape.get_editor_property("landscape_material"))
    result["landscape"]["landscape_hole_material"] = material_record(landscape.get_editor_property("landscape_hole_material"))

    for label in TERRAIN_LABELS:
        actor = by_label.get(label)
        require(actor is not None, f"District terrain missing: {label}")
        result["district_terrain"].append(static_mesh_actor_record(actor))

    for label in CROSS_STREET_LABELS:
        actor = by_label.get(label)
        require(actor is not None, f"CrossStreet missing: {label}")
        result["cross_streets"].append(static_mesh_actor_record(actor))

    for label in REPRESENTATIVE_BUILDING_LABELS:
        actor = by_label.get(label)
        require(actor is not None, f"Representative building actor missing: {label}")
        result["representative_buildings"].append(static_mesh_actor_record(actor))

    for label in LIGHT_LABELS:
        actor = by_label.get(label)
        require(actor is not None, f"Lighting actor missing: {label}")
        result["lighting"][label] = light_record(actor)

    for label in WATER_LABELS:
        actor = by_label.get(label)
        require(actor is not None, f"Water actor missing: {label}")
        result["water"][label] = water_record(actor)

    for asset_path in MATERIAL_ASSETS:
        asset = unreal.EditorAssetLibrary.load_asset(asset_path)
        require(asset is not None, f"Material failed to load: {asset_path}")
        result["materials"][asset_path] = material_record(asset)

    landscape_bounds = result["landscape"]["bounds"]
    terrain_bounds = [item["bounds"] for item in result["district_terrain"]]
    result["camera_surface_analysis"] = {
        "rear_gunner_camera_y_cm": 3000.0,
        "rear_gunner_camera_z_cm": 1600.0,
        "view_direction": "+Y",
        "district_strip_y_range_cm": [
            min(item["minimum_cm"][1] for item in terrain_bounds),
            max(item["maximum_cm"][1] for item in terrain_bounds),
        ],
        "district_strip_z_range_cm": [
            min(item["minimum_cm"][2] for item in terrain_bounds),
            max(item["maximum_cm"][2] for item in terrain_bounds),
        ],
        "landscape_y_range_cm": [landscape_bounds["minimum_cm"][1], landscape_bounds["maximum_cm"][1]],
        "landscape_z_range_cm": [landscape_bounds["minimum_cm"][2], landscape_bounds["maximum_cm"][2]],
        "district_landscape_y_overlap_cm": max(
            0.0,
            min(max(item["maximum_cm"][1] for item in terrain_bounds), landscape_bounds["maximum_cm"][1])
            - max(min(item["minimum_cm"][1] for item in terrain_bounds), landscape_bounds["minimum_cm"][1]),
        ),
        "interpretation": "The near-camera district strip and the flat-color landscape are both visible along the rear-gunner +Y sightline; their overlap and material response determine the slab-like foreground.",
    }

    require(len(result["district_terrain"]) == 4, "District terrain count changed")
    require(len(result["cross_streets"]) == 15, "CrossStreet count changed")
    require(all("M_ENV_Concrete_Pavers_2K" in str(item["materials"][0]["path"]) for item in result["district_terrain"]), "District paver binding changed")
    require(all("M_ENV_Asphalt_2K" in str(item["materials"][0]["path"]) and "M_ENV_Asphalt_2K" in str(item["materials"][2]["path"]) for item in result["cross_streets"]), "CrossStreet correction changed")
    require("M_Terrain" in str(result["landscape"]["landscape_material"]["path"]), "Landscape material authority changed")

    result["map_sha256_after"] = sha256(MAP_FILE)
    result["map_unchanged"] = result["map_sha256_after"] == result["map_sha256_before"]
    require(result["map_unchanged"], "Read-only probe changed StructuralCleanup03")
    result["classification"] = "PASSED_READY_FOR_EVIDENCE_BACKED_GROUND_LIGHTING_CORRECTION04"
except Exception as exc:
    result["errors"].append({"type": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()})
finally:
    if result["map_sha256_after"] is None and MAP_FILE.is_file():
        result["map_sha256_after"] = sha256(MAP_FILE)
        result["map_unchanged"] = result["map_sha256_after"] == result["map_sha256_before"]
    write_json_atomic(RECEIPT, result)

print("SKYGUARD_M01_GROUND_LIGHTING_PROBE04=" + str(result["classification"]))
if result["classification"] != "PASSED_READY_FOR_EVIDENCE_BACKED_GROUND_LIGHTING_CORRECTION04":
    raise RuntimeError(result["errors"][-1]["message"] if result["errors"] else "Ground/lighting probe failed")
