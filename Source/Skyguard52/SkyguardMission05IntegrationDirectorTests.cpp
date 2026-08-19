#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardMission05IntegrationDirector.h"

#include "SkyguardMissionDefinition.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

// Neighbor of SkyguardMission05IntegrationTests.cpp.
// Public director API only: nullptr map/Yak/Gunner/Tempest, no Tempest spawn,
// no rifle/Igla hits, no AdvanceStabilizedIglaLock.

namespace SkyguardMission05IntegrationDirectorTests
{
	static const TCHAR* MissionAssetPath =
		TEXT("/Game/Skyguard/Data/Campaign_v1/DA_Mission_M05_StormFront.DA_Mission_M05_StormFront");

	class FWorldScope
	{
	public:
		FWorldScope()
		{
			World = UWorld::CreateWorld(
				EWorldType::Game, false,
				TEXT("SkyguardMission05DirectorTestWorld"));
			check(World);
			FWorldContext& Context =
				GEngine->CreateNewWorldContext(EWorldType::Game);
			Context.SetCurrentWorld(World);
		}
		~FWorldScope()
		{
			if (World)
			{
				GEngine->DestroyWorldContext(World);
				World->DestroyWorld(false);
			}
		}
		UWorld* Get() const { return World; }
	private:
		UWorld* World = nullptr;
	};

	USkyguardMissionDefinition* TryLoadMission()
	{
		return LoadObject<USkyguardMissionDefinition>(
			nullptr, MissionAssetPath);
	}

	USkyguardMissionDefinition* MakeIsolatedStormFrontDefinition()
	{
		USkyguardMissionDefinition* Mission =
			NewObject<USkyguardMissionDefinition>();
		Mission->MissionId =
			ASkyguardMission05IntegrationDirector::GetMissionId();
		Mission->DisplayName = FText::FromString(TEXT("Storm Front"));
		for (int32 Index = 0; Index < 4; ++Index)
		{
			FSkyguardRoutePoint Point;
			Point.PointId =
				FName(*FString::Printf(TEXT("M05_Isolated_P%d"), Index));
			Point.WorldLocation = FVector(Index * 12000.f, 0.f, 8000.f);
			Mission->Route.Points.Add(Point);
		}

		FSkyguardObjectiveDefinition Protect;
		Protect.ObjectiveId = TEXT("ProtectOffshoreCrew");
		Protect.RequiredProgress = 1;
		FSkyguardObjectiveDefinition Disable;
		Disable.ObjectiveId = TEXT("DisableDischargeBooms");
		Disable.RequiredProgress = 2;
		FSkyguardObjectiveDefinition Defeat;
		Defeat.ObjectiveId = TEXT("DefeatTempest");
		Defeat.RequiredProgress = 4;
		Mission->Objectives = {Protect, Disable, Defeat};

		Mission->Boss.BossId = TEXT("Tempest");
		Mission->Boss.DefeatObjectiveId = TEXT("DefeatTempest");
		Mission->Boss.MaximumBreakupPieces = 3;
		const FName WeakPointIds[] = {
			TEXT("PortDischargeBoom"),
			TEXT("StarboardDischargeBoom"),
			TEXT("ControlServo"),
			TEXT("EngineIntake")};
		const FName RequiredWeapons[] = {
			TEXT("Rifle"), TEXT("Rifle"),
			TEXT("Rifle"), TEXT("Igla")};
		const FName Exposes[] = {
			TEXT("ControlServo"), TEXT("ControlServo"),
			TEXT("EngineIntake"), NAME_None};
		for (int32 Index = 0; Index < 4; ++Index)
		{
			FSkyguardBossWeakPointDefinition Point;
			Point.WeakPointId = WeakPointIds[Index];
			Point.RequiredWeapon = RequiredWeapons[Index];
			Point.ExposesWeakPointId = Exposes[Index];
			Mission->Boss.WeakPoints.Add(Point);
		}

		for (int32 Index = 0; Index < 3; ++Index)
		{
			FSkyguardEnemyWaveDefinition Wave;
			Wave.WaveId =
				FName(*FString::Printf(TEXT("M05_Isolated_Wave_%d"), Index + 1));
			Mission->Waves.Add(Wave);
		}
		Mission->Weather.ProfileId = TEXT("SevereSquall");
		Mission->Presentation.Briefing =
			FText::FromString(TEXT("Isolated Mission 5 storm contract."));
		Mission->Presentation.RadioChatter = {
			FText::FromString(TEXT("Isolated radio 1")),
			FText::FromString(TEXT("Isolated radio 2")),
			FText::FromString(TEXT("Isolated radio 3"))};
		return Mission;
	}

