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
    "SkyguardBossTypes.h",
    "SkyguardBossDroneBase.h",
    "SkyguardBossDroneBase.cpp",
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
    "Scripts/tests/test_boss_phase_enum_contract.py",
    "Scripts/tests/test_mission_score_rules_defaults_contract.py",
    "Scripts/tests/test_weather_profile_defaults_contract.py",
    "Scripts/tests/test_enemy_formation_defaults_contract.py",
    "Scripts/tests/test_objective_progress_defaults_contract.py",
    "Scripts/tests/test_objective_definition_defaults_contract.py",
    "Scripts/tests/test_route_point_defaults_contract.py",
    "Scripts/tests/test_mission_result_defaults_contract.py",
    "Scripts/tests/test_briefing_card_defaults_contract.py",
    "Scripts/tests/test_mission_debrief_defaults_contract.py",
    "Scripts/tests/test_mission_debrief_state_enum_contract.py",
    "Scripts/tests/test_mission_objective_formation_enum_contract.py",
    "Scripts/tests/test_mission_weather_enum_contract.py",
    "Scripts/tests/test_mission_types_defaults_contract.py",
)
PUBLIC_FIELDS = (
    "FName BossId;",
    "FText Callsign;",
    "TArray<FSkyguardBossWeakPointDefinition> WeakPoints;",
    "FName DefeatObjectiveId;",
    "int32 MaximumBreakupPieces = 3;",
)
IN_CLASS_DEFAULTS = {
    "MaximumBreakupPieces": "3",
}
UNINITIALIZED_FIELDS = (
    "BossId",
    "Callsign",
    "WeakPoints",
    "DefeatObjectiveId",
)
BANNED = ("igla", "yak", "rifle")
# ESkyguardBossPhase (#162) and ESkyguardBossWeapon stay off this draft.
# Rifle / Igla are not live player weapons.
BOSS_PHASE_ENUMERATORS_OWNED_BY_162 = (
    "Approach",
    "Disarm",
    "LockWindow",
    "Critical",
    "Defeated",
)
OTHER_TYPES = (
    "ESkyguardBossPhase",
    "ESkyguardBossWeapon",
    "FSkyguardBossTelemetry",
    "ESkyguardPilotCommand",
    "FSkyguardMissionScoreRules",
    "FSkyguardMissionResult",
    "FSkyguardMissionDebrief",
    "FSkyguardWeatherProfile",
    "FSkyguardObjectiveDefinition",
    "FSkyguardObjectiveProgress",
    "FSkyguardRoutePoint",
    "FSkyguardEnemyFormationDefinition",
)
WEAK_POINT_INTERNALS = (
    "WeakPointId",
    "RequiredWeapon",
    "ExposesWeakPointId",
    "Integrity",
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


def boss_definition_body(header: str) -> str:
    start = header.index("struct FSkyguardBossDefinition")
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


class BossDefinitionDefaultsContractTests(unittest.TestCase):
    def test_boss_definition_struct_exists(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn("struct FSkyguardBossDefinition", header)
        self.assertIn("USTRUCT(BlueprintType)", header)
        self.assertIn("GENERATED_BODY()", boss_definition_body(header))

    def test_public_fields_match_origin_main_in_order(self) -> None:
        body = boss_definition_body(origin_main(HEADER_NAME))
        positions = [body.index(field) for field in PUBLIC_FIELDS]
        self.assertEqual(positions, sorted(positions), PUBLIC_FIELDS)
        for field in PUBLIC_FIELDS:
            self.assertIn(field, body)
        self.assertEqual(body.count("UPROPERTY("), 5)
        self.assertEqual(body.count("BlueprintReadOnly"), 5)
        self.assertEqual(body.count("EditAnywhere"), 5)
        self.assertIn('meta = (ClampMin = "0", ClampMax = "12")', body)

    def test_in_class_defaults_match_origin_main(self) -> None:
        body = boss_definition_body(origin_main(HEADER_NAME))
        defaults = in_class_defaults(body)
        self.assertEqual(defaults, IN_CLASS_DEFAULTS)
        self.assertEqual(defaults.get("MaximumBreakupPieces"), "3")
        self.assertIn("int32 MaximumBreakupPieces = 3;", body)
        self.assertEqual(len(defaults), 1)

    def test_struct_does_not_invent_index_none(self) -> None:
        body = boss_definition_body(origin_main(HEADER_NAME))
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("NAME_None", body)
        self.assertNotIn("FName BossId =", body)
        self.assertNotIn("FText Callsign =", body)
        self.assertNotIn("WeakPoints =", body)
        self.assertNotIn("FName DefeatObjectiveId =", body)
        for field in UNINITIALIZED_FIELDS:
            self.assertNotIn(f"{field} =", body)
            self.assertNotIn(f"{field} = INDEX_NONE", body)
            self.assertNotIn(f"{field} = NAME_None", body)

    def test_struct_does_not_lock_boss_weapon_or_re_lock_phase(self) -> None:
        body = boss_definition_body(origin_main(HEADER_NAME))
        self.assertNotIn("ESkyguardBossWeapon", body)
        self.assertNotIn("ESkyguardBossPhase", body)
        self.assertNotIn("enum class ESkyguardBossWeapon", body)
        self.assertNotIn("enum class ESkyguardBossPhase", body)
        self.assertNotIn("Rifle", body)
        self.assertNotIn("Igla", body)
        for enumerator in BOSS_PHASE_ENUMERATORS_OWNED_BY_162:
            self.assertNotIn(enumerator, body)

    def test_struct_does_not_re_lock_siblings_or_harbor(self) -> None:
        body = boss_definition_body(origin_main(HEADER_NAME))
        for name in OTHER_TYPES:
            self.assertNotIn(name, body)
        for token in WEAK_POINT_INTERNALS:
            self.assertNotIn(token, body)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        self.assertNotIn("enum class", body)

    def test_struct_bans_igla_yak_rifle(self) -> None:
        lowered = boss_definition_body(origin_main(HEADER_NAME)).lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"FSkyguardBossDefinition contains {banned}",
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
