#include "SkyguardMission09IntegrationDirector.h"

#include "SkyguardDaySortieBeatKit.h"
#include "SkyguardDrone.h"
#include "SkyguardAudioDirectorComponent.h"
#include "SkyguardAudioTypes.h"
#include "SkyguardBossWeakPointComponent.h"
#include "SkyguardCampaignDefinition.h"
#include "SkyguardCampaignSubsystem.h"
#include "SkyguardGunner.h"
#include "SkyguardIronRainBoss.h"
#include "SkyguardMissionBriefingComponent.h"
#include "SkyguardMissionDefinition.h"
#include "SkyguardMissionDirectorCampaignHelpers.h"
#include "SkyguardMissionDirectorPresentationHelpers.h"
#include "SkyguardMissionMapAssemblyDirector.h"
#include "SkyguardObjectiveRuntime.h"
#include "SkyguardRadioChatterComponent.h"
#include "SkyguardSortiePresentationComponent.h"
#include "SkyguardPlayerAircraft.h"
#include "SkyguardYak52Aircraft.h"
#include "Components/SceneComponent.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "EngineUtils.h"

namespace
{
	template <typename T>
	T* FindFirstMission09Actor(UWorld* World)
	{
		if (!World) return nullptr;
		for (TActorIterator<T> It(World); It; ++It)
		{
			if (IsValid(*It)) return *It;
		}
		return nullptr;
	}

	template <typename T>
	T* SpawnMission09Actor(UWorld* World, const FVector& Location)
	{
		if (!World) return nullptr;
		FActorSpawnParameters Parameters;
		Parameters.SpawnCollisionHandlingOverride =
			ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
		return World->SpawnActor<T>(
			T::StaticClass(), Location, FRotator::ZeroRotator, Parameters);
	}
}

ASkyguardMission09IntegrationDirector::ASkyguardMission09IntegrationDirector()
{
	PrimaryActorTick.bCanEverTick = true;
	Root = CreateDefaultSubobject<USceneComponent>(TEXT("Mission09IntegrationRoot"));
	SetRootComponent(Root);
	SkylineAnchor = CreateDefaultSubobject<USceneComponent>(TEXT("ProtectedMetropolitanSkyline"));
	SkylineAnchor->SetupAttachment(Root);
	PowerStationAnchor = CreateDefaultSubobject<USceneComponent>(TEXT("ProtectedCoastalPowerStation"));
	PowerStationAnchor->SetupAttachment(Root);
	MajorBridgeAnchor = CreateDefaultSubobject<USceneComponent>(TEXT("ProtectedMajorBridge"));
	MajorBridgeAnchor->SetupAttachment(Root);
	Briefing = CreateDefaultSubobject<USkyguardMissionBriefingComponent>(TEXT("Briefing"));
	AudioDirector = CreateDefaultSubobject<USkyguardAudioDirectorComponent>(TEXT("AudioDirector"));
	RadioChatter = CreateDefaultSubobject<USkyguardRadioChatterComponent>(TEXT("RadioChatter"));
	SortiePresentation = CreateDefaultSubobject<USkyguardSortiePresentationComponent>(
		TEXT("SortiePresentation"));
	CampaignDefinition = TSoftObjectPtr<USkyguardCampaignDefinition>(
		FSoftObjectPath(
			TEXT("/Game/Skyguard/Data/Campaign_v1/DA_Campaign_Skyguard52.DA_Campaign_Skyguard52")));
	MissionDefinition = TSoftObjectPtr<USkyguardMissionDefinition>(
		FSoftObjectPath(
			TEXT("/Game/Skyguard/Data/Campaign_v1/DA_Mission_M09_SaturationAttack.DA_Mission_M09_SaturationAttack")));
	Tags.AddUnique(TEXT("Skyguard.Mission09.PlayableIntegration"));
	Tags.AddUnique(TEXT("Skyguard.Performance.BoundedPool"));
}

void ASkyguardMission09IntegrationDirector::BeginPlay()
{
	Super::BeginPlay();
	ASkyguardDrone::OnAnyCityImpacted.AddUObject(
		this,
		&ASkyguardMission09IntegrationDirector::HandleDroneCityImpact);
	if (bAutoInitialize) InitializePlayableMission();
}

void ASkyguardMission09IntegrationDirector::Tick(const float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	TickDayBeatKit(DeltaSeconds);
}

