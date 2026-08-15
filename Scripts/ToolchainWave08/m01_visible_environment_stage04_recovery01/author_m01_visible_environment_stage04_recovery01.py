"""Fresh bounded recovery for Mission 1 visible-environment Stage04 authoring."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import struct
import traceback
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
ISOLATED = Path(r"D:\SG52T08_ENV01")
HERE = ROOT / "Scripts/ToolchainWave08/m01_visible_environment_stage04_recovery01"
CONTRACT_PATH = HERE / "stage04_recovery01_authoring_contract.json"
PROJECT = ISOLATED / "Skyguard52.uproject"
PROJECT_AUTHORITY = (3703, "7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a")
INPUT_ASSET = "/Game/M01/Lvl_M01_VisibleEnvironmentStage03"
OUTPUT_ASSET = "/Game/M01/Lvl_M01_VisibleEnvironmentStage04Recovery01"
INPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_VisibleEnvironmentStage03.umap"
OUTPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_VisibleEnvironmentStage04Recovery01.umap"
DESTINATION = "/Game/M01/VisibleEnvironmentStage04Recovery01"
DESTINATION_DISK = ISOLATED / "Content/M01/VisibleEnvironmentStage04Recovery01"
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_VISIBLE_ENVIRONMENT_STAGE04_AUTHORING01_RECOVERY01/attempt_01"
RECEIPT = ATTEMPT / "authoring_receipt.json"

FACADE_SOURCE = ROOT / "Production/Derived/m01-visible-environment-stage04-accepted-glbs-normalized01/M01_CoastalFacadeBay_Production01_UE.glb"
LIGHTHOUSE_SOURCE = ROOT / "Production/Derived/m01-visible-environment-stage04-accepted-glbs-normalized01/M01_Lighthouse_Production_Refinement01_UE.glb"
FACADE_RENDER_MATERIALS = {
    "SM_M01_CoastalFacadeBay_A_BalconyDetails": [
        "M_M01_CoastalFacadeBay_R02_PaleLimestone",
        "M_M01_CoastalFacadeBay_R02_BlackenedSquareSteel",
        "M_M01_CoastalFacadeBay_R02_AgedBrass",
    ],
    "SM_M01_CoastalFacadeBay_A_Glass": ["M_M01_PrewarWindowR03_Glass_CandidateB"],
    "SM_M01_CoastalFacadeBay_A_Interior": [
        "M_M01_PrewarWindowR03_BookRed", "M_M01_PrewarWindowR03_BookGreen",
        "M_M01_PrewarWindowR03_Furniture", "M_M01_PrewarWindowR03_AgedBronzeHardware",
        "M_M01_PrewarWindow_CurtainCloth", "M_M01_PrewarWindow_WarmLamp",
        "M_M01_PrewarWindowR03_Radiator", "M_M01_PrewarWindowR03_InteriorWall",
        "M_M01_PrewarWindow_InteriorWood",
    ],
    "SM_M01_CoastalFacadeBay_A_StructureFrame": [
        "M_M01_PrewarWindow_PaintedTimber", "M_M01_PrewarWindowR03_AgedBronzeHardware",
        "M_M01_PrewarWindowR03_FastenerSlot", "M_M01_PrewarWindow_RevealPlaster",
        "M_M01_PrewarWindow_WeatheredPlaster", "M_M01_CoastalFacadeBay_R02_WarmGreyStucco",
        "M_M01_CoastalFacadeBay_R02_WeatheredPlinth", "M_M01_CoastalFacadeBay_R02_PaleLimestone",
    ],
}
LIGHTHOUSE_RENDER_MATERIALS = {
    "SM_M01_Lighthouse_Details_A": [
        "M_M01_Lighthouse_MasonryJoint", "M_M01_Lighthouse_FoundationStone",
        "M_M01_Lighthouse_BlackMarineMetal", "M_M01_Lighthouse_AgedMarineMetal",
        "M_M01_Lighthouse_BrassHardware", "M_M01_Lighthouse_WindowGlass",
        "M_M01_Lighthouse_WeatheredDoor",
    ],
    "SM_M01_Lighthouse_Lantern_A": [
        "M_M01_Lighthouse_AgedMarineMetal", "M_M01_Lighthouse_BlackMarineMetal",
        "M_M01_Lighthouse_FoundationStone", "M_M01_Lighthouse_LanternGlass",
        "M_M01_Lighthouse_BrassHardware", "M_M01_Lighthouse_FresnelLens",
        "M_M01_Lighthouse_RedMasonry",
    ],
    "SM_M01_Lighthouse_Tower_A": [
        "M_M01_Lighthouse_FoundationStone", "M_M01_Lighthouse_WhiteMasonry",
        "M_M01_Lighthouse_RedMasonry",
    ],
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


def vector(value: object) -> list[float]:
    return [float(value.x), float(value.y), float(value.z)]


def read_glb_document(path: Path) -> dict[str, object]:
    with path.open("rb") as stream:
        magic, version, total = struct.unpack("<4sII", stream.read(12))
        require(magic == b"glTF" and version == 2 and total == path.stat().st_size, f"Invalid GLB: {path}")
        json_length, json_type = struct.unpack("<II", stream.read(8))
        require(json_type == 0x4E4F534A, f"GLB JSON chunk missing: {path}")
        return json.loads(stream.read(json_length).decode("utf-8").rstrip("\x00 \t\r\n"))


def validate_glb(path: Path, authority: dict[str, object], expected: dict[str, list[str]]) -> dict[str, object]:
    require(path.is_file() and path.stat().st_size == int(authority["bytes"]), f"GLB authority missing or changed: {path}")
    require(sha256(path) == str(authority["sha256"]), f"GLB hash changed: {path}")
    document = read_glb_document(path)
    materials = [str(row.get("name", "")) for row in document.get("materials", [])]
    observed: dict[str, list[str]] = {}
    collision: list[str] = []
    for mesh in document.get("meshes", []):
        name = str(mesh.get("name", ""))
        if name.startswith("UCX_"):
            collision.append(name)
        else:
            observed[name] = [materials[int(primitive["material"])] for primitive in mesh.get("primitives", [])]
    require(observed == expected, f"Renderable GLB contract changed: {path.name}: {observed}")
    require(collision, f"Collision contract missing: {path}")
    return {"source": record(path), "render_materials": observed, "collision_meshes": sorted(collision)}


def load_contract() -> dict[str, object]:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    require(contract["contract_id"] == "M01-VISIBLE-ENVIRONMENT-STAGE04-AUTHORING01-RECOVERY01", "Recovery01 contract identity changed")
    return contract


def validate_authorities(contract: dict[str, object]) -> dict[str, object]:
    require(PROJECT.is_file() and PROJECT.stat().st_size == PROJECT_AUTHORITY[0] and sha256(PROJECT) == PROJECT_AUTHORITY[1], "Isolated project authority changed")
    input_spec = contract["input"]
    require(INPUT_FILE.is_file() and INPUT_FILE.stat().st_size == int(input_spec["bytes"]), "Stage03 map byte count changed")
    require(sha256(INPUT_FILE) == str(input_spec["sha256"]), "Stage03 map hash changed")
    for key in ("metadata_receipt", "scene_inventory", "failed_stage04_terminal", "failed_import_probe_terminal", "failed_import_probe_receipt"):
        spec = contract["accepted_sources"][key]
        path = Path(spec["file"])
        require(path.is_file() and path.stat().st_size == int(spec["bytes"]), f"Authority byte count changed: {key}")
        require(sha256(path) == str(spec["sha256"]), f"Authority hash changed: {key}")
    return {
        "facade": validate_glb(FACADE_SOURCE, contract["accepted_sources"]["facade_glb"], FACADE_RENDER_MATERIALS),
        "lighthouse": validate_glb(LIGHTHOUSE_SOURCE, contract["accepted_sources"]["lighthouse_glb"], LIGHTHOUSE_RENDER_MATERIALS),
    }


def assert_fresh() -> None:
    require(not DESTINATION_DISK.exists(), "Fresh Recovery01 Unreal destination exists")
    require(not OUTPUT_FILE.exists(), "Fresh Recovery01 output map exists")
    require(not ATTEMPT.exists(), "Fresh Recovery01 attempt exists")


def offline_contract_test() -> int:
    contract = load_contract()
    validate_authorities(contract)
    assert_fresh()
    compile(Path(__file__).read_text(encoding="utf-8"), __file__, "exec")
    print("PASS_M01_VISIBLE_ENVIRONMENT_STAGE04_RECOVERY01_AUTHORING_CONTRACT")
    return 0


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


def object_path(value: object) -> str:
    return "" if value is None else str(value.get_path_name())


def material_name(slot: object) -> str:
    material = slot.get_editor_property("material_interface")
    return "" if material is None else str(material.get_name())


def set_visible(actor: object, visible: bool, unreal: object) -> None:
    component = actor.get_component_by_class(unreal.StaticMeshComponent)
    require(component is not None, f"StaticMeshComponent missing: {actor.get_actor_label()}")
    component.set_editor_property("visible", bool(visible))
    component.set_editor_property("hidden_in_game", not bool(visible))


def extent_matches(actual: list[float], expected: list[float], tolerance: float) -> bool:
    return all(abs(float(a) - float(e)) <= tolerance for a, e in zip(actual, expected))


def import_source(
    source: Path,
    destination: str,
    render_materials: dict[str, list[str]],
    expected_extents: dict[str, list[float]],
    collision_only_material: str | None,
    unreal: object,
) -> tuple[dict[str, object], list[dict[str, object]], list[dict[str, object]]]:
    pipeline = unreal.InterchangeGenericAssetsPipeline()
    rotation = unreal.Rotator()
    rotation.roll = rotation.pitch = rotation.yaw = 0.0
    pipeline.set_editor_property("import_offset_rotation", rotation)
    pipeline.set_editor_property("scene_name_sub_folder", False)
    pipeline.set_editor_property("asset_type_sub_folders", True)
    pipeline.set_editor_property("use_source_name_for_asset", False)
    common = pipeline.get_editor_property("common_meshes_properties")
    common.set_editor_property("import_sockets", True)
    common.set_editor_property("bake_meshes", True)
    stack = unreal.InterchangePipelineStackOverride()
    stack.add_pipeline(pipeline)

    require(unreal.EditorAssetLibrary.make_directory(destination), f"Failed to create import destination: {destination}")
    task = unreal.AssetImportTask()
    task.filename, task.destination_path, task.destination_name = str(source), destination, ""
    task.automated, task.replace_existing, task.save, task.options = True, False, True, stack
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    registry.scan_paths_synchronous([destination], True, False)
    paths = sorted(unreal.EditorAssetLibrary.list_assets(destination, recursive=True, include_folder=False))
    require(paths, f"Import produced no assets: {source}")

    meshes: dict[str, object] = {}
    rows: list[dict[str, object]] = []
    cleanup: list[dict[str, object]] = []
    tolerance = float(load_contract()["import_contract"]["extent_tolerance_cm"])
    for asset_path in paths:
        asset = unreal.EditorAssetLibrary.load_asset(asset_path)
        require(asset is not None, f"Imported asset failed to load: {asset_path}")
        row: dict[str, object] = {"path": asset_path, "class": asset.get_class().get_name(), "name": asset.get_name()}
        if isinstance(asset, unreal.StaticMesh):
            name = asset.get_name()
            extent = vector(asset.get_bounds().box_extent)
            slots = list(asset.get_editor_property("static_materials"))
            names_before = [material_name(slot) for slot in slots]
            row.update({"bounds_extent_cm": extent, "material_names_before": names_before})
            if name in render_materials:
                expected_names = render_materials[name]
                extras = names_before[len(expected_names):] if names_before[:len(expected_names)] == expected_names else names_before
                if collision_only_material and extras == [collision_only_material]:
                    asset.set_editor_property("static_materials", slots[:len(expected_names)])
                    asset.post_edit_change()
                    cleanup.append({"mesh": name, "removed_final_slot": collision_only_material})
                    slots = list(asset.get_editor_property("static_materials"))
                names_after = [material_name(slot) for slot in slots]
                require(names_after == expected_names, f"Material contract changed: {name}: {names_after}")
                require(extent_matches(extent, expected_extents[name], tolerance), f"Axis/bounds contract failed: {name}: {extent} != {expected_extents[name]}")
                row["material_names_after"] = names_after
                meshes[name] = asset
        rows.append(row)
    require(set(meshes) == set(render_materials), f"Imported semantic meshes changed: {sorted(meshes)}")
    if collision_only_material:
        require({row["mesh"] for row in cleanup} == {
            "SM_M01_CoastalFacadeBay_A_BalconyDetails",
            "SM_M01_CoastalFacadeBay_A_StructureFrame",
        }, f"Collision-only slot cleanup was not exact: {cleanup}")
    try:
        unreal.EditorAssetLibrary.save_directory(destination, only_if_is_dirty=False, recursive=True)
    except TypeError:
        unreal.EditorAssetLibrary.save_directory(destination)
    return meshes, rows, cleanup


def spawn_group(actors_api: object, meshes: dict[str, object], prefix: str, location: list[float], rotation: list[float], unreal: object) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for name, mesh in sorted(meshes.items()):
        actor = actors_api.spawn_actor_from_class(
            unreal.StaticMeshActor, unreal.Vector(*location),
            unreal.Rotator(pitch=float(rotation[0]), yaw=float(rotation[2]), roll=float(rotation[1])), False,
        )
        require(actor is not None, f"Failed to spawn {name}")
        actor.set_actor_label(f"{prefix}_{name.removeprefix('SM_M01_')}")
        actor.set_folder_path("M01/VisibleEnvironmentStage04Recovery01")
        component = actor.get_component_by_class(unreal.StaticMeshComponent)
        require(component is not None, f"StaticMeshComponent missing: {name}")
        component.set_static_mesh(mesh)
        component.set_mobility(unreal.ComponentMobility.STATIC)
        component.set_editor_property("cast_shadow", True)
        component.set_collision_profile_name("BlockAll")
        origin, extent = actor.get_actor_bounds(False)
        rows.append({
            "label": actor.get_actor_label(), "mesh": object_path(mesh),
            "location_cm": vector(actor.get_actor_location()),
            "bounds_origin_cm": vector(origin), "bounds_extent_cm": vector(extent),
        })
    return rows


def scale_and_ground_vegetation(actor: object, multiplier: float, unreal: object) -> dict[str, object]:
    before_scale = actor.get_actor_scale3d()
    actor.set_actor_scale3d(unreal.Vector(before_scale.x * multiplier, before_scale.y * multiplier, before_scale.z * multiplier))
    location = actor.get_actor_location()
    origin, extent = actor.get_actor_bounds(False)
    target = corridor_surface_z_cm(float(location.x), float(location.y))
    shift = target - float(origin.z - extent.z)
    require(abs(shift) <= 350.0, f"Vegetation grounding shift exceeds bound: {actor.get_actor_label()} -> {shift}")
    actor.set_actor_location(unreal.Vector(location.x, location.y, location.z + shift), False, True)
    after_origin, after_extent = actor.get_actor_bounds(False)
    require(abs(float(after_origin.z - after_extent.z) - target) <= 1.0, f"Vegetation grounding failed: {actor.get_actor_label()}")
    return {
        "label": actor.get_actor_label(), "multiplier": multiplier,
        "scale_before": vector(before_scale), "scale_after": vector(actor.get_actor_scale3d()),
        "target_bottom_cm": target,
    }


def run_unreal() -> None:
    import unreal

    result: dict[str, object] = {
        "schema": "skyguard.m01-visible-environment-stage04-recovery01.authoring01.v1",
        "classification": "FAILED_WITH_EVIDENCE", "authorities": None,
        "input_map_before": None, "input_map_after": None, "output_map": None,
        "imported_assets": {}, "material_slot_cleanup": [], "material_calibration": [],
        "hidden_actors": [], "created_actors": [], "vegetation_adjustments": [],
        "lighting": {}, "actor_count_before": None, "actor_count_after": None,
        "rollback_manifest": {"created_asset_namespace": DESTINATION, "created_map": OUTPUT_ASSET, "accepted_input_mutated": False},
        "runtime_promotion_performed": False, "error": None, "traceback": None,
    }
    try:
        contract = load_contract()
        result["authorities"] = validate_authorities(contract)
        result["input_map_before"] = record(INPUT_FILE)
        require(not DESTINATION_DISK.exists() and not unreal.EditorAssetLibrary.does_directory_exist(DESTINATION), "Fresh Recovery01 destination exists")
        require(not OUTPUT_FILE.exists() and not unreal.EditorAssetLibrary.does_asset_exist(OUTPUT_ASSET), "Fresh Recovery01 map exists")

        import_spec = contract["import_contract"]
        facade_destination, lighthouse_destination = DESTINATION + "/FacadeBayR02", DESTINATION + "/LighthouseR04"
        facade_meshes, facade_rows, facade_cleanup = import_source(
            FACADE_SOURCE, facade_destination, FACADE_RENDER_MATERIALS,
            import_spec["facade_expected_extents_cm"], str(import_spec["collision_only_material"]), unreal,
        )
        lighthouse_meshes, lighthouse_rows, lighthouse_cleanup = import_source(
            LIGHTHOUSE_SOURCE, lighthouse_destination, LIGHTHOUSE_RENDER_MATERIALS,
            import_spec["lighthouse_expected_extents_cm"], None, unreal,
        )
        require(not lighthouse_cleanup, "Lighthouse cleanup must remain empty")
        result["imported_assets"] = {"facade": facade_rows, "lighthouse": lighthouse_rows}
        result["material_slot_cleanup"] = facade_cleanup

        replacements = {source: unreal.load_asset(path) for source, path in contract["material_calibration"].items()}
        require(all(value is not None for value in replacements.values()), "Accepted local calibration materials failed to load")
        calibration: list[dict[str, object]] = []
        for mesh in facade_meshes.values():
            for index, slot in enumerate(list(mesh.get_editor_property("static_materials"))):
                source_name = material_name(slot)
                replacement = replacements.get(source_name)
                if replacement is not None:
                    mesh.set_material(index, replacement)
                    calibration.append({"mesh": mesh.get_name(), "slot": index, "source": source_name, "replacement": object_path(replacement)})
            mesh.post_edit_change()
        require(calibration, "Facade material calibration found no governed slots")
        result["material_calibration"] = calibration
        try:
            unreal.EditorAssetLibrary.save_directory(facade_destination, only_if_is_dirty=False, recursive=True)
        except TypeError:
            unreal.EditorAssetLibrary.save_directory(facade_destination)

        levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        actors_api = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        require(levels is not None and actors_api is not None, "Required editor subsystems unavailable")
        require(levels.new_level_from_template(OUTPUT_ASSET, INPUT_ASSET), "Failed to clone Stage03 into fresh Stage04 Recovery01")
        actors = list(actors_api.get_all_level_actors())
        result["actor_count_before"] = len(actors)
        require(len(actors) == int(contract["input"]["actor_count"]), f"Stage03 actor count changed: {len(actors)}")
        by_label = {actor.get_actor_label(): actor for actor in actors}

        hidden: list[str] = []
        for label in contract["placement"]["lighthouse"]["legacy_labels_to_hide"]:
            require(label in by_label, f"Legacy lighthouse actor missing: {label}")
            set_visible(by_label[label], False, unreal)
            hidden.append(label)
        for actor in actors:
            if any(actor.get_actor_label().startswith(prefix) for prefix in contract["placement"]["facade"]["legacy_window_label_prefixes_to_hide"]):
                set_visible(actor, False, unreal)
                hidden.append(actor.get_actor_label())
        require(len(hidden) == 75, f"Expected 75 bounded legacy actors hidden; found {len(hidden)}")
        result["hidden_actors"] = sorted(hidden)

        created: list[dict[str, object]] = []
        facade = contract["placement"]["facade"]
        for column, x_cm in enumerate(facade["column_centers_x_cm"]):
            for floor in range(int(facade["floor_count"])):
                location = [float(x_cm), float(facade["y_cm"]), float(facade["base_z_cm"]) + floor * float(facade["floor_spacing_cm"])]
                created += spawn_group(actors_api, facade_meshes, f"M01_STAGE04R01_Facade_C{column:02d}_F{floor:02d}", location, [0.0, 0.0, float(facade["yaw_degrees"])], unreal)
        lighthouse = contract["placement"]["lighthouse"]
        created += spawn_group(actors_api, lighthouse_meshes, "M01_STAGE04R01_LighthouseHero", lighthouse["asset_location_cm"], lighthouse["asset_rotation_degrees"], unreal)
        require(len(created) == 35, f"Expected 35 Recovery01 accepted-asset actors; found {len(created)}")
        result["created_actors"] = created

        vegetation_contract = contract["placement"]["vegetation"]
        for actor in actors:
            label = actor.get_actor_label()
            if not label.startswith("M01_PHV02_"):
                continue
            if "fir_sapling" in label or "pine_sapling" in label:
                multiplier = float(vegetation_contract["tree_scale_multiplier"])
            elif "shrub_02" in label:
                multiplier = float(vegetation_contract["shrub_scale_multiplier"])
            else:
                multiplier = float(vegetation_contract["groundcover_scale_multiplier"])
            result["vegetation_adjustments"].append(scale_and_ground_vegetation(actor, multiplier, unreal))
        require(len(result["vegetation_adjustments"]) == 28, "Expected 28 Recovery01 vegetation adjustments")

        lighting = contract["lighting"]
        sun = by_label["M01_RS01_Sun"].get_component_by_class(unreal.DirectionalLightComponent)
        fill = by_label["M01_PR01_FillSun"].get_component_by_class(unreal.DirectionalLightComponent)
        sky = by_label["M01_RS01_SkyLight"].get_component_by_class(unreal.SkyLightComponent)
        post = by_label["M01_RS01_PostProcess"]
        require(sun is not None and fill is not None and sky is not None, "Recovery01 lighting components unavailable")
        before = {"sun": float(sun.get_editor_property("intensity")), "fill": float(fill.get_editor_property("intensity")), "sky": float(sky.get_editor_property("intensity"))}
        sun.set_editor_property("intensity", float(lighting["sun_intensity"]))
        fill.set_editor_property("intensity", float(lighting["fill_intensity"]))
        fill.set_editor_property("cast_shadows", False)
        sky.set_editor_property("intensity", float(lighting["skylight_intensity"]))
        sky.set_editor_property("real_time_capture", True)
        settings = post.get_editor_property("settings")
        for name, value in (
            ("auto_exposure_bias", lighting["exposure_bias"]), ("film_slope", lighting["film_slope"]),
            ("film_toe", lighting["film_toe"]), ("film_shoulder", lighting["film_shoulder"]),
            ("film_white_clip", lighting["film_white_clip"]), ("film_black_clip", lighting["film_black_clip"]),
        ):
            settings.set_editor_property("override_" + name, True)
            settings.set_editor_property(name, float(value))
        post.set_editor_property("settings", settings)
        result["lighting"] = {"before": before, "after": lighting}

        actors_after = list(actors_api.get_all_level_actors())
        result["actor_count_after"] = len(actors_after)
        require(len(actors_after) == int(contract["output"]["expected_actor_count"]), f"Recovery01 actor count changed: {len(actors_after)}")
        require(levels.save_current_level(), "Failed to save fresh Stage04 Recovery01 map")
        require(OUTPUT_FILE.is_file(), "Fresh Stage04 Recovery01 map was not created")
        result["input_map_after"] = record(INPUT_FILE)
        require(result["input_map_after"] == result["input_map_before"], "Immutable Stage03 input map changed")
        result["output_map"] = record(OUTPUT_FILE)
        result["classification"] = "PASSED_STAGE04_RECOVERY01_AUTHORING_AWAITING_GOVERNED_D3D12_VISUAL_PROOF"
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        result["traceback"] = traceback.format_exc()
    finally:
        write_json_atomic(RECEIPT, result)

    if str(result["classification"]).startswith("PASSED_"):
        unreal.SystemLibrary.quit_editor()
    else:
        raise RuntimeError(result["error"] or "Stage04 Recovery01 authoring failed")


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
