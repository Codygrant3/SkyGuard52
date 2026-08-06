#!/usr/bin/env python3
"""Fail-closed verification for the M01 packaged input-combat performance gate.

The supervisor manifest and runtime receipts are untrusted inputs.  This
verifier re-hashes bound files, parses every CSV/memory series, scans every log,
and requires actual player-input telemetry inside each measured window.  It
never infers combat coverage from process exit, frame data, or native tests.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
import re
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MANIFEST_SCHEMA = "skyguard.m01.input-combat-performance.manifest.v1"
RUNTIME_SCHEMA = "skyguard.m01.input-combat.runtime-receipt.v1"
REPORT_SCHEMA = "skyguard.m01.input-combat-performance.verification.v1"
EXPECTED_STAGE_NAMES = ("combat_01", "combat_02", "combat_03", "soak_01")
EXPECTED_MAP = "/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_Playable_v1"
REQUIRED_EVENTS = {
    "aim_input": 1,
    "ads_started": 1,
    "ads_left_fire_overlap": 1,
    "rifle_shot": 5,
    "weapon_switch": 1,
    "igla_lock_acquired": 1,
    "igla_launch": 1,
    "drone_breakup": 1,
    "boss_destroyed": 1,
    "weather_visibility_transition": 1,
}
CRITICAL_PATTERNS = {
    "fatal_error": re.compile(r"\bFatal error:", re.IGNORECASE),
    "assertion": re.compile(r"Assertion failed:|LowLevelFatalError", re.IGNORECASE),
    "gpu_crash": re.compile(
        r"GPU crash|GPU Crashed or D3D Device Removed|DXGI_ERROR_DEVICE_",
        re.IGNORECASE,
    ),
    "out_of_memory": re.compile(
        r"Out of memory|Ran out of memory|Out of video memory", re.IGNORECASE
    ),
    "access_violation": re.compile(r"EXCEPTION_ACCESS_VIOLATION", re.IGNORECASE),
    "unhandled_exception": re.compile(r"Unhandled Exception:", re.IGNORECASE),
    "blueprint_error": re.compile(r"Blueprint Runtime Error:", re.IGNORECASE),
    "property_error": re.compile(
        r"Failed to find property|Unknown property", re.IGNORECASE
    ),
    "linker_error": re.compile(
        r"LogLinker: Error:|Can't find file for asset", re.IGNORECASE
    ),
    "class_error": re.compile(
        r"Failed to find class|Could not find class", re.IGNORECASE
    ),
}
PSO_PATTERNS = {
    "bundled_cache_opened": re.compile(
        r"Opened FPipelineCacheFile: .*Skyguard52_PCD3D_SM6\.stable"
        r"\.upipelinecache|FPipelineCacheFile\[Skyguard52\] opened Skyguard52",
        re.IGNORECASE,
    ),
    "precompile_completed": re.compile(
        r"FShaderPipelineCache .* completed \d+ tasks", re.IGNORECASE
    ),
    "zero_missing_shaders": re.compile(r"\b0 had missing shaders\b", re.IGNORECASE),
}
PSO_FAILURE = re.compile(
    r"Could not open FPipelineCacheFile|[1-9]\d*\s+had missing shaders|"
    r"missing shader(?:s)?\s*[:=]\s*[1-9]\d*",
    re.IGNORECASE,
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def resolve_path(value: Any, base: Path) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        return None
    path = Path(value)
    if not path.is_absolute():
        path = base / path
    return path.resolve()


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


def load_frame_analyzer():
    module_path = Path(__file__).with_name(
        "verify_skyguard_phase1_performance_gate.py"
    )
    spec = importlib.util.spec_from_file_location(
        "skyguard_phase1_frame_analyzer", module_path
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load frame analyzer: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.analyze_csv


def validate_file_record(
    record: Any,
    base: Path,
    issues: list[str],
    label: str,
) -> dict[str, Any]:
    result = {
        "label": label,
        "path": None,
        "exists": False,
        "bytes": None,
        "sha256": None,
        "declared_sha256": None,
        "valid": False,
    }
    if not isinstance(record, dict):
        issues.append(f"{label} record must be an object")
        return result
    path = resolve_path(record.get("path"), base)
    result["path"] = str(path) if path else None
    declared_hash = record.get("sha256")
    result["declared_sha256"] = declared_hash
    if not path or not path.is_file():
        issues.append(f"{label} file is missing: {record.get('path')!r}")
        return result
    result["exists"] = True
    result["bytes"] = path.stat().st_size
    result["sha256"] = sha256_file(path)
    hash_shape = isinstance(declared_hash, str) and bool(
        re.fullmatch(r"[0-9a-f]{64}", declared_hash)
    )
    size_ok = record.get("bytes") == path.stat().st_size
    result["valid"] = bool(
        hash_shape and size_ok and declared_hash == result["sha256"]
    )
    if not result["valid"]:
        issues.append(f"{label} bytes/hash does not match the bound file")
    return result


def parse_memory_series(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "path": str(path),
        "parseable": False,
        "sample_count": 0,
        "duration_seconds": 0.0,
        "working_set_start_bytes": None,
        "working_set_end_bytes": None,
        "working_set_peak_bytes": None,
        "tail_growth_bytes": None,
        "slope_bytes_per_minute": None,
    }
    if not path.is_file() or path.stat().st_size == 0:
        return result
    samples: list[tuple[float, float]] = []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            for row in csv.DictReader(stream):
                elapsed = float(row["elapsed_seconds"])
                working_set = float(row["working_set_bytes"])
                if elapsed >= 0.0 and working_set > 0.0:
                    samples.append((elapsed, working_set))
    except (OSError, ValueError, KeyError, csv.Error):
        return result
    if len(samples) < 2:
        return result
    samples.sort(key=lambda item: item[0])
    duration = samples[-1][0] - samples[0][0]
    if duration <= 0.0:
        return result

    # Ignore the first ten percent (capped at 60 seconds) so initial map/PSO
    # residency does not masquerade as a persistent leak.
    discard_until = samples[0][0] + min(60.0, duration * 0.10)
    stable = [sample for sample in samples if sample[0] >= discard_until]
    if len(stable) < 2:
        stable = samples
    xs = [item[0] for item in stable]
    ys = [item[1] for item in stable]
    x_mean = statistics.fmean(xs)
    y_mean = statistics.fmean(ys)
    denominator = sum((value - x_mean) ** 2 for value in xs)
    slope_per_second = (
        sum((x - x_mean) * (y - y_mean) for x, y in stable) / denominator
        if denominator > 0.0
        else 0.0
    )
    quarter = max(1, len(stable) // 4)
    first_median = statistics.median(y for _, y in stable[:quarter])
    last_median = statistics.median(y for _, y in stable[-quarter:])
    result.update(
        {
            "parseable": True,
            "sample_count": len(samples),
            "duration_seconds": round(duration, 3),
            "working_set_start_bytes": int(samples[0][1]),
            "working_set_end_bytes": int(samples[-1][1]),
            "working_set_peak_bytes": int(max(y for _, y in samples)),
            "tail_growth_bytes": int(last_median - first_median),
            "slope_bytes_per_minute": round(slope_per_second * 60.0, 3),
        }
    )
    return result


def scan_log(text: str) -> tuple[list[str], dict[str, bool]]:
    critical = [
        name for name, pattern in CRITICAL_PATTERNS.items() if pattern.search(text)
    ]
    pso = {name: bool(pattern.search(text)) for name, pattern in PSO_PATTERNS.items()}
    pso["no_cache_or_shader_failure"] = not bool(PSO_FAILURE.search(text))
    return critical, pso


def verify_runtime_receipt(
    receipt: dict[str, Any],
    expected_stage: str,
    expected_duration: int,
    issues: list[str],
) -> dict[str, Any]:
    checks: dict[str, bool] = {}
    add_check(
        checks,
        issues,
        "schema",
        receipt.get("schema") == RUNTIME_SCHEMA,
        f"{expected_stage}: runtime receipt schema is invalid",
    )
    add_check(
        checks,
        issues,
        "state_complete",
        receipt.get("state") == "COMPLETE",
        f"{expected_stage}: runtime state is not COMPLETE",
    )
    add_check(
        checks,
        issues,
        "declared_gate",
        receipt.get("gate") == "PASS",
        f"{expected_stage}: runtime gate is not PASS",
    )
    add_check(
        checks,
        issues,
        "run_id",
        receipt.get("run_id") == expected_stage,
        f"{expected_stage}: runtime run_id does not match",
    )
    add_check(
        checks,
        issues,
        "map",
        receipt.get("map") == EXPECTED_MAP,
        f"{expected_stage}: exact M01 playable map was not reported",
    )
    add_check(
        checks,
        issues,
        "resolution",
        receipt.get("resolution") == {"x": 1920, "y": 1080},
        f"{expected_stage}: runtime resolution is not exactly 1920x1080",
    )
    rhi = str(receipt.get("rhi", ""))
    add_check(
        checks,
        issues,
        "d3d12_sm6",
        "D3D12" in rhi.upper() and "SM6" in rhi.upper(),
        f"{expected_stage}: runtime did not report D3D12/SM6",
    )
    add_check(
        checks,
        issues,
        "player_input_source",
        receipt.get("input_source") in {"PlayerInput", "EnhancedInput"},
        f"{expected_stage}: input_source must prove PlayerInput or EnhancedInput",
    )
    add_check(
        checks,
        issues,
        "not_automation_injected",
        receipt.get("automation_injected") is False,
        f"{expected_stage}: automation-injected events cannot prove input-driven play",
    )

    window = receipt.get("measurement_window")
    window_ok = isinstance(window, dict)
    duration = float(window.get("duration_seconds", 0.0)) if window_ok else 0.0
    add_check(
        checks,
        issues,
        "measurement_duration",
        window_ok and duration >= expected_duration,
        f"{expected_stage}: measured duration {duration} is below {expected_duration}",
    )
    add_check(
        checks,
        issues,
        "measurement_timestamps",
        bool(
            window_ok
            and isinstance(window.get("started_at_utc"), str)
            and isinstance(window.get("ended_at_utc"), str)
        ),
        f"{expected_stage}: measurement timestamps are missing",
    )

    events = receipt.get("events")
    events_ok = isinstance(events, list) and bool(events)
    add_check(
        checks,
        issues,
        "events_array",
        events_ok,
        f"{expected_stage}: runtime events must be a non-empty array",
    )
    event_counts = {name: 0 for name in REQUIRED_EVENTS}
    timestamps: list[float] = []
    event_shape_ok = events_ok
    if events_ok:
        for index, event in enumerate(events):
            if not isinstance(event, dict):
                issues.append(f"{expected_stage}: events[{index}] is not an object")
                event_shape_ok = False
                continue
            name = event.get("name")
            timestamp = event.get("seconds_from_measurement_start")
            if (
                not isinstance(name, str)
                or not isinstance(timestamp, (int, float))
                or isinstance(timestamp, bool)
                or not math.isfinite(float(timestamp))
                or float(timestamp) < 0.0
                or float(timestamp) > duration
            ):
                issues.append(
                    f"{expected_stage}: events[{index}] is outside the measured window"
                )
                event_shape_ok = False
                continue
            timestamps.append(float(timestamp))
            if name in event_counts:
                event_counts[name] += 1
    add_check(
        checks,
        issues,
        "events_inside_window",
        event_shape_ok,
        f"{expected_stage}: one or more events are invalid/outside the window",
    )
    add_check(
        checks,
        issues,
        "events_monotonic",
        timestamps == sorted(timestamps),
        f"{expected_stage}: event timestamps are not monotonic",
    )
    for name, minimum in REQUIRED_EVENTS.items():
        add_check(
            checks,
            issues,
            f"event_{name}",
            event_counts[name] >= minimum,
            f"{expected_stage}: {name} requires {minimum}, found {event_counts[name]}",
        )
    return {
        "checks": checks,
        "duration_seconds": duration,
        "event_counts": event_counts,
    }


def verify_manifest(manifest_path: Path) -> dict[str, Any]:
    manifest = read_json(manifest_path)
    base = manifest_path.parent
    checks: dict[str, bool] = {}
    issues: list[str] = []
    binding_inventory: list[dict[str, Any]] = []
    stage_results: list[dict[str, Any]] = []
    analyze_csv = load_frame_analyzer()

    add_check(
        checks,
        issues,
        "schema",
        manifest.get("schema") == MANIFEST_SCHEMA,
        f"manifest schema must be {MANIFEST_SCHEMA}",
    )
    add_check(
        checks,
        issues,
        "terminal_state",
        manifest.get("terminal_state") == "EXECUTION_COMPLETE",
        "supervisor terminal_state must be EXECUTION_COMPLETE",
    )
    add_check(
        checks,
        issues,
        "expected_map",
        manifest.get("expected_map") == EXPECTED_MAP,
        "manifest expected_map must be the exact M01 playable map",
    )
    add_check(
        checks,
        issues,
        "package_configuration",
        manifest.get("package_configuration") == "Development",
        "input-combat profiling must use the Development package",
    )

    bindings = manifest.get("bindings")
    bindings_ok = isinstance(bindings, list)
    add_check(
        checks,
        issues,
        "bindings_array",
        bindings_ok,
        "bindings must be an array",
    )
    labels: set[str] = set()
    if bindings_ok:
        for index, binding in enumerate(bindings):
            label = (
                str(binding.get("label", "")).strip()
                if isinstance(binding, dict)
                else ""
            )
            if not label or label in labels:
                issues.append(f"binding {index} has an empty or duplicate label")
            labels.add(label)
            binding_inventory.append(
                validate_file_record(binding, base, issues, label or f"binding_{index}")
            )
    required_binding_labels = {
        "package_executable",
        "package_runtime_binary",
        "source_map",
        "uproject",
        "default_engine_config",
        "default_game_config",
        "default_input_config",
        "packaged_pso_cache",
    }
    add_check(
        checks,
        issues,
        "required_bindings",
        required_binding_labels.issubset(labels),
        "one or more executable/map/config/PSO bindings are missing",
    )
    add_check(
        checks,
        issues,
        "binding_hashes",
        bool(binding_inventory)
        and len(binding_inventory) == len(bindings or [])
        and all(record["valid"] for record in binding_inventory),
        "one or more bound files failed bytes/hash verification",
    )

    stages = manifest.get("stages")
    stage_names = [
        stage.get("name") for stage in stages if isinstance(stage, dict)
    ] if isinstance(stages, list) else []
    add_check(
        checks,
        issues,
        "exact_stage_sequence",
        stage_names == list(EXPECTED_STAGE_NAMES),
        "exactly combat_01, combat_02, combat_03, soak_01 are required in order",
    )
    if not isinstance(stages, list):
        stages = []

    all_stage_checks: list[bool] = []
    for stage in stages:
        if not isinstance(stage, dict):
            issues.append("stage must be an object")
            continue
        name = str(stage.get("name", ""))
        kind = stage.get("kind")
        expected_duration = 1200 if kind == "soak" else 180
        stage_checks: dict[str, bool] = {}
        add_check(
            stage_checks,
            issues,
            "known_kind",
            kind in {"combat", "soak"},
            f"{name}: kind must be combat or soak",
        )
        add_check(
            stage_checks,
            issues,
            "requested_duration",
            stage.get("requested_duration_seconds") == expected_duration,
            f"{name}: requested duration must be {expected_duration} seconds",
        )
        add_check(
            stage_checks,
            issues,
            "resolution",
            stage.get("resolution") == {"x": 1920, "y": 1080},
            f"{name}: supervisor resolution is not 1920x1080",
        )
        add_check(
            stage_checks,
            issues,
            "process_outcome",
            stage.get("timed_out") is False and stage.get("exit_code") == 0,
            f"{name}: process timed out or did not exit zero",
        )

        receipt_path = resolve_path(stage.get("runtime_receipt"), base)
        csv_path = resolve_path(stage.get("csv"), base)
        trace_path = resolve_path(stage.get("trace"), base)
        memory_path = resolve_path(stage.get("memory_series"), base)
        stdout_path = resolve_path(stage.get("stdout"), base)
        stderr_path = resolve_path(stage.get("stderr"), base)

        artifacts_present = all(
            path and path.is_file()
            for path in (
                receipt_path,
                csv_path,
                trace_path,
                memory_path,
                stdout_path,
                stderr_path,
            )
        )
        add_check(
            stage_checks,
            issues,
            "artifacts_present",
            bool(artifacts_present),
            f"{name}: one or more required stage artifacts are missing",
        )
        if not artifacts_present:
            all_stage_checks.append(False)
            stage_results.append({"name": name, "checks": stage_checks})
            continue

        runtime = verify_runtime_receipt(
            read_json(receipt_path), name, expected_duration, issues
        )
        for key, value in runtime["checks"].items():
            stage_checks[f"runtime_{key}"] = value

        frame = analyze_csv(csv_path, warmup_frames=120)
        metrics = frame.get("metrics", {})
        frame_checks = {
            "parseable": bool(frame.get("parseable")),
            "minimum_frame_count": frame.get("frame_count", 0)
            >= int(expected_duration * 45),
            "mean_at_or_below_16_7_ms": metrics.get(
                "frame_time_ms_mean", float("inf")
            )
            <= 16.7,
            "p95_at_or_below_22_2_ms": metrics.get(
                "frame_time_ms_p95", float("inf")
            )
            <= 22.2,
            "max_at_or_below_100_ms": metrics.get(
                "frame_time_ms_max", float("inf")
            )
            <= 100.0,
            "zero_over_100_ms": metrics.get("hitch_over_100ms_count", -1) == 0,
        }
        for key, value in frame_checks.items():
            add_check(
                stage_checks,
                issues,
                f"frame_{key}",
                value,
                f"{name}: frame check failed: {key}",
            )

        memory = parse_memory_series(memory_path)
        max_slope = 8 * 1024 * 1024 if kind == "soak" else 32 * 1024 * 1024
        max_tail = 256 * 1024 * 1024 if kind == "soak" else 512 * 1024 * 1024
        memory_checks = {
            "parseable": memory["parseable"],
            "covers_window": memory["duration_seconds"] >= expected_duration * 0.9,
            "sample_count": memory["sample_count"] >= int(expected_duration * 0.75),
            "stable_slope": (
                memory["slope_bytes_per_minute"] is not None
                and memory["slope_bytes_per_minute"] <= max_slope
            ),
            "stable_tail": (
                memory["tail_growth_bytes"] is not None
                and memory["tail_growth_bytes"] <= max_tail
            ),
        }
        for key, value in memory_checks.items():
            add_check(
                stage_checks,
                issues,
                f"memory_{key}",
                value,
                f"{name}: memory check failed: {key}",
            )

        trace_ok = trace_path.stat().st_size >= 4096
        add_check(
            stage_checks,
            issues,
            "trace_nontrivial",
            trace_ok,
            f"{name}: trace is empty or too small",
        )
        log_text = (
            stdout_path.read_text(encoding="utf-8", errors="replace")
            + "\n"
            + stderr_path.read_text(encoding="utf-8", errors="replace")
        )
        critical, pso = scan_log(log_text)
        add_check(
            stage_checks,
            issues,
            "critical_logs_clean",
            not critical,
            f"{name}: critical log signatures: {', '.join(critical)}",
        )
        for key, value in pso.items():
            add_check(
                stage_checks,
                issues,
                f"pso_{key}",
                value,
                f"{name}: PSO check failed: {key}",
            )

        artifact_hashes = {
            label: sha256_file(path)
            for label, path in {
                "runtime_receipt": receipt_path,
                "csv": csv_path,
                "trace": trace_path,
                "memory_series": memory_path,
                "stdout": stdout_path,
                "stderr": stderr_path,
            }.items()
        }
        stage_pass = all(stage_checks.values())
        all_stage_checks.append(stage_pass)
        stage_results.append(
            {
                "name": name,
                "kind": kind,
                "gate": "PASS" if stage_pass else "FAIL",
                "checks": stage_checks,
                "runtime": runtime,
                "frame": frame,
                "memory": memory,
                "critical_signatures": critical,
                "pso": pso,
                "artifact_sha256": artifact_hashes,
            }
        )

    add_check(
        checks,
        issues,
        "all_four_stages_pass",
        len(all_stage_checks) == 4 and all(all_stage_checks),
        "one or more combat/soak stages failed",
    )
    passed = bool(checks) and all(checks.values())
    return {
        "schema": REPORT_SCHEMA,
        "verified_at_utc": datetime.now(timezone.utc).isoformat(),
        "gate": "PASS" if passed else "FAIL",
        "terminal_state": "VERIFICATION_COMPLETE",
        "manifest": str(manifest_path),
        "manifest_sha256": sha256_file(manifest_path),
        "checks": checks,
        "issues": issues,
        "binding_inventory": binding_inventory,
        "stages": stage_results,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        report = verify_manifest(args.manifest.resolve(strict=True))
    except (OSError, ValueError, json.JSONDecodeError, RuntimeError) as exc:
        report = {
            "schema": REPORT_SCHEMA,
            "verified_at_utc": datetime.now(timezone.utc).isoformat(),
            "gate": "FAIL",
            "terminal_state": "FAILED_HARNESS",
            "checks": {},
            "issues": [f"{type(exc).__name__}: {exc}"],
        }
    text = json.dumps(report, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if report["gate"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
