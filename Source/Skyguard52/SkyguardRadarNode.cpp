#include "SkyguardRadarNode.h"

#include "SkyguardCombatVFX.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "UObject/ConstructorHelpers.h"

ASkyguardRadarNode::ASkyguardRadarNode()
{
	PrimaryActorTick.bCanEverTick = false;
	Body = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Body"));
	SetRootComponent(Body);
	Body->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
	Body->SetCollisionResponseToAllChannels(ECR_Block);
	static ConstructorHelpers::FObjectFinder<UStaticMesh> Cube(
		TEXT("/Engine/BasicShapes/Cube.Cube"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> Cylinder(
		TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
	if (Cube.Succeeded())
	{
		Body->SetStaticMesh(Cube.Object);
	}
	Body->SetRelativeScale3D(FVector(2.4f, 1.6f, 1.1f));

	Dish = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Dish"));
	Dish->SetupAttachment(Body);
	if (Cylinder.Succeeded())
	{
		Dish->SetStaticMesh(Cylinder.Object);
	}
	Dish->SetRelativeLocation(FVector(0.f, 0.f, 90.f));
	Dish->SetRelativeScale3D(FVector(1.8f, 1.8f, 0.12f));

	Tags.AddUnique(TEXT("Skyguard.RadarNode"));
	Health = MaxHealth;
}

void ASkyguardRadarNode::ApplyDamage(const float Amount)
{
	if (bDead || Amount <= 0.f)
	{
		return;
	}
	Health -= Amount;
	if (Health <= 0.f)
	{
		bDead = true;
		USkyguardCombatVFX::SpawnExplosion(GetWorld(), GetActorLocation(), 1.4f);
		if (Dish)
		{
			Dish->SetVisibility(false);
		}
		SetActorEnableCollision(false);
	}
}

void ASkyguardRadarNode::ResetNode()
{
	bDead = false;
	Health = MaxHealth;
	SetActorEnableCollision(true);
	if (Dish)
	{
		Dish->SetVisibility(true);
	}
	if (Body)
	{
		Body->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
	}
}
