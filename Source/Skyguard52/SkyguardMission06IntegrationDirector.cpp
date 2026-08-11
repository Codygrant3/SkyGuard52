#include "SkyguardMission06IntegrationDirector.h"

#include "SkyguardDrone.h"
#include "SkyguardAudioDirectorComponent.h"
#include "SkyguardBossWeakPointComponent.h"
#include "SkyguardCampaignDefinition.h"
#include "SkyguardCampaignSubsystem.h"
#include "SkyguardGunner.h"
#include "SkyguardMissionBriefingComponent.h"
#include "SkyguardMissionDefinition.h"
#include "SkyguardMissionDirectorCampaignHelpers.h"
#include "SkyguardMissionMapAssemblyDirector.h"
#include "SkyguardObjectiveRuntime.h"
#include "SkyguardRadioChatterComponent.h"
#include "SkyguardSortiePresentationComponent.h"
#include "SkyguardRunwayBreakerBoss.h"
#include "SkyguardYak52Aircraft.h"
#include "Components/SceneComponent.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "EngineUtils.h"

namespace
{
	template <typename T>
	T* FindFirstMission06Actor(UWorld* World)
	{
		if (!World)
		{
			return nullptr;
		}
		for (TActorIterator<T> It(World); It; ++It)
		{
			if (IsValid(*It))
			{
				return *It;
			}
		}
		return nullptr;
	}

	template <typename T>
	T* SpawnMission06Actor(
		UWorld* World,
		const FVector& Location,
		const FRotator& Rotation)
	{
		if (!World)
		{
			return nullptr;
		}
		FActorSpawnParameters Parameters;
		Parameters.SpawnCollisionHandlingOverride =
			ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
		return World->SpawnActor<T>(
			T::StaticClass(), Location, Rotation, Parameters);
	}
}

ASkyguardMission06IntegrationDirector::ASkyguardMission06IntegrationDirector()
{
	PrimaryActorTick.bCanEverTick = true;
	Root = CreateDefaultSubobject<USceneComponent>(
		TEXT("Mission06IntegrationRoot"));
	SetRootComponent(Root);
	Briefing = CreateDefaultSubobject<USkyguardMissionBriefingComponent>(
		TEXT("Briefing"));
	AudioDirector = CreateDefaultSubobject<USkyguardAudioDirectorComponent>(
		TEXT("AudioDirector"));
	RadioChatter = CreateDefaultSubobject<USkyguardRadioChatterComponent>(
		TEXT("RadioChatter"));
	SortiePresentation =
		CreateDefaultSubobject<USkyguardSortiePresentationComponent>(
			TEXT("SortiePresentation"));
	CampaignDefinition = TSoftObjectPtr<USkyguardCampaignDefinition>(
		FSoftObjectPath(
			TEXT("/Game/Skyguard/Data/Campaign_v1/DA_Campaign_Skyguard52.DA_Campaign_Skyguard52")));
	MissionDefinition = TSoftObjectPtr<USkyguardMissionDefinition>(
		FSoftObjectPath(
			TEXT("/Game/Skyguard/Data/Campaign_v1/DA_Mission_M06_AirfieldDefense.DA_Mission_M06_AirfieldDefense")));
	Tags.AddUnique(TEXT("Skyguard.Mission06.PlayableIntegration"));
	Tags.AddUnique(TEXT("Skyguard.PackagePrep.Native"));
}

void ASkyguardMission06IntegrationDirector::BeginPlay()
{
	Super::BeginPlay();
	ASkyguardDrone::OnAnyCityImpacted.AddUObject(
		this,
		&ASkyguardMission06IntegrationDirector::HandleDroneCityImpact);
	if (bAutoInitialize)
	{
		InitializePlayableMission();
	}
}

