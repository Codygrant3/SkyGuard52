from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardMission01LandscapeGroundingLibrary.h"
LOCKED = {
    "SkyguardMission01LandscapeGroundingLibrary.h",
    "SkyguardMission01LandscapeGroundingLibrary.cpp",
    "SkyguardMission01LandscapeGroundingTests.cpp",
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
    "Scripts/tests/test_storm_rain_beat_kit_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
    "Scripts/tests/test_phase4_m01_landscape_repair_contract.py",
    "Scripts/tests/test_landscape_footprint_sample_defaults_contract.py",
    "Scripts/tests/test_production_audio_entry_defaults_contract.py",
    "Scripts/tests/test_production_audio_routing_defaults_contract.py",
    "Scripts/tests/test_production_audio_audit_defaults_contract.py",
)
PUBLIC_FIELDS = (
    "bool bValid = false;",
    "FVector QueryLocation = FVector::ZeroVector;",
    "float HeightCentimeters = 0.f;",
    "FString HeightfieldSource;",
    "FString Error;",
)
IN_CLASS_DEFAULTS = {
    "bValid": "false",
    "QueryLocation": "FVector::ZeroVector",
    "HeightCentimeters": "0.f",
}
PRESENCE_ONLY_FIELDS = (
    "FString HeightfieldSource;",
    "FString Error;",
)
# FSkyguardLandscapeFootprintSampleResult stays on a sibling or later worker.
FOOTPRINT_FIELDS_NOT_LOCKED = (
    "struct FSkyguardLandscapeFootprintSampleResult",
    "bool bSuccess = false;",
    "int32 RequiredSampleCount = 0;",
    "int32 ValidSampleCount = 0;",
    "float SupportedFraction = 0.f;",
    "float MinimumHeightCentimeters = 0.f;",
    "float MaximumHeightCentimeters = 0.f;",
    "float MeanHeightCentimeters = 0.f;",
    "float HeightDeltaCentimeters = 0.f;",
    "TArray<FSkyguardLandscapeHeightSample> Samples;",
)
LIBRARY_SYMBOLS_NOT_LOCKED = (
    "SampleLandscapeHeight",
    "SampleLandscapeFootprint",
    "USkyguardMission01LandscapeGroundingLibrary",
    "UCLASS()",
    "UFUNCTION(",
)
INVENTED_DEFAULTS = (
    "NAME_None",
    "INDEX_NONE",
    "HeightfieldSource =",
    "Error =",
    "TEXT(",
    "FString()",
    'TEXT("")',
)
BANNED = ("igla", "yak", "rifle")
HARBOR_TUNING = ("40.f", "80.f")


def origin_main_header() -> str:
    result = subprocess.run(
        ["git", "show", f"origin/main:{HEADER_PATH}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def height_sample_body(header: str) -> str:
    start = header.index("struct FSkyguardLandscapeHeightSample")
    brace = header.index("{", start)
    finish = header.index("};", brace)
    return header[brace : finish + 2]


def in_class_defaults(body: str) -> dict[str, str]:
    return {
        name: re.sub(r"\s+", " ", value).strip()
        for name, value in re.findall(
            r"(?:bool|FVector|float)\s+(\w+)\s*=\s*([^;]+);",
            body,
        )
    }


class LandscapeHeightSampleDefaultsContractTests(unittest.TestCase):
    def test_height_sample_struct_exists(self) -> None:
        header = origin_main_header()
        self.assertIn("struct FSkyguardLandscapeHeightSample", header)
        self.assertIn("USTRUCT(BlueprintType)", header)
        self.assertIn("GENERATED_BODY()", height_sample_body(header))

    def test_public_fields_match_origin_main_in_order(self) -> None:
        body = height_sample_body(origin_main_header())
        positions = [body.index(field) for field in PUBLIC_FIELDS]
        self.assertEqual(positions, sorted(positions), PUBLIC_FIELDS)
        for field in PUBLIC_FIELDS:
            self.assertIn(field, body)
        self.assertEqual(body.count("UPROPERTY("), 5)
        self.assertEqual(
            body.count("UPROPERTY(VisibleAnywhere, BlueprintReadOnly)"),
            5,
        )

    def test_in_class_defaults_match_origin_main(self) -> None:
        body = height_sample_body(origin_main_header())
        self.assertEqual(in_class_defaults(body), IN_CLASS_DEFAULTS)
        self.assertIn("bool bValid = false;", body)
        self.assertIn("FVector QueryLocation = FVector::ZeroVector;", body)
        self.assertIn("float HeightCentimeters = 0.f;", body)
        self.assertNotIn("bValid = true", body)
        self.assertNotIn("HeightCentimeters = 0.0f", body)

    def test_string_fields_are_presence_only(self) -> None:
        body = height_sample_body(origin_main_header())
        for field in PRESENCE_ONLY_FIELDS:
            self.assertIn(field, body)
        self.assertNotIn("HeightfieldSource =", body)
        self.assertNotIn("Error =", body)
        self.assertNotIn("TEXT(", body)
        self.assertNotIn("FString()", body)
        defaults = in_class_defaults(body)
        self.assertNotIn("HeightfieldSource", defaults)
        self.assertNotIn("Error", defaults)
        string_defaults = dict(
            re.findall(r"FString\s+(\w+)\s*=\s*([^;]+);", body)
        )
        self.assertEqual(string_defaults, {})

    def test_struct_does_not_invent_index_none_or_name_none(self) -> None:
        body = height_sample_body(origin_main_header())
        for token in INVENTED_DEFAULTS:
            self.assertNotIn(token, body)
        self.assertNotIn("= INDEX_NONE", body)
        self.assertNotIn("= NAME_None", body)

    def test_contract_does_not_lock_footprint_sample_result(self) -> None:
        body = height_sample_body(origin_main_header())
        for field in FOOTPRINT_FIELDS_NOT_LOCKED:
            self.assertNotIn(field, body)
        for symbol in LIBRARY_SYMBOLS_NOT_LOCKED:
            self.assertNotIn(symbol, body)
        self.assertNotIn("int32", body)
        self.assertNotIn("TArray<", body)

    def test_contract_does_not_retune_harbor(self) -> None:
        body = height_sample_body(origin_main_header())
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        self.assertNotIn("40.f, 80.f", body)

    def test_struct_bans_igla_yak_rifle(self) -> None:
        lowered = height_sample_body(origin_main_header()).lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"FSkyguardLandscapeHeightSample contains {banned}",
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
