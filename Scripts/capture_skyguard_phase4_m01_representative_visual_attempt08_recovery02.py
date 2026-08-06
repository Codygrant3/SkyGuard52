"""One-shot, read-only Recovery02 representative Mission 1 Unreal proof."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import time
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
CONTRACT_PATH = ROOT / "Docs/AAA_Review/PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY02_CONTRACT.json"
CAMERAS_PATH = ROOT / "Docs/AAA_Review/PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_CAMERAS.json"
CONTRACT_ID = "P4.6-M01-REPRESENTATIVE-VISUAL-008-RECOVERY-02"
_STATE = None


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def path_for(record: dict) -> Path:
    return Path(record["absolute_file"]) if "absolute_file" in record else ROOT / record["file"]


def verify_record(record: dict) -> None:
    path = path_for(record)
    if not path.is_file():
        raise RuntimeError(f"Missing immutable source: {path}")
    if path.stat().st_size != record["bytes"]:
        raise RuntimeError(f"Immutable byte count changed: {path}")
    if sha256_file(path) != record["sha256"]:
        raise RuntimeError(f"Immutable hash changed: {path}")


def verify_locked_sources(contract: dict) -> None:
    for section in (
        "terminal_recovery01_authority",
        "engine_authority",
        "locked_assets",
        "inherited_design_authority",
    ):
        for record in contract[section].values():
            verify_record(record)


def parse_switch(name: str) -> str:
    line = unreal.SystemLibrary.get_command_line()
    match = re.search(rf'(?:^|\s)-{re.escape(name)}=(?:"([^"]+)"|(\S+))', line, re.I)
    if not match:
        raise RuntimeError(f"Missing required -{name} switch")
    return match.group(1) or match.group(2)


def asset_identity(asset) -> str | None:
    return None if asset is None else asset.get_path_name()


def png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()[:24]
    if len(data) != 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError(f"Invalid PNG: {path}")
    return int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")


class Recovery02State:
    def __init__(self, contract: dict, cameras: dict, proof_root: Path):
        self.contract = contract
        self.cameras = cameras
        self.proof_root = proof_root
        self.capture_root = proof_root / "captures"
        self.receipt_path = proof_root / "capture_receipt.json"
        self.restoration_path = proof_root / "restoration_receipt.json"
        self.frame_csv = proof_root / "frame_samples.csv"
        self.authoring = unreal.SkyguardMission01EnvironmentAuthoringLibrary
        self.callback = None
        self.landscape = None
        self.original_material = None
        self.bound_material = None
        self.original_material_identity = None
        self.binding_started = False
        self.restoration_verified = False
        self.started = time.monotonic()
        self.ready_at = None
        self.measurement_started = None
        self.stable_ready = 0
        self.tick_count = 0
        self.capture_index = 0
        self.gap_ticks = 0
        self.captures: list[dict] = []
        self.frame_samples: list[tuple[int, float]] = []
        self.specs = cameras["cameras"] + cameras["temporal_route_samples"]
        self.finished = False

    def bind_transient_material(self) -> None:
        self.original_material = self.landscape.get_editor_property("landscape_material")
        self.original_material_identity = asset_identity(self.original_material)
        self.bound_material = unreal.load_asset(
            self.contract["locked_assets"]["validation_material"]["asset"]
        )
        if self.bound_material is None:
            raise RuntimeError("Validation material did not resolve")
        audit = self.authoring.begin_transient_landscape_diagnostic_material_deferred(
            self.landscape, self.bound_material
        )
        self.binding_started = True
        current = self.landscape.get_editor_property("landscape_material")
        if current is None or asset_identity(current) != asset_identity(self.bound_material):
            raise RuntimeError("Transient material is not non-null and exact before polling")
        if int(audit.landscape_component_count) != 16:
            raise RuntimeError("Transient binding did not expose sixteen Landscape components")

    def compilation_ready(self) -> bool:
        audit = self.authoring.audit_landscape_material_compilation(
            self.landscape, self.bound_material
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
        actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.SceneCapture2D, unreal.Vector(), unreal.Rotator()
        )
        if actor is None:
            raise RuntimeError("Could not create transient SceneCapture2D")
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
                    pitch=rotation["pitch"], yaw=rotation["yaw"], roll=rotation["roll"]
                ),
                False,
            )
            component.capture_scene()
            output = self.capture_root / f"{spec['id']}.png"
            unreal.RenderingLibrary.export_render_target(
                world, target, str(self.capture_root), output.name
            )
            if not output.is_file() or output.stat().st_size == 0:
                raise RuntimeError(f"Missing capture: {output}")
            if list(png_dimensions(output)) != [2560, 1440]:
                raise RuntimeError(f"Wrong PNG dimensions: {output}")
            self.captures.append({
                "id": spec["id"],
                "path": str(output),
                "bytes": output.stat().st_size,
                "sha256": sha256_file(output),
                "location_cm": spec["location_cm"],
                "rotation_degrees": rotation,
                "tick": self.tick_count,
            })
        finally:
            unreal.EditorLevelLibrary.destroy_actor(actor)

    def restore_original_material(self) -> dict:
        result = {
            "attempted": self.binding_started,
            "original_material_identity": self.original_material_identity,
            "bound_material_identity": asset_identity(self.bound_material),
            "restored_material_identity": None,
            "property_identity_matches_original": False,
            "world_saved": False,
            "gate": "FAIL_RESTORATION_NOT_ATTEMPTED",
        }
        if self.binding_started and self.landscape is not None:
            self.landscape.set_editor_property("landscape_material", self.original_material)
            restored = self.landscape.get_editor_property("landscape_material")
            result["restored_material_identity"] = asset_identity(restored)
            result["property_identity_matches_original"] = (
                result["restored_material_identity"] == self.original_material_identity
            )
            result["gate"] = (
                "PASS_RESTORED_IN_MEMORY_NO_SAVE"
                if result["property_identity_matches_original"]
                else "FAIL_RESTORATION_IDENTITY_MISMATCH"
            )
            self.restoration_verified = result["property_identity_matches_original"]
        self.restoration_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        return result

    def finish(self, gate: str, error: str | None = None) -> None:
        if self.finished:
            return
        self.finished = True
        try:
            if self.callback is not None:
                unreal.unregister_slate_post_tick_callback(self.callback)
                self.callback = None
        finally:
            restoration = self.restore_original_material()
        if not restoration["property_identity_matches_original"]:
            gate = "FAILED_WITH_EVIDENCE"
            error = f"{error + '; ' if error else ''}material restoration verification failed"
        report = {
            "schema": "skyguard.phase4.m01-representative-visual-attempt08-recovery02-capture.v1",
            "contract_id": CONTRACT_ID,
            "gate": gate,
            "error": error,
            "rhi": self.authoring.get_active_rhi_and_feature_level().strip().upper(),
            "deferred_tick_wait_used": True,
            "stable_ready_polls": self.stable_ready,
            "tick_count": self.tick_count,
            "captures": self.captures,
            "original_material_identity": self.original_material_identity,
            "bound_material_identity": asset_identity(self.bound_material),
            "restoration_verified": self.restoration_verified,
            "restoration_in_finally": True,
            "world_saved": False,
            "asset_mutation_invoked": False,
            "pcg_generation_invoked": False,
            "network_acquisition_invoked": False,
            "promotion_invoked": False,
            "integration_invoked": False,
            "packaging_invoked": False,
        }
        self.receipt_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        with self.frame_csv.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(["tick", "frame_ms"])
            writer.writerows(self.frame_samples)
        unreal.SystemLibrary.quit_editor()

    def tick(self, delta_time: float) -> None:
        try:
            self.tick_count += 1
            if time.monotonic() - self.started > self.contract["execution"]["maximum_process_seconds"]:
                raise TimeoutError("Recovery02 bounded process timeout")
            ready = self.compilation_ready()
            if self.measurement_started is not None and not ready:
                raise RuntimeError("Compilation resumed during measured interval")
            if not ready:
                return
            if self.ready_at is None:
                self.ready_at = time.monotonic()
            if time.monotonic() - self.ready_at < self.contract["performance_contract"]["warmup_seconds_after_ready"]:
                return
            if self.measurement_started is None:
                self.measurement_started = time.monotonic()
            self.frame_samples.append((self.tick_count, float(delta_time) * 1000.0))
            if self.gap_ticks:
                self.gap_ticks -= 1
                return
            if self.capture_index < len(self.specs):
                spec = self.specs[self.capture_index]
                self.capture(spec)
                self.capture_index += 1
                self.gap_ticks = int(spec.get("minimum_tick_gap_from_previous_capture", 1))
                return
            if len(self.captures) != 8:
                raise RuntimeError("Eight governed captures were not produced")
            performance = self.contract["performance_contract"]
            if time.monotonic() - self.measurement_started < performance["measured_seconds"]:
                return
            if len(self.frame_samples) < performance["minimum_tick_samples"]:
                return
            self.finish("PASS_CAPTURE_COMPLETE_PENDING_OFFLINE_ACCEPTANCE")
        except Exception as exc:
            self.finish("FAILED_WITH_EVIDENCE", f"{type(exc).__name__}: {exc}")


def main() -> None:
    global _STATE
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8-sig"))
    cameras = json.loads(CAMERAS_PATH.read_text(encoding="utf-8-sig"))
    if contract["contract_id"] != CONTRACT_ID:
        raise RuntimeError("Recovery02 contract identity failed")
    attempt_root = Path(parse_switch("SkyguardRecovery02AttemptRoot")).resolve()
    proof_root = Path(parse_switch("SkyguardRecovery02ProofRoot")).resolve()
    expected_attempt = (ROOT / contract["execution"]["attempt_root"]).resolve()
    expected_proof = (ROOT / contract["execution"]["proof_root"]).resolve()
    if attempt_root != expected_attempt or proof_root != expected_proof:
        raise RuntimeError("Recovery02 namespace switches do not match the contract")
    if attempt_root.exists() or proof_root.exists():
        raise RuntimeError("Recovery02 namespace already exists")
    verify_locked_sources(contract)
    rhi = unreal.SkyguardMission01EnvironmentAuthoringLibrary.get_active_rhi_and_feature_level().strip().upper()
    if rhi != "D3D12|SM6":
        raise RuntimeError(f"Recovery02 requires D3D12|SM6; got {rhi}")
    if not unreal.EditorLevelLibrary.load_level(contract["locked_assets"]["production_map"]["asset"]):
        raise RuntimeError("Could not load immutable Mission 1 production map")
    matches = [
        actor for actor in unreal.EditorLevelLibrary.get_all_level_actors()
        if actor.get_class().get_name() in {"Landscape", "LandscapeStreamingProxy"}
        and actor.get_actor_label() == contract["landscape_contract"]["actor_label"]
    ]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one governed Landscape; found {len(matches)}")
    if unreal.load_asset(contract["locked_assets"]["validation_material"]["asset"]) is None:
        raise RuntimeError("Validation material did not resolve before namespace creation")
    attempt_root.mkdir(parents=True, exist_ok=False)
    proof_root.mkdir(parents=False, exist_ok=False)
    (proof_root / "captures").mkdir(parents=False, exist_ok=False)
    _STATE = Recovery02State(contract, cameras, proof_root)
    _STATE.landscape = matches[0]
    try:
        _STATE.bind_transient_material()
        _STATE.callback = unreal.register_slate_post_tick_callback(_STATE.tick)
    except Exception:
        _STATE.finish("FAILED_WITH_EVIDENCE", "Pre-poll transient binding failed")
        raise


if __name__ == "__main__":
    main()
