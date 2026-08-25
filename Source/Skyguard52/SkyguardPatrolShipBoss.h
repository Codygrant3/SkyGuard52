#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SkyguardGunshipTypes.h"
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
	virtual void Tick(float DeltaSeconds) override;

	UFUNCTION(BlueprintCallable, Category="Skyguard|Campaign")
	void ApplyHit(UPrimitiveComponent* HitComponent, float Damage);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Campaign")
	void ApplyHitToSystem(ESkyguardPatrolShipSystem System, float Damage);

	UFUNCTION(BlueprintPure, Category="Skyguard|Campaign")
	bool IsDefeated() const;

	UFUNCTION(BlueprintPure, Category="Skyguard|Campaign")
	bool IsSystemDead(ESkyguardPatrolShipSystem System) const;

	UFUNCTION(BlueprintPure, Category="Skyguard|Campaign")
	bool IsRadarDead() const
	{
		return IsSystemDead(ESkyguardPatrolShipSystem::Radar);
	}

	UFUNCTION(BlueprintPure, Category="Skyguard|Campaign")
	bool AreEnginesDead() const
	{
		return IsSystemDead(ESkyguardPatrolShipSystem::Engines);
	}

	UFUNCTION(BlueprintPure, Category="Skyguard|Campaign")
	bool CanCoordinateAda() const
	{
		return !IsSystemDead(ESkyguardPatrolShipSystem::Radar);
	}

	UFUNCTION(BlueprintPure, Category="Skyguard|Campaign")
	bool CanLaunchInbound() const
	{
		return !IsSystemDead(ESkyguardPatrolShipSystem::Launcher);
	}

	UFUNCTION(BlueprintPure, Category="Skyguard|Campaign")
	bool CanFireCannon() const
	{
		return !IsSystemDead(ESkyguardPatrolShipSystem::Cannon);
	}

	UFUNCTION(BlueprintPure, Category="Skyguard|Campaign")
	bool CanLaunchDrones() const
	{
		return !IsSystemDead(ESkyguardPatrolShipSystem::DroneDeck);
	}

	UFUNCTION(BlueprintPure, Category="Skyguard|Campaign")
	float GetUnderwaySpeed() const;

	UFUNCTION(BlueprintPure, Category="Skyguard|Campaign")
	float GetCannonThreatDamage() const;

	UFUNCTION(BlueprintCallable, Category="Skyguard|Campaign")
	bool ConsumeDeckLaunch(float DeltaSeconds);

	UFUNCTION(BlueprintPure, Category="Skyguard|Campaign")
	int32 GetDestroyedSystemCount() const;

	UFUNCTION(BlueprintPure, Category="Skyguard|Campaign")
	FName GetLastDestroyedSystem() const { return LastDestroyedSystem; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Campaign")
	FString GetHudSystemLine() const;

	UFUNCTION(BlueprintPure, Category="Skyguard|Campaign")
	ESkyguardPatrolShipSystem GetPriorityLiveSystem() const;

	UPrimitiveComponent* GetSystemComponent(ESkyguardPatrolShipSystem System) const;
	UPrimitiveComponent* FindNearestLiveSystem(const FVector& WorldLocation) const;

	static constexpr float UnderwayCruiseSpeed = 180.f;
	static constexpr float CannonThreatDamage = 10.f;
	static constexpr float DeckLaunchIntervalSeconds = 18.f;

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
	float DeckLaunchCooldown = DeckLaunchIntervalSeconds;
	FName LastDestroyedSystem = NAME_None;

	UStaticMeshComponent* MakePart(const TCHAR* Name, UStaticMesh* Mesh);
	void KillPart(UStaticMeshComponent* Part, float& Health, FName Id);
	float& HealthFor(ESkyguardPatrolShipSystem System);
	float HealthFor(ESkyguardPatrolShipSystem System) const;
	void AnnounceSystemKill(ESkyguardPatrolShipSystem System);
};
