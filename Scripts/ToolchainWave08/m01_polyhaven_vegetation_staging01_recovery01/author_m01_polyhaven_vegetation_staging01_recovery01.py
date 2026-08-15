"""One-shot reversible UE 5.8 staging import for accepted Poly Haven vegetation candidates."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import traceback
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
PROJECT_ROOT = Path(r"D:\SG52T08_ENV01")
CONTRACT_PATH = ROOT / "Scripts/ToolchainWave08/m01_polyhaven_vegetation_staging01_recovery01/vegetation_staging01_recovery01_contract.json"
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_POLYHAVEN_VEGETATION_STAGING01_RECOVERY01/attempt_01"
RECEIPT = ATTEMPT / "authoring_receipt.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def record(path: Path) -> dict[str, object]:
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def load_contract() -> dict[str, object]:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def verify_file(entry: dict[str, object]) -> dict[str, object]:
    path = Path(str(entry["path"]))
    require(path.is_file(), f"Authority missing: {path}")
    require(path.stat().st_size == int(entry["bytes"]), f"Authority byte mismatch: {path}")
    require(sha256(path) == str(entry["sha256"]), f"Authority hash mismatch: {path}")
    return record(path)


def verify_authorities(contract: dict[str, object]) -> list[dict[str, object]]:
    rows = [verify_file(contract["project"]), verify_file(contract["editor"])]
    rows.extend(verify_file(entry) for entry in contract["accepted_source_authorities"])
    input_map = contract["input_map"]
    rows.append(verify_file({"path": input_map["path"], "bytes": input_map["bytes"], "sha256": input_map["sha256"]}))

    manifest_path = Path(str(contract["accepted_source_authorities"][3]["path"]))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_assets = {str(asset["asset_id"]): asset for asset in manifest["assets"]}
    expected_ids = [str(asset["id"]) for asset in contract["assets"]]
    require(set(expected_ids).issubset(manifest_assets), "Contract asset is absent from the frozen quarantine manifest")
    require("tree_small_02" not in expected_ids, "Held tree_small_02 entered staging contract")
    for spec in contract["assets"]:
        asset_id = str(spec["id"])
        gltf = Path(str(spec["gltf"]))
        require(gltf.is_file(), f"Source glTF missing: {gltf}")
        require(gltf.stat().st_size == int(spec["gltf_bytes"]), f"Source glTF byte mismatch: {gltf}")
        require(sha256(gltf) == str(spec["gltf_sha256"]), f"Source glTF hash mismatch: {gltf}")
        manifest_rows = {str(item["path"]): item for item in manifest_assets[asset_id]["downloads"]}
        require(str(gltf) in manifest_rows, f"Source glTF is not licensed-manifest governed: {gltf}")
        for item in manifest_assets[asset_id]["downloads"]:
            dependency = Path(str(item["path"]))
            require(dependency.is_file(), f"Source dependency missing: {dependency}")
            require(dependency.stat().st_size == int(item["bytes"]), f"Source dependency byte mismatch: {dependency}")
            require(sha256(dependency) == str(item["sha256"]), f"Source dependency hash mismatch: {dependency}")
    return rows


def assert_fresh(contract: dict[str, object]) -> None:
    fresh = contract["fresh_outputs"]
    for key in ("asset_disk_root", "map_path", "attempt", "terminal_manifest", "emergency_receipt"):
        require(not Path(str(fresh[key])).exists(), f"Fresh namespace already exists: {fresh[key]}")


def offline_contract_test() -> int:
    contract = load_contract()
    require(contract["classification"] == "PASSED_READY_FOR_EXPLICIT_SINGLE_UNREAL_STAGING_AUTHORIZATION", "Contract classification changed")
    verify_authorities(contract)
    assert_fresh(contract)
    require(sum(int(asset["placement_count"]) for asset in contract["assets"]) == int(contract["policies"]["map_placement_count"]), "Placement count contract mismatch")
    compile(Path(__file__).read_text(encoding="utf-8"), __file__, "exec")
    print("PASS_M01_POLYHAVEN_VEGETATION_STAGING01_RECOVERY01_OFFLINE_CONTRACT")
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


PLACEMENTS = {
    "fir_sapling": [(7200.0, 9550.0, 17.0, 0.94), (20700.0, 9600.0, 211.0, 1.02)],
    "pine_sapling_small": [(10850.0, 9650.0, 103.0, 0.97), (16400.0, 9525.0, 286.0, 1.03)],
    "shrub_02": [
        (6100.0, 9250.0, 12.0, 0.88), (8900.0, 9300.0, 74.0, 1.02),
        (11800.0, 9180.0, 139.0, 0.94), (14800.0, 9320.0, 203.0, 1.06),
        (17800.0, 9190.0, 267.0, 0.91), (21500.0, 9290.0, 331.0, 1.00),
    ],
    "shrub_04": [
        (6900.0, 8780.0, 33.0, 1.04), (8400.0, 8860.0, 81.0, 0.92),
        (10300.0, 8820.0, 128.0, 1.08), (12600.0, 8910.0, 176.0, 0.97),
        (15100.0, 8790.0, 223.0, 1.03), (17300.0, 8890.0, 271.0, 0.95),
        (19600.0, 8810.0, 318.0, 1.06), (22000.0, 8900.0, 7.0, 0.99),
    ],
    "grass_medium_02": [
        (6400.0, 9020.0, 19.0, 0.82), (7900.0, 9100.0, 56.0, 0.91),
        (9500.0, 9000.0, 93.0, 0.86), (11200.0, 9090.0, 130.0, 0.95),
        (13100.0, 9010.0, 167.0, 0.88), (15000.0, 9100.0, 204.0, 0.93),
        (17000.0, 9000.0, 241.0, 0.84), (18800.0, 9090.0, 278.0, 0.96),
        (20500.0, 9010.0, 315.0, 0.89), (22200.0, 9100.0, 352.0, 0.94),
    ],
}


def vector(value: object) -> list[float]:
    return [float(value.x), float(value.y), float(value.z)]


def material_record(material: object) -> dict[str, object]:
    row: dict[str, object] = {
        "path": material.get_path_name(),
        "class": material.get_class().get_name(),
        "name": material.get_name(),
        "blend_mode": None,
        "two_sided": None,
    }
    for prop in ("blend_mode", "two_sided"):
        try:
            row[prop] = str(material.get_editor_property(prop)) if prop == "blend_mode" else bool(material.get_editor_property(prop))
        except Exception:
            pass
    return row


def import_candidate(unreal: object, spec: dict[str, object], root_asset: str) -> tuple[object, dict[str, object]]:
    asset_id = str(spec["id"])
    destination = f"{root_asset}/{asset_id}"
    require(unreal.EditorAssetLibrary.make_directory(destination), f"Could not create asset destination: {destination}")

    pipeline = unreal.InterchangeGenericAssetsPipeline()
    pipeline.set_editor_property("scene_name_sub_folder", False)
    pipeline.set_editor_property("asset_type_sub_folders", False)
    pipeline.set_editor_property("use_source_name_for_asset", True)
    common = pipeline.get_editor_property("common_meshes_properties")
    common.set_editor_property("import_sockets", False)
    common.set_editor_property("bake_meshes", True)
    mesh_pipeline = pipeline.get_editor_property("mesh_pipeline")
    combine_enum = getattr(unreal, "InterchangeCombineStaticMeshesBehavior", None)
    require(combine_enum is not None, "UE 5.8 Interchange combine enum is unavailable")
    mesh_pipeline.set_editor_property("combine_static_meshes_behavior", combine_enum.ALL)
    mesh_pipeline.set_editor_property("collision", False)
    mesh_pipeline.set_editor_property("build_nanite", bool(spec["nanite"]))
    mesh_pipeline.set_editor_property("nanite_triangle_threshold", 0)
    mesh_pipeline.set_editor_property("generate_lightmap_u_vs", True)
    mesh_pipeline.set_editor_property("generate_distance_field_as_if_two_sided", True)
    material_pipeline = pipeline.get_editor_property("material_pipeline")
    material_pipeline.set_editor_property("import_materials", True)
    texture_pipeline = material_pipeline.get_editor_property("texture_pipeline")
    texture_pipeline.set_editor_property("import_textures", True)
    stack = unreal.InterchangePipelineStackOverride()
    stack.add_pipeline(pipeline)

    task = unreal.AssetImportTask()
    task.filename = str(spec["gltf"])
    task.destination_path = destination
    task.destination_name = ""
    task.automated = True
    task.replace_existing = False
    task.save = True
    task.options = stack
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])

    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    registry.scan_paths_synchronous([destination], True, False)
    imported_paths = sorted(unreal.EditorAssetLibrary.list_assets(destination, recursive=True, include_folder=False))
    require(imported_paths, f"Interchange imported no assets for {asset_id}")
    static_meshes = []
    imported_rows = []
    for asset_path in imported_paths:
        asset = unreal.EditorAssetLibrary.load_asset(asset_path)
        require(asset is not None, f"Imported asset failed to load: {asset_path}")
        imported_rows.append({"path": asset_path, "class": asset.get_class().get_name(), "name": asset.get_name()})
        if isinstance(asset, unreal.StaticMesh):
            static_meshes.append(asset)
    require(len(static_meshes) == 1, f"Expected one combined StaticMesh for {asset_id}; found {len(static_meshes)}")
    mesh = static_meshes[0]
    target_name = "SM_M01_PHV_" + "".join(part.capitalize() for part in asset_id.split("_"))
    target_path = f"{destination}/{target_name}"
    if mesh.get_path_name().split(".")[0] != target_path:
        require(unreal.EditorAssetLibrary.rename_asset(mesh.get_path_name().split(".")[0], target_path), f"StaticMesh rename failed: {asset_id}")
        mesh = unreal.EditorAssetLibrary.load_asset(target_path)
    require(isinstance(mesh, unreal.StaticMesh), f"Renamed asset is not a StaticMesh: {target_path}")

    subsystem = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    if subsystem is not None:
        subsystem.remove_collisions(mesh)
    settings = mesh.get_editor_property("nanite_settings")
    settings.enabled = bool(spec["nanite"])
    mesh.set_editor_property("nanite_settings", settings)
    unreal.EditorAssetLibrary.set_metadata_tag(mesh, "Skyguard.SourceProvider", "Poly Haven")
    unreal.EditorAssetLibrary.set_metadata_tag(mesh, "Skyguard.SourceLicense", "CC0-1.0")
    unreal.EditorAssetLibrary.set_metadata_tag(mesh, "Skyguard.SourceAssetId", asset_id)
    unreal.EditorAssetLibrary.set_metadata_tag(mesh, "Skyguard.SourceSha256", str(spec["gltf_sha256"]))
    unreal.EditorAssetLibrary.set_metadata_tag(mesh, "Skyguard.RuntimePromotionAllowed", "false")
    unreal.EditorAssetLibrary.set_metadata_tag(mesh, "Skyguard.DensityPolicy", str(spec["density_policy"]))

    actual = vector(mesh.get_bounds().box_extent)
    actual_full = [abs(value) * 2.0 for value in actual]
    expected = [float(value) for value in spec["expected_dimensions_cm"]]
    errors = [abs(a - e) / max(e, 0.001) for a, e in zip(sorted(actual_full), sorted(expected))]
    require(max(errors) <= 0.12, f"Imported bounds differ from source authority for {asset_id}: actual={actual_full}, expected={expected}")

    slots = list(mesh.get_editor_property("static_materials"))
    require(len(slots) >= int(spec["expected_material_slots"]), f"Material-slot count too low for {asset_id}: {len(slots)}")
    materials = []
    for slot in slots:
        material = slot.get_editor_property("material_interface")
        require(material is not None, f"Null material slot on {asset_id}")
        materials.append(material_record(material))
    try:
        unreal.EditorAssetLibrary.save_loaded_asset(mesh, only_if_is_dirty=False)
        unreal.EditorAssetLibrary.save_directory(destination, only_if_is_dirty=False, recursive=True)
    except TypeError:
        unreal.EditorAssetLibrary.save_loaded_asset(mesh)
        unreal.EditorAssetLibrary.save_directory(destination)

    return mesh, {
        "asset_id": asset_id,
        "source_gltf": record(Path(str(spec["gltf"]))),
        "destination": destination,
        "mesh": mesh.get_path_name(),
        "bounds_cm": actual_full,
        "expected_dimensions_cm": expected,
        "maximum_dimension_relative_error": max(errors),
        "source_triangles": int(spec["source_triangles"]),
        "material_slots": len(slots),
        "materials": materials,
        "nanite_enabled": bool(mesh.get_editor_property("nanite_settings").enabled),
        "collision_policy": "NONE",
        "density_policy": spec["density_policy"],
        "imported_assets": imported_rows,
    }


def run_unreal() -> None:
    import unreal

    contract = load_contract()
    fresh = contract["fresh_outputs"]
    result: dict[str, object] = {
        "schema": "skyguard.m01-polyhaven-vegetation-staging01-recovery01.authoring-receipt.v1",
        "classification": "FAILED_WITH_EVIDENCE",
        "runtime_promotion": False,
        "accepted_map_mutated": False,
        "authorities": [],
        "input_map_before": None,
        "input_map_after": None,
        "output_map": None,
        "asset_records": [],
        "placements": [],
        "actor_count_before": None,
        "actor_count_after": None,
        "error": None,
        "traceback": None,
    }
    try:
        result["authorities"] = verify_authorities(contract)
        input_path = Path(str(contract["input_map"]["path"]))
        output_path = Path(str(fresh["map_path"]))
        asset_disk_root = Path(str(fresh["asset_disk_root"]))
        result["input_map_before"] = record(input_path)
        require(not asset_disk_root.exists(), f"Fresh asset namespace exists: {asset_disk_root}")
        require(not unreal.EditorAssetLibrary.does_directory_exist(str(fresh["asset_root"])), "Fresh Unreal asset namespace exists")
        require(not output_path.exists(), f"Fresh output map exists: {output_path}")
        require(not unreal.EditorAssetLibrary.does_asset_exist(str(fresh["map_asset"])), "Fresh Unreal map asset exists")

        meshes: dict[str, object] = {}
        for spec in contract["assets"]:
            mesh, mesh_record = import_candidate(unreal, spec, str(fresh["asset_root"]))
            meshes[str(spec["id"])] = mesh
            result["asset_records"].append(mesh_record)

        levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        actors_api = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        require(levels is not None and actors_api is not None, "Required editor subsystems are unavailable")
        require(levels.new_level_from_template(str(fresh["map_asset"]), str(contract["input_map"]["asset"])), "Failed to duplicate accepted Cell03 map")
        before = list(actors_api.get_all_level_actors())
        result["actor_count_before"] = len(before)
        require(len(before) == int(contract["input_map"]["expected_actor_count"]), f"Accepted Cell03 actor count changed: {len(before)}")
        require(not any(actor.get_actor_label().startswith("M01_PHV01_") for actor in before), "Vegetation staging labels already exist")

        for spec in contract["assets"]:
            asset_id = str(spec["id"])
            placements = PLACEMENTS[asset_id]
            require(len(placements) == int(spec["placement_count"]), f"Placement contract mismatch: {asset_id}")
            mesh = meshes[asset_id]
            for index, (x_cm, y_cm, yaw, scale) in enumerate(placements, start=1):
                actor = actors_api.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x_cm, y_cm, 0.0), unreal.Rotator(0.0, yaw, 0.0), False)
                require(actor is not None, f"Could not spawn {asset_id} placement {index}")
                actor.set_actor_label(f"M01_PHV01_{asset_id}_{index:02d}")
                actor.set_folder_path(f"M01/SourceBacked/VegetationStaging01Recovery01/{asset_id}")
                actor.set_actor_scale3d(unreal.Vector(scale, scale, scale))
                component = actor.get_component_by_class(unreal.StaticMeshComponent)
                require(component is not None, f"StaticMeshComponent missing for {asset_id} placement {index}")
                component.set_static_mesh(mesh)
                component.set_mobility(unreal.ComponentMobility.STATIC)
                component.set_editor_property("cast_shadow", True)
                component.set_collision_profile_name("NoCollision")
                origin_before, extent_before = actor.get_actor_bounds(False)
                bottom_before = float(origin_before.z - extent_before.z)
                target_z = promenade_surface_z_cm(x_cm, y_cm)
                location = actor.get_actor_location()
                actor.set_actor_location(unreal.Vector(location.x, location.y, location.z + target_z - bottom_before), False, True)
                origin_after, extent_after = actor.get_actor_bounds(False)
                bottom_after = float(origin_after.z - extent_after.z)
                require(abs(bottom_after - target_z) <= 1.0, f"Grounding failed for {actor.get_actor_label()}")
                result["placements"].append({
                    "label": actor.get_actor_label(),
                    "asset_id": asset_id,
                    "location_cm": vector(actor.get_actor_location()),
                    "yaw_degrees": yaw,
                    "scale": scale,
                    "surface_target_z_cm": target_z,
                    "bottom_after_cm": bottom_after,
                    "bounds_extent_cm": vector(extent_after),
                })

        after = list(actors_api.get_all_level_actors())
        result["actor_count_after"] = len(after)
        expected_after = int(contract["input_map"]["expected_actor_count"]) + int(contract["policies"]["map_placement_count"])
        require(len(result["placements"]) == int(contract["policies"]["map_placement_count"]), "Final placement count changed")
        require(len(after) == expected_after, f"Final actor count changed: {len(after)}")
        require(levels.save_current_level(), "Failed to save fresh vegetation staging map")
        require(output_path.is_file(), "Saved vegetation staging map is missing")
        result["input_map_after"] = record(input_path)
        require(result["input_map_after"] == result["input_map_before"], "Accepted Cell03 input map was mutated")
        result["output_map"] = record(output_path)
        result["classification"] = "PASSED_AUTOMATIC_AWAITING_D3D12_VISUAL_AND_PERFORMANCE_PROOF"
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        result["traceback"] = traceback.format_exc()
    finally:
        ATTEMPT.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["classification"] != "PASSED_AUTOMATIC_AWAITING_D3D12_VISUAL_AND_PERFORMANCE_PROOF":
        raise RuntimeError(str(result["error"]))


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
