from __future__ import annotations

import hashlib
import json
import math
import os
import re
import traceback
from collections import Counter
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
ISOLATED = Path(r"D:\SG52T08_ENV01")
INPUT_ASSET = "/Game/M01/Lvl_M01_VisibleEnvironmentKit02_PresentationRefinement01_Recovery01"
OUTPUT_ASSET = "/Game/M01/Lvl_M01_PhotorealFoundation_NonVegetation01"
INPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_VisibleEnvironmentKit02_PresentationRefinement01_Recovery01.umap"
OUTPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_PhotorealFoundation_NonVegetation01.umap"
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_PHOTOREAL_FOUNDATION_WAVE01_NONVEGETATION01_AUTHORING/attempt_01"
RECEIPT = ATTEMPT / "authoring_receipt.json"

EXPECTED_INPUT_BYTES = 845823
EXPECTED_INPUT_SHA256 = "7ff5370b03b090c1111395e7873da9d8333c1063d3492d30c4e6e7a7006a3430"
EXPECTED_INPUT_ACTORS = 180
EXPECTED_TREE_COUNT = 60
EXPECTED_CITY_GROUPS = 27
EXPECTED_OUTPUT_ACTORS = 120

WINDOW_MATERIAL = (
    "/Game/Skyguard/Meshes/Mission01/Wave1Refinement/"
    "m01_wave1_aaa_refinement/Materials/M_M01_Window"
)
GLASS_MATERIAL = (
    "/Game/Skyguard/Meshes/Mission01/Wave1Refinement/"
    "m01_wave1_aaa_refinement/Materials/M_M01_Glass"
)

CITY_PATTERN = re.compile(
    r"^(?P<placement>M01_VEK02_City_R(?P<row>\d{2})_C(?P<column>\d{2})_"
    r"(?P<family>ApartmentA|MidriseB|CornerC))_(?P<group>STRUCTURAL|GLAZING|DETAILS)$"
)

