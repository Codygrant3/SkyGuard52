from __future__ import annotations

import hashlib
import json
import os
import traceback
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
ISOLATED = Path(r"D:\SG52T08_ENV01")
MAP_ASSET = "/Game/M01/Lvl_M01_PhotorealFoundation_NonVegetation01"
MAP_FILE = ISOLATED / "Content/M01/Lvl_M01_PhotorealFoundation_NonVegetation01.umap"
EXPECTED_MAP_BYTES = 736476
EXPECTED_MAP_SHA256 = "618a260a905680cf5b17c1ac82a114a69f93f947334f45701cd1a8daa2b1f2a1"
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_PHOTOREAL_FOUNDATION_WAVE01_LIGHTING_ROADS_WATERLINE02_PROPERTY_PROBE/attempt_01"
RECEIPT = ATTEMPT / "property_probe_receipt.json"

CROSS_STREET_PREFIX = "M01_RS01_CrossStreet_"
LIGHT_LABELS = (
    "M01_RS01_Sun",
    "M01_PR01_FillSun",
    "M01_RS01_SkyLight",
    "M01_RS01_PostProcess",
    "M01_RS01_HeightFog",
)
WATER_LABELS = (
    "M01_A01_WaterBodyOcean",
    "M01_A01_WaterZone",
    "M01_A01_Landscape_Production_WaterBrushManager",
)
BOUND_LABELS = (
    "M01_A01_Landscape_Production",
    "M01_VEK02_District_00_TERRAIN",
    "M01_VEK02_District_01_TERRAIN",
    "M01_VEK02_District_02_TERRAIN",
    "M01_VEK02_District_03_TERRAIN",
)

CANDIDATE_MATERIALS = (
    "/Game/Skyguard/Meshes/Mission01/Wave1Refinement/m01_wave1_aaa_refinement/Materials/M_M01_Asphalt",
    "/Game/Skyguard/Meshes/Mission01/Wave1Refinement/m01_wave1_aaa_refinement/Materials/M_M01_ConcreteDark",
    "/Game/Skyguard/Meshes/Mission01/Wave1Refinement/m01_wave1_aaa_refinement/Materials/M_M01_ConcreteLight",
    "/Game/Skyguard/Meshes/Mission01/Wave1Refinement/m01_wave1_aaa_refinement/Materials/M_M01_RoadMark",
    "/Game/M01/EnvKit02/M01_COASTAL_DISTRICT_A/Materials/M_ENV_Asphalt_2K",
    "/Game/M01/EnvKit02/M01_COASTAL_DISTRICT_A/Materials/M_ENV_Concrete_Pavers_2K",
    "/Game/M01/EnvKit02/M01_COASTAL_DISTRICT_A/Materials/M_ENV_Sand_Coast_2K",
    "/Game/Skyguard/Materials/M_Road",
    "/Game/Skyguard/Materials/M_Asphalt",
    "/Game/Skyguard/Materials/M_L5_WetAsphalt",
    "/Game/Skyguard/Materials/M_Beach",
    "/Game/Skyguard/Materials/M_WetSand",
    "/Game/Skyguard/Materials/M_Ocean",
    "/Game/Skyguard/Materials/M_OceanDeep",
)

