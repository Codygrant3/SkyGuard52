#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardMissionDirectorPresentationHelpers.h"

#include "SkyguardGunner.h"
#include "SkyguardSortieHudHostComponent.h"
#include "SkyguardSortiePresentationComponent.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Actor.h"
#include "Misc/AutomationTest.h"

// Neighbor of SkyguardMissionDirectorCampaignHelpersTests.cpp.
// Fail-closed BindHudHostToPresentation only: no Gunner / Yak / Igla /
// rifle spawn, no ApplyWeaponHit, no Harbor 40/80.

namespace SkyguardMissionDirectorPresentationHelpersTests
{
	int32 CountActors(UWorld* World)
	{
		int32 Count = 0;
		if (!World)
		{
			return 0;
		}
		for (TActorIterator<AActor> It(World); It; ++It)
		{
			++Count;
		}
		return Count;
	}

	int32 CountValidGunners(UWorld* World)
	{
		int32 Count = 0;
		if (!World)
		{
			return 0;
		}
		for (TActorIterator<ASkyguardGunner> It(World); It; ++It)
		{
			if (IsValid(*It))
			{
				++Count;
			}
		}
		return Count;
	}

	int32 CountHudHosts(UWorld* World)
	{
		int32 Count = 0;
		if (!World)
		{
			return 0;
		}
		for (TActorIterator<AActor> It(World); It; ++It)
		{
			if (It->FindComponentByClass<USkyguardSortieHudHostComponent>())
			{
				++Count;
			}
		}
		return Count;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMissionDirectorPresentationHelpersBothNullTest,
	"Skyguard52.Presentation.DirectorHelpers.BindHudHostBothNullDoesNotCrash",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMissionDirectorPresentationHelpersBothNullTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMissionDirectorPresentationHelpers;

	BindHudHostToPresentation(nullptr, nullptr);
	TestTrue(
		TEXT("BindHudHostToPresentation(nullptr, nullptr) returns without crashing"),
		true);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMissionDirectorPresentationHelpersNullWorldTest,
	"Skyguard52.Presentation.DirectorHelpers.BindHudHostNullWorldDoesNotCrash",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMissionDirectorPresentationHelpersNullWorldTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMissionDirectorPresentationHelpers;

	USkyguardSortiePresentationComponent* Presentation =
		NewObject<USkyguardSortiePresentationComponent>(
			GetTransientPackage());
	TestNotNull(TEXT("NewObject presentation constructs"), Presentation);
	if (!Presentation)
	{
		return false;
	}

	BindHudHostToPresentation(nullptr, Presentation);
	TestTrue(
		TEXT("BindHudHostToPresentation(nullptr, Presentation) returns without crashing"),
		true);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMissionDirectorPresentationHelpersNullPresentationTest,
	"Skyguard52.Presentation.DirectorHelpers.BindHudHostNullPresentationDoesNotCrash",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMissionDirectorPresentationHelpersNullPresentationTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMissionDirectorPresentationHelpers;

	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game,
		false,
		TEXT("SkyguardBindHudHostNullPresentationWorld"));
	TestNotNull(TEXT("Automation Game world is created"), World);
	if (!World)
	{
		return false;
	}

	BindHudHostToPresentation(World, nullptr);
	TestTrue(
		TEXT("BindHudHostToPresentation(World, nullptr) returns without crashing"),
		true);
	TestEqual(
		TEXT("Null presentation does not create a SortieHudHost"),
		SkyguardMissionDirectorPresentationHelpersTests::CountHudHosts(World),
		0);

	World->DestroyWorld(false);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMissionDirectorPresentationHelpersNoHostOwnerTest,
	"Skyguard52.Presentation.DirectorHelpers.BindHudHostNoHostOwnerCreatesNoHost",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMissionDirectorPresentationHelpersNoHostOwnerTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMissionDirectorPresentationHelpers;
	using namespace SkyguardMissionDirectorPresentationHelpersTests;

	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game,
		false,
		TEXT("SkyguardBindHudHostNoHostOwnerWorld"));
	TestNotNull(TEXT("Automation Game world is created"), World);
	if (!World)
	{
		return false;
	}

	USkyguardSortiePresentationComponent* Presentation =
		NewObject<USkyguardSortiePresentationComponent>(
			GetTransientPackage());
	TestNotNull(TEXT("NewObject presentation constructs"), Presentation);
	if (!Presentation)
	{
		World->DestroyWorld(false);
		return false;
	}

	TestTrue(
		TEXT("Bare Game world has no player controller"),
		World->GetFirstPlayerController() == nullptr);
	TestEqual(
		TEXT("Bare Game world has no Gunner; do not spawn one"),
		CountValidGunners(World),
		0);

	const int32 ActorCountBefore = CountActors(World);
	BindHudHostToPresentation(World, Presentation);
	TestTrue(
		TEXT("BindHudHostToPresentation returns without crashing when HostOwner is null"),
		true);
	TestTrue(
		TEXT("Still no player controller after the bind"),
		World->GetFirstPlayerController() == nullptr);
	TestEqual(
		TEXT("Still no Gunner after the bind"),
		CountValidGunners(World),
		0);
	TestEqual(
		TEXT("No SortieHudHost is created when HostOwner is null"),
		CountHudHosts(World),
		0);
	TestEqual(
		TEXT("No actor is spawned to host a HUD component"),
		CountActors(World),
		ActorCountBefore);

	World->DestroyWorld(false);
	return true;
}

#endif
