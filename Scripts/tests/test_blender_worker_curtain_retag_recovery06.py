import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "Scripts" / "Workers" / "worker_m01_hero_prewar_window_bay_a01_recovery06.py"


class CurtainRetagRecovery06Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = TARGET.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source, filename=str(TARGET))

    def test_package_import_and_blender_args_are_safe(self) -> None:
        self.assertIn("from Scripts.Workers import worker_m01_hero_prewar_window_bay_a01_recovery03", self.source)
        self.assertIn('sys.argv.index("--") + 1', self.source)

    def test_internal_signature_is_preserved(self) -> None:
        self.assertIn('IMMUTABLE_INTERNAL_SIGNATURE = "A_PREWAR_CASEMENT_RECOVERY03_CANDIDATE_B"', self.source)
        self.assertNotIn("implementation.SIGNATURE =", self.source)

    def test_only_legacy_curtain_factory_is_wrapped(self) -> None:
        self.assertIn("original_add_curtain = implementation.legacy.add_curtain", self.source)
        self.assertIn("implementation.legacy.add_curtain = add_curtain_retagged", self.source)
        self.assertIn("implementation.legacy.add_curtain = original_add_curtain", self.source)
        self.assertNotIn("implementation.build_window =", self.source)

    def test_retag_uses_expected_role_and_signature(self) -> None:
        self.assertIn('implementation.base.tag(obj, "window_interior_textile", IMMUTABLE_INTERNAL_SIGNATURE)', self.source)
        self.assertIn('CURTAIN_NAMES = ["SM_M01_WindowR03_Curtain_L", "SM_M01_WindowR03_Curtain_R"]', self.source)

    def test_correction_receipt_declares_no_art_change(self) -> None:
        for marker in ('"geometry_changed": False', '"materials_changed": False', '"lighting_changed": False', '"cameras_changed": False'):
            self.assertIn(marker, self.source)


if __name__ == "__main__":
    unittest.main()
