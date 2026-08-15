#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
PBR = HERE.parents[2] / "Production" / "Templates" / "PBR"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


pbr_validator = load_module("pbr_validator", HERE / "validate_pbr_manifest.py")
profile_validator = load_module("profile_validator", HERE / "validate_profiling_receipt.py")
sentry_validator = load_module("sentry_validator", HERE / "validate_sentry_readiness.py")


class ToolchainWave08Tests(unittest.TestCase):
    def test_pbr_example_passes_structure(self):
        data = json.loads((PBR / "example_pbr_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual([], pbr_validator.validate(data))

    def test_high_to_low_requires_high_source(self):
        data = json.loads((PBR / "example_pbr_manifest.json").read_text(encoding="utf-8"))
        data["bake_method"] = "high_to_low"
        self.assertTrue(any("source.high" in item for item in pbr_validator.validate(data)))

    def test_profile_rejects_missing_gpu_memory(self):
        data = valid_profile_receipt()
        data["metrics"]["peak_gpu_memory_mb"] = 0
        self.assertTrue(any("GPU-memory" in item for item in profile_validator.validate(data)))

    def test_profile_rejects_retry(self):
        data = valid_profile_receipt(); data["execution"]["retries"] = 1
        self.assertTrue(any("retries" in item for item in profile_validator.validate(data)))

    def test_sentry_current_state_is_honestly_blocked(self):
        path = HERE / "sentry_readiness.json"
        raw = path.read_text(encoding="utf-8")
        self.assertEqual([], sentry_validator.validate(json.loads(raw), raw))

    def test_sentry_rejects_embedded_dsn(self):
        path = HERE / "sentry_readiness.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["credentials"]["example"] = "https://abc@example.ingest.sentry.io/123"
        raw = json.dumps(data)
        self.assertTrue(any("DSN" in item for item in sentry_validator.validate(data, raw)))


def valid_profile_receipt() -> dict:
    sha = "0" * 64
    return {
        "schema": "skyguard.profiling-receipt.v1",
        "attempt_id": "attempt_20260807T120000000Z",
        "classification": "PASSED_PROFILE_CAPTURE_AWAITING_REVIEW",
        "build": {"configuration": "Development", "executable": "D:/build.exe", "sha256": sha},
        "scenario": "ads_rifle_drone_breakup",
        "execution": {"duration_seconds": 120, "resolution": "1920x1080", "rhi": "D3D12_SM6", "exit_code": 0, "timeout": False, "retries": 0},
        "insights": {"tool": "UnrealInsights.exe", "tool_sha256": sha, "trace_channels": ["cpu", "gpu", "frame", "memory"], "trace": {}},
        "frameview": {"provider": "NVIDIA_FrameView_PresentMon", "tool": "PresentMon_x64.exe", "tool_sha256": sha, "csv": {}},
        "metrics": {"sample_count": 900, "mean_ms": 10, "p95_ms": 15, "p99_ms": 18, "max_ms": 40, "frames_over_50ms": 0, "frames_over_100ms": 0, "peak_working_set_mb": 4096, "peak_gpu_memory_mb": 8000},
        "artifacts": [{}, {}, {}, {}, {}], "limitations": []
    }


if __name__ == "__main__": unittest.main(verbosity=2)

