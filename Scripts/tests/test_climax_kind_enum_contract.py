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
    "SkyguardBossTypes.h",
}
LIVE_KINDS = [
    "PatrolShip",
    "RivalHelo",
    "ArmorColumn",
    "MixedSwarm",
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


class ClimaxKindEnumContractTests(unittest.TestCase):
    def test_climax_kind_enum_exists(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn("enum class ESkyguardClimaxKind : uint8", header)
        self.assertIn("UENUM(BlueprintType)", header)

    def test_enumerators_match_live_order(self) -> None:
        header = origin_main(HEADER_NAME)
        enumerators = enum_enumerators(header, "ESkyguardClimaxKind")
        self.assertEqual(enumerators, LIVE_KINDS)
        self.assertEqual(
            enumerators,
            [
                "PatrolShip",
                "RivalHelo",
                "ArmorColumn",
                "MixedSwarm",
            ],
        )
        self.assertEqual(len(enumerators), 4, enumerators)
        body = enum_body(header, "ESkyguardClimaxKind")
        for name in LIVE_KINDS:
            self.assertIn(name, body)
            self.assertIn(name, enumerators)

    def test_climax_kind_enum_does_not_require_rifle_or_igla(self) -> None:
        enumerators = enum_enumerators(
            origin_main(HEADER_NAME),
            "ESkyguardClimaxKind",
        )
        self.assertNotIn("Rifle", enumerators)
        self.assertNotIn("Igla", enumerators)
        self.assertNotIn("Yak", enumerators)
        self.assertNotEqual(enumerators, ["Rifle", "Igla"])

    def test_contract_is_climax_kind_enum_only(self) -> None:
        header = origin_main(HEADER_NAME)
        body = enum_body(header, "ESkyguardClimaxKind")
        self.assertIn("PatrolShip", body)
        self.assertIn("MixedSwarm", body)
        for sibling in (
            "ESkyguardGunshipWeapon",
            "ESkyguardCpgSightMode",
            "ESkyguardGuidedLockPhase",
            "ESkyguardLoadout",
            "ESkyguardPilotCommand",
            "ESkyguardPatrolShipSystem",
            "SkyguardApacheCpgFeel",
        ):
            self.assertNotIn(sibling, body)
        self.assertNotIn("CannonFireRate", body)
        self.assertNotIn("GuidedLockSeconds", body)
        self.assertNotIn("CannonMagazineSize", body)
        self.assertNotIn("12.0f", body)
        self.assertNotIn("1.80f", body)
        self.assertNotIn("22.0f", body)
        self.assertNotIn("Helmet", body)
        self.assertNotIn("TargetingSensor", body)
        self.assertNotIn("Search", body)
        self.assertNotIn("Detect", body)
        self.assertNotIn("Balanced", body)
        self.assertNotIn("AntiArmor", body)
        self.assertNotIn("DroneDeck", body)
        self.assertNotIn("40.f", body)
        self.assertNotIn("80.f", body)
        self.assertNotIn("Rifle", body)
        self.assertNotIn("Igla", body)
        self.assertNotIn("Yak", body)
        enumerators = enum_enumerators(header, "ESkyguardClimaxKind")
        self.assertEqual(enumerators, LIVE_KINDS)
        self.assertNotEqual(enumerators, ["Rifle", "Igla"])

    def test_locked_files_were_not_the_edit_surface(self) -> None:
        existing = [
            f"Source/Skyguard52/{name}"
            for name in LOCKED
            if (SOURCE / name).exists()
        ]
        for sibling in (
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
