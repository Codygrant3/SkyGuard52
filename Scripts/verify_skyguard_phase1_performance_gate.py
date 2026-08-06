"""Verify a bounded Skyguard Phase 1 profile without trusting process exit codes.

The PowerShell supervisor owns processes. This verifier independently checks its
manifest, raw logs, native automation completion, D3D12 startup, benchmark exit,
CSV/Insights artifacts, and fatal/error signatures. It never promotes a smoke
run into a frame-time pass unless a parseable CSV provides the required data.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import math
import re
import shutil
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


csv.field_size_limit(min(sys.maxsize, 64 * 1024 * 1024))


FATAL_PATTERNS = {
    "fatal_error": re.compile(r"Fatal error|LowLevelFatalError", re.IGNORECASE),
    "assertion": re.compile(r"Assertion failed", re.IGNORECASE),
    "gpu_crash": re.compile(
        r"GPU Crash|DXGI_ERROR_DEVICE_(?:REMOVED|HUNG|RESET)|Aftermath.*crash",
        re.IGNORECASE,
    ),
    "out_of_memory": re.compile(
        r"Out of video memory|Ran out of memory|OOM detected", re.IGNORECASE
    ),
    "blueprint_error": re.compile(
        r"Blueprint Runtime Error|LogBlueprint: Error|LogProperty: Error|"
        r"LogLinker: Error|LogClass: Error",
        re.IGNORECASE,
    ),
    "unhandled_exception": re.compile(
        r"Unhandled Exception|EXCEPTION_ACCESS_VIOLATION", re.IGNORECASE
    ),
}

AUTOMATION_STARTED_RE = re.compile(
    r"Test Started\..*Path=\{(?P<path>Skyguard52\.Boss\.Pathfinder[^}]*)\}"
)
AUTOMATION_COMPLETED_RE = re.compile(
    r"Test Completed\. Result=\{(?P<result>[^}]*)\}.*"
    r"Path=\{(?P<path>Skyguard52\.Boss\.Pathfinder[^}]*)\}"
)
AUTOMATION_QUEUE_RE = re.compile(
    r"Automation Test Queue Empty (?P<count>\d+) tests performed"
)


def read_text(path: Path | None) -> str:
    if path is None or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def scan_log(text: str) -> dict[str, Any]:
    matches: dict[str, list[str]] = {}
    for name, pattern in FATAL_PATTERNS.items():
        lines = [line.strip() for line in text.splitlines() if pattern.search(line)]
        matches[name] = lines[:25]
    return {
        "counts": {name: len(lines) for name, lines in matches.items()},
        "samples": matches,
        "total_critical_count": sum(len(lines) for lines in matches.values()),
    }


def analyze_automation(text: str, expected_filter: str) -> dict[str, Any]:
    started = sorted(set(match.group("path") for match in AUTOMATION_STARTED_RE.finditer(text)))
    completed = [
        {"path": match.group("path"), "result": match.group("result")}
        for match in AUTOMATION_COMPLETED_RE.finditer(text)
    ]
    queue_matches = list(AUTOMATION_QUEUE_RE.finditer(text))
    performed_count = int(queue_matches[-1].group("count")) if queue_matches else None
    success_paths = sorted(
        item["path"] for item in completed if item["result"].lower() == "success"
    )
    failed = [item for item in completed if item["result"].lower() != "success"]
    required_paths = {
        f"{expected_filter}.EncounterFlightAndAttackController",
        f"{expected_filter}.SequenceAndBoundedDestruction",
    }
    return {
        "expected_filter": expected_filter,
        "required_paths": sorted(required_paths),
        "started_paths": started,
        "completed": completed,
        "success_paths": success_paths,
        "failed": failed,
        "queue_empty": bool(queue_matches),
        "performed_count": performed_count,
        "pass": required_paths.issubset(set(success_paths))
        and not failed
        and performed_count == len(required_paths),
    }


def open_csv(path: Path):
    if path.suffix.lower() == ".gz":
        return gzip.open(path, "rt", encoding="utf-8-sig", errors="replace", newline="")
    return path.open("r", encoding="utf-8-sig", errors="replace", newline="")


def number(value: str) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if math.isfinite(parsed) else None


def percentile(values: list[float], percentile_value: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    rank = (len(ordered) - 1) * percentile_value
    low = math.floor(rank)
    high = math.ceil(rank)
    if low == high:
        return ordered[low]
    return ordered[low] * (high - rank) + ordered[high] * (rank - low)


def analyze_csv(path: Path, warmup_frames: int = 120) -> dict[str, Any]:
    result: dict[str, Any] = {
        "path": str(path),
        "exists": path.is_file(),
        "size_bytes": path.stat().st_size if path.is_file() else 0,
        "parseable": False,
        "frame_count": 0,
        "warmup_frames_discarded": 0,
        "frame_time_column": None,
        "gpu_time_column": None,
        "metrics": {},
    }
    if not path.is_file() or path.stat().st_size == 0:
        return result
    try:
        with open_csv(path) as handle:
            rows = list(csv.reader(handle))
    except (OSError, csv.Error):
        return result

    header_index = None
    for index, row in enumerate(rows):
        lowered = [cell.strip().lower() for cell in row]
        if any(
            cell in {"frametime", "frame time", "frame time (ms)", "frame"}
            or "frametime" in cell
            for cell in lowered
        ):
            header_index = index
            break
    if header_index is None:
        return result

    header = [cell.strip() for cell in rows[header_index]]
    data_rows = rows[header_index + 1 :]
    frame_candidates = [
        index
        for index, name in enumerate(header)
        if name.lower() in {"frametime", "frame time", "frame time (ms)"}
        or "frametime" in name.lower()
    ]
    gpu_candidates = [
        index
        for index, name in enumerate(header)
        if name.lower()
        in {"gpu", "gputime", "gpu time", "gpu time (ms)", "gpu frametime"}
        or "gpu frametime" in name.lower()
    ]
    if not frame_candidates:
        return result

    frame_index = frame_candidates[0]
    gpu_index = gpu_candidates[0] if gpu_candidates else None
    frame_values_all: list[float] = []
    gpu_values_all: list[float] = []
    for row in data_rows:
        if frame_index >= len(row):
            continue
        frame_value = number(row[frame_index])
        if frame_value is not None and 0.0 < frame_value < 60_000.0:
            frame_values_all.append(frame_value)
        if gpu_index is not None and gpu_index < len(row):
            gpu_value = number(row[gpu_index])
            if gpu_value is not None and 0.0 <= gpu_value < 60_000.0:
                gpu_values_all.append(gpu_value)

    if not frame_values_all:
        return result
    discard_count = min(warmup_frames, max(0, len(frame_values_all) - 60))
    frame_values = frame_values_all[discard_count:]
    # GPU data may contain a different number of non-empty samples. Apply the
    # same bounded warm-up only when enough GPU samples exist.
    gpu_discard = min(discard_count, max(0, len(gpu_values_all) - 60))
    gpu_values = gpu_values_all[gpu_discard:]
    result["parseable"] = True
    result["frame_count"] = len(frame_values)
    result["warmup_frames_discarded"] = discard_count
    result["frame_time_column"] = header[frame_index]
    result["gpu_time_column"] = header[gpu_index] if gpu_index is not None else None
    result["metrics"] = {
        "frame_time_ms_mean": round(statistics.fmean(frame_values), 4),
        "frame_time_ms_median": round(statistics.median(frame_values), 4),
        "frame_time_ms_p95": round(percentile(frame_values, 0.95) or 0.0, 4),
        "frame_time_ms_p99": round(percentile(frame_values, 0.99) or 0.0, 4),
        "frame_time_ms_max": round(max(frame_values), 4),
        "hitch_over_50ms_count": sum(value > 50.0 for value in frame_values),
        "hitch_over_100ms_count": sum(value > 100.0 for value in frame_values),
        "gpu_time_ms_mean": round(statistics.fmean(gpu_values), 4)
        if gpu_values
        else None,
        "gpu_time_ms_p95": round(percentile(gpu_values, 0.95) or 0.0, 4)
        if gpu_values
        else None,
    }
    return result


def stage_by_name(manifest: dict[str, Any], name: str) -> dict[str, Any] | None:
    return next((stage for stage in manifest.get("stages", []) if stage.get("name") == name), None)


def stage_log(stage: dict[str, Any] | None) -> tuple[str, dict[str, Any]]:
    if not stage:
        return "", scan_log("")
    stdout = read_text(Path(stage["stdout"])) if stage.get("stdout") else ""
    stderr = read_text(Path(stage["stderr"])) if stage.get("stderr") else ""
    combined = stdout + "\n" + stderr
    return combined, scan_log(combined)


def clean_process_completion(stage: dict[str, Any] | None) -> bool:
    """Require bounded observed exit; reject an explicit nonzero exit code.

    Windows PowerShell 5.1 can lose ExitCode on a redirected native process
    after the asynchronous readers close. In that case semantic log completion
    remains mandatory for each stage and the missing code stays explicit in the
    report rather than being fabricated.
    """
    if stage is None or stage.get("timed_out"):
        return False
    if stage.get("process_exit_observed") is False:
        return False
    exit_code = stage.get("exit_code")
    return exit_code is None or exit_code == 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--latest-output", type=Path)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8-sig"))
    build_stage = stage_by_name(manifest, "build_development_game")
    automation_stage = stage_by_name(
        manifest, "pathfinder_combat_destruction_automation"
    )
    runtime_stage = stage_by_name(manifest, "d3d12_runtime_profile")

    build_text, build_scan = stage_log(build_stage)
    automation_text, automation_scan = stage_log(automation_stage)
    runtime_text, runtime_scan = stage_log(runtime_stage)
    automation = analyze_automation(
        automation_text, manifest.get("automation_filter", "Skyguard52.Boss.Pathfinder")
    )

    trace_path = Path(manifest.get("artifacts", {}).get("trace", ""))
    csv_paths = [
        Path(path) for path in manifest.get("artifacts", {}).get("csv_files", [])
    ]
    for match in re.finditer(
        r"Capture Ended\. Writing CSV to file\s*:\s*(?P<path>[^\r\n]+)",
        runtime_text,
        re.IGNORECASE,
    ):
        logged_path = Path(match.group("path").strip())
        if logged_path not in csv_paths:
            csv_paths.append(logged_path)
    csv_results = [analyze_csv(path) for path in csv_paths]
    parseable_csv = [item for item in csv_results if item["parseable"]]
    selected_csv = max(parseable_csv, key=lambda item: item["frame_count"], default=None)

    terminal_state = manifest.get("terminal_state")
    validate_only = bool(manifest.get("controls", {}).get("validate_only"))
    skip_build = bool(manifest.get("controls", {}).get("skip_build"))
    skip_automation = bool(manifest.get("controls", {}).get("skip_automation"))
    requested_profile = manifest.get("requested_profile", {})
    promotion_profile = (
        not skip_build
        and not skip_automation
        and requested_profile.get("duration_seconds", 0) >= 60
        and requested_profile.get("resolution_x", 0) >= 1920
        and requested_profile.get("resolution_y", 0) >= 1080
    )

    build_pass = (
        skip_build
        or (
            build_stage is not None
            and clean_process_completion(build_stage)
            and build_scan["total_critical_count"] == 0
            and re.search(
                r"Result:\s*Succeeded|Target is up to date",
                build_text,
                re.IGNORECASE,
            )
            is not None
            and re.search(r"Result:\s*Failed", build_text, re.IGNORECASE) is None
        )
    )
    automation_pass = skip_automation or (
        automation_stage is not None
        and clean_process_completion(automation_stage)
        and automation_scan["total_critical_count"] == 0
        and automation["pass"]
    )
    runtime_started = bool(
        re.search(r"Running engine for game: Skyguard52", runtime_text)
        and re.search(r"rhiname=\"D3D12\"|verbatimrhiname=\"D3D12\"", runtime_text)
    )
    map_loaded = manifest.get("map", "") in runtime_text and bool(
        re.search(r"Bringing World .* up for play|LoadMap:", runtime_text)
    )
    benchmark_exit = bool(
        re.search(r"RequestExit.*Benchmarking|reason:.*Benchmarking", runtime_text)
    )
    runtime_pass = (
        runtime_stage is not None
        and clean_process_completion(runtime_stage)
        and runtime_scan["total_critical_count"] == 0
        and runtime_started
        and map_loaded
        and benchmark_exit
    )
    trace_pass = trace_path.is_file() and trace_path.stat().st_size >= 4096
    csv_artifact_pass = bool(csv_paths) and any(
        item["exists"] and item["size_bytes"] >= 1024 for item in csv_results
    )

    smoke_checks = {
        "bounded_processes": all(
            not stage.get("timed_out") for stage in manifest.get("stages", [])
        ),
        "build": build_pass,
        "combat_destruction_automation": automation_pass,
        "runtime_d3d12": runtime_pass,
        "insights_trace": trace_pass,
        "csv_artifact": csv_artifact_pass,
    }
    smoke_pass = all(smoke_checks.values())

    performance_checks: dict[str, bool | None] = {
        "mean_frame_time_at_or_below_16_7_ms": None,
        "p95_frame_time_at_or_below_22_2_ms": None,
        "max_hitch_at_or_below_100_ms": None,
        "zero_hitches_over_100_ms": None,
    }
    if selected_csv:
        metrics = selected_csv["metrics"]
        performance_checks = {
            "mean_frame_time_at_or_below_16_7_ms": metrics["frame_time_ms_mean"]
            <= 16.7,
            "p95_frame_time_at_or_below_22_2_ms": metrics["frame_time_ms_p95"]
            <= 22.2,
            "max_hitch_at_or_below_100_ms": metrics["frame_time_ms_max"] <= 100.0,
            "zero_hitches_over_100_ms": metrics["hitch_over_100ms_count"] == 0,
        }
    performance_gate = (
        "PASS"
        if selected_csv and all(performance_checks.values())
        else "FAIL"
        if selected_csv
        else "NOT_MEASURED"
    )

    if validate_only:
        gate = "VALIDATED_NOT_EXECUTED"
    elif terminal_state == "BLOCKED_ACTIVE_UNREAL_PROCESS":
        gate = "BLOCKED_ACTIVE_UNREAL_PROCESS"
    elif smoke_pass and performance_gate == "PASS":
        gate = "PASS" if promotion_profile else "DIAGNOSTIC_PASS_NOT_PROMOTABLE"
    elif smoke_pass and performance_gate == "NOT_MEASURED":
        gate = "SMOKE_PASS_PERFORMANCE_UNVERIFIED"
    else:
        gate = "FAIL"

    report = {
        "schema": "skyguard.phase1.performance-gate.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "gate": gate,
        "attempt_id": manifest.get("attempt_id"),
        "manifest": str(args.manifest),
        "terminal_state": terminal_state,
        "runtime_selection": manifest.get("runtime_selection"),
        "requested_profile": manifest.get("requested_profile"),
        "promotion_profile": promotion_profile,
        "smoke_gate": "PASS" if smoke_pass else "FAIL",
        "smoke_checks": smoke_checks,
        "performance_gate": performance_gate,
        "performance_checks": performance_checks,
        "selected_csv": selected_csv,
        "csv_artifacts": csv_results,
        "trace": {
            "path": str(trace_path),
            "exists": trace_path.is_file(),
            "size_bytes": trace_path.stat().st_size if trace_path.is_file() else 0,
        },
        "automation": automation,
        "log_scans": {
            "build": build_scan,
            "automation": automation_scan,
            "runtime": runtime_scan,
        },
        "stages": manifest.get("stages", []),
        "limitations": [
            "The current native combat automation exercises Pathfinder rifle, Igla, pilot-command, and bounded-destruction logic under NullRHI; it is not an input-driven packaged-game playthrough.",
            "A performance PASS requires a parseable Unreal CSV. Exit code, normal benchmark exit, and a trace file alone prove only a bounded D3D12 smoke.",
            "This harness measures one machine, map, resolution, quality state, and run. Promotion still requires repeated runs and a longer manual or Gauntlet combat soak.",
            "VRAM residency and shader/PSO warm-up acceptance require dedicated Insights review until stable project-specific CSV counters are authored.",
        ],
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if args.latest_output:
        args.latest_output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(args.output, args.latest_output)
    print(json.dumps({"gate": gate, "report": str(args.output)}, indent=2))
    return (
        0
        if gate
        in {
            "PASS",
            "DIAGNOSTIC_PASS_NOT_PROMOTABLE",
            "SMOKE_PASS_PERFORMANCE_UNVERIFIED",
            "VALIDATED_NOT_EXECUTED",
        }
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
