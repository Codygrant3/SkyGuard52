import hashlib
import json
import re
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
ISOLATED = Path(r"D:\SG52T08_ENV01")
INPUT_ASSET = "/Game/M01/Lvl_M01_VisibleEnvironmentKit02_VisualRemediation01_Recovery01"
OUTPUT_ASSET = "/Game/M01/Lvl_M01_VisibleEnvironmentKit02_PresentationRefinement01"
INPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_VisibleEnvironmentKit02_VisualRemediation01_Recovery01.umap"
OUTPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_VisibleEnvironmentKit02_PresentationRefinement01.umap"
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_VISIBLE_ENVIRONMENT_PRESENTATION_REFINEMENT01/attempt_01"
RECEIPT = ATTEMPT / "authoring_receipt.json"

EXPECTED_INPUT_BYTES = 841114
EXPECTED_INPUT_SHA256 = "d5a134978dec578f2833647d95545d228928cd6d30aee86f69e51e69506c8669"
EXPECTED_INPUT_ACTOR_COUNT = 179
EXPECTED_OUTPUT_ACTOR_COUNT = 180
EXPECTED_STRUCTURAL_ACTORS = 27

FILL_LABEL = "M01_PR01_FillSun"
FILL_INTENSITY = 2.75
FILL_ROTATION = {"pitch": -25.0, "yaw": -105.0, "roll": 0.0}

BLUE_PLASTER = (
    "/Game/M01/EnvKit02/M01_APARTMENT_A/Materials/"
    "M_ENV_Plaster_Blue_Weathered_2K.M_ENV_Plaster_Blue_Weathered_2K"
)
WARM_PLASTER = (
    "/Game/M01/EnvKit02/M01_MIDRISE_B/Materials/"
    "M_ENV_Plaster_Warm_2K.M_ENV_Plaster_Warm_2K"
)

LABEL_PATTERN = re.compile(
    r"^M01_VEK02_City_R(?P<row>\d{2})_C(?P<column>\d{2})_"
    r"(?P<family>ApartmentA|MidriseB|CornerC)_STRUCTURAL$"
)
PLASTER_SLOT_BY_FAMILY = {
    "ApartmentA": 0,
    "MidriseB": 0,
    "CornerC": 2,
}
EXPECTED_INHERITED_MATERIAL_BY_FAMILY = {
    "ApartmentA": "M_ENV_Plaster_Blue_Weathered_2K",
    "MidriseB": "M_ENV_Plaster_Warm_2K",
    "CornerC": "M_ENV_Plaster_Warm_2K",
}


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
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def find_exact(actors, label):
    matches = [actor for actor in actors if actor.get_actor_label() == label]
    require(len(matches) == 1, f"Expected exactly one actor {label}; found {len(matches)}")
    return matches[0]


def transform_state(actor):
    location = actor.get_actor_location()
    rotation = actor.get_actor_rotation()
    scale = actor.get_actor_scale3d()
    return {
        "location_cm": [float(location.x), float(location.y), float(location.z)],
        "rotation_degrees": [float(rotation.pitch), float(rotation.yaw), float(rotation.roll)],
        "scale": [float(scale.x), float(scale.y), float(scale.z)],
    }


result = {
    "schema": "skyguard.m01-visible-environment-presentation-refinement01.authoring.v1",
    "classification": "FAILED_WITH_EVIDENCE",
    "input_asset": INPUT_ASSET,
    "output_asset": OUTPUT_ASSET,
    "input_sha256_before": None,
    "input_sha256_after": None,
    "output_sha256": None,
    "actor_count_before": None,
    "actor_count_after": None,
    "fill_light": None,
    "material_variation_count": 0,
    "material_variations": [],
    "unchanged_structural_count": 0,
    "key_sun": None,
    "skylight": None,
    "error": None,
}

