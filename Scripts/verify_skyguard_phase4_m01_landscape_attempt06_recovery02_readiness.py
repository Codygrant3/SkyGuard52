"""Fail-closed offline readiness for Attempt06 Recovery02."""

from __future__ import annotations

import ast
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
sys.path.insert(0, str(ROOT / "Scripts"))
from phase4_m01_landscape_attempt06_contract import load_attempt06_contract
from phase4_m01_landscape_repair_contract import load_attempt05_contract
from verify_skyguard_phase4_m01_landscape_visible_gpu_gate import (
    analyze_csv,
    normalized_repaired_capture_thresholds,
)


CONTRACT_PATH = (
    ROOT
    / "Docs/AAA_Review/"
    "PHASE4_M01_LANDSCAPE_VISIBLE_ATTEMPT06_RECOVERY02_CONTRACT.json"
)
SUPERVISOR = (
    ROOT
    / "Scripts/"
    "supervise_skyguard_phase4_m01_landscape_visible_"
    "attempt06_recovery02.py"
)
LAUNCHER = (
    ROOT
    / "Scripts/"
    "run_skyguard_phase4_m01_landscape_visible_attempt06_recovery02.ps1"
)
OUTPUT = (
    ROOT
    / "Saved/Reports/"
    "PHASE4_M01_LANDSCAPE_VISIBLE_ATTEMPT06_RECOVERY02_READINESS.json"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inventory_check(contract: dict) -> tuple[bool, int]:
    spec = contract["recovery01_evidence"]["inventory"]
    inventory_path = ROOT / spec["file"]
    if (
        not inventory_path.is_file()
        or sha256_file(inventory_path) != spec["sha256"]
    ):
        return False, 0
    inventory = json.loads(
        inventory_path.read_text(encoding="utf-8-sig")
    )
    source_root = ROOT / inventory["source_root"]
    expected = {
        item["file"].replace("\\", "/") for item in inventory["files"]
    }
    actual = {
        path.relative_to(source_root).as_posix()
        for path in source_root.rglob("*")
        if path.is_file()
    }
    if expected != actual:
        return False, len(expected)
    all_items = [
        (source_root / item["file"], item)
        for item in inventory["files"]
    ] + [
        (ROOT / item["file"], item)
        for item in inventory["external_profile_csv_files"]
    ]
    exact = all(
        path.is_file()
        and path.stat().st_size == item["bytes"]
        and sha256_file(path) == item["sha256"]
        for path, item in all_items
    )
    return exact, len(all_items)


def main() -> int:
    contract = json.loads(
        CONTRACT_PATH.read_text(encoding="utf-8-sig")
    )
    manifest_spec = contract["recovery01_evidence"]["manifest"]
    manifest_path = ROOT / manifest_spec["file"]
    manifest = json.loads(
        manifest_path.read_text(encoding="utf-8-sig")
    )
    inventory_exact, evidence_count = inventory_check(contract)
    gate_spec = contract["offline_gate_implementation"]
    gate_source_path = ROOT / gate_spec["source"]
    gate_source = gate_source_path.read_text(encoding="utf-8")
    supervisor_source = SUPERVISOR.read_text(encoding="utf-8")
    launcher_source = LAUNCHER.read_text(encoding="utf-8")
    attempt05_thresholds = normalized_repaired_capture_thresholds(
        load_attempt05_contract()
    )["minimum_landscape_pixel_fraction_by_camera"]
    attempt06_thresholds = normalized_repaired_capture_thresholds(
        load_attempt06_contract()
    )["minimum_landscape_pixel_fraction_by_camera"]
    expected_thresholds = contract["threshold_normalization"][
        "normalized_camera_thresholds"
    ]
    inventory = json.loads(
        (
            ROOT / contract["recovery01_evidence"]["inventory"]["file"]
        ).read_text(encoding="utf-8-sig")
    )
    csv_analysis = [
        analyze_csv(ROOT / item["file"])
        for item in inventory["external_profile_csv_files"]
    ]
    recovery_root = ROOT / contract["recovery_execution"]["root"]
    checks = {
        "recovery01_inventory_exhaustive_and_exact": (
            inventory_exact
            and evidence_count
            == (
                contract["recovery01_evidence"]["inventory"][
                    "exhaustive_source_root_file_count"
                ]
                + contract["recovery01_evidence"]["inventory"][
                    "external_profile_csv_file_count"
                ]
            )
        ),
        "recovery01_manifest_hash_and_boundary_exact": (
            sha256_file(manifest_path) == manifest_spec["sha256"]
            and manifest["terminal_state"] == "FAILED"
            and [stage["name"] for stage in manifest["stages"]]
            == contract["recovery01_evidence"][
                "required_successful_stage_names"
            ]
            and all(
                stage["exit_code"] == 0
                and stage["timed_out"] is False
                and stage["process_exit_observed"] is True
                for stage in manifest["stages"]
            )
            and len(manifest["errors"]) == 1
            and contract["recovery01_evidence"][
                "required_only_error_contains"
            ]
            in manifest["errors"][0]
        ),
        "gate_implementation_hash_and_parse_exact": (
            sha256_file(gate_source_path) == gate_spec["recovery02_sha256"]
            and bool(ast.parse(gate_source))
        ),
        "attempt05_legacy_thresholds_preserved": (
            attempt05_thresholds == expected_thresholds
        ),
        "attempt06_per_camera_thresholds_normalized": (
            attempt06_thresholds == expected_thresholds
        ),
        "normalizer_is_fail_closed": all(
            marker in gate_source
            for marker in (
                "def normalized_repaired_capture_thresholds",
                "camera_id in camera_thresholds",
                "minimum < 0.0",
                "minimum > 1.0",
                "invalid Attempt06 per-camera coverage threshold",
            )
        ),
        "immutable_csv_memory_fallback_is_available_and_provenanced": (
            all(
                item["parseable"]
                and item["metrics"].get("peak_physical_used_mib")
                is not None
                for item in csv_analysis
            )
            and "supervisor_stage_peak_working_set_mib" in gate_source
            and "immutable_csv_PhysicalUsedMB" in gate_source
            and "peak_working_set_source" in gate_source
        ),
        "offline_supervisor_parseable": bool(ast.parse(supervisor_source)),
        "offline_supervisor_cannot_launch_or_rerun_heavy_work": (
            "UnrealEditor" not in supervisor_source
            and "UnrealEditor-Cmd" not in supervisor_source
            and "blender.exe" not in supervisor_source.lower()
            and "Build.bat" not in supervisor_source
            and "capture_skyguard" not in supervisor_source
            and "ProfileWarmupSeconds" not in supervisor_source
            and '"unreal_launched": False' in supervisor_source
            and '"captures_rerun": False' in supervisor_source
            and '"profiles_rerun": False' in supervisor_source
        ),
        "offline_supervisor_hash_locks_and_refuses_duplicate": (
            "verify_recovery01_inventory" in supervisor_source
            and "verify_recovery01_boundary" in supervisor_source
            and "Recovery02 root already exists" in supervisor_source
            and "source_evidence_unchanged" in supervisor_source
            and '"promotion_allowed": False' in supervisor_source
        ),
        "launcher_requires_explicit_offline_authorization": (
            "if (-not $AuthorizeOfflineRecoveryRun)" in launcher_source
            and "--authorize-offline-recovery-run" in launcher_source
        ),
        "recovery_root_absent": not recovery_root.exists(),
        "contract_forbids_heavy_work_mutation_retry_and_promotion": all(
            contract["recovery_execution"][field] is False
            for field in (
                "unreal_launch_allowed",
                "blender_launch_allowed",
                "build_allowed",
                "authoring_allowed",
                "capture_allowed",
                "profile_allowed",
                "network_allowed",
                "automatic_retry_allowed",
                "source_recovery_mutation_allowed",
                "promotion_allowed",
                "duplicate_or_overwrite_allowed",
            )
        ),
    }
    ready = all(checks.values())
    report = {
        "schema": (
            "skyguard.phase4.m01-landscape-visible-"
            "attempt06-recovery02-readiness.v1"
        ),
        "recovery_id": contract["recovery_id"],
        "gate": (
            "PASS_RECOVERY02_OFFLINE_READY_PENDING_AUTHORIZATION"
            if ready
            else "FAIL_RECOVERY02_OFFLINE_NOT_READY"
        ),
        "source_evidence_file_count": evidence_count,
        "unreal_launched": False,
        "captures_rerun": False,
        "profiles_rerun": False,
        "promotion_allowed": False,
        "checks": checks,
        "authorized_command": (
            "powershell -NoProfile -ExecutionPolicy Bypass -File "
            "\"D:\\Skyguard52\\Scripts\\run_skyguard_phase4_m01_"
            "landscape_visible_attempt06_recovery02.ps1\" "
            "-AuthorizeOfflineRecoveryRun"
            if ready
            else None
        ),
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
