#include "SkyguardMission07IntegrationDirector.h"

#include "SkyguardDrone.h"
#include "SkyguardAudioDirectorComponent.h"
#include "SkyguardCampaignDefinition.h"
#include "SkyguardCampaignSubsystem.h"
#include "SkyguardGunner.h"
#include "SkyguardMissionBriefingComponent.h"
#include "SkyguardMissionDefinition.h"
#include "SkyguardMissionDirectorCampaignHelpers.h"
#include "SkyguardMissionMapAssemblyDirector.h"
#include "SkyguardObjectiveRuntime.h"
#include "SkyguardRadarGhostBoss.h"
#include "SkyguardRadioChatterComponent.h"
#include "SkyguardSortiePresentationComponent.h"
#include "SkyguardYak52Aircraft.h"
#include "Components/SceneComponent.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "EngineUtils.h"

namespace
{
	template <typename T>
	T* FindFirstMission07Actor(UWorld* World)
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
	T* SpawnMission07Actor(
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

ASkyguardMission07IntegrationDirector::ASkyguardMission07IntegrationDirector()
{
	PrimaryActorTick.bCanEverTick = true;
	Root = CreateDefaultSubobject<USceneComponent>(
		TEXT("Mission07IntegrationRoot"));
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
			TEXT("/Game/Skyguard/Data/Campaign_v1/DA_Mission_M07_SearchIntercept.DA_Mission_M07_SearchIntercept")));
	Tags.AddUnique(TEXT("Skyguard.Mission07.PlayableIntegration"));
	Tags.AddUnique(TEXT("Skyguard.PackagePrep.Native"));
}

void ASkyguardMission07IntegrationDirector::BeginPlay()
{
	Super::BeginPlay();
	ASkyguardDrone::OnAnyCityImpacted.AddUObject(
		this,
		&ASkyguardMission07IntegrationDirector::HandleDroneCityImpact);
	if (bAutoInitialize)
	{
		InitializePlayableMission();
	}
}

void ASkyguardMission07IntegrationDirector::EndPlay(
	const EEndPlayReason::Type EndPlayReason)
{
	ASkyguardDrone::OnAnyCityImpacted.RemoveAll(this);
	if (RadarGhost)
	{
		RadarGhost->OnBossPhaseChanged.RemoveDynamic(
			this,
			&ASkyguardMission07IntegrationDirector::HandleBossPhaseChanged);
		RadarGhost->OnPilotCommandNative.RemoveAll(this);
	}
	Super::EndPlay(EndPlayReason);
}

void ASkyguardMission07IntegrationDirector::HandleDroneCityImpact(
	ASkyguardDrone* Drone)
{
	if (!Drone || !bInitialized || bMissionCompleted)
	{
		return;
	}
	NotifyProtectedAssetFailed();
}

bool ASkyguardMission07IntegrationDirector::NotifyProtectedAssetFailed()
{
	return NotifyProtectedTargetDamage(
		ESkyguardMission07ProtectedTarget::NavigationStation,
		FMath::Max(MaximumProtectedTargetIntegrity, 1));
}

