"""Derive and remediate the quarantined M01 accepted-module assembly v2."""

from __future__ import annotations

import hashlib
import json
import os
import traceback
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
SOURCE_MAP = "/Game/Skyguard/Maps/Assembly/Lvl_M01_AcceptedModuleAssembly_v1"
SOURCE_DISK = ROOT / r"Content\Skyguard\Maps\Assembly\Lvl_M01_AcceptedModuleAssembly_v1.umap"
SOURCE_BYTES = 48_799
SOURCE_SHA256 = "0ca7a3d0ef71f7979d8ecf556bd4b870c9269b88a3c220df76e98848964eda7e"
TARGET_MAP = "/Game/Skyguard/Maps/Assembly/Lvl_M01_AcceptedModuleAssembly_v2"
TARGET_DISK = ROOT / r"Content\Skyguard\Maps\Assembly\Lvl_M01_AcceptedModuleAssembly_v2.umap"
PLAYABLE_DISK = ROOT / r"Content\Skyguard\Maps\Lvl_M01_CoastalIntercept_Playable_v1.umap"
PLAYABLE_BYTES = 70_545
PLAYABLE_SHA256 = "9d2ca2e50b446f488926bdd8a29eca9fe33d62ec25656fc77ca55997f5a08afa"
ATTEMPT = (
    ROOT
    / r"Saved\BuildAttempts\M01_ACCEPTED_MODULE_ASSEMBLY_V2_REMEDIATION01"
    / "attempt_01"
)
RECEIPT = ATTEMPT / "author_receipt.json"
ACTOR_FOLDER = "M01/AcceptedModules/V2_Remediation01"
ROW_CENTER_X = 2500.0
ROW_Y = -3850.0
ROW_Z = 480.0
ALLOW_EXISTING_TARGET = False

