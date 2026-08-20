from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
VOICE_CPP = "SkyguardPilotVoice.cpp"
TYPES_H = "SkyguardBossTypes.h"
LOCKED = {
    "SkyguardPilotVoice.cpp",
    "SkyguardPilotVoice.h",
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
    "SkyguardObjectiveRuntimeFailClosedTests.cpp",
}

CONFIRM_LINES = {
    "OrbitLeft": "Coming left. Holding the circle.",
    "OrbitRight": "Coming right. Holding the circle.",
    "AttackRun": "Rolling in.",
    "Break": "Breaking off.",
    "Extend": "Opening the range.",
    "Hold": "Holding station.",
    "Climb": "Popping up.",
    "Descend": "Dropping behind cover.",
    "FaceTarget": "Coming onto your target.",
    "Pursuit": "Staying in the fight.",
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


def confirm_line_body(impl: str) -> str:
    return between(
        impl,
        "FString SkyguardPilotVoice::ConfirmLineForCommand",
        "void SkyguardPilotVoice::ConfirmCommand",
    )


def mapped_confirm_lines(block: str) -> dict[str, str]:
    mapping: dict[str, str] = {}
    pending: list[str] = []
    for raw in block.splitlines():
        line = raw.strip()
        case_match = re.match(r"case\s+ESkyguardPilotCommand::(\w+):", line)
        if case_match:
            pending.append(case_match.group(1))
            continue
        if line.startswith("default:"):
            pending.append("default")
            continue
        text_match = re.search(r'return\s+TEXT\("([^"]+)"\)', line)
        if text_match:
            for name in pending:
                mapping[name] = text_match.group(1)
            pending.clear()
    return mapping


class PilotConfirmLineContractTests(unittest.TestCase):
    def test_confirm_line_for_command_exists(self) -> None:
        header = text("SkyguardPilotVoice.h")
        impl = text(VOICE_CPP)
        self.assertIn(
            "FString ConfirmLineForCommand(ESkyguardPilotCommand Command);",
            header,
        )
        self.assertIn("FString SkyguardPilotVoice::ConfirmLineForCommand", impl)
        self.assertIn("switch (Command)", confirm_line_body(impl))

    def test_confirm_line_for_command_maps_each_enumerator(self) -> None:
        mapping = mapped_confirm_lines(confirm_line_body(text(VOICE_CPP)))
        expected = dict(CONFIRM_LINES)
        expected["default"] = CONFIRM_LINES["Pursuit"]
        self.assertEqual(mapping, expected)

    def test_pilot_command_enumerators_exist(self) -> None:
        enumerators = enum_enumerators(text(TYPES_H), "ESkyguardPilotCommand")
        self.assertIn("enum class ESkyguardPilotCommand", text(TYPES_H))
        for name in CONFIRM_LINES:
            self.assertIn(name, enumerators)

    def test_pursuit_and_default_share_the_stay_in_the_fight_line(self) -> None:
        body = confirm_line_body(text(VOICE_CPP))
        self.assertIn("case ESkyguardPilotCommand::Pursuit:", body)
        self.assertIn("default:", body)
        mapping = mapped_confirm_lines(body)
        self.assertEqual(mapping["Pursuit"], "Staying in the fight.")
        self.assertEqual(mapping["default"], "Staying in the fight.")
        pursuit = body.index("case ESkyguardPilotCommand::Pursuit:")
        default = body.index("default:")
        stay = body.index('return TEXT("Staying in the fight.")')
        self.assertLess(pursuit, default)
        self.assertLess(default, stay)

    def test_confirm_lines_ban_igla_yak_rifle(self) -> None:
        mapping = mapped_confirm_lines(confirm_line_body(text(VOICE_CPP)))
        self.assertTrue(mapping)
        for command, line in mapping.items():
            lowered = line.lower()
            for banned in BANNED:
                self.assertNotIn(banned, lowered, f"{command}: {line}")

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
