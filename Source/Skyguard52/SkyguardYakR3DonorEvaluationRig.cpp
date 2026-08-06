#include "SkyguardYakR3DonorEvaluationRig.h"

#include "Components/BoxComponent.h"
#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"

namespace
{
	const TCHAR* QuarantineRoot =
		TEXT("/Game/Skyguard/Quarantine/M01/YakR3ComponentEval/");

	struct FDonorDefinition
	{
		const TCHAR* ComponentName;
		const TCHAR* AssetName;
	};

	const FDonorDefinition DonorDefinitions[] = {
		{TEXT("R3_CowlingShell"), TEXT("SM_M01Q_YAKR3_CowlingShell")},
		{TEXT("R3_CowlingFrontRing"), TEXT("SM_M01Q_YAKR3_CowlingFrontRing")},
		{TEXT("R3_CowlingShutters"), TEXT("SM_M01Q_YAKR3_CowlingShutters")},
		{TEXT("R3_CowlingInletCone"), TEXT("SM_M01Q_YAKR3_CowlingInletCone")},
		{TEXT("R3_Spinner"), TEXT("SM_M01Q_YAKR3_Spinner")},
		{TEXT("R3_PropBlade_A"), TEXT("SM_M01Q_YAKR3_PropBlade_A")},
		{TEXT("R3_PropBlade_B"), TEXT("SM_M01Q_YAKR3_PropBlade_B")},
		{TEXT("R3_MainWheelWell_L"), TEXT("SM_M01Q_YAKR3_MainWheelWell_L")},
		{TEXT("R3_MainWheelWell_R"), TEXT("SM_M01Q_YAKR3_MainWheelWell_R")},
		{TEXT("R3_NoseWheelWell"), TEXT("SM_M01Q_YAKR3_NoseWheelWell")},
	};

	UBoxComponent* CreateClearanceVolume(
		ASkyguardYakR3DonorEvaluationRig* Owner,
		USceneComponent* Root,
		const TCHAR* Name,
		const FVector& Center,
		const FVector& HalfExtents)
	{
		UBoxComponent* Volume = Owner->CreateDefaultSubobject<UBoxComponent>(Name);
		Volume->SetupAttachment(Root);
		Volume->SetRelativeLocation(Center);
		Volume->SetBoxExtent(HalfExtents);
		Volume->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		Volume->SetGenerateOverlapEvents(false);
		Volume->SetHiddenInGame(true);
		return Volume;
	}
}

ASkyguardYakR3DonorEvaluationRig::ASkyguardYakR3DonorEvaluationRig()
{
	PrimaryActorTick.bCanEverTick = false;

	EvaluationRoot = CreateDefaultSubobject<USceneComponent>(TEXT("EvaluationRoot"));
	SetRootComponent(EvaluationRoot);

	for (const FDonorDefinition& Definition : DonorDefinitions)
	{
		UStaticMeshComponent* Component =
			CreateDefaultSubobject<UStaticMeshComponent>(Definition.ComponentName);
		Component->SetupAttachment(EvaluationRoot);
		Component->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
		Component->SetCollisionResponseToAllChannels(ECR_Block);
		Component->SetGenerateOverlapEvents(false);
		Component->SetCanEverAffectNavigation(false);

		const FString AssetPath = FString::Printf(
			TEXT("%s%s.%s"),
			QuarantineRoot,
			Definition.AssetName,
			Definition.AssetName);
		Component->SetStaticMesh(LoadObject<UStaticMesh>(nullptr, *AssetPath));
		DonorComponents.Add(Component);
	}

	RearGunnerEye = CreateDefaultSubobject<USceneComponent>(TEXT("R3_RearGunnerEye"));
	RearGunnerEye->SetupAttachment(EvaluationRoot);
	RearGunnerEye->SetRelativeLocation(FVector(-90.f, -64.f, 108.f));

	RearGunnerSightTarget =
		CreateDefaultSubobject<USceneComponent>(TEXT("R3_RearGunnerSightTarget"));
	RearGunnerSightTarget->SetupAttachment(EvaluationRoot);
	RearGunnerSightTarget->SetRelativeLocation(FVector(158.f, -64.f, 106.f));

	CameraClearance = CreateClearanceVolume(
		this,
		EvaluationRoot,
		TEXT("R3_CameraClearance"),
		FVector(-90.f, -64.f, 108.f),
		FVector(24.f, 24.f, 22.f));
	PilotSafety = CreateClearanceVolume(
		this,
		EvaluationRoot,
		TEXT("R3_PilotSafety"),
		FVector(62.f, 0.f, 106.f),
		FVector(72.f, 55.f, 62.f));
	RifleMuzzleClearance = CreateClearanceVolume(
		this,
		EvaluationRoot,
		TEXT("R3_RifleMuzzleClearance"),
		FVector(38.f, -64.f, 102.f),
		FVector(145.f, 23.f, 23.f));
	IglaBackblastClearance = CreateClearanceVolume(
		this,
		EvaluationRoot,
		TEXT("R3_IglaBackblastClearance"),
		FVector(-125.f, -42.f, 124.f),
		FVector(72.f, 34.f, 34.f));
}

const TArray<UStaticMeshComponent*>&
ASkyguardYakR3DonorEvaluationRig::GetDonorComponents() const
{
	DonorComponentView.Reset(DonorComponents.Num());
	for (const TObjectPtr<UStaticMeshComponent>& Component : DonorComponents)
	{
		DonorComponentView.Add(Component.Get());
	}
	return DonorComponentView;
}

bool ASkyguardYakR3DonorEvaluationRig::AreAllDonorsLoaded() const
{
	if (DonorComponents.Num() != UE_ARRAY_COUNT(DonorDefinitions))
	{
		return false;
	}
	for (const UStaticMeshComponent* Component : DonorComponents)
	{
		if (!Component || !Component->GetStaticMesh())
		{
			return false;
		}
	}
	return true;
}

bool ASkyguardYakR3DonorEvaluationRig::DoDonorsPreserveRequiredClearances() const
{
	const UBoxComponent* Volumes[] = {
		CameraClearance,
		PilotSafety,
		RifleMuzzleClearance,
		IglaBackblastClearance,
	};
	for (const UStaticMeshComponent* Component : DonorComponents)
	{
		if (!Component || !Component->GetStaticMesh())
		{
			return false;
		}
		const FBox DonorBounds = Component->Bounds.GetBox();
		for (const UBoxComponent* Volume : Volumes)
		{
			if (!Volume)
			{
				return false;
			}
			const FBox ClearanceBounds = Volume->Bounds.GetBox();
			if (DonorBounds.Intersect(ClearanceBounds))
			{
				return false;
			}
		}
	}
	return true;
}

FVector ASkyguardYakR3DonorEvaluationRig::GetRearGunnerEyeLocation() const
{
	return RearGunnerEye ? RearGunnerEye->GetComponentLocation() : FVector::ZeroVector;
}

FVector ASkyguardYakR3DonorEvaluationRig::GetRearGunnerSightTarget() const
{
	return RearGunnerSightTarget
		? RearGunnerSightTarget->GetComponentLocation()
		: FVector::ZeroVector;
}
