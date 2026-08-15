#!/usr/bin/env python3
"""Focused tests for the StageB source-preparation gate."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("verify_m01_visible_environment_kit_refinement01_stageb_source.py")
SPEC = importlib.util.spec_from_file_location("stageb_verifier", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class StageBSourceTests(unittest.TestCase):
    def test_complete_source_gate_passes(self) -> None:
        result = MODULE.verify()
        self.assertEqual("PASS", result["classification"], result["failures"])

    def test_stagea_acceptance_is_required(self) -> None:
        contract = json.loads(MODULE.CONTRACT.read_text(encoding="utf-8"))
        self.assertTrue(contract["stagea_dependency"]["stageb_must_not_launch_before_dependency"])
        self.assertEqual(
            "PASSED_READY_FOR_M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEB",
            contract["stagea_dependency"]["required_before_stageb_authorization"],
        )

    def test_output_cardinality(self) -> None:
        contract = json.loads(MODULE.CONTRACT.read_text(encoding="utf-8"))
        output = contract["output_contract"]
        self.assertEqual((1, 6, 3, 15, 5), (output["blend_count"], output["glb_count"], output["checkpoint_png_count"], output["final_png_count"], output["texture_png_count"]))

    def test_no_external_import_paths(self) -> None:
        source = MODULE.SOURCE.read_text(encoding="utf-8")
        for token in ("bpy.ops.import_scene", "bpy.data.libraries.load", "requests.get", "urllib.request"):
            self.assertNotIn(token, source)

    def test_future_stageb_namespaces_absent(self) -> None:
        self.assertFalse([path for path in MODULE.FUTURE_PATHS if path.exists()])

    def test_machine_readable_report(self) -> None:
        with tempfile.TemporaryDirectory(prefix="sg52_stageb_source_") as temporary:
            output = Path(temporary) / "report.json"
            result = MODULE.verify(output)
            loaded = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(result["classification"], loaded["classification"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
