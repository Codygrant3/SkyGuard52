"""Capture a quarantined, real-RHI visual proof of the M01 assembly map.

This gate never saves the assembly map and verifies that the playable M01 map
and the quarantined assembly package remain byte-identical throughout capture.
"""

from __future__ import annotations

import hashlib
import json
import os
import struct
import traceback
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
TARGET_MAP = "/Game/Skyguard/Maps/Assembly/Lvl_M01_AcceptedModuleAssembly_v1"
TARGET_DISK = ROOT / r"Content\Skyguard\Maps\Assembly\Lvl_M01_AcceptedModuleAssembly_v1.umap"
PLAYABLE_DISK = ROOT / r"Content\Skyguard\Maps\Lvl_M01_CoastalIntercept_Playable_v1.umap"
PLAYABLE_BYTES = 70_545
PLAYABLE_SHA256 = "9d2ca2e50b446f488926bdd8a29eca9fe33d62ec25656fc77ca55997f5a08afa"
ATTEMPT = (
    ROOT
    / r"Saved\BuildAttempts\M01_ACCEPTED_MODULE_ASSEMBLY_V1_INTEGRATION_GATE01"
    / "attempt_01"
)
PROOF = ATTEMPT / "proof"
RECEIPT = ATTEMPT / "integration_gate_receipt.json"
WIDTH = 1920
HEIGHT = 1080

CAMERAS = (
    {
        "id": "assembly_aerial",
        "location": (-5600.0, -5200.0, 4200.0),
        "target": (0.0, 1400.0, 150.0),
        "fov": 60.0,
    },
    {
        "id": "facade_coastal_front",
        "location": (0.0, 500.0, 420.0),
        "target": (0.0, 2400.0, 240.0),
        "fov": 48.0,
    },
    {
        "id": "facade_coastal_reverse",
        "location": (0.0, 4300.0, 420.0),
        "target": (0.0, 2400.0, 240.0),
        "fov": 48.0,
    },
    {
        "id": "shoreline_contact_oblique",
        "location": (4200.0, -700.0, 950.0),
        "target": (0.0, 2100.0, 80.0),
        "fov": 55.0,
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


def look_at(
    location: tuple[float, float, float],
    target: tuple[float, float, float],
) -> unreal.Rotator:
    direction = unreal.Vector(
        target[0] - location[0],
        target[1] - location[1],
        target[2] - location[2],
    )
    return direction.rotator()


def playable_record() -> dict[str, object]:
    require(PLAYABLE_DISK.is_file(), f"Playable map missing: {PLAYABLE_DISK}")
    result = record(PLAYABLE_DISK)
    require(result["bytes"] == PLAYABLE_BYTES, "Playable map byte count changed")
    require(result["sha256"] == PLAYABLE_SHA256, "Playable map SHA-256 changed")
    return result


def actor_audit() -> dict[str, object]:
    labels: list[str] = []
    classes: dict[str, int] = {}
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        label = actor.get_actor_label()
        labels.append(label)
        class_name = actor.get_class().get_name()
        classes[class_name] = classes.get(class_name, 0) + 1
    required_labels = (
        "M01_Polish01_DirectionalLight_Sun",
        "M01_Polish01_SkyLight",
        "M01_Polish01_SkyAtmosphere",
        "M01_Polish01_ExponentialHeightFog",
        "M01_Polish01_PostProcess_Unbound",
        "M01_Polish01_CoastalWaterPlane",
        "M01_AcceptedCorridor_TERRAIN_Grounding",
    )
    missing = [label for label in required_labels if label not in labels]
    window_labels = [
        label for label in labels if label.startswith("M01_AcceptedWindowBay_")
    ]
    require(not missing, f"Assembly actors missing: {missing}")
    require(len(window_labels) >= 12, "Expected four three-part window bays")
    return {
        "actor_count": len(labels),
        "class_counts": classes,
        "required_labels": list(required_labels),
        "missing_required_labels": missing,
        "window_actor_count": len(window_labels),
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
        try:
            component.set_editor_property("post_process_blend_weight", 1.0)
            settings = component.get_editor_property("post_process_settings")
            settings.set_editor_property("override_auto_exposure_method", True)
            settings.set_editor_property(
                "auto_exposure_method",
                unreal.AutoExposureMethod.AEM_MANUAL,
            )
            settings.set_editor_property("override_auto_exposure_bias", True)
            settings.set_editor_property("auto_exposure_bias", 0.0)
            component.set_editor_property("post_process_settings", settings)
        except Exception:
            pass
        unreal.SystemLibrary.execute_console_command(world, "r.EyeAdaptationQuality 0")
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
        "capture_method": "SceneCapture2D_FinalColorLDR_real_rhi",
    }


def main() -> None:
    result: dict[str, object] = {
        "schema": "skyguard.m01-assembly.integration-gate01.v1",
        "classification": "FAILED_WITH_EVIDENCE",
        "target_map": TARGET_MAP,
        "runtime_promotion": False,
        "blender_used": False,
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
        result["playable_before"] = playable_record()
        require(TARGET_DISK.is_file(), f"Assembly map missing: {TARGET_DISK}")
        result["target_before"] = record(TARGET_DISK)
        loaded = unreal.EditorLoadingAndSavingUtils.load_map(TARGET_MAP)
        require(loaded is not None, f"Failed to load {TARGET_MAP}")
        world = unreal.EditorLevelLibrary.get_editor_world()
        require(world is not None, "Editor world unavailable")
        result["actor_audit"] = actor_audit()
        captures = [capture(world, spec) for spec in CAMERAS]
        result["captures"] = captures
        result["playable_after"] = playable_record()
        result["target_after"] = record(TARGET_DISK)
        require(
            result["playable_before"] == result["playable_after"],
            "Playable map changed during visual capture",
        )
        require(
            result["target_before"] == result["target_after"],
            "Assembly map changed during read-only visual capture",
        )
        result["classification"] = (
            "CAPTURED_M01_ASSEMBLY_GATE01_AWAITING_DIRECT_VISUAL_REVIEW"
        )
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        result["traceback"] = traceback.format_exc()
        if PLAYABLE_DISK.is_file():
            result["playable_after"] = record(PLAYABLE_DISK)
        if TARGET_DISK.is_file():
            result["target_after"] = record(TARGET_DISK)
    finally:
        write_json_atomic(RECEIPT, result)
    if str(result["classification"]).startswith("CAPTURED_"):
        return
    raise RuntimeError(result["error"] or result["classification"])


if __name__ == "__main__":
    main()
