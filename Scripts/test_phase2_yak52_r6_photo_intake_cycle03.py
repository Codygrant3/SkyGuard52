from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


VERIFIER_PATH = Path(__file__).with_name(
    "verify_phase2_yak52_r6_photo_intake_cycle03.py"
)
SPEC = importlib.util.spec_from_file_location("yak_cycle03_verifier", VERIFIER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Unable to load Yak-52 Cycle03 verifier")
VERIFIER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFIER)


class Yak52Cycle03PhotoIntakeTests(unittest.TestCase):
    def test_png_dimension_reader(self) -> None:
        png_header = (
            b"\x89PNG\r\n\x1a\n"
            + b"\x00\x00\x00\rIHDR"
            + b"\x00\x00\x05\x00"
            + b"\x00\x00\x02\xd0"
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "header.png"
            path.write_bytes(png_header)
            self.assertEqual(VERIFIER.png_dimensions(path), (1280, 720))

    def test_hash_is_lowercase(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.bin"
            path.write_bytes(b"yak52-cycle03")
            digest = VERIFIER.sha256_file(path)
            self.assertEqual(digest, digest.lower())
            self.assertEqual(len(digest), 64)

    def test_live_package(self) -> None:
        result = VERIFIER.run_verification()
        self.assertEqual(result["gate"], "PASS", result["failures"])
        self.assertEqual(result["failures"], [])
        self.assertFalse(result["checks"]["blender_authorized"])
        self.assertFalse(result["checks"]["unreal_authorized"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
