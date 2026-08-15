"""Capture-only visual proof for the accepted GW02 window-bay import.

The immutable Recovery02 review map is opened by the Unreal command line. This
script creates only transient scene-capture actors and never saves the world.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import struct
import time
import traceback
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
ISOLATED = Path(r"D:\SG52T08_ENV01")
PROJECT = ISOLATED / "Skyguard52.uproject"
PROJECT_SHA256 = "7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a"
MAP_ASSET = "/Game/T08/GW02PreviewR02/Lvl_GW02_WindowPreview01_Recovery02"
MAP_FILE = ISOLATED / r"Content\T08\GW02PreviewR02\Lvl_GW02_WindowPreview01_Recovery02.umap"
MAP_SHA256 = "d83666579f4ef49b30daaed27fc8ba80ffec7af4b924b655998b440e56742c71"
SOURCE_ROOT = ISOLATED / r"Content\T08\GW02"
IMPORT_FREEZE = ROOT / r"Docs\AAA_Review\M01_WINDOW_RECOVERY06_UNREALREADY01_REVERSIBLE_UNREAL_IMPORT01_RECOVERY02_ACCEPTANCE_FREEZE.json"
IMPORT_FREEZE_SHA256 = "362579881b7df83bf32ce48a50e104f51149c08e3a1949b1894fad57a413b58c"
PRIOR_FREEZE = ROOT / r"Docs\AAA_Review\M01_WINDOW_RECOVERY06_UNREALREADY01_MAPPED_PREVIEW01_RECOVERY03_ATTEMPT01_TERMINAL_FREEZE.json"
PRIOR_FREEZE_SHA256 = "a6a5b98dbb69825d33f6aa179820a4dbd830dc16b8cf8f568c5343b6c74f6d05"
ATTEMPT = ROOT / r"Saved\BuildAttempts\M01_WINDOW_RECOVERY06_UNREALREADY01_MAPPED_PREVIEW01_RECOVERY04\attempt_01"
PROOF = ATTEMPT / "proof"
RECEIPT = ATTEMPT / "mapped_preview_receipt.json"
HEARTBEAT = ATTEMPT / "lifecycle_heartbeat.jsonl"

EXPECTED_ACTORS = {
    "GW02_FrameFacadeHardware": "/Game/T08/GW02/StaticMeshes/SM_M01_PrewarWindowBay_A01_FrameFacadeHardware.SM_M01_PrewarWindowBay_A01_FrameFacadeHardware",
    "GW02_Glass": "/Game/T08/GW02/StaticMeshes/SM_M01_PrewarWindowBay_A01_Glass.SM_M01_PrewarWindowBay_A01_Glass",
    "GW02_Interior": "/Game/T08/GW02/StaticMeshes/SM_M01_PrewarWindowBay_A01_Interior.SM_M01_PrewarWindowBay_A01_Interior",
}

CAMERAS = [
    {"id": "01_front_hero", "location": (0.0, 760.0, 250.0), "target": (0.0, -10.0, 210.0), "fov": 42.0},
    {"id": "02_front_left", "location": (-430.0, 690.0, 275.0), "target": (0.0, -15.0, 210.0), "fov": 45.0},
    {"id": "03_front_right", "location": (430.0, 690.0, 275.0), "target": (0.0, -15.0, 210.0), "fov": 45.0},
    {"id": "04_close_hardware", "location": (150.0, 370.0, 245.0), "target": (35.0, 0.0, 220.0), "fov": 34.0},
    {"id": "05_rear_interior", "location": (0.0, -720.0, 235.0), "target": (0.0, -55.0, 205.0), "fov": 46.0},
    {"id": "06_high_oblique", "location": (-360.0, 570.0, 520.0), "target": (0.0, -30.0, 205.0), "fov": 48.0},
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def hash_tree(root: Path) -> dict[str, dict[str, object]]:
    result: dict[str, dict[str, object]] = {}
    for path in sorted(root.rglob("*")) if root.is_dir() else []:
        if path.is_file():
            result[path.relative_to(root).as_posix()] = {
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
    return result


def write_json_atomic(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    os.replace(temporary, path)


def append_jsonl(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(payload, sort_keys=True) + "\n")


def png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as stream:
        if stream.read(8) != b"\x89PNG\r\n\x1a\n":
            raise RuntimeError(f"Not a PNG: {path}")
        length = struct.unpack(">I", stream.read(4))[0]
        if stream.read(4) != b"IHDR" or length < 8:
            raise RuntimeError(f"PNG IHDR missing: {path}")
        return struct.unpack(">II", stream.read(8))


def look_at(location: tuple[float, float, float], target: tuple[float, float, float]) -> unreal.Rotator:
    dx = target[0] - location[0]
    dy = target[1] - location[1]
    dz = target[2] - location[2]
    horizontal = math.sqrt(dx * dx + dy * dy)
    return unreal.Rotator(
        pitch=math.degrees(math.atan2(dz, horizontal)),
        yaw=math.degrees(math.atan2(dy, dx)),
        roll=0.0,
    )


class CaptureState:
    def __init__(self, source_before: dict[str, dict[str, object]]) -> None:
        self.source_before = source_before
        self.started = time.monotonic()
        self.phase_started = self.started
        self.phase = "warmup"
        self.tick_count = 0
        self.capture_index = 0
        self.capture_gap_ticks = 0
        self.captures: list[dict[str, object]] = []
        self.callback = None
        self.finished = False
        self.warmup_seconds = 45.0
        self.maximum_seconds = 900.0

    def event(self, event: str, **fields: object) -> None:
        append_jsonl(
            HEARTBEAT,
            {
                "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "event": event,
                "phase": self.phase,
                "tick": self.tick_count,
                **fields,
            },
        )

    def capture(self, spec: dict[str, object]) -> None:
        world = unreal.EditorLevelLibrary.get_editor_world()
        render_target = unreal.RenderingLibrary.create_render_target2d(
            world, 2560, 1440, unreal.TextureRenderTargetFormat.RTF_RGBA8
        )
        actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.SceneCapture2D, unreal.Vector(), unreal.Rotator()
        )
        if actor is None:
            raise RuntimeError("Could not spawn transient SceneCapture2D")
        try:
            component = actor.capture_component2d
            component.set_editor_property("texture_target", render_target)
            component.set_editor_property(
                "capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR
            )
            component.set_editor_property("capture_every_frame", False)
            component.set_editor_property("capture_on_movement", False)
            component.set_editor_property("fov_angle", float(spec["fov"]))
            location = tuple(float(value) for value in spec["location"])
            target = tuple(float(value) for value in spec["target"])
            rotation = look_at(location, target)
            actor.set_actor_location(unreal.Vector(*location), False, False)
            actor.set_actor_rotation(rotation, False)
            component.capture_scene()
            output = PROOF / f"{spec['id']}.png"
            unreal.RenderingLibrary.export_render_target(
                world, render_target, str(PROOF), output.name
            )
            if not output.is_file() or output.stat().st_size < 4096:
                raise RuntimeError(f"Capture missing or implausibly small: {output}")
            if png_dimensions(output) != (2560, 1440):
                raise RuntimeError(f"Capture dimensions changed: {output}")
            self.captures.append(
                {
                    "id": spec["id"],
                    "path": str(output),
                    "bytes": output.stat().st_size,
                    "sha256": sha256(output),
                    "location_cm": list(location),
                    "target_cm": list(target),
                    "rotation_degrees": {
                        "pitch": float(rotation.pitch),
                        "yaw": float(rotation.yaw),
                        "roll": float(rotation.roll),
                    },
                    "fov_degrees": float(spec["fov"]),
                }
            )
            self.event("capture_complete", camera=spec["id"])
        finally:
            unreal.EditorLevelLibrary.destroy_actor(actor)

    def finish(self, classification: str, error: str | None = None) -> None:
        if self.finished:
            return
        self.finished = True
        if self.callback is not None:
            unreal.unregister_slate_post_tick_callback(self.callback)
            self.callback = None
        source_after = hash_tree(SOURCE_ROOT)
        map_after = sha256(MAP_FILE) if MAP_FILE.is_file() else None
        if classification.startswith("PASSED_") and source_after != self.source_before:
            classification = "FAILED_WITH_EVIDENCE"
            error = "Accepted GW02 imported asset packages changed during capture"
        if classification.startswith("PASSED_") and map_after != MAP_SHA256:
            classification = "FAILED_WITH_EVIDENCE"
            error = "Immutable Recovery02 review map changed during capture"
        receipt = {
            "schema": "skyguard.m01-window-recovery06-unrealready01.mapped-preview01-recovery04.v1",
            "classification": classification,
            "error": error,
            "map_asset": MAP_ASSET,
            "map_file": str(MAP_FILE),
            "map_sha256_before": MAP_SHA256,
            "map_sha256_after": map_after,
            "map_unchanged": map_after == MAP_SHA256,
            "accepted_source_tree_unchanged": source_after == self.source_before,
            "source_file_count": len(source_after),
            "captures": self.captures,
            "capture_count": len(self.captures),
            "resolution": [2560, 1440],
            "warmup_seconds": self.warmup_seconds,
            "tick_count": self.tick_count,
            "runtime_promotion_performed": False,
            "world_saved": False,
        }
        write_json_atomic(RECEIPT, receipt)
        self.event("terminal", classification=classification, error=error)
        unreal.SystemLibrary.quit_editor()

    def tick(self, delta_time: float) -> None:
        try:
            self.tick_count += 1
            now = time.monotonic()
            if now - self.started > self.maximum_seconds:
                raise TimeoutError("Recovery04 capture exceeded its 900-second native timeout")
            if self.phase == "warmup":
                if now - self.phase_started < self.warmup_seconds:
                    return
                self.phase = "capture"
                self.phase_started = now
                self.event("capture_phase_started")
                return
            if self.capture_gap_ticks > 0:
                self.capture_gap_ticks -= 1
                return
            if self.capture_index < len(CAMERAS):
                self.capture(CAMERAS[self.capture_index])
                self.capture_index += 1
                self.capture_gap_ticks = 4
                return
            if len(self.captures) != len(CAMERAS):
                raise RuntimeError("Capture count changed")
            self.finish("PASSED_RECOVERY04_AUTOMATIC_AWAITING_DIRECT_VISUAL_REVIEW")
        except Exception as exc:
            self.finish(
                "FAILED_WITH_EVIDENCE",
                f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}",
            )


_STATE: CaptureState | None = None


def main() -> None:
    global _STATE
    for path, expected in (
        (PROJECT, PROJECT_SHA256),
        (MAP_FILE, MAP_SHA256),
        (IMPORT_FREEZE, IMPORT_FREEZE_SHA256),
        (PRIOR_FREEZE, PRIOR_FREEZE_SHA256),
    ):
        if not path.is_file() or sha256(path) != expected:
            raise RuntimeError(f"Frozen authority changed: {path}")
    allowed_launcher_files = {
        "unreal.stdout.log",
        "unreal.stderr.log",
        "unreal.engine.log",
        "process_tree_samples.jsonl",
    }
    unexpected = []
    if ATTEMPT.exists():
        unexpected = sorted(
            path.name for path in ATTEMPT.iterdir() if path.name not in allowed_launcher_files
        )
    if unexpected or RECEIPT.exists() or PROOF.exists():
        raise RuntimeError(f"Fresh Recovery04 executor namespace is not clean: {unexpected}")
    PROOF.mkdir(parents=True, exist_ok=False)
    source_before = hash_tree(SOURCE_ROOT)
    if len(source_before) != 30:
        raise RuntimeError(f"Accepted GW02 source file count changed: {len(source_before)}")

    world = unreal.EditorLevelLibrary.get_editor_world()
    world_path = str(world.get_path_name())
    if "GW02PreviewR02/Lvl_GW02_WindowPreview01_Recovery02" not in world_path:
        raise RuntimeError(f"Wrong review map loaded: {world_path}")
    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    labels: dict[str, list[object]] = {}
    for actor in actors:
        labels.setdefault(actor.get_actor_label(), []).append(actor)
    for label, expected_asset in EXPECTED_ACTORS.items():
        matches = labels.get(label, [])
        if len(matches) != 1:
            raise RuntimeError(f"Expected one actor {label}; found {len(matches)}")
        component = matches[0].get_component_by_class(unreal.StaticMeshComponent)
        if component is None:
            raise RuntimeError(f"Actor {label} lacks StaticMeshComponent")
        mesh = component.get_editor_property("static_mesh")
        if mesh is None or str(mesh.get_path_name()) != expected_asset:
            raise RuntimeError(f"Actor {label} mesh changed: {mesh}")

    _STATE = CaptureState(source_before)
    _STATE.event("capture_only_preview_ready", world_path=world_path, actor_count=len(actors))
    _STATE.callback = unreal.register_slate_post_tick_callback(_STATE.tick)


try:
    main()
except Exception as exc:
    write_json_atomic(
        RECEIPT,
        {
            "schema": "skyguard.m01-window-recovery06-unrealready01.mapped-preview01-recovery04.v1",
            "classification": "FAILED_WITH_EVIDENCE",
            "error": f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}",
            "runtime_promotion_performed": False,
            "world_saved": False,
        },
    )
    unreal.SystemLibrary.quit_editor()
    raise
