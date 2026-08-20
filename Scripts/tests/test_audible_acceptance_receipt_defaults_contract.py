from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_NAME = "SkyguardAudioAcceptanceHarness.h"
LOCKED = {
    "SkyguardAudioAcceptanceHarness.h",
    "SkyguardAudioAcceptanceHarness.cpp",
    "SkyguardAudioAcceptanceHarnessFailClosedTests.cpp",
    "SkyguardAudioProductionBankTests.cpp",
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
LOCKED_SCRIPTS = (
    "Scripts/tests/test_audio_telemetry_defaults_contract.py",
    "Scripts/tests/test_how_to_fly_row_defaults_contract.py",
    "Scripts/tests/test_briefing_radio_row_defaults_contract.py",
    "Scripts/tests/test_route_definition_defaults_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_contract.py",
)
PUBLIC_FIELDS = (
    "FString BuildSha256;",
    "FString EvidenceSha256;",
    "int32 SampleCount = 0;",
    "int32 PeakActiveVoices = 0;",
    "int32 TotalUnderruns = 0;",
    "float MaximumAudioThreadMs = 0.f;",
    "float MaximumTruePeakDbTP = -120.f;",
    "bool bPackagedDevelopmentBuild = false;",
    "bool bAudibleDeviceObserved = false;",
    "bool bCalibratedMetering = false;",
    "bool bProductionBankReady = false;",
    "bool bAccepted = false;",
)
IN_CLASS_DEFAULTS = {
    "SampleCount": "0",
    "PeakActiveVoices": "0",
    "TotalUnderruns": "0",
    "MaximumAudioThreadMs": "0.f",
    "MaximumTruePeakDbTP": "-120.f",
    "bPackagedDevelopmentBuild": "false",
    "bAudibleDeviceObserved": "false",
    "bCalibratedMetering": "false",
    "bProductionBankReady": "false",
    "bAccepted": "false",
}
STRING_FIELDS_WITHOUT_DEFAULTS = (
    "BuildSha256",
    "EvidenceSha256",
)
HARNESS_FAIL_CLOSED_OWNED_BY_116 = (
    "BeginEvidenceRun",
    "RecordMeasuredSample",
    "CompleteEvidenceRun",
    "IsSha256",
    "MinimumMeasuredSamples",
    "MaximumAllowedVoices",
)
BANNED = ("igla", "yak", "rifle")
HARBOR_TUNING = ("40.f", "80.f")


def origin_main(name: str) -> str:
    result = subprocess.run(
        ["git", "show", f"origin/main:Source/Skyguard52/{name}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def receipt_body(header: str) -> str:
    start = header.index("struct FSkyguardAudibleAcceptanceReceipt")
    brace = header.index("{", start)
    finish = header.index("};", brace)
    return header[brace : finish + 2]


def in_class_defaults(body: str) -> dict[str, str]:
    return dict(
        re.findall(
            r"(?:bool|int32|float)\s+(\w+)\s*=\s*([^;]+);",
            body,
        )
    )


class AudibleAcceptanceReceiptDefaultsContractTests(unittest.TestCase):
    def test_receipt_struct_exists(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn("struct FSkyguardAudibleAcceptanceReceipt", header)
        self.assertIn("USTRUCT(BlueprintType)", header)
        self.assertIn("GENERATED_BODY()", receipt_body(header))

    def test_public_fields_match_origin_main_in_order(self) -> None:
        body = receipt_body(origin_main(HEADER_NAME))
        positions = [body.index(field) for field in PUBLIC_FIELDS]
        self.assertEqual(positions, sorted(positions), PUBLIC_FIELDS)
        for field in PUBLIC_FIELDS:
            self.assertIn(field, body)
        self.assertEqual(body.count("UPROPERTY("), 12)
        self.assertEqual(body.count("BlueprintReadOnly"), 12)
        self.assertIn("FString BuildSha256;", body)
        self.assertIn("FString EvidenceSha256;", body)

    def test_in_class_defaults_match_origin_main(self) -> None:
        body = receipt_body(origin_main(HEADER_NAME))
        self.assertEqual(in_class_defaults(body), IN_CLASS_DEFAULTS)
        self.assertIn("int32 SampleCount = 0;", body)
        self.assertIn("int32 PeakActiveVoices = 0;", body)
        self.assertIn("int32 TotalUnderruns = 0;", body)
        self.assertIn("float MaximumAudioThreadMs = 0.f;", body)
        self.assertIn("float MaximumTruePeakDbTP = -120.f;", body)
        self.assertIn("bool bPackagedDevelopmentBuild = false;", body)
        self.assertIn("bool bAudibleDeviceObserved = false;", body)
        self.assertIn("bool bCalibratedMetering = false;", body)
        self.assertIn("bool bProductionBankReady = false;", body)
        self.assertIn("bool bAccepted = false;", body)

    def test_struct_does_not_invent_string_defaults_or_index_none(self) -> None:
        body = receipt_body(origin_main(HEADER_NAME))
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("NAME_None", body)
        self.assertNotIn("= INDEX_NONE", body)
        self.assertNotIn("= NAME_None", body)
        for name in STRING_FIELDS_WITHOUT_DEFAULTS:
            self.assertIn(f"FString {name};", body)
            self.assertNotIn(f"{name} =", body)
            self.assertNotIn(name, in_class_defaults(body))
        self.assertNotIn('TEXT("")', body)
        self.assertNotIn('= ""', body)
        self.assertNotIn("FString BuildSha256 =", body)
        self.assertNotIn("FString EvidenceSha256 =", body)

    def test_contract_does_not_re_lock_harness_fail_closed(self) -> None:
        body = receipt_body(origin_main(HEADER_NAME))
        for name in HARNESS_FAIL_CLOSED_OWNED_BY_116:
            self.assertNotIn(name, body)
        self.assertNotIn("USkyguardAudioAcceptanceHarness", body)
        self.assertNotIn("UCLASS", body)
        self.assertNotIn("MinimumMeasuredSamples = 600", body)
        self.assertNotIn("MaximumAllowedVoices = 48", body)
        self.assertNotIn("MaximumAudioThreadMs = 2.f", body)
        self.assertNotIn("MaximumTruePeakDbTP = -1.f", body)
        self.assertNotIn("2.5", body)
        self.assertNotIn("NewObject", body)
        defaults = in_class_defaults(body)
        self.assertNotEqual(defaults.get("MaximumAudioThreadMs"), "2.f")
        self.assertNotEqual(defaults.get("MaximumTruePeakDbTP"), "-1.f")

    def test_struct_does_not_re_lock_harbor(self) -> None:
        body = receipt_body(origin_main(HEADER_NAME))
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)

    def test_struct_bans_igla_yak_rifle(self) -> None:
        lowered = receipt_body(origin_main(HEADER_NAME)).lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"FSkyguardAudibleAcceptanceReceipt contains {banned}",
            )

    def test_locked_files_were_not_the_edit_surface(self) -> None:
        existing = [
            f"Source/Skyguard52/{name}"
            for name in LOCKED
            if (SOURCE / name).exists()
        ]
        for sibling in LOCKED_SCRIPTS:
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
