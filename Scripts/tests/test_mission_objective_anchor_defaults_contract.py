from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_NAME = "SkyguardMissionMapAssemblyDirector.h"
LOCKED = {
    "SkyguardMissionMapAssemblyDirector.h",
    "SkyguardMissionMapAssemblyDirector.cpp",
    "SkyguardMissionMapAssemblyDirectorTests.cpp",
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
    "Scripts/tests/test_mission_map_readiness_defaults_contract.py",
    "Scripts/tests/test_environment_readiness_defaults_contract.py",
    "Scripts/tests/test_landscape_height_sample_defaults_contract.py",
    "Scripts/tests/test_landscape_footprint_sample_defaults_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
    "Scripts/tests/test_day_sortie_beat_kit_contract.py",
    "Scripts/tests/test_night_sortie_beat_kit_contract.py",
)
PUBLIC_FIELDS = (
    "FName ObjectiveId;",
    "FVector WorldLocation = FVector::ZeroVector;",
)
IN_CLASS_DEFAULTS = {
    "WorldLocation": "FVector::ZeroVector",
}
BANNED = ("igla", "yak", "rifle")
SIBLING_TYPES = (
    "FSkyguardMissionMapReadiness",
    "FSkyguardMissionLandmarkAnchor",
    "FSkyguardEnvironmentReadiness",
    "FSkyguardLandscapeHeightSample",
    "FSkyguardLandscapeFootprintSample",
    "ESkyguardMissionSkylineStyle",
)
LANDMARK_ONLY = (
    "LandmarkId",
    "bMissionExclusive",
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


def objective_anchor_body(header: str) -> str:
    start = header.index("struct FSkyguardMissionObjectiveAnchor")
    brace = header.index("{", start)
    finish = header.index("};", brace)
    return header[brace : finish + 2]


def in_class_defaults(body: str) -> dict[str, str]:
    return dict(
        re.findall(
            r"(?:FVector)\s+(\w+)\s*=\s*([^;]+);",
            body,
        )
    )


class MissionObjectiveAnchorDefaultsContractTests(unittest.TestCase):
    def test_objective_anchor_struct_exists(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn("struct FSkyguardMissionObjectiveAnchor", header)
        self.assertIn("USTRUCT(BlueprintType)", header)
        self.assertIn("GENERATED_BODY()", objective_anchor_body(header))

    def test_public_fields_match_origin_main_in_order(self) -> None:
        body = objective_anchor_body(origin_main(HEADER_NAME))
        positions = [body.index(field) for field in PUBLIC_FIELDS]
        self.assertEqual(positions, sorted(positions), PUBLIC_FIELDS)
        for field in PUBLIC_FIELDS:
            self.assertIn(field, body)
        self.assertIn("FName ObjectiveId;", body)
        self.assertEqual(body.count("UPROPERTY(EditAnywhere, BlueprintReadOnly)"), 2)

    def test_in_class_defaults_match_origin_main(self) -> None:
        body = objective_anchor_body(origin_main(HEADER_NAME))
        self.assertEqual(in_class_defaults(body), IN_CLASS_DEFAULTS)
        self.assertIn("FVector WorldLocation = FVector::ZeroVector;", body)
        self.assertEqual(len(in_class_defaults(body)), 1, in_class_defaults(body))

    def test_struct_does_not_invent_index_none(self) -> None:
        body = objective_anchor_body(origin_main(HEADER_NAME))
        defaults = in_class_defaults(body)
        self.assertNotIn("INDEX_NONE", defaults.values())
        self.assertNotIn("NAME_None", defaults.values())
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("NAME_None", body)
        self.assertNotIn("ObjectiveId =", body)

    def test_struct_does_not_re_lock_siblings_or_harbor(self) -> None:
        body = objective_anchor_body(origin_main(HEADER_NAME))
        defaults = in_class_defaults(body)
        for name in SIBLING_TYPES:
            self.assertNotIn(name, body)
            self.assertNotIn(name, defaults)
        for token in LANDMARK_ONLY:
            self.assertNotIn(token, body)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        self.assertNotIn("enum class", body)
        self.assertNotIn("BoundCapabilityCount", body)
        self.assertNotIn("RouteLengthCentimeters", body)
        self.assertNotIn("HeightCentimeters", body)

    def test_struct_bans_igla_yak_rifle(self) -> None:
        body = objective_anchor_body(origin_main(HEADER_NAME))
        defaults = in_class_defaults(body)
        lowered = body.lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"FSkyguardMissionObjectiveAnchor contains {banned}",
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
