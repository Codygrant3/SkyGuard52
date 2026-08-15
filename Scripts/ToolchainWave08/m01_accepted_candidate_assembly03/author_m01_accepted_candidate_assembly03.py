"""Author a fresh Mission 1 map from accepted production candidates.

This gate is intentionally structural. It removes presentation patterns already
rejected by full-resolution mapped review, preserves accepted candidate assets,
and saves a new reversible map. It does not promote runtime content.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import sys
import traceback
from collections import Counter
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
ISOLATED = Path(r"D:\SG52T08_ENV01")
PROJECT = ISOLATED / "Skyguard52.uproject"
PROJECT_BYTES = 3_703
PROJECT_SHA256 = "7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a"

INPUT_ASSET = (
    "/Game/M01/"
    "Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01Recovery01_"
    "PromenadeBollards01_BicycleRacks01_UtilityCabinets01Recovery01_"
    "StormDrains01_LitterBins01"
)
INPUT_FILE = ISOLATED / (
    "Content/M01/"
    "Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01Recovery01_"
    "PromenadeBollards01_BicycleRacks01_UtilityCabinets01Recovery01_"
    "StormDrains01_LitterBins01.umap"
)
INPUT_BYTES = 813_648
INPUT_SHA256 = "3bc0fdb85429de7cd471a1ba5d305caab9d8e6f554e52d4f7cf4ef138c741ce2"

OUTPUT_ASSET = "/Game/M01/Lvl_M01_AcceptedCandidateAssembly03"
OUTPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_AcceptedCandidateAssembly03.umap"
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_ACCEPTED_CANDIDATE_ASSEMBLY03/attempt_01"
RECEIPT = ATTEMPT / "authoring_receipt.json"

CONTACT_MESH_PATH = (
    "/Game/M01/CoastalCorridorC06R01/"
    "M01_CoastalCorridor_C06R01_UNREAL_READY/StaticMeshes/"
    "SM_M01_CoastalCorridor_C06R01_CONTACT."
    "SM_M01_CoastalCorridor_C06R01_CONTACT"
)
WINDOW_MATERIAL_PATH = (
    "/Game/M01/GroundLightingCorrection04Recovery01/Materials/"
    "MI_M01_Window_Lifted.MI_M01_Window_Lifted"
)
GLASS_MATERIAL_PATH = (
    "/Game/M01/GroundLightingCorrection04Recovery01/Materials/"
    "MI_M01_Glass_Lifted.MI_M01_Glass_Lifted"
)

EXPECTED_INPUT_ACTORS = 148
EXPECTED_CITY_GROUPS = 27
EXPECTED_OUTPUT_CITY_GROUPS = 18
EXPECTED_PROP_COUNTS = {
    "M01_Promenade_Bollard_": 13,
    "M01_Promenade_BicycleRack_": 8,
    "M01_Promenade_UtilityCabinet_": 5,
    "M01_Promenade_StormDrain_": 12,
    "M01_Promenade_LitterBin_": 10,
}
EXPECTED_OUTPUT_ACTORS = 119

CITY_PATTERN = re.compile(
    r"^(?P<placement>M01_VEK02_City_R(?P<row>\d{2})_C(?P<column>\d{2})_"
    r"(?P<family>ApartmentA|MidriseB|CornerC))_"
    r"(?P<group>STRUCTURAL|GLAZING|DETAILS)$"
)
LIGHTHOUSE_PATTERN = re.compile(
    r"^M01_VEK02_Lighthouse_Hero_(STRUCTURAL|GLAZING|DETAILS)$"
)

# Irregular, staggered coastal frontage.  Centers are in centimeters and stay
# within the accepted corridor's -4 km to 54 km X support and urban-side Y.
LAYOUT = (
    # row, column, family, center_x, center_y, yaw, uniform scale
    (0, 0, "ApartmentA", -800.0, 11100.0, 176.0, 1.00),
    (0, 1, "CornerC", 5200.0, 11400.0, 183.0, 0.96),
    (0, 2, "MidriseB", 11700.0, 10950.0, 178.0, 1.04),
    (0, 3, "ApartmentA", 18350.0, 11550.0, 185.0, 0.94),
    (0, 4, "MidriseB", 25300.0, 11050.0, 174.0, 1.02),
    (0, 5, "CornerC", 32200.0, 11650.0, 181.0, 1.00),
    (0, 6, "ApartmentA", 38750.0, 10850.0, 177.0, 1.05),
    (0, 7, "MidriseB", 45600.0, 11450.0, 184.0, 0.97),
    (0, 8, "CornerC", 52000.0, 11000.0, 179.0, 1.01),
    (1, 0, "MidriseB", 2100.0, 15050.0, 182.0, 0.95),
    (1, 1, "ApartmentA", 9100.0, 14600.0, 175.0, 1.03),
    (1, 2, "CornerC", 16400.0, 15300.0, 186.0, 0.98),
    (1, 3, "MidriseB", 24050.0, 14750.0, 177.0, 1.00),
    (1, 4, "ApartmentA", 31600.0, 15400.0, 183.0, 0.96),
    (1, 5, "CornerC", 39200.0, 14650.0, 174.0, 1.04),
    (1, 6, "MidriseB", 47000.0, 15250.0, 181.0, 0.97),
    (2, 0, "CornerC", 11200.0, 18750.0, 178.0, 0.95),
    (2, 1, "MidriseB", 35500.0, 18650.0, 184.0, 1.02),
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def record(path: Path) -> dict[str, object]:
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)}


def write_json_atomic(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    os.replace(temporary, path)


def vector(value: object) -> list[float]:
    return [float(value.x), float(value.y), float(value.z)]


def transform_state(actor: object) -> dict[str, object]:
    location = actor.get_actor_location()
    rotation = actor.get_actor_rotation()
    scale = actor.get_actor_scale3d()
    return {
        "location_cm": vector(location),
        "rotation_degrees": [
            float(rotation.pitch),
            float(rotation.yaw),
            float(rotation.roll),
        ],
        "scale": vector(scale),
    }


def validate_authorities() -> None:
    require(PROJECT.is_file(), "Isolated project is missing")
    require(PROJECT.stat().st_size == PROJECT_BYTES, "Isolated project bytes changed")
    require(sha256(PROJECT) == PROJECT_SHA256, "Isolated project hash changed")
    require(INPUT_FILE.is_file(), "Accepted candidate-rich input map is missing")
    require(INPUT_FILE.stat().st_size == INPUT_BYTES, "Accepted input-map bytes changed")
    require(sha256(INPUT_FILE) == INPUT_SHA256, "Accepted input-map hash changed")


def rotated_center_offset(bounds: object, yaw: float, scale: float) -> tuple[float, float]:
    angle = math.radians(yaw)
    cosine, sine = math.cos(angle), math.sin(angle)
    x = float(bounds.origin.x) * scale
    y = float(bounds.origin.y) * scale
    return cosine * x - sine * y, sine * x + cosine * y


def actor_location_for_center(
    mesh: object,
    center_x: float,
    center_y: float,
    target_bottom: float,
    yaw: float,
    scale: float,
):
    import unreal

    bounds = mesh.get_bounds()
    offset_x, offset_y = rotated_center_offset(bounds, yaw, scale)
    local_bottom = float(bounds.origin.z - bounds.box_extent.z) * scale
    return unreal.Vector(
        center_x - offset_x,
        center_y - offset_y,
        target_bottom - local_bottom,
    )


def corridor_surface_z_cm(x_cm: float, y_cm: float) -> float:
    x = x_cm / 100.0
    y = y_cm / 100.0
    long_wave = 0.045 * math.sin(x / 72.0) + 0.025 * math.sin(x / 19.0 + 0.7)
    shore = 38.0 + 2.45 * math.sin(x / 47.0) + 0.82 * math.sin(x / 13.0 + 0.4)
    boundaries = [
        (18.0, -1.25),
        (shore, -0.54 + long_wave),
        (shore + 10.0 + 0.65 * math.sin(x / 23.0), -0.10 + long_wave),
        (shore + 29.0 + 1.35 * math.sin(x / 39.0 + 0.8), 0.42 + long_wave),
        (78.0 + 0.62 * math.sin(x / 61.0), 0.70 + long_wave * 0.35),
        (86.0, 0.72 + long_wave * 0.20),
        (100.0, 0.56 + long_wave * 0.15),
        (104.0, 0.72 + long_wave * 0.15),
    ]
    if y >= 104.0:
        return (0.76 + 0.025 * math.sin(x / 31.0)) * 100.0
    for (left_y, left_z), (right_y, right_z) in zip(boundaries, boundaries[1:]):
        if left_y <= y <= right_y:
            alpha = (y - left_y) / max(0.0001, right_y - left_y)
            return (left_z + (right_z - left_z) * alpha) * 100.0
    return boundaries[0][1] * 100.0


def static_mesh_component(actor: object):
    import unreal

    component = actor.get_component_by_class(unreal.StaticMeshComponent)
    require(component is not None, f"StaticMeshComponent missing: {actor.get_actor_label()}")
    mesh = component.get_editor_property("static_mesh")
    require(mesh is not None, f"StaticMesh missing: {actor.get_actor_label()}")
    return component, mesh


def set_director_proxy_tiles_hidden(director: object) -> dict[str, object]:
    # The three inherited HISM surfaces are obsolete presentation proxies in this
    # assembly. Hiding them is reversible and avoids another overlapping slab.
    hidden = []
    for property_name in ("ocean_tiles", "beach_tiles", "land_tiles"):
        component = director.get_editor_property(property_name)
        require(component is not None, f"Director component missing: {property_name}")
        instance_count = int(component.get_instance_count())
        component.set_visibility(False, True)
        component.set_hidden_in_game(True)
        hidden.append(
            {
                "property": property_name,
                "instance_count": instance_count,
                "visible": bool(component.is_visible()),
                "hidden_in_game": bool(component.get_editor_property("hidden_in_game")),
            }
        )
    require(all(not row["visible"] and row["hidden_in_game"] for row in hidden), "Proxy tile visibility correction failed")
    return {"director": director.get_actor_label(), "components": hidden}


def run_offline_contract_test() -> int:
    validate_authorities()
    require(len(LAYOUT) == EXPECTED_OUTPUT_CITY_GROUPS, "Layout count changed")
    require(len({(row[0], row[1]) for row in LAYOUT}) == len(LAYOUT), "Duplicate layout cells")
    require(all(row[2] in {"ApartmentA", "MidriseB", "CornerC"} for row in LAYOUT), "Unknown family in layout")
    require(not OUTPUT_FILE.exists(), "Fresh output map already exists")
    require(not ATTEMPT.exists(), "Fresh attempt namespace already exists")
    compile(Path(__file__).read_text(encoding="utf-8"), __file__, "exec")
    print("PASS_M01_ACCEPTED_CANDIDATE_ASSEMBLY03_OFFLINE_CONTRACT")
    return 0


def run_unreal() -> None:
    import unreal

    result: dict[str, object] = {
        "schema": "skyguard.m01-accepted-candidate-assembly03.authoring.v1",
        "classification": "FAILED_WITH_EVIDENCE",
        "input_asset": INPUT_ASSET,
        "output_asset": OUTPUT_ASSET,
        "input_map_before": None,
        "input_map_after": None,
        "output_map": None,
        "actor_count_before": None,
        "actor_count_after": None,
        "removed_labels": [],
        "retained_prop_counts": {},
        "proxy_tile_visibility": None,
        "contact_actor": None,
        "city_placements": [],
        "quality_metrics": {},
        "deferred_items": [
            "production_vegetation_until_governed_nonproxy_library_is_accepted",
            "lighthouse_hero_until_faceting_is_refined",
            "hero_window_bay_until_architecturally_integrated_into_a_matching_facade",
            "mapped_D3D12_visual_acceptance",
        ],
        "rollback_manifest": {
            "created_map": OUTPUT_ASSET,
            "accepted_input_mutated": False,
            "runtime_promotion": False,
        },
        "error": None,
        "traceback": None,
    }

    try:
        validate_authorities()
        result["input_map_before"] = record(INPUT_FILE)
        require(not OUTPUT_FILE.exists(), "Fresh output-map file exists")
        require(not unreal.EditorAssetLibrary.does_asset_exist(OUTPUT_ASSET), "Fresh output-map asset exists")

        levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        actors_api = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        require(levels is not None and actors_api is not None, "Required editor subsystems unavailable")
        require(levels.new_level_from_template(OUTPUT_ASSET, INPUT_ASSET), "Failed to clone accepted input map")
        actors = list(actors_api.get_all_level_actors())
        result["actor_count_before"] = len(actors)
        require(len(actors) == EXPECTED_INPUT_ACTORS, f"Input actor count changed: {len(actors)}")

        by_label = {actor.get_actor_label(): actor for actor in actors}
        require(len(by_label) == len(actors), "Duplicate actor labels in accepted input map")
        director = by_label.get("M01_A01_EnvironmentDirector")
        require(director is not None, "Mission 1 environment director missing")
        result["proxy_tile_visibility"] = set_director_proxy_tiles_hidden(director)

        # Remove only previously rejected presentation instances. Accepted assets
        # remain untouched on disk and can be reintroduced in later fresh maps.
        removals = []
        city_groups: dict[str, dict[str, object]] = {}
        city_metadata: dict[str, dict[str, object]] = {}
        for actor in actors:
            label = actor.get_actor_label()
            match = CITY_PATTERN.match(label)
            if match:
                placement = match.group("placement")
                city_groups.setdefault(placement, {})[match.group("group")] = actor
                city_metadata[placement] = {"family": match.group("family")}
                removals.append(actor)
            elif LIGHTHOUSE_PATTERN.match(label):
                removals.append(actor)
            elif label.startswith("M01_RS01_Tree_"):
                removals.append(actor)
        require(len(city_groups) == EXPECTED_CITY_GROUPS, f"Expected {EXPECTED_CITY_GROUPS} inherited city groups; found {len(city_groups)}")
        require(all(set(group) == {"STRUCTURAL", "GLAZING", "DETAILS"} for group in city_groups.values()), "Inherited city triplet incomplete")
        lighthouse_labels = [actor.get_actor_label() for actor in removals if LIGHTHOUSE_PATTERN.match(actor.get_actor_label())]
        require(len(lighthouse_labels) == 3, f"Expected three inherited lighthouse actors; found {len(lighthouse_labels)}")
        result["removed_labels"] = sorted(actor.get_actor_label() for actor in removals)
        require(len(result["removed_labels"]) == 84, f"Unexpected removal count: {len(result['removed_labels'])}")
        for actor in removals:
            require(actors_api.destroy_actor(actor), f"Failed to remove rejected presentation actor: {actor.get_actor_label()}")

        # Preserve and validate all accepted repeated props already staged.
        remaining = list(actors_api.get_all_level_actors())
        for prefix, expected in EXPECTED_PROP_COUNTS.items():
            count = sum(
                1
                for actor in remaining
                if actor.get_actor_label().startswith(prefix)
                and actor.get_actor_label()[len(prefix) :].isdigit()
            )
            result["retained_prop_counts"][prefix] = count
            require(count == expected, f"Accepted prop count changed for {prefix}: {count}")

        # Add the accepted CONTACT semantic group omitted by the original import
        # integration. It is a shoreline-contact aid, not a replacement ocean.
        contact_mesh = unreal.load_asset(CONTACT_MESH_PATH)
        require(contact_mesh is not None and isinstance(contact_mesh, unreal.StaticMesh), "Accepted CONTACT mesh failed to load")
        contact = actors_api.spawn_actor_from_class(
            unreal.StaticMeshActor,
            unreal.Vector(0.0, 0.0, 0.0),
            unreal.Rotator(),
            False,
        )
        require(contact is not None, "Failed to spawn accepted CONTACT group")
        contact.set_actor_label("M01_ACA03_Corridor_CONTACT")
        contact.set_folder_path("M01/AcceptedCandidates/CoastalCorridor")
        contact.set_actor_scale3d(unreal.Vector(1.0, -1.0, 1.0))
        contact_component = contact.get_component_by_class(unreal.StaticMeshComponent)
        require(contact_component is not None, "CONTACT StaticMeshComponent missing")
        contact_component.set_static_mesh(contact_mesh)
        contact_component.set_mobility(unreal.ComponentMobility.STATIC)
        contact_component.set_collision_profile_name("NoCollision")
        contact_origin, contact_extent = contact.get_actor_bounds(False)
        result["contact_actor"] = {
            "label": contact.get_actor_label(),
            "mesh": contact_mesh.get_path_name(),
            "transform": transform_state(contact),
            "bounds_origin_cm": vector(contact_origin),
            "bounds_extent_cm": vector(contact_extent),
            "material_slot_count": int(contact_component.get_num_materials()),
        }
        require(2500.0 <= float(contact_origin.y - contact_extent.y) <= 6500.0, "CONTACT shoreline bound is outside the accepted coastal band")

        # Reuse the accepted imported building meshes, but not the rejected 3x9
        # placement pattern. Source triplets are discovered from inherited actors.
        family_sources: dict[str, dict[str, object]] = {}
        for placement, triplet in city_groups.items():
            family = city_metadata[placement]["family"]
            if family not in family_sources:
                family_sources[family] = {}
                for group_name, actor in triplet.items():
                    component, mesh = static_mesh_component(actor)
                    family_sources[family][group_name] = mesh
        require(set(family_sources) == {"ApartmentA", "MidriseB", "CornerC"}, "Accepted family mesh authority incomplete")

        window_material = unreal.load_asset(WINDOW_MATERIAL_PATH)
        glass_material = unreal.load_asset(GLASS_MATERIAL_PATH)
        require(window_material is not None and glass_material is not None, "Lifted glazing materials failed to load")

        placed_bounds: list[dict[str, object]] = []
        for row, column, family, center_x, center_y, yaw, scale in LAYOUT:
            triplet: dict[str, object] = {}
            structural_mesh = family_sources[family]["STRUCTURAL"]
            target_bottom = corridor_surface_z_cm(center_x, center_y)
            location = actor_location_for_center(
                structural_mesh,
                center_x,
                center_y,
                target_bottom,
                yaw,
                scale,
            )
            placement = f"M01_ACA03_City_R{row:02d}_C{column:02d}_{family}"
            for group_name in ("STRUCTURAL", "GLAZING", "DETAILS"):
                mesh = family_sources[family][group_name]
                actor = actors_api.spawn_actor_from_class(
                    unreal.StaticMeshActor,
                    location,
                    unreal.Rotator(roll=0.0, pitch=0.0, yaw=yaw),
                    False,
                )
                require(actor is not None, f"Failed to spawn {placement}_{group_name}")
                actor.set_actor_label(f"{placement}_{group_name}")
                actor.set_folder_path("M01/AcceptedCandidates/City")
                actor.set_actor_scale3d(unreal.Vector(scale, scale, scale))
                component = actor.get_component_by_class(unreal.StaticMeshComponent)
                require(component is not None, f"StaticMeshComponent missing: {placement}_{group_name}")
                component.set_static_mesh(mesh)
                component.set_mobility(unreal.ComponentMobility.STATIC)
                component.set_collision_profile_name("BlockAll" if group_name == "STRUCTURAL" else "NoCollision")
                if group_name == "GLAZING":
                    require(component.get_num_materials() == 3, f"Unexpected glazing slots: {placement}")
                    component.set_material(0, window_material)
                    component.set_material(1, glass_material)
                triplet[group_name] = actor

            states = {name: transform_state(actor) for name, actor in triplet.items()}
            require(states["STRUCTURAL"] == states["GLAZING"] == states["DETAILS"], f"Triplet transform mismatch: {placement}")
            origin, extent = triplet["STRUCTURAL"].get_actor_bounds(False)
            bottom = float(origin.z - extent.z)
            require(abs(bottom - target_bottom) <= 1.0, f"Building grounding gap: {placement} -> {bottom-target_bottom}")
            bounds_row = {
                "placement": placement,
                "row": row,
                "column": column,
                "family": family,
                "center_cm": vector(origin),
                "extent_cm": vector(extent),
                "target_bottom_cm": target_bottom,
                "ground_gap_cm": bottom - target_bottom,
                "transform": states["STRUCTURAL"],
                "material_slots": {
                    "structural": int(triplet["STRUCTURAL"].get_component_by_class(unreal.StaticMeshComponent).get_num_materials()),
                    "glazing": int(triplet["GLAZING"].get_component_by_class(unreal.StaticMeshComponent).get_num_materials()),
                    "details": int(triplet["DETAILS"].get_component_by_class(unreal.StaticMeshComponent).get_num_materials()),
                },
            }
            placed_bounds.append(bounds_row)
            result["city_placements"].append(bounds_row)

        # Fail closed on same-row intersections and excessive regularity.
        minimum_gap = float("inf")
        row_deltas: dict[str, list[float]] = {}
        maximum_equal_spacing_repetition = 0
        for row in sorted({int(item["row"]) for item in placed_bounds}):
            items = sorted(
                (item for item in placed_bounds if int(item["row"]) == row),
                key=lambda item: float(item["center_cm"][0]),
            )
            deltas = [
                round(float(right["center_cm"][0]) - float(left["center_cm"][0]), 1)
                for left, right in zip(items, items[1:])
            ]
            row_deltas[str(row)] = deltas
            if deltas:
                maximum_equal_spacing_repetition = max(
                    maximum_equal_spacing_repetition,
                    max(Counter(deltas).values()),
                )
            for left, right in zip(items, items[1:]):
                left_max = float(left["center_cm"][0]) + float(left["extent_cm"][0])
                right_min = float(right["center_cm"][0]) - float(right["extent_cm"][0])
                minimum_gap = min(minimum_gap, right_min - left_max)
        require(minimum_gap >= 225.0, f"Same-row building clearance below 225 cm: {minimum_gap}")
        require(maximum_equal_spacing_repetition <= 1, f"Repeated grid spacing remains: {maximum_equal_spacing_repetition}")

        output_actors = list(actors_api.get_all_level_actors())
        result["actor_count_after"] = len(output_actors)
        require(len(output_actors) == EXPECTED_OUTPUT_ACTORS, f"Output actor count changed: {len(output_actors)}")
        require(not any(CITY_PATTERN.match(actor.get_actor_label()) for actor in output_actors), "Rejected city labels remain")
        require(not any(LIGHTHOUSE_PATTERN.match(actor.get_actor_label()) for actor in output_actors), "Rejected lighthouse hero remains")
        require(sum(1 for actor in output_actors if actor.get_actor_label().startswith("M01_ACA03_City_") and actor.get_actor_label().endswith("_STRUCTURAL")) == EXPECTED_OUTPUT_CITY_GROUPS, "Assembly03 city count mismatch")
        result["quality_metrics"] = {
            "accepted_city_group_count": EXPECTED_OUTPUT_CITY_GROUPS,
            "accepted_corridor_contact_count": 1,
            "proxy_tile_component_count_hidden": 3,
            "rejected_lighthouse_actor_count_removed": 3,
            "rejected_legacy_city_actor_count_removed": 81,
            "distinct_yaws": len({round(float(item["transform"]["rotation_degrees"][1]), 1) for item in placed_bounds}),
            "distinct_scales": len({round(float(item["transform"]["scale"][0]), 2) for item in placed_bounds}),
            "minimum_same_row_aabb_gap_cm": minimum_gap,
            "maximum_equal_spacing_repetition": maximum_equal_spacing_repetition,
            "row_center_deltas_cm": row_deltas,
            "runtime_promotion": False,
        }
        require(result["quality_metrics"]["distinct_yaws"] >= 9, "Insufficient authored yaw variation")
        require(result["quality_metrics"]["distinct_scales"] >= 7, "Insufficient authored scale variation")

        require(levels.save_current_level(), "Failed to save Assembly03 map")
        require(OUTPUT_FILE.is_file(), "Assembly03 output map not created")
        result["output_map"] = record(OUTPUT_FILE)
        result["input_map_after"] = record(INPUT_FILE)
        require(result["input_map_after"]["sha256"] == INPUT_SHA256, "Accepted input map mutated")
        result["classification"] = "PASSED_M01_ACCEPTED_CANDIDATE_ASSEMBLY03_READY_FOR_STRUCTURAL_ADJUDICATION"
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        result["traceback"] = traceback.format_exc()
    finally:
        if result["input_map_after"] is None and INPUT_FILE.is_file():
            result["input_map_after"] = record(INPUT_FILE)
        write_json_atomic(RECEIPT, result)

    if result["classification"].startswith("PASSED_"):
        unreal.SystemLibrary.quit_editor()
    else:
        raise RuntimeError(result["error"] or "Assembly03 authoring failed")


if "--offline-contract-test" in sys.argv:
    raise SystemExit(run_offline_contract_test())

run_unreal()
