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
    "Scripts/tests/test_mission_objective_formation_enum_contract.py",
    "Scripts/tests/test_mission_result_defaults_contract.py",
    "Scripts/tests/test_objective_progress_defaults_contract.py",
    "Scripts/tests/test_mission_debrief_defaults_contract.py",
    "Scripts/tests/test_mission_debrief_state_enum_contract.py",
    "Scripts/tests/test_mission_weather_enum_contract.py",
)
PUBLIC_FIELDS = (
    "FName ObjectiveId;",
    "FText DisplayName;",
    "ESkyguardMissionObjectiveType Type = ESkyguardMissionObjectiveType::DestroyTargets;",
    "int32 RequiredProgress = 1;",
    "bool bRequiredForMissionSuccess = true;",
    "bool bFailureEndsMission = false;",
    "int32 ScoreReward = 1000;",
)
IN_CLASS_DEFAULTS = {
    "Type": "ESkyguardMissionObjectiveType::DestroyTargets",
    "RequiredProgress": "1",
    "bRequiredForMissionSuccess": "true",
    "bFailureEndsMission": "false",
    "ScoreReward": "1000",
}
BANNED = ("igla", "yak", "rifle")
OTHER_ENUMS = (
    "ESkyguardFormationType",
    "ESkyguardMissionObjectiveState",
    "ESkyguardMissionWeather",
    "ESkyguardMissionDebriefState",
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


def definition_body(header: str) -> str:
    start = header.index("struct FSkyguardObjectiveDefinition")
    brace = header.index("{", start)
    finish = header.index("};", brace)
    return header[brace : finish + 2]


def in_class_defaults(body: str) -> dict[str, str]:
    return dict(
        re.findall(
            r"(?:ESkyguardMissionObjectiveType|int32|bool)\s+(\w+)\s*=\s*([^;]+);",
            body,
        )
    )


class ObjectiveDefinitionDefaultsContractTests(unittest.TestCase):
    def test_definition_struct_exists(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn("struct FSkyguardObjectiveDefinition", header)
        self.assertIn("USTRUCT(BlueprintType)", header)
        self.assertIn("GENERATED_BODY()", definition_body(header))

    def test_public_fields_match_origin_main_in_order(self) -> None:
        body = definition_body(origin_main(HEADER_NAME))
        positions = [body.index(field) for field in PUBLIC_FIELDS]
        self.assertEqual(positions, sorted(positions), PUBLIC_FIELDS)
        for field in PUBLIC_FIELDS:
            self.assertIn(field, body)

    def test_in_class_defaults_match_origin_main(self) -> None:
        body = definition_body(origin_main(HEADER_NAME))
        self.assertEqual(in_class_defaults(body), IN_CLASS_DEFAULTS)
        self.assertIn(
            "ESkyguardMissionObjectiveType Type = "
            "ESkyguardMissionObjectiveType::DestroyTargets;",
            body,
        )
        self.assertIn("int32 RequiredProgress = 1;", body)
        self.assertIn("bool bRequiredForMissionSuccess = true;", body)
        self.assertIn("bool bFailureEndsMission = false;", body)
        self.assertIn("int32 ScoreReward = 1000;", body)

    def test_struct_does_not_invent_index_none(self) -> None:
        body = definition_body(origin_main(HEADER_NAME))
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("NAME_None", body)
        self.assertNotIn("ObjectiveId =", body)
        self.assertNotIn("DisplayName =", body)

    def test_struct_does_not_re_lock_objective_type_enumerator_list(self) -> None:
        body = definition_body(origin_main(HEADER_NAME))
        self.assertNotIn("enum class ESkyguardMissionObjectiveType", body)
        self.assertNotIn("enum class ESkyguardFormationType", body)
        self.assertIn(
            "ESkyguardMissionObjectiveType::DestroyTargets",
            body,
        )
        self.assertEqual(
            body.count("ESkyguardMissionObjectiveType::"),
            1,
        )

    def test_struct_does_not_re_lock_other_enums_or_harbor(self) -> None:
        body = definition_body(origin_main(HEADER_NAME))
        for name in OTHER_ENUMS:
            self.assertNotIn(name, body)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)

    def test_struct_bans_igla_yak_rifle(self) -> None:
        lowered = definition_body(origin_main(HEADER_NAME)).lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"FSkyguardObjectiveDefinition contains {banned}",
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
