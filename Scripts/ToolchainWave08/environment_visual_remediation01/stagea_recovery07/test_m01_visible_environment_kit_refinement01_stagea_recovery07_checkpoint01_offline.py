from __future__ import annotations

import ast
import importlib.util
import unittest
from pathlib import Path


WORKER = Path(__file__).with_name(
    "build_m01_visible_environment_kit_refinement01_stagea_recovery07_checkpoint01.py"
)


def load_worker():
    spec = importlib.util.spec_from_file_location("skyguard_r07_worker_test", WORKER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load Recovery07 worker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Recovery07WorkerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_worker()
        cls.source, cls.receipt = cls.module.load_recovery07_source()
        cls.tree = ast.parse(cls.source)

    def test_generated_source_parses_and_has_no_unresolved_calls(self) -> None:
        self.assertTrue(self.receipt["generated_call_graph"]["passed"])
        self.assertEqual([], self.receipt["generated_call_graph"]["unresolved_named_calls"])

    def test_fast_box_replaces_operator_box_path(self) -> None:
        functions = {
            node.name: node
            for node in self.tree.body
            if isinstance(node, ast.FunctionDef)
        }
        add_box_source = ast.get_source_segment(self.source, functions["add_box"])
        self.assertIn("_fast_box_mesh", add_box_source)
        self.assertNotIn("bpy.ops", add_box_source)
        self.assertIn("bmesh.ops.bevel", self.source)

    def test_phase_telemetry_is_flushed_and_bounded(self) -> None:
        self.assertIn('trace_phase("building_complete"', self.source)
        self.assertIn('trace_phase("checkpoint_render_start"', self.source)
        self.assertIn("flush=True", self.source)
        self.assertEqual(9, self.receipt["checkpoint_count"])

    def test_visual_and_output_contract_remain_checkpoint_only(self) -> None:
        self.assertIn('require(len(results) == 9, "Checkpoint render count is not exactly nine")', self.source)
        self.assertIn('"finalization_authorized":False', self.source)
        self.assertEqual(0, self.receipt["glb_count"])
        self.assertEqual(0, self.receipt["texture_count"])
        self.assertFalse(self.receipt["recovery06_attempt_or_output_reused"])

    def test_recovery06_worker_is_frozen(self) -> None:
        self.assertEqual(7427, self.module.RECOVERY06_WORKER.stat().st_size)
        self.assertEqual(
            self.module.RECOVERY06_WORKER_SHA256,
            self.module.sha256_file(self.module.RECOVERY06_WORKER),
        )


if __name__ == "__main__":
    unittest.main()
