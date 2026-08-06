#include "SkyguardAudioProceduralBankComponent.h"

#include "Kismet/GameplayStatics.h"
#include "Misc/Crc.h"
#include "Sound/SoundWaveProcedural.h"

USkyguardAudioProceduralBankComponent::USkyguardAudioProceduralBankComponent()
{
	PrimaryComponentTick.bCanEverTick = false;
}

void USkyguardAudioProceduralBankComponent::BeginPlay()
{
	Super::BeginPlay();
	BuildDevelopmentCues();
}

int32 USkyguardAudioProceduralBankComponent::CueIndex(const ESkyguardProceduralAuditionCue Cue)
{
	return static_cast<int32>(Cue);
}

bool USkyguardAudioProceduralBankComponent::IsAuditionAllowed() const
{
#if UE_BUILD_SHIPPING
	return false;
#else
	return bEnableDevelopmentAudition;
#endif
}

void USkyguardAudioProceduralBankComponent::BuildDevelopmentCues()
{
	Waves.Reset();
	PCMData.Reset();
	Checksums.Reset();
	TotalGeneratedBytes = 0;
	if (!IsAuditionAllowed())
	{
		return;
	}

	BuildCue(ESkyguardProceduralAuditionCue::RifleImpulse, 0.25f);
	BuildCue(ESkyguardProceduralAuditionCue::IglaLockTone, 0.4f);
	BuildCue(ESkyguardProceduralAuditionCue::IglaLaunchImpulse, 1.2f);
	BuildCue(ESkyguardProceduralAuditionCue::ExplosionSmall, 1.5f);
	BuildCue(ESkyguardProceduralAuditionCue::ExplosionHeavy, 2.5f);
	BuildCue(ESkyguardProceduralAuditionCue::RadioBeep, 0.12f);
}

void USkyguardAudioProceduralBankComponent::BuildCue(
	const ESkyguardProceduralAuditionCue Cue,
	const float DurationSeconds)
{
	TArray<uint8> PCM = GeneratePCM(Cue, DurationSeconds);
	if (PCM.IsEmpty() || TotalGeneratedBytes + PCM.Num() > GeneratedByteBudget)
	{
		return;
	}

	USoundWaveProcedural* Wave = NewObject<USoundWaveProcedural>(this);
	Wave->SetSampleRate(SampleRate);
	Wave->NumChannels = 1;
	Wave->Duration = DurationSeconds;
	Wave->SoundGroup = SOUNDGROUP_Default;
	Wave->bLooping = false;
	Wave->QueueAudio(PCM.GetData(), PCM.Num());

	const int32 ExpectedIndex = CueIndex(Cue);
	while (Waves.Num() < ExpectedIndex)
	{
		Waves.Add(nullptr);
		PCMData.AddDefaulted();
		Checksums.Add(0);
	}
	Waves.Add(Wave);
	Checksums.Add(FCrc::MemCrc32(PCM.GetData(), PCM.Num()));
	TotalGeneratedBytes += PCM.Num();
	PCMData.Add(MoveTemp(PCM));
}

TArray<uint8> USkyguardAudioProceduralBankComponent::GeneratePCM(
	const ESkyguardProceduralAuditionCue Cue,
	const float DurationSeconds) const
{
	const int32 SafeRate = FMath::Clamp(SampleRate, 8000, 48000);
	const int32 SampleCount = FMath::Max(1, FMath::RoundToInt(DurationSeconds * SafeRate));
	TArray<uint8> Bytes;
	Bytes.Reserve(SampleCount * static_cast<int32>(sizeof(int16)));
	FRandomStream Random(5200 + CueIndex(Cue) * 97);
	float SmoothedNoise = 0.f;

	for (int32 Index = 0; Index < SampleCount; ++Index)
	{
		const float Time = static_cast<float>(Index) / static_cast<float>(SafeRate);
		const float Progress = static_cast<float>(Index) / static_cast<float>(SampleCount);
		const float White = Random.FRandRange(-1.f, 1.f);
		SmoothedNoise = FMath::Lerp(SmoothedNoise, White, 0.08f);
		float Signal = 0.f;

		switch (Cue)
		{
		case ESkyguardProceduralAuditionCue::RifleImpulse:
			Signal = (0.82f * White + 0.18f * FMath::Sin(2.f * PI * 95.f * Time))
				* FMath::Exp(-24.f * Progress);
			break;
		case ESkyguardProceduralAuditionCue::IglaLockTone:
			Signal = 0.45f * FMath::Sin(
				2.f * PI * (FMath::Fmod(Time, 0.2f) < 0.1f ? 880.f : 1040.f) * Time);
			break;
		case ESkyguardProceduralAuditionCue::IglaLaunchImpulse:
			Signal = (0.65f * SmoothedNoise + 0.35f * FMath::Sin(2.f * PI * 82.f * Time))
				* FMath::Pow(1.f - Progress, 0.7f);
			break;
		case ESkyguardProceduralAuditionCue::ExplosionSmall:
			Signal = (0.72f * SmoothedNoise + 0.28f * FMath::Sin(2.f * PI * 58.f * Time))
				* FMath::Exp(-4.8f * Progress);
			break;
		case ESkyguardProceduralAuditionCue::ExplosionHeavy:
			Signal = (0.68f * SmoothedNoise + 0.32f * FMath::Sin(2.f * PI * 38.f * Time))
				* FMath::Exp(-3.2f * Progress);
			break;
		case ESkyguardProceduralAuditionCue::RadioBeep:
			Signal = 0.35f * FMath::Sin(2.f * PI * 1250.f * Time)
				* FMath::Sin(PI * Progress);
			break;
		default:
			break;
		}

		const int16 Sample = static_cast<int16>(
			FMath::Clamp(Signal, -1.f, 1.f) * 30000.f);
		Bytes.Add(static_cast<uint8>(Sample & 0xff));
		Bytes.Add(static_cast<uint8>((static_cast<uint16>(Sample) >> 8) & 0xff));
	}
	return Bytes;
}

USoundBase* USkyguardAudioProceduralBankComponent::GetCue(
	const ESkyguardProceduralAuditionCue Cue) const
{
	const int32 Index = CueIndex(Cue);
	return Waves.IsValidIndex(Index) ? Waves[Index] : nullptr;
}

uint32 USkyguardAudioProceduralBankComponent::GetCueChecksum(
	const ESkyguardProceduralAuditionCue Cue) const
{
	const int32 Index = CueIndex(Cue);
	return Checksums.IsValidIndex(Index) ? Checksums[Index] : 0;
}

bool USkyguardAudioProceduralBankComponent::AuditionCue(
	const ESkyguardProceduralAuditionCue Cue)
{
	if (!IsAuditionAllowed())
	{
		return false;
	}
	const int32 Index = CueIndex(Cue);
	if (!Waves.IsValidIndex(Index) || !PCMData.IsValidIndex(Index) || !Waves[Index])
	{
		return false;
	}
	// Sequential QA audition only. Resetting the procedural queue while a prior
	// audition is active is intentionally outside the production combat path.
	Waves[Index]->ResetAudio();
	Waves[Index]->QueueAudio(PCMData[Index].GetData(), PCMData[Index].Num());
	UGameplayStatics::PlaySound2D(this, Waves[Index]);
	return true;
}

