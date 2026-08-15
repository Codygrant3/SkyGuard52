"""Polish only the accepted-module M01 assembly map.

This Unreal Editor Python author is intentionally scoped to the derived assembly
map. It never loads or saves the playable M01 package as an editor world and
guards the playable file by its frozen byte count and SHA-256 before and after.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import traceback
from pathlib import Path

try:
    import unreal
except ModuleNotFoundError:
    unreal = None


ROOT = Path(r"D:\Skyguard52")
TARGET_MAP = "/Game/Skyguard/Maps/Assembly/Lvl_M01_AcceptedModuleAssembly_v1"
TARGET_DISK = ROOT / r"Content\Skyguard\Maps\Assembly\Lvl_M01_AcceptedModuleAssembly_v1.umap"
PLAYABLE_MAP = "/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_Playable_v1"
PLAYABLE_DISK = ROOT / r"Content\Skyguard\Maps\Lvl_M01_CoastalIntercept_Playable_v1.umap"
PLAYABLE_BYTES = 70_545
PLAYABLE_SHA256 = "9d2ca2e50b446f488926bdd8a29eca9fe33d62ec25656fc77ca55997f5a08afa"
ATTEMPT = ROOT / r"Saved\BuildAttempts\M01_ACCEPTED_MODULE_ASSEMBLY_v1_POLISH01_RECOVERY01\attempt_01"
RECEIPT = ATTEMPT / "polish_receipt.json"
WATER_MATERIAL = "/Game/Skyguard/Maps/Assembly/Materials/MI_M01_AssemblyWater_Polish01"
WATER_MESH = "/Engine/BasicShapes/Plane.Plane"
ACTOR_FOLDER = "M01/AcceptedModules/Polish01"


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
    temporary = path.with_name(path.name + f".tmp.{os.getpid()}")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def validate_playable() -> dict[str, object]:
    require(PLAYABLE_DISK.is_file(), f"Playable map missing: {PLAYABLE_DISK}")
    observed = record(PLAYABLE_DISK)
    require(observed["bytes"] == PLAYABLE_BYTES, "Playable map byte count changed")
    require(observed["sha256"] == PLAYABLE_SHA256, "Playable map SHA-256 changed")
    return observed


def run_offline_contract_test() -> int:
    require(ROOT == Path(r"D:\Skyguard52"), "Canonical root drifted")
    require(TARGET_MAP.startswith("/Game/Skyguard/Maps/Assembly/"), "Target is outside Assembly")
    require(TARGET_MAP != PLAYABLE_MAP, "Assembly and playable map targets overlap")
    require(TARGET_DISK.is_file(), f"Accepted-module assembly map missing: {TARGET_DISK}")
    validate_playable()
    compile(Path(__file__).read_text(encoding="utf-8"), __file__, "exec")
    print("PASS_M01_ACCEPTED_MODULE_ASSEMBLY_V1_POLISH01_OFFLINE_CONTRACT")
    return 0


def class_name(value: object) -> str:
    return value.get_class().get_name() if value is not None else ""


def set_first_property(target: object, names: tuple[str, ...], value: object) -> str:
    errors: list[str] = []
    for name in names:
        try:
            target.set_editor_property(name, value)
            return name
        except Exception as exc:
            errors.append(f"{name}={type(exc).__name__}")
    raise RuntimeError(f"Could not set any of {names} on {class_name(target)}: {errors}")


def current_world_package() -> str:
    subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    world = subsystem.get_editor_world()
    require(world is not None, "Editor world unavailable after map load")
    return world.get_outermost().get_name()


def find_by_label(label: str) -> object | None:
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        if actor.get_actor_label() == label:
            return actor
    return None


def ensure_actor(actor_class: object, label: str, location: object, rotation: object) -> tuple[object, str]:
    existing = find_by_label(label)
    if existing is not None:
        require(isinstance(existing, actor_class), f"Actor label collision for {label}: {class_name(existing)}")
        actor = existing
        action = "reused"
    else:
        actor = unreal.EditorLevelLibrary.spawn_actor_from_class(actor_class, location, rotation)
        require(actor is not None, f"Failed to spawn {label}")
        actor.set_actor_label(label)
        action = "created"
    actor.set_folder_path(ACTOR_FOLDER)
    return actor, action


def load_material(path: str) -> object | None:
    asset = unreal.EditorAssetLibrary.load_asset(path)
    if asset is None:
        return None
    return asset if isinstance(asset, unreal.MaterialInterface) else None


def ensure_water_material() -> tuple[object, dict[str, object]]:
    parent_candidates = (
        "/Game/Skyguard/Materials/M_Ocean",
        "/Game/Skyguard/Materials/M_OceanDeep",
        "/Game/Skyguard/Materials/Generated/M_L61_Waterline",
        "/Engine/BasicShapes/BasicShapeMaterial",
    )
    parent = None
    parent_path = None
    for candidate in parent_candidates:
        parent = load_material(candidate)
        if parent is not None:
            parent_path = candidate
            break
    require(parent is not None, "No project or engine water-material parent could be loaded")

    material = unreal.EditorAssetLibrary.load_asset(WATER_MATERIAL)
    action = "reused"
    if material is None:
        package, name = WATER_MATERIAL.rsplit("/", 1)
        unreal.EditorAssetLibrary.make_directory(package)
        factory = unreal.MaterialInstanceConstantFactoryNew()
        material = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            name, package, unreal.MaterialInstanceConstant, factory
        )
        require(material is not None, f"Failed to create {WATER_MATERIAL}")
        action = "created"
    require(
        isinstance(material, unreal.MaterialInstanceConstant),
        f"Wrong class at {WATER_MATERIAL}: {class_name(material)}",
    )
    material.set_editor_property("parent", parent)

    applied: list[str] = []
    color = unreal.LinearColor(0.015, 0.12, 0.22, 0.62)
    for parameter in ("WaterColor", "BaseColor", "Color", "Tint"):
        try:
            result = unreal.MaterialEditingLibrary.set_material_instance_vector_parameter_value(
                material, parameter, color
            )
            if result is not False:
                applied.append(parameter)
        except Exception:
            continue
    for parameter, value in (("Roughness", 0.18), ("Metallic", 0.0), ("Opacity", 0.62)):
        try:
            result = unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(
                material, parameter, value
            )
            if result is not False:
                applied.append(parameter)
        except Exception:
            continue
    try:
        unreal.EditorAssetLibrary.save_loaded_asset(material, only_if_is_dirty=False)
    except TypeError:
        unreal.EditorAssetLibrary.save_loaded_asset(material)
    return material, {
        "asset": WATER_MATERIAL,
        "action": action,
        "parent": parent_path,
        "parameter_overrides_supported": bool(applied),
        "parameter_overrides": applied,
        "fallback_note": None if applied else "Parent exposes no supported named overrides; inherited material retained.",
    }


def run_unreal() -> None:
    require(unreal is not None, "This mode must run inside Unreal Editor Python")
    result: dict[str, object] = {
        "schema": "skyguard.m01-accepted-module-assembly.polish01.v1",
        "classification": "FAILED_WITH_EVIDENCE",
        "target_map": TARGET_MAP,
        "playable_map": PLAYABLE_MAP,
        "playable_before": None,
        "playable_after": None,
        "actors": [],
        "water_material": None,
        "source_playable_mutated": None,
        "error": None,
        "traceback": None,
    }
    try:
        ATTEMPT.mkdir(parents=True, exist_ok=True)
        result["playable_before"] = validate_playable()
        require(TARGET_DISK.is_file(), f"Target map missing: {TARGET_DISK}")
        loaded = unreal.EditorLoadingAndSavingUtils.load_map(TARGET_MAP)
        require(loaded is not None, f"Failed to load {TARGET_MAP}")
        require(current_world_package() == TARGET_MAP, f"Wrong editor world loaded: {current_world_package()}")

        actor_rows: list[dict[str, object]] = []
        sun, action = ensure_actor(
            unreal.DirectionalLight,
            "M01_Polish01_DirectionalLight_Sun",
            unreal.Vector(0.0, 0.0, 1800.0),
            unreal.Rotator(-38.0, -24.0, 0.0),
        )
        sun_component = sun.get_component_by_class(unreal.DirectionalLightComponent)
        require(sun_component is not None, "DirectionalLightComponent unavailable")
        set_first_property(sun_component, ("intensity",), 8.0)
        actor_rows.append({"label": sun.get_actor_label(), "class": class_name(sun), "action": action})

        skylight, action = ensure_actor(
            unreal.SkyLight,
            "M01_Polish01_SkyLight",
            unreal.Vector(0.0, 0.0, 900.0),
            unreal.Rotator(0.0, 0.0, 0.0),
        )
        skylight_component = skylight.get_component_by_class(unreal.SkyLightComponent)
        require(skylight_component is not None, "SkyLightComponent unavailable")
        set_first_property(skylight_component, ("intensity",), 1.0)
        actor_rows.append({"label": skylight.get_actor_label(), "class": class_name(skylight), "action": action})

        atmosphere, action = ensure_actor(
            unreal.SkyAtmosphere,
            "M01_Polish01_SkyAtmosphere",
            unreal.Vector(0.0, 0.0, 0.0),
            unreal.Rotator(0.0, 0.0, 0.0),
        )
        actor_rows.append({"label": atmosphere.get_actor_label(), "class": class_name(atmosphere), "action": action})

        fog, action = ensure_actor(
            unreal.ExponentialHeightFog,
            "M01_Polish01_ExponentialHeightFog",
            unreal.Vector(0.0, 0.0, 0.0),
            unreal.Rotator(0.0, 0.0, 0.0),
        )
        fog_component = fog.get_component_by_class(unreal.ExponentialHeightFogComponent)
        if fog_component is not None:
            set_first_property(fog_component, ("fog_density",), 0.018)
        actor_rows.append({"label": fog.get_actor_label(), "class": class_name(fog), "action": action})

        post, action = ensure_actor(
            unreal.PostProcessVolume,
            "M01_Polish01_PostProcess_Unbound",
            unreal.Vector(0.0, 0.0, 0.0),
            unreal.Rotator(0.0, 0.0, 0.0),
        )
        unbound_property = set_first_property(post, ("unbound", "infinite_extent_unbound"), True)
        actor_rows.append(
            {"label": post.get_actor_label(), "class": class_name(post), "action": action, "unbound_property": unbound_property}
        )

        water_mesh = unreal.EditorAssetLibrary.load_asset(WATER_MESH)
        require(isinstance(water_mesh, unreal.StaticMesh), f"Engine water plane unavailable: {WATER_MESH}")
        water_material, material_row = ensure_water_material()
        water, action = ensure_actor(
            unreal.StaticMeshActor,
            "M01_Polish01_CoastalWaterPlane",
            unreal.Vector(0.0, 2400.0, -20.0),
            unreal.Rotator(0.0, 0.0, 0.0),
        )
        water.set_actor_location(unreal.Vector(0.0, 2400.0, -20.0), False, False)
        water.set_actor_scale3d(unreal.Vector(100.0, 100.0, 1.0))
        water_component = water.get_component_by_class(unreal.StaticMeshComponent)
        require(water_component is not None, "Water StaticMeshComponent unavailable")
        water_component.set_static_mesh(water_mesh)
        water_component.set_material(0, water_material)
        actor_rows.append(
            {
                "label": water.get_actor_label(),
                "class": class_name(water),
                "action": action,
                "mesh": WATER_MESH,
                "location_cm": [0.0, 2400.0, -20.0],
                "scale": [100.0, 100.0, 1.0],
                "material": WATER_MATERIAL,
            }
        )

        require(current_world_package() == TARGET_MAP, "Editor world changed before save")
        require(unreal.EditorLevelLibrary.save_current_level(), f"Failed to save {TARGET_MAP}")
        result["actors"] = actor_rows
        result["water_material"] = material_row
        result["target_map_record"] = record(TARGET_DISK)
        result["playable_after"] = validate_playable()
        require(
            result["playable_before"] == result["playable_after"],
            "Playable map changed during assembly polish",
        )
        result["source_playable_mutated"] = False
        result["classification"] = "PASSED_M01_ACCEPTED_MODULE_ASSEMBLY_V1_POLISH01_AWAITING_REVIEW"
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        result["traceback"] = traceback.format_exc()
        try:
            result["playable_after"] = record(PLAYABLE_DISK) if PLAYABLE_DISK.is_file() else None
            result["source_playable_mutated"] = result["playable_after"] != result["playable_before"]
        except Exception:
            pass
    finally:
        write_json_atomic(RECEIPT, result)

    if str(result["classification"]).startswith("PASSED_"):
        unreal.SystemLibrary.quit_editor()
        return
    raise RuntimeError(result["error"] or result["classification"])


if "--offline-contract-test" in sys.argv:
    raise SystemExit(run_offline_contract_test())

run_unreal()
