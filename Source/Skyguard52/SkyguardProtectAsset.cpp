#include "SkyguardProtectAsset.h"

#include "SkyguardCombatVFX.h"
#include "Components/BoxComponent.h"
#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "UObject/ConstructorHelpers.h"

ASkyguardProtectAsset::ASkyguardProtectAsset()
{
	Root = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
	SetRootComponent(Root);

	Hull = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Hull"));
	Hull->SetupAttachment(Root);
	Hull->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
	Hull->SetCollisionResponseToAllChannels(ECR_Ignore);
	Hull->SetCollisionResponseToChannel(ECC_WorldDynamic, ECR_Block);
	static ConstructorHelpers::FObjectFinder<UStaticMesh> Cube(
		TEXT("/Engine/BasicShapes/Cube.Cube"));
	if (Cube.Succeeded())
	{
		Hull->SetStaticMesh(Cube.Object);
	}
	Hull->SetRelativeScale3D(FVector(18.f, 5.2f, 3.4f));
	Hull->SetRelativeLocation(FVector(0.f, 0.f, 160.f));

	Volume = CreateDefaultSubobject<UBoxComponent>(TEXT("Volume"));
	Volume->SetupAttachment(Root);
	Volume->SetBoxExtent(FVector(900.f, 260.f, 180.f));
	Volume->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
	Volume->SetCollisionResponseToAllChannels(ECR_Ignore);

	Tags.AddUnique(TEXT("Skyguard.ProtectAsset"));
	CurrentIntegrity = MaxIntegrity;
}

void ASkyguardProtectAsset::ApplyDamage(const float Amount)
{
	if (bDead || Amount <= 0.f)
	{
		return;
	}
	CurrentIntegrity = FMath::Max(0.f, CurrentIntegrity - Amount);
	if (CurrentIntegrity <= 0.f)
	{
		bDead = true;
		USkyguardCombatVFX::SpawnExplosion(GetWorld(), GetActorLocation(), 2.4f);
		if (Hull)
		{
			Hull->SetVisibility(false, true);
		}
	}
}

float ASkyguardProtectAsset::GetIntegrityFraction() const
{
	if (MaxIntegrity <= KINDA_SMALL_NUMBER)
	{
		return 0.f;
	}
	return FMath::Clamp(CurrentIntegrity / MaxIntegrity, 0.f, 1.f);
}

void ASkyguardProtectAsset::ResetIntegrity()
{
	bDead = false;
	CurrentIntegrity = MaxIntegrity;
	if (Hull)
	{
		Hull->SetVisibility(true, true);
	}
}