CORRIDOR_MESHES = {
    "TERRAIN": (
        "/Game/Skyguard/Candidates/M01/CoastalCorridorC06R01/StaticMeshes/"
        "SM_M01_CoastalCorridor_C06R01_TERRAIN"
    ),
    "HARDSCAPE": (
        "/Game/Skyguard/Candidates/M01/CoastalCorridorC06R01/StaticMeshes/"
        "SM_M01_CoastalCorridor_C06R01_HARDSCAPE"
    ),
    "DETAILS": (
        "/Game/Skyguard/Candidates/M01/CoastalCorridorC06R01/StaticMeshes/"
        "SM_M01_CoastalCorridor_C06R01_DETAILS"
    ),
    "CONTACT": (
        "/Game/Skyguard/Candidates/M01/CoastalCorridorC06R01/StaticMeshes/"
        "SM_M01_CoastalCorridor_C06R01_CONTACT"
    ),
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
    return {
        "path": str(path),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def write_json_atomic(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def verify_file(
    path: Path,
    expected_bytes: int,
    expected_sha256: str,
    label: str,
) -> dict[str, object]:
    require(path.is_file(), f"{label} missing: {path}")
    observed = record(path)
    require(observed["bytes"] == expected_bytes, f"{label} byte count changed")
    require(observed["sha256"] == expected_sha256, f"{label} SHA-256 changed")
    return observed


def vector_row(value: unreal.Vector) -> list[float]:
    return [float(value.x), float(value.y), float(value.z)]


def rotator_row(value: unreal.Rotator) -> list[float]:
    return [float(value.pitch), float(value.yaw), float(value.roll)]


def actor_bounds(actor: object) -> dict[str, object]:
    origin, extent = actor.get_actor_bounds(False)
    return {
        "origin_cm": vector_row(origin),
        "extent_cm": vector_row(extent),
        "minimum_cm": [
            float(origin.x - extent.x),
            float(origin.y - extent.y),
            float(origin.z - extent.z),
        ],
        "maximum_cm": [
            float(origin.x + extent.x),
            float(origin.y + extent.y),
            float(origin.z + extent.z),
        ],
    }


def actors_by_label() -> dict[str, object]:
    return {
        actor.get_actor_label(): actor
        for actor in unreal.EditorLevelLibrary.get_all_level_actors()
    }


def set_mobility(component: object) -> None:
    try:
        component.set_mobility(unreal.ComponentMobility.MOVABLE)
    except Exception:
        pass


def ensure_actor(
    labels: dict[str, object],
    actor_class: object,
    label: str,
    location: unreal.Vector,
    rotation: unreal.Rotator,
) -> object:
    actor = labels.get(label)
    if actor is None:
        actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
            actor_class,
            location,
            rotation,
        )
        require(actor is not None, f"Could not spawn {label}")
        actor.set_actor_label(label)
        labels[label] = actor
    require(isinstance(actor, actor_class), f"Actor class mismatch for {label}")
    actor.set_actor_location(location, False, False)
    actor.set_actor_rotation(rotation, False)
    actor.set_folder_path(ACTOR_FOLDER)
    return actor


def configure_static_mesh_actor(
    actor: object,
    mesh: object,
    material: object | None = None,
) -> object:
    component = actor.get_component_by_class(unreal.StaticMeshComponent)
    require(component is not None, f"StaticMeshComponent missing on {actor}")
    component.set_static_mesh(mesh)
    if material is not None:
        component.set_material(0, material)
    return component


def load_static_mesh(path: str) -> object:
    mesh = unreal.EditorAssetLibrary.load_asset(path)
    require(isinstance(mesh, unreal.StaticMesh), f"StaticMesh missing: {path}")
    return mesh


def configure_post_process(post: object) -> list[str]:
    applied: list[str] = []
    settings = post.get_editor_property("settings")
    candidates = (
        ("override_auto_exposure_method", True),
        ("auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL),
        ("override_auto_exposure_bias", True),
        ("auto_exposure_bias", 2.5),
    )
    for name, value in candidates:
        try:
            settings.set_editor_property(name, value)
            applied.append(name)
        except Exception:
            continue
    post.set_editor_property("settings", settings)
    require("auto_exposure_bias" in applied, "Could not apply fixed exposure bias")
    return applied


def main() -> None:
    result: dict[str, object] = {
        "schema": "skyguard.m01-assembly.v2-remediation01.author.v1",
        "classification": "FAILED_WITH_EVIDENCE",
        "source_map": SOURCE_MAP,
        "target_map": TARGET_MAP,
        "runtime_promotion": False,
        "candidate_promotion": False,
        "blender_used": False,
        "source_before": None,
        "source_after": None,
        "playable_before": None,
        "playable_after": None,
        "target_record": None,
        "actors": [],
        "corridor_bounds": {},
        "post_process_properties": [],
        "error": None,
        "traceback": None,
    }
    try:
        ATTEMPT.mkdir(parents=True, exist_ok=False)
        result["source_before"] = verify_file(
            SOURCE_DISK,
            SOURCE_BYTES,
            SOURCE_SHA256,
            "Assembly v1",
        )
        result["playable_before"] = verify_file(
            PLAYABLE_DISK,
            PLAYABLE_BYTES,
            PLAYABLE_SHA256,
            "Playable M01",
        )
        target_exists = (
            TARGET_DISK.exists()
            or unreal.EditorAssetLibrary.does_asset_exist(TARGET_MAP)
        )
        if target_exists:
            require(
                ALLOW_EXISTING_TARGET,
                f"Fresh target already exists: {TARGET_MAP}",
            )
        else:
            duplicated = unreal.EditorAssetLibrary.duplicate_asset(
                SOURCE_MAP,
                TARGET_MAP,
            )
            require(duplicated, f"Could not duplicate {SOURCE_MAP} to {TARGET_MAP}")
        loaded = unreal.EditorLoadingAndSavingUtils.load_map(TARGET_MAP)
        require(loaded is not None, f"Could not load {TARGET_MAP}")
        world = unreal.get_editor_subsystem(
            unreal.UnrealEditorSubsystem
        ).get_editor_world()
        require(world is not None, "Editor world unavailable")
        require(world.get_outermost().get_name() == TARGET_MAP, "Wrong editor world")
        labels = actors_by_label()
        actor_rows: list[dict[str, object]] = []

        existing_terrain = labels.pop(
            "M01_AcceptedCorridor_TERRAIN_Grounding",
            None,
        )
        if existing_terrain is not None:
            existing_terrain.set_actor_label("M01_V2_Corridor_TERRAIN")
            labels["M01_V2_Corridor_TERRAIN"] = existing_terrain

        corridor_actors: dict[str, object] = {}
        for semantic, asset_path in CORRIDOR_MESHES.items():
            mesh = load_static_mesh(asset_path)
            label = f"M01_V2_Corridor_{semantic}"
            actor = ensure_actor(
                labels,
                unreal.StaticMeshActor,
                label,
                unreal.Vector(0.0, 0.0, 0.0),
                unreal.Rotator(0.0, 0.0, 0.0),
            )
            configure_static_mesh_actor(actor, mesh)
            corridor_actors[semantic] = actor
            actor_rows.append(
                {
                    "label": label,
                    "mesh": mesh.get_path_name(),
                    "location_cm": vector_row(actor.get_actor_location()),
                    "bounds": actor_bounds(actor),
                }
            )

        terrain_bounds = actor_bounds(corridor_actors["TERRAIN"])
        contact_bounds = actor_bounds(corridor_actors["CONTACT"])
        result["corridor_bounds"] = {
            "terrain": terrain_bounds,
            "contact": contact_bounds,
        }
        shoreline_y = max(
            float(terrain_bounds["maximum_cm"][1]),
            float(contact_bounds["maximum_cm"][1]),
        )
        terrain_center_x = float(terrain_bounds["origin_cm"][0])
        terrain_extent_x = float(terrain_bounds["extent_cm"][0])

        for actor in unreal.EditorLevelLibrary.get_all_level_actors():
            label = actor.get_actor_label()
            if not label.startswith("M01_AcceptedWindowBay_"):
                continue
            before = actor.get_actor_location()
            actor.set_actor_location(
                unreal.Vector(
                    ROW_CENTER_X + before.x,
                    ROW_Y,
                    ROW_Z,
                ),
                False,
                False,
            )
            actor.set_actor_rotation(unreal.Rotator(0.0, 0.0, 0.0), False)
            actor.set_folder_path(ACTOR_FOLDER)
            actor.set_actor_label(label.replace("M01_Accepted", "M01_V2"))
            actor_rows.append(
                {
                    "label": actor.get_actor_label(),
                    "location_cm": vector_row(actor.get_actor_location()),
                    "rotation": rotator_row(actor.get_actor_rotation()),
                    "bounds": actor_bounds(actor),
                }
            )

        cube = load_static_mesh("/Engine/BasicShapes/Cube.Cube")
        basic_material = unreal.EditorAssetLibrary.load_asset(
            "/Engine/BasicShapes/BasicShapeMaterial"
        )
        facade_backing = ensure_actor(
            labels,
            unreal.StaticMeshActor,
            "M01_V2_FacadeReviewBacking",
            unreal.Vector(ROW_CENTER_X, ROW_Y - 145.0, 280.0),
            unreal.Rotator(),
        )
        configure_static_mesh_actor(facade_backing, cube, basic_material)
        facade_backing.set_actor_scale3d(unreal.Vector(18.0, 0.25, 6.0))
        actor_rows.append(
            {
                "label": facade_backing.get_actor_label(),
                "location_cm": vector_row(facade_backing.get_actor_location()),
                "scale": vector_row(facade_backing.get_actor_scale3d()),
                "bounds": actor_bounds(facade_backing),
            }
        )
        facade_plinth = ensure_actor(
            labels,
            unreal.StaticMeshActor,
            "M01_V2_FacadeReviewPlinth",
            unreal.Vector(ROW_CENTER_X, ROW_Y, 35.0),
            unreal.Rotator(),
        )
        configure_static_mesh_actor(facade_plinth, cube, basic_material)
        facade_plinth.set_actor_scale3d(unreal.Vector(18.0, 3.0, 0.7))
        actor_rows.append(
            {
                "label": facade_plinth.get_actor_label(),
                "location_cm": vector_row(facade_plinth.get_actor_location()),
                "scale": vector_row(facade_plinth.get_actor_scale3d()),
                "bounds": actor_bounds(facade_plinth),
            }
        )

        old_water = labels.pop("M01_Polish01_CoastalWaterPlane", None)
        if old_water is not None:
            old_water.set_actor_label("M01_V2_CoastalWater")
            labels["M01_V2_CoastalWater"] = old_water
        water = ensure_actor(
            labels,
            unreal.StaticMeshActor,
            "M01_V2_CoastalWater",
            unreal.Vector(),
            unreal.Rotator(),
        )
        water_component = water.get_component_by_class(unreal.StaticMeshComponent)
        require(water_component is not None, "Water StaticMeshComponent missing")
        water_mesh = load_static_mesh("/Engine/BasicShapes/Plane.Plane")
        water_component.set_static_mesh(water_mesh)
        water_half_y = 8000.0
        water_scale_x = (terrain_extent_x + 2000.0) / 50.0
        water_scale_y = water_half_y / 50.0
        water.set_actor_location(
            unreal.Vector(
                terrain_center_x,
                shoreline_y + water_half_y - 25.0,
                -25.0,
            ),
            False,
            False,
        )
        water.set_actor_scale3d(
            unreal.Vector(water_scale_x, water_scale_y, 1.0)
        )
        actor_rows.append(
            {
                "label": water.get_actor_label(),
                "location_cm": vector_row(water.get_actor_location()),
                "scale": vector_row(water.get_actor_scale3d()),
                "shoreline_y_cm": shoreline_y,
                "edge_overlap_cm": 25.0,
                "bounds": actor_bounds(water),
            }
        )

        sun = labels.get("M01_Polish01_DirectionalLight_Sun")
        require(sun is not None, "Inherited sun missing")
        sun.set_actor_rotation(unreal.Rotator(-35.0, 120.0, 0.0), False)
        sun.set_actor_label("M01_V2_DirectionalLight_Sun")
        sun.set_folder_path(ACTOR_FOLDER)
        sun_component = sun.get_component_by_class(unreal.DirectionalLightComponent)
        require(sun_component is not None, "Sun component missing")
        sun_component.set_intensity(50.0)
        set_mobility(sun_component)

        skylight = labels.get("M01_Polish01_SkyLight")
        require(skylight is not None, "Inherited skylight missing")
        skylight.set_actor_label("M01_V2_SkyLight")
        skylight.set_folder_path(ACTOR_FOLDER)
        skylight_component = skylight.get_component_by_class(
            unreal.SkyLightComponent
        )
        require(skylight_component is not None, "SkyLight component missing")
        skylight_component.set_intensity(3.0)
        set_mobility(skylight_component)
        try:
            skylight_component.recapture_sky()
        except Exception:
            pass

        fill = ensure_actor(
            labels,
            unreal.DirectionalLight,
            "M01_V2_DirectionalLight_Fill",
            unreal.Vector(ROW_CENTER_X, ROW_Y + 1000.0, 1500.0),
            unreal.Rotator(-25.0, -60.0, 0.0),
        )
        fill_component = fill.get_component_by_class(
            unreal.DirectionalLightComponent
        )
        require(fill_component is not None, "Fill component missing")
        fill_component.set_intensity(8.0)
        set_mobility(fill_component)

        facade_key = ensure_actor(
            labels,
            unreal.PointLight,
            "M01_V2_FacadeKeyLight",
            unreal.Vector(ROW_CENTER_X, ROW_Y + 1100.0, 650.0),
            unreal.Rotator(),
        )
        point_component = facade_key.get_component_by_class(
            unreal.PointLightComponent
        )
        require(point_component is not None, "Facade PointLight component missing")
        point_component.set_intensity(8000.0)
        point_component.set_editor_property("attenuation_radius", 4500.0)
        set_mobility(point_component)

        fog = labels.get("M01_Polish01_ExponentialHeightFog")
        require(fog is not None, "Inherited height fog missing")
        fog.set_actor_label("M01_V2_ExponentialHeightFog")
        fog.set_folder_path(ACTOR_FOLDER)
        fog_component = fog.get_component_by_class(
            unreal.ExponentialHeightFogComponent
        )
        require(fog_component is not None, "Fog component missing")
        fog_component.set_editor_property("fog_density", 0.002)

        post = labels.get("M01_Polish01_PostProcess_Unbound")
        require(post is not None, "Inherited post-process volume missing")
        post.set_actor_label("M01_V2_PostProcess_Unbound")
        post.set_folder_path(ACTOR_FOLDER)
        try:
            post.set_editor_property("unbound", True)
        except Exception:
            post.set_editor_property("infinite_extent_unbound", True)
        result["post_process_properties"] = configure_post_process(post)

        require(
            unreal.EditorLevelLibrary.save_current_level(),
            f"Could not save {TARGET_MAP}",
        )
        result["actors"] = actor_rows
        result["target_record"] = record(TARGET_DISK)
        result["source_after"] = verify_file(
            SOURCE_DISK,
            SOURCE_BYTES,
            SOURCE_SHA256,
            "Assembly v1",
        )
        result["playable_after"] = verify_file(
            PLAYABLE_DISK,
            PLAYABLE_BYTES,
            PLAYABLE_SHA256,
            "Playable M01",
        )
        require(
            result["source_before"] == result["source_after"],
            "Assembly v1 changed",
        )
        require(
            result["playable_before"] == result["playable_after"],
            "Playable M01 changed",
        )
        result["classification"] = (
            "PASSED_M01_ASSEMBLY_V2_REMEDIATION01_AWAITING_D3D12_REVIEW"
        )
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        result["traceback"] = traceback.format_exc()
        if SOURCE_DISK.is_file():
            result["source_after"] = record(SOURCE_DISK)
        if PLAYABLE_DISK.is_file():
            result["playable_after"] = record(PLAYABLE_DISK)
        if TARGET_DISK.is_file():
            result["target_record"] = record(TARGET_DISK)
    finally:
        write_json_atomic(RECEIPT, result)
    if str(result["classification"]).startswith("PASSED_"):
        return
    raise RuntimeError(result["error"] or result["classification"])


if __name__ == "__main__":
    main()
