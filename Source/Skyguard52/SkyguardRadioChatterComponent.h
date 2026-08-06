#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Sound/SoundBase.h"
#include "SkyguardRadioChatterComponent.generated.h"

struct FStreamableHandle;

USTRUCT(BlueprintType)
struct FSkyguardRadioLine
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	FName LineId;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	FText Speaker;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	FText Subtitle;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	TSoftObjectPtr<USoundBase> Sound;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, meta=(ClampMin="0", ClampMax="100"))
	int32 Priority = 50;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, meta=(ClampMin="0.1"))
	float EstimatedDurationSeconds = 2.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, meta=(ClampMin="0.0"))
	float CooldownSeconds = 0.f;
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FSkyguardRadioLineEvent, const FSkyguardRadioLine&, Line);

UCLASS(ClassGroup=(Skyguard), meta=(BlueprintSpawnableComponent))
class SKYGUARD52_API USkyguardRadioChatterComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	USkyguardRadioChatterComponent();
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

	UFUNCTION(BlueprintCallable, Category="Skyguard|Radio")
	void PrimeLines(const TArray<FSkyguardRadioLine>& Lines);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Radio")
	bool EnqueueLine(const FSkyguardRadioLine& Line);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Radio")
	void AdvanceRadioState(float DeltaSeconds);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Radio")
	void ClearQueue();

	UFUNCTION(BlueprintPure, Category="Skyguard|Radio")
	int32 GetQueuedLineCount() const { return Queue.Num(); }

	UFUNCTION(BlueprintPure, Category="Skyguard|Radio")
	FName GetCurrentLineId() const { return bPlaying ? CurrentLine.LineId : NAME_None; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Radio")
	int32 GetDroppedLineCount() const { return DroppedLines; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Radio")
	int32 GetPlayedLineCount() const { return PlayedLines; }

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Radio", meta=(ClampMin="1", ClampMax="64"))
	int32 MaxQueuedLines = 16;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Radio", meta=(ClampMin="0.0"))
	float InterLineGapSeconds = 0.15f;

	UPROPERTY(BlueprintAssignable, Category="Skyguard|Radio")
	FSkyguardRadioLineEvent OnLineStarted;

	UPROPERTY(BlueprintAssignable, Category="Skyguard|Radio")
	FSkyguardRadioLineEvent OnLineFinished;

private:
	UPROPERTY(Transient)
	TArray<FSkyguardRadioLine> Queue;

	FSkyguardRadioLine CurrentLine;
	TMap<FName, float> Cooldowns;
	float RemainingSeconds = 0.f;
	float GapRemainingSeconds = 0.f;
	bool bPlaying = false;
	int32 DroppedLines = 0;
	int32 PlayedLines = 0;
	TArray<TSharedPtr<FStreamableHandle>> PrimeHandles;

	void StartNextLine();
};
