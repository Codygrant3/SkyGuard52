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
    "Scripts/tests/test_mission_debrief_state_enum_contract.py",
    "Scripts/tests/test_mission_objective_formation_enum_contract.py",
    "Scripts/tests/test_mission_weather_enum_contract.py",
)
PUBLIC_FIELDS = (
    "ESkyguardMissionDebriefState State =\n"
    "\t\tESkyguardMissionDebriefState::Unavailable;",
    "FSkyguardMissionResult Result;",
    "FText MissionDisplayName;",
    "FText Narrative;",
    "bool bNewBestScore = false;",
    "bool bNewBestMedal = false;",
    "bool bProgressSaved = false;",
    "FString SaveSlotName;",
    "FName NextMissionId;",
    "FText NextMissionDisplayName;",
    "TSoftObjectPtr<UWorld> NextMissionMap;",
    "bool bNextMissionUnlocked = false;",
    "bool bCampaignComplete = false;",
)
IN_CLASS_DEFAULTS = {
    "State": "ESkyguardMissionDebriefState::Unavailable",
    "bNewBestScore": "false",
    "bNewBestMedal": "false",
    "bProgressSaved": "false",
    "bNextMissionUnlocked": "false",
    "bCampaignComplete": "false",
}
BANNED = ("igla", "yak", "rifle")
OTHER_ENUMS = (
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


def debrief_body(header: str) -> str:
    start = header.index("struct FSkyguardMissionDebrief")
    brace = header.index("{", start)
    finish = header.index("};", brace)
    return header[brace : finish + 2]


def in_class_defaults(body: str) -> dict[str, str]:
    return {
        name: re.sub(r"\s+", " ", value).strip()
        for name, value in re.findall(
            r"(?:ESkyguardMissionDebriefState|bool)\s+(\w+)\s*=\s*([^;]+);",
            body,
        )
    }


class MissionDebriefDefaultsContractTests(unittest.TestCase):
    def test_debrief_struct_exists(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn("struct FSkyguardMissionDebrief", header)
        self.assertIn("USTRUCT(BlueprintType)", header)
        self.assertIn("GENERATED_BODY()", debrief_body(header))

    def test_public_fields_match_origin_main_in_order(self) -> None:
        body = debrief_body(origin_main(HEADER_NAME))
        positions = [body.index(field) for field in PUBLIC_FIELDS]
        self.assertEqual(positions, sorted(positions), PUBLIC_FIELDS)
        for field in PUBLIC_FIELDS:
            self.assertIn(field, body)

    def test_in_class_defaults_match_origin_main(self) -> None:
        body = debrief_body(origin_main(HEADER_NAME))
        self.assertEqual(in_class_defaults(body), IN_CLASS_DEFAULTS)
        self.assertIn(
            "ESkyguardMissionDebriefState State =\n"
            "\t\tESkyguardMissionDebriefState::Unavailable;",
            body,
        )
        self.assertIn("bool bNewBestScore = false;", body)
        self.assertIn("bool bNewBestMedal = false;", body)
        self.assertIn("bool bProgressSaved = false;", body)
        self.assertIn("bool bNextMissionUnlocked = false;", body)
        self.assertIn("bool bCampaignComplete = false;", body)

    def test_struct_does_not_invent_index_none(self) -> None:
        body = debrief_body(origin_main(HEADER_NAME))
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("NAME_None", body)
        self.assertNotIn("NextMissionId =", body)
        self.assertNotIn("SaveSlotName =", body)
        self.assertNotIn("Result =", body)
        self.assertNotIn("MissionDisplayName =", body)
        self.assertNotIn("Narrative =", body)
        self.assertNotIn("NextMissionDisplayName =", body)
        self.assertNotIn("NextMissionMap =", body)

    def test_struct_does_not_re_lock_other_enums_or_harbor(self) -> None:
        body = debrief_body(origin_main(HEADER_NAME))
        for name in OTHER_ENUMS:
            self.assertNotIn(name, body)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        self.assertNotIn("enum class ESkyguardMissionDebriefState", body)

    def test_struct_bans_igla_yak_rifle(self) -> None:
        lowered = debrief_body(origin_main(HEADER_NAME)).lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"FSkyguardMissionDebrief contains {banned}",
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
