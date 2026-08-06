"""Offline fail-closed readiness for Attempt06 Recovery01."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT_PATH = (
    ROOT
    / "Docs/AAA_Review/"
    "PHASE4_M01_LANDSCAPE_VISIBLE_ATTEMPT06_RECOVERY01_CONTRACT.json"
)
RENDER_VERIFIER = (
    ROOT
    / "Scripts/"
    "verify_skyguard_phase4_m01_landscape_attempt06_"
    "recovery01_render_state.py"
)
SUPERVISOR = (
    ROOT
    / "Scripts/"
    "supervise_skyguard_phase4_m01_landscape_visible_"
    "attempt06_recovery01.py"
)
LAUNCHER = (
    ROOT
    / "Scripts/"
    "run_skyguard_phase4_m01_landscape_visible_attempt06_recovery01.ps1"
)
OUTPUT = (
    ROOT
    / "Saved/Reports/"
    "PHASE4_M01_LANDSCAPE_VISIBLE_ATTEMPT06_RECOVERY01_READINESS.json"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def locked_files_pass(items: dict) -> bool:
    return all(
        (ROOT / item["file"]).is_file()
        and sha256_file(ROOT / item["file"]) == item["sha256"]
        for item in items.values()
        if isinstance(item, dict) and "file" in item
    )


def main() -> int:
    contract = json.loads(
        CONTRACT_PATH.read_text(encoding="utf-8-sig")
    )
    failure = contract["failure_boundary"]
    failed_manifest = json.loads(
        (ROOT / failure["failed_manifest"]["file"]).read_text(
            encoding="utf-8-sig"
        )
    )
    failed_acceptance = json.loads(
        (ROOT / failure["failed_editor_acceptance"]["file"]).read_text(
            encoding="utf-8-sig"
        )
    )
    verifier_source = RENDER_VERIFIER.read_text(encoding="utf-8")
    supervisor_source = SUPERVISOR.read_text(encoding="utf-8")
    launcher_source = LAUNCHER.read_text(encoding="utf-8")
    module_spec = contract["compiled_module"]
    module = ROOT / module_spec["file"]
    source_mtimes = [
        path.stat().st_mtime_ns
        for path in (ROOT / "Source/Skyguard52").glob("*")
        if path.is_file() and path.suffix.lower() in {".h", ".cpp"}
    ]
    recovery_root = (
        ROOT / contract["recovery_execution"]["recovery_root"]
    )
    checks = {
        "failed_attempt_evidence_hashes_locked": locked_files_pass(
            {
                "manifest": failure["failed_manifest"],
                "acceptance": failure["failed_editor_acceptance"],
            }
        ),
        "failed_boundary_exact": (
            failed_manifest["terminal_state"] == "FAILED"
            and len(failed_manifest["stages"]) == 2
            and failed_manifest["stages"][1]["name"]
            == "author_immutable_candidate_attempt06"
            and failed_manifest["stages"][1]["exit_code"] == 0
            and failed_acceptance["gate"] == "FAIL"
            and failed_acceptance["landscape_visible_audit"][
                "visible_component_count"
            ]
            == 16
            and failed_acceptance["landscape_visible_audit"][
                "registered_component_count"
            ]
            == 16
            and failed_acceptance["landscape_visible_audit"][
                "render_state_created_component_count"
            ]
            == 0
            and failed_acceptance["landscape_visible_audit"][
                "contract_camera_frustum_intersection_count"
            ]
            == 5
        ),
        "authored_attempt06_packages_locked": locked_files_pass(
            contract["immutable_packages"]
        ),
        "compiled_module_exact_and_fresh": (
            module.is_file()
            and sha256_file(module) == module_spec["sha256"]
            and bool(source_mtimes)
            and module.stat().st_mtime_ns >= max(source_mtimes)
        ),
        "recovery_root_absent": not recovery_root.exists(),
        "render_verifier_is_d3d12_read_only_and_parseable": (
            bool(ast.parse(verifier_source))
            and 'rhi != "D3D12|SM6"' in verifier_source
            and "render_state_created_component_count" in verifier_source
            and "package_hashes_unchanged" in verifier_source
            and '"world_saved": False' in verifier_source
            and '"pcg_generation_invoked": False' in verifier_source
            and "save_current_level" not in verifier_source
            and "save_asset" not in verifier_source
        ),
        "recovery_supervisor_parseable": bool(ast.parse(supervisor_source)),
        "recovery_supervisor_has_no_build_or_author_stage": (
            "build_skyguard52_editor_attempt06" not in supervisor_source
            and "author_immutable_candidate_attempt06" not in supervisor_source
            and "Build.bat" not in supervisor_source
            and "-run=pythonscript" not in supervisor_source
            and "-NullRHI" not in supervisor_source
        ),
        "render_gate_precedes_capture_and_profile": (
            supervisor_source.index(
                '"verify_candidate_render_state_d3d12_sm6"'
            )
            < supervisor_source.index('f"{mode}_capture"')
            < supervisor_source.index('f"{mode}_profile_measured"')
            and "render_state_created_component_count" in supervisor_source
            and "capture_manifest_pass" in supervisor_source
        ),
        "profiles_are_true_same_process_and_sequential": (
            "-SkyguardP45ProfileWarmupSeconds=30" in supervisor_source
            and "-SkyguardP45ProfileMeasuredSeconds=60" in supervisor_source
            and "-csvCaptureFrames" not in supervisor_source
            and "-benchmark" not in supervisor_source
            and '("baseline", baseline["asset"])' in supervisor_source
            and '("candidate", candidate["asset"])' in supervisor_source
        ),
        "recovery_supervisor_locks_packages_and_refuses_duplicate": (
            "assert_locked_items" in supervisor_source
            and "Recovery01 root already exists" in supervisor_source
            and "failed Attempt06 boundary no longer matches"
            in supervisor_source
            and '"promotion_allowed": False' in supervisor_source
        ),
        "launcher_requires_explicit_single_recovery_authorization": (
            "AuthorizeSingleRecoveryRun" in launcher_source
            and "if (-not $AuthorizeSingleRecoveryRun)" in launcher_source
            and "--authorize-single-recovery-run" in launcher_source
        ),
        "contract_forbids_retry_save_pcg_network_and_promotion": all(
            contract["recovery_execution"][key] is False
            for key in (
                "automatic_retry_allowed",
                "world_or_package_save_allowed",
                "pcg_generation_allowed",
                "network_download_allowed",
                "promotion_allowed",
            )
        ),
    }
    ready = all(checks.values())
    report = {
        "schema": (
            "skyguard.phase4.m01-landscape-visible-"
            "attempt06-recovery01-readiness.v1"
        ),
        "recovery_id": contract["recovery_id"],
        "gate": (
            "PASS_RECOVERY01_READY_PENDING_AUTHORIZATION"
            if ready
            else "FAIL_RECOVERY01_OFFLINE_NOT_READY"
        ),
        "scope": "offline resume-only recovery validation",
        "unreal_launched": False,
        "attempt06_reauthored": False,
        "failed_attempt_mutated": False,
        "promotion_allowed": False,
        "checks": checks,
        "authorized_launch_command": (
            "powershell -NoProfile -ExecutionPolicy Bypass -File "
            "\"D:\\Skyguard52\\Scripts\\run_skyguard_phase4_m01_"
            "landscape_visible_attempt06_recovery01.ps1\" "
            "-AuthorizeSingleRecoveryRun"
            if ready
            else None
        ),
        "remaining_before_execution": (
            ["obtain authorization for exactly one Recovery01 run"]
            if ready
            else ["repair failing offline checks"]
        ),
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
