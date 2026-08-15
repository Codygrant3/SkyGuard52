from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("verify_m01_visible_environment_kit_refinement01_stageb_recovery03_binding_template.py")
SPEC = importlib.util.spec_from_file_location("stageb_recovery03_binding_verifier", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class StageBRecovery03BindingTemplateTests(unittest.TestCase):
    def test_complete_verifier_passes(self) -> None:
        self.assertEqual("PASS", MODULE.validate()["classification"])

    def test_template_waits_for_four_acceptance_authorities(self) -> None:
        data = json.loads(MODULE.REQUIREMENTS.read_text(encoding="utf-8"))
        self.assertEqual(4, len(data["future_required_stagea_recovery03_evidence"]))
        self.assertTrue(all(not Path(row["path"]).exists() for row in data["future_required_stagea_recovery03_evidence"]))

    def test_worker_is_reused_without_changes(self) -> None:
        self.assertEqual("a5c901411511939fd2e2a63b48dc22455280e9f8c9409151ef1465e8e19d7c6b", MODULE.sha256(MODULE.STAGEB_WORKER))
        self.assertEqual("ec787aae6b0017078634e11ef4d5ad56ada06ba0133d8c3f6a81ad9206374c61", MODULE.sha256(MODULE.STAGEA_WORKER))

    def test_binding_cannot_authorize_blender(self) -> None:
        data = json.loads(MODULE.REQUIREMENTS.read_text(encoding="utf-8"))
        rules = data["binding_rules"]
        self.assertFalse(rules["stageb_blender_execution_may_be_authorized_by_binding_gate"])
        self.assertTrue(rules["separate_stageb_execution_authorization_required"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
