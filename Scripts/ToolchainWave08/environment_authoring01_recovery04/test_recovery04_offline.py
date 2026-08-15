import pathlib
import unittest


ROOT = pathlib.Path(r"D:\Skyguard52")
SCRIPT_DIR = ROOT / "Scripts" / "ToolchainWave08" / "environment_authoring01_recovery04"
SUPERVISOR = SCRIPT_DIR / "invoke_dependency_probe_once.ps1"
PROBE = SCRIPT_DIR / "probe_environment_dependencies.py"
OLD_PROBE = ROOT / "Scripts" / "ToolchainWave08" / "environment_authoring01_recovery03" / "probe_environment_dependencies.py"


class Recovery04OfflineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SUPERVISOR.read_text(encoding="utf-8-sig")

    def test_probe_is_byte_identical(self):
        self.assertEqual(PROBE.read_bytes(), OLD_PROBE.read_bytes())

    def test_one_process_start(self):
        self.assertEqual(self.source.count("$process.Start()"), 1)
        self.assertNotIn("Start-Process", self.source)

    def test_mode_dispatch_precedes_governed_lifecycle(self):
        self.assertLess(
            self.source.index("# Mode dispatch occurs before the governed lifecycle"),
            self.source.index("# Governed paths and the outer terminal lifecycle exist only in authorized mode"),
        )

    def test_offline_test_is_temporary_and_isolated(self):
        self.assertIn("[System.IO.Path]::GetTempPath()", self.source)
        self.assertIn("[Guid]::NewGuid", self.source)
        segment = self.source[
            self.source.index("function Invoke-OfflineContractTest"):
            self.source.index("function Invoke-AuthorizationRefusal")
        ]
        self.assertNotIn("Invoke-CapturedProcess", segment)

    def test_mode_functions_have_clean_success_pipeline(self):
        offline = self.source[
            self.source.index("function Invoke-OfflineContractTest"):
            self.source.index("function Invoke-AuthorizationRefusal")
        ]
        refusal = self.source[
            self.source.index("function Invoke-AuthorizationRefusal"):
            self.source.index("function Invoke-CapturedProcess")
        ]
        self.assertNotIn("Write-Output", offline)
        self.assertNotIn("Write-Output", refusal)
        self.assertEqual(offline.count("return [int]"), 2)
        self.assertEqual(refusal.count("return [int]"), 1)
        self.assertIn("returned a collection instead of a scalar exit code", self.source)

    def test_read_only_probe(self):
        text = PROBE.read_text(encoding="utf-8-sig").lower()
        for token in ("duplicate_asset", "save_asset", "save_loaded_asset", "save_map"):
            self.assertNotIn(token, text)

    def test_conflicting_switch_uses_nonterminating_stderr(self):
        segment = self.source[
            self.source.index("if ($OfflineContractTest -and $AuthorizeSingleDependencyProbe)"):
            self.source.index("if ($OfflineContractTest) {")
        ]
        self.assertNotIn("Write-Error", segment)
        self.assertIn("[Console]::Error.WriteLine", segment)
        self.assertIn("[Environment]::Exit([int]3)", segment)

    def test_recovery04_status_versioning(self):
        self.assertNotIn("recovery02", self.source.lower())
        self.assertIn("PASSED_DEPENDENCY_PROBE_READY_FOR_RECOVERY04_FREEZE", self.source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
