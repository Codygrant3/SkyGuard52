from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
THREAT_TYPES = "SkyguardThreatTypes.h"
ROSTER_HEADER = "SkyguardCampaignRoster.h"
LOCKED = {
    "SkyguardThreatTypes.h",
    "SkyguardCampaignRoster.h",
    "SkyguardCampaignRoster.cpp",
    "SkyguardDrone.h",
    "SkyguardDrone.cpp",
    "SkyguardDroneThreatKindTests.cpp",
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
    "SkyguardCampaignDefinitionTests.cpp",
    "SkyguardCampaignSubsystemTests.cpp",
    "SkyguardMissionDefinitionTests.cpp",
    "SkyguardCampaignRosterLookupTests.cpp",
    "SkyguardSortiePresentationFailClosedTests.cpp",
    "SkyguardApacheChinMuzzleTests.cpp",
    "SkyguardGunshipTypesLoadoutTests.cpp",
    "SkyguardMissionDirectorPresentationHelpersTests.cpp",
    "SkyguardAudioAcceptanceHarnessFailClosedTests.cpp",
    "SkyguardPilotVoiceDurationTests.cpp",
    "SkyguardObjectiveRuntimeFailClosedTests.cpp",
    "SkyguardRadioChatterEmptyLineTests.cpp",
    "SkyguardRouteRuntimeFailClosedTests.cpp",
    "SkyguardPauseHostFailClosedTests.cpp",
}

THREAT_KINDS = [
    ("FastAttacker", "Fast Attacker"),
    ("HeavyAttacker", "Heavy Attacker"),
    ("RotorScout", "Rotor Scout"),
    ("GroundArmor", "Ground Armor"),
    ("FastBoat", "Fast Boat"),
]
MISSION_SPEC_DEFAULTS = {
    "ContactKind": "FastAttacker",
    "ShoreKind": "GroundArmor",
    "SupportKind": "HeavyAttacker",
    "ExtractKind": "RotorScout",
}
BANNED = ("igla", "yak", "rifle")


def text(name: str) -> str:
    return (SOURCE / name).read_text(encoding="utf-8-sig")


def between(source: str, start: str, end: str) -> str:
    begin = source.index(start)
    finish = source.index(end, begin)
    return source[begin:finish]


def enum_enumerators(header: str, enum_name: str) -> list[str]:
    start = header.index(f"enum class {enum_name}")
    brace = header.index("{", start)
    finish = header.index("}", brace)
    return re.findall(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\b", header[brace:finish], re.M)


def threat_kind_display_names(header: str) -> list[tuple[str, str]]:
    block = between(header, "enum class ESkyguardThreatKind", "}")
    return re.findall(
        r"([A-Za-z_][A-Za-z0-9_]*)\s+UMETA\(\s*DisplayName\s*=\s*\"([^\"]+)\"\s*\)",
        block,
    )


def mission_spec_kind_defaults(header: str) -> dict[str, str]:
    block = between(
        header,
        "struct FSkyguardCampaignMissionSpec",
        "ESkyguardClimaxKind Climax",
    )
    return dict(
        re.findall(
            r"ESkyguardThreatKind\s+(\w+)\s*=\s*ESkyguardThreatKind::(\w+);",
            block,
        )
    )


class ThreatKindRosterContractTests(unittest.TestCase):
    def test_threat_kind_enum_exists(self) -> None:
        header = text(THREAT_TYPES)
        self.assertIn("enum class ESkyguardThreatKind", header)
        self.assertIn("UENUM(BlueprintType)", header)

    def test_threat_kind_enumerators_and_display_names_in_order(self) -> None:
        header = text(THREAT_TYPES)
        enumerators = enum_enumerators(header, "ESkyguardThreatKind")
        self.assertEqual(enumerators, [name for name, _ in THREAT_KINDS])
        self.assertEqual(threat_kind_display_names(header), THREAT_KINDS)

    def test_enum_has_all_five_kinds_not_fast_attacker_only(self) -> None:
        enumerators = enum_enumerators(text(THREAT_TYPES), "ESkyguardThreatKind")
        self.assertEqual(len(enumerators), 5, enumerators)
        self.assertNotEqual(enumerators, ["FastAttacker"])
        for name, _ in THREAT_KINDS:
            self.assertIn(name, enumerators)
        self.assertIn("FastAttacker", enumerators)
        self.assertIn("HeavyAttacker", enumerators)
        self.assertIn("RotorScout", enumerators)
        self.assertIn("GroundArmor", enumerators)
        self.assertIn("FastBoat", enumerators)

    def test_header_comment_keeps_shahed_as_one_option(self) -> None:
        header = text(THREAT_TYPES)
        self.assertIn(
            "Shahed-style fast attackers are one option, not the",
            header,
        )
        self.assertIn("whole campaign", header)
        self.assertIn("Live threat roster", header)

    def test_mission_spec_kind_defaults(self) -> None:
        header = text(ROSTER_HEADER)
        self.assertIn("struct FSkyguardCampaignMissionSpec", header)
        defaults = mission_spec_kind_defaults(header)
        self.assertEqual(defaults, MISSION_SPEC_DEFAULTS)
        self.assertEqual(defaults.get("ContactKind"), "FastAttacker")
        self.assertEqual(defaults.get("ShoreKind"), "GroundArmor")
        self.assertEqual(defaults.get("SupportKind"), "HeavyAttacker")
        self.assertEqual(defaults.get("ExtractKind"), "RotorScout")

    def test_threat_types_ban_igla_yak_rifle(self) -> None:
        lowered = text(THREAT_TYPES).lower()
        for banned in BANNED:
            self.assertNotIn(banned, lowered, f"{THREAT_TYPES} contains {banned}")

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
