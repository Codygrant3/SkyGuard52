from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


VERIFIER_PATH = Path(__file__).with_name(
    "verify_gate7_combat_art_offline_control.py"
)
SPEC = importlib.util.spec_from_file_location("gate7_verifier", VERIFIER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Unable to load Gate 7 verifier")
VERIFIER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFIER)


class Gate7OfflineControlRecovery01Tests(unittest.TestCase):
    def test_sha256_file_is_lowercase_and_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.bin"
            path.write_bytes(b"skyguard52")
            digest = VERIFIER.sha256_file(path)
            self.assertEqual(
                digest,
                "a40a504dd722d3d2ceb1aaab5895d057a624bdfb1be0d06aa865994f50ee30b8",
            )
            self.assertEqual(digest, digest.lower())

    def test_expected_lane_set_is_complete(self) -> None:
        self.assertEqual(
            VERIFIER.EXPECTED_LANES,
            {"G7.1", "G7.2", "G7.3", "G7.4", "G7.5", "G7.6", "G7.7", "G7.8"},
        )

    def test_disallowlist_covers_proxy_sources(self) -> None:
        self.assertIn(
            "/Game/Skyguard/Meshes/WebGame",
            VERIFIER.REQUIRED_FORBIDDEN_FRAGMENTS,
        )
        self.assertIn(
            "/Game/Skyguard/Meshes/L88/yak52_l88_silhouette_blockout",
            VERIFIER.REQUIRED_FORBIDDEN_FRAGMENTS,
        )
        self.assertIn("/Engine/BasicShapes", VERIFIER.REQUIRED_FORBIDDEN_FRAGMENTS)

    def test_waiting_classification_is_not_a_pass_claim(self) -> None:
        self.assertEqual(
            VERIFIER.EXPECTED_CLASSIFICATION,
            "AWAITING_GATE6_AND_EXPLICIT_PRODUCTION_AUTHORIZATION",
        )
        self.assertNotIn("PASSED", VERIFIER.EXPECTED_CLASSIFICATION)

    def test_live_offline_control_package(self) -> None:
        result = VERIFIER.run_verification()
        self.assertEqual(result["gate"], "PASS", result["failures"])
        self.assertEqual(result["failures"], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
