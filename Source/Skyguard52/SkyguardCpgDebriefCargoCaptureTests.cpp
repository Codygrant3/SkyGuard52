#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardCpgDebrief.h"
#include "SkyguardGunshipSortieDirector.h"
#include "SkyguardProtectAsset.h"

#include "Engine/World.h"
#include "Misc/AutomationTest.h"

namespace
{
	void SetCargoRemainingPercent(ASkyguardProtectAsset& Cargo, const int32 Percent)
	{
		Cargo.ResetIntegrity();
		const float Clamped = FMath::Clamp(static_cast<float>(Percent), 0.f, 100.f);
		Cargo.ApplyDamage(Cargo.MaxIntegrity * (1.f - Clamped / 100.f));
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardCpgDebriefCaptureRecordsLiveCargoPercentTest,
	"Skyguard52.Presentation.Sortie.CpgDebriefCaptureRecordsLiveCargoPercent",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardCpgDebriefCaptureRecordsLiveCargoPercentTest::RunTest(
	const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game,
		false,
		TEXT("SkyguardCpgDebriefCargoWorld"));
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

	Director->bAutoStart = false;
	Director->StartMissionIndex(1);

	ASkyguardProtectAsset* Cargo = Director->GetCargoAsset();
	TestNotNull(TEXT("harbor protect-asset cargo"), Cargo);
	if (!Cargo)
	{
		World->DestroyWorld(false);
		return false;
	}

	const int32 ExpectedPercent = 40;
	SetCargoRemainingPercent(*Cargo, ExpectedPercent);
	TestEqual(
		TEXT("live cargo remaining is 40 percent"),
		FMath::RoundToInt(Cargo->GetIntegrityFraction() * 100.f),
		ExpectedPercent);

	const FSkyguardCpgDebriefSnapshot Snap =
		SkyguardCaptureCpgDebrief(Director, nullptr, nullptr);
	TestTrue(TEXT("debrief snapshot is valid"), Snap.bValid);
	TestEqual(
		TEXT("CaptureCpgDebrief stores live cargo remaining percent"),
		Snap.CargoPercent,
		ExpectedPercent);

	const int32 SecondPercent = 25;
	SetCargoRemainingPercent(*Cargo, SecondPercent);
	const FSkyguardCpgDebriefSnapshot SecondSnap =
		SkyguardCaptureCpgDebrief(Director, nullptr, nullptr);
	TestEqual(
		TEXT("second live cargo remaining is 25 percent"),
		FMath::RoundToInt(Cargo->GetIntegrityFraction() * 100.f),
		SecondPercent);
	TestEqual(
		TEXT("CaptureCpgDebrief follows a later cargo remaining percent"),
		SecondSnap.CargoPercent,
		SecondPercent);

	World->DestroyWorld(false);
	return true;
}

#endif
