#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SkyguardGunshipTypes.h"
#include "SkyguardThreatTypes.h"
#include "SkyguardGunshipSortieDirector.generated.h"

class ASkyguardApacheAircraft;
class UWorld;
class ASkyguardDrone;
class ASkyguardGunner;
class ASkyguardPatrolShipBoss;
class ASkyguardProtectAsset;
class ASkyguardRadarNode;

UENUM(BlueprintType)
enum class ESkyguardSortieBeat : uint8
{
	Approach,
	InitialContact,
	ShoreAssault,
	RadarNet,
	Choice,
	Climax,
	Extraction,
	Succeeded,
	Failed
};

UCLASS()
class SKYGUARD52_API ASkyguardGunshipSortieDirector : public AActor
{
	GENERATED_BODY()

public:
	ASkyguardGunshipSortieDirector();
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
	virtual void Tick(float DeltaSeconds) override;

	UFUNCTION(BlueprintCallable, Category="Skyguard|Campaign")
	void StartMissionIndex(int32 Index);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Campaign")
	void StartNextMission();

	UFUNCTION(BlueprintCallable, Category="Skyguard|Campaign")
	void ConfirmContinue();

	UFUNCTION(BlueprintCallable, Category="Skyguard|Campaign")
	void SetPendingLoadout(ESkyguardLoadout Loadout);

	UFUNCTION(BlueprintPure, Category="Skyguard|Campaign")
	ESkyguardLoadout GetPendingLoadout() const { return PendingLoadout; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Campaign")
	bool IsAwaitingContinue() const { return bAwaitingContinue; }

	void ResolveSortie(bool bWon, const TCHAR* FailReason = nullptr);

	UFUNCTION(BlueprintPure, Category="Skyguard|Campaign")
	ASkyguardProtectAsset* GetCargoAsset() const { return Cargo; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Campaign")
	ASkyguardRadarNode* GetRadarNode() const { return Radar; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Campaign")
	ASkyguardPatrolShipBoss* GetPatrolShip() const { return PatrolShip; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Campaign")
	int32 GetLastScore() const { return LastScore; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Campaign")
	int32 GetLastMedal() const { return LastMedal; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Campaign")
	int32 GetMissionIndex() const { return MissionIndex; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Campaign")
	ESkyguardSortieBeat GetBeat() const { return Beat; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Campaign")
	FName GetMissionId() const;

	UFUNCTION(BlueprintPure, Category="Skyguard|Campaign")
	FString GetMissionTitle() const;

	UFUNCTION(BlueprintPure, Category="Skyguard|Campaign")
	bool IsSortieOver() const
	{
		return Beat == ESkyguardSortieBeat::Succeeded ||
			Beat == ESkyguardSortieBeat::Failed;
	}

	/** Harbor Breaker shoreline column. Five hulls on the yellow coastal highway. */
	static constexpr int32 CoastalConvoyCount = 5;

	/** Authored coastal-highway polyline in front of HarborHover, toward the city. */
	UFUNCTION(BlueprintPure, Category="Skyguard|Campaign")
	static TArray<FVector> GetCoastalHighwayPath();

	UFUNCTION(BlueprintCallable, Category="Skyguard|Campaign")
	int32 SpawnCoastalConvoy();

	UFUNCTION(BlueprintPure, Category="Skyguard|Campaign")
	int32 CountLiveRoadConvoy() const;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Campaign")
	bool bAutoStart = true;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Campaign")
	int32 StartingMissionIndex = 0;

protected:
	void AdvanceBeats();
	void EnterBeat(ESkyguardSortieBeat NewBeat);
	void SpawnThreat(ESkyguardThreatKind Kind, const FVector& Location);
	void SpawnBeatWave();
	void EnsureSetPieces();
	void DestroyRoadConvoy();
	void BindThreatToCoastalRoad(ASkyguardDrone* Threat);
	TArray<FVector> BuildGroundedCoastalHighwayPath() const;
	static FName ConvoyVehicleSlotForIndex(int32 Index);
	static float SnapRoadHeight(const UWorld* World, const FVector& Horizontal);
	void HandleDroneImpact(ASkyguardDrone* Drone);
	void TickIncoming(float DeltaSeconds);
	void TickShipSystems(float DeltaSeconds);
	void ResolveWin();
	void ResolveFail(const TCHAR* Reason);
	void ScoreSortie(bool bWon);
	void ShowDebrief() const;
	void PushDebriefToPresentation();
	void HandleDebriefInput();
	void ApplyPendingLoadout();
	ASkyguardApacheAircraft* FindApache() const;
	ASkyguardGunner* FindGunner() const;

	int32 MissionIndex = 0;
	ESkyguardSortieBeat Beat = ESkyguardSortieBeat::Approach;
	float Elapsed = 0.f;
	float IncomingCooldown = 12.f;
	float IncomingWindow = 0.f;
	float PostSortieSeconds = 0.f;
	bool bInbound = false;
	bool bChoiceRadarFirst = false;
	bool bClimaxSpawned = false;
	bool bExtractSpawned = false;
	bool bAwaitingContinue = false;
	int32 LastScore = 0;
	int32 LastMedal = 0;
	int32 ThreatsKilled = 0;
	int32 NextRoadConvoySlot = 0;
	float LastCargoFraction = 1.f;
	ESkyguardLoadout PendingLoadout = ESkyguardLoadout::Balanced;

	UPROPERTY(Transient)
	TObjectPtr<ASkyguardProtectAsset> Cargo;

	UPROPERTY(Transient)
	TObjectPtr<ASkyguardRadarNode> Radar;

	UPROPERTY(Transient)
	TObjectPtr<ASkyguardPatrolShipBoss> PatrolShip;
};
