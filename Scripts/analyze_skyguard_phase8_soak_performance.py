"""Analyze the ten packaged Phase 8 mission-soak CSV captures.

This is a baseline performance receipt, not the later input-driven combat
acceptance gate. It reuses the Phase 1 CSV parser so both gates calculate frame
statistics identically.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PHASE1_VERIFIER = PROJECT_ROOT / "Scripts" / "verify_skyguard_phase1_performance_gate.py"
MISSION_IDS = tuple(f"M{index:02d}" for index in range(1, 11))


def load_phase1_analyzer():
    spec = importlib.util.spec_from_file_location(
        "skyguard_phase1_performance_verifier", PHASE1_VERIFIER
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load CSV analyzer: {PHASE1_VERIFIER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.analyze_csv


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def file_record(path: Path) -> dict[str, Any]:
    return {
        "path": str(path),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def mission_stage_map(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    stages = {
        str(stage.get("name", "")).removeprefix("mission_soak_"): stage
        for stage in manifest.get("stages", [])
        if str(stage.get("name", "")).startswith("mission_soak_")
    }
    return {mission_id: stages[mission_id] for mission_id in MISSION_IDS if mission_id in stages}


def thresholds(metrics: dict[str, Any]) -> dict[str, bool]:
    return {
        "mean_frame_time_at_or_below_16_7_ms": metrics["frame_time_ms_mean"]
        <= 16.7,
        "p95_frame_time_at_or_below_22_2_ms": metrics["frame_time_ms_p95"]
        <= 22.2,
        "max_hitch_at_or_below_100_ms": metrics["frame_time_ms_max"] <= 100.0,
        "zero_hitches_over_100_ms": metrics["hitch_over_100ms_count"] == 0,
    }


def build_report(release_attempt: Path, warmup_frames: int = 120) -> dict[str, Any]:
    manifest_path = release_attempt / "run_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    csv_root = (
        release_attempt
        / "packages"
        / "Development"
        / "Windows"
        / "Skyguard52"
        / "Saved"
        / "Profiling"
        / "CSV"
    )
    csv_paths = sorted(csv_root.glob("Profile(*).csv"))
    trace_paths = sorted((release_attempt / "artifacts").glob("soak_M??.utrace"))
    stages = mission_stage_map(manifest)
    analyze_csv = load_phase1_analyzer()

    mission_results: list[dict[str, Any]] = []
    if len(csv_paths) == len(MISSION_IDS):
        for mission_id, csv_path in zip(MISSION_IDS, csv_paths, strict=True):
            analysis = analyze_csv(csv_path, warmup_frames=warmup_frames)
            checks = (
                thresholds(analysis["metrics"]) if analysis.get("parseable") else {}
            )
            stage = stages.get(mission_id, {})
            mission_results.append(
                {
                    "mission": mission_id,
                    "csv": file_record(csv_path),
                    "stage_exit_code": stage.get("exit_code"),
                    "stage_timed_out": stage.get("timed_out"),
                    "analysis": analysis,
                    "checks": checks,
                    "pass": bool(
                        analysis.get("parseable")
                        and analysis.get("frame_count", 0) >= 60
                        and stage.get("exit_code") == 0
                        and stage.get("timed_out") is False
                        and checks
                        and all(checks.values())
                    ),
                }
            )

    trace_records = [file_record(path) for path in trace_paths]
    checks = {
        "release_gate_pass": (
            (release_attempt / "gate_report.json").is_file()
            and json.loads(
                (release_attempt / "gate_report.json").read_text(encoding="utf-8-sig")
            ).get("gate")
            == "PASS"
        ),
        "exactly_ten_clean_soak_stages": (
            len(stages) == 10
            and all(
                stage.get("exit_code") == 0 and stage.get("timed_out") is False
                for stage in stages.values()
            )
        ),
        "exactly_ten_csv_captures": len(csv_paths) == 10,
        "exactly_ten_nonempty_trace_captures": (
            len(trace_records) == 10
            and all(record["bytes"] >= 4096 for record in trace_records)
        ),
        "all_missions_within_baseline_budget": (
            len(mission_results) == 10
            and all(result["pass"] for result in mission_results)
        ),
    }
    worst = {}
    if mission_results:
        worst = {
            "highest_mean_ms": max(
                mission_results,
                key=lambda result: result["analysis"]["metrics"]["frame_time_ms_mean"],
            )["mission"],
            "mean_ms": max(
                result["analysis"]["metrics"]["frame_time_ms_mean"]
                for result in mission_results
            ),
            "highest_p95_ms": max(
                mission_results,
                key=lambda result: result["analysis"]["metrics"]["frame_time_ms_p95"],
            )["mission"],
            "p95_ms": max(
                result["analysis"]["metrics"]["frame_time_ms_p95"]
                for result in mission_results
            ),
            "highest_max_hitch_ms": max(
                mission_results,
                key=lambda result: result["analysis"]["metrics"]["frame_time_ms_max"],
            )["mission"],
            "max_hitch_ms": max(
                result["analysis"]["metrics"]["frame_time_ms_max"]
                for result in mission_results
            ),
            "total_hitches_over_100ms": sum(
                result["analysis"]["metrics"]["hitch_over_100ms_count"]
                for result in mission_results
            ),
        }
    return {
        "schema": "skyguard.phase8.soak-performance-baseline.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "release_attempt": str(release_attempt),
        "release_manifest": file_record(manifest_path),
        "warmup_frames_discarded_per_capture": warmup_frames,
        "gate": "PASS_BASELINE" if all(checks.values()) else "FAIL",
        "checks": checks,
        "worst_case": worst,
        "missions": mission_results,
        "traces": trace_records,
        "limitations": [
            "Offscreen fixed-route benchmark evidence is not an input-driven combat run.",
            "Final gold acceptance still requires three packaged 1920x1080 combat runs.",
            "ADS, rifle fire, Igla launch, drone breakup, and boss destruction must occur inside those later measured windows.",
            "A 20-minute input-driven combat soak with stable memory remains required.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release-attempt", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--warmup-frames", type=int, default=120)
    args = parser.parse_args()
    report = build_report(args.release_attempt.resolve(), args.warmup_frames)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"gate": report["gate"], "checks": report["checks"], "worst_case": report["worst_case"]}, indent=2))
    return 0 if report["gate"] == "PASS_BASELINE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
