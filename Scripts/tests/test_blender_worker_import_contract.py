import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "Scripts" / "Workers" / "worker_m01_hero_prewar_window_bay_a01_recovery04.py"


class BlenderWorkerImportContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = TARGET.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source, filename=str(TARGET))

    def test_rejects_bare_sibling_worker_imports(self) -> None:
        bare = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                bare.extend(alias.name for alias in node.names if alias.name.startswith("worker_"))
        self.assertEqual([], bare)

    def test_uses_package_qualified_worker_import(self) -> None:
        modules = [node.module for node in ast.walk(self.tree) if isinstance(node, ast.ImportFrom)]
        self.assertIn("Scripts.Workers", modules)

    def test_bootstrap_precedes_project_import(self) -> None:
        root_line = next(node.lineno for node in self.tree.body if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "ROOT" for target in node.targets))
        import_line = next(node.lineno for node in self.tree.body if isinstance(node, ast.ImportFrom) and node.module == "Scripts.Workers")
        self.assertLess(root_line, import_line)
        self.assertIn("sys.path.insert", self.source[: self.source.find("from Scripts.Workers")])

    def test_blender_argument_separator_is_handled(self) -> None:
        self.assertIn('sys.argv.index("--") + 1', self.source)

    def test_recovery04_identity_is_fresh(self) -> None:
        self.assertIn('ASSET_ID = "m01-hero-prewar-window-bay-a01-recovery04"', self.source)
        self.assertIn("M01_Hero_Prewar_Window_Bay_A01_Recovery04.blend", self.source)
        self.assertIn("M01_Hero_Prewar_Window_Bay_A01_Recovery04.glb", self.source)


if __name__ == "__main__":
    unittest.main()
