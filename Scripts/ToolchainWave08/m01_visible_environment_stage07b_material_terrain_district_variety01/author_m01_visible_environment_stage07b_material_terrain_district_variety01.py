"""Author the Stage 7B Mission 1 material, terrain, and district-variety corridor."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import time
import traceback
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
ISOLATED = Path(r"D:\SG52T08_ENV01")
HERE = ROOT / "Scripts/ToolchainWave08/m01_visible_environment_stage07b_material_terrain_district_variety01"
CONTRACT_PATH = HERE / "stage07b_contract.json"
INPUT_ASSET = "/Game/M01/Lvl_M01_VisibleEnvironmentStage07AHeroCorridor01Correction01"
OUTPUT_ASSET = "/Game/M01/Lvl_M01_VisibleEnvironmentStage07BMaterialTerrainDistrictVariety01"
INPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_VisibleEnvironmentStage07AHeroCorridor01Correction01.umap"
OUTPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_VisibleEnvironmentStage07BMaterialTerrainDistrictVariety01.umap"
DESTINATION = "/Game/M01/VisibleEnvironmentStage07BMaterialTerrainDistrictVariety01"
DESTINATION_DISK = ISOLATED / "Content/M01/VisibleEnvironmentStage07BMaterialTerrainDistrictVariety01"
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_VISIBLE_ENVIRONMENT_STAGE07B_MATERIAL_TERRAIN_DISTRICT_VARIETY01_AUTHORING01/attempt_01"
RECEIPT = ATTEMPT / "authoring_receipt.json"
CHECKPOINT_DIR = ATTEMPT / "checkpoints"

MATERIALS = {
    "planting_soil": "/Game/M01/CoastalCorridorC06R01/M01_CoastalCorridor_C06R01_UNREAL_READY/Materials/M_M01_C06R01_PlantingSoil",
    "wet_sand": "/Game/M01/CoastalCorridorC06R01/M01_CoastalCorridor_C06R01_UNREAL_READY/Materials/M_M01_C06_WetSand",
    "dry_sand": "/Game/M01/CoastalCorridorC06R01/M01_CoastalCorridor_C06R01_UNREAL_READY/Materials/M_M01_C06_DrySand",
    "dune_sand": "/Game/M01/CoastalCorridorC06R01/M01_CoastalCorridor_C06R01_UNREAL_READY/Materials/M_M01_C06_DuneSand",
    "pavers": "/Game/M01/CoastalCorridorC06R01/M01_CoastalCorridor_C06R01_UNREAL_READY/Materials/M_M01_C06_PromenadePavers",
    "asphalt": "/Game/M01/CoastalCorridorC06R01/M01_CoastalCorridor_C06R01_UNREAL_READY/Materials/M_M01_C06_Asphalt",
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

FACADE_BAY_ASSETS = {
    "STRUCTURAL": "/Game/M01/VisibleEnvironmentStage04Recovery02/FacadeBayR02/StaticMeshes/SM_M01_CoastalFacadeBay_A_StructureFrame",
    "GLAZING": "/Game/M01/VisibleEnvironmentStage04Recovery02/FacadeBayR02/StaticMeshes/SM_M01_CoastalFacadeBay_A_Glass",
    "DETAILS": "/Game/M01/VisibleEnvironmentStage04Recovery02/FacadeBayR02/StaticMeshes/SM_M01_CoastalFacadeBay_A_BalconyDetails",
    "INTERIOR": "/Game/M01/VisibleEnvironmentStage04Recovery02/FacadeBayR02/StaticMeshes/SM_M01_CoastalFacadeBay_A_Interior",
}

NEW_BUILDINGS = (
    {"id": "B01", "family": "MidriseB", "location_cm": [4200.0, 19200.0, 500.0], "yaw": 172.0, "scale": 0.94, "treatment": "pale_limestone"},
    {"id": "B02", "family": "CornerC", "location_cm": [8800.0, 18800.0, 500.0], "yaw": -176.0, "scale": 0.86, "treatment": "weathered_plinth"},
    {"id": "B03", "family": "ApartmentA", "location_cm": [14800.0, 19500.0, 500.0], "yaw": 168.0, "scale": 0.78, "treatment": "warm_stucco"},
    {"id": "B04", "family": "MidriseB", "location_cm": [21000.0, 18600.0, 500.0], "yaw": -162.0, "scale": 1.02, "treatment": "pale_limestone"},
)

FACADE_BAYS = (
    {"id": "F01", "location_cm": [7000.0, 16800.0, 500.0], "yaw": 180.0, "scale": 1.15, "treatment": "black_steel"},
    {"id": "F02", "location_cm": [17500.0, 17000.0, 500.0], "yaw": 174.0, "scale": 1.08, "treatment": "weathered_plinth"},
)

VEGETATION_ASSETS = {
    "fir_sapling": "/Game/M01/SourceBacked/VegetationStaging02/fir_sapling/SM_M01_PHV_FirSapling",
    "pine_sapling_small": "/Game/M01/SourceBacked/VegetationStaging02/pine_sapling_small/SM_M01_PHV_PineSaplingSmall",
    "shrub_02": "/Game/M01/SourceBacked/VegetationStaging02/shrub_02/SM_M01_PHV_Shrub02",
    "shrub_04": "/Game/M01/SourceBacked/VegetationStaging02/shrub_04/SM_M01_PHV_Shrub04",
    "grass_medium_02": "/Game/M01/SourceBacked/VegetationStaging02/grass_medium_02/SM_M01_PHV_GrassMedium02",
}

# cluster, species, x, y, scale, yaw
VEGETATION_PLACEMENTS = (
    (1, "shrub_04", 4680, 9080, 3.4, 22), (1, "grass_medium_02", 4920, 9340, 2.5, 81),
    (1, "shrub_02", 5040, 9110, 1.8, 144), (1, "grass_medium_02", 4760, 9420, 2.7, 203),
    (2, "fir_sapling", 6080, 12640, 6.4, 37), (2, "shrub_02", 6320, 12980, 1.9, 118),
    (2, "grass_medium_02", 6180, 13040, 2.4, 266), (2, "shrub_04", 6440, 12720, 3.2, 311),
    (3, "pine_sapling_small", 7760, 8780, 6.6, 54), (3, "shrub_04", 8040, 9020, 3.5, 167),
    (3, "grass_medium_02", 7980, 8720, 2.6, 289),
    (4, "shrub_02", 8920, 15040, 1.8, 12), (4, "grass_medium_02", 9180, 15380, 2.5, 98),
    (4, "shrub_04", 9340, 15120, 3.3, 201), (4, "grass_medium_02", 9040, 15460, 2.8, 244),
    (4, "shrub_02", 9260, 14980, 1.7, 333),
    (5, "shrub_04", 11040, 9660, 3.6, 41), (5, "grass_medium_02", 11320, 9940, 2.4, 129),
    (5, "shrub_02", 11460, 9720, 1.9, 188), (5, "pine_sapling_small", 11120, 10020, 6.3, 275),
    (6, "fir_sapling", 12240, 13940, 6.8, 63), (6, "shrub_02", 12560, 14280, 1.8, 141),
    (6, "shrub_04", 12620, 14020, 3.4, 219), (6, "grass_medium_02", 12320, 14340, 2.6, 302),
    (7, "grass_medium_02", 13640, 8480, 2.7, 18), (7, "shrub_04", 13920, 8740, 3.1, 96),
    (7, "grass_medium_02", 14040, 8520, 2.5, 174),
    (8, "shrub_02", 14920, 11640, 1.9, 29), (8, "grass_medium_02", 15240, 11980, 2.6, 107),
    (8, "shrub_04", 15300, 11720, 3.5, 185), (8, "shrub_02", 15040, 12040, 1.7, 263),
    (8, "grass_medium_02", 15180, 11580, 2.4, 341),
    (9, "pine_sapling_small", 16140, 15340, 6.5, 48), (9, "fir_sapling", 16480, 15680, 6.2, 126),
    (9, "shrub_04", 16540, 15420, 3.3, 204), (9, "grass_medium_02", 16220, 15740, 2.5, 282),
    (10, "shrub_02", 17640, 9160, 1.8, 71), (10, "grass_medium_02", 17920, 9440, 2.7, 159),
    (10, "shrub_04", 18040, 9220, 3.4, 247),
    (11, "grass_medium_02", 19040, 10840, 2.6, 33), (11, "shrub_04", 19320, 11160, 3.2, 111),
    (11, "shrub_02", 19460, 10920, 1.9, 199), (11, "grass_medium_02", 19120, 11220, 2.4, 287),
    (12, "fir_sapling", 20340, 14640, 6.7, 55), (12, "shrub_02", 20660, 14980, 1.8, 133),
    (12, "grass_medium_02", 20720, 14720, 2.5, 211), (12, "shrub_04", 20420, 15040, 3.6, 289),
    (13, "shrub_04", 21640, 8860, 3.3, 14), (13, "grass_medium_02", 21920, 9140, 2.6, 92),
    (13, "shrub_02", 22040, 8920, 1.7, 170), (13, "grass_medium_02", 21720, 9220, 2.8, 248),
    (14, "pine_sapling_small", 23040, 13440, 6.4, 66), (14, "shrub_04", 23360, 13780, 3.5, 144),
    (14, "grass_medium_02", 23420, 13520, 2.5, 222), (14, "shrub_02", 23120, 13840, 1.8, 300),
)

CHECKPOINT_CAMERAS = (
    {"id": "CP01_REAR_GUNNER_ROUTE", "location_cm": [12500.0, 3000.0, 1600.0], "pitch": -7.0, "yaw": 90.0, "fov": 82.0},
    {"id": "CP02_FACADE_VEGETATION_OBLIQUE", "location_cm": [7800.0, 6500.0, 1700.0], "pitch": -3.0, "yaw": 55.0, "fov": 72.0},
    {"id": "CP03_SHORE_MATERIAL_TRANSITION", "location_cm": [9000.0, 1200.0, 1800.0], "pitch": -9.0, "yaw": 82.0, "fov": 72.0},
)

TREATMENT_CYCLE = ("warm_stucco", "pale_limestone", "weathered_plinth", "black_steel")


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
    require(contract["contract_id"] == "M01-VISIBLE-ENVIRONMENT-STAGE07B-MATERIAL-TERRAIN-DISTRICT-VARIETY01-AUTHORING01", "Contract identity changed")
    return contract


def verify_record(spec: dict[str, object]) -> dict[str, object]:
    path = Path(str(spec["path"]))
    require(path.is_file(), f"Authority missing: {path}")
    require(path.stat().st_size == int(spec["bytes"]), f"Authority byte count changed: {path}")
    require(sha256(path) == str(spec["sha256"]), f"Authority hash changed: {path}")
    return record(path)


def validate_authorities(contract: dict[str, object]) -> list[dict[str, object]]:
    spec = contract["input"]
    require(INPUT_FILE.is_file(), "Stage 7A Correction01 input map missing")
    require(INPUT_FILE.stat().st_size == int(spec["bytes"]), "Stage 7A Correction01 input bytes changed")
    require(sha256(INPUT_FILE) == str(spec["sha256"]), "Stage 7A Correction01 input hash changed")
    return [verify_record(row) for row in contract["authorities"]]


def assert_fresh() -> None:
    require(not OUTPUT_FILE.exists(), f"Fresh output map exists: {OUTPUT_FILE}")
    require(not DESTINATION_DISK.exists(), f"Fresh asset namespace exists: {DESTINATION_DISK}")
    require(not ATTEMPT.exists(), f"Fresh attempt exists: {ATTEMPT}")


def offline_contract_test() -> int:
    contract = load_contract()
    validate_authorities(contract)
    assert_fresh()
    clusters = {int(row[0]) for row in VEGETATION_PLACEMENTS}
    require(len(clusters) == int(contract["corrections"]["vegetation_cluster_count"]), "Vegetation cluster budget changed")
    require(len(VEGETATION_PLACEMENTS) == int(contract["corrections"]["new_vegetation_actors"]), "Vegetation actor budget changed")
    require(len(NEW_BUILDINGS) == int(contract["corrections"]["new_building_groups"]), "Building group budget changed")
    require(len(NEW_BUILDINGS) * 3 == int(contract["corrections"]["new_building_actors"]), "Building actor budget changed")
    require(len(FACADE_BAYS) == int(contract["corrections"]["new_facade_bay_groups"]), "Facade-bay group budget changed")
    require(len(FACADE_BAYS) * 4 == int(contract["corrections"]["new_facade_bay_actors"]), "Facade-bay actor budget changed")
    require(
        len(VEGETATION_PLACEMENTS) + len(NEW_BUILDINGS) * 3 + len(FACADE_BAYS) * 4
        == int(contract["corrections"]["total_new_actors"]),
        "Actor budget changed",
    )
    require(len({row[1] for row in VEGETATION_PLACEMENTS}) == 5, "Approved vegetation species count changed")
    compile(Path(__file__).read_text(encoding="utf-8"), __file__, "exec")
    print("PASS_M01_VISIBLE_ENVIRONMENT_STAGE07B_MATERIAL_TERRAIN_DISTRICT_VARIETY01_AUTHORING_CONTRACT")
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


def set_slot(component: object, slot: int, material: object, label: str) -> dict[str, object]:
    require(slot < int(component.get_num_materials()), f"Material slot missing: {label}:{slot}")
    before = asset_identity(component.get_material(slot))
    component.set_material(slot, material)
    after = asset_identity(component.get_material(slot))
    require(after == asset_identity(material), f"Material binding failed: {label}:{slot}")
    return {"actor": label, "slot": slot, "before": before, "after": after}


def bind_available_slots(component: object, slot_map: dict[str, object], path_to_asset: dict[str, object], label: str) -> list[dict[str, object]]:
    applied = []
    count = int(component.get_num_materials())
    require(count >= 1, f"No material slots: {label}")
    for slot_name, material_path in slot_map.items():
        slot = int(slot_name)
        if slot >= count:
            continue
        material = path_to_asset.get(str(material_path))
        require(material is not None, f"Contracted material not loaded for {label}:{slot}: {material_path}")
        applied.append(set_slot(component, slot, material, label))
    require(applied, f"No contracted slots applied: {label}")
    return applied


def hide_line_vegetation(actors: list[object], prefixes: list[str], unreal: object) -> list[dict[str, object]]:
    hidden = []
    for actor in actors:
        label = actor.get_actor_label()
        if not any(label.startswith(prefix) for prefix in prefixes):
            continue
        component = actor.get_component_by_class(unreal.StaticMeshComponent)
        if component is None:
            actor.set_actor_hidden_in_game(True)
            hidden.append({"label": label, "hidden_in_game": True, "component": False})
            continue
        component.set_visibility(False, True)
        component.set_hidden_in_game(True)
        hidden.append({"label": label, "visible": False, "hidden_in_game": True})
    return hidden


def capture_checkpoints(unreal: object) -> list[dict[str, object]]:
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    require(subsystem is not None, "UnrealEditorSubsystem unavailable for checkpoint capture")
    captured = []
    for camera in CHECKPOINT_CAMERAS:
        location = unreal.Vector(*camera["location_cm"])
        rotation = unreal.Rotator(pitch=float(camera["pitch"]), yaw=float(camera["yaw"]), roll=0.0)
        subsystem.set_level_viewport_camera_info(location, rotation)
        target = CHECKPOINT_DIR / f"{camera['id']}.png"
        if target.exists():
            target.unlink()
        ok = unreal.AutomationLibrary.take_high_res_screenshot(2560, 1440, str(target))
        require(ok is not False, f"Checkpoint screenshot command failed: {camera['id']}")
        deadline = time.time() + 30.0
        while time.time() < deadline and not target.is_file():
            time.sleep(0.25)
        require(target.is_file() and target.stat().st_size > 1024, f"Checkpoint capture missing: {target}")
        captured.append({"id": camera["id"], **record(target)})
    require(len(captured) == 3, "Checkpoint capture count changed")
    return captured


def run_unreal() -> None:
    import unreal

    result: dict[str, object] = {
        "schema": "skyguard.m01-visible-environment-stage07b-material-terrain-district-variety01.authoring01.v1",
        "classification": "FAILED_WITH_EVIDENCE",
        "authorities": [], "input_map_before": None, "input_map_after": None, "output_map": None,
        "actor_count_before_raw": None, "actor_count_before_governed": None,
        "actor_count_after_raw": None, "actor_count_after_governed": None,
        "surface_bindings": [], "hidden_line_vegetation": [], "created_buildings": [],
        "created_facade_bays": [], "created_vegetation": [], "lighting": None,
        "checkpoint_captures": [], "runtime_promotion_performed": False,
        "error": None, "traceback": None,
    }
    try:
        contract = load_contract()
        result["authorities"] = validate_authorities(contract)
        result["input_map_before"] = record(INPUT_FILE)
        require(not OUTPUT_FILE.exists() and not unreal.EditorAssetLibrary.does_asset_exist(OUTPUT_ASSET), "Fresh Stage7B map exists")
        require(not DESTINATION_DISK.exists() and not unreal.EditorAssetLibrary.does_directory_exist(DESTINATION), "Fresh Stage7B namespace exists")
        require(unreal.EditorAssetLibrary.make_directory(DESTINATION), "Failed to create Stage7B namespace")

        loaded_materials = {name: load_asset(path, unreal) for name, path in MATERIALS.items()}
        path_to_asset = {path: loaded_materials[name] for name, path in MATERIALS.items()}
        levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        actors_api = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        require(levels is not None and actors_api is not None, "Required editor subsystems unavailable")
        require(levels.new_level_from_template(OUTPUT_ASSET, INPUT_ASSET), "Failed to clone Correction01 into Stage7B")
        actors = list(actors_api.get_all_level_actors())
        governed = [actor for actor in actors if actor.get_actor_label() != "PCGWorldActor0"]
        result["actor_count_before_raw"] = len(actors)
        result["actor_count_before_governed"] = len(governed)
        require(len(governed) == int(contract["input"]["expected_governed_actor_count"]), f"Correction01 governed actor count changed: {len(governed)}")
        require(len(actors) - len(governed) <= int(contract["input"]["maximum_editor_only_actor_delta"]), "Unexpected editor-only actor count")
        by_label = {actor.get_actor_label(): actor for actor in actors}
        require(len(by_label) == len(actors), "Duplicate inherited actor labels")

        landscape = by_label["M01_A01_Landscape_Production"]
        landscape.set_editor_property("landscape_material", loaded_materials["planting_soil"])
        bound = asset_identity(landscape.get_editor_property("landscape_material"))
        require("M_M01_C06R01_PlantingSoil" in bound, "Landscape planting-soil binding failed")
        require("MI_M01_Stage07A_DistrictGround" not in bound, "Forbidden Stage7A white-slab material rebound")
        result["surface_bindings"].append({"actor": "M01_A01_Landscape_Production", "slot": "landscape_material", "after": bound})

        bindings = contract["bindings"]
        result["surface_bindings"].extend(bind_available_slots(
            static_component(by_label[bindings["corridor_terrain_actor"]], unreal),
            bindings["corridor_terrain_slots"], path_to_asset, bindings["corridor_terrain_actor"],
        ))
        result["surface_bindings"].extend(bind_available_slots(
            static_component(by_label[bindings["corridor_hardscape_actor"]], unreal),
            bindings["corridor_hardscape_slots"], path_to_asset, bindings["corridor_hardscape_actor"],
        ))
        result["surface_bindings"].extend(bind_available_slots(
            static_component(by_label[bindings["coastal_terrain_actor"]], unreal),
            bindings["coastal_terrain_slots"], path_to_asset, bindings["coastal_terrain_actor"],
        ))

        contact = by_label[str(contract["preserve_hidden_rejected_contact"])]
        contact_component = static_component(contact, unreal)
        contact_component.set_visibility(False, True)
        contact_component.set_hidden_in_game(True)

        result["hidden_line_vegetation"] = hide_line_vegetation(actors, list(contract["hide_line_vegetation_prefixes"]), unreal)
        require(result["hidden_line_vegetation"], "No line-placed vegetation was hidden")

        structural_by_name = {
            "warm_stucco": loaded_materials["warm_stucco"],
            "pale_limestone": loaded_materials["pale_limestone"],
            "weathered_plinth": loaded_materials["weathered_plinth"],
            "black_steel": loaded_materials["black_steel"],
        }
        inherited_city = sorted(
            (
                actor for actor in actors
                if actor.get_actor_label().startswith(("M01_STAGE05R01_City_", "M01_STAGE06_City_", "M01_STAGE07A_City_"))
            ),
            key=lambda actor: actor.get_actor_label(),
        )
        structural_index = 0
        for actor in inherited_city:
            label = actor.get_actor_label()
            component = static_component(actor, unreal)
            if label.endswith("_STRUCTURAL"):
                treatment = TREATMENT_CYCLE[structural_index % len(TREATMENT_CYCLE)]
                result["surface_bindings"].append(set_slot(component, 0, structural_by_name[treatment], label))
                structural_index += 1
            elif label.endswith("_GLAZING") and component.get_num_materials() >= 2:
                result["surface_bindings"].append(set_slot(component, 0, loaded_materials["window"], label))
                result["surface_bindings"].append(set_slot(component, 1, loaded_materials["glass"], label))

        loaded_buildings = {family: {suffix: load_asset(path, unreal) for suffix, path in rows.items()} for family, rows in BUILDING_ASSETS.items()}
        for placement in NEW_BUILDINGS:
            family = str(placement["family"])
            members = []
            for suffix, mesh in loaded_buildings[family].items():
                actor = spawn_mesh_actor(
                    actors_api, mesh, f"M01_STAGE07B_City_{placement['id']}_{family}_{suffix}",
                    float(placement["location_cm"][0]), float(placement["location_cm"][1]), float(placement["location_cm"][2]),
                    float(placement["yaw"]), float(placement["scale"]), "M01/VisibleEnvironmentStage07B/City", unreal,
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
                    set_slot(component, 0, structural_by_name[str(placement["treatment"])], label)
                elif label.endswith("_GLAZING") and component.get_num_materials() >= 2:
                    set_slot(component, 0, loaded_materials["window"], label)
                    set_slot(component, 1, loaded_materials["glass"], label)
                result["created_buildings"].append({"label": label, "mesh": asset_identity(component.get_editor_property("static_mesh")), "location_cm": vector(actor.get_actor_location())})
        require(len(result["created_buildings"]) == int(contract["corrections"]["new_building_actors"]), "Created building count changed")

        loaded_bays = {suffix: load_asset(path, unreal) for suffix, path in FACADE_BAY_ASSETS.items()}
        for placement in FACADE_BAYS:
            members = []
            for suffix, mesh in loaded_bays.items():
                actor = spawn_mesh_actor(
                    actors_api, mesh, f"M01_STAGE07B_FacadeBay_{placement['id']}_{suffix}",
                    float(placement["location_cm"][0]), float(placement["location_cm"][1]), float(placement["location_cm"][2]),
                    float(placement["yaw"]), float(placement["scale"]), "M01/VisibleEnvironmentStage07B/FacadeBay", unreal,
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
                    set_slot(component, 0, structural_by_name[str(placement["treatment"])], label)
                elif label.endswith("_GLAZING"):
                    set_slot(component, 0, loaded_materials["glass"], label)
                elif label.endswith("_INTERIOR"):
                    set_slot(component, 0, loaded_materials["warm_lamp"], label)
                result["created_facade_bays"].append({"label": label, "mesh": asset_identity(component.get_editor_property("static_mesh")), "location_cm": vector(actor.get_actor_location())})
        require(len(result["created_facade_bays"]) == int(contract["corrections"]["new_facade_bay_actors"]), "Created facade-bay count changed")

        vegetation_meshes = {species: load_asset(path, unreal) for species, path in VEGETATION_ASSETS.items()}
        for index, (cluster, species, x, y, scale, yaw) in enumerate(VEGETATION_PLACEMENTS, start=1):
            actor = spawn_mesh_actor(
                actors_api, vegetation_meshes[species], f"M01_STAGE07B_Vegetation_C{cluster:02d}_{species}_{index:02d}",
                float(x), float(y), 400.0, float(yaw), float(scale),
                "M01/VisibleEnvironmentStage07B/Vegetation", unreal,
            )
            shift = ground_actor(actor, unreal)
            result["created_vegetation"].append({
                "label": actor.get_actor_label(), "cluster": int(cluster), "species": species,
                "location_cm": vector(actor.get_actor_location()), "scale": float(scale), "yaw": float(yaw),
                "ground_shift_cm": shift,
            })
        require(len(result["created_vegetation"]) == int(contract["corrections"]["new_vegetation_actors"]), "Created vegetation count changed")
        require(len({row["cluster"] for row in result["created_vegetation"]}) == 14, "Vegetation cluster count changed")

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
        require(len(governed_after) == expected, f"Stage7B governed actor count changed: {len(governed_after)} != {expected}")
        require(levels.save_current_level(), "Failed to save Stage7B map")
        require(OUTPUT_FILE.is_file(), "Stage7B output map missing")
        result["input_map_after"] = record(INPUT_FILE)
        require(result["input_map_after"] == result["input_map_before"], "Immutable Stage 7A Correction01 map changed")
        result["output_map"] = record(OUTPUT_FILE)
        result["checkpoint_captures"] = capture_checkpoints(unreal)
        result["classification"] = "PASSED_STAGE07B_AUTHORING_AWAITING_CHECKPOINT_VISUAL"
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        result["traceback"] = traceback.format_exc()
    finally:
        write_json_atomic(RECEIPT, result)

    if str(result["classification"]).startswith("PASSED_"):
        unreal.SystemLibrary.quit_editor()
    else:
        raise RuntimeError(result["error"] or "Stage7B authoring failed")


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