X_OFFSETS = (
    (-420.0, 180.0, -110.0, 460.0, -260.0, 320.0, -480.0, 80.0, 390.0),
    (260.0, -360.0, 430.0, -120.0, 90.0, -470.0, 350.0, -210.0, 510.0),
    (-190.0, 470.0, -430.0, 230.0, -40.0, 390.0, -280.0, 140.0, -510.0),
)
Y_OFFSETS = (
    (-180.0, 240.0, -320.0, 110.0, 360.0, -90.0, 280.0, -260.0, 40.0),
    (310.0, -140.0, 220.0, -330.0, 70.0, 350.0, -210.0, 130.0, -280.0),
    (-260.0, 90.0, 340.0, -120.0, 210.0, -350.0, 160.0, 300.0, -60.0),
)
YAW_OFFSETS = (
    (-8.0, -3.0, 4.0, 7.0, -5.0, 2.0, 9.0, -1.0, 5.0),
    (6.0, -7.0, 1.0, 8.0, -2.0, 4.0, -9.0, 3.0, -4.0),
    (-5.0, 8.0, -1.0, 5.0, -8.0, 2.0, 7.0, -3.0, 4.0),
)
SCALES = (
    (0.96, 1.04, 1.00, 1.07, 0.94, 1.02, 0.98, 1.06, 1.00),
    (1.03, 0.95, 1.08, 0.99, 1.05, 0.97, 1.01, 1.06, 0.94),
    (0.98, 1.07, 0.95, 1.03, 1.00, 1.06, 0.96, 1.04, 1.01),
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def prop(value: object, *names: str):
    for name in names:
        try:
            return value.get_editor_property(name)
        except Exception:
            if hasattr(value, name):
                return getattr(value, name)
    raise RuntimeError(f"Missing property {names} on {type(value).__name__}")


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


def vector3(value: object) -> list[float]:
    return [float(value.x), float(value.y), float(value.z)]


def transform_state(actor: object) -> dict[str, object]:
    location = actor.get_actor_location()
    rotation = actor.get_actor_rotation()
    scale = actor.get_actor_scale3d()
    return {
        "location_cm": vector3(location),
        "rotation_degrees": [float(rotation.pitch), float(rotation.yaw), float(rotation.roll)],
        "scale": vector3(scale),
    }


def near(a: float, b: float, tolerance: float = 0.02) -> bool:
    return abs(float(a) - float(b)) <= tolerance


def same_transform(a: dict[str, object], b: dict[str, object]) -> bool:
    return all(
        near(left, right)
        for key in ("location_cm", "rotation_degrees", "scale")
        for left, right in zip(a[key], b[key])
    )


def mesh_component(actor: object):
    component = actor.get_component_by_class(unreal.StaticMeshComponent)
    require(component is not None, f"StaticMeshComponent missing: {actor.get_actor_label()}")
    mesh = component.get_editor_property("static_mesh")
    require(mesh is not None, f"StaticMesh missing: {actor.get_actor_label()}")
    return component, mesh


def rotated_center_offset(bounds: object, yaw_degrees: float, scale: float) -> tuple[float, float]:
    radians = math.radians(float(yaw_degrees))
    cosine, sine = math.cos(radians), math.sin(radians)
    x = float(bounds.origin.x) * scale
    y = float(bounds.origin.y) * scale
    return cosine * x - sine * y, sine * x + cosine * y


def rotated_extents(bounds: object, yaw_degrees: float, scale: float) -> tuple[float, float]:
    radians = math.radians(float(yaw_degrees))
    cosine, sine = abs(math.cos(radians)), abs(math.sin(radians))
    ex = float(bounds.box_extent.x) * scale
    ey = float(bounds.box_extent.y) * scale
    return cosine * ex + sine * ey, sine * ex + cosine * ey


def actor_location_for_center(
    mesh: object,
    center_x: float,
    center_y: float,
    target_bottom: float,
    yaw_degrees: float,
    scale: float,
):
    bounds = mesh.get_bounds()
    offset_x, offset_y = rotated_center_offset(bounds, yaw_degrees, scale)
    local_bottom = float(bounds.origin.z - bounds.box_extent.z) * scale
    return unreal.Vector(center_x - offset_x, center_y - offset_y, target_bottom - local_bottom)


def sample_ground(library: object, landscape: object, center_x: float, center_y: float, extent_x: float, extent_y: float) -> dict[str, float]:
    ex, ey = max(50.0, extent_x * 0.90), max(50.0, extent_y * 0.90)
    points = [
        unreal.Vector(center_x, center_y, 100000.0),
        unreal.Vector(center_x - ex, center_y - ey, 100000.0),
        unreal.Vector(center_x + ex, center_y - ey, 100000.0),
        unreal.Vector(center_x - ex, center_y + ey, 100000.0),
        unreal.Vector(center_x + ex, center_y + ey, 100000.0),
        unreal.Vector(center_x - ex, center_y, 100000.0),
        unreal.Vector(center_x + ex, center_y, 100000.0),
        unreal.Vector(center_x, center_y - ey, 100000.0),
        unreal.Vector(center_x, center_y + ey, 100000.0),
    ]
    sampled = library.sample_landscape_footprint(landscape, points)
    success = bool(prop(sampled, "success", "b_success"))
    supported = float(prop(sampled, "supported_fraction"))
    delta = float(prop(sampled, "height_delta_centimeters"))
    require(success, f"Landscape sample failed: {prop(sampled, 'error')}")
    require(supported == 1.0, f"Landscape support incomplete: {supported}")
    require(delta <= 300.0, f"Landscape height delta exceeds 300 cm: {delta}")
    return {
        "mean_height_cm": float(prop(sampled, "mean_height_centimeters")),
        "minimum_height_cm": float(prop(sampled, "minimum_height_centimeters")),
        "maximum_height_cm": float(prop(sampled, "maximum_height_centimeters")),
        "height_delta_cm": delta,
        "supported_fraction": supported,
    }


def find_exact(actors: list[object], label: str):
    matches = [actor for actor in actors if actor.get_actor_label() == label]
    require(len(matches) == 1, f"Expected one {label}; found {len(matches)}")
    return matches[0]


result: dict[str, object] = {
    "schema": "skyguard.m01-photoreal-foundation.nonvegetation01.authoring.v1",
    "classification": "FAILED_WITH_EVIDENCE",
    "input_asset": INPUT_ASSET,
    "output_asset": OUTPUT_ASSET,
    "input_sha256_before": None,
    "input_sha256_after": None,
    "output_sha256": None,
    "actor_count_before": None,
    "actor_count_after": None,
    "removed_tree_labels": [],
    "city_placements": [],
    "window_overrides": [],
    "road_marking_overrides": [],
    "quality_metrics": {},
    "errors": [],
}

try:
    require(INPUT_FILE.is_file(), "Accepted input map is missing")
    require(INPUT_FILE.stat().st_size == EXPECTED_INPUT_BYTES, "Accepted input map byte count changed")
    result["input_sha256_before"] = sha256(INPUT_FILE)
    require(result["input_sha256_before"] == EXPECTED_INPUT_SHA256, "Accepted input map hash changed")
    require(not OUTPUT_FILE.exists(), f"Fresh output file exists: {OUTPUT_FILE}")
    require(not unreal.EditorAssetLibrary.does_asset_exist(OUTPUT_ASSET), f"Fresh output asset exists: {OUTPUT_ASSET}")

    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    actors_api = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    require(levels is not None and actors_api is not None, "Required editor subsystems unavailable")
    require(levels.new_level_from_template(OUTPUT_ASSET, INPUT_ASSET), "Failed to clone accepted map")
    actors = list(actors_api.get_all_level_actors())
    result["actor_count_before"] = len(actors)
    require(len(actors) == EXPECTED_INPUT_ACTORS, f"Expected {EXPECTED_INPUT_ACTORS} actors; found {len(actors)}")

    trees = [actor for actor in actors if actor.get_actor_label().startswith("M01_RS01_Tree_")]
    require(len(trees) == EXPECTED_TREE_COUNT, f"Expected {EXPECTED_TREE_COUNT} rejected PCG sample trees; found {len(trees)}")
    result["removed_tree_labels"] = sorted(actor.get_actor_label() for actor in trees)
    for actor in trees:
        require(actors_api.destroy_actor(actor), f"Failed to remove rejected tree {actor.get_actor_label()}")

    actors = list(actors_api.get_all_level_actors())
    landscape = find_exact(actors, "M01_A01_Landscape_Production")
    grounding_library = unreal.SkyguardMission01LandscapeGroundingLibrary
    require(grounding_library is not None, "Landscape grounding library unavailable")
    window_material = unreal.load_asset(WINDOW_MATERIAL)
    glass_material = unreal.load_asset(GLASS_MATERIAL)
    require(window_material is not None and glass_material is not None, "Refined window materials failed to load")

    groups: dict[str, dict[str, object]] = {}
    metadata: dict[str, dict[str, object]] = {}
    for actor in actors:
        match = CITY_PATTERN.match(actor.get_actor_label())
        if not match:
            continue
        placement = match.group("placement")
        group = match.group("group")
        require(group not in groups.setdefault(placement, {}), f"Duplicate city group {actor.get_actor_label()}")
        groups[placement][group] = actor
        metadata[placement] = {
            "row": int(match.group("row")),
            "column": int(match.group("column")),
            "family": match.group("family"),
        }
    require(len(groups) == EXPECTED_CITY_GROUPS, f"Expected {EXPECTED_CITY_GROUPS} city groups; found {len(groups)}")
    require(all(set(value) == {"STRUCTURAL", "GLAZING", "DETAILS"} for value in groups.values()), "Incomplete city triplet")

    for placement in sorted(groups):
        triplet = groups[placement]
        meta = metadata[placement]
        row = int(meta["row"])
        column = int(meta["column"])
        structural = triplet["STRUCTURAL"]
        _, structural_mesh = mesh_component(structural)
        before_origin, before_extent = structural.get_actor_bounds(False)
        desired_center_x = float(before_origin.x) + X_OFFSETS[row][column]
        desired_center_y = float(before_origin.y) + Y_OFFSETS[row][column]
        yaw = 180.0 + YAW_OFFSETS[row][column]
        scale = SCALES[row][column]
        local_bounds = structural_mesh.get_bounds()
        extent_x, extent_y = rotated_extents(local_bounds, yaw, scale)
        ground = sample_ground(grounding_library, landscape, desired_center_x, desired_center_y, extent_x, extent_y)
        location = actor_location_for_center(
            structural_mesh,
            desired_center_x,
            desired_center_y,
            ground["mean_height_cm"],
            yaw,
            scale,
        )
        before = transform_state(structural)
        for actor in triplet.values():
            component, _ = mesh_component(actor)
            require(component.get_editor_property("mobility") == unreal.ComponentMobility.STATIC, f"Non-static city actor: {actor.get_actor_label()}")
            actor.set_actor_scale3d(unreal.Vector(scale, scale, scale))
            actor.set_actor_rotation(unreal.Rotator(roll=0.0, pitch=0.0, yaw=yaw), False)
            actor.set_actor_location(location, False, False)

        glazing_component, _ = mesh_component(triplet["GLAZING"])
        require(glazing_component.get_num_materials() == 3, f"Unexpected glazing slot count: {placement}")
        glazing_component.set_material(0, window_material)
        glazing_component.set_material(1, glass_material)
        require(glazing_component.get_material(0).get_path_name() == window_material.get_path_name(), f"Window override failed: {placement}")
        require(glazing_component.get_material(1).get_path_name() == glass_material.get_path_name(), f"Glass override failed: {placement}")
        result["window_overrides"].append(
            {
                "placement": placement,
                "slot_0": glazing_component.get_material(0).get_path_name(),
                "slot_1": glazing_component.get_material(1).get_path_name(),
            }
        )

        states = {name: transform_state(actor) for name, actor in triplet.items()}
        require(same_transform(states["STRUCTURAL"], states["GLAZING"]), f"Glazing transform drift: {placement}")
        require(same_transform(states["STRUCTURAL"], states["DETAILS"]), f"Detail transform drift: {placement}")
        after_origin, after_extent = structural.get_actor_bounds(False)
        after_bottom = float(after_origin.z - after_extent.z)
        require(abs(after_bottom - ground["mean_height_cm"]) <= 1.0, f"Grounding gap exceeds 1 cm: {placement}")
        result["city_placements"].append(
            {
                "placement": placement,
                "family": meta["family"],
                "row": row,
                "column": column,
                "before": before,
                "after": states["STRUCTURAL"],
                "structural_center_cm": vector3(after_origin),
                "structural_extent_cm": vector3(after_extent),
                "grounding": ground,
                "ground_gap_cm": after_bottom - ground["mean_height_cm"],
            }
        )

    hardscapes = sorted(
        (actor for actor in actors if re.match(r"^M01_VEK02_District_\d{2}_HARDSCAPE$", actor.get_actor_label())),
        key=lambda actor: actor.get_actor_label(),
    )
    require(len(hardscapes) == 4, f"Expected four district hardscapes; found {len(hardscapes)}")
    for actor in hardscapes:
        component, _ = mesh_component(actor)
        require(component.get_num_materials() == 6, f"Hardscape slot count changed: {actor.get_actor_label()}")
        asphalt = component.get_material(3)
        marking_before = component.get_material(4)
        require(asphalt is not None and marking_before is not None, f"Hardscape material missing: {actor.get_actor_label()}")
        require("M_ENV_Asphalt_2K" in asphalt.get_path_name(), f"Expected asphalt in slot 3: {actor.get_actor_label()}")
        require("M_ENV_Road_Marking" in marking_before.get_path_name(), f"Expected road marking in slot 4: {actor.get_actor_label()}")
        component.set_material(4, asphalt)
        require(component.get_material(4).get_path_name() == asphalt.get_path_name(), f"Road-marking suppression failed: {actor.get_actor_label()}")
        result["road_marking_overrides"].append(
            {
                "actor": actor.get_actor_label(),
                "before": marking_before.get_path_name(),
                "after": asphalt.get_path_name(),
            }
        )

    remaining = list(actors_api.get_all_level_actors())
    result["actor_count_after"] = len(remaining)
    require(len(remaining) == EXPECTED_OUTPUT_ACTORS, f"Expected {EXPECTED_OUTPUT_ACTORS} output actors; found {len(remaining)}")
    require(not any(actor.get_actor_label().startswith("M01_RS01_Tree_") for actor in remaining), "Rejected PCG tree remains")

    yaws = Counter(round(float(row["after"]["rotation_degrees"][1]), 2) for row in result["city_placements"])
    scales = Counter(round(float(row["after"]["scale"][0]), 2) for row in result["city_placements"])
    row_spacing: dict[str, object] = {}
    minimum_gap = float("inf")
    maximum_equal_spacing = 0
    for row_index in range(3):
        row_values = sorted((row for row in result["city_placements"] if row["row"] == row_index), key=lambda row: row["structural_center_cm"][0])
        centers = [float(row["structural_center_cm"][0]) for row in row_values]
        deltas = [round(centers[index + 1] - centers[index], 1) for index in range(len(centers) - 1)]
        repeated = max(Counter(deltas).values()) if deltas else 0
        maximum_equal_spacing = max(maximum_equal_spacing, repeated)
        gaps = []
        for left, right in zip(row_values, row_values[1:]):
            left_max = float(left["structural_center_cm"][0]) + float(left["structural_extent_cm"][0])
            right_min = float(right["structural_center_cm"][0]) - float(right["structural_extent_cm"][0])
            gap = right_min - left_max
            gaps.append(gap)
            minimum_gap = min(minimum_gap, gap)
        row_spacing[str(row_index)] = {"center_deltas_cm": deltas, "equal_spacing_max_repetition": repeated, "aabb_gaps_cm": gaps}

    city_dark_glass = 0
    for placement, triplet in groups.items():
        component, _ = mesh_component(triplet["GLAZING"])
        city_dark_glass += sum(
            1 for index in range(component.get_num_materials()) if "M_ENV_Glass_Dark" in str(component.get_material(index).get_path_name())
        )
    bright_road_markings = sum(
        1
        for actor in hardscapes
        if "M_ENV_Road_Marking" in str(mesh_component(actor)[0].get_material(4).get_path_name())
    )
    result["quality_metrics"] = {
        "distinct_building_yaws": len(yaws),
        "distinct_uniform_scales": len(scales),
        "maximum_equal_spacing_repetition_per_row": maximum_equal_spacing,
        "minimum_adjacent_building_aabb_gap_cm": minimum_gap,
        "city_dark_glass_usage": city_dark_glass,
        "bright_road_marking_usage": bright_road_markings,
        "removed_rejected_tree_count": len(result["removed_tree_labels"]),
        "window_override_count": len(result["window_overrides"]),
        "road_marking_override_count": len(result["road_marking_overrides"]),
        "row_spacing": row_spacing,
    }
    require(len(yaws) >= 7, f"Insufficient yaw variation: {len(yaws)}")
    require(len(scales) >= 5, f"Insufficient scale variation: {len(scales)}")
    require(maximum_equal_spacing <= 2, f"Repeated equal spacing remains: {maximum_equal_spacing}")
    require(minimum_gap >= 250.0, f"Adjacent building gap below 250 cm: {minimum_gap}")
    require(city_dark_glass == 0, f"Dark city glass remains: {city_dark_glass}")
    require(bright_road_markings == 0, f"Bright road marking remains: {bright_road_markings}")
    require(len(result["window_overrides"]) == 27, "Window override count mismatch")
    require(len(result["road_marking_overrides"]) == 4, "Road marking override count mismatch")

    require(levels.save_current_level(), "Failed to save non-vegetation remediation map")
    require(OUTPUT_FILE.is_file(), "Fresh output map was not created")
    result["output_sha256"] = sha256(OUTPUT_FILE)
    result["input_sha256_after"] = sha256(INPUT_FILE)
    require(result["input_sha256_after"] == EXPECTED_INPUT_SHA256, "Accepted input map changed")
    result["classification"] = "PASSED_M01_PHOTOREAL_FOUNDATION_NONVEGETATION01_AUTOMATIC"
except Exception as exc:
    result["errors"].append(f"{type(exc).__name__}: {exc}")
    result["errors"].append(traceback.format_exc())
finally:
    if result["input_sha256_after"] is None and INPUT_FILE.is_file():
        result["input_sha256_after"] = sha256(INPUT_FILE)
    write_json_atomic(RECEIPT, result)
    print("SKYGUARD_M01_NONVEGETATION01_AUTHORING=" + str(result["classification"]))

if result["classification"] != "PASSED_M01_PHOTOREAL_FOUNDATION_NONVEGETATION01_AUTOMATIC":
    raise RuntimeError(str(result["errors"][0] if result["errors"] else "authoring failed"))
