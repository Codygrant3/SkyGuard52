"""Stage 7A tick-driven D3D12 proof bound to the Recovery01 corridor.

Waits for two stable landscape-shader polls, warms 30s, measures 30s, then
captures eight SceneCapture LDR frames. Does not save the world.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import time
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
ISOLATED = Path(r"D:\SG52T08_ENV01")
HERE = ROOT / "Scripts/ToolchainWave08/m01_visible_environment_stage07b_material_terrain_district_variety01_recovery01_visual_proof01_recovery02"
CONTRACT_PATH = HERE / "stage07b_recovery01_visual_proof01_recovery02_contract.json"
CAMERAS_PATH = ROOT / "Docs/AAA_Review/M01_VISIBLE_ENVIRONMENT_STAGE07B_MATERIAL_TERRAIN_DISTRICT_VARIETY01_CAMERAS.json"
CONTRACT_ID = "M01-VISIBLE-ENVIRONMENT-STAGE07B-MATERIAL-TERRAIN-DISTRICT-VARIETY01-RECOVERY01-VISUAL-PROOF01-RECOVERY02"
CSV_FILENAME = "M01VisibleEnvironmentStage07BRecovery01VisualProof01Recovery02.csv"
MAP_FILE = ISOLATED / "Content/M01/Lvl_M01_VisibleEnvironmentStage07BMaterialTerrainDistrictVariety01Recovery01.umap"
LAUNCHER = ROOT / "Saved/BuildAttempts/M01_VISIBLE_ENVIRONMENT_STAGE07B_MATERIAL_TERRAIN_DISTRICT_VARIETY01_RECOVERY01_VISUAL_PROOF01_RECOVERY02/launcher_attempt_01"
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_VISIBLE_ENVIRONMENT_STAGE07B_MATERIAL_TERRAIN_DISTRICT_VARIETY01_RECOVERY01_VISUAL_PROOF01_RECOVERY02/attempt_01"
_STATE = None


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_json_atomic(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def append_jsonl(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(value, sort_keys=True) + "\n")


def parse_switch(name: str) -> str:
    command_line = unreal.SystemLibrary.get_command_line()
    match = re.search(rf'(?:^|\s)-{re.escape(name)}=(?:"([^"]+)"|(\S+))', command_line, re.IGNORECASE)
    if not match:
        raise RuntimeError(f"Missing required -{name} switch")
    return match.group(1) or match.group(2)


def asset_identity(asset) -> str:
    return "" if asset is None else str(asset.get_path_name())


def png_dimensions(path: Path) -> tuple[int, int]:
    header = path.read_bytes()[:24]
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError(f"Invalid PNG: {path}")
    return int.from_bytes(header[16:20], "big"), int.from_bytes(header[20:24], "big")


class ProofState:
    def __init__(self, contract: dict, cameras: dict, landscape, terrain_material, actors: list, map_hash_before: str) -> None:
        self.contract = contract
        self.cameras = cameras
        self.attempt_root = ATTEMPT
        self.proof_root = ATTEMPT / "proof"
        self.capture_root = self.proof_root / "captures"
        self.heartbeat_path = self.proof_root / "lifecycle_heartbeat.jsonl"
        self.frame_csv = self.proof_root / "frame_samples.csv"
        self.capture_receipt = self.proof_root / "capture_receipt.json"
        self.landscape = landscape
        self.terrain_material = terrain_material
        self.actors = actors
        self.map_hash_before = map_hash_before
        self.authoring = unreal.SkyguardMission01EnvironmentAuthoringLibrary
        self.callback = None
        self.started = time.monotonic()
        self.phase_started = self.started
        self.phase = "shader_readiness"
        self.next_audit_at = self.started
        self.stable_ready_polls = 0
        self.tick_count = 0
        self.measurement_started = 0.0
        self.csv_started = False
        self.csv_stopped = False
        self.csv_last_size = -1
        self.csv_stable_polls = 0
        self.capture_index = 0
        self.capture_gap_ticks = 0
        self.captures: list[dict] = []
        self.frame_samples: list[tuple[int, float, float]] = []
        self.finished = False
        self.specs = cameras["static_cameras"] + cameras["temporal_cameras"]
        self.capture_root.mkdir(parents=True, exist_ok=True)

    def heartbeat(self, event: str, **fields) -> None:
        payload = {"event": event, "phase": self.phase, "tick": self.tick_count, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        payload.update(fields)
        append_jsonl(self.heartbeat_path, payload)

    def audit_compilation(self, update_stability: bool = True) -> tuple[bool, dict]:
        audit = self.authoring.audit_landscape_material_compilation(self.landscape, self.terrain_material)
        record = {
            "success": bool(audit.success),
            "landscape_components": int(audit.landscape_component_count),
            "generated_instances": int(audit.generated_material_instance_count),
            "material_resources": int(audit.material_resource_count),
            "finished_resources": int(audit.compilation_finished_resource_count),
            "valid_shader_maps": int(audit.valid_shader_map_resource_count),
            "asset_queue_empty": bool(audit.asset_compilation_queue_empty),
            "shader_queue_empty": bool(audit.shader_compilation_queue_empty),
            "error": str(audit.error),
        }
        ready = (
            record["success"]
            and record["material_resources"] > 0
            and record["finished_resources"] == record["material_resources"]
            and record["valid_shader_maps"] == record["material_resources"]
            and record["asset_queue_empty"]
            and record["shader_queue_empty"]
        )
        if update_stability:
            self.stable_ready_polls = self.stable_ready_polls + 1 if ready else 0
        return ready, record

    def begin_measurement(self) -> None:
        world = unreal.EditorLevelLibrary.get_editor_world()
        unreal.SystemLibrary.execute_console_command(world, f"csvprofile startfile={CSV_FILENAME}")
        unreal.SystemLibrary.execute_console_command(world, "csvprofile start")
        self.csv_started = True
        self.measurement_started = time.monotonic()
        self.phase = "measurement"
        self.phase_started = self.measurement_started
        self.next_audit_at = self.measurement_started
        self.heartbeat("measurement_started")

    def stop_measurement(self) -> None:
        if self.csv_started and not self.csv_stopped:
            unreal.SystemLibrary.execute_console_command(unreal.EditorLevelLibrary.get_editor_world(), "csvprofile stop")
            self.csv_stopped = True
        self.phase = "csv_flush"
        self.phase_started = time.monotonic()
        self.heartbeat("measurement_complete", frame_sample_count=len(self.frame_samples))

    def capture(self, spec: dict) -> None:
        world = unreal.EditorLevelLibrary.get_editor_world()
        width = int(self.contract["capture"]["width"])
        height = int(self.contract["capture"]["height"])
        target = unreal.RenderingLibrary.create_render_target2d(world, width, height, unreal.TextureRenderTargetFormat.RTF_RGBA8)
        actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(), unreal.Rotator())
        if actor is None:
            raise RuntimeError(f"Could not create SceneCapture2D for {spec['id']}")
        try:
            component = actor.capture_component2d
            component.set_editor_property("texture_target", target)
            component.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
            component.set_editor_property("capture_every_frame", False)
            component.set_editor_property("capture_on_movement", False)
            component.set_editor_property("fov_angle", float(spec["fov_degrees"]))
            actor.set_actor_location(unreal.Vector(*spec["location_cm"]), False, False)
            rotation = spec["rotation_degrees"]
            actor.set_actor_rotation(unreal.Rotator(pitch=rotation["pitch"], yaw=rotation["yaw"], roll=rotation["roll"]), False)
            component.capture_scene()
            output = self.capture_root / f"{spec['id']}.png"
            unreal.RenderingLibrary.export_render_target(world, target, str(self.capture_root), output.name)
            if not output.is_file() or png_dimensions(output) != (width, height):
                raise RuntimeError(f"Capture failed: {output}")
            self.captures.append({"id": spec["id"], "path": str(output), "bytes": output.stat().st_size, "sha256": sha256_file(output)})
            self.heartbeat("capture_complete", camera_id=spec["id"], bytes=output.stat().st_size)
        finally:
            unreal.EditorLevelLibrary.destroy_actor(actor)

    def finish(self, classification: str, error: str | None = None) -> None:
        if self.finished:
            return
        self.finished = True
        if self.callback is not None:
            unreal.unregister_slate_post_tick_callback(self.callback)
            self.callback = None
        if self.csv_started and not self.csv_stopped:
            try:
                unreal.SystemLibrary.execute_console_command(unreal.EditorLevelLibrary.get_editor_world(), "csvprofile stop")
                self.csv_stopped = True
            except Exception:
                pass
        if self.frame_samples:
            with self.frame_csv.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.writer(stream)
                writer.writerow(["tick", "elapsed_seconds", "frame_ms"])
                writer.writerows(self.frame_samples)
        times = [row[2] for row in self.frame_samples]
        times_sorted = sorted(times)
        p95 = times_sorted[int(len(times_sorted) * 0.95)] if times_sorted else 0.0
        map_after = sha256_file(MAP_FILE)
        payload = {
            "schema": "skyguard.m01-visible-environment-stage07b-recovery01.visual-proof01-recovery02-receipt.v1",
            "classification": classification,
            "error": error,
            "sample_count": len(times),
            "mean_frame_ms": (sum(times) / len(times)) if times else 0.0,
            "p95_frame_ms": p95,
            "max_frame_ms": max(times) if times else 0.0,
            "frames_over_50_ms": sum(1 for item in times if item > 50.0),
            "captures": self.captures,
            "map_before_sha256": self.map_hash_before,
            "map_after_sha256": map_after,
            "world_saved": False,
        }
        if map_after != self.map_hash_before:
            payload["classification"] = "FAILED_WITH_EVIDENCE"
            payload["error"] = "Proof mutated the Recovery01 map"
        elif classification.startswith("PASSED") or classification.startswith("PASS_"):
            if payload["p95_frame_ms"] > 16.7 or payload["max_frame_ms"] > 33.3 or payload["frames_over_50_ms"] != 0 or len(self.captures) != 8:
                payload["classification"] = "FAILED_WITH_EVIDENCE"
                payload["error"] = payload["error"] or "Automatic performance or capture-count gate failed"
            else:
                payload["classification"] = "PASSED_AUTOMATIC_AWAITING_HUMAN_VISUAL_REVIEW"
        write_json(self.capture_receipt, payload)
        self.heartbeat("terminal", classification=payload["classification"], error=payload.get("error"))
        unreal.SystemLibrary.quit_editor()

    def tick(self, delta_time: float) -> None:
        try:
            self.tick_count += 1
            now = time.monotonic()
            if now - self.started > float(self.contract["runtime"]["maximum_seconds"]):
                raise TimeoutError("Mapped visual proof exceeded its native timeout")
            if self.phase == "shader_readiness":
                if now < self.next_audit_at:
                    return
                ready, audit = self.audit_compilation(update_stability=True)
                self.heartbeat("shader_readiness_poll", stable_ready_polls=self.stable_ready_polls, audit=audit)
                self.next_audit_at = now + 0.5
                if ready and self.stable_ready_polls >= int(self.contract["runtime"]["stable_shader_polls"]):
                    self.phase = "warmup"
                    self.phase_started = now
                    self.heartbeat("shader_ready_two_stable_polls", audit=audit)
                return
            if self.phase == "warmup":
                if now >= self.next_audit_at:
                    ready, audit = self.audit_compilation(update_stability=False)
                    self.next_audit_at = now + 0.5
                    if not ready:
                        self.phase = "shader_readiness"
                        self.stable_ready_polls = 0
                        self.heartbeat("compilation_resumed_warmup_reset", audit=audit)
                        return
                if now - self.phase_started >= float(self.contract["runtime"]["warmup_seconds"]):
                    self.begin_measurement()
                return
            if self.phase == "measurement":
                self.frame_samples.append((self.tick_count, now - self.measurement_started, float(delta_time) * 1000.0))
                if now >= self.next_audit_at:
                    ready, audit = self.audit_compilation(update_stability=False)
                    self.next_audit_at = now + 0.5
                    if not ready:
                        raise RuntimeError("Compilation resumed during measured interval")
                if now - self.measurement_started >= float(self.contract["runtime"]["measurement_seconds"]):
                    if len(self.frame_samples) < int(self.contract["runtime"]["minimum_frame_samples"]):
                        raise RuntimeError("Thirty-second measurement produced fewer than 900 samples")
                    self.stop_measurement()
                return
            if self.phase == "csv_flush":
                csv_path = ISOLATED / "Saved/Profiling/CSV" / CSV_FILENAME
                if now >= self.next_audit_at:
                    size = csv_path.stat().st_size if csv_path.is_file() else -1
                    if size >= 1024 and size == self.csv_last_size:
                        self.csv_stable_polls += 1
                    else:
                        self.csv_stable_polls = 0
                    self.csv_last_size = size
                    self.next_audit_at = now + 0.5
                    self.heartbeat("csv_flush_poll", csv_bytes=size, stable_polls=self.csv_stable_polls)
                if self.csv_stable_polls >= 2:
                    self.phase = "capture"
                    self.phase_started = now
                    self.heartbeat("capture_phase_started")
                elif now - self.phase_started > 10.0:
                    # CSV profile is diagnostic; do not fail the visual proof if the file is absent.
                    self.phase = "capture"
                    self.heartbeat("csv_flush_skipped")
                return
            if self.phase == "capture":
                if self.capture_gap_ticks > 0:
                    self.capture_gap_ticks -= 1
                    return
                if self.capture_index < len(self.specs):
                    self.capture(self.specs[self.capture_index])
                    self.capture_index += 1
                    self.capture_gap_ticks = 2
                    return
                if len(self.captures) != 8:
                    raise RuntimeError("Exactly eight governed captures were not produced")
                self.finish("PASSED_AUTOMATIC_AWAITING_HUMAN_VISUAL_REVIEW")
        except Exception as exc:
            self.finish("FAILED_WITH_EVIDENCE", f"{type(exc).__name__}: {exc}")


def main() -> None:
    global _STATE
    startup = LAUNCHER / "executor_startup_receipt.json"
    write_json_atomic(startup, {
        "schema": "skyguard.executor-startup-receipt.v1",
        "gate": "EXECUTOR_INVOKED",
        "contract_id": CONTRACT_ID,
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    })
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    cameras = json.loads(CAMERAS_PATH.read_text(encoding="utf-8"))
    if contract["contract_id"] != CONTRACT_ID:
        raise RuntimeError("Contract identity mismatch")
    if sha256_file(MAP_FILE) != contract["world"]["map_sha256"]:
        raise RuntimeError("Recovery01 map hash changed before proof")
    authoring = Path(contract["authoring_authority"]["receipt"])
    if sha256_file(authoring) != contract["authoring_authority"]["receipt_sha256"]:
        raise RuntimeError("Authoring receipt hash changed")
    failed = Path(contract["failed_proof_authority"]["path"])
    if sha256_file(failed) != contract["failed_proof_authority"]["sha256"]:
        raise RuntimeError("Failed Recovery01 proof freeze hash changed")
    actors = list(unreal.EditorLevelLibrary.get_all_level_actors())
    governed = [actor for actor in actors if actor.get_actor_label() != "PCGWorldActor0"]
    if len(governed) != int(contract["world"]["expected_governed_actor_count"]):
        raise RuntimeError(f"Governed actor count changed: {len(governed)}")
    landscape = next(actor for actor in actors if actor.get_actor_label() == "M01_A01_Landscape_Production")
    terrain_material = unreal.load_asset(contract["world"]["landscape_material"])
    if terrain_material is None:
        raise RuntimeError("Planting-soil material did not resolve")
    current = landscape.get_editor_property("landscape_material")
    if contract["world"]["landscape_material"].rsplit("/", 1)[-1] not in asset_identity(current):
        raise RuntimeError(f"Landscape material mismatch: {asset_identity(current)}")
    vegetation = [actor for actor in actors if actor.get_actor_label().startswith("M01_STAGE07B_Vegetation_")]
    if len(vegetation) != int(contract["world"]["stage07b_vegetation_count"]):
        raise RuntimeError(f"Stage7B vegetation count changed: {len(vegetation)}")
    if ATTEMPT.exists() and any(ATTEMPT.iterdir()):
        # attempt dir may be created empty by the supervisor before ExecCmds
        proof = ATTEMPT / "proof"
        if proof.exists():
            raise RuntimeError("Proof attempt namespace already populated")
    _STATE = ProofState(contract, cameras, landscape, terrain_material, actors, contract["world"]["map_sha256"])
    _STATE.heartbeat("executor_started")
    _STATE.callback = unreal.register_slate_post_tick_callback(_STATE.tick)


if __name__ == "__main__":
    main()
