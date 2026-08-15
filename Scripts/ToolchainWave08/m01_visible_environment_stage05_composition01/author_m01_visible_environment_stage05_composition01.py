"""Author a fresh Mission 1 Stage05 composition from the stable Stage04 map."""

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
HERE = ROOT / "Scripts/ToolchainWave08/m01_visible_environment_stage05_composition01"
CONTRACT_PATH = HERE / "stage05_composition01_authoring_contract.json"
PROJECT = ISOLATED / "Skyguard52.uproject"
INPUT_ASSET = "/Game/M01/Lvl_M01_VisibleEnvironmentStage04Recovery03"
OUTPUT_ASSET = "/Game/M01/Lvl_M01_VisibleEnvironmentStage05Composition01"
INPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_VisibleEnvironmentStage04Recovery03.umap"
OUTPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_VisibleEnvironmentStage05Composition01.umap"
DESTINATION = "/Game/M01/VisibleEnvironmentStage05Composition01"
DESTINATION_DISK = ISOLATED / "Content/M01/VisibleEnvironmentStage05Composition01"
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_VISIBLE_ENVIRONMENT_STAGE05_COMPOSITION01_AUTHORING01/attempt_01"
RECEIPT = ATTEMPT / "authoring_receipt.json"


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
    require(contract["contract_id"] == "M01-VISIBLE-ENVIRONMENT-STAGE05-COMPOSITION01-AUTHORING01", "Contract identity changed")
    return contract


def verify_file(spec: dict[str, object]) -> dict[str, object]:
    path = Path(str(spec["path"]))
    require(path.is_file(), f"Authority missing: {path}")
    require(path.stat().st_size == int(spec["bytes"]), f"Authority byte count changed: {path}")
    require(sha256(path) == str(spec["sha256"]), f"Authority hash changed: {path}")
    return record(path)


def validate_authorities(contract: dict[str, object]) -> list[dict[str, object]]:
    input_spec = contract["input"]
    require(INPUT_FILE.is_file(), "Stage04 input map missing")
    require(INPUT_FILE.stat().st_size == int(input_spec["bytes"]), "Stage04 input map byte count changed")
    require(sha256(INPUT_FILE) == str(input_spec["sha256"]), "Stage04 input map hash changed")
    return [verify_file(spec) for spec in contract["authorities"]]


def assert_fresh() -> None:
    require(not OUTPUT_FILE.exists(), f"Fresh output map already exists: {OUTPUT_FILE}")
    require(not DESTINATION_DISK.exists(), f"Fresh asset namespace already exists: {DESTINATION_DISK}")
    require(not ATTEMPT.exists(), f"Fresh attempt already exists: {ATTEMPT}")


def offline_contract_test() -> int:
    contract = load_contract()
    validate_authorities(contract)
    assert_fresh()
    require(len(contract["building_placements"]) == 6, "Building placement count changed")
    require(len(contract["facade_placements"]) == 4, "Facade placement count changed")
    require(int(contract["acceptance"]["expected_actor_count"]) == 217, "Expected actor count changed")
    compile(Path(__file__).read_text(encoding="utf-8"), __file__, "exec")
    print("PASS_M01_VISIBLE_ENVIRONMENT_STAGE05_COMPOSITION01_AUTHORING_CONTRACT")
    return 0


def vector(value: object) -> list[float]:
    return [float(value.x), float(value.y), float(value.z)]


def asset_identity(value: object) -> str:
    return "" if value is None else str(value.get_path_name())


def load_asset(path: str, unreal: object) -> object:
    asset = unreal.load_asset(path)
    require(asset is not None, f"Asset failed to load: {path}")
    return asset


def corridor_surface_z_cm(x_cm: float, y_cm: float) -> float:
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


def static_component(actor: object, unreal: object) -> object:
    component = actor.get_component_by_class(unreal.StaticMeshComponent)
    require(component is not None, f"StaticMeshComponent missing: {actor.get_actor_label()}")
    return component


def set_visible(actor: object, visible: bool, unreal: object) -> None:
    component = static_component(actor, unreal)
    component.set_editor_property("visible", bool(visible))
    component.set_editor_property("hidden_in_game", not bool(visible))


def ground_actor(actor: object, unreal: object) -> float:
    location = actor.get_actor_location()
    origin, extent = actor.get_actor_bounds(False)
    target = corridor_surface_z_cm(float(location.x), float(location.y))
    shift = target - float(origin.z - extent.z)
    actor.set_actor_location(unreal.Vector(location.x, location.y, location.z + shift), False, True)
    return float(shift)


