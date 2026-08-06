from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "verify_skyguard_phase8_release_gate.py"
)
sys.path.insert(0, str(SCRIPT.parent))
SPEC = importlib.util.spec_from_file_location("release_gate_verifier", SCRIPT)
assert SPEC and SPEC.loader
VERIFIER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFIER)


class ReleaseGateStageScanTests(unittest.TestCase):
    def test_shipping_smoke_requires_explicit_complete_marker(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / "shipping.log"
            log.write_text(
                "\n".join(
                    [
                        'LogRHI: Display: RHI adapters: rhiname="D3D12"',
                        "LogLoad: LoadMap: /Game/Skyguard/Maps/Lvl_M01",
                        "LogWorld: Bringing World /Game/Skyguard/Maps/Lvl_M01 up for play",
                        "[SkyguardStartupSmoke] MAP_READY map=Lvl_M01 seconds=5.00",
                    ]
                ),
                encoding="utf-8",
            )
            scan = VERIFIER.scan_stage(
                {"name": "shipping_startup_smoke", "stdout": str(log)}
            )
            self.assertTrue(scan["d3d12"])
            self.assertTrue(scan["map_loaded"])
            self.assertFalse(scan["shipping_smoke_exit"])

            with log.open("a", encoding="utf-8") as handle:
                handle.write("\n[SkyguardStartupSmoke] COMPLETE map=Lvl_M01\n")
            scan = VERIFIER.scan_stage(
                {"name": "shipping_startup_smoke", "stdout": str(log)}
            )
            self.assertTrue(scan["shipping_smoke_exit"])

    def test_shipping_receipt_requires_complete_exact_map_and_d3d12(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            receipt = Path(directory) / "shipping-receipt.json"
            receipt.write_text(
                """{
  "schema": "skyguard.shipping-startup-smoke.v1",
  "state": "COMPLETE",
  "map": "Lvl_M01_CoastalIntercept_Playable_v1",
  "rhi": "D3D12"
}
""",
                encoding="utf-8",
            )
            result = VERIFIER.verify_shipping_smoke_receipt(
                str(receipt),
                "/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_Playable_v1",
            )
            self.assertTrue(result["pass"], result)

            receipt.write_text(
                receipt.read_text(encoding="utf-8").replace(
                    '"state": "COMPLETE"', '"state": "MAP_READY"'
                ),
                encoding="utf-8",
            )
            result = VERIFIER.verify_shipping_smoke_receipt(
                str(receipt),
                "/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_Playable_v1",
            )
            self.assertFalse(result["pass"])
            self.assertFalse(result["checks"]["state_complete"])

    def test_historical_manifest_is_engineering_only(self) -> None:
        result = VERIFIER.verify_release_tier_receipt({"controls": {}})
        self.assertTrue(result["pass"])
        self.assertEqual("Engineering", result["release_tier"])
        self.assertTrue(result["historical_implicit_engineering_exception"])
        self.assertFalse(result["external_distribution_allowed"])
        self.assertFalse(result["shipping_promotion_allowed"])

    def test_explicit_friend_facing_receipt_requires_production_audio(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            receipt = Path(directory) / "tier.json"
            receipt.write_text(
                """{
  "schema": "skyguard.phase8.release-tier-preflight.v1",
  "result": {
    "release_tier": "FriendFacing",
    "audio_shipping_allowed": false,
    "engineering_audio_exception_requested": false,
    "engineering_audio_exception_applied": false,
    "effective_audio_state": "BLOCK_SHIPPING_UNVERIFIED_AUDIO",
    "packaging_allowed": true,
    "external_distribution_allowed": true,
    "shipping_promotion_allowed": true
  }
}
""",
                encoding="utf-8",
            )
            result = VERIFIER.verify_release_tier_receipt(
                {
                    "controls": {
                        "release_tier": "FriendFacing",
                        "engineering_audio_exception": False,
                    },
                    "release_tier_receipt": str(receipt),
                }
            )
            self.assertFalse(result["pass"])
            self.assertFalse(result["checks"]["tier_audio_policy"])


if __name__ == "__main__":
    unittest.main()
