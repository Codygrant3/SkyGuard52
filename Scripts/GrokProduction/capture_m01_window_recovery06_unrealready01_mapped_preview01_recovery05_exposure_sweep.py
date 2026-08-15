"""Manual-exposure sweep for the accepted GW02 review map.

This is a capture-only calibration pass. It never saves the map or changes the
accepted imported assets. The backdrop is hidden only in memory for rear views.
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
MAP_ASSET = "/Game/T08/GW02PreviewR02/Lvl_GW02_WindowPreview01_Recovery02"
MAP_FILE = ISOLATED / r"Content\T08\GW02PreviewR02\Lvl_GW02_WindowPreview01_Recovery02.umap"
MAP_SHA256 = "d83666579f4ef49b30daaed27fc8ba80ffec7af4b924b655998b440e56742c71"
SOURCE_ROOT = ISOLATED / r"Content\T08\GW02"
PRIOR_FREEZE = ROOT / r"Docs\AAA_Review\M01_WINDOW_RECOVERY06_UNREALREADY01_MAPPED_PREVIEW01_RECOVERY04_ATTEMPT01_TERMINAL_FREEZE.json"
PRIOR_FREEZE_SHA256 = "582883d3b49db62ada2c5dc47afe65b9a859019b33ec8f37951c29d64828c7aa"
ATTEMPT = ROOT / r"Saved\BuildAttempts\M01_WINDOW_RECOVERY06_UNREALREADY01_MAPPED_PREVIEW01_RECOVERY05_EXPOSURE_SWEEP\attempt_01"
PROOF = ATTEMPT / "proof"
RECEIPT = ATTEMPT / "exposure_sweep_receipt.json"
HEARTBEAT = ATTEMPT / "lifecycle_heartbeat.jsonl"

EXPOSURES = [-18, -16, -14, -12, -10, -8, -6]
VIEWS = [
    {
        "id": "front_hero",
        "location": (0.0, 760.0, 250.0),
        "target": (0.0, -10.0, 210.0),
        "fov": 42.0,
        "hide_backdrop": False,
    },
    {
        "id": "rear_interior",
        "location": (0.0, -720.0, 235.0),
        "target": (0.0, -55.0, 205.0),
        "fov": 46.0,
        "hide_backdrop": True,
    },
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


def ev_token(value: int) -> str:
    return f"m{abs(value)}" if value < 0 else f"p{value}"


class SweepState:
    def __init__(self, source_before: dict[str, dict[str, object]], backdrop: object) -> None:
        self.source_before = source_before
        self.backdrop = backdrop
        self.backdrop_component = backdrop.get_component_by_class(unreal.StaticMeshComponent)
        if self.backdrop_component is None:
            raise RuntimeError("Review backdrop lacks StaticMeshComponent")
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
        self.specs = [
            {"view": view, "exposure": exposure}
            for view in VIEWS
            for exposure in EXPOSURES
        ]
        world = unreal.EditorLevelLibrary.get_editor_world()
        self.render_target = unreal.RenderingLibrary.create_render_target2d(
            world, 1920, 1080, unreal.TextureRenderTargetFormat.RTF_RGBA8
        )
        self.capture_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.SceneCapture2D, unreal.Vector(), unreal.Rotator()
        )
        if self.capture_actor is None:
            raise RuntimeError("Could not spawn transient SceneCapture2D")
        self.component = self.capture_actor.capture_component2d
        self.component.set_editor_property("texture_target", self.render_target)
        self.component.set_editor_property(
            "capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR
        )
        self.component.set_editor_property("capture_every_frame", False)
        self.component.set_editor_property("capture_on_movement", False)
        self.component.set_editor_property("post_process_blend_weight", 1.0)

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

    def set_manual_exposure(self, bias: float) -> None:
        settings = self.component.get_editor_property("post_process_settings")
        settings.set_editor_property("override_auto_exposure_method", True)
        settings.set_editor_property(
            "auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL
        )
        settings.set_editor_property("override_auto_exposure_bias", True)
        settings.set_editor_property("auto_exposure_bias", float(bias))
        self.component.set_editor_property("post_process_settings", settings)

    def set_backdrop_visible(self, visible: bool) -> None:
        self.backdrop.set_actor_hidden_in_game(not visible)
        self.backdrop_component.set_visibility(visible, True)

    def capture(self, spec: dict[str, object]) -> None:
        view = spec["view"]
        exposure = int(spec["exposure"])
        self.set_backdrop_visible(not bool(view["hide_backdrop"]))
        self.set_manual_exposure(exposure)
        location = tuple(float(value) for value in view["location"])
        target = tuple(float(value) for value in view["target"])
        rotation = look_at(location, target)
        self.capture_actor.set_actor_location(unreal.Vector(*location), False, False)
        self.capture_actor.set_actor_rotation(rotation, False)
        self.component.set_editor_property("fov_angle", float(view["fov"]))
        for _ in range(3):
            self.component.capture_scene()
        output = PROOF / f"{view['id']}_ev_{ev_token(exposure)}.png"
        unreal.RenderingLibrary.export_render_target(
            unreal.EditorLevelLibrary.get_editor_world(),
            self.render_target,
            str(PROOF),
            output.name,
        )
        if not output.is_file() or output.stat().st_size < 4096:
            raise RuntimeError(f"Capture missing or implausibly small: {output}")
        if png_dimensions(output) != (1920, 1080):
            raise RuntimeError(f"Capture dimensions changed: {output}")
        self.captures.append(
            {
                "view": view["id"],
                "exposure_bias_ev": exposure,
                "backdrop_hidden": bool(view["hide_backdrop"]),
                "path": str(output),
                "bytes": output.stat().st_size,
                "sha256": sha256(output),
            }
        )
        self.event(
            "capture_complete", view=view["id"], exposure_bias_ev=exposure
        )

    def restore(self) -> None:
        self.set_backdrop_visible(True)
        if self.capture_actor is not None:
            unreal.EditorLevelLibrary.destroy_actor(self.capture_actor)
            self.capture_actor = None

    def finish(self, classification: str, error: str | None = None) -> None:
        if self.finished:
            return
        self.finished = True
        if self.callback is not None:
            unreal.unregister_slate_post_tick_callback(self.callback)
            self.callback = None
        restoration_error = None
        try:
            self.restore()
        except Exception as exc:
            restoration_error = f"{type(exc).__name__}: {exc}"
            classification = "FAILED_WITH_EVIDENCE"
            error = f"{error or ''}\nRestoration failed: {restoration_error}".strip()
        source_after = hash_tree(SOURCE_ROOT)
        map_after = sha256(MAP_FILE) if MAP_FILE.is_file() else None
        if classification.startswith("PASSED_") and source_after != self.source_before:
            classification = "FAILED_WITH_EVIDENCE"
            error = "Accepted GW02 imported asset packages changed during sweep"
        if classification.startswith("PASSED_") and map_after != MAP_SHA256:
            classification = "FAILED_WITH_EVIDENCE"
            error = "Immutable Recovery02 review map changed during sweep"
        receipt = {
            "schema": "skyguard.m01-window-recovery06-unrealready01.mapped-preview01-recovery05-exposure-sweep.v1",
            "classification": classification,
            "error": error,
            "restoration_error": restoration_error,
            "map_asset": MAP_ASSET,
            "map_sha256_before": MAP_SHA256,
            "map_sha256_after": map_after,
            "map_unchanged": map_after == MAP_SHA256,
            "accepted_source_tree_unchanged": source_after == self.source_before,
            "source_file_count": len(source_after),
            "exposure_candidates_ev": EXPOSURES,
            "views": [view["id"] for view in VIEWS],
            "captures": self.captures,
            "capture_count": len(self.captures),
            "resolution": [1920, 1080],
            "warmup_seconds": self.warmup_seconds,
            "tick_count": self.tick_count,
            "backdrop_restored": restoration_error is None,
            "world_saved": False,
            "runtime_promotion_performed": False,
        }
        write_json_atomic(RECEIPT, receipt)
        self.event("terminal", classification=classification, error=error)
        unreal.SystemLibrary.quit_editor()

    def tick(self, delta_time: float) -> None:
        try:
            self.tick_count += 1
            now = time.monotonic()
            if now - self.started > self.maximum_seconds:
                raise TimeoutError("Recovery05 exposure sweep exceeded 900 seconds")
            if self.phase == "warmup":
                if now - self.phase_started < self.warmup_seconds:
                    return
                self.phase = "capture"
                self.event("capture_phase_started")
                return
            if self.capture_gap_ticks > 0:
                self.capture_gap_ticks -= 1
                return
            if self.capture_index < len(self.specs):
                self.capture(self.specs[self.capture_index])
                self.capture_index += 1
                self.capture_gap_ticks = 3
                return
            if len(self.captures) != len(self.specs):
                raise RuntimeError("Exposure-sweep capture count changed")
            self.finish("PASSED_RECOVERY05_EXPOSURE_SWEEP_AWAITING_SELECTION")
        except Exception as exc:
            self.finish(
                "FAILED_WITH_EVIDENCE",
                f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}",
            )


_STATE: SweepState | None = None


def main() -> None:
    global _STATE
    if not PRIOR_FREEZE.is_file() or sha256(PRIOR_FREEZE) != PRIOR_FREEZE_SHA256:
        raise RuntimeError("Recovery04 terminal freeze changed")
    if not MAP_FILE.is_file() or sha256(MAP_FILE) != MAP_SHA256:
        raise RuntimeError("Immutable Recovery02 review map changed")
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
        raise RuntimeError(f"Fresh Recovery05 namespace is not clean: {unexpected}")
    PROOF.mkdir(parents=True, exist_ok=False)
    source_before = hash_tree(SOURCE_ROOT)
    if len(source_before) != 30:
        raise RuntimeError(f"Accepted GW02 source file count changed: {len(source_before)}")
    world = unreal.EditorLevelLibrary.get_editor_world()
    world_path = str(world.get_path_name())
    if "GW02PreviewR02/Lvl_GW02_WindowPreview01_Recovery02" not in world_path:
        raise RuntimeError(f"Wrong review map loaded: {world_path}")
    backdrop_matches = [
        actor
        for actor in unreal.EditorLevelLibrary.get_all_level_actors()
        if actor.get_actor_label() == "GW02_ReviewBackdrop"
    ]
    if len(backdrop_matches) != 1:
        raise RuntimeError(
            f"Expected one review backdrop; found {len(backdrop_matches)}"
        )
    _STATE = SweepState(source_before, backdrop_matches[0])
    _STATE.event("exposure_sweep_ready", world_path=world_path)
    _STATE.callback = unreal.register_slate_post_tick_callback(_STATE.tick)


try:
    main()
except Exception as exc:
    write_json_atomic(
        RECEIPT,
        {
            "schema": "skyguard.m01-window-recovery06-unrealready01.mapped-preview01-recovery05-exposure-sweep.v1",
            "classification": "FAILED_WITH_EVIDENCE",
            "error": f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}",
            "world_saved": False,
            "runtime_promotion_performed": False,
        },
    )
    unreal.SystemLibrary.quit_editor()
    raise