void ASkyguardMission06IntegrationDirector::EndPlay(
	const EEndPlayReason::Type EndPlayReason)
{
	ASkyguardDrone::OnAnyCityImpacted.RemoveAll(this);
	if (RunwayBreaker)
	{
		RunwayBreaker->OnBossPhaseChanged.RemoveDynamic(
			this,
			&ASkyguardMission06IntegrationDirector::HandleBossPhaseChanged);
		RunwayBreaker->OnPilotCommandNative.RemoveAll(this);
	}
	Super::EndPlay(EndPlayReason);
}

void ASkyguardMission06IntegrationDirector::HandleDroneCityImpact(
	ASkyguardDrone* Drone)
{
	if (!Drone || !bInitialized || bMissionCompleted)
	{
		return;
	}
	NotifyProtectedAssetFailed();
}

bool ASkyguardMission06IntegrationDirector::NotifyProtectedAssetFailed()
{
	// ProtectAirfieldAssets fails once fewer than two targets remain.
	NotifyAirfieldTargetDamage(
		ESkyguardAirfieldTarget::Runway,
		FMath::Max(MaximumTargetIntegrity, 1));
	return NotifyAirfieldTargetDamage(
		ESkyguardAirfieldTarget::Hangars,
		FMath::Max(MaximumTargetIntegrity, 1));
}

void ASkyguardMission06IntegrationDirector::Tick(const float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	if (!bInitialized)
	{
		return;
	}
	Briefing->AdvanceBriefing(DeltaSeconds);
	TryLaunchSortie();
	if (PayloadWindow.bActive)
	{
		AdvancePayloadWindow(DeltaSeconds);
	}
	if (bSortieLaunched)
	{
		SynchronizeRuntimeState();
	}
	if (YakAircraft && AudioDirector)
	{
		AudioDirector->SetEngineState(
			FMath::Clamp(YakAircraft->GetPropellerRPM() / 2800.f, 0.f, 1.f),
			0.82f, 220.f, 1.f);
	}
}

bool ASkyguardMission06IntegrationDirector::InitializePlayableMission()
{
	if (bInitialized)
	{
		UpdateReadiness();
		return IsCorePlayableReady();
	}
	ResolvedMission = MissionDefinition.LoadSynchronous();
	ResolvedCampaign = CampaignDefinition.LoadSynchronous();
	TArray<FText> Errors;
	if (!ValidateMissionContract(ResolvedMission, Errors))
	{
		UpdateReadiness();
		return false;
	}
	ConfigureMissionDefinition(ResolvedMission);
	ResolveOrSpawnActors();
	if (UGameInstance* GameInstance = GetGameInstance())
	{
		CampaignRuntime =
			GameInstance->GetSubsystem<USkyguardCampaignSubsystem>();
		if (CampaignRuntime && ResolvedCampaign)
		{
			const bool bConfigured =
				CampaignRuntime->ConfigureCampaign(ResolvedCampaign);
			if (bConfigured)
			{
				SkyguardMissionDirectorCampaignHelpers::LoadCampaignProgressAfterConfigure(
					CampaignRuntime,
					CampaignSaveSlotName,
					CampaignSaveUserIndex);
			}
			const bool bAlreadyActive =
				CampaignRuntime->GetActiveMission() == ResolvedMission;
			Readiness.bCampaignRuntimeStarted =
				bConfigured && (bAlreadyActive ||
					CampaignRuntime->StartMission(GetMissionId()));
		}
	}
	ConfigurePresentation();
	bInitialized = true;
	UpdateReadiness();
	Briefing->SetAssetsReady(IsCorePlayableReady());
	return IsCorePlayableReady();
}

