from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"


def source_text(name: str) -> str:
    return (SOURCE / name).read_text(encoding="utf-8-sig")


def function_body(source: str, signature: str, next_signature: str) -> str:
    start = source.index(signature)
    end = source.index(next_signature, start)
    return source[start:end]


class Mission09CampaignHandoffContractTests(unittest.TestCase):
    def test_director_binds_the_governed_campaign_asset(self) -> None:
        header = source_text("SkyguardMission09IntegrationDirector.h")
        source = source_text("SkyguardMission09IntegrationDirector.cpp")
        self.assertIn(
            "TSoftObjectPtr<USkyguardCampaignDefinition> CampaignDefinition",
            header,
        )
        self.assertIn(
            "/Game/Skyguard/Data/Campaign_v1/DA_Campaign_Skyguard52."
            "DA_Campaign_Skyguard52",
            source,
        )
        self.assertIn(
            "GameInstance->GetSubsystem<USkyguardCampaignSubsystem>()",
            source,
        )
        self.assertIn("Runtime->StartMission(GetMissionId())", source)

    def test_objective_events_route_to_the_active_campaign_runtime(self) -> None:
        source = source_text("SkyguardMission09IntegrationDirector.cpp")
        progress = function_body(
            source,
            "bool ASkyguardMission09IntegrationDirector::NotifyObjectiveProgress",
            "void ASkyguardMission09IntegrationDirector::FailObjective",
        )
        failure = function_body(
            source,
            "void ASkyguardMission09IntegrationDirector::FailObjective",
            "void ASkyguardMission09IntegrationDirector::CompleteMissionIfReady",
        )
        self.assertIn(
            "CampaignRuntime->GetActiveMission() == ResolvedMission",
            progress,
        )
        self.assertIn(
            "CampaignRuntime->AddObjectiveProgress(ObjectiveId, Amount)",
            progress,
        )
        self.assertIn(
            "LocalObjectiveRuntime->AddProgress(ObjectiveId, Amount)",
            progress,
        )
        self.assertIn("CampaignRuntime->FailObjective(ObjectiveId)", failure)
        self.assertIn("LocalObjectiveRuntime->FailObjective(ObjectiveId)", failure)

    def test_success_records_m09_before_marking_the_wave_complete(self) -> None:
        source = source_text("SkyguardMission09IntegrationDirector.cpp")
        completion = function_body(
            source,
            "void ASkyguardMission09IntegrationDirector::CompleteMissionIfReady",
            "FSkyguardMission09ProtectedTargetRuntime*",
        )
        campaign_completion = completion.index(
            "CampaignRuntime->CompleteActiveMission(Result)"
        )
        wave_completion = completion.index(
            "WaveState = ESkyguardMission09WaveState::Completed"
        )
        self.assertLess(campaign_completion, wave_completion)
        self.assertIn("Objectives->HasTerminalFailure()", completion)
        self.assertIn("Objectives->AreRequiredObjectivesComplete()", completion)

    def test_native_regression_covers_record_and_finale_unlock(self) -> None:
        tests = source_text("SkyguardMission09IntegrationTests.cpp")
        self.assertIn(
            "Skyguard52.Mission09.Campaign."
            "CompletionRecordsAndUnlocksFinale",
            tests,
        )
        self.assertIn(
            'Runtime->GetMissionRecords().Find(',
            tests,
        )
        self.assertIn(
            'Runtime->IsMissionUnlocked(TEXT("M10_EvacuationFinale"))',
            tests,
        )

    def test_campaign_authoring_keeps_m10_directly_behind_m09(self) -> None:
        build_script = (
            ROOT / "Scripts" / "build_skyguard_phase7_campaign_v1.py"
        ).read_text(encoding="utf-8-sig")
        mission_ids = re.findall(r'"id": "(M\d{2}_[A-Za-z0-9]+)"', build_script)
        self.assertIn("M09_SaturationAttack", mission_ids)
        self.assertIn("M10_EvacuationFinale", mission_ids)
        self.assertEqual(
            mission_ids.index("M09_SaturationAttack") + 1,
            mission_ids.index("M10_EvacuationFinale"),
        )
        self.assertIn(
            '[unreal.Name(MISSIONS[order - 2]["id"])] if order > 1 else []',
            build_script,
        )


if __name__ == "__main__":
    unittest.main()
