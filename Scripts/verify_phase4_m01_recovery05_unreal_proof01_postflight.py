from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import pathlib
import statistics
import sys
from typing import Any

ROOT = pathlib.Path(r"D:\Skyguard52")
BINDING_ID = "P4.6-M01-RECOVERY05-UNREAL-PROOF-01"
CONTRACT_ID = (
    "P4.6-M01-REPRESENTATIVE-VISUAL-008-RECOVERY-03-"
    "NATIVE-BUILD-RECOVERY-01"
)
RUNTIME = (
    ROOT
    / "Saved/BuildAttempts/"
    "PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY03_"
    "NATIVE_BUILD_RECOVERY01/runtime_attempt_01"
)
PROOF = RUNTIME / "proof"
LAUNCHER = (
    ROOT
    / "Saved/BuildAttempts/"
    "PHASE4_M01_RECOVERY05_UNREAL_PROOF01/launcher_attempt_01"
)
PREFLIGHT = (
    ROOT
    / "Saved/Reports/"
    "PHASE4_M01_RECOVERY05_UNREAL_PROOF01_EXECUTION_PREFLIGHT.json"
)
SUPERVISOR = (
    ROOT
    / "Saved/Reports/"
    "PHASE4_M01_RECOVERY05_UNREAL_PROOF01_TERMINAL_SUPERVISOR.json"
)
LAUNCHER_SOURCE = (
    ROOT
    / "Scripts/"
    "invoke_phase4_m01_recovery05_unreal_proof01_once.ps1"
)
CONTRACT = (
    ROOT
    / "Docs/AAA_Review/"
    "PHASE4_M01_RECOVERY05_UNREAL_PROOF01_CONTRACT.json"
)
CAMERA_IDS = [
    "C01_REAR_GUNNER_PORT",
    "C02_REAR_GUNNER_STARBOARD",
    "C03_SHORELINE_APPROACH",
    "C04_ROUTE_EXTERIOR",
    "C05_CITY_INLAND",
    "T01_ROUTE_ENTRY",
    "T02_ROUTE_MID",
    "T03_ROUTE_EXIT",
]
TEMPORAL_IDS = CAMERA_IDS[-3:]


def require(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: pathlib.Path) -> dict[str, Any]:
    require(path.is_file(), f"missing JSON: {path}")
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def percentile(values: list[float], proportion: float) -> float:
    require(bool(values), "empty metric")
    ordered = sorted(values)
    rank = (len(ordered) - 1) * proportion
    lower = math.floor(rank)
    upper = math.ceil(rank)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (rank - lower)


def verify_locked_inputs(contract: dict[str, Any]) -> None:
    for record in contract["locked_inputs"]:
        path = ROOT / record["file"]
        require(path.is_file(), f"missing locked input: {path}")
        require(path.stat().st_size == record["bytes"], f"byte mismatch: {path}")
        require(sha256(path) == record["sha256"], f"hash mismatch: {path}")


def offline_contract_test() -> dict[str, Any]:
    contract = load_json(CONTRACT)
    require(contract["binding_id"] == BINDING_ID, "binding id")
    binding = contract["immutable_binary_binding"]
    require(binding["contract_id"] == CONTRACT_ID, "contract id")
    require(
        binding["required_attempt_suffix"]
        == "Saved/BuildAttempts/"
        "PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY03_"
        "NATIVE_BUILD_RECOVERY01/runtime_attempt_01",
        "runtime suffix",
    )
    verify_locked_inputs(contract)

    source = LAUNCHER_SOURCE.read_text(encoding="utf-8")
    require(
        source.count("Start-Process -FilePath $editor") == 1,
        "launcher must contain exactly one Unreal launch",
    )
    for marker in (
        "-EnablePlugins=SkyguardRecovery03NativeRecovery05",
        "-DisablePlugins=SkyguardRecovery03,"
        "SkyguardRecovery03NativeRecovery01,"
        "SkyguardRecovery03NativeRecovery04,"
        "Fab,Bridge,EditorTelemetry,RuntimeTelemetry,EOSShared",
        "SkyguardRecovery01ContractId=" + CONTRACT_ID,
        "SkyguardRecovery01Authorization=" + CONTRACT_ID + "-ONE-SHOT",
        "SkyguardRecovery01ExpectedMap=/Game/Skyguard/Maps/"
        "Lvl_M01_CoastalIntercept_ProductionEnvironment_v5_attempt03",
        "SkyguardRecovery01AttemptRoot=",
        "WaitForExit()",
        "Refresh()",
        "actual_exit_code_type",
        "retry_count=0",
        "bSendUsageData=False",
    ):
        require(marker in source, f"launcher marker missing: {marker}")
    require("RunUAT.bat" not in source, "forbidden build launcher")
    require("AutomationTool.exe" not in source, "forbidden AutomationTool launcher")
    require(
        "Start-Process -FilePath $unrealBuildTool" not in source,
        "forbidden UBT launch path",
    )

    for path in (RUNTIME, PROOF, LAUNCHER, PREFLIGHT, SUPERVISOR):
        require(not path.exists(), f"future namespace exists: {path}")
    return {
        "schema": "skyguard.phase4.m01-recovery05-unreal-proof01-offline-test.v1",
        "gate": "PASS",
        "binding_id": BINDING_ID,
        "single_unreal_launch_path": True,
        "runtime_namespaces_absent": True,
        "unreal_launched": False,
    }


