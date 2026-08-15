"""One-shot mapped visual proof for the accepted Recovery07 Mission 1 world.

This file is executed inside the full UE 5.8 editor through ``-ExecCmds=py``.
It deliberately returns after registering a Slate tick callback so the normal
editor lifecycle remains alive for shader readiness, warmup, measurement and
capture.  It never saves a package or changes a persisted asset.
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
ISOLATED_ROOT = Path(r"D:\SG52T08_ENV01")
CONTRACT_PATH = ROOT / (
    "Docs/AAA_Review/"
    "TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY07_"
    "MAPPED_VISUAL_PROOF01_RECOVERY03_CONTRACT.json"
)
CAMERAS_PATH = ROOT / (
    "Docs/AAA_Review/"
    "TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY07_"
    "MAPPED_VISUAL_PROOF01_RECOVERY03_CAMERAS.json"
)
CONTRACT_ID = "T08-M01-ENV-AUTH01-RECOVERY07-MAPPED-VISUAL-PROOF01-RECOVERY03"
EXPECTED_MAP = (
    "/Game/ToolchainWave08/Environment/"
    "Lvl_M01_T08_EnvironmentAuthoring01_Recovery07"
)
EXPECTED_MATERIAL = "/Game/Skyguard/Materials/M_Terrain"
CSV_FILENAME = "Recovery07MappedVisualProof01Recovery03.csv"
EXPECTED_STARTUP_RECEIPT = ROOT / (
    "Saved/BuildAttempts/"
    "TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY07_"
    "MAPPED_VISUAL_PROOF01_RECOVERY03/launcher_attempt_01/"
    "executor_startup_receipt.json"
)
_STATE = None


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise RuntimeError(f"JSON root is not an object: {path}")
    return value


def record_path(record: dict) -> Path:
    if "absolute_path" in record:
        return Path(record["absolute_path"])
    if "file" in record:
        return ROOT / record["file"]
    raise RuntimeError(f"Frozen record has no path: {record}")


def verify_record(record: dict) -> None:
    path = record_path(record)
    if not path.is_file():
        raise RuntimeError(f"Missing immutable input: {path}")
    if path.stat().st_size != int(record["bytes"]):
        raise RuntimeError(f"Immutable byte count changed: {path}")
    if sha256_file(path) != record["sha256"]:
        raise RuntimeError(f"Immutable hash changed: {path}")


def parse_switch(name: str) -> str:
    command_line = unreal.SystemLibrary.get_command_line()
    match = re.search(
        rf'(?:^|\s)-{re.escape(name)}=(?:"([^"]+)"|(\S+))',
        command_line,
        re.IGNORECASE,
    )
    if not match:
        raise RuntimeError(f"Missing required -{name} switch")
    return match.group(1) or match.group(2)


def asset_identity(asset) -> str | None:
    return None if asset is None else asset.get_path_name()


def png_dimensions(path: Path) -> tuple[int, int]:
    header = path.read_bytes()[:24]
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError(f"Invalid PNG: {path}")
    return int.from_bytes(header[16:20], "big"), int.from_bytes(
        header[20:24], "big"
    )


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def write_json_atomic(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f"{path.name}.tmp")
    if temporary.exists():
        raise RuntimeError(f"Startup temporary path already exists: {temporary}")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def append_jsonl(path: Path, value: dict) -> None:
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(value, sort_keys=True) + "\n")


def actor_transform_record(actor) -> dict:
    location = actor.get_actor_location()
    rotation = actor.get_actor_rotation()
    scale = actor.get_actor_scale3d()
    return {
        "label": actor.get_actor_label(),
        "class": actor.get_class().get_path_name(),
        "location_cm": [location.x, location.y, location.z],
        "rotation_deg": [rotation.pitch, rotation.yaw, rotation.roll],
        "scale": [scale.x, scale.y, scale.z],
    }


def governed_transform_fingerprint(actors: list) -> tuple[str, list[dict]]:
    records = sorted(
        (
            actor_transform_record(actor)
            for actor in actors
            if actor.get_actor_label().startswith("M01_A01_")
        ),
        key=lambda item: item["label"],
    )
    encoded = json.dumps(records, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest(), records


class ProofState:
    def __init__(
        self,
        contract: dict,
        cameras: dict,
        attempt_root: Path,
        landscape,
        terrain_material,
        actors: list,
        map_hash_before: str,
    ) -> None:
        self.contract = contract
        self.cameras = cameras
        self.attempt_root = attempt_root
        self.proof_root = attempt_root / "proof"
        self.capture_root = self.proof_root / "captures"
        self.heartbeat_path = self.proof_root / "lifecycle_heartbeat.jsonl"
        self.frame_csv = self.proof_root / "frame_samples.csv"
        self.capture_receipt = self.proof_root / "capture_receipt.json"
        self.restoration_receipt = self.proof_root / "restoration_receipt.json"
        self.terminal_receipt = attempt_root / "terminal_receipt.json"
        self.landscape = landscape
        self.terrain_material = terrain_material
        self.actors = actors
        self.map_file = ISOLATED_ROOT / (
            "Content/ToolchainWave08/Environment/"
            "Lvl_M01_T08_EnvironmentAuthoring01_Recovery07.umap"
        )
        self.map_hash_before = map_hash_before
        self.original_material_identity = asset_identity(
            landscape.get_editor_property("landscape_material")
        )
        self.authoring = unreal.SkyguardMission01EnvironmentAuthoringLibrary
        self.callback = None
        self.started = time.monotonic()
        self.phase_started = self.started
        self.phase = "shader_readiness"
        self.next_audit_at = self.started
        self.stable_ready_polls = 0
        self.tick_count = 0
        self.measurement_started = None
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
        self.transform_hash_before, self.transforms_before = (
            governed_transform_fingerprint(actors)
        )

    def heartbeat(self, event: str, **fields) -> None:
        append_jsonl(
            self.heartbeat_path,
            {
                "event": event,
                "phase": self.phase,
                "tick": self.tick_count,
                "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                **fields,
            },
        )

    def audit_compilation(self, update_stability: bool = True) -> tuple[bool, dict]:
        audit = self.authoring.audit_landscape_material_compilation(
            self.landscape, self.terrain_material
        )
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
            and record["landscape_components"] == 16
            and record["generated_instances"] == 16
            and record["material_resources"] == 16
            and record["finished_resources"] == 16
            and record["valid_shader_maps"] == 16
            and record["asset_queue_empty"]
            and record["shader_queue_empty"]
        )
        if update_stability:
            self.stable_ready_polls = self.stable_ready_polls + 1 if ready else 0
        return ready, record

    def begin_measurement(self) -> None:
        world = unreal.EditorLevelLibrary.get_editor_world()
        unreal.SystemLibrary.execute_console_command(
            world, f"csvprofile startfile={CSV_FILENAME}"
        )
        unreal.SystemLibrary.execute_console_command(world, "csvprofile start")
        self.csv_started = True
        self.measurement_started = time.monotonic()
        self.phase = "measurement"
        self.phase_started = self.measurement_started
        self.next_audit_at = self.measurement_started
        self.heartbeat("measurement_started", csv_filename=CSV_FILENAME)

    def stop_measurement(self) -> None:
        if self.csv_started and not self.csv_stopped:
            world = unreal.EditorLevelLibrary.get_editor_world()
            unreal.SystemLibrary.execute_console_command(world, "csvprofile stop")
            self.csv_stopped = True
        self.phase = "csv_flush"
        self.phase_started = time.monotonic()
        self.heartbeat(
            "measurement_complete",
            frame_sample_count=len(self.frame_samples),
            elapsed_seconds=self.phase_started - self.measurement_started,
        )

    def capture(self, spec: dict) -> None:
        world = unreal.EditorLevelLibrary.get_editor_world()
        width = int(self.contract["capture"]["width"])
        height = int(self.contract["capture"]["height"])
        target = unreal.RenderingLibrary.create_render_target2d(
            world,
            width,
            height,
            unreal.TextureRenderTargetFormat.RTF_RGBA8,
        )
        actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.SceneCapture2D, unreal.Vector(), unreal.Rotator()
        )
        if actor is None:
            raise RuntimeError("Could not create transient SceneCapture2D")
        try:
            component = actor.capture_component2d
            component.set_editor_property("texture_target", target)
            component.set_editor_property(
                "capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR
            )
            component.set_editor_property("capture_every_frame", False)
            component.set_editor_property("capture_on_movement", False)
            component.set_editor_property("fov_angle", float(spec["fov_degrees"]))
            actor.set_actor_location(unreal.Vector(*spec["location_cm"]), False, False)
            rotation = spec["rotation_degrees"]
            actor.set_actor_rotation(
                unreal.Rotator(
                    pitch=rotation["pitch"],
                    yaw=rotation["yaw"],
                    roll=rotation["roll"],
                ),
                False,
            )
            component.capture_scene()
            output = self.capture_root / f"{spec['id']}.png"
            unreal.RenderingLibrary.export_render_target(
                world, target, str(self.capture_root), output.name
            )
            if not output.is_file() or output.stat().st_size < 1024:
                raise RuntimeError(f"Capture is absent or implausibly small: {output}")
            if png_dimensions(output) != (width, height):
                raise RuntimeError(f"Wrong PNG dimensions: {output}")
            self.captures.append(
                {
                    "id": spec["id"],
                    "role": spec["role"],
                    "file": str(output),
                    "bytes": output.stat().st_size,
                    "sha256": sha256_file(output),
                    "location_cm": spec["location_cm"],
                    "rotation_degrees": rotation,
                    "fov_degrees": spec["fov_degrees"],
                    "tick": self.tick_count,
                }
            )
            self.heartbeat("capture_complete", camera_id=spec["id"])
        finally:
            unreal.EditorLevelLibrary.destroy_actor(actor)

    def write_frame_samples(self) -> None:
        with self.frame_csv.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(["tick", "elapsed_seconds", "frame_ms"])
            writer.writerows(self.frame_samples)

    def finish(self, gate: str, error: str | None = None) -> None:
        if self.finished:
            return
        self.finished = True
        if self.callback is not None:
            unreal.unregister_slate_post_tick_callback(self.callback)
            self.callback = None
        if self.csv_started and not self.csv_stopped:
            try:
                unreal.SystemLibrary.execute_console_command(
                    unreal.EditorLevelLibrary.get_editor_world(), "csvprofile stop"
                )
                self.csv_stopped = True
            except Exception as exc:
                gate = "FAILED_WITH_EVIDENCE"
                error = f"{error}; CSV stop failed: {exc}" if error else str(exc)
        self.write_frame_samples()
        final_material_identity = asset_identity(
            self.landscape.get_editor_property("landscape_material")
        )
        transform_hash_after, transforms_after = governed_transform_fingerprint(
            self.actors
        )
        map_hash_after = sha256_file(self.map_file)
        restoration_passed = (
            final_material_identity == self.original_material_identity
            and self.original_material_identity == asset_identity(self.terrain_material)
            and transform_hash_after == self.transform_hash_before
            and map_hash_after == self.map_hash_before
        )
        restoration = {
            "schema": "skyguard.t08.m01.recovery07-mapped-proof01-restoration.v1",
            "gate": (
                "PASS_NO_MUTATION_REQUIRED" if restoration_passed else "FAILED_WITH_EVIDENCE"
            ),
            "action": "NO_MUTATION_REQUIRED",
            "original_material_identity": self.original_material_identity,
            "final_material_identity": final_material_identity,
            "material_identity_matches": (
                final_material_identity == self.original_material_identity
            ),
            "governed_transform_sha256_before": self.transform_hash_before,
            "governed_transform_sha256_after": transform_hash_after,
            "governed_transforms_unchanged": (
                transform_hash_after == self.transform_hash_before
            ),
            "map_sha256_before": self.map_hash_before,
            "map_sha256_after": map_hash_after,
            "map_unchanged": map_hash_after == self.map_hash_before,
            "world_saved": False,
            "asset_mutation_performed": False,
            "transforms_before": self.transforms_before,
            "transforms_after": transforms_after,
        }
        write_json(self.restoration_receipt, restoration)
        if not restoration_passed:
            gate = "FAILED_WITH_EVIDENCE"
            error = (
                f"{error}; restoration/no-mutation verification failed"
                if error
                else "restoration/no-mutation verification failed"
            )
        capture_receipt = {
            "schema": "skyguard.t08.m01.recovery07-mapped-proof01-capture.v1",
            "gate": gate,
            "capture_count": len(self.captures),
            "captures": self.captures,
            "frame_sample_count": len(self.frame_samples),
            "csv_filename": CSV_FILENAME,
            "measurement_seconds": (
                0.0
                if self.measurement_started is None
                else max(0.0, time.monotonic() - self.measurement_started)
            ),
            "world_saved": False,
        }
        write_json(self.capture_receipt, capture_receipt)
        terminal = {
            "schema": "skyguard.t08.m01.recovery07-mapped-proof01-terminal.v1",
            "contract_id": CONTRACT_ID,
            "gate": gate,
            "passed": gate == "PASS_CAPTURE_COMPLETE_PENDING_OFFLINE_ADJUDICATION",
            "error": error,
            "rhi": self.authoring.get_active_rhi_and_feature_level().strip().upper(),
            "map": EXPECTED_MAP,
            "landscape_label": "M01_A01_Landscape_Production",
            "terrain_material": self.original_material_identity,
            "stable_shader_polls": self.stable_ready_polls,
            "frame_sample_count": len(self.frame_samples),
            "capture_count": len(self.captures),
            "csv_started": self.csv_started,
            "csv_stopped": self.csv_stopped,
            "restoration_verified": restoration_passed,
            "world_saved": False,
            "asset_imported": False,
            "pcg_generated": False,
            "promotion_performed": False,
            "integration_performed": False,
            "packaging_performed": False,
        }
        write_json(self.terminal_receipt, terminal)
        self.heartbeat("terminal_receipt_written", gate=gate, error=error)
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
                self.heartbeat(
                    "shader_readiness_poll",
                    stable_ready_polls=self.stable_ready_polls,
                    audit=audit,
                )
                self.next_audit_at = now + 0.5
                if ready and self.stable_ready_polls >= 2:
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
                if now - self.phase_started >= float(
                    self.contract["runtime"]["warmup_seconds"]
                ):
                    self.begin_measurement()
                return

            if self.phase == "measurement":
                self.frame_samples.append(
                    (
                        self.tick_count,
                        now - self.measurement_started,
                        float(delta_time) * 1000.0,
                    )
                )
                if now >= self.next_audit_at:
                    ready, audit = self.audit_compilation(update_stability=False)
                    self.next_audit_at = now + 0.5
                    if not ready:
                        self.heartbeat("compilation_resumed_during_measurement", audit=audit)
                        raise RuntimeError("Compilation resumed during measured interval")
                measured = now - self.measurement_started
                if measured >= float(self.contract["runtime"]["measurement_seconds"]):
                    if len(self.frame_samples) < int(
                        self.contract["runtime"]["minimum_frame_samples"]
                    ):
                        raise RuntimeError(
                            "Thirty-second measurement produced fewer than 900 samples"
                        )
                    self.stop_measurement()
                return

            if self.phase == "csv_flush":
                csv_path = ISOLATED_ROOT / "Saved/Profiling/CSV" / CSV_FILENAME
                if now >= self.next_audit_at:
                    size = csv_path.stat().st_size if csv_path.is_file() else -1
                    if size >= 1024 and size == self.csv_last_size:
                        self.csv_stable_polls += 1
                    else:
                        self.csv_stable_polls = 0
                    self.csv_last_size = size
                    self.next_audit_at = now + 0.5
                    self.heartbeat(
                        "csv_flush_poll",
                        csv_file=str(csv_path),
                        csv_bytes=size,
                        stable_polls=self.csv_stable_polls,
                    )
                if self.csv_stable_polls >= 2:
                    self.phase = "capture"
                    self.phase_started = now
                    self.heartbeat("capture_phase_started", csv_bytes=self.csv_last_size)
                elif now - self.phase_started > 10.0:
                    raise RuntimeError("CSV profile did not become stable within ten seconds")
                return

            if self.phase == "capture":
                if self.capture_gap_ticks > 0:
                    self.capture_gap_ticks -= 1
                    return
                if self.capture_index < len(self.specs):
                    spec = self.specs[self.capture_index]
                    self.capture(spec)
                    self.capture_index += 1
                    self.capture_gap_ticks = 2
                    return
                if len(self.captures) != 8:
                    raise RuntimeError("Exactly eight governed captures were not produced")
                self.finish("PASS_CAPTURE_COMPLETE_PENDING_OFFLINE_ADJUDICATION")
        except Exception as exc:
            self.finish("FAILED_WITH_EVIDENCE", f"{type(exc).__name__}: {exc}")


def validate_actor_contract(actors: list, contract: dict) -> tuple[object, object]:
    by_label: dict[str, list] = {}
    for actor in actors:
        by_label.setdefault(actor.get_actor_label(), []).append(actor)
    expected = contract["world"]["expected_labels"]
    for label in expected:
        if len(by_label.get(label, [])) != 1:
            raise RuntimeError(
                f"Expected exactly one governed actor named {label}; "
                f"found {len(by_label.get(label, []))}"
            )
    for prefix, count in contract["world"]["expected_prefix_counts"].items():
        actual = sum(label.startswith(prefix) for label in by_label)
        if actual != int(count):
            raise RuntimeError(f"Actor prefix {prefix}: expected {count}, found {actual}")
    if len(actors) != int(contract["world"]["expected_total_actor_count"]):
        raise RuntimeError(
            f"Expected {contract['world']['expected_total_actor_count']} level actors; "
            f"found {len(actors)}"
        )
    landscape = by_label["M01_A01_Landscape_Production"][0]
    terrain_material = unreal.load_asset(EXPECTED_MATERIAL)
    if terrain_material is None:
        raise RuntimeError("Governed terrain material did not resolve")
    current = landscape.get_editor_property("landscape_material")
    if asset_identity(current) != asset_identity(terrain_material):
        raise RuntimeError(
            f"Landscape material mismatch: {asset_identity(current)} != "
            f"{asset_identity(terrain_material)}"
        )
    return landscape, terrain_material


def main() -> None:
    global _STATE
    startup_receipt = Path(
        parse_switch("SkyguardRecovery07ProofStartupReceipt")
    ).resolve()
    if startup_receipt != EXPECTED_STARTUP_RECEIPT.resolve():
        raise RuntimeError("Executor startup receipt path mismatch")
    if startup_receipt.exists():
        raise RuntimeError("Executor startup receipt already exists")
    write_json_atomic(
        startup_receipt,
        {
            "schema": "skyguard.t08.m01.recovery07-mapped-proof01-executor-startup.v1",
            "gate": "EXECUTOR_INVOKED",
            "contract_id": CONTRACT_ID,
            "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "executor": str(Path(__file__).resolve()),
        },
    )
    contract = read_json(CONTRACT_PATH)
    cameras = read_json(CAMERAS_PATH)
    if contract["contract_id"] != CONTRACT_ID:
        raise RuntimeError("Mapped proof contract identity mismatch")
    if parse_switch("SkyguardRecovery07ProofContract") != CONTRACT_ID:
        raise RuntimeError("Mapped proof command-line authorization mismatch")
    expected_attempt = (ROOT / contract["runtime"]["attempt_relative_path"]).resolve()
    attempt_root = Path(parse_switch("SkyguardRecovery07ProofAttemptRoot")).resolve()
    if attempt_root != expected_attempt:
        raise RuntimeError("Mapped proof attempt root does not match the frozen contract")
    if attempt_root.exists():
        raise RuntimeError("Mapped proof attempt namespace already exists")
    for record in contract["locked_inputs"]:
        verify_record(record)
    map_file = ISOLATED_ROOT / (
        "Content/ToolchainWave08/Environment/"
        "Lvl_M01_T08_EnvironmentAuthoring01_Recovery07.umap"
    )
    map_hash_before = sha256_file(map_file)
    rhi = (
        unreal.SkyguardMission01EnvironmentAuthoringLibrary
        .get_active_rhi_and_feature_level()
        .strip()
        .upper()
    )
    if rhi != "D3D12|SM6":
        raise RuntimeError(f"Mapped proof requires D3D12|SM6; got {rhi}")
    world = unreal.EditorLevelLibrary.get_editor_world()
    world_identity = world.get_path_name()
    if EXPECTED_MAP not in world_identity:
        raise RuntimeError(f"Wrong loaded world: {world_identity}")
    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    landscape, terrain_material = validate_actor_contract(actors, contract)
    attempt_root.mkdir(parents=True, exist_ok=False)
    (attempt_root / "proof" / "captures").mkdir(parents=True, exist_ok=False)
    _STATE = ProofState(
        contract,
        cameras,
        attempt_root,
        landscape,
        terrain_material,
        actors,
        map_hash_before,
    )
    _STATE.heartbeat(
        "preflight_complete",
        rhi=rhi,
        world=world_identity,
        actor_count=len(actors),
        material=asset_identity(terrain_material),
    )
    _STATE.callback = unreal.register_slate_post_tick_callback(_STATE.tick)


if __name__ == "__main__":
    main()
