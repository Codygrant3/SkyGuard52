from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_NAME = "SkyguardBossTypes.h"
LOCKED = {
    "SkyguardBossTypes.h",
    "SkyguardPilotVoice.h",
    "SkyguardPilotVoice.cpp",
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
LIVE_COMMANDS = [
    "Pursuit",
    "Break",
    "OrbitLeft",
    "OrbitRight",
    "Extend",
    "Hold",
    "Climb",
    "Descend",
    "AttackRun",
    "FaceTarget",
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


class PilotCommandRosterContractTests(unittest.TestCase):
    def test_pilot_command_enum_exists(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn("enum class ESkyguardPilotCommand : uint8", header)
        self.assertIn("UENUM(BlueprintType)", header)

    def test_enumerators_match_live_apache_cpg_roster_in_order(self) -> None:
        header = origin_main(HEADER_NAME)
        enumerators = enum_enumerators(header, "ESkyguardPilotCommand")
        self.assertEqual(enumerators, LIVE_COMMANDS)
        self.assertEqual(
            enumerators,
            [
                "Pursuit",
                "Break",
                "OrbitLeft",
                "OrbitRight",
                "Extend",
                "Hold",
                "Climb",
                "Descend",
                "AttackRun",
                "FaceTarget",
            ],
        )
        self.assertEqual(len(enumerators), 10, enumerators)
        body = enum_body(header, "ESkyguardPilotCommand")
        for name in LIVE_COMMANDS:
            self.assertIn(name, body)
            self.assertIn(name, enumerators)

    def test_pilot_command_does_not_require_rifle_or_igla(self) -> None:
        enumerators = enum_enumerators(
            origin_main(HEADER_NAME),
            "ESkyguardPilotCommand",
        )
        self.assertNotIn("Rifle", enumerators)
        self.assertNotIn("Igla", enumerators)
        self.assertNotIn("Yak", enumerators)
        self.assertNotEqual(enumerators, ["Rifle", "Igla"])

    def test_boss_weapon_rifle_igla_are_not_live_player_weapons(self) -> None:
        header = origin_main(HEADER_NAME)
        commands = enum_enumerators(header, "ESkyguardPilotCommand")
        weapons = enum_enumerators(header, "ESkyguardBossWeapon")
        self.assertEqual(commands, LIVE_COMMANDS)
        self.assertNotEqual(commands, weapons)
        self.assertNotIn("Rifle", commands)
        self.assertNotIn("Igla", commands)
        self.assertNotEqual(commands, ["Rifle", "Igla"])

    def test_contract_is_pilot_command_roster_only(self) -> None:
        header = origin_main(HEADER_NAME)
        command_body = enum_body(header, "ESkyguardPilotCommand")
        self.assertIn("Pursuit", command_body)
        self.assertIn("FaceTarget", command_body)
        self.assertNotIn("RifleHits", command_body)
        self.assertNotIn("IglaHits", command_body)
        self.assertNotIn("Rifle", command_body)
        self.assertNotIn("Igla", command_body)
        enumerators = enum_enumerators(header, "ESkyguardPilotCommand")
        self.assertEqual(enumerators, LIVE_COMMANDS)

    def test_locked_files_were_not_the_edit_surface(self) -> None:
        existing = [
            f"Source/Skyguard52/{name}"
            for name in LOCKED
            if (SOURCE / name).exists()
        ]
        sibling = ROOT / "Scripts" / "tests" / "test_pilot_confirm_line_contract.py"
        if sibling.exists():
            existing.append("Scripts/tests/test_pilot_confirm_line_contract.py")
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
