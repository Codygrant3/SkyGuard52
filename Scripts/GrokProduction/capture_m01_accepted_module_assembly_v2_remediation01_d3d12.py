"""Capture fixed real-D3D12 review views of the remediated M01 assembly v2."""

from __future__ import annotations

import hashlib
import json
import os
import struct
import traceback
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
SOURCE_DISK = ROOT / r"Content\Skyguard\Maps\Assembly\Lvl_M01_AcceptedModuleAssembly_v1.umap"
SOURCE_BYTES = 48_799
SOURCE_SHA256 = "0ca7a3d0ef71f7979d8ecf556bd4b870c9269b88a3c220df76e98848964eda7e"
TARGET_MAP = "/Game/Skyguard/Maps/Assembly/Lvl_M01_AcceptedModuleAssembly_v2"
TARGET_DISK = ROOT / r"Content\Skyguard\Maps\Assembly\Lvl_M01_AcceptedModuleAssembly_v2.umap"
TARGET_BYTES = 61_287
TARGET_SHA256 = "2d005f2e045fec030eb954ec80d0eb494ae509efdb439d1e8b7d60ceded74346"
PLAYABLE_DISK = ROOT / r"Content\Skyguard\Maps\Lvl_M01_CoastalIntercept_Playable_v1.umap"
PLAYABLE_BYTES = 70_545
PLAYABLE_SHA256 = "9d2ca2e50b446f488926bdd8a29eca9fe33d62ec25656fc77ca55997f5a08afa"
ATTEMPT = (
    ROOT
    / r"Saved\BuildAttempts\M01_ACCEPTED_MODULE_ASSEMBLY_V2_REMEDIATION01_D3D12"
    / "attempt_01"
)
PROOF = ATTEMPT / "proof"
RECEIPT = ATTEMPT / "capture_receipt.json"
WIDTH = 1920
HEIGHT = 1080