def verify_receipts() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    preflight = load_json(PREFLIGHT)
    supervisor = load_json(SUPERVISOR)
    terminal = load_json(RUNTIME / "terminal_receipt.json")
    capture = load_json(PROOF / "capture_receipt.json")
    restoration = load_json(PROOF / "restoration_receipt.json")

    require(
        preflight["gate"] == "PASS_READY_TO_START_SINGLE_UNREAL_PROCESS",
        "execution preflight failed",
    )
    require(preflight["launch_count"] == 0, "preflight launch count")
    require(preflight["retry_count"] == 0, "preflight retry count")
    require(
        supervisor["gate"] == "UNREAL_EXITED_AWAITING_POSTFLIGHT",
        "supervisor gate",
    )
    require(supervisor["actual_exit_code"] == 0, "Unreal exit code")
    require(supervisor["actual_exit_code_type"] == "System.Int32", "exit type")
    require(supervisor["timed_out"] is False, "process timed out")
    require(supervisor["launch_count"] == 1, "launch count")
    require(supervisor["retry_count"] == 0, "retry count")
    require(supervisor["process_handle_retained"] is True, "process handle")

    require(terminal["contract_id"] == CONTRACT_ID, "terminal contract")
    require(terminal["passed"] is True, "terminal failed")
    require(terminal["exit_code"] == 0, "native exit code")
    require(terminal["stable_shader_polls"] >= 2, "shader-ready polls")
    require(terminal["frame_sample_count"] >= 900, "frame samples")
    require(terminal["capture_count"] == 8, "capture count")
    require(terminal["restoration_verified"] is True, "restoration")
    for key in (
        "world_saved",
        "asset_imported",
        "pcg_generated",
        "promotion_performed",
        "integration_performed",
        "packaging_performed",
    ):
        require(terminal[key] is False, f"forbidden terminal flag: {key}")

    require(capture["passed"] is True, "capture receipt")
    require(capture["capture_count"] == 8, "capture receipt count")
    require(capture["frame_sample_count"] >= 900, "capture sample count")
    require(capture["world_saved"] is False, "capture world save")
    require(restoration["passed"] is True, "restoration receipt")
    require(restoration["identity_matches"] is True, "material identity")
    require(
        restoration["original_material_identity"]
        == restoration["restored_material_identity"],
        "restored material differs",
    )
    require(restoration["world_saved"] is False, "restoration world save")
    return terminal, capture, restoration


def verify_heartbeat() -> dict[str, Any]:
    path = RUNTIME / "lifecycle_heartbeat.jsonl"
    require(path.is_file(), "missing lifecycle heartbeat")
    lines = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    text = "\n".join(json.dumps(item, sort_keys=True) for item in lines)
    for marker in (
        "preflight_and_binding_complete",
        "shader_ready_1_finished_16_valid_16",
        "shader_ready_2_finished_16_valid_16",
        "measurement_started",
        "measurement_complete",
    ):
        require(marker in text, f"heartbeat marker missing: {marker}")
    require(
        "compilation_resumed_measurement_reset" not in text,
        "shader compilation resumed during measurement",
    )
    return {"event_count": len(lines), "sha256": sha256(path)}


