from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "verify_skyguard_input_combat_performance_gate.py"
)
SPEC = importlib.util.spec_from_file_location("input_combat_gate", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = (
    ROOT / "Scripts" / "skyguard_input_combat_performance_contract_v1.json"
)


def make_manifest(tmp_path: Path, markers_ready: bool) -> Path:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    source = []
    for window in contract["required_windows"]:
        for key in ("region", "begin_bookmark", "end_bookmark"):
            source.append(
                {
                    "window_id": window["id"],
                    "kind": key,
                    "literal": window[key],
                    "found": markers_ready,
                    "locations": [],
                }
            )
    trace_channels = contract["required_trace_channels"]
    csv_categories = contract["required_csv_categories"]
    manifest = {
        "schema": "skyguard.input-combat-performance.run.v1",
        "attempt_id": "attempt_20260802T120000000Z",
        "contract": {
            "path": str(CONTRACT),
            "sha256": MODULE.sha256(CONTRACT),
        },
        "controls": {"validate_only": True},
        "prerequisite": {"gate": "MISSING"},
        "source_instrumentation": source,
        "requested_profile": {
            "trace_channels": trace_channels,
            "csv_categories": csv_categories,
            "runtime_arguments": [
                "-d3d12",
                "-sm6",
                "-ResX=1920",
                "-ResY=1080",
                "-csvGpuStats",
                "-csvNamedEvents",
                f"-trace={','.join(trace_channels)}",
                "-tracefile=C:/capture.utrace",
            ],
            "external_gpu_telemetry": {"provider": "nvidia-smi"},
        },
        "execution": {"terminal_state": "VALIDATED_NOT_EXECUTED"},
        "artifacts": {},
    }
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    return path


class InputCombatGateTests(unittest.TestCase):
    def test_validate_only_is_blocked_by_missing_runtime_markers(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            report = MODULE.verify(make_manifest(Path(directory), False))
        self.assertEqual(report["contract_gate"], "PASS")
        self.assertEqual(
            report["gate"], "VALIDATED_CONTRACT_BLOCKED_RUNTIME_BOOKMARKS"
        )
        self.assertEqual(report["runtime_bookmark_coverage"]["found_literal_count"], 0)
        self.assertEqual(report["requirement_disposition"]["P8.10"], "NOT_EXECUTED")

    def test_ready_markers_still_do_not_promote_without_prerequisite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            report = MODULE.verify(make_manifest(Path(directory), True))
        self.assertEqual(report["contract_gate"], "PASS")
        self.assertEqual(
            report["gate"], "VALIDATED_CONTRACT_BLOCKED_PREREQUISITE"
        )
        self.assertTrue(report["runtime_bookmark_coverage"]["ready"])


if __name__ == "__main__":
    unittest.main()
