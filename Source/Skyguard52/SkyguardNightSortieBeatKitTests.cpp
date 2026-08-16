#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardNightSortieBeatKit.h"

#include "SkyguardCampaignRoster.h"
#include "SkyguardCpgDebrief.h"
#include "SkyguardGunner.h"
#include "SkyguardMission04IntegrationDirector.h"
#include "SkyguardMission07IntegrationDirector.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

namespace SkyguardNightSortieBeatKitTests
{
	class FWorldScope
	{
	public:
		FWorldScope()
		{
			World = UWorld::CreateWorld(
				EWorldType::Game, false,
				TEXT("SkyguardNightSortieBeatKitWorld"));
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

	bool KitCopyHasBannedTerm(const FSkyguardNightSortieBeatKit& Kit)
	{
		if (SkyguardCpgCopyHasBannedTerm(Kit.MissionId.ToString()) ||
			SkyguardCpgCopyHasBannedTerm(Kit.WeatherIdentity.ToString()))
		{
			return true;
		}
		for (int32 Index = 0; Index < 7; ++Index)
		{
			if (SkyguardCpgCopyHasBannedTerm(Kit.Beats[Index].Call))
			{
				return true;
			}
		}
		return false;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardNightBeatKitSequencesDifferTest,
	"Skyguard52.Campaign.NightBeatKitSequencesDiffer",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardNightBeatKitSequencesDifferTest::RunTest(const FString& Parameters)
{
	const FSkyguardNightSortieBeatKit& NightEyes =
		SkyguardNightSortieBeatKit::NightEyes();
	const FSkyguardNightSortieBeatKit& DownedBird =
		SkyguardNightSortieBeatKit::DownedBird();

	TestEqual(
		TEXT("Night Eyes keys M04"),
		NightEyes.MissionId,
		FName(TEXT("M04_NightBlackout")));
	TestEqual(
		TEXT("Downed Bird keys M07"),
		DownedBird.MissionId,
		FName(TEXT("M07_SearchIntercept")));
	TestEqual(
		TEXT("Night Eyes keeps BlackoutNight"),
		NightEyes.WeatherIdentity,
		FName(TEXT("BlackoutNight")));
	TestEqual(
		TEXT("Downed Bird keeps IslandMist"),
		DownedBird.WeatherIdentity,
		FName(TEXT("IslandMist")));
	TestTrue(
		TEXT("M04 sequence != M07 sequence"),
		SkyguardNightSortieBeatKit::SequencesDiffer(NightEyes, DownedBird));

	const ESkyguardNightSortieBeatKind NightEyesKinds[7] = {
		ESkyguardNightSortieBeatKind::DarkIngress,
		ESkyguardNightSortieBeatKind::ThermalHunt,
		ESkyguardNightSortieBeatKind::RadarVanHunt,
		ESkyguardNightSortieBeatKind::RooftopHeat,
		ESkyguardNightSortieBeatKind::RadarNetCollapse,
		ESkyguardNightSortieBeatKind::MixedSwarm,
		ESkyguardNightSortieBeatKind::Extraction
	};
	const ESkyguardNightSortieBeatKind DownedBirdKinds[7] = {
		ESkyguardNightSortieBeatKind::IslandIngress,
		ESkyguardNightSortieBeatKind::SearchIsland,
		ESkyguardNightSortieBeatKind::HoldTheWreck,
		ESkyguardNightSortieBeatKind::RescuePressure,
		ESkyguardNightSortieBeatKind::RescueLift,
		ESkyguardNightSortieBeatKind::MixedSwarm,
		ESkyguardNightSortieBeatKind::Extraction
	};
	for (int32 Index = 0; Index < 7; ++Index)
	{
		TestEqual(
			*FString::Printf(TEXT("Night Eyes beat %d is radar-net hunt"), Index),
			NightEyes.Beats[Index].Kind,
			NightEyesKinds[Index]);
		TestEqual(
			*FString::Printf(TEXT("Downed Bird beat %d is hold-the-wreck / search island"), Index),
			DownedBird.Beats[Index].Kind,
			DownedBirdKinds[Index]);
	}

	TestEqual(
		TEXT("ForMission(M04) is Night Eyes"),
		SkyguardNightSortieBeatKit::ForMission(TEXT("M04_NightBlackout")).MissionId,
		NightEyes.MissionId);
	TestEqual(
		TEXT("ForMission(M07) is Downed Bird"),
		SkyguardNightSortieBeatKit::ForMission(TEXT("M07_SearchIntercept")).MissionId,
		DownedBird.MissionId);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardNightBeatKitKeepsThermalTest,
	"Skyguard52.Campaign.NightBeatKitKeepsThermal",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardNightBeatKitKeepsThermalTest::RunTest(const FString& Parameters)
{
	ASkyguardGunner* Gunner = NewObject<ASkyguardGunner>();
	TestNotNull(TEXT("gunner"), Gunner);
	if (!Gunner)
	{
		return false;
	}

	const int32 NightIndexes[] = {3, 6};
	for (const int32 Index : NightIndexes)
	{
		const FSkyguardCampaignMissionSpec& Spec =
			SkyguardCampaignRoster::Get(Index);
		const FSkyguardNightSortieBeatKit& Kit =
			SkyguardNightSortieBeatKit::ForMission(Spec.MissionId);
		TestTrue(
			*FString::Printf(TEXT("%s roster night identity"), *Spec.MissionId.ToString()),
			Spec.bNightIdentity);
		TestTrue(
			*FString::Printf(TEXT("%s kit keeps thermal"), *Spec.MissionId.ToString()),
			Kit.bKeepThermal);
		TestEqual(
			*FString::Printf(TEXT("%s kit weather identity matches roster"), *Spec.MissionId.ToString()),
			Kit.WeatherIdentity,
			Spec.WeatherIdentity);
		Gunner->ApplyWeatherPlayContracts(Spec.bNightIdentity && Kit.bKeepThermal, false);
		TestTrue(
			TEXT("both night identities enable thermal"),
			Gunner->IsThermalEnabled());
	}

	const FSkyguardCampaignMissionSpec& Harbor = SkyguardCampaignRoster::Get(1);
	Gunner->ApplyWeatherPlayContracts(Harbor.bNightIdentity, false);
	TestFalse(TEXT("harbor day clears thermal"), Gunner->IsThermalEnabled());
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardNightBeatKitCopyBansYakIglaRifleTest,
	"Skyguard52.Campaign.NightBeatKitCopyBansYakIglaRifle",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardNightBeatKitCopyBansYakIglaRifleTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardNightSortieBeatKitTests;

	const FSkyguardNightSortieBeatKit* Kits[] = {
		&SkyguardNightSortieBeatKit::NightEyes(),
		&SkyguardNightSortieBeatKit::DownedBird()
	};
	for (const FSkyguardNightSortieBeatKit* Kit : Kits)
	{
		TestFalse(
			TEXT("banned terms stay banned"),
			KitCopyHasBannedTerm(*Kit));
		for (int32 Index = 0; Index < 7; ++Index)
		{
			TestTrue(
				*FString::Printf(TEXT("%s beat %d has a CPG call"), *Kit->MissionId.ToString(), Index),
				FCString::Strlen(Kit->Beats[Index].Call) > 0);
		}
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardNightBeatKitDirectorsDriveDistinctClocksTest,
	"Skyguard52.Campaign.NightBeatKitDirectorsDriveDistinctClocks",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardNightBeatKitDirectorsDriveDistinctClocksTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardNightSortieBeatKitTests;

	FWorldScope Scope;
	ASkyguardMission04IntegrationDirector* NightEyes =
		Scope.Get()->SpawnActor<ASkyguardMission04IntegrationDirector>();
	ASkyguardMission07IntegrationDirector* DownedBird =
		Scope.Get()->SpawnActor<ASkyguardMission07IntegrationDirector>();
	ASkyguardGunner* NightGunner = Scope.Get()->SpawnActor<ASkyguardGunner>();
	ASkyguardGunner* MistGunner = Scope.Get()->SpawnActor<ASkyguardGunner>();
	TestNotNull(TEXT("M04 director"), NightEyes);
	TestNotNull(TEXT("M07 director"), DownedBird);
	TestNotNull(TEXT("M04 gunner"), NightGunner);
	TestNotNull(TEXT("M07 gunner"), MistGunner);
	if (!NightEyes || !DownedBird || !NightGunner || !MistGunner)
	{
		return false;
	}

	NightEyes->bAutoInitialize = false;
	DownedBird->bAutoInitialize = false;
	NightEyes->BindRuntimeActors(nullptr, nullptr, NightGunner, nullptr);
	DownedBird->BindRuntimeActors(nullptr, nullptr, MistGunner, nullptr);

	TestEqual(
		TEXT("M04 kit is Night Eyes"),
		NightEyes->GetNightBeatKit().MissionId,
		FName(TEXT("M04_NightBlackout")));
	TestEqual(
		TEXT("M07 kit is Downed Bird"),
		DownedBird->GetNightBeatKit().MissionId,
		FName(TEXT("M07_SearchIntercept")));
	TestEqual(
		TEXT("M04 starts dark ingress"),
		NightEyes->GetNightBeatKind(),
		ESkyguardNightSortieBeatKind::DarkIngress);
	TestEqual(
		TEXT("M07 starts island ingress"),
		DownedBird->GetNightBeatKind(),
		ESkyguardNightSortieBeatKind::IslandIngress);
	TestTrue(TEXT("M04 night identity enables thermal"), NightGunner->IsThermalEnabled());
	TestTrue(TEXT("M07 night identity enables thermal"), MistGunner->IsThermalEnabled());

	NightEyes->TickNightBeatKit(30.f);
	DownedBird->TickNightBeatKit(30.f);
	TestEqual(
		TEXT("M04 clock enters thermal hunt"),
		NightEyes->GetNightBeatKind(),
		ESkyguardNightSortieBeatKind::ThermalHunt);
	TestEqual(
		TEXT("M07 clock enters search island"),
		DownedBird->GetNightBeatKind(),
		ESkyguardNightSortieBeatKind::SearchIsland);
	TestTrue(
		TEXT("M04 sequence != M07 sequence after the same elapsed time"),
		NightEyes->GetNightBeatKind() != DownedBird->GetNightBeatKind());
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardNightBeatKitKeepsHarborBreakerClockTest,
	"Skyguard52.Campaign.NightBeatKitKeepsHarborBreakerClock",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardNightBeatKitKeepsHarborBreakerClockTest::RunTest(
	const FString& Parameters)
{
	const FSkyguardCampaignMissionSpec& Harbor = SkyguardCampaignRoster::Get(1);
	const float ExpectedBeats[7] = {120.f, 240.f, 360.f, 480.f, 600.f, 780.f, 900.f};
	for (int32 Index = 0; Index < 7; ++Index)
	{
		TestTrue(
			*FString::Printf(TEXT("harbor beat %d stays on the 15-minute proof"), Index),
			FMath::IsNearlyEqual(Harbor.BeatSeconds[Index], ExpectedBeats[Index], 2.f));
	}
	return true;
}

#endif
