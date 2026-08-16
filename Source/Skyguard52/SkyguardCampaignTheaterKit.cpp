#include "SkyguardCampaignTheaterKit.h"

#include "SkyguardGunshipSortieDirector.h"
#include "Components/HierarchicalInstancedStaticMeshComponent.h"
#include "Components/MeshComponent.h"
#include "Components/PointLightComponent.h"
#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Materials/MaterialInterface.h"
#include "UObject/ConstructorHelpers.h"

namespace
{
	FSkyguardTheaterKitSpec MakeKit(
		const TCHAR* WeatherIdentity,
		const TCHAR* KitId,
		const TCHAR* LandmarkSet,
		const TCHAR* BuildingKit,
		const FLinearColor BuildingTint,
		const TCHAR* LampTreatment,
		const FLinearColor LampColor,
		const float LampIntensity,
		const TCHAR* RoadTreatment,
		const FLinearColor RoadTint,
		const TCHAR* NamedLandmark,
		const FLinearColor LandmarkTint,
		const TCHAR* SilhouetteKit,
		const FLinearColor SilhouetteTint,
		const int32 LandmarkMeshIndex,
		const FVector LandmarkScale)
	{
		FSkyguardTheaterKitSpec Spec;
		Spec.WeatherIdentity = WeatherIdentity;
		Spec.KitId = KitId;
		Spec.LandmarkSet = LandmarkSet;
		Spec.BuildingKit = BuildingKit;
		Spec.BuildingTint = BuildingTint;
		Spec.LampTreatment = LampTreatment;
		Spec.LampColor = LampColor;
		Spec.LampIntensity = LampIntensity;
		Spec.RoadTreatment = RoadTreatment;
		Spec.RoadTint = RoadTint;
		Spec.NamedLandmark = NamedLandmark;
		Spec.LandmarkTint = LandmarkTint;
		Spec.SilhouetteKit = SilhouetteKit;
		Spec.SilhouetteTint = SilhouetteTint;
		Spec.LandmarkMeshIndex = LandmarkMeshIndex;
		Spec.LandmarkScale = LandmarkScale;
		return Spec;
	}

