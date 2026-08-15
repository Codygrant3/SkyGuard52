from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from Scripts import skyguard_production_cycle as subject


class ProductionCycleTests(unittest.TestCase):
    def test_standing_authorization_is_active(self) -> None:
        payload = subject.verify_standing_authorization()
        self.assertEqual(payload["status"], "ACTIVE")
        self.assertFalse(payload["execution_policy"]["per_run_user_authorization_required"])

    def test_failed_shahed_lane_preserves_v2_postflight_and_quality_contract(self) -> None:
        manifest = subject.controller.load_manifest()
        asset = subject.controller.asset_index(manifest)["core-shahed136"]
        self.assertEqual(asset["status"], "failed")
        self.assertEqual(
            asset["worker"]["postflight"]["script"],
            r"Scripts\adjudicate_ready_blender_asset_attempt_v2.py",
        )
        contract = subject.controller.load_json(subject.postflight_v2.base.CONTRACT_PATH)[
            "contracts"
        ]["core-shahed136"]
        self.assertEqual(contract["worker_script"], asset["worker"]["script"])
        self.assertEqual(
            contract["quality_gate"]["profile"],
            "hero_airframe_proxy_rejection_v1",
        )

    def test_format_postflight_keeps_report_outside_attempt(self) -> None:
        manifest = subject.controller.load_manifest()
        asset = subject.controller.asset_index(manifest)[
            "core-reargunner-character-refinement01"
        ]
        with tempfile.TemporaryDirectory() as directory:
            attempt = Path(directory) / "attempt_fixture"
            attempt.mkdir()
            command, report = subject.format_postflight(asset, attempt)
            self.assertIn("--attempt-dir", command)
            self.assertIn(str(attempt), command)
            self.assertNotIn(attempt, report.parents)
            self.assertTrue(str(report).endswith("attempt_fixture.json"))

    def test_audit_does_not_create_attempt(self) -> None:
        manifest = subject.controller.load_manifest()
        asset_id = "core-reargunner-character-refinement01"
        asset = subject.controller.asset_index(manifest)[asset_id]
        self.assertEqual(asset["status"], "ready")
        attempt_parent = subject.controller.ATTEMPTS_ROOT / asset_id
        before = (
            sorted(path.name for path in attempt_parent.iterdir() if path.is_dir())
            if attempt_parent.exists()
            else []
        )
        result = subject.audit_asset(asset_id)
        self.assertTrue(result["pass"])
        after = (
            sorted(path.name for path in attempt_parent.iterdir() if path.is_dir())
            if attempt_parent.exists()
            else []
        )
        self.assertEqual(after, before)


if __name__ == "__main__":
    unittest.main()