bool ASkyguardMission06IntegrationDirector::ConfigureMissionDefinition(
	USkyguardMissionDefinition* Mission)
{
	TArray<FText> Errors;
	if (!ValidateMissionContract(Mission, Errors))
	{
		return false;
	}
	ResolvedMission = Mission;
	LocalObjectiveRuntime =
		NewObject<USkyguardObjectiveRuntime>(
			this, TEXT("Mission06LocalObjectives"));
	LocalObjectiveRuntime->InitializeObjectives(Mission->Objectives);
	ProtectedTargets.Reset();
	for (const ESkyguardAirfieldTarget Target : {
		ESkyguardAirfieldTarget::Runway,
		ESkyguardAirfieldTarget::Hangars,
		ESkyguardAirfieldTarget::ParkedAircraft})
	{
		FSkyguardAirfieldTargetRuntime Runtime;
		Runtime.Target = Target;
		Runtime.Integrity = MaximumTargetIntegrity;
		ProtectedTargets.Add(Runtime);
	}
	PayloadWindow = FSkyguardPayloadWindowRuntime();
	WaveState = ESkyguardMission06WaveState::AwaitingWave;
	CurrentWaveIndex = -1;
	RemainingThreatsInWave = 0;
	ObservedBossWeakPointsDestroyed = 0;
	ObservedPayloadRacksDestroyed = 0;
	return true;
}

void ASkyguardMission06IntegrationDirector::ResolveOrSpawnActors()
{
	UWorld* World = GetWorld();
	MapAssembly =
		FindFirstMission06Actor<ASkyguardMissionMapAssemblyDirector>(World);
	YakAircraft = FindFirstMission06Actor<ASkyguardYak52Aircraft>(World);
	Gunner = FindFirstMission06Actor<ASkyguardGunner>(World);
	RunwayBreaker =
		FindFirstMission06Actor<ASkyguardRunwayBreakerBoss>(World);
	if (bAllowBoundedActorSpawning)
	{
		if (!YakAircraft)
		{
			YakAircraft = SpawnMission06Actor<ASkyguardYak52Aircraft>(
				World, YakSpawnLocation, YakSpawnRotation);
		}
		if (!Gunner)
		{
			Gunner = SpawnMission06Actor<ASkyguardGunner>(
				World, YakSpawnLocation, YakSpawnRotation);
		}
		if (!RunwayBreaker)
		{
			RunwayBreaker = SpawnMission06Actor<ASkyguardRunwayBreakerBoss>(
				World,
				RunwayBreakerSpawnLocation,
				RunwayBreakerSpawnRotation);
		}
	}
	BindRuntimeActors(MapAssembly, YakAircraft, Gunner, RunwayBreaker);
}

void ASkyguardMission06IntegrationDirector::BindRuntimeActors(
	ASkyguardMissionMapAssemblyDirector* InMapAssembly,
	ASkyguardYak52Aircraft* Aircraft,
	ASkyguardGunner* InGunner,
	ASkyguardRunwayBreakerBoss* InRunwayBreaker)
{
	if (RunwayBreaker && RunwayBreaker != InRunwayBreaker)
	{
		RunwayBreaker->OnBossPhaseChanged.RemoveDynamic(
			this,
			&ASkyguardMission06IntegrationDirector::HandleBossPhaseChanged);
		RunwayBreaker->OnPilotCommandNative.RemoveAll(this);
	}
	MapAssembly = InMapAssembly;
	YakAircraft = Aircraft;
	Gunner = InGunner;
	if (Gunner)
	{
		Gunner->ResetSortieCombatStats();
	}
	RunwayBreaker = InRunwayBreaker;
	ObservedBossWeakPointsDestroyed =
		RunwayBreaker
			? RunwayBreaker->GetTelemetry().WeakPointsDestroyed
			: 0;
	ObservedPayloadRacksDestroyed = CountDestroyedPayloadRacks();
	if (YakAircraft)
	{
		YakAircraft->SetEnginePower(0.82f);
		YakAircraft->SetRearCanopyOpen(true);
	}
	if (YakAircraft && Gunner && YakAircraft->GetRearGunnerMount())
	{
		Gunner->AttachToComponent(
			YakAircraft->GetRearGunnerMount(),
			FAttachmentTransformRules::SnapToTargetNotIncludingScale);
	}
	if (RunwayBreaker)
	{
		RunwayBreaker->OnBossPhaseChanged.AddUniqueDynamic(
			this,
			&ASkyguardMission06IntegrationDirector::HandleBossPhaseChanged);
		RunwayBreaker->OnPilotCommandNative.RemoveAll(this);
		RunwayBreaker->OnPilotCommandNative.AddUObject(
			this,
			&ASkyguardMission06IntegrationDirector::HandlePilotCommand);
	}
	UpdateReadiness();
}

