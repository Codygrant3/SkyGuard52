#!/usr/bin/env python3
"""Validate profile receipt structure and fail closed on missing memory evidence."""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

SHA = re.compile(r"^[0-9a-f]{64}$")
SCENARIOS = {"boot_to_briefing", "rear_gunner_traversal", "ads_rifle_drone_breakup", "igla_lock_launch_heavy", "boss_destruction", "weather_transition", "soak_20min"}


def validate(data: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["root must be object"]
    if data.get("schema") != "skyguard.profiling-receipt.v1": errors.append("schema mismatch")
    if data.get("scenario") not in SCENARIOS: errors.append("scenario unsupported")
    execution = data.get("execution", {})
    if execution.get("retries") != 0: errors.append("automatic retries must be zero")
    if execution.get("rhi") != "D3D12_SM6": errors.append("rhi must be D3D12_SM6")
    if execution.get("timeout") is not False: errors.append("timeout must be false")
    if not isinstance(execution.get("exit_code"), int) or isinstance(execution.get("exit_code"), bool): errors.append("numeric exit_code required")
    insights = data.get("insights", {})
    channels = set(insights.get("trace_channels", []))
    if not {"cpu", "gpu", "frame", "memory"}.issubset(channels): errors.append("required Insights channels absent")
    frameview = data.get("frameview", {})
    if frameview.get("provider") != "NVIDIA_FrameView_PresentMon": errors.append("FrameView provider mismatch")
    for group_name in ("build", "insights", "frameview"):
        digest = data.get(group_name, {}).get("sha256" if group_name == "build" else "tool_sha256")
        if not isinstance(digest, str) or not SHA.fullmatch(digest): errors.append(f"{group_name}: invalid SHA-256")
    metrics = data.get("metrics", {})
    for key in ("sample_count", "mean_ms", "p95_ms", "p99_ms", "max_ms", "frames_over_50ms", "frames_over_100ms", "peak_working_set_mb", "peak_gpu_memory_mb"):
        value = metrics.get(key)
        if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value) or value < 0: errors.append(f"metrics.{key}: finite nonnegative number required")
    if metrics.get("sample_count", 0) < 900 and data.get("classification") != "DIAGNOSTIC_ONLY": errors.append("at least 900 samples required")
    if metrics.get("peak_gpu_memory_mb", 0) <= 0: errors.append("explicit GPU-memory evidence required")
    if data.get("classification") == "PASSED_PROFILE_CAPTURE_AWAITING_REVIEW":
        if metrics.get("mean_ms", math.inf) > 16.7 or metrics.get("p95_ms", math.inf) > 22.2 or metrics.get("max_ms", math.inf) > 100 or metrics.get("frames_over_100ms") != 0:
            errors.append("passing capture exceeds frozen performance limits")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", required=True)
    args = parser.parse_args()
    try: data = json.loads(Path(args.receipt).read_text(encoding="utf-8"))
    except Exception as exc:
        print(json.dumps({"result": "FAIL", "errors": [str(exc)]}, indent=2)); return 2
    errors = validate(data)
    print(json.dumps({"result": "PASS" if not errors else "FAIL", "errors": errors}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__": sys.exit(main())