void ASkyguardMission09IntegrationDirector::EndPlay(
	const EEndPlayReason::Type EndPlayReason)
{
	ASkyguardDrone::OnAnyCityImpacted.RemoveAll(this);
	if (IronRain)
	{
		IronRain->OnBossPhaseChanged.RemoveDynamic(
			this,
			&ASkyguardMission09IntegrationDirector::HandleBossPhaseChanged);
		IronRain->OnPilotCommandNative.RemoveAll(this);
	}
	Super::EndPlay(EndPlayReason);
}

void ASkyguardMission09IntegrationDirector::HandleDroneCityImpact(
	ASkyguardDrone* Drone)
{
	if (!Drone || !bInitialized || bMissionCompleted)
	{
		return;
	}
	NotifyProtectedAssetFailed();
}

bool ASkyguardMission09IntegrationDirector::NotifyProtectedAssetFailed()
{
	// ProtectCityInfrastructure fails once fewer than two targets remain.
	NotifyProtectedTargetDamage(
		ESkyguardMission09ProtectedTarget::MetropolitanSkyline,
		FMath::Max(MaximumProtectedTargetIntegrity, 1));
	return NotifyProtectedTargetDamage(
		ESkyguardMission09ProtectedTarget::CoastalPowerStation,
		FMath::Max(MaximumProtectedTargetIntegrity, 1));
}

bool ASkyguardMission09IntegrationDirector::InitializePlayableMission()
{
	if (bInitialized)
	{
		UpdateReadiness();
		return IsCorePlayableReady();
	}
	ResolvedMission = MissionDefinition.LoadSynchronous();
	ResolvedCampaign = CampaignDefinition.LoadSynchronous();
	if (!ConfigureMissionDefinition(ResolvedMission)) return false;
	UWorld* World = GetWorld();
	ASkyguardMissionMapAssemblyDirector* Assembly =
		FindFirstMission09Actor<ASkyguardMissionMapAssemblyDirector>(World);
	ASkyguardYak52Aircraft* Yak =
		FindFirstMission09Actor<ASkyguardYak52Aircraft>(World);
	ASkyguardGunner* ResolvedGunner =
		FindFirstMission09Actor<ASkyguardGunner>(World);
	ASkyguardIronRainBoss* Boss =
		FindFirstMission09Actor<ASkyguardIronRainBoss>(World);
	if (bAllowBoundedActorSpawning)
	{
		if (!Yak) Yak = SpawnMission09Actor<ASkyguardYak52Aircraft>(World, YakSpawnLocation);
		if (!ResolvedGunner) ResolvedGunner = SpawnMission09Actor<ASkyguardGunner>(World, YakSpawnLocation);
		if (!Boss) Boss = SpawnMission09Actor<ASkyguardIronRainBoss>(World, IronRainSpawnLocation);
	}
	BindRuntimeActors(Assembly, Yak, ResolvedGunner, Boss);
	if (UGameInstance* GameInstance = GetGameInstance())
	{
		USkyguardCampaignSubsystem* Runtime =
			GameInstance->GetSubsystem<USkyguardCampaignSubsystem>();
		if (Runtime && ResolvedCampaign)
		{
			const bool bConfigured =
				Runtime->ConfigureCampaign(ResolvedCampaign);
			if (bConfigured)
			{
				SkyguardMissionDirectorCampaignHelpers::LoadCampaignProgressAfterConfigure(
					Runtime,
					CampaignSaveSlotName,
					CampaignSaveUserIndex);
			}
			const bool bAlreadyActive =
				Runtime->GetActiveMission() == ResolvedMission;
			const bool bStarted =
				bConfigured && (bAlreadyActive ||
					Runtime->StartMission(GetMissionId()));
			BindCampaignRuntime(bStarted ? Runtime : nullptr);
		}
	}
	ConfigurePresentation();
	bInitialized = true;
	UpdateReadiness();
	Briefing->SetAssetsReady(IsCorePlayableReady());
	return IsCorePlayableReady();
}