bool ASkyguardMission06IntegrationDirector::StartNextWave()
{
	if (!ResolvedMission ||
		WaveState != ESkyguardMission06WaveState::AwaitingWave)
	{
		return false;
	}
	const int32 Next = CurrentWaveIndex + 1;
	if (!ResolvedMission->Waves.IsValidIndex(Next))
	{
		return false;
	}
	const int32 Threats = CalculateWaveThreatCount(Next);
	if (Threats <= 0)
	{
		return false;
	}
	CurrentWaveIndex = Next;
	RemainingThreatsInWave = Threats;
	WaveState = ESkyguardMission06WaveState::WaveActive;
	return true;
}

bool ASkyguardMission06IntegrationDirector::NotifyThreatDestroyed(
	const int32 Amount)
{
	if (WaveState != ESkyguardMission06WaveState::WaveActive || Amount <= 0)
	{
		return false;
	}
	RemainingThreatsInWave =
		FMath::Max(0, RemainingThreatsInWave - Amount);
	if (RemainingThreatsInWave == 0)
	{
		const bool bLast =
			ResolvedMission &&
			CurrentWaveIndex == ResolvedMission->Waves.Num() - 1;
		WaveState = bLast
			? ESkyguardMission06WaveState::BossEngaged
			: ESkyguardMission06WaveState::AwaitingWave;
		if (bLast)
		{
			SynchronizeRuntimeState();
		}
	}
	return true;
}

bool ASkyguardMission06IntegrationDirector::StartPayloadWindow(
	const ESkyguardAirfieldTarget Target,
	const float WindowSeconds)
{
	if (WindowSeconds <= 0.f ||
		PayloadWindow.bActive ||
		(WaveState != ESkyguardMission06WaveState::WaveActive &&
			WaveState != ESkyguardMission06WaveState::BossEngaged) ||
		WaveState == ESkyguardMission06WaveState::Failed ||
		WaveState == ESkyguardMission06WaveState::Completed ||
		!FindTarget(Target) ||
		FindTarget(Target)->bDestroyed)
	{
		return false;
	}
	PayloadWindow.bActive = true;
	PayloadWindow.Target = Target;
	PayloadWindow.RemainingSeconds = WindowSeconds;
	PayloadWindow.bJammed = false;
	return true;
}

bool ASkyguardMission06IntegrationDirector::AdvancePayloadWindow(
	const float DeltaSeconds)
{
	if (!PayloadWindow.bActive || DeltaSeconds <= 0.f)
	{
		return false;
	}
	if (TryJamActivePayload())
	{
		return true;
	}
	PayloadWindow.RemainingSeconds =
		FMath::Max(0.f, PayloadWindow.RemainingSeconds - DeltaSeconds);
	if (PayloadWindow.RemainingSeconds <= KINDA_SMALL_NUMBER)
	{
		const ESkyguardAirfieldTarget ImpactTarget = PayloadWindow.Target;
		PayloadWindow.bActive = false;
		NotifyAirfieldTargetDamage(ImpactTarget, PayloadImpactDamage);
	}
	return true;
}

bool ASkyguardMission06IntegrationDirector::TryJamActivePayload()
{
	if (!PayloadWindow.bActive ||
		!IsPayloadJammedForTarget(PayloadWindow.Target))
	{
		return false;
	}
	PayloadWindow.bActive = false;
	PayloadWindow.bJammed = true;
	PayloadWindow.RemainingSeconds = 0.f;
	return true;
}

