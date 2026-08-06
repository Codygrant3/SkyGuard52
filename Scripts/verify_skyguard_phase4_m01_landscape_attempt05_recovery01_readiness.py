"""Offline fail-closed readiness for attempt05 recovery continuation 01."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT_PATH = (
    ROOT
    / "Docs/AAA_Review"
    / "PHASE4_M01_LANDSCAPE_VISIBLE_ATTEMPT05_RECOVERY_CONTRACT_01.json"
)
RENDER_VERIFIER = (
    ROOT
    / "Scripts"
    / "verify_skyguard_phase4_m01_landscape_render_state_attempt05_recovery01.py"
)
SUPERVISOR = (
    ROOT
    / "Scripts"
    / "run_skyguard_phase4_m01_landscape_visible_attempt05_recovery01.ps1"
)
OUTPUT = (
    ROOT
    / "Saved/Reports"
    / "PHASE4_M01_LANDSCAPE_VISIBLE_ATTEMPT05_RECOVERY01_READINESS.json"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def locked_files_pass(section: dict) -> bool:
    return all(
        (ROOT / spec["file"]).is_file()
        and sha256_file(ROOT / spec["file"]) == spec["sha256"]
        for spec in section.values()
    )


def main() -> int:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8-sig"))
    verifier_source = RENDER_VERIFIER.read_text(encoding="utf-8")
    supervisor_source = SUPERVISOR.read_text(encoding="utf-8")
    predecessor_manifest = json.loads(
        (
            ROOT
            / contract["immutable_predecessor_evidence"][
                "invocation02_manifest"
            ]["file"]
        ).read_text(encoding="utf-8-sig")
    )
    author_report = json.loads(
        (
            ROOT
            / contract["immutable_predecessor_evidence"]["authoring_report"][
                "file"
            ]
        ).read_text(encoding="utf-8-sig")
    )
    nullrhi_report = json.loads(
        (
            ROOT
            / contract["immutable_predecessor_evidence"][
                "failed_nullrhi_acceptance"
            ]["file"]
        ).read_text(encoding="utf-8-sig")
    )
    recovery_root = ROOT / contract["recovery_execution"]["recovery_root"]
    render_receipt = (
        ROOT
        / "Saved/Reports"
        / "PHASE4_M01_LANDSCAPE_RENDER_STATE_ACCEPTANCE_ATTEMPT05_RECOVERY01.json"
    )
    first_stage_index = supervisor_source.find(
        '-Name "verify_candidate_render_state_d3d12_sm6"'
    )
    first_capture_index = supervisor_source.find(
        '-Name "$($spec.mode)_capture"'
    )
    stage_persist_index = supervisor_source.find(
        "$manifest.stages += $stage",
        first_stage_index,
    )
    save_index = supervisor_source.find(
        "Save-Json -Value $manifest -Path $ManifestPath",
        stage_persist_index,
    )
    assert_index = supervisor_source.find(
        "Assert-StagePassed -Stage $stage",
        save_index,
    )
    rhi_check_index = verifier_source.find("if rhi != EXPECTED_RHI:")
    shared_verifier_index = verifier_source.find("verifier.main()")

    checks = {
        "recovery_contract_offline_only": (
            contract["status"]
            == "OFFLINE_RECOVERY_DESIGN_READY_NOT_AUTHORIZED_FOR_UNREAL_EXECUTION"
            and contract["recovery_execution"]["promotion_allowed"] is False
        ),
        "predecessor_evidence_hashes_locked": locked_files_pass(
            contract["immutable_predecessor_evidence"]
        ),
        "all_five_package_hashes_locked": locked_files_pass(
            contract["immutable_packages"]
        ),
        "invocation02_is_exact_failed_boundary": (
            predecessor_manifest["attempt_id"]
            == contract["fault_boundary"]["attempt_id"]
            and predecessor_manifest["terminal_state"] == "FAILED"
            and len(predecessor_manifest["stages"]) == 1
            and predecessor_manifest["stages"][0]["name"]
            == "author_immutable_candidate_attempt05"
        ),
        "authoring_live_audit_passed_16_16_16_5": (
            author_report["gate"] == "PASS"
            and author_report["landscape_visible_audit"]["success"] is True
            and author_report["landscape_visible_audit"][
                "visible_component_count"
            ]
            == 16
            and author_report["landscape_visible_audit"][
                "registered_component_count"
            ]
            == 16
            and author_report["landscape_visible_audit"][
                "render_state_created_component_count"
            ]
            == 16
            and author_report["landscape_visible_audit"][
                "contract_camera_frustum_intersection_count"
            ]
            == 5
        ),
        "nullrhi_fault_is_exactly_render_state_zero": (
            nullrhi_report["gate"] == "FAIL"
            and nullrhi_report["landscape_visible_audit"][
                "visible_component_count"
            ]
            == 16
            and nullrhi_report["landscape_visible_audit"][
                "registered_component_count"
            ]
            == 16
            and nullrhi_report["landscape_visible_audit"][
                "render_state_created_component_count"
            ]
            == 0
            and nullrhi_report["landscape_visible_audit"][
                "contract_camera_frustum_intersection_count"
            ]
            == 5
        ),
        "normal_editor_verifier_requires_rhi_before_shared_audit": (
            0 <= rhi_check_index < shared_verifier_index
            and "EXPECTED_RHI = \"D3D12|SM6\"" in verifier_source
            and "locked_package_hashes(recovery)" in verifier_source
            and "world_saved" in verifier_source
            and "pcg_generation_invoked" in verifier_source
        ),
        "supervisor_never_authors_or_uses_nullrhi": (
            "build_skyguard_phase4_m01_landscape_material_validation"
            not in supervisor_source
            and "author_immutable_candidate" not in supervisor_source
            and "-NullRHI" not in supervisor_source
        ),
        "render_state_gate_precedes_every_capture": (
            0 <= first_stage_index < first_capture_index
            and "renderReceipt.gate" in supervisor_source
            and "render_state_created_component_count -ne 16"
            in supervisor_source
        ),
        "stage_receipt_persisted_before_assertion": (
            0
            <= stage_persist_index
            < save_index
            < assert_index
        ),
        "package_hashes_checked_after_every_unreal_stage": (
            "immutable_package_hashes_after = $lockResult.hashes"
            in supervisor_source
            and "immutable_package_lock_error = $lockResult.error"
            in supervisor_source
            and "Get-LockedPackageSnapshotSafe" in supervisor_source
            and "initial_package_hashes = $initialPackageHashes"
            in supervisor_source
            and "final_package_hashes = $finalLockResult.hashes"
            in supervisor_source
        ),
        "supervisor_uses_internal_sha256_and_fixed_idempotency_root": (
            "Get-FileHash" not in supervisor_source
            and "[System.Security.Cryptography.SHA256]::Create()"
            in supervisor_source
            and "Recovery root already exists; refuse duplicate or overwrite"
            in supervisor_source
            and "Recovery render-state receipt already exists; refuse overwrite"
            in supervisor_source
        ),
        "same_process_profile_contract_preserved": (
            "-SkyguardP45ProfileWarmupSeconds=30" in supervisor_source
            and "-SkyguardP45ProfileMeasuredSeconds=60" in supervisor_source
            and "-csvCaptureFrames" not in supervisor_source
            and "-d3d12" in supervisor_source
            and "-sm6" in supervisor_source
        ),
        "recovery_outputs_do_not_exist_before_authorized_run": (
            not recovery_root.exists() and not render_receipt.exists()
        ),
    }
    gate = (
        "PASS_RECOVERY_OFFLINE_READY_PENDING_EXCLUSIVE_UNREAL_AUTHORIZATION"
        if all(checks.values())
        else "FAIL_RECOVERY_OFFLINE_NOT_READY"
    )
    report = {
        "schema": (
            "skyguard.phase4.m01-landscape-visible-attempt05-recovery-readiness.v1"
        ),
        "recovery_id": contract["recovery_id"],
        "gate": gate,
        "scope": "offline recovery implementation and immutable evidence only",
        "unreal_launched": False,
        "candidate_mutated": False,
        "authoring_will_rerun": False,
        "promotion_allowed": False,
        "checks": checks,
        "remaining_before_execution": [
            "obtain explicit root authorization for exactly one recovery_01 supervisor run"
        ],
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if gate.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