def verify_metrics() -> dict[str, Any]:
    path = PROOF / "frame_samples.csv"
    require(path.is_file(), "missing frame samples")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    require(len(rows) >= 900, "insufficient frame samples")
    required = {
        "frame_ms",
        "gpu_ms",
        "working_set_bytes",
        "texture_memory_bytes",
        "total_gpu_memory_bytes",
        "available_texture_memory_bytes",
    }
    require(required.issubset(rows[0]), "missing metric column")
    frame = [float(row["frame_ms"]) for row in rows]
    gpu = [float(row["gpu_ms"]) for row in rows]
    working = [int(row["working_set_bytes"]) for row in rows]
    texture = [int(row["texture_memory_bytes"]) for row in rows]
    total_gpu = [int(row["total_gpu_memory_bytes"]) for row in rows]
    available = [int(row["available_texture_memory_bytes"]) for row in rows]
    require(all(math.isfinite(value) and value >= 0 for value in frame), "frame metric")
    require(all(math.isfinite(value) and value >= 0 for value in gpu), "GPU metric")
    require(all(value >= 0 for value in working + texture + total_gpu), "memory metric")
    require(all(value >= 0 for value in available), "texture pool over budget")

    metrics = {
        "sample_count": len(rows),
        "mean_frame_ms": statistics.fmean(frame),
        "p95_frame_ms": percentile(frame, 0.95),
        "p99_frame_ms": percentile(frame, 0.99),
        "max_frame_ms": max(frame),
        "frames_over_50_ms": sum(value > 50.0 for value in frame),
        "mean_gpu_ms": statistics.fmean(gpu),
        "p95_gpu_ms": percentile(gpu, 0.95),
        "peak_working_set_mib": max(working) / 1048576.0,
        "peak_gpu_memory_mib": max(total_gpu) / 1048576.0,
        "peak_texture_memory_mib": max(texture) / 1048576.0,
        "texture_pool_over_budget_frames": sum(value < 0 for value in available),
        "sha256": sha256(path),
    }
    require(metrics["mean_frame_ms"] <= 16.7, "mean frame time")
    require(metrics["p95_frame_ms"] <= 22.2, "p95 frame time")
    require(metrics["p99_frame_ms"] <= 33.3, "p99 frame time")
    require(metrics["max_frame_ms"] <= 50.0, "single-frame hitch")
    require(metrics["frames_over_50_ms"] == 0, "frames over 50 ms")
    require(metrics["mean_gpu_ms"] <= 14.0, "mean GPU time")
    require(metrics["p95_gpu_ms"] <= 20.0, "p95 GPU time")
    require(metrics["peak_working_set_mib"] <= 12288, "working set")
    require(metrics["peak_gpu_memory_mib"] <= 10240, "GPU memory")
    require(metrics["texture_pool_over_budget_frames"] == 0, "texture pool")
    return metrics


def image_statistics(path: pathlib.Path) -> tuple[dict[str, Any], list[float]]:
    try:
        from PIL import Image
    except ImportError as exc:
        raise AssertionError("Pillow is required for visual verification") from exc
    with Image.open(path) as source:
        require(source.size == (2560, 1440), f"PNG dimensions: {path}")
        image = source.convert("RGB")
        pixels = list(image.getdata())
        require(bool(pixels), f"empty image: {path}")
        unique = len(set(pixels))
        black = sum(max(pixel) <= 2 for pixel in pixels) / len(pixels)
        white = sum(min(pixel) >= 253 for pixel in pixels) / len(pixels)
        luma = sorted(
            0.2126 * pixel[0] + 0.7152 * pixel[1] + 0.0722 * pixel[2]
            for pixel in pixels
        )
        histogram = [value / len(pixels) for value in image.convert("L").histogram()]
        stats = {
            "width": 2560,
            "height": 1440,
            "unique_rgb8_colors": unique,
            "black_pixel_fraction": black,
            "white_pixel_fraction": white,
            "luma_p01": percentile(luma, 0.01),
            "luma_p99": percentile(luma, 0.99),
        }
        require(unique >= 1024, f"insufficient image diversity: {path}")
        require(black <= 0.08, f"black fraction: {path}")
        require(white <= 0.02, f"white fraction: {path}")
        require(stats["luma_p01"] >= 3, f"crushed shadows: {path}")
        require(stats["luma_p99"] <= 250, f"overexposure: {path}")
        return stats, histogram


