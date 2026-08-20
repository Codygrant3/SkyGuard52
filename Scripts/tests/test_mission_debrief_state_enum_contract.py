from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_NAME = "SkyguardMissionTypes.h"
LOCKED = {
    "SkyguardMissionTypes.h",
    "SkyguardMissionTypesDefaultsTests.cpp",
    "SkyguardCampaignTheaterKit.h",
    "SkyguardCampaignTheaterKitTests.cpp",
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
}
LIVE_DEBRIEF_STATES = [
    "Unavailable",
    "Ready",
    "Acknowledged",
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


class MissionDebriefStateEnumContractTests(unittest.TestCase):
    def test_debrief_state_enum_exists(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn("enum class ESkyguardMissionDebriefState : uint8", header)
        self.assertIn("UENUM(BlueprintType)", header)

    def test_enumerators_match_live_order(self) -> None:
        header = origin_main(HEADER_NAME)
        enumerators = enum_enumerators(header, "ESkyguardMissionDebriefState")
        self.assertEqual(enumerators, LIVE_DEBRIEF_STATES)
        self.assertEqual(
            enumerators,
            [
                "Unavailable",
                "Ready",
                "Acknowledged",
            ],
        )
        self.assertEqual(len(enumerators), 3, enumerators)
        body = enum_body(header, "ESkyguardMissionDebriefState")
        for name in LIVE_DEBRIEF_STATES:
            self.assertIn(name, body)
            self.assertIn(name, enumerators)

    def test_debrief_state_enum_does_not_require_rifle_or_igla(self) -> None:
        enumerators = enum_enumerators(
            origin_main(HEADER_NAME),
            "ESkyguardMissionDebriefState",
        )
        self.assertNotIn("Rifle", enumerators)
        self.assertNotIn("Igla", enumerators)
        self.assertNotIn("Yak", enumerators)
        self.assertNotEqual(enumerators, ["Rifle", "Igla"])

    def test_contract_is_debrief_state_enum_only(self) -> None:
        header = origin_main(HEADER_NAME)
        body = enum_body(header, "ESkyguardMissionDebriefState")
        self.assertIn("Unavailable", body)
        self.assertIn("Acknowledged", body)
        self.assertNotIn("ESkyguardMissionObjectiveType", body)
        self.assertNotIn("ESkyguardFormationType", body)
        self.assertNotIn("ESkyguardMissionObjectiveState", body)
        self.assertNotIn("ESkyguardMissionWeather", body)
        self.assertNotIn("DestroyTargets", body)
        self.assertNotIn("ProtectAsset", body)
        self.assertNotIn("EchelonLeft", body)
        self.assertNotIn("LooseSwarm", body)
        self.assertNotIn("Inactive", body)
        self.assertNotIn("Completed", body)
        self.assertNotIn("Clear", body)
        self.assertNotIn("Overcast", body)
        self.assertNotIn("NightClear", body)
        self.assertNotIn("NightOvercast", body)
        self.assertNotIn("RequiredProgress", body)
        self.assertNotIn("ScoreReward", body)
        self.assertNotIn("UnitCount", body)
        self.assertNotIn("SpacingCentimeters", body)
        self.assertNotIn("1000", body)
        self.assertNotIn("1200.f", body)
        self.assertNotIn("40.f", body)
        self.assertNotIn("80.f", body)
        self.assertNotIn("Rifle", body)
        self.assertNotIn("Igla", body)
        self.assertNotIn("Yak", body)
        enumerators = enum_enumerators(header, "ESkyguardMissionDebriefState")
        self.assertEqual(enumerators, LIVE_DEBRIEF_STATES)
        self.assertNotEqual(enumerators, ["Rifle", "Igla"])

    def test_locked_files_were_not_the_edit_surface(self) -> None:
        existing = [
            f"Source/Skyguard52/{name}"
            for name in LOCKED
            if (SOURCE / name).exists()
        ]
        for sibling in (
            "Scripts/tests/test_storm_rain_beat_kit_contract.py",
            "Scripts/tests/test_mission_objective_formation_enum_contract.py",
            "Scripts/tests/test_mission_weather_enum_contract.py",
            "Scripts/tests/test_boss_phase_enum_contract.py",
            "Scripts/tests/test_environment_quality_enum_contract.py",
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
