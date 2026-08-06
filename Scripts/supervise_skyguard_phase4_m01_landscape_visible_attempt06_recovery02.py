"""Run exactly one immutable, offline-only Attempt06 Recovery02 analysis."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT_PATH = (
    ROOT
    / "Docs/AAA_Review/"
    "PHASE4_M01_LANDSCAPE_VISIBLE_ATTEMPT06_RECOVERY02_CONTRACT.json"
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def verify_recovery01_inventory(root: Path, contract: dict) -> dict[str, str]:
    inventory_spec = contract["recovery01_evidence"]["inventory"]
    inventory_path = root / inventory_spec["file"]
    if (
        not inventory_path.is_file()
        or sha256_file(inventory_path) != inventory_spec["sha256"]
    ):
        raise RuntimeError("Recovery01 inventory file hash failed")
    inventory = read_json(inventory_path)
    source_root = root / inventory["source_root"]
    expected_relative = {
        item["file"].replace("\\", "/") for item in inventory["files"]
    }
    actual_relative = {
        path.relative_to(source_root).as_posix()
        for path in source_root.rglob("*")
        if path.is_file()
    }
    if expected_relative != actual_relative:
        missing = sorted(expected_relative - actual_relative)
        extra = sorted(actual_relative - expected_relative)
        raise RuntimeError(
            "Recovery01 inventory set mismatch; "
            f"missing={missing!r}; extra={extra!r}"
        )
    hashes = {}
    for item in inventory["files"]:
        path = source_root / item["file"]
        if path.stat().st_size != item["bytes"]:
            raise RuntimeError("Recovery01 evidence size changed: " + str(path))
        digest = sha256_file(path)
        if digest != item["sha256"]:
            raise RuntimeError("Recovery01 evidence hash changed: " + str(path))
        hashes[path.relative_to(root).as_posix()] = digest
    for item in inventory["external_profile_csv_files"]:
        path = root / item["file"]
        if not path.is_file() or path.stat().st_size != item["bytes"]:
            raise RuntimeError("Recovery01 CSV size changed: " + str(path))
        digest = sha256_file(path)
        if digest != item["sha256"]:
            raise RuntimeError("Recovery01 CSV hash changed: " + str(path))
        hashes[path.relative_to(root).as_posix()] = digest
    return hashes


def verify_recovery01_boundary(root: Path, contract: dict) -> dict:
    evidence = contract["recovery01_evidence"]
    manifest_path = root / evidence["manifest"]["file"]
    if sha256_file(manifest_path) != evidence["manifest"]["sha256"]:
        raise RuntimeError("Recovery01 manifest hash failed")
    manifest = read_json(manifest_path)
    stages = manifest.get("stages", [])
    expected_names = evidence["required_successful_stage_names"]
    if (
        manifest.get("terminal_state") != evidence["required_terminal_state"]
        or [stage.get("name") for stage in stages] != expected_names
        or any(
            stage.get("exit_code") != evidence["required_stage_exit_code"]
            or stage.get("timed_out") is not False
            or stage.get("process_exit_observed") is not True
            for stage in stages
        )
        or len(manifest.get("errors", [])) != 1
        or evidence["required_only_error_contains"]
        not in manifest["errors"][0]
    ):
        raise RuntimeError("Recovery01 failure boundary no longer matches")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=ROOT)
    parser.add_argument(
        "--authorize-offline-recovery-run", action="store_true"
    )
    parser.add_argument("--timeout-seconds", type=int, default=180)
    args = parser.parse_args()
    if not args.authorize_offline_recovery_run:
        raise RuntimeError(
            "Recovery02 requires --authorize-offline-recovery-run"
        )
    root = args.project_root.resolve()
    contract = read_json(
        root
        / "Docs/AAA_Review/"
        "PHASE4_M01_LANDSCAPE_VISIBLE_ATTEMPT06_RECOVERY02_CONTRACT.json"
    )
    if contract["recovery_id"] != (
        "P4.5-M01-LANDSCAPE-VISIBLE-006-RECOVERY-02"
    ):
        raise RuntimeError("Recovery02 contract ID mismatch")
    if contract["recovery_execution"]["execution_type"] != (
        "OFFLINE_PYTHON_ONLY"
    ):
        raise RuntimeError("Recovery02 is not offline-only")
    source_hashes_before = verify_recovery01_inventory(root, contract)
    source_manifest = verify_recovery01_boundary(root, contract)
    implementation = contract["offline_gate_implementation"]
    gate_source = root / implementation["source"]
    entrypoint = root / implementation["entrypoint"]
    if sha256_file(gate_source) != implementation["recovery02_sha256"]:
        raise RuntimeError("Recovery02 gate implementation hash failed")
    if sha256_file(entrypoint) != implementation["entrypoint_sha256"]:
        raise RuntimeError("Recovery02 gate entrypoint hash failed")
    recovery_root = root / contract["recovery_execution"]["root"]
    if recovery_root.exists():
        raise RuntimeError(
            "Recovery02 root already exists; refusing duplicate or overwrite"
        )
    logs_root = recovery_root / "logs"
    logs_root.mkdir(parents=True, exist_ok=False)
    manifest_path = recovery_root / contract["recovery_execution"]["manifest"]
    gate_path = recovery_root / contract["recovery_execution"]["gate_report"]
    latest_path = (
        recovery_root / contract["recovery_execution"]["latest_snapshot"]
    )
    receipt_path = recovery_root / contract["recovery_execution"]["receipt"]
    stdout_path = recovery_root / contract["recovery_execution"]["stdout_log"]
    stderr_path = recovery_root / contract["recovery_execution"]["stderr_log"]
    source_manifest_path = root / contract["recovery01_evidence"]["manifest"][
        "file"
    ]
    manifest = {
        "schema": (
            "skyguard.phase4.m01-landscape-visible-"
            "attempt06-recovery02-manifest.v1"
        ),
        "recovery_id": contract["recovery_id"],
        "contract_id": contract["contract_id"],
        "created_at_utc": utc_now(),
        "execution_type": "OFFLINE_PYTHON_ONLY",
        "source_recovery01_manifest": str(source_manifest_path),
        "source_recovery01_manifest_sha256": (
            contract["recovery01_evidence"]["manifest"]["sha256"]
        ),
        "source_recovery01_terminal_state": source_manifest["terminal_state"],
        "source_evidence_hashes_before": source_hashes_before,
        "source_evidence_hashes_after": None,
        "source_evidence_unchanged": None,
        "stage": None,
        "gate_report": str(gate_path),
        "receipt": str(receipt_path),
        "unreal_launched": False,
        "blender_launched": False,
        "captures_rerun": False,
        "profiles_rerun": False,
        "promotion_allowed": False,
        "terminal_state": "RUNNING",
        "errors": [],
    }
    write_json(manifest_path, manifest)
    started = utc_now()
    command = [
        sys.executable,
        str(entrypoint),
        "--manifest",
        str(source_manifest_path),
        "--output",
        str(gate_path),
        "--latest-output",
        str(latest_path),
    ]
    try:
        with stdout_path.open("w", encoding="utf-8") as stdout, (
            stderr_path.open("w", encoding="utf-8")
        ) as stderr:
            process = subprocess.run(
                command,
                cwd=root,
                stdout=stdout,
                stderr=stderr,
                timeout=args.timeout_seconds,
                check=False,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        allowed = contract["recovery_execution"]["gate_exit_codes_allowed"]
        manifest["stage"] = {
            "name": "offline_gate_schema_recovery02",
            "command": command,
            "started_at_utc": started,
            "finished_at_utc": utc_now(),
            "timeout_seconds": args.timeout_seconds,
            "exit_code": process.returncode,
            "stdout": str(stdout_path),
            "stderr": str(stderr_path),
        }
        if process.returncode not in allowed:
            raise RuntimeError(
                "Recovery02 offline gate process failed with exit "
                + str(process.returncode)
            )
        if not gate_path.is_file() or not latest_path.is_file():
            raise RuntimeError("Recovery02 gate outputs are missing")
        gate = read_json(gate_path)
        if gate != read_json(latest_path):
            raise RuntimeError("Recovery02 gate and latest snapshot differ")
        source_hashes_after = verify_recovery01_inventory(root, contract)
        if source_hashes_after != source_hashes_before:
            raise RuntimeError("Recovery01 evidence changed during Recovery02")
        receipt = {
            "schema": (
                "skyguard.phase4.m01-landscape-visible-"
                "attempt06-recovery02-receipt.v1"
            ),
            "recovery_id": contract["recovery_id"],
            "completed_at_utc": utc_now(),
            "execution_type": "OFFLINE_PYTHON_ONLY",
            "gate": gate.get("gate"),
            "technical_gate": gate.get("technical_gate"),
            "human_review_complete": gate.get("human_review_complete"),
            "gate_report": str(gate_path),
            "gate_report_sha256": sha256_file(gate_path),
            "latest_snapshot_sha256": sha256_file(latest_path),
            "source_recovery01_evidence_unchanged": True,
            "source_recovery01_evidence_file_count": len(
                source_hashes_before
            ),
            "unreal_launched": False,
            "captures_rerun": False,
            "profiles_rerun": False,
            "performance_evidence_fabricated": False,
            "promotion_allowed": False,
        }
        write_json(receipt_path, receipt)
        manifest["source_evidence_hashes_after"] = source_hashes_after
        manifest["source_evidence_unchanged"] = True
        manifest["gate"] = gate.get("gate")
        manifest["technical_gate"] = gate.get("technical_gate")
        manifest["terminal_state"] = "OFFLINE_GATE_COMPLETE"
    except Exception as error:
        manifest["errors"].append(str(error))
        manifest["terminal_state"] = "FAILED"
        raise
    finally:
        manifest["finished_at_utc"] = utc_now()
        write_json(manifest_path, manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
