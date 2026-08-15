import ast
import unittest
from pathlib import Path

ROOT = Path(r"D:\Skyguard52")
SOURCE07 = ROOT / r"Scripts\ToolchainWave08\environment_authoring01_recovery07\author_m01_environment_authoring01_recovery07.py"
SUPERVISOR07 = ROOT / r"Scripts\ToolchainWave08\environment_authoring01_recovery07\invoke_environment_authoring01_recovery07_once.ps1"
SOURCE06 = ROOT / r"Scripts\ToolchainWave08\environment_authoring01_recovery06\author_m01_environment_authoring01_recovery06.py"

OLD_BLOCK = """    output_world = unreal.EditorAssetLibrary.duplicate_asset(INPUT_ASSET, OUTPUT_ASSET)
    require(output_world is not None, "Unreal API duplication failed")
    require(unreal.EditorLevelLibrary.load_level(OUTPUT_ASSET), "Fresh Authoring01 world failed to load")"""
NEW_BLOCK = """    level_editor_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    require(level_editor_subsystem is not None, "LevelEditorSubsystem is unavailable")
    require(
        level_editor_subsystem.new_level_from_template(OUTPUT_ASSET, INPUT_ASSET),
        "Fresh Authoring01 world failed to create from the accepted template",
    )"""


class Recovery07Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source07 = SOURCE07.read_text(encoding="utf-8")
        cls.source06 = SOURCE06.read_text(encoding="utf-8")
        cls.supervisor07 = SUPERVISOR07.read_text(encoding="utf-8")

    def test_source_parses(self):
        ast.parse(self.source07, filename=str(SOURCE07))

    def test_source_diff_is_only_namespace_and_world_lifecycle(self):
        normalized = (
            self.source07
            .replace("RECOVERY07", "RECOVERY06")
            .replace("Recovery07", "Recovery06")
            .replace("recovery07", "recovery06")
            .replace(NEW_BLOCK, OLD_BLOCK)
        )
        self.assertEqual(normalized, self.source06)

    def test_one_step_template_lifecycle(self):
        self.assertEqual(self.source07.count("new_level_from_template(OUTPUT_ASSET, INPUT_ASSET)"), 1)
        self.assertNotIn("duplicate_asset(INPUT_ASSET, OUTPUT_ASSET)", self.source07)
        self.assertNotIn("load_level(OUTPUT_ASSET)", self.source07)
        self.assertNotIn("output_world =", self.source07)

    def test_regular_editor_python_mode(self):
        self.assertIn('"-ExecutePythonScript=$AttemptAuthoring"', self.supervisor07)
        self.assertIn("'-ScriptErrorsAreFatal'", self.supervisor07)
        self.assertNotIn("'-run=pythonscript'", self.supervisor07)
        self.assertNotIn('"-script=$AttemptAuthoring"', self.supervisor07)

    def test_one_launch_zero_retry(self):
        self.assertEqual(self.supervisor07.count("$run=Invoke-CapturedProcess -FilePath $Editor"), 1)
        self.assertIn("retry_count=0", self.supervisor07)
        self.assertNotIn("Remove-Item -LiteralPath $OutputMap", self.supervisor07)

    def test_recovery06_terminal_authority(self):
        self.assertIn("Recovery06 world-lifecycle failure terminal freeze", self.supervisor07)
        self.assertIn("65413962002d1c1ecc5c2760882a12e2186cdd4a20eb42246a34e6b1a9b2aea9", self.supervisor07)

    def test_environment_contract_preserved(self):
        for token in (
            "/Script/Water.WaterBodyOcean",
            "/Script/Water.WaterZone",
            "scan_pcg_registry(registry)",
            "director_acquisition",
            "grounding_records",
            "shore_contact_checks",
            "save_asset(OUTPUT_ASSET, only_if_is_dirty=False)",
        ):
            self.assertIn(token, self.source07)

    def test_recovery07_output_and_receipts_are_versioned(self):
        self.assertIn("Lvl_M01_T08_EnvironmentAuthoring01_Recovery07", self.source07)
        self.assertIn("PASSED_M01_ENVIRONMENT_AUTHORING01_RECOVERY07_AUTOMATIC", self.source07)
        self.assertNotIn("Authoring01_Recovery06", self.source07)


if __name__ == "__main__":
    unittest.main()