void ASkyguardMission09IntegrationDirector::ConfigurePresentation()
{
	if (!ResolvedMission)
	{
		return;
	}
	Briefing->ConfigureFromMission(ResolvedMission);
	SortiePresentation->ConfigureFromMission(ResolvedMission);
	SortiePresentation->BindCampaignRuntime(CampaignRuntime);
	AudioDirector->PrimeConfiguredAssets();
	AudioDirector->SetListenerPerspective(
		ESkyguardListenerPerspective::RearCockpit);
	RadioChatter->ClearQueue();
	TArray<FSkyguardRadioLine> Lines;
	for (int32 Index = 0;
		Index < ResolvedMission->Presentation.RadioChatter.Num();
		++Index)
	{
		FSkyguardRadioLine Line;
		Line.LineId = FName(*FString::Printf(
			TEXT("M09_Saturation_%02d"),
			Index + 1));
		Line.Speaker = FText::FromString(
			Index == 0 ? TEXT("City Defense") : TEXT("Pilot"));
		Line.Subtitle = ResolvedMission->Presentation.RadioChatter[Index];
		Line.Priority = 95 - Index;
		Line.EstimatedDurationSeconds = 2.8f;
		Lines.Add(Line);
	}
	RadioChatter->PrimeLines(Lines);
	SkyguardMissionDirectorPresentationHelpers::BindHudHostToPresentation(
		this,
		SortiePresentation);
}

bool ASkyguardMission09IntegrationDirector::ConfigureMissionDefinition(
	USkyguardMissionDefinition* Mission)
{
	TArray<FText> Errors;
	if (!ValidateMissionContract(Mission, Errors)) return false;
	ResolvedMission = Mission;
	CampaignRuntime = nullptr;
	Readiness.bCampaignRuntimeStarted = false;
	LocalObjectiveRuntime = NewObject<USkyguardObjectiveRuntime>(
		this, TEXT("Mission09LocalObjectives"));
	LocalObjectiveRuntime->InitializeObjectives(Mission->Objectives);
	WaveState = ESkyguardMission09WaveState::AwaitingWave;
	CurrentWaveIndex = -1;
	RemainingThreatsInWave = 0;
	ObservedDispenserMilestones = 0;
	ObservedBossMilestones = 0;
	PoolRuntime = FSkyguardMission09PoolRuntime();
	PoolRuntime.Available = PoolBudget.PoolCapacity;
	ProtectedTargets.Reset();
	for (const ESkyguardMission09ProtectedTarget Target : {
		ESkyguardMission09ProtectedTarget::MetropolitanSkyline,
		ESkyguardMission09ProtectedTarget::CoastalPowerStation,
		ESkyguardMission09ProtectedTarget::MajorBridge})
	{
		FSkyguardMission09ProtectedTargetRuntime Runtime;
		Runtime.Target = Target;
		Runtime.Integrity = MaximumProtectedTargetIntegrity;
		ProtectedTargets.Add(Runtime);
	}
	bMissionCompleted = false;
	DayBeatIndex = 0;
	DayBeatElapsed = 0.f;
	UpdateReadiness();
	return true;
}

bool ASkyguardMission09IntegrationDirector::BindCampaignRuntime(
	USkyguardCampaignSubsystem* InCampaignRuntime)
{
	CampaignRuntime =
		InCampaignRuntime &&
		InCampaignRuntime->GetActiveMission() == ResolvedMission
			? InCampaignRuntime
			: nullptr;
	Readiness.bCampaignRuntimeStarted = CampaignRuntime != nullptr;
	if (SortiePresentation)
	{
		SortiePresentation->BindCampaignRuntime(CampaignRuntime);
	}
	UpdateReadiness();
	return Readiness.bCampaignRuntimeStarted;
}

void ASkyguardMission09IntegrationDirector::BindRuntimeActors(
	ASkyguardMissionMapAssemblyDirector* InAssembly,
	ASkyguardYak52Aircraft* InYak,
	ASkyguardGunner* InGunner,
	ASkyguardIronRainBoss* InIronRain)
{
	if (IronRain && IronRain != InIronRain)
	{
		IronRain->OnBossPhaseChanged.RemoveDynamic(
			this, &ASkyguardMission09IntegrationDirector::HandleBossPhaseChanged);
		IronRain->OnPilotCommandNative.RemoveAll(this);
	}
	MapAssembly = InAssembly;
	YakAircraft = InYak;
	Gunner = InGunner;
	if (Gunner)
	{
		Gunner->ResetSortieCombatStats();
	}
	IronRain = InIronRain;
	if (YakAircraft)
	{
		YakAircraft->SetEnginePower(0.84f);
		YakAircraft->SetRearCanopyOpen(true);
	}
	FSkyguardPlayerAircraft::AttachGunner(Gunner, YakAircraft);
	if (IronRain)
	{
		IronRain->OnBossPhaseChanged.AddUniqueDynamic(
			this, &ASkyguardMission09IntegrationDirector::HandleBossPhaseChanged);
		IronRain->OnPilotCommandNative.AddUObject(
			this, &ASkyguardMission09IntegrationDirector::HandlePilotCommand);
	}
	UpdateReadiness();
}

