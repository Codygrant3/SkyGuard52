from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("adjudicate_completed_authoring.py")
SPEC = importlib.util.spec_from_file_location("adjudicator", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class AdjudicatorTests(unittest.TestCase):
    def test_authorities_and_completed_output_pass(self) -> None:
        result = MODULE.adjudicate()
        self.assertEqual(
            result["classification"],
            "PASSED_RECOVERY02_AUTHORING_OUTPUT_ACCEPTED_AFTER_INDEPENDENT_POSTFLIGHT",
        )
        self.assertEqual(result["unreal_launches_during_adjudication"], 0)
        self.assertFalse(result["source_attempt_reused_or_retried"])

    def test_hash_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.bin"
            path.write_bytes(b"fixture")
            with self.assertRaises(ValueError):
                MODULE.verify_authority(path, len(b"fixture"), "0" * 64)

    def test_fatal_log_pattern_is_bounded(self) -> None:
        self.assertIsNotNone(MODULE.FATAL_LOG_PATTERN.search("LogPython: Error: failed"))
        self.assertIsNone(MODULE.FATAL_LOG_PATTERN.search("LogPython: Display: completed"))


if __name__ == "__main__":
    unittest.main()
