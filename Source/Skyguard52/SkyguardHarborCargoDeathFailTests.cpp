#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardGunshipSortieDirector.h"
#include "SkyguardProtectAsset.h"

#include "Engine/World.h"
#include "Misc/AutomationTest.h"

namespace SkyguardHarborCargoDeathFailTests
{
	// Short of Approach (120s) and IncomingFirstDelay (12s). Same clock
	// for the kill path and the intact-cargo control.
	constexpr float ProbeTickSeconds = 0.1f;

	bool StartHarbor(
		FAutomationTestBase& Test,
		ASkyguardGunshipSortieDirector& Director)
	{
		Director.bAutoStart = false;
		Director.StartMissionIndex(1);
		ASkyguardProtectAsset* Cargo = Director.GetCargoAsset();
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
				ESkyguardSortieBeat::Approach) &&
			Test.TestNotNull(TEXT("harbor cargo"), Cargo) &&
			Test.TestFalse(
				TEXT("harbor cargo starts alive"),
				Cargo && Cargo->IsDestroyed()) &&
			Test.TestEqual(
				TEXT("harbor cargo starts at full integrity"),
				Cargo ? Cargo->GetIntegrityFraction() : -1.f,
				1.f);
	}

	void KillCargo(ASkyguardProtectAsset& Cargo)
	{
		int32 Guard = 0;
		while (!Cargo.IsDestroyed() && Guard < 16)
		{
			const float Remaining = FMath::Max(Cargo.CurrentIntegrity, Cargo.MaxIntegrity);
			Cargo.ApplyDamage(Remaining);
			++Guard;
		}
	}

	void TickProbe(ASkyguardGunshipSortieDirector& Director)
	{
		Director.Tick(ProbeTickSeconds);
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardHarborCargoDeathFailsSortieTest,
	"Skyguard52.Harbor.CargoDeathFailsSortie",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardHarborCargoDeathFailsSortieTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardHarborCargoDeathFailTests;

	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game, false, TEXT("SkyguardHarborCargoDeathFailWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardGunshipSortieDirector* Director =
		World->SpawnActor<ASkyguardGunshipSortieDirector>();
	TestNotNull(TEXT("director"), Director);
	if (!Director)
	{
		World->DestroyWorld(false);
		return false;
	}

	if (!StartHarbor(*this, *Director))
	{
		World->DestroyWorld(false);
		return false;
	}

	ASkyguardProtectAsset* Cargo = Director->GetCargoAsset();
	TestNotNull(TEXT("cargo after Harbor start"), Cargo);
	if (!Cargo)
	{
		World->DestroyWorld(false);
		return false;
	}

	KillCargo(*Cargo);
	TestTrue(TEXT("ApplyDamage killed the harbor cargo"), Cargo->IsDestroyed());
	TestEqual(
		TEXT("dead cargo integrity is zero"),
		Cargo->GetIntegrityFraction(),
		0.f);

	TickProbe(*Director);

	TestTrue(
		TEXT("cargo death ends the sortie"),
		Director->IsSortieOver());
	TestEqual(
		TEXT("cargo death takes the fail beat / ResolveFail path"),
		Director->GetBeat(),
		ESkyguardSortieBeat::Failed);
	TestTrue(
		TEXT("failed beat is not Succeeded"),
		Director->GetBeat() != ESkyguardSortieBeat::Succeeded);
	TestTrue(
		TEXT("ResolveFail leaves the sortie awaiting continue"),
		Director->IsAwaitingContinue());

	World->DestroyWorld(false);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardHarborIntactCargoDoesNotEndSortieTest,
	"Skyguard52.Harbor.IntactCargoDoesNotEndSortie",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardHarborIntactCargoDoesNotEndSortieTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardHarborCargoDeathFailTests;

	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game, false, TEXT("SkyguardHarborIntactCargoControlWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardGunshipSortieDirector* Director =
		World->SpawnActor<ASkyguardGunshipSortieDirector>();
	TestNotNull(TEXT("director"), Director);
	if (!Director)
	{
		World->DestroyWorld(false);
		return false;
	}

	if (!StartHarbor(*this, *Director))
	{
		World->DestroyWorld(false);
		return false;
	}

	ASkyguardProtectAsset* Cargo = Director->GetCargoAsset();
	TestNotNull(TEXT("control cargo"), Cargo);
	if (!Cargo)
	{
		World->DestroyWorld(false);
		return false;
	}

	TickProbe(*Director);

	TestFalse(
		TEXT("full-integrity cargo after the same ticks is not over"),
		Director->IsSortieOver());
	TestEqual(
		TEXT("intact cargo stays on approach"),
		Director->GetBeat(),
		ESkyguardSortieBeat::Approach);
	TestTrue(
		TEXT("intact control is not Succeeded"),
		Director->GetBeat() != ESkyguardSortieBeat::Succeeded);
	TestTrue(
		TEXT("intact control is not Failed"),
		Director->GetBeat() != ESkyguardSortieBeat::Failed);
	TestFalse(TEXT("control cargo stays alive"), Cargo->IsDestroyed());
	TestEqual(
		TEXT("control cargo stays at full integrity"),
		Cargo->GetIntegrityFraction(),
		1.f);

	World->DestroyWorld(false);
	return true;
}

#endif