int32 ASkyguardMission09IntegrationDirector::CalculateWaveThreatCount(
	const int32 WaveIndex) const
{
	static const int32 Counts[] = {8, 12, 16};
	return WaveIndex >= 0 && WaveIndex < UE_ARRAY_COUNT(Counts)
		? Counts[WaveIndex] : 0;
}

bool ASkyguardMission09IntegrationDirector::ReservePooledThreats(const int32 Count)
{
	if (Count <= 0 || PoolRuntime.Available < Count ||
		PoolRuntime.Active + Count > PoolBudget.MaxActiveThreats)
	{
		return false;
	}
	PoolRuntime.Available -= Count;
	PoolRuntime.Active += Count;
	PoolRuntime.PeakActive = FMath::Max(PoolRuntime.PeakActive, PoolRuntime.Active);
	return true;
}

void ASkyguardMission09IntegrationDirector::RecycleThreats(const int32 Count)
{
	const int32 Recycled = FMath::Clamp(Count, 0, PoolRuntime.Active);
	PoolRuntime.Active -= Recycled;
	PoolRuntime.Available = FMath::Min(
		PoolBudget.PoolCapacity, PoolRuntime.Available + Recycled);
	PoolRuntime.Recycled += Recycled;
}

bool ASkyguardMission09IntegrationDirector::StartNextWave()
{
	if (!ResolvedMission || WaveState != ESkyguardMission09WaveState::AwaitingWave)
		return false;
	const int32 Next = CurrentWaveIndex + 1;
	const int32 Count = CalculateWaveThreatCount(Next);
	if (!ResolvedMission->Waves.IsValidIndex(Next) || !ReservePooledThreats(Count))
		return false;
	CurrentWaveIndex = Next;
	RemainingThreatsInWave = Count;
	WaveState = ESkyguardMission09WaveState::WaveActive;
	return true;
}

bool ASkyguardMission09IntegrationDirector::NotifyThreatDestroyed(const int32 Amount)
{
	if (WaveState != ESkyguardMission09WaveState::WaveActive || Amount <= 0)
		return false;
	const int32 Applied = FMath::Min(Amount, RemainingThreatsInWave);
	RemainingThreatsInWave -= Applied;
	RecycleThreats(Applied);
	if (RemainingThreatsInWave == 0)
	{
		WaveState = CurrentWaveIndex == 2
			? ESkyguardMission09WaveState::BossEngaged
			: ESkyguardMission09WaveState::AwaitingWave;
	}
	return Applied > 0;
}

bool ASkyguardMission09IntegrationDirector::NotifyProtectedTargetDamage(
	const ESkyguardMission09ProtectedTarget Target,
	const int32 Damage)
{
	FSkyguardMission09ProtectedTargetRuntime* Runtime = FindProtectedTarget(Target);
	if (!Runtime || Damage <= 0 || Runtime->bDestroyed ||
		WaveState == ESkyguardMission09WaveState::Completed) return false;
	Runtime->Integrity = FMath::Max(0, Runtime->Integrity - Damage);
	Runtime->bDestroyed = Runtime->Integrity == 0;
	if (GetSurvivingTargetCount() < 2)
	{
		FailObjective(TEXT("ProtectCityInfrastructure"));
		WaveState = ESkyguardMission09WaveState::Failed;

		if (!bMissionCompleted &&
			CampaignRuntime &&
			CampaignRuntime->GetActiveMission() == ResolvedMission)
		{
			bMissionCompleted =
				SkyguardMissionDirectorCampaignHelpers::FillAndFail(
					CampaignRuntime,
					Gunner,
					this,
					SortiePresentation,
					CampaignSaveSlotName,
					CampaignSaveUserIndex);
		}
		else if (!bMissionCompleted)
		{
			bMissionCompleted = true;
		}
	}
	return true;
}

