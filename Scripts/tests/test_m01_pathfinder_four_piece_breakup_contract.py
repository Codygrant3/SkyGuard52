from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class PathfinderFourPieceBreakupContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.boss_cpp = (
            ROOT / "Source/Skyguard52/SkyguardPathfinderBoss.cpp"
        ).read_text(encoding="utf-8-sig")
        cls.boss_h = (
            ROOT / "Source/Skyguard52/SkyguardPathfinderBoss.h"
        ).read_text(encoding="utf-8-sig")
        cls.boss_tests = (
            ROOT / "Source/Skyguard52/SkyguardPathfinderBossTests.cpp"
        ).read_text(encoding="utf-8-sig")
        cls.director = (
            ROOT / "Source/Skyguard52/SkyguardMission01IntegrationDirector.cpp"
        ).read_text(encoding="utf-8-sig")
        cls.campaign_builder = (
            ROOT / "Scripts/build_skyguard_phase7_campaign_v1.py"
        ).read_text(encoding="utf-8-sig")
        cls.validation_builder = (
            ROOT / "Scripts/build_skyguard_m01_wave1_refinement_validation.py"
        ).read_text(encoding="utf-8-sig")

    def test_spine_component_is_authored_and_registered(self) -> None:
        self.assertIn("TObjectPtr<UStaticMeshComponent> DebrisSpine", self.boss_h)
        self.assertIn(
            'CreateDefaultSubobject<UStaticMeshComponent>(TEXT("DebrisSpine"))',
            self.boss_cpp,
        )
        self.assertIn("RegisterDefeatDebris(DebrisSpine)", self.boss_cpp)

    def test_runtime_uses_the_imported_collidable_spine_candidate(self) -> None:
        self.assertIn(
            "SM_Boss_Pathfinder_BreakChunk_Spine_AAA."
            "SM_Boss_Pathfinder_BreakChunk_Spine_AAA",
            self.boss_cpp,
        )
        self.assertLess(
            self.boss_cpp.index("MaxDefeatDebrisPieces = 4"),
            self.boss_cpp.index("RegisterDefeatDebris(DebrisSpine)"),
        )

    def test_m01_contract_requires_exactly_four_bounded_pieces(self) -> None:
        self.assertIn(
            "Pathfinder->GetDefeatDebrisPieceCount() == 4", self.director
        )
        self.assertIn(
            "Pathfinder->GetMaxDefeatDebrisPieces() <= 4", self.director
        )
        self.assertRegex(
            self.director,
            re.compile(r"Mission->Boss\.MaximumBreakupPieces\s*!=\s*4"),
        )

    def test_campaign_authoring_preserves_the_m01_exception(self) -> None:
        self.assertIn(
            'if spec["id"] == "M01_CoastalIntercept"', self.campaign_builder
        )
        self.assertIn('"maximum_breakup_pieces": (', self.campaign_builder)

    def test_validation_and_native_regression_cover_spine_activation(self) -> None:
        self.assertIn(
            '"DebrisSpine": "SM_Boss_Pathfinder_BreakChunk_Spine_AAA"',
            self.validation_builder,
        )
        self.assertIn(
            "Defeat activates the preallocated spine debris", self.boss_tests
        )
        self.assertIn(
            "Spine debris uses the imported refinement mesh", self.boss_tests
        )


if __name__ == "__main__":
    unittest.main()
