#include "SkyguardAudioDirectorComponent.h"

#include "Components/AudioComponent.h"
#include "Engine/AssetManager.h"
#include "Engine/World.h"
#include "GameFramework/Actor.h"
#include "Kismet/GameplayStatics.h"
#include "Sound/SoundAttenuation.h"
#include "Sound/SoundConcurrency.h"
#include "Sound/SoundMix.h"
#include "Sound/SoundSubmix.h"

namespace
{
	TMap<TWeakObjectPtr<UWorld>, TWeakObjectPtr<USkyguardAudioDirectorComponent>>
		RegisteredAudioDirectors;
}

USkyguardAudioDirectorComponent::USkyguardAudioDirectorComponent()
{
	PrimaryComponentTick.bCanEverTick = true;
	ProductionBankAsset = TSoftObjectPtr<USkyguardAudioProductionBank>(
		FSoftObjectPath(
			TEXT("/Game/Skyguard/Audio/Production/DA_P5A_ProductionAudioBank.DA_P5A_ProductionAudioBank")));

	auto AddDefault = [this](const ESkyguardAudioEvent Event, const float Cooldown, const float Duration, const int32 Concurrent, const int32 Priority)
	{
		FSkyguardAudioEventDefinition Definition;
		Definition.Event = Event;
		Definition.CooldownSeconds = Cooldown;
		Definition.EstimatedDurationSeconds = Duration;
		Definition.MaxConcurrent = Concurrent;
		Definition.Priority = Priority;
		EventDefinitions.Add(Definition);
	};

	AddDefault(ESkyguardAudioEvent::RifleShot, 0.075f, 1.2f, 6, 75);
	AddDefault(ESkyguardAudioEvent::RifleMechanical, 0.075f, 0.4f, 3, 55);
	AddDefault(ESkyguardAudioEvent::IglaSeekerSearch, 0.2f, 0.5f, 1, 45);
	AddDefault(ESkyguardAudioEvent::IglaLock, 0.25f, 0.8f, 1, 80);
	AddDefault(ESkyguardAudioEvent::IglaLaunch, 1.f, 3.f, 2, 95);
	AddDefault(ESkyguardAudioEvent::IglaImpact, 0.05f, 2.5f, 4, 90);
	AddDefault(ESkyguardAudioEvent::DroneMotor, 0.1f, 1.f, 8, 35);
	AddDefault(ESkyguardAudioEvent::DroneFlyby, 0.5f, 2.f, 3, 65);
	AddDefault(ESkyguardAudioEvent::ExplosionSmall, 0.05f, 3.f, 6, 85);
	AddDefault(ESkyguardAudioEvent::ExplosionHeavy, 0.25f, 6.f, 3, 100);
	AddDefault(ESkyguardAudioEvent::DebrisImpact, 0.03f, 1.f, 8, 30);
}

void USkyguardAudioDirectorComponent::BeginPlay()
{
	Super::BeginPlay();
	if (UWorld* World = GetWorld())
	{
		RegisteredAudioDirectors.FindOrAdd(World) = this;
	}
	PrimeConfiguredAssets();
}

void USkyguardAudioDirectorComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	if (bCockpitSoundMixPushed && ProductionBank &&
		ProductionBank->Routing.CockpitSoundMix.Get())
	{
		UGameplayStatics::PopSoundMixModifier(
			this,
			ProductionBank->Routing.CockpitSoundMix.Get());
		bCockpitSoundMixPushed = false;
	}
	if (UWorld* World = GetWorld())
	{
		if (const TWeakObjectPtr<USkyguardAudioDirectorComponent>* Registered =
			RegisteredAudioDirectors.Find(World);
			Registered && Registered->Get() == this)
		{
			RegisteredAudioDirectors.Remove(World);
		}
	}
	for (TSharedPtr<FStreamableHandle>& Handle : PrimeHandles)
	{
		if (Handle.IsValid())
		{
			Handle->CancelHandle();
		}
	}
	PrimeHandles.Reset();
	ActiveVoices.Reset();
	StopLoopComponents();
	Super::EndPlay(EndPlayReason);
}

void USkyguardAudioDirectorComponent::TickComponent(const float DeltaTime, const ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	AdvanceAudioState(DeltaTime);
}