void ASkyguardMission09IntegrationDirector::SynchronizeRuntimeState()
{
	if (!IronRain || !GetObjectiveRuntime() ||
		WaveState == ESkyguardMission09WaveState::Failed) return;
	const int32 Dispensers = IronRain->GetDestroyedDispenserCount();
	while (ObservedDispenserMilestones < Dispensers)
	{
		NotifyObjectiveProgress(TEXT("BreakSwarmRelays"), 1);
		++ObservedDispenserMilestones;
	}
	int32 Milestones = 0;
	if (Dispensers == 3) ++Milestones;
	if (IronRain->GetDestroyedAntennaCount() == 2) ++Milestones;
	if (IronRain->DecoyController->bDestroyed) ++Milestones;
	if (IronRain->GetBossPhase() == ESkyguardBossPhase::Defeated) ++Milestones;
	while (ObservedBossMilestones < Milestones)
	{
		NotifyObjectiveProgress(TEXT("DefeatIronRain"), 1);
		++ObservedBossMilestones;
	}
	CompleteMissionIfReady();
}

bool ASkyguardMission09IntegrationDirector::NotifyObjectiveProgress(
	const FName ObjectiveId,
	const int32 Amount)
{
	if (!ResolvedMission || ObjectiveId.IsNone() || Amount <= 0 ||
		!ResolvedMission->FindObjective(ObjectiveId))
	{
		return false;
	}
	if (CampaignRuntime &&
		CampaignRuntime->GetActiveMission() == ResolvedMission)
	{
		return CampaignRuntime->AddObjectiveProgress(ObjectiveId, Amount);
	}
	return LocalObjectiveRuntime &&
		LocalObjectiveRuntime->AddProgress(ObjectiveId, Amount);
}

void ASkyguardMission09IntegrationDirector::FailObjective(
	const FName ObjectiveId)
{
	if (CampaignRuntime &&
		CampaignRuntime->GetActiveMission() == ResolvedMission)
	{
		CampaignRuntime->FailObjective(ObjectiveId);
	}
	else if (LocalObjectiveRuntime)
	{
		LocalObjectiveRuntime->FailObjective(ObjectiveId);
	}
}

void ASkyguardMission09IntegrationDirector::CompleteMissionIfReady()
{
	if (bMissionCompleted || WaveState != ESkyguardMission09WaveState::BossEngaged ||
		!IronRain || IronRain->GetBossPhase() != ESkyguardBossPhase::Defeated ||
		GetSurvivingTargetCount() < 2)
	{
		return;
	}
	USkyguardObjectiveRuntime* Objectives = GetObjectiveRuntime();
	if (Objectives &&
                Objectives->GetProgress(TEXT("ProtectCityInfrastructure")).State ==
                ESkyguardMissionObjectiveState::Active)
        {
                if (CampaignRuntime &&
                        CampaignRuntime->GetActiveMission() == ResolvedMission)
                {
                        CampaignRuntime->CompleteSurviveObjectiveIfIntact(TEXT("ProtectCityInfrastructure"));
                }
                else
                {
                        Objectives->CompleteSurviveObjectiveIfIntact(TEXT("ProtectCityInfrastructure"));
                }
        }
	Objectives = GetObjectiveRuntime();
	if (!Objectives || Objectives->HasTerminalFailure() ||
		!Objectives->AreRequiredObjectivesComplete())
	{
		return;
	}
	if (CampaignRuntime &&
		CampaignRuntime->GetActiveMission() == ResolvedMission)
	{
		bMissionCompleted =
			SkyguardMissionDirectorCampaignHelpers::FillAndFinalize(
				CampaignRuntime,
				Gunner,
				this,
				SortiePresentation,
				CampaignSaveSlotName,
				CampaignSaveUserIndex);
	}
	else
	{
		bMissionCompleted = true;
	}
	if (bMissionCompleted)
	{
		WaveState = ESkyguardMission09WaveState::Completed;
	}
}

FSkyguardMission09ProtectedTargetRuntime*
ASkyguardMission09IntegrationDirector::FindProtectedTarget(
	const ESkyguardMission09ProtectedTarget Target)
{
	return ProtectedTargets.FindByPredicate(
		[Target](const auto& Runtime) { return Runtime.Target == Target; });
}

const FSkyguardMission09ProtectedTargetRuntime*
ASkyguardMission09IntegrationDirector::FindProtectedTarget(
	const ESkyguardMission09ProtectedTarget Target) const
{
	return ProtectedTargets.FindByPredicate(
		[Target](const auto& Runtime) { return Runtime.Target == Target; });
}

