#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardApacheAircraft.h"
#include "SkyguardArcadeLookComponent.h"
#include "SkyguardCampaignRoster.h"
#include "SkyguardCoastalEnvironmentDirector.h"
#include "SkyguardCpgHud.h"
#include "SkyguardDrone.h"
#include "SkyguardGuidedLockRules.h"
#include "SkyguardGunner.h"
#include "SkyguardGunshipSortieDirector.h"
#include "SkyguardGunshipTypes.h"
#include "SkyguardPlayerAircraft.h"
#include "SkyguardThreatTypes.h"
#include "Components/SceneComponent.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "Misc/AutomationTest.h"

/**
 * Five live shipping checks from Docs/SKYGUARD_OWN_THING.md.
 * Calls existing public APIs only. Does not invent gameplay.
 */

namespace SkyguardShippingCheckTests
{
	UWorld* MakeWorld(const TCHAR* Name)
	{
		return UWorld::CreateWorld(EWorldType::Game, false, Name);
	}

	void TearDown(UWorld* World)
	{
		if (World)
		{
			World->DestroyWorld(false);
		}
	}

	FActorSpawnParameters AlwaysSpawn()
	{
		FActorSpawnParameters Params;
		Params.SpawnCollisionHandlingOverride =
			ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
		return Params;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardShippingCpgSeatAndChinGunFollowsLookTest,
	"Skyguard52.Shipping.CpgSeatAndChinGunFollowsLook",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardShippingCpgSeatAndChinGunFollowsLookTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardShippingCheckTests;

	UWorld* World = MakeWorld(TEXT("SkyguardShippingCpgSeatWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardApacheAircraft* Apache = FSkyguardPlayerAircraft::EnsureApache(World);
	TestNotNull(TEXT("apache"), Apache);
	if (!Apache)
	{
		TearDown(World);
		return false;
	}

	USceneComponent* CpgSeat = Apache->GetGunnerMount();
	USceneComponent* Chin = Apache->GetChinTurret();
	TestNotNull(TEXT("CPG seat"), CpgSeat);
	TestNotNull(TEXT("chin turret"), Chin);
	TestNotNull(TEXT("aft pilot mount"), Apache->GetPilotMount());
	TestTrue(
		TEXT("CPG sits forward of aircraft origin"),
		CpgSeat->GetRelativeLocation().X > 0.f);
	TestTrue(
		TEXT("pilot sits aft of the CPG"),
		Apache->GetPilotMount()->GetRelativeLocation().X <
			CpgSeat->GetRelativeLocation().X);

	ASkyguardGunner* Gunner = World->SpawnActor<ASkyguardGunner>(
		FVector::ZeroVector,
		FRotator::ZeroRotator,
		AlwaysSpawn());
	TestNotNull(TEXT("gunner"), Gunner);
	if (!Gunner || !Chin)
	{
		TearDown(World);
		return false;
	}

	FSkyguardPlayerAircraft::AttachGunner(Gunner, nullptr);
	if (!Gunner->HasActorBegunPlay())
	{
		Gunner->DispatchBeginPlay();
	}

	TestTrue(TEXT("player is in Apache CPG mode"), Gunner->IsApacheGunnerMode());
	TestTrue(
		TEXT("gunner is attached to the Apache"),
		Gunner->GetAttachParentActor() == Apache);
	if (USceneComponent* Root = Gunner->GetRootComponent())
	{
		TestTrue(
			TEXT("gunner is snapped to the CPG seat"),
			Root->GetAttachParent() == CpgSeat);
	}

	Apache->AimChinTurret(
		Apache->GetActorRotation() + FRotator(0.f, 40.f, 0.f));
	TestTrue(
		TEXT("chin gun yaws toward look"),
		FMath::IsNearlyEqual(Chin->GetRelativeRotation().Yaw, 40.f, 1.f));
	Apache->AimChinTurret(
		Apache->GetActorRotation() + FRotator(-20.f, -25.f, 0.f));
	TestTrue(
		TEXT("chin gun pitches toward look"),
		FMath::IsNearlyEqual(Chin->GetRelativeRotation().Pitch, -20.f, 1.f));
	TestTrue(
		TEXT("chin gun yaws to a second look"),
		FMath::IsNearlyEqual(Chin->GetRelativeRotation().Yaw, -25.f, 1.f));

	Apache->AimChinTurret(
		Apache->GetActorRotation() + FRotator(0.f, 40.f, 0.f));
	const float AimedYaw = Chin->GetRelativeRotation().Yaw;
	Gunner->Tick(0.016f);
	TestTrue(
		TEXT("gunner tick slaves the chin gun off the posed aim"),
		!FMath::IsNearlyEqual(Chin->GetRelativeRotation().Yaw, AimedYaw, 5.f));

	TearDown(World);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardShippingStationsDifferTest,
	"Skyguard52.Shipping.StationsDiffer",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardShippingStationsDifferTest::RunTest(const FString& Parameters)
{
	ASkyguardGunner* Gunner = NewObject<ASkyguardGunner>();
	TestNotNull(TEXT("gunner"), Gunner);
	if (!Gunner)
	{
		return false;
	}

	TestEqual(
		TEXT("default station is cannon"),
		Gunner->GetSelectedGunshipWeapon(),
		ESkyguardGunshipWeapon::Cannon);
	Gunner->SelectGunshipWeapon(ESkyguardGunshipWeapon::Rockets);
	TestEqual(
		TEXT("rockets station exists"),
		Gunner->GetSelectedGunshipWeapon(),
		ESkyguardGunshipWeapon::Rockets);
	Gunner->SelectGunshipWeapon(ESkyguardGunshipWeapon::GuidedMissile);
	TestEqual(
		TEXT("guided-missile station exists"),
		Gunner->GetSelectedGunshipWeapon(),
		ESkyguardGunshipWeapon::GuidedMissile);

	const FString CannonLabel(SkyguardCpgWeaponLabel(ESkyguardGunshipWeapon::Cannon));
	const FString RocketLabel(SkyguardCpgWeaponLabel(ESkyguardGunshipWeapon::Rockets));
	const FString MissileLabel(
		SkyguardCpgWeaponLabel(ESkyguardGunshipWeapon::GuidedMissile));
	TestTrue(TEXT("cannon has a station label"), CannonLabel.Len() > 0);
	TestTrue(TEXT("rockets have a station label"), RocketLabel.Len() > 0);
	TestTrue(TEXT("missiles have a station label"), MissileLabel.Len() > 0);
	TestTrue(TEXT("cannon label differs from rockets"), CannonLabel != RocketLabel);
	TestTrue(TEXT("rockets label differs from missiles"), RocketLabel != MissileLabel);
	TestTrue(TEXT("cannon label differs from missiles"), CannonLabel != MissileLabel);
	TestFalse(
		TEXT("station labels are not Yak/Igla/rifle"),
		SkyguardCpgHudHasLegacyLiveWording(
			CannonLabel + TEXT(" ") + RocketLabel + TEXT(" ") + MissileLabel));

	TestEqual(
		TEXT("cannon magazine is the CPG feel size"),
		Gunner->GetCannonMagazine(),
		SkyguardApacheCpgFeel::CannonMagazineSize);
	TestEqual(
		TEXT("rocket ammo is the CPG feel size"),
		Gunner->GetRocketAmmo(),
		SkyguardApacheCpgFeel::RocketMagazineSize);
	TestEqual(
		TEXT("guided ammo is the CPG feel size"),
		Gunner->GetGuidedAmmo(),
		SkyguardApacheCpgFeel::GuidedMagazineSize);
	TestTrue(
		TEXT("cannon magazine is not the rocket load"),
		SkyguardApacheCpgFeel::CannonMagazineSize !=
			SkyguardApacheCpgFeel::RocketMagazineSize);
	TestTrue(
		TEXT("rocket magazine is not the missile load"),
		SkyguardApacheCpgFeel::RocketMagazineSize !=
			SkyguardApacheCpgFeel::GuidedMagazineSize);
	TestTrue(
		TEXT("cannon magazine is not the missile load"),
		SkyguardApacheCpgFeel::CannonMagazineSize !=
			SkyguardApacheCpgFeel::GuidedMagazineSize);

	TestTrue(
		TEXT("rocket salvo wait is longer than a cannon interval"),
		SkyguardApacheCpgFeel::RocketSalvoSeconds >
			1.f / SkyguardApacheCpgFeel::CannonFireRate);
	TestTrue(
		TEXT("missile lock is a hold, not a cannon tap"),
		SkyguardApacheCpgFeel::GuidedLockSeconds >
			1.f / SkyguardApacheCpgFeel::CannonFireRate);
	TestFalse(
		TEXT("search cannot fire a missile"),
		FSkyguardGuidedLockRules::CanFire(ESkyguardGuidedLockPhase::Search));
	TestFalse(
		TEXT("track cannot fire a missile"),
		FSkyguardGuidedLockRules::CanFire(ESkyguardGuidedLockPhase::Track));
	TestTrue(
		TEXT("only lock can fire a missile"),
		FSkyguardGuidedLockRules::CanFire(ESkyguardGuidedLockPhase::Lock));
	TestEqual(
		TEXT("open seeker is search"),
		Gunner->GetGuidedLockPhase(),
		ESkyguardGuidedLockPhase::Search);
	TestFalse(
		TEXT("missile station refuses fire without a completed lock"),
		Gunner->CanFireGuidedMissile());
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardShippingMixedThreatsTest,
	"Skyguard52.Shipping.MixedThreats",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardShippingMixedThreatsTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardShippingCheckTests;

	const FSkyguardCampaignMissionSpec& Harbor = SkyguardCampaignRoster::Get(1);
	TestEqual(
		TEXT("harbor contact is boats"),
		Harbor.ContactKind,
		ESkyguardThreatKind::FastBoat);
	TestEqual(
		TEXT("harbor shore is armor"),
		Harbor.ShoreKind,
		ESkyguardThreatKind::GroundArmor);
	TestEqual(
		TEXT("harbor extract is air"),
		Harbor.ExtractKind,
		ESkyguardThreatKind::RotorScout);
	TestEqual(
		TEXT("contact wave is boats"),
		ASkyguardGunshipSortieDirector::BeatWaveKind(
			1, ESkyguardSortieBeat::InitialContact),
		ESkyguardThreatKind::FastBoat);
	TestEqual(
		TEXT("shore wave is armor"),
		ASkyguardGunshipSortieDirector::BeatWaveKind(
			1, ESkyguardSortieBeat::ShoreAssault),
		ESkyguardThreatKind::GroundArmor);
	TestEqual(
		TEXT("extract wave is air"),
		ASkyguardGunshipSortieDirector::BeatWaveKind(
			1, ESkyguardSortieBeat::Extraction),
		ESkyguardThreatKind::RotorScout);
	TestTrue(
		TEXT("boats, armor, and air are three kinds"),
		Harbor.ContactKind != Harbor.ShoreKind &&
			Harbor.ShoreKind != Harbor.ExtractKind &&
			Harbor.ContactKind != Harbor.ExtractKind);
	TestTrue(
		TEXT("harbor contact is not a FastAttacker wall"),
		Harbor.ContactKind != ESkyguardThreatKind::FastAttacker);
	TestTrue(
		TEXT("harbor shore is not a FastAttacker wall"),
		Harbor.ShoreKind != ESkyguardThreatKind::FastAttacker);
	TestTrue(
		TEXT("harbor extract is not a FastAttacker wall"),
		Harbor.ExtractKind != ESkyguardThreatKind::FastAttacker);

	TestEqual(
		TEXT("boat tape"),
		FString(SkyguardCpgThreatLabel(ESkyguardThreatKind::FastBoat)),
		FString(TEXT("BOAT")));
	TestEqual(
		TEXT("armor tape"),
		FString(SkyguardCpgThreatLabel(ESkyguardThreatKind::GroundArmor)),
		FString(TEXT("ARM")));
	TestEqual(
		TEXT("air tape"),
		FString(SkyguardCpgThreatLabel(ESkyguardThreatKind::RotorScout)),
		FString(TEXT("RTR")));

	UWorld* World = MakeWorld(TEXT("SkyguardShippingMixedThreatsWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardDrone* Boat = World->SpawnActor<ASkyguardDrone>(
		FVector::ZeroVector, FRotator::ZeroRotator, AlwaysSpawn());
	ASkyguardDrone* Armor = World->SpawnActor<ASkyguardDrone>(
		FVector(200.f, 0.f, 0.f), FRotator::ZeroRotator, AlwaysSpawn());
	ASkyguardDrone* Scout = World->SpawnActor<ASkyguardDrone>(
		FVector(400.f, 0.f, 0.f), FRotator::ZeroRotator, AlwaysSpawn());
	TestNotNull(TEXT("boat"), Boat);
	TestNotNull(TEXT("armor"), Armor);
	TestNotNull(TEXT("scout"), Scout);
	if (!Boat || !Armor || !Scout)
	{
		TearDown(World);
		return false;
	}

	Boat->ConfigureThreat(ESkyguardThreatKind::FastBoat);
	Armor->ConfigureThreat(ESkyguardThreatKind::GroundArmor);
	Scout->ConfigureThreat(ESkyguardThreatKind::RotorScout);
	TestEqual(TEXT("boat kind sticks"), Boat->GetThreatKind(), ESkyguardThreatKind::FastBoat);
	TestEqual(
		TEXT("armor kind sticks"),
		Armor->GetThreatKind(),
		ESkyguardThreatKind::GroundArmor);
	TestEqual(
		TEXT("air kind sticks"),
		Scout->GetThreatKind(),
		ESkyguardThreatKind::RotorScout);

	TearDown(World);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardShippingMoodAndNightThermalTest,
	"Skyguard52.Shipping.MoodAndNightThermal",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardShippingMoodAndNightThermalTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardShippingCheckTests;

	const FSkyguardCampaignMissionSpec& Harbor = SkyguardCampaignRoster::Get(1);
	TestFalse(TEXT("harbor has a weather identity"), Harbor.WeatherIdentity.IsNone());
	TestEqual(
		TEXT("harbor weather identity"),
		Harbor.WeatherIdentity,
		FName(TEXT("HarborOvercast")));
	TestEqual(
		TEXT("harbor weather"),
		Harbor.Weather,
		ESkyguardMissionWeather::Overcast);
	TestTrue(TEXT("harbor weather label is set"), FCString::Strlen(Harbor.WeatherLabel) > 0);

	UWorld* World = MakeWorld(TEXT("SkyguardShippingMoodWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardCoastalEnvironmentDirector* Coast =
		World->SpawnActor<ASkyguardCoastalEnvironmentDirector>(
			FVector::ZeroVector,
			FRotator::ZeroRotator,
			AlwaysSpawn());
	TestNotNull(TEXT("coast"), Coast);
	if (!Coast)
	{
		TearDown(World);
		return false;
	}

	USkyguardArcadeLookComponent::ApplyWorldMoodForWeather(
		World,
		Harbor.Weather,
		Harbor.TimeOfDayHours);
	int32 MoodActors = 0;
	for (TActorIterator<AActor> It(World); It; ++It)
	{
		if (It->ActorHasTag(TEXT("Skyguard.ArcadeMood")))
		{
			++MoodActors;
		}
	}
	TestTrue(TEXT("mood identity is applied"), MoodActors >= 1);

	Coast->ApplyMissionWeather(Harbor.Weather);
	TestEqual(
		TEXT("coast applies harbor weather"),
		Coast->GetAppliedWeather(),
		ESkyguardMissionWeather::Overcast);

	ASkyguardGunner* Gunner = NewObject<ASkyguardGunner>();
	TestNotNull(TEXT("gunner"), Gunner);
	if (!Gunner)
	{
		TearDown(World);
		return false;
	}

	int32 NightCount = 0;
	for (int32 Index = 0; Index < SkyguardCampaignRoster::NumMissions(); ++Index)
	{
		const FSkyguardCampaignMissionSpec& Spec = SkyguardCampaignRoster::Get(Index);
		if (!Spec.bNightIdentity)
		{
			continue;
		}
		++NightCount;
		Gunner->ApplyWeatherPlayContracts(true, false);
		TestTrue(
			*FString::Printf(TEXT("%s night enables thermal"), *Spec.MissionId.ToString()),
			Gunner->IsThermalEnabled());
	}
	TestTrue(TEXT("at least one night mission"), NightCount >= 1);

	Gunner->ApplyWeatherPlayContracts(false, false);
	TestFalse(TEXT("day weather clears thermal"), Gunner->IsThermalEnabled());

	TearDown(World);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardShippingHarborBreakerProofClockTest,
	"Skyguard52.Shipping.HarborBreakerProofClock",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardShippingHarborBreakerProofClockTest::RunTest(
	const FString& Parameters)
{
	const FSkyguardCampaignMissionSpec& Spec = SkyguardCampaignRoster::Get(1);
	TestEqual(
		TEXT("harbor id"),
		Spec.MissionId,
		FName(TEXT("M02_HarborShield")));
	TestEqual(
		TEXT("harbor title"),
		FString(Spec.Title),
		FString(TEXT("Harbor Breaker")));

	const float ExpectedBeats[7] = {120.f, 240.f, 360.f, 480.f, 600.f, 780.f, 900.f};
	const TCHAR* BeatNames[7] = {
		TEXT("approach ends 120s"),
		TEXT("boats end 240s"),
		TEXT("shore armor ends 360s"),
		TEXT("radar ends 480s"),
		TEXT("choice ends 600s"),
		TEXT("patrol-ship climax ends 780s"),
		TEXT("extract ends 900s")
	};
	for (int32 Index = 0; Index < 7; ++Index)
	{
		TestTrue(
			BeatNames[Index],
			FMath::IsNearlyEqual(Spec.BeatSeconds[Index], ExpectedBeats[Index], 0.1f));
	}

	TestEqual(TEXT("contact boats"), Spec.ContactKind, ESkyguardThreatKind::FastBoat);
	TestEqual(TEXT("shore armor"), Spec.ShoreKind, ESkyguardThreatKind::GroundArmor);
	TestEqual(
		TEXT("extract rotors"),
		Spec.ExtractKind,
		ESkyguardThreatKind::RotorScout);
	TestEqual(
		TEXT("patrol-ship climax"),
		Spec.Climax,
		ESkyguardClimaxKind::PatrolShip);
	TestTrue(
		TEXT("harbor is not a FastAttacker-only wall"),
		Spec.ContactKind != ESkyguardThreatKind::FastAttacker &&
			Spec.ShoreKind != ESkyguardThreatKind::FastAttacker &&
			Spec.ExtractKind != ESkyguardThreatKind::FastAttacker);
	TestFalse(
		TEXT("harbor brief is not a shoot-down-the-drones wall"),
		FString(Spec.Brief).Contains(
			TEXT("shoot down the drones"),
			ESearchCase::IgnoreCase));
	return true;
}

#endif
