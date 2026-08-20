from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_NAME = "SkyguardMissionMapAssemblyDirector.h"
LOCKED = {
    "SkyguardMissionMapAssemblyDirector.h",
    "SkyguardMissionMapAssemblyDirector.cpp",
    "SkyguardMissionMapAssemblyDirectorTests.cpp",
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
LOCKED_SCRIPTS = (
    "Scripts/tests/test_storm_rain_beat_kit_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
    "Scripts/tests/test_day_sortie_beat_kit_contract.py",
    "Scripts/tests/test_night_sortie_beat_kit_contract.py",
    "Scripts/tests/test_mission_map_readiness_defaults_contract.py",
    "Scripts/tests/test_mission_objective_anchor_defaults_contract.py",
    "Scripts/tests/test_mission_landmark_anchor_defaults_contract.py",
)
LIVE_STYLES = [
    "HarborIndustrial",
    "CoastalHighway",
    "BlackoutUrban",
    "OffshoreStorm",
    "AirfieldMilitary",
    "IslandSearch",
]
SIBLING_TYPES = (
    "FSkyguardMissionMapReadiness",
    "FSkyguardMissionObjectiveAnchor",
    "FSkyguardMissionLandmarkAnchor",
)
HARBOR_TUNING = (
    "IncomingRadarLiveIntervalSeconds",
    "IncomingRadarDownIntervalSeconds",
    "40.f",
    "80.f",
)


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


class MissionSkylineStyleEnumContractTests(unittest.TestCase):
    def test_skyline_style_enum_exists(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn("enum class ESkyguardMissionSkylineStyle : uint8", header)
        self.assertIn("UENUM(BlueprintType)", header)

    def test_enumerators_match_live_order(self) -> None:
        header = origin_main(HEADER_NAME)
        enumerators = enum_enumerators(header, "ESkyguardMissionSkylineStyle")
        self.assertEqual(enumerators, LIVE_STYLES)
        self.assertEqual(
            enumerators,
            [
                "HarborIndustrial",
                "CoastalHighway",
                "BlackoutUrban",
                "OffshoreStorm",
                "AirfieldMilitary",
                "IslandSearch",
            ],
        )
        self.assertEqual(len(enumerators), 6, enumerators)
        body = enum_body(header, "ESkyguardMissionSkylineStyle")
        for name in LIVE_STYLES:
            self.assertIn(name, body)
            self.assertIn(name, enumerators)

    def test_skyline_style_enum_does_not_invent_index_none(self) -> None:
        enumerators = enum_enumerators(
            origin_main(HEADER_NAME),
            "ESkyguardMissionSkylineStyle",
        )
        body = enum_body(
            origin_main(HEADER_NAME),
            "ESkyguardMissionSkylineStyle",
        )
        self.assertNotIn("INDEX_NONE", enumerators)
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("NAME_None", enumerators)
        self.assertNotIn("NAME_None", body)

    def test_skyline_style_enum_does_not_require_rifle_or_igla(self) -> None:
        enumerators = enum_enumerators(
            origin_main(HEADER_NAME),
            "ESkyguardMissionSkylineStyle",
        )
        self.assertNotIn("Rifle", enumerators)
        self.assertNotIn("Igla", enumerators)
        self.assertNotIn("Yak", enumerators)
        self.assertNotEqual(enumerators, ["Rifle", "Igla"])

    def test_contract_is_skyline_style_enum_only(self) -> None:
        header = origin_main(HEADER_NAME)
        body = enum_body(header, "ESkyguardMissionSkylineStyle")
        self.assertIn("HarborIndustrial", body)
        self.assertIn("IslandSearch", body)
        for name in SIBLING_TYPES:
            self.assertNotIn(name, body)
        self.assertNotIn("bDefinitionValid", body)
        self.assertNotIn("ObjectiveId", body)
        self.assertNotIn("LandmarkId", body)
        self.assertNotIn("bMissionExclusive", body)
        self.assertNotIn("RouteLengthCentimeters", body)
        self.assertNotIn("WorldLocation", body)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        self.assertNotIn("Rifle", body)
        self.assertNotIn("Igla", body)
        self.assertNotIn("Yak", body)
        enumerators = enum_enumerators(header, "ESkyguardMissionSkylineStyle")
        self.assertEqual(enumerators, LIVE_STYLES)
        self.assertNotEqual(enumerators, ["Rifle", "Igla"])

    def test_locked_files_were_not_the_edit_surface(self) -> None:
        existing = [
            f"Source/Skyguard52/{name}"
            for name in LOCKED
            if (SOURCE / name).exists()
        ]
        for sibling in LOCKED_SCRIPTS:
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