FSkyguardMission09ProtectedTargetRuntime
ASkyguardMission09IntegrationDirector::GetProtectedTarget(
	const ESkyguardMission09ProtectedTarget Target) const
{
	const auto* Runtime = FindProtectedTarget(Target);
	return Runtime ? *Runtime : FSkyguardMission09ProtectedTargetRuntime();
}

int32 ASkyguardMission09IntegrationDirector::GetSurvivingTargetCount() const
{
	int32 Count = 0;
	for (const FSkyguardMission09ProtectedTargetRuntime& Runtime : ProtectedTargets)
	{
		if (!Runtime.bDestroyed) ++Count;
	}
	return Count;
}

USkyguardObjectiveRuntime*
ASkyguardMission09IntegrationDirector::GetObjectiveRuntime() const
{
	if (CampaignRuntime &&
		CampaignRuntime->GetActiveMission() == ResolvedMission)
	{
		return CampaignRuntime->GetObjectiveRuntime();
	}
	return LocalObjectiveRuntime;
}

bool ASkyguardMission09IntegrationDirector::IsCorePlayableReady() const
{
	return Readiness.bMissionDefinitionValid &&
		Readiness.bCampaignDefinitionValid &&
		Readiness.bMapAssemblyReady &&
		Readiness.bYakRuntimeReady && Readiness.bGunnerReady &&
		Readiness.bIronRainReady && Readiness.bObjectivesReady &&
		Readiness.bEscalatingWavesReady && Readiness.bProtectedTargetsReady &&
		Readiness.bPoolBudgetSafe && Readiness.bPresentationReady &&
		Readiness.bSortiePresentationReady;
}

void ASkyguardMission09IntegrationDirector::UpdateReadiness()
{
	TArray<FText> Errors;
	Readiness.bMissionDefinitionValid = ValidateMissionContract(ResolvedMission, Errors);
	Readiness.bCampaignDefinitionValid =
		ResolvedCampaign &&
		ResolvedCampaign->FindMission(GetMissionId()) == ResolvedMission;
	TArray<FText> AssemblyErrors;
	Readiness.bMapAssemblyReady = MapAssembly &&
		MapAssembly->MissionId == GetMissionId() &&
		MapAssembly->SkylineStyle == ESkyguardMissionSkylineStyle::BlackoutUrban &&
		MapAssembly->ValidateAssembly(AssemblyErrors);
	Readiness.bYakRuntimeReady = YakAircraft && YakAircraft->GetRearGunnerMount();
	Readiness.bGunnerReady = Gunner && YakAircraft &&
		Gunner->GetAttachParentActor() == YakAircraft;
	Readiness.bIronRainReady = IronRain &&
		IronRain->DispenserPort && IronRain->DispenserCenter &&
		IronRain->DispenserStarboard && IronRain->CommandAntennaPort &&
		IronRain->CommandAntennaStarboard && IronRain->DecoyController &&
		IronRain->EnginePodPort && IronRain->EnginePodCenter &&
		IronRain->EnginePodStarboard && IronRain->FuelControlPort &&
		IronRain->FuelControlStarboard &&
		IronRain->GetMaxDefeatDebrisPieces() <= 3;
	Readiness.bObjectivesReady = GetObjectiveRuntime() && ResolvedMission &&
		ResolvedMission->Objectives.Num() == 3;
	Readiness.bEscalatingWavesReady = ResolvedMission &&
		ResolvedMission->Waves.Num() == 3 &&
		CalculateWaveThreatCount(0) == 8 &&
		CalculateWaveThreatCount(1) == 12 &&
		CalculateWaveThreatCount(2) == 16;
	Readiness.bProtectedTargetsReady = ProtectedTargets.Num() == 3 &&
		SkylineAnchor && PowerStationAnchor && MajorBridgeAnchor;
	Readiness.bPoolBudgetSafe =
		PoolBudget.MaxActiveThreats >= 16 &&
		PoolBudget.MaxActiveThreats <= 24 &&
		PoolBudget.PoolCapacity >= PoolBudget.MaxActiveThreats &&
		PoolBudget.PoolCapacity <= 48 &&
		PoolBudget.MaxActiveDecoys <= 12 &&
		PoolBudget.MaxSimultaneousExplosions <= 6;
	Readiness.bPresentationReady = Briefing && AudioDirector && RadioChatter;
	Readiness.bSortiePresentationReady =
		SortiePresentation && SortiePresentation->IsConfigured();
	Readiness.ObjectiveCount = ResolvedMission ? ResolvedMission->Objectives.Num() : 0;
	Readiness.WaveCount = ResolvedMission ? ResolvedMission->Waves.Num() : 0;
	Readiness.ProtectedTargetCount = ProtectedTargets.Num();
}

