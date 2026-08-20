from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_NAME = "SkyguardMissionTypes.h"
LOCKED = {
    "SkyguardMissionTypes.h",
    "SkyguardMissionTypesDefaultsTests.cpp",
    "SkyguardCpgDebriefFailClosedTests.cpp",
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
    "Scripts/tests/test_mission_debrief_defaults_contract.py",
    "Scripts/tests/test_mission_debrief_state_enum_contract.py",
    "Scripts/tests/test_mission_objective_formation_enum_contract.py",
    "Scripts/tests/test_mission_weather_enum_contract.py",
)
PUBLIC_FIELDS = (
    "FName MissionId;",
    "bool bMissionSucceeded = false;",
    "int32 ShotsFired = 0;",
    "int32 Hits = 0;",
    "float AircraftDamageFraction = 0.f;",
    "float CompletionTimeSeconds = 0.f;",
    "TArray<FName> CompletedObjectiveIds;",
    "int32 FinalScore = 0;",
    "int32 MedalTier = 0;",
)
IN_CLASS_DEFAULTS = {
    "bMissionSucceeded": "false",
    "ShotsFired": "0",
    "Hits": "0",
    "AircraftDamageFraction": "0.f",
    "CompletionTimeSeconds": "0.f",
    "FinalScore": "0",
    "MedalTier": "0",
}
BANNED = ("igla", "yak", "rifle")
OTHER_ENUMS = (
    "ESkyguardMissionDebriefState",
    "ESkyguardMissionObjectiveType",
    "ESkyguardFormationType",
    "ESkyguardMissionObjectiveState",
    "ESkyguardMissionWeather",
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


def result_body(header: str) -> str:
    start = header.index("struct FSkyguardMissionResult")
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


class MissionResultDefaultsContractTests(unittest.TestCase):
    def test_result_struct_exists(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn("struct FSkyguardMissionResult", header)
        self.assertIn("USTRUCT(BlueprintType)", header)
        self.assertIn("GENERATED_BODY()", result_body(header))

    def test_public_fields_match_origin_main_in_order(self) -> None:
        body = result_body(origin_main(HEADER_NAME))
        positions = [body.index(field) for field in PUBLIC_FIELDS]
        self.assertEqual(positions, sorted(positions), PUBLIC_FIELDS)
        for field in PUBLIC_FIELDS:
            self.assertIn(field, body)

    def test_in_class_defaults_match_origin_main(self) -> None:
        body = result_body(origin_main(HEADER_NAME))
        self.assertEqual(in_class_defaults(body), IN_CLASS_DEFAULTS)
        self.assertIn("bool bMissionSucceeded = false;", body)
        self.assertIn("int32 ShotsFired = 0;", body)
        self.assertIn("int32 Hits = 0;", body)
        self.assertIn("float AircraftDamageFraction = 0.f;", body)
        self.assertIn("float CompletionTimeSeconds = 0.f;", body)
        self.assertIn("int32 FinalScore = 0;", body)
        self.assertIn("int32 MedalTier = 0;", body)

    def test_struct_does_not_invent_index_none(self) -> None:
        body = result_body(origin_main(HEADER_NAME))
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("NAME_None", body)
        self.assertNotIn("MissionId =", body)
        self.assertNotIn("CompletedObjectiveIds =", body)

    def test_struct_does_not_re_lock_debrief_enums_or_harbor(self) -> None:
        body = result_body(origin_main(HEADER_NAME))
        self.assertNotIn("struct FSkyguardMissionDebrief", body)
        self.assertNotIn("enum class ESkyguardMissionDebriefState", body)
        for name in OTHER_ENUMS:
            self.assertNotIn(name, body)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)

    def test_struct_bans_igla_yak_rifle(self) -> None:
        lowered = result_body(origin_main(HEADER_NAME)).lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"FSkyguardMissionResult contains {banned}",
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