LIGHT_PROPERTIES = (
    "intensity",
    "light_color",
    "cast_shadows",
    "cast_static_shadows",
    "cast_dynamic_shadows",
    "indirect_lighting_intensity",
    "volumetric_scattering_intensity",
    "use_temperature",
    "temperature",
    "source_angle",
    "source_soft_angle",
    "atmosphere_sun_light",
    "atmosphere_sun_light_index",
    "contact_shadow_length",
)
SKYLIGHT_PROPERTIES = (
    "intensity_scale",
    "source_type",
    "real_time_capture",
    "cubemap",
    "lower_hemisphere_is_solid_color",
    "lower_hemisphere_color",
    "indirect_lighting_intensity",
    "volumetric_scattering_intensity",
    "cast_shadows",
)
POST_PROCESS_PROPERTIES = (
    "auto_exposure_method",
    "auto_exposure_bias",
    "auto_exposure_min_brightness",
    "auto_exposure_max_brightness",
    "auto_exposure_low_percent",
    "auto_exposure_high_percent",
    "auto_exposure_speed_up",
    "auto_exposure_speed_down",
    "dynamic_global_illumination_method",
    "reflection_method",
    "lumen_reflection_quality",
    "color_saturation",
    "color_contrast",
    "color_gamma",
    "color_gain",
    "color_offset",
    "film_slope",
    "film_toe",
    "film_shoulder",
    "film_black_clip",
    "film_white_clip",
    "ambient_cubemap_intensity",
)
WATER_PROPERTIES = (
    "water_material",
    "underwater_post_process_material",
    "water_info_material",
    "physical_material",
    "overlap_material_priority",
    "shape_dilation",
    "collision_extents",
    "navigation_collision_offset",
    "target_wave_mask_depth",
    "max_wave_height_offset",
    "zone_extent",
    "render_target_resolution",
    "capture_z_offset",
    "local_only_tessellation",
    "tessellation_extent",
    "water_heightmap_settings",
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
    for method in ("get_path_name", "get_name"):
        try:
            return str(getattr(value, method)())
        except Exception:
            pass
    return str(value)


def normalize(value: object):
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
    path = object_path(value)
    return path


def safe_property(value: object, name: str) -> dict[str, object]:
    try:
        return {"available": True, "value": normalize(value.get_editor_property(name))}
    except Exception as exc:
        return {"available": False, "error": f"{type(exc).__name__}: {exc}"}


def property_set(value: object, names: tuple[str, ...]) -> dict[str, object]:
    return {name: safe_property(value, name) for name in names}


def bounds_record(actor: object) -> dict[str, object]:
    origin, extent = actor.get_actor_bounds(False)
    return {
        "origin_cm": normalize(origin),
        "extent_cm": normalize(extent),
        "minimum_cm": [float(origin.x - extent.x), float(origin.y - extent.y), float(origin.z - extent.z)],
        "maximum_cm": [float(origin.x + extent.x), float(origin.y + extent.y), float(origin.z + extent.z)],
    }


def actor_base(actor: object) -> dict[str, object]:
    location = actor.get_actor_location()
    rotation = actor.get_actor_rotation()
    return {
        "label": actor.get_actor_label(),
        "class": actor.get_class().get_path_name(),
        "location_cm": normalize(location),
        "rotation_degrees": [float(rotation.pitch), float(rotation.yaw), float(rotation.roll)],
        "scale": normalize(actor.get_actor_scale3d()),
        "bounds": bounds_record(actor),
    }


def components(actor: object) -> list[object]:
    values: list[object] = []
    try:
        values = list(actor.get_components_by_class(unreal.ActorComponent))
    except Exception:
        root = actor.get_root_component()
        if root is not None:
            values = [root]
    return values


def component_record(component: object, property_names: tuple[str, ...]) -> dict[str, object]:
    return {
        "name": object_path(component),
        "class": component.get_class().get_path_name(),
        "properties": property_set(component, property_names),
    }


def cross_street_record(actor: object) -> dict[str, object]:
    record = actor_base(actor)
    component = actor.get_component_by_class(unreal.StaticMeshComponent)
    require(component is not None, f"StaticMeshComponent missing: {actor.get_actor_label()}")
    mesh = component.get_editor_property("static_mesh")
    require(mesh is not None, f"Static mesh missing: {actor.get_actor_label()}")
    slots = list(mesh.get_editor_property("static_materials"))
    record["static_mesh"] = object_path(mesh)
    record["material_slot_names"] = [str(slot.get_editor_property("material_slot_name")) for slot in slots]
    record["materials"] = [object_path(component.get_material(index)) for index in range(component.get_num_materials())]
    record["component_mobility"] = normalize(component.get_editor_property("mobility"))
    return record


def asset_record(path: str) -> dict[str, object]:
    exists = bool(unreal.EditorAssetLibrary.does_asset_exist(path))
    asset = unreal.EditorAssetLibrary.load_asset(path) if exists else None
    return {
        "asset_path": path,
        "exists": exists,
        "loaded": asset is not None,
        "class": asset.get_class().get_path_name() if asset is not None else None,
    }


result: dict[str, object] = {
    "schema": "skyguard.m01-photoreal-foundation-wave01.lighting-roads-waterline02-property-probe.v1",
    "classification": "FAILED_WITH_EVIDENCE",
    "read_only": True,
    "world_saved": False,
    "map_asset": MAP_ASSET,
    "map_sha256_before": None,
    "map_sha256_after": None,
    "map_unchanged": False,
    "actor_count": 0,
    "cross_streets": [],
    "lighting": {},
    "post_process": {},
    "water": {},
    "reference_bounds": {},
    "candidate_materials": [],
    "errors": [],
}

try:
    require(MAP_FILE.is_file(), "NonVegetation01 map is missing")
    require(MAP_FILE.stat().st_size == EXPECTED_MAP_BYTES, "NonVegetation01 map byte count changed")
    result["map_sha256_before"] = sha256(MAP_FILE)
    require(result["map_sha256_before"] == EXPECTED_MAP_SHA256, "NonVegetation01 map hash changed")

    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    actors_api = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    require(levels is not None and actors_api is not None, "Required editor subsystems unavailable")
    require(bool(levels.load_level(MAP_ASSET)), "NonVegetation01 map failed to load")
    actors = list(actors_api.get_all_level_actors())
    result["actor_count"] = len(actors)
    require(len(actors) == 120, f"Expected 120 actors; found {len(actors)}")
    by_label = {actor.get_actor_label(): actor for actor in actors}

    cross_streets = sorted(
        (actor for actor in actors if actor.get_actor_label().startswith(CROSS_STREET_PREFIX)),
        key=lambda actor: actor.get_actor_label(),
    )
    require(len(cross_streets) == 15, f"Expected 15 CrossStreet actors; found {len(cross_streets)}")
    result["cross_streets"] = [cross_street_record(actor) for actor in cross_streets]
    require(
        all(len(record["materials"]) == 3 for record in result["cross_streets"]),
        "A CrossStreet material layout changed",
    )

    for label in LIGHT_LABELS:
        actor = by_label.get(label)
        require(actor is not None, f"Required lighting actor missing: {label}")
        record = actor_base(actor)
        actor_components = components(actor)
        record["components"] = []
        for component in actor_components:
            class_name = component.get_class().get_name()
            if "SkyLight" in class_name:
                record["components"].append(component_record(component, SKYLIGHT_PROPERTIES))
            elif "Light" in class_name:
                record["components"].append(component_record(component, LIGHT_PROPERTIES))
            elif "Fog" in class_name:
                record["components"].append(
                    component_record(
                        component,
                        (
                            "fog_density",
                            "fog_height_falloff",
                            "fog_inscattering_color",
                            "volumetric_fog",
                            "volumetric_fog_scattering_distribution",
                            "volumetric_fog_albedo",
                            "volumetric_fog_emissive",
                            "volumetric_fog_extinction_scale",
                            "volumetric_fog_view_distance",
                        ),
                    )
                )
        if label == "M01_RS01_PostProcess":
            record["volume_properties"] = property_set(actor, ("unbound", "blend_weight", "priority", "blend_radius"))
            settings = actor.get_editor_property("settings")
            record["settings"] = property_set(settings, POST_PROCESS_PROPERTIES)
        result["lighting"][label] = record

    for label in WATER_LABELS:
        actor = by_label.get(label)
        require(actor is not None, f"Required water actor missing: {label}")
        record = actor_base(actor)
        record["actor_properties"] = property_set(actor, WATER_PROPERTIES)
        record["components"] = [component_record(component, WATER_PROPERTIES) for component in components(actor)]
        result["water"][label] = record

    for label in BOUND_LABELS:
        actor = by_label.get(label)
        require(actor is not None, f"Required bounds actor missing: {label}")
        result["reference_bounds"][label] = actor_base(actor)

    result["candidate_materials"] = [asset_record(path) for path in CANDIDATE_MATERIALS]
    require(all(record["loaded"] for record in result["candidate_materials"]), "A candidate material failed to load")

    first = result["cross_streets"][0]
    require(first["material_slot_names"] == ["M_M01_Asphalt", "M_M01_ConcreteLight", "M_M01_RoadMark"], "CrossStreet slot authority changed")
    require("M_M01_ConcreteLight" in str(first["materials"][1]), "CrossStreet white slab source is not slot 1")

    result["map_sha256_after"] = sha256(MAP_FILE)
    result["map_unchanged"] = result["map_sha256_after"] == result["map_sha256_before"]
    require(result["map_unchanged"], "Read-only property probe changed NonVegetation01")
    result["classification"] = "PASSED_READY_FOR_LIGHTING_ROADS_WATERLINE02_AUTHORING_DESIGN"
except Exception as exc:
    result["errors"].append(f"{type(exc).__name__}: {exc}")
    result["errors"].append(traceback.format_exc())
finally:
    if result["map_sha256_after"] is None and MAP_FILE.is_file():
        result["map_sha256_after"] = sha256(MAP_FILE)
        result["map_unchanged"] = result["map_sha256_after"] == result["map_sha256_before"]
    write_json_atomic(RECEIPT, result)
    print("SKYGUARD_M01_LIGHTING_ROADS_WATERLINE02_PROPERTY_PROBE=" + str(result["classification"]))

if result["classification"] != "PASSED_READY_FOR_LIGHTING_ROADS_WATERLINE02_AUTHORING_DESIGN":
    raise RuntimeError(str(result["errors"][0] if result["errors"] else "property probe failed"))
