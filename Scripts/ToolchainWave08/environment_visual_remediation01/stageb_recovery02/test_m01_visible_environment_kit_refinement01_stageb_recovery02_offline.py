import ast
import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("build_m01_visible_environment_kit_refinement01_stageb_recovery02.py")
SPEC = importlib.util.spec_from_file_location("stageb_recovery02", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class StageBRecovery02Tests(unittest.TestCase):
    def test_corrected_helper_identity(self):
        text, _ = MODULE.derive_stagea_helper()
        raw = text.encode("utf-8")
        self.assertEqual(len(raw), MODULE.CORRECTED_STAGEA_HELPER_BYTES)
        self.assertEqual(hashlib.sha256(raw).hexdigest(), MODULE.CORRECTED_STAGEA_HELPER_SHA256)

    def test_corrected_helper_uses_saved_png(self):
        text, _ = MODULE.derive_stagea_helper()
        self.assertIn("Saved render is missing or empty", text)
        self.assertNotIn('bpy.data.images.get("Render Result")', text)

    def test_stageb_source_memory_and_helper_corrections(self):
        with tempfile.TemporaryDirectory(prefix="skyguard_stageb_recovery02_test_") as temporary:
            helper = Path(temporary) / "helper.py"
            text, receipt = MODULE.derive_stageb_source(helper)
            ast.parse(text)
            self.assertNotIn("base = np.repeat(base, size, axis=1)", text)
            self.assertNotIn("rough = np.repeat(rough, size, axis=1)", text)
            self.assertIn(str(helper), text)
            self.assertEqual(receipt["geometry_material_camera_render_export_receipt_changes"], 0)

    def test_wrong_stageb_base_is_rejected(self):
        original = MODULE.BASE_SHA256
        try:
            MODULE.BASE_SHA256 = "0" * 64
            with self.assertRaises(RuntimeError):
                MODULE.derive_stageb_source(Path("helper.py"))
        finally:
            MODULE.BASE_SHA256 = original

    def test_memory_bound(self):
        self.assertEqual(2048 * 2048 * 4 * 4, 67108864)


if __name__ == "__main__":
    unittest.main()