def verify_captures(capture: dict[str, Any]) -> dict[str, Any]:
    records = capture["captures"]
    require(len(records) == 8, "capture record count")
    by_id = {record["id"]: record for record in records}
    require(set(by_id) == set(CAMERA_IDS), "camera IDs")
    output: dict[str, Any] = {}
    histograms: dict[str, list[float]] = {}
    mean_luma: dict[str, float] = {}
    for camera_id in CAMERA_IDS:
        record = by_id[camera_id]
        path = pathlib.Path(record["file"])
        require(path.is_file() and path.stat().st_size > 0, f"PNG missing: {path}")
        require(path.stat().st_size == int(record["bytes"]), f"PNG bytes: {path}")
        require(sha256(path) == record["sha256"], f"PNG hash: {path}")
        stats, histogram = image_statistics(path)
        stats["sha256"] = record["sha256"]
        output[camera_id] = stats
        histograms[camera_id] = histogram
        mean_luma[camera_id] = sum(index * value for index, value in enumerate(histogram))
    temporal = []
    for left, right in zip(TEMPORAL_IDS, TEMPORAL_IDS[1:]):
        distance = 0.5 * sum(
            abs(a - b) for a, b in zip(histograms[left], histograms[right])
        )
        luma_delta = abs(mean_luma[left] - mean_luma[right])
        require(distance <= 0.22, f"temporal histogram distance: {left}/{right}")
        require(luma_delta <= 18.0, f"temporal luma delta: {left}/{right}")
        temporal.append(
            {
                "left": left,
                "right": right,
                "histogram_distance": distance,
                "mean_luma_delta": luma_delta,
            }
        )
    return {"frames": output, "temporal_pairs": temporal}


def verify_logs() -> dict[str, Any]:
    engine = LAUNCHER / "logs/recovery04.engine.log"
    stdout = LAUNCHER / "logs/recovery04.stdout.log"
    stderr = LAUNCHER / "logs/recovery04.stderr.log"
    for path in (engine, stdout, stderr):
        require(path.is_file(), f"missing log: {path}")
    text = "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in (engine, stdout, stderr)
    )
    critical = (
        "Fatal error:",
        "Ensure condition failed",
        "DXGI_ERROR_DEVICE_REMOVED",
        "GPU Crashed",
        "LowLevelFatalError",
    )
    network = (
        "LogHttp: Warning: Request",
        "LogEOS: Warning",
        "LogAnalytics: Display: StartSession",
        "datarouter.ol.epicgames.com",
    )
    critical_hits = sum(text.count(term) for term in critical)
    network_hits = sum(text.count(term) for term in network)
    require(critical_hits == 0, "critical log hit")
    require(network_hits == 0, "network attempt")
    return {
        "critical_log_hits": critical_hits,
        "network_attempt_hits": network_hits,
        "engine_log_sha256": sha256(engine),
        "stdout_sha256": sha256(stdout),
        "stderr_sha256": sha256(stderr),
    }


def postflight() -> dict[str, Any]:
    contract = load_json(CONTRACT)
    verify_locked_inputs(contract)
    terminal, capture, restoration = verify_receipts()
    result = {
        "schema": "skyguard.phase4.m01-recovery05-unreal-proof01-postflight.v1",
        "gate": "PASSED_AUTOMATIC_AWAITING_HUMAN_VISUAL_REVIEW",
        "binding_id": BINDING_ID,
        "terminal": terminal,
        "restoration": restoration,
        "heartbeat": verify_heartbeat(),
        "metrics": verify_metrics(),
        "captures": verify_captures(capture),
        "logs": verify_logs(),
        "world_saved": False,
        "network_attempts": 0,
        "human_visual_review_required": True,
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline-contract-test", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args()
    result = offline_contract_test() if args.offline_contract_test else postflight()
    rendered = json.dumps(result, indent=2)
    if args.output:
        pathlib.Path(args.output).write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(
            json.dumps(
                {
                    "schema": "skyguard.phase4.m01-recovery05-unreal-proof01-postflight.v1",
                    "gate": "FAILED_WITH_EVIDENCE",
                    "error": str(exc),
                },
                indent=2,
            ),
            file=sys.stderr,
        )
        raise
