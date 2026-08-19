#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardGunner.h"
#include "SkyguardGunshipSortieDirector.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

namespace SkyguardFlareEmptyInboundTests
{
	void EmptyFlareMagazine(ASkyguardGunner& Gunner)
	{
		int32 Guard = 0;
		while (Gunner.GetFlareCount() > 0 && Guard < 64)
		{
			Gunner.PopFlares();
			++Guard;
		}
	}

	bool StartHarborAndHoldApproach(
		FAutomationTestBase& Test,
		ASkyguardGunshipSortieDirector& Director)
	{
		Director.bAutoStart = false;
		Director.StartMissionIndex(1);
		return Test.TestEqual(
				   TEXT("harbor id"),
				   Director.GetMissionId(),
				   FName(TEXT("M02_HarborShield"))) &&
			Test.TestEqual(
				TEXT("harbor title"),
				Director.GetMissionTitle(),
				FString(TEXT("Harbor Breaker"))) &&
			Test.TestEqual(
				TEXT("harbor starts on approach"),
				Director.GetBeat(),
				ESkyguardSortieBeat::Approach);
	}

	// Contact opens at 120s. First inbound delay is 12s and approach
	// refuses fire, so 119s leaves the clock armed, then 1s crosses
	// contact and the director notifies the inbound.
	bool TickHarborContactInbound(
		FAutomationTestBase& Test,
		ASkyguardGunshipSortieDirector& Director,
		ASkyguardGunner& Gunner)
	{
		Director.Tick(119.f);
		const bool bHeldApproach =
			Test.TestEqual(
				TEXT("119s is still approach"),
				Director.GetBeat(),
				ESkyguardSortieBeat::Approach) &&
			Test.TestFalse(
				TEXT("approach does not tick-fire inbound"),
				Gunner.IsMissileInbound());
		if (!bHeldApproach)
		{
			return false;
		}

		Director.Tick(1.f);
		return Test.TestEqual(
				   TEXT("120s opens Harbor contact"),
				   Director.GetBeat(),
				   ESkyguardSortieBeat::InitialContact) &&
			Test.TestTrue(
				TEXT("Harbor contact inbound is live"),
				Gunner.IsMissileInbound());
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardEmptyFlareMagazineCannotDefeatHarborInboundTest,
	"Skyguard52.Harbor.EmptyFlareMagazineCannotDefeatInbound",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardEmptyFlareMagazineCannotDefeatHarborInboundTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardFlareEmptyInboundTests;

	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game, false, TEXT("SkyguardFlareEmptyHarborInboundWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardGunshipSortieDirector* Director =
		World->SpawnActor<ASkyguardGunshipSortieDirector>();
	ASkyguardGunner* Gunner = World->SpawnActor<ASkyguardGunner>();
	TestNotNull(TEXT("director"), Director);
	TestNotNull(TEXT("gunner"), Gunner);
	if (!Director || !Gunner)
	{
		World->DestroyWorld(false);
		return false;
	}

	if (!StartHarborAndHoldApproach(*this, *Director))
	{
		World->DestroyWorld(false);
		return false;
	}

	TestTrue(TEXT("Harbor starts with a flare magazine"), Gunner->GetFlareCount() > 0);
	EmptyFlareMagazine(*Gunner);
	TestEqual(TEXT("magazine is empty before the inbound"), Gunner->GetFlareCount(), 0);

	if (!TickHarborContactInbound(*this, *Director, *Gunner))
	{
		World->DestroyWorld(false);
		return false;
	}

	Gunner->PopFlares();
	TestEqual(TEXT("empty dispense spends nothing"), Gunner->GetFlareCount(), 0);
	TestFalse(
		TEXT("empty can does not defeat the Harbor inbound"),
		Gunner->TryDefeatInboundWithFlares());
	TestTrue(
		TEXT("Harbor inbound stays live after the empty-can call"),
		Gunner->IsMissileInbound());

	Director->Tick(0.1f);
	TestFalse(
		TEXT("director tick still cannot break inbound with an empty can"),
		Gunner->TryDefeatInboundWithFlares());
	TestTrue(
		TEXT("Harbor inbound is not marked broken"),
		Gunner->IsMissileInbound());

	World->DestroyWorld(false);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardRemainingFlareMagazineDefeatsHarborInboundTest,
	"Skyguard52.Harbor.RemainingFlareMagazineDefeatsInbound",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardRemainingFlareMagazineDefeatsHarborInboundTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardFlareEmptyInboundTests;

	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game,
		false,
		TEXT("SkyguardFlareRemainingHarborInboundWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardGunshipSortieDirector* Director =
		World->SpawnActor<ASkyguardGunshipSortieDirector>();
	ASkyguardGunner* Gunner = World->SpawnActor<ASkyguardGunner>();
	TestNotNull(TEXT("director"), Director);
	TestNotNull(TEXT("gunner"), Gunner);
	if (!Director || !Gunner)
	{
		World->DestroyWorld(false);
		return false;
	}

	if (!StartHarborAndHoldApproach(*this, *Director))
	{
		World->DestroyWorld(false);
		return false;
	}

	const int32 FlaresBefore = Gunner->GetFlareCount();
	TestTrue(TEXT("positive control has flares remaining"), FlaresBefore > 0);

	if (!TickHarborContactInbound(*this, *Director, *Gunner))
	{
		World->DestroyWorld(false);
		return false;
	}

	TestFalse(
		TEXT("no flare popped yet"),
		Gunner->TryDefeatInboundWithFlares());
	Gunner->PopFlares();
	TestEqual(TEXT("one flare spent"), Gunner->GetFlareCount(), FlaresBefore - 1);
	TestTrue(
		TEXT("remaining can still breaks the Harbor inbound"),
		Gunner->TryDefeatInboundWithFlares());
	TestFalse(
		TEXT("Harbor inbound is cleared"),
		Gunner->IsMissileInbound());

	World->DestroyWorld(false);
	return true;
}

#endif
