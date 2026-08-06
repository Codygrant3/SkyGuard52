from __future__ import annotations

import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "verify_skyguard_phase8_pso_workflow.py"
SPEC = importlib.util.spec_from_file_location("pso_verifier", MODULE_PATH)
VERIFIER = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(VERIFIER)


class PsoWorkflowVerifierTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.config = self.root / "DefaultEngine.ini"
        self.config.write_text(
            "[DevOptions.Shaders]\nNeedsShaderStableKeys=True\n"
            "[SystemSettings]\nr.ShaderPipelineCache.Enabled=1\n"
            "r.PSOPrecaching=1\n",
            encoding="utf-8",
        )
        self.exe = self.write("Skyguard52.exe", b"exe")
        self.matrix = self.write("matrix.json", b"matrix")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write(self, name: str, data: bytes) -> Path:
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    @staticmethod
    def record(path: Path) -> dict:
        return {
            "path": str(path),
            "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }

    def preflight(self) -> dict:
        return {
            "phase": "PREFLIGHT",
            "config": str(self.config),
            "package_executable": self.record(self.exe),
            "mission_matrix": self.record(self.matrix),
        }

    def test_preflight_passes(self) -> None:
        self.assertEqual("PASS", VERIFIER.evaluate(self.preflight())["gate"])

    def test_tampered_bound_executable_fails(self) -> None:
        manifest = self.preflight()
        self.exe.write_bytes(b"tampered")
        report = VERIFIER.evaluate(manifest)
        self.assertEqual("FAIL", report["gate"])
        self.assertFalse(report["checks"]["bound_package_executable"])

    def make_packaged_manifest(self) -> tuple[dict, Path]:
        manifest = self.preflight()
        stable = self.write(
            "Skyguard52_PCD3D_SM6.spc", b"stable"
        )
        shk = self.write("ShaderStableInfo-Skyguard52-PCD3D_SM6.shk", b"keys")
        cooked = self.write(
            "Skyguard52_PCD3D_SM6.stable.upipelinecache", b"cooked"
        )
        shipping = self.root / "shipping"
        utoc = shipping / "Skyguard52-Windows.utoc"
        utoc.parent.mkdir(parents=True)
        utoc.write_bytes(cooked.name.encode())
        log = self.write("capture.log", b"clean")
        captures = []
        for index in range(1, 11):
            cache = self.write(f"M{index:02d}.rec.upipelinecache", b"capture")
            captures.append(
                {
                    "mission": f"M{index:02d}",
                    "cache": self.record(cache),
                    "exit_code": 0,
                    "timed_out": False,
                    "log": str(log),
                }
            )
        manifest.update(
            {
                "phase": "PACKAGED",
                "captures": captures,
                "stable_cache": self.record(stable),
                "stable_keys": [self.record(shk)],
                "stabilize_stage": {"exit_code": 0, "timed_out": False},
                "packaged_cache": {
                    "shipping_root": str(shipping),
                    "shipping_executable": self.record(self.exe),
                    "expected_name": cooked.name,
                    "cooked_cache": self.record(cooked),
                    "shipping_utocs": [self.record(utoc)],
                },
            }
        )
        return manifest, utoc

    def test_packaged_cache_requires_shipping_index(self) -> None:
        manifest, utoc = self.make_packaged_manifest()
        self.assertEqual("PASS", VERIFIER.evaluate(manifest)["gate"])
        utoc.write_bytes(b"missing-cache")
        self.assertEqual("FAIL", VERIFIER.evaluate(manifest)["gate"])

    def test_loose_runtime_seed_requires_matching_staged_hashes(self) -> None:
        manifest, utoc = self.make_packaged_manifest()
        source = self.write(
            "Build/Windows/PipelineCaches/"
            "Skyguard52_PCD3D_SM6.stable.upipelinecache",
            b"merged-cache",
        )
        development_cache = self.write(
            "development/Skyguard52/Content/PipelineCaches/Windows/"
            "Skyguard52_PCD3D_SM6.stable.upipelinecache",
            b"merged-cache",
        )
        shipping_cache = self.write(
            "shipping/Skyguard52/Content/PipelineCaches/Windows/"
            "Skyguard52_PCD3D_SM6.stable.upipelinecache",
            b"merged-cache",
        )
        manifest["packaged_cache"].update(
            {
                "mode": "loose_nonufs_runtime_seed",
                "development_executable": self.record(self.exe),
                "source_cache": self.record(source),
                "development_cache": self.record(development_cache),
                "packaged_cache": self.record(shipping_cache),
            }
        )
        manifest["packaged_cache"].pop("cooked_cache")
        utoc.write_bytes(b"container-index-without-loose-cache")
        manifest["packaged_cache"]["shipping_utocs"] = [self.record(utoc)]
        self.assertEqual("PASS", VERIFIER.evaluate(manifest)["gate"])
        shipping_cache.write_bytes(b"tampered")
        self.assertEqual("FAIL", VERIFIER.evaluate(manifest)["gate"])

    def test_cook_native_fallback_requires_two_engine_defect_receipts(self) -> None:
        manifest = self.preflight()
        shk = self.write("ShaderStableInfo-Skyguard52-PCD3D_SM6.shk", b"keys")
        first = self.write("loader-failure-1.log", b"failure one")
        second = self.write("loader-failure-2.log", b"failure two")
        log = self.write("capture.log", b"clean")
        captures = []
        for index in range(1, 11):
            cache = self.write(f"fallback-M{index:02d}.rec.upipelinecache", b"capture")
            captures.append(
                {
                    "mission": f"M{index:02d}",
                    "cache": self.record(cache),
                    "exit_code": 0,
                    "timed_out": False,
                    "log": str(log),
                }
            )
        manifest.update(
            {
                "phase": "STABILIZED",
                "captures": captures,
                "stabilization_mode": "cook_native_compute_fallback",
                "stable_keys": [self.record(shk)],
                "stable_cache": None,
                "stabilize_stage": {
                    "mode": "cook_native_compute_fallback",
                    "recorded_graphics_cache_status":
                        "BLOCKED_UE58_BINARY_LOADER_DEFECT",
                    "cook_generated_cache_required": True,
                    "engine_defect_evidence": [
                        self.record(first),
                        self.record(second),
                    ],
                },
            }
        )
        self.assertEqual("PASS", VERIFIER.evaluate(manifest)["gate"])
        manifest["stabilize_stage"]["engine_defect_evidence"].pop()
        self.assertEqual("FAIL", VERIFIER.evaluate(manifest)["gate"])

    def test_raw_binary_merge_requires_nine_clean_steps_and_valid_dump(self) -> None:
        manifest = self.preflight()
        stable = self.write(
            "Build/Windows/PipelineCaches/"
            "Skyguard52_PCD3D_SM6.stable.upipelinecache",
            b"merged-cache",
        )
        validated = self.write("raw/merge_step_10.upipelinecache", b"merged-cache")
        shk = self.write("ShaderStableInfo-Skyguard52-PCD3D_SM6.shk", b"keys")
        capture_log = self.write("capture.log", b"clean")
        dump_log = self.write("dump.log", b"Total PSOs logged: 94\n")
        captures = []
        for index in range(1, 11):
            cache = self.write(f"raw-M{index:02d}.rec.upipelinecache", b"capture")
            captures.append(
                {
                    "mission": f"M{index:02d}",
                    "cache": self.record(cache),
                    "exit_code": 0,
                    "timed_out": False,
                    "log": str(capture_log),
                }
            )
        steps = []
        for index in range(2, 11):
            output = self.write(f"raw/merge_step_{index:02d}.upipelinecache", b"merged")
            if index == 10:
                output.write_bytes(b"merged-cache")
            steps.append(
                {
                    "output": self.record(output),
                    "stage": {"exit_code": 0, "timed_out": False},
                }
            )
        manifest.update(
            {
                "phase": "STABILIZED",
                "captures": captures,
                "stabilization_mode": "raw_recorded_binary_merge",
                "stable_keys": [self.record(shk)],
                "stable_cache": self.record(stable),
                "stabilize_stage": {
                    "mode": "raw_recorded_binary_merge",
                    "merge_steps": steps,
                    "dump_stage": {"exit_code": 0, "timed_out": False},
                    "dump_log": self.record(dump_log),
                    "total_pso_count": 94,
                    "validated_merge_output": self.record(validated),
                },
            }
        )
        self.assertEqual("PASS", VERIFIER.evaluate(manifest)["gate"])
        manifest["stabilize_stage"]["merge_steps"].pop()
        self.assertEqual("FAIL", VERIFIER.evaluate(manifest)["gate"])

    def test_consumption_requires_bundled_open_and_precompile_complete(self) -> None:
        manifest, _ = self.make_packaged_manifest()
        log = self.write(
            "consumption.log",
            (
                b"Opened FPipelineCacheFile: ../../../Skyguard52/Content/"
                b"PipelineCaches/Windows/"
                b"Skyguard52_PCD3D_SM6.stable.upipelinecache with 42 entries.\n"
                b"FShaderPipelineCache starting pipeline cache 'Skyguard52' "
                b"(cache contains 42, 42 eligible, 0 had missing shaders. "
                b"0 already compiled).\n"
                b"FShaderPipelineCache Skyguard52 completed 42 tasks in 0.25s\n"
            ),
        )
        manifest["phase"] = "CONSUMED"
        manifest["consumption"] = {
            "exit_code": 0,
            "timed_out": False,
            "log": str(log),
        }
        self.assertEqual("PASS", VERIFIER.evaluate(manifest)["gate"])
        log.write_bytes(b"Could not open FPipelineCacheFile")
        self.assertEqual("FAIL", VERIFIER.evaluate(manifest)["gate"])


if __name__ == "__main__":
    unittest.main()
