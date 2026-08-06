#if WITH_EDITOR && WITH_DEV_AUTOMATION_TESTS

#include "SkyguardYakR3DonorEvaluationRig.h"

#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Misc/AutomationTest.h"
#include "PhysicsEngine/BodySetup.h"
#include "Tests/AutomationEditorCommon.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardYakR3DonorAssetContractTest,
	"Skyguard52.Yak.R3DonorEvaluation.AssetPivotMaterialAndCollisionContract",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardYakR3DonorAssetContractTest::RunTest(const FString& Parameters)
{
	UWorld* World = FAutomationEditorCommonUtils::CreateNewMap();
	TestNotNull(TEXT("Automation world exists"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardYakR3DonorEvaluationRig* Rig =
		World->SpawnActor<ASkyguardYakR3DonorEvaluationRig>();
	TestNotNull(TEXT("R3 donor evaluation rig spawns"), Rig);
	if (!Rig)
	{
		return false;
	}

	const TArray<UStaticMeshComponent*>& Components = Rig->GetDonorComponents();
	TestEqual(TEXT("Exactly ten governed donor components"), Components.Num(), 10);
	TestTrue(TEXT("All ten quarantine donor meshes load"), Rig->AreAllDonorsLoaded());

	const FVector ExpectedOrigins[] = {
		FVector(404.f, 0.f, 13.f),
		FVector(437.f, 0.f, 13.f),
		FVector(438.5f, 0.f, 13.f),
		FVector(441.f, 0.f, 13.f),
		FVector(440.5f, 0.f, 13.f),
		FVector(440.5f, 0.f, 82.f),
		FVector(440.5f, 0.f, -56.f),
		FVector(75.f, 105.f, 4.f),
		FVector(75.f, -105.f, 4.f),
		FVector(305.f, 0.f, -18.f),
	};

	for (int32 Index = 0; Index < Components.Num(); ++Index)
	{
		UStaticMeshComponent* Component = Components[Index];
		TestNotNull(
			*FString::Printf(TEXT("Donor component %d exists"), Index),
			Component);
		if (!Component)
		{
			continue;
		}

		UStaticMesh* Mesh = Component->GetStaticMesh();
		TestNotNull(
			*FString::Printf(TEXT("Donor mesh %d exists"), Index),
			Mesh);
		if (!Mesh)
		{
			continue;
		}

		TestTrue(
			*FString::Printf(TEXT("Donor %d pivot/bounds origin matches contract"), Index),
			Mesh->GetBounds().Origin.Equals(ExpectedOrigins[Index], 0.25f));
		TestTrue(
			*FString::Printf(TEXT("Donor %d has at least one material slot"), Index),
			Mesh->GetStaticMaterials().Num() > 0);

		const UBodySetup* BodySetup = Mesh->GetBodySetup();
		TestNotNull(
			*FString::Printf(TEXT("Donor %d has body setup"), Index),
			BodySetup);
		if (BodySetup)
		{
			TestTrue(
				*FString::Printf(TEXT("Donor %d has simple collision"), Index),
				BodySetup->AggGeom.GetElementCount() > 0);
		}
		TestEqual(
			*FString::Printf(TEXT("Donor %d uses query-and-physics collision"), Index),
			Component->GetCollisionEnabled(),
			ECollisionEnabled::QueryAndPhysics);
	}

	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardYakR3DonorClearanceContractTest,
	"Skyguard52.Yak.R3DonorEvaluation.CameraPilotRifleAndIglaClearanceContract",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardYakR3DonorClearanceContractTest::RunTest(const FString& Parameters)
{
	UWorld* World = FAutomationEditorCommonUtils::CreateNewMap();
	TestNotNull(TEXT("Automation world exists"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardYakR3DonorEvaluationRig* Rig =
		World->SpawnActor<ASkyguardYakR3DonorEvaluationRig>();
	TestNotNull(TEXT("R3 donor evaluation rig spawns"), Rig);
	if (!Rig)
	{
		return false;
	}

	TestTrue(
		TEXT("Approved donor bounds preserve all four required clearance volumes"),
		Rig->DoDonorsPreserveRequiredClearances());
	TestTrue(
		TEXT("Rear-gunner physical sightline has forward separation"),
		Rig->GetRearGunnerSightTarget().X - Rig->GetRearGunnerEyeLocation().X > 240.f);
	TestTrue(
		TEXT("Rear-gunner physical sightline remains nearly level"),
		FMath::Abs(
			Rig->GetRearGunnerSightTarget().Z -
			Rig->GetRearGunnerEyeLocation().Z) <= 3.f);

	FHitResult Hit;
	FCollisionQueryParams QueryParams(
		TEXT("SkyguardYakR3DonorRearSightline"),
		true,
		Rig);
	const bool bBlocked = World->LineTraceSingleByChannel(
		Hit,
		Rig->GetRearGunnerEyeLocation(),
		Rig->GetRearGunnerSightTarget(),
		ECC_Visibility,
		QueryParams);
	TestFalse(TEXT("Approved donor set does not block the rear-gunner sightline"), bBlocked);

	return true;
}

#endif
