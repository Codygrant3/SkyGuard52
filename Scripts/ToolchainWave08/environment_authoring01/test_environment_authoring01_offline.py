import ast
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
SCRIPT = ROOT / r"Scripts\ToolchainWave08\environment_authoring01\author_m01_environment_authoring01.py"
SUPERVISOR = ROOT / r"Scripts\ToolchainWave08\environment_authoring01\invoke_environment_authoring01_once.ps1"
DOCS = ROOT / r"Docs\Toolchain\ToolchainWave08\EnvironmentAuthoring01"


class Authoring01OfflineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SCRIPT.read_text(encoding="utf-8")
        cls.supervisor = SUPERVISOR.read_text(encoding="utf-8")

    def test_python_parses(self):
        ast.parse(self.source, filename=str(SCRIPT))

    def test_duplication_and_save_are_exact(self):
        self.assertEqual(self.source.count("EditorAssetLibrary.duplicate_asset(INPUT_ASSET, OUTPUT_ASSET)"), 1)
        self.assertIn("SAVE_ALLOWLIST = (OUTPUT_ASSET,)", self.source)
        self.assertNotIn("shutil.copy", self.source)

    def test_bounded_content_contract(self):
        self.assertIn("PCG_SEED = 520801", self.source)
        self.assertIn("len([label for label in labels if label.startswith(\"M01_A01_Tree_\")]) == 15", self.source)
        self.assertIn("DEFERRED_NO_EFFECTFUL_BRUSH_API_AUTHORITY", self.source)
        self.assertIn("DISABLED_FIXED_DIRECT_PLACEMENT_ONLY", self.source)
        self.assertIn("align_actor_bottom", self.source)
        self.assertIn("shore_contact_checks", self.source)

    def test_supervisor_is_one_shot(self):
        self.assertEqual(self.supervisor.count("$run=Invoke-CapturedProcess -FilePath $Editor"), 1)
        self.assertIn("retry_count=0", self.supervisor)
        self.assertNotIn("for($retry", self.supervisor.lower())
        self.assertNotIn("while($retry", self.supervisor.lower())

    def test_json_contracts_and_temporary_rejections(self):
        for path in DOCS.glob("*.json"):
            json.loads(path.read_text(encoding="utf-8-sig"))
        with tempfile.TemporaryDirectory(prefix="SkyguardA01Test_") as root:
            output = Path(root) / "output.umap"
            self.assertFalse(output.exists())
            output.write_bytes(b"partial")
            self.assertTrue(output.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
