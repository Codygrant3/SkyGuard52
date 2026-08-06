from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"


def text(name: str) -> str:
    return (SOURCE / name).read_text(encoding="utf-8-sig")


def between(source: str, start: str, end: str) -> str:
    begin = source.index(start)
    finish = source.index(end, begin)
    return source[begin:finish]


class CampaignSortieFlowContractTests(unittest.TestCase):
    def test_debrief_is_a_blueprint_safe_presentation_contract(self) -> None:
        types = text("SkyguardMissionTypes.h")
        self.assertIn("enum class ESkyguardMissionDebriefState", types)
        self.assertIn("struct FSkyguardMissionDebrief", types)
        for field in (
            "FSkyguardMissionResult Result",
            "FText Narrative",
            "bool bNewBestScore",
            "bool bNewBestMedal",
            "bool bProgressSaved",
            "FName NextMissionId",
            "TSoftObjectPtr<UWorld> NextMissionMap",
            "bool bNextMissionUnlocked",
            "bool bCampaignComplete",
        ):
            self.assertIn(field, types)

    def test_completion_builds_debrief_before_clearing_active_mission(self) -> None:
        source = text("SkyguardCampaignSubsystem.cpp")
        completion = between(
            source,
            "bool USkyguardCampaignSubsystem::CompleteActiveMission",
            "void USkyguardCampaignSubsystem::BuildSuccessDebrief",
        )
        build = completion.index("BuildSuccessDebrief(")
        clear = completion.index("ActiveMission = nullptr")
        self.assertLess(build, clear)
        self.assertIn("CompletedMission.Presentation.SuccessDebrief", source)
        self.assertIn("IsMissionUnlocked(NextMission->MissionId)", source)

    def test_finalize_scores_then_persists_with_visible_save_status(self) -> None:
        source = text("SkyguardCampaignSubsystem.cpp")
        finalize = between(
            source,
            "bool USkyguardCampaignSubsystem::FinalizeActiveMission",
            "bool USkyguardCampaignSubsystem::RetrySaveLastDebrief",
        )
        self.assertLess(
            finalize.index("CompleteActiveMission(InOutResult)"),
            finalize.index("SaveCampaignToSlot(SlotName, UserIndex)"),
        )
        self.assertIn("LastDebrief.bProgressSaved", finalize)
        self.assertIn("RetrySaveLastDebrief", source)

    def test_travel_requires_acknowledged_saved_unlocked_map(self) -> None:
        source = text("SkyguardCampaignSubsystem.cpp")
        gate = between(
            source,
            "bool USkyguardCampaignSubsystem::CanTravelToNextMission",
            "bool USkyguardCampaignSubsystem::TravelToNextMission",
        )
        for condition in (
            "ESkyguardMissionDebriefState::Acknowledged",
            "LastDebrief.bProgressSaved",
            "LastDebrief.bNextMissionUnlocked",
            "!GetNextMissionMapPackageName().IsEmpty()",
        ):
            self.assertIn(condition, gate)
        self.assertIn("UGameplayStatics::OpenLevel(", source)

    def test_m01_template_finalizes_instead_of_discarding_result(self) -> None:
        source = text("SkyguardMission01IntegrationDirector.cpp")
        completion = between(
            source,
            "void ASkyguardMission01IntegrationDirector::CompleteMissionIfReady",
            "void ASkyguardMission01IntegrationDirector::HandleBossPhaseChanged",
        )
        self.assertIn("CampaignRuntime->FinalizeActiveMission(", completion)
        self.assertNotIn(
            "CampaignRuntime->CompleteActiveMission(Result)",
            completion,
        )
        header = text("SkyguardMission01IntegrationDirector.h")
        self.assertIn("CampaignSaveSlotName", header)
        self.assertIn("CampaignSaveUserIndex", header)

    def test_native_automation_covers_full_non_visual_lifecycle(self) -> None:
        tests = text("SkyguardCampaignTests.cpp")
        self.assertIn(
            "Skyguard52.Campaign.Sortie."
            "BriefingToDebriefSaveAndTravelContract",
            tests,
        )
        for assertion in (
            "Sortie is blocked while the briefing warms",
            "Player acknowledges the briefing",
            "Debrief uses authored success copy",
            "Debrief exposes deterministic score",
            "Sortie progression persists before travel",
            "Travel remains gated until debrief acknowledgment",
            "Next mission unlock survives persistence",
        ):
            self.assertIn(assertion, tests)


if __name__ == "__main__":
    unittest.main()
