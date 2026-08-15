"""Mandatory automatic postflight for the Recovery07 mapped visual proof."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
import sys
from pathlib import Path
from typing import Any


ROOT = Path(r"D:\Skyguard52")
ISOLATED_ROOT = Path(r"D:\SG52T08_ENV01")
PREFIX = "TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY07_MAPPED_VISUAL_PROOF01_RECOVERY03"
CONTRACT_ID = "T08-M01-ENV-AUTH01-RECOVERY07-MAPPED-VISUAL-PROOF01-RECOVERY03"
CONTRACT = ROOT / f"Docs/AAA_Review/{PREFIX}_CONTRACT.json"
CAMERAS = ROOT / f"Docs/AAA_Review/{PREFIX}_CAMERAS.json"
VISUAL_RUBRIC = ROOT / f"Docs/AAA_Review/{PREFIX}_VISUAL_RUBRIC.json"
PERFORMANCE_RUBRIC = ROOT / f"Docs/AAA_Review/{PREFIX}_PERFORMANCE_RUBRIC.json"
ATTEMPT = ROOT / f"Saved/BuildAttempts/{PREFIX}/attempt_01"
LAUNCHER = ROOT / f"Saved/BuildAttempts/{PREFIX}/launcher_attempt_01"
STARTUP_RECEIPT = LAUNCHER / "executor_startup_receipt.json"
PREFLIGHT = ROOT / f"Saved/Reports/{PREFIX}_EXECUTION_PREFLIGHT.json"
SUPERVISOR = ROOT / f"Saved/Reports/{PREFIX}_TERMINAL_SUPERVISOR.json"
PROFILE = ISOLATED_ROOT / "Saved/Profiling/CSV/Recovery07MappedVisualProof01Recovery03.csv"
MAP_FILE = ISOLATED_ROOT / (
    "Content/ToolchainWave08/Environment/"
    "Lvl_M01_T08_EnvironmentAuthoring01_Recovery07.umap"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    require(path.is_file(), f"Missing JSON: {path}")
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def record_path(record: dict[str, Any]) -> Path:
    if "absolute_path" in record:
        return Path(record["absolute_path"])
    return ROOT / record["file"]


def verify_locked_inputs(contract: dict[str, Any]) -> None:
    for record in contract["locked_inputs"]:
        path = record_path(record)
        require(path.is_file(), f"Missing locked input: {path}")
        require(path.stat().st_size == int(record["bytes"]), f"Byte mismatch: {path}")
        require(sha256_file(path) == record["sha256"], f"Hash mismatch: {path}")


def percentile(values: list[float], proportion: float) -> float:
    require(bool(values), "Cannot calculate a percentile from no values")
    ordered = sorted(values)
    rank = (len(ordered) - 1) * proportion
    lower = math.floor(rank)
    upper = math.ceil(rank)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (rank - lower)


def parse_number(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if math.isfinite(parsed) else None


def parse_profile(path: Path) -> dict[str, Any]:
    require(path.is_file() and path.stat().st_size > 1024, "CSV profile is absent or empty")
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        require(reader.fieldnames is not None, "CSV profile has no header")
        required = {"FrameTime", "GPUTime", "GPUMem/LocalUsedMB"}
        require(required.issubset(set(reader.fieldnames)), f"CSV columns missing: {required - set(reader.fieldnames)}")
        frame: list[float] = []
        gpu: list[float] = []
        gpu_memory: list[float] = []
        for row in reader:
            frame_value = parse_number(row.get("FrameTime"))
            gpu_value = parse_number(row.get("GPUTime"))
            memory_value = parse_number(row.get("GPUMem/LocalUsedMB"))
            if frame_value is None:
                continue
            frame.append(frame_value)
            if gpu_value is not None:
                gpu.append(gpu_value)
            if memory_value is not None:
                gpu_memory.append(memory_value)
    require(len(frame) >= 900, f"CSV profile has only {len(frame)} measured frames")
    require(len(gpu) >= 900, f"CSV profile has only {len(gpu)} GPU samples")
    require(len(gpu_memory) >= 900, f"CSV profile has only {len(gpu_memory)} GPU-memory samples")
    return {
        "sample_count": len(frame),
        "mean_frame_ms": statistics.fmean(frame),
        "p95_frame_ms": percentile(frame, 0.95),
        "p99_frame_ms": percentile(frame, 0.99),
        "max_frame_ms": max(frame),
        "frames_over_50_ms": sum(value > 50.0 for value in frame),
        "mean_gpu_ms": statistics.fmean(gpu),
        "p95_gpu_ms": percentile(gpu, 0.95),
        "peak_gpu_memory_mib": max(gpu_memory),
        "sha256": sha256_file(path),
        "bytes": path.stat().st_size,
    }


def verify_performance(supervisor: dict[str, Any]) -> dict[str, Any]:
    rubric = load_json(PERFORMANCE_RUBRIC)
    thresholds = rubric["thresholds"]
    metrics = parse_profile(PROFILE)
    metrics["peak_working_set_mib"] = int(supervisor["peak_working_set_bytes"]) / 1048576.0
    require(metrics["mean_frame_ms"] <= thresholds["mean_frame_ms_max"], "Mean frame time")
    require(metrics["p95_frame_ms"] <= thresholds["p95_frame_ms_max"], "P95 frame time")
    require(metrics["p99_frame_ms"] <= thresholds["p99_frame_ms_max"], "P99 frame time")
    require(metrics["max_frame_ms"] <= thresholds["max_frame_ms"], "Maximum frame hitch")
    require(metrics["frames_over_50_ms"] <= thresholds["frames_over_50ms_max"], "Frames above 50 ms")
    require(metrics["mean_gpu_ms"] <= thresholds["mean_gpu_ms_max"], "Mean GPU time")
    require(metrics["p95_gpu_ms"] <= thresholds["p95_gpu_ms_max"], "P95 GPU time")
    require(metrics["peak_working_set_mib"] <= thresholds["working_set_mib_max"], "Working set")
    require(metrics["peak_gpu_memory_mib"] <= thresholds["gpu_memory_mib_max"], "GPU memory")
    return metrics


def grayscale_statistics(path: Path) -> tuple[dict[str, Any], list[float]]:
    try:
        from PIL import Image
    except ImportError as exc:
        raise AssertionError("Pillow is required for PNG adjudication") from exc
    with Image.open(path) as source:
        require(source.size == (2560, 1440), f"Wrong PNG dimensions: {path}")
        image = source.convert("RGB")
        grayscale = image.convert("L")
        histogram_counts = grayscale.histogram()
        total = sum(histogram_counts)
        require(total == 2560 * 1440, f"Pixel count mismatch: {path}")
        histogram = [value / total for value in histogram_counts]
        cumulative = 0
        p01 = 0
        p99 = 255
        for index, count in enumerate(histogram_counts):
            cumulative += count
            if cumulative >= total * 0.01:
                p01 = index
                break
        cumulative = 0
        for index, count in enumerate(histogram_counts):
            cumulative += count
            if cumulative >= total * 0.99:
                p99 = index
                break
        sample = image.resize((640, 360))
        colors = sample.getcolors(maxcolors=640 * 360)
        unique = 640 * 360 if colors is None else len(colors)
        stats = {
            "width": 2560,
            "height": 1440,
            "sample_unique_rgb_colors": unique,
            "black_pixel_fraction": sum(histogram_counts[:3]) / total,
            "white_pixel_fraction": sum(histogram_counts[253:]) / total,
            "luma_p01": p01,
            "luma_p99": p99,
            "mean_luma": sum(i * value for i, value in enumerate(histogram)),
        }
        require(unique >= 1024, f"Insufficient image diversity: {path}")
        require(stats["black_pixel_fraction"] <= 0.08, f"Black frame/shadow crush: {path}")
        require(stats["white_pixel_fraction"] <= 0.02, f"White frame/overexposure: {path}")
        require(stats["luma_p01"] >= 3, f"Crushed shadows: {path}")
        require(stats["luma_p99"] <= 250, f"Overexposure: {path}")
        return stats, histogram


def verify_captures(capture: dict[str, Any]) -> dict[str, Any]:
    cameras = load_json(CAMERAS)
    expected_specs = cameras["static_cameras"] + cameras["temporal_cameras"]
    expected_ids = [item["id"] for item in expected_specs]
    records = capture["captures"]
    require(capture["capture_count"] == 8 and len(records) == 8, "Capture count")
    require([item["id"] for item in records] == expected_ids, "Capture order or identities")
    frames: dict[str, Any] = {}
    histograms: dict[str, list[float]] = {}
    for record in records:
        path = Path(record["file"])
        require(path.is_file() and path.stat().st_size >= 1024, f"Missing PNG: {path}")
        require(path.stat().st_size == int(record["bytes"]), f"PNG byte mismatch: {path}")
        require(sha256_file(path) == record["sha256"], f"PNG hash mismatch: {path}")
        stats, histogram = grayscale_statistics(path)
        stats["bytes"] = path.stat().st_size
        stats["sha256"] = record["sha256"]
        frames[record["id"]] = stats
        histograms[record["id"]] = histogram
    temporal_ids = [item["id"] for item in cameras["temporal_cameras"]]
    temporal_pairs = []
    for left, right in zip(temporal_ids, temporal_ids[1:]):
        distance = 0.5 * sum(
            abs(a - b) for a, b in zip(histograms[left], histograms[right])
        )
        luma_delta = abs(frames[left]["mean_luma"] - frames[right]["mean_luma"])
        require(distance <= 0.30, f"Temporal histogram instability: {left}/{right}")
        require(luma_delta <= 24.0, f"Temporal exposure instability: {left}/{right}")
        temporal_pairs.append(
            {
                "left": left,
                "right": right,
                "histogram_distance": distance,
                "mean_luma_delta": luma_delta,
            }
        )
    return {"frames": frames, "temporal_pairs": temporal_pairs}


def verify_logs() -> dict[str, Any]:
    logs = [
        LAUNCHER / "logs/recovery07_mapped_visual_proof01_recovery03.engine.log",
        LAUNCHER / "logs/recovery07_mapped_visual_proof01_recovery03.stdout.log",
        LAUNCHER / "logs/recovery07_mapped_visual_proof01_recovery03.stderr.log",
    ]
    for path in logs:
        require(path.is_file(), f"Missing log: {path}")
    text = "\n".join(
        path.read_text(encoding="utf-8", errors="replace") for path in logs
    )
    critical_terms = (
        "Fatal error:",
        "LowLevelFatalError",
        "GPU Crashed",
        "DXGI_ERROR_DEVICE_REMOVED",
        "Ensure condition failed",
    )
    network_terms = (
        "datarouter.ol.epicgames.com",
        "LogAnalytics: Display: StartSession",
        "LogEOS: Warning",
        "LogHttp: Warning: Request",
    )
    critical_hits = {term: text.count(term) for term in critical_terms if term in text}
    network_hits = {term: text.count(term) for term in network_terms if term in text}
    require(not critical_hits, f"Critical log evidence: {critical_hits}")
    require(not network_hits, f"Network/telemetry evidence: {network_hits}")
    return {
        "critical_hits": critical_hits,
        "network_hits": network_hits,
        "files": [
            {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256_file(path)}
            for path in logs
        ],
    }


def adjudicate() -> dict[str, Any]:
    contract = load_json(CONTRACT)
    require(contract["contract_id"] == CONTRACT_ID, "Contract identity")
    verify_locked_inputs(contract)
    preflight = load_json(PREFLIGHT)
    supervisor = load_json(SUPERVISOR)
    startup = load_json(STARTUP_RECEIPT)
    terminal = load_json(ATTEMPT / "terminal_receipt.json")
    capture = load_json(ATTEMPT / "proof/capture_receipt.json")
    restoration = load_json(ATTEMPT / "proof/restoration_receipt.json")
    require(preflight["gate"] == "PASS_READY_FOR_SINGLE_UNREAL_LAUNCH", "Preflight")
    require(supervisor["gate"] == "UNREAL_EXITED_AWAITING_POSTFLIGHT", "Supervisor pre-postflight gate")
    require(supervisor["unreal_launch_count"] == 1, "Unreal launch count")
    require(supervisor["retry_count"] == 0, "Retry count")
    require(supervisor["actual_exit_code"] == 0, "Unreal exit code")
    require(supervisor["actual_exit_code_type"] == "System.Int32", "Unreal exit-code type")
    require(supervisor["timed_out"] is False, "Unreal timeout")
    require(supervisor["executor_startup_receipt_observed"] is True, "Executor startup observation")
    require(supervisor["executor_startup_timed_out"] is False, "Executor startup timeout")
    require(startup["gate"] == "EXECUTOR_INVOKED", "Executor startup gate")
    require(startup["contract_id"] == CONTRACT_ID, "Executor startup contract")
    require(terminal["contract_id"] == CONTRACT_ID, "Executor contract")
    require(terminal["gate"] == "PASS_CAPTURE_COMPLETE_PENDING_OFFLINE_ADJUDICATION", "Executor gate")
    require(terminal["rhi"] == "D3D12|SM6", "RHI/feature level")
    require(terminal["stable_shader_polls"] >= 2, "Shader readiness")
    require(terminal["frame_sample_count"] >= 900, "Executor frame samples")
    require(terminal["capture_count"] == 8, "Executor capture count")
    require(terminal["restoration_verified"] is True, "Restoration")
    for key in (
        "world_saved",
        "asset_imported",
        "pcg_generated",
        "promotion_performed",
        "integration_performed",
        "packaging_performed",
    ):
        require(terminal[key] is False, f"Forbidden executor flag: {key}")
    require(restoration["gate"] == "PASS_NO_MUTATION_REQUIRED", "No-mutation receipt")
    require(restoration["material_identity_matches"] is True, "Material identity")
    require(restoration["governed_transforms_unchanged"] is True, "Governed transforms")
    require(restoration["map_unchanged"] is True, "Map changed")
    require(sha256_file(MAP_FILE) == contract["world"]["map_sha256"], "Map hash after proof")

    heartbeat = ATTEMPT / "proof/lifecycle_heartbeat.jsonl"
    require(heartbeat.is_file(), "Lifecycle heartbeat is absent")
    heartbeat_text = heartbeat.read_text(encoding="utf-8-sig")
    for marker in (
        "preflight_complete",
        "shader_ready_two_stable_polls",
        "measurement_started",
        "measurement_complete",
        "capture_phase_started",
        "terminal_receipt_written",
    ):
        require(marker in heartbeat_text, f"Heartbeat marker missing: {marker}")
    require(
        "compilation_resumed_during_measurement" not in heartbeat_text,
        "Compilation resumed during measurement",
    )

    return {
        "schema": "skyguard.t08.m01.recovery07-mapped-proof01-postflight.v1",
        "classification": "PASSED_AUTOMATIC_AWAITING_HUMAN_VISUAL_REVIEW",
        "contract_id": CONTRACT_ID,
        "performance": verify_performance(supervisor),
        "captures": verify_captures(capture),
        "restoration": restoration,
        "logs": verify_logs(),
        "heartbeat": {
            "bytes": heartbeat.stat().st_size,
            "sha256": sha256_file(heartbeat),
        },
        "executor_startup": {
            "bytes": STARTUP_RECEIPT.stat().st_size,
            "sha256": sha256_file(STARTUP_RECEIPT),
        },
        "human_full_resolution_review_required": True,
        "accepted_automatically": False,
        "world_saved": False,
        "next_gate": "DIRECT_FULL_RESOLUTION_HUMAN_VISUAL_REVIEW",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output)
    try:
        result = adjudicate()
        code = 0
    except Exception as exc:
        result = {
            "schema": "skyguard.t08.m01.recovery07-mapped-proof01-postflight.v1",
            "classification": "FAILED_WITH_EVIDENCE",
            "error": f"{type(exc).__name__}: {exc}",
        }
        code = 1
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
