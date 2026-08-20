from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
TYPES_H = "SkyguardAudioTypes.h"
DIRECTOR_H = "SkyguardAudioDirectorComponent.h"
DIRECTOR_CPP = "SkyguardAudioDirectorComponent.cpp"
LOCKED = {
    "SkyguardAudioTypes.h",
    "SkyguardAudioDirectorComponent.h",
    "SkyguardAudioDirectorComponent.cpp",
    "SkyguardAudioDirectorTests.cpp",
    "SkyguardAudioDirectorSuppressionFailClosedTests.cpp",
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
PERSPECTIVES = ["RearCockpit", "Exterior"]


def origin_main(name: str) -> str:
    result = subprocess.run(
        ["git", "show", f"origin/main:Source/Skyguard52/{name}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def between(source: str, start: str, end: str) -> str:
    begin = source.index(start)
    finish = source.index(end, begin)
    return source[begin:finish]


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


def function_body(source: str, signature: str) -> str:
    start = source.index(signature)
    brace = source.index("{", start)
    depth = 0
    for index, char in enumerate(source[brace:], brace):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[brace : index + 1]
    raise AssertionError(f"unclosed function {signature}")


class AudioListenerPerspectiveContractTests(unittest.TestCase):
    def test_listener_perspective_enum_is_rear_cockpit_and_exterior(self) -> None:
        header = origin_main(TYPES_H)
        self.assertIn(
            "enum class ESkyguardListenerPerspective : uint8",
            header,
        )
        self.assertEqual(
            enum_enumerators(header, "ESkyguardListenerPerspective"),
            PERSPECTIVES,
        )
        body = enum_body(header, "ESkyguardListenerPerspective")
        self.assertIn("RearCockpit", body)
        self.assertIn("Exterior", body)

    def test_director_defaults_to_rear_cockpit(self) -> None:
        header = origin_main(DIRECTOR_H)
        self.assertIn(
            "ESkyguardListenerPerspective ListenerPerspective = "
            "ESkyguardListenerPerspective::RearCockpit",
            header,
        )

    def test_set_listener_perspective_is_declared(self) -> None:
        header = origin_main(DIRECTOR_H)
        self.assertIn(
            "void SetListenerPerspective(ESkyguardListenerPerspective NewPerspective)",
            header,
        )

    def test_set_listener_perspective_assigns_then_applies_mix(self) -> None:
        impl = origin_main(DIRECTOR_CPP)
        self.assertIn(
            "void USkyguardAudioDirectorComponent::SetListenerPerspective",
            impl,
        )
        body = function_body(
            impl,
            "void USkyguardAudioDirectorComponent::SetListenerPerspective",
        )
        assign = body.index("ListenerPerspective = NewPerspective;")
        apply_mix = body.index("ApplyListenerSoundMix();")
        update_loop = body.index("UpdateLoopMix();")
        self.assertLess(assign, apply_mix)
        self.assertLess(apply_mix, update_loop)

    def test_apply_listener_sound_mix_returns_without_production_bank(self) -> None:
        impl = origin_main(DIRECTOR_CPP)
        body = function_body(
            impl,
            "void USkyguardAudioDirectorComponent::ApplyListenerSoundMix",
        )
        self.assertRegex(body, r"\{\s*if\s*\(\s*!ProductionBank\s*\)")
        bank_guard = body.index("if (!ProductionBank)")
        early_return = body.index("return;")
        push_mix = body.index("PushSoundMixModifier")
        self.assertLess(bank_guard, early_return)
        self.assertLess(early_return, push_mix)

    def test_listener_perspective_enum_bans_igla_yak_rifle(self) -> None:
        header = origin_main(TYPES_H)
        lowered = enum_body(header, "ESkyguardListenerPerspective").lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"ESkyguardListenerPerspective contains {banned}",
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
