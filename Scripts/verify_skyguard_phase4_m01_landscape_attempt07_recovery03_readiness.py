"""Offline-only readiness check for Attempt07 Recovery03."""

from __future__ import annotations

import ast
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT_PATH = (
    ROOT
    / "Docs/AAA_Review/"
    "PHASE4_M01_LANDSCAPE_VISIBLE_ATTEMPT07_RECOVERY03_CONTRACT.json"
)
REPORT_PATH = (
    ROOT
    / "Saved/Reports/"
    "PHASE4_M01_LANDSCAPE_VISIBLE_ATTEMPT07_RECOVERY03_READINESS.json"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def active_heavy_processes() -> list[str]:
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
    contract = read_json(CONTRACT_PATH)
    checks: dict[str, object] = {}
    checks["contract_identity"] = (
        contract.get("schema")
        == "skyguard.phase4.m01-landscape-visible-attempt07-recovery03.v1"
        and contract.get("contract_id")
        == "P4.5-M01-LANDSCAPE-VISIBLE-007-RECOVERY-03"
    )
    checks["contract_blocked_state"] = (
        contract.get("status")
        == "OFFLINE_IMPLEMENTED_BLOCKED_ON_SEPARATE_FULL_MODULE_COMPILE_PROOF"
        and contract["execution_authorization"]["current_state"]
        == "BLOCKED_PREREQUISITE_FULL_MODULE_COMPILE_PROOF_REQUIRED"
    )

    recovery02 = contract["immutable_recovery02_failure"]
    recovery02_root = ROOT / recovery02["root"]
    recovery02_files_ok = True
    for item in recovery02["files"].values():
        path = recovery02_root / item["file"]
        recovery02_files_ok = recovery02_files_ok and (
            path.is_file()
            and path.stat().st_size == item["bytes"]
            and sha256_file(path) == item["sha256"]
        )
    checks["immutable_recovery02_inventory"] = recovery02_files_ok
    recovery02_manifest = read_json(recovery02_root / "run_manifest.json")
    stages = recovery02_manifest.get("stages", [])
    checks["immutable_recovery02_boundary"] = (
        recovery02_manifest.get("terminal_state") == "FAILED"
        and len(stages) == 1
        and stages[0].get("exit_code") == 6
        and recovery02_manifest.get("author_stage_invoked") is False
        and recovery02_manifest.get("full_capture_invoked") is False
        and recovery02_manifest.get("profile_invoked") is False
        and not (recovery02_root / "tiny_proof_receipt.json").exists()
    )
    build_stdout = (
        recovery02_root
        / "logs/build_recovery02_deferred_material_bridge.stdout.log"
    ).read_text(encoding="utf-8-sig", errors="replace")
    checks["immutable_recovery02_compiler_errors"] = all(
        text in build_stdout
        for text in recovery02["compiler_errors_required"]
    )

    locked_ok = True
    for item in contract["locked_production_packages"].values():
        path = ROOT / item["file"]
        locked_ok = locked_ok and (
            path.is_file() and sha256_file(path) == item["sha256"]
        )
    checks["locked_production_packages"] = locked_ok

    implementation_ok = True
    python_ast_ok = True
    for item in contract["implementation_files"].values():
        path = ROOT / item["file"]
        implementation_ok = implementation_ok and (
            path.is_file() and sha256_file(path) == item["sha256"]
        )
        if path.suffix == ".py":
            try:
                ast.parse(path.read_text(encoding="utf-8-sig"))
            except SyntaxError:
                python_ast_ok = False
    checks["implementation_hashes"] = implementation_ok
    checks["python_ast"] = python_ast_ok

    wrapper_text = (
        ROOT
        / contract["implementation_files"]["recovery03_tiny_proof"]["file"]
    ).read_text(encoding="utf-8-sig")
    checks["frozen_deferred_proof_inherited"] = (
        "prove_skyguard_phase4_m01_landscape_attempt07_recovery02_tiny_live"
        in wrapper_text
        and "SkyguardAttempt07Recovery03ProofRoot" in wrapper_text
        and sha256_file(
            ROOT
            / contract["implementation_files"][
                "frozen_recovery02_tiny_proof"
            ]["file"]
        )
        == "5635d15262db7e7f597f62e2f8466a640bccde61088acc2a232842a713a31ffc"
    )
    supervisor_text = (
        ROOT
        / contract["implementation_files"]["recovery03_supervisor"]["file"]
    ).read_text(encoding="utf-8-sig")
    launcher_text = (
        ROOT
        / contract["implementation_files"]["recovery03_launcher"]["file"]
    ).read_text(encoding="utf-8-sig")
    forbidden_build_tokens = (
        "Build.bat",
        "dotnet.exe",
        "build_recovery03",
        "author_recovery03",
    )
    checks["proof_only_tooling"] = (
        not any(
            token in supervisor_text or token in launcher_text
            for token in forbidden_build_tokens
        )
        and '"build_stage_allowed": False' in supervisor_text
        and '"author_stage_allowed": False' in supervisor_text
        and "UnrealEditor.exe" in supervisor_text
    )

    execution_root = ROOT / contract["tiny_live_proof"]["execution_root"]
    checks["recovery03_namespace_unused"] = not execution_root.exists()
    checks["compile_activation_supplied"] = False
    checks["compile_prerequisite_satisfied"] = False
    heavy = active_heavy_processes()
    checks["heavy_lane_observed_free"] = not heavy

    offline_tooling_ready = all(
        bool(value)
        for key, value in checks.items()
        if key
        not in {
            "compile_activation_supplied",
            "compile_prerequisite_satisfied",
            "heavy_lane_observed_free",
        }
    )
    report = {
        "schema": (
            "skyguard.phase4.m01-landscape-visible-"
            "attempt07-recovery03-readiness.v1"
        ),
        "contract_id": contract["contract_id"],
        "created_at_utc": datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        "gate": (
            "BLOCKED_PREREQUISITE_FULL_MODULE_COMPILE_PROOF_REQUIRED"
        ),
        "offline_tooling_ready": offline_tooling_ready,
        "execution_ready": False,
        "unreal_launched": False,
        "native_build_launched": False,
        "recovery02_retried": False,
        "activation_created": False,
        "contract": {
            "file": str(CONTRACT_PATH.relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha256_file(CONTRACT_PATH),
        },
        "checks": checks,
        "active_heavy_processes_observed": heavy,
        "blocking_prerequisite": contract[
            "full_module_compile_prerequisite"
        ],
        "conditional_command_template": contract[
            "execution_authorization"
        ]["conditional_command_template"],
        "expected_processes_and_runtime": contract[
            "expected_future_processes_and_runtime"
        ],
        "next_action": (
            "A separately authorized lane must prove a successful full "
            "Skyguard52Editor module compile and create a hash-bound "
            "activation. Do not run Recovery03 before then."
        ),
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    if not offline_tooling_ready:
        raise RuntimeError("Recovery03 offline tooling readiness failed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
