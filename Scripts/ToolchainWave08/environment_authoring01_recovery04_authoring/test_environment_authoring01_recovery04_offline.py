import ast
import unittest
from pathlib import Path

ROOT = Path(r"D:\Skyguard52")
SOURCE = ROOT / r"Scripts\ToolchainWave08\environment_authoring01_recovery04_authoring\author_m01_environment_authoring01_recovery04.py"
SUPERVISOR = ROOT / r"Scripts\ToolchainWave08\environment_authoring01_recovery04_authoring\invoke_environment_authoring01_recovery04_once.ps1"


def fixture_accepts(scan_passed=True, records=None):
    if not scan_passed:
        return False
    if records is None:
        records = [dict(registry_visible=True, editor_asset_library_visible=True, load_asset_success=True, load_object_success=True, class_name="StaticMesh", bounds=(1, 1, 1)) for _ in range(3)]
    if len(records) != 3:
        return False
    return all(
        r.get("registry_visible")
        and r.get("editor_asset_library_visible")
        and r.get("load_asset_success")
        and r.get("load_object_success")
        and r.get("class_name") == "StaticMesh"
        and len(r.get("bounds", ())) == 3
        and all(v > 0 for v in r.get("bounds", ()))
        for r in records
    )


class Recovery04OptionATests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")
        cls.supervisor = SUPERVISOR.read_text(encoding="utf-8")

    def test_python_parses(self):
        ast.parse(self.source, filename=str(SOURCE))

    def test_scan_precedes_dependency_load_and_duplication(self):
        scan = self.source.index('result["pcg_registry_initialization"] = scan_pcg_registry(registry)')
        validate = self.source.index('validate_pcg_tree_dependency(registry, path)')
        load = self.source.index('loaded = {path: load_required_asset(path) for path in dependencies}')
        duplicate = self.source.index('EditorAssetLibrary.duplicate_asset(INPUT_ASSET, OUTPUT_ASSET)')
        self.assertLess(scan, validate)
        self.assertLess(validate, load)
        self.assertLess(load, duplicate)

    def test_exact_required_trees_and_no_proxy_substitution(self):
        for name in ("PCG_Tree_01", "PCG_Tree_02", "PCG_Tree_03"):
            self.assertEqual(self.source.count(name), 2)
        self.assertNotIn("coast_tree_proxy", self.source)

    def test_fixture_accepts_complete_valid_records(self):
        self.assertTrue(fixture_accepts())

    def test_fixture_rejects_scan_failure(self):
        self.assertFalse(fixture_accepts(scan_passed=False))

    def test_fixture_rejects_partial_resolution(self):
        self.assertFalse(fixture_accepts(records=[]))

    def test_fixture_rejects_missing_or_wrong_class(self):
        rows = [dict(registry_visible=True, editor_asset_library_visible=True, load_asset_success=True, load_object_success=True, class_name="StaticMesh", bounds=(1, 1, 1)) for _ in range(3)]
        rows[1]["class_name"] = "StaticMeshActor"
        self.assertFalse(fixture_accepts(records=rows))

    def test_fixture_rejects_zero_bounds(self):
        rows = [dict(registry_visible=True, editor_asset_library_visible=True, load_asset_success=True, load_object_success=True, class_name="StaticMesh", bounds=(1, 1, 1)) for _ in range(3)]
        rows[2]["bounds"] = (1, 0, 1)
        self.assertFalse(fixture_accepts(records=rows))

    def test_governance_preserved(self):
        self.assertEqual(self.source.count("EditorAssetLibrary.duplicate_asset(INPUT_ASSET, OUTPUT_ASSET)"), 1)
        self.assertIn("SAVE_ALLOWLIST = (OUTPUT_ASSET,)", self.source)
        self.assertIn("PCG_SEED = 520801", self.source)
        self.assertIn("DISABLED_FIXED_DIRECT_PLACEMENT_ONLY", self.source)
        self.assertEqual(self.supervisor.count("$run=Invoke-CapturedProcess -FilePath $Editor"), 1)
        self.assertIn("retry_count=0", self.supervisor)


if __name__ == "__main__":
    unittest.main()
