from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_NAME = "SkyguardEnvironmentVFXPoolComponent.h"
LOCKED = {
    "SkyguardEnvironmentVFXPoolComponent.h",
    "SkyguardEnvironmentVFXPoolComponent.cpp",
    "SkyguardEnvironmentVFXPoolTests.cpp",
    "SkyguardEnvironmentVFXPoolFailClosedTests.cpp",
    "SkyguardCoastalEnvironmentDirector.h",
    "SkyguardCoastalEnvironmentDirector.cpp",
    "SkyguardCoastalEnvironmentDirectorEmptyFailClosedTests.cpp",
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
LIVE_VFX_TYPES = [
    "Smoke",
    "Fire",
    "Sparks",
    "Explosion",
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


class EnvironmentVfxTypeEnumContractTests(unittest.TestCase):
    def test_environment_vfx_type_enum_exists(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn("enum class ESkyguardEnvironmentVFXType : uint8", header)
        self.assertIn("UENUM(BlueprintType)", header)

    def test_enumerators_match_live_order(self) -> None:
        header = origin_main(HEADER_NAME)
        enumerators = enum_enumerators(header, "ESkyguardEnvironmentVFXType")
        self.assertEqual(enumerators, LIVE_VFX_TYPES)
        self.assertEqual(
            enumerators,
            [
                "Smoke",
                "Fire",
                "Sparks",
                "Explosion",
            ],
        )
        self.assertEqual(len(enumerators), 4, enumerators)
        body = enum_body(header, "ESkyguardEnvironmentVFXType")
        for name in LIVE_VFX_TYPES:
            self.assertIn(name, body)
            self.assertIn(name, enumerators)

    def test_public_api_uses_live_vfx_type(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn("bool ActivatePooledEffect(", header)
        self.assertIn("ESkyguardEnvironmentVFXType Type", header)
        self.assertIn("void DeactivateAllEffects();", header)
        self.assertIn("int32 GetAllocatedPoolSize() const", header)
        self.assertIn("int32 GetActivationCount() const", header)
        enumerators = enum_enumerators(header, "ESkyguardEnvironmentVFXType")
        self.assertEqual(enumerators, LIVE_VFX_TYPES)
        self.assertNotIn("Rifle", enumerators)
        self.assertNotIn("Igla", enumerators)
        self.assertNotIn("Yak", enumerators)

    def test_vfx_type_enum_does_not_require_rifle_or_igla(self) -> None:
        enumerators = enum_enumerators(
            origin_main(HEADER_NAME),
            "ESkyguardEnvironmentVFXType",
        )
        self.assertNotIn("Rifle", enumerators)
        self.assertNotIn("Igla", enumerators)
        self.assertNotIn("Yak", enumerators)
        self.assertNotEqual(enumerators, ["Rifle", "Igla"])

    def test_contract_is_vfx_type_enum_only(self) -> None:
        header = origin_main(HEADER_NAME)
        body = enum_body(header, "ESkyguardEnvironmentVFXType")
        self.assertIn("Smoke", body)
        self.assertIn("Explosion", body)
        self.assertNotIn("ESkyguardEnvironmentQuality", body)
        self.assertNotIn("Low", body)
        self.assertNotIn("Medium", body)
        self.assertNotIn("High", body)
        self.assertNotIn("Epic", body)
        self.assertNotIn("PlacementSeed", body)
        self.assertNotIn("EpicTreeBudget", body)
        self.assertNotIn("EpicShrubBudget", body)
        self.assertNotIn("RouteLengthCm", body)
        self.assertNotIn("RouteCorridorHalfWidthCm", body)
        self.assertNotIn("ShorelineLandOffsetCm", body)
        self.assertNotIn("InlandExtentCm", body)
        self.assertNotIn("VegetationStartCullDistanceCm", body)
        self.assertNotIn("VegetationEndCullDistanceCm", body)
        self.assertNotIn("WindStrength", body)
        self.assertNotIn("WindSpeed", body)
        self.assertNotIn("5201", body)
        self.assertNotIn("45000.f", body)
        self.assertNotIn("2800.f", body)
        self.assertNotIn("PoolCapacity", body)
        self.assertNotIn("40.f", body)
        self.assertNotIn("80.f", body)
        self.assertNotIn("Rifle", body)
        self.assertNotIn("Igla", body)
        self.assertNotIn("Yak", body)
        enumerators = enum_enumerators(header, "ESkyguardEnvironmentVFXType")
        self.assertEqual(enumerators, LIVE_VFX_TYPES)
        self.assertNotEqual(enumerators, ["Rifle", "Igla"])

    def test_locked_files_were_not_the_edit_surface(self) -> None:
        existing = [
            f"Source/Skyguard52/{name}"
            for name in LOCKED
            if (SOURCE / name).exists()
        ]
        for sibling in (
            "Scripts/tests/test_storm_rain_beat_kit_contract.py",
            "Scripts/tests/test_environment_quality_enum_contract.py",
            "Scripts/tests/test_mission_weather_enum_contract.py",
            "Scripts/tests/test_mission_objective_formation_enum_contract.py",
            "Scripts/tests/test_boss_phase_enum_contract.py",
            "Scripts/tests/test_mission_debrief_state_enum_contract.py",
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
