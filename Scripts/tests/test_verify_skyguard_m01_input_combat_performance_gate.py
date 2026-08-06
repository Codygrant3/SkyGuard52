from __future__ import annotations

import copy
import csv
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "verify_skyguard_m01_input_combat_performance_gate.py"
)
SPEC = importlib.util.spec_from_file_location("m01_input_combat_gate", MODULE_PATH)
VERIFIER = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(VERIFIER)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class M01InputCombatPerformanceVerifierTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.bindings = []
        for label in (
            "package_executable",
            "package_runtime_binary",
            "source_map",
            "uproject",
            "default_engine_config",
            "default_game_config",
            "default_input_config",
            "packaged_pso_cache",
        ):
            path = self.root / f"{label}.bin"
            path.write_bytes(f"bound {label}".encode())
            self.bindings.append(
                {
                    "label": label,
                    "path": str(path),
                    "bytes": path.stat().st_size,
                    "sha256": sha(path),
                }
            )
        self.stages = [
            self.make_stage("combat_01", "combat", 180),
            self.make_stage("combat_02", "combat", 180),
            self.make_stage("combat_03", "combat", 180),
            self.make_stage("soak_01", "soak", 1200),
        ]
        self.manifest = {
            "schema": VERIFIER.MANIFEST_SCHEMA,
            "terminal_state": "EXECUTION_COMPLETE",
            "package_configuration": "Development",
            "expected_map": VERIFIER.EXPECTED_MAP,
            "bindings": self.bindings,
            "stages": self.stages,
        }

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_json(self, name: str, value: dict) -> Path:
        path = self.root / name
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def make_events(self, duration: int) -> list[dict]:
        names = [
            "aim_input",
            "ads_started",
            "ads_left_fire_overlap",
            "rifle_shot",
            "rifle_shot",
            "rifle_shot",
            "rifle_shot",
            "rifle_shot",
            "weapon_switch",
            "igla_lock_acquired",
            "igla_launch",
            "drone_breakup",
            "boss_destroyed",
            "weather_visibility_transition",
        ]
        return [
            {
                "name": name,
                "seconds_from_measurement_start": round(
                    5.0 + index * ((duration - 10.0) / len(names)), 3
                ),
            }
            for index, name in enumerate(names)
        ]

    def make_stage(self, name: str, kind: str, duration: int) -> dict:
        receipt = self.write_json(
            f"{name}.receipt.json",
            {
                "schema": VERIFIER.RUNTIME_SCHEMA,
                "state": "COMPLETE",
                "gate": "PASS",
                "run_id": name,
                "map": VERIFIER.EXPECTED_MAP,
                "resolution": {"x": 1920, "y": 1080},
                "rhi": "D3D12 (SM6)",
                "input_source": "PlayerInput",
                "automation_injected": False,
                "measurement_window": {
                    "started_at_utc": "2026-08-02T00:00:00Z",
                    "ended_at_utc": "2026-08-02T00:20:00Z",
                    "duration_seconds": duration,
                },
                "events": self.make_events(duration),
            },
        )
        frame_count = duration * 45 + 120
        csv_path = self.root / f"{name}.csv"
        with csv_path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(["FrameTime", "GPUTime"])
            writer.writerows([[12.0, 7.0]] * frame_count)
        memory = self.root / f"{name}.memory.csv"
        with memory.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(
                [
                    "timestamp_utc",
                    "elapsed_seconds",
                    "working_set_bytes",
                    "private_memory_bytes",
                ]
            )
            for second in range(duration + 1):
                writer.writerow(
                    [
                        "2026-08-02T00:00:00Z",
                        second,
                        2_000_000_000 + second * 1024,
                        2_100_000_000 + second * 1024,
                    ]
                )
        trace = self.root / f"{name}.utrace"
        trace.write_bytes(b"trace" * 1000)
        stdout = self.root / f"{name}.stdout.log"
        stdout.write_text(
            "Opened FPipelineCacheFile: Skyguard52_PCD3D_SM6.stable.upipelinecache\n"
            "FShaderPipelineCache Skyguard completed 97 tasks\n"
            "0 had missing shaders\n",
            encoding="utf-8",
        )
        stderr = self.root / f"{name}.stderr.log"
        stderr.write_text("", encoding="utf-8")
        return {
            "name": name,
            "kind": kind,
            "requested_duration_seconds": duration,
            "resolution": {"x": 1920, "y": 1080},
            "timed_out": False,
            "exit_code": 0,
            "runtime_receipt": str(receipt),
            "csv": str(csv_path),
            "trace": str(trace),
            "memory_series": str(memory),
            "stdout": str(stdout),
            "stderr": str(stderr),
        }

    def evaluate(self, manifest: dict | None = None) -> dict:
        path = self.write_json("manifest.json", manifest or self.manifest)
        return VERIFIER.verify_manifest(path)

    def test_complete_synthetic_attempt_passes(self) -> None:
        report = self.evaluate()
        self.assertEqual("PASS", report["gate"])
        self.assertTrue(report["checks"]["all_four_stages_pass"])

    def test_missing_fourth_stage_fails(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["stages"] = manifest["stages"][:3]
        report = self.evaluate(manifest)
        self.assertEqual("FAIL", report["gate"])
        self.assertFalse(report["checks"]["exact_stage_sequence"])

    def test_tampered_executable_binding_fails(self) -> None:
        Path(self.bindings[0]["path"]).write_bytes(b"tampered")
        report = self.evaluate()
        self.assertEqual("FAIL", report["gate"])
        self.assertFalse(report["checks"]["binding_hashes"])

    def test_missing_igla_launch_fails(self) -> None:
        receipt_path = Path(self.stages[0]["runtime_receipt"])
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        receipt["events"] = [
            event for event in receipt["events"] if event["name"] != "igla_launch"
        ]
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
        report = self.evaluate()
        self.assertEqual("FAIL", report["gate"])
        first = report["stages"][0]
        self.assertFalse(first["checks"]["runtime_event_igla_launch"])

    def test_event_outside_measurement_window_fails(self) -> None:
        receipt_path = Path(self.stages[1]["runtime_receipt"])
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        receipt["events"][0]["seconds_from_measurement_start"] = 9999
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
        report = self.evaluate()
        self.assertEqual("FAIL", report["gate"])
        self.assertFalse(
            report["stages"][1]["checks"]["runtime_events_inside_window"]
        )

    def test_soak_memory_leak_fails(self) -> None:
        memory = Path(self.stages[3]["memory_series"])
        with memory.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(["elapsed_seconds", "working_set_bytes"])
            for second in range(1201):
                writer.writerow([second, 2_000_000_000 + second * 2_000_000])
        report = self.evaluate()
        self.assertEqual("FAIL", report["gate"])
        self.assertFalse(report["stages"][3]["checks"]["memory_stable_slope"])

    def test_missing_pso_completion_marker_fails(self) -> None:
        Path(self.stages[2]["stdout"]).write_text(
            "Opened FPipelineCacheFile: Skyguard52_PCD3D_SM6.stable.upipelinecache\n"
            "0 had missing shaders\n",
            encoding="utf-8",
        )
        report = self.evaluate()
        self.assertEqual("FAIL", report["gate"])
        self.assertFalse(report["stages"][2]["checks"]["pso_precompile_completed"])

    def test_automation_injected_input_fails(self) -> None:
        receipt_path = Path(self.stages[0]["runtime_receipt"])
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        receipt["automation_injected"] = True
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
        report = self.evaluate()
        self.assertEqual("FAIL", report["gate"])
        self.assertFalse(
            report["stages"][0]["checks"]["runtime_not_automation_injected"]
        )


if __name__ == "__main__":
    unittest.main()
