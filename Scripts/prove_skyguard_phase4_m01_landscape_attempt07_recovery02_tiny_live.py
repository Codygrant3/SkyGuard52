"""Deferred editor-tick proof for Attempt07 Recovery02 Landscape diagnostics."""

from __future__ import annotations

import hashlib
import json
import sys
import time
import traceback
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
sys.path.insert(0, str(ROOT / "Scripts"))
import prove_skyguard_phase4_m01_landscape_attempt07_tiny_live as proof_base
from phase4_m01_landscape_attempt06_contract import load_attempt06_contract


CONTRACT_PATH = (
    ROOT
    / "Docs/AAA_Review/"
    "PHASE4_M01_LANDSCAPE_VISIBLE_ATTEMPT07_RECOVERY02_CONTRACT.json"
)
CONTRACT_ID = "P4.5-M01-LANDSCAPE-VISIBLE-007-RECOVERY-02"
_STATE = None


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def visible_audit_dict(audit) -> dict:
    return {
        "success": bool(audit.success),
        "landscape_component_count": int(audit.landscape_component_count),
        "visible_component_count": int(audit.visible_component_count),
        "registered_component_count": int(audit.registered_component_count),
        "render_state_created_component_count": int(
            audit.render_state_created_component_count
        ),
        "generated_material_instance_count": int(
            audit.generated_material_instance_ready_component_count
        ),
        "material_parent_match_count": int(
            audit.governed_material_parent_match_component_count
        ),
        "error": str(audit.error),
    }


def compilation_audit_dict(audit) -> dict:
    return {
        "success": bool(audit.success),
        "landscape_component_count": int(audit.landscape_component_count),
        "generated_material_instance_count": int(
            audit.generated_material_instance_count
        ),
        "material_resource_count": int(audit.material_resource_count),
        "compilation_finished_resource_count": int(
            audit.compilation_finished_resource_count
        ),
        "valid_shader_map_resource_count": int(
            audit.valid_shader_map_resource_count
        ),
        "asset_compilation_queue_empty": bool(
            audit.asset_compilation_queue_empty
        ),
        "shader_compilation_queue_empty": bool(
            audit.shader_compilation_queue_empty
        ),
        "error": str(audit.error),
    }


def compilation_ready(audit: dict) -> bool:
    return (
        audit["success"]
        and audit["landscape_component_count"] == 16
        and audit["generated_material_instance_count"] == 16
        and audit["material_resource_count"] == 16
        and audit["compilation_finished_resource_count"] == 16
        and audit["valid_shader_map_resource_count"] == 16
        and audit["asset_compilation_queue_empty"]
        and audit["shader_compilation_queue_empty"]
    )


