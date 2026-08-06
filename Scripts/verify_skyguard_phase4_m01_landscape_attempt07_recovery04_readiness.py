"""Offline readiness and analytical preflight for Attempt07 Recovery04."""

from __future__ import annotations

import ast
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import audit_skyguard_phase4_m01_landscape_attempt07_recovery04 as audit


ROOT = Path(r"D:\Skyguard52")
CONTRACT_PATH = (
    ROOT
    / "Docs/AAA_Review/"
    "PHASE4_M01_LANDSCAPE_VISIBLE_ATTEMPT07_RECOVERY04_CONTRACT.json"
)
REPORT_PATH = (
    ROOT
    / "Saved/Reports/"
    "PHASE4_M01_LANDSCAPE_VISIBLE_ATTEMPT07_RECOVERY04_READINESS.json"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def heavy_processes() -> list[str]:
    result = subprocess.run(
        ["tasklist", "/fo", "csv", "/nh"],
        capture_output=True,
        text=True,
        check=False,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    needles = (
        "unrealeditor.exe",
        "unrealeditor-cmd.exe",
        "unrealbuildtool.exe",
        "blender.exe",
    )
    return [
        line
        for line in result.stdout.splitlines()
        if any(needle in line.lower() for needle in needles)
    ]


def main() -> int:
    contract = json.loads(
        CONTRACT_PATH.read_text(encoding="utf-8-sig")
    )
    checks: dict[str, bool] = {}
    checks["contract_identity"] = (
        contract.get("schema")
        == "skyguard.phase4.m01-landscape-visible-attempt07-recovery04.v1"
        and contract.get("contract_id")
        == "P4.5-M01-LANDSCAPE-VISIBLE-007-RECOVERY-04"
    )
    checks["audit_only_policy"] = all(
        contract["offline_audit_execution"][name] is False
        for name in (
            "unreal_launch_allowed",
            "native_build_allowed",
            "author_stage_allowed",
            "recapture_allowed",
            "full_capture_allowed",
            "profile_allowed",
            "promotion_allowed",
        )
    )
    implementation_ok = True
    syntax_ok = True
    for item in contract["implementation_files"].values():
        path = ROOT / item["file"]
        implementation_ok = implementation_ok and (
            path.is_file()
            and path.stat().st_size == item["bytes"]
            and sha256_file(path) == item["sha256"]
        )
        if path.suffix == ".py":
            try:
                ast.parse(path.read_text(encoding="utf-8-sig"))
            except SyntaxError:
                syntax_ok = False
    checks["implementation_hashes"] = implementation_ok
    checks["python_syntax"] = syntax_ok

    locked_ok = True
    for item in contract["locked_production_packages"].values():
        path = ROOT / item["file"]
        locked_ok = locked_ok and (
            path.is_file() and sha256_file(path) == item["sha256"]
        )
    checks["locked_production_packages"] = locked_ok

    recovery03_root, receipt, evidence_hashes = audit.verify_recovery03(
        contract
    )
    checks["immutable_recovery03"] = True
    analysis = audit.analyze_component_png(
        recovery03_root
        / contract["offline_palette_audit"]["component_capture_file"],
        contract,
        receipt,
    )
    checks["direct_linear_rgb8_palette_passes"] = (
        analysis["component_id_count"] == 16
        and analysis["unique_rgb8_color_count"] == 17
        and analysis["nonblack_pixel_count"] == 72022
        and analysis["all_components_single_four_connected_regions"]
        and analysis["horizontal_order_valid"]
        and analysis["vertical_pairing_valid"]
    )
    old_palette = receipt["component_palette"]
    checks["old_analyzer_failed_as_recorded"] = (
        old_palette["matching_id_count"] == 0
        and all(
            count == 0 for count in old_palette["pixel_counts"].values()
        )
    )
    recovery04_root = (
        ROOT / contract["offline_audit_execution"]["root"]
    )
    checks["new_namespace_unused"] = not recovery04_root.exists()
    active_heavy = heavy_processes()
    checks["heavy_lane_observed_free"] = not active_heavy

    offline_tooling_ready = all(
        value
        for name, value in checks.items()
        if name != "heavy_lane_observed_free"
    )
    execution_ready = (
        offline_tooling_ready and checks["heavy_lane_observed_free"]
    )
    report = {
        "schema": (
            "skyguard.phase4.m01-landscape-visible-"
            "attempt07-recovery04-readiness.v1"
        ),
        "contract_id": contract["contract_id"],
        "created_at_utc": datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        "gate": (
            "READY_FOR_SINGLE_OFFLINE_AUDIT"
            if execution_ready
            else (
                "BLOCKED_HEAVY_LANE_ACTIVE"
                if offline_tooling_ready
                else "BLOCKED_OFFLINE_READINESS_FAILED"
            )
        ),
        "offline_tooling_ready": offline_tooling_ready,
        "execution_ready": execution_ready,
        "offline_audit_executed": False,
        "recovery04_namespace_created": False,
        "unreal_launched": False,
        "native_build_launched": False,
        "recapture_performed": False,
        "full_capture_invoked": False,
        "profile_invoked": False,
        "promotion_allowed": False,
        "contract": {
            "file": str(CONTRACT_PATH.relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha256_file(CONTRACT_PATH),
        },
        "checks": checks,
        "active_heavy_processes_observed": active_heavy,
        "immutable_recovery03_hashes": evidence_hashes,
        "analytical_preflight": analysis,
        "authorized_command": contract["offline_audit_execution"][
            "command"
        ],
        "expected_processes": contract["offline_audit_execution"][
            "expected_processes"
        ],
        "expected_runtime_seconds": contract[
            "offline_audit_execution"
        ]["expected_runtime_seconds"],
        "next_gate": contract["offline_audit_execution"][
            "next_gate_on_pass"
        ],
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    if not offline_tooling_ready:
        raise RuntimeError("Recovery04 offline readiness failed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
