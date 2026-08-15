#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SkyguardPatrolShipBoss.generated.h"

class UPrimitiveComponent;
class USceneComponent;
class UStaticMeshComponent;

/** Harbor climax: systems you strip, not a single health bar. */
UCLASS()
class SKYGUARD52_API ASkyguardPatrolShipBoss : public AActor
{
	GENERATED_BODY()

public:
	ASkyguardPatrolShipBoss();

	UFUNCTION(BlueprintCallable, Category="Skyguard|Campaign")
	void ApplyHit(UPrimitiveComponent* HitComponent, float Damage);

	UFUNCTION(BlueprintPure, Category="Skyguard|Campaign")
	bool IsDefeated() const;

	UFUNCTION(BlueprintPure, Category="Skyguard|Campaign")
	bool IsRadarDead() const { return SearchRadarHealth <= 0.f; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Campaign")
	bool AreEnginesDead() const { return EngineHealth <= 0.f; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Campaign")
	int32 GetDestroyedSystemCount() const;

	UFUNCTION(BlueprintPure, Category="Skyguard|Campaign")
	FName GetLastDestroyedSystem() const { return LastDestroyedSystem; }

protected:
	UPROPERTY(VisibleAnywhere)
	TObjectPtr<USceneComponent> Root;

	UPROPERTY(VisibleAnywhere)
	TObjectPtr<UStaticMeshComponent> Hull;

	UPROPERTY(VisibleAnywhere)
	TObjectPtr<UStaticMeshComponent> Superstructure;

	UPROPERTY(VisibleAnywhere)
	TObjectPtr<UStaticMeshComponent> SearchRadar;

	UPROPERTY(VisibleAnywhere)
	TObjectPtr<UStaticMeshComponent> MissileBank;

	UPROPERTY(VisibleAnywhere)
	TObjectPtr<UStaticMeshComponent> Ciws;

	UPROPERTY(VisibleAnywhere)
	TObjectPtr<UStaticMeshComponent> Engines;

	UPROPERTY(VisibleAnywhere)
	TObjectPtr<UStaticMeshComponent> DroneDeck;

	float SearchRadarHealth = 90.f;
	float MissileHealth = 110.f;
	float CiwsHealth = 80.f;
	float EngineHealth = 130.f;
	float DeckHealth = 70.f;
	FName LastDestroyedSystem = NAME_None;

	UStaticMeshComponent* MakePart(const TCHAR* Name, UStaticMesh* Mesh);
	void KillPart(UStaticMeshComponent* Part, float& Health, FName Id);
};