void USkyguardAudioDirectorComponent::PrimeConfiguredAssets()
{
	if (!ProductionBank && !ProductionBankAsset.IsNull())
	{
		if (USkyguardAudioProductionBank* ResolvedBank = ProductionBankAsset.Get())
		{
			ApplyProductionBank(ResolvedBank);
		}
		else if (!bProductionBankPrimeRequested)
		{
			bProductionBankPrimeRequested = true;
			PrimeHandles.Add(
				UAssetManager::GetStreamableManager().RequestAsyncLoad(
					ProductionBankAsset.ToSoftObjectPath(),
					FStreamableDelegate::CreateUObject(
						this,
						&USkyguardAudioDirectorComponent::OnProductionBankLoaded)));
			return;
		}
	}

	TArray<FSoftObjectPath> Paths;
	auto AddPath = [&Paths](const auto& Asset)
	{
		if (!Asset.IsNull())
		{
			Paths.AddUnique(Asset.ToSoftObjectPath());
		}
	};
	AddPath(EngineIdleLoop);
	AddPath(EngineCruiseLoop);
	AddPath(EnginePowerLoop);
	AddPath(PropellerLoop);
	AddPath(OpenCockpitWindLoop);
	for (const FResolvedLoopRoute& Route : ResolvedLoopRoutes)
	{
		AddPath(Route.Sound);
		if (!Route.Attenuation.IsNull()) Paths.AddUnique(Route.Attenuation.ToSoftObjectPath());
		if (!Route.Concurrency.IsNull()) Paths.AddUnique(Route.Concurrency.ToSoftObjectPath());
		if (!Route.OutputSubmix.IsNull()) Paths.AddUnique(Route.OutputSubmix.ToSoftObjectPath());
	}
	for (const FSkyguardAudioEventDefinition& Definition : EventDefinitions)
	{
		AddPath(Definition.Sound);
		if (!Definition.Attenuation.IsNull()) Paths.AddUnique(Definition.Attenuation.ToSoftObjectPath());
		if (!Definition.Concurrency.IsNull()) Paths.AddUnique(Definition.Concurrency.ToSoftObjectPath());
		if (!Definition.OutputSubmix.IsNull()) Paths.AddUnique(Definition.OutputSubmix.ToSoftObjectPath());
	}
	if (ProductionBank)
	{
		AddPath(ProductionBank->Routing.MasterSubmix);
		AddPath(ProductionBank->Routing.CockpitSubmix);
		AddPath(ProductionBank->Routing.ExteriorSubmix);
		AddPath(ProductionBank->Routing.WeaponsSubmix);
		AddPath(ProductionBank->Routing.ExplosionsSubmix);
		AddPath(ProductionBank->Routing.RadioSubmix);
		AddPath(ProductionBank->Routing.CockpitSoundMix);
	}
	if (Paths.IsEmpty())
	{
		return;
	}
	PrimeHandles.Add(
		UAssetManager::GetStreamableManager().RequestAsyncLoad(
			Paths,
			FStreamableDelegate::CreateUObject(
				this,
				&USkyguardAudioDirectorComponent::OnConfiguredAssetsLoaded)));
}

