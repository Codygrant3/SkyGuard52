"""Author the bounded Stage06 Mission 1 district correction in a fresh map."""

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
HERE = ROOT / "Scripts/ToolchainWave08/m01_visible_environment_stage06_district_correction01"
CONTRACT_PATH = HERE / "stage06_district_correction01_contract.json"
INPUT_ASSET = "/Game/M01/Lvl_M01_VisibleEnvironmentStage05Composition01Recovery01"
OUTPUT_ASSET = "/Game/M01/Lvl_M01_VisibleEnvironmentStage06DistrictCorrection01"
INPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_VisibleEnvironmentStage05Composition01Recovery01.umap"
OUTPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_VisibleEnvironmentStage06DistrictCorrection01.umap"
DESTINATION = "/Game/M01/VisibleEnvironmentStage06DistrictCorrection01"
DESTINATION_DISK = ISOLATED / "Content/M01/VisibleEnvironmentStage06DistrictCorrection01"
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_VISIBLE_ENVIRONMENT_STAGE06_DISTRICT_CORRECTION01_AUTHORING01/attempt_01"
RECEIPT = ATTEMPT / "authoring_receipt.json"

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
    {"id": "D06", "family": "MidriseB", "location_cm": [4800.0, 19800.0, 720.0], "yaw": 164.0, "scale": 0.84},
    {"id": "D07", "family": "ApartmentA", "location_cm": [12700.0, 21000.0, 720.0], "yaw": -172.0, "scale": 0.90},
    {"id": "D08", "family": "CornerC", "location_cm": [20700.0, 20200.0, 720.0], "yaw": -148.0, "scale": 0.86},
)

VEGETATION_ASSETS = {
    "fir_sapling": "/Game/M01/SourceBacked/VegetationStaging02/fir_sapling/SM_M01_PHV_FirSapling",
    "pine_sapling_small": "/Game/M01/SourceBacked/VegetationStaging02/pine_sapling_small/SM_M01_PHV_PineSaplingSmall",
    "shrub_02": "/Game/M01/SourceBacked/VegetationStaging02/shrub_02/SM_M01_PHV_Shrub02",
    "shrub_04": "/Game/M01/SourceBacked/VegetationStaging02/shrub_04/SM_M01_PHV_Shrub04",
    "grass_medium_02": "/Game/M01/SourceBacked/VegetationStaging02/grass_medium_02/SM_M01_PHV_GrassMedium02",
}

NEW_VEGETATION = (
    ("fir_sapling", 2, 4.2),
    ("pine_sapling_small", 2, 4.3),
    ("shrub_02", 6, 1.25),
    ("shrub_04", 8, 3.1),
    ("grass_medium_02", 10, 2.1),
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
    require(contract["contract_id"] == "M01-VISIBLE-ENVIRONMENT-STAGE06-DISTRICT-CORRECTION01-AUTHORING01", "Contract identity changed")
    return contract


def verify_record(spec: dict[str, object]) -> dict[str, object]:
    path = Path(str(spec["path"]))
    require(path.is_file(), f"Authority missing: {path}")
    require(path.stat().st_size == int(spec["bytes"]), f"Authority byte count changed: {path}")
    require(sha256(path) == str(spec["sha256"]), f"Authority hash changed: {path}")
    return record(path)


def validate_authorities(contract: dict[str, object]) -> list[dict[str, object]]:
    input_spec = contract["input"]
    require(INPUT_FILE.is_file(), "Stage05 input map missing")
    require(INPUT_FILE.stat().st_size == int(input_spec["bytes"]), "Stage05 input bytes changed")
    require(sha256(INPUT_FILE) == str(input_spec["sha256"]), "Stage05 input hash changed")
    return [verify_record(spec) for spec in contract["authorities"]]


def assert_fresh() -> None:
    require(not OUTPUT_FILE.exists(), f"Fresh output map already exists: {OUTPUT_FILE}")
    require(not DESTINATION_DISK.exists(), f"Fresh asset namespace already exists: {DESTINATION_DISK}")
    require(not ATTEMPT.exists(), f"Fresh attempt already exists: {ATTEMPT}")


def offline_contract_test() -> int:
    contract = load_contract()
    validate_authorities(contract)
    assert_fresh()
    require(sum(row[1] for row in NEW_VEGETATION) == int(contract["corrections"]["vegetation_duplicate_count"]), "Vegetation count changed")
    require(len(NEW_BUILDINGS) == int(contract["corrections"]["additional_building_groups"]), "Building count changed")
    require(int(contract["acceptance"]["expected_actor_count"]) == 225, "Expected actor count changed")
    compile(Path(__file__).read_text(encoding="utf-8"), __file__, "exec")
    print("PASS_M01_VISIBLE_ENVIRONMENT_STAGE06_DISTRICT_CORRECTION01_AUTHORING_CONTRACT")
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


def spawn_mesh_actor(actors_api: object, mesh: object, label: str, location: list[float], yaw: float, scale: float, folder: str, unreal: object) -> object:
    actor = actors_api.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(*location), unreal.Rotator(pitch=0.0, yaw=yaw, roll=0.0), False)
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


