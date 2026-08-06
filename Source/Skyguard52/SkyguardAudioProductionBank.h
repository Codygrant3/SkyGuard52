#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "Sound/SoundBase.h"
#include "SkyguardAudioProductionBank.generated.h"

class USoundAttenuation;
class USoundConcurrency;
class USoundMix;
class USoundSubmixBase;

UENUM(BlueprintType)
enum class ESkyguardProductionAudioCategory : uint8
{
	EngineIdle,
	EngineCruise,
	EnginePower,
	Propeller,
	OpenCockpitWind,
	RifleMuzzle,
	RifleMechanical,
	RifleCasing,
	RifleReflection,
	IglaSearch,
	IglaLock,
	IglaLaunch,
	IglaFlyby,
	IglaImpact,
	DroneLightMotor,
	DroneHeavyMotor,
	DroneFlyby,
	ExplosionSmallCrack,
	ExplosionSmallBody,
	ExplosionSmallDebris,
	ExplosionSmallTail,
	ExplosionHeavyCrack,
	ExplosionHeavyBody,
	ExplosionHeavyDebris,
	ExplosionHeavyTail
};

UENUM(BlueprintType)
enum class ESkyguardAudioSourceStatus : uint8
{
	MISSING_SOURCE,
	PROJECT_OWNED_RECORDING,
	LICENSED_THIRD_PARTY,
	PROCEDURAL_QA_TEST_ONLY
};

USTRUCT(BlueprintType)
struct FSkyguardProductionAudioEntry
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	ESkyguardProductionAudioCategory Category = ESkyguardProductionAudioCategory::EngineIdle;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	ESkyguardAudioSourceStatus SourceStatus = ESkyguardAudioSourceStatus::MISSING_SOURCE;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	TSoftObjectPtr<USoundBase> Sound;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	TSoftObjectPtr<USoundAttenuation> Attenuation;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	TSoftObjectPtr<USoundConcurrency> Concurrency;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	TSoftObjectPtr<USoundSubmixBase> OutputSubmix;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	FName ProvenanceId;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	FString SourceSha256;
};

USTRUCT(BlueprintType)
struct FSkyguardProductionAudioRouting
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	TSoftObjectPtr<USoundSubmixBase> MasterSubmix;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	TSoftObjectPtr<USoundSubmixBase> CockpitSubmix;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	TSoftObjectPtr<USoundSubmixBase> ExteriorSubmix;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	TSoftObjectPtr<USoundSubmixBase> WeaponsSubmix;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	TSoftObjectPtr<USoundSubmixBase> ExplosionsSubmix;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	TSoftObjectPtr<USoundSubmixBase> RadioSubmix;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	TSoftObjectPtr<USoundMix> CockpitSoundMix;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, meta=(ClampMin="0.0", ClampMax="1.0"))
	float CockpitExteriorAttenuation = 0.72f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, meta=(ClampMin="100.0", ClampMax="20000.0"))
	float CockpitLowPassHz = 7200.f;
};

USTRUCT(BlueprintType)
struct FSkyguardProductionAudioAudit
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadOnly)
	int32 RequiredCategoryCount = 0;

	UPROPERTY(BlueprintReadOnly)
	int32 BoundProductionSourceCount = 0;

	UPROPERTY(BlueprintReadOnly)
	int32 ExplicitMissingSourceCount = 0;

	UPROPERTY(BlueprintReadOnly)
	int32 QATestOnlyCount = 0;

	UPROPERTY(BlueprintReadOnly)
	TArray<FName> MissingCategoryEntries;

	UPROPERTY(BlueprintReadOnly)
	TArray<FName> InvalidSourceEntries;

	UPROPERTY(BlueprintReadOnly)
	TArray<FName> MissingSoundBindings;

	UPROPERTY(BlueprintReadOnly)
	TArray<FName> MissingAttenuationBindings;

	UPROPERTY(BlueprintReadOnly)
	TArray<FName> MissingConcurrencyBindings;

	UPROPERTY(BlueprintReadOnly)
	TArray<FName> MissingOutputSubmixBindings;

	UPROPERTY(BlueprintReadOnly)
	TArray<FName> MissingRoutingAssets;

	UPROPERTY(BlueprintReadOnly)
	bool bCategoryContractComplete = false;

	UPROPERTY(BlueprintReadOnly)
	bool bProductionReady = false;
};

UCLASS(BlueprintType)
class SKYGUARD52_API USkyguardAudioProductionBank : public UPrimaryDataAsset
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, Category="Skyguard|Audio|Production")
	void InitializeRequiredEntries();

	UFUNCTION(BlueprintPure, Category="Skyguard|Audio|Production")
	FSkyguardProductionAudioAudit EvaluateReadiness() const;

	UFUNCTION(BlueprintCallable, Category="Skyguard|Audio|Production")
	bool ConfigureRoutingTopology();

	const FSkyguardProductionAudioEntry* FindEntry(ESkyguardProductionAudioCategory Category) const;

	static const TArray<ESkyguardProductionAudioCategory>& GetRequiredCategories();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Audio|Production")
	TArray<FSkyguardProductionAudioEntry> Entries;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Audio|Production")
	FSkyguardProductionAudioRouting Routing;

private:
	static bool HasBoundObject(const TSoftObjectPtr<USoundBase>& Value);
	static bool HasValidSha256(const FString& Value);
};
