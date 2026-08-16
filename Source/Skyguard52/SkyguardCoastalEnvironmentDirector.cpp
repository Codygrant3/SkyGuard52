#include "SkyguardCoastalEnvironmentDirector.h"
#include "SkyguardEnvironmentVFXPoolComponent.h"
#include "SkyguardMissionTypes.h"
#include "Components/HierarchicalInstancedStaticMeshComponent.h"
#include "Components/SceneComponent.h"
#include "Components/WindDirectionalSourceComponent.h"
#include "Engine/StaticMesh.h"
#include "EngineUtils.h"
#include "UObject/ConstructorHelpers.h"

namespace
{
	const FName CapabilityTags[] = {
		TEXT("Skyguard.Environment.Water"),
		TEXT("Skyguard.Environment.Landmass"),
		TEXT("Skyguard.Environment.PCG"),
		TEXT("Skyguard.Environment.Atmosphere"),
		TEXT("Skyguard.Environment.Cloud"),
		TEXT("Skyguard.Environment.Fog"),
		TEXT("Skyguard.Environment.Wind")
	};
}

ASkyguardCoastalEnvironmentDirector::ASkyguardCoastalEnvironmentDirector()
{
	PrimaryActorTick.bCanEverTick = false;

	Root = CreateDefaultSubobject<USceneComponent>(TEXT("EnvironmentRoot"));
	SetRootComponent(Root);

	TreeInstances =
		CreateDefaultSubobject<UHierarchicalInstancedStaticMeshComponent>(TEXT("TreeInstances"));
	TreeInstances->SetupAttachment(Root);
	TreeInstances->SetCollisionEnabled(ECollisionEnabled::NoCollision);

	ShrubInstances =
		CreateDefaultSubobject<UHierarchicalInstancedStaticMeshComponent>(TEXT("ShrubInstances"));
	ShrubInstances->SetupAttachment(Root);
	ShrubInstances->SetCollisionEnabled(ECollisionEnabled::NoCollision);

	WindSource =
		CreateDefaultSubobject<UWindDirectionalSourceComponent>(TEXT("WindSource"));
	WindSource->SetupAttachment(Root);

	VFXPool =
		CreateDefaultSubobject<USkyguardEnvironmentVFXPoolComponent>(TEXT("EnvironmentVFXPool"));

	static ConstructorHelpers::FObjectFinder<UStaticMesh> TreeAsset(
		TEXT("/Game/Skyguard/Meshes/Hero/coast_tree_proxy.coast_tree_proxy"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> ShrubAsset(
		TEXT("/Engine/BasicShapes/Cone.Cone"));
	if (TreeAsset.Succeeded()) TreeInstances->SetStaticMesh(TreeAsset.Object);
	if (ShrubAsset.Succeeded()) ShrubInstances->SetStaticMesh(ShrubAsset.Object);
}

void ASkyguardCoastalEnvironmentDirector::BeginPlay()
{
	Super::BeginPlay();
	WindSource->SetStrength(WindStrength);
	WindSource->SetSpeed(WindSpeed);
	RebuildDeterministicVegetation();
	RefreshCapabilityBindings();
}

float ASkyguardCoastalEnvironmentDirector::GetQualityMultiplier() const
{
	switch (Quality)
	{
	case ESkyguardEnvironmentQuality::Low:
		return 0.25f;
	case ESkyguardEnvironmentQuality::Medium:
		return 0.5f;
	case ESkyguardEnvironmentQuality::High:
		return 0.75f;
	case ESkyguardEnvironmentQuality::Epic:
		return 1.f;
	default:
		return 0.75f;
	}
}

void ASkyguardCoastalEnvironmentDirector::PlaceInstances(
	UHierarchicalInstancedStaticMeshComponent* Component,
	const int32 Count,
	FRandomStream& Random,
	const float ScaleMin,
	const float ScaleMax)
{
	if (!Component || !Component->GetStaticMesh() || Count <= 0)
	{
		return;
	}

	for (int32 Index = 0; Index < Count; ++Index)
	{
		const float AlongRoute = Random.FRandRange(0.f, FMath::Max(1000.f, RouteLengthCm));
		const float Landward = Random.FRandRange(
			FMath::Max(ShorelineLandOffsetCm, RouteCorridorHalfWidthCm + 250.f),
			FMath::Max(ShorelineLandOffsetCm + 250.f, InlandExtentCm));
		const float Scale = Random.FRandRange(ScaleMin, ScaleMax);
		const FRotator Rotation(0.f, Random.FRandRange(-180.f, 180.f), 0.f);
		Component->AddInstance(
			FTransform(
				Rotation,
				FVector(AlongRoute, Landward, 0.f),
				FVector(Scale)));
	}
}

void ASkyguardCoastalEnvironmentDirector::RebuildDeterministicVegetation()
{
	TreeInstances->ClearInstances();
	ShrubInstances->ClearInstances();
	TreeInstances->SetCullDistances(
		FMath::Max(1000, VegetationStartCullDistanceCm),
		FMath::Max(VegetationStartCullDistanceCm + 1000, VegetationEndCullDistanceCm));
	ShrubInstances->SetCullDistances(
		FMath::Max(1000, VegetationStartCullDistanceCm / 2),
		FMath::Max(VegetationStartCullDistanceCm, VegetationEndCullDistanceCm / 2));

	const float Multiplier = GetQualityMultiplier();
	const int32 TreeCount =
		FMath::Clamp(FMath::RoundToInt(EpicTreeBudget * Multiplier), 0, 1024);
	const int32 ShrubCount =
		FMath::Clamp(FMath::RoundToInt(EpicShrubBudget * Multiplier), 0, 2048);
	FRandomStream Random(PlacementSeed);
	PlaceInstances(TreeInstances, TreeCount, Random, 0.82f, 1.2f);
	PlaceInstances(ShrubInstances, ShrubCount, Random, 0.3f, 0.8f);

	Readiness.TreeInstanceCount = TreeInstances->GetInstanceCount();
	Readiness.ShrubInstanceCount = ShrubInstances->GetInstanceCount();
	Readiness.VFXPoolSize = VFXPool ? VFXPool->GetAllocatedPoolSize() : 0;
}

void ASkyguardCoastalEnvironmentDirector::RefreshCapabilityBindings()
{
	int32 BoundCount = 0;
	if (UWorld* World = GetWorld())
	{
		for (const FName CapabilityTag : CapabilityTags)
		{
			bool bFound = false;
			for (TActorIterator<AActor> ActorIt(World); ActorIt; ++ActorIt)
			{
				if (*ActorIt != this && ActorIt->ActorHasTag(CapabilityTag))
				{
					bFound = true;
					break;
				}
			}
			BoundCount += bFound ? 1 : 0;
		}
	}
	Readiness.BoundCapabilityCount = BoundCount;
	Readiness.VFXPoolSize = VFXPool ? VFXPool->GetAllocatedPoolSize() : 0;
}

void ASkyguardCoastalEnvironmentDirector::ApplyQuality(
	const ESkyguardEnvironmentQuality NewQuality)
{
	Quality = NewQuality;
	RebuildDeterministicVegetation();
}

void ASkyguardCoastalEnvironmentDirector::ApplyMissionWeather(
	const ESkyguardMissionWeather Weather)
{
	AppliedWeather = Weather;
	switch (Weather)
	{
	case ESkyguardMissionWeather::Storm:
		WindStrength = 0.92f;
		WindSpeed = 1.f;
		break;
	case ESkyguardMissionWeather::Rain:
		WindStrength = 0.62f;
		WindSpeed = 0.78f;
		break;
	case ESkyguardMissionWeather::Overcast:
		WindStrength = 0.42f;
		WindSpeed = 0.58f;
		break;
	case ESkyguardMissionWeather::NightClear:
		WindStrength = 0.22f;
		WindSpeed = 0.28f;
		break;
	case ESkyguardMissionWeather::NightOvercast:
		WindStrength = 0.38f;
		WindSpeed = 0.48f;
		break;
	case ESkyguardMissionWeather::Clear:
	default:
		WindStrength = 0.28f;
		WindSpeed = 0.4f;
		break;
	}
	if (WindSource)
	{
		WindSource->SetStrength(WindStrength);
		WindSource->SetSpeed(WindSpeed);
	}
}

bool ASkyguardCoastalEnvironmentDirector::IsVegetationOutsideRouteCorridor() const
{
	const UHierarchicalInstancedStaticMeshComponent* Components[] = {
		TreeInstances,
		ShrubInstances
	};
	for (const UHierarchicalInstancedStaticMeshComponent* Component : Components)
	{
		if (!Component)
		{
			continue;
		}
		for (int32 Index = 0; Index < Component->GetInstanceCount(); ++Index)
		{
			FTransform Transform;
			if (!Component->GetInstanceTransform(Index, Transform, false) ||
				FMath::Abs(Transform.GetLocation().Y) <= RouteCorridorHalfWidthCm ||
				Transform.GetLocation().X < 0.f ||
				Transform.GetLocation().X > RouteLengthCm)
			{
				return false;
			}
		}
	}
	return true;
}
