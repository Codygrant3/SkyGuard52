#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardApacheAircraft.h"
#include "SkyguardBossTypes.h"

#include "Components/SceneComponent.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

namespace SkyguardApacheChinMuzzleTests
{
	UWorld* MakeGameWorld(const TCHAR* Name)
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

	ASkyguardApacheAircraft* SpawnApache(UWorld* World, const FVector& Location)
	{
		if (!World)
		{
			return nullptr;
		}
		return World->SpawnActor<ASkyguardApacheAircraft>(
			Location,
			FRotator::ZeroRotator);
	}

	bool IsFiniteVector(const FVector& Value)
	{
		return FMath::IsFinite(Value.X) &&
			FMath::IsFinite(Value.Y) &&
			FMath::IsFinite(Value.Z);
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardApacheChinMuzzleAndFaceTargetPublicApiTest,
	"Skyguard52.Apache.ChinMuzzle.EyeMountMuzzleAndFaceTarget",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardApacheChinMuzzleAndFaceTargetPublicApiTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardApacheChinMuzzleTests;

	UWorld* World = MakeGameWorld(TEXT("SkyguardApacheChinMuzzleWorld"));
	TestNotNull(TEXT("Game world is created"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardApacheAircraft* Apache = SpawnApache(
		World,
		FVector(0.f, 0.f, 800.f));
	ASkyguardApacheAircraft* IssueShip = SpawnApache(
		World,
		FVector(200.f, 0.f, 800.f));
	TestNotNull(TEXT("apache spawns"), Apache);
	TestNotNull(TEXT("issue-command apache spawns"), IssueShip);
	if (!Apache || !IssueShip)
	{
		TearDown(World);
		return false;
	}

	Apache->DispatchBeginPlay();
	IssueShip->DispatchBeginPlay();

	TestNotNull(TEXT("GetEyeMount is non-null"), Apache->GetEyeMount());
	TestNotNull(TEXT("GetWeaponMount exists"), Apache->GetWeaponMount());
	if (Apache->GetWeaponMount())
	{
		TestEqual(
			TEXT("GetChinMuzzleLocation equals WeaponMount location"),
			Apache->GetChinMuzzleLocation(),
			Apache->GetWeaponMount()->GetComponentLocation());
	}

	const FVector OffNose =
		Apache->GetActorLocation() + Apache->GetActorForwardVector() * 4000.f;
	const int32 FaceBefore = Apache->GetPilotConfirmationsIssued();
	Apache->FaceWorldLocation(OffNose);
	TestEqual(
		TEXT("FaceWorldLocation sets FaceTarget"),
		Apache->GetPilotCommand(),
		ESkyguardPilotCommand::FaceTarget);
	TestEqual(
		TEXT("FaceWorldLocation increments confirmations"),
		Apache->GetPilotConfirmationsIssued(),
		FaceBefore + 1);

	const int32 IssueBefore = IssueShip->GetPilotConfirmationsIssued();
	IssueShip->IssuePilotCommand(ESkyguardPilotCommand::FaceTarget);
	TestEqual(
		TEXT("IssuePilotCommand(FaceTarget) sets FaceTarget"),
		IssueShip->GetPilotCommand(),
		ESkyguardPilotCommand::FaceTarget);
	TestEqual(
		TEXT("IssuePilotCommand(FaceTarget) increments confirmations"),
		IssueShip->GetPilotConfirmationsIssued(),
		IssueBefore + 1);
	TestEqual(
		TEXT("FaceWorldLocation increments the same as IssuePilotCommand(FaceTarget)"),
		Apache->GetPilotConfirmationsIssued() - FaceBefore,
		IssueShip->GetPilotConfirmationsIssued() - IssueBefore);

	Apache->AimChinTurret(FRotator(-10.f, 25.f, 0.f));
	const FVector AfterAim = Apache->GetChinMuzzleLocation();
	TestTrue(
		TEXT("GetChinMuzzleLocation is finite after AimChinTurret"),
		IsFiniteVector(AfterAim));
	if (Apache->GetWeaponMount())
	{
		TestEqual(
			TEXT("after aim, muzzle still equals WeaponMount location"),
			AfterAim,
			Apache->GetWeaponMount()->GetComponentLocation());
	}

	TearDown(World);
	return true;
}

#endif