bool ASkyguardMission06IntegrationDirector::NotifyAirfieldTargetDamage(
	const ESkyguardAirfieldTarget Target,
	const int32 Damage)
{
	FSkyguardAirfieldTargetRuntime* Runtime = FindTarget(Target);
	if (!Runtime || Runtime->bDestroyed || Damage <= 0 ||
		WaveState == ESkyguardMission06WaveState::Completed)
	{
		return false;
	}
	Runtime->Integrity = FMath::Max(0, Runtime->Integrity - Damage);
	Runtime->bDestroyed = Runtime->Integrity == 0;
	if (GetSurvivingTargetCount() < 2)
	{
		static const FName ProtectObjective(TEXT("ProtectAirfieldAssets"));
		if (CampaignRuntime &&
			CampaignRuntime->GetActiveMission() == ResolvedMission)
		{
			CampaignRuntime->FailObjective(ProtectObjective);
		}
		else if (LocalObjectiveRuntime)
		{
			LocalObjectiveRuntime->FailObjective(ProtectObjective);
		}
		WaveState = ESkyguardMission06WaveState::Failed;

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
		PayloadWindow.bActive = false;
	}
	return true;
}

void ASkyguardMission06IntegrationDirector::SynchronizeRuntimeState()
{
	if (!RunwayBreaker || !ResolvedMission)
	{
		return;
	}
	const int32 RacksDestroyed = CountDestroyedPayloadRacks();
	const int32 NewRacks =
		FMath::Max(0, RacksDestroyed - ObservedPayloadRacksDestroyed);
	if (NewRacks > 0)
	{
		NotifyObjectiveProgress(TEXT("JamPayloadRacks"), NewRacks);
		ObservedPayloadRacksDestroyed = RacksDestroyed;
	}
	if (PayloadWindow.bActive)
	{
		TryJamActivePayload();
	}
	const int32 Destroyed =
		FMath::Clamp(
			RunwayBreaker->GetTelemetry().WeakPointsDestroyed, 0, 4);
	const int32 NewDestroyed =
		FMath::Max(0, Destroyed - ObservedBossWeakPointsDestroyed);
	if (NewDestroyed > 0)
	{
		NotifyObjectiveProgress(TEXT("DefeatRunwayBreaker"), NewDestroyed);
		ObservedBossWeakPointsDestroyed = Destroyed;
	}
	if (RunwayBreaker->GetBossPhase() == ESkyguardBossPhase::Defeated)
	{
		CompleteMissionIfReady();
	}
	UpdateReadiness();
}

