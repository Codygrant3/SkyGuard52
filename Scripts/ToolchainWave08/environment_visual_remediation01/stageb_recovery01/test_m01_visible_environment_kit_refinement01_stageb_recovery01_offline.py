from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


WRAPPER = Path(
    r"D:\Skyguard52\Scripts\ToolchainWave08\environment_visual_remediation01\stageb_recovery01\build_m01_visible_environment_kit_refinement01_stageb_recovery01.py"
)


def load_wrapper():
    spec = importlib.util.spec_from_file_location("stageb_recovery01_wrapper", WRAPPER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load Recovery01 wrapper")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class StageBRecovery01Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_wrapper()
        cls.corrected, cls.receipt = cls.module.load_bounded_source()

    def test_frozen_source_identity(self) -> None:
        self.assertEqual(self.receipt["base_bytes"], 37220)
        self.assertEqual(
            self.receipt["base_sha256"],
            "d73abc1fc8f25b7bb167aa3287fa754eab906bcd0c5950b2c01abd5fc452570a",
        )

    def test_exactly_two_bounded_replacements(self) -> None:
        self.assertEqual(len(self.receipt["replacements"]), 2)
        self.assertTrue(all(item["old_token_count"] == 1 for item in self.receipt["replacements"]))
        self.assertTrue(all(item["new_token_count"] == 1 for item in self.receipt["replacements"]))

    def test_redundant_repeats_are_absent(self) -> None:
        self.assertNotIn("base = np.repeat(base, size, axis=1)", self.corrected)
        self.assertNotIn("rough = np.repeat(rough, size, axis=1)", self.corrected)

    def test_shape_assertions_are_present(self) -> None:
        self.assertIn("base.shape == (size, size, 3)", self.corrected)
        self.assertIn("rough.shape == (size, size, 1)", self.corrected)

    def test_geometry_and_render_contract_text_is_preserved(self) -> None:
        base = self.module.BASE_SOURCE.read_text(encoding="utf-8")
        normalized = self.corrected
        for old_token, new_token in self.module.REPLACEMENTS:
            normalized = normalized.replace(new_token, old_token, 1)
        self.assertEqual(base, normalized)

    def test_wrapper_compiles_without_blender(self) -> None:
        compile(WRAPPER.read_text(encoding="utf-8"), str(WRAPPER), "exec")


if __name__ == "__main__":
    unittest.main()
