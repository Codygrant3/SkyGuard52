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
    "SkyguardPatrolShipBoss.h",
    "SkyguardPatrolShipBoss.cpp",
    "SkyguardPatrolShipEmptyFailClosedTests.cpp",
    "SkyguardPatrolShipBossTests.cpp",
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
LIVE_SYSTEMS = [
    ("Radar", "Search Radar"),
    ("Cannon", "Cannon"),
    ("Launcher", "Launcher"),
    ("Engines", "Engines"),
    ("DroneDeck", "Drone Deck"),
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


def nearby_system_copy(header: str) -> str:
    start = header.index("enum class ESkyguardPatrolShipSystem")
    finish = header.index("enum class ESkyguardPilotLine", start)
    preface = header[max(0, start - 240) : start]
    return preface + header[start:finish]


class PatrolShipSystemEnumContractTests(unittest.TestCase):
    def test_patrol_ship_system_enum_exists(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn("enum class ESkyguardPatrolShipSystem : uint8", header)
        self.assertIn("UENUM(BlueprintType)", header)

    def test_enumerators_match_live_order(self) -> None:
        header = origin_main(HEADER_NAME)
        enumerators = enum_enumerators(header, "ESkyguardPatrolShipSystem")
        self.assertEqual(enumerators, [name for name, _ in LIVE_SYSTEMS])
        self.assertEqual(
            enumerators,
            [
                "Radar",
                "Cannon",
                "Launcher",
                "Engines",
                "DroneDeck",
            ],
        )
        self.assertEqual(len(enumerators), 5, enumerators)
        self.assertEqual(
            enum_display_names(header, "ESkyguardPatrolShipSystem"),
            LIVE_SYSTEMS,
        )
        body = enum_body(header, "ESkyguardPatrolShipSystem")
        self.assertIn('Radar UMETA(DisplayName = "Search Radar")', body)
        self.assertIn('Cannon UMETA(DisplayName = "Cannon")', body)
        self.assertIn('Launcher UMETA(DisplayName = "Launcher")', body)
        self.assertIn('Engines UMETA(DisplayName = "Engines")', body)
        self.assertIn('DroneDeck UMETA(DisplayName = "Drone Deck")', body)
        for name, display in LIVE_SYSTEMS:
            self.assertIn(name, body)
            self.assertIn(name, enumerators)
            self.assertIn(display, body)

    def test_nearby_copy_names_harbor_breaker_systems(self) -> None:
        nearby = nearby_system_copy(origin_main(HEADER_NAME))
        self.assertIn("Harbor Breaker patrol-ship systems", nearby)
        self.assertIn("Not a single health bar", nearby)
        self.assertIn("enum class ESkyguardPatrolShipSystem : uint8", nearby)

    def test_patrol_ship_system_enum_does_not_require_rifle_or_igla(self) -> None:
        header = origin_main(HEADER_NAME)
        enumerators = enum_enumerators(header, "ESkyguardPatrolShipSystem")
        body = enum_body(header, "ESkyguardPatrolShipSystem")
        self.assertNotIn("Rifle", enumerators)
        self.assertNotIn("Igla", enumerators)
        self.assertNotIn("Yak", enumerators)
        self.assertNotIn("Rifle", body)
        self.assertNotIn("Igla", body)
        self.assertNotIn("Yak", body)
        self.assertNotEqual(enumerators, ["Rifle", "Igla"])

    def test_contract_is_patrol_ship_system_enum_only(self) -> None:
        header = origin_main(HEADER_NAME)
        body = enum_body(header, "ESkyguardPatrolShipSystem")
        self.assertIn("Radar", body)
        self.assertIn("DroneDeck", body)
        for sibling in (
            "ESkyguardClimaxKind",
            "ESkyguardGunshipWeapon",
            "ESkyguardCpgSightMode",
            "ESkyguardGuidedLockPhase",
            "ESkyguardLoadout",
            "ESkyguardPilotCommand",
            "SkyguardApacheCpgFeel",
        ):
            self.assertNotIn(sibling, body)
        self.assertNotIn("RivalHelo", body)
        self.assertNotIn("ArmorColumn", body)
        self.assertNotIn("MixedSwarm", body)
        self.assertNotIn("Rockets", body)
        self.assertNotIn("GuidedMissile", body)
        self.assertNotIn("Helmet", body)
        self.assertNotIn("TargetingSensor", body)
        self.assertNotIn("Detect", body)
        self.assertNotIn("Track", body)
        self.assertNotIn("Balanced", body)
        self.assertNotIn("AntiArmor", body)
        self.assertNotIn("RocketHeavy", body)
        self.assertNotIn("Intercept", body)
        self.assertNotIn("OrbitLeft", body)
        self.assertNotIn("AttackRun", body)
        self.assertNotIn("CannonFireRate", body)
        self.assertNotIn("GuidedLockSeconds", body)
        self.assertNotIn("CannonMagazineSize", body)
        self.assertNotIn("12.0f", body)
        self.assertNotIn("1.80f", body)
        self.assertNotIn("22.0f", body)
        self.assertNotIn("IncomingRadarLiveIntervalSeconds", body)
        self.assertNotIn("IncomingRadarDownIntervalSeconds", body)
        self.assertNotIn("40.f", body)
        self.assertNotIn("80.f", body)
        self.assertNotIn("Rifle", body)
        self.assertNotIn("Igla", body)
        self.assertNotIn("Yak", body)
        enumerators = enum_enumerators(header, "ESkyguardPatrolShipSystem")
        self.assertEqual(enumerators, [name for name, _ in LIVE_SYSTEMS])
        self.assertNotEqual(enumerators, ["Rifle", "Igla"])

    def test_locked_files_were_not_the_edit_surface(self) -> None:
        existing = [
            f"Source/Skyguard52/{name}"
            for name in LOCKED
            if (SOURCE / name).exists()
        ]
        for sibling in (
            "Scripts/tests/test_climax_kind_enum_contract.py",
            "Scripts/tests/test_gunship_weapon_stations_contract.py",
            "Scripts/tests/test_gunship_loadout_lock_phase_contract.py",
            "Scripts/tests/test_pilot_command_roster_contract.py",
            "Scripts/tests/test_apache_cpg_feel_contract.py",
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
