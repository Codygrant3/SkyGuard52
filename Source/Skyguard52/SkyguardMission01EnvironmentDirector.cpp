#include "SkyguardMission01EnvironmentDirector.h"

#include "Components/BoxComponent.h"
#include "Components/ExponentialHeightFogComponent.h"
#include "Components/HierarchicalInstancedStaticMeshComponent.h"
#include "Components/SceneComponent.h"
#include "Engine/ExponentialHeightFog.h"
#include "Engine/StaticMesh.h"
#include "EngineUtils.h"
#include "LandscapeComponent.h"
#include "LandscapeProxy.h"
#include "Materials/MaterialInterface.h"
#include "PCGComponent.h"
#include "PCGGraph.h"
#include "SkyguardInputCombatPerformanceCapture.h"
#include "UObject/ConstructorHelpers.h"

namespace
{
	const FName Mission01LandscapeTag =
		TEXT("Skyguard.Environment.Mission01.Landscape");
	const FName PCGInclusionTag = TEXT("Skyguard.PCG.Inclusion");
	const FName PCGExclusionTag = TEXT("Skyguard.PCG.Exclusion");
}

ASkyguardMission01EnvironmentDirector::ASkyguardMission01EnvironmentDirector()
{
	PrimaryActorTick.bCanEverTick = true;

	Root = CreateDefaultSubobject<USceneComponent>(TEXT("Mission01EnvironmentRoot"));
	Root->SetMobility(EComponentMobility::Static);
	SetRootComponent(Root);

	OceanTiles = CreateDefaultSubobject<UHierarchicalInstancedStaticMeshComponent>(TEXT("OceanTiles"));
	OceanTiles->SetupAttachment(Root);
	OceanTiles->SetCollisionEnabled(ECollisionEnabled::NoCollision);

	BeachTiles = CreateDefaultSubobject<UHierarchicalInstancedStaticMeshComponent>(TEXT("BeachTiles"));
	BeachTiles->SetupAttachment(Root);
	BeachTiles->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);

	LandTiles = CreateDefaultSubobject<UHierarchicalInstancedStaticMeshComponent>(TEXT("LandTiles"));
	LandTiles->SetupAttachment(Root);
	LandTiles->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);

	RouteExclusion = CreateDefaultSubobject<UBoxComponent>(TEXT("RouteExclusion"));
	RouteExclusion->SetupAttachment(Root);
	RouteExclusion->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	RouteExclusion->SetHiddenInGame(true);
	RouteExclusion->ComponentTags.AddUnique(PCGExclusionTag);

	LandScatterBounds = CreateDefaultSubobject<UBoxComponent>(TEXT("LandScatterBounds"));
	LandScatterBounds->SetupAttachment(Root);
	LandScatterBounds->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	LandScatterBounds->SetHiddenInGame(true);
	LandScatterBounds->ComponentTags.AddUnique(PCGInclusionTag);

	InlandVegetationPCG =
		CreateDefaultSubobject<UPCGComponent>(TEXT("InlandVegetationPCG"));
	InlandVegetationPCG->bActivated = false;
	InlandVegetationPCG->GenerationTrigger =
		EPCGComponentGenerationTrigger::GenerateOnDemand;
	AuthoredPCGGraph = TSoftObjectPtr<UPCGGraphInterface>(
		FSoftObjectPath(TEXT(
			"/Game/Skyguard/Environment/Mission01/PCG/"
			"PCG_M01_InlandVegetation.PCG_M01_InlandVegetation")));

	static ConstructorHelpers::FObjectFinder<UStaticMesh> PlaneMesh(
		TEXT("/Engine/BasicShapes/Plane.Plane"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> CubeMesh(
		TEXT("/Engine/BasicShapes/Cube.Cube"));
	if (PlaneMesh.Succeeded())
	{
		OceanTiles->SetStaticMesh(PlaneMesh.Object);
	}
	if (CubeMesh.Succeeded())
	{
		BeachTiles->SetStaticMesh(CubeMesh.Object);
		LandTiles->SetStaticMesh(CubeMesh.Object);
	}

	static ConstructorHelpers::FObjectFinder<UMaterialInterface> OceanMaterialAsset(
		TEXT("/Game/Skyguard/Materials/Generated/M_L23_Ocean.M_L23_Ocean"));
	static ConstructorHelpers::FObjectFinder<UMaterialInterface> BeachMaterialAsset(
		TEXT("/Game/Skyguard/Materials/Generated/M_L23_Beach.M_L23_Beach"));
	static ConstructorHelpers::FObjectFinder<UMaterialInterface> LandMaterialAsset(
		TEXT("/Game/Skyguard/Materials/Generated/M_AsphaltRoad.M_AsphaltRoad"));
	if (OceanMaterialAsset.Succeeded()) OceanMaterial = OceanMaterialAsset.Object;
	if (BeachMaterialAsset.Succeeded()) BeachMaterial = BeachMaterialAsset.Object;
	if (LandMaterialAsset.Succeeded()) LandMaterial = LandMaterialAsset.Object;

	Tags.AddUnique(TEXT("Skyguard.Environment.Mission01.Production"));
	Tags.AddUnique(TEXT("Skyguard.Environment.Water"));
	Tags.AddUnique(TEXT("Skyguard.Environment.Coastline"));
	Tags.AddUnique(TEXT("Skyguard.Environment.PCGReady"));
}

void ASkyguardMission01EnvironmentDirector::BeginPlay()
{
	Super::BeginPlay();
	RefreshAuthoredEnvironmentBindings();
	if (!bEnableCoastalHazeTransition || !GetWorld())
	{
		SetActorTickEnabled(false);
		return;
	}
	for (TActorIterator<AExponentialHeightFog> It(GetWorld()); It; ++It)
	{
		AExponentialHeightFog* FogActor = *It;
		if (FogActor && FogActor->GetComponent())
		{
			RuntimeFogComponent = FogActor->GetComponent();
			RuntimeBaseFogDensity = RuntimeFogComponent->FogDensity;
			break;
		}
	}
	if (!RuntimeFogComponent.IsValid())
	{
		SetActorTickEnabled(false);
	}
}

void ASkyguardMission01EnvironmentDirector::Tick(const float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	UExponentialHeightFogComponent* Fog = RuntimeFogComponent.Get();
	if (!Fog || !bEnableCoastalHazeTransition)
	{
		return;
	}

	RuntimeVisibilityElapsedSeconds += FMath::Max(0.f, DeltaSeconds);
	const float Fade = FMath::Max(1.f, CoastalHazeFadeSeconds);
	const float FadeInStart = FMath::Max(5.f, CoastalHazeDelaySeconds);
	const float FadeInEnd = FadeInStart + Fade;
	const float FadeOutStart = FadeInEnd + FMath::Max(1.f, CoastalHazeHoldSeconds);
	const float FadeOutEnd = FadeOutStart + Fade;
	const float HazeDensity =
		RuntimeBaseFogDensity + FMath::Max(0.001f, CoastalHazeDensityIncrease);

	float AppliedDensity = RuntimeBaseFogDensity;
	if (RuntimeVisibilityElapsedSeconds >= FadeInStart &&
		RuntimeVisibilityElapsedSeconds < FadeInEnd)
	{
		const float Alpha =
			(RuntimeVisibilityElapsedSeconds - FadeInStart) / Fade;
		AppliedDensity = FMath::Lerp(RuntimeBaseFogDensity, HazeDensity, Alpha);
	}
	else if (RuntimeVisibilityElapsedSeconds < FadeOutStart &&
		RuntimeVisibilityElapsedSeconds >= FadeInEnd)
	{
		AppliedDensity = HazeDensity;
		if (!bVisibilityTransitionRecorded)
		{
			// Apply the real world-state change before recording evidence. The
			// telemetry observer never creates or substitutes the transition.
			Fog->SetFogDensity(HazeDensity);
			bVisibilityTransitionRecorded = true;
			USkyguardInputCombatPerformanceCapture::RecordGameplayEvent(
				this, TEXT("weather_visibility_transition"));
		}
	}
	else if (RuntimeVisibilityElapsedSeconds >= FadeOutStart &&
		RuntimeVisibilityElapsedSeconds < FadeOutEnd)
	{
		const float Alpha =
			(RuntimeVisibilityElapsedSeconds - FadeOutStart) / Fade;
		AppliedDensity = FMath::Lerp(HazeDensity, RuntimeBaseFogDensity, Alpha);
	}
	else if (RuntimeVisibilityElapsedSeconds >= FadeOutEnd)
	{
		Fog->SetFogDensity(RuntimeBaseFogDensity);
		USkyguardInputCombatPerformanceCapture::RecordGameplayEvent(
			this, TEXT("weather_visibility_transition_complete"));
		SetActorTickEnabled(false);
		return;
	}
	Fog->SetFogDensity(AppliedDensity);
}

void ASkyguardMission01EnvironmentDirector::OnConstruction(const FTransform& Transform)
{
	Super::OnConstruction(Transform);
	RebuildProductionLayout();
}

void ASkyguardMission01EnvironmentDirector::ConfigureInstanceComponent(
	UHierarchicalInstancedStaticMeshComponent* Component) const
{
	if (!Component)
	{
		return;
	}
	Component->SetMobility(EComponentMobility::Static);
	Component->SetCullDistances(30000, 180000);
	Component->bCastDynamicShadow = true;
	Component->bCastStaticShadow = true;
}

void ASkyguardMission01EnvironmentDirector::RebuildProductionLayout()
{
	OceanTiles->ClearInstances();
	BeachTiles->ClearInstances();
	LandTiles->ClearInstances();
	ConfigureInstanceComponent(OceanTiles);
	ConfigureInstanceComponent(BeachTiles);
	ConfigureInstanceComponent(LandTiles);
	LandTiles->SetVisibility(!bUseAuthoredLandscapeSurface, true);
	LandTiles->SetHiddenInGame(bUseAuthoredLandscapeSurface);

	if (OceanMaterial) OceanTiles->SetMaterial(0, OceanMaterial);
	if (BeachMaterial) BeachTiles->SetMaterial(0, BeachMaterial);
	if (LandMaterial) LandTiles->SetMaterial(0, LandMaterial);

	const float SafeDistrictLength = FMath::Max(1000.f, DistrictLengthCm);
	const int32 DistrictCount = FMath::Max(1, FMath::CeilToInt(RouteLengthCm / SafeDistrictLength));
	AddDistrictInstances(DistrictCount);

	RouteExclusion->SetRelativeLocation(FVector(RouteLengthCm * 0.5f, 0.f, 1000.f));
	RouteExclusion->SetBoxExtent(
		FVector(RouteLengthCm * 0.5f, RouteCorridorHalfWidthCm, 2500.f),
		false);

	const float LandStart = ShorelineLandOffsetCm + BeachWidthCm;
	const float LandWidth = FMath::Max(1000.f, InlandExtentCm - LandStart);
	LandScatterBounds->SetRelativeLocation(
		FVector(RouteLengthCm * 0.5f, LandStart + LandWidth * 0.5f, 1000.f));
	LandScatterBounds->SetBoxExtent(
		FVector(RouteLengthCm * 0.5f, LandWidth * 0.5f, 2500.f),
		false);

	Readiness.OceanTileCount = OceanTiles->GetInstanceCount();
	Readiness.BeachTileCount = BeachTiles->GetInstanceCount();
	Readiness.LandTileCount = LandTiles->GetInstanceCount();
	Readiness.bAuthoredLandscapeSurfaceExposed =
		bUseAuthoredLandscapeSurface
		&& Readiness.LandTileCount == 0;
	Readiness.bContinuousCoastline = HasContinuousCoastline();
	Readiness.bRouteExclusionValid = IsRouteExclusionSafe();
	RefreshAuthoredEnvironmentBindings();
}

void ASkyguardMission01EnvironmentDirector::
SetUseAuthoredLandscapeSurfaceForValidation(const bool bEnable)
{
	bUseAuthoredLandscapeSurface = bEnable;
	RebuildProductionLayout();
}

void ASkyguardMission01EnvironmentDirector::AddDistrictInstances(const int32 DistrictCount)
{
	const float SafeDistrictLength = FMath::Max(1000.f, DistrictLengthCm);
	const float LandStart = ShorelineLandOffsetCm + BeachWidthCm;
	const float LandWidth = FMath::Max(1000.f, InlandExtentCm - LandStart);
	const float OceanWidth = FMath::Max(1000.f, ShorelineLandOffsetCm + SeawardExtentCm);

	for (int32 Index = 0; Index < DistrictCount; ++Index)
	{
		const float Remaining = FMath::Max(0.f, RouteLengthCm - SafeDistrictLength * Index);
		const float TileLength = FMath::Min(SafeDistrictLength, Remaining);
		if (TileLength <= UE_KINDA_SMALL_NUMBER)
		{
			break;
		}
		const float X = SafeDistrictLength * Index + TileLength * 0.5f;
		OceanTiles->AddInstance(FTransform(
			FQuat::Identity,
			FVector(X, (ShorelineLandOffsetCm - SeawardExtentCm) * 0.5f, -160.f),
			FVector(TileLength / 100.f, OceanWidth / 100.f, 1.f)));
		BeachTiles->AddInstance(FTransform(
			FQuat::Identity,
			FVector(X, ShorelineLandOffsetCm + BeachWidthCm * 0.5f, -110.f),
			FVector(TileLength / 100.f, BeachWidthCm / 100.f, 1.f)));
		if (!bUseAuthoredLandscapeSurface)
		{
			LandTiles->AddInstance(FTransform(
				FQuat::Identity,
				FVector(X, LandStart + LandWidth * 0.5f, -120.f),
				FVector(TileLength / 100.f, LandWidth / 100.f, 1.f)));
		}
	}
}

bool ASkyguardMission01EnvironmentDirector::IsPointAllowedForPCG(const FVector& WorldPoint) const
{
	const FVector LocalPoint = GetActorTransform().InverseTransformPosition(WorldPoint);
	const float LandStart = ShorelineLandOffsetCm + BeachWidthCm;
	return LocalPoint.X >= 0.f
		&& LocalPoint.X <= RouteLengthCm
		&& LocalPoint.Y >= LandStart
		&& LocalPoint.Y <= InlandExtentCm
		&& FMath::Abs(LocalPoint.Y) > RouteCorridorHalfWidthCm;
}

bool ASkyguardMission01EnvironmentDirector::IsRouteExclusionSafe() const
{
	const FVector Extent = RouteExclusion ? RouteExclusion->GetUnscaledBoxExtent() : FVector::ZeroVector;
	return RouteExclusion
		&& FMath::IsNearlyEqual(Extent.X * 2.f, RouteLengthCm, 1.f)
		&& Extent.Y >= RouteCorridorHalfWidthCm
		&& ShorelineLandOffsetCm > RouteCorridorHalfWidthCm;
}

void ASkyguardMission01EnvironmentDirector::RefreshAuthoredEnvironmentBindings()
{
	if (!ProductionLandscape && GetWorld())
	{
		for (TActorIterator<ALandscapeProxy> It(GetWorld()); It; ++It)
		{
			if (It->ActorHasTag(Mission01LandscapeTag))
			{
				ProductionLandscape = *It;
				break;
			}
		}
	}

	UPCGGraphInterface* GraphInterface = AuthoredPCGGraph.Get();
	if (!GraphInterface && !AuthoredPCGGraph.IsNull())
	{
		GraphInterface = AuthoredPCGGraph.LoadSynchronous();
	}

	if (InlandVegetationPCG)
	{
		InlandVegetationPCG->SetGraphLocal(GraphInterface);
	}

	TArray<ULandscapeComponent*> LandscapeComponents;
	if (ProductionLandscape)
	{
		ProductionLandscape->GetComponents<ULandscapeComponent>(
			LandscapeComponents);
	}

	const float LandStart = ShorelineLandOffsetCm + BeachWidthCm;
	const float LandWidth = FMath::Max(1000.f, InlandExtentCm - LandStart);
	const FVector InclusionExtent = LandScatterBounds
		? LandScatterBounds->GetUnscaledBoxExtent()
		: FVector::ZeroVector;
	const bool bInclusionTagged =
		LandScatterBounds
		&& LandScatterBounds->ComponentHasTag(PCGInclusionTag)
		&& FMath::IsNearlyEqual(InclusionExtent.X * 2.f, RouteLengthCm, 1.f)
		&& FMath::IsNearlyEqual(InclusionExtent.Y * 2.f, LandWidth, 1.f);
	const bool bExclusionTagged =
		RouteExclusion
		&& RouteExclusion->ComponentHasTag(PCGExclusionTag)
		&& IsRouteExclusionSafe();

	Readiness.LandscapeComponentCount = LandscapeComponents.Num();
	Readiness.bProductionLandscapeBound =
		ProductionLandscape
		&& ProductionLandscape->GetLandscapeGuid().IsValid()
		&& Readiness.LandscapeComponentCount > 0;
	Readiness.bAuthoredPCGGraphBound =
		GraphInterface
		&& InlandVegetationPCG
		&& InlandVegetationPCG->GetGraph() != nullptr;
	Readiness.bPCGBoundsTagged = bInclusionTagged && bExclusionTagged;
	Readiness.bAuthoredPCGStructureReady =
		Readiness.bProductionLandscapeBound
		&& Readiness.bAuthoredPCGGraphBound
		&& Readiness.bPCGBoundsTagged
		&& Readiness.bContinuousCoastline
		&& Readiness.bRouteExclusionValid;
	Readiness.bLicensedVegetationApproved =
		bLicensedVegetationLibraryApproved;
	Readiness.bPCGGenerationAuthorized =
		bLicensedVegetationLibraryApproved
		&& bAllowAuthoredPCGGeneration;
	Readiness.bReadyForAuthoredPCGGeneration =
		Readiness.bAuthoredPCGStructureReady
		&& Readiness.bPCGGenerationAuthorized;

	if (InlandVegetationPCG)
	{
		// This gate is intentionally fail-closed. The editor authoring tool must
		// explicitly generate and bake governed output after this becomes true.
		InlandVegetationPCG->bActivated =
			Readiness.bReadyForAuthoredPCGGeneration;
	}
}

bool ASkyguardMission01EnvironmentDirector::HasContinuousCoastline() const
{
	const int32 Expected = FMath::Max(
		1,
		FMath::CeilToInt(RouteLengthCm / FMath::Max(1000.f, DistrictLengthCm)));
	const int32 ExpectedLandTiles =
		bUseAuthoredLandscapeSurface ? 0 : Expected;
	if (!OceanTiles || !BeachTiles || !LandTiles
		|| OceanTiles->GetInstanceCount() != Expected
		|| BeachTiles->GetInstanceCount() != Expected
		|| LandTiles->GetInstanceCount() != ExpectedLandTiles)
	{
		return false;
	}

	float PreviousEnd = 0.f;
	for (int32 Index = 0; Index < BeachTiles->GetInstanceCount(); ++Index)
	{
		FTransform Transform;
		if (!BeachTiles->GetInstanceTransform(Index, Transform, false))
		{
			return false;
		}
		const float HalfLength = Transform.GetScale3D().X * 50.f;
		const float Start = Transform.GetLocation().X - HalfLength;
		if (!FMath::IsNearlyEqual(Start, PreviousEnd, 1.f))
		{
			return false;
		}
		PreviousEnd = Transform.GetLocation().X + HalfLength;
	}
	return FMath::IsNearlyEqual(PreviousEnd, RouteLengthCm, 1.f);
}
