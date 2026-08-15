from __future__ import annotations

import importlib.util
import struct
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(r"D:\Skyguard52\Scripts\ToolchainWave08\environment_visual_remediation01\stagea_recovery05_postflight\adjudicate_m01_visible_environment_kit_refinement01_stagea_recovery05_checkpoint01.py")


def load_module():
    spec = importlib.util.spec_from_file_location("r05_checkpoint_postflight", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Recovery05CheckpointPostflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_module()

    def fixture(self, width: int, height: int, prefix: bytes = b"\x89PNG\r\n\x1a\n") -> Path:
        root = Path(tempfile.mkdtemp(prefix="skyguard-r05-png-"))
        path = root / "fixture.png"
        path.write_bytes(prefix + struct.pack(">I", 13) + b"IHDR" + struct.pack(">II", width, height))
        return path

    def test_supported_dimensions(self) -> None:
        for dimensions in ((1280,720),(1920,1080),(2560,1440),(2048,2048)):
            self.assertEqual(self.module.png_dimensions(self.fixture(*dimensions)), dimensions)

    def test_malformed_signature_rejected(self) -> None:
        with self.assertRaises(self.module.AdjudicationError):
            self.module.png_dimensions(self.fixture(1920, 1080, b"BAD_DATA"))

    def test_truncated_header_rejected(self) -> None:
        root = Path(tempfile.mkdtemp(prefix="skyguard-r05-png-truncated-"))
        path = root / "fixture.png"
        path.write_bytes(b"\x89PNG\r\n\x1a\n")
        with self.assertRaises(self.module.AdjudicationError):
            self.module.png_dimensions(path)

    def test_struct_unpack_is_big_endian(self) -> None:
        source = MODULE_PATH.read_text(encoding="utf-8")
        self.assertIn('struct.unpack(">II", header[16:24])', source)


if __name__ == "__main__":
    unittest.main()
