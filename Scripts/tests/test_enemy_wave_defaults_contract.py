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
    "Scripts/tests/test_weather_profile_defaults_contract.py",
    "Scripts/tests/test_mission_score_rules_defaults_contract.py",
    "Scripts/tests/test_mission_presentation_defaults_contract.py",
    "Scripts/tests/test_boss_definition_defaults_contract.py",
    "Scripts/tests/test_boss_weak_point_defaults_contract.py",
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
    "FName WaveId;",
    "float StartTimeSeconds = 0.f;",
    "TArray<FSkyguardEnemyFormationDefinition> Formations;",
    "FName CompletionObjectiveId;",
)
IN_CLASS_DEFAULTS = {
    "StartTimeSeconds": "0.f",
}
BANNED = ("igla", "yak", "rifle")
# FSkyguardEnemyFormationDefinition (#183 UnitCount/Spacing/Formation) and
# ESkyguardFormationType (#159) stay on their own isolated drafts.
FORMATION_FIELDS_NOT_LOCKED = (
    "int32 UnitCount = 3;",
    "float SpacingCentimeters = 1200.f;",
    "ESkyguardFormationType Formation = ESkyguardFormationType::Vee;",
    "ESkyguardFormationType::Vee",
    "FormationId",
)
FORMATION_ENUMERATORS_NOT_LOCKED = (
    "Line",
    "Vee",
    "EchelonLeft",
    "EchelonRight",
    "Trail",
    "LooseSwarm",
)
OTHER_TYPES = (
    "FSkyguardRoutePoint",
    "FSkyguardObjectiveDefinition",
    "FSkyguardObjectiveProgress",
    "FSkyguardMissionResult",
    "FSkyguardMissionDebrief",
    "FSkyguardMissionScoreRules",
    "FSkyguardWeatherProfile",
    "FSkyguardMissionPresentation",
    "FSkyguardBossDefinition",
    "FSkyguardBossWeakPointDefinition",
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


def wave_body(header: str) -> str:
    start = header.index("struct FSkyguardEnemyWaveDefinition")
    brace = header.index("{", start)
    finish = header.index("};", brace)
    return header[brace : finish + 2]


def in_class_defaults(body: str) -> dict[str, str]:
    return dict(
        re.findall(
            r"float\s+(\w+)\s*=\s*([^;]+);",
            body,
        )
    )


class EnemyWaveDefaultsContractTests(unittest.TestCase):
    def test_enemy_wave_struct_exists(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn("struct FSkyguardEnemyWaveDefinition", header)
        self.assertIn("USTRUCT(BlueprintType)", header)
        self.assertIn("GENERATED_BODY()", wave_body(header))

    def test_public_fields_match_origin_main_in_order(self) -> None:
        body = wave_body(origin_main(HEADER_NAME))
        positions = [body.index(field) for field in PUBLIC_FIELDS]
        self.assertEqual(positions, sorted(positions), PUBLIC_FIELDS)
        for field in PUBLIC_FIELDS:
            self.assertIn(field, body)
        self.assertIn("FName WaveId;", body)
        self.assertIn("float StartTimeSeconds = 0.f;", body)
        self.assertIn("TArray<FSkyguardEnemyFormationDefinition> Formations;", body)
        self.assertIn("FName CompletionObjectiveId;", body)
        self.assertEqual(body.count("UPROPERTY("), 4)
        self.assertEqual(
            body.count("\tUPROPERTY(EditAnywhere, BlueprintReadOnly)\n"),
            3,
        )
        self.assertIn(
            'UPROPERTY(EditAnywhere, BlueprintReadOnly, meta = (ClampMin = "0.0"))',
            body,
        )

    def test_in_class_defaults_match_origin_main(self) -> None:
        body = wave_body(origin_main(HEADER_NAME))
        defaults = in_class_defaults(body)
        self.assertEqual(defaults, IN_CLASS_DEFAULTS)
        self.assertEqual(defaults.get("StartTimeSeconds"), "0.f")
        self.assertIn("float StartTimeSeconds = 0.f;", body)
        self.assertEqual(list(defaults), ["StartTimeSeconds"])

    def test_struct_does_not_invent_index_none(self) -> None:
        body = wave_body(origin_main(HEADER_NAME))
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("NAME_None", body)
        self.assertNotIn("WaveId =", body)
        self.assertNotIn("Formations =", body)
        self.assertNotIn("CompletionObjectiveId =", body)

    def test_contract_does_not_re_lock_enemy_formation_or_type(self) -> None:
        body = wave_body(origin_main(HEADER_NAME))
        self.assertNotIn("struct FSkyguardEnemyFormationDefinition", body)
        self.assertNotIn("enum class ESkyguardFormationType", body)
        self.assertIn("TArray<FSkyguardEnemyFormationDefinition> Formations;", body)
        for field in FORMATION_FIELDS_NOT_LOCKED:
            self.assertNotIn(field, body)
        for name in FORMATION_ENUMERATORS_NOT_LOCKED:
            self.assertNotIn(name, body)
            self.assertNotIn(f"ESkyguardFormationType::{name}", body)

    def test_struct_does_not_re_lock_siblings_or_harbor(self) -> None:
        body = wave_body(origin_main(HEADER_NAME))
        for name in OTHER_TYPES:
            self.assertNotIn(name, body)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        self.assertNotIn("enum class", body)

    def test_struct_bans_igla_yak_rifle(self) -> None:
        lowered = wave_body(origin_main(HEADER_NAME)).lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"FSkyguardEnemyWaveDefinition contains {banned}",
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
