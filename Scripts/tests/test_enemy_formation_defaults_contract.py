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
    "Scripts/tests/test_mission_types_defaults_contract.py",
    "Scripts/tests/test_objective_progress_defaults_contract.py",
    "Scripts/tests/test_objective_definition_defaults_contract.py",
    "Scripts/tests/test_route_point_defaults_contract.py",
)
PUBLIC_FIELDS = (
    "FName FormationId;",
    "ESkyguardFormationType Formation = ESkyguardFormationType::Vee;",
    "int32 UnitCount = 3;",
    "float SpacingCentimeters = 1200.f;",
)
IN_CLASS_DEFAULTS = {
    "Formation": "ESkyguardFormationType::Vee",
    "UnitCount": "3",
    "SpacingCentimeters": "1200.f",
}
BANNED = ("igla", "yak", "rifle")
# ESkyguardFormationType enumerators belong to #159. This contract locks
# only the FSkyguardEnemyFormationDefinition Formation default (Vee).
FORMATION_ENUMERATORS_NOT_LOCKED = (
    "Line",
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
    "ESkyguardMissionObjectiveType",
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


def formation_body(header: str) -> str:
    start = header.index("struct FSkyguardEnemyFormationDefinition")
    brace = header.index("{", start)
    finish = header.index("};", brace)
    return header[brace : finish + 2]


def in_class_defaults(body: str) -> dict[str, str]:
    return {
        name: value.strip()
        for name, value in re.findall(
            r"(?:ESkyguardFormationType|int32|float)\s+(\w+)\s*=\s*([^;]+);",
            body,
        )
    }


class EnemyFormationDefaultsContractTests(unittest.TestCase):
    def test_enemy_formation_struct_exists(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn("struct FSkyguardEnemyFormationDefinition", header)
        self.assertIn("USTRUCT(BlueprintType)", header)
        self.assertIn("GENERATED_BODY()", formation_body(header))

    def test_public_fields_match_origin_main_in_order(self) -> None:
        body = formation_body(origin_main(HEADER_NAME))
        positions = [body.index(field) for field in PUBLIC_FIELDS]
        self.assertEqual(positions, sorted(positions), PUBLIC_FIELDS)
        for field in PUBLIC_FIELDS:
            self.assertIn(field, body)
        self.assertEqual(body.count("UPROPERTY("), 4)
        self.assertEqual(
            body.count("\tUPROPERTY(EditAnywhere, BlueprintReadOnly)\n"),
            2,
        )
        self.assertIn(
            'UPROPERTY(EditAnywhere, BlueprintReadOnly, meta = (ClampMin = "1", ClampMax = "32"))',
            body,
        )
        self.assertIn(
            'UPROPERTY(EditAnywhere, BlueprintReadOnly, meta = (ClampMin = "100.0"))',
            body,
        )

    def test_in_class_defaults_match_origin_main(self) -> None:
        body = formation_body(origin_main(HEADER_NAME))
        defaults = in_class_defaults(body)
        self.assertEqual(defaults, IN_CLASS_DEFAULTS)
        self.assertEqual(defaults.get("Formation"), "ESkyguardFormationType::Vee")
        self.assertEqual(defaults.get("UnitCount"), "3")
        self.assertEqual(defaults.get("SpacingCentimeters"), "1200.f")
        self.assertIn(
            "ESkyguardFormationType Formation = ESkyguardFormationType::Vee;",
            body,
        )
        self.assertIn("int32 UnitCount = 3;", body)
        self.assertIn("float SpacingCentimeters = 1200.f;", body)
        self.assertEqual(
            re.findall(r"ESkyguardFormationType::(\w+)", body),
            ["Vee"],
        )

    def test_struct_does_not_invent_index_none(self) -> None:
        body = formation_body(origin_main(HEADER_NAME))
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("NAME_None", body)
        self.assertNotIn("FormationId =", body)

    def test_contract_does_not_re_lock_formation_enumerators(self) -> None:
        body = formation_body(origin_main(HEADER_NAME))
        self.assertNotIn("enum class ESkyguardFormationType", body)
        self.assertIn("ESkyguardFormationType::Vee", body)
        for name in FORMATION_ENUMERATORS_NOT_LOCKED:
            self.assertNotIn(name, body)
            self.assertNotIn(f"ESkyguardFormationType::{name}", body)

    def test_struct_does_not_re_lock_siblings_or_harbor(self) -> None:
        body = formation_body(origin_main(HEADER_NAME))
        for name in OTHER_TYPES:
            self.assertNotIn(name, body)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        self.assertNotIn("enum class", body)

    def test_struct_bans_igla_yak_rifle(self) -> None:
        lowered = formation_body(origin_main(HEADER_NAME)).lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"FSkyguardEnemyFormationDefinition contains {banned}",
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
