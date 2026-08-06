"""Verify and summarize a headless Unreal Insights export for Phase 1 P1.4.

This verifier deliberately separates a successful, hash-bound headless export
from acceptance of P1.4.  The latter remains insufficient when the source trace
did not capture memory/VRAM evidence or when timer spikes still need contextual
review.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "skyguard.phase1.insights-review.v1"
DOMAIN_PATTERNS = {
    "loading_streaming": re.compile(
        r"load|stream|io(dispatcher)?|asset|package|postload", re.IGNORECASE
    ),
    "shader_pso": re.compile(
        r"shader|pipeline.?state|\bpso\b|compile(?!din)", re.IGNORECASE
    ),
    "niagara": re.compile(r"niagara", re.IGNORECASE),
}
CRITICAL_LOG_RE = re.compile(
    r"Failed to open the response file|Analysis failed|Fatal error|"
    r"LowLevelFatalError|Assertion failed|Unhandled Exception|"
    r"EXCEPTION_ACCESS_VIOLATION",
    re.IGNORECASE,
)
ANALYSIS_COMPLETE_RE = re.compile(r"Analysis has completed", re.IGNORECASE)
AUTOQUIT_RE = re.compile(
    r"AutoQuit parameter and session analysis is complete", re.IGNORECASE
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_record(path: Path) -> dict[str, Any]:
    exists = path.is_file()
    return {
        "path": str(path),
        "exists": exists,
        "bytes": path.stat().st_size if exists else 0,
        "sha256": sha256(path) if exists else None,
    }


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]], str | None]:
    if not path.is_file() or path.stat().st_size == 0:
        return [], [], "missing_or_empty"
    try:
        with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as handle:
            reader = csv.DictReader(handle)
            headers = list(reader.fieldnames or [])
            return headers, list(reader), None
    except (OSError, csv.Error) as exc:
        return [], [], f"{type(exc).__name__}: {exc}"


def number(value: str | None) -> float | None:
    try:
        return float(value) if value not in (None, "") else None
    except (TypeError, ValueError):
        return None


def analyze_domain(
    name: str,
    event_rows: list[dict[str, str]],
    statistic_rows: list[dict[str, str]],
) -> dict[str, Any]:
    pattern = DOMAIN_PATTERNS[name]
    matching_events = [
        row for row in event_rows if pattern.search(row.get("TimerName", ""))
    ]
    matching_statistics = [
        row for row in statistic_rows if pattern.search(row.get("Name", ""))
    ]
    durations = [
        value
        for value in (number(row.get("Duration")) for row in matching_events)
        if value is not None
    ]
    maximums = [
        value
        for value in (number(row.get("I.Max")) for row in matching_statistics)
        if value is not None
    ]
    max_duration = max(durations + maximums, default=None)
    longest = sorted(
        (
            {
                "timer": row.get("TimerName") or row.get("Name"),
                "thread": row.get("ThreadName"),
                "start_seconds": number(row.get("StartTime")),
                "duration_seconds": number(row.get("Duration"))
                if row.get("Duration") is not None
                else number(row.get("I.Max")),
            }
            for row in matching_events + matching_statistics
        ),
        key=lambda item: item["duration_seconds"] or 0.0,
        reverse=True,
    )[:25]
    return {
        "status": "OBSERVED" if matching_events or matching_statistics else "NO_MATCHES",
        "event_count": len(matching_events),
        "statistic_row_count": len(matching_statistics),
        "max_observed_duration_seconds": max_duration,
        "review_candidates_over_100ms": sum(
            1
            for item in longest
            if (item["duration_seconds"] or 0.0) >= 0.1
        ),
        "longest_candidates": longest,
        "interpretation": (
            "Descriptive timer evidence only. Timer-name matching and aggregate "
            "duration do not by themselves prove a user-visible hitch."
        ),
    }


def verify(manifest_path: Path) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    log_path = Path(manifest["execution"]["log_path"])
    log_text = (
        log_path.read_text(encoding="utf-8", errors="replace")
        if log_path.is_file()
        else ""
    )

    binding_checks = []
    for binding in manifest.get("bindings", []):
        path = Path(binding["path"])
        actual = file_record(path)
        expected_sha = binding.get("sha256")
        binding_checks.append(
            {
                "label": binding.get("label"),
                **actual,
                "expected_sha256": expected_sha,
                "hash_matches": bool(actual["exists"])
                and actual["sha256"] == expected_sha,
            }
        )

    export_reports: dict[str, Any] = {}
    parsed_rows: dict[str, list[dict[str, str]]] = {}
    for name, raw_path in manifest.get("exports", {}).items():
        path = Path(raw_path)
        headers, rows, error = read_csv(path)
        parsed_rows[name] = rows
        export_reports[name] = {
            **file_record(path),
            "headers": headers,
            "row_count": len(rows),
            "parse_error": error,
            "parseable": error is None and bool(headers),
        }

    required_exports = {"threads", "timers", "timer_statistics"}
    required_parseable = all(
        export_reports.get(name, {}).get("parseable", False)
        for name in required_exports
    )
    statistic_rows = parsed_rows.get("timer_statistics", [])
    domains = {
        "loading_streaming": analyze_domain(
            "loading_streaming",
            parsed_rows.get("loading_streaming_events", []),
            statistic_rows,
        ),
        "shader_pso": analyze_domain(
            "shader_pso",
            parsed_rows.get("shader_pso_events", []),
            statistic_rows,
        ),
        "niagara": analyze_domain(
            "niagara",
            parsed_rows.get("niagara_events", []),
            statistic_rows,
        ),
    }

    requested_channels = [
        str(channel).lower() for channel in manifest.get("requested_channels", [])
    ]
    memory_captured = "memory" in requested_channels
    execution = manifest.get("execution", {})
    critical_lines = [
        line.strip()
        for line in log_text.splitlines()
        if CRITICAL_LOG_RE.search(line)
    ][:50]
    headless_pass = (
        manifest.get("schema") == "skyguard.phase1.insights-review-run.v1"
        and execution.get("exit_code") == 0
        and not execution.get("timed_out", False)
        and all(check["hash_matches"] for check in binding_checks)
        and required_parseable
        and ANALYSIS_COMPLETE_RE.search(log_text) is not None
        and AUTOQUIT_RE.search(log_text) is not None
        and not critical_lines
    )

    blockers = []
    if not memory_captured:
        blockers.append(
            "The accepted trace channel contract omits memory; Memory Insights "
            "and stable process-memory behavior cannot be accepted from this trace."
        )
    blockers.append(
        "The accepted trace has no explicit VRAM residency/budget evidence; CPU/GPU "
        "timer exports are not a substitute for a VRAM residency review."
    )
    if any(
        domain["review_candidates_over_100ms"] > 0 for domain in domains.values()
    ):
        blockers.append(
            "One or more name-matched timer candidates exceed 100 ms and require "
            "contextual review in the timeline before they can be classified."
        )

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "attempt_id": manifest.get("attempt_id"),
        "terminal_state": (
            "EXECUTION_COMPLETE" if headless_pass else "EXECUTION_FAILED"
        ),
        "headless_export_gate": "PASS" if headless_pass else "FAIL",
        "p1_4_disposition": "INSUFFICIENT_EVIDENCE",
        "manifest": str(manifest_path),
        "bindings": binding_checks,
        "execution": {
            **execution,
            "analysis_complete_logged": ANALYSIS_COMPLETE_RE.search(log_text)
            is not None,
            "autoquit_complete_logged": AUTOQUIT_RE.search(log_text) is not None,
            "critical_lines": critical_lines,
        },
        "exports": export_reports,
        "domains": {
            **domains,
            "memory_vram": {
                "status": "NOT_CAPTURED"
                if not memory_captured
                else "CAPTURE_REQUESTED_NOT_ACCEPTED",
                "requested_memory_channel": memory_captured,
                "vram_residency_evidence": False,
            },
        },
        "p1_4_blockers": blockers,
        "required_interactive_action": (
            "Open the hash-bound trace in Unreal Insights 5.8, select the post-warmup "
            "combat interval in Timing Insights, inspect the exported loading/streaming, "
            "shader/PSO, and Niagara candidates in timeline context, and save a dated "
            "review record with screenshots and pass/fail findings."
        ),
        "required_recapture_action": (
            "Capture a new input-driven combat trace with the memory channel and "
            "explicit GPU-memory/VRAM budget telemetry enabled; include ADS+rifle, "
            "Igla launch, drone breakup, boss destruction, weather transition, and "
            "fast camera movement in the measured interval."
        ),
        "limitations": [
            "This gate does not launch visible Unreal or mutate system settings.",
            "Timer-name matching is triage, not proof of a visual hitch.",
            "A successful headless export proves trace readability and reproducible "
            "tables, not P1.4 acceptance.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = verify(args.manifest.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["headless_export_gate"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
