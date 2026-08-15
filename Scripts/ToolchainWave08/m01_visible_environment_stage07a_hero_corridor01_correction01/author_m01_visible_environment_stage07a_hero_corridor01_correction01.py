"""Apply the sole bounded post-checkpoint correction to Stage 7A in a fresh map."""

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
HERE = ROOT / "Scripts/ToolchainWave08/m01_visible_environment_stage07a_hero_corridor01_correction01"
CONTRACT_PATH = HERE / "stage07a_hero_corridor01_correction01_contract.json"
INPUT_ASSET = "/Game/M01/Lvl_M01_VisibleEnvironmentStage07AHeroCorridor01"
OUTPUT_ASSET = "/Game/M01/Lvl_M01_VisibleEnvironmentStage07AHeroCorridor01Correction01"
INPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_VisibleEnvironmentStage07AHeroCorridor01.umap"
OUTPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_VisibleEnvironmentStage07AHeroCorridor01Correction01.umap"
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_VISIBLE_ENVIRONMENT_STAGE07A_HERO_CORRIDOR01_CORRECTION01_AUTHORING01/attempt_01"
RECEIPT = ATTEMPT / "authoring_receipt.json"


BUILDING_SCALE_FACTORS = {
    "B00": (1.08, 0.92, 1.05),
    "B01": (0.95, 1.08, 0.86),
    "B02": (1.05, 0.90, 1.12),
    "B03": (0.90, 1.06, 0.94),
    "B04": (1.12, 0.88, 0.80),
    "B05": (0.93, 1.10, 1.06),
    "D06": (1.06, 0.94, 0.90),
    "D07": (0.92, 1.05, 1.13),
    "D08": (1.10, 0.90, 0.85),
    "H01": (1.08, 0.94, 0.82),
    "H02": (0.90, 1.10, 1.05),
    "H03": (1.04, 0.92, 0.92),
    "H04": (0.94, 1.06, 1.15),
}


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
    require(contract["contract_id"] == "M01-VISIBLE-ENVIRONMENT-STAGE07A-HERO-CORRIDOR01-CORRECTION01-AUTHORING01", "Contract identity changed")
    return contract


def verify_record(spec: dict[str, object]) -> dict[str, object]:
    path = Path(str(spec["path"]))
    require(path.is_file(), f"Authority missing: {path}")
    require(path.stat().st_size == int(spec["bytes"]), f"Authority byte count changed: {path}")
    require(sha256(path) == str(spec["sha256"]), f"Authority hash changed: {path}")
    return record(path)


def validate_authorities(contract: dict[str, object]) -> list[dict[str, object]]:
    spec = contract["input"]
    require(INPUT_FILE.is_file(), "Stage07A input map missing")
    require(INPUT_FILE.stat().st_size == int(spec["bytes"]), "Stage07A input bytes changed")
    require(sha256(INPUT_FILE) == str(spec["sha256"]), "Stage07A input hash changed")
    return [verify_record(row) for row in contract["authorities"]]


def assert_fresh() -> None:
    require(not OUTPUT_FILE.exists(), f"Fresh correction output exists: {OUTPUT_FILE}")
    require(not ATTEMPT.exists(), f"Fresh correction attempt exists: {ATTEMPT}")


def offline_contract_test() -> int:
    contract = load_contract()
    validate_authorities(contract)
    assert_fresh()
    require(len(BUILDING_SCALE_FACTORS) == int(contract["correction"]["building_group_count"]), "Building-group budget changed")
    for factor in BUILDING_SCALE_FACTORS.values():
        require(float(contract["correction"]["building_scale_bounds"]["xy_min"]) <= factor[0] <= float(contract["correction"]["building_scale_bounds"]["xy_max"]), "Building X scale outside contract")
        require(float(contract["correction"]["building_scale_bounds"]["xy_min"]) <= factor[1] <= float(contract["correction"]["building_scale_bounds"]["xy_max"]), "Building Y scale outside contract")
        require(float(contract["correction"]["building_scale_bounds"]["z_min"]) <= factor[2] <= float(contract["correction"]["building_scale_bounds"]["z_max"]), "Building Z scale outside contract")
    compile(Path(__file__).read_text(encoding="utf-8"), __file__, "exec")
    print("PASS_M01_VISIBLE_ENVIRONMENT_STAGE07A_HERO_CORRIDOR01_CORRECTION01_CONTRACT")
    return 0


