#include "SkyguardPatrolShipBoss.h"

#include "SkyguardCombatVFX.h"
#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "UObject/ConstructorHelpers.h"

ASkyguardPatrolShipBoss::ASkyguardPatrolShipBoss()
{
	Root = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
	SetRootComponent(Root);

	static ConstructorHelpers::FObjectFinder<UStaticMesh> Cube(
		TEXT("/Engine/BasicShapes/Cube.Cube"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> Cylinder(
		TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
	UStaticMesh* CubeMesh = Cube.Succeeded() ? Cube.Object : nullptr;
	UStaticMesh* CylMesh = Cylinder.Succeeded() ? Cylinder.Object : nullptr;

	Hull = MakePart(TEXT("Hull"), CubeMesh);
	Hull->SetRelativeScale3D(FVector(22.f, 6.4f, 3.6f));
	Hull->SetRelativeLocation(FVector(0.f, 0.f, 180.f));

	Superstructure = MakePart(TEXT("Superstructure"), CubeMesh);
	Superstructure->SetRelativeScale3D(FVector(6.f, 4.2f, 3.2f));
	Superstructure->SetRelativeLocation(FVector(-280.f, 0.f, 420.f));

	SearchRadar = MakePart(TEXT("SearchRadar"), CylMesh);
	SearchRadar->SetRelativeScale3D(FVector(2.4f, 2.4f, 0.18f));
	SearchRadar->SetRelativeLocation(FVector(-280.f, 0.f, 620.f));

	MissileBank = MakePart(TEXT("MissileBank"), CubeMesh);
	MissileBank->SetRelativeScale3D(FVector(3.2f, 2.2f, 1.1f));
	MissileBank->SetRelativeLocation(FVector(220.f, 0.f, 320.f));

	Ciws = MakePart(TEXT("CIWS"), CylMesh);
	Ciws->SetRelativeScale3D(FVector(0.8f, 0.8f, 1.4f));
	Ciws->SetRelativeLocation(FVector(620.f, 0.f, 340.f));

	Engines = MakePart(TEXT("Engines"), CubeMesh);
	Engines->SetRelativeScale3D(FVector(3.4f, 5.4f, 2.2f));
	Engines->SetRelativeLocation(FVector(-820.f, 0.f, 200.f));

	DroneDeck = MakePart(TEXT("DroneDeck"), CubeMesh);
	DroneDeck->SetRelativeScale3D(FVector(5.5f, 5.8f, 0.35f));
	DroneDeck->SetRelativeLocation(FVector(80.f, 0.f, 370.f));

	Tags.AddUnique(TEXT("Skyguard.PatrolShip"));
}

UStaticMeshComponent* ASkyguardPatrolShipBoss::MakePart(
	const TCHAR* Name,
	UStaticMesh* Mesh)
{
	UStaticMeshComponent* Part =
		CreateDefaultSubobject<UStaticMeshComponent>(Name);
	Part->SetupAttachment(Root);
	Part->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
	Part->SetCollisionResponseToAllChannels(ECR_Block);
	if (Mesh)
	{
		Part->SetStaticMesh(Mesh);
	}
	return Part;
}

void ASkyguardPatrolShipBoss::ApplyHit(
	UPrimitiveComponent* HitComponent,
	const float Damage)
{
	if (Damage <= 0.f || IsDefeated())
	{
		return;
	}
	auto Hurt = [this, HitComponent, Damage](
		UStaticMeshComponent* Part, float& Health, const FName Id)
	{
		if (HitComponent == Part || (!HitComponent && Part == Hull))
		{
			Health -= Damage;
			if (Health <= 0.f)
			{
				KillPart(Part, Health, Id);
			}
			return true;
		}
		return false;
	};

	if (Hurt(SearchRadar, SearchRadarHealth, TEXT("SearchRadar"))) return;
	if (Hurt(MissileBank, MissileHealth, TEXT("MissileBank"))) return;
	if (Hurt(Ciws, CiwsHealth, TEXT("CIWS"))) return;
	if (Hurt(Engines, EngineHealth, TEXT("Engines"))) return;
	if (Hurt(DroneDeck, DeckHealth, TEXT("DroneDeck"))) return;

	// Hull splash feeds the closest remaining system.
	if (MissileHealth > 0.f) { MissileHealth -= Damage * 0.35f; }
	else if (EngineHealth > 0.f) { EngineHealth -= Damage * 0.35f; }
	if (MissileHealth <= 0.f) KillPart(MissileBank, MissileHealth, TEXT("MissileBank"));
	if (EngineHealth <= 0.f) KillPart(Engines, EngineHealth, TEXT("Engines"));
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
}

bool ASkyguardPatrolShipBoss::IsDefeated() const
{
	return GetDestroyedSystemCount() >= 4;
}

int32 ASkyguardPatrolShipBoss::GetDestroyedSystemCount() const
{
	int32 Count = 0;
	Count += SearchRadarHealth <= 0.f ? 1 : 0;
	Count += MissileHealth <= 0.f ? 1 : 0;
	Count += CiwsHealth <= 0.f ? 1 : 0;
	Count += EngineHealth <= 0.f ? 1 : 0;
	Count += DeckHealth <= 0.f ? 1 : 0;
	return Count;
}
