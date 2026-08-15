from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name(
    "adjudicate_m01_visible_environment_kit_refinement01_stagea_recovery10_checkpoint01.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("skyguard_r10_postflight_test", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load Recovery10 postflight")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Recovery10PostflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_module()

    def png(self, path: Path, width: int, height: int) -> None:
        header = bytearray(24)
        header[:8] = b"\x89PNG\r\n\x1a\n"
        header[12:16] = b"IHDR"
        header[16:20] = width.to_bytes(4, "big")
        header[20:24] = height.to_bytes(4, "big")
        path.write_bytes(header)

    def test_supported_dimensions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "valid.png"
            self.png(path, 1920, 1080)
            self.assertEqual((1920, 1080), self.module.png_dimensions(path))

    def test_invalid_dimensions_remain_observable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "wrong.png"
            self.png(path, 640, 360)
            self.assertEqual((640, 360), self.module.png_dimensions(path))

    def test_truncated_header_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "bad.png"
            path.write_bytes(b"\x89PNG")
            with self.assertRaises(self.module.AdjudicationError):
                self.module.png_dimensions(path)

    def test_malformed_signature_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "bad.png"
            path.write_bytes(b"x" * 24)
            with self.assertRaises(self.module.AdjudicationError):
                self.module.png_dimensions(path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
