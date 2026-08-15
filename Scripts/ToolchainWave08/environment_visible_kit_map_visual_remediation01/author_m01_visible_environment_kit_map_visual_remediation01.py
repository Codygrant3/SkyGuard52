import hashlib
import json
import math
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
ISOLATED = Path(r"D:\SG52T08_ENV01")
INPUT_ASSET = "/Game/M01/Lvl_M01_VisibleEnvironmentKit02_Recovery02"
OUTPUT_ASSET = "/Game/M01/Lvl_M01_VisibleEnvironmentKit02_VisualRemediation01"
INPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_VisibleEnvironmentKit02_Recovery02.umap"
OUTPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_VisibleEnvironmentKit02_VisualRemediation01.umap"
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_VISIBLE_ENVIRONMENT_KIT_MAP_VISUAL_REMEDIATION01/attempt_01"
RECEIPT = ATTEMPT / "authoring_receipt.json"
EXPECTED_INPUT_BYTES = 827791
EXPECTED_INPUT_SHA256 = "186cb23fc67c78613453552d1da9c203161a63b12cc894f66019784e04b00fee"
EXPECTED_ACTOR_COUNT = 179
EXPECTED_BUILDING_PLACEMENTS = 27
EXPECTED_CITY_ACTORS = 81
TARGET_BUILDING_YAW = 180.0
TARGET_SKYLIGHT_INTENSITY = 3.25


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def vector(value):
    return [float(value.x), float(value.y), float(value.z)]


def rotator(value):
    return [float(value.pitch), float(value.yaw), float(value.roll)]


def find_exact(actors, label):
    matches = [actor for actor in actors if actor.get_actor_label() == label]
    require(len(matches) == 1, f"Expected exactly one actor {label}; found {len(matches)}")
    return matches[0]


def mesh_for(actor):
    component = actor.get_component_by_class(unreal.StaticMeshComponent)
    require(component is not None, f"StaticMeshComponent missing on {actor.get_actor_label()}")
    mesh = component.get_editor_property("static_mesh")
    require(isinstance(mesh, unreal.StaticMesh), f"StaticMesh missing on {actor.get_actor_label()}")
    return component, mesh


def rotated_center_offset(bounds, yaw_degrees):
    radians = math.radians(float(yaw_degrees))
    cosine, sine = math.cos(radians), math.sin(radians)
    return (
        cosine * float(bounds.origin.x) - sine * float(bounds.origin.y),
        sine * float(bounds.origin.x) + cosine * float(bounds.origin.y),
    )


def actor_location_for_center(mesh, center_x, center_y, target_bottom, yaw_degrees):
    bounds = mesh.get_bounds()
    offset_x, offset_y = rotated_center_offset(bounds, yaw_degrees)
    local_bottom = float(bounds.origin.z - bounds.box_extent.z)
    return unreal.Vector(center_x - offset_x, center_y - offset_y, target_bottom - local_bottom)


def light_state(component):
    return {
        "mobility": str(component.get_editor_property("mobility")),
        "intensity": float(component.get_editor_property("intensity")),
        "real_time_capture": bool(component.get_editor_property("real_time_capture")),
        "lower_hemisphere_is_solid_color": bool(
            component.get_editor_property("lower_hemisphere_is_solid_color")
        ),
    }


result = {
    "schema": "skyguard.m01-visible-environment-kit-map-visual-remediation01.authoring.v1",
    "classification": "FAILED_WITH_EVIDENCE",
    "input_asset": INPUT_ASSET,
    "output_asset": OUTPUT_ASSET,
    "input_sha256_before": None,
    "input_sha256_after": None,
    "output_sha256": None,
    "actor_count": None,
    "building_placements": [],
    "rotated_city_actor_count": 0,
    "facade_axis_evidence": {
        "accepted_import_axis": "glazing occupies +Y edge before correction",
        "target": "glazing occupies -Y ocean-facing edge after correction",
    },
    "skylight_before": None,
    "skylight_after": None,
    "sun_unchanged": None,
    "error": None,
}

