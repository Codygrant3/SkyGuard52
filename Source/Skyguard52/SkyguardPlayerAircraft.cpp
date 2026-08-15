#include "SkyguardPlayerAircraft.h"

#include "SkyguardApacheAircraft.h"
#include "SkyguardGunner.h"
#include "SkyguardYak52Aircraft.h"
#include "Components/BoxComponent.h"
#include "Components/SceneComponent.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Actor.h"

namespace
{
	template <typename T>
	T* FindFirst(const UWorld* World)
	{
		if (!World)
		{
			return nullptr;
		}
		for (TActorIterator<T> It(const_cast<UWorld*>(World)); It; ++It)
		{
			if (IsValid(*It))
			{
				return *It;
			}
		}
		return nullptr;
	}

	void HideLegacyYak(ASkyguardYak52Aircraft* Yak)
	{
		if (!IsValid(Yak))
		{
			return;
		}
		Yak->SetActorHiddenInGame(true);
		if (UBoxComponent* Hull = Yak->HullCollider)
		{
			Hull->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		}
		Yak->SetActorEnableCollision(false);
		Yak->Tags.AddUnique(FName(TEXT("Skyguard.LegacyYakHidden")));
	}
}

ASkyguardApacheAircraft* FSkyguardPlayerAircraft::FindApache(const UWorld* World)
{
	return FindFirst<ASkyguardApacheAircraft>(World);
}

ASkyguardYak52Aircraft* FSkyguardPlayerAircraft::FindYak(const UWorld* World)
{
	return FindFirst<ASkyguardYak52Aircraft>(World);
}

AActor* FSkyguardPlayerAircraft::FindPlatform(UWorld* World)
{
	if (ASkyguardApacheAircraft* Apache = FindApache(World))
	{
		return Apache;
	}
	return FindYak(World);
}

USceneComponent* FSkyguardPlayerAircraft::FindGunnerMount(UWorld* World)
{
	if (ASkyguardApacheAircraft* Apache = FindApache(World))
	{
		return Apache->GetGunnerMount();
	}
	if (ASkyguardYak52Aircraft* Yak = FindYak(World))
	{
		return Yak->GetRearGunnerMount();
	}
	return nullptr;
}

ASkyguardApacheAircraft* FSkyguardPlayerAircraft::EnsureApache(UWorld* World)
{
	if (!World)
	{
		return nullptr;
	}
	if (ASkyguardApacheAircraft* Existing = FindApache(World))
	{
		if (ASkyguardYak52Aircraft* Yak = FindYak(World))
		{
			HideLegacyYak(Yak);
		}
		return Existing;
	}

	// Face the city/coast (-X), not out to sea. Old Yak intercept looked +X.
	const FVector HarborHover(2500.f, -8000.f, 2200.f);
	const FVector City(-1800.f, 0.f, 400.f);
	FVector SpawnLocation = HarborHover;
	if (ASkyguardYak52Aircraft* Yak = FindYak(World))
	{
		SpawnLocation = Yak->GetActorLocation();
		HideLegacyYak(Yak);
	}
	const FVector ToCity = (City - SpawnLocation).GetSafeNormal2D();
	const float Yaw = ToCity.IsNearlyZero()
		? 180.f
		: FMath::RadiansToDegrees(FMath::Atan2(ToCity.Y, ToCity.X));
	const FTransform SpawnTransform(FRotator(-6.f, Yaw, 0.f), SpawnLocation);

	FActorSpawnParameters Params;
	Params.SpawnCollisionHandlingOverride =
		ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
	ASkyguardApacheAircraft* Apache =
		World->SpawnActor<ASkyguardApacheAircraft>(
			ASkyguardApacheAircraft::StaticClass(),
			SpawnTransform,
			Params);
	return Apache;
}

void FSkyguardPlayerAircraft::AttachGunner(
	ASkyguardGunner* Gunner,
	ASkyguardYak52Aircraft* YakFallback)
{
	if (!IsValid(Gunner))
	{
		return;
	}

	if (ASkyguardApacheAircraft* Apache = FindApache(Gunner->GetWorld()))
	{
		if (USceneComponent* Mount = Apache->GetGunnerMount())
		{
			Gunner->AttachToComponent(
				Mount,
				FAttachmentTransformRules::SnapToTargetNotIncludingScale);
			Gunner->SetActorRelativeLocation(FVector::ZeroVector);
			Gunner->SetActorRelativeRotation(FRotator::ZeroRotator);
			return;
		}
	}

	if (IsValid(YakFallback) && YakFallback->GetRearGunnerMount())
	{
		Gunner->AttachToComponent(
			YakFallback->GetRearGunnerMount(),
			FAttachmentTransformRules::SnapToTargetNotIncludingScale);
		Gunner->SetActorRelativeLocation(FVector::ZeroVector);
		Gunner->SetActorRelativeRotation(FRotator::ZeroRotator);
	}
}

void FSkyguardPlayerAircraft::ApplyHullDamage(AActor* Platform, const float Amount)
{
	if (!IsValid(Platform) || Amount <= 0.f)
	{
		return;
	}
	if (ASkyguardApacheAircraft* Apache = Cast<ASkyguardApacheAircraft>(Platform))
	{
		Apache->ApplyDamage(Amount);
		return;
	}
	if (ASkyguardYak52Aircraft* Yak = Cast<ASkyguardYak52Aircraft>(Platform))
	{
		Yak->ApplyDamage(Amount);
	}
}

float FSkyguardPlayerAircraft::GetHullDamageFraction(const AActor* Platform)
{
	if (const ASkyguardApacheAircraft* Apache =
		Cast<ASkyguardApacheAircraft>(Platform))
	{
		return Apache->GetDamageFraction();
	}
	if (const ASkyguardYak52Aircraft* Yak = Cast<ASkyguardYak52Aircraft>(Platform))
	{
		return Yak->GetDamageFraction();
	}
	return 0.f;
}

bool FSkyguardPlayerAircraft::IsPlayerPlatform(const AActor* Actor)
{
	return IsValid(Actor) &&
		(Actor->IsA<ASkyguardApacheAircraft>() ||
		 Actor->IsA<ASkyguardYak52Aircraft>());
}