def create_ground_material(contract: dict[str, object], unreal: object) -> tuple[object, dict[str, object]]:
    material = contract["material"]
    source_path = str(material["source"])
    output_path = str(material["output"])
    output_directory, output_name = output_path.rsplit("/", 1)
    require(not unreal.EditorAssetLibrary.does_asset_exist(output_path), f"Fresh material already exists: {output_path}")
    source = load_asset(source_path, unreal)
    duplicated = unreal.AssetToolsHelpers.get_asset_tools().duplicate_asset(output_name, output_directory, source)
    require(duplicated is not None, "Could not duplicate governed Stage05 ground material")
    library = unreal.MaterialEditingLibrary
    factor = material["base_color_factor"]
    scale = material["offset_scale"]
    library.set_material_instance_vector_parameter_value(duplicated, "BaseColorFactor", unreal.LinearColor(*[float(v) for v in factor]))
    for name in ("BaseColorTexture_OffsetScale", "MetallicRoughnessTexture_OffsetScale", "NormalTexture_OffsetScale"):
        library.set_material_instance_vector_parameter_value(duplicated, name, unreal.LinearColor(*[float(v) for v in scale]))
    library.set_material_instance_scalar_parameter_value(duplicated, "NormalScale", float(material["normal_scale"]))
    library.set_material_instance_scalar_parameter_value(duplicated, "RoughnessFactor", float(material["roughness_factor"]))
    require(unreal.EditorAssetLibrary.save_loaded_asset(duplicated, only_if_is_dirty=False), "Could not save Stage05 ground material")
    return duplicated, {"source": source_path, "output": asset_identity(duplicated), "base_color_factor": factor, "offset_scale": scale}


def spawn_mesh_actor(actors_api: object, mesh: object, label: str, location: list[float], yaw: float, scale: float, folder: str, unreal: object) -> object:
    actor = actors_api.spawn_actor_from_class(
        unreal.StaticMeshActor,
        unreal.Vector(*[float(v) for v in location]),
        unreal.Rotator(pitch=0.0, yaw=float(yaw), roll=0.0),
        False,
    )
    require(actor is not None, f"Failed to spawn: {label}")
    actor.set_actor_label(label)
    actor.set_folder_path(folder)
    actor.set_actor_scale3d(unreal.Vector(float(scale), float(scale), float(scale)))
    component = static_component(actor, unreal)
    component.set_static_mesh(mesh)
    component.set_mobility(unreal.ComponentMobility.STATIC)
    component.set_editor_property("cast_shadow", True)
    component.set_collision_profile_name("BlockAll")
    return actor


def spawn_building_group(actors_api: object, placement: dict[str, object], meshes: dict[str, object], unreal: object) -> list[dict[str, object]]:
    family = str(placement["family"])
    group: list[object] = []
    for suffix in ("STRUCTURAL", "GLAZING", "DETAILS"):
        group.append(spawn_mesh_actor(
            actors_api, meshes[suffix], f"M01_STAGE05_City_{placement['id']}_{family}_{suffix}",
            placement["location_cm"], float(placement["yaw_degrees"]), float(placement["uniform_scale"]),
            "M01/VisibleEnvironmentStage05Composition01/City", unreal,
        ))
    structural = group[0]
    target = corridor_surface_z_cm(float(placement["location_cm"][0]), float(placement["location_cm"][1]))
    origin, extent = structural.get_actor_bounds(False)
    shift = target - float(origin.z - extent.z)
    for actor in group:
        location = actor.get_actor_location()
        actor.set_actor_location(unreal.Vector(location.x, location.y, location.z + shift), False, True)
    return [{
        "label": actor.get_actor_label(),
        "mesh": asset_identity(static_component(actor, unreal).get_editor_property("static_mesh")),
        "location_cm": vector(actor.get_actor_location()),
        "rotation_degrees": vector(actor.get_actor_rotation()),
        "scale": vector(actor.get_actor_scale3d()),
    } for actor in group]


