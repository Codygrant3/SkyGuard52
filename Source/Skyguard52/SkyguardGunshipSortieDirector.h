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

	/**
	 * Inbound SAM cadence for a 15-minute Harbor Breaker.
	 * Old clock: first delay 12s, radar-live 14s, radar-down 28s.
	 * That is a missile every 14s across 13 combat minutes.
	 */
	static constexpr float IncomingFirstDelaySeconds = 12.f;
	static constexpr float IncomingRadarLiveIntervalSeconds = 40.f;
	static constexpr float IncomingRadarDownIntervalSeconds = 80.f;
	static constexpr float IncomingRadarLitDelaySeconds = 3.f;
	static constexpr float IncomingWindowSeconds = 2.6f;
	static constexpr float IncomingRadarLiveHitDamage = 22.f;
	static constexpr float IncomingRadarDownHitDamage = 12.f;

	/** Beat-wave sizes. Early beats stay light; extract is a spike, not a 4-pack. */
	static constexpr int32 ContactWaveCount = 2;
	static constexpr int32 ShoreWaveCount = 4;
	static constexpr int32 RadarNetWaveCount = 4;
	static constexpr int32 ChoiceWaveCount = 3;
	static constexpr int32 ExtractWaveCount = 5;

	static int32 BeatWaveCount(ESkyguardSortieBeat InBeat);
	static ESkyguardThreatKind BeatWaveKind(int32 InMissionIndex, ESkyguardSortieBeat InBeat);
	static float IncomingIntervalSeconds(bool bRadarLive);
	static bool BeatAllowsInbound(ESkyguardSortieBeat InBeat);
	static bool UsesRadarLiveInboundCadence(ESkyguardSortieBeat InBeat);

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

	friend class FSkyguardSortieApproachHasNoInboundTest;
	friend class FSkyguardSortieExtractUsesExtractKindTest;
	friend class FSkyguardSortieBeatWaveSkipsRoadConvoyTest;

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
	void ResolveWin();
	void ResolveFail(const TCHAR* Reason);
	void ScoreSortie(bool bWon);
	void ShowDebrief() const;
	void HandleDebriefInput();
	void ApplyPendingLoadout();
	ASkyguardApacheAircraft* FindApache() const;
	ASkyguardGunner* FindGunner() const;

	int32 MissionIndex = 0;
	ESkyguardSortieBeat Beat = ESkyguardSortieBeat::Approach;
	float Elapsed = 0.f;
	float IncomingCooldown = IncomingFirstDelaySeconds;
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