	const FSkyguardTheaterKitSpec GKits[] = {
		MakeKit(
			TEXT("ClearNoon"), TEXT("Kit.ClearNoon.CoastalPier"),
			TEXT("PierSet"), TEXT("SunbleachedCoast"),
			FLinearColor(0.76f, 0.68f, 0.48f),
			TEXT("DayOff"), FLinearColor(1.f, 0.92f, 0.7f), 0.f,
			TEXT("DryAsphalt"), FLinearColor(0.22f, 0.22f, 0.2f),
			TEXT("WatchPier"), FLinearColor(0.82f, 0.74f, 0.52f),
			TEXT("LowCoast"), FLinearColor(0.55f, 0.58f, 0.5f),
			0, FVector(3.2f, 8.f, 2.4f)),
		MakeKit(
			TEXT("HarborOvercast"), TEXT("Kit.HarborOvercast.Breakwater"),
			TEXT("CraneSet"), TEXT("HarborConcrete"),
			FLinearColor(0.42f, 0.46f, 0.5f),
			TEXT("HarborAmber"), FLinearColor(1.f, 0.62f, 0.28f), 4200.f,
			TEXT("WetHarbor"), FLinearColor(0.16f, 0.18f, 0.2f),
			TEXT("BreakwaterLight"), FLinearColor(0.7f, 0.72f, 0.68f),
			TEXT("CraneRow"), FLinearColor(0.32f, 0.34f, 0.36f),
			1, FVector(2.2f, 2.2f, 16.f)),
		MakeKit(
			TEXT("DryMorning"), TEXT("Kit.DryMorning.RidgeHighway"),
			TEXT("OverpassSet"), TEXT("DustStucco"),
			FLinearColor(0.72f, 0.58f, 0.36f),
			TEXT("HighwaySodium"), FLinearColor(1.f, 0.72f, 0.22f), 2800.f,
			TEXT("DryDust"), FLinearColor(0.48f, 0.4f, 0.26f),
			TEXT("RidgeOverpass"), FLinearColor(0.62f, 0.5f, 0.32f),
			TEXT("RidgeCut"), FLinearColor(0.5f, 0.42f, 0.3f),
			0, FVector(10.f, 2.4f, 3.6f)),
		MakeKit(
			TEXT("BlackoutNight"), TEXT("Kit.BlackoutNight.GridBlackout"),
			TEXT("DarkBlockSet"), TEXT("BlackoutMasonry"),
			FLinearColor(0.12f, 0.13f, 0.16f),
			TEXT("BlackoutDark"), FLinearColor(0.35f, 0.4f, 0.55f), 80.f,
			TEXT("NightAsphalt"), FLinearColor(0.08f, 0.08f, 0.1f),
			TEXT("DarkGridTower"), FLinearColor(0.18f, 0.2f, 0.24f),
			TEXT("DarkBlocks"), FLinearColor(0.1f, 0.11f, 0.14f),
			1, FVector(2.8f, 2.8f, 18.f)),
		MakeKit(
			TEXT("SevereSquall"), TEXT("Kit.SevereSquall.RiverSpan"),
			TEXT("BargeSet"), TEXT("StormConcrete"),
			FLinearColor(0.28f, 0.32f, 0.34f),
			TEXT("StormStrobe"), FLinearColor(0.7f, 0.82f, 1.f), 5600.f,
			TEXT("Flooded"), FLinearColor(0.14f, 0.16f, 0.18f),
			TEXT("RiverSpan"), FLinearColor(0.36f, 0.4f, 0.42f),
			TEXT("BargeLine"), FLinearColor(0.24f, 0.26f, 0.28f),
			2, FVector(14.f, 2.f, 2.8f)),
		MakeKit(
			TEXT("AirfieldHaze"), TEXT("Kit.AirfieldHaze.FieldTower"),
			TEXT("HangarSet"), TEXT("HazeHangar"),
			FLinearColor(0.62f, 0.58f, 0.42f),
			TEXT("AirfieldBlue"), FLinearColor(0.55f, 0.72f, 1.f), 3800.f,
			TEXT("Tarmac"), FLinearColor(0.2f, 0.2f, 0.18f),
			TEXT("ControlTower"), FLinearColor(0.7f, 0.68f, 0.5f),
			TEXT("HangarRow"), FLinearColor(0.46f, 0.44f, 0.34f),
			1, FVector(3.4f, 3.4f, 14.f)),
		MakeKit(
			TEXT("IslandMist"), TEXT("Kit.IslandMist.WreckBeacon"),
			TEXT("WreckSet"), TEXT("MistTimber"),
			FLinearColor(0.48f, 0.44f, 0.38f),
			TEXT("IslandFog"), FLinearColor(1.f, 0.78f, 0.45f), 1600.f,
			TEXT("IslandTrack"), FLinearColor(0.3f, 0.28f, 0.22f),
			TEXT("WreckBeacon"), FLinearColor(0.55f, 0.42f, 0.3f),
			TEXT("WreckMast"), FLinearColor(0.4f, 0.36f, 0.3f),
			3, FVector(2.4f, 2.4f, 10.f)),
		MakeKit(
			TEXT("RescueSunset"), TEXT("Kit.RescueSunset.BatteryHouse"),
			TEXT("BatterySet"), TEXT("SunsetBrick"),
			FLinearColor(0.58f, 0.28f, 0.18f),
			TEXT("SunsetWarm"), FLinearColor(1.f, 0.48f, 0.18f), 4400.f,
			TEXT("CityWet"), FLinearColor(0.18f, 0.16f, 0.16f),
			TEXT("BatteryHouse"), FLinearColor(0.64f, 0.3f, 0.16f),
			TEXT("GunLine"), FLinearColor(0.42f, 0.24f, 0.18f),
			0, FVector(5.f, 4.f, 6.f)),
		MakeKit(
			TEXT("CityDusk"), TEXT("Kit.CityDusk.TelYard"),
			TEXT("YardSet"), TEXT("DuskGlass"),
			FLinearColor(0.32f, 0.36f, 0.42f),
			TEXT("CitySodium"), FLinearColor(1.f, 0.58f, 0.2f), 5000.f,
			TEXT("CityDuskAsphalt"), FLinearColor(0.12f, 0.12f, 0.14f),
			TEXT("TelYardStack"), FLinearColor(0.28f, 0.32f, 0.38f),
			TEXT("StackRow"), FLinearColor(0.22f, 0.24f, 0.3f),
			1, FVector(2.6f, 2.6f, 20.f)),
		MakeKit(
			TEXT("EvacuationDawn"), TEXT("Kit.EvacuationDawn.FortressKeep"),
			TEXT("KeepSet"), TEXT("DawnBunker"),
			FLinearColor(0.38f, 0.4f, 0.34f),
			TEXT("DawnCold"), FLinearColor(0.7f, 0.82f, 1.f), 2400.f,
			TEXT("FortressStone"), FLinearColor(0.26f, 0.26f, 0.22f),
			TEXT("FortressKeep"), FLinearColor(0.44f, 0.46f, 0.38f),
			TEXT("KeepWall"), FLinearColor(0.3f, 0.32f, 0.28f),
			0, FVector(8.f, 8.f, 12.f))
	};

