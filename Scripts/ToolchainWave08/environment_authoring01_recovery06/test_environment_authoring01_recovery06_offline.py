import ast
import unittest
from pathlib import Path

ROOT = Path(r"D:\Skyguard52")
SOURCE = ROOT / r"Scripts\ToolchainWave08\environment_authoring01_recovery06\author_m01_environment_authoring01_recovery06.py"
SUPERVISOR = ROOT / r"Scripts\ToolchainWave08\environment_authoring01_recovery06\invoke_environment_authoring01_recovery06_once.ps1"
SOURCE05 = ROOT / r"Scripts\ToolchainWave08\environment_authoring01_recovery05\author_m01_environment_authoring01_recovery05.py"


class Recovery06Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")
        cls.source05 = SOURCE05.read_text(encoding="utf-8")
        cls.supervisor = SUPERVISOR.read_text(encoding="utf-8")

    def test_source_parses(self):
        ast.parse(self.source, filename=str(SOURCE))

    def test_source_behavior_only_namespaced(self):
        normalized = self.source.replace("RECOVERY06", "RECOVERY05").replace("Recovery06", "Recovery05").replace("recovery06", "recovery05")
        self.assertEqual(normalized, self.source05)

    def test_regular_editor_python_mode(self):
        self.assertIn('"-ExecutePythonScript=$AttemptAuthoring"', self.supervisor)
        self.assertIn("'-ScriptErrorsAreFatal'", self.supervisor)
        self.assertNotIn("'-run=pythonscript'", self.supervisor)
        self.assertNotIn('"-script=$AttemptAuthoring"', self.supervisor)

    def test_one_launch_zero_retry(self):
        self.assertEqual(self.supervisor.count("$run=Invoke-CapturedProcess -FilePath $Editor"), 1)
        self.assertIn("retry_count=0", self.supervisor)

    def test_recovery05_terminal_authority(self):
        self.assertIn("Recovery05 commandlet crash terminal freeze", self.supervisor)
        self.assertIn("4fb2b6375021bc74083faccd5c2ad55d5ee1c34119ccfd5853090f347bf0dccb", self.supervisor)

    def test_water_and_pcg_contract_preserved(self):
        for token in ("/Script/Water.WaterBodyOcean", "/Script/Water.WaterZone", "scan_pcg_registry(registry)", "director_acquisition", "shore_contact_checks"):
            self.assertIn(token, self.source)


if __name__ == "__main__":
    unittest.main()
