from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
HEADER = ROOT / "Source" / "Skyguard52" / "SkyguardYakR3DonorEvaluationRig.h"
SOURCE = ROOT / "Source" / "Skyguard52" / "SkyguardYakR3DonorEvaluationRig.cpp"
TESTS = ROOT / "Source" / "Skyguard52" / "SkyguardYakR3DonorEvaluationRigTests.cpp"


class YakR3DonorEvaluationContractTests(unittest.TestCase):
    def test_evaluation_rig_is_quarantined_and_not_runtime_replacement(self):
        text = HEADER.read_text(encoding="utf-8")
        self.assertIn("Quarantined evaluation-only", text)
        self.assertIn("Transient", text)
        self.assertNotIn('#include "SkyguardYak52Aircraft.h"', text)
        self.assertIn("public AActor", text)

    def test_exact_ten_approved_donor_assets_are_bound(self):
        text = SOURCE.read_text(encoding="utf-8")
        self.assertEqual(text.count('{TEXT("R3_'), 10)
        for name in (
            "CowlingShell",
            "CowlingFrontRing",
            "CowlingShutters",
            "CowlingInletCone",
            "Spinner",
            "PropBlade_A",
            "PropBlade_B",
            "MainWheelWell_L",
            "MainWheelWell_R",
            "NoseWheelWell",
        ):
            self.assertIn(f"SM_M01Q_YAKR3_{name}", text)

    def test_four_contract_clearance_volumes_are_present(self):
        text = SOURCE.read_text(encoding="utf-8")
        for name in (
            "R3_CameraClearance",
            "R3_PilotSafety",
            "R3_RifleMuzzleClearance",
            "R3_IglaBackblastClearance",
        ):
            self.assertIn(name, text)
        self.assertIn("DoDonorsPreserveRequiredClearances", text)

    def test_native_tests_cover_assets_and_clearance(self):
        text = TESTS.read_text(encoding="utf-8")
        self.assertIn("AssetPivotMaterialAndCollisionContract", text)
        self.assertIn("CameraPilotRifleAndIglaClearanceContract", text)
        self.assertIn("GetElementCount() > 0", text)
        self.assertIn("LineTraceSingleByChannel", text)


if __name__ == "__main__":
    unittest.main()
