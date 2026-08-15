"""Read-only UE 5.8 probe for Stage02 Mission 1 visual root causes.

This script never saves a world or asset. It records enough live editor evidence
to correct vegetation orientation/grounding, broad white surfaces, facade
lighting, and camera-facing composition without guessing.
"""

from __future__ import annotations

import hashlib
import json
import os
import traceback
from pathlib import Path
from typing import Any

import unreal


ROOT = Path(r"D:\Skyguard52")
PROJECT_ROOT = Path(r"D:\SG52T08_ENV01")
MAP_ASSET = "/Game/M01/Lvl_M01_PolyHavenVegetationStaging02"
MAP_FILE = PROJECT_ROOT / "Content/M01/Lvl_M01_PolyHavenVegetationStaging02.umap"
EXPECTED_MAP_BYTES = 906770
EXPECTED_MAP_SHA256 = "183a05414ed5f3c4ccfe70e9b92cbce4bfb60812f5662a0c539a0c42385cab5e"
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_VISIBLE_ENVIRONMENT_STAGE03_DIAGNOSTIC01/attempt_01"
RECEIPT = ATTEMPT / "stage02_visual_root_cause_probe.json"

VEGETATION_PREFIX = "M01_PHV02_"
KEY_LABELS = {
    "M01_A01_Landscape_Production",
    "M01_A01_WaterBodyOcean",
    "M01_A01_WaterZone",
    "M01_RS01_Sun",
    "M01_PR01_FillSun",
    "M01_RS01_SkyLight",
    "M01_RS01_PostProcess",
    "M01_RS01_HeightFog",
}
REPRESENTATIVE_BUILDING_TOKENS = (
    "City_R00_C02_MidriseB_STRUCTURAL",
    "City_R01_C01_ApartmentA_STRUCTURAL",
    "City_R01_C02_CornerC_STRUCTURAL",
    "City_R00_C02_MidriseB_GLAZING",
    "City_R01_C01_ApartmentA_GLAZING",
    "City_R01_C02_CornerC_GLAZING",
)
SURFACE_SUFFIXES = ("_TERRAIN", "_HARDSCAPE", "_DETAILS", "_CONTACT")


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


def bounds_record(actor: object) -> dict[str, list[float]]:
    origin, extent = actor.get_actor_bounds(False)
    return {
        "origin_cm": [float(origin.x), float(origin.y), float(origin.z)],
        "extent_cm": [float(extent.x), float(extent.y), float(extent.z)],
        "minimum_cm": [float(origin.x - extent.x), float(origin.y - extent.y), float(origin.z - extent.z)],
        "maximum_cm": [float(origin.x + extent.x), float(origin.y + extent.y), float(origin.z + extent.z)],
    }


def actor_base(actor: object) -> dict[str, object]:
    rotation = actor.get_actor_rotation()
    row: dict[str, object] = {
        "label": actor.get_actor_label(),
        "class": actor.get_class().get_path_name(),
        "location_cm": normalize(actor.get_actor_location()),
        "rotation_degrees": {
            "pitch": float(rotation.pitch),
            "yaw": float(rotation.yaw),
            "roll": float(rotation.roll),
        },
        "scale": normalize(actor.get_actor_scale3d()),
        "bounds": bounds_record(actor),
    }
    for method_name in ("is_hidden_ed", "is_temporarily_hidden_in_editor"):
        try:
            row[method_name] = bool(getattr(actor, method_name)())
        except Exception as exc:
            row[method_name] = {"error": f"{type(exc).__name__}: {exc}"}
    return row


def texture_record(texture: object) -> dict[str, object] | None:
    if texture is None:
        return None
    return {
        "path": object_path(texture),
        "class": texture.get_class().get_path_name(),
        "srgb": safe_property(texture, "srgb"),
        "compression_settings": safe_property(texture, "compression_settings"),
    }