void USkyguardAudioDirectorComponent::ApplyProductionBank(USkyguardAudioProductionBank* Bank)
{
	if (bCockpitSoundMixPushed && ProductionBank &&
		ProductionBank->Routing.CockpitSoundMix.Get())
	{
		UGameplayStatics::PopSoundMixModifier(
			this,
			ProductionBank->Routing.CockpitSoundMix.Get());
		bCockpitSoundMixPushed = false;
	}
	ProductionBank = Bank;
	if (!Bank)
	{
		return;
	}

	auto SoundFor = [Bank](const ESkyguardProductionAudioCategory Category)
	{
		const FSkyguardProductionAudioEntry* Entry = Bank->FindEntry(Category);
		return Entry ? Entry->Sound : TSoftObjectPtr<USoundBase>();
	};
	EngineIdleLoop = SoundFor(ESkyguardProductionAudioCategory::EngineIdle);
	EngineCruiseLoop = SoundFor(ESkyguardProductionAudioCategory::EngineCruise);
	EnginePowerLoop = SoundFor(ESkyguardProductionAudioCategory::EnginePower);
	PropellerLoop = SoundFor(ESkyguardProductionAudioCategory::Propeller);
	OpenCockpitWindLoop = SoundFor(ESkyguardProductionAudioCategory::OpenCockpitWind);
	RebuildResolvedLoopRoutes();
	CockpitExteriorAttenuation = Bank->Routing.CockpitExteriorAttenuation;
	CockpitLowPassHz = Bank->Routing.CockpitLowPassHz;

	auto BindEvent = [this, Bank](
		const ESkyguardAudioEvent Event,
		const ESkyguardProductionAudioCategory Category)
	{
		FSkyguardAudioEventDefinition* Definition = EventDefinitions.FindByPredicate(
			[Event](const FSkyguardAudioEventDefinition& Candidate)
			{
				return Candidate.Event == Event;
			});
		const FSkyguardProductionAudioEntry* Entry = Bank->FindEntry(Category);
		if (Definition && Entry)
		{
			Definition->Sound = Entry->Sound;
			Definition->Attenuation = Entry->Attenuation;
			Definition->Concurrency = Entry->Concurrency;
			Definition->OutputSubmix = Entry->OutputSubmix;
		}
	};
	BindEvent(ESkyguardAudioEvent::RifleShot, ESkyguardProductionAudioCategory::RifleMuzzle);
	BindEvent(ESkyguardAudioEvent::RifleMechanical, ESkyguardProductionAudioCategory::RifleMechanical);
	BindEvent(ESkyguardAudioEvent::IglaSeekerSearch, ESkyguardProductionAudioCategory::IglaSearch);
	BindEvent(ESkyguardAudioEvent::IglaLock, ESkyguardProductionAudioCategory::IglaLock);
	BindEvent(ESkyguardAudioEvent::IglaLaunch, ESkyguardProductionAudioCategory::IglaLaunch);
	BindEvent(ESkyguardAudioEvent::IglaImpact, ESkyguardProductionAudioCategory::IglaImpact);
	BindEvent(ESkyguardAudioEvent::DroneMotor, ESkyguardProductionAudioCategory::DroneLightMotor);
	BindEvent(ESkyguardAudioEvent::DroneFlyby, ESkyguardProductionAudioCategory::DroneFlyby);
	BindEvent(ESkyguardAudioEvent::ExplosionSmall, ESkyguardProductionAudioCategory::ExplosionSmallBody);
	BindEvent(ESkyguardAudioEvent::ExplosionHeavy, ESkyguardProductionAudioCategory::ExplosionHeavyBody);
	BindEvent(ESkyguardAudioEvent::DebrisImpact, ESkyguardProductionAudioCategory::ExplosionSmallDebris);
	UpdateLoopMix();
}

void USkyguardAudioDirectorComponent::OnProductionBankLoaded()
{
	bProductionBankPrimeRequested = false;
	if (USkyguardAudioProductionBank* Bank = ProductionBankAsset.Get())
	{
		ApplyProductionBank(Bank);
		PrimeConfiguredAssets();
	}
}

void USkyguardAudioDirectorComponent::OnConfiguredAssetsLoaded()
{
	ApplyListenerSoundMix();
	if (HasBegunPlay())
	{
		StopLoopComponents();
		CreateResolvedLoopComponents();
	}
}

void USkyguardAudioDirectorComponent::RebuildResolvedLoopRoutes()
{
	ResolvedLoopRoutes.Reset();
	if (!ProductionBank)
	{
		return;
	}
	const ESkyguardProductionAudioCategory LoopCategories[] = {
		ESkyguardProductionAudioCategory::EngineIdle,
		ESkyguardProductionAudioCategory::EngineCruise,
		ESkyguardProductionAudioCategory::EnginePower,
		ESkyguardProductionAudioCategory::Propeller,
		ESkyguardProductionAudioCategory::OpenCockpitWind,
	};
	for (const ESkyguardProductionAudioCategory Category : LoopCategories)
	{
		const FSkyguardProductionAudioEntry* Entry =
			ProductionBank->FindEntry(Category);
		if (!Entry)
		{
			continue;
		}
		FResolvedLoopRoute& Route = ResolvedLoopRoutes.AddDefaulted_GetRef();
		Route.Category = Category;
		Route.Sound = Entry->Sound;
		Route.Attenuation = Entry->Attenuation;
		Route.Concurrency = Entry->Concurrency;
		Route.OutputSubmix = Entry->OutputSubmix;
	}
}

