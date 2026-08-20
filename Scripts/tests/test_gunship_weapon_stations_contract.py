from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_NAME = "SkyguardGunshipTypes.h"
LOCKED = {
    "SkyguardGunshipTypes.h",
    "SkyguardGunshipTypes.cpp",
    "SkyguardGunshipTypesLoadoutTests.cpp",
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
LIVE_STATIONS = [
    ("Cannon", "30mm Cannon"),
    ("Rockets", "Rocket Pods"),
    ("GuidedMissile", "Guided Missile"),
]
SIGHT_MODES = [
    ("Helmet", "Helmet Sight"),
    ("TargetingSensor", "Targeting Sensor"),
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


def enum_display_names(header: str, enum_name: str) -> list[tuple[str, str]]:
    return re.findall(
        r"([A-Za-z_][A-Za-z0-9_]*)\s+UMETA\(\s*DisplayName\s*=\s*\"([^\"]+)\"\s*\)",
        enum_body(header, enum_name),
    )


def nearby_weapon_copy(header: str) -> str:
    start = header.index("enum class ESkyguardGunshipWeapon")
    finish = header.index("enum class ESkyguardGuidedLockPhase", start)
    preface = header[max(0, start - 240) : start]
    return preface + header[start:finish]


class GunshipWeaponStationsContractTests(unittest.TestCase):
    def test_weapon_station_enum_exists(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn("enum class ESkyguardGunshipWeapon : uint8", header)
        self.assertIn("UENUM(BlueprintType)", header)

    def test_enumerators_match_live_apache_cpg_stations_in_order(self) -> None:
        header = origin_main(HEADER_NAME)
        enumerators = enum_enumerators(header, "ESkyguardGunshipWeapon")
        self.assertEqual(
            enumerators,
            [name for name, _ in LIVE_STATIONS],
        )
        self.assertEqual(enumerators, ["Cannon", "Rockets", "GuidedMissile"])
        self.assertEqual(len(enumerators), 3, enumerators)
        self.assertEqual(enum_display_names(header, "ESkyguardGunshipWeapon"), LIVE_STATIONS)
        body = enum_body(header, "ESkyguardGunshipWeapon")
        self.assertIn('Cannon UMETA(DisplayName = "30mm Cannon")', body)
        self.assertIn('Rockets UMETA(DisplayName = "Rocket Pods")', body)
        self.assertIn('GuidedMissile UMETA(DisplayName = "Guided Missile")', body)

    def test_nearby_copy_says_igla_is_not_a_player_weapon(self) -> None:
        header = origin_main(HEADER_NAME)
        nearby = nearby_weapon_copy(header)
        self.assertIn("Igla is not a player weapon", nearby)
        self.assertIn("Live Apache CPG stations", nearby)

    def test_sight_mode_is_helmet_then_targeting_sensor(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn("enum class ESkyguardCpgSightMode : uint8", header)
        enumerators = enum_enumerators(header, "ESkyguardCpgSightMode")
        self.assertEqual(enumerators, [name for name, _ in SIGHT_MODES])
        self.assertEqual(enumerators, ["Helmet", "TargetingSensor"])
        self.assertEqual(len(enumerators), 2, enumerators)
        self.assertEqual(enum_display_names(header, "ESkyguardCpgSightMode"), SIGHT_MODES)

    def test_station_enum_does_not_contain_rifle_or_igla(self) -> None:
        header = origin_main(HEADER_NAME)
        weapon_body = enum_body(header, "ESkyguardGunshipWeapon")
        sight_body = enum_body(header, "ESkyguardCpgSightMode")
        weapon_names = enum_enumerators(header, "ESkyguardGunshipWeapon")
        sight_names = enum_enumerators(header, "ESkyguardCpgSightMode")
        for banned in ("Rifle", "Igla", "Yak"):
            self.assertNotIn(banned, weapon_names)
            self.assertNotIn(banned, sight_names)
            self.assertNotIn(banned, weapon_body)
            self.assertNotIn(banned, sight_body)

    def test_locked_files_were_not_the_edit_surface(self) -> None:
        existing = [
            f"Source/Skyguard52/{name}"
            for name in LOCKED
            if (SOURCE / name).exists()
        ]
        feel = ROOT / "Scripts" / "tests" / "test_apache_cpg_feel_contract.py"
        if feel.exists():
            existing.append("Scripts/tests/test_apache_cpg_feel_contract.py")
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
