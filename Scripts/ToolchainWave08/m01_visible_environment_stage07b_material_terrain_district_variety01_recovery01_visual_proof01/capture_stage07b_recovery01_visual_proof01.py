"""D3D12 eight-camera proof for the Stage 7B Recovery01 corridor. Does not save."""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
ISOLATED = Path(r"D:\SG52T08_ENV01")
HERE = ROOT / "Scripts/ToolchainWave08/m01_visible_environment_stage07b_material_terrain_district_variety01_recovery01_visual_proof01"
CONTRACT_PATH = HERE / "stage07b_recovery01_visual_proof01_contract.json"
CAMERAS_PATH = ROOT / "Docs/AAA_Review/M01_VISIBLE_ENVIRONMENT_STAGE07B_MATERIAL_TERRAIN_DISTRICT_VARIETY01_CAMERAS.json"
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_VISIBLE_ENVIRONMENT_STAGE07B_MATERIAL_TERRAIN_DISTRICT_VARIETY01_RECOVERY01_VISUAL_PROOF01/attempt_01"
CAPTURE_DIR = ATTEMPT / "proof" / "captures"
RECEIPT = ATTEMPT / "proof" / "capture_receipt.json"
MAP_FILE = ISOLATED / "Content/M01/Lvl_M01_VisibleEnvironmentStage07BMaterialTerrainDistrictVariety01Recovery01.umap"
_STATE = None


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def record(path: Path) -> dict[str, object]:
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)}


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def png_size(path: Path) -> tuple[int, int]:
    header = path.read_bytes()[:24]
    if header[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError(f"Invalid PNG: {path}")
    return int.from_bytes(header[16:20], "big"), int.from_bytes(header[20:24], "big")


class Proof:
    def __init__(self) -> None:
        self.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        self.cameras = json.loads(CAMERAS_PATH.read_text(encoding="utf-8"))
        self.started = time.perf_counter()
        self.last = self.started
        self.samples: list[float] = []
        self.captures: list[dict[str, object]] = []
        self.callback = None
        self.done = False
        self.phase = "warmup"
        self.camera_queue = list(self.cameras["static_cameras"]) + list(self.cameras["temporal_cameras"])
        self.map_before = record(MAP_FILE)
        if self.map_before["sha256"] != self.contract["world"]["map_sha256"]:
            raise RuntimeError("Recovery01 map hash changed before proof")
        auth = Path(self.contract["authoring_authority"]["receipt"])
        if sha256(auth) != self.contract["authoring_authority"]["receipt_sha256"]:
            raise RuntimeError("Authoring receipt hash changed")
        actors = list(unreal.EditorLevelLibrary.get_all_level_actors())
        governed = [a for a in actors if a.get_actor_label() != "PCGWorldActor0"]
        if len(governed) != int(self.contract["world"]["expected_governed_actor_count"]):
            raise RuntimeError(f"Governed actor count changed: {len(governed)}")
        landscape = next(a for a in actors if a.get_actor_label() == "M01_A01_Landscape_Production")
        material = landscape.get_editor_property("landscape_material")
        identity = "" if material is None else material.get_path_name()
        if self.contract["world"]["landscape_material_contains"] not in identity:
            raise RuntimeError(f"Landscape material is not planting soil: {identity}")
        veg = [a for a in actors if a.get_actor_label().startswith("M01_STAGE07B_Vegetation_")]
        if len(veg) != 55:
            raise RuntimeError(f"Stage7B vegetation count changed: {len(veg)}")
        CAPTURE_DIR.mkdir(parents=True, exist_ok=True)

    def tick(self, delta: float) -> None:
        if self.done:
            return
        now = time.perf_counter()
        elapsed = now - self.started
        frame_ms = (now - self.last) * 1000.0
        self.last = now
        if self.phase == "warmup" and elapsed >= 30.0:
            self.phase = "measure"
            self.measure_started = now
            return
        if self.phase == "measure":
            self.samples.append(frame_ms)
            if now - self.measure_started >= 30.0:
                if len(self.samples) < 900:
                    raise RuntimeError(f"Insufficient samples: {len(self.samples)}")
                self.phase = "capture"
            return
        if self.phase == "capture":
            if not self.camera_queue:
                self.finish()
                return
            spec = self.camera_queue.pop(0)
            self.capture_one(spec)

    def capture_one(self, spec: dict[str, object]) -> None:
        world = unreal.EditorLevelLibrary.get_editor_world()
        actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.SceneCapture2D, unreal.Vector(*spec["location_cm"]),
            unreal.Rotator(pitch=spec["rotation_degrees"]["pitch"], yaw=spec["rotation_degrees"]["yaw"], roll=0.0),
        )
        if actor is None:
            raise RuntimeError(f"Failed to spawn capture camera {spec['id']}")
        try:
            component = actor.get_component_by_class(unreal.SceneCaptureComponent2D)
            target = unreal.RenderingLibrary.create_render_target2d(world, 2560, 1440, unreal.TextureRenderTargetFormat.RTF_RGBA8)
            component.set_editor_property("texture_target", target)
            component.set_editor_property("fov_angle", float(spec["fov_degrees"]))
            component.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
            component.capture_scene()
            output = CAPTURE_DIR / f"{spec['id']}.png"
            unreal.RenderingLibrary.export_render_target(world, target, str(CAPTURE_DIR), output.name)
            if not output.is_file() or png_size(output) != (2560, 1440):
                raise RuntimeError(f"Capture failed: {output}")
            self.captures.append({"id": spec["id"], **record(output)})
        finally:
            unreal.EditorLevelLibrary.destroy_actor(actor)

    def finish(self) -> None:
        if self.done:
            return
        self.done = True
        if self.callback is not None:
            unreal.unregister_slate_post_tick_callback(self.callback)
        samples = sorted(self.samples)
        p95 = samples[int(len(samples) * 0.95)] if samples else 0.0
        payload = {
            "schema": "skyguard.m01-visible-environment-stage07b-recovery01.visual-proof01-receipt.v1",
            "classification": "PASSED_AUTOMATIC_AWAITING_HUMAN_VISUAL_REVIEW",
            "sample_count": len(self.samples),
            "mean_frame_ms": sum(self.samples) / len(self.samples) if self.samples else 0.0,
            "p95_frame_ms": p95,
            "max_frame_ms": max(self.samples) if self.samples else 0.0,
            "frames_over_50_ms": sum(1 for item in self.samples if item > 50.0),
            "captures": self.captures,
            "map_before": self.map_before,
            "map_after": record(MAP_FILE),
            "world_saved": False,
        }
        if payload["map_after"]["sha256"] != payload["map_before"]["sha256"]:
            payload["classification"] = "FAILED_WITH_EVIDENCE"
            payload["error"] = "Proof mutated the Recovery01 map"
        if payload["p95_frame_ms"] > 16.7 or payload["max_frame_ms"] > 33.3 or payload["frames_over_50_ms"] != 0:
            payload["classification"] = "FAILED_WITH_EVIDENCE"
            payload["error"] = "Performance bounds failed"
        if len(self.captures) != 8:
            payload["classification"] = "FAILED_WITH_EVIDENCE"
            payload["error"] = "Capture count changed"
        write_json(RECEIPT, payload)
        unreal.SystemLibrary.quit_game(unreal.EditorLevelLibrary.get_editor_world())


def main() -> None:
    global _STATE
    _STATE = Proof()
    _STATE.callback = unreal.register_slate_post_tick_callback(_STATE.tick)


if __name__ == "__main__":
    main()