class Recovery02State:
    def __init__(
        self,
        contract: dict,
        output_root: Path,
        locked_before: dict,
        authoring,
        landscape,
        governed,
        coverage,
        component,
        camera_specs: dict,
    ) -> None:
        self.contract = contract
        self.output_root = output_root
        self.receipt = output_root / "tiny_proof_receipt.json"
        self.locked_before = locked_before
        self.authoring = authoring
        self.landscape = landscape
        self.governed = governed
        self.coverage = coverage
        self.component = component
        self.camera_specs = camera_specs
        self.proof = contract["tiny_live_proof"]
        self.width, self.height = self.proof["resolution"]
        self.captures_root = output_root / "captures"
        self.phase = "WAIT_COVERAGE_COMPILATION"
        self.phase_started = time.monotonic()
        self.started = self.phase_started
        self.tick_count = 0
        self.last_poll_time = 0.0
        self.stable_ready_ticks = 0
        self.poll_records = []
        self.phase_transitions = []
        self.begin_audits = {}
        self.capture_records = []
        self.capture_paths = {}
        self.callback_handle = None
        self.finished = False
        self.in_callback = False
        self.failure = None

    def begin_material(self, label: str, material) -> None:
        audit = visible_audit_dict(
            self.authoring
            .begin_transient_landscape_diagnostic_material_deferred(
                self.landscape, material
            )
        )
        self.begin_audits[label] = audit
        if not (
            audit["success"]
            and audit["landscape_component_count"] == 16
            and audit["visible_component_count"] == 16
            and audit["registered_component_count"] == 16
            and audit["render_state_created_component_count"] == 16
            and audit["generated_material_instance_count"] == 16
            and audit["material_parent_match_count"] == 16
        ):
            raise RuntimeError(
                "Deferred material begin audit failed: "
                + label
                + " "
                + json.dumps(audit)
            )

    def transition(self, phase: str) -> None:
        now = time.monotonic()
        self.phase_transitions.append(
            {
                "from": self.phase,
                "to": phase,
                "tick": self.tick_count,
                "elapsed_seconds": now - self.started,
            }
        )
        self.phase = phase
        self.phase_started = now
        self.stable_ready_ticks = 0

    def current_material(self):
        if self.phase == "WAIT_COVERAGE_COMPILATION":
            return self.coverage
        if self.phase == "WAIT_COMPONENT_COMPILATION":
            return self.component
        if self.phase == "WAIT_GOVERNED_RESTORE_COMPILATION":
            return self.governed
        raise RuntimeError("No material for phase " + self.phase)

    def record_poll(self, delta_time: float) -> dict:
        audit = compilation_audit_dict(
            self.authoring.audit_landscape_material_compilation(
                self.landscape, self.current_material()
            )
        )
        ready = compilation_ready(audit)
        if ready:
            self.stable_ready_ticks += 1
        else:
            self.stable_ready_ticks = 0
        self.poll_records.append(
            {
                "tick": self.tick_count,
                "phase": self.phase,
                "delta_time_seconds": float(delta_time),
                "phase_elapsed_seconds": time.monotonic()
                - self.phase_started,
                "total_elapsed_seconds": time.monotonic() - self.started,
                "stable_ready_ticks": self.stable_ready_ticks,
                "ready": ready,
                "audit": audit,
            }
        )
        return audit

    def ensure_not_timed_out(self) -> None:
        now = time.monotonic()
        if self.tick_count > self.proof["maximum_editor_ticks"]:
            raise TimeoutError("Recovery02 maximum editor ticks exceeded")
        if now - self.started > self.proof["whole_timeout_seconds"]:
            raise TimeoutError("Recovery02 whole proof timeout exceeded")
        if now - self.phase_started > self.proof["phase_timeout_seconds"]:
            raise TimeoutError(
                "Recovery02 phase timeout exceeded: " + self.phase
            )

    def capture_coverage(self) -> None:
        c05 = self.captures_root / "coverage_C05.png"
        c04 = self.captures_root / "coverage_C04.png"
        self.capture_records.append(
            proof_base.capture_one(
                self.authoring,
                self.landscape,
                self.camera_specs["C05_COVERAGE_HIGH"],
                unreal.SkyguardLandscapeCaptureDiagnosticMode
                .LANDSCAPE_COVERAGE,
                c05,
                self.width,
                self.height,
                self.proof["fov_degrees"],
            )
        )
        self.capture_records.append(
            proof_base.capture_one(
                self.authoring,
                self.landscape,
                self.camera_specs["C04_INLAND_CLOSE"],
                unreal.SkyguardLandscapeCaptureDiagnosticMode
                .LANDSCAPE_COVERAGE,
                c04,
                self.width,
                self.height,
                self.proof["fov_degrees"],
            )
        )
        self.capture_paths["coverage_c05"] = c05
        self.capture_paths["coverage_c04"] = c04

    def capture_component(self) -> None:
        c05 = self.captures_root / "component_id_C05.png"
        self.capture_records.append(
            proof_base.capture_one(
                self.authoring,
                self.landscape,
                self.camera_specs["C05_COVERAGE_HIGH"],
                unreal.SkyguardLandscapeCaptureDiagnosticMode
                .COMPONENT_BOUNDARY,
                c05,
                self.width,
                self.height,
                self.proof["fov_degrees"],
            )
        )
        self.capture_paths["component_c05"] = c05

    def tick(self, delta_time: float) -> None:
        if self.finished or self.in_callback:
            return
        self.in_callback = True
        try:
            self.tick_count += 1
            self.ensure_not_timed_out()
            now = time.monotonic()
            if (
                now - self.last_poll_time
                < self.proof["minimum_poll_interval_seconds"]
            ):
                return
            self.last_poll_time = now
            self.record_poll(delta_time)
            required = self.proof["stable_ready_ticks_required"]
            if self.stable_ready_ticks < required:
                return
            if self.phase == "WAIT_COVERAGE_COMPILATION":
                self.capture_coverage()
                self.begin_material("component_id", self.component)
                self.transition("WAIT_COMPONENT_COMPILATION")
            elif self.phase == "WAIT_COMPONENT_COMPILATION":
                self.capture_component()
                self.begin_material("governed_restore", self.governed)
                self.transition("WAIT_GOVERNED_RESTORE_COMPILATION")
            elif self.phase == "WAIT_GOVERNED_RESTORE_COMPILATION":
                self.finish_success()
            else:
                raise RuntimeError("Unexpected Recovery02 phase " + self.phase)
        except Exception as error:
            self.finish_failure(error)
        finally:
            self.in_callback = False

    def common_report(self) -> dict:
        locked_after = {
            name: sha256_file(ROOT / item["file"])
            for name, item in self.contract[
                "locked_production_packages"
            ].items()
        }
        recovery01 = self.contract["immutable_recovery01_failure"]
        recovery01_root = ROOT / recovery01["root"]
        recovery01_after = {
            name: sha256_file(recovery01_root / item["file"])
            for name, item in recovery01["files"].items()
        }
        return {
            "schema": (
                "skyguard.phase4.m01-landscape-visible-"
                "attempt07-recovery02-tiny-proof.v1"
            ),
            "contract_id": self.contract["contract_id"],
            "tick_count": self.tick_count,
            "total_elapsed_seconds": time.monotonic() - self.started,
            "phase_transitions": self.phase_transitions,
            "begin_audits": self.begin_audits,
            "poll_records": self.poll_records,
            "capture_records": self.capture_records,
            "locked_packages_before": self.locked_before,
            "locked_packages_after": locked_after,
            "locked_production_packages_unchanged": (
                locked_after == self.locked_before
            ),
            "recovery01_hashes_after": recovery01_after,
            "recovery01_evidence_unchanged": (
                recovery01_after
                == {
                    name: item["sha256"]
                    for name, item in recovery01["files"].items()
                }
            ),
            "deferred_tick_wait_used": True,
            "same_stack_compilation_finish_called": False,
            "world_saved": False,
            "pcg_generation_invoked": False,
            "full_capture_invoked": False,
            "profile_invoked": False,
            "promotion_allowed": False,
        }

    def finish_success(self) -> None:
        c05 = proof_base.coverage_analysis(
            self.capture_paths["coverage_c05"],
            self.proof["coverage_white_rgb8_minimum"],
        )
        c04 = proof_base.coverage_analysis(
            self.capture_paths["coverage_c04"],
            self.proof["coverage_white_rgb8_minimum"],
        )
        palette = proof_base.palette_analysis(
            self.capture_paths["component_c05"],
            self.proof[
                "component_palette_rgb8_tolerance_per_channel"
            ],
        )
        minimum = self.proof[
            "component_palette_minimum_pixels_per_id"
        ]
        required = self.proof["stable_ready_ticks_required"]
        phases = {
            phase
            for phase in (
                "WAIT_COVERAGE_COMPILATION",
                "WAIT_COMPONENT_COMPILATION",
                "WAIT_GOVERNED_RESTORE_COMPILATION",
            )
            if any(
                item["phase"] == phase
                and item["stable_ready_ticks"] >= required
                for item in self.poll_records
            )
        }
        checks = {
            "all_three_phases_reached_stable_compilation_readiness": (
                len(phases) == 3
            ),
            "no_valid_shader_map_only_acceptance": all(
                not item["ready"]
                or (
                    item["audit"][
                        "compilation_finished_resource_count"
                    ]
                    == 16
                    and item["audit"]["asset_compilation_queue_empty"]
                    and item["audit"]["shader_compilation_queue_empty"]
                )
                for item in self.poll_records
            ),
            "three_captures_exact": len(self.capture_records) == 3,
            "captures_only_after_stable_ready_ticks": all(
                record["stable_ready_ticks"] >= required
                for record in (
                    next(
                        item
                        for item in reversed(self.poll_records)
                        if item["phase"]
                        == "WAIT_COVERAGE_COMPILATION"
                    ),
                    next(
                        item
                        for item in reversed(self.poll_records)
                        if item["phase"]
                        == "WAIT_COMPONENT_COMPILATION"
                    ),
                )
            ),
            "coverage_c05_visible_white": (
                c05["white_fraction"]
                >= self.proof["coverage_c05_minimum_fraction"]
            ),
            "coverage_c04_visible_white": (
                c04["white_fraction"]
                >= self.proof["coverage_c04_minimum_fraction"]
            ),
            "all_16_component_ids_visible": (
                palette["matching_id_count"] == 16
                and all(
                    count >= minimum
                    for count in palette["pixel_counts"].values()
                )
            ),
            "governed_material_restored": (
                self.begin_audits["governed_restore"]["success"]
            ),
        }
        report = self.common_report()
        checks["locked_production_packages_unchanged"] = report[
            "locked_production_packages_unchanged"
        ]
        checks["recovery01_evidence_unchanged"] = report[
            "recovery01_evidence_unchanged"
        ]
        report.update(
            {
                "gate": "PASS" if all(checks.values()) else "FAIL",
                "terminal_phase": self.phase,
                "coverage_c05": c05,
                "coverage_c04": c04,
                "component_palette": palette,
                "checks": checks,
                "error": None,
            }
        )
        self.finish(report)

    def finish_failure(self, error: Exception) -> None:
        restore_error = None
        if "governed_restore" not in self.begin_audits:
            try:
                self.begin_material("governed_restore", self.governed)
            except Exception as restore:
                restore_error = repr(restore)
        report = self.common_report()
        report.update(
            {
                "gate": "FAIL",
                "terminal_phase": self.phase,
                "checks": {
                    "bounded_wait_completed": False,
                    "capture_blocked_until_full_compilation_readiness": (
                        len(self.capture_records) in (0, 2)
                    ),
                    "valid_shader_maps_alone_not_accepted": True,
                    "governed_restore_begin_succeeded": (
                        self.begin_audits.get(
                            "governed_restore", {}
                        ).get("success", False)
                    ),
                },
                "error": repr(error),
                "traceback": traceback.format_exc(),
                "restore_error": restore_error,
            }
        )
        self.finish(report)

    def finish(self, report: dict) -> None:
        if self.finished:
            return
        self.finished = True
        self.receipt.parent.mkdir(parents=True, exist_ok=True)
        self.receipt.write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
        if self.callback_handle is not None:
            unreal.unregister_slate_post_tick_callback(
                self.callback_handle
            )
            self.callback_handle = None
        unreal.log(
            "[SkyguardAttempt07Recovery02TinyProof] "
            + json.dumps(
                {
                    "gate": report["gate"],
                    "tick_count": report["tick_count"],
                    "elapsed_seconds": report["total_elapsed_seconds"],
                    "error": report.get("error"),
                }
            )
        )
        unreal.EditorPythonScripting.set_keep_python_script_alive(False)


