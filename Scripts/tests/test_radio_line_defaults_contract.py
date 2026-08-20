from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_NAME = "SkyguardRadioChatterComponent.h"
LOCKED = {
    "SkyguardRadioChatterComponent.h",
    "SkyguardRadioChatterComponent.cpp",
    "SkyguardRadioChatterTests.cpp",
    "SkyguardRadioChatterEmptyLineTests.cpp",
    "SkyguardRadioChatterEmptyQueueFailClosedTests.cpp",
    "SkyguardRadioChatterQueueBoundTests.cpp",
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
PUBLIC_FIELDS = (
    "FName LineId;",
    "FText Speaker;",
    "FText Subtitle;",
    "TSoftObjectPtr<USoundBase> Sound;",
    "int32 Priority = 50;",
    "float EstimatedDurationSeconds = 2.f;",
    "float CooldownSeconds = 0.f;",
)
IN_CLASS_DEFAULTS = {
    "Priority": "50",
    "EstimatedDurationSeconds": "2.f",
    "CooldownSeconds": "0.f",
}
BANNED = ("igla", "yak", "rifle")


def origin_main(name: str) -> str:
    result = subprocess.run(
        ["git", "show", f"origin/main:Source/Skyguard52/{name}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def radio_line_body(header: str) -> str:
    start = header.index("struct FSkyguardRadioLine")
    brace = header.index("{", start)
    finish = header.index("};", brace)
    return header[brace : finish + 2]


def in_class_defaults(body: str) -> dict[str, str]:
    return dict(
        re.findall(
            r"(?:int32|float)\s+(\w+)\s*=\s*([^;]+);",
            body,
        )
    )


class RadioLineDefaultsContractTests(unittest.TestCase):
    def test_radio_line_struct_exists(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn("struct FSkyguardRadioLine", header)
        self.assertIn("USTRUCT(BlueprintType)", header)
        self.assertIn("GENERATED_BODY()", radio_line_body(header))

    def test_public_fields_match_origin_main_in_order(self) -> None:
        body = radio_line_body(origin_main(HEADER_NAME))
        positions = [body.index(field) for field in PUBLIC_FIELDS]
        self.assertEqual(positions, sorted(positions), PUBLIC_FIELDS)
        for field in PUBLIC_FIELDS:
            self.assertIn(field, body)

    def test_in_class_defaults_match_origin_main(self) -> None:
        body = radio_line_body(origin_main(HEADER_NAME))
        self.assertEqual(in_class_defaults(body), IN_CLASS_DEFAULTS)
        self.assertIn("int32 Priority = 50;", body)
        self.assertIn("float EstimatedDurationSeconds = 2.f;", body)
        self.assertIn("float CooldownSeconds = 0.f;", body)

    def test_struct_does_not_invent_index_none(self) -> None:
        body = radio_line_body(origin_main(HEADER_NAME))
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("LineId =", body)

    def test_struct_bans_igla_yak_rifle(self) -> None:
        lowered = radio_line_body(origin_main(HEADER_NAME)).lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"FSkyguardRadioLine contains {banned}",
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
