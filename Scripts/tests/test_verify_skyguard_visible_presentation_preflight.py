from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "verify_skyguard_visible_presentation_preflight.py"
)
SPEC = importlib.util.spec_from_file_location("visible_presentation_preflight", MODULE_PATH)
VERIFIER = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(VERIFIER)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class VisiblePresentationPreflightVerifierTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.bindings = []
        for label in ("package_launcher", "package_runtime"):
            path = self.root / f"{label}.exe"
            path.write_bytes(f"bound {label}".encode())
            self.bindings.append(
                {
                    "label": label,
                    "path": str(path),
                    "bytes": path.stat().st_size,
                    "sha256": digest(path),
                }
            )
        self.report = {
            "schema": VERIFIER.REPORT_SCHEMA,
            "attempt_id": "attempt_20260802T120000000Z",
            "generated_at_utc": "2026-08-02T12:00:30Z",
            "terminal_state": "EXECUTION_COMPLETE",
            "failure": None,
            "package_attempt_root": str(self.root),
            "configuration": {
                "visible": True,
                "rhi": "D3D12",
                "feature_level": "SM6",
                "resolution": {"x": 1280, "y": 720},
                "smoke_seconds": 10,
                "stage_timeout_seconds": 35,
                "module_sample_milliseconds": 250,
            },
            "bindings": self.bindings,
            "driver": {
                "query_complete": True,
                "query_error": None,
                "selected_adapter": {
                    "name": "NVIDIA GeForce RTX 3090",
                    "driver_version": "99.99",
                    "pnp_device_id": "PCI\\VEN_10DE&DEV_TEST",
                },
                "adapters": [],
            },
            "firewall": {
                "operation": "READ_ONLY_INSPECTION",
                "mutation_attempted": False,
                "target_program": str(self.root / "package_runtime.exe"),
                "query_complete": True,
                "query_error": None,
                "action_summary": "ALLOW",
                "rules": [
                    {
                        "name": "Skyguard test",
                        "enabled": True,
                        "action": "Allow",
                    }
                ],
            },
            "stages": [
                self.stage("entry_visible", "/Engine/Maps/Entry", "Entry"),
                self.stage(
                    "m01_visible",
                    "/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_Playable_v1",
                    "Lvl_M01_CoastalIntercept_Playable_v1",
                ),
            ],
        }

    def tearDown(self) -> None:
        self.temp.cleanup()

    def stage(self, name: str, map_path: str, receipt_map: str) -> dict:
        return {
            "name": name,
            "map": map_path,
            "status": "COMPLETE",
            "visible": True,
            "rhi": "D3D12",
            "feature_level": "SM6",
            "resolution": {"x": 1280, "y": 720},
            "smoke_seconds": 10,
            "supervisor_seconds": 35,
            "pid": 1234,
            "command_line": "Skyguard52.exe ...",
            "started_at_utc": "2026-08-02T12:00:00Z",
            "finished_at_utc": "2026-08-02T12:00:12Z",
            "elapsed_seconds": 12.0,
            "timed_out": False,
            "natural_exit": True,
            "exit_code": 0,
            "receipt": {
                "path": "receipt.json",
                "exists": True,
                "schema": "skyguard.shipping-startup-smoke.v1",
                "state": "COMPLETE",
                "map": receipt_map,
                "rhi": "D3D12 (SM6)",
            },
            "logs": {},
            "signatures": {
                "gpu_timeout_count": 0,
                "critical_signature_count": 0,
                "matches": [],
            },
            "module_scan": {
                "query_complete": True,
                "samples": 4,
                "errors": [],
                "overlay_modules": [],
            },
            "cleanup": {
                "needed": False,
                "attempted": False,
                "command": None,
                "exit_code": None,
                "post_cleanup_process_exists": False,
                "success": True,
            },
        }

    def verify(self, report: dict | None = None) -> dict:
        path = self.root / "report.json"
        path.write_text(json.dumps(report or self.report), encoding="utf-8")
        return VERIFIER.verify_report(path)

    def test_complete_synthetic_preflight_passes(self) -> None:
        result = self.verify()
        self.assertEqual("PASS", result["gate"])
        self.assertTrue(result["input_combat_gate_authorized"])
        self.assertTrue(all(result["checks"].values()))

    def test_map_ready_receipt_fails_closed(self) -> None:
        report = copy.deepcopy(self.report)
        report["stages"][0]["receipt"]["state"] = "MAP_READY"
        result = self.verify(report)
        self.assertEqual("FAIL", result["gate"])
        self.assertFalse(result["checks"]["all_receipts_complete"])

    def test_gpu_timeout_fails_closed(self) -> None:
        report = copy.deepcopy(self.report)
        report["stages"][0]["signatures"]["gpu_timeout_count"] = 2
        report["stages"][0]["signatures"]["critical_signature_count"] = 2
        result = self.verify(report)
        self.assertFalse(result["checks"]["no_gpu_timeouts"])
        self.assertFalse(result["input_combat_gate_authorized"])

    def test_loaded_overlay_module_fails_closed(self) -> None:
        report = copy.deepcopy(self.report)
        report["stages"][0]["status"] = "FAILED"
        report["stages"][0]["module_scan"]["overlay_modules"] = [
            {
                "module_name": "nvspcap64.dll",
                "path": "C:\\example\\nvspcap64.dll",
            }
        ]
        result = self.verify(report)
        self.assertFalse(result["checks"]["no_overlay_modules"])
        self.assertTrue(result["checks"]["natural_clean_exit"])

    def test_enabled_firewall_block_fails_closed(self) -> None:
        report = copy.deepcopy(self.report)
        report["firewall"]["action_summary"] = "BLOCK"
        report["firewall"]["rules"][0]["action"] = "Block"
        result = self.verify(report)
        self.assertFalse(result["checks"]["firewall_no_enabled_block"])

    def test_firewall_query_for_different_binary_fails_closed(self) -> None:
        report = copy.deepcopy(self.report)
        report["firewall"]["target_program"] = "C:\\different\\Skyguard52.exe"
        result = self.verify(report)
        self.assertFalse(result["checks"]["firewall_exact_runtime"])

    def test_unclean_process_cleanup_fails_closed(self) -> None:
        report = copy.deepcopy(self.report)
        report["stages"][1]["cleanup"]["success"] = False
        report["stages"][1]["cleanup"]["post_cleanup_process_exists"] = True
        result = self.verify(report)
        self.assertFalse(result["checks"]["process_cleanup"])

    def test_tampered_package_binding_fails_closed(self) -> None:
        Path(self.bindings[1]["path"]).write_bytes(b"tampered")
        result = self.verify()
        self.assertFalse(result["checks"]["binding_hashes"])

    def test_wrong_m01_receipt_map_fails_closed(self) -> None:
        report = copy.deepcopy(self.report)
        report["stages"][1]["receipt"]["map"] = "Entry"
        result = self.verify(report)
        self.assertFalse(result["checks"]["all_receipts_complete"])


if __name__ == "__main__":
    unittest.main()
