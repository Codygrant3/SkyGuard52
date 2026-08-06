from __future__ import annotations

import ast
import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT_PATH = (
    ROOT
    / "Docs/AAA_Review/"
    "PHASE4_M01_LANDSCAPE_VISIBLE_ATTEMPT07_RECOVERY02_CONTRACT.json"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


class Attempt07Recovery02Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(
            CONTRACT_PATH.read_text(encoding="utf-8-sig")
        )

    def test_recovery01_failure_is_exhaustively_bound(self) -> None:
        failed = self.contract["immutable_recovery01_failure"]
        root = ROOT / failed["root"]
        files = sorted(path for path in root.rglob("*") if path.is_file())
        expected = {
            item["file"]: item for item in failed["files"].values()
        }
        self.assertEqual(len(files), len(expected))
        for path in files:
            relative = path.relative_to(root).as_posix()
            self.assertIn(relative, expected)
            self.assertEqual(path.stat().st_size, expected[relative]["bytes"])
            self.assertEqual(
                sha256_file(path), expected[relative]["sha256"]
            )

    def test_recovery01_exact_live_failure_is_preserved(self) -> None:
        failed = self.contract["immutable_recovery01_failure"]
        root = ROOT / failed["root"]
        manifest = json.loads(
            (root / "run_manifest.json").read_text(
                encoding="utf-8-sig"
            )
        )
        self.assertEqual(manifest["terminal_state"], "FAILED")
        self.assertEqual(
            [stage["exit_code"] for stage in manifest["stages"]],
            [0, 0, 3],
        )
        self.assertFalse((root / "tiny_proof_receipt.json").exists())
        log = (
            root / failed["files"]["proof_engine_log"]["file"]
        ).read_text(encoding="utf-8", errors="replace")
        self.assertIn('"compilation_finished_resource_count": 0', log)
        self.assertIn('"valid_shader_map_resource_count": 16', log)
        self.assertIn('"asset_compilation_queue_empty": false', log)
        self.assertIn('"shader_compilation_queue_empty": false', log)

    def test_implementation_hashes_and_python_syntax(self) -> None:
        for item in self.contract["implementation_files"].values():
            path = ROOT / item["file"]
            self.assertTrue(path.is_file(), path)
            self.assertEqual(sha256_file(path), item["sha256"], path)
            if path.suffix == ".py":
                ast.parse(path.read_text(encoding="utf-8"))

    def test_native_deferred_begin_has_no_blocking_finish(self) -> None:
        path = ROOT / self.contract["implementation_files"][
            "native_implementation"
        ]["file"]
        source = path.read_text(encoding="utf-8")
        section = source.split(
            "BeginTransientLandscapeDiagnosticMaterialDeferred(", 1
        )[1].split("SetTransientLandscapeDiagnosticMaterial(", 1)[0]
        self.assertIn(
            "Landscape->UpdateAllComponentMaterialInstances(true)", section
        )
        self.assertIn("RecreateRenderState_Concurrent", section)
        self.assertNotIn("FinishAllCompilation", section)
        self.assertNotIn("Resource->FinishCompilation", section)

    def test_proof_waits_on_later_ticks_and_all_readiness_fields(self) -> None:
        path = ROOT / self.contract["implementation_files"][
            "recovery02_tiny_proof"
        ]["file"]
        source = path.read_text(encoding="utf-8")
        self.assertIn("register_slate_post_tick_callback", source)
        self.assertIn("set_keep_python_script_alive(True)", source)
        ready = source.split("def compilation_ready", 1)[1].split(
            "class Recovery02State", 1
        )[0]
        for token in (
            'audit["compilation_finished_resource_count"] == 16',
            'audit["valid_shader_map_resource_count"] == 16',
            'audit["asset_compilation_queue_empty"]',
            'audit["shader_compilation_queue_empty"]',
        ):
            self.assertIn(token, ready)
        tick = source.split(
            "def tick(self, delta_time: float)", 1
        )[1].split("def common_report", 1)[0]
        gate = tick.index("if self.stable_ready_ticks < required:")
        self.assertLess(gate, tick.index("self.capture_coverage()"))
        self.assertLess(gate, tick.index("self.capture_component()"))

    def test_execution_is_unauthorized_and_output_absent(self) -> None:
        for field in (
            "unreal_launch_allowed",
            "native_build_allowed",
            "author_stage_allowed",
            "tiny_live_proof_allowed",
            "full_capture_allowed",
            "profile_allowed",
            "automatic_retry_allowed",
            "network_allowed",
            "promotion_allowed",
        ):
            self.assertFalse(
                self.contract["execution_authorization"][field], field
            )
        self.assertFalse(
            (
                ROOT / self.contract["tiny_live_proof"]["execution_root"]
            ).exists()
        )


if __name__ == "__main__":
    unittest.main()
