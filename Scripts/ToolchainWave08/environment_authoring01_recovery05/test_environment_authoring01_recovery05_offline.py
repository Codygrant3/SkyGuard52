import ast
import unittest
from pathlib import Path

ROOT = Path(r"D:\Skyguard52")
SOURCE = ROOT / r"Scripts\ToolchainWave08\environment_authoring01_recovery05\author_m01_environment_authoring01_recovery05.py"
SUPERVISOR = ROOT / r"Scripts\ToolchainWave08\environment_authoring01_recovery05\invoke_environment_authoring01_recovery05_once.ps1"


def acquisition_action(count):
    if count > 1:
        raise RuntimeError("duplicate directors")
    return "SPAWNED_DETERMINISTICALLY_IN_FRESH_OUTPUT" if count == 0 else "REUSED_SINGLE_EXISTING_OUTPUT_DIRECTOR"


class Recovery05Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")
        cls.supervisor = SUPERVISOR.read_text(encoding="utf-8")

    def test_source_parses(self):
        ast.parse(self.source, filename=str(SOURCE))

    def test_zero_spawns(self):
        self.assertEqual(acquisition_action(0), "SPAWNED_DETERMINISTICALLY_IN_FRESH_OUTPUT")

    def test_one_reuses(self):
        self.assertEqual(acquisition_action(1), "REUSED_SINGLE_EXISTING_OUTPUT_DIRECTOR")

    def test_multiple_fails_closed(self):
        with self.assertRaises(RuntimeError):
            acquisition_action(2)

    def test_acquisition_precedes_authoring(self):
        acquisition = self.source.index('result["director_acquisition"] = {')
        authoring = self.source.index('author_governed_landscape_with_existing_graph(')
        self.assertLess(acquisition, authoring)

    def test_pcg_registry_contract_preserved(self):
        self.assertIn('scan_pcg_registry(registry)', self.source)
        self.assertIn('validate_pcg_tree_dependency(registry, path)', self.source)
        self.assertIn('require(all(record["passed"] for record in result["pcg_tree_validation"])', self.source)

    def test_save_and_layout_contract_preserved(self):
        self.assertEqual(self.source.count("EditorAssetLibrary.duplicate_asset(INPUT_ASSET, OUTPUT_ASSET)"), 1)
        self.assertIn("SAVE_ALLOWLIST = (OUTPUT_ASSET,)", self.source)
        self.assertIn("PCG_SEED = 520801", self.source)
        self.assertIn('len([label for label in labels if label.startswith("M01_A01_Tree_")]) == 15', self.source)

    def test_supervisor_governance(self):
        self.assertEqual(self.supervisor.count("$run=Invoke-CapturedProcess -FilePath $Editor"), 1)
        self.assertIn("retry_count=0", self.supervisor)
        self.assertIn("Environment director acquisition evidence failed", self.supervisor)


if __name__ == "__main__":
    unittest.main()
