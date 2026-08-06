from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_skyguard_polyhaven_empty_placeholder_exclusion_recovery01 import (  # noqa: E402
    FAMILIES,
    verify,
)


class EmptyPlaceholderExclusionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for relative in ("Source", "Config", "Plugins", "Content"):
            (self.root / relative).mkdir(parents=True)
        for family in FAMILIES:
            (
                self.root
                / "Content"
                / "Skyguard"
                / "Textures"
                / "PolyHaven"
                / family
            ).mkdir(parents=True)
        contract = (
            self.root
            / "Docs"
            / "AAA_Review"
            / "PHASE4_M01_LANDSCAPE_VISIBLE_GPU_REVIEW_CONTRACT.json"
        )
        contract.parent.mkdir(parents=True)
        contract.write_text(json.dumps({
            "provenance": {
                "excluded": [
                    f"{family}_empty_unverified_placeholder"
                    for family in FAMILIES
                ]
            }
        }), encoding="utf-8")
        (self.root / "Content" / "safe.uasset").write_bytes(b"safe")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def codes(self) -> set[str]:
        return {item["code"] for item in verify(self.root)["failures"]}

    def test_empty_and_excluded_passes(self) -> None:
        result = verify(self.root)
        self.assertEqual(
            result["classification"],
            "PASSED_OFFLINE_EXCLUDED_FROM_CURRENT_CANDIDATE",
        )
        self.assertEqual(result["failures"], [])

    def test_runtime_reference_fails(self) -> None:
        (self.root / "Source" / "runtime.cpp").write_text(
            "ship_hull",
            encoding="utf-8",
        )
        self.assertIn("RUNTIME_REFERENCE_DETECTED", self.codes())

    def test_nonempty_placeholder_fails(self) -> None:
        (
            self.root
            / "Content"
            / "Skyguard"
            / "Textures"
            / "PolyHaven"
            / "painted_metal_02"
            / "unexpected.jpg"
        ).write_bytes(b"x")
        self.assertIn("PLACEHOLDER_NOT_EMPTY", self.codes())

    def test_missing_contract_exclusion_fails(self) -> None:
        contract = (
            self.root
            / "Docs"
            / "AAA_Review"
            / "PHASE4_M01_LANDSCAPE_VISIBLE_GPU_REVIEW_CONTRACT.json"
        )
        contract.write_text(
            json.dumps({"provenance": {"excluded": []}}),
            encoding="utf-8",
        )
        self.assertIn("CONTRACT_EXCLUSION_MISSING", self.codes())


if __name__ == "__main__":
    unittest.main()
