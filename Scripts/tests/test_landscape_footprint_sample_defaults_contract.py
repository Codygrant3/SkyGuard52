from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_NAME = "SkyguardMission01LandscapeGroundingLibrary.h"
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
    "Scripts/tests/test_landscape_height_sample_defaults_contract.py",
    "Scripts/tests/test_mission_map_readiness_defaults_contract.py",
)
PUBLIC_FIELDS = (
    "bool bSuccess = false;",
    "int32 RequiredSampleCount = 0;",
    "int32 ValidSampleCount = 0;",
    "float SupportedFraction = 0.f;",
    "float MinimumHeightCentimeters = 0.f;",
    "float MaximumHeightCentimeters = 0.f;",
    "float MeanHeightCentimeters = 0.f;",
    "float HeightDeltaCentimeters = 0.f;",
    "TArray<FSkyguardLandscapeHeightSample> Samples;",
    "FString Error;",
)
IN_CLASS_DEFAULTS = {
    "bSuccess": "false",
    "RequiredSampleCount": "0",
    "ValidSampleCount": "0",
    "SupportedFraction": "0.f",
    "MinimumHeightCentimeters": "0.f",
    "MaximumHeightCentimeters": "0.f",
    "MeanHeightCentimeters": "0.f",
    "HeightDeltaCentimeters": "0.f",
}
PRESENCE_ONLY_FIELDS = (
    "TArray<FSkyguardLandscapeHeightSample> Samples;",
    "FString Error;",
)
# FSkyguardLandscapeHeightSample stays on its own isolated draft.
# This contract locks footprint-result fields only.
HEIGHT_SAMPLE_DEFAULTS = (
    "bool bValid = false;",
    "FVector QueryLocation = FVector::ZeroVector;",
    "float HeightCentimeters = 0.f;",
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


def footprint_body(header: str) -> str:
    start = header.index("struct FSkyguardLandscapeFootprintSampleResult")
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


class LandscapeFootprintSampleDefaultsContractTests(unittest.TestCase):
    def test_footprint_struct_exists(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn("struct FSkyguardLandscapeFootprintSampleResult", header)
        self.assertIn("USTRUCT(BlueprintType)", header)
        self.assertIn("GENERATED_BODY()", footprint_body(header))

    def test_public_fields_match_origin_main_in_order(self) -> None:
        body = footprint_body(origin_main(HEADER_NAME))
        positions = [body.index(field) for field in PUBLIC_FIELDS]
        self.assertEqual(positions, sorted(positions), PUBLIC_FIELDS)
        for field in PUBLIC_FIELDS:
            self.assertIn(field, body)
        self.assertEqual(body.count("UPROPERTY("), 10)
        self.assertEqual(
            body.count("UPROPERTY(VisibleAnywhere, BlueprintReadOnly)"),
            10,
        )
        for field in PRESENCE_ONLY_FIELDS:
            self.assertIn(field, body)

    def test_in_class_defaults_match_origin_main(self) -> None:
        body = footprint_body(origin_main(HEADER_NAME))
        defaults = in_class_defaults(body)
        self.assertEqual(defaults, IN_CLASS_DEFAULTS)
        self.assertEqual(defaults.get("bSuccess"), "false")
        self.assertEqual(defaults.get("RequiredSampleCount"), "0")
        self.assertEqual(defaults.get("ValidSampleCount"), "0")
        self.assertEqual(defaults.get("SupportedFraction"), "0.f")
        self.assertEqual(defaults.get("MinimumHeightCentimeters"), "0.f")
        self.assertEqual(defaults.get("MaximumHeightCentimeters"), "0.f")
        self.assertEqual(defaults.get("MeanHeightCentimeters"), "0.f")
        self.assertEqual(defaults.get("HeightDeltaCentimeters"), "0.f")
        self.assertIn("bool bSuccess = false;", body)
        self.assertIn("int32 RequiredSampleCount = 0;", body)
        self.assertIn("int32 ValidSampleCount = 0;", body)
        self.assertIn("float SupportedFraction = 0.f;", body)
        self.assertIn("float MinimumHeightCentimeters = 0.f;", body)
        self.assertIn("float MaximumHeightCentimeters = 0.f;", body)
        self.assertIn("float MeanHeightCentimeters = 0.f;", body)
        self.assertIn("float HeightDeltaCentimeters = 0.f;", body)
        self.assertNotIn("Samples", defaults)
        self.assertNotIn("Error", defaults)
        self.assertEqual(len(defaults), 8, defaults)

    def test_samples_and_error_presence_without_invented_defaults(self) -> None:
        body = footprint_body(origin_main(HEADER_NAME))
        self.assertIn("TArray<FSkyguardLandscapeHeightSample> Samples;", body)
        self.assertIn("FString Error;", body)
        self.assertNotIn("Samples =", body)
        self.assertNotIn("Error =", body)
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("NAME_None", body)
        self.assertNotIn("= INDEX_NONE", body)
        self.assertNotIn("= NAME_None", body)
        self.assertNotIn("= TEXT(", body)

    def test_struct_does_not_re_lock_height_sample_defaults_or_harbor(self) -> None:
        body = footprint_body(origin_main(HEADER_NAME))
        defaults = in_class_defaults(body)
        self.assertNotIn("struct FSkyguardLandscapeHeightSample", body)
        for field in HEIGHT_SAMPLE_DEFAULTS:
            self.assertNotIn(field, body)
        self.assertNotIn("bValid", defaults)
        self.assertNotIn("HeightCentimeters", defaults)
        self.assertNotIn("QueryLocation", defaults)
        self.assertNotIn("HeightfieldSource", body)
        self.assertNotIn("FVector::ZeroVector", body)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        self.assertNotIn("enum class", body)

    def test_struct_bans_igla_yak_rifle(self) -> None:
        lowered = footprint_body(origin_main(HEADER_NAME)).lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"FSkyguardLandscapeFootprintSampleResult contains {banned}",
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
