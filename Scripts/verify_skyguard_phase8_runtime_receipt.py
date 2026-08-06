#!/usr/bin/env python3
"""Independently verify a packaged Skyguard Phase 8 runtime receipt.

The receipt is intentionally treated as untrusted input.  This verifier checks
the executable hash, case cardinality and uniqueness, referenced artifacts,
launch logs, exit state, and critical Unreal signatures before returning PASS.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "skyguard.phase8.runtime-validation-receipt.v1"
REPORT_SCHEMA = "skyguard.phase8.runtime-validation-receipt-verification.v1"
MINIMUM_CASES = {
    "input_cases": 8,
    "save_cases": 4,
    "settings_cases": 5,
}
CRITICAL_PATTERNS = {
    "fatal_error": re.compile(r"\bFatal error:", re.IGNORECASE),
    "assertion": re.compile(r"Assertion failed:|LowLevelFatalError", re.IGNORECASE),
    "gpu_crash": re.compile(r"GPU crash|GPU Crashed or D3D Device Removed", re.IGNORECASE),
    "out_of_memory": re.compile(r"Out of memory|Ran out of memory", re.IGNORECASE),
    "access_violation": re.compile(r"EXCEPTION_ACCESS_VIOLATION", re.IGNORECASE),
    "unhandled_exception": re.compile(r"Unhandled Exception:", re.IGNORECASE),
    "blueprint_error": re.compile(r"Blueprint Runtime Error:", re.IGNORECASE),
    "property_error": re.compile(r"Failed to find property|Unknown property", re.IGNORECASE),
    "linker_error": re.compile(r"LogLinker: Error:|Can't find file for asset", re.IGNORECASE),
    "class_error": re.compile(r"Failed to find class|Could not find class", re.IGNORECASE),
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError("receipt root must be an object")
    return value


def resolve_artifact(value: Any, receipt_dir: Path) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        return None
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = receipt_dir / candidate
    return candidate.resolve()


def add_check(
    checks: dict[str, bool],
    issues: list[str],
    name: str,
    passed: bool,
    issue: str,
) -> None:
    checks[name] = bool(passed)
    if not passed:
        issues.append(issue)


def verify_case_group(
    receipt: dict[str, Any],
    receipt_dir: Path,
    group_name: str,
    minimum: int,
    checks: dict[str, bool],
    issues: list[str],
    artifact_records: list[dict[str, Any]],
) -> None:
    evidence = receipt.get("evidence")
    group = evidence.get(group_name) if isinstance(evidence, dict) else None
    group_is_list = isinstance(group, list)
    add_check(
        checks,
        issues,
        f"{group_name}_is_array",
        group_is_list,
        f"{group_name} must be an array",
    )
    if not group_is_list:
        return

    add_check(
        checks,
        issues,
        f"{group_name}_minimum_count",
        len(group) >= minimum,
        f"{group_name} requires at least {minimum} cases; found {len(group)}",
    )

    names: list[str] = []
    all_pass = True
    all_artifacts = True
    for index, case in enumerate(group):
        if not isinstance(case, dict):
            issues.append(f"{group_name}[{index}] must be an object")
            all_pass = False
            all_artifacts = False
            continue

        name = case.get("name")
        result = case.get("result")
        if not isinstance(name, str) or not name.strip():
            issues.append(f"{group_name}[{index}] has no non-empty name")
            all_pass = False
        else:
            names.append(name.strip())

        if result != "PASS":
            issues.append(f"{group_name}[{index}] result is not PASS")
            all_pass = False

        artifact = resolve_artifact(case.get("artifact"), receipt_dir)
        artifact_exists = bool(artifact and artifact.is_file())
        if not artifact_exists:
            issues.append(
                f"{group_name}[{index}] artifact is missing or not a file: "
                f"{case.get('artifact')!r}"
            )
            all_artifacts = False
            continue
        artifact_records.append(
            {
                "group": group_name,
                "case": name,
                "path": str(artifact),
                "size_bytes": artifact.stat().st_size,
                "sha256": sha256_file(artifact),
            }
        )

    add_check(
        checks,
        issues,
        f"{group_name}_all_pass",
        all_pass,
        f"{group_name} contains an invalid or non-PASS case",
    )
    unique_names = len(names) == len(set(names))
    add_check(
        checks,
        issues,
        f"{group_name}_unique_names",
        unique_names,
        f"{group_name} contains duplicate case names",
    )
    add_check(
        checks,
        issues,
        f"{group_name}_artifacts_exist",
        all_artifacts,
        f"{group_name} does not have a readable artifact for every case",
    )


def verify_receipt(
    receipt_path: Path,
    executable_path: Path,
    expected_attempt_id: str | None,
) -> dict[str, Any]:
    checks: dict[str, bool] = {}
    issues: list[str] = []
    artifacts: list[dict[str, Any]] = []
    launches_out: list[dict[str, Any]] = []

    receipt = read_json(receipt_path)
    add_check(
        checks,
        issues,
        "schema",
        receipt.get("schema") == SCHEMA,
        f"schema must be {SCHEMA}",
    )
    add_check(
        checks,
        issues,
        "declared_gate",
        receipt.get("gate") == "PASS",
        "receipt gate is not PASS",
    )
    add_check(
        checks,
        issues,
        "package_configuration",
        receipt.get("package_configuration") in {"Development", "Shipping"},
        "package_configuration must be Development or Shipping",
    )

    attempt_id = receipt.get("package_attempt_id")
    attempt_ok = isinstance(attempt_id, str) and bool(attempt_id.strip())
    if expected_attempt_id is not None:
        attempt_ok = attempt_ok and attempt_id == expected_attempt_id
    add_check(
        checks,
        issues,
        "package_attempt_id",
        attempt_ok,
        "package_attempt_id is empty or does not match the expected attempt",
    )

    executable_exists = executable_path.is_file()
    add_check(
        checks,
        issues,
        "package_executable_exists",
        executable_exists,
        f"package executable does not exist: {executable_path}",
    )
    executable_hash = sha256_file(executable_path) if executable_exists else None
    declared_hash = receipt.get("package_executable_sha256")
    hash_shape_ok = isinstance(declared_hash, str) and bool(
        re.fullmatch(r"[0-9a-f]{64}", declared_hash)
    )
    add_check(
        checks,
        issues,
        "package_executable_hash_shape",
        hash_shape_ok,
        "package_executable_sha256 is not lowercase SHA-256",
    )
    add_check(
        checks,
        issues,
        "package_executable_hash_matches",
        bool(executable_hash and declared_hash == executable_hash),
        "receipt executable hash does not match the supplied package executable",
    )

    for field in ("input", "save_round_trip", "settings_round_trip"):
        add_check(
            checks,
            issues,
            field,
            receipt.get(field) == "PASS",
            f"{field} is not PASS",
        )

    evidence = receipt.get("evidence")
    evidence_ok = isinstance(evidence, dict)
    add_check(
        checks,
        issues,
        "evidence_object",
        evidence_ok,
        "evidence must be an object",
    )

    for group_name, minimum in MINIMUM_CASES.items():
        verify_case_group(
            receipt,
            receipt_path.parent,
            group_name,
            minimum,
            checks,
            issues,
            artifacts,
        )

    launches = evidence.get("launches") if evidence_ok else None
    launches_is_list = isinstance(launches, list)
    add_check(
        checks,
        issues,
        "launches_is_array",
        launches_is_list,
        "launches must be an array",
    )
    if launches_is_list:
        add_check(
            checks,
            issues,
            "launches_minimum_count",
            len(launches) >= 2,
            f"at least two launches are required; found {len(launches)}",
        )
        launch_state_ok = True
        launch_logs_ok = True
        critical_clean = True
        seen_logs: set[str] = set()
        for index, launch in enumerate(launches):
            if not isinstance(launch, dict):
                issues.append(f"launches[{index}] must be an object")
                launch_state_ok = False
                launch_logs_ok = False
                continue
            state_ok = (
                isinstance(launch.get("pid"), int)
                and launch["pid"] > 0
                and launch.get("exit_code") == 0
                and launch.get("timed_out") is False
            )
            if not state_ok:
                issues.append(f"launches[{index}] has invalid process outcome")
                launch_state_ok = False

            log_path = resolve_artifact(launch.get("log"), receipt_path.parent)
            if not log_path or not log_path.is_file():
                issues.append(f"launches[{index}] log is missing: {launch.get('log')!r}")
                launch_logs_ok = False
                continue
            canonical_log = str(log_path).casefold()
            if canonical_log in seen_logs:
                issues.append(f"launches[{index}] reuses another launch log")
                launch_logs_ok = False
            seen_logs.add(canonical_log)

            log_text = log_path.read_text(encoding="utf-8", errors="replace")
            matched = [
                name for name, pattern in CRITICAL_PATTERNS.items() if pattern.search(log_text)
            ]
            if matched:
                critical_clean = False
                issues.append(
                    f"launches[{index}] log contains critical signatures: "
                    + ", ".join(matched)
                )
            launches_out.append(
                {
                    "pid": launch.get("pid"),
                    "exit_code": launch.get("exit_code"),
                    "timed_out": launch.get("timed_out"),
                    "log": str(log_path),
                    "log_size_bytes": log_path.stat().st_size,
                    "log_sha256": sha256_file(log_path),
                    "critical_signatures": matched,
                }
            )
        add_check(
            checks,
            issues,
            "launch_process_outcomes",
            launch_state_ok,
            "one or more launches did not exit cleanly",
        )
        add_check(
            checks,
            issues,
            "launch_logs_unique_and_present",
            launch_logs_ok,
            "launch logs are missing, invalid, or reused",
        )
        add_check(
            checks,
            issues,
            "launch_logs_no_critical_signatures",
            critical_clean,
            "one or more launch logs contain critical Unreal signatures",
        )

    passed = bool(checks) and all(checks.values())
    return {
        "schema": REPORT_SCHEMA,
        "verified_at_utc": datetime.now(timezone.utc).isoformat(),
        "gate": "PASS" if passed else "FAIL",
        "receipt": str(receipt_path),
        "receipt_sha256": sha256_file(receipt_path),
        "package_attempt_id": attempt_id,
        "package_configuration": receipt.get("package_configuration"),
        "package_executable": str(executable_path),
        "package_executable_sha256": executable_hash,
        "checks": checks,
        "issues": issues,
        "artifact_inventory": artifacts,
        "launch_inventory": launches_out,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", required=True, type=Path)
    parser.add_argument("--package-executable", required=True, type=Path)
    parser.add_argument("--expected-attempt-id")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    try:
        receipt_path = args.receipt.resolve(strict=True)
        executable_path = args.package_executable.resolve()
        report = verify_receipt(
            receipt_path,
            executable_path,
            args.expected_attempt_id,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        report = {
            "schema": REPORT_SCHEMA,
            "verified_at_utc": datetime.now(timezone.utc).isoformat(),
            "gate": "FAIL",
            "checks": {},
            "issues": [f"{type(exc).__name__}: {exc}"],
        }

    rendered = json.dumps(report, indent=2, sort_keys=False)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if report.get("gate") == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