void ASkyguardMission07IntegrationDirector::Tick(const float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	if (!bInitialized)
	{
		return;
	}
	Briefing->AdvanceBriefing(DeltaSeconds);
	TryLaunchSortie();
	if (WaveState == ESkyguardMission07WaveState::BossEngaged)
	{
		AdvanceReinforcementTimer(DeltaSeconds);
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

bool ASkyguardMission07IntegrationDirector::InitializePlayableMission()
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

bool ASkyguardMission07IntegrationDirector::ConfigureMissionDefinition(
	USkyguardMissionDefinition* Mission)
{
	TArray<FText> Errors;
	if (!ValidateMissionContract(Mission, Errors))
	{
		return false;
	}
	ResolvedMission = Mission;
	LocalObjectiveRuntime = NewObject<USkyguardObjectiveRuntime>(
		this, TEXT("Mission07LocalObjectives"));
	LocalObjectiveRuntime->InitializeObjectives(Mission->Objectives);
	WaveState = ESkyguardMission07WaveState::Searching;
	SearchSector = ESkyguardSearchSector::SectorA;
	CurrentWaveIndex = -1;
	RemainingThreatsInWave = 0;
	ObservedBossWeakPointsDestroyed = 0;
	ReinforcementTimeRemaining = ReinforcementDeadlineSeconds;
	bHostileContactConfirmed = false;
	bMissionCompleted = false;
	SearchTracks.Reset();
	const FName TrackIds[] = {
		FName(TEXT("FalseTrack_A")),
		FName(TEXT("FalseTrack_B")),
		FName(TEXT("FalseTrack_C"))};
	for (int32 Index = 0; Index < 3; ++Index)
	{
		FSkyguardSearchTrackRuntime Track;
		Track.TrackId = TrackIds[Index];
		Track.Sector = Index < 2
			? ESkyguardSearchSector::SectorA
			: ESkyguardSearchSector::SectorB;
		SearchTracks.Add(Track);
	}
	ProtectedTargets.Reset();
	for (const ESkyguardMission07ProtectedTarget Target : {
		ESkyguardMission07ProtectedTarget::NavigationStation,
		ESkyguardMission07ProtectedTarget::FishingFleet})
	{
		FSkyguardMission07ProtectedTargetRuntime Runtime;
		Runtime.Target = Target;
		Runtime.Integrity = MaximumProtectedTargetIntegrity;
		ProtectedTargets.Add(Runtime);
	}
	return true;
}

void ASkyguardMission07IntegrationDirector::ResolveOrSpawnActors()
{
	UWorld* World = GetWorld();
	MapAssembly =
		FindFirstMission07Actor<ASkyguardMissionMapAssemblyDirector>(World);
	YakAircraft = FindFirstMission07Actor<ASkyguardYak52Aircraft>(World);
	Gunner = FindFirstMission07Actor<ASkyguardGunner>(World);
	RadarGhost = FindFirstMission07Actor<ASkyguardRadarGhostBoss>(World);
	if (bAllowBoundedActorSpawning)
	{
		if (!YakAircraft)
		{
			YakAircraft = SpawnMission07Actor<ASkyguardYak52Aircraft>(
				World, YakSpawnLocation, YakSpawnRotation);
		}
		if (!Gunner)
		{
			Gunner = SpawnMission07Actor<ASkyguardGunner>(
				World, YakSpawnLocation, YakSpawnRotation);
		}
		if (!RadarGhost)
		{
			RadarGhost = SpawnMission07Actor<ASkyguardRadarGhostBoss>(
				World, RadarGhostSpawnLocation, RadarGhostSpawnRotation);
		}
	}
	BindRuntimeActors(MapAssembly, YakAircraft, Gunner, RadarGhost);
}

void ASkyguardMission07IntegrationDirector::BindRuntimeActors(
	ASkyguardMissionMapAssemblyDirector* InMapAssembly,
	ASkyguardYak52Aircraft* Aircraft,
	ASkyguardGunner* InGunner,
	ASkyguardRadarGhostBoss* InRadarGhost)
{
	if (RadarGhost && RadarGhost != InRadarGhost)
	{
		RadarGhost->OnBossPhaseChanged.RemoveDynamic(
			this,
			&ASkyguardMission07IntegrationDirector::HandleBossPhaseChanged);
		RadarGhost->OnPilotCommandNative.RemoveAll(this);
	}
	MapAssembly = InMapAssembly;
	YakAircraft = Aircraft;
	Gunner = InGunner;
	if (Gunner)
	{
		Gunner->ResetSortieCombatStats();
	}
	RadarGhost = InRadarGhost;
	ObservedBossWeakPointsDestroyed =
		RadarGhost ? RadarGhost->GetTelemetry().WeakPointsDestroyed : 0;
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
	if (RadarGhost)
	{
		RadarGhost->OnBossPhaseChanged.AddUniqueDynamic(
			this,
			&ASkyguardMission07IntegrationDirector::HandleBossPhaseChanged);
		RadarGhost->OnPilotCommandNative.RemoveAll(this);
		RadarGhost->OnPilotCommandNative.AddUObject(
			this,
			&ASkyguardMission07IntegrationDirector::HandlePilotCommand);
	}
	UpdateReadiness();
}

bool ASkyguardMission07IntegrationDirector::ClassifyFalseTrack(
	const FName TrackId)
{
	if (WaveState != ESkyguardMission07WaveState::Searching ||
		TrackId.IsNone())
	{
		return false;
	}
	FSkyguardSearchTrackRuntime* Track =
		SearchTracks.FindByPredicate(
			[TrackId](const FSkyguardSearchTrackRuntime& Candidate)
			{
				return Candidate.TrackId == TrackId;
			});
	if (!Track || Track->bClassifiedFalse ||
		Track->Sector != SearchSector)
	{
		return false;
	}
	Track->bClassifiedFalse = true;
	NotifyObjectiveProgress(TEXT("ClassifyFalseTracks"), 1);
	if (GetClassifiedFalseTrackCount() == 2)
	{
		SearchSector = ESkyguardSearchSector::SectorB;
	}
	return true;
}

bool ASkyguardMission07IntegrationDirector::ConfirmRadarGhostIdentification(
	const bool bExhaustObserved,
	const bool bShadowObserved,
	const bool bEngineSoundObserved)
{
	if (WaveState != ESkyguardMission07WaveState::Searching ||
		GetClassifiedFalseTrackCount() != 3 ||
		!bExhaustObserved || !bShadowObserved || !bEngineSoundObserved ||
		!RadarGhost)
	{
		return false;
	}
	bHostileContactConfirmed = true;
	SearchSector = ESkyguardSearchSector::Intercept;
	WaveState = ESkyguardMission07WaveState::AwaitingWave;
	RadarGhost->SetContactIdentified(true);
	return true;
}

bool ASkyguardMission07IntegrationDirector::StartNextWave()
{
	if (!ResolvedMission || !bHostileContactConfirmed ||
		WaveState != ESkyguardMission07WaveState::AwaitingWave)
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
	WaveState = ESkyguardMission07WaveState::WaveActive;
	return true;
}

bool ASkyguardMission07IntegrationDirector::NotifyThreatDestroyed(
	const int32 Amount)
{
	if (WaveState != ESkyguardMission07WaveState::WaveActive ||
		Amount <= 0)
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
			? ESkyguardMission07WaveState::BossEngaged
			: ESkyguardMission07WaveState::AwaitingWave;
		if (bLast)
		{
			ReinforcementTimeRemaining = ReinforcementDeadlineSeconds;
		}
	}
	return true;
}

bool ASkyguardMission07IntegrationDirector::NotifyProtectedTargetDamage(
	const ESkyguardMission07ProtectedTarget Target,
	const int32 Damage)
{
	FSkyguardMission07ProtectedTargetRuntime* Runtime =
		FindProtectedTarget(Target);
	if (!Runtime || Damage <= 0 || Runtime->bDestroyed ||
		WaveState == ESkyguardMission07WaveState::Completed)
	{
		return false;
	}
	Runtime->Integrity = FMath::Max(0, Runtime->Integrity - Damage);
	Runtime->bDestroyed = Runtime->Integrity == 0;
	if (Runtime->bDestroyed)
	{
		static const FName ProtectObjective(TEXT("ProtectRadarChain"));
		if (CampaignRuntime &&
			CampaignRuntime->GetActiveMission() == ResolvedMission)
		{
			CampaignRuntime->FailObjective(ProtectObjective);
		}
		else if (LocalObjectiveRuntime)
		{
			LocalObjectiveRuntime->FailObjective(ProtectObjective);
		}
		WaveState = ESkyguardMission07WaveState::Failed;

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

bool ASkyguardMission07IntegrationDirector::AdvanceReinforcementTimer(
	const float DeltaSeconds)
{
	if (WaveState != ESkyguardMission07WaveState::BossEngaged ||
		DeltaSeconds <= 0.f || !RadarGhost)
	{
		return false;
	}
	if (RadarGhost->GetBossPhase() == ESkyguardBossPhase::Defeated)
	{
		return true;
	}
	ReinforcementTimeRemaining =
		FMath::Max(0.f, ReinforcementTimeRemaining - DeltaSeconds);
	if (ReinforcementTimeRemaining <= 0.f)
	{
		NotifyProtectedTargetDamage(
			ESkyguardMission07ProtectedTarget::NavigationStation,
			MaximumProtectedTargetIntegrity);
	}
	return true;
}

void ASkyguardMission07IntegrationDirector::SynchronizeRuntimeState()
{
	if (!RadarGhost || !ResolvedMission)
	{
		return;
	}
	const int32 Destroyed = FMath::Clamp(
		RadarGhost->GetTelemetry().WeakPointsDestroyed, 0, 4);
	const int32 NewDestroyed =
		FMath::Max(0, Destroyed - ObservedBossWeakPointsDestroyed);
	if (NewDestroyed > 0)
	{
		NotifyObjectiveProgress(TEXT("DefeatRadarGhost"), NewDestroyed);
		ObservedBossWeakPointsDestroyed = Destroyed;
	}
	if (RadarGhost->GetBossPhase() == ESkyguardBossPhase::Defeated)
	{
		CompleteMissionIfReady();
	}
	UpdateReadiness();
}

bool ASkyguardMission07IntegrationDirector::NotifyObjectiveProgress(
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

int32 ASkyguardMission07IntegrationDirector::CalculateWaveThreatCount(
	const int32 WaveIndex) const
{
	if (!ResolvedMission ||
		!ResolvedMission->Waves.IsValidIndex(WaveIndex))
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

int32
ASkyguardMission07IntegrationDirector::GetClassifiedFalseTrackCount() const
{
	int32 ClassifiedCount = 0;
	for (const FSkyguardSearchTrackRuntime& Track : SearchTracks)
	{
		if (Track.bClassifiedFalse)
		{
			++ClassifiedCount;
		}
	}
	return ClassifiedCount;
}

FSkyguardMission07ProtectedTargetRuntime*
ASkyguardMission07IntegrationDirector::FindProtectedTarget(
	const ESkyguardMission07ProtectedTarget Target)
{
	return ProtectedTargets.FindByPredicate(
		[Target](const FSkyguardMission07ProtectedTargetRuntime& Runtime)
		{
			return Runtime.Target == Target;
		});
}

const FSkyguardMission07ProtectedTargetRuntime*
ASkyguardMission07IntegrationDirector::FindProtectedTarget(
	const ESkyguardMission07ProtectedTarget Target) const
{
	return ProtectedTargets.FindByPredicate(
		[Target](const FSkyguardMission07ProtectedTargetRuntime& Runtime)
		{
			return Runtime.Target == Target;
		});
}

FSkyguardMission07ProtectedTargetRuntime
ASkyguardMission07IntegrationDirector::GetProtectedTarget(
	const ESkyguardMission07ProtectedTarget Target) const
{
	const FSkyguardMission07ProtectedTargetRuntime* Runtime =
		FindProtectedTarget(Target);
	return Runtime
		? *Runtime
		: FSkyguardMission07ProtectedTargetRuntime();
}

int32 ASkyguardMission07IntegrationDirector::GetSurvivingTargetCount() const
{
	int32 Count = 0;
	for (const FSkyguardMission07ProtectedTargetRuntime& Runtime :
		ProtectedTargets)
	{
		if (!Runtime.bDestroyed && Runtime.Integrity > 0)
		{
			++Count;
		}
	}
	return Count;
}

void ASkyguardMission07IntegrationDirector::ConfigurePresentation()
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
	AudioDirector->SetEngineState(0.82f, 0.82f, 220.f, 1.f);
	RadioChatter->ClearQueue();
	TArray<FSkyguardRadioLine> Lines;
	for (int32 Index = 0;
		Index < ResolvedMission->Presentation.RadioChatter.Num();
		++Index)
	{
		FSkyguardRadioLine Line;
		Line.LineId = FName(
			*FString::Printf(TEXT("M07_Briefing_%02d"), Index + 1));
		Line.Speaker = Index == 0
			? FText::FromString(TEXT("Island Radar"))
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

void ASkyguardMission07IntegrationDirector::TryLaunchSortie()
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
}

void ASkyguardMission07IntegrationDirector::CompleteMissionIfReady()
{
	if (bMissionCompleted ||
		WaveState != ESkyguardMission07WaveState::BossEngaged ||
		GetSurvivingTargetCount() != 2 || !RadarGhost ||
		RadarGhost->GetBossPhase() != ESkyguardBossPhase::Defeated)
	{
		return;
	}
	static const FName ProtectObjective(TEXT("ProtectRadarChain"));
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
		WaveState = ESkyguardMission07WaveState::Completed;
	}
}

void ASkyguardMission07IntegrationDirector::HandleBossPhaseChanged(
	ESkyguardBossPhase PreviousPhase,
	const ESkyguardBossPhase NewPhase)
{
	SynchronizeRuntimeState();
	if (NewPhase == ESkyguardBossPhase::Defeated && AudioDirector)
	{
		AudioDirector->TriggerEvent(
			ESkyguardAudioEvent::ExplosionHeavy,
			RadarGhost
				? RadarGhost->GetActorLocation()
				: GetActorLocation());
	}
}

void ASkyguardMission07IntegrationDirector::HandlePilotCommand(
	const ESkyguardPilotCommand Command)
{
	if (YakAircraft)
	{
		YakAircraft->IssuePilotCommand(Command);
	}
}

USkyguardObjectiveRuntime*
ASkyguardMission07IntegrationDirector::GetObjectiveRuntime() const
{
	if (CampaignRuntime &&
		CampaignRuntime->GetActiveMission() == ResolvedMission)
	{
		return CampaignRuntime->GetObjectiveRuntime();
	}
	return LocalObjectiveRuntime;
}

bool ASkyguardMission07IntegrationDirector::IsCorePlayableReady() const
{
	return Readiness.bMissionDefinitionValid &&
		Readiness.bCampaignDefinitionValid &&
		Readiness.bMapAssemblyReady &&
		Readiness.bYakRuntimeReady &&
		Readiness.bGunnerReady &&
		Readiness.bRadarGhostReady &&
		Readiness.bObjectivesReady &&
		Readiness.bWavesReady &&
		Readiness.bSearchRuntimeReady &&
		Readiness.bProtectedTargetsReady &&
		Readiness.bBriefingReady &&
		Readiness.bAudioReady &&
		Readiness.bSortiePresentationReady;
}

void ASkyguardMission07IntegrationDirector::UpdateReadiness()
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
			ESkyguardMissionSkylineStyle::IslandSearch &&
		MapAssembly->ValidateAssembly(AssemblyErrors);
	Readiness.bYakRuntimeReady =
		YakAircraft && YakAircraft->GetRearGunnerMount() &&
		YakAircraft->GetRearEyeMount() &&
		YakAircraft->GetRearWeaponMount();
	Readiness.bGunnerReady =
		Gunner && YakAircraft &&
		Gunner->GetAttachParentActor() == YakAircraft;
	Readiness.bRadarGhostReady =
		RadarGhost && RadarGhost->SignatureModulator &&
		RadarGhost->RadarReceiver && RadarGhost->CoolingDoor &&
		RadarGhost->Engine &&
		RadarGhost->GetMaxDefeatDebrisPieces() <= 3;
	Readiness.bObjectivesReady =
		GetObjectiveRuntime() && ResolvedMission &&
		ResolvedMission->Objectives.Num() == 3;
	Readiness.bWavesReady =
		ResolvedMission && ResolvedMission->Waves.Num() == 3 &&
		CalculateWaveThreatCount(0) == 2 &&
		CalculateWaveThreatCount(1) == 3 &&
		CalculateWaveThreatCount(2) == 4;
	Readiness.bSearchRuntimeReady =
		SearchTracks.Num() == 3 &&
		ReinforcementDeadlineSeconds > 0.f;
	Readiness.bProtectedTargetsReady =
		ProtectedTargets.Num() == 2 &&
		FindProtectedTarget(
			ESkyguardMission07ProtectedTarget::NavigationStation) &&
		FindProtectedTarget(
			ESkyguardMission07ProtectedTarget::FishingFleet);
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
	Readiness.SearchTrackCount = SearchTracks.Num();
}

bool ASkyguardMission07IntegrationDirector::ValidateMissionContract(
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
		AddError(TEXT("Mission id must be M07_SearchIntercept."));
	}
	if (Mission->Route.Points.Num() < 4)
	{
		AddError(TEXT("Mission 7 route requires at least four island points."));
	}
	if (Mission->Objectives.Num() != 3)
	{
		AddError(TEXT("Mission 7 requires exactly three objectives."));
	}
	for (const FName RequiredObjective : {
		FName(TEXT("ProtectRadarChain")),
		FName(TEXT("ClassifyFalseTracks")),
		FName(TEXT("DefeatRadarGhost"))})
	{
		if (!Mission->FindObjective(RequiredObjective))
		{
			AddError(FString::Printf(
				TEXT("Mission 7 is missing objective %s."),
				*RequiredObjective.ToString()));
		}
	}
	const FSkyguardObjectiveDefinition* Protect =
		Mission->FindObjective(TEXT("ProtectRadarChain"));
	const FSkyguardObjectiveDefinition* Classify =
		Mission->FindObjective(TEXT("ClassifyFalseTracks"));
	const FSkyguardObjectiveDefinition* Defeat =
		Mission->FindObjective(TEXT("DefeatRadarGhost"));
	if ((Protect && Protect->RequiredProgress != 1) ||
		(Classify && Classify->RequiredProgress != 3) ||
		(Defeat && Defeat->RequiredProgress != 4))
	{
		AddError(TEXT(
			"Mission 7 objective progress must be protect=1, "
			"classify=3 and boss=4."));
	}
	const TArray<FName> Ids = {
		FName(TEXT("SignatureModulator")),
		FName(TEXT("RadarReceiver")),
		FName(TEXT("CoolingDoor")),
		FName(TEXT("Engine"))};
	const TArray<FName> Weapons = {
		FName(TEXT("Rifle")), FName(TEXT("Rifle")),
		FName(TEXT("Rifle")), FName(TEXT("Igla"))};
	const TArray<FName> Exposes = {
		FName(TEXT("RadarReceiver")), FName(TEXT("CoolingDoor")),
		FName(TEXT("Engine")), NAME_None};
	if (Mission->Boss.BossId != TEXT("RadarGhost") ||
		Mission->Boss.DefeatObjectiveId != TEXT("DefeatRadarGhost") ||
		Mission->Boss.WeakPoints.Num() != 4 ||
		Mission->Boss.MaximumBreakupPieces > 3)
	{
		AddError(TEXT("Mission 7 Radar Ghost boss contract is invalid."));
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
					TEXT("Radar Ghost graph differs at index %d."),
					Index));
			}
		}
	}
	if (Mission->Waves.Num() != 3)
	{
		AddError(TEXT("Mission 7 requires exactly three waves."));
	}
	if (Mission->Weather.ProfileId != TEXT("IslandMist"))
	{
		AddError(TEXT("Mission 7 weather must be IslandMist."));
	}
	if (Mission->Presentation.Briefing.IsEmpty() ||
		Mission->Presentation.RadioChatter.Num() < 3)
	{
		AddError(TEXT("Mission 7 briefing/radio contract is incomplete."));
	}
	return OutErrors.IsEmpty();
}