int32 USkyguardAudioDirectorComponent::GetResolvedProductionLoopRouteCount() const
{
	return ResolvedLoopRoutes.Num();
}

bool USkyguardAudioDirectorComponent::AreResolvedProductionLoopRoutesComplete() const
{
	if (ResolvedLoopRoutes.Num() != 5)
	{
		return false;
	}
	for (const FResolvedLoopRoute& Route : ResolvedLoopRoutes)
	{
		if (Route.Sound.IsNull() || Route.Attenuation.IsNull() ||
			Route.Concurrency.IsNull() || Route.OutputSubmix.IsNull())
		{
			return false;
		}
	}
	return true;
}

FSkyguardProductionAudioAudit USkyguardAudioDirectorComponent::GetProductionBankAudit() const
{
	return ProductionBank
		? ProductionBank->EvaluateReadiness()
		: FSkyguardProductionAudioAudit();
}

const FSkyguardAudioEventDefinition* USkyguardAudioDirectorComponent::FindDefinition(const ESkyguardAudioEvent Event) const
{
	return EventDefinitions.FindByPredicate([Event](const FSkyguardAudioEventDefinition& Definition)
	{
		return Definition.Event == Event;
	});
}

bool USkyguardAudioDirectorComponent::TriggerEvent(const ESkyguardAudioEvent Event, const FVector& WorldLocation)
{
	++Telemetry.RequestedEvents;
	const FSkyguardAudioEventDefinition* Definition = FindDefinition(Event);
	if (!Definition)
	{
		++Telemetry.RejectedMissingAsset;
		return false;
	}
	if (Cooldowns.FindRef(Event) > 0.f)
	{
		++Telemetry.RejectedByCooldown;
		return false;
	}

	int32 SameEventCount = 0;
	for (const FActiveVoice& Voice : ActiveVoices)
	{
		SameEventCount += Voice.Event == Event ? 1 : 0;
	}
	if (SameEventCount >= Definition->MaxConcurrent)
	{
		++Telemetry.RejectedByConcurrency;
		return false;
	}

	if (ActiveVoices.Num() >= GlobalVoiceLimit)
	{
		int32 LowestIndex = INDEX_NONE;
		int32 LowestPriority = MAX_int32;
		for (int32 Index = 0; Index < ActiveVoices.Num(); ++Index)
		{
			if (ActiveVoices[Index].Priority < LowestPriority)
			{
				LowestPriority = ActiveVoices[Index].Priority;
				LowestIndex = Index;
			}
		}
		if (LowestIndex == INDEX_NONE || LowestPriority >= Definition->Priority)
		{
			++Telemetry.RejectedByConcurrency;
			return false;
		}
		if (ActiveVoices[LowestIndex].Component.IsValid())
		{
			ActiveVoices[LowestIndex].Component->Stop();
		}
		ActiveVoices.RemoveAtSwap(LowestIndex);
		++Telemetry.PriorityEvictions;
	}

	USoundBase* ResolvedSound = Definition->Sound.Get();
	UAudioComponent* Spawned = nullptr;
	if (!Definition->Sound.IsNull() && !ResolvedSound)
	{
		++Telemetry.RejectedMissingAsset;
		return false;
	}
	if (ResolvedSound && GetWorld())
	{
		const float MixVolume = Definition->Volume
			* (ListenerPerspective == ESkyguardListenerPerspective::RearCockpit ? CockpitExteriorAttenuation : 1.f)
			* FMath::Lerp(1.f, 0.32f, SuppressionAmount);
		Spawned = UGameplayStatics::SpawnSoundAtLocation(
			this,
			ResolvedSound,
			WorldLocation,
			FRotator::ZeroRotator,
			MixVolume,
			Definition->Pitch,
			0.f,
			Definition->Attenuation.Get(),
			Definition->Concurrency.Get(),
			true);
		if (Spawned && ListenerPerspective == ESkyguardListenerPerspective::RearCockpit)
		{
			Spawned->SetLowPassFilterEnabled(true);
			Spawned->SetLowPassFilterFrequency(CockpitLowPassHz);
		}
		if (Spawned && Definition->OutputSubmix.Get())
		{
			Spawned->SetSubmixSend(Definition->OutputSubmix.Get(), 1.f);
		}
	}

	FActiveVoice& Voice = ActiveVoices.AddDefaulted_GetRef();
	Voice.Event = Event;
	Voice.Priority = Definition->Priority;
	Voice.RemainingSeconds = Definition->EstimatedDurationSeconds;
	Voice.Component = Spawned;
	Cooldowns.Add(Event, Definition->CooldownSeconds);
	++Telemetry.PlayedEvents;
	Telemetry.PeakActiveVoices = FMath::Max(Telemetry.PeakActiveVoices, ActiveVoices.Num());
	return true;
}

