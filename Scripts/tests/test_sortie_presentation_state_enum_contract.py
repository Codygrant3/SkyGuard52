from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_NAME = "SkyguardSortiePresentationComponent.h"
IMPLEMENTATION_NAME = "SkyguardSortiePresentationComponent.cpp"
LOCKED = {
    "SkyguardSortiePresentationComponent.h",
    "SkyguardSortiePresentationComponent.cpp",
    "SkyguardSortiePresentationTests.cpp",
    "SkyguardSortiePresentationFailClosedTests.cpp",
    "SkyguardSortiePresentationWidgets.h",
    "SkyguardSortiePresentationWidgets.cpp",
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
LIVE_STATES = [
    "Unconfigured",
    "Briefing",
    "SortieActive",
    "DebriefReady",
    "SaveFailure",
    "TravelReady",
    "TravelBlocked",
    "CampaignComplete",
]
PUBLIC_API = (
    "bool ConfigureFromMission(USkyguardMissionDefinition* Mission);",
    "void BindCampaignRuntime(USkyguardCampaignSubsystem* Runtime);",
    "void SetSortieLaunched();",
    "bool AcknowledgeBriefing();",
    "bool LaunchSortie();",
    "void RefreshDebrief();",
    "void BindGunshipDirector(ASkyguardGunshipSortieDirector* Director);",
    "bool HasCpgDebrief() const { return CpgDebrief.bValid; }",
    "FText GetCpgDebriefCopy() const;",
    "bool SelectLoadoutSlot(int32 Slot);",
    "bool HandleDebriefKey(FKey Key);",
    "bool ContinueSortie();",
    "bool AcknowledgeDebrief();",
    "bool RequestNextMissionTravel(UObject* WorldContextObject);",
    "bool IsConfigured() const { return MissionDefinition != nullptr; }",
    "ESkyguardSortiePresentationState GetPresentationState() const",
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


class SortiePresentationStateEnumContractTests(unittest.TestCase):
    def test_presentation_state_enum_exists(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn(
            "enum class ESkyguardSortiePresentationState : uint8",
            header,
        )
        self.assertIn("UENUM(BlueprintType)", header)

    def test_enumerators_match_live_order(self) -> None:
        header = origin_main(HEADER_NAME)
        enumerators = enum_enumerators(
            header,
            "ESkyguardSortiePresentationState",
        )
        self.assertEqual(enumerators, LIVE_STATES)
        self.assertEqual(
            enumerators,
            [
                "Unconfigured",
                "Briefing",
                "SortieActive",
                "DebriefReady",
                "SaveFailure",
                "TravelReady",
                "TravelBlocked",
                "CampaignComplete",
            ],
        )
        self.assertEqual(len(enumerators), 8, enumerators)
        body = enum_body(header, "ESkyguardSortiePresentationState")
        for name in LIVE_STATES:
            self.assertIn(name, body)
            self.assertIn(name, enumerators)

    def test_public_api_matches_origin_main_header(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn(
            "class SKYGUARD52_API USkyguardSortiePresentationComponent",
            header,
        )
        for signature in PUBLIC_API:
            self.assertIn(signature, header)
        self.assertIn('Category="Skyguard|Sortie Presentation"', header)
        self.assertIn(
            "ESkyguardSortiePresentationState GetPresentationState() const",
            header,
        )
        self.assertIn(
            "FSkyguardSortiePresentationStateChanged",
            header,
        )
        self.assertIn(
            "OnPresentationStateChanged",
            header,
        )
        self.assertIn(
            "ESkyguardSortiePresentationState PresentationState =\n"
            "\t\tESkyguardSortiePresentationState::Unconfigured;",
            header,
        )

    def test_public_api_uses_live_presentation_states(self) -> None:
        implementation = origin_main(IMPLEMENTATION_NAME)
        self.assertIn(
            "SetPresentationState(ESkyguardSortiePresentationState::Unconfigured);",
            implementation,
        )
        self.assertIn(
            "SetPresentationState(ESkyguardSortiePresentationState::Briefing);",
            implementation,
        )
        self.assertIn(
            "PresentationState == ESkyguardSortiePresentationState::Briefing ||",
            implementation,
        )
        self.assertIn(
            "PresentationState == ESkyguardSortiePresentationState::Unconfigured))",
            implementation,
        )
        self.assertIn(
            "SetPresentationState(ESkyguardSortiePresentationState::SortieActive);",
            implementation,
        )
        self.assertIn(
            "? ESkyguardSortiePresentationState::DebriefReady",
            implementation,
        )
        self.assertIn(
            ": ESkyguardSortiePresentationState::SaveFailure);",
            implementation,
        )
        self.assertIn(
            "ESkyguardSortiePresentationState::CampaignComplete);",
            implementation,
        )
        self.assertIn(
            "SetPresentationState(ESkyguardSortiePresentationState::TravelReady);",
            implementation,
        )
        self.assertIn(
            "SetPresentationState(ESkyguardSortiePresentationState::TravelBlocked);",
            implementation,
        )
        self.assertIn(
            "SetPresentationState(ESkyguardSortiePresentationState::DebriefReady);",
            implementation,
        )
        for name in LIVE_STATES:
            self.assertIn(f"ESkyguardSortiePresentationState::{name}", implementation)
        for invented in (
            "ESkyguardSortiePresentationState::Unavailable",
            "ESkyguardSortiePresentationState::Ready",
            "ESkyguardSortiePresentationState::Acknowledged",
            "ESkyguardSortiePresentationState::Rifle",
            "ESkyguardSortiePresentationState::Igla",
            "ESkyguardSortiePresentationState::Yak",
            "ESkyguardSortiePresentationState::Warming",
            "ESkyguardSortiePresentationState::Launched",
        ):
            self.assertNotIn(invented, implementation)

    def test_presentation_state_enum_does_not_require_rifle_or_igla(self) -> None:
        enumerators = enum_enumerators(
            origin_main(HEADER_NAME),
            "ESkyguardSortiePresentationState",
        )
        self.assertNotIn("Rifle", enumerators)
        self.assertNotIn("Igla", enumerators)
        self.assertNotIn("Yak", enumerators)
        self.assertNotEqual(enumerators, ["Rifle", "Igla"])

    def test_does_not_lock_briefing_pictogram(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn("enum class ESkyguardBriefingPictogram : uint8", header)
        pictograms = enum_enumerators(header, "ESkyguardBriefingPictogram")
        states = enum_enumerators(header, "ESkyguardSortiePresentationState")
        self.assertEqual(states, LIVE_STATES)
        self.assertNotEqual(states, pictograms)
        self.assertNotIn("Rifle", states)
        self.assertNotIn("Igla", states)
        self.assertNotIn("Yak", states)
        body = enum_body(header, "ESkyguardSortiePresentationState")
        self.assertNotIn("Mission", body)
        self.assertNotIn("Route", body)
        self.assertNotIn("DroneSwarm", body)
        self.assertNotIn("ProtectedAsset", body)
        self.assertNotIn("Boss", body)
        self.assertNotIn("Weather", body)
        self.assertNotIn("Radio", body)

    def test_contract_is_presentation_state_enum_only(self) -> None:
        header = origin_main(HEADER_NAME)
        body = enum_body(header, "ESkyguardSortiePresentationState")
        self.assertIn("Unconfigured", body)
        self.assertIn("CampaignComplete", body)
        self.assertNotIn("ESkyguardBriefingPictogram", body)
        self.assertNotIn("ESkyguardMissionDebriefState", body)
        self.assertNotIn("ESkyguardMissionBriefingState", body)
        self.assertNotIn("ESkyguardMissionWeather", body)
        self.assertNotIn("Warming", body)
        self.assertNotIn("Launched", body)
        self.assertNotIn("Unavailable", body)
        self.assertNotIn("Acknowledged", body)
        self.assertNotIn("DestroyTargets", body)
        self.assertNotIn("ProtectAsset", body)
        self.assertNotIn("40.f", body)
        self.assertNotIn("80.f", body)
        self.assertNotIn("Rifle", body)
        self.assertNotIn("Igla", body)
        self.assertNotIn("Yak", body)
        enumerators = enum_enumerators(header, "ESkyguardSortiePresentationState")
        self.assertEqual(enumerators, LIVE_STATES)
        self.assertNotEqual(enumerators, ["Rifle", "Igla"])
        self.assertNotEqual(
            enumerators,
            ["Unconfigured", "Warming", "Ready", "Launched"],
        )
        self.assertNotEqual(
            enumerators,
            ["Unavailable", "Ready", "Acknowledged"],
        )

    def test_locked_files_were_not_the_edit_surface(self) -> None:
        existing = [
            f"Source/Skyguard52/{name}"
            for name in LOCKED
            if (SOURCE / name).exists()
        ]
        for sibling in (
            "Scripts/tests/test_sortie_presentation_contract.py",
            "Scripts/tests/test_mission_briefing_state_enum_contract.py",
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
