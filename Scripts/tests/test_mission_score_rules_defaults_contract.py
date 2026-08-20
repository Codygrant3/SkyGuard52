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
    "Scripts/tests/test_enemy_formation_defaults_contract.py",
    "Scripts/tests/test_mission_debrief_defaults_contract.py",
    "Scripts/tests/test_mission_debrief_state_enum_contract.py",
    "Scripts/tests/test_mission_objective_formation_enum_contract.py",
    "Scripts/tests/test_mission_result_defaults_contract.py",
    "Scripts/tests/test_mission_types_defaults_contract.py",
    "Scripts/tests/test_mission_weather_enum_contract.py",
    "Scripts/tests/test_objective_definition_defaults_contract.py",
    "Scripts/tests/test_objective_progress_defaults_contract.py",
    "Scripts/tests/test_route_point_defaults_contract.py",
)
PUBLIC_FIELDS = (
    "int32 CompletionScore = 5000;",
    "int32 PerfectAccuracyBonus = 2500;",
    "int32 NoDamageBonus = 1500;",
    "int32 BronzeThreshold = 5000;",
    "int32 SilverThreshold = 8000;",
    "int32 GoldThreshold = 11000;",
)
IN_CLASS_DEFAULTS = {
    "CompletionScore": "5000",
    "PerfectAccuracyBonus": "2500",
    "NoDamageBonus": "1500",
    "BronzeThreshold": "5000",
    "SilverThreshold": "8000",
    "GoldThreshold": "11000",
}
BANNED = ("igla", "yak", "rifle")
# FSkyguardMissionResult (#179) and FSkyguardMissionDebrief (#176) stay
# on their own isolated drafts. This contract locks score-rule fields only.
OTHER_TYPES = (
    "FSkyguardMissionResult",
    "FSkyguardMissionDebrief",
    "FSkyguardObjectiveProgress",
    "FSkyguardObjectiveDefinition",
    "FSkyguardRoutePoint",
    "FSkyguardEnemyFormationDefinition",
    "ESkyguardMissionObjectiveType",
    "ESkyguardMissionObjectiveState",
    "ESkyguardFormationType",
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


def score_rules_body(header: str) -> str:
    start = header.index("struct FSkyguardMissionScoreRules")
    brace = header.index("{", start)
    finish = header.index("};", brace)
    return header[brace : finish + 2]


def in_class_defaults(body: str) -> dict[str, str]:
    return dict(
        re.findall(
            r"int32\s+(\w+)\s*=\s*([^;]+);",
            body,
        )
    )


class MissionScoreRulesDefaultsContractTests(unittest.TestCase):
    def test_score_rules_struct_exists(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn("struct FSkyguardMissionScoreRules", header)
        self.assertIn("USTRUCT(BlueprintType)", header)
        self.assertIn("GENERATED_BODY()", score_rules_body(header))

    def test_public_fields_match_origin_main_in_order(self) -> None:
        body = score_rules_body(origin_main(HEADER_NAME))
        positions = [body.index(field) for field in PUBLIC_FIELDS]
        self.assertEqual(positions, sorted(positions), PUBLIC_FIELDS)
        for field in PUBLIC_FIELDS:
            self.assertIn(field, body)
        self.assertEqual(body.count("UPROPERTY("), 6)
        self.assertEqual(
            body.count(
                'UPROPERTY(EditAnywhere, BlueprintReadOnly, meta = (ClampMin = "0"))'
            ),
            3,
        )
        self.assertEqual(
            body.count(
                'UPROPERTY(EditAnywhere, BlueprintReadOnly, meta = (ClampMin = "1"))'
            ),
            3,
        )

    def test_in_class_defaults_match_origin_main(self) -> None:
        body = score_rules_body(origin_main(HEADER_NAME))
        defaults = in_class_defaults(body)
        self.assertEqual(defaults, IN_CLASS_DEFAULTS)
        self.assertEqual(defaults.get("CompletionScore"), "5000")
        self.assertEqual(defaults.get("PerfectAccuracyBonus"), "2500")
        self.assertEqual(defaults.get("NoDamageBonus"), "1500")
        self.assertEqual(defaults.get("BronzeThreshold"), "5000")
        self.assertEqual(defaults.get("SilverThreshold"), "8000")
        self.assertEqual(defaults.get("GoldThreshold"), "11000")
        self.assertIn("int32 CompletionScore = 5000;", body)
        self.assertIn("int32 PerfectAccuracyBonus = 2500;", body)
        self.assertIn("int32 NoDamageBonus = 1500;", body)
        self.assertIn("int32 BronzeThreshold = 5000;", body)
        self.assertIn("int32 SilverThreshold = 8000;", body)
        self.assertIn("int32 GoldThreshold = 11000;", body)

    def test_struct_does_not_invent_index_none(self) -> None:
        body = score_rules_body(origin_main(HEADER_NAME))
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("NAME_None", body)
        self.assertNotIn("FName", body)
        self.assertNotIn(" = INDEX_NONE", body)

    def test_struct_does_not_re_lock_result_debrief_or_harbor(self) -> None:
        body = score_rules_body(origin_main(HEADER_NAME))
        for name in OTHER_TYPES:
            self.assertNotIn(name, body)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        self.assertNotIn("enum class", body)
        self.assertNotIn("struct FSkyguardMissionResult", body)
        self.assertNotIn("struct FSkyguardMissionDebrief", body)

    def test_struct_bans_igla_yak_rifle(self) -> None:
        lowered = score_rules_body(origin_main(HEADER_NAME)).lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"FSkyguardMissionScoreRules contains {banned}",
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