	const FName BuildingTag(TEXT("Skyguard.Theater.Building"));
	const FName LampTag(TEXT("Skyguard.Theater.Lamp"));
	const FName RoadTag(TEXT("Skyguard.Theater.Road"));
	const FName LandmarkTag(TEXT("Skyguard.Theater.Landmark"));
	const FName SilhouetteTag(TEXT("Skyguard.Theater.Silhouette"));
}

int32 SkyguardCampaignTheaterKit::NumKits()
{
	return UE_ARRAY_COUNT(GKits);
}

const FSkyguardTheaterKitSpec& SkyguardCampaignTheaterKit::GetByIndex(const int32 Index)
{
	const int32 Safe = FMath::Clamp(Index, 0, NumKits() - 1);
	return GKits[Safe];
}

const FSkyguardTheaterKitSpec& SkyguardCampaignTheaterKit::Resolve(
	const FName WeatherIdentity)
{
	for (int32 Index = 0; Index < NumKits(); ++Index)
	{
		if (GKits[Index].WeatherIdentity == WeatherIdentity)
		{
			return GKits[Index];
		}
	}
	return GKits[0];
}

FString SkyguardCampaignTheaterKit::Fingerprint(const FSkyguardTheaterKitSpec& Spec)
{
	return FString::Printf(
		TEXT("%s|%s|%s|%s|%s|%s|%s|%.3f,%.3f,%.3f"),
		*Spec.KitId.ToString(),
		*Spec.NamedLandmark.ToString(),
		*Spec.LandmarkSet.ToString(),
		*Spec.BuildingKit.ToString(),
		*Spec.LampTreatment.ToString(),
		*Spec.RoadTreatment.ToString(),
		*Spec.SilhouetteKit.ToString(),
		Spec.BuildingTint.R,
		Spec.BuildingTint.G,
		Spec.BuildingTint.B);
}

bool SkyguardCampaignTheaterKit::AreKitsPairwiseDistinct()
{
	TSet<FName> KitIds;
	TSet<FName> Landmarks;
	TSet<FString> Prints;
	for (int32 Index = 0; Index < NumKits(); ++Index)
	{
		const FSkyguardTheaterKitSpec& Spec = GKits[Index];
		if (Spec.KitId.IsNone() ||
			Spec.NamedLandmark.IsNone() ||
			KitIds.Contains(Spec.KitId) ||
			Landmarks.Contains(Spec.NamedLandmark) ||
			Prints.Contains(Fingerprint(Spec)))
		{
			return false;
		}
		KitIds.Add(Spec.KitId);
		Landmarks.Add(Spec.NamedLandmark);
		Prints.Add(Fingerprint(Spec));
	}
	return KitIds.Num() == NumKits();
}

