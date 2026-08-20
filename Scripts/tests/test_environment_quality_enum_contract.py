from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_NAME = "SkyguardCoastalEnvironmentDirector.h"
LOCKED = {
    "SkyguardCoastalEnvironmentDirector.h",
    "SkyguardCoastalEnvironmentDirector.cpp",
    "SkyguardCoastalEnvironmentDirectorEmptyFailClosedTests.cpp",
    "SkyguardCoastalEnvironmentDirectorTests.cpp",
    "SkyguardRadarNode.cpp",
    "SkyguardRadarNode.h",
    "SkyguardGuidedLockRules.cpp",
    "SkyguardGuidedLockRules.h",
    "SkyguardCpgHud.cpp",
    "SkyguardCpgHud.h",
    "SkyguardCpgHudTests.cpp",
    "SkyguardCpgSightHud.cpp",
    "SkyguardCpgSightHud.h",
    "SkyguardGunner.cpp",
    "SkyguardGunner.h",
    "SkyguardGunnerCampaign.cpp",
    "SkyguardProtectAsset.cpp",
    "SkyguardProtectAsset.h",
    "SkyguardHarborProofTests.cpp",
    "SkyguardCampaignTheaterKitTests.cpp",
}
LIVE_QUALITIES = [
    "Low",
    "Medium",
    "High",
    "Epic",
]


def origin_main(name: str) -> str:
    result = subprocess.run(
        ["git", "show", f"origin/main:Source/Skyguard52/{name}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def enum_body(header: str, enum_name: str) -> str:
    start = header.index(f"enum class {enum_name}")
    brace = header.index("{", start)
    finish = header.index("}", brace)
    return header[brace : finish + 1]


def enum_enumerators(header: str, enum_name: str) -> list[str]:
    return re.findall(
        r"^\s*([A-Za-z_][A-Za-z0-9_]*)\b",
        enum_body(header, enum_name),
        re.M,
    )


class EnvironmentQualityEnumContractTests(unittest.TestCase):
    def test_environment_quality_enum_exists(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn("enum class ESkyguardEnvironmentQuality : uint8", header)
        self.assertIn("UENUM(BlueprintType)", header)

    def test_enumerators_match_live_order(self) -> None:
        header = origin_main(HEADER_NAME)
        enumerators = enum_enumerators(header, "ESkyguardEnvironmentQuality")
        self.assertEqual(enumerators, LIVE_QUALITIES)
        self.assertEqual(
            enumerators,
            [
                "Low",
                "Medium",
                "High",
                "Epic",
            ],
        )
        self.assertEqual(len(enumerators), 4, enumerators)
        body = enum_body(header, "ESkyguardEnvironmentQuality")
        for name in LIVE_QUALITIES:
            self.assertIn(name, body)
            self.assertIn(name, enumerators)

    def test_quality_enum_does_not_require_rifle_or_igla(self) -> None:
        enumerators = enum_enumerators(
            origin_main(HEADER_NAME),
            "ESkyguardEnvironmentQuality",
        )
        self.assertNotIn("Rifle", enumerators)
        self.assertNotIn("Igla", enumerators)
        self.assertNotIn("Yak", enumerators)
        self.assertNotEqual(enumerators, ["Rifle", "Igla"])

    def test_contract_is_quality_enum_only(self) -> None:
        header = origin_main(HEADER_NAME)
        body = enum_body(header, "ESkyguardEnvironmentQuality")
        self.assertIn("Low", body)
        self.assertIn("Epic", body)
        self.assertNotIn("PlacementSeed", body)
        self.assertNotIn("EpicTreeBudget", body)
        self.assertNotIn("EpicShrubBudget", body)
        self.assertNotIn("RouteLengthCm", body)
        self.assertNotIn("RouteCorridorHalfWidthCm", body)
        self.assertNotIn("ShorelineLandOffsetCm", body)
        self.assertNotIn("InlandExtentCm", body)
        self.assertNotIn("VegetationStartCullDistanceCm", body)
        self.assertNotIn("VegetationEndCullDistanceCm", body)
        self.assertNotIn("WindStrength", body)
        self.assertNotIn("WindSpeed", body)
        self.assertNotIn("5201", body)
        self.assertNotIn("240", body)
        self.assertNotIn("480", body)
        self.assertNotIn("45000.f", body)
        self.assertNotIn("2800.f", body)
        self.assertNotIn("40.f", body)
        self.assertNotIn("80.f", body)
        self.assertNotIn("Rifle", body)
        self.assertNotIn("Igla", body)
        self.assertNotIn("Yak", body)
        enumerators = enum_enumerators(header, "ESkyguardEnvironmentQuality")
        self.assertEqual(enumerators, LIVE_QUALITIES)

    def test_locked_files_were_not_the_edit_surface(self) -> None:
        existing = [
            f"Source/Skyguard52/{name}"
            for name in LOCKED
            if (SOURCE / name).exists()
        ]
        for sibling in (
            "Scripts/tests/test_storm_rain_beat_kit_contract.py",
            "Scripts/tests/test_campaign_theater_kit_contract.py",
            "Scripts/tests/test_day_sortie_beat_kit_contract.py",
            "Scripts/tests/test_night_sortie_beat_kit_contract.py",
        ):
            if (ROOT / sibling).exists():
                existing.append(sibling)
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD", "--", *existing],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.stdout.strip(), "")


if __name__ == "__main__":
    unittest.main()