def main() -> None:
    global _STATE
    contract = json.loads(
        CONTRACT_PATH.read_text(encoding="utf-8-sig")
    )
    if contract["contract_id"] != CONTRACT_ID:
        raise RuntimeError("Attempt07 Recovery02 contract ID mismatch")
    output_root = Path(
        proof_base.parse_switch("SkyguardAttempt07Recovery02ProofRoot")
    )
    if (
        (output_root / "tiny_proof_receipt.json").exists()
        or (output_root / "captures").exists()
    ):
        raise RuntimeError(
            "Attempt07 Recovery02 proof artifacts already exist"
        )

    recovery01 = contract["immutable_recovery01_failure"]
    recovery01_root = ROOT / recovery01["root"]
    for name, item in recovery01["files"].items():
        path = recovery01_root / item["file"]
        if (
            not path.is_file()
            or path.stat().st_size != item["bytes"]
            or sha256_file(path) != item["sha256"]
        ):
            raise RuntimeError(
                "Recovery01 immutable evidence changed: " + name
            )

    locked_before = {}
    for name, item in contract["locked_production_packages"].items():
        path = ROOT / item["file"]
        digest = sha256_file(path)
        if digest != item["sha256"]:
            raise RuntimeError("Locked package hash failed: " + name)
        locked_before[name] = digest

    authoring = unreal.SkyguardMission01EnvironmentAuthoringLibrary
    rhi = authoring.get_active_rhi_and_feature_level().strip().upper()
    if rhi != contract["tiny_live_proof"]["rhi_required"]:
        raise RuntimeError("Recovery02 requires D3D12|SM6: " + rhi)
    effective = load_attempt06_contract()
    if not unreal.EditorLevelLibrary.load_level(
        effective["candidate"]["immutable_map"]
    ):
        raise RuntimeError("Could not load Attempt06 candidate map read-only")
    landscape = proof_base.find_landscape(effective)
    governed = unreal.load_asset(
        effective["candidate"]["landscape_material"]
    )
    materials = contract["recovery01_diagnostic_materials"]
    coverage = unreal.load_asset(materials["coverage_material"]["asset"])
    component = unreal.load_asset(
        materials["component_id_material"]["asset"]
    )
    if not governed or not coverage or not component:
        raise RuntimeError("Recovery02 material set is incomplete")

    specs = {
        item["id"]: item for item in effective["capture"]["cameras"]
    }
    output_root.mkdir(parents=True, exist_ok=True)
    _STATE = Recovery02State(
        contract,
        output_root,
        locked_before,
        authoring,
        landscape,
        governed,
        coverage,
        component,
        specs,
    )
    _STATE.begin_material("coverage", coverage)
    unreal.EditorPythonScripting.set_keep_python_script_alive(True)
    _STATE.callback_handle = unreal.register_slate_post_tick_callback(
        _STATE.tick
    )


if __name__ == "__main__":
    main()