bool USkyguardAudioDirectorComponent::TriggerWorldEvent(
	UObject* WorldContextObject,
	const ESkyguardAudioEvent Event,
	const FVector& WorldLocation)
{
	if (!WorldContextObject)
	{
		return false;
	}
	UWorld* World = WorldContextObject->GetWorld();
	if (!World)
	{
		return false;
	}
	const TWeakObjectPtr<USkyguardAudioDirectorComponent>* Registered =
		RegisteredAudioDirectors.Find(World);
	USkyguardAudioDirectorComponent* Director =
		Registered ? Registered->Get() : nullptr;
	return Director && Director->TriggerEvent(Event, WorldLocation);
}

void USkyguardAudioDirectorComponent::SetEngineState(const float NormalizedRpm, const float NormalizedLoad, const float AirspeedKph, const float OpenCanopyFraction)
{
	Rpm = FMath::Clamp(NormalizedRpm, 0.f, 1.f);
	Load = FMath::Clamp(NormalizedLoad, 0.f, 1.f);
	Airspeed = FMath::Max(0.f, AirspeedKph);
	CanopyOpen = FMath::Clamp(OpenCanopyFraction, 0.f, 1.f);

	IdleBlend = FMath::Clamp(1.f - Rpm * 2.f, 0.f, 1.f);
	CruiseBlend = FMath::Clamp(1.f - FMath::Abs(Rpm - 0.55f) / 0.45f, 0.f, 1.f) * FMath::Lerp(1.f, 0.8f, Load);
	PowerBlend = FMath::Clamp((Rpm - 0.55f) / 0.45f, 0.f, 1.f) * FMath::Lerp(0.55f, 1.f, Load);
	WindBlend = FMath::Clamp(Airspeed / 260.f, 0.f, 1.f) * FMath::Lerp(0.2f, 1.f, CanopyOpen);
	UpdateLoopMix();
}

void USkyguardAudioDirectorComponent::SetListenerPerspective(const ESkyguardListenerPerspective NewPerspective)
{
	ListenerPerspective = NewPerspective;
	ApplyListenerSoundMix();
	UpdateLoopMix();
}

void USkyguardAudioDirectorComponent::ApplyListenerSoundMix()
{
	if (!ProductionBank)
	{
		return;
	}
	USoundMix* CockpitMix = ProductionBank->Routing.CockpitSoundMix.Get();
	if (!CockpitMix)
	{
		return;
	}
	const bool bNeedsCockpitMix =
		ListenerPerspective == ESkyguardListenerPerspective::RearCockpit;
	if (bNeedsCockpitMix && !bCockpitSoundMixPushed)
	{
		UGameplayStatics::PushSoundMixModifier(this, CockpitMix);
		bCockpitSoundMixPushed = true;
	}
	else if (!bNeedsCockpitMix && bCockpitSoundMixPushed)
	{
		UGameplayStatics::PopSoundMixModifier(this, CockpitMix);
		bCockpitSoundMixPushed = false;
	}
}

void USkyguardAudioDirectorComponent::ApplyHearingSuppression(const float Strength, const float DurationSeconds)
{
	SuppressionAmount = FMath::Max(SuppressionAmount, FMath::Clamp(Strength, 0.f, 1.f));
	SuppressionRemainingSeconds = FMath::Max(SuppressionRemainingSeconds, FMath::Max(0.f, DurationSeconds));
	UpdateLoopMix();
}

