from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_NAME = "SkyguardMission01EnvironmentDirector.h"
LOCKED = {
    "SkyguardMission01EnvironmentDirector.h",
    "SkyguardMission01EnvironmentDirector.cpp",
    "SkyguardMission01EnvironmentTests.cpp",
    "SkyguardCoastalEnvironmentDirector.h",
    "SkyguardCoastalEnvironmentDirector.cpp",
    "SkyguardCoastalEnvironmentDirectorTests.cpp",
    "SkyguardMissionMapAssemblyDirector.h",
    "SkyguardMissionMapAssemblyDirector.cpp",
    "SkyguardMissionMapAssemblyDirectorTests.cpp",
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
    "Scripts/tests/test_environment_readiness_defaults_contract.py",
    "Scripts/tests/test_mission_map_readiness_defaults_contract.py",
    "Scripts/tests/test_mission_landmark_anchor_defaults_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
    "Scripts/tests/test_day_sortie_beat_kit_contract.py",
    "Scripts/tests/test_night_sortie_beat_kit_contract.py",
)
PUBLIC_FIELDS = (
    "int32 OceanTileCount = 0;",
    "int32 BeachTileCount = 0;",
    "int32 LandTileCount = 0;",
    "bool bAuthoredLandscapeSurfaceExposed = false;",
    "bool bContinuousCoastline = false;",
    "bool bRouteExclusionValid = false;",
    "int32 LandscapeComponentCount = 0;",
    "bool bProductionLandscapeBound = false;",
    "bool bAuthoredPCGGraphBound = false;",
    "bool bPCGBoundsTagged = false;",
    "bool bAuthoredPCGStructureReady = false;",
    "bool bLicensedVegetationApproved = false;",
    "bool bPCGGenerationAuthorized = false;",
    "bool bReadyForAuthoredPCGGeneration = false;",
)
IN_CLASS_DEFAULTS = {
    "OceanTileCount": "0",
    "BeachTileCount": "0",
    "LandTileCount": "0",
    "bAuthoredLandscapeSurfaceExposed": "false",
    "bContinuousCoastline": "false",
    "bRouteExclusionValid": "false",
    "LandscapeComponentCount": "0",
    "bProductionLandscapeBound": "false",
    "bAuthoredPCGGraphBound": "false",
    "bPCGBoundsTagged": "false",
    "bAuthoredPCGStructureReady": "false",
    "bLicensedVegetationApproved": "false",
    "bPCGGenerationAuthorized": "false",
    "bReadyForAuthoredPCGGeneration": "false",
}
BANNED = ("igla", "yak", "rifle")
SIBLING_TYPES = (
    "FSkyguardEnvironmentReadiness",
    "FSkyguardMissionMapReadiness",
    "FSkyguardLandscapeHeightSample",
    "ESkyguardMissionSkylineStyle",
    "FSkyguardMissionObjectiveAnchor",
    "FSkyguardMissionLandmarkAnchor",
)
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


def readiness_body(header: str) -> str:
    start = header.index("struct FSkyguardMission01EnvironmentReadiness")
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


class Mission01EnvironmentReadinessDefaultsContractTests(unittest.TestCase):
    def test_readiness_struct_exists(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn("struct FSkyguardMission01EnvironmentReadiness", header)
        self.assertIn("USTRUCT(BlueprintType)", header)
        self.assertIn("GENERATED_BODY()", readiness_body(header))

    def test_public_fields_match_origin_main_in_order(self) -> None:
        body = readiness_body(origin_main(HEADER_NAME))
        positions = [body.index(field) for field in PUBLIC_FIELDS]
        self.assertEqual(positions, sorted(positions), PUBLIC_FIELDS)
        for field in PUBLIC_FIELDS:
            self.assertIn(field, body)
        self.assertEqual(
            body.count("UPROPERTY(VisibleAnywhere, BlueprintReadOnly)"),
            14,
        )

    def test_in_class_defaults_match_origin_main(self) -> None:
        body = readiness_body(origin_main(HEADER_NAME))
        defaults = in_class_defaults(body)
        self.assertEqual(defaults, IN_CLASS_DEFAULTS)
        self.assertIn("int32 OceanTileCount = 0;", body)
        self.assertIn("int32 BeachTileCount = 0;", body)
        self.assertIn("int32 LandTileCount = 0;", body)
        self.assertIn("bool bAuthoredLandscapeSurfaceExposed = false;", body)
        self.assertIn("bool bContinuousCoastline = false;", body)
        self.assertIn("bool bRouteExclusionValid = false;", body)
        self.assertIn("int32 LandscapeComponentCount = 0;", body)
        self.assertIn("bool bProductionLandscapeBound = false;", body)
        self.assertIn("bool bAuthoredPCGGraphBound = false;", body)
        self.assertIn("bool bPCGBoundsTagged = false;", body)
        self.assertIn("bool bAuthoredPCGStructureReady = false;", body)
        self.assertIn("bool bLicensedVegetationApproved = false;", body)
        self.assertIn("bool bPCGGenerationAuthorized = false;", body)
        self.assertIn("bool bReadyForAuthoredPCGGeneration = false;", body)
        self.assertEqual(len(defaults), 14, defaults)

    def test_public_get_readiness_returns_the_struct(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn(
            "const FSkyguardMission01EnvironmentReadiness& GetReadiness() const { return Readiness; }",
            header,
        )
        self.assertIn(
            'UFUNCTION(BlueprintPure, Category="Skyguard|Mission01|Environment")',
            header,
        )
        self.assertIn("FSkyguardMission01EnvironmentReadiness Readiness;", header)

    def test_struct_does_not_invent_index_none(self) -> None:
        body = readiness_body(origin_main(HEADER_NAME))
        defaults = in_class_defaults(body)
        self.assertNotIn("INDEX_NONE", defaults.values())
        self.assertNotIn("NAME_None", defaults.values())
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("NAME_None", body)

    def test_struct_does_not_re_lock_siblings_or_harbor(self) -> None:
        body = readiness_body(origin_main(HEADER_NAME))
        defaults = in_class_defaults(body)
        for name in SIBLING_TYPES:
            self.assertNotIn(name, body)
            self.assertNotIn(name, defaults)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        self.assertNotIn("enum class", body)
        self.assertNotIn("BoundCapabilityCount", body)
        self.assertNotIn("TreeInstanceCount", body)
        self.assertNotIn("HeightCentimeters", body)
        self.assertNotIn("RouteLengthCentimeters", body)

    def test_struct_bans_igla_yak_rifle(self) -> None:
        body = readiness_body(origin_main(HEADER_NAME))
        defaults = in_class_defaults(body)
        lowered = body.lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"FSkyguardMission01EnvironmentReadiness contains {banned}",
            )
            self.assertNotIn(banned, defaults)

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
