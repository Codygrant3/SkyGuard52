#include "SkyguardPatrolShipBoss.h"

#include "Misc/NumericLimits.h"
#include "SkyguardCpgHud.h"
#include "SkyguardCombatVFX.h"
#include "SkyguardPilotVoice.h"
#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "UObject/SoftObjectPath.h"

namespace SkyguardPatrolShipBossPrivate
{
	void BindMeshIfEmpty(UStaticMeshComponent* Component, UStaticMesh* Mesh)
	{
		if (!Component || Component->GetStaticMesh() || !Mesh)
		{
			return;
		}
		Component->SetStaticMesh(Mesh);
	}
}

ASkyguardPatrolShipBoss::ASkyguardPatrolShipBoss()
{
	PrimaryActorTick.bCanEverTick = true;

	Root = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
	SetRootComponent(Root);

	Hull = MakePart(TEXT("Hull"));
	Hull->SetRelativeScale3D(FVector(22.f, 6.4f, 3.6f));
	Hull->SetRelativeLocation(FVector(0.f, 0.f, 180.f));

	Superstructure = MakePart(TEXT("Superstructure"));
	Superstructure->SetRelativeScale3D(FVector(6.f, 4.2f, 3.2f));
	Superstructure->SetRelativeLocation(FVector(-280.f, 0.f, 420.f));

	SearchRadar = MakePart(TEXT("SearchRadar"));
	SearchRadar->SetRelativeScale3D(FVector(2.4f, 2.4f, 0.18f));
	SearchRadar->SetRelativeLocation(FVector(-280.f, 0.f, 620.f));

	MissileBank = MakePart(TEXT("MissileBank"));
	MissileBank->SetRelativeScale3D(FVector(3.2f, 2.2f, 1.1f));
	MissileBank->SetRelativeLocation(FVector(220.f, 0.f, 320.f));

	Ciws = MakePart(TEXT("CIWS"));
	Ciws->SetRelativeScale3D(FVector(0.8f, 0.8f, 1.4f));
	Ciws->SetRelativeLocation(FVector(620.f, 0.f, 340.f));

	Engines = MakePart(TEXT("Engines"));
	Engines->SetRelativeScale3D(FVector(3.4f, 5.4f, 2.2f));
	Engines->SetRelativeLocation(FVector(-820.f, 0.f, 200.f));

	DroneDeck = MakePart(TEXT("DroneDeck"));
	DroneDeck->SetRelativeScale3D(FVector(5.5f, 5.8f, 0.35f));
	DroneDeck->SetRelativeLocation(FVector(80.f, 0.f, 370.f));

	Tags.AddUnique(TEXT("Skyguard.PatrolShip"));
}

UStaticMeshComponent* ASkyguardPatrolShipBoss::MakePart(const TCHAR* Name)
{
	UStaticMeshComponent* Part =
		CreateDefaultSubobject<UStaticMeshComponent>(Name);
	Part->SetupAttachment(Root);
	Part->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
	Part->SetCollisionResponseToAllChannels(ECR_Block);
	return Part;
}

void ASkyguardPatrolShipBoss::BeginPlay()
{
	Super::BeginPlay();
	BindPresentation();
}

FSkyguardMeshBindSlot ASkyguardPatrolShipBoss::MakeHullBindSlot()
{
	FSkyguardMeshBindSlot Slot;
	Slot.SlotId = TEXT("PatrolShip.Hull");
	Slot.ProxyFallback = TSoftObjectPtr<UStaticMesh>(FSoftObjectPath(
		TEXT("/Engine/BasicShapes/Cube.Cube")));
	Slot.Notes = TEXT(
		"Preferred empty. ProxyFallback=engine Cube. No Harbor kit ship Preferred fill.");
	return Slot;
}

void ASkyguardPatrolShipBoss::BindPresentation()
{
	using namespace SkyguardPatrolShipBossPrivate;

	if (UStaticMesh* HullMesh =
		USkyguardRuntimeMeshCatalog::ResolveSlot(MakeHullBindSlot()))
	{
		BindMeshIfEmpty(Hull, HullMesh);
		BindMeshIfEmpty(Superstructure, HullMesh);
		BindMeshIfEmpty(MissileBank, HullMesh);
		BindMeshIfEmpty(Engines, HullMesh);
		BindMeshIfEmpty(DroneDeck, HullMesh);
	}

	FSkyguardMeshBindSlot CylinderSlot;
	CylinderSlot.ProxyFallback = TSoftObjectPtr<UStaticMesh>(FSoftObjectPath(
		TEXT("/Engine/BasicShapes/Cylinder.Cylinder")));
	if (UStaticMesh* CylinderMesh =
		USkyguardRuntimeMeshCatalog::ResolveSlot(CylinderSlot))
	{
		BindMeshIfEmpty(SearchRadar, CylinderMesh);
		BindMeshIfEmpty(Ciws, CylinderMesh);
	}
}

