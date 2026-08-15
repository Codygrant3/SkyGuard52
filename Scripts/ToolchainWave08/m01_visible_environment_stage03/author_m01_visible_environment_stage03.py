"""Author a fresh Mission 1 Stage03 map from immutable Stage02 evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import traceback
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
PROJECT_ROOT = Path(r"D:\SG52T08_ENV01")
SCRIPT_ROOT = ROOT / "Scripts/ToolchainWave08/m01_visible_environment_stage03"
CONTRACT_PATH = SCRIPT_ROOT / "stage03_authoring_contract.json"
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_VISIBLE_ENVIRONMENT_STAGE03_AUTHORING01/attempt_01"
RECEIPT = ATTEMPT / "authoring_receipt.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def record(path: Path) -> dict[str, object]:
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)}


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json_atomic(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def verify_record(entry: dict[str, object]) -> dict[str, object]:
    path = Path(str(entry["path"]))
    require(path.is_file(), f"Authority missing: {path}")
    require(path.stat().st_size == int(entry["bytes"]), f"Authority byte mismatch: {path}")
    require(sha256(path) == str(entry["sha256"]), f"Authority hash mismatch: {path}")
    return record(path)


def verify_contract(contract: dict[str, object]) -> list[dict[str, object]]:
    require(contract["classification"] == "PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_STAGE03_AUTHORING", "Contract classification changed")
    rows = [verify_record(contract["project"]), verify_record(contract["editor"])]
    rows.append(verify_record({key: contract["input_map"][key] for key in ("path", "bytes", "sha256")}))
    rows.extend(verify_record(entry) for entry in contract["authorities"])
    rows.extend(verify_record(entry) for entry in contract["reused_assets"])
    require(contract["policies"]["single_unreal_launch"] is True, "Single-launch policy changed")
    require(contract["policies"]["automatic_retries"] == 0, "Automatic-retry policy changed")
    require(contract["policies"]["runtime_promotion"] is False, "Promotion guard changed")
    return rows


def assert_fresh(contract: dict[str, object]) -> None:
    output = contract["output"]
    for key in ("path", "attempt", "terminal_manifest", "emergency_receipt"):
        require(not Path(str(output[key])).exists(), f"Fresh namespace already exists: {output[key]}")


def source_transform_is_bounded() -> None:
    source = Path(__file__).read_text(encoding="utf-8")
    require("unreal.Rotator(roll=0.0, pitch=0.0, yaw=float(intended_yaw))" in source, "Named Rotator correction is absent")
    require("source_receipt[\"placements\"]" in source, "Frozen Stage02 placement authority is not consumed")
    require("levels.new_level_from_template" in source, "Fresh-map creation is absent")
    require("levels.save_current_level()" in source, "Fresh-map save is absent")


def offline_contract_test() -> int:
    contract = load_json(CONTRACT_PATH)
    verify_contract(contract)
    assert_fresh(contract)
    source_transform_is_bounded()
    print("PASS_M01_VISIBLE_ENVIRONMENT_STAGE03_OFFLINE_CONTRACT")
    return 0


def promenade_surface_z_cm(x_cm: float, y_cm: float) -> float:
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


def asset_identity(value: object) -> str:
    if value is None:
        return ""
    try:
        return str(value.get_path_name())
    except Exception:
        return str(value)


def vector(value: object) -> list[float]:
    return [float(value.x), float(value.y), float(value.z)]


def find_exact(actors: list[object], label: str) -> object:
    matches = [actor for actor in actors if actor.get_actor_label() == label]
    require(len(matches) == 1, f"Expected exactly one actor {label}; found {len(matches)}")
    return matches[0]


def static_component(actor: object) -> object:
    component = actor.get_component_by_class(unreal.StaticMeshComponent)
    require(component is not None, f"StaticMeshComponent missing: {actor.get_actor_label()}")
    return component


def load_asset(path: str) -> object:
    asset = unreal.load_asset(path)
    require(asset is not None, f"Asset failed to load: {path}")
    return asset


def set_actor_visibility(actor: object, visible: bool) -> None:
    component = static_component(actor)
    component.set_editor_property("visible", bool(visible))
    component.set_editor_property("hidden_in_game", not bool(visible))


def create_ground_material(contract: dict[str, object]) -> tuple[object, dict[str, object]]:
    corrections = contract["corrections"]
    source_path = str(corrections["landscape_material_source"])
    output_path = str(corrections["landscape_material_output"])
    output_directory, output_name = output_path.rsplit("/", 1)
    require(not unreal.EditorAssetLibrary.does_asset_exist(output_path), f"Fresh material already exists: {output_path}")
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    source = load_asset(source_path)
    duplicated = tools.duplicate_asset(output_name, output_directory, source)
    require(duplicated is not None, "Could not duplicate Stage03 landscape material")
    textures = {name: load_asset(path) for name, path in corrections["landscape_textures"].items()}
    library = unreal.MaterialEditingLibrary
    for name, texture in textures.items():
        library.set_material_instance_texture_parameter_value(duplicated, name, texture)
    for name in ("BaseColorTexture_OffsetScale", "MetallicRoughnessTexture_OffsetScale", "NormalTexture_OffsetScale"):
        library.set_material_instance_vector_parameter_value(duplicated, name, unreal.LinearColor(0.0, 0.0, 126.0, 47.0))
    library.set_material_instance_vector_parameter_value(duplicated, "BaseColorFactor", unreal.LinearColor(0.62, 0.68, 0.58, 1.0))
    library.set_material_instance_scalar_parameter_value(duplicated, "NormalScale", 0.72)
    library.set_material_instance_scalar_parameter_value(duplicated, "RoughnessFactor", 0.96)
    require(unreal.EditorAssetLibrary.save_loaded_asset(duplicated, only_if_is_dirty=False), "Could not save Stage03 landscape material")
    return duplicated, {
        "source": source_path,
        "output": asset_identity(duplicated),
        "textures": {name: asset_identity(texture) for name, texture in textures.items()},
        "base_color_factor": [0.62, 0.68, 0.58, 1.0],
        "tiling": [0.0, 0.0, 126.0, 47.0],
    }


def ground_actor(actor: object, target_z: float) -> dict[str, object]:
    before_origin, before_extent = actor.get_actor_bounds(False)
    before_bottom = float(before_origin.z - before_extent.z)
    location = actor.get_actor_location()
    actor.set_actor_location(unreal.Vector(location.x, location.y, location.z + target_z - before_bottom), False, True)
    after_origin, after_extent = actor.get_actor_bounds(False)
    after_bottom = float(after_origin.z - after_extent.z)
    require(abs(after_bottom - target_z) <= 1.0, f"Grounding failed: {actor.get_actor_label()}")
    return {"before_bottom_cm": before_bottom, "target_z_cm": target_z, "after_bottom_cm": after_bottom}


def spawn_lighthouse_group(actors_api: object, mesh: object, group: str, location: object) -> dict[str, object]:
    actor = actors_api.spawn_actor_from_class(
        unreal.StaticMeshActor,
        location,
        unreal.Rotator(roll=0.0, pitch=0.0, yaw=0.0),
        False,
    )
    require(actor is not None, f"Could not spawn Stage03 lighthouse {group}")
    actor.set_actor_label(f"M01_STAGE03_Lighthouse_Hero_{group}")
    actor.set_folder_path("M01/VisibleEnvironmentStage03/Landmarks")
    component = static_component(actor)
    component.set_static_mesh(mesh)
    component.set_mobility(unreal.ComponentMobility.STATIC)
    component.set_editor_property("cast_shadow", True)
    return {"label": actor.get_actor_label(), "asset": asset_identity(mesh), "location_cm": vector(actor.get_actor_location())}


def run_unreal() -> int:
    contract = load_json(CONTRACT_PATH)
    result: dict[str, object] = {
        "schema": "skyguard.m01-visible-environment-stage03.authoring-receipt.v1",
        "classification": "FAILED_WITH_EVIDENCE",
        "runtime_promotion": False,
        "authorities": [],
        "input_map_before": None,
        "input_map_after": None,
        "output_map": None,
        "actor_count_before": None,
        "actor_count_after": None,
        "vegetation_corrections": [],
        "hidden_legacy_overlaps": [],
        "landscape_material": None,
        "lighthouse": [],
        "lighting": None,
        "error": None,
        "traceback": None,
    }
    try:
        result["authorities"] = verify_contract(contract)
        input_path = Path(str(contract["input_map"]["path"]))
        output_path = Path(str(contract["output"]["path"]))
        result["input_map_before"] = record(input_path)
        require(not output_path.exists(), "Fresh Stage03 output map already exists")
        require(not unreal.EditorAssetLibrary.does_asset_exist(str(contract["output"]["asset"])), "Fresh Stage03 map asset already exists")

        levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        actors_api = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        require(levels is not None and actors_api is not None, "Required editor subsystems unavailable")
        require(levels.new_level_from_template(str(contract["output"]["asset"]), str(contract["input_map"]["asset"])), "Could not clone Stage02 map")
        actors = list(actors_api.get_all_level_actors())
        result["actor_count_before"] = len(actors)
        require(len(actors) == int(contract["input_map"]["expected_actor_count"]), f"Stage02 actor count changed: {len(actors)}")

        source_receipt = load_json(Path(str(contract["authorities"][1]["path"])))
        placements = {str(row["label"]): row for row in source_receipt["placements"]}
        vegetation = [actor for actor in actors if actor.get_actor_label().startswith("M01_PHV02_")]
        require(len(vegetation) == 28, f"Expected 28 Stage02 vegetation actors; found {len(vegetation)}")
        for actor in sorted(vegetation, key=lambda item: item.get_actor_label()):
            label = actor.get_actor_label()
            require(label in placements, f"Frozen placement missing: {label}")
            row = placements[label]
            intended_yaw = float(row["yaw_degrees"])
            actor.set_actor_rotation(unreal.Rotator(roll=0.0, pitch=0.0, yaw=float(intended_yaw)), False)
            location = actor.get_actor_location()
            grounding = ground_actor(actor, promenade_surface_z_cm(float(location.x), float(location.y)))
            rotation = actor.get_actor_rotation()
            require(abs(float(rotation.pitch)) <= 0.01 and abs(float(rotation.roll)) <= 0.01, f"Vegetation upright validation failed: {label}")
            result["vegetation_corrections"].append({
                "label": label,
                "intended_yaw_degrees": intended_yaw,
                "rotation_degrees": {"pitch": float(rotation.pitch), "yaw": float(rotation.yaw), "roll": float(rotation.roll)},
                "grounding": grounding,
            })

        for label in contract["corrections"]["legacy_overlap_labels_hidden"]:
            actor = find_exact(actors, str(label))
            set_actor_visibility(actor, False)
            result["hidden_legacy_overlaps"].append(label)

        landscape = find_exact(actors, "M01_A01_Landscape_Production")
        ground_material, material_record = create_ground_material(contract)
        landscape.set_editor_property("landscape_material", ground_material)
        require(asset_identity(landscape.get_editor_property("landscape_material")) == asset_identity(ground_material), "Landscape material readback failed")
        result["landscape_material"] = material_record

        center_x, center_y = [float(value) for value in contract["corrections"]["lighthouse_center_cm"]]
        target_bottom = promenade_surface_z_cm(center_x, center_y)
        lighthouse_assets = {
            "DETAILS": "/Game/M01/EnvKit02/M01_LIGHTHOUSE_A/StaticMeshes/SM_M01_LighthouseA_DETAILS",
            "GLAZING": "/Game/M01/EnvKit02/M01_LIGHTHOUSE_A/StaticMeshes/SM_M01_LighthouseA_GLAZING",
            "STRUCTURAL": "/Game/M01/EnvKit02/M01_LIGHTHOUSE_A/StaticMeshes/SM_M01_LighthouseA_STRUCTURAL",
        }
        structural = load_asset(lighthouse_assets["STRUCTURAL"])
        bounds = structural.get_bounds()
        structural_location = unreal.Vector(center_x - float(bounds.origin.x), center_y - float(bounds.origin.y), target_bottom - float(bounds.origin.z - bounds.box_extent.z))
        for group in ("STRUCTURAL", "GLAZING", "DETAILS"):
            result["lighthouse"].append(spawn_lighthouse_group(actors_api, load_asset(lighthouse_assets[group]), group, structural_location))
        structural_actor = find_exact(list(actors_api.get_all_level_actors()), "M01_STAGE03_Lighthouse_Hero_STRUCTURAL")
        lighthouse_origin, lighthouse_extent = structural_actor.get_actor_bounds(False)
        require(abs(float(lighthouse_origin.z - lighthouse_extent.z) - target_bottom) <= 1.0, "Lighthouse grounding failed")

        lighting = contract["corrections"]["lighting"]
        sun = find_exact(actors, "M01_RS01_Sun")
        fill = find_exact(actors, "M01_PR01_FillSun")
        sky = find_exact(actors, "M01_RS01_SkyLight")
        post = find_exact(actors, "M01_RS01_PostProcess")
        sun_component = sun.get_component_by_class(unreal.DirectionalLightComponent)
        fill_component = fill.get_component_by_class(unreal.DirectionalLightComponent)
        sky_component = sky.get_component_by_class(unreal.SkyLightComponent)
        require(sun_component is not None and fill_component is not None and sky_component is not None, "Stage03 lighting components unavailable")
        before = {
            "sun": float(sun_component.get_editor_property("intensity")),
            "fill": float(fill_component.get_editor_property("intensity")),
            "sky": float(sky_component.get_editor_property("intensity")),
        }
        sun_component.set_editor_property("intensity", float(lighting["sun_intensity"]))
        sun_component.set_editor_property("use_temperature", False)
        fill_component.set_editor_property("intensity", float(lighting["fill_intensity"]))
        fill_component.set_editor_property("cast_shadows", False)
        sky_component.set_editor_property("intensity", float(lighting["skylight_intensity"]))
        sky_component.set_editor_property("real_time_capture", True)
        sky_component.set_editor_property("lower_hemisphere_is_black", False)
        sky_component.set_editor_property("lower_hemisphere_color", unreal.LinearColor(0.18, 0.23, 0.27, 1.0))
        settings = post.get_editor_property("settings")
        for property_name, value in (
            ("auto_exposure_bias", lighting["exposure_bias"]),
            ("film_slope", lighting["film_slope"]),
            ("film_toe", lighting["film_toe"]),
            ("film_shoulder", lighting["film_shoulder"]),
            ("film_white_clip", lighting["film_white_clip"]),
            ("film_black_clip", lighting["film_black_clip"]),
        ):
            settings.set_editor_property("override_" + property_name, True)
            settings.set_editor_property(property_name, float(value))
        post.set_editor_property("settings", settings)
        result["lighting"] = {"before": before, "after": lighting}

        after = list(actors_api.get_all_level_actors())
        result["actor_count_after"] = len(after)
        require(len(after) == int(contract["output"]["expected_actor_count"]), f"Stage03 final actor count changed: {len(after)}")
        require(len(result["vegetation_corrections"]) == 28, "Stage03 vegetation correction count changed")
        require(len(result["lighthouse"]) == 3, "Stage03 lighthouse group count changed")
        require(levels.save_current_level(), "Could not save fresh Stage03 map")
        require(output_path.is_file(), "Stage03 output map was not created")
        result["output_map"] = record(output_path)
        result["input_map_after"] = record(input_path)
        require(result["input_map_after"] == result["input_map_before"], "Accepted Stage02 input map changed")
        result["classification"] = "PASSED_STAGE03_AUTHORING_AWAITING_D3D12_VISUAL_PROOF"
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        result["traceback"] = traceback.format_exc()
    finally:
        write_json_atomic(RECEIPT, result)
    return 0 if str(result["classification"]).startswith("PASSED_") else 3


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline-contract-test", action="store_true")
    args = parser.parse_args()
    if args.offline_contract_test:
        return offline_contract_test()
    global unreal
    import unreal
    return run_unreal()


if __name__ == "__main__":
    raise SystemExit(main())
