"""Author the targeted Mission 1 Hero Street/Shore Cell03 correction.

Cell03 derives from the immutable Cell02 visual failure and corrects its recorded
causes in one fresh map: unsuitable prop pitch/roll, crushed fill lighting,
stretched asphalt, the white guide-contact mesh, incohesive water bindings, weak
city massing, and a blank rear facade. It does not promote runtime content and
does not fabricate the still-missing licensed vegetation or vehicle set.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import sys
import traceback
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
ISOLATED = Path(r"D:\SG52T08_ENV01")
PROJECT = ISOLATED / "Skyguard52.uproject"
PROJECT_BYTES = 3_703
PROJECT_SHA256 = "7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a"
INPUT_ASSET = "/Game/M01/Lvl_M01_HeroStreetShoreCell02"
INPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_HeroStreetShoreCell02.umap"
INPUT_BYTES = 747_443
INPUT_SHA256 = "5847609807972cfdf9b8d8d87f4c2f52aabaebfbbf68c9304404b5abb99f6622"
OUTPUT_ASSET = "/Game/M01/Lvl_M01_HeroStreetShoreCell03Recovery01"
OUTPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_HeroStreetShoreCell03Recovery01.umap"
MATERIAL_ROOT = "/Game/M01/HeroStreetShoreCell03Recovery01/Materials"
MATERIAL_DIRECTORY = ISOLATED / "Content/M01/HeroStreetShoreCell03Recovery01"
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_HERO_STREET_SHORE_CELL03_RECOVERY01/attempt_01"
RECEIPT = ATTEMPT / "authoring_receipt.json"

AUTHOR_FREEZE = ROOT / "Docs/AAA_Review/M01_HERO_STREET_SHORE_CELL02_AUTHORING_ATTEMPT01_ACCEPTANCE_FREEZE.json"
AUTHOR_FREEZE_BYTES = 3_483
AUTHOR_FREEZE_SHA256 = "5e698b23b8baa335710775bb0920e8df9cf650cf16b8f9088c018ede445710af"
VISUAL_FREEZE = ROOT / "Docs/AAA_Review/M01_HERO_STREET_SHORE_CELL02_VISUAL_PROOF01_ATTEMPT01_TERMINAL_FREEZE.json"
VISUAL_FREEZE_BYTES = 5_118
VISUAL_FREEZE_SHA256 = "65567b95e6441281fa1f74847fccfc3e76f6b9df1bec51b78e0a81e2177c2718"
VISUAL_REVIEW = ROOT / "Docs/AAA_Review/M01_HERO_STREET_SHORE_CELL02_VISUAL_PROOF01_DIRECT_VISUAL_REVIEW.json"
VISUAL_REVIEW_BYTES = 3_722
VISUAL_REVIEW_SHA256 = "07091598851c73a83fd96677782997adc8b2ecd07990d175b71a47770b83ba95"
CAMERAS = ROOT / "Docs/AAA_Review/M01_HERO_STREET_SHORE_CELL02_VISUAL_PROOF01_CAMERAS.json"
CAMERAS_BYTES = 2_035
CAMERAS_SHA256 = "a5355e03764b35f929dd6ce81fef0e169969d0b858c594d0abf31254033742b9"

EXPECTED_ACTORS_BEFORE = 122
EXPECTED_ACTORS_AFTER = 164

ASPHALT_SOURCE = "/Game/M01/EnvKit02/M01_COASTAL_DISTRICT_A/Materials/M_ENV_Asphalt_2K"
ASPHALT_DESTINATION = MATERIAL_ROOT + "/MI_M01_Cell03_Asphalt_Tiled"
ASPHALT_PARAMETERS = (
    "BaseColorTexture_OffsetScale",
    "MetallicRoughnessTexture_OffsetScale",
    "NormalTexture_OffsetScale",
)
TARGET_ASPHALT_TILING = (0.0, 0.0, 160.0, 12.0)
WINDOW_MATERIAL = "/Game/M01/GroundLightingCorrection04Recovery01/Materials/MI_M01_Window_Lifted"
GLASS_MATERIAL = "/Game/M01/GroundLightingCorrection04Recovery01/Materials/MI_M01_Glass_Lifted"
OCEAN_MATERIAL = "/Water/Materials/WaterSurface/Water_Material_Ocean"
FAR_WATER_MATERIAL = "/Water/Materials/WaterSurface/Water_FarMesh"

TARGET_SUN_INTENSITY = 6.5
TARGET_FILL_INTENSITY = 8.0
TARGET_SKYLIGHT_INTENSITY = 9.0
TARGET_LOWER_HEMISPHERE = (0.08, 0.11, 0.15, 1.0)
TARGET_EXPOSURE_BIAS = 1.05
TARGET_FILM_TOE = 0.55

FAMILY_LABELS = {
    "ApartmentA": {
        group: f"M01_ACA03R01_City_R01_C01_ApartmentA_{group}"
        for group in ("STRUCTURAL", "GLAZING", "DETAILS")
    },
    "MidriseB": {
        group: f"M01_ACA03R01_City_R00_C02_MidriseB_{group}"
        for group in ("STRUCTURAL", "GLAZING", "DETAILS")
    },
    "CornerC": {
        group: f"M01_ACA03R01_City_R01_C02_CornerC_{group}"
        for group in ("STRUCTURAL", "GLAZING", "DETAILS")
    },
}
FRONT_ROW = {
    "ApartmentA": (7_500.0, 10_800.0, 176.0, 0.94),
    "CornerC": (17_500.0, 10_950.0, 182.0, 1.01),
}
SECOND_ROW = (
    ("ApartmentA", 8_300.0, 14_500.0, 172.0, 1.02),
    ("CornerC", 16_500.0, 14_900.0, 188.0, 0.96),
)

UPRIGHT_PROP_PREFIXES = (
    "M01_HSSC01R01_Prop_",
    "M01_Promenade_Bollard_",
    "M01_Promenade_BicycleRack_",
    "M01_Promenade_LitterBin_",
    "M01_Promenade_UtilityCabinet_",
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


def require_file(path: Path, size: int, digest: str) -> dict[str, object]:
    require(path.is_file(), f"Authority missing: {path}")
    require(path.stat().st_size == size, f"Authority byte count changed: {path}")
    require(sha256(path) == digest, f"Authority hash changed: {path}")
    return record(path)


def write_json_atomic(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def vector(value: object) -> list[float]:
    return [float(value.x), float(value.y), float(value.z)]


def rgba(value: object) -> list[float]:
    return [float(value.r), float(value.g), float(value.b), float(value.a)]


def actor_state(actor: object) -> dict[str, object]:
    rotation = actor.get_actor_rotation()
    return {
        "location_cm": vector(actor.get_actor_location()),
        "rotation_deg": [float(rotation.roll), float(rotation.pitch), float(rotation.yaw)],
        "scale": vector(actor.get_actor_scale3d()),
    }


def verify_authorities() -> list[dict[str, object]]:
    review = json.loads(VISUAL_REVIEW.read_text(encoding="utf-8")) if VISUAL_REVIEW.is_file() else {}
    require(review.get("classification") == "FAILED_WITH_EVIDENCE", "Cell02 visual failure authority changed")
    require(review.get("next_gate") == "M01_HERO_STREET_SHORE_CELL03_TARGETED_ART_AND_COMPOSITION_CORRECTION",
            "Cell03 routing authority changed")
    return [
        require_file(PROJECT, PROJECT_BYTES, PROJECT_SHA256),
        require_file(INPUT_FILE, INPUT_BYTES, INPUT_SHA256),
        require_file(AUTHOR_FREEZE, AUTHOR_FREEZE_BYTES, AUTHOR_FREEZE_SHA256),
        require_file(VISUAL_FREEZE, VISUAL_FREEZE_BYTES, VISUAL_FREEZE_SHA256),
        require_file(VISUAL_REVIEW, VISUAL_REVIEW_BYTES, VISUAL_REVIEW_SHA256),
        require_file(CAMERAS, CAMERAS_BYTES, CAMERAS_SHA256),
    ]


def run_offline_contract_test() -> int:
    verify_authorities()
    require(not OUTPUT_FILE.exists(), "Fresh Cell03 output map already exists")
    require(not ATTEMPT.exists(), "Fresh Cell03 attempt already exists")
    require(not MATERIAL_DIRECTORY.exists(), "Fresh Cell03 material namespace already exists")
    require(set(FAMILY_LABELS) == {"ApartmentA", "MidriseB", "CornerC"}, "Building family contract changed")
    require(len(SECOND_ROW) == 2 and len(FRONT_ROW) == 2, "Cell03 placement contract changed")
    compile(Path(__file__).read_text(encoding="utf-8"), __file__, "exec")
    print("PASS_M01_HERO_STREET_SHORE_CELL03_RECOVERY01_AUTHORING_CONTRACT")
    return 0


def run_unreal() -> None:
    import unreal

    result: dict[str, object] = {
        "schema": "skyguard.m01-hero-street-shore-cell03-recovery01.authoring.v1",
        "classification": "FAILED_WITH_EVIDENCE",
        "runtime_promotion": False,
        "authorities": [],
        "input_map_before": None,
        "input_map_after": None,
        "output_map": None,
        "actor_count_before": None,
        "actor_count_after": None,
        "uprighted_props": [],
        "contact_correction": None,
        "proxy_tile_visibility": None,
        "asphalt_bindings": [],
        "created_materials": [],
        "asphalt_parameter_readback": [],
        "front_row_recomposition": [],
        "second_row_placements": [],
        "rear_window_actors": [],
        "glazing_bindings": [],
        "lighting": None,
        "water": None,
        "deferred": [
            "licensed_production_vegetation",
            "accepted_vehicle_set",
            "accepted_signage_and_utility_set",
            "accepted_landmark_hero",
        ],
        "rollback_manifest": {
            "created_map": OUTPUT_ASSET,
            "created_material_directory": MATERIAL_ROOT,
            "accepted_input_mutated": False,
            "runtime_promotion": False,
        },
        "error": None,
        "traceback": None,
    }

    def find_exact(actors: list[object], label: str):
        matches = [actor for actor in actors if actor.get_actor_label() == label]
        require(len(matches) == 1, f"Expected exactly one {label}; found {len(matches)}")
        return matches[0]

    def static_component(actor: object):
        component = actor.get_component_by_class(unreal.StaticMeshComponent)
        require(component is not None, f"StaticMeshComponent missing: {actor.get_actor_label()}")
        mesh = component.get_editor_property("static_mesh")
        require(mesh is not None, f"Static mesh missing: {actor.get_actor_label()}")
        return component, mesh

    def material_path(component: object, slot: int) -> str:
        material = component.get_material(slot)
        return material.get_path_name() if material is not None else ""

    def rotated_center_offset(bounds: object, yaw: float, scale: float) -> tuple[float, float]:
        angle = math.radians(yaw)
        cosine, sine = math.cos(angle), math.sin(angle)
        x = float(bounds.origin.x) * scale
        y = float(bounds.origin.y) * scale
        return cosine * x - sine * y, sine * x + cosine * y

    def actor_location_for_center(mesh: object, center_x: float, center_y: float,
                                  target_bottom: float, yaw: float, scale: float):
        bounds = mesh.get_bounds()
        offset_x, offset_y = rotated_center_offset(bounds, yaw, scale)
        local_bottom = float(bounds.origin.z - bounds.box_extent.z) * scale
        return unreal.Vector(center_x - offset_x, center_y - offset_y, target_bottom - local_bottom)

    def copy_materials(source_component: object, destination_component: object) -> None:
        require(destination_component.get_num_materials() == source_component.get_num_materials(),
                "Static-mesh material slot count changed while cloning")
        for slot in range(source_component.get_num_materials()):
            material = source_component.get_material(slot)
            if material is not None:
                destination_component.set_material(slot, material)

    def place_triplet(actors_api: object, sources: dict[str, object], placement: str,
                      center_x: float, center_y: float, yaw: float, scale: float,
                      target_bottom: float, folder: str, window_material: object,
                      glass_material: object) -> dict[str, object]:
        structural_component, structural_mesh = static_component(sources["STRUCTURAL"])
        del structural_component
        location = actor_location_for_center(structural_mesh, center_x, center_y, target_bottom, yaw, scale)
        spawned: dict[str, object] = {}
        for group in ("STRUCTURAL", "GLAZING", "DETAILS"):
            source_component, source_mesh = static_component(sources[group])
            actor = actors_api.spawn_actor_from_class(
                unreal.StaticMeshActor,
                location,
                unreal.Rotator(roll=0.0, pitch=0.0, yaw=yaw),
                False,
            )
            require(actor is not None, f"Failed to spawn {placement}_{group}")
            actor.set_actor_label(f"{placement}_{group}")
            actor.set_folder_path(folder)
            actor.set_actor_scale3d(unreal.Vector(scale, scale, scale))
            component = actor.get_component_by_class(unreal.StaticMeshComponent)
            require(component is not None, f"Spawned component missing: {placement}_{group}")
            component.set_static_mesh(source_mesh)
            component.set_mobility(unreal.ComponentMobility.STATIC)
            component.set_collision_profile_name("BlockAll" if group == "STRUCTURAL" else "NoCollision")
            copy_materials(source_component, component)
            if group == "GLAZING":
                require(component.get_num_materials() >= 2, f"Glazing material slots changed: {placement}")
                component.set_material(0, window_material)
                component.set_material(1, glass_material)
            spawned[group] = actor
        states = {group: actor_state(actor) for group, actor in spawned.items()}
        require(states["STRUCTURAL"] == states["GLAZING"] == states["DETAILS"],
                f"Triplet transform mismatch: {placement}")
        origin, extent = spawned["STRUCTURAL"].get_actor_bounds(False)
        require(abs(float(origin.z - extent.z) - target_bottom) <= 1.0,
                f"Triplet grounding failed: {placement}")
        return {
            "placement": placement,
            "center_cm": vector(origin),
            "extent_cm": vector(extent),
            "bottom_cm": float(origin.z - extent.z),
            "transform": states["STRUCTURAL"],
        }

    try:
        result["authorities"] = verify_authorities()
        result["input_map_before"] = record(INPUT_FILE)
        require(not OUTPUT_FILE.exists(), "Fresh Cell03 output package exists")
        require(not MATERIAL_DIRECTORY.exists(), "Fresh Cell03 material directory exists")
        require(not unreal.EditorAssetLibrary.does_asset_exist(OUTPUT_ASSET), "Fresh Cell03 map asset exists")
        require(not unreal.EditorAssetLibrary.does_asset_exist(ASPHALT_DESTINATION), "Fresh Cell03 asphalt asset exists")

        require(unreal.EditorAssetLibrary.make_directory(MATERIAL_ROOT), "Failed to create Cell03 material directory")
        require(unreal.EditorAssetLibrary.does_asset_exist(ASPHALT_SOURCE), "Accepted asphalt source is missing")
        created_asphalt = unreal.EditorAssetLibrary.duplicate_asset(ASPHALT_SOURCE, ASPHALT_DESTINATION)
        require(created_asphalt is not None, "Failed to duplicate Cell03 asphalt material")
        asphalt = unreal.load_asset(ASPHALT_DESTINATION)
        require(asphalt is not None and isinstance(asphalt, unreal.MaterialInstanceConstant),
                "Cell03 asphalt is not a material instance")
        setter_evidence = []
        for parameter in ASPHALT_PARAMETERS:
            reported_return = unreal.MaterialEditingLibrary.set_material_instance_vector_parameter_value(
                asphalt, parameter, unreal.LinearColor(*TARGET_ASPHALT_TILING)
            )
            actual_color = unreal.MaterialEditingLibrary.get_material_instance_vector_parameter_value(asphalt, parameter)
            actual = rgba(actual_color)
            require(
                len(actual) == 4 and all(abs(a - b) <= 0.0005 for a, b in zip(actual, TARGET_ASPHALT_TILING)),
                f"Asphalt tiling readback mismatch: {parameter}: {actual} != {TARGET_ASPHALT_TILING}",
            )
            setter_evidence.append({
                "parameter": parameter,
                "known_invalid_ue58_boolean_return": bool(reported_return),
                "readback": actual,
                "accepted_by_readback": True,
            })
        result["asphalt_parameter_readback"] = setter_evidence
        unreal.MaterialEditingLibrary.update_material_instance(asphalt)
        require(unreal.EditorAssetLibrary.save_loaded_asset(asphalt), "Failed to save Cell03 asphalt")
        asphalt_file = ISOLATED / "Content/M01/HeroStreetShoreCell03Recovery01/Materials/MI_M01_Cell03_Asphalt_Tiled.uasset"
        require(asphalt_file.is_file(), "Saved Cell03 asphalt package missing")
        result["created_materials"].append(record(asphalt_file))

        window_material = unreal.load_asset(WINDOW_MATERIAL)
        glass_material = unreal.load_asset(GLASS_MATERIAL)
        ocean_material = unreal.load_asset(OCEAN_MATERIAL)
        far_water_material = unreal.load_asset(FAR_WATER_MATERIAL)
        for asset, name in (
            (window_material, "lifted window material"),
            (glass_material, "lifted glass material"),
            (ocean_material, "UE ocean material"),
            (far_water_material, "UE far-water material"),
        ):
            require(asset is not None, f"Required {name} failed to load")

        levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        actors_api = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        require(levels is not None and actors_api is not None, "Required editor subsystems unavailable")
        require(levels.new_level_from_template(OUTPUT_ASSET, INPUT_ASSET), "Failed to clone Cell02 map")
        actors = list(actors_api.get_all_level_actors())
        result["actor_count_before"] = len(actors)
        require(len(actors) == EXPECTED_ACTORS_BEFORE, f"Cell02 actor count changed: {len(actors)}")
        by_label = {actor.get_actor_label(): actor for actor in actors}
        require(len(by_label) == len(actors), "Duplicate actor labels in Cell02 map")

        # Remove the diagnostic guide responsible for the bright polygonal shore strip.
        contact = find_exact(actors, "M01_ACA03R01_Corridor_CONTACT")
        contact_component, _ = static_component(contact)
        before_contact = {
            "visible": bool(contact_component.is_visible()),
            "hidden_in_game": bool(contact_component.get_editor_property("hidden_in_game")),
        }
        contact_component.set_visibility(False, True)
        contact_component.set_hidden_in_game(True)
        result["contact_correction"] = {
            "label": contact.get_actor_label(),
            "before": before_contact,
            "after": {
                "visible": bool(contact_component.is_visible()),
                "hidden_in_game": bool(contact_component.get_editor_property("hidden_in_game")),
            },
        }
        require(not result["contact_correction"]["after"]["visible"] and
                result["contact_correction"]["after"]["hidden_in_game"],
                "Guide-contact visibility correction failed")

        # Hide legacy procedural slab components so accepted corridor and UE Water own the presentation.
        director = find_exact(actors, "M01_A01_EnvironmentDirector")
        hidden_components = []
        for property_name in ("ocean_tiles", "beach_tiles", "land_tiles"):
            component = director.get_editor_property(property_name)
            require(component is not None, f"Director component missing: {property_name}")
            before = {"visible": bool(component.is_visible()), "hidden_in_game": bool(component.get_editor_property("hidden_in_game"))}
            component.set_visibility(False, True)
            component.set_hidden_in_game(True)
            after = {"visible": bool(component.is_visible()), "hidden_in_game": bool(component.get_editor_property("hidden_in_game"))}
            require(not after["visible"] and after["hidden_in_game"], f"Director proxy hiding failed: {property_name}")
            hidden_components.append({"component": property_name, "before": before, "after": after, "instances": int(component.get_instance_count())})
        result["proxy_tile_visibility"] = hidden_components

        # Replace the stretched road slot and any imported district asphalt slot.
        for label in ("M01_C06R01_Corridor_HARDSCAPE", "M01_HSSC02_CoastalA_HARDSCAPE"):
            actor = find_exact(actors, label)
            component, _ = static_component(actor)
            matched = 0
            for slot in range(component.get_num_materials()):
                before = material_path(component, slot)
                if label == "M01_C06R01_Corridor_HARDSCAPE" and slot == 4 or "Asphalt" in before:
                    component.set_material(slot, asphalt)
                    after = material_path(component, slot)
                    require(after == asphalt.get_path_name(), f"Cell03 asphalt binding failed: {label}:{slot}")
                    result["asphalt_bindings"].append({"label": label, "slot": slot, "before": before, "after": after})
                    matched += 1
            require(matched >= 1, f"No asphalt slot corrected on {label}")

        # Upright every visible small promenade prop in the hero cell, then ground it.
        for actor in actors:
            label = actor.get_actor_label()
            if not label.startswith(UPRIGHT_PROP_PREFIXES):
                continue
            if "StormDrain" in label:
                continue
            location = actor.get_actor_location()
            if not (5_500.0 <= float(location.x) <= 19_500.0 and 7_750.0 <= float(location.y) <= 9_950.0):
                continue
            component, _ = static_component(actor)
            before_state = actor_state(actor)
            rotation = actor.get_actor_rotation()
            actor.set_actor_rotation(unreal.Rotator(roll=0.0, pitch=0.0, yaw=float(rotation.yaw)), False)
            origin, extent = actor.get_actor_bounds(False)
            bottom = float(origin.z - extent.z)
            corrected_location = actor.get_actor_location()
            actor.set_actor_location(
                unreal.Vector(corrected_location.x, corrected_location.y, corrected_location.z + 71.0 - bottom),
                False,
                False,
            )
            after_origin, after_extent = actor.get_actor_bounds(False)
            after_bottom = float(after_origin.z - after_extent.z)
            require(abs(after_bottom - 71.0) <= 1.0, f"Prop grounding failed: {label}")
            after_rotation = actor.get_actor_rotation()
            require(abs(float(after_rotation.pitch)) <= 0.01 and abs(float(after_rotation.roll)) <= 0.01,
                    f"Prop remains tilted: {label}")
            result["uprighted_props"].append({
                "label": label,
                "before": before_state,
                "after": actor_state(actor),
                "bottom_after_cm": after_bottom,
                "material_slots": int(component.get_num_materials()),
            })
        require(len(result["uprighted_props"]) >= 15, "Too few hero-cell props were corrected")

        # Discover immutable source triplets before moving the two existing families.
        family_sources: dict[str, dict[str, object]] = {}
        for family, labels in FAMILY_LABELS.items():
            family_sources[family] = {group: find_exact(actors, label) for group, label in labels.items()}

        for family, (center_x, center_y, yaw, scale) in FRONT_ROW.items():
            triplet = family_sources[family]
            _, structural_mesh = static_component(triplet["STRUCTURAL"])
            location = actor_location_for_center(structural_mesh, center_x, center_y, 76.0, yaw, scale)
            before = actor_state(triplet["STRUCTURAL"])
            for group, actor in triplet.items():
                actor.set_actor_scale3d(unreal.Vector(scale, scale, scale))
                actor.set_actor_rotation(unreal.Rotator(roll=0.0, pitch=0.0, yaw=yaw), False)
                actor.set_actor_location(location, False, False)
                component, _ = static_component(actor)
                if group == "GLAZING":
                    component.set_material(0, window_material)
                    component.set_material(1, glass_material)
            origin, extent = triplet["STRUCTURAL"].get_actor_bounds(False)
            require(abs(float(origin.z - extent.z) - 76.0) <= 1.0, f"Front-row grounding failed: {family}")
            result["front_row_recomposition"].append({
                "family": family, "before": before, "after": actor_state(triplet["STRUCTURAL"]),
                "center_cm": vector(origin), "extent_cm": vector(extent),
            })

        for index, (family, center_x, center_y, yaw, scale) in enumerate(SECOND_ROW, start=1):
            result["second_row_placements"].append(place_triplet(
                actors_api,
                family_sources[family],
                f"M01_HSSC03_City_R01_C{index:02d}_{family}",
                center_x,
                center_y,
                yaw,
                scale,
                76.0,
                "M01/HeroStreetShoreCell03/City",
                window_material,
                glass_material,
            ))

        # Mirror the accepted front window modules onto the Midrise rear facade.
        front_windows = sorted(
            (actor for actor in actors if actor.get_actor_label().startswith("M01_HSSC01R01_Window_")),
            key=lambda actor: actor.get_actor_label(),
        )
        require(len(front_windows) == 36, f"Accepted front-window count changed: {len(front_windows)}")
        for source in front_windows:
            source_component, source_mesh = static_component(source)
            source_rotation = source.get_actor_rotation()
            actor = actors_api.spawn_actor_from_class(
                unreal.StaticMeshActor,
                source.get_actor_location(),
                unreal.Rotator(roll=0.0, pitch=0.0, yaw=float(source_rotation.yaw) + 180.0),
                False,
            )
            require(actor is not None, f"Failed to mirror rear window: {source.get_actor_label()}")
            actor.set_actor_label(source.get_actor_label().replace("M01_HSSC01R01_Window_", "M01_HSSC03_RearWindow_"))
            actor.set_folder_path("M01/HeroStreetShoreCell03/RearFacade")
            actor.set_actor_scale3d(source.get_actor_scale3d())
            component = actor.get_component_by_class(unreal.StaticMeshComponent)
            require(component is not None, "Mirrored rear-window component missing")
            component.set_static_mesh(source_mesh)
            component.set_mobility(unreal.ComponentMobility.STATIC)
            component.set_collision_profile_name("NoCollision")
            copy_materials(source_component, component)
            result["rear_window_actors"].append({"label": actor.get_actor_label(), "transform": actor_state(actor)})
        require(len(result["rear_window_actors"]) == 36, "Rear facade window count changed")

        # Apply lifted glazing consistently to all building triplets.
        for actor in list(actors_api.get_all_level_actors()):
            label = actor.get_actor_label()
            if not (label.startswith("M01_ACA03R01_City_") or label.startswith("M01_HSSC03_City_")):
                continue
            if not label.endswith("_GLAZING"):
                continue
            component, _ = static_component(actor)
            require(component.get_num_materials() >= 2, f"City glazing slot count changed: {label}")
            before = [material_path(component, slot) for slot in range(component.get_num_materials())]
            component.set_material(0, window_material)
            component.set_material(1, glass_material)
            result["glazing_bindings"].append({
                "label": label,
                "before": before,
                "after": [material_path(component, slot) for slot in range(component.get_num_materials())],
            })
        require(len(result["glazing_bindings"]) == 5, "Cell03 city glazing count changed")

        # Restore readable exterior light while retaining a bounded daylight presentation.
        sun = find_exact(actors, "M01_RS01_Sun")
        fill = find_exact(actors, "M01_PR01_FillSun")
        sky = find_exact(actors, "M01_RS01_SkyLight")
        post = find_exact(actors, "M01_RS01_PostProcess")
        sun_component = sun.get_component_by_class(unreal.DirectionalLightComponent)
        fill_component = fill.get_component_by_class(unreal.DirectionalLightComponent)
        sky_component = sky.get_component_by_class(unreal.SkyLightComponent)
        require(sun_component is not None and fill_component is not None and sky_component is not None,
                "Cell03 lighting components missing")
        settings = post.get_editor_property("settings")
        lighting_before = {
            "sun": float(sun_component.get_editor_property("intensity")),
            "fill": float(fill_component.get_editor_property("intensity")),
            "sky": float(sky_component.get_editor_property("intensity")),
            "exposure": float(settings.get_editor_property("auto_exposure_bias")),
            "toe": float(settings.get_editor_property("film_toe")),
        }
        sun_component.set_editor_property("intensity", TARGET_SUN_INTENSITY)
        fill_component.set_editor_property("intensity", TARGET_FILL_INTENSITY)
        fill_component.set_editor_property("cast_shadows", False)
        sky_component.set_mobility(unreal.ComponentMobility.MOVABLE)
        sky_component.set_editor_property("intensity", TARGET_SKYLIGHT_INTENSITY)
        sky_component.set_editor_property("real_time_capture", True)
        sky_component.set_editor_property("lower_hemisphere_is_black", False)
        sky_component.set_editor_property("lower_hemisphere_color", unreal.LinearColor(*TARGET_LOWER_HEMISPHERE))
        settings.set_editor_property("override_auto_exposure_bias", True)
        settings.set_editor_property("auto_exposure_bias", TARGET_EXPOSURE_BIAS)
        settings.set_editor_property("override_film_toe", True)
        settings.set_editor_property("film_toe", TARGET_FILM_TOE)
        post.set_editor_property("settings", settings)
        checked = post.get_editor_property("settings")
        result["lighting"] = {
            "before": lighting_before,
            "after": {
                "sun": float(sun_component.get_editor_property("intensity")),
                "fill": float(fill_component.get_editor_property("intensity")),
                "fill_cast_shadows": bool(fill_component.get_editor_property("cast_shadows")),
                "sky": float(sky_component.get_editor_property("intensity")),
                "lower_hemisphere": rgba(sky_component.get_editor_property("lower_hemisphere_color")),
                "exposure": float(checked.get_editor_property("auto_exposure_bias")),
                "toe": float(checked.get_editor_property("film_toe")),
            },
        }

        # Bind the matched UE Water near/far pair and preserve the existing wave object.
        ocean = find_exact(actors, "M01_A01_WaterBodyOcean")
        water_component = ocean.get_water_body_component()
        require(water_component is not None, "WaterBodyOceanComponent missing")
        near_before = water_component.get_water_material()
        waves_before = ocean.get_editor_property("water_waves")
        water_component.set_water_material(ocean_material)
        require(water_component.get_water_material().get_path_name() == ocean_material.get_path_name(),
                "Near-water binding failed")
        water_zone = find_exact(actors, "M01_A01_WaterZone")
        water_mesh_class = unreal.load_class(None, "/Script/Water.WaterMeshComponent")
        require(water_mesh_class is not None, "WaterMeshComponent class failed to load")
        water_mesh = water_zone.get_component_by_class(water_mesh_class)
        require(water_mesh is not None, "WaterMeshComponent missing")
        far_before = water_mesh.get_editor_property("far_distance_material")
        far_extent_before = float(water_mesh.get_editor_property("far_distance_mesh_extent"))
        water_mesh.set_editor_property("far_distance_material", far_water_material)
        require(water_mesh.get_editor_property("far_distance_material").get_path_name() == far_water_material.get_path_name(),
                "Far-water binding failed")
        require(ocean.get_editor_property("water_waves") == waves_before, "Existing ocean wave state changed")
        result["water"] = {
            "near_before": near_before.get_path_name() if near_before else None,
            "near_after": water_component.get_water_material().get_path_name(),
            "far_before": far_before.get_path_name() if far_before else None,
            "far_after": water_mesh.get_editor_property("far_distance_material").get_path_name(),
            "far_extent_before_cm": far_extent_before,
            "far_extent_after_cm": float(water_mesh.get_editor_property("far_distance_mesh_extent")),
            "waves_preserved": True,
        }

        final_actors = list(actors_api.get_all_level_actors())
        result["actor_count_after"] = len(final_actors)
        require(len(final_actors) == EXPECTED_ACTORS_AFTER, f"Cell03 actor count changed: {len(final_actors)}")
        require(sum(actor.get_actor_label().startswith("M01_HSSC03_RearWindow_") for actor in final_actors) == 36,
                "Rear-window runtime count changed")
        require(sum(actor.get_actor_label().startswith("M01_HSSC03_City_") for actor in final_actors) == 6,
                "Second-row city actor count changed")
        require(levels.save_current_level(), "Failed to save Cell03 map")
        require(OUTPUT_FILE.is_file(), "Cell03 output map is missing")
        result["output_map"] = record(OUTPUT_FILE)
        result["input_map_after"] = record(INPUT_FILE)
        require(result["input_map_after"]["sha256"] == INPUT_SHA256, "Immutable Cell02 input changed")
        result["classification"] = "PASSED_M01_HERO_STREET_SHORE_CELL03_RECOVERY01_READY_FOR_D3D12_MAPPED_VISUAL_PROOF"
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
        raise RuntimeError(result["error"] or "Cell03 authoring failed")


if "--offline-contract-test" in sys.argv:
    raise SystemExit(run_offline_contract_test())

run_unreal()