def run_unreal() -> None:
    import unreal

    result: dict[str, object] = {
        "schema": "skyguard.m01-visible-environment-stage05-composition01.authoring01.v1",
        "classification": "FAILED_WITH_EVIDENCE",
        "authorities": [],
        "input_map_before": None,
        "input_map_after": None,
        "output_map": None,
        "actor_count_before": None,
        "actor_count_after": None,
        "removed_actors": [],
        "created_buildings": [],
        "created_facades": [],
        "vegetation_adjustments": [],
        "prop_adjustments": [],
        "ground_material": None,
        "lighting": None,
        "runtime_promotion_performed": False,
        "error": None,
        "traceback": None,
    }
    try:
        contract = load_contract()
        result["authorities"] = validate_authorities(contract)
        result["input_map_before"] = record(INPUT_FILE)
        require(not OUTPUT_FILE.exists() and not unreal.EditorAssetLibrary.does_asset_exist(OUTPUT_ASSET), "Fresh Stage05 map exists")
        require(not DESTINATION_DISK.exists() and not unreal.EditorAssetLibrary.does_directory_exist(DESTINATION), "Fresh Stage05 asset namespace exists")

        levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        actors_api = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        require(levels is not None and actors_api is not None, "Required editor subsystems unavailable")
        require(levels.new_level_from_template(OUTPUT_ASSET, INPUT_ASSET), "Failed to clone Stage04 into fresh Stage05")
        actors = list(actors_api.get_all_level_actors())
        result["actor_count_before"] = len(actors)
        require(len(actors) == int(contract["input"]["actor_count"]), f"Stage04 actor count changed: {len(actors)}")

        removal_prefixes = tuple(str(value) for value in contract["remove_visible_actor_prefixes"])
        removed = [actor for actor in actors if actor.get_actor_label().startswith(removal_prefixes)]
        expected_removed = int(contract["acceptance"]["removed_old_city_actors"]) + int(contract["acceptance"]["removed_old_facade_actors"])
        require(len(removed) == expected_removed, f"Removal allowlist changed: {len(removed)} != {expected_removed}")
        for actor in removed:
            result["removed_actors"].append(actor.get_actor_label())
            require(actors_api.destroy_actor(actor), f"Failed to remove inherited presentation actor: {actor.get_actor_label()}")

        current = list(actors_api.get_all_level_actors())
        by_label = {actor.get_actor_label(): actor for actor in current}
        ground_material, material_receipt = create_ground_material(contract, unreal)
        result["ground_material"] = material_receipt
        landscape = by_label["M01_A01_Landscape_Production"]
        landscape.set_editor_property("landscape_material", ground_material)
        require(asset_identity(landscape.get_editor_property("landscape_material")) == asset_identity(ground_material), "Landscape material readback failed")
        city_terrain = by_label[str(contract["material"]["apply_to_city_terrain_actor"])]
        set_visible(city_terrain, True, unreal)
        city_terrain_component = static_component(city_terrain, unreal)
        city_terrain_component.set_material(0, ground_material)
        require(asset_identity(city_terrain_component.get_material(0)) == asset_identity(ground_material), "City terrain material readback failed")

        loaded_families: dict[str, dict[str, object]] = {}
        for family, paths in contract["building_meshes"].items():
            loaded_families[family] = {suffix: load_asset(path, unreal) for suffix, path in paths.items()}
        for placement in contract["building_placements"]:
            result["created_buildings"] += spawn_building_group(actors_api, placement, loaded_families[str(placement["family"])], unreal)
        require(len(result["created_buildings"]) == int(contract["acceptance"]["created_building_actors"]), "Created building count changed")

        facade_meshes = {suffix: load_asset(path, unreal) for suffix, path in contract["facade_meshes"].items()}
        for placement in contract["facade_placements"]:
            for suffix, mesh in facade_meshes.items():
                actor = spawn_mesh_actor(
                    actors_api, mesh, f"M01_STAGE05_Facade_{placement['id']}_{suffix}", placement["location_cm"],
                    float(placement["yaw_degrees"]), 1.0, "M01/VisibleEnvironmentStage05Composition01/Facade", unreal,
                )
                result["created_facades"].append({"label": actor.get_actor_label(), "mesh": asset_identity(mesh), "location_cm": vector(actor.get_actor_location())})
        require(len(result["created_facades"]) == int(contract["acceptance"]["created_facade_actors"]), "Created facade count changed")

        current = list(actors_api.get_all_level_actors())
        vegetation = sorted([actor for actor in current if actor.get_actor_label().startswith("M01_PHV02_")], key=lambda actor: actor.get_actor_label())
        require(len(vegetation) == int(contract["vegetation"]["expected_count"]), "Vegetation actor count changed")
        species_rows: dict[str, list[object]] = {
            "fir_sapling": [actor for actor in vegetation if "fir_sapling" in actor.get_actor_label()],
            "pine_sapling_small": [actor for actor in vegetation if "pine_sapling_small" in actor.get_actor_label()],
            "shrub_02": [actor for actor in vegetation if "shrub_02" in actor.get_actor_label()],
            "shrub_04": [actor for actor in vegetation if "shrub_04" in actor.get_actor_label()],
            "grass_medium_02": [actor for actor in vegetation if "grass_medium_02" in actor.get_actor_label()],
        }
        positions = {
            "fir_sapling": [(6200.0, 9550.0), (20200.0, 9625.0)],
            "pine_sapling_small": [(10200.0, 9650.0), (15800.0, 9525.0)],
            "shrub_02": [(5700.0, 9180.0), (8200.0, 9380.0), (11100.0, 9200.0), (14300.0, 9400.0), (17600.0, 9175.0), (21200.0, 9360.0)],
            "shrub_04": [(6400.0, 8860.0), (7900.0, 8990.0), (9800.0, 8840.0), (12100.0, 9010.0), (14700.0, 8830.0), (16900.0, 8990.0), (19400.0, 8820.0), (21700.0, 8980.0)],
            "grass_medium_02": [(5900.0, 8750.0), (7300.0, 8920.0), (9000.0, 8750.0), (10800.0, 8940.0), (12900.0, 8760.0), (15100.0, 8950.0), (17100.0, 8750.0), (18800.0, 8940.0), (20400.0, 8770.0), (21800.0, 8950.0)],
        }
        for species, rows in species_rows.items():
            require(len(rows) == len(positions[species]), f"Vegetation species count changed: {species}")
            low, high = [float(value) for value in contract["vegetation"]["absolute_scale_ranges"][species]]
            for index, (actor, xy) in enumerate(zip(rows, positions[species])):
                alpha = 0.5 if len(rows) == 1 else index / (len(rows) - 1)
                scale = low + (high - low) * alpha
                actor.set_actor_rotation(unreal.Rotator(pitch=0.0, yaw=float((index * 61 + len(species) * 7) % 360), roll=0.0), False)
                actor.set_actor_scale3d(unreal.Vector(scale, scale, scale))
                old = actor.get_actor_location()
                actor.set_actor_location(unreal.Vector(float(xy[0]), float(xy[1]), old.z), False, True)
                shift = ground_actor(actor, unreal)
                result["vegetation_adjustments"].append({"label": actor.get_actor_label(), "species": species, "location_cm": vector(actor.get_actor_location()), "scale": scale, "ground_shift_cm": shift})

        prop_prefixes = tuple(str(value) for value in contract["props"]["prefixes"])
        props = sorted([actor for actor in list(actors_api.get_all_level_actors()) if actor.get_actor_label().startswith(prop_prefixes)], key=lambda actor: actor.get_actor_label())
        require(len(props) >= int(contract["props"]["minimum_count"]), f"Governed prop count changed: {len(props)}")
        for index, actor in enumerate(props):
            actor.set_actor_rotation(unreal.Rotator(pitch=0.0, yaw=float((index * 37) % 360), roll=0.0), False)
            shift = ground_actor(actor, unreal)
            result["prop_adjustments"].append({"label": actor.get_actor_label(), "rotation": vector(actor.get_actor_rotation()), "ground_shift_cm": shift})

        current = list(actors_api.get_all_level_actors())
        by_label = {actor.get_actor_label(): actor for actor in current}
        lighting = contract["lighting"]
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
        color = lighting["lower_hemisphere_color"]
        sky.set_editor_property("lower_hemisphere_color", unreal.LinearColor(*[float(value) for value in color]))
        settings = post.get_editor_property("settings")
        for name, value in (
            ("auto_exposure_bias", lighting["exposure_bias"]),
            ("film_slope", lighting["film_slope"]),
            ("film_toe", lighting["film_toe"]),
            ("film_shoulder", lighting["film_shoulder"]),
            ("film_white_clip", lighting["film_white_clip"]),
            ("film_black_clip", lighting["film_black_clip"]),
        ):
            settings.set_editor_property("override_" + name, True)
            settings.set_editor_property(name, float(value))
        post.set_editor_property("settings", settings)
        result["lighting"] = lighting

        after = list(actors_api.get_all_level_actors())
        result["actor_count_after"] = len(after)
        require(len(after) == int(contract["acceptance"]["expected_actor_count"]), f"Stage05 actor count changed: {len(after)}")
        require(levels.save_current_level(), "Failed to save fresh Stage05 map")
        require(OUTPUT_FILE.is_file(), "Fresh Stage05 map was not created")
        result["input_map_after"] = record(INPUT_FILE)
        require(result["input_map_after"] == result["input_map_before"], "Immutable Stage04 input map changed")
        result["output_map"] = record(OUTPUT_FILE)
        result["classification"] = "PASSED_STAGE05_COMPOSITION01_AUTHORING_AWAITING_POSTFLIGHT_AND_D3D12_PROOF"
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        result["traceback"] = traceback.format_exc()
    finally:
        write_json_atomic(RECEIPT, result)

    if str(result["classification"]).startswith("PASSED_"):
        unreal.SystemLibrary.quit_editor()
    else:
        raise RuntimeError(result["error"] or "Stage05 authoring failed")


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