def run_unreal() -> None:
    import unreal

    result: dict[str, object] = {
        "schema": "skyguard.m01-visible-environment-stage06-district-correction01.authoring01.v1",
        "classification": "FAILED_WITH_EVIDENCE",
        "authorities": [], "input_map_before": None, "input_map_after": None, "output_map": None,
        "actor_count_before": None, "actor_count_after": None, "removed_facades": [], "removed_bollards": [],
        "created_buildings": [], "created_vegetation": [], "material_bindings": [], "water": None, "lighting": None,
        "runtime_promotion_performed": False, "error": None, "traceback": None,
    }
    try:
        contract = load_contract()
        result["authorities"] = validate_authorities(contract)
        result["input_map_before"] = record(INPUT_FILE)
        require(not OUTPUT_FILE.exists() and not unreal.EditorAssetLibrary.does_asset_exist(OUTPUT_ASSET), "Fresh Stage06 map exists")
        require(not DESTINATION_DISK.exists() and not unreal.EditorAssetLibrary.does_directory_exist(DESTINATION), "Fresh Stage06 namespace exists")

        levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        actors_api = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        require(levels is not None and actors_api is not None, "Required editor subsystems unavailable")
        require(levels.new_level_from_template(OUTPUT_ASSET, INPUT_ASSET), "Failed to clone Stage05 into Stage06")
        actors = list(actors_api.get_all_level_actors())
        result["actor_count_before"] = len(actors)
        require(len(actors) == int(contract["input"]["actor_count"]), f"Stage05 actor count changed: {len(actors)}")

        facades = [actor for actor in actors if actor.get_actor_label().startswith(contract["corrections"]["remove_detached_facade_prefix"])]
        bollards = [actor for actor in actors if actor.get_actor_label().startswith(contract["corrections"]["remove_misgrounded_bollard_prefix"])]
        require(len(facades) == int(contract["acceptance"]["removed_detached_facade_actors"]), "Detached facade count changed")
        require(len(bollards) == int(contract["acceptance"]["removed_misgrounded_bollards"]), "Bollard count changed")
        for actor in facades:
            result["removed_facades"].append(actor.get_actor_label())
            require(actors_api.destroy_actor(actor), "Failed to remove detached facade")
        for actor in bollards:
            result["removed_bollards"].append(actor.get_actor_label())
            require(actors_api.destroy_actor(actor), "Failed to remove misplaced bollard")

        accepted = contract["accepted_local_assets"]
        urban = load_asset(accepted["urban_ground"], unreal)
        window = load_asset(accepted["window_lifted"], unreal)
        glass = load_asset(accepted["glass_lifted"], unreal)
        ocean_material = load_asset(accepted["ocean_near"], unreal)
        far_material = load_asset(accepted["ocean_far"], unreal)

        current = list(actors_api.get_all_level_actors())
        by_label = {actor.get_actor_label(): actor for actor in current}
        landscape = by_label["M01_A01_Landscape_Production"]
        landscape.set_editor_property("landscape_material", urban)
        require(asset_identity(landscape.get_editor_property("landscape_material")) == asset_identity(urban), "Landscape material binding failed")
        terrain = by_label[str(contract["corrections"]["city_terrain_label"])]
        terrain_component = static_component(terrain, unreal)
        terrain_component.set_material(0, urban)
        require(asset_identity(terrain_component.get_material(0)) == asset_identity(urban), "City terrain material binding failed")
        result["material_bindings"] += [
            {"actor": landscape.get_actor_label(), "material": asset_identity(urban)},
            {"actor": terrain.get_actor_label(), "material": asset_identity(urban)},
        ]

        for actor in current:
            label = actor.get_actor_label()
            component = actor.get_component_by_class(unreal.StaticMeshComponent)
            if component is None:
                continue
            if label.endswith("_GLAZING") or label.endswith("_GLASS"):
                material = glass if label.endswith("_GLASS") else window
                for index in range(max(1, int(component.get_num_materials()))):
                    component.set_material(index, material)
                require(asset_identity(component.get_material(0)) == asset_identity(material), f"Glazing material failed: {label}")
                result["material_bindings"].append({"actor": label, "material": asset_identity(material)})

        loaded_buildings = {family: {suffix: load_asset(path, unreal) for suffix, path in rows.items()} for family, rows in BUILDING_ASSETS.items()}
        for placement in NEW_BUILDINGS:
            family = placement["family"]
            members = []
            for suffix, mesh in loaded_buildings[family].items():
                actor = spawn_mesh_actor(actors_api, mesh, f"M01_STAGE06_City_{placement['id']}_{family}_{suffix}", placement["location_cm"], placement["yaw"], placement["scale"], "M01/VisibleEnvironmentStage06DistrictCorrection01/City", unreal)
                members.append(actor)
            structural = members[0]
            origin, extent = structural.get_actor_bounds(False)
            target = terrain_z_cm(float(placement["location_cm"][0]), float(placement["location_cm"][1]))
            shift = target - float(origin.z - extent.z)
            for actor in members:
                loc = actor.get_actor_location()
                actor.set_actor_location(unreal.Vector(loc.x, loc.y, loc.z + shift), False, True)
                if actor.get_actor_label().endswith("_GLAZING"):
                    component = static_component(actor, unreal)
                    for index in range(max(1, int(component.get_num_materials()))):
                        component.set_material(index, window)
                result["created_buildings"].append({"label": actor.get_actor_label(), "mesh": asset_identity(static_component(actor, unreal).get_editor_property("static_mesh")), "location_cm": vector(actor.get_actor_location())})
        require(len(result["created_buildings"]) == int(contract["acceptance"]["created_building_actors"]), "Created building count changed")

        vegetation_meshes = {species: load_asset(path, unreal) for species, path in VEGETATION_ASSETS.items()}
        cursor = 0
        for species, count, base_scale in NEW_VEGETATION:
            for index in range(count):
                x = 4800.0 + ((cursor * 1973) % 17200)
                y = 9400.0 + ((cursor * 811) % 5200)
                scale = base_scale * (0.92 + 0.04 * (index % 5))
                actor = spawn_mesh_actor(actors_api, vegetation_meshes[species], f"M01_STAGE06_Vegetation_{species}_{index + 1:02d}", [x, y, 250.0], float((cursor * 67) % 360), scale, "M01/VisibleEnvironmentStage06DistrictCorrection01/Vegetation", unreal)
                shift = ground_actor(actor, unreal)
                result["created_vegetation"].append({"label": actor.get_actor_label(), "species": species, "location_cm": vector(actor.get_actor_location()), "scale": scale, "ground_shift_cm": shift})
                cursor += 1
        require(len(result["created_vegetation"]) == int(contract["corrections"]["vegetation_duplicate_count"]), "Created vegetation count changed")

        current = list(actors_api.get_all_level_actors())
        by_label = {actor.get_actor_label(): actor for actor in current}
        ocean = by_label["M01_A01_WaterBodyOcean"]
        water_component = ocean.get_water_body_component()
        require(water_component is not None, "WaterBodyOceanComponent unavailable")
        waves_before = ocean.get_editor_property("water_waves")
        near_before = water_component.get_water_material()
        water_component.set_water_material(ocean_material)
        require(asset_identity(water_component.get_water_material()) == asset_identity(ocean_material), "Near-water binding failed")
        zone = by_label["M01_A01_WaterZone"]
        mesh_class = unreal.load_class(None, "/Script/Water.WaterMeshComponent")
        require(mesh_class is not None, "WaterMeshComponent class unavailable")
        water_mesh = zone.get_component_by_class(mesh_class)
        require(water_mesh is not None, "WaterMeshComponent unavailable")
        far_before = water_mesh.get_editor_property("far_distance_material")
        water_mesh.set_editor_property("far_distance_material", far_material)
        require(asset_identity(water_mesh.get_editor_property("far_distance_material")) == asset_identity(far_material), "Far-water binding failed")
        require(ocean.get_editor_property("water_waves") == waves_before, "Water-wave authority changed")
        result["water"] = {"near_before": asset_identity(near_before), "near_after": asset_identity(water_component.get_water_material()), "far_before": asset_identity(far_before), "far_after": asset_identity(water_mesh.get_editor_property("far_distance_material")), "waves_preserved": True}

        lighting = contract["corrections"]["lighting"]
        sun = by_label["M01_RS01_Sun"].get_component_by_class(unreal.DirectionalLightComponent)
        fill = by_label["M01_PR01_FillSun"].get_component_by_class(unreal.DirectionalLightComponent)
        sky = by_label["M01_RS01_SkyLight"].get_component_by_class(unreal.SkyLightComponent)
        post = by_label["M01_RS01_PostProcess"]
        require(sun is not None and fill is not None and sky is not None, "Lighting components unavailable")
        sun.set_editor_property("intensity", float(lighting["sun_intensity"]))
        fill.set_editor_property("intensity", float(lighting["fill_intensity"]))
        fill.set_editor_property("cast_shadows", False)
        sky.set_editor_property("intensity", float(lighting["skylight_intensity"]))
        sky.set_editor_property("real_time_capture", True)
        sky.set_editor_property("lower_hemisphere_is_black", False)
        sky.set_editor_property("lower_hemisphere_color", unreal.LinearColor(*lighting["lower_hemisphere_color"]))
        settings = post.get_editor_property("settings")
        for name in ("auto_exposure_bias", "film_slope", "film_toe", "film_shoulder"):
            source_name = "exposure_bias" if name == "auto_exposure_bias" else name
            settings.set_editor_property("override_" + name, True)
            settings.set_editor_property(name, float(lighting[source_name]))
        post.set_editor_property("settings", settings)
        result["lighting"] = lighting

        after = list(actors_api.get_all_level_actors())
        result["actor_count_after"] = len(after)
        require(len(after) == int(contract["acceptance"]["expected_actor_count"]), f"Stage06 actor count changed: {len(after)}")
        require(levels.save_current_level(), "Failed to save Stage06 map")
        require(OUTPUT_FILE.is_file(), "Stage06 output map missing")
        result["input_map_after"] = record(INPUT_FILE)
        require(result["input_map_after"] == result["input_map_before"], "Immutable Stage05 map changed")
        result["output_map"] = record(OUTPUT_FILE)
        result["classification"] = "PASSED_STAGE06_DISTRICT_CORRECTION01_AUTHORING_AWAITING_D3D12_PROOF"
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        result["traceback"] = traceback.format_exc()
    finally:
        write_json_atomic(RECEIPT, result)

    if str(result["classification"]).startswith("PASSED_"):
        unreal.SystemLibrary.quit_editor()
    else:
        raise RuntimeError(result["error"] or "Stage06 authoring failed")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline-contract-test", action="store_true")
    arguments = parser.parse_args()
    if arguments.offline_contract_test:
        return offline_contract_test()
    run_unreal()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
