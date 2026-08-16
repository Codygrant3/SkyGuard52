#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardDaySortieBeatKit.h"

#include "SkyguardCampaignRoster.h"
#include "SkyguardCpgDebrief.h"
#include "SkyguardMission03IntegrationDirector.h"
#include "SkyguardMission06IntegrationDirector.h"
#include "SkyguardMission09IntegrationDirector.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

namespace SkyguardDaySortieBeatKitTests
{
	class FWorldScope
	{
	public:
		FWorldScope()
		{
			World = UWorld::CreateWorld(
				EWorldType::Game, false,
				TEXT("SkyguardDaySortieBeatKitWorld"));
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

	bool KitCopyHasBannedTerm(const FSkyguardDaySortieBeatKit& Kit)
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
	FSkyguardDayBeatKitSequencesDifferTest,
	"Skyguard52.Campaign.DayBeatKitSequencesDiffer",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardDayBeatKitSequencesDifferTest::RunTest(const FString& Parameters)
{
	const FSkyguardDaySortieBeatKit& BrokenHighway =
		SkyguardDaySortieBeatKit::BrokenHighway();
	const FSkyguardDaySortieBeatKit& DustOffensive =
		SkyguardDaySortieBeatKit::DustOffensive();
	const FSkyguardDaySortieBeatKit& HunterKiller =
		SkyguardDaySortieBeatKit::HunterKiller();

	TestEqual(
		TEXT("Broken Highway keys M03"),
		BrokenHighway.MissionId,
		FName(TEXT("M03_ConvoyEscort")));
	TestEqual(
		TEXT("Dust Offensive keys M06"),
		DustOffensive.MissionId,
		FName(TEXT("M06_AirfieldDefense")));
	TestEqual(
		TEXT("Hunter-Killer keys M09"),
		HunterKiller.MissionId,
		FName(TEXT("M09_SaturationAttack")));
	TestEqual(
		TEXT("Broken Highway keeps DryMorning"),
		BrokenHighway.WeatherIdentity,
		FName(TEXT("DryMorning")));
	TestEqual(
		TEXT("Dust Offensive keeps AirfieldHaze"),
		DustOffensive.WeatherIdentity,
		FName(TEXT("AirfieldHaze")));
	TestEqual(
		TEXT("Hunter-Killer keeps CityDusk"),
		HunterKiller.WeatherIdentity,
		FName(TEXT("CityDusk")));

	TestTrue(
		TEXT("M03 sequence != M06 sequence"),
		SkyguardDaySortieBeatKit::SequencesDiffer(BrokenHighway, DustOffensive));
	TestTrue(
		TEXT("M03 sequence != M09 sequence"),
		SkyguardDaySortieBeatKit::SequencesDiffer(BrokenHighway, HunterKiller));
	TestTrue(
		TEXT("M06 sequence != M09 sequence"),
		SkyguardDaySortieBeatKit::SequencesDiffer(DustOffensive, HunterKiller));

	const ESkyguardDaySortieBeatKind BrokenHighwayKinds[7] = {
		ESkyguardDaySortieBeatKind::RidgeIngress,
		ESkyguardDaySortieBeatKind::TechnicalScreen,
		ESkyguardDaySortieBeatKind::ClusterRidge,
		ESkyguardDaySortieBeatKind::TankAmbush,
		ESkyguardDaySortieBeatKind::ConvoyPressure,
		ESkyguardDaySortieBeatKind::ArmorColumn,
		ESkyguardDaySortieBeatKind::Extraction
	};
	const ESkyguardDaySortieBeatKind DustOffensiveKinds[7] = {
		ESkyguardDaySortieBeatKind::HazeIngress,
		ESkyguardDaySortieBeatKind::FenceSweep,
		ESkyguardDaySortieBeatKind::DugInLine,
		ESkyguardDaySortieBeatKind::AdaAcquire,
		ESkyguardDaySortieBeatKind::AdaSuppress,
		ESkyguardDaySortieBeatKind::ArmorPush,
		ESkyguardDaySortieBeatKind::Extraction
	};
	const ESkyguardDaySortieBeatKind HunterKillerKinds[7] = {
		ESkyguardDaySortieBeatKind::DuskIngress,
		ESkyguardDaySortieBeatKind::SensorTrack,
		ESkyguardDaySortieBeatKind::DecoyScreen,
		ESkyguardDaySortieBeatKind::TelAcquire,
		ESkyguardDaySortieBeatKind::TelStrike,
		ESkyguardDaySortieBeatKind::ConvoyBreak,
		ESkyguardDaySortieBeatKind::Extraction
	};
	for (int32 Index = 0; Index < 7; ++Index)
	{
		TestEqual(
			*FString::Printf(TEXT("Broken Highway beat %d is ridge highway escort"), Index),
			BrokenHighway.Beats[Index].Kind,
			BrokenHighwayKinds[Index]);
		TestEqual(
			*FString::Printf(TEXT("Dust Offensive beat %d is airfield ADA suppress"), Index),
			DustOffensive.Beats[Index].Kind,
			DustOffensiveKinds[Index]);
		TestEqual(
			*FString::Printf(TEXT("Hunter-Killer beat %d is metro TEL hunt"), Index),
			HunterKiller.Beats[Index].Kind,
			HunterKillerKinds[Index]);
	}

	TestEqual(
		TEXT("ForMission(M03) is Broken Highway"),
		SkyguardDaySortieBeatKit::ForMission(TEXT("M03_ConvoyEscort")).MissionId,
		BrokenHighway.MissionId);
	TestEqual(
		TEXT("ForMission(M06) is Dust Offensive"),
		SkyguardDaySortieBeatKit::ForMission(TEXT("M06_AirfieldDefense")).MissionId,
		DustOffensive.MissionId);
	TestEqual(
		TEXT("ForMission(M09) is Hunter-Killer"),
		SkyguardDaySortieBeatKit::ForMission(TEXT("M09_SaturationAttack")).MissionId,
		HunterKiller.MissionId);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardDayBeatKitCopyBansYakIglaRifleTest,
	"Skyguard52.Campaign.DayBeatKitCopyBansYakIglaRifle",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardDayBeatKitCopyBansYakIglaRifleTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardDaySortieBeatKitTests;

	const FSkyguardDaySortieBeatKit* Kits[] = {
		&SkyguardDaySortieBeatKit::BrokenHighway(),
		&SkyguardDaySortieBeatKit::DustOffensive(),
		&SkyguardDaySortieBeatKit::HunterKiller()
	};
	for (const FSkyguardDaySortieBeatKit* Kit : Kits)
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
	FSkyguardDayBeatKitDirectorsDriveDistinctClocksTest,
	"Skyguard52.Campaign.DayBeatKitDirectorsDriveDistinctClocks",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardDayBeatKitDirectorsDriveDistinctClocksTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardDaySortieBeatKitTests;

	FWorldScope Scope;
	ASkyguardMission03IntegrationDirector* Highway =
		Scope.Get()->SpawnActor<ASkyguardMission03IntegrationDirector>();
	ASkyguardMission06IntegrationDirector* Airfield =
		Scope.Get()->SpawnActor<ASkyguardMission06IntegrationDirector>();
	ASkyguardMission09IntegrationDirector* Metro =
		Scope.Get()->SpawnActor<ASkyguardMission09IntegrationDirector>();
	TestNotNull(TEXT("M03 director"), Highway);
	TestNotNull(TEXT("M06 director"), Airfield);
	TestNotNull(TEXT("M09 director"), Metro);
	if (!Highway || !Airfield || !Metro)
	{
		return false;
	}

	Highway->bAutoInitialize = false;
	Airfield->bAutoInitialize = false;
	Metro->bAutoInitialize = false;

	TestEqual(
		TEXT("M03 kit is Broken Highway"),
		Highway->GetDayBeatKit().MissionId,
		FName(TEXT("M03_ConvoyEscort")));
	TestEqual(
		TEXT("M06 kit is Dust Offensive"),
		Airfield->GetDayBeatKit().MissionId,
		FName(TEXT("M06_AirfieldDefense")));
	TestEqual(
		TEXT("M09 kit is Hunter-Killer"),
		Metro->GetDayBeatKit().MissionId,
		FName(TEXT("M09_SaturationAttack")));
	TestEqual(
		TEXT("M03 starts ridge ingress"),
		Highway->GetDayBeatKind(),
		ESkyguardDaySortieBeatKind::RidgeIngress);
	TestEqual(
		TEXT("M06 starts haze ingress"),
		Airfield->GetDayBeatKind(),
		ESkyguardDaySortieBeatKind::HazeIngress);
	TestEqual(
		TEXT("M09 starts dusk ingress"),
		Metro->GetDayBeatKind(),
		ESkyguardDaySortieBeatKind::DuskIngress);

	Highway->TickDayBeatKit(30.f);
	Airfield->TickDayBeatKit(30.f);
	Metro->TickDayBeatKit(30.f);
	TestEqual(
		TEXT("M03 clock enters technical screen"),
		Highway->GetDayBeatKind(),
		ESkyguardDaySortieBeatKind::TechnicalScreen);
	TestEqual(
		TEXT("M06 clock enters fence sweep"),
		Airfield->GetDayBeatKind(),
		ESkyguardDaySortieBeatKind::FenceSweep);
	TestEqual(
		TEXT("M09 clock enters sensor track"),
		Metro->GetDayBeatKind(),
		ESkyguardDaySortieBeatKind::SensorTrack);
	TestTrue(
		TEXT("M03 sequence != M06 sequence after the same elapsed time"),
		Highway->GetDayBeatKind() != Airfield->GetDayBeatKind());
	TestTrue(
		TEXT("M03 sequence != M09 sequence after the same elapsed time"),
		Highway->GetDayBeatKind() != Metro->GetDayBeatKind());
	TestTrue(
		TEXT("M06 sequence != M09 sequence after the same elapsed time"),
		Airfield->GetDayBeatKind() != Metro->GetDayBeatKind());
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardDayBeatKitKeepsHarborBreakerClockTest,
	"Skyguard52.Campaign.DayBeatKitKeepsHarborBreakerClock",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardDayBeatKitKeepsHarborBreakerClockTest::RunTest(
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
