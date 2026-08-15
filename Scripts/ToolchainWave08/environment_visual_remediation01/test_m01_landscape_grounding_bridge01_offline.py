#!/usr/bin/env python3
"""Focused offline tests for the Mission 1 Landscape grounding bridge gate."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("verify_m01_landscape_grounding_bridge01_offline.py")
SPEC = importlib.util.spec_from_file_location("grounding_verifier", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class GroundingBridgeOfflineTests(unittest.TestCase):
    def test_complete_gate_passes(self) -> None:
        result = MODULE.verify()
        self.assertEqual("PASS", result["classification"], result["failures"])

    def test_source_contract_has_exact_counts(self) -> None:
        contract = json.loads((MODULE.DOC_ROOT / "source_contract.json").read_text(encoding="utf-8"))
        self.assertEqual([5, 9, 13], contract["api"]["permitted_footprint_counts"])
        self.assertEqual(1.0, contract["api"]["required_supported_fraction"])

    def test_parity_contains_new_sources(self) -> None:
        parity = json.loads(MODULE.PARITY.read_text(encoding="utf-8"))
        paths = {record["relative_path"] for record in parity["records"]}
        self.assertIn("Source/Skyguard52/SkyguardMission01LandscapeGroundingLibrary.cpp", paths)
        self.assertIn("Source/Skyguard52/SkyguardMission01LandscapeGroundingTests.cpp", paths)

    def test_verifier_writes_machine_readable_report(self) -> None:
        with tempfile.TemporaryDirectory(prefix="sg52_grounding_test_") as temp:
            output = Path(temp) / "result.json"
            result = MODULE.verify(output)
            loaded = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(result["classification"], loaded["classification"])
            self.assertEqual("PASS", loaded["classification"])

    def test_future_namespaces_are_absent(self) -> None:
        self.assertFalse([path for path in MODULE.FUTURE_PATHS if path.exists()])

    def test_no_mutation_tokens_in_implementation(self) -> None:
        cpp = (
            MODULE.ROOT
            / "Source"
            / "Skyguard52"
            / "SkyguardMission01LandscapeGroundingLibrary.cpp"
        ).read_text(encoding="utf-8")
        for token in ("SetActorLocation", "SavePackage", "LineTrace", "Landscape->Modify"):
            self.assertNotIn(token, cpp)


if __name__ == "__main__":
    unittest.main(verbosity=2)
