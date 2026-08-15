"""Import the accepted coastal corridor and assemble one fresh Mission 1 map."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import struct
import sys
import traceback
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
ISOLATED = Path(r"D:\SG52T08_ENV01")
SOURCE = ROOT / (
    r"Production\Derived"
    r"\m01-coastal-corridor-correction06-recovery01-unrealready01-normalized01"
    r"\M01_CoastalCorridor_C06R01_UNREAL_READY.glb"
)
SOURCE_BYTES = 48_367_620
SOURCE_SHA256 = "935ba333c18cc6b8da0083cbee069f35728155a1159fe276140a601d3b591e93"
NORMALIZATION_RECEIPT = SOURCE.parent / "metadata_normalization_receipt.json"
NORMALIZATION_RECEIPT_SHA256 = "183e140104694f04b483a517ef9d744d9aec988a1d79c1ce7f1e9f5d7827595c"
PROJECT = ISOLATED / "Skyguard52.uproject"
PROJECT_SHA256 = "7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a"
INPUT_ASSET = "/Game/M01/Lvl_M01_PhotorealFoundation_EnvironmentCompositionCorrection05Recovery02"
OUTPUT_ASSET = "/Game/M01/Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01"
INPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_PhotorealFoundation_EnvironmentCompositionCorrection05Recovery02.umap"
OUTPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01.umap"
INPUT_BYTES = 781_174
INPUT_SHA256 = "d868fc50959eda83e3e4d9dc495e95ea0fd9d83e34ebdd191a6cd43a5b0c04cd"
DESTINATION = "/Game/M01/CoastalCorridorC06R01"
DESTINATION_DISK = ISOLATED / "Content/M01/CoastalCorridorC06R01"
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_COASTAL_CORRIDOR_C06R01_UNREAL_INTEGRATION01/attempt_01"
RECEIPT = ATTEMPT / "integration_receipt.json"
EXPECTED_ACTORS_BEFORE = 140
EXPECTED_REMOVED = 43
EXPECTED_VISIBLE_CREATED = 3
EXPECTED_ACTORS_AFTER = 100

EXPECTED_RENDER_MESHES = {
    "SM_M01_CoastalCorridor_C06R01_CONTACT": 2,
    "SM_M01_CoastalCorridor_C06R01_DETAILS": 6,
    "SM_M01_CoastalCorridor_C06R01_HARDSCAPE": 5,
    "SM_M01_CoastalCorridor_C06R01_TERRAIN": 4,
}
EXPECTED_COLLISION = "UCX_SM_M01_CoastalCorridor_C06R01_TERRAIN_00"
EXPECTED_SOCKET = "SOCKET_M01_CoastalCorridor_C06R01_Origin"
VISIBLE_GROUPS = ("TERRAIN", "HARDSCAPE", "DETAILS")
BUILDING_PATTERN = re.compile(
    r"^(?P<instance>M01_VEK02_City_R\d{2}_C\d{2}_[A-Za-z]+)_(?P<group>DETAILS|GLAZING|STRUCTURAL)$"
)
LIGHTHOUSE_PATTERN = re.compile(r"^M01_VEK02_Lighthouse_Hero_(?P<group>DETAILS|GLAZING|STRUCTURAL)$")
DISTRICT_HARDSCAPE_PATTERN = re.compile(r"^M01_VEK02_District_\d{2}_HARDSCAPE$")
CROSS_STREET_PATTERN = re.compile(r"^M01_RS01_CrossStreet_\d{2}_\d{2}$")


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
        require(magic == b"glTF" and version == 2 and total == path.stat().st_size, "Invalid normalized GLB header")
        json_length, json_type = struct.unpack("<II", stream.read(8))
        require(json_type == 0x4E4F534A, "Normalized GLB JSON chunk is absent")
        return json.loads(stream.read(json_length).decode("utf-8").rstrip("\x00 \t\r\n"))


def validate_source_contract() -> dict[str, object]:
    require(SOURCE.is_file() and SOURCE.stat().st_size == SOURCE_BYTES, "Normalized corridor GLB is missing or changed")
    require(sha256(SOURCE) == SOURCE_SHA256, "Normalized corridor GLB hash changed")
    require(NORMALIZATION_RECEIPT.is_file(), "Normalization receipt is missing")
    require(sha256(NORMALIZATION_RECEIPT) == NORMALIZATION_RECEIPT_SHA256, "Normalization receipt hash changed")
    document = read_glb_document(SOURCE)
    material_names = [str(row.get("name", "")) for row in document.get("materials", [])]
    observed = {}
    collision_names = []
    for mesh in document.get("meshes", []):
        name = str(mesh.get("name", ""))
        primitives = mesh.get("primitives", [])
        if name.startswith("UCX_"):
            collision_names.append(name)
        else:
            observed[name] = len(primitives)
        require(all(row.get("material") is not None for row in primitives), f"Unmaterialed primitive in {name}")
    nodes = [str(row.get("name", "")) for row in document.get("nodes", [])]
    require(observed == EXPECTED_RENDER_MESHES, f"Normalized semantic mesh contract changed: {observed}")
    require(collision_names == [EXPECTED_COLLISION], f"Collision contract changed: {collision_names}")
    require(nodes.count(EXPECTED_SOCKET) == 1, "Origin socket contract changed")
    require(len(material_names) == 14 and len(set(material_names)) == 14, "Material identity contract changed")
    return {
        "source": record(SOURCE),
        "render_meshes": observed,
        "collision": collision_names[0],
        "socket": EXPECTED_SOCKET,
        "materials": material_names,
    }


def corridor_surface_z_cm(x_cm: float, y_cm: float) -> float:
    """Mirror the accepted Blender corridor profile for deterministic grounding."""
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
            alpha = 0.0 if right_y == left_y else (y - left_y) / (right_y - left_y)
            return (left_z + (right_z - left_z) * alpha) * 100.0
    return boundaries[0][1] * 100.0


def run_offline_contract_test() -> int:
    validate_source_contract()
    require(PROJECT.is_file() and sha256(PROJECT) == PROJECT_SHA256, "Isolated project authority changed")
    require(INPUT_FILE.is_file() and INPUT_FILE.stat().st_size == INPUT_BYTES and sha256(INPUT_FILE) == INPUT_SHA256, "Accepted input map authority changed")
    require(not DESTINATION_DISK.exists(), "Fresh Unreal asset namespace already exists")
    require(not OUTPUT_FILE.exists(), "Fresh output map already exists")
    require(not ATTEMPT.exists(), "Fresh attempt namespace already exists")
    compile(Path(__file__).read_text(encoding="utf-8"), __file__, "exec")
    print("PASS_M01_COASTAL_CORRIDOR_C06R01_UNREAL_INTEGRATION01_CONTRACT")
    return 0


def run_unreal() -> None:
    import unreal

    result: dict[str, object] = {
        "schema": "skyguard.m01-coastal-corridor-c06r01.unreal-integration01.v1",
        "classification": "FAILED_WITH_EVIDENCE",
        "source_contract": None,
        "input_asset": INPUT_ASSET,
        "output_asset": OUTPUT_ASSET,
        "destination": DESTINATION,
        "input_sha256_before": None,
        "input_sha256_after": None,
        "output_map": None,
        "task_imported_object_paths": [],
        "imported_assets": [],
        "semantic_static_meshes": {},
        "collision_assets": [],
        "actor_count_before": None,
        "actor_count_after": None,
        "removed_actor_labels": [],
        "created_actors": [],
        "contact_asset_imported_not_spawned": True,
        "building_grounding": [],
        "lighthouse_grounding": None,
        "rollback_manifest": {
            "created_asset_namespace": DESTINATION,
            "created_map": OUTPUT_ASSET,
            "accepted_input_mutated": False,
        },
        "error": None,
        "traceback": None,
    }

    try:
        result["source_contract"] = validate_source_contract()
        require(PROJECT.is_file() and sha256(PROJECT) == PROJECT_SHA256, "Isolated project authority changed")
        require(INPUT_FILE.is_file() and INPUT_FILE.stat().st_size == INPUT_BYTES, "Accepted input map byte count changed")
        result["input_sha256_before"] = sha256(INPUT_FILE)
        require(result["input_sha256_before"] == INPUT_SHA256, "Accepted input map hash changed")
        require(not DESTINATION_DISK.exists(), f"Fresh asset namespace exists: {DESTINATION_DISK}")
        require(not unreal.EditorAssetLibrary.does_directory_exist(DESTINATION), f"Fresh asset namespace exists: {DESTINATION}")
        require(not OUTPUT_FILE.exists() and not unreal.EditorAssetLibrary.does_asset_exist(OUTPUT_ASSET), "Fresh output map namespace exists")

        require(unreal.EditorAssetLibrary.make_directory(DESTINATION), "Failed to create corridor import namespace")
        task = unreal.AssetImportTask()
        task.filename = str(SOURCE)
        task.destination_path = DESTINATION
        task.destination_name = ""
        task.automated = True
        task.replace_existing = False
        task.save = True
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
        result["task_imported_object_paths"] = sorted(str(path) for path in (task.imported_object_paths or []))
        registry = unreal.AssetRegistryHelpers.get_asset_registry()
        registry.scan_paths_synchronous([DESTINATION], True, False)
        imported_paths = sorted(unreal.EditorAssetLibrary.list_assets(DESTINATION, recursive=True, include_folder=False))
        require(imported_paths, "Interchange produced no assets")

        semantic_meshes = {}
        collision_assets = []
        for asset_path in imported_paths:
            asset = unreal.EditorAssetLibrary.load_asset(asset_path)
            require(asset is not None, f"Imported asset failed to load: {asset_path}")
            row = {"path": asset_path, "class": asset.get_class().get_name(), "name": asset.get_name()}
            if isinstance(asset, unreal.StaticMesh):
                name = asset.get_name()
                bounds = asset.get_bounds()
                slots = list(asset.get_editor_property("static_materials"))
                row.update({
                    "bounds_origin_cm": vector(bounds.origin),
                    "bounds_extent_cm": vector(bounds.box_extent),
                    "material_slot_count": len(slots),
                    "lod_count": int(asset.get_num_lods()),
                })
                if name in EXPECTED_RENDER_MESHES:
                    require(name not in semantic_meshes, f"Duplicate semantic StaticMesh: {name}")
                    require(len(slots) == EXPECTED_RENDER_MESHES[name], f"Material slot count changed for {name}: {len(slots)}")
                    semantic_meshes[name] = asset
                elif name.startswith("UCX_"):
                    collision_assets.append(asset_path)
            result["imported_assets"].append(row)
        require(set(semantic_meshes) == set(EXPECTED_RENDER_MESHES), f"Imported semantic meshes changed: {sorted(semantic_meshes)}")
        result["semantic_static_meshes"] = {name: mesh.get_path_name() for name, mesh in sorted(semantic_meshes.items())}
        result["collision_assets"] = collision_assets

        terrain_bounds = semantic_meshes["SM_M01_CoastalCorridor_C06R01_TERRAIN"].get_bounds()
        require(abs(float(terrain_bounds.origin.x) - 25000.0) <= 150.0, f"Terrain X origin scale/axis mismatch: {terrain_bounds.origin.x}")
        require(abs(float(terrain_bounds.box_extent.x) - 29000.0) <= 150.0, f"Terrain X extent scale mismatch: {terrain_bounds.box_extent.x}")
        require(7000.0 <= float(terrain_bounds.box_extent.y) <= 9000.0, f"Terrain Y extent scale mismatch: {terrain_bounds.box_extent.y}")
        require(float(terrain_bounds.box_extent.z) <= 150.0, f"Terrain Z extent scale mismatch: {terrain_bounds.box_extent.z}")
        try:
            unreal.EditorAssetLibrary.save_directory(DESTINATION, only_if_is_dirty=False, recursive=True)
        except TypeError:
            unreal.EditorAssetLibrary.save_directory(DESTINATION)

        levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        actors_api = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        require(levels is not None and actors_api is not None, "Required editor subsystems are unavailable")
        require(levels.new_level_from_template(OUTPUT_ASSET, INPUT_ASSET), "Failed to clone accepted Mission 1 map")
        actors = list(actors_api.get_all_level_actors())
        result["actor_count_before"] = len(actors)
        require(len(actors) == EXPECTED_ACTORS_BEFORE, f"Accepted map actor count changed: {len(actors)}")

        removals = []
        removal_groups = {
            "beach": [actor for actor in actors if actor.get_actor_label().startswith("M01_ECC05_Beach_")],
            "cross_street": [actor for actor in actors if CROSS_STREET_PATTERN.match(actor.get_actor_label())],
            "district_hardscape": [actor for actor in actors if DISTRICT_HARDSCAPE_PATTERN.match(actor.get_actor_label())],
        }
        require(len(removal_groups["beach"]) == 24, "Expected 24 obsolete beach actors")
        require(len(removal_groups["cross_street"]) == 15, "Expected 15 obsolete cross-street actors")
        require(len(removal_groups["district_hardscape"]) == 4, "Expected four obsolete district hardscape actors")
        for group in removal_groups.values():
            removals.extend(group)
        require(len(removals) == EXPECTED_REMOVED, "Obsolete actor aggregate changed")
        require(len({actor.get_path_name() for actor in removals}) == EXPECTED_REMOVED, "Removal set contains duplicates")
        result["removed_actor_labels"] = sorted(actor.get_actor_label() for actor in removals)
        for actor in removals:
            require(actors_api.destroy_actor(actor), f"Failed to remove obsolete actor: {actor.get_actor_label()}")

        created = []
        for group in VISIBLE_GROUPS:
            name = f"SM_M01_CoastalCorridor_C06R01_{group}"
            mesh = semantic_meshes[name]
            actor = actors_api.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0.0, 0.0, 0.0), unreal.Rotator(), False)
            require(actor is not None, f"Failed to spawn corridor actor: {group}")
            actor.set_actor_label(f"M01_C06R01_Corridor_{group}")
            actor.set_folder_path("M01/CoastalCorridorC06R01")
            component = actor.get_component_by_class(unreal.StaticMeshComponent)
            require(component is not None, f"StaticMeshComponent missing: {group}")
            component.set_static_mesh(mesh)
            component.set_mobility(unreal.ComponentMobility.STATIC)
            component.set_editor_property("cast_shadow", True)
            component.set_collision_profile_name("BlockAll")
            origin, extent = actor.get_actor_bounds(False)
            created.append({
                "label": actor.get_actor_label(),
                "mesh": mesh.get_path_name(),
                "location_cm": vector(actor.get_actor_location()),
                "bounds_origin_cm": vector(origin),
                "bounds_extent_cm": vector(extent),
                "material_slot_count": component.get_num_materials(),
                "collision_profile": str(component.get_collision_profile_name()),
            })
        result["created_actors"] = created
        require(len(created) == EXPECTED_VISIBLE_CREATED, "Visible corridor actor count changed")

        current = list(actors_api.get_all_level_actors())
        building_groups: dict[str, dict[str, object]] = {}
        lighthouse_group: dict[str, object] = {}
        for actor in current:
            label = actor.get_actor_label()
            building = BUILDING_PATTERN.match(label)
            if building:
                building_groups.setdefault(building.group("instance"), {})[building.group("group")] = actor
            lighthouse = LIGHTHOUSE_PATTERN.match(label)
            if lighthouse:
                lighthouse_group[lighthouse.group("group")] = actor
        require(len(building_groups) == 27, f"Expected 27 building groups; found {len(building_groups)}")
        for instance in sorted(building_groups):
            members = building_groups[instance]
            require(set(members) == {"DETAILS", "GLAZING", "STRUCTURAL"}, f"Incomplete building group: {instance}")
            structural = members["STRUCTURAL"]
            location = structural.get_actor_location()
            before_origin, before_extent = structural.get_actor_bounds(False)
            before_bottom = float(before_origin.z - before_extent.z)
            target = corridor_surface_z_cm(float(location.x), float(location.y))
            delta = target - before_bottom
            require(abs(delta) <= 200.0, f"Building grounding shift exceeds bound: {instance} -> {delta}")
            for member in members.values():
                member_location = member.get_actor_location()
                member.set_actor_location(unreal.Vector(member_location.x, member_location.y, member_location.z + delta), False, True)
            after_origin, after_extent = structural.get_actor_bounds(False)
            after_bottom = float(after_origin.z - after_extent.z)
            require(abs(after_bottom - target) <= 1.0, f"Building grounding failed: {instance}")
            result["building_grounding"].append({"instance": instance, "target_cm": target, "before_bottom_cm": before_bottom, "after_bottom_cm": after_bottom, "shift_cm": delta})

        require(set(lighthouse_group) == {"DETAILS", "GLAZING", "STRUCTURAL"}, "Lighthouse group is incomplete")
        lighthouse_structural = lighthouse_group["STRUCTURAL"]
        lighthouse_location = lighthouse_structural.get_actor_location()
        lighthouse_origin, lighthouse_extent = lighthouse_structural.get_actor_bounds(False)
        lighthouse_before = float(lighthouse_origin.z - lighthouse_extent.z)
        lighthouse_target = corridor_surface_z_cm(float(lighthouse_location.x), float(lighthouse_location.y))
        lighthouse_delta = lighthouse_target - lighthouse_before
        require(abs(lighthouse_delta) <= 250.0, f"Lighthouse grounding shift exceeds bound: {lighthouse_delta}")
        for member in lighthouse_group.values():
            member_location = member.get_actor_location()
            member.set_actor_location(unreal.Vector(member_location.x, member_location.y, member_location.z + lighthouse_delta), False, True)
        lighthouse_after_origin, lighthouse_after_extent = lighthouse_structural.get_actor_bounds(False)
        lighthouse_after = float(lighthouse_after_origin.z - lighthouse_after_extent.z)
        require(abs(lighthouse_after - lighthouse_target) <= 1.0, "Lighthouse grounding failed")
        result["lighthouse_grounding"] = {"target_cm": lighthouse_target, "before_bottom_cm": lighthouse_before, "after_bottom_cm": lighthouse_after, "shift_cm": lighthouse_delta}

        actors_after = list(actors_api.get_all_level_actors())
        result["actor_count_after"] = len(actors_after)
        require(len(actors_after) == EXPECTED_ACTORS_AFTER, f"Final actor count changed: {len(actors_after)}")
        labels_after = [actor.get_actor_label() for actor in actors_after]
        require(not any(label.startswith("M01_ECC05_Beach_") for label in labels_after), "Obsolete beach actors remain")
        require(not any(CROSS_STREET_PATTERN.match(label) for label in labels_after), "Obsolete cross streets remain")
        require(not any(DISTRICT_HARDSCAPE_PATTERN.match(label) for label in labels_after), "Obsolete district hardscape remains")
        require(len([label for label in labels_after if label.startswith("M01_C06R01_Corridor_")]) == 3, "Corridor actor labels changed")

        require(levels.save_current_level(), "Failed to save fresh corridor map")
        require(OUTPUT_FILE.is_file(), "Fresh corridor map file was not created")
        result["input_sha256_after"] = sha256(INPUT_FILE)
        require(result["input_sha256_after"] == INPUT_SHA256, "Accepted input map changed")
        result["output_map"] = record(OUTPUT_FILE)
        result["classification"] = "PASSED_M01_COASTAL_CORRIDOR_C06R01_UNREAL_INTEGRATION01_READY_FOR_D3D12_VISUAL_PROOF"
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        result["traceback"] = traceback.format_exc()
    finally:
        write_json_atomic(RECEIPT, result)

    if result["classification"].startswith("PASSED_"):
        unreal.SystemLibrary.quit_editor()
    else:
        raise RuntimeError(result["error"] or "Corridor integration failed")


if "--offline-contract-test" in sys.argv:
    raise SystemExit(run_offline_contract_test())

run_unreal()
