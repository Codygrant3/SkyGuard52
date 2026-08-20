from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_NAME = "SkyguardApacheAircraft.h"
LOCKED = {
    "SkyguardApacheAircraft.h",
    "SkyguardApacheAircraft.cpp",
    "SkyguardApacheAircraftTests.cpp",
    "SkyguardApacheOwnShipSystemHitTests.cpp",
    "SkyguardApacheLiveSystemTests.cpp",
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
BANNED = ("igla", "yak", "rifle")
OWN_SHIP_SYSTEMS = [
    ("Sensor", "TADS"),
    ("Canopy", "Canopy"),
    ("Engines", "Engines"),
    ("ChinTurret", "Chin turret"),
    ("Rotor", "Main rotor"),
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


def system_display_names(header: str) -> list[tuple[str, str]]:
    return re.findall(
        r"([A-Za-z_][A-Za-z0-9_]*)\s+UMETA\(\s*DisplayName\s*=\s*\"([^\"]+)\"\s*\)",
        enum_body(header, "ESkyguardApacheSystem"),
    )


class ApacheOwnShipSystemsContractTests(unittest.TestCase):
    def test_own_ship_system_enum_exists(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn("enum class ESkyguardApacheSystem : uint8", header)
        self.assertIn("UENUM(BlueprintType)", header)

    def test_enumerators_match_live_named_system_set_in_order(self) -> None:
        header = origin_main(HEADER_NAME)
        enumerators = enum_enumerators(header, "ESkyguardApacheSystem")
        self.assertEqual(
            enumerators,
            [name for name, _ in OWN_SHIP_SYSTEMS],
        )
        self.assertEqual(enumerators, [
            "Sensor",
            "Canopy",
            "Engines",
            "ChinTurret",
            "Rotor",
        ])
        self.assertEqual(len(enumerators), 5, enumerators)
        self.assertEqual(system_display_names(header), OWN_SHIP_SYSTEMS)
        body = enum_body(header, "ESkyguardApacheSystem")
        self.assertIn('Sensor UMETA(DisplayName = "TADS")', body)

    def test_header_describes_own_ship_named_system_hits_not_a_hull_bar(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn(
            "Own-ship systems that change Play. Not a second hull bar.",
            header,
        )
        self.assertIn(
            "Named-system hit. Does not move the hull integrity bar.",
            header,
        )
        self.assertIn(
            "void ApplySystemHit(ESkyguardApacheSystem System, float Amount);",
            header,
        )
        self.assertIn("Not a hull-bar query.", header)

    def test_enum_does_not_require_rifle_or_igla(self) -> None:
        enumerators = enum_enumerators(
            origin_main(HEADER_NAME),
            "ESkyguardApacheSystem",
        )
        self.assertNotIn("Rifle", enumerators)
        self.assertNotIn("Igla", enumerators)
        self.assertNotIn("Yak", enumerators)

    def test_own_ship_system_enum_bans_igla_yak_rifle(self) -> None:
        lowered = enum_body(
            origin_main(HEADER_NAME),
            "ESkyguardApacheSystem",
        ).lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"ESkyguardApacheSystem contains {banned}",
            )

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
