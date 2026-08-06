from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "verify_skyguard_phase8_release_tier.py"
)
SPEC = importlib.util.spec_from_file_location("phase8_release_tier", SCRIPT)
VERIFIER = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(VERIFIER)


class Phase8ReleaseTierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = VERIFIER.load_json(VERIFIER.CONTRACT_PATH)
        cls.blocked_audio = {
            "shipping_allowed": False,
            "blockers": ["AUTHENTIC_SOURCE_BUNDLES_NOT_APPROVED"],
        }
        cls.accepted_audio = {
            "shipping_allowed": True,
            "blockers": [],
        }

    def evaluate(self, tier, exception, audio):
        return VERIFIER.evaluate_tier(
            self.contract, tier, exception, audio
        )

    def test_engineering_preserves_baseline_with_explicit_exception(self):
        result = self.evaluate("Engineering", True, self.blocked_audio)
        self.assertTrue(result["packaging_allowed"])
        self.assertTrue(result["engineering_audio_exception_applied"])
        self.assertFalse(result["external_distribution_allowed"])
        self.assertFalse(result["shipping_promotion_allowed"])
        self.assertEqual(
            "BLOCK_SHIPPING_UNVERIFIED_AUDIO_WITH_ENGINEERING_EXCEPTION",
            result["effective_audio_state"],
        )

    def test_engineering_without_exception_is_blocked(self):
        result = self.evaluate("Engineering", False, self.blocked_audio)
        self.assertFalse(result["packaging_allowed"])

    def test_aaa_rejects_blocked_audio_even_if_exception_requested(self):
        result = self.evaluate("AAA", True, self.blocked_audio)
        self.assertFalse(result["packaging_allowed"])
        self.assertTrue(result["contract_errors"])

    def test_friend_facing_rejects_blocked_audio(self):
        result = self.evaluate("FriendFacing", False, self.blocked_audio)
        self.assertFalse(result["packaging_allowed"])
        self.assertFalse(result["external_distribution_allowed"])

    def test_aaa_accepts_only_shipping_audio_pass(self):
        result = self.evaluate("AAA", False, self.accepted_audio)
        self.assertTrue(result["packaging_allowed"])
        self.assertTrue(result["shipping_promotion_allowed"])
        self.assertFalse(result["external_distribution_allowed"])

    def test_friend_facing_pass_enables_distribution(self):
        result = self.evaluate("FriendFacing", False, self.accepted_audio)
        self.assertTrue(result["packaging_allowed"])
        self.assertTrue(result["external_distribution_allowed"])

    def test_unsafe_contract_drift_fails(self):
        contract = copy.deepcopy(self.contract)
        contract["tiers"]["FriendFacing"][
            "blocked_audio_exception_allowed"
        ] = True
        errors = VERIFIER.validate_contract(contract)
        self.assertTrue(any("cannot allow" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
