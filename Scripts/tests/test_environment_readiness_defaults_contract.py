from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_NAME = "SkyguardCoastalEnvironmentDirector.h"
LOCKED = {
    "SkyguardCoastalEnvironmentDirector.h",
    "SkyguardCoastalEnvironmentDirector.cpp",
    "SkyguardCoastalEnvironmentDirectorEmptyFailClosedTests.cpp",
    "SkyguardCoastalEnvironmentDirectorTests.cpp",
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
SIBLING_CONTRACTS = (
    "Scripts/tests/test_environment_quality_enum_contract.py",
    "Scripts/tests/test_environment_vfx_type_enum_contract.py",
)
# In-class defaults on FSkyguardEnvironmentReadiness in origin/main.
# Do not invent INDEX_NONE; origin/main uses 0 for every field.
READINESS_DEFAULTS = {
    "BoundCapabilityCount": "0",
    "TreeInstanceCount": "0",
    "ShrubInstanceCount": "0",
    "VFXPoolSize": "0",
}
# Coastal-director numeric getter defaults belong to #156. Quality and VFX
# type enumerators belong to #160 and #167. Do not re-lock them here.
DIRECTOR_NUMERIC_DEFAULT_FIELDS = (
    "PlacementSeed",
    "EpicTreeBudget",
    "EpicShrubBudget",
    "RouteLengthCm",
    "RouteCorridorHalfWidthCm",
    "ShorelineLandOffsetCm",
    "InlandExtentCm",
    "VegetationStartCullDistanceCm",
    "VegetationEndCullDistanceCm",
    "WindStrength",
    "WindSpeed",
)


def origin_main(name: str) -> str:
    result = subprocess.run(
        ["git", "show", f"origin/main:Source/Skyguard52/{name}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def struct_body(header: str, struct_name: str) -> str:
    start = header.index(f"struct {struct_name}")
    brace = header.index("{", start)
    finish = header.index("};", brace)
    return header[brace : finish + 2]


def struct_field_defaults(header: str, struct_name: str) -> dict[str, str]:
    return dict(
        re.findall(
            r"int32\s+(\w+)\s*=\s*([^;]+);",
            struct_body(header, struct_name),
        )
    )


class EnvironmentReadinessDefaultsContractTests(unittest.TestCase):
    def test_readiness_struct_exists(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn("USTRUCT(BlueprintType)", header)
        self.assertIn("struct FSkyguardEnvironmentReadiness", header)
        body = struct_body(header, "FSkyguardEnvironmentReadiness")
        self.assertIn("GENERATED_BODY()", body)

    def test_in_class_defaults_are_zero(self) -> None:
        header = origin_main(HEADER_NAME)
        defaults = struct_field_defaults(header, "FSkyguardEnvironmentReadiness")
        self.assertEqual(defaults, READINESS_DEFAULTS)
        self.assertEqual(
            defaults,
            {
                "BoundCapabilityCount": "0",
                "TreeInstanceCount": "0",
                "ShrubInstanceCount": "0",
                "VFXPoolSize": "0",
            },
        )
        body = struct_body(header, "FSkyguardEnvironmentReadiness")
        for name, value in READINESS_DEFAULTS.items():
            self.assertIn(f"int32 {name} = {value};", body)
            self.assertEqual(defaults.get(name), "0", name)
        self.assertEqual(len(defaults), 4, defaults)
        self.assertNotIn("INDEX_NONE", defaults.values())
        self.assertNotIn("INDEX_NONE", body)

    def test_public_get_readiness_returns_the_struct(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn(
            "const FSkyguardEnvironmentReadiness& GetReadiness() const { return Readiness; }",
            header,
        )
        self.assertIn(
            'UFUNCTION(BlueprintPure, Category="Skyguard|Environment")',
            header,
        )
        self.assertIn(
            "FSkyguardEnvironmentReadiness Readiness;",
            header,
        )

    def test_readiness_fields_are_blueprint_visible(self) -> None:
        body = struct_body(
            origin_main(HEADER_NAME),
            "FSkyguardEnvironmentReadiness",
        )
        self.assertEqual(body.count("UPROPERTY(VisibleAnywhere, BlueprintReadOnly)"), 4)
        for name in READINESS_DEFAULTS:
            self.assertIn(name, body)

    def test_struct_does_not_require_rifle_or_igla(self) -> None:
        body = struct_body(
            origin_main(HEADER_NAME),
            "FSkyguardEnvironmentReadiness",
        )
        defaults = struct_field_defaults(
            origin_main(HEADER_NAME),
            "FSkyguardEnvironmentReadiness",
        )
        for banned in ("Rifle", "Igla", "Yak"):
            self.assertNotIn(banned, defaults)
            self.assertNotIn(banned, body)
        self.assertNotEqual(list(defaults), ["Rifle", "Igla"])

    def test_contract_is_readiness_defaults_only(self) -> None:
        header = origin_main(HEADER_NAME)
        body = struct_body(header, "FSkyguardEnvironmentReadiness")
        defaults = struct_field_defaults(header, "FSkyguardEnvironmentReadiness")
        self.assertEqual(list(defaults), list(READINESS_DEFAULTS))
        for name in DIRECTOR_NUMERIC_DEFAULT_FIELDS:
            self.assertNotIn(name, body)
            self.assertNotIn(name, defaults)
        self.assertNotIn("enum class ESkyguardEnvironmentQuality", body)
        self.assertNotIn("enum class ESkyguardEnvironmentVFXType", body)
        self.assertNotIn("ESkyguardEnvironmentQuality::High", body)
        self.assertNotIn("ESkyguardMissionWeather::Clear", body)
        self.assertNotIn("GetAppliedWeather", body)
        self.assertNotIn("5201", body)
        self.assertNotIn("240", body)
        self.assertNotIn("480", body)
        self.assertNotIn("45000.f", body)
        self.assertNotIn("2800.f", body)
        self.assertNotIn("40.f", body)
        self.assertNotIn("80.f", body)
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("Rifle", body)
        self.assertNotIn("Igla", body)
        self.assertNotIn("Yak", body)
        self.assertEqual(defaults, READINESS_DEFAULTS)

    def test_locked_files_were_not_the_edit_surface(self) -> None:
        existing = [
            f"Source/Skyguard52/{name}"
            for name in LOCKED
            if (SOURCE / name).exists()
        ]
        for sibling in (
            *SIBLING_CONTRACTS,
            "Scripts/tests/test_storm_rain_beat_kit_contract.py",
            "Scripts/tests/test_campaign_theater_kit_contract.py",
            "Scripts/tests/test_day_sortie_beat_kit_contract.py",
            "Scripts/tests/test_night_sortie_beat_kit_contract.py",
        ):
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
