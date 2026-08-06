#!/usr/bin/env python3
"""Fail-closed verifier for the fresh Phase 7 second automation pass."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


EXPECTED_FAMILIES = {
    "Skyguard52.Mission01Integration": 2,
    "Skyguard52.Mission02": 4,
    "Skyguard52.Mission03": 4,
    "Skyguard52.Mission04": 4,
    "Skyguard52.Mission05": 4,
    "Skyguard52.Mission06": 4,
    "Skyguard52.Mission07": 4,
    "Skyguard52.Mission08": 4,
    "Skyguard52.Mission09": 5,
    "Skyguard52.Mission10": 4,
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify(manifest_path: Path) -> tuple[dict[str, Any], bool]:
    manifest = _load_json(manifest_path)
    failures: list[str] = []

    if manifest.get("schema") != "skyguard.phase7.second-pass-run.v1":
        failures.append("manifest_schema")
    if manifest.get("terminal_state") != "EXECUTION_COMPLETE":
        failures.append("terminal_state")

    stages = manifest.get("stages")
    if not isinstance(stages, list) or not stages:
        failures.append("stages_missing")
        stages = []
    for stage in stages:
        if stage.get("timed_out") is not False:
            failures.append(f"stage_timeout:{stage.get('name', 'unknown')}")
        if stage.get("exit_code") != 0:
            failures.append(f"stage_exit:{stage.get('name', 'unknown')}")

    report_path = Path(str(manifest.get("automation_report", "")))
    report: dict[str, Any] = {}
    if not report_path.is_file():
        failures.append("automation_report_missing")
    else:
        try:
            report = _load_json(report_path)
        except (OSError, json.JSONDecodeError):
            failures.append("automation_report_invalid")

    tests = report.get("tests", []) if isinstance(report, dict) else []
    if not isinstance(tests, list):
        failures.append("automation_tests_invalid")
        tests = []

    family_results: dict[str, Any] = {}
    seen_paths: set[str] = set()
    for prefix, expected_count in EXPECTED_FAMILIES.items():
        family_tests = [
            test
            for test in tests
            if str(test.get("fullTestPath", "")).startswith(prefix + ".")
        ]
        test_paths = [str(test.get("fullTestPath", "")) for test in family_tests]
        duplicates = sorted(
            {path for path in test_paths if test_paths.count(path) > 1}
        )
        unsuccessful = [
            path
            for path, test in zip(test_paths, family_tests)
            if test.get("state") != "Success"
            or int(test.get("warnings", 0)) != 0
            or int(test.get("errors", 0)) != 0
        ]
        if len(family_tests) != expected_count:
            failures.append(
                f"family_count:{prefix}:{len(family_tests)}:{expected_count}"
            )
        if duplicates:
            failures.append(f"family_duplicates:{prefix}")
        if unsuccessful:
            failures.append(f"family_unsuccessful:{prefix}")
        seen_paths.update(test_paths)
        family_results[prefix] = {
            "expected_count": expected_count,
            "actual_count": len(family_tests),
            "paths": sorted(test_paths),
            "duplicates": duplicates,
            "unsuccessful": unsuccessful,
            "pass": (
                len(family_tests) == expected_count
                and not duplicates
                and not unsuccessful
            ),
        }

    expected_total = sum(EXPECTED_FAMILIES.values())
    if len(seen_paths) != expected_total:
        failures.append(f"unique_expected_test_count:{len(seen_paths)}:{expected_total}")
    if int(report.get("failed", -1)) != 0:
        failures.append("report_failed")
    if int(report.get("notRun", -1)) != 0:
        failures.append("report_not_run")
    if int(report.get("inProcess", -1)) != 0:
        failures.append("report_in_process")
    if int(report.get("succeededWithWarnings", -1)) != 0:
        failures.append("report_succeeded_with_warnings")

    log_path = Path(str(manifest.get("automation_stdout", "")))
    critical_counts: dict[str, int] = {}
    patterns = {
        "fatal": "Fatal error:",
        "assert": "Assertion failed:",
        "ensure": "Ensure condition failed:",
        "gpu_timeout": "GPU timeout",
    }
    if not log_path.is_file():
        failures.append("automation_stdout_missing")
    else:
        text = log_path.read_text(encoding="utf-8", errors="replace")
        for label, pattern in patterns.items():
            critical_counts[label] = text.lower().count(pattern.lower())
            if critical_counts[label] > 0:
                failures.append(f"critical_log:{label}")

    failures = sorted(set(failures))
    passed = not failures
    result = {
        "schema": "skyguard.phase7.second-pass-gate.v1",
        "gate": "PASS" if passed else "FAIL",
        "terminal_state": manifest.get("terminal_state"),
        "manifest": str(manifest_path.resolve()),
        "manifest_sha256": _sha256(manifest_path),
        "automation_report": (
            {
                "path": str(report_path.resolve()),
                "sha256": _sha256(report_path),
                "succeeded": report.get("succeeded"),
                "failed": report.get("failed"),
                "not_run": report.get("notRun"),
                "in_process": report.get("inProcess"),
                "succeeded_with_warnings": report.get("succeededWithWarnings"),
            }
            if report_path.is_file()
            else None
        ),
        "expected_test_count": expected_total,
        "verified_unique_test_count": len(seen_paths),
        "families": family_results,
        "critical_log_counts": critical_counts,
        "failures": failures,
    }
    return result, passed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--latest-output", type=Path)
    args = parser.parse_args()

    result, passed = verify(args.manifest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if args.latest_output:
        args.latest_output.parent.mkdir(parents=True, exist_ok=True)
        args.latest_output.write_text(
            json.dumps(result, indent=2) + "\n", encoding="utf-8"
        )
    print(json.dumps(result, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
