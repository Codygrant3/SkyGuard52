from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_NAME = "SkyguardMissionBriefingComponent.h"
IMPLEMENTATION_NAME = "SkyguardMissionBriefingComponent.cpp"
LOCKED = {
    "SkyguardMissionBriefingComponent.h",
    "SkyguardMissionBriefingComponent.cpp",
    "SkyguardMissionBriefingComponentTests.cpp",
    "SkyguardMissionBriefingFailClosedTests.cpp",
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
LIVE_BRIEFING_STATES = [
    "Unconfigured",
    "Warming",
    "Ready",
    "Launched",
]
PUBLIC_API = (
    "bool ConfigureFromMission(USkyguardMissionDefinition* Mission);",
    "void SetAssetsReady(bool bReady);",
    "void AdvanceBriefing(float DeltaSeconds);",
    "bool AcknowledgeAndLaunch();",
    "bool CanLaunch() const;",
    "ESkyguardMissionBriefingState GetBriefingState() const { return State; }",
    "float GetElapsedSeconds() const { return ElapsedSeconds; }",
    "float GetMinimumWarmupSeconds() const { return MinimumWarmupSeconds; }",
    "FText GetBriefingText() const { return BriefingText; }",
    "TArray<FText> GetRadioChatter() const { return RadioChatter; }",
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


def enum_body(header: str, enum_name: str) -> str:
    start = header.index(f"enum class {enum_name}")
    brace = header.index("{", start)
    finish = header.index("}", brace)
    return header[brace : finish + 1]


def enum_enumerators(header: str, enum_name: str) -> list[str]:
    return re.findall(
        r"^\s*([A-Za-z_][A-Za-z0-9_]*)\b",
        enum_body(header, enum_name),
        re.M,
    )


class MissionBriefingStateEnumContractTests(unittest.TestCase):
    def test_briefing_state_enum_exists(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn("enum class ESkyguardMissionBriefingState : uint8", header)
        self.assertIn("UENUM(BlueprintType)", header)

    def test_enumerators_match_live_order(self) -> None:
        header = origin_main(HEADER_NAME)
        enumerators = enum_enumerators(header, "ESkyguardMissionBriefingState")
        self.assertEqual(enumerators, LIVE_BRIEFING_STATES)
        self.assertEqual(
            enumerators,
            [
                "Unconfigured",
                "Warming",
                "Ready",
                "Launched",
            ],
        )
        self.assertEqual(len(enumerators), 4, enumerators)
        body = enum_body(header, "ESkyguardMissionBriefingState")
        for name in LIVE_BRIEFING_STATES:
            self.assertIn(name, body)
            self.assertIn(name, enumerators)

    def test_public_api_matches_origin_main_header(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn("class SKYGUARD52_API USkyguardMissionBriefingComponent", header)
        for signature in PUBLIC_API:
            self.assertIn(signature, header)
        self.assertIn('Category="Skyguard|Briefing"', header)
        self.assertIn("ESkyguardMissionBriefingState GetBriefingState() const", header)
        self.assertIn(
            "ESkyguardMissionBriefingState State =\n"
            "\t\tESkyguardMissionBriefingState::Unconfigured;",
            header,
        )

    def test_public_api_uses_live_briefing_states(self) -> None:
        implementation = origin_main(IMPLEMENTATION_NAME)
        self.assertIn(
            "State = ESkyguardMissionBriefingState::Unconfigured;",
            implementation,
        )
        self.assertIn(
            "State = ESkyguardMissionBriefingState::Warming;",
            implementation,
        )
        self.assertIn(
            "return State == ESkyguardMissionBriefingState::Ready ||",
            implementation,
        )
        self.assertIn(
            "State == ESkyguardMissionBriefingState::Launched;",
            implementation,
        )
        self.assertIn(
            "State = ESkyguardMissionBriefingState::Launched;",
            implementation,
        )
        self.assertIn(
            "? ESkyguardMissionBriefingState::Ready",
            implementation,
        )
        self.assertIn(
            ": ESkyguardMissionBriefingState::Warming;",
            implementation,
        )
        for name in LIVE_BRIEFING_STATES:
            self.assertIn(f"ESkyguardMissionBriefingState::{name}", implementation)
        for invented in (
            "ESkyguardMissionBriefingState::Unavailable",
            "ESkyguardMissionBriefingState::Acknowledged",
            "ESkyguardMissionBriefingState::Rifle",
            "ESkyguardMissionBriefingState::Igla",
            "ESkyguardMissionBriefingState::Yak",
        ):
            self.assertNotIn(invented, implementation)

    def test_briefing_state_enum_does_not_require_rifle_or_igla(self) -> None:
        enumerators = enum_enumerators(
            origin_main(HEADER_NAME),
            "ESkyguardMissionBriefingState",
        )
        self.assertNotIn("Rifle", enumerators)
        self.assertNotIn("Igla", enumerators)
        self.assertNotIn("Yak", enumerators)
        self.assertNotEqual(enumerators, ["Rifle", "Igla"])

    def test_contract_is_briefing_state_enum_only(self) -> None:
        header = origin_main(HEADER_NAME)
        body = enum_body(header, "ESkyguardMissionBriefingState")
        self.assertIn("Unconfigured", body)
        self.assertIn("Launched", body)
        self.assertNotIn("ESkyguardMissionDebriefState", body)
        self.assertNotIn("ESkyguardMissionObjectiveType", body)
        self.assertNotIn("ESkyguardFormationType", body)
        self.assertNotIn("ESkyguardMissionObjectiveState", body)
        self.assertNotIn("ESkyguardMissionWeather", body)
        self.assertNotIn("Unavailable", body)
        self.assertNotIn("Acknowledged", body)
        self.assertNotIn("DestroyTargets", body)
        self.assertNotIn("ProtectAsset", body)
        self.assertNotIn("EchelonLeft", body)
        self.assertNotIn("LooseSwarm", body)
        self.assertNotIn("Inactive", body)
        self.assertNotIn("Completed", body)
        self.assertNotIn("Clear", body)
        self.assertNotIn("Overcast", body)
        self.assertNotIn("NightClear", body)
        self.assertNotIn("NightOvercast", body)
        self.assertNotIn("RequiredProgress", body)
        self.assertNotIn("ScoreReward", body)
        self.assertNotIn("UnitCount", body)
        self.assertNotIn("SpacingCentimeters", body)
        self.assertNotIn("1000", body)
        self.assertNotIn("1200.f", body)
        self.assertNotIn("40.f", body)
        self.assertNotIn("80.f", body)
        self.assertNotIn("Rifle", body)
        self.assertNotIn("Igla", body)
        self.assertNotIn("Yak", body)
        enumerators = enum_enumerators(header, "ESkyguardMissionBriefingState")
        self.assertEqual(enumerators, LIVE_BRIEFING_STATES)
        self.assertNotEqual(enumerators, ["Rifle", "Igla"])
        self.assertNotEqual(
            enumerators,
            ["Unavailable", "Ready", "Acknowledged"],
        )

    def test_does_not_re_lock_debrief_or_mission_type_enums(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertNotIn("enum class ESkyguardMissionDebriefState", header)
        self.assertNotIn("enum class ESkyguardMissionObjectiveType", header)
        self.assertNotIn("enum class ESkyguardFormationType", header)
        self.assertNotIn("enum class ESkyguardMissionObjectiveState", header)
        self.assertNotIn("enum class ESkyguardMissionWeather", header)
        self.assertEqual(
            header.count("enum class "),
            1,
        )
        self.assertIn("enum class ESkyguardMissionBriefingState : uint8", header)

    def test_locked_files_were_not_the_edit_surface(self) -> None:
        existing = [
            f"Source/Skyguard52/{name}"
            for name in LOCKED
            if (SOURCE / name).exists()
        ]
        for sibling in (
            "Scripts/tests/test_mission_debrief_state_enum_contract.py",
            "Scripts/tests/test_mission_weather_enum_contract.py",
            "Scripts/tests/test_mission_objective_formation_enum_contract.py",
            "Scripts/tests/test_storm_rain_beat_kit_contract.py",
            "Scripts/tests/test_campaign_theater_kit_contract.py",
            "Scripts/tests/test_day_sortie_beat_kit_contract.py",
            "Scripts/tests/test_night_sortie_beat_kit_contract.py",
        ):
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