bool ASkyguardMission06IntegrationDirector::NotifyObjectiveProgress(
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

int32 ASkyguardMission06IntegrationDirector::CalculateWaveThreatCount(
	const int32 WaveIndex) const
{
	if (!ResolvedMission || !ResolvedMission->Waves.IsValidIndex(WaveIndex))
	{
		return 0;
	}
	int32 Count = 0;
	for (const FSkyguardEnemyFormationDefinition& Formation :
		ResolvedMission->Waves[WaveIndex].Formations)
	{
		Count += FMath::Max(0, Formation.UnitCount);
	}
	return Count;
}

int32 ASkyguardMission06IntegrationDirector::CountDestroyedPayloadRacks() const
{
	if (!RunwayBreaker)
	{
		return 0;
	}
	return
		(RunwayBreaker->RunwayRack->bDestroyed ? 1 : 0) +
		(RunwayBreaker->HangarRack->bDestroyed ? 1 : 0);
}

bool ASkyguardMission06IntegrationDirector::IsPayloadJammedForTarget(
	const ESkyguardAirfieldTarget Target) const
{
	if (!RunwayBreaker)
	{
		return false;
	}
	switch (Target)
	{
	case ESkyguardAirfieldTarget::Runway:
		return RunwayBreaker->RunwayRack->bDestroyed;
	case ESkyguardAirfieldTarget::Hangars:
		return RunwayBreaker->HangarRack->bDestroyed;
	case ESkyguardAirfieldTarget::ParkedAircraft:
		return RunwayBreaker->HeatManifold->bDestroyed;
	default:
		return false;
	}
}

FSkyguardAirfieldTargetRuntime*
ASkyguardMission06IntegrationDirector::FindTarget(
	const ESkyguardAirfieldTarget Target)
{
	return ProtectedTargets.FindByPredicate(
		[Target](const FSkyguardAirfieldTargetRuntime& Candidate)
		{
			return Candidate.Target == Target;
		});
}

const FSkyguardAirfieldTargetRuntime*
ASkyguardMission06IntegrationDirector::FindTarget(
	const ESkyguardAirfieldTarget Target) const
{
	return ProtectedTargets.FindByPredicate(
		[Target](const FSkyguardAirfieldTargetRuntime& Candidate)
		{
			return Candidate.Target == Target;
		});
}

FSkyguardAirfieldTargetRuntime
ASkyguardMission06IntegrationDirector::GetTargetRuntime(
	const ESkyguardAirfieldTarget Target) const
{
	if (const FSkyguardAirfieldTargetRuntime* Runtime = FindTarget(Target))
	{
		return *Runtime;
	}
	return FSkyguardAirfieldTargetRuntime();
}

int32 ASkyguardMission06IntegrationDirector::GetSurvivingTargetCount() const
{
	int32 SurvivingTargetCount = 0;
	for (const FSkyguardAirfieldTargetRuntime& Runtime : ProtectedTargets)
	{
		if (!Runtime.bDestroyed && Runtime.Integrity > 0)
		{
			++SurvivingTargetCount;
		}
	}
	return SurvivingTargetCount;
}

void ASkyguardMission06IntegrationDirector::ConfigurePresentation()
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
		Line.LineId = FName(
			*FString::Printf(TEXT("M06_Briefing_%02d"), Index + 1));
		Line.Speaker = Index == 0
			? FText::FromString(TEXT("Airfield Control"))
			: FText::FromString(TEXT("Pilot"));
		Line.Subtitle = ResolvedMission->Presentation.RadioChatter[Index];
		Line.Priority = 90 - Index;
		Line.EstimatedDurationSeconds = 2.8f;
		Lines.Add(Line);
	}
	RadioChatter->PrimeLines(Lines);
	for (const FSkyguardRadioLine& Line : Lines)
	{
		RadioChatter->EnqueueLine(Line);
	}
}

void ASkyguardMission06IntegrationDirector::TryLaunchSortie()
{
	if (bSortieLaunched || !Briefing->CanLaunch())
	{
		return;
	}
	if (Briefing->GetBriefingState() ==
		ESkyguardMissionBriefingState::Launched)
	{
		bSortieLaunched = true;
		SortiePresentation->SetSortieLaunched();
	}
	else if (bAutoLaunchAfterBriefing &&
		Briefing->AcknowledgeAndLaunch())
	{
		bSortieLaunched = true;
		SortiePresentation->SetSortieLaunched();
	}
	if (bSortieLaunched &&
		WaveState == ESkyguardMission06WaveState::AwaitingWave)
	{
		StartNextWave();
	}
}