	ASkyguardMission05IntegrationDirector* SpawnBoundDirector(UWorld* World)
	{
		ASkyguardMission05IntegrationDirector* Director =
			World->SpawnActor<ASkyguardMission05IntegrationDirector>();
		if (!Director)
		{
			return nullptr;
		}
		Director->bAutoInitialize = false;
		Director->bAllowBoundedActorSpawning = false;
		Director->BindRuntimeActors(nullptr, nullptr, nullptr, nullptr);
		return Director;
	}

	void AssertStormRuntimeAsImplemented(
		FAutomationTestBase& Test,
		const ASkyguardMission05IntegrationDirector* Director,
		const float ExpectedTurbulence,
		const bool bExpectedMaintainingAim)
	{
		const FSkyguardStormRuntime& Storm = Director->GetStormRuntime();
		Test.TestFalse(
			TEXT("Lightning stays inactive without Tempest"),
			Storm.bLightningActive);
		Test.TestEqual(
			TEXT("Lightning remaining seconds stay at implementation default"),
			Storm.LightningRemainingSeconds,
			0.f);
		Test.TestEqual(
			TEXT("Lightning flash count stays at implementation default"),
			Storm.LightningFlashCount,
			0);
		Test.TestEqual(
			TEXT("Turbulence matches isolated AdvanceTurbulence result"),
			Storm.Turbulence,
			ExpectedTurbulence);
		if (bExpectedMaintainingAim)
		{
			Test.TestTrue(
				TEXT("Aim-hold matches isolated AdvanceTurbulence result"),
				Storm.bMaintainingAim);
		}
		else
		{
			Test.TestFalse(
				TEXT("Aim-hold matches isolated AdvanceTurbulence result"),
				Storm.bMaintainingAim);
		}
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission05DirectorMissionIdNullContractAndStormRuntimeTest,
	"Skyguard52.Mission05.Director.MissionIdNullContractAndStormRuntime",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission05DirectorMissionIdNullContractAndStormRuntimeTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMission05IntegrationDirectorTests;

	TestEqual(
		TEXT("GetMissionId is M05_StormFront"),
		ASkyguardMission05IntegrationDirector::GetMissionId(),
		FName(TEXT("M05_StormFront")));

	TArray<FText> NullContractErrors;
	TestFalse(
		TEXT("ValidateMissionContract rejects a null definition"),
		ASkyguardMission05IntegrationDirector::ValidateMissionContract(
			nullptr, NullContractErrors));
	TestTrue(
		TEXT("Null contract reports at least one error"),
		NullContractErrors.Num() > 0);

	FWorldScope Scope;
	ASkyguardMission05IntegrationDirector* Director =
		SpawnBoundDirector(Scope.Get());
	TestNotNull(TEXT("Director spawns without Yak, Gunner, or Tempest"), Director);
	if (!Director)
	{
		return false;
	}

	TestFalse(
		TEXT("TriggerLightningWindow is fail-closed without Tempest"),
		Director->TriggerLightningWindow(2.f));
	TestFalse(
		TEXT("AdvanceLightningWindow is fail-closed while lightning is inactive"),
		Director->AdvanceLightningWindow(1.f));
	AssertStormRuntimeAsImplemented(*this, Director, 0.f, false);

	TestFalse(
		TEXT("AdvanceTurbulence is fail-closed without Tempest"),
		Director->AdvanceTurbulence(1.f, 0.75f, true));
	AssertStormRuntimeAsImplemented(*this, Director, 0.f, false);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission05DirectorContractAndProtectedTargetTest,
	"Skyguard52.Mission05.Director.ContractAndProtectedTargetIntegrity",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission05DirectorContractAndProtectedTargetTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMission05IntegrationDirectorTests;

	USkyguardMissionDefinition* Mission = TryLoadMission();
	if (Mission)
	{
		TArray<FText> Errors;
		TestTrue(
			TEXT("Loaded Mission 5 contract validates"),
			ASkyguardMission05IntegrationDirector::ValidateMissionContract(
				Mission, Errors));
		TestEqual(TEXT("Loaded contract emits no errors"), Errors.Num(), 0);
	}
	else
	{
		AddWarning(TEXT(
			"Mission 5 DataAsset unavailable; using an isolated in-memory "
			"contract so public-API protected-target tests still run."));
		Mission = MakeIsolatedStormFrontDefinition();
		TArray<FText> IsolatedErrors;
		if (!ASkyguardMission05IntegrationDirector::ValidateMissionContract(
				Mission, IsolatedErrors))
		{
			AddError(TEXT("Isolated Mission 5 contract must validate."));
			return false;
		}
	}

	FWorldScope Scope;
	ASkyguardMission05IntegrationDirector* Director =
		SpawnBoundDirector(Scope.Get());
	TestNotNull(TEXT("Director binds nullptr map/Yak/Gunner/Tempest"), Director);
	if (!Director)
	{
		return false;
	}

	TestTrue(
		TEXT("Director configures from the isolated or loaded mission"),
		Director->ConfigureMissionDefinition(Mission));
	TestEqual(
		TEXT("Both protected targets start intact"),
		Director->GetSurvivingTargetCount(),
		2);

	TestTrue(
		TEXT("Offshore platform accepts bounded damage"),
		Director->NotifyProtectedTargetDamage(
			ESkyguardMission05ProtectedTarget::OffshorePlatform, 25));
	const FSkyguardMission05ProtectedTargetRuntime PlatformAfterHit =
		Director->GetProtectedTarget(
			ESkyguardMission05ProtectedTarget::OffshorePlatform);
	TestEqual(
		TEXT("Platform integrity drops by the applied damage"),
		PlatformAfterHit.Integrity,
		Director->MaximumProtectedTargetIntegrity - 25);
	TestFalse(TEXT("Damaged platform is not destroyed"), PlatformAfterHit.bDestroyed);

	TestTrue(
		TEXT("Distressed trawler accepts bounded damage"),
		Director->NotifyProtectedTargetDamage(
			ESkyguardMission05ProtectedTarget::DistressedTrawler, 40));
	const FSkyguardMission05ProtectedTargetRuntime TrawlerAfterHit =
		Director->GetProtectedTarget(
			ESkyguardMission05ProtectedTarget::DistressedTrawler);
	TestEqual(
		TEXT("Trawler integrity drops by the applied damage"),
		TrawlerAfterHit.Integrity,
		Director->MaximumProtectedTargetIntegrity - 40);
	TestFalse(TEXT("Damaged trawler is not destroyed"), TrawlerAfterHit.bDestroyed);
	TestEqual(
		TEXT("Both targets still survive after partial damage"),
		Director->GetSurvivingTargetCount(),
		2);

	TestTrue(
		TEXT("Wiping the platform is accepted"),
		Director->NotifyProtectedTargetDamage(
			ESkyguardMission05ProtectedTarget::OffshorePlatform,
			Director->MaximumProtectedTargetIntegrity));
	const FSkyguardMission05ProtectedTargetRuntime WipedPlatform =
		Director->GetProtectedTarget(
			ESkyguardMission05ProtectedTarget::OffshorePlatform);
	TestEqual(TEXT("Wiped platform integrity is zero"), WipedPlatform.Integrity, 0);
	TestTrue(TEXT("Wiped platform is marked destroyed"), WipedPlatform.bDestroyed);
	TestEqual(
		TEXT("Surviving target count drops after one wipe"),
		Director->GetSurvivingTargetCount(),
		1);
	return true;
}

#endif
