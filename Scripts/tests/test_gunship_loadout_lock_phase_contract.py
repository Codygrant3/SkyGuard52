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
LOADOUTS = [
    ("Balanced", "Balanced"),
    ("AntiArmor", "Anti-Armor"),
    ("RocketHeavy", "Rocket Heavy"),
    ("Intercept", "Intercept"),
]
LOCK_PHASES = [
    ("Search", "Search"),
    ("Detect", "Detect"),
    ("Track", "Track"),
    ("Lock", "Lock"),
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


def nearby_lock_phase_copy(header: str) -> str:
    start = header.index("enum class ESkyguardGuidedLockPhase")
    finish = header.index("enum class ESkyguardCpgSightMode", start)
    preface = header[max(0, start - 240) : start]
    return preface + header[start:finish]


def nearby_loadout_copy(header: str) -> str:
    start = header.index("enum class ESkyguardLoadout")
    finish = header.index("enum class ESkyguardClimaxKind", start)
    preface = header[max(0, start - 80) : start]
    return preface + header[start:finish]


class GunshipLoadoutLockPhaseContractTests(unittest.TestCase):
    def test_loadout_and_lock_phase_enums_exist(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn("enum class ESkyguardLoadout : uint8", header)
        self.assertIn("enum class ESkyguardGuidedLockPhase : uint8", header)
        self.assertIn("UENUM(BlueprintType)", header)

    def test_loadout_enumerators_match_live_playstyle_kit_in_order(self) -> None:
        header = origin_main(HEADER_NAME)
        enumerators = enum_enumerators(header, "ESkyguardLoadout")
        self.assertEqual(enumerators, [name for name, _ in LOADOUTS])
        self.assertEqual(
            enumerators,
            ["Balanced", "AntiArmor", "RocketHeavy", "Intercept"],
        )
        self.assertEqual(len(enumerators), 4, enumerators)
        self.assertEqual(enum_display_names(header, "ESkyguardLoadout"), LOADOUTS)
        body = enum_body(header, "ESkyguardLoadout")
        self.assertIn('Balanced UMETA(DisplayName = "Balanced")', body)
        self.assertIn('AntiArmor UMETA(DisplayName = "Anti-Armor")', body)
        self.assertIn('RocketHeavy UMETA(DisplayName = "Rocket Heavy")', body)
        self.assertIn('Intercept UMETA(DisplayName = "Intercept")', body)

    def test_lock_phase_enumerators_match_readable_escalation_in_order(self) -> None:
        header = origin_main(HEADER_NAME)
        enumerators = enum_enumerators(header, "ESkyguardGuidedLockPhase")
        self.assertEqual(enumerators, [name for name, _ in LOCK_PHASES])
        self.assertEqual(enumerators, ["Search", "Detect", "Track", "Lock"])
        self.assertEqual(len(enumerators), 4, enumerators)
        self.assertEqual(
            enum_display_names(header, "ESkyguardGuidedLockPhase"),
            LOCK_PHASES,
        )
        body = enum_body(header, "ESkyguardGuidedLockPhase")
        self.assertIn('Search UMETA(DisplayName = "Search")', body)
        self.assertIn('Detect UMETA(DisplayName = "Detect")', body)
        self.assertIn('Track UMETA(DisplayName = "Track")', body)
        self.assertIn('Lock UMETA(DisplayName = "Lock")', body)

    def test_nearby_copy_says_playstyle_kit_and_fire_is_last(self) -> None:
        header = origin_main(HEADER_NAME)
        loadout_nearby = nearby_loadout_copy(header)
        lock_nearby = nearby_lock_phase_copy(header)
        self.assertIn("Playstyle kit", loadout_nearby)
        self.assertIn("Keys 1-4", loadout_nearby)
        self.assertIn("Fire is last", lock_nearby)
        self.assertIn("guided-missile", lock_nearby)
        self.assertIn("Igla is not a player weapon", header)

    def test_enums_do_not_require_rifle_or_igla(self) -> None:
        header = origin_main(HEADER_NAME)
        loadout_names = enum_enumerators(header, "ESkyguardLoadout")
        lock_names = enum_enumerators(header, "ESkyguardGuidedLockPhase")
        loadout_body = enum_body(header, "ESkyguardLoadout")
        lock_body = enum_body(header, "ESkyguardGuidedLockPhase")
        for banned in ("Rifle", "Igla", "Yak"):
            self.assertNotIn(banned, loadout_names)
            self.assertNotIn(banned, lock_names)
            self.assertNotIn(banned, loadout_body)
            self.assertNotIn(banned, lock_body)

    def test_locked_files_were_not_the_edit_surface(self) -> None:
        existing = [
            f"Source/Skyguard52/{name}"
            for name in LOCKED
            if (SOURCE / name).exists()
        ]
        for sibling in (
            "Scripts/tests/test_gunship_weapon_stations_contract.py",
            "Scripts/tests/test_apache_cpg_feel_contract.py",
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
