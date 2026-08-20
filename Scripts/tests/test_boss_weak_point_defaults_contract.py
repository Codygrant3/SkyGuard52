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
    "SkyguardBossTypes.h",
    "SkyguardBossWeakPointComponent.h",
    "SkyguardBossWeakPointComponent.cpp",
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
    "Scripts/tests/test_mission_types_defaults_contract.py",
    "Scripts/tests/test_mission_score_rules_defaults_contract.py",
    "Scripts/tests/test_weather_profile_defaults_contract.py",
    "Scripts/tests/test_enemy_formation_defaults_contract.py",
)
PUBLIC_FIELDS = (
    "FName WeakPointId;",
    "FName RequiredWeapon;",
    "FName ExposesWeakPointId;",
    "float Integrity = 100.f;",
)
IN_CLASS_DEFAULTS = {
    "Integrity": "100.f",
}
BANNED = ("igla", "yak", "rifle")
# ESkyguardBossPhase enumerators belong to #162. This contract locks
# FSkyguardBossWeakPointDefinition Integrity only.
BOSS_PHASE_ENUMERATORS_OWNED_BY_162 = (
    "Approach",
    "Disarm",
    "LockWindow",
    "Critical",
    "Defeated",
)
# ESkyguardBossWeapon (Rifle / Igla) is not a live CPG station and is
# not locked here. RequiredWeapon is a catalog FName on origin/main.
OTHER_TYPES = (
    "ESkyguardBossPhase",
    "ESkyguardBossWeapon",
    "FSkyguardBossDefinition",
    "FSkyguardBossTelemetry",
    "FSkyguardWeatherProfile",
    "FSkyguardMissionScoreRules",
    "FSkyguardEnemyFormationDefinition",
    "ESkyguardMissionWeather",
    "ESkyguardFormationType",
)
HARBOR_TUNING = ("40.f", "80.f")
UNINITIALIZED_FNAMES = (
    "WeakPointId",
    "RequiredWeapon",
    "ExposesWeakPointId",
)


def origin_main(name: str) -> str:
    result = subprocess.run(
        ["git", "show", f"origin/main:Source/Skyguard52/{name}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def weak_point_body(header: str) -> str:
    start = header.index("struct FSkyguardBossWeakPointDefinition")
    brace = header.index("{", start)
    finish = header.index("};", brace)
    return header[brace : finish + 2]


def in_class_defaults(body: str) -> dict[str, str]:
    return {
        name: value.strip()
        for name, value in re.findall(
            r"float\s+(\w+)\s*=\s*([^;]+);",
            body,
        )
    }


class BossWeakPointDefaultsContractTests(unittest.TestCase):
    def test_weak_point_struct_exists(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn("struct FSkyguardBossWeakPointDefinition", header)
        self.assertIn("USTRUCT(BlueprintType)", header)
        self.assertIn("GENERATED_BODY()", weak_point_body(header))

    def test_public_fields_match_origin_main_in_order(self) -> None:
        body = weak_point_body(origin_main(HEADER_NAME))
        positions = [body.index(field) for field in PUBLIC_FIELDS]
        self.assertEqual(positions, sorted(positions), PUBLIC_FIELDS)
        for field in PUBLIC_FIELDS:
            self.assertIn(field, body)
        self.assertEqual(body.count("UPROPERTY("), 4)
        self.assertEqual(
            body.count("\tUPROPERTY(EditAnywhere, BlueprintReadOnly)\n"),
            3,
        )
        self.assertIn(
            'UPROPERTY(EditAnywhere, BlueprintReadOnly, meta = (ClampMin = "1.0"))',
            body,
        )
        self.assertEqual(body.count("FName "), 3)
        self.assertEqual(body.count("float "), 1)

    def test_in_class_defaults_match_origin_main(self) -> None:
        body = weak_point_body(origin_main(HEADER_NAME))
        defaults = in_class_defaults(body)
        self.assertEqual(defaults, IN_CLASS_DEFAULTS)
        self.assertEqual(defaults.get("Integrity"), "100.f")
        self.assertIn("float Integrity = 100.f;", body)
        self.assertEqual(len(defaults), 1)

    def test_fname_fields_do_not_invent_name_none_or_index_none(self) -> None:
        body = weak_point_body(origin_main(HEADER_NAME))
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("NAME_None", body)
        self.assertNotIn(" = INDEX_NONE", body)
        self.assertNotIn(" = NAME_None", body)
        for field in UNINITIALIZED_FNAMES:
            self.assertIn(f"FName {field};", body)
            self.assertNotIn(f"{field} =", body)
            self.assertNotIn(f"{field} = NAME_None", body)
            self.assertNotIn(f"{field} = INDEX_NONE", body)

    def test_required_weapon_is_catalog_fname_not_live_station(self) -> None:
        body = weak_point_body(origin_main(HEADER_NAME))
        self.assertIn("FName RequiredWeapon;", body)
        self.assertNotIn("ESkyguardBossWeapon", body)
        self.assertNotIn("RequiredWeapon =", body)
        self.assertNotIn("ESkyguardGunshipWeapon", body)
        self.assertNotIn("Rifle", body)
        self.assertNotIn("Igla", body)
        self.assertNotIn("Hydra", body)
        self.assertNotIn("Hellfire", body)
        self.assertNotIn("30 mm", body)
        self.assertNotIn("30mm", body)

    def test_struct_does_not_re_lock_boss_phase_or_weapon_enum(self) -> None:
        body = weak_point_body(origin_main(HEADER_NAME))
        self.assertNotIn("enum class ESkyguardBossPhase", body)
        self.assertNotIn("enum class ESkyguardBossWeapon", body)
        self.assertNotIn("ESkyguardBossPhase", body)
        self.assertNotIn("ESkyguardBossWeapon", body)
        self.assertNotIn("enum class", body)
        for enumerator in BOSS_PHASE_ENUMERATORS_OWNED_BY_162:
            self.assertNotIn(enumerator, body)

    def test_struct_does_not_re_lock_siblings_or_harbor(self) -> None:
        body = weak_point_body(origin_main(HEADER_NAME))
        for name in OTHER_TYPES:
            self.assertNotIn(name, body)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        self.assertNotIn("enum class", body)
        self.assertNotIn("struct FSkyguardBossDefinition", body)

    def test_struct_bans_igla_yak_rifle(self) -> None:
        lowered = weak_point_body(origin_main(HEADER_NAME)).lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"FSkyguardBossWeakPointDefinition contains {banned}",
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
