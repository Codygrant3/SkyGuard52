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
    "SkyguardRouteRuntime.h",
    "SkyguardRouteRuntime.cpp",
    "SkyguardRouteRuntimeFailClosedTests.cpp",
    "SkyguardRouteRuntimeTests.cpp",
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
    "Scripts/tests/test_briefing_radio_row_contract.py",
    "Scripts/tests/test_how_to_fly_row_contract.py",
    "Scripts/tests/test_sortie_presentation_contract.py",
    "Scripts/tests/test_enemy_wave_defaults_contract.py",
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
    "FName RouteId;",
    "TArray<FSkyguardRoutePoint> Points;",
)
BANNED = ("igla", "yak", "rifle")
# FSkyguardRoutePoint in-class defaults stay on isolated draft #180.
ROUTE_POINT_FIELDS_NOT_LOCKED = (
    "FName PointId;",
    "FVector WorldLocation = FVector::ZeroVector;",
    "float TargetAirspeedKph = 220.f;",
    "float LookAheadSeconds = 2.f;",
    "bool bAllowCombatOrbit = true;",
    "FVector::ZeroVector",
    "TargetAirspeedKph",
    "LookAheadSeconds",
    "bAllowCombatOrbit",
    "PointId",
    "WorldLocation",
)
# FSkyguardEnemyWaveDefinition stays on isolated draft #189.
WAVE_FIELDS_NOT_LOCKED = (
    "FName WaveId;",
    "float StartTimeSeconds = 0.f;",
    "TArray<FSkyguardEnemyFormationDefinition> Formations;",
    "FName CompletionObjectiveId;",
    "struct FSkyguardEnemyWaveDefinition",
)
OTHER_TYPES = (
    "FSkyguardObjectiveDefinition",
    "FSkyguardEnemyFormationDefinition",
    "FSkyguardEnemyWaveDefinition",
    "FSkyguardBossWeakPointDefinition",
    "FSkyguardBossDefinition",
    "FSkyguardWeatherProfile",
    "FSkyguardMissionPresentation",
    "FSkyguardMissionScoreRules",
    "FSkyguardObjectiveProgress",
    "FSkyguardMissionResult",
    "FSkyguardMissionDebrief",
    "ESkyguardMissionObjectiveType",
    "ESkyguardMissionObjectiveState",
    "ESkyguardFormationType",
    "ESkyguardMissionWeather",
    "ESkyguardMissionDebriefState",
)
INVENTED_DEFAULTS = (
    "NAME_None",
    "INDEX_NONE",
    "RouteId =",
    "Points =",
    "Points{}",
    "TArray<FSkyguardRoutePoint> Points =",
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


def route_definition_body(header: str) -> str:
    start = header.index("struct FSkyguardRouteDefinition")
    brace = header.index("{", start)
    finish = header.index("};", brace)
    return header[brace : finish + 2]


def in_class_assignments(body: str) -> dict[str, str]:
    return dict(
        re.findall(
            r"(?:FName|FVector|FText|TArray<[^>]+>|float|int32|bool)\s+(\w+)\s*=\s*([^;]+);",
            body,
        )
    )


class RouteDefinitionFieldsContractTests(unittest.TestCase):
    def test_route_definition_struct_exists(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn(
            "USTRUCT(BlueprintType)\nstruct FSkyguardRouteDefinition",
            header,
        )
        self.assertIn("GENERATED_BODY()", route_definition_body(header))

    def test_public_fields_match_origin_main_in_order(self) -> None:
        body = route_definition_body(origin_main(HEADER_NAME))
        positions = [body.index(field) for field in PUBLIC_FIELDS]
        self.assertEqual(positions, sorted(positions), PUBLIC_FIELDS)
        for field in PUBLIC_FIELDS:
            self.assertIn(field, body)
        self.assertIn("FName RouteId;", body)
        self.assertIn("TArray<FSkyguardRoutePoint> Points;", body)
        self.assertEqual(body.count("UPROPERTY(EditAnywhere, BlueprintReadOnly)"), 2)
        self.assertEqual(body.count("UPROPERTY("), 2)

    def test_struct_has_no_in_class_defaults_on_origin_main(self) -> None:
        body = route_definition_body(origin_main(HEADER_NAME))
        self.assertEqual(in_class_assignments(body), {})
        self.assertNotIn(" = ", body)
        for token in INVENTED_DEFAULTS:
            self.assertNotIn(token, body)

    def test_contract_does_not_re_lock_route_point(self) -> None:
        body = route_definition_body(origin_main(HEADER_NAME))
        self.assertNotIn("struct FSkyguardRoutePoint", body)
        self.assertIn("TArray<FSkyguardRoutePoint> Points;", body)
        for field in ROUTE_POINT_FIELDS_NOT_LOCKED:
            self.assertNotIn(field, body)

    def test_contract_does_not_re_lock_enemy_wave(self) -> None:
        body = route_definition_body(origin_main(HEADER_NAME))
        for field in WAVE_FIELDS_NOT_LOCKED:
            self.assertNotIn(field, body)

    def test_struct_does_not_re_lock_siblings_or_harbor(self) -> None:
        body = route_definition_body(origin_main(HEADER_NAME))
        for name in OTHER_TYPES:
            self.assertNotIn(name, body)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        self.assertNotIn("enum class", body)
        self.assertNotIn("220.f", body)
        self.assertNotIn("0.f", body)

    def test_struct_bans_igla_yak_rifle(self) -> None:
        lowered = route_definition_body(origin_main(HEADER_NAME)).lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"FSkyguardRouteDefinition contains {banned}",
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
