"""Read-only tick-driven representative Mission 1 proof for Attempt08.

This module is imported only by a separately authorized Unreal process. It
never saves packages, generates PCG, modifies assets, promotes content, or
reuses an existing output namespace.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
import time
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
CONTRACT_PATH = ROOT / "Docs/AAA_Review/PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_CONTRACT.json"
CAMERAS_PATH = ROOT / "Docs/AAA_Review/PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_CAMERAS.json"
CONTRACT_ID = "P4.6-M01-REPRESENTATIVE-VISUAL-008"
_STATE = None


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_switch(name: str) -> str:
    line = unreal.SystemLibrary.get_command_line()
    match = re.search(rf'(?:^|\s)-{re.escape(name)}=(?:"([^"]+)"|(\S+))', line, re.I)
    if not match:
        raise RuntimeError(f"Missing required -{name} switch")
    return match.group(1) or match.group(2)


def png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()[:24]
    if len(data) != 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError(f"Invalid PNG: {path}")
    return int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")


class Attempt08State:
    def __init__(self, contract: dict, cameras: dict, output_root: Path):
        self.contract = contract
        self.cameras = cameras
        self.output_root = output_root
        self.capture_root = output_root / "captures"
        self.receipt = output_root / "capture_receipt.json"
        self.frame_csv = output_root / "frame_samples.csv"
        self.callback = None
        self.started = time.monotonic()
        self.last_tick = self.started
        self.tick_count = 0
        self.stable_ready = 0
        self.capture_index = 0
        self.gap_ticks = 0
        self.measurement_started: float | None = None
        self.records: list[dict] = []
        self.frame_samples: list[tuple[int, float]] = []
        self.failed = False
        self.authoring = unreal.SkyguardMission01EnvironmentAuthoringLibrary
        self.landscape = None
        self.governed_material = None
        self.specs = cameras["cameras"] + cameras["temporal_route_samples"]

    def find_landscape(self):
        matches = [
            actor for actor in unreal.EditorLevelLibrary.get_all_level_actors()
            if actor.get_class().get_name() in {"Landscape", "LandscapeStreamingProxy"}
            and actor.get_actor_label() == "M01_P4_Landscape_Production"
        ]
        if len(matches) != 1:
            raise RuntimeError(f"Expected one governed landscape; found {len(matches)}")
        return matches[0]

    def compilation_ready(self) -> bool:
        audit = self.authoring.audit_landscape_material_compilation(
            self.landscape, self.governed_material
        )
        ready = (
            bool(audit.success)
            and int(audit.landscape_component_count) == 16
            and int(audit.compilation_finished_resource_count) == 16
            and int(audit.valid_shader_map_resource_count) == 16
            and bool(audit.asset_compilation_queue_empty)
            and bool(audit.shader_compilation_queue_empty)
        )
        self.stable_ready = self.stable_ready + 1 if ready else 0
        return self.stable_ready >= self.contract["execution"]["stable_ready_polls_required"]

    def capture(self, spec: dict) -> None:
        world = unreal.EditorLevelLibrary.get_editor_world()
        width, height = self.contract["execution"]["resolution"]
        target = unreal.RenderingLibrary.create_render_target2d(
            world, width, height, unreal.TextureRenderTargetFormat.RTF_RGBA8
        )
        target.set_editor_property("clear_color", unreal.LinearColor(0, 0, 0, 1))
        actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.SceneCapture2D, unreal.Vector(), unreal.Rotator()
        )
        if actor is None:
            raise RuntimeError("Could not create transient whole-world capture")
        try:
            component = actor.capture_component2d
            component.set_editor_property("texture_target", target)
            component.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
            component.set_editor_property("capture_every_frame", False)
            component.set_editor_property("capture_on_movement", False)
            component.set_editor_property("fov_angle", self.cameras["fov_degrees"])
            rotation = spec["rotation_degrees"]
            actor.set_actor_location(unreal.Vector(*spec["location_cm"]), False, False)
            actor.set_actor_rotation(
                unreal.Rotator(
                    pitch=rotation["pitch"],
                    yaw=rotation["yaw"],
                    roll=rotation["roll"],
                ),
                False,
            )
            component.capture_scene()
            self.capture_root.mkdir(parents=True, exist_ok=True)
            output = self.capture_root / f"{spec['id']}.png"
            unreal.RenderingLibrary.export_render_target(
                world, target, str(self.capture_root), output.name
            )
            if not output.is_file() or output.stat().st_size == 0:
                raise RuntimeError(f"Missing capture: {output}")
            if list(png_dimensions(output)) != self.contract["execution"]["resolution"]:
                raise RuntimeError(f"Capture dimensions failed: {output}")
            self.records.append({
                "id": spec["id"],
                "path": str(output),
                "bytes": output.stat().st_size,
                "sha256": sha256_file(output),
                "location_cm": spec["location_cm"],
                "rotation_degrees": rotation,
                "tick": self.tick_count
            })
        finally:
            unreal.EditorLevelLibrary.destroy_actor(actor)

    def finish(self, gate: str, error: str | None = None) -> None:
        report = {
            "schema": "skyguard.phase4.m01-representative-visual-attempt08-capture.v1",
            "contract_id": CONTRACT_ID,
            "gate": gate,
            "error": error,
            "rhi": self.authoring.get_active_rhi_and_feature_level().strip().upper(),
            "deferred_tick_wait_used": True,
            "same_stack_compilation_finish_called": False,
            "stable_ready_polls": self.stable_ready,
            "tick_count": self.tick_count,
            "captures": self.records,
            "world_saved": False,
            "pcg_generation_invoked": False,
            "asset_mutation_invoked": False,
            "promotion_allowed": False
        }
        self.receipt.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        with self.frame_csv.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(["tick", "frame_ms"])
            writer.writerows(self.frame_samples)
        if self.callback is not None:
            unreal.unregister_slate_post_tick_callback(self.callback)
        unreal.SystemLibrary.quit_editor()

    def tick(self, delta_time: float) -> None:
        try:
            self.tick_count += 1
            if time.monotonic() - self.started > self.contract["execution"]["maximum_process_seconds"]:
                raise TimeoutError("Attempt08 bounded process timeout")
            ready = self.compilation_ready()
            if self.measurement_started is not None and not ready:
                raise RuntimeError("Shader or asset compilation resumed during measured interval")
            if not ready:
                return
            warmup_seconds = self.contract["performance_contract"]["warmup_seconds"]
            if time.monotonic() - self.started < warmup_seconds:
                return
            if self.measurement_started is None:
                self.measurement_started = time.monotonic()
            self.frame_samples.append((self.tick_count, float(delta_time) * 1000.0))
            if self.gap_ticks > 0:
                self.gap_ticks -= 1
                return
            if self.capture_index < len(self.specs):
                spec = self.specs[self.capture_index]
                self.capture(spec)
                self.capture_index += 1
                self.gap_ticks = int(spec.get("minimum_tick_gap_from_previous_capture", 1))
                return
            expected = self.contract["required_outputs"]["lit_png_count"]
            if len(self.records) != expected:
                raise RuntimeError(f"Expected {expected} captures; found {len(self.records)}")
            measured_seconds = time.monotonic() - self.measurement_started
            if (
                measured_seconds < self.contract["performance_contract"]["measured_seconds"]
                or len(self.frame_samples) < self.contract["performance_contract"]["minimum_tick_samples"]
            ):
                return
            self.finish("PASS_CAPTURE_COMPLETE_PENDING_OFFLINE_ACCEPTANCE")
        except Exception as exc:
            self.failed = True
            self.finish("FAIL_WITH_EVIDENCE", f"{type(exc).__name__}: {exc}")


def main() -> None:
    global _STATE
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8-sig"))
    cameras = json.loads(CAMERAS_PATH.read_text(encoding="utf-8-sig"))
    if contract["contract_id"] != CONTRACT_ID or cameras["contract_id"] != CONTRACT_ID:
        raise RuntimeError("Attempt08 contract identity failed")
    output_root = Path(parse_switch("SkyguardAttempt08OutputRoot")).resolve()
    expected = (ROOT / contract["execution"]["output_root"]).resolve()
    if output_root != expected or output_root.exists():
        raise RuntimeError("Attempt08 output namespace is invalid or already exists")
    rhi = unreal.SkyguardMission01EnvironmentAuthoringLibrary.get_active_rhi_and_feature_level().strip().upper()
    if rhi != "D3D12|SM6":
        raise RuntimeError(f"Attempt08 requires D3D12|SM6; got {rhi}")
    for item in contract["locked_sources"].values():
        if "sha256" in item and sha256_file(ROOT / item["file"]) != item["sha256"]:
            raise RuntimeError(f"Locked source changed: {item['file']}")
    output_root.mkdir(parents=True, exist_ok=False)
    if not unreal.EditorLevelLibrary.load_level(contract["locked_sources"]["primary_map"]["asset"]):
        raise RuntimeError("Could not load immutable Mission 1 production environment")
    _STATE = Attempt08State(contract, cameras, output_root)
    _STATE.landscape = _STATE.find_landscape()
    _STATE.governed_material = _STATE.landscape.get_editor_property("landscape_material")
    if _STATE.governed_material is None:
        raise RuntimeError("Governed landscape material is missing")
    _STATE.callback = unreal.register_slate_post_tick_callback(_STATE.tick)


if __name__ == "__main__":
    main()
