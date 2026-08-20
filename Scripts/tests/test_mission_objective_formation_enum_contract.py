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
LIVE_OBJECTIVE_TYPES = [
    "DestroyTargets",
    "ProtectAsset",
    "ReachRoutePoint",
    "Survive",
    "ScanTargets",
    "Rescue",
    "BossPhase",
]
LIVE_FORMATION_TYPES = [
    "Line",
    "Vee",
    "EchelonLeft",
    "EchelonRight",
    "Trail",
    "LooseSwarm",
]
LIVE_OBJECTIVE_STATES = [
    "Inactive",
    "Active",
    "Completed",
    "Failed",
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


class MissionObjectiveFormationEnumContractTests(unittest.TestCase):
    def test_objective_formation_and_state_enums_exist(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn("enum class ESkyguardMissionObjectiveType : uint8", header)
        self.assertIn("enum class ESkyguardFormationType : uint8", header)
        self.assertIn("enum class ESkyguardMissionObjectiveState : uint8", header)
        self.assertIn("UENUM(BlueprintType)", header)

    def test_objective_type_enumerators_match_live_order(self) -> None:
        header = origin_main(HEADER_NAME)
        enumerators = enum_enumerators(header, "ESkyguardMissionObjectiveType")
        self.assertEqual(enumerators, LIVE_OBJECTIVE_TYPES)
        self.assertEqual(
            enumerators,
            [
                "DestroyTargets",
                "ProtectAsset",
                "ReachRoutePoint",
                "Survive",
                "ScanTargets",
                "Rescue",
                "BossPhase",
            ],
        )
        self.assertEqual(len(enumerators), 7, enumerators)
        body = enum_body(header, "ESkyguardMissionObjectiveType")
        for name in LIVE_OBJECTIVE_TYPES:
            self.assertIn(name, body)
            self.assertIn(name, enumerators)

    def test_formation_type_enumerators_match_live_order(self) -> None:
        header = origin_main(HEADER_NAME)
        enumerators = enum_enumerators(header, "ESkyguardFormationType")
        self.assertEqual(enumerators, LIVE_FORMATION_TYPES)
        self.assertEqual(
            enumerators,
            [
                "Line",
                "Vee",
                "EchelonLeft",
                "EchelonRight",
                "Trail",
                "LooseSwarm",
            ],
        )
        self.assertEqual(len(enumerators), 6, enumerators)
        body = enum_body(header, "ESkyguardFormationType")
        for name in LIVE_FORMATION_TYPES:
            self.assertIn(name, body)
            self.assertIn(name, enumerators)

    def test_objective_state_enumerators_match_live_order(self) -> None:
        header = origin_main(HEADER_NAME)
        enumerators = enum_enumerators(header, "ESkyguardMissionObjectiveState")
        self.assertEqual(enumerators, LIVE_OBJECTIVE_STATES)
        self.assertEqual(
            enumerators,
            [
                "Inactive",
                "Active",
                "Completed",
                "Failed",
            ],
        )
        self.assertEqual(len(enumerators), 4, enumerators)
        body = enum_body(header, "ESkyguardMissionObjectiveState")
        for name in LIVE_OBJECTIVE_STATES:
            self.assertIn(name, body)
            self.assertIn(name, enumerators)

    def test_enums_do_not_require_rifle_or_igla(self) -> None:
        header = origin_main(HEADER_NAME)
        for enum_name in (
            "ESkyguardMissionObjectiveType",
            "ESkyguardFormationType",
            "ESkyguardMissionObjectiveState",
        ):
            enumerators = enum_enumerators(header, enum_name)
            self.assertNotIn("Rifle", enumerators)
            self.assertNotIn("Igla", enumerators)
            self.assertNotIn("Yak", enumerators)
            self.assertNotEqual(enumerators, ["Rifle", "Igla"])
            body = enum_body(header, enum_name)
            self.assertNotIn("Rifle", body)
            self.assertNotIn("Igla", body)
            self.assertNotIn("Yak", body)

    def test_contract_does_not_re_lock_weather_or_struct_defaults(self) -> None:
        header = origin_main(HEADER_NAME)
        locked_bodies = (
            enum_body(header, "ESkyguardMissionObjectiveType")
            + enum_body(header, "ESkyguardFormationType")
            + enum_body(header, "ESkyguardMissionObjectiveState")
        )
        self.assertNotIn("ESkyguardMissionWeather", locked_bodies)
        self.assertNotIn("Clear", locked_bodies)
        self.assertNotIn("Overcast", locked_bodies)
        self.assertNotIn("NightClear", locked_bodies)
        self.assertNotIn("NightOvercast", locked_bodies)
        self.assertNotIn("RequiredProgress", locked_bodies)
        self.assertNotIn("ScoreReward", locked_bodies)
        self.assertNotIn("UnitCount", locked_bodies)
        self.assertNotIn("SpacingCentimeters", locked_bodies)
        self.assertNotIn("1000", locked_bodies)
        self.assertNotIn("1200.f", locked_bodies)
        self.assertNotIn("40.f", locked_bodies)
        self.assertNotIn("80.f", locked_bodies)
        self.assertNotEqual(
            enum_enumerators(header, "ESkyguardMissionObjectiveType"),
            enum_enumerators(header, "ESkyguardMissionWeather"),
        )
        self.assertEqual(
            enum_enumerators(header, "ESkyguardMissionObjectiveType"),
            LIVE_OBJECTIVE_TYPES,
        )
        self.assertEqual(
            enum_enumerators(header, "ESkyguardFormationType"),
            LIVE_FORMATION_TYPES,
        )
        self.assertEqual(
            enum_enumerators(header, "ESkyguardMissionObjectiveState"),
            LIVE_OBJECTIVE_STATES,
        )

    def test_locked_files_were_not_the_edit_surface(self) -> None:
        existing = [
            f"Source/Skyguard52/{name}"
            for name in LOCKED
            if (SOURCE / name).exists()
        ]
        for sibling in (
            "Scripts/tests/test_mission_weather_enum_contract.py",
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