ASkyguardCampaignTheaterKit::ASkyguardCampaignTheaterKit()
{
	PrimaryActorTick.bCanEverTick = false;

	Root = CreateDefaultSubobject<USceneComponent>(TEXT("TheaterRoot"));
	SetRootComponent(Root);

	RoadInstances =
		CreateDefaultSubobject<UHierarchicalInstancedStaticMeshComponent>(TEXT("RoadInstances"));
	RoadInstances->SetupAttachment(Root);
	RoadInstances->SetCollisionEnabled(ECollisionEnabled::NoCollision);

	BuildingInstances =
		CreateDefaultSubobject<UHierarchicalInstancedStaticMeshComponent>(TEXT("BuildingInstances"));
	BuildingInstances->SetupAttachment(Root);
	BuildingInstances->SetCollisionEnabled(ECollisionEnabled::NoCollision);

	LampInstances =
		CreateDefaultSubobject<UHierarchicalInstancedStaticMeshComponent>(TEXT("LampInstances"));
	LampInstances->SetupAttachment(Root);
	LampInstances->SetCollisionEnabled(ECollisionEnabled::NoCollision);

	SilhouetteInstances =
		CreateDefaultSubobject<UHierarchicalInstancedStaticMeshComponent>(TEXT("SilhouetteInstances"));
	SilhouetteInstances->SetupAttachment(Root);
	SilhouetteInstances->SetCollisionEnabled(ECollisionEnabled::NoCollision);

	NamedLandmarkMesh =
		CreateDefaultSubobject<UStaticMeshComponent>(TEXT("NamedLandmarkMesh"));
	NamedLandmarkMesh->SetupAttachment(Root);
	NamedLandmarkMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);

	static ConstructorHelpers::FObjectFinder<UStaticMesh> CubeAsset(
		TEXT("/Engine/BasicShapes/Cube.Cube"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> CylinderAsset(
		TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> ConeAsset(
		TEXT("/Engine/BasicShapes/Cone.Cone"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> SphereAsset(
		TEXT("/Engine/BasicShapes/Sphere.Sphere"));
	static ConstructorHelpers::FObjectFinder<UMaterialInterface> ShapeMat(
		TEXT("/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial"));
	if (CubeAsset.Succeeded())
	{
		CubeMesh = CubeAsset.Object;
	}
	if (CylinderAsset.Succeeded())
	{
		CylinderMesh = CylinderAsset.Object;
	}
	if (ConeAsset.Succeeded())
	{
		ConeMesh = ConeAsset.Object;
	}
	if (SphereAsset.Succeeded())
	{
		SphereMesh = SphereAsset.Object;
	}
	if (ShapeMat.Succeeded())
	{
		ShapeMaterial = ShapeMat.Object;
	}

	if (CubeMesh)
	{
		RoadInstances->SetStaticMesh(CubeMesh);
		BuildingInstances->SetStaticMesh(CubeMesh);
		SilhouetteInstances->SetStaticMesh(CubeMesh);
		NamedLandmarkMesh->SetStaticMesh(CubeMesh);
	}
	if (CylinderMesh)
	{
		LampInstances->SetStaticMesh(CylinderMesh);
	}
	else if (CubeMesh)
	{
		LampInstances->SetStaticMesh(CubeMesh);
	}

	Tags.AddUnique(TEXT("Skyguard.CampaignTheaterKit"));
}

void ASkyguardCampaignTheaterKit::BeginPlay()
{
	Super::BeginPlay();
	if (AppliedSpec.KitId.IsNone())
	{
		ApplyTheaterKit(TEXT("ClearNoon"));
	}
}

void ASkyguardCampaignTheaterKit::ApplyTheaterKitToWorld(
	UObject* WorldContextObject,
	const FName WeatherIdentity)
{
	UWorld* World = WorldContextObject ? WorldContextObject->GetWorld() : nullptr;
	if (!World)
	{
		return;
	}

	ASkyguardCampaignTheaterKit* Kit = nullptr;
	for (TActorIterator<ASkyguardCampaignTheaterKit> It(World); It; ++It)
	{
		if (IsValid(*It))
		{
			Kit = *It;
			break;
		}
	}
	if (!Kit)
	{
		FActorSpawnParameters Params;
		Params.SpawnCollisionHandlingOverride =
			ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
		Kit = World->SpawnActor<ASkyguardCampaignTheaterKit>(
			FVector::ZeroVector, FRotator::ZeroRotator, Params);
	}
	if (Kit)
	{
		Kit->ApplyTheaterKit(WeatherIdentity);
	}
}

void ASkyguardCampaignTheaterKit::ApplyTheaterKit(const FName WeatherIdentity)
{
	AppliedSpec = SkyguardCampaignTheaterKit::Resolve(WeatherIdentity);
	RebuildDressing();
	RestyleTaggedWorldActors();
}

int32 ASkyguardCampaignTheaterKit::CountInstances(
	const UHierarchicalInstancedStaticMeshComponent* Component)
{
	return Component ? Component->GetInstanceCount() : 0;
}

int32 ASkyguardCampaignTheaterKit::GetRoadInstanceCount() const
{
	return CountInstances(RoadInstances);
}

int32 ASkyguardCampaignTheaterKit::GetBuildingInstanceCount() const
{
	return CountInstances(BuildingInstances);
}

int32 ASkyguardCampaignTheaterKit::GetLampInstanceCount() const
{
	return CountInstances(LampInstances);
}

int32 ASkyguardCampaignTheaterKit::GetSilhouetteInstanceCount() const
{
	return CountInstances(SilhouetteInstances);
}

UStaticMesh* ASkyguardCampaignTheaterKit::MeshForLandmark(const int32 MeshIndex) const
{
	switch (MeshIndex)
	{
	case 1:
		return CylinderMesh ? CylinderMesh : CubeMesh;
	case 2:
		return ConeMesh ? ConeMesh : CubeMesh;
	case 3:
		return SphereMesh ? SphereMesh : CubeMesh;
	case 0:
	default:
		return CubeMesh;
	}
}

void ASkyguardCampaignTheaterKit::ApplyTint(
	UMeshComponent* Component,
	const FLinearColor& Tint) const
{
	if (!Component || !ShapeMaterial)
	{
		return;
	}
	UMaterialInstanceDynamic* Mid =
		UMaterialInstanceDynamic::Create(ShapeMaterial, Component);
	if (!Mid)
	{
		return;
	}
	Mid->SetVectorParameterValue(TEXT("Color"), Tint);
	Mid->SetVectorParameterValue(TEXT("BaseColor"), Tint);
	Component->SetMaterial(0, Mid);
}

void ASkyguardCampaignTheaterKit::EnsureLamps()
{
	if (Lamps.Num() > 0)
	{
		return;
	}
	for (int32 Index = 0; Index < 6; ++Index)
	{
		UPointLightComponent* Light = NewObject<UPointLightComponent>(
			this,
			*FString::Printf(TEXT("TheaterLamp%d"), Index));
		if (!Light)
		{
			continue;
		}
		Light->SetupAttachment(Root);
		Light->SetMobility(EComponentMobility::Movable);
		if (!Light->IsRegistered())
		{
			Light->RegisterComponent();
		}
		Lamps.Add(Light);
	}
}

void ASkyguardCampaignTheaterKit::RebuildDressing()
{
	const TArray<FVector> Path = ASkyguardGunshipSortieDirector::GetCoastalHighwayPath();
	if (RoadInstances)
	{
		RoadInstances->ClearInstances();
		ApplyTint(RoadInstances, AppliedSpec.RoadTint);
		for (int32 Index = 0; Index < Path.Num(); ++Index)
		{
			const FVector& From = Path[Index];
			const FVector& To = Path[(Index + 1) % Path.Num()];
			const FVector Mid = (From + To) * 0.5f;
			const FVector Delta = To - From;
			const float Length = FMath::Max(200.f, Delta.Size2D());
			const float Yaw = FMath::RadiansToDegrees(FMath::Atan2(Delta.Y, Delta.X));
			RoadInstances->AddInstance(
				FTransform(
					FRotator(0.f, Yaw, 0.f),
					FVector(Mid.X, Mid.Y, Mid.Z - 20.f),
					FVector(Length / 100.f, 1.8f, 0.18f)));
		}
	}

	if (BuildingInstances)
	{
		BuildingInstances->ClearInstances();
		ApplyTint(BuildingInstances, AppliedSpec.BuildingTint);
		const int32 BuildingCount = 8 + (AppliedSpec.LandmarkMeshIndex % 3);
		for (int32 Index = 0; Index < BuildingCount && Path.Num() > 0; ++Index)
		{
			const FVector Anchor = Path[Index % Path.Num()];
			const float Inland = 900.f + (Index % 4) * 280.f;
			const float Height = 4.f + static_cast<float>((Index * 3) % 7);
			BuildingInstances->AddInstance(
				FTransform(
					FRotator::ZeroRotator,
					FVector(Anchor.X + 180.f, Anchor.Y + Inland, Height * 50.f),
					FVector(2.4f + (Index % 3), 2.2f, Height)));
		}
	}

	if (LampInstances)
	{
		LampInstances->ClearInstances();
		ApplyTint(LampInstances, AppliedSpec.LampColor);
		EnsureLamps();
		const int32 LampCount = FMath::Min(Lamps.Num(), Path.Num());
		for (int32 Index = 0; Index < LampCount; ++Index)
		{
			const FVector Anchor = Path[(Index * 2) % Path.Num()];
			const FVector Post(Anchor.X, Anchor.Y + 220.f, Anchor.Z + 180.f);
			LampInstances->AddInstance(
				FTransform(
					FRotator::ZeroRotator,
					Post,
					FVector(0.18f, 0.18f, 3.6f)));
			if (UPointLightComponent* Light = Lamps[Index])
			{
				Light->SetWorldLocation(Post + FVector(0.f, 0.f, 220.f));
				Light->SetLightColor(AppliedSpec.LampColor);
				Light->SetIntensity(AppliedSpec.LampIntensity);
				Light->SetVisibility(AppliedSpec.LampIntensity > 1.f);
				Light->SetAttenuationRadius(2400.f);
			}
		}
		for (int32 Index = LampCount; Index < Lamps.Num(); ++Index)
		{
			if (Lamps[Index])
			{
				Lamps[Index]->SetVisibility(false);
			}
		}
	}

	if (SilhouetteInstances)
	{
		SilhouetteInstances->ClearInstances();
		ApplyTint(SilhouetteInstances, AppliedSpec.SilhouetteTint);
		const int32 Row = 5 + AppliedSpec.LandmarkMeshIndex;
		for (int32 Index = 0; Index < Row; ++Index)
		{
			const float Along = -2000.f + Index * 720.f;
			const float Height = 8.f + static_cast<float>((Index + AppliedSpec.LandmarkMeshIndex) % 5) * 3.f;
			SilhouetteInstances->AddInstance(
				FTransform(
					FRotator::ZeroRotator,
					FVector(Along, 2800.f, Height * 50.f),
					FVector(3.2f, 2.4f, Height)));
		}
	}

	if (NamedLandmarkMesh)
	{
		if (UStaticMesh* LandmarkMesh = MeshForLandmark(AppliedSpec.LandmarkMeshIndex))
		{
			NamedLandmarkMesh->SetStaticMesh(LandmarkMesh);
		}
		NamedLandmarkMesh->SetWorldLocation(FVector(1800.f, -5200.f, 420.f));
		NamedLandmarkMesh->SetWorldScale3D(AppliedSpec.LandmarkScale);
		ApplyTint(NamedLandmarkMesh, AppliedSpec.LandmarkTint);
		NamedLandmarkMesh->ComponentTags.Reset();
		NamedLandmarkMesh->ComponentTags.AddUnique(AppliedSpec.NamedLandmark);
	}
}

void ASkyguardCampaignTheaterKit::RestyleTaggedWorldActors() const
{
	UWorld* World = GetWorld();
	if (!World)
	{
		return;
	}

	struct FTagTint
	{
		FName Tag;
		FLinearColor Tint;
	};
	const FTagTint Tints[] = {
		{BuildingTag, AppliedSpec.BuildingTint},
		{RoadTag, AppliedSpec.RoadTint},
		{LandmarkTag, AppliedSpec.LandmarkTint},
		{SilhouetteTag, AppliedSpec.SilhouetteTint},
		{LampTag, AppliedSpec.LampColor}
	};

	for (TActorIterator<AActor> It(World); It; ++It)
	{
		AActor* Actor = *It;
		if (!IsValid(Actor) || Actor == this)
		{
			continue;
		}
		for (const FTagTint& Entry : Tints)
		{
			if (!Actor->ActorHasTag(Entry.Tag))
			{
				continue;
			}
			TArray<UMeshComponent*> Meshes;
			Actor->GetComponents<UMeshComponent>(Meshes);
			for (UMeshComponent* Mesh : Meshes)
			{
				ApplyTint(Mesh, Entry.Tint);
			}
			if (Entry.Tag == LampTag)
			{
				TArray<UPointLightComponent*> Lights;
				Actor->GetComponents<UPointLightComponent>(Lights);
				for (UPointLightComponent* Light : Lights)
				{
					Light->SetLightColor(AppliedSpec.LampColor);
					Light->SetIntensity(AppliedSpec.LampIntensity);
					Light->SetVisibility(AppliedSpec.LampIntensity > 1.f);
				}
			}
		}
	}
}
