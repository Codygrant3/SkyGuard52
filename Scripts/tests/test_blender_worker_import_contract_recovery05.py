import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "Scripts" / "Workers" / "worker_m01_hero_prewar_window_bay_a01_recovery05.py"


class BlenderWorkerRecovery05ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = TARGET.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source, filename=str(TARGET))

    def test_package_bootstrap_precedes_project_import(self) -> None:
        import_node = next(node for node in self.tree.body if isinstance(node, ast.ImportFrom) and node.module == "Scripts.Workers")
        self.assertIn("sys.path.insert", self.source[: self.source.find("from Scripts.Workers")])
        root_node = next(node for node in self.tree.body if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "ROOT" for target in node.targets))
        self.assertLess(root_node.lineno, import_node.lineno)

    def test_blender_separator_is_required(self) -> None:
        self.assertIn('sys.argv.index("--") + 1', self.source)

    def test_internal_signature_is_not_mutated(self) -> None:
        assignments = []
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for target in targets:
                    if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name):
                        if target.value.id == "implementation" and target.attr == "SIGNATURE":
                            assignments.append(target.lineno)
        self.assertEqual([], assignments)
        self.assertIn('IMMUTABLE_INTERNAL_SIGNATURE = "A_PREWAR_CASEMENT_RECOVERY03_CANDIDATE_B"', self.source)

    def test_external_identity_is_fresh(self) -> None:
        self.assertIn('ASSET_ID = "m01-hero-prewar-window-bay-a01-recovery05"', self.source)
        self.assertIn("M01_Hero_Prewar_Window_Bay_A01_Recovery05.blend", self.source)
        self.assertIn("M01_Hero_Prewar_Window_Bay_A01_Recovery05.glb", self.source)

    def test_compatibility_receipt_is_explicit(self) -> None:
        self.assertIn('payload["recovery05_preserved_internal_signature"] = True', self.source)


if __name__ == "__main__":
    unittest.main()