void ASkyguardMission09IntegrationDirector::HandleBossPhaseChanged(
	ESkyguardBossPhase PreviousPhase,
	ESkyguardBossPhase NewPhase)
{
	SynchronizeRuntimeState();
	if (NewPhase == ESkyguardBossPhase::Defeated)
	{
		AudioDirector->TriggerEvent(ESkyguardAudioEvent::ExplosionHeavy, IronRain->GetActorLocation());
	}
}

void ASkyguardMission09IntegrationDirector::HandlePilotCommand(
	const ESkyguardPilotCommand Command)
{
	if (YakAircraft) YakAircraft->IssuePilotCommand(Command);
}

const FSkyguardDaySortieBeatKit&
ASkyguardMission09IntegrationDirector::GetDayBeatKit() const
{
	return SkyguardDaySortieBeatKit::HunterKiller();
}

ESkyguardDaySortieBeatKind
ASkyguardMission09IntegrationDirector::GetDayBeatKind() const
{
	return SkyguardDaySortieBeatKit::KindAt(GetDayBeatKit(), DayBeatIndex);
}

void ASkyguardMission09IntegrationDirector::TickDayBeatKit(
	const float DeltaSeconds)
{
	DayBeatElapsed += FMath::Max(DeltaSeconds, 0.f);
	DayBeatIndex = SkyguardDaySortieBeatKit::BeatIndexForElapsed(
		GetMissionId(),
		DayBeatElapsed);
}

bool ASkyguardMission09IntegrationDirector::ValidateMissionContract(
	const USkyguardMissionDefinition* Mission,
	TArray<FText>& OutErrors)
{
	OutErrors.Reset();
	auto Add = [&OutErrors](const TCHAR* Message)
	{
		OutErrors.Add(FText::FromString(Message));
	};
	if (!Mission)
	{
		Add(TEXT("Mission definition is missing."));
		return false;
	}
	if (Mission->MissionId != GetMissionId()) Add(TEXT("Mission id must be M09_SaturationAttack."));
	if (Mission->Route.Points.Num() != 4) Add(TEXT("Mission 9 requires four metropolitan route points."));
	if (Mission->Objectives.Num() != 3) Add(TEXT("Mission 9 requires exactly three objectives."));
	const FSkyguardObjectiveDefinition* Protect = Mission->FindObjective(TEXT("ProtectCityInfrastructure"));
	const FSkyguardObjectiveDefinition* Relays = Mission->FindObjective(TEXT("BreakSwarmRelays"));
	const FSkyguardObjectiveDefinition* Defeat = Mission->FindObjective(TEXT("DefeatIronRain"));
	if (!Protect || Protect->RequiredProgress != 1) Add(TEXT("ProtectCityInfrastructure must require one completion."));
	if (!Relays || Relays->RequiredProgress != 3) Add(TEXT("BreakSwarmRelays must require three dispenser milestones."));
	if (!Defeat || Defeat->RequiredProgress != 4) Add(TEXT("DefeatIronRain must require four phase milestones."));
	if (Mission->Waves.Num() != 3) Add(TEXT("Mission 9 requires three escalating saturation waves."));
	if (Mission->Boss.BossId != TEXT("IronRain") ||
		Mission->Boss.DefeatObjectiveId != TEXT("DefeatIronRain") ||
		Mission->Boss.MaximumBreakupPieces > 3)
	{
		Add(TEXT("Iron Rain governed boss identity or breakup budget is invalid."));
	}
	if (Mission->Weather.ProfileId != TEXT("CityDusk")) Add(TEXT("Mission 9 weather must be CityDusk."));
	if (Mission->Presentation.Briefing.IsEmpty() ||
		Mission->Presentation.RadioChatter.Num() < 3)
	{
		Add(TEXT("Mission 9 presentation is incomplete."));
	}
	return OutErrors.IsEmpty();
}