void ASkyguardPatrolShipBoss::Tick(const float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	const float Speed = GetUnderwaySpeed();
	if (Speed <= KINDA_SMALL_NUMBER)
	{
		return;
	}
	AddActorWorldOffset(GetActorForwardVector() * Speed * DeltaSeconds, false);
}

void ASkyguardPatrolShipBoss::ApplyHit(
	UPrimitiveComponent* HitComponent,
	const float Damage)
{
	if (Damage <= 0.f || IsDefeated())
	{
		return;
	}

	const ESkyguardPatrolShipSystem Systems[] = {
		ESkyguardPatrolShipSystem::Radar,
		ESkyguardPatrolShipSystem::Launcher,
		ESkyguardPatrolShipSystem::Cannon,
		ESkyguardPatrolShipSystem::Engines,
		ESkyguardPatrolShipSystem::DroneDeck
	};
	for (const ESkyguardPatrolShipSystem System : Systems)
	{
		UPrimitiveComponent* Part = GetSystemComponent(System);
		if (HitComponent == Part)
		{
			ApplyHitToSystem(System, Damage);
			return;
		}
	}

	// Hull / superstructure / nullptr is a splash on the hull, not a
	// system kill. A single ApplyDamage to "the ship" cannot prove the boss.
}

void ASkyguardPatrolShipBoss::ApplyHitToSystem(
	const ESkyguardPatrolShipSystem System,
	const float Damage)
{
	if (Damage <= 0.f || IsDefeated() || IsSystemDead(System))
	{
		return;
	}
	float& Health = HealthFor(System);
	Health -= Damage;
	if (Health <= 0.f)
	{
		KillPart(
			Cast<UStaticMeshComponent>(GetSystemComponent(System)),
			Health,
			FName(SkyguardCpgShipSystemLabel(System)));
		AnnounceSystemKill(System);
	}
}

float ASkyguardPatrolShipBoss::GetUnderwaySpeed() const
{
	return AreEnginesDead() ? 0.f : UnderwayCruiseSpeed;
}

float ASkyguardPatrolShipBoss::GetCannonThreatDamage() const
{
	return CanFireCannon() ? CannonThreatDamage : 0.f;
}

bool ASkyguardPatrolShipBoss::ConsumeDeckLaunch(const float DeltaSeconds)
{
	if (!CanLaunchDrones())
	{
		DeckLaunchCooldown = DeckLaunchIntervalSeconds;
		return false;
	}
	DeckLaunchCooldown -= DeltaSeconds;
	if (DeckLaunchCooldown > 0.f)
	{
		return false;
	}
	DeckLaunchCooldown = DeckLaunchIntervalSeconds;
	return true;
}

void ASkyguardPatrolShipBoss::KillPart(
	UStaticMeshComponent* Part,
	float& Health,
	const FName Id)
{
	if (Health > 0.f)
	{
		return;
	}
	Health = 0.f;
	LastDestroyedSystem = Id;
	if (Part)
	{
		Part->SetVisibility(false);
		Part->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		USkyguardCombatVFX::SpawnExplosion(
			GetWorld(), Part->GetComponentLocation(), 1.15f);
	}
	if (IsDefeated())
	{
		SkyguardPilotVoice::CallEvent(this, ESkyguardPilotLine::ShipDead);
	}
}

bool ASkyguardPatrolShipBoss::IsDefeated() const
{
	return GetDestroyedSystemCount() >= 4;
}

bool ASkyguardPatrolShipBoss::IsSystemDead(const ESkyguardPatrolShipSystem System) const
{
	return HealthFor(System) <= 0.f;
}

int32 ASkyguardPatrolShipBoss::GetDestroyedSystemCount() const
{
	int32 Count = 0;
	Count += IsSystemDead(ESkyguardPatrolShipSystem::Radar) ? 1 : 0;
	Count += IsSystemDead(ESkyguardPatrolShipSystem::Cannon) ? 1 : 0;
	Count += IsSystemDead(ESkyguardPatrolShipSystem::Launcher) ? 1 : 0;
	Count += IsSystemDead(ESkyguardPatrolShipSystem::Engines) ? 1 : 0;
	Count += IsSystemDead(ESkyguardPatrolShipSystem::DroneDeck) ? 1 : 0;
	return Count;
}

FString ASkyguardPatrolShipBoss::GetHudSystemLine() const
{
	const ESkyguardPatrolShipSystem Systems[] = {
		ESkyguardPatrolShipSystem::Radar,
		ESkyguardPatrolShipSystem::Cannon,
		ESkyguardPatrolShipSystem::Launcher,
		ESkyguardPatrolShipSystem::Engines,
		ESkyguardPatrolShipSystem::DroneDeck
	};
	FString Line;
	for (int32 Index = 0; Index < UE_ARRAY_COUNT(Systems); ++Index)
	{
		if (Index > 0)
		{
			Line += TEXT(" ");
		}
		const TCHAR* Label = SkyguardCpgShipSystemLabel(Systems[Index]);
		if (IsSystemDead(Systems[Index]))
		{
			Line += FString::Printf(TEXT("X%s"), Label);
		}
		else
		{
			Line += Label;
		}
	}
	return Line;
}