void ASkyguardMission06IntegrationDirector::CompleteMissionIfReady()
{
	if (bMissionCompleted ||
		WaveState != ESkyguardMission06WaveState::BossEngaged ||
		!RunwayBreaker ||
		RunwayBreaker->GetBossPhase() != ESkyguardBossPhase::Defeated ||
		GetSurvivingTargetCount() < 2)
	{
		return;
	}
	static const FName ProtectObjective(TEXT("ProtectAirfieldAssets"));
	USkyguardObjectiveRuntime* Objectives = GetObjectiveRuntime();
	if (Objectives &&
                Objectives->GetProgress(ProtectObjective).State ==
                ESkyguardMissionObjectiveState::Active)
        {
                if (CampaignRuntime &&
                        CampaignRuntime->GetActiveMission() == ResolvedMission)
                {
                        CampaignRuntime->CompleteSurviveObjectiveIfIntact(ProtectObjective);
                }
                else
                {
                        Objectives->CompleteSurviveObjectiveIfIntact(ProtectObjective);
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
		WaveState = ESkyguardMission06WaveState::Completed;
	}
}

void ASkyguardMission06IntegrationDirector::HandleBossPhaseChanged(
	ESkyguardBossPhase PreviousPhase,
	const ESkyguardBossPhase NewPhase)
{
	SynchronizeRuntimeState();
	if (NewPhase == ESkyguardBossPhase::Defeated && AudioDirector)
	{
		AudioDirector->TriggerEvent(
			ESkyguardAudioEvent::ExplosionHeavy,
			RunwayBreaker
				? RunwayBreaker->GetActorLocation()
				: GetActorLocation());
	}
}

void ASkyguardMission06IntegrationDirector::HandlePilotCommand(
	const ESkyguardPilotCommand Command)
{
	if (YakAircraft)
	{
		YakAircraft->IssuePilotCommand(Command);
	}
}

USkyguardObjectiveRuntime*
ASkyguardMission06IntegrationDirector::GetObjectiveRuntime() const
{
	if (CampaignRuntime &&
		CampaignRuntime->GetActiveMission() == ResolvedMission)
	{
		return CampaignRuntime->GetObjectiveRuntime();
	}
	return LocalObjectiveRuntime;
}

bool ASkyguardMission06IntegrationDirector::IsCorePlayableReady() const
{
	return Readiness.bMissionDefinitionValid &&
		Readiness.bCampaignDefinitionValid &&
		Readiness.bMapAssemblyReady &&
		Readiness.bYakRuntimeReady &&
		Readiness.bGunnerReady &&
		Readiness.bRunwayBreakerReady &&
		Readiness.bObjectivesReady &&
		Readiness.bWavesReady &&
		Readiness.bProtectedTargetsReady &&
		Readiness.bBriefingReady &&
		Readiness.bAudioReady &&
		Readiness.bSortiePresentationReady;
}

void ASkyguardMission06IntegrationDirector::UpdateReadiness()
{
	TArray<FText> Errors;
	Readiness.bMissionDefinitionValid =
		ValidateMissionContract(ResolvedMission, Errors);
	Readiness.bCampaignDefinitionValid =
		ResolvedCampaign &&
		ResolvedCampaign->FindMission(GetMissionId()) == ResolvedMission;
	TArray<FText> AssemblyErrors;
	Readiness.bMapAssemblyReady =
		MapAssembly &&
		MapAssembly->MissionId == GetMissionId() &&
		MapAssembly->SkylineStyle ==
			ESkyguardMissionSkylineStyle::AirfieldMilitary &&
		MapAssembly->ValidateAssembly(AssemblyErrors);
	Readiness.bYakRuntimeReady =
		YakAircraft && YakAircraft->GetRearGunnerMount() &&
		YakAircraft->GetRearEyeMount() &&
		YakAircraft->GetRearWeaponMount();
	Readiness.bGunnerReady =
		Gunner && YakAircraft &&
		Gunner->GetAttachParentActor() == YakAircraft;
	Readiness.bRunwayBreakerReady =
		RunwayBreaker &&
		RunwayBreaker->RunwayRack &&
		RunwayBreaker->HangarRack &&
		RunwayBreaker->HeatManifold &&
		RunwayBreaker->PortEngine &&
		RunwayBreaker->GetMaxDefeatDebrisPieces() <= 3;
	Readiness.bObjectivesReady =
		GetObjectiveRuntime() && ResolvedMission &&
		ResolvedMission->Objectives.Num() == 3;
	Readiness.bWavesReady =
		ResolvedMission && ResolvedMission->Waves.Num() == 3 &&
		CalculateWaveThreatCount(0) == 2 &&
		CalculateWaveThreatCount(1) == 3 &&
		CalculateWaveThreatCount(2) == 4;
	Readiness.bProtectedTargetsReady =
		ProtectedTargets.Num() == 3 &&
		FindTarget(ESkyguardAirfieldTarget::Runway) &&
		FindTarget(ESkyguardAirfieldTarget::Hangars) &&
		FindTarget(ESkyguardAirfieldTarget::ParkedAircraft);
	Readiness.bBriefingReady =
		Briefing &&
		Briefing->GetBriefingState() !=
			ESkyguardMissionBriefingState::Unconfigured;
	Readiness.bAudioReady = AudioDirector && RadioChatter;
	Readiness.bSortiePresentationReady =
		SortiePresentation && SortiePresentation->IsConfigured();
	Readiness.ObjectiveCount =
		ResolvedMission ? ResolvedMission->Objectives.Num() : 0;
	Readiness.WaveCount =
		ResolvedMission ? ResolvedMission->Waves.Num() : 0;
	Readiness.ProtectedTargetCount = ProtectedTargets.Num();
}

bool ASkyguardMission06IntegrationDirector::ValidateMissionContract(
	const USkyguardMissionDefinition* Mission,
	TArray<FText>& OutErrors)
{
	OutErrors.Reset();
	auto AddError = [&OutErrors](const FString& Message)
	{
		OutErrors.Add(FText::FromString(Message));
	};
	if (!Mission)
	{
		AddError(TEXT("Mission definition is missing."));
		return false;
	}
	if (Mission->MissionId != GetMissionId())
	{
		AddError(TEXT("Mission id must be M06_AirfieldDefense."));
	}
	if (Mission->Route.Points.Num() < 4)
	{
		AddError(TEXT("Mission 6 route requires at least four points."));
	}
	if (Mission->Objectives.Num() != 3)
	{
		AddError(TEXT("Mission 6 requires exactly three objectives."));
	}
	for (const FName RequiredObjective : {
		FName(TEXT("ProtectAirfieldAssets")),
		FName(TEXT("JamPayloadRacks")),
		FName(TEXT("DefeatRunwayBreaker"))})
	{
		if (!Mission->FindObjective(RequiredObjective))
		{
			AddError(FString::Printf(
				TEXT("Mission 6 is missing objective %s."),
				*RequiredObjective.ToString()));
		}
	}
	const TArray<FName> Ids = {
		FName(TEXT("RunwayRack")), FName(TEXT("HangarRack")),
		FName(TEXT("HeatManifold")), FName(TEXT("PortEngine"))};
	const TArray<FName> Weapons = {
		FName(TEXT("Rifle")), FName(TEXT("Rifle")),
		FName(TEXT("Rifle")), FName(TEXT("Igla"))};
	const TArray<FName> Exposes = {
		FName(TEXT("HeatManifold")), FName(TEXT("HeatManifold")),
		FName(TEXT("PortEngine")), NAME_None};
	if (Mission->Boss.BossId != TEXT("RunwayBreaker") ||
		Mission->Boss.DefeatObjectiveId != TEXT("DefeatRunwayBreaker") ||
		Mission->Boss.WeakPoints.Num() != 4 ||
		Mission->Boss.MaximumBreakupPieces > 3)
	{
		AddError(TEXT("Mission 6 payload-carrier boss contract is invalid."));
	}
	else
	{
		for (int32 Index = 0; Index < Ids.Num(); ++Index)
		{
			const FSkyguardBossWeakPointDefinition& Point =
				Mission->Boss.WeakPoints[Index];
			if (Point.WeakPointId != Ids[Index] ||
				Point.RequiredWeapon != Weapons[Index] ||
				Point.ExposesWeakPointId != Exposes[Index])
			{
				AddError(FString::Printf(
					TEXT("Runway Breaker graph differs at index %d."),
					Index));
			}
		}
	}
	if (Mission->Waves.Num() != 3)
	{
		AddError(TEXT("Mission 6 requires exactly three waves."));
	}
	if (Mission->Weather.ProfileId != TEXT("AirfieldHaze"))
	{
		AddError(TEXT("Mission 6 weather must be AirfieldHaze."));
	}
	if (Mission->Presentation.Briefing.IsEmpty() ||
		Mission->Presentation.RadioChatter.Num() < 3)
	{
		AddError(TEXT("Mission 6 briefing/radio contract is incomplete."));
	}
	return OutErrors.IsEmpty();
}