def asset_identity(value: object) -> str:
    return "" if value is None else str(value.get_path_name())


def vector(value: object) -> list[float]:
    return [float(value.x), float(value.y), float(value.z)]


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
    shift = terrain_z_cm(float(location.x), float(location.y)) - float(origin.z - extent.z)
    actor.set_actor_location(unreal.Vector(location.x, location.y, location.z + shift), False, True)
    return float(shift)


def group_id(label: str) -> str | None:
    for identifier in BUILDING_SCALE_FACTORS:
        if f"_{identifier}_" in label:
            return identifier
    return None


def run_unreal() -> None:
    import unreal

    result: dict[str, object] = {
        "schema": "skyguard.m01-visible-environment-stage07a-hero-corridor01-correction01.authoring01.v1",
        "classification": "FAILED_WITH_EVIDENCE",
        "authorities": [], "input_map_before": None, "input_map_after": None, "output_map": None,
        "actor_count_before_raw": None, "actor_count_before_governed": None,
        "actor_count_after_raw": None, "actor_count_after_governed": None,
        "terrain_material_binding": None, "vegetation_corrections": [], "building_corrections": [],
        "lighting": None, "runtime_promotion_performed": False, "error": None, "traceback": None,
    }
    try:
        contract = load_contract()
        result["authorities"] = validate_authorities(contract)
        result["input_map_before"] = record(INPUT_FILE)
        require(not OUTPUT_FILE.exists() and not unreal.EditorAssetLibrary.does_asset_exist(OUTPUT_ASSET), "Fresh correction map exists")

        levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        actors_api = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        require(levels is not None and actors_api is not None, "Required editor subsystems unavailable")
        require(levels.new_level_from_template(OUTPUT_ASSET, INPUT_ASSET), "Failed to clone Stage07A into Correction01")
        actors = list(actors_api.get_all_level_actors())
        governed = [actor for actor in actors if actor.get_actor_label() != "PCGWorldActor0"]
        result["actor_count_before_raw"] = len(actors)
        result["actor_count_before_governed"] = len(governed)
        require(len(governed) == int(contract["input"]["expected_governed_actor_count"]), f"Stage07A governed actor count changed: {len(governed)}")
        require(len(actors) - len(governed) <= int(contract["input"]["maximum_editor_only_actor_delta"]), "Unexpected editor-only actor count")
        by_label = {actor.get_actor_label(): actor for actor in actors}
        require(len(by_label) == len(actors), "Duplicate inherited actor labels")

        correction = contract["correction"]
        terrain = by_label[str(correction["terrain_actor"])]
        terrain_component = static_component(terrain, unreal)
        planting_soil = unreal.load_asset(str(correction["terrain_material"]))
        require(planting_soil is not None, "Accepted planting-soil material failed to load")
        slot = int(correction["terrain_slot"])
        require(slot < int(terrain_component.get_num_materials()), "Terrain material slot missing")
        before = asset_identity(terrain_component.get_material(slot))
        terrain_component.set_material(slot, planting_soil)
        after = asset_identity(terrain_component.get_material(slot))
        require(after == asset_identity(planting_soil), "Planting-soil binding failed")
        result["terrain_material_binding"] = {"actor": terrain.get_actor_label(), "slot": slot, "before": before, "after": after}

        stage7_vegetation = sorted(
            (actor for actor in actors if actor.get_actor_label().startswith("M01_STAGE07A_Vegetation_")),
            key=lambda actor: actor.get_actor_label(),
        )
        require(len(stage7_vegetation) == int(correction["vegetation_actor_count"]), "Stage07A vegetation count changed")
        scale_multipliers = correction["vegetation_scale_multipliers"]
        max_y = float(correction["vegetation_max_y_cm"])
        for index, actor in enumerate(stage7_vegetation):
            label = actor.get_actor_label()
            species = next((name for name in scale_multipliers if f"Vegetation_{name}_" in label), None)
            require(species is not None, f"Unknown Stage07A vegetation identity: {label}")
            before_location = actor.get_actor_location()
            before_scale = actor.get_actor_scale3d()
            target_y = min(float(before_location.y), 10350.0 + float((index * 173) % 1750))
            actor.set_actor_location(unreal.Vector(before_location.x, target_y, before_location.z), False, True)
            multiplier = float(scale_multipliers[species])
            actor.set_actor_scale3d(unreal.Vector(before_scale.x * multiplier, before_scale.y * multiplier, before_scale.z * multiplier))
            shift = ground_actor(actor, unreal)
            final_location = actor.get_actor_location()
            final_scale = actor.get_actor_scale3d()
            require(float(final_location.y) <= max_y, f"Vegetation outside visible-verge contract: {label}")
            result["vegetation_corrections"].append({
                "label": label, "species": species, "before_location_cm": vector(before_location),
                "after_location_cm": vector(final_location), "before_scale": vector(before_scale),
                "after_scale": vector(final_scale), "multiplier": multiplier, "ground_shift_cm": shift,
            })

        city_parts = sorted(
            (actor for actor in actors if actor.get_actor_label().startswith(("M01_STAGE05R01_City_", "M01_STAGE06_City_", "M01_STAGE07A_City_"))),
            key=lambda actor: actor.get_actor_label(),
        )
        require(len(city_parts) == int(correction["building_part_count"]), f"Building-part count changed: {len(city_parts)}")
        groups: dict[str, list[object]] = {}
        for actor in city_parts:
            identifier = group_id(actor.get_actor_label())
            require(identifier is not None, f"Building-group identity unresolved: {actor.get_actor_label()}")
            groups.setdefault(identifier, []).append(actor)
        require(set(groups) == set(BUILDING_SCALE_FACTORS), "Building-group set changed")
        for identifier in sorted(groups):
            members = groups[identifier]
            require(len(members) == 3, f"Building group {identifier} no longer has three parts")
            factor = BUILDING_SCALE_FACTORS[identifier]
            before_scales = {}
            for actor in members:
                before_scale = actor.get_actor_scale3d()
                before_scales[actor.get_actor_label()] = vector(before_scale)
                actor.set_actor_scale3d(unreal.Vector(before_scale.x * factor[0], before_scale.y * factor[1], before_scale.z * factor[2]))
            structural = next((actor for actor in members if actor.get_actor_label().endswith("_STRUCTURAL")), None)
            require(structural is not None, f"Structural actor missing for group {identifier}")
            origin, extent = structural.get_actor_bounds(False)
            structural_location = structural.get_actor_location()
            shift = terrain_z_cm(float(structural_location.x), float(structural_location.y)) - float(origin.z - extent.z)
            for actor in members:
                location = actor.get_actor_location()
                actor.set_actor_location(unreal.Vector(location.x, location.y, location.z + shift), False, True)
                result["building_corrections"].append({
                    "group": identifier, "label": actor.get_actor_label(), "factor": list(factor),
                    "before_scale": before_scales[actor.get_actor_label()], "after_scale": vector(actor.get_actor_scale3d()),
                    "location_cm": vector(actor.get_actor_location()), "ground_shift_cm": float(shift),
                })

        lighting = correction["lighting"]
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

        after_actors = list(actors_api.get_all_level_actors())
        governed_after = [actor for actor in after_actors if actor.get_actor_label() != "PCGWorldActor0"]
        result["actor_count_after_raw"] = len(after_actors)
        result["actor_count_after_governed"] = len(governed_after)
        require(len(governed_after) == int(contract["input"]["expected_governed_actor_count"]), "Correction changed governed actor count")
        require(len(result["vegetation_corrections"]) == 48, "Vegetation correction receipt count changed")
        require(len(result["building_corrections"]) == 39, "Building correction receipt count changed")
        require(levels.save_current_level(), "Failed to save Correction01 map")
        require(OUTPUT_FILE.is_file(), "Correction01 output map missing")
        result["input_map_after"] = record(INPUT_FILE)
        require(result["input_map_after"] == result["input_map_before"], "Immutable Stage07A map changed")
        result["output_map"] = record(OUTPUT_FILE)
        result["classification"] = "PASSED_STAGE07A_HERO_CORRIDOR01_CORRECTION01_AUTHORING_AWAITING_FINAL_VISUAL"
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        result["traceback"] = traceback.format_exc()
    finally:
        write_json_atomic(RECEIPT, result)

    if str(result["classification"]).startswith("PASSED_"):
        unreal.SystemLibrary.quit_editor()
    else:
        raise RuntimeError(result["error"] or "Stage07A Correction01 authoring failed")


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
