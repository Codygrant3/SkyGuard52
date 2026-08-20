from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_NAME = "SkyguardAudioTypes.h"
LOCKED = {
    "SkyguardAudioTypes.h",
    "SkyguardAudioDirectorComponent.h",
    "SkyguardAudioDirectorComponent.cpp",
    "SkyguardAudioDirectorTests.cpp",
    "SkyguardAudioDirectorTelemetryFailClosedTests.cpp",
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
    "int32 RequestedEvents = 0;",
    "int32 PlayedEvents = 0;",
    "int32 RejectedByCooldown = 0;",
    "int32 RejectedByConcurrency = 0;",
    "int32 RejectedMissingAsset = 0;",
    "int32 PriorityEvictions = 0;",
    "int32 PeakActiveVoices = 0;",
)
IN_CLASS_DEFAULTS = {
    "RequestedEvents": "0",
    "PlayedEvents": "0",
    "RejectedByCooldown": "0",
    "RejectedByConcurrency": "0",
    "RejectedMissingAsset": "0",
    "PriorityEvictions": "0",
    "PeakActiveVoices": "0",
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


def telemetry_body(header: str) -> str:
    start = header.index("struct FSkyguardAudioTelemetry")
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


class AudioTelemetryDefaultsContractTests(unittest.TestCase):
    def test_telemetry_struct_exists(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn("struct FSkyguardAudioTelemetry", header)
        self.assertIn("USTRUCT(BlueprintType)", header)
        self.assertIn("GENERATED_BODY()", telemetry_body(header))

    def test_public_fields_match_origin_main_in_order(self) -> None:
        body = telemetry_body(origin_main(HEADER_NAME))
        positions = [body.index(field) for field in PUBLIC_FIELDS]
        self.assertEqual(positions, sorted(positions), PUBLIC_FIELDS)
        for field in PUBLIC_FIELDS:
            self.assertIn(field, body)
            self.assertIn("UPROPERTY(BlueprintReadOnly)", body)

    def test_in_class_defaults_match_origin_main(self) -> None:
        body = telemetry_body(origin_main(HEADER_NAME))
        self.assertEqual(in_class_defaults(body), IN_CLASS_DEFAULTS)
        self.assertIn("int32 RequestedEvents = 0;", body)
        self.assertIn("int32 PlayedEvents = 0;", body)
        self.assertIn("int32 RejectedByCooldown = 0;", body)
        self.assertIn("int32 RejectedByConcurrency = 0;", body)
        self.assertIn("int32 RejectedMissingAsset = 0;", body)
        self.assertIn("int32 PriorityEvictions = 0;", body)
        self.assertIn("int32 PeakActiveVoices = 0;", body)

    def test_struct_does_not_invent_index_none(self) -> None:
        body = telemetry_body(origin_main(HEADER_NAME))
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("= INDEX_NONE", body)

    def test_contract_does_not_lock_audio_event_enum(self) -> None:
        body = telemetry_body(origin_main(HEADER_NAME))
        self.assertNotIn("enum class ESkyguardAudioEvent", body)
        self.assertNotIn("ESkyguardAudioEvent", body)

    def test_struct_bans_igla_yak_rifle(self) -> None:
        lowered = telemetry_body(origin_main(HEADER_NAME)).lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"FSkyguardAudioTelemetry contains {banned}",
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
