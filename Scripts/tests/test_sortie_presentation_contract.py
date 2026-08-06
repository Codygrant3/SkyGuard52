from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"


def text(name: str) -> str:
    return (SOURCE / name).read_text(encoding="utf-8-sig")


class SortiePresentationContractTests(unittest.TestCase):
    def test_component_is_umg_bindable_without_owning_widget_layout(self) -> None:
        header = text("SkyguardSortiePresentationComponent.h")
        self.assertIn(
            "class SKYGUARD52_API USkyguardSortiePresentationComponent",
            header,
        )
        self.assertIn("meta=(BlueprintSpawnableComponent)", header)
        self.assertIn("FSkyguardSortiePresentationStateChanged", header)
        self.assertNotIn("UUserWidget", header)

    def test_dense_briefing_contract_exposes_semantic_pictograms(self) -> None:
        header = text("SkyguardSortiePresentationComponent.h")
        for pictogram in (
            "Mission",
            "Route",
            "DroneSwarm",
            "ProtectedAsset",
            "Boss",
            "Rifle",
            "Igla",
            "Weather",
            "Radio",
        ):
            self.assertIn(pictogram, header)
        for structure in (
            "FSkyguardBriefingCard",
            "FSkyguardBriefingRadioRow",
            "FSkyguardHowToFlyRow",
        ):
            self.assertIn(f"struct {structure}", header)

    def test_briefing_rows_derive_from_mission_data(self) -> None:
        source = text("SkyguardSortiePresentationComponent.cpp")
        for governed_input in (
            "MissionDefinition->Route.Points",
            "MissionDefinition->Waves",
            "MissionDefinition->Objectives",
            "MissionDefinition->Boss.WeakPoints",
            "MissionDefinition->Weather",
            "MissionDefinition->Presentation.RadioChatter",
        ):
            self.assertIn(governed_input, source)
        for required_card in (
            'TEXT("MissionDirective")',
            'TEXT("FlightRoute")',
            'TEXT("ThreatPicture")',
            'TEXT("BossProfile")',
            'TEXT("Weather")',
        ):
            self.assertIn(required_card, source)

    def test_how_to_fly_includes_immersive_weapon_and_safety_guidance(self) -> None:
        source = text("SkyguardSortiePresentationComponent.cpp")
        for step in (
            "ScanRearArc",
            "AimIronSights",
            "FireRifle",
            "EmployIgla",
            "ProtectObjective",
        ):
            self.assertIn(f'TEXT("{step}")', source)
        self.assertIn("no HUD reticle", source)
        self.assertIn("pilot safety arc", source)

    def test_debrief_state_machine_exposes_save_retry_ack_and_travel(self) -> None:
        header = text("SkyguardSortiePresentationComponent.h")
        for state in (
            "DebriefReady",
            "SaveFailure",
            "TravelReady",
            "TravelBlocked",
            "CampaignComplete",
        ):
            self.assertIn(state, header)
        source = text("SkyguardSortiePresentationComponent.cpp")
        self.assertIn("RetrySaveLastDebrief", source)
        self.assertIn("AcknowledgeDebrief", source)
        self.assertIn("TravelToNextMission", source)
        self.assertIn("Debrief.bProgressSaved", source)

    def test_m01_owns_and_updates_the_reusable_component(self) -> None:
        header = text("SkyguardMission01IntegrationDirector.h")
        source = text("SkyguardMission01IntegrationDirector.cpp")
        self.assertIn(
            "TObjectPtr<USkyguardSortiePresentationComponent> "
            "SortiePresentation",
            header,
        )
        self.assertIn(
            "SortiePresentation->ConfigureFromMission(ResolvedMission)",
            source,
        )
        self.assertIn(
            "SortiePresentation->BindCampaignRuntime(CampaignRuntime)",
            source,
        )
        self.assertIn("SortiePresentation->SetSortieLaunched()", source)
        self.assertIn("SortiePresentation->RefreshDebrief()", source)

    def test_native_tests_cover_briefing_and_debrief_states(self) -> None:
        tests = text("SkyguardSortiePresentationTests.cpp")
        self.assertIn(
            "Skyguard52.Presentation.Sortie.DenseMissionSpecificBriefing",
            tests,
        )
        self.assertIn(
            "Skyguard52.Presentation.Sortie."
            "DebriefSaveRetryAckAndTravelStates",
            tests,
        )
        for evidence in (
            "Dense briefing provides at least seven cards",
            "Save failure becomes an explicit UI state",
            "Player can retry persistence",
            "Acknowledged saved sortie becomes travel-ready",
        ):
            self.assertIn(evidence, tests)


if __name__ == "__main__":
    unittest.main()
