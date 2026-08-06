from __future__ import annotations

import ast
import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WRAPPER = ROOT / "Scripts/blender_phase2_yak52_r5_slice01_recovery01.py"
FROZEN_R5 = ROOT / "Scripts/blender_phase2_yak52_r5_slice01.py"
FAILED_ATTEMPT = (
    ROOT
    / "Saved/BuildAttempts/PHASE2_YAK52_R5_SLICE01/"
    "attempt_20260802T2153188883706Z_008a64e4"
)
BASELINE = (
    ROOT
    / "Content/Skyguard/Meshes/Source/Mission01/Yak52_FinalArt_R4/"
    "Slice01_Recovery05/BLD_M01_YAK_FINAL_ART_R4_S01_RECOVERY05_MASTER.blend"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Recovery01CompatibilityTests(unittest.TestCase):
    def test_wrapper_parses_and_is_import_side_effect_free(self) -> None:
        tree = ast.parse(WRAPPER.read_text(encoding="utf-8"))
        top_level_calls = [
            node
            for node in tree.body
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
        ]
        self.assertEqual(top_level_calls, [])

    def test_only_supported_datum_token_is_present(self) -> None:
        source = WRAPPER.read_text(encoding="utf-8")
        self.assertIn('obj.empty_display_type = "PLAIN_AXES"', source)
        self.assertNotIn('obj.empty_display_type = "CROSS"', source)

    def test_new_namespace_is_isolated_and_absent(self) -> None:
        source = WRAPPER.read_text(encoding="utf-8")
        self.assertIn("Slice01_Recovery01", source)
        self.assertFalse(
            (
                ROOT
                / "Content/Skyguard/Meshes/Source/Mission01/"
                "Yak52_FinalArt_R5/Slice01_Recovery01"
            ).exists()
        )

    def test_frozen_source_and_baseline_hashes_match(self) -> None:
        self.assertEqual(
            sha256(FROZEN_R5),
            "446b4e8d71457b2f9bac3798c22b82fec212e89161ec30c7d2d800683fdfa1f2",
        )
        self.assertEqual(
            sha256(BASELINE),
            "a7694e012e1dbdef06c432919f2a93d62ec3845c888506fe7019ef81aeb2f30e",
        )

    def test_failed_attempt_remains_immutable(self) -> None:
        expected = {
            "blender.stderr.log": "427cc94ab8126345af52aa459761d7fde1103aa62ed4448992e05369fd7c7e5a",
            "blender.stdout.log": "62aa68d052234759fcf2f662c9277a117896bb0a66d46f104de825c9b1ad1ecc",
            "process.json": "dac1f6617facd4bf1e5b632d1056f08394efdddc31b840201f298595b2006dbf",
            "terminal_receipt.json": "84c64a73a9dfc70912f4eb8423db753ee50ca88591611fc3278319646bba7e5f",
        }
        observed = {
            path.name: sha256(path)
            for path in FAILED_ATTEMPT.iterdir()
            if path.is_file()
        }
        self.assertEqual(observed, expected)


if __name__ == "__main__":
    unittest.main()