void USkyguardAudioDirectorComponent::AdvanceAudioState(const float DeltaSeconds)
{
	const float SafeDelta = FMath::Max(0.f, DeltaSeconds);
	for (TPair<ESkyguardAudioEvent, float>& Pair : Cooldowns)
	{
		Pair.Value = FMath::Max(0.f, Pair.Value - SafeDelta);
	}
	for (int32 Index = ActiveVoices.Num() - 1; Index >= 0; --Index)
	{
		ActiveVoices[Index].RemainingSeconds -= SafeDelta;
		if (ActiveVoices[Index].RemainingSeconds <= 0.f)
		{
			ActiveVoices.RemoveAtSwap(Index);
		}
	}
	if (SuppressionRemainingSeconds > 0.f)
	{
		SuppressionRemainingSeconds = FMath::Max(0.f, SuppressionRemainingSeconds - SafeDelta);
		if (SuppressionRemainingSeconds <= 0.f)
		{
			SuppressionAmount = 0.f;
			UpdateLoopMix();
		}
	}
}

void USkyguardAudioDirectorComponent::CreateResolvedLoopComponents()
{
	if (!GetOwner() || !GetOwner()->GetRootComponent())
	{
		return;
	}
	if (ResolvedLoopRoutes.Num() == 5)
	{
		for (const FResolvedLoopRoute& Route : ResolvedLoopRoutes)
		{
			USoundBase* Sound = Route.Sound.Get();
			if (!Sound)
			{
				LoopComponents.Add(nullptr);
				continue;
			}
			UAudioComponent* Component = UGameplayStatics::SpawnSoundAttached(
				Sound,
				GetOwner()->GetRootComponent(),
				NAME_None,
				FVector::ZeroVector,
				FRotator::ZeroRotator,
				EAttachLocation::KeepRelativeOffset,
				false,
				0.f,
				1.f,
				0.f,
				Route.Attenuation.Get(),
				Route.Concurrency.Get(),
				false);
			if (Component && Route.OutputSubmix.Get())
			{
				Component->SetSubmixSend(Route.OutputSubmix.Get(), 1.f);
			}
			LoopComponents.Add(Component);
		}
	}
	else
	{
		const TSoftObjectPtr<USoundBase> Loops[] =
		{
			EngineIdleLoop, EngineCruiseLoop, EnginePowerLoop, PropellerLoop, OpenCockpitWindLoop
		};
		for (const TSoftObjectPtr<USoundBase>& SoftSound : Loops)
		{
			USoundBase* Sound = SoftSound.Get();
			if (!Sound)
			{
				LoopComponents.Add(nullptr);
				continue;
			}
			UAudioComponent* Component = UGameplayStatics::SpawnSoundAttached(
				Sound,
				GetOwner()->GetRootComponent(),
				NAME_None,
				FVector::ZeroVector,
				EAttachLocation::KeepRelativeOffset,
				false,
				0.f);
			LoopComponents.Add(Component);
		}
	}
	UpdateLoopMix();
}

void USkyguardAudioDirectorComponent::StopLoopComponents()
{
	for (UAudioComponent* Component : LoopComponents)
	{
		if (Component)
		{
			Component->Stop();
		}
	}
	LoopComponents.Reset();
}

void USkyguardAudioDirectorComponent::UpdateLoopMix()
{
	const float CockpitMix = ListenerPerspective == ESkyguardListenerPerspective::RearCockpit
		? CockpitExteriorAttenuation
		: 1.f;
	const float SuppressionMix = FMath::Lerp(1.f, 0.3f, SuppressionAmount);
	const float Volumes[] = { IdleBlend, CruiseBlend, PowerBlend, Rpm, WindBlend };
	for (int32 Index = 0; Index < LoopComponents.Num() && Index < UE_ARRAY_COUNT(Volumes); ++Index)
	{
		if (UAudioComponent* Component = LoopComponents[Index])
		{
			Component->SetVolumeMultiplier(Volumes[Index] * CockpitMix * SuppressionMix);
			Component->SetPitchMultiplier(FMath::Lerp(0.75f, 1.35f, Rpm));
			const bool bCockpit = ListenerPerspective == ESkyguardListenerPerspective::RearCockpit;
			Component->SetLowPassFilterEnabled(bCockpit || SuppressionAmount > 0.f);
			Component->SetLowPassFilterFrequency(
				FMath::Lerp(
					bCockpit ? CockpitLowPassHz : 20000.f,
					950.f,
					SuppressionAmount));
		}
	}
}
