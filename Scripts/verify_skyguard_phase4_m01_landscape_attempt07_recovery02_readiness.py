"""Offline, fail-closed readiness for Attempt07 Recovery02."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT_PATH = (
    ROOT
    / "Docs/AAA_Review/"
    "PHASE4_M01_LANDSCAPE_VISIBLE_ATTEMPT07_RECOVERY02_CONTRACT.json"
)
OUTPUT = (
    ROOT
    / "Saved/Reports/"
    "PHASE4_M01_LANDSCAPE_VISIBLE_ATTEMPT07_RECOVERY02_READINESS.json"
)
CONTRACT_ID = "P4.5-M01-LANDSCAPE-VISIBLE-007-RECOVERY-02"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def exact_files(root: Path, items: dict) -> bool:
    return all(
        (root / item["file"]).is_file()
        and sha256_file(root / item["file"]) == item["sha256"]
        and (
            "bytes" not in item
            or (root / item["file"]).stat().st_size == item["bytes"]
        )
        for item in items.values()
    )


def main() -> int:
    contract = json.loads(
        CONTRACT_PATH.read_text(encoding="utf-8-sig")
    )
    if contract["contract_id"] != CONTRACT_ID:
        raise RuntimeError("Recovery02 contract ID mismatch")

    recovery01 = contract["immutable_recovery01_failure"]
    recovery01_root = ROOT / recovery01["root"]
    recovery01_manifest = json.loads(
        (recovery01_root / "run_manifest.json").read_text(
            encoding="utf-8-sig"
        )
    )
    proof_log = (
        recovery01_root / recovery01["files"]["proof_engine_log"]["file"]
    ).read_text(encoding="utf-8", errors="replace")

    implementation_paths = {
        name: ROOT / item["file"]
        for name, item in contract["implementation_files"].items()
    }
    sources = {
        name: path.read_text(encoding="utf-8")
        for name, path in implementation_paths.items()
        if path.suffix in {".h", ".cpp", ".py", ".ps1"}
    }
    native_header = sources["native_header"]
    native_cpp = sources["native_implementation"]
    proof = sources["recovery02_tiny_proof"]
    supervisor = sources["recovery02_supervisor"]
    launcher = sources["recovery02_launcher"]
    deferred_native = native_cpp.split(
        "BeginTransientLandscapeDiagnosticMaterialDeferred(", 1
    )[1].split(
        "SetTransientLandscapeDiagnosticMaterial(", 1
    )[0]
    callback_tick = proof.split(
        "def tick(self, delta_time: float)", 1
    )[1].split("def common_report", 1)[0]
    finish_success = proof.split("def finish_success(self)", 1)[1].split(
        "def finish_failure", 1
    )[0]

    module_spec = contract["compiled_module_before_recovery02"]
    module = ROOT / module_spec["file"]
    output_root = ROOT / contract["tiny_live_proof"]["execution_root"]
    checks = {
        "contract_offline_and_all_execution_unauthorized": (
            contract["status"]
            == "OFFLINE_IMPLEMENTED_PENDING_EXPLICIT_AUTHORIZATION"
            and all(
                contract["execution_authorization"][field] is False
                for field in (
                    "unreal_launch_allowed",
                    "native_build_allowed",
                    "author_stage_allowed",
                    "tiny_live_proof_allowed",
                    "full_capture_allowed",
                    "profile_allowed",
                    "automatic_retry_allowed",
                    "network_allowed",
                    "promotion_allowed",
                )
            )
        ),
        "recovery01_inventory_exact": exact_files(
            recovery01_root, recovery01["files"]
        ),
        "recovery01_failure_boundary_exact": (
            recovery01_manifest.get("terminal_state") == "FAILED"
            and [
                stage.get("exit_code")
                for stage in recovery01_manifest.get("stages", [])
            ]
            == recovery01["stage_exit_codes_required"]
            and not (
                recovery01_root / "tiny_proof_receipt.json"
            ).exists()
            and recovery01_manifest.get("full_capture_invoked") is False
            and recovery01_manifest.get("profile_invoked") is False
        ),
        "recovery01_live_audit_exact": all(
            token in proof_log
            for token in (
                '"landscape_component_count": 16',
                '"generated_material_instance_count": 16',
                '"material_resource_count": 16',
                '"compilation_finished_resource_count": 0',
                '"valid_shader_map_resource_count": 16',
                '"asset_compilation_queue_empty": false',
                '"shader_compilation_queue_empty": false',
            )
        ),
        "locked_packages_and_recovery01_materials_exact": exact_files(
            ROOT, contract["locked_production_packages"]
        ),
        "pre_recovery02_module_exact": (
            module.is_file()
            and module.stat().st_size == module_spec["bytes"]
            and sha256_file(module) == module_spec["sha256"]
        ),
        "implementation_hashes_exact": exact_files(
            ROOT, contract["implementation_files"]
        ),
        "python_syntax_exact": all(
            bool(ast.parse(path.read_text(encoding="utf-8")))
            for path in implementation_paths.values()
            if path.suffix == ".py"
        ),
        "native_deferred_begin_does_not_block_compile_managers": (
            "BeginTransientLandscapeDiagnosticMaterialDeferred"
            in native_header
            and "Landscape->UpdateAllComponentMaterialInstances(true)"
            in deferred_native
            and "Component->RecreateRenderState_Concurrent()"
            in deferred_native
            and "FinishAllCompilation" not in deferred_native
            and "Resource->FinishCompilation" not in deferred_native
        ),
        "proof_uses_true_deferred_slate_post_ticks": all(
            token in proof
            for token in (
                "register_slate_post_tick_callback",
                "unregister_slate_post_tick_callback",
                "set_keep_python_script_alive(True)",
                "set_keep_python_script_alive(False)",
                "minimum_poll_interval_seconds",
                "phase_timeout_seconds",
                "whole_timeout_seconds",
                "maximum_editor_ticks",
            )
        ),
        "readiness_requires_all_counters_and_both_queues": all(
            token in proof.split("def compilation_ready", 1)[1].split(
                "class Recovery02State", 1
            )[0]
            for token in (
                'audit["compilation_finished_resource_count"] == 16',
                'audit["valid_shader_map_resource_count"] == 16',
                'audit["asset_compilation_queue_empty"]',
                'audit["shader_compilation_queue_empty"]',
            )
        ),
        "capture_is_gated_by_two_stable_ready_ticks": (
            "if self.stable_ready_ticks < required:" in callback_tick
            and callback_tick.index(
                "if self.stable_ready_ticks < required:"
            )
            < callback_tick.index("self.capture_coverage()")
            < callback_tick.index("self.capture_component()")
            and contract["tiny_live_proof"][
                "stable_ready_ticks_required"
            ]
            == 2
        ),
        "valid_shader_maps_alone_never_accepted": (
            '"no_valid_shader_map_only_acceptance"' in finish_success
            and "compilation_finished_resource_count" in finish_success
            and "asset_compilation_queue_empty" in finish_success
            and "shader_compilation_queue_empty" in finish_success
        ),
        "proof_writes_bounded_poll_evidence_and_failure_receipt": all(
            token in proof
            for token in (
                '"poll_records": self.poll_records',
                '"stable_ready_ticks": self.stable_ready_ticks',
                '"total_elapsed_seconds"',
                "def finish_failure",
                '"gate": "FAIL"',
                "self.receipt.write_text",
            )
        ),
        "proof_restores_governed_material_and_waits": (
            'self.begin_material("governed_restore", self.governed)'
            in proof
            and 'self.transition("WAIT_GOVERNED_RESTORE_COMPILATION")'
            in proof
            and "WAIT_GOVERNED_RESTORE_COMPILATION" in finish_success
        ),
        "supervisor_is_build_then_proof_only": (
            supervisor.index(
                '"build_recovery02_deferred_material_bridge"'
            )
            < supervisor.index(
                '"recovery02_deferred_tiny_live_proof_d3d12_sm6"'
            )
            and '"author_stage_allowed": False' in supervisor
            and '"full_capture_allowed": False' in supervisor
            and '"profile_allowed": False' in supervisor
            and '"automatic_retry_allowed": False' in supervisor
            and "UnrealEditor-Cmd.exe" not in supervisor
        ),
        "launcher_requires_exact_authorization_switch": (
            "if (-not $AuthorizeSingleRecovery02TinyProof)" in launcher
            and "--authorize-single-recovery02-tiny-proof" in launcher
        ),
        "recovery02_output_root_absent": not output_root.exists(),
    }
    ready = all(checks.values())
    report = {
        "schema": (
            "skyguard.phase4.m01-landscape-visible-"
            "attempt07-recovery02-readiness.v1"
        ),
        "contract_id": contract["contract_id"],
        "gate": (
            "PASS_ATTEMPT07_RECOVERY02_OFFLINE_IMPLEMENTATION_READY_"
            "PENDING_AUTHORIZATION"
            if ready
            else "FAIL_ATTEMPT07_RECOVERY02_OFFLINE_NOT_READY"
        ),
        "checks": checks,
        "expected_processes_and_runtime": contract[
            "expected_future_processes_and_runtime"
        ],
        "unreal_launched": False,
        "native_build_invoked": False,
        "author_stage_invoked": False,
        "recovery01_mutated": False,
        "full_capture_invoked": False,
        "profile_invoked": False,
        "promotion_allowed": False,
        "future_authorized_command": (
            "powershell -NoProfile -ExecutionPolicy Bypass -File "
            "\"D:\\Skyguard52\\Scripts\\run_skyguard_phase4_m01_"
            "landscape_visible_attempt07_recovery02.ps1\" "
            "-AuthorizeSingleRecovery02TinyProof"
            if ready
            else None
        ),
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2))
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
