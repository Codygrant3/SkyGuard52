"""Author the Stage 7A Mission 1 production hero corridor in a fresh map."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import traceback
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
ISOLATED = Path(r"D:\SG52T08_ENV01")
HERE = ROOT / "Scripts/ToolchainWave08/m01_visible_environment_stage07a_hero_corridor01"
CONTRACT_PATH = HERE / "stage07a_hero_corridor01_contract.json"
INPUT_ASSET = "/Game/M01/Lvl_M01_VisibleEnvironmentStage06DistrictCorrection01"
OUTPUT_ASSET = "/Game/M01/Lvl_M01_VisibleEnvironmentStage07AHeroCorridor01"
INPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_VisibleEnvironmentStage06DistrictCorrection01.umap"
OUTPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_VisibleEnvironmentStage07AHeroCorridor01.umap"
DESTINATION = "/Game/M01/VisibleEnvironmentStage07AHeroCorridor01"
DESTINATION_DISK = ISOLATED / "Content/M01/VisibleEnvironmentStage07AHeroCorridor01"
GROUND_OUTPUT = DESTINATION + "/Materials/MI_M01_Stage07A_DistrictGround"
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_VISIBLE_ENVIRONMENT_STAGE07A_HERO_CORRIDOR01_AUTHORING01/attempt_01"
RECEIPT = ATTEMPT / "authoring_receipt.json"


MATERIALS = {
    "ground_source": "/Game/M01/VisibleEnvironmentStage05Composition01Recovery01/Materials/MI_M01_Stage05_UrbanGround_GrassRock",
    "weathered_concrete": "/Game/M01/CoastalCorridorC06R01/M01_CoastalCorridor_C06R01_UNREAL_READY/Materials/M_M01_C06_WeatheredConcrete",
    "asphalt": "/Game/M01/CoastalCorridorC06R01/M01_CoastalCorridor_C06R01_UNREAL_READY/Materials/M_M01_C06_Asphalt",
    "dry_sand": "/Game/M01/CoastalCorridorC06R01/M01_CoastalCorridor_C06R01_UNREAL_READY/Materials/M_M01_C06_DrySand",
    "wet_sand": "/Game/M01/CoastalCorridorC06R01/M01_CoastalCorridor_C06R01_UNREAL_READY/Materials/M_M01_C06_WetSand",
    "road_marking": "/Game/M01/CoastalCorridorC06R01/M01_CoastalCorridor_C06R01_UNREAL_READY/Materials/M_M01_C06_RoadMarking",
    "planting_soil": "/Game/M01/CoastalCorridorC06R01/M01_CoastalCorridor_C06R01_UNREAL_READY/Materials/M_M01_C06R01_PlantingSoil",
    "warm_stucco": "/Game/M01/VisibleEnvironmentStage04Recovery02/FacadeBayR02/Materials/M_M01_CoastalFacadeBay_R02_WarmGreyStucco",
    "pale_limestone": "/Game/M01/VisibleEnvironmentStage04Recovery02/FacadeBayR02/Materials/M_M01_CoastalFacadeBay_R02_PaleLimestone",
    "weathered_plinth": "/Game/M01/VisibleEnvironmentStage04Recovery02/FacadeBayR02/Materials/M_M01_CoastalFacadeBay_R02_WeatheredPlinth",
    "black_steel": "/Game/M01/VisibleEnvironmentStage04Recovery02/FacadeBayR02/Materials/M_M01_CoastalFacadeBay_R02_BlackenedSquareSteel",
    "warm_lamp": "/Game/M01/VisibleEnvironmentStage04Recovery02/FacadeBayR02/Materials/M_M01_PrewarWindow_WarmLamp",
    "window": "/Game/M01/GroundLightingCorrection04Recovery01/Materials/MI_M01_Window_Lifted",
    "glass": "/Game/M01/GroundLightingCorrection04Recovery01/Materials/MI_M01_Glass_Lifted",
}

BUILDING_ASSETS = {
    "ApartmentA": {
        "STRUCTURAL": "/Game/M01/EnvKit02/M01_APARTMENT_A/StaticMeshes/SM_M01_ApartmentA_STRUCTURAL",
        "GLAZING": "/Game/M01/EnvKit02/M01_APARTMENT_A/StaticMeshes/SM_M01_ApartmentA_GLAZING",
        "DETAILS": "/Game/M01/EnvKit02/M01_APARTMENT_A/StaticMeshes/SM_M01_ApartmentA_DETAILS",
    },
    "MidriseB": {
        "STRUCTURAL": "/Game/M01/EnvKit02/M01_MIDRISE_B/StaticMeshes/SM_M01_MidriseB_STRUCTURAL",
        "GLAZING": "/Game/M01/EnvKit02/M01_MIDRISE_B/StaticMeshes/SM_M01_MidriseB_GLAZING",
        "DETAILS": "/Game/M01/EnvKit02/M01_MIDRISE_B/StaticMeshes/SM_M01_MidriseB_DETAILS",
    },
    "CornerC": {
        "STRUCTURAL": "/Game/M01/EnvKit02/M01_CORNER_RESIDENCE_C/StaticMeshes/SM_M01_CornerC_STRUCTURAL",
        "GLAZING": "/Game/M01/EnvKit02/M01_CORNER_RESIDENCE_C/StaticMeshes/SM_M01_CornerC_GLAZING",
        "DETAILS": "/Game/M01/EnvKit02/M01_CORNER_RESIDENCE_C/StaticMeshes/SM_M01_CornerC_DETAILS",
    },
}

NEW_BUILDINGS = (
    {"id": "H01", "family": "ApartmentA", "location_cm": [3700.0, 17100.0, 500.0], "yaw": 168.0, "scale": 0.79},
    {"id": "H02", "family": "CornerC", "location_cm": [10300.0, 18150.0, 500.0], "yaw": 178.0, "scale": 0.83},
    {"id": "H03", "family": "MidriseB", "location_cm": [16900.0, 17600.0, 500.0], "yaw": -171.0, "scale": 0.76},
    {"id": "H04", "family": "ApartmentA", "location_cm": [22800.0, 18400.0, 500.0], "yaw": -158.0, "scale": 0.72},
)

VEGETATION_ASSETS = {
    "fir_sapling": "/Game/M01/SourceBacked/VegetationStaging02/fir_sapling/SM_M01_PHV_FirSapling",
    "pine_sapling_small": "/Game/M01/SourceBacked/VegetationStaging02/pine_sapling_small/SM_M01_PHV_PineSaplingSmall",
    "shrub_02": "/Game/M01/SourceBacked/VegetationStaging02/shrub_02/SM_M01_PHV_Shrub02",
    "shrub_04": "/Game/M01/SourceBacked/VegetationStaging02/shrub_04/SM_M01_PHV_Shrub04",
    "grass_medium_02": "/Game/M01/SourceBacked/VegetationStaging02/grass_medium_02/SM_M01_PHV_GrassMedium02",
}

VEGETATION_PLACEMENTS = (
    # Street trees and taller parcel-edge silhouettes.
    ("fir_sapling", 4500, 9850, 6.6), ("pine_sapling_small", 5650, 10150, 6.9),
    ("fir_sapling", 7850, 9700, 7.2), ("pine_sapling_small", 9050, 10050, 6.5),
    ("fir_sapling", 11100, 9550, 7.5), ("pine_sapling_small", 12300, 10020, 6.8),
    ("fir_sapling", 14600, 9700, 7.0), ("pine_sapling_small", 15900, 10120, 7.3),
    ("fir_sapling", 18100, 9600, 6.7), ("pine_sapling_small", 19300, 10040, 7.1),
    ("fir_sapling", 21400, 9750, 7.4), ("pine_sapling_small", 22400, 10100, 6.6),
    ("fir_sapling", 5150, 13500, 6.2), ("pine_sapling_small", 8300, 14300, 6.4),
    ("fir_sapling", 11500, 13700, 6.8), ("pine_sapling_small", 14800, 14600, 6.3),
    ("fir_sapling", 17800, 13850, 6.5), ("pine_sapling_small", 21100, 14400, 6.7),
    # Dense shrub and groundcover islands break the empty parcels.
    ("shrub_04", 4900, 9300, 3.5), ("shrub_02", 6200, 9450, 1.8),
    ("grass_medium_02", 7000, 9200, 2.6), ("shrub_04", 8450, 9350, 3.2),
    ("shrub_02", 9700, 9200, 1.9), ("grass_medium_02", 10600, 9450, 2.4),
    ("shrub_04", 11900, 9250, 3.6), ("shrub_02", 13200, 9480, 1.7),
    ("grass_medium_02", 14100, 9200, 2.7), ("shrub_04", 15400, 9400, 3.3),
    ("shrub_02", 16800, 9250, 1.9), ("grass_medium_02", 17650, 9470, 2.5),
    ("shrub_04", 18800, 9220, 3.4), ("shrub_02", 20100, 9430, 1.8),
    ("grass_medium_02", 21300, 9250, 2.6), ("shrub_04", 22450, 9480, 3.1),
    ("shrub_02", 5900, 12800, 1.9), ("grass_medium_02", 7200, 13200, 2.5),
    ("shrub_04", 9200, 12600, 3.4), ("shrub_02", 10800, 13100, 1.8),
    ("grass_medium_02", 12600, 12700, 2.7), ("shrub_04", 14300, 13300, 3.2),
    ("shrub_02", 16200, 12650, 1.9), ("grass_medium_02", 17900, 13200, 2.5),
    ("shrub_04", 19700, 12700, 3.5), ("shrub_02", 21800, 13350, 1.8),
    ("grass_medium_02", 7600, 16400, 2.6), ("shrub_04", 15100, 16800, 3.3),
    ("grass_medium_02", 18800, 16500, 2.5), ("shrub_02", 21900, 16900, 1.8),
)

PROP_ASSETS = {
    "Bollard": "/Game/M01/PromenadeBollardRecovery01/StaticMeshes/SM_M01_Promenade_Bollard_A",
    "BicycleRack": "/Game/M01/PromenadeBicycleRackRecovery02/StaticMeshes/SM_M01_Promenade_BicycleRack_A",
    "LitterBin": "/Game/M01/PromenadeLitterBinProduction01/StaticMeshes/SM_M01_Promenade_LitterBin_A",
    "UtilityCabinet": "/Game/M01/PromenadeUtilityCabinetRecovery04/StaticMeshes/SM_M01_Promenade_UtilityCabinet_A",
}

STREET_DETAILS = (
    ("Bollard", 5250, 8350, 5), ("BicycleRack", 6800, 8050, 92),
    ("LitterBin", 8100, 8120, 18), ("UtilityCabinet", 9300, 9550, 176),
    ("Bollard", 10600, 8380, 11), ("BicycleRack", 12100, 8020, 88),
    ("LitterBin", 13500, 8150, -12), ("UtilityCabinet", 14800, 9600, 171),
    ("Bollard", 16100, 8340, -4), ("BicycleRack", 17400, 8060, 95),
    ("LitterBin", 18700, 8110, 21), ("UtilityCabinet", 19900, 9520, -168),
    ("Bollard", 21100, 8370, 8), ("BicycleRack", 22300, 8040, 91),
    ("LitterBin", 23200, 8130, -17), ("UtilityCabinet", 21800, 9650, 179),
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
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def load_contract() -> dict[str, object]:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    require(contract["contract_id"] == "M01-VISIBLE-ENVIRONMENT-STAGE07A-HERO-CORRIDOR01-AUTHORING01", "Contract identity changed")
    return contract


def verify_record(spec: dict[str, object]) -> dict[str, object]:
    path = Path(str(spec["path"]))
    require(path.is_file(), f"Authority missing: {path}")
    require(path.stat().st_size == int(spec["bytes"]), f"Authority byte count changed: {path}")
    require(sha256(path) == str(spec["sha256"]), f"Authority hash changed: {path}")
    return record(path)


def validate_authorities(contract: dict[str, object]) -> list[dict[str, object]]:
    spec = contract["input"]
    require(INPUT_FILE.is_file(), "Stage06 input map missing")
    require(INPUT_FILE.stat().st_size == int(spec["bytes"]), "Stage06 input bytes changed")
    require(sha256(INPUT_FILE) == str(spec["sha256"]), "Stage06 input hash changed")
    return [verify_record(row) for row in contract["authorities"]]


def assert_fresh() -> None:
    require(not OUTPUT_FILE.exists(), f"Fresh output map exists: {OUTPUT_FILE}")
    require(not DESTINATION_DISK.exists(), f"Fresh asset namespace exists: {DESTINATION_DISK}")
    require(not ATTEMPT.exists(), f"Fresh attempt exists: {ATTEMPT}")


def offline_contract_test() -> int:
    contract = load_contract()
    validate_authorities(contract)
    assert_fresh()
    require(len(NEW_BUILDINGS) * 3 == int(contract["corrections"]["new_building_actors"]), "Building budget changed")
    require(len(VEGETATION_PLACEMENTS) == int(contract["corrections"]["new_vegetation_actors"]), "Vegetation budget changed")
    require(len(STREET_DETAILS) == int(contract["corrections"]["new_street_detail_actors"]), "Street-detail budget changed")
    require(len(NEW_BUILDINGS) * 3 + len(VEGETATION_PLACEMENTS) + len(STREET_DETAILS) == int(contract["corrections"]["total_new_actors"]), "Actor budget changed")
    compile(Path(__file__).read_text(encoding="utf-8"), __file__, "exec")
    print("PASS_M01_VISIBLE_ENVIRONMENT_STAGE07A_HERO_CORRIDOR01_AUTHORING_CONTRACT")
    return 0


def asset_identity(value: object) -> str:
    return "" if value is None else str(value.get_path_name())


def vector(value: object) -> list[float]:
    return [float(value.x), float(value.y), float(value.z)]


def load_asset(path: str, unreal: object) -> object:
    asset = unreal.load_asset(path)
    require(asset is not None, f"Asset failed to load: {path}")
    return asset


def static_component(actor: object, unreal: object) -> object:
    component = actor.get_component_by_class(unreal.StaticMeshComponent)
    require(component is not None, f"StaticMeshComponent missing: {actor.get_actor_label()}")
    return component


def terrain_z_cm(x_cm: float, y_cm: float) -> float:
    x, y = x_cm / 100.0, y_cm / 100.0
    long_wave = 0.045 * math.sin(x / 72.0) + 0.025 * math.sin(x / 19.0 + 0.7)
    shore = 38.0 + 2.45 * math.sin(x / 47.0) + 0.82 * math.sin(x / 13.0 + 0.4)
    boundaries = [
        (18.0, -1.25), (shore, -0.54 + long_wave),
        (shore + 10.0 + 0.65 * math.sin(x / 23.0), -0.10 + long_wave),
        (shore + 29.0 + 1.35 * math.sin(x / 39.0 + 0.8), 0.42 + long_wave),
        (78.0 + 0.62 * math.sin(x / 61.0), 0.70 + long_wave * 0.35),
        (86.0, 0.72 + long_wave * 0.20), (100.0, 0.56 + long_wave * 0.15),
        (104.0, 0.72 + long_wave * 0.15),
    ]
    if y >= 104.0:
        return (0.76 + 0.025 * math.sin(x / 31.0)) * 100.0
    for (left_y, left_z), (right_y, right_z) in zip(boundaries, boundaries[1:]):
        if left_y <= y <= right_y:
            alpha = (y - left_y) / max(0.0001, right_y - left_y)
            return (left_z + (right_z - left_z) * alpha) * 100.0
    return boundaries[0][1] * 100.0


def ground_actor(actor: object, unreal: object) -> float:
    location = actor.get_actor_location()
    origin, extent = actor.get_actor_bounds(False)
    target = terrain_z_cm(float(location.x), float(location.y))
    shift = target - float(origin.z - extent.z)
    actor.set_actor_location(unreal.Vector(location.x, location.y, location.z + shift), False, True)
    return float(shift)


def spawn_mesh_actor(actors_api: object, mesh: object, label: str, x: float, y: float, z: float, yaw: float, scale: float, folder: str, unreal: object) -> object:
    actor = actors_api.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x, y, z), unreal.Rotator(pitch=0.0, yaw=yaw, roll=0.0), False)
    require(actor is not None, f"Failed to spawn: {label}")
    actor.set_actor_label(label)
    actor.set_folder_path(folder)
    actor.set_actor_scale3d(unreal.Vector(scale, scale, scale))
    component = static_component(actor, unreal)
    component.set_static_mesh(mesh)
    component.set_mobility(unreal.ComponentMobility.STATIC)
    component.set_editor_property("cast_shadow", True)
    component.set_collision_profile_name("BlockAll")
    return actor


def create_ground_material(unreal: object) -> tuple[object, dict[str, object]]:
    require(not unreal.EditorAssetLibrary.does_asset_exist(GROUND_OUTPUT), "Fresh Stage7A ground material exists")
    source = load_asset(MATERIALS["ground_source"], unreal)
    directory, name = GROUND_OUTPUT.rsplit("/", 1)
    material = unreal.AssetToolsHelpers.get_asset_tools().duplicate_asset(name, directory, source)
    require(material is not None, "Failed to duplicate Stage7A ground material")
    library = unreal.MaterialEditingLibrary
    target_factor = (0.16, 0.22, 0.14, 1.0)
    target_scale = (0.0, 0.0, 48.0, 24.0)
    library.set_material_instance_vector_parameter_value(material, "BaseColorFactor", unreal.LinearColor(*target_factor))
    for parameter in ("BaseColorTexture_OffsetScale", "MetallicRoughnessTexture_OffsetScale", "NormalTexture_OffsetScale"):
        library.set_material_instance_vector_parameter_value(material, parameter, unreal.LinearColor(*target_scale))
    library.set_material_instance_scalar_parameter_value(material, "NormalScale", 1.0)
    library.set_material_instance_scalar_parameter_value(material, "RoughnessFactor", 0.96)
    library.update_material_instance(material)
    require(unreal.EditorAssetLibrary.save_loaded_asset(material, only_if_is_dirty=False), "Failed to save Stage7A ground material")
    return material, {"source": MATERIALS["ground_source"], "output": asset_identity(material), "base_color_factor": list(target_factor), "offset_scale": list(target_scale)}


def set_slot(component: object, slot: int, material: object, label: str) -> dict[str, object]:
    require(slot < int(component.get_num_materials()), f"Material slot missing: {label}:{slot}")
    before = asset_identity(component.get_material(slot))
    component.set_material(slot, material)
    after = asset_identity(component.get_material(slot))
    require(after == asset_identity(material), f"Material binding failed: {label}:{slot}")
    return {"actor": label, "slot": slot, "before": before, "after": after}


def run_unreal() -> None:
    import unreal

    result: dict[str, object] = {
        "schema": "skyguard.m01-visible-environment-stage07a-hero-corridor01.authoring01.v1",
        "classification": "FAILED_WITH_EVIDENCE",
        "authorities": [], "input_map_before": None, "input_map_after": None, "output_map": None,
        "actor_count_before_raw": None, "actor_count_before_governed": None, "actor_count_after_raw": None,
        "actor_count_after_governed": None, "ground_material": None, "semantic_materials": [],
        "building_materials": [], "interior_materials": [], "created_buildings": [],
        "created_vegetation": [], "created_street_details": [], "contact_preservation": None,
        "lighting": None, "runtime_promotion_performed": False, "error": None, "traceback": None,
    }
    try:
        contract = load_contract()
        result["authorities"] = validate_authorities(contract)
        result["input_map_before"] = record(INPUT_FILE)
        require(not OUTPUT_FILE.exists() and not unreal.EditorAssetLibrary.does_asset_exist(OUTPUT_ASSET), "Fresh Stage7A map exists")
        require(not DESTINATION_DISK.exists() and not unreal.EditorAssetLibrary.does_directory_exist(DESTINATION), "Fresh Stage7A namespace exists")
        require(unreal.EditorAssetLibrary.make_directory(DESTINATION), "Failed to create Stage7A namespace")
        ground_material, ground_receipt = create_ground_material(unreal)
        result["ground_material"] = ground_receipt

        loaded_materials = {name: load_asset(path, unreal) for name, path in MATERIALS.items() if name != "ground_source"}
        levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        actors_api = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        require(levels is not None and actors_api is not None, "Required editor subsystems unavailable")
        require(levels.new_level_from_template(OUTPUT_ASSET, INPUT_ASSET), "Failed to clone Stage06 into Stage7A")
        actors = list(actors_api.get_all_level_actors())
        governed = [actor for actor in actors if actor.get_actor_label() != "PCGWorldActor0"]
        result["actor_count_before_raw"] = len(actors)
        result["actor_count_before_governed"] = len(governed)
        require(len(governed) == int(contract["input"]["expected_governed_actor_count"]), f"Stage06 governed actor count changed: {len(governed)}")
        require(len(actors) - len(governed) <= int(contract["input"]["maximum_editor_only_actor_delta"]), "Unexpected editor-only actor count")
        by_label = {actor.get_actor_label(): actor for actor in actors}
        require(len(by_label) == len(actors), "Duplicate inherited actor labels")

        # Restore a darker, visibly textured district substrate instead of Stage06's bright slab material.
        landscape = by_label["M01_A01_Landscape_Production"]
        landscape.set_editor_property("landscape_material", ground_material)
        require(asset_identity(landscape.get_editor_property("landscape_material")) == asset_identity(ground_material), "Landscape ground binding failed")
        district_terrain = by_label["M01_HSSC02_CoastalA_TERRAIN"]
        result["semantic_materials"].append(set_slot(static_component(district_terrain, unreal), 0, ground_material, district_terrain.get_actor_label()))

        # Preserve all accepted corridor semantic slots and prove the known-bad contact guide remains hidden.
        for label in ("M01_C06R01_Corridor_TERRAIN", "M01_C06R01_Corridor_HARDSCAPE", "M01_C06R01_Corridor_DETAILS", "M01_HSSC02_CoastalA_HARDSCAPE"):
            component = static_component(by_label[label], unreal)
            paths = [asset_identity(component.get_material(index)) for index in range(component.get_num_materials())]
            require(paths and all(path for path in paths), f"Semantic material missing: {label}")
            result["semantic_materials"].append({"actor": label, "materials": paths, "preserved": True})
        contact = by_label[str(contract["corrections"]["preserve_hidden_rejected_contact"])]
        contact_component = static_component(contact, unreal)
        contact_component.set_visibility(False, True)
        contact_component.set_hidden_in_game(True)
        require(not bool(contact_component.is_visible()) and bool(contact_component.get_editor_property("hidden_in_game")), "Rejected contact guide became visible")
        result["contact_preservation"] = {"actor": contact.get_actor_label(), "visible": False, "hidden_in_game": True}

        # Correct Stage06's flattened glazing assignment and establish restrained facade variation.
        structural_variants = [loaded_materials["warm_stucco"], loaded_materials["pale_limestone"], loaded_materials["weathered_plinth"]]
        inherited_city = sorted(
            (
                actor for actor in actors
                if actor.get_actor_label().startswith(("M01_STAGE05R01_City_", "M01_STAGE06_City_"))
            ),
            key=lambda actor: actor.get_actor_label(),
        )
        structural_index = 0
        for actor in inherited_city:
            label = actor.get_actor_label()
            component = static_component(actor, unreal)
            if label.endswith("_STRUCTURAL"):
                material = structural_variants[structural_index % len(structural_variants)]
                result["building_materials"].append(set_slot(component, 0, material, label))
                structural_index += 1
            elif label.endswith("_GLAZING"):
                require(component.get_num_materials() >= 2, f"Building glazing slot count changed: {label}")
                result["building_materials"].append(set_slot(component, 0, loaded_materials["window"], label))
                result["building_materials"].append(set_slot(component, 1, loaded_materials["glass"], label))

        interior_actors = sorted(
            (actor for actor in actors if actor.get_actor_label().endswith("_INTERIOR")),
            key=lambda actor: actor.get_actor_label(),
        )
        for index, actor in enumerate(interior_actors):
            if index % 3 == 0:
                result["interior_materials"].append(set_slot(static_component(actor, unreal), 0, loaded_materials["warm_lamp"], actor.get_actor_label()))

        # Add a varied rear skyline without replacing or moving accepted Stage06 buildings.
        loaded_buildings = {family: {suffix: load_asset(path, unreal) for suffix, path in rows.items()} for family, rows in BUILDING_ASSETS.items()}
        for placement_index, placement in enumerate(NEW_BUILDINGS):
            family = str(placement["family"])
            members = []
            for suffix, mesh in loaded_buildings[family].items():
                actor = spawn_mesh_actor(
                    actors_api, mesh, f"M01_STAGE07A_City_{placement['id']}_{family}_{suffix}",
                    float(placement["location_cm"][0]), float(placement["location_cm"][1]), float(placement["location_cm"][2]),
                    float(placement["yaw"]), float(placement["scale"]), "M01/VisibleEnvironmentStage07A/City", unreal,
                )
                members.append(actor)
            structural = next(actor for actor in members if actor.get_actor_label().endswith("_STRUCTURAL"))
            origin, extent = structural.get_actor_bounds(False)
            shift = terrain_z_cm(float(placement["location_cm"][0]), float(placement["location_cm"][1])) - float(origin.z - extent.z)
            for actor in members:
                location = actor.get_actor_location()
                actor.set_actor_location(unreal.Vector(location.x, location.y, location.z + shift), False, True)
                component = static_component(actor, unreal)
                label = actor.get_actor_label()
                if label.endswith("_STRUCTURAL"):
                    result["building_materials"].append(set_slot(component, 0, structural_variants[(placement_index + 1) % len(structural_variants)], label))
                elif label.endswith("_GLAZING"):
                    require(component.get_num_materials() >= 2, f"New building glazing slot count changed: {label}")
                    result["building_materials"].append(set_slot(component, 0, loaded_materials["window"], label))
                    result["building_materials"].append(set_slot(component, 1, loaded_materials["glass"], label))
                result["created_buildings"].append({"label": label, "mesh": asset_identity(component.get_editor_property("static_mesh")), "location_cm": vector(actor.get_actor_location())})
        require(len(result["created_buildings"]) == int(contract["corrections"]["new_building_actors"]), "Created building count changed")

        # Cluster governed source-backed vegetation where the fixed gameplay cameras can read it.
        vegetation_meshes = {species: load_asset(path, unreal) for species, path in VEGETATION_ASSETS.items()}
        for index, (species, x, y, scale) in enumerate(VEGETATION_PLACEMENTS, start=1):
            actor = spawn_mesh_actor(
                actors_api, vegetation_meshes[species], f"M01_STAGE07A_Vegetation_{species}_{index:02d}",
                float(x), float(y), 400.0, float((index * 67 + len(species) * 13) % 360), float(scale),
                "M01/VisibleEnvironmentStage07A/Vegetation", unreal,
            )
            shift = ground_actor(actor, unreal)
            result["created_vegetation"].append({"label": actor.get_actor_label(), "species": species, "location_cm": vector(actor.get_actor_location()), "scale": float(scale), "ground_shift_cm": shift})
        require(len(result["created_vegetation"]) == int(contract["corrections"]["new_vegetation_actors"]), "Created vegetation count changed")

        # Add only accepted promenade props to the camera-visible corridor.
        prop_meshes = {name: load_asset(path, unreal) for name, path in PROP_ASSETS.items()}
        for index, (kind, x, y, yaw) in enumerate(STREET_DETAILS, start=1):
            actor = spawn_mesh_actor(
                actors_api, prop_meshes[kind], f"M01_STAGE07A_Street_{kind}_{index:02d}", float(x), float(y), 300.0,
                float(yaw), 1.0, "M01/VisibleEnvironmentStage07A/StreetDetails", unreal,
            )
            shift = ground_actor(actor, unreal)
            result["created_street_details"].append({"label": actor.get_actor_label(), "kind": kind, "location_cm": vector(actor.get_actor_location()), "ground_shift_cm": shift})
        require(len(result["created_street_details"]) == int(contract["corrections"]["new_street_detail_actors"]), "Street-detail count changed")

        # Lift facade readability while preserving the established daylight/weather state.
        current = list(actors_api.get_all_level_actors())
        by_label = {actor.get_actor_label(): actor for actor in current}
        lighting = contract["corrections"]["lighting"]
        sun = by_label["M01_RS01_Sun"].get_component_by_class(unreal.DirectionalLightComponent)
        fill = by_label["M01_PR01_FillSun"].get_component_by_class(unreal.DirectionalLightComponent)
        sky = by_label["M01_RS01_SkyLight"].get_component_by_class(unreal.SkyLightComponent)
        post = by_label["M01_RS01_PostProcess"]
        require(sun is not None and fill is not None and sky is not None, "Lighting components unavailable")
        sun.set_editor_property("intensity", float(lighting["sun_intensity"]))
        fill.set_editor_property("intensity", float(lighting["fill_intensity"]))
        fill.set_editor_property("cast_shadows", False)
        sky.set_mobility(unreal.ComponentMobility.MOVABLE)
        sky.set_editor_property("intensity", float(lighting["skylight_intensity"]))
        sky.set_editor_property("real_time_capture", True)
        sky.set_editor_property("lower_hemisphere_is_black", False)
        sky.set_editor_property("lower_hemisphere_color", unreal.LinearColor(*lighting["lower_hemisphere_color"]))
        settings = post.get_editor_property("settings")
        for property_name, source_name in (("auto_exposure_bias", "exposure_bias"), ("film_slope", "film_slope"), ("film_toe", "film_toe"), ("film_shoulder", "film_shoulder")):
            settings.set_editor_property("override_" + property_name, True)
            settings.set_editor_property(property_name, float(lighting[source_name]))
        post.set_editor_property("settings", settings)
        result["lighting"] = lighting

        after = list(actors_api.get_all_level_actors())
        governed_after = [actor for actor in after if actor.get_actor_label() != "PCGWorldActor0"]
        result["actor_count_after_raw"] = len(after)
        result["actor_count_after_governed"] = len(governed_after)
        expected = int(contract["input"]["expected_governed_actor_count"]) + int(contract["acceptance"]["actor_delta"])
        require(len(governed_after) == expected, f"Stage7A governed actor count changed: {len(governed_after)} != {expected}")
        require(levels.save_current_level(), "Failed to save Stage7A map")
        require(OUTPUT_FILE.is_file(), "Stage7A output map missing")
        result["input_map_after"] = record(INPUT_FILE)
        require(result["input_map_after"] == result["input_map_before"], "Immutable Stage06 map changed")
        result["output_map"] = record(OUTPUT_FILE)
        result["classification"] = "PASSED_STAGE07A_HERO_CORRIDOR01_AUTHORING_AWAITING_CHECKPOINT_VISUAL"
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        result["traceback"] = traceback.format_exc()
    finally:
        write_json_atomic(RECEIPT, result)

    if str(result["classification"]).startswith("PASSED_"):
        unreal.SystemLibrary.quit_editor()
    else:
        raise RuntimeError(result["error"] or "Stage7A authoring failed")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline-contract-test", action="store_true")
    args = parser.parse_args()
    if args.offline_contract_test:
        return offline_contract_test()
    run_unreal()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
