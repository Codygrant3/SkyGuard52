from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("build_m01_lighthouse_production_refinement01_recovery02.py")
SPEC = importlib.util.spec_from_file_location("recovery02", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Unable to load Recovery02 module")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class PngLuminanceTests(unittest.TestCase):
    def test_original_attempt_png(self):
        path = Path(
            r"D:\Skyguard52\Saved\BuildAttempts\M01_LIGHTHOUSE_PRODUCTION_REFINEMENT01\attempt_01\output\renders\01_daylight_front_full.png"
        )
        width, height, pixels = MODULE.decode_png_rgba8(path)
        self.assertEqual((width, height, len(pixels)), (2048, 1152, 2048 * 1152 * 4))
        luminance = MODULE.png_mean_luminance(path)
        self.assertGreater(luminance, 0.08)
        self.assertLess(luminance, 0.90)

    def test_recovery01_attempt_png(self):
        path = Path(
            r"D:\Skyguard52\Saved\BuildAttempts\M01_LIGHTHOUSE_PRODUCTION_REFINEMENT01_RECOVERY01\attempt_01\output\renders\01_daylight_front_full.png"
        )
        width, height, pixels = MODULE.decode_png_rgba8(path)
        self.assertEqual((width, height, len(pixels)), (2048, 1152, 2048 * 1152 * 4))
        luminance = MODULE.png_mean_luminance(path)
        self.assertGreater(luminance, 0.08)
        self.assertLess(luminance, 0.90)


if __name__ == "__main__":
    unittest.main()