try:
    require(INPUT_FILE.is_file(), f"Accepted input map missing: {INPUT_FILE}")
    require(INPUT_FILE.stat().st_size == EXPECTED_INPUT_BYTES, "Accepted input map byte count changed")
    result["input_sha256_before"] = sha256(INPUT_FILE)
    require(result["input_sha256_before"] == EXPECTED_INPUT_SHA256, "Accepted input map hash changed")
    require(not OUTPUT_FILE.exists(), f"Fresh output namespace exists: {OUTPUT_FILE}")

    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    actors_api = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    require(levels is not None and actors_api is not None, "Required editor subsystems are unavailable")
    require(levels.new_level_from_template(OUTPUT_ASSET, INPUT_ASSET), "Failed to clone accepted Recovery02 map")
    actors = list(actors_api.get_all_level_actors())
    result["actor_count"] = len(actors)
    require(len(actors) == EXPECTED_ACTOR_COUNT, f"Expected {EXPECTED_ACTOR_COUNT} actors; found {len(actors)}")

    city_actors = [actor for actor in actors if actor.get_actor_label().startswith("M01_VEK02_City_")]
    require(len(city_actors) == EXPECTED_CITY_ACTORS, f"Expected {EXPECTED_CITY_ACTORS} city actors; found {len(city_actors)}")
    placements = {}
    for actor in city_actors:
        label = actor.get_actor_label()
        group = label.rsplit("_", 1)[-1]
        require(group in {"STRUCTURAL", "GLAZING", "DETAILS"}, f"Unexpected city semantic group: {label}")
        placement = label[: -(len(group) + 1)]
        require(group not in placements.setdefault(placement, {}), f"Duplicate semantic group: {label}")
        placements[placement][group] = actor
    require(len(placements) == EXPECTED_BUILDING_PLACEMENTS, f"Expected {EXPECTED_BUILDING_PLACEMENTS} placements; found {len(placements)}")

    for placement in sorted(placements):
        groups = placements[placement]
        require(set(groups) == {"STRUCTURAL", "GLAZING", "DETAILS"}, f"Incomplete placement: {placement}")
        structural = groups["STRUCTURAL"]
        structural_component, structural_mesh = mesh_for(structural)
        before_origin, before_extent = structural.get_actor_bounds(False)
        before_bottom = float(before_origin.z - before_extent.z)
        before_location = structural.get_actor_location()
        before_rotation = structural.get_actor_rotation()
        glazing_before_origin, _ = groups["GLAZING"].get_actor_bounds(False)
        require(
            float(glazing_before_origin.y) > float(before_origin.y) + 100.0,
            f"Expected inherited glazing on +Y inland edge: {placement}",
        )
        new_location = actor_location_for_center(
            structural_mesh,
            float(before_origin.x),
            float(before_origin.y),
            before_bottom,
            TARGET_BUILDING_YAW,
        )
        for group in ("STRUCTURAL", "GLAZING", "DETAILS"):
            actor = groups[group]
            component, _ = mesh_for(actor)
            require(
                component.get_editor_property("mobility") == unreal.ComponentMobility.STATIC,
                f"Non-static city actor: {actor.get_actor_label()}",
            )
            actor.set_actor_rotation(
                unreal.Rotator(roll=0.0, pitch=0.0, yaw=TARGET_BUILDING_YAW), False
            )
            actor.set_actor_location(new_location, False, False)
            result["rotated_city_actor_count"] += 1

        after_origin, after_extent = structural.get_actor_bounds(False)
        after_bottom = float(after_origin.z - after_extent.z)
        glazing_after_origin, _ = groups["GLAZING"].get_actor_bounds(False)
        require(abs(float(after_origin.x) - float(before_origin.x)) <= 0.25, f"Structural X center moved: {placement}")
        require(abs(float(after_origin.y) - float(before_origin.y)) <= 0.25, f"Structural Y center moved: {placement}")
        require(abs(after_bottom - before_bottom) <= 0.25, f"Structural grounding moved: {placement}")
        require(
            float(glazing_after_origin.y) < float(after_origin.y) - 100.0,
            f"Glazing did not rotate to -Y ocean edge: {placement}",
        )
        result["building_placements"].append(
            {
                "placement": placement,
                "before_location_cm": vector(before_location),
                "after_location_cm": vector(new_location),
                "before_rotation_degrees": rotator(before_rotation),
                "after_rotation_degrees": rotator(structural.get_actor_rotation()),
                "structural_center_before_cm": vector(before_origin),
                "structural_center_after_cm": vector(after_origin),
                "structural_bottom_before_cm": before_bottom,
                "structural_bottom_after_cm": after_bottom,
                "glazing_center_y_before_cm": float(glazing_before_origin.y),
                "glazing_center_y_after_cm": float(glazing_after_origin.y),
                "facade_facing_ocean": True,
            }
        )

    require(result["rotated_city_actor_count"] == EXPECTED_CITY_ACTORS, "Rotated city actor count mismatch")

    sky = find_exact(actors, "M01_RS01_SkyLight")
    sky_component = sky.get_component_by_class(unreal.SkyLightComponent)
    require(sky_component is not None, "SkyLightComponent is unavailable")
    result["skylight_before"] = light_state(sky_component)
    sky_component.set_mobility(unreal.ComponentMobility.MOVABLE)
    sky_component.set_editor_property("intensity", TARGET_SKYLIGHT_INTENSITY)
    sky_component.set_editor_property("real_time_capture", True)
    sky_component.set_editor_property("lower_hemisphere_is_solid_color", False)
    result["skylight_after"] = light_state(sky_component)
    require(result["skylight_after"]["mobility"] == str(unreal.ComponentMobility.MOVABLE), "Skylight mobility correction failed")
    require(abs(result["skylight_after"]["intensity"] - TARGET_SKYLIGHT_INTENSITY) <= 0.001, "Skylight intensity correction failed")
    require(result["skylight_after"]["real_time_capture"] is True, "Real-time skylight capture is disabled")
    require(result["skylight_after"]["lower_hemisphere_is_solid_color"] is False, "Lower-hemisphere fill correction failed")

    sun = find_exact(actors, "M01_RS01_Sun")
    sun_component = sun.get_component_by_class(unreal.DirectionalLightComponent)
    require(sun_component is not None, "DirectionalLightComponent is unavailable")
    result["sun_unchanged"] = {
        "rotation_degrees": rotator(sun.get_actor_rotation()),
        "intensity": float(sun_component.get_editor_property("intensity")),
    }

    require(levels.save_current_level(), "Failed to save VisualRemediation01 map")
    require(OUTPUT_FILE.is_file(), "VisualRemediation01 map was not created")
    result["output_sha256"] = sha256(OUTPUT_FILE)
    result["input_sha256_after"] = sha256(INPUT_FILE)
    require(result["input_sha256_after"] == EXPECTED_INPUT_SHA256, "Accepted Recovery02 map changed")
    result["classification"] = "PASSED_M01_VISIBLE_ENVIRONMENT_KIT_MAP_VISUAL_REMEDIATION01_AUTOMATIC"
except Exception as exc:
    result["error"] = f"{type(exc).__name__}: {exc}"
finally:
    write_json(RECEIPT, result)

if result["classification"] != "PASSED_M01_VISIBLE_ENVIRONMENT_KIT_MAP_VISUAL_REMEDIATION01_AUTOMATIC":
    raise RuntimeError(result["error"] or "VisualRemediation01 failed")
