from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_NAME = "SkyguardCampaignSaveGame.h"
LOCKED = {
    "SkyguardCampaignSaveGame.h",
    "SkyguardCampaignSaveGame.cpp",
    "SkyguardCampaignSaveGameEmptyFailClosedTests.cpp",
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
# Isolated-test drafts stay off this lane. Environment-readiness and
# skyline-style enum contracts are pending siblings, not this PR.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_campaign_theater_kit_contract.py",
    "Scripts/tests/test_environment_readiness_defaults_contract.py",
    "Scripts/tests/test_mission_map_readiness_defaults_contract.py",
    "Scripts/tests/test_mission_result_defaults_contract.py",
    "Scripts/tests/test_mission_skyline_style_enum_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_contract.py",
)
PUBLIC_FIELDS = (
    "bool bCompleted = false;",
    "int32 BestScore = 0;",
    "int32 BestMedalTier = 0;",
    "float BestCompletionTimeSeconds = 0.f;",
)
IN_CLASS_DEFAULTS = {
    "bCompleted": "false",
    "BestScore": "0",
    "BestMedalTier": "0",
    "BestCompletionTimeSeconds": "0.f",
}
BANNED = ("igla", "yak", "rifle")
# Identity-migrate helpers and save-version constants belong to #146.
# Mission01 environment-readiness / skyline-style enums stay on their drafts.
OTHER_TYPES = (
    "MigrateCampaignSave",
    "MinSupportedSaveVersion",
    "CurrentSaveVersion",
    "FSkyguardEnvironmentReadiness",
    "FSkyguardMissionMapReadiness",
    "ESkyguardMissionSkylineStyle",
    "FSkyguardMissionResult",
    "FSkyguardMissionDebrief",
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


def record_body(header: str) -> str:
    start = header.index("struct FSkyguardMissionSaveRecord")
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


class MissionSaveRecordDefaultsContractTests(unittest.TestCase):
    def test_save_record_struct_exists(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn("struct FSkyguardMissionSaveRecord", header)
        self.assertIn("USTRUCT(BlueprintType)", header)
        self.assertIn("GENERATED_BODY()", record_body(header))

    def test_public_fields_match_origin_main_in_order(self) -> None:
        body = record_body(origin_main(HEADER_NAME))
        positions = [body.index(field) for field in PUBLIC_FIELDS]
        self.assertEqual(positions, sorted(positions), PUBLIC_FIELDS)
        for field in PUBLIC_FIELDS:
            self.assertIn(field, body)
        self.assertEqual(body.count("UPROPERTY("), 4)
        self.assertIn(
            'UPROPERTY(EditAnywhere, BlueprintReadWrite, meta = (ClampMin = "0", ClampMax = "3"))',
            body,
        )

    def test_in_class_defaults_match_origin_main(self) -> None:
        body = record_body(origin_main(HEADER_NAME))
        defaults = in_class_defaults(body)
        self.assertEqual(defaults, IN_CLASS_DEFAULTS)
        self.assertEqual(defaults.get("bCompleted"), "false")
        self.assertEqual(defaults.get("BestScore"), "0")
        self.assertEqual(defaults.get("BestMedalTier"), "0")
        self.assertEqual(defaults.get("BestCompletionTimeSeconds"), "0.f")
        self.assertIn("bool bCompleted = false;", body)
        self.assertIn("int32 BestScore = 0;", body)
        self.assertIn("int32 BestMedalTier = 0;", body)
        self.assertIn("float BestCompletionTimeSeconds = 0.f;", body)

    def test_struct_does_not_invent_index_none(self) -> None:
        body = record_body(origin_main(HEADER_NAME))
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("NAME_None", body)
        self.assertNotIn(" = INDEX_NONE", body)
        self.assertNotIn(" = NAME_None", body)

    def test_struct_does_not_re_lock_save_game_migrate_or_harbor(self) -> None:
        body = record_body(origin_main(HEADER_NAME))
        for name in OTHER_TYPES:
            self.assertNotIn(name, body)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        self.assertNotIn("static bool MigrateCampaignSave", body)
        self.assertNotIn("static constexpr int32 MinSupportedSaveVersion", body)
        self.assertNotIn("static constexpr int32 CurrentSaveVersion", body)

    def test_struct_bans_igla_yak_rifle(self) -> None:
        lowered = record_body(origin_main(HEADER_NAME)).lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"FSkyguardMissionSaveRecord contains {banned}",
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
