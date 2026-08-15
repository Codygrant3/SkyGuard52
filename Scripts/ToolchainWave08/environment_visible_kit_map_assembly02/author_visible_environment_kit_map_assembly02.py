"""Assemble the accepted Mission 1 visible environment kit into a fresh map.

The accepted RealismStack03 map and imported EnvKit02 assets are read-only
authorities.  This script clones the map, replaces only the legacy visible
coast/city placeholders in the clone, grounds the production kit, and saves
one fresh review map for the subsequent mapped visual proof.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
ISOLATED = Path(r"D:\SG52T08_ENV01")
INPUT_ASSET = "/Game/ToolchainWave08/Environment/Lvl_M01_T08_EnvironmentRealismStack03"
OUTPUT_ASSET = "/Game/M01/Lvl_M01_VisibleEnvironmentKit02"
INPUT_FILE = ISOLATED / "Content/ToolchainWave08/Environment/Lvl_M01_T08_EnvironmentRealismStack03.umap"
OUTPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_VisibleEnvironmentKit02.umap"
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_VISIBLE_ENVIRONMENT_KIT_MAP_ASSEMBLY02/attempt_01"
RECEIPT = ATTEMPT / "assembly_receipt.json"
EXPECTED_INPUT_BYTES = 856016
EXPECTED_INPUT_SHA256 = "c68de75000c25569f38b9307fd8760cce85236e2f3166785350ea0c641de81e8"
EXPECTED_ACTOR_COUNT = 186
EXPECTED_REMOVED_COUNT = 99
EXPECTED_CREATED_COUNT = 92
EXPECTED_FINAL_COUNT = 179


ASSETS = {
    "ApartmentA": {
        "DETAILS": ("/Game/M01/EnvKit02/M01_APARTMENT_A/StaticMeshes/SM_M01_ApartmentA_DETAILS", 6),
        "GLAZING": ("/Game/M01/EnvKit02/M01_APARTMENT_A/StaticMeshes/SM_M01_ApartmentA_GLAZING", 3),
        "STRUCTURAL": ("/Game/M01/EnvKit02/M01_APARTMENT_A/StaticMeshes/SM_M01_ApartmentA_STRUCTURAL", 4),
    },
    "MidriseB": {
        "DETAILS": ("/Game/M01/EnvKit02/M01_MIDRISE_B/StaticMeshes/SM_M01_MidriseB_DETAILS", 6),
        "GLAZING": ("/Game/M01/EnvKit02/M01_MIDRISE_B/StaticMeshes/SM_M01_MidriseB_GLAZING", 3),
        "STRUCTURAL": ("/Game/M01/EnvKit02/M01_MIDRISE_B/StaticMeshes/SM_M01_MidriseB_STRUCTURAL", 5),
    },
    "CornerC": {
        "DETAILS": ("/Game/M01/EnvKit02/M01_CORNER_RESIDENCE_C/StaticMeshes/SM_M01_CornerC_DETAILS", 6),
        "GLAZING": ("/Game/M01/EnvKit02/M01_CORNER_RESIDENCE_C/StaticMeshes/SM_M01_CornerC_GLAZING", 3),
        "STRUCTURAL": ("/Game/M01/EnvKit02/M01_CORNER_RESIDENCE_C/StaticMeshes/SM_M01_CornerC_STRUCTURAL", 5),
    },
    "CoastalA": {
        "HARDSCAPE": ("/Game/M01/EnvKit02/M01_COASTAL_DISTRICT_A/StaticMeshes/SM_M01_CoastalA_HARDSCAPE", 6),
        "TERRAIN": ("/Game/M01/EnvKit02/M01_COASTAL_DISTRICT_A/StaticMeshes/SM_M01_CoastalA_TERRAIN", 1),
    },
    "LighthouseA": {
        "DETAILS": ("/Game/M01/EnvKit02/M01_LIGHTHOUSE_A/StaticMeshes/SM_M01_LighthouseA_DETAILS", 1),
        "GLAZING": ("/Game/M01/EnvKit02/M01_LIGHTHOUSE_A/StaticMeshes/SM_M01_LighthouseA_GLAZING", 1),
        "STRUCTURAL": ("/Game/M01/EnvKit02/M01_LIGHTHOUSE_A/StaticMeshes/SM_M01_LighthouseA_STRUCTURAL", 4),
    },
}

REMOVAL_PREFIX_COUNTS = {
    "M01_RS01_Beach_": 10,
    "M01_RS01_Seawall_": 20,
    "M01_RS01_Promenade_": 16,
    "M01_RS01_CoastalRoad_": 16,
    "M01_RS01_City_": 36,
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


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def prop(value, *names):
    for name in names:
        try:
            return value.get_editor_property(name)
        except Exception:
            if hasattr(value, name):
                return getattr(value, name)
    raise RuntimeError(f"Missing property {names} on {type(value).__name__}")


def vector(value):
    return [float(value.x), float(value.y), float(value.z)]


def find_exact(actors, label):
    matches = [actor for actor in actors if actor.get_actor_label() == label]
    require(len(matches) == 1, f"Expected exactly one actor {label}; found {len(matches)}")
    return matches[0]


def load_meshes():
    loaded = {}
    records = []
    for family, groups in ASSETS.items():
        loaded[family] = {}
        for group, (asset_path, expected_slots) in groups.items():
            mesh = unreal.load_asset(asset_path)
            require(isinstance(mesh, unreal.StaticMesh), f"StaticMesh unavailable: {asset_path}")
            slots = list(mesh.get_static_materials())
            require(len(slots) == expected_slots, f"Material-slot mismatch {asset_path}: {len(slots)} != {expected_slots}")
            bounds = mesh.get_bounds()
            loaded[family][group] = mesh
            records.append(
                {
                    "family": family,
                    "group": group,
                    "path": asset_path,
                    "material_slot_count": len(slots),
                    "material_slot_names": [str(prop(slot, "material_slot_name")) for slot in slots],
                    "bounds_origin_cm": vector(bounds.origin),
                    "bounds_extent_cm": vector(bounds.box_extent),
                }
            )
    require(len(records) == 14, f"Expected fourteen loaded StaticMeshes; found {len(records)}")
    require(sum(row["material_slot_count"] for row in records) == 54, "Accepted material-slot total changed")
    return loaded, records


def rotated_center_offset(bounds, yaw_degrees):
    radians = math.radians(float(yaw_degrees))
    cosine, sine = math.cos(radians), math.sin(radians)
    return (
        cosine * float(bounds.origin.x) - sine * float(bounds.origin.y),
        sine * float(bounds.origin.x) + cosine * float(bounds.origin.y),
    )


def rotated_extents(bounds, yaw_degrees):
    radians = math.radians(float(yaw_degrees))
    cosine, sine = abs(math.cos(radians)), abs(math.sin(radians))
    ex, ey = float(bounds.box_extent.x), float(bounds.box_extent.y)
    return cosine * ex + sine * ey, sine * ex + cosine * ey


def sample_ground(library, landscape, center_x, center_y, extent_x, extent_y):
    ex, ey = max(50.0, extent_x * 0.92), max(50.0, extent_y * 0.92)
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
    error = str(prop(sampled, "error"))
    require(success, f"Landscape footprint unsupported: {error}")
    require(supported == 1.0, f"Incomplete landscape footprint support: {supported}")
    require(delta <= 225.0, f"Landscape footprint delta exceeds 225 cm: {delta}")
    return {
        "mean_height_cm": float(prop(sampled, "mean_height_centimeters")),
        "minimum_height_cm": float(prop(sampled, "minimum_height_centimeters")),
        "maximum_height_cm": float(prop(sampled, "maximum_height_centimeters")),
        "height_delta_cm": delta,
        "supported_fraction": supported,
    }


def actor_location_for_center(mesh, center_x, center_y, target_bottom, yaw_degrees):
    bounds = mesh.get_bounds()
    offset_x, offset_y = rotated_center_offset(bounds, yaw_degrees)
    local_bottom = float(bounds.origin.z - bounds.box_extent.z)
    return unreal.Vector(center_x - offset_x, center_y - offset_y, target_bottom - local_bottom)


def spawn_mesh_actor(mesh, label, location, yaw_degrees, folder):
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.StaticMeshActor,
        location,
        unreal.Rotator(roll=0.0, pitch=0.0, yaw=float(yaw_degrees)),
    )
    require(actor is not None, f"Failed to spawn {label}")
    actor.set_actor_label(label)
    actor.set_folder_path(folder)
    component = actor.static_mesh_component
    require(component is not None, f"StaticMeshComponent missing on {label}")
    component.set_static_mesh(mesh)
    component.set_mobility(unreal.ComponentMobility.STATIC)
    component.set_editor_property("cast_shadow", True)
    return actor


def actor_record(actor, family, group, placement, ground=None):
    origin, extent = actor.get_actor_bounds(False)
    location = actor.get_actor_location()
    rotation = actor.get_actor_rotation()
    record = {
        "label": actor.get_actor_label(),
        "family": family,
        "group": group,
        "asset": actor.static_mesh_component.get_static_mesh().get_path_name(),
        "placement": placement,
        "location_cm": vector(location),
        "rotation_degrees": [float(rotation.pitch), float(rotation.yaw), float(rotation.roll)],
        "bounds_origin_cm": vector(origin),
        "bounds_extent_cm": vector(extent),
        "bounds_min_z_cm": float(origin.z - extent.z),
        "mobility": str(actor.static_mesh_component.get_editor_property("mobility")),
    }
    if ground is not None:
        record["grounding"] = ground
        record["grounding"]["gap_cm"] = record["bounds_min_z_cm"] - float(ground["target_bottom_cm"])
    return record


def spawn_family(loaded, family, instance_key, center_x, center_y, target_bottom, yaw, folder, grounding):
    structural_group = "STRUCTURAL"
    structural = loaded[family][structural_group]
    location = actor_location_for_center(structural, center_x, center_y, target_bottom, yaw)
    rows = []
    for group in sorted(loaded[family]):
        label = f"M01_VEK02_{instance_key}_{group}"
        actor = spawn_mesh_actor(loaded[family][group], label, location, yaw, folder)
        row_grounding = dict(grounding) if group == structural_group else None
        rows.append(actor_record(actor, family, group, instance_key, row_grounding))
    structural_row = next(row for row in rows if row["group"] == structural_group)
    require(abs(structural_row["grounding"]["gap_cm"]) <= 1.0, f"Grounding gap exceeds 1 cm: {structural_row['label']}")
    return rows


result = {
    "schema": "skyguard.m01-visible-environment-kit-map-assembly02.receipt.v1",
    "classification": "FAILED_WITH_EVIDENCE",
    "input_asset": INPUT_ASSET,
    "output_asset": OUTPUT_ASSET,
    "input_sha256_before": None,
    "input_sha256_after": None,
    "output_sha256": None,
    "actor_count_before": 0,
    "actor_count_after": 0,
    "removed_actor_labels": [],
    "removed_actor_counts": {},
    "loaded_assets": [],
    "created_actors": [],
    "district_seams_cm": [],
    "waterline_target_cm": None,
    "legacy_placeholder_families_remaining": [],
    "saved_assets": [],
    "error": None,
}

try:
    require(INPUT_FILE.is_file(), "Accepted RealismStack03 map is missing")
    require(INPUT_FILE.stat().st_size == EXPECTED_INPUT_BYTES, "Accepted RealismStack03 byte count changed")
    require(sha256(INPUT_FILE) == EXPECTED_INPUT_SHA256, "Accepted RealismStack03 hash changed")
    require(not OUTPUT_FILE.exists(), "Fresh output map file already exists")
    require(not unreal.EditorAssetLibrary.does_asset_exist(OUTPUT_ASSET), "Fresh output map asset already exists")
    result["input_sha256_before"] = sha256(INPUT_FILE)
    loaded, result["loaded_assets"] = load_meshes()

    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    actors_api = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    require(levels is not None and actors_api is not None, "Required editor subsystems are unavailable")
    require(levels.new_level_from_template(OUTPUT_ASSET, INPUT_ASSET), "Failed to clone accepted RealismStack03 map")
    actors = list(actors_api.get_all_level_actors())
    result["actor_count_before"] = len(actors)
    require(len(actors) == EXPECTED_ACTOR_COUNT, f"Expected {EXPECTED_ACTOR_COUNT} cloned actors; found {len(actors)}")

    landscape = find_exact(actors, "M01_A01_Landscape_Production")
    ocean = find_exact(actors, "M01_A01_WaterBodyOcean")
    old_lighthouse = find_exact(actors, "M01_RS01_Lighthouse_Hero")
    old_lighthouse_origin, old_lighthouse_extent = old_lighthouse.get_actor_bounds(False)
    old_lighthouse_bottom = float(old_lighthouse_origin.z - old_lighthouse_extent.z)
    ocean_z = float(ocean.get_actor_location().z)
    waterline_target = ocean_z + 65.0
    result["waterline_target_cm"] = waterline_target

    to_remove = []
    for prefix, expected_count in REMOVAL_PREFIX_COUNTS.items():
        matches = [actor for actor in actors if actor.get_actor_label().startswith(prefix)]
        require(len(matches) == expected_count, f"Legacy family count changed {prefix}: {len(matches)} != {expected_count}")
        result["removed_actor_counts"][prefix] = len(matches)
        to_remove.extend(matches)
    to_remove.append(old_lighthouse)
    require(len(to_remove) == EXPECTED_REMOVED_COUNT, f"Expected {EXPECTED_REMOVED_COUNT} legacy actors; found {len(to_remove)}")
    require(len(set(actor.get_path_name() for actor in to_remove)) == len(to_remove), "Legacy removal set contains duplicates")
    result["removed_actor_labels"] = sorted(actor.get_actor_label() for actor in to_remove)
    for actor in to_remove:
        require(actors_api.destroy_actor(actor), f"Failed to remove legacy actor {actor.get_actor_label()}")

    # Four exact 140 m coastal modules cover the full 560 m review corridor.
    terrain_mesh = loaded["CoastalA"]["TERRAIN"]
    terrain_bounds = terrain_mesh.get_bounds()
    district_centers_x = [3000.0, 17000.0, 31000.0, 45000.0]
    district_center_y = 5600.0
    terrain_rows = []
    for index, center_x in enumerate(district_centers_x):
        location = actor_location_for_center(terrain_mesh, center_x, district_center_y, waterline_target, 0.0)
        tile_rows = []
        for group in ("TERRAIN", "HARDSCAPE"):
            label = f"M01_VEK02_District_{index:02d}_{group}"
            actor = spawn_mesh_actor(loaded["CoastalA"][group], label, location, 0.0, "M01/VisibleEnvironmentKit02/Coast")
            grounding = {"target_bottom_cm": waterline_target, "basis": "ocean_z_plus_65cm"} if group == "TERRAIN" else None
            row = actor_record(actor, "CoastalA", group, f"District_{index:02d}", grounding)
            tile_rows.append(row)
            result["created_actors"].append(row)
        terrain_row = next(row for row in tile_rows if row["group"] == "TERRAIN")
        require(abs(terrain_row["grounding"]["gap_cm"]) <= 1.0, f"District terrain waterline gap exceeded: {index}")
        terrain_rows.append(terrain_row)

    terrain_rows.sort(key=lambda row: row["bounds_origin_cm"][0])
    for left, right in zip(terrain_rows, terrain_rows[1:]):
        left_max = left["bounds_origin_cm"][0] + left["bounds_extent_cm"][0]
        right_min = right["bounds_origin_cm"][0] - right["bounds_extent_cm"][0]
        gap = right_min - left_max
        require(abs(gap) <= 1.0, f"Coastal district seam exceeded 1 cm: {gap}")
        result["district_seams_cm"].append(gap)

    library = unreal.SkyguardMission01LandscapeGroundingLibrary
    require(library is not None, "Landscape grounding library is unavailable")
    family_cycles = (
        ("ApartmentA", "MidriseB", "CornerC"),
        ("CornerC", "ApartmentA", "MidriseB"),
        ("MidriseB", "CornerC", "ApartmentA"),
    )
    row_settings = ((2500.0, 10850.0), (3000.0, 14500.0), (2000.0, 18150.0))
    for row_index, (start_x, center_y) in enumerate(row_settings):
        for column in range(9):
            family = family_cycles[row_index][column % 3]
            center_x = start_x + column * 5500.0
            structural = loaded[family]["STRUCTURAL"]
            bounds = structural.get_bounds()
            extent_x, extent_y = rotated_extents(bounds, 0.0)
            sampled = sample_ground(library, landscape, center_x, center_y, extent_x, extent_y)
            grounding = dict(sampled)
            grounding.update({"target_bottom_cm": sampled["mean_height_cm"], "basis": "nine_point_landscape_footprint"})
            instance_key = f"City_R{row_index:02d}_C{column:02d}_{family}"
            result["created_actors"].extend(
                spawn_family(
                    loaded,
                    family,
                    instance_key,
                    center_x,
                    center_y,
                    sampled["mean_height_cm"],
                    0.0,
                    "M01/VisibleEnvironmentKit02/City",
                    grounding,
                )
            )

    lighthouse_grounding = {
        "target_bottom_cm": old_lighthouse_bottom,
        "basis": "accepted_legacy_lighthouse_ground_contact",
        "supported_fraction": 1.0,
        "height_delta_cm": 0.0,
    }
    result["created_actors"].extend(
        spawn_family(
            loaded,
            "LighthouseA",
            "Lighthouse_Hero",
            3200.0,
            7600.0,
            old_lighthouse_bottom,
            0.0,
            "M01/VisibleEnvironmentKit02/Landmarks",
            lighthouse_grounding,
        )
    )

    require(len(result["created_actors"]) == EXPECTED_CREATED_COUNT, f"Expected {EXPECTED_CREATED_COUNT} created actors; found {len(result['created_actors'])}")
    require(all("STATIC" in row["mobility"].upper() for row in result["created_actors"]), "A created environment actor is not static")
    remaining = list(actors_api.get_all_level_actors())
    result["actor_count_after"] = len(remaining)
    require(len(remaining) == EXPECTED_FINAL_COUNT, f"Expected {EXPECTED_FINAL_COUNT} final actors; found {len(remaining)}")
    result["legacy_placeholder_families_remaining"] = sorted(
        actor.get_actor_label()
        for actor in remaining
        if any(actor.get_actor_label().startswith(prefix) for prefix in REMOVAL_PREFIX_COUNTS)
        or actor.get_actor_label() == "M01_RS01_Lighthouse_Hero"
    )
    require(not result["legacy_placeholder_families_remaining"], "Legacy visible placeholders remain in the fresh map")
    require(len([actor for actor in remaining if actor.get_actor_label().startswith("M01_VEK02_")]) == EXPECTED_CREATED_COUNT, "Created actor label count changed")

    require(levels.save_current_level(), "Failed to save VisibleEnvironmentKit02 map")
    require(OUTPUT_FILE.is_file(), "VisibleEnvironmentKit02 map file was not created")
    result["saved_assets"] = [OUTPUT_ASSET]
    result["output_sha256"] = sha256(OUTPUT_FILE)
    result["input_sha256_after"] = sha256(INPUT_FILE)
    require(result["input_sha256_after"] == EXPECTED_INPUT_SHA256, "Accepted RealismStack03 map changed")
    result["classification"] = "PASSED_M01_VISIBLE_ENVIRONMENT_KIT_MAP_ASSEMBLY02_AUTOMATIC"
except Exception as exc:
    result["error"] = f"{type(exc).__name__}: {exc}"
finally:
    write_json(RECEIPT, result)

if result["classification"].startswith("PASSED_"):
    unreal.SystemLibrary.quit_editor()
else:
    raise RuntimeError(result["error"] or "Visible environment kit map assembly failed")
