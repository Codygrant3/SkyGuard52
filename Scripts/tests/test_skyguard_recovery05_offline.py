from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


VERIFIER = Path(r"D:\Skyguard52\Scripts\verify_skyguard_recovery05_offline.py")


def load_verifier():
    spec = importlib.util.spec_from_file_location("recovery05_verifier", VERIFIER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load Recovery05 verifier")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Recovery05OfflineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.verifier = load_verifier()

    def test_full_offline_contract(self):
        result = self.verifier.run_checks()
        self.assertEqual(result["classification"], "PASS", result["failures"])

    def test_unique_module_identity(self):
        text = (
            self.verifier.NEW
            / "Source/SkyguardRecovery03NativeRecovery05/Private/"
              "SkyguardRecovery03NativeRecovery05Module.cpp"
        ).read_text(encoding="utf-8")
        self.assertIn("SkyguardRecovery03NativeRecovery05", text)
        self.assertNotIn("SkyguardRecovery03NativeRecovery01", text)

    def test_environment_patch_is_one_line(self):
        patch = (
            self.verifier.ROOT
            / "SourceCorrections/Recovery05/"
              "SkyguardMission01EnvironmentDirector.mobility.patch"
        ).read_text(encoding="utf-8")
        added = [
            line for line in patch.splitlines()
            if line.startswith("+") and not line.startswith("+++")
        ]
        removed = [
            line for line in patch.splitlines()
            if line.startswith("-") and not line.startswith("---")
        ]
        self.assertEqual(
            added,
            ["+\tRoot->SetMobility(EComponentMobility::Static);"],
        )
        self.assertEqual(removed, [])

    def test_network_rejection_contract(self):
        contract = self.verifier.json.loads(
            (
                self.verifier.DOCS
                / "PHASE4_M01_RECOVERY05_MESSAGING_ISOLATION_CONTRACT.json"
            ).read_text(encoding="utf-8")
        )
        self.assertIn("TcpMessaging", contract["future_disable_plugins"])
        self.assertIn("UdpMessaging", contract["future_disable_plugins"])
        self.assertIn(
            "Initializing TcpMessaging bridge",
            contract["reject_log_patterns"],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