try:
    require(INPUT_FILE.is_file(), f"Accepted input map missing: {INPUT_FILE}")
    require(INPUT_FILE.stat().st_size == EXPECTED_INPUT_BYTES, "Input map byte count changed")
    result["input_sha256_before"] = sha256(INPUT_FILE)
    require(result["input_sha256_before"] == EXPECTED_INPUT_SHA256, "Input map hash changed")
    require(not OUTPUT_FILE.exists(), f"Fresh output namespace exists: {OUTPUT_FILE}")

    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    actors_api = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    require(levels is not None and actors_api is not None, "Required editor subsystems unavailable")
    require(levels.new_level_from_template(OUTPUT_ASSET, INPUT_ASSET), "Failed to clone accepted map")

    actors = list(actors_api.get_all_level_actors())
    result["actor_count_before"] = len(actors)
    require(
        len(actors) == EXPECTED_INPUT_ACTOR_COUNT,
        f"Expected {EXPECTED_INPUT_ACTOR_COUNT} inherited actors; found {len(actors)}",
    )
    require(not any(actor.get_actor_label() == FILL_LABEL for actor in actors), "Fill light already exists")

    blue_plaster = unreal.load_asset(BLUE_PLASTER)
    warm_plaster = unreal.load_asset(WARM_PLASTER)
    require(blue_plaster is not None, f"Blue plaster failed to load: {BLUE_PLASTER}")
    require(warm_plaster is not None, f"Warm plaster failed to load: {WARM_PLASTER}")

    structural_actors = []
    for actor in actors:
        match = LABEL_PATTERN.match(actor.get_actor_label())
        if match:
            structural_actors.append((actor, match))
    require(
        len(structural_actors) == EXPECTED_STRUCTURAL_ACTORS,
        f"Expected {EXPECTED_STRUCTURAL_ACTORS} structural actors; found {len(structural_actors)}",
    )

    for actor, match in sorted(structural_actors, key=lambda item: item[0].get_actor_label()):
        family = match.group("family")
        row = int(match.group("row"))
        column = int(match.group("column"))
        component = actor.get_component_by_class(unreal.StaticMeshComponent)
        require(component is not None, f"StaticMeshComponent missing: {actor.get_actor_label()}")
        require(
            component.get_editor_property("mobility") == unreal.ComponentMobility.STATIC,
            f"Structural actor is not static: {actor.get_actor_label()}",
        )
        slot_index = PLASTER_SLOT_BY_FAMILY[family]
        current = component.get_material(slot_index)
        require(current is not None, f"Inherited plaster material missing: {actor.get_actor_label()}")
        current_name = current.get_name()
        require(
            current_name == EXPECTED_INHERITED_MATERIAL_BY_FAMILY[family],
            f"Unexpected inherited plaster material on {actor.get_actor_label()}: {current_name}",
        )
        before_transform = transform_state(actor)

        # A deterministic checker pattern breaks the obvious repeated facade color rhythm
        # while preserving each mesh, transform, collision setup and material-slot meaning.
        should_vary = (row + column) % 2 == 0
        if should_vary:
            replacement = warm_plaster if family == "ApartmentA" else blue_plaster
            component.set_material(slot_index, replacement)
            actual = component.get_material(slot_index)
            require(actual is not None, f"Material override failed: {actor.get_actor_label()}")
            require(actual.get_path_name() == replacement.get_path_name(), f"Material override mismatch: {actor.get_actor_label()}")
            result["material_variations"].append(
                {
                    "actor": actor.get_actor_label(),
                    "family": family,
                    "row": row,
                    "column": column,
                    "slot_index": slot_index,
                    "before": current.get_path_name(),
                    "after": actual.get_path_name(),
                }
            )
            result["material_variation_count"] += 1
        else:
            result["unchanged_structural_count"] += 1

        require(transform_state(actor) == before_transform, f"Transform drift: {actor.get_actor_label()}")

    require(result["material_variation_count"] == 14, "Unexpected material variation count")
    require(result["unchanged_structural_count"] == 13, "Unexpected unchanged structural count")

    fill = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.DirectionalLight,
        unreal.Vector(22500.0, 12000.0, 8000.0),
        unreal.Rotator(
            roll=FILL_ROTATION["roll"],
            pitch=FILL_ROTATION["pitch"],
            yaw=FILL_ROTATION["yaw"],
        ),
    )
    require(fill is not None, "Failed to spawn presentation fill light")
    fill.set_actor_label(FILL_LABEL)
    fill_component = fill.get_component_by_class(unreal.DirectionalLightComponent)
    require(fill_component is not None, "DirectionalLightComponent missing on fill")
    fill_component.set_mobility(unreal.ComponentMobility.MOVABLE)
    fill_component.set_editor_property("intensity", FILL_INTENSITY)
    fill_component.set_editor_property("cast_shadows", False)
    fill_component.set_editor_property("atmosphere_sun_light", False)
    result["fill_light"] = {
        "label": fill.get_actor_label(),
        "transform": transform_state(fill),
        "mobility": str(fill_component.get_editor_property("mobility")),
        "intensity": float(fill_component.get_editor_property("intensity")),
        "cast_shadows": bool(fill_component.get_editor_property("cast_shadows")),
        "atmosphere_sun_light": bool(fill_component.get_editor_property("atmosphere_sun_light")),
    }
    require(result["fill_light"]["mobility"] == str(unreal.ComponentMobility.MOVABLE), "Fill mobility mismatch")
    require(abs(result["fill_light"]["intensity"] - FILL_INTENSITY) <= 0.001, "Fill intensity mismatch")
    require(result["fill_light"]["cast_shadows"] is False, "Fill must not cast a second shadow")
    require(result["fill_light"]["atmosphere_sun_light"] is False, "Fill must not drive a second sun disk")

    key = find_exact(actors, "M01_RS01_Sun")
    key_component = key.get_component_by_class(unreal.DirectionalLightComponent)
    require(key_component is not None, "Key DirectionalLightComponent unavailable")
    result["key_sun"] = {
        "transform": transform_state(key),
        "intensity": float(key_component.get_editor_property("intensity")),
    }
    require(abs(result["key_sun"]["intensity"] - 10.0) <= 0.001, "Inherited key intensity changed")

    sky = find_exact(actors, "M01_RS01_SkyLight")
    sky_component = sky.get_component_by_class(unreal.SkyLightComponent)
    require(sky_component is not None, "SkyLightComponent unavailable")
    result["skylight"] = {
        "mobility": str(sky_component.get_editor_property("mobility")),
        "intensity": float(sky_component.get_editor_property("intensity")),
        "real_time_capture": bool(sky_component.get_editor_property("real_time_capture")),
        "lower_hemisphere_is_solid_color": bool(
            sky_component.get_editor_property("lower_hemisphere_is_solid_color")
        ),
    }
    require(abs(result["skylight"]["intensity"] - 3.25) <= 0.001, "Inherited skylight intensity changed")
    require(result["skylight"]["real_time_capture"] is True, "Inherited skylight real-time capture changed")
    require(result["skylight"]["lower_hemisphere_is_solid_color"] is False, "Inherited lower hemisphere changed")

    actors_after = list(actors_api.get_all_level_actors())
    result["actor_count_after"] = len(actors_after)
    require(
        len(actors_after) == EXPECTED_OUTPUT_ACTOR_COUNT,
        f"Expected {EXPECTED_OUTPUT_ACTOR_COUNT} output actors; found {len(actors_after)}",
    )
    require(levels.save_current_level(), "Failed to save PresentationRefinement01 map")
    require(OUTPUT_FILE.is_file(), "PresentationRefinement01 map was not created")
    result["output_sha256"] = sha256(OUTPUT_FILE)
    result["input_sha256_after"] = sha256(INPUT_FILE)
    require(result["input_sha256_after"] == EXPECTED_INPUT_SHA256, "Accepted input map changed")
    result["classification"] = "PASSED_M01_VISIBLE_ENVIRONMENT_PRESENTATION_REFINEMENT01_AUTOMATIC"
except Exception as exc:
    result["error"] = f"{type(exc).__name__}: {exc}"
finally:
    write_json(RECEIPT, result)

if result["classification"] != "PASSED_M01_VISIBLE_ENVIRONMENT_PRESENTATION_REFINEMENT01_AUTOMATIC":
    raise RuntimeError(result["error"] or "PresentationRefinement01 failed")
