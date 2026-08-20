from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_NAME = "SkyguardMissionTypes.h"
DEFINITION_NAME = "SkyguardMissionDefinition.h"
LOCKED = {
    "SkyguardMissionTypes.h",
    "SkyguardMissionTypesDefaultsTests.cpp",
    "SkyguardMissionBriefingComponent.h",
    "SkyguardMissionBriefingComponent.cpp",
    "SkyguardMissionBriefingComponentTests.cpp",
    "SkyguardMissionBriefingFailClosedTests.cpp",
    "SkyguardSortiePresentationComponent.h",
    "SkyguardSortiePresentationComponent.cpp",
    "SkyguardSortiePresentationTests.cpp",
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
    "Scripts/tests/test_mission_briefing_state_enum_contract.py",
    "Scripts/tests/test_briefing_card_defaults_contract.py",
    "Scripts/tests/test_briefing_fail_closed_tests.py",
    "Scripts/tests/test_mission_debrief_defaults_contract.py",
    "Scripts/tests/test_mission_result_defaults_contract.py",
    "Scripts/tests/test_mission_debrief_state_enum_contract.py",
    "Scripts/tests/test_mission_objective_formation_enum_contract.py",
    "Scripts/tests/test_mission_weather_enum_contract.py",
    "Scripts/tests/test_mission_types_defaults_contract.py",
)
PUBLIC_FIELDS = (
    "FText Briefing;",
    "TArray<FText> RadioChatter;",
    "FText SuccessDebrief;",
    "FText FailureDebrief;",
    "float MinimumBriefingWarmupSeconds = 3.f;",
)
IN_CLASS_DEFAULTS = {
    "MinimumBriefingWarmupSeconds": "3.f",
}
BANNED = ("igla", "yak", "rifle")
# ESkyguardMissionBriefingState belongs to #171.
BRIEFING_STATES_NOT_RELOCKED = (
    "Unconfigured",
    "Warming",
    "Ready",
    "Launched",
)
# FSkyguardBriefingCard belongs to #178.
BRIEFING_CARD_API_NOT_RELOCKED = (
    "FSkyguardBriefingCard",
    "ESkyguardBriefingPictogram",
    "GetBriefingCards",
    "CardId",
    "Pictogram",
)
OTHER_TYPES = (
    "FSkyguardMissionResult",
    "FSkyguardMissionDebrief",
    "FSkyguardBriefingCard",
    "ESkyguardMissionBriefingState",
    "ESkyguardMissionDebriefState",
    "ESkyguardMissionObjectiveType",
    "ESkyguardMissionObjectiveState",
    "ESkyguardFormationType",
    "ESkyguardMissionWeather",
    "ESkyguardBriefingPictogram",
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


def presentation_body(header: str) -> str:
    start = header.index("struct FSkyguardMissionPresentation")
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


class MissionPresentationDefaultsContractTests(unittest.TestCase):
    def test_presentation_struct_exists(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn("struct FSkyguardMissionPresentation", header)
        self.assertIn("USTRUCT(BlueprintType)", header)
        self.assertIn("GENERATED_BODY()", presentation_body(header))

    def test_public_fields_match_origin_main_in_order(self) -> None:
        body = presentation_body(origin_main(HEADER_NAME))
        positions = [body.index(field) for field in PUBLIC_FIELDS]
        self.assertEqual(positions, sorted(positions), PUBLIC_FIELDS)
        for field in PUBLIC_FIELDS:
            self.assertIn(field, body)
        self.assertEqual(body.count("UPROPERTY("), 5)
        self.assertEqual(body.count("UPROPERTY(EditAnywhere, BlueprintReadOnly"), 5)
        self.assertEqual(body.count('meta = (MultiLine = "true")'), 3)
        self.assertIn(
            'UPROPERTY(EditAnywhere, BlueprintReadOnly, meta = (ClampMin = "0.0"))',
            body,
        )

    def test_in_class_defaults_match_origin_main(self) -> None:
        body = presentation_body(origin_main(HEADER_NAME))
        defaults = in_class_defaults(body)
        self.assertEqual(defaults, IN_CLASS_DEFAULTS)
        self.assertEqual(defaults.get("MinimumBriefingWarmupSeconds"), "3.f")
        self.assertIn("float MinimumBriefingWarmupSeconds = 3.f;", body)
        self.assertEqual(list(defaults), ["MinimumBriefingWarmupSeconds"])

    def test_public_api_exposes_presentation_on_mission_definition(self) -> None:
        header = origin_main(DEFINITION_NAME)
        self.assertIn("FSkyguardMissionPresentation Presentation;", header)
        self.assertIn(
            'UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Presentation")',
            header,
        )
        self.assertNotIn("INDEX_NONE", header)
        self.assertNotIn("MinimumBriefingWarmupSeconds =", header)

    def test_struct_does_not_invent_index_none_or_text_array_defaults(self) -> None:
        body = presentation_body(origin_main(HEADER_NAME))
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("NAME_None", body)
        self.assertNotIn("Briefing =", body)
        self.assertNotIn("RadioChatter =", body)
        self.assertNotIn("SuccessDebrief =", body)
        self.assertNotIn("FailureDebrief =", body)

    def test_contract_does_not_relock_briefing_state(self) -> None:
        body = presentation_body(origin_main(HEADER_NAME))
        self.assertNotIn("enum class ESkyguardMissionBriefingState", body)
        self.assertNotIn("ESkyguardMissionBriefingState", body)
        self.assertNotIn("GetBriefingState", body)
        self.assertNotIn("ConfigureFromMission", body)
        self.assertNotIn("AcknowledgeAndLaunch", body)
        for name in BRIEFING_STATES_NOT_RELOCKED:
            self.assertNotIn(f"ESkyguardMissionBriefingState::{name}", body)
            if name != "Ready":
                self.assertNotIn(name, body)

    def test_contract_does_not_relock_briefing_card(self) -> None:
        body = presentation_body(origin_main(HEADER_NAME))
        for name in BRIEFING_CARD_API_NOT_RELOCKED:
            self.assertNotIn(name, body)
        self.assertNotIn("ESkyguardBriefingPictogram::Mission", body)
        self.assertNotIn("int32 Priority = 0;", body)

    def test_struct_does_not_re_lock_siblings_or_harbor(self) -> None:
        body = presentation_body(origin_main(HEADER_NAME))
        for name in OTHER_TYPES:
            self.assertNotIn(name, body)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        self.assertNotIn("enum class", body)

    def test_contract_is_mission_presentation_defaults_only(self) -> None:
        body = presentation_body(origin_main(HEADER_NAME))
        defaults = in_class_defaults(body)
        self.assertEqual(defaults, IN_CLASS_DEFAULTS)
        self.assertNotIn("struct FSkyguardBriefingCard", body)
        self.assertNotIn("enum class ESkyguardMissionBriefingState", body)
        self.assertNotIn("GetBriefingCards", body)
        self.assertNotIn("GetBriefingState", body)
        self.assertNotIn("40.f", body)
        self.assertNotIn("80.f", body)
        self.assertNotIn("INDEX_NONE", body)
        for banned in ("Rifle", "Igla", "Yak"):
            self.assertNotIn(banned, body)
            self.assertNotIn(banned, defaults)
        self.assertNotEqual(list(defaults), ["Rifle", "Igla"])

    def test_struct_bans_igla_yak_rifle(self) -> None:
        lowered = presentation_body(origin_main(HEADER_NAME)).lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"FSkyguardMissionPresentation contains {banned}",
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
