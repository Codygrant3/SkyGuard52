#include "SkyguardAudioAcceptanceHarness.h"

USkyguardAudioAcceptanceHarness::USkyguardAudioAcceptanceHarness()
{
	PrimaryComponentTick.bCanEverTick = false;
}

bool USkyguardAudioAcceptanceHarness::IsSha256(const FString& Value)
{
	if (Value.Len() != 64)
	{
		return false;
	}
	for (const TCHAR Character : Value)
	{
		if (!FChar::IsHexDigit(Character))
		{
			return false;
		}
	}
	return true;
}

void USkyguardAudioAcceptanceHarness::BeginEvidenceRun(
	const FString& BuildSha256,
	const FString& EvidenceSha256,
	const bool bPackagedDevelopmentBuild,
	const bool bAudibleDeviceObserved,
	const bool bCalibratedMetering,
	const bool bProductionBankReady)
{
	Receipt = FSkyguardAudibleAcceptanceReceipt();
	Receipt.BuildSha256 = BuildSha256;
	Receipt.EvidenceSha256 = EvidenceSha256;
	Receipt.bPackagedDevelopmentBuild = bPackagedDevelopmentBuild;
	Receipt.bAudibleDeviceObserved = bAudibleDeviceObserved;
	Receipt.bCalibratedMetering = bCalibratedMetering;
	Receipt.bProductionBankReady = bProductionBankReady;
	bRunActive = true;
}

void USkyguardAudioAcceptanceHarness::RecordMeasuredSample(
	const int32 ActiveVoices,
	const int32 UnderrunCount,
	const float AudioThreadMs,
	const float TruePeakDbTP)
{
	if (!bRunActive)
	{
		return;
	}
	++Receipt.SampleCount;
	Receipt.PeakActiveVoices = FMath::Max(Receipt.PeakActiveVoices, FMath::Max(0, ActiveVoices));
	Receipt.TotalUnderruns += FMath::Max(0, UnderrunCount);
	Receipt.MaximumAudioThreadMs = FMath::Max(Receipt.MaximumAudioThreadMs, FMath::Max(0.f, AudioThreadMs));
	Receipt.MaximumTruePeakDbTP = FMath::Max(Receipt.MaximumTruePeakDbTP, TruePeakDbTP);
}

bool USkyguardAudioAcceptanceHarness::CompleteEvidenceRun()
{
	bRunActive = false;
	Receipt.bAccepted =
		IsSha256(Receipt.BuildSha256)
		&& IsSha256(Receipt.EvidenceSha256)
		&& Receipt.bPackagedDevelopmentBuild
		&& Receipt.bAudibleDeviceObserved
		&& Receipt.bCalibratedMetering
		&& Receipt.bProductionBankReady
		&& Receipt.SampleCount >= MinimumMeasuredSamples
		&& Receipt.PeakActiveVoices <= MaximumAllowedVoices
		&& Receipt.TotalUnderruns == 0
		&& Receipt.MaximumAudioThreadMs <= MaximumAudioThreadMs
		&& Receipt.MaximumTruePeakDbTP <= MaximumTruePeakDbTP;
	return Receipt.bAccepted;
}

