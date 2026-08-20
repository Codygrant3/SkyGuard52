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
    "SkyguardGunshipTypesLoadoutTests.cpp",
    "SkyguardMissionDirectorPresentationHelpersTests.cpp",
    "SkyguardAudioAcceptanceHarnessFailClosedTests.cpp",
}

CANNON_FEEL = {
    "CannonFireRate": "12.0f",
    "CannonDamage": "22.0f",
    "CannonMagazineSize": "30",
    "CannonReserve": "300",
    "CannonReloadSeconds": "1.7f",
    "CannonTraceRange": "32000.f",
}
ROCKET_FEEL = {
    "RocketSalvoSeconds": "1.65f",
    "RocketDamage": "85.0f",
    "RocketsPerSalvo": "5",
    "RocketMagazineSize": "14",
    "RocketReserve": "24",
    "RocketReloadSeconds": "2.3f",
}
GUIDED_FEEL = {
    "GuidedLockSeconds": "1.80f",
    "GuidedLockConeDegrees": "6.0f",
    "GuidedMinRange": "350.f",
    "GuidedMaxRange": "18000.f",
    "GuidedDamage": "240.0f",
    "GuidedMagazineSize": "2",
    "GuidedReserve": "6",
    "GuidedReloadSeconds": "2.8f",
}


def text(name: str) -> str:
    return (SOURCE / name).read_text(encoding="utf-8-sig")


def between(source: str, start: str, end: str) -> str:
    begin = source.index(start)
    finish = source.index(end, begin)
    return source[begin:finish]


def feel_constants(header: str) -> dict[str, str]:
    block = between(header, "namespace SkyguardApacheCpgFeel", "\n}")
    return dict(
        re.findall(
            r"constexpr\s+(?:float|int32)\s+(\w+)\s*=\s*([^;]+);",
            block,
        )
    )


def enum_enumerators(header: str, enum_name: str) -> list[str]:
    start = header.index(f"enum class {enum_name}")
    brace = header.index("{", start)
    finish = header.index("}", brace)
    return re.findall(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\b", header[brace:finish], re.M)


class ApacheCpgFeelContractTests(unittest.TestCase):
    def test_namespace_exists(self) -> None:
        header = text(HEADER_NAME)
        self.assertIn("namespace SkyguardApacheCpgFeel", header)
        self.assertIn("{", between(header, "namespace SkyguardApacheCpgFeel", "\n}"))

    def test_cannon_feel_constants(self) -> None:
        constants = feel_constants(text(HEADER_NAME))
        for name, value in CANNON_FEEL.items():
            self.assertEqual(constants.get(name), value, name)

    def test_rocket_feel_constants(self) -> None:
        constants = feel_constants(text(HEADER_NAME))
        for name, value in ROCKET_FEEL.items():
            self.assertEqual(constants.get(name), value, name)

    def test_guided_feel_constants(self) -> None:
        constants = feel_constants(text(HEADER_NAME))
        for name, value in GUIDED_FEEL.items():
            self.assertEqual(constants.get(name), value, name)

    def test_gunship_weapon_enumerates_three_stations_only(self) -> None:
        header = text(HEADER_NAME)
        self.assertIn("enum class ESkyguardGunshipWeapon", header)
        enumerators = enum_enumerators(header, "ESkyguardGunshipWeapon")
        self.assertEqual(enumerators, ["Cannon", "Rockets", "GuidedMissile"])
        self.assertNotIn("Igla", enumerators)

    def test_cpg_sight_mode_is_helmet_and_targeting_sensor(self) -> None:
        header = text(HEADER_NAME)
        self.assertIn("enum class ESkyguardCpgSightMode", header)
        self.assertEqual(
            enum_enumerators(header, "ESkyguardCpgSightMode"),
            ["Helmet", "TargetingSensor"],
        )

    def test_loadout_enumerates_playstyle_kits(self) -> None:
        header = text(HEADER_NAME)
        self.assertIn("enum class ESkyguardLoadout", header)
        self.assertEqual(
            enum_enumerators(header, "ESkyguardLoadout"),
            ["Balanced", "AntiArmor", "RocketHeavy", "Intercept"],
        )

    def test_header_comment_keeps_igla_off_the_player_station(self) -> None:
        header = text(HEADER_NAME)
        self.assertIn("Igla is not a player weapon", header)

    def test_locked_files_were_not_the_edit_surface(self) -> None:
        existing = [
            f"Source/Skyguard52/{name}"
            for name in LOCKED
            if (SOURCE / name).exists()
        ]
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
