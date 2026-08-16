#include "SkyguardRadioChatterComponent.h"

#include "Engine/AssetManager.h"
#include "Kismet/GameplayStatics.h"

USkyguardRadioChatterComponent::USkyguardRadioChatterComponent()
{
	PrimaryComponentTick.bCanEverTick = true;
}

void USkyguardRadioChatterComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	for (TSharedPtr<FStreamableHandle>& Handle : PrimeHandles)
	{
		if (Handle.IsValid())
		{
			Handle->CancelHandle();
		}
	}
	PrimeHandles.Reset();
	Super::EndPlay(EndPlayReason);
}

void USkyguardRadioChatterComponent::PrimeLines(const TArray<FSkyguardRadioLine>& Lines)
{
	TArray<FSoftObjectPath> Paths;
	for (const FSkyguardRadioLine& Line : Lines)
	{
		if (!Line.Sound.IsNull())
		{
			Paths.AddUnique(Line.Sound.ToSoftObjectPath());
		}
	}
	if (!Paths.IsEmpty())
	{
		PrimeHandles.Add(UAssetManager::GetStreamableManager().RequestAsyncLoad(Paths));
	}
}

void USkyguardRadioChatterComponent::TickComponent(const float DeltaTime, const ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	AdvanceRadioState(DeltaTime);
}

bool USkyguardRadioChatterComponent::EnqueueLine(const FSkyguardRadioLine& Line)
{
	if (Line.LineId.IsNone() || Cooldowns.FindRef(Line.LineId) > 0.f)
	{
		++DroppedLines;
		return false;
	}
	if (Queue.Num() >= MaxQueuedLines)
	{
		int32 LowestIndex = INDEX_NONE;
		int32 LowestPriority = MAX_int32;
		for (int32 Index = 0; Index < Queue.Num(); ++Index)
		{
			if (Queue[Index].Priority < LowestPriority)
			{
				LowestPriority = Queue[Index].Priority;
				LowestIndex = Index;
			}
		}
		if (LowestIndex == INDEX_NONE || LowestPriority >= Line.Priority)
		{
			++DroppedLines;
			return false;
		}
		Queue.RemoveAt(LowestIndex);
		++DroppedLines;
	}
	Queue.Add(Line);
	Queue.StableSort([](const FSkyguardRadioLine& A, const FSkyguardRadioLine& B)
	{
		return A.Priority > B.Priority;
	});
	if (!bPlaying && GapRemainingSeconds <= 0.f)
	{
		StartNextLine();
	}
	return true;
}

void USkyguardRadioChatterComponent::AdvanceRadioState(const float DeltaSeconds)
{
	const float SafeDelta = FMath::Max(0.f, DeltaSeconds);
	for (TPair<FName, float>& Pair : Cooldowns)
	{
		Pair.Value = FMath::Max(0.f, Pair.Value - SafeDelta);
	}
	if (bPlaying)
	{
		RemainingSeconds -= SafeDelta;
		if (RemainingSeconds <= 0.f)
		{
			OnLineFinished.Broadcast(CurrentLine);
			bPlaying = false;
			GapRemainingSeconds = InterLineGapSeconds;
		}
	}
	else if (GapRemainingSeconds > 0.f)
	{
		GapRemainingSeconds = FMath::Max(0.f, GapRemainingSeconds - SafeDelta);
	}
	if (!bPlaying && GapRemainingSeconds <= 0.f)
	{
		StartNextLine();
	}
}

void USkyguardRadioChatterComponent::ClearQueue()
{
	Queue.Reset();
	bPlaying = false;
	RemainingSeconds = 0.f;
	GapRemainingSeconds = 0.f;
	CurrentLine = FSkyguardRadioLine();
}

void USkyguardRadioChatterComponent::StartNextLine()
{
	if (Queue.IsEmpty())
	{
		return;
	}
	CurrentLine = Queue[0];
	Queue.RemoveAt(0);
	bPlaying = true;
	RemainingSeconds = FMath::Max(0.1f, CurrentLine.EstimatedDurationSeconds);
	Cooldowns.Add(CurrentLine.LineId, CurrentLine.CooldownSeconds);
	++PlayedLines;
	OnLineStarted.Broadcast(CurrentLine);

	if (USoundBase* ResolvedSound = CurrentLine.Sound.Get())
	{
		UGameplayStatics::PlaySound2D(this, ResolvedSound);
	}
}
