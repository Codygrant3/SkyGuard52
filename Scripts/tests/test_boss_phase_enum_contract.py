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
    "SkyguardBossDroneBase.cpp",
    "SkyguardBossDroneBase.h",
    "SkyguardBossWeakPointComponent.cpp",
    "SkyguardBossWeakPointComponent.h",
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
LIVE_PHASES = [
    "Approach",
    "Disarm",
    "LockWindow",
    "Critical",
    "Defeated",
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


class BossPhaseEnumContractTests(unittest.TestCase):
    def test_boss_phase_enum_exists(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn("enum class ESkyguardBossPhase : uint8", header)
        self.assertIn("UENUM(BlueprintType)", header)

    def test_enumerators_match_live_order(self) -> None:
        header = origin_main(HEADER_NAME)
        enumerators = enum_enumerators(header, "ESkyguardBossPhase")
        self.assertEqual(enumerators, LIVE_PHASES)
        self.assertEqual(
            enumerators,
            [
                "Approach",
                "Disarm",
                "LockWindow",
                "Critical",
                "Defeated",
            ],
        )
        self.assertEqual(len(enumerators), 5, enumerators)
        body = enum_body(header, "ESkyguardBossPhase")
        for name in LIVE_PHASES:
            self.assertIn(name, body)
            self.assertIn(name, enumerators)

    def test_phase_enum_does_not_require_rifle_or_igla(self) -> None:
        enumerators = enum_enumerators(
            origin_main(HEADER_NAME),
            "ESkyguardBossPhase",
        )
        self.assertNotIn("Rifle", enumerators)
        self.assertNotIn("Igla", enumerators)
        self.assertNotIn("Yak", enumerators)
        self.assertNotEqual(enumerators, ["Rifle", "Igla"])

    def test_contract_is_boss_phase_enum_only(self) -> None:
        header = origin_main(HEADER_NAME)
        body = enum_body(header, "ESkyguardBossPhase")
        self.assertIn("Approach", body)
        self.assertIn("Defeated", body)
        self.assertNotIn("Rifle", body)
        self.assertNotIn("Igla", body)
        self.assertNotIn("Yak", body)
        self.assertNotIn("RifleHits", body)
        self.assertNotIn("IglaHits", body)
        self.assertNotIn("40.f", body)
        self.assertNotIn("80.f", body)
        enumerators = enum_enumerators(header, "ESkyguardBossPhase")
        self.assertEqual(enumerators, LIVE_PHASES)
        self.assertNotEqual(enumerators, ["Rifle", "Igla"])

    def test_locked_files_were_not_the_edit_surface(self) -> None:
        existing = [
            f"Source/Skyguard52/{name}"
            for name in LOCKED
            if (SOURCE / name).exists()
        ]
        for sibling in (
            "Scripts/tests/test_storm_rain_beat_kit_contract.py",
            "Scripts/tests/test_apache_own_ship_systems_contract.py",
            "Scripts/tests/test_pilot_command_roster_contract.py",
            "Scripts/tests/test_mission_objective_formation_enum_contract.py",
            "Scripts/tests/test_mission_weather_enum_contract.py",
            "Scripts/tests/test_environment_quality_enum_contract.py",
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