ESkyguardPatrolShipSystem ASkyguardPatrolShipBoss::GetPriorityLiveSystem() const
{
	const ESkyguardPatrolShipSystem Systems[] = {
		ESkyguardPatrolShipSystem::Radar,
		ESkyguardPatrolShipSystem::Cannon,
		ESkyguardPatrolShipSystem::Launcher,
		ESkyguardPatrolShipSystem::Engines,
		ESkyguardPatrolShipSystem::DroneDeck
	};
	for (const ESkyguardPatrolShipSystem System : Systems)
	{
		if (!IsSystemDead(System))
		{
			return System;
		}
	}
	return ESkyguardPatrolShipSystem::Radar;
}

UPrimitiveComponent* ASkyguardPatrolShipBoss::GetSystemComponent(
	const ESkyguardPatrolShipSystem System) const
{
	switch (System)
	{
	case ESkyguardPatrolShipSystem::Radar:
		return SearchRadar;
	case ESkyguardPatrolShipSystem::Cannon:
		return Ciws;
	case ESkyguardPatrolShipSystem::Launcher:
		return MissileBank;
	case ESkyguardPatrolShipSystem::Engines:
		return Engines;
	case ESkyguardPatrolShipSystem::DroneDeck:
		return DroneDeck;
	default:
		return nullptr;
	}
}

UPrimitiveComponent* ASkyguardPatrolShipBoss::FindNearestLiveSystem(
	const FVector& WorldLocation) const
{
	UPrimitiveComponent* Best = nullptr;
	float BestDistSq = TNumericLimits<float>::Max();
	const ESkyguardPatrolShipSystem Systems[] = {
		ESkyguardPatrolShipSystem::Radar,
		ESkyguardPatrolShipSystem::Cannon,
		ESkyguardPatrolShipSystem::Launcher,
		ESkyguardPatrolShipSystem::Engines,
		ESkyguardPatrolShipSystem::DroneDeck
	};
	for (const ESkyguardPatrolShipSystem System : Systems)
	{
		if (IsSystemDead(System))
		{
			continue;
		}
		UPrimitiveComponent* Part = GetSystemComponent(System);
		if (!Part)
		{
			continue;
		}
		const float DistSq =
			FVector::DistSquared(WorldLocation, Part->GetComponentLocation());
		if (DistSq < BestDistSq)
		{
			BestDistSq = DistSq;
			Best = Part;
		}
	}
	return Best;
}

float& ASkyguardPatrolShipBoss::HealthFor(const ESkyguardPatrolShipSystem System)
{
	switch (System)
	{
	case ESkyguardPatrolShipSystem::Radar:
		return SearchRadarHealth;
	case ESkyguardPatrolShipSystem::Cannon:
		return CiwsHealth;
	case ESkyguardPatrolShipSystem::Launcher:
		return MissileHealth;
	case ESkyguardPatrolShipSystem::Engines:
		return EngineHealth;
	case ESkyguardPatrolShipSystem::DroneDeck:
		return DeckHealth;
	default:
		checkNoEntry();
		return SearchRadarHealth;
	}
}

float ASkyguardPatrolShipBoss::HealthFor(const ESkyguardPatrolShipSystem System) const
{
	switch (System)
	{
	case ESkyguardPatrolShipSystem::Radar:
		return SearchRadarHealth;
	case ESkyguardPatrolShipSystem::Cannon:
		return CiwsHealth;
	case ESkyguardPatrolShipSystem::Launcher:
		return MissileHealth;
	case ESkyguardPatrolShipSystem::Engines:
		return EngineHealth;
	case ESkyguardPatrolShipSystem::DroneDeck:
		return DeckHealth;
	default:
		return 0.f;
	}
}

void ASkyguardPatrolShipBoss::AnnounceSystemKill(
	const ESkyguardPatrolShipSystem System)
{
	switch (System)
	{
	case ESkyguardPatrolShipSystem::Radar:
		SkyguardPilotVoice::CallEvent(this, ESkyguardPilotLine::ShipRadarDown);
		break;
	case ESkyguardPatrolShipSystem::Cannon:
		SkyguardPilotVoice::CallEvent(this, ESkyguardPilotLine::ShipCannonDown);
		break;
	case ESkyguardPatrolShipSystem::Launcher:
		SkyguardPilotVoice::CallEvent(this, ESkyguardPilotLine::ShipLauncherDown);
		break;
	case ESkyguardPatrolShipSystem::Engines:
		SkyguardPilotVoice::CallEvent(this, ESkyguardPilotLine::ShipEnginesDown);
		break;
	case ESkyguardPatrolShipSystem::DroneDeck:
		SkyguardPilotVoice::CallEvent(this, ESkyguardPilotLine::ShipDeckDown);
		break;
	default:
		break;
	}
}
