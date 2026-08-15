from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
VERIFIER = ROOT / "Scripts/verify_phase2_reargunner_character_refinement01_recovery01_offline.py"


def load_verifier():
    spec = importlib.util.spec_from_file_location("character_recovery01_verifier", VERIFIER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load Recovery01 verifier")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CharacterRecovery01Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_verifier()
        cls.manifest = json.loads((ROOT / "Production/production_manifest.json").read_text(encoding="utf-8"))
        authority = json.loads(
            (ROOT / "Saved/Reports/PHASE2_REARGUNNER_CHARACTER_REFINEMENT01_RECOVERY01_EXECUTION_AUTHORITY.json").read_text(
                encoding="utf-8"
            )
        )
        cls.contract = authority["manifest_semantic_contract"]

    def assert_rejected(self, manifest) -> None:
        with self.assertRaises(self.module.VerificationError):
            self.module.verify_manifest_semantics(manifest, self.contract)

    def test_canonical_manifest_semantics_pass(self) -> None:
        result = self.module.verify_manifest_semantics(self.manifest, self.contract)
        self.assertEqual(result["status"], "ready")

    def test_status_drift_rejected(self) -> None:
        value = copy.deepcopy(self.manifest)
        next(item for item in value["assets"] if item["id"] == self.contract["asset_id"])["status"] = "queued"
        self.assert_rejected(value)

    def test_worker_drift_rejected(self) -> None:
        value = copy.deepcopy(self.manifest)
        next(item for item in value["assets"] if item["id"] == self.contract["asset_id"])["worker"]["script"] = "wrong.py"
        self.assert_rejected(value)

    def test_argument_drift_rejected(self) -> None:
        value = copy.deepcopy(self.manifest)
        next(item for item in value["assets"] if item["id"] == self.contract["asset_id"])["worker"]["arguments"] = []
        self.assert_rejected(value)

    def test_duplicate_asset_rejected(self) -> None:
        value = copy.deepcopy(self.manifest)
        value["assets"].append(copy.deepcopy(next(item for item in value["assets"] if item["id"] == self.contract["asset_id"])))
        self.assert_rejected(value)

    def test_legacy_status_drift_rejected(self) -> None:
        value = copy.deepcopy(self.manifest)
        next(item for item in value["assets"] if item["id"] == self.contract["legacy_asset_id"])["status"] = "accepted"
        self.assert_rejected(value)


if __name__ == "__main__":
    unittest.main()