CAMERAS = (
    {
        "id": "facade_front_fixed",
        "location": (2500.0, -2250.0, 620.0),
        "target": (2500.0, -3850.0, 620.0),
        "fov": 48.0,
    },
    {
        "id": "facade_oblique_fixed",
        "location": (-200.0, -1850.0, 1050.0),
        "target": (2500.0, -3850.0, 560.0),
        "fov": 52.0,
    },
    {
        "id": "shoreline_contact_fixed",
        "location": (7500.0, -1100.0, 1300.0),
        "target": (7500.0, -3900.0, -15.0),
        "fov": 56.0,
    },
    {
        "id": "corridor_semantic_fixed",
        "location": (18000.0, -26000.0, 11000.0),
        "target": (22000.0, -9000.0, 0.0),
        "fov": 62.0,
    },
    {
        "id": "coastal_aerial_fixed",
        "location": (4000.0, -17000.0, 7500.0),
        "target": (11000.0, -3500.0, 0.0),
        "fov": 60.0,
    },
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
    return {
        "path": str(path),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def verify_record(
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


def write_json_atomic(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as stream:
        signature = stream.read(24)
    require(
        signature[:8] == b"\x89PNG\r\n\x1a\n" and signature[12:16] == b"IHDR",
        f"Not a valid PNG: {path}",
    )
    return struct.unpack(">II", signature[16:24])


def vector_row(value: unreal.Vector) -> list[float]:
    return [float(value.x), float(value.y), float(value.z)]


def look_at(
    location: tuple[float, float, float],
    target: tuple[float, float, float],
) -> unreal.Rotator:
    return unreal.Vector(
        target[0] - location[0],
        target[1] - location[1],
        target[2] - location[2],
    ).rotator()


def bounds_row(actor: object) -> dict[str, object]:
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


def actor_audit() -> dict[str, object]:
    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    by_label = {actor.get_actor_label(): actor for actor in actors}
    required_labels = (
        "M01_V2_Corridor_TERRAIN",
        "M01_V2_Corridor_HARDSCAPE",
        "M01_V2_Corridor_DETAILS",
        "M01_V2_Corridor_CONTACT",
        "M01_V2_CoastalWater",
        "M01_V2_DirectionalLight_Sun",
        "M01_V2_DirectionalLight_Fill",
        "M01_V2_SkyLight",
        "M01_V2_PostProcess_Unbound",
        "M01_V2_FacadeReviewBacking",
        "M01_V2_FacadeReviewPlinth",
        "M01_V2_FacadeKeyLight",
    )
    missing = [label for label in required_labels if label not in by_label]
    require(not missing, f"Required v2 actors missing: {missing}")
    window_labels = sorted(
        label for label in by_label if label.startswith("M01_V2WindowBay_")
    )
    require(len(window_labels) == 12, "Expected exactly twelve window actors")
    audited_labels = list(required_labels[:6]) + window_labels
    rows: list[dict[str, object]] = []
    for label in audited_labels:
        actor = by_label[label]
        row: dict[str, object] = {
            "label": label,
            "class": actor.get_class().get_name(),
            "location_cm": vector_row(actor.get_actor_location()),
            "bounds": bounds_row(actor),
        }
        component = actor.get_component_by_class(unreal.StaticMeshComponent)
        if component is not None:
            mesh = component.get_editor_property("static_mesh")
            row["mesh"] = mesh.get_path_name() if mesh is not None else None
        rows.append(row)
    contact_max_y = float(
        bounds_row(by_label["M01_V2_Corridor_CONTACT"])["maximum_cm"][1]
    )
    water_min_y = float(
        bounds_row(by_label["M01_V2_CoastalWater"])["minimum_cm"][1]
    )
    require(
        abs(contact_max_y - water_min_y) <= 50.0,
        "Water edge is not grounded to CONTACT bounds",
    )
    return {
        "actor_count": len(actors),
        "required_labels": list(required_labels),
        "missing_required_labels": missing,
        "window_actor_count": len(window_labels),
        "shoreline_contact_delta_cm": water_min_y - contact_max_y,
        "actors": rows,
    }


def capture(
    world: unreal.World,
    spec: dict[str, object],
) -> dict[str, object]:
    output = PROOF / f"{spec['id']}.png"
    location = tuple(float(value) for value in spec["location"])
    target = tuple(float(value) for value in spec["target"])
    rotation = look_at(location, target)
    render_target = unreal.RenderingLibrary.create_render_target2d(
        world,
        WIDTH,
        HEIGHT,
        unreal.TextureRenderTargetFormat.RTF_RGBA8,
    )
    capture_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.SceneCapture2D,
        unreal.Vector(*location),
        rotation,
    )
    require(capture_actor is not None, f"Could not spawn camera {spec['id']}")
    try:
        component = capture_actor.get_component_by_class(
            unreal.SceneCaptureComponent2D
        )
        require(component is not None, "SceneCaptureComponent2D unavailable")
        component.set_editor_property("texture_target", render_target)
        component.set_editor_property(
            "capture_source",
            unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR,
        )
        component.set_editor_property("capture_every_frame", False)
        component.set_editor_property("capture_on_movement", False)
        component.set_editor_property("fov_angle", float(spec["fov"]))
        component.set_editor_property("post_process_blend_weight", 1.0)
        settings = component.get_editor_property("post_process_settings")
        settings.set_editor_property("override_auto_exposure_method", True)
        settings.set_editor_property(
            "auto_exposure_method",
            unreal.AutoExposureMethod.AEM_MANUAL,
        )
        settings.set_editor_property("override_auto_exposure_bias", True)
        settings.set_editor_property("auto_exposure_bias", 2.5)
        component.set_editor_property("post_process_settings", settings)
        unreal.SystemLibrary.execute_console_command(
            world,
            "r.EyeAdaptationQuality 0",
        )
        unreal.SystemLibrary.execute_console_command(
            world,
            "r.DefaultFeature.AutoExposure 0",
        )
        component.capture_scene()
        unreal.RenderingLibrary.export_render_target(
            world,
            render_target,
            str(PROOF),
            output.name,
        )
    finally:
        unreal.EditorLevelLibrary.destroy_actor(capture_actor)
    require(output.is_file(), f"Capture missing: {output}")
    require(output.stat().st_size > 4096, f"Capture too small: {output}")
    dimensions = png_dimensions(output)
    require(dimensions == (WIDTH, HEIGHT), f"Unexpected dimensions: {dimensions}")
    return {
        **record(output),
        "id": spec["id"],
        "dimensions": list(dimensions),
        "location_cm": list(location),
        "target_cm": list(target),
        "fov_degrees": float(spec["fov"]),
        "exposure_bias": 2.5,
        "capture_method": "SceneCapture2D_FinalColorLDR_D3D12_SM6",
    }


def main() -> None:
    result: dict[str, object] = {
        "schema": "skyguard.m01-assembly.v2-remediation01.d3d12-capture.v1",
        "classification": "FAILED_WITH_EVIDENCE",
        "target_map": TARGET_MAP,
        "rhi": "D3D12_SM6",
        "runtime_promotion": False,
        "blender_used": False,
        "source_before": None,
        "source_after": None,
        "playable_before": None,
        "playable_after": None,
        "target_before": None,
        "target_after": None,
        "actor_audit": None,
        "captures": [],
        "error": None,
        "traceback": None,
    }
    try:
        PROOF.mkdir(parents=True, exist_ok=False)
        result["source_before"] = verify_record(
            SOURCE_DISK,
            SOURCE_BYTES,
            SOURCE_SHA256,
            "Assembly v1",
        )
        result["playable_before"] = verify_record(
            PLAYABLE_DISK,
            PLAYABLE_BYTES,
            PLAYABLE_SHA256,
            "Playable M01",
        )
        result["target_before"] = verify_record(
            TARGET_DISK,
            TARGET_BYTES,
            TARGET_SHA256,
            "Assembly v2",
        )
        loaded = unreal.EditorLoadingAndSavingUtils.load_map(TARGET_MAP)
        require(loaded is not None, f"Could not load {TARGET_MAP}")
        world = unreal.get_editor_subsystem(
            unreal.UnrealEditorSubsystem
        ).get_editor_world()
        require(world is not None, "Editor world unavailable")
        require(world.get_outermost().get_name() == TARGET_MAP, "Wrong editor world")
        result["actor_audit"] = actor_audit()
        result["captures"] = [capture(world, spec) for spec in CAMERAS]
        result["source_after"] = verify_record(
            SOURCE_DISK,
            SOURCE_BYTES,
            SOURCE_SHA256,
            "Assembly v1",
        )
        result["playable_after"] = verify_record(
            PLAYABLE_DISK,
            PLAYABLE_BYTES,
            PLAYABLE_SHA256,
            "Playable M01",
        )
        result["target_after"] = verify_record(
            TARGET_DISK,
            TARGET_BYTES,
            TARGET_SHA256,
            "Assembly v2",
        )
        require(
            result["source_before"] == result["source_after"],
            "Assembly v1 changed during capture",
        )
        require(
            result["playable_before"] == result["playable_after"],
            "Playable M01 changed during capture",
        )
        require(
            result["target_before"] == result["target_after"],
            "Assembly v2 changed during capture",
        )
        result["classification"] = (
            "CAPTURED_M01_ASSEMBLY_V2_AWAITING_DIRECT_VISUAL_REVIEW"
        )
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        result["traceback"] = traceback.format_exc()
        if SOURCE_DISK.is_file():
            result["source_after"] = record(SOURCE_DISK)
        if PLAYABLE_DISK.is_file():
            result["playable_after"] = record(PLAYABLE_DISK)
        if TARGET_DISK.is_file():
            result["target_after"] = record(TARGET_DISK)
    finally:
        write_json_atomic(RECEIPT, result)
    if not str(result["classification"]).startswith("CAPTURED_"):
        raise RuntimeError(result["error"] or result["classification"])


main()
unreal.SystemLibrary.collect_garbage()

_ticks_until_exit = 20
_callback_handle = None


def _delayed_exit(delta_seconds: float) -> None:
    del delta_seconds
    global _callback_handle
    global _ticks_until_exit
    _ticks_until_exit -= 1
    if _ticks_until_exit > 0:
        return
    if _callback_handle is not None:
        unreal.unregister_slate_post_tick_callback(_callback_handle)
        _callback_handle = None
    unreal.SystemLibrary.quit_editor()


_callback_handle = unreal.register_slate_post_tick_callback(_delayed_exit)