def material_record(material: object) -> dict[str, object] | None:
    if material is None:
        return None
    row: dict[str, object] = {
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
        row["base_material"] = object_path(material.get_base_material())
    except Exception as exc:
        row["base_material"] = {"error": f"{type(exc).__name__}: {exc}"}
    library = unreal.MaterialEditingLibrary
    specs = (
        ("scalar_parameters", library.get_scalar_parameter_names, library.get_material_instance_scalar_parameter_value),
        ("vector_parameters", library.get_vector_parameter_names, library.get_material_instance_vector_parameter_value),
        ("texture_parameters", library.get_texture_parameter_names, library.get_material_instance_texture_parameter_value),
        ("static_switch_parameters", library.get_static_switch_parameter_names, library.get_material_instance_static_switch_parameter_value),
    )
    for output_key, names_getter, value_getter in specs:
        try:
            names = [str(name) for name in names_getter(material)]
        except Exception as exc:
            row[output_key] = {"error": f"{type(exc).__name__}: {exc}"}
            continue
        values: dict[str, object] = {}
        for name in names:
            try:
                value = value_getter(material, name)
                values[name] = texture_record(value) if output_key == "texture_parameters" else normalize(value)
            except Exception as exc:
                values[name] = {"error": f"{type(exc).__name__}: {exc}"}
        row[output_key] = values
    return row


def static_mesh_actor_record(actor: object) -> dict[str, object]:
    row = actor_base(actor)
    component = actor.get_component_by_class(unreal.StaticMeshComponent)
    require(component is not None, f"StaticMeshComponent missing: {actor.get_actor_label()}")
    mesh = component.get_editor_property("static_mesh")
    require(mesh is not None, f"Static mesh missing: {actor.get_actor_label()}")
    row["static_mesh"] = object_path(mesh)
    row["component_visibility"] = safe_property(component, "visible")
    row["component_hidden_in_game"] = safe_property(component, "hidden_in_game")
    row["component_mobility"] = safe_property(component, "mobility")
    row["materials"] = [material_record(component.get_material(index)) for index in range(component.get_num_materials())]
    row["mesh_bounds_extent_cm"] = normalize(mesh.get_bounds().box_extent)
    return row


def component_records(actor: object) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for component in actor.get_components_by_class(unreal.ActorComponent):
        row = {
            "path": object_path(component),
            "class": component.get_class().get_path_name(),
            "visible": safe_property(component, "visible"),
            "hidden_in_game": safe_property(component, "hidden_in_game"),
            "mobility": safe_property(component, "mobility"),
        }
        if isinstance(component, unreal.StaticMeshComponent):
            row["static_mesh"] = object_path(component.get_editor_property("static_mesh"))
            row["materials"] = [material_record(component.get_material(index)) for index in range(component.get_num_materials())]
        rows.append(row)
    return rows


def light_record(actor: object) -> dict[str, object]:
    row = actor_base(actor)
    component = actor.get_component_by_class(unreal.LightComponentBase)
    if component is None:
        component = actor.get_component_by_class(unreal.SkyLightComponent)
    if component is not None:
        row["component"] = {
            name: safe_property(component, name)
            for name in (
                "intensity", "intensity_scale", "light_color", "cast_shadows",
                "indirect_lighting_intensity", "volumetric_scattering_intensity",
                "temperature", "use_temperature", "source_angle", "source_soft_angle",
                "real_time_capture", "lower_hemisphere_is_solid_color", "lower_hemisphere_color",
            )
        }
    if actor.get_actor_label() == "M01_RS01_PostProcess":
        settings = actor.get_editor_property("settings")
        row["volume"] = {
            name: safe_property(actor, name) for name in ("unbound", "blend_weight", "priority", "blend_radius")
        }
        row["settings"] = {
            name: safe_property(settings, name)
            for name in (
                "auto_exposure_method", "auto_exposure_bias", "auto_exposure_min_brightness",
                "auto_exposure_max_brightness", "film_slope", "film_toe", "film_shoulder",
                "film_black_clip", "film_white_clip", "color_saturation", "color_contrast",
                "color_gamma", "color_gain", "color_offset", "dynamic_global_illumination_method",
                "reflection_method",
            )
        }
    return row


result: dict[str, Any] = {
    "schema": "skyguard.m01-visible-environment-stage03.diagnostic01.v1",
    "classification": "FAILED_WITH_EVIDENCE",
    "read_only": True,
    "world_saved": False,
    "map_asset": MAP_ASSET,
    "map_sha256_before": None,
    "map_sha256_after": None,
    "map_unchanged": False,
    "actor_count": 0,
    "landscape": {},
    "broad_surfaces": [],
    "representative_buildings": [],
    "vegetation": [],
    "lighting": {},
    "environment_directors": [],
    "errors": [],
}

try:
    require(MAP_FILE.is_file(), "Stage02 map is missing")
    require(MAP_FILE.stat().st_size == EXPECTED_MAP_BYTES, "Stage02 map byte count changed")
    result["map_sha256_before"] = sha256(MAP_FILE)
    require(result["map_sha256_before"] == EXPECTED_MAP_SHA256, "Stage02 map hash changed")

    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    actors_api = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    require(levels is not None and actors_api is not None, "Required editor subsystems unavailable")
    require(bool(levels.load_level(MAP_ASSET)), "Stage02 map failed to load")
    actors = list(actors_api.get_all_level_actors())
    result["actor_count"] = len(actors)
    require(len(actors) >= 192, f"Stage02 actor count regressed: {len(actors)}")
    by_label = {actor.get_actor_label(): actor for actor in actors}

    landscape = by_label.get("M01_A01_Landscape_Production")
    require(landscape is not None, "Production Landscape is missing")
    result["landscape"] = actor_base(landscape)
    result["landscape"]["landscape_material"] = material_record(landscape.get_editor_property("landscape_material"))
    result["landscape"]["landscape_hole_material"] = material_record(landscape.get_editor_property("landscape_hole_material"))

    for actor in actors:
        label = actor.get_actor_label()
        if isinstance(actor, unreal.StaticMeshActor):
            record = static_mesh_actor_record(actor)
            extent = record["bounds"]["extent_cm"]
            broad = float(extent[0]) >= 2500.0 or float(extent[1]) >= 2500.0
            if broad or label.endswith(SURFACE_SUFFIXES):
                result["broad_surfaces"].append(record)
            if any(token in label for token in REPRESENTATIVE_BUILDING_TOKENS):
                result["representative_buildings"].append(record)
            if label.startswith(VEGETATION_PREFIX):
                result["vegetation"].append(record)
        elif label.startswith("Mission01EnvironmentDirector") or "EnvironmentDirector" in label:
            row = actor_base(actor)
            row["components"] = component_records(actor)
            result["environment_directors"].append(row)

    for label in KEY_LABELS:
        actor = by_label.get(label)
        if actor is not None and label != "M01_A01_Landscape_Production":
            result["lighting"][label] = light_record(actor)

    result["broad_surfaces"].sort(key=lambda row: str(row["label"]))
    result["representative_buildings"].sort(key=lambda row: str(row["label"]))
    result["vegetation"].sort(key=lambda row: str(row["label"]))
    require(len(result["vegetation"]) == 28, f"Expected 28 vegetation actors; found {len(result['vegetation'])}")

    pitched = [row for row in result["vegetation"] if abs(float(row["rotation_degrees"]["pitch"])) > 0.01]
    yawed = [row for row in result["vegetation"] if abs(float(row["rotation_degrees"]["yaw"])) > 0.01]
    result["vegetation_transform_summary"] = {
        "actor_count": len(result["vegetation"]),
        "nonzero_pitch_count": len(pitched),
        "nonzero_yaw_count": len(yawed),
        "root_cause_confirmed": len(pitched) == 28 and len(yawed) == 0,
        "interpretation": "Positional Rotator construction assigned intended yaw values to pitch. Use named pitch/yaw/roll fields and re-ground after rotation.",
    }
    require(result["vegetation_transform_summary"]["root_cause_confirmed"], "Vegetation transform root cause did not match evidence")

    result["map_sha256_after"] = sha256(MAP_FILE)
    result["map_unchanged"] = result["map_sha256_after"] == result["map_sha256_before"]
    require(result["map_unchanged"], "Read-only probe changed Stage02 map")
    result["classification"] = "PASSED_STAGE02_ROOT_CAUSE_EVIDENCE_READY_FOR_STAGE03_CORRECTION"
except Exception as exc:
    result["errors"].append({"type": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()})
finally:
    if result["map_sha256_after"] is None and MAP_FILE.is_file():
        result["map_sha256_after"] = sha256(MAP_FILE)
        result["map_unchanged"] = result["map_sha256_after"] == result["map_sha256_before"]
    write_json_atomic(RECEIPT, result)

print("SKYGUARD_M01_STAGE03_DIAGNOSTIC01=" + str(result["classification"]))
if result["classification"] != "PASSED_STAGE02_ROOT_CAUSE_EVIDENCE_READY_FOR_STAGE03_CORRECTION":
    raise RuntimeError(result["errors"][-1]["message"] if result["errors"] else "Stage02 root-cause probe failed")
