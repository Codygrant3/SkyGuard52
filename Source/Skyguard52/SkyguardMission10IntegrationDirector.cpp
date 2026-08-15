#include "SkyguardMission10IntegrationDirector.h"

#include "SkyguardDrone.h"
#include "SkyguardAudioDirectorComponent.h"
#include "SkyguardCampaignDefinition.h"
#include "SkyguardCampaignSubsystem.h"
#include "SkyguardGunner.h"
#include "SkyguardLastFlightBoss.h"
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
	T* FindFirstMission10Actor(UWorld* World)
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
	T* SpawnMission10Actor(
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

ASkyguardMission10IntegrationDirector::ASkyguardMission10IntegrationDirector()
{
	PrimaryActorTick.bCanEverTick = true;
	Root = CreateDefaultSubobject<USceneComponent>(
		TEXT("Mission10IntegrationRoot"));
	SetRootComponent(Root);
	HighwayConvoyAnchor = CreateDefaultSubobject<USceneComponent>(
		TEXT("HighwayConvoyAnchor"));
	HighwayConvoyAnchor->SetupAttachment(Root);
	BusAAnchor = CreateDefaultSubobject<USceneComponent>(TEXT("BusAAnchor"));
	BusAAnchor->SetupAttachment(HighwayConvoyAnchor);
	BusBAnchor = CreateDefaultSubobject<USceneComponent>(TEXT("BusBAnchor"));
	BusBAnchor->SetupAttachment(HighwayConvoyAnchor);
	AmbulanceAAnchor = CreateDefaultSubobject<USceneComponent>(
		TEXT("AmbulanceAAnchor"));
	AmbulanceAAnchor->SetupAttachment(HighwayConvoyAnchor);
	AmbulanceBAnchor = CreateDefaultSubobject<USceneComponent>(
		TEXT("AmbulanceBAnchor"));
	AmbulanceBAnchor->SetupAttachment(HighwayConvoyAnchor);
	FerryTerminalAnchor = CreateDefaultSubobject<USceneComponent>(
		TEXT("FerryTerminalAnchor"));
	FerryTerminalAnchor->SetupAttachment(Root);
	EvacuationShipAnchor = CreateDefaultSubobject<USceneComponent>(
		TEXT("EvacuationShipAnchor"));
	EvacuationShipAnchor->SetupAttachment(Root);
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
			TEXT("/Game/Skyguard/Data/Campaign_v1/DA_Mission_M10_EvacuationFinale.DA_Mission_M10_EvacuationFinale")));
	Tags.AddUnique(TEXT("Skyguard.Mission10.PlayableIntegration"));
	Tags.AddUnique(TEXT("Skyguard.PackagePrep.Native"));
}

void ASkyguardMission10IntegrationDirector::BeginPlay()
{
	Super::BeginPlay();
	ASkyguardDrone::OnAnyCityImpacted.AddUObject(
		this,
		&ASkyguardMission10IntegrationDirector::HandleDroneCityImpact);
	if (bAutoInitialize)
	{
		InitializePlayableMission();
	}
}

void ASkyguardMission10IntegrationDirector::EndPlay(
	const EEndPlayReason::Type EndPlayReason)
{
	ASkyguardDrone::OnAnyCityImpacted.RemoveAll(this);
	if (LastFlight)
	{
		LastFlight->OnBossPhaseChanged.RemoveDynamic(
			this,
			&ASkyguardMission10IntegrationDirector::HandleBossPhaseChanged);
		LastFlight->OnPilotCommandNative.RemoveAll(this);
	}
	Super::EndPlay(EndPlayReason);
}

void ASkyguardMission10IntegrationDirector::HandleDroneCityImpact(
	ASkyguardDrone* Drone)
{
	if (!Drone || !bInitialized || bMissionCompleted)
	{
		return;
	}
	NotifyProtectedAssetFailed();
}

bool ASkyguardMission10IntegrationDirector::NotifyProtectedAssetFailed()
{
	return NotifyProtectedGroupDamage(
		ESkyguardMission10ProtectedGroup::Convoy,
		FMath::Max(MaximumProtectedIntegrity, 1));
}

void ASkyguardMission10IntegrationDirector::Tick(
	const float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	if (!bInitialized)
	{
		return;
	}
	Briefing->AdvanceBriefing(DeltaSeconds);
	TryLaunchSortie();
	UpdateEvacuationAnimation(DeltaSeconds);
	if (bSortieLaunched)
	{
		SynchronizeRuntimeState();
	}
	if (YakAircraft && AudioDirector)
	{
		AudioDirector->SetEngineState(
			FMath::Clamp(YakAircraft->GetPropellerRPM() / 2800.f, 0.f, 1.f),
			0.86f, 235.f, 1.f);
	}
}

bool ASkyguardMission10IntegrationDirector::InitializePlayableMission()
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

bool ASkyguardMission10IntegrationDirector::ConfigureMissionDefinition(
	USkyguardMissionDefinition* Mission)
{
	TArray<FText> Errors;
	if (!ValidateMissionContract(Mission, Errors))
	{
		return false;
	}
	ResolvedMission = Mission;
	LocalObjectiveRuntime = NewObject<USkyguardObjectiveRuntime>(
		this, TEXT("Mission10LocalObjectives"));
	LocalObjectiveRuntime->InitializeObjectives(Mission->Objectives);
	RoutePhase = ESkyguardMission10RoutePhase::Highway;
	CurrentWaveIndex = -1;
	RemainingThreatsInWave = 0;
	ObservedBossMilestones = 0;
	RejectedWeaponReleases = 0;
	EvacuationAnimationSeconds = 0.f;
	ProtectedGroups.Reset();
	for (const ESkyguardMission10ProtectedGroup Group : {
		ESkyguardMission10ProtectedGroup::Convoy,
		ESkyguardMission10ProtectedGroup::FerryTerminal,
		ESkyguardMission10ProtectedGroup::EvacuationShip})
	{
		FSkyguardMission10ProtectedRuntime Runtime;
		Runtime.Group = Group;
		Runtime.Integrity = MaximumProtectedIntegrity;
		ProtectedGroups.Add(Runtime);
	}
	bMissionCompleted = false;
	return true;
}

void ASkyguardMission10IntegrationDirector::ResolveOrSpawnActors()
{
	UWorld* World = GetWorld();
	MapAssembly =
		FindFirstMission10Actor<ASkyguardMissionMapAssemblyDirector>(World);
	YakAircraft = FindFirstMission10Actor<ASkyguardYak52Aircraft>(World);
	Gunner = FindFirstMission10Actor<ASkyguardGunner>(World);
	LastFlight = FindFirstMission10Actor<ASkyguardLastFlightBoss>(World);
	if (bAllowBoundedActorSpawning)
	{
		if (!YakAircraft)
		{
			YakAircraft = SpawnMission10Actor<ASkyguardYak52Aircraft>(
				World, YakSpawnLocation, YakSpawnRotation);
		}
		if (!Gunner)
		{
			Gunner = SpawnMission10Actor<ASkyguardGunner>(
				World, YakSpawnLocation, YakSpawnRotation);
		}
		if (!LastFlight)
		{
			LastFlight = SpawnMission10Actor<ASkyguardLastFlightBoss>(
				World, LastFlightSpawnLocation, LastFlightSpawnRotation);
		}
	}
	BindRuntimeActors(MapAssembly, YakAircraft, Gunner, LastFlight);
}

void ASkyguardMission10IntegrationDirector::BindRuntimeActors(
	ASkyguardMissionMapAssemblyDirector* InMapAssembly,
	ASkyguardYak52Aircraft* Aircraft,
	ASkyguardGunner* InGunner,
	ASkyguardLastFlightBoss* InLastFlight)
{
	if (LastFlight && LastFlight != InLastFlight)
	{
		LastFlight->OnBossPhaseChanged.RemoveDynamic(
			this,
			&ASkyguardMission10IntegrationDirector::HandleBossPhaseChanged);
		LastFlight->OnPilotCommandNative.RemoveAll(this);
	}
	MapAssembly = InMapAssembly;
	YakAircraft = Aircraft;
	Gunner = InGunner;
	if (Gunner)
	{
		Gunner->ResetSortieCombatStats();
	}
	LastFlight = InLastFlight;
	ObservedBossMilestones =
		LastFlight ? LastFlight->GetObjectiveMilestonesReached() : 0;
	if (YakAircraft)
	{
		YakAircraft->SetEnginePower(0.86f);
		YakAircraft->SetRearCanopyOpen(true);
	}
	FSkyguardPlayerAircraft::AttachGunner(Gunner, YakAircraft);
	if (LastFlight)
	{
		LastFlight->OnBossPhaseChanged.AddUniqueDynamic(
			this,
			&ASkyguardMission10IntegrationDirector::HandleBossPhaseChanged);
		LastFlight->OnPilotCommandNative.RemoveAll(this);
		LastFlight->OnPilotCommandNative.AddUObject(
			this,
			&ASkyguardMission10IntegrationDirector::HandlePilotCommand);
	}
	UpdateReadiness();
}

bool ASkyguardMission10IntegrationDirector::StartPhaseWave()
{
	if (!ResolvedMission ||
		RoutePhase == ESkyguardMission10RoutePhase::Briefing ||
		RoutePhase == ESkyguardMission10RoutePhase::BossEngaged ||
		RoutePhase == ESkyguardMission10RoutePhase::Completed ||
		RoutePhase == ESkyguardMission10RoutePhase::Failed ||
		RemainingThreatsInWave > 0)
	{
		return false;
	}
	const int32 NextWave = CurrentWaveIndex + 1;
	if (!ResolvedMission->Waves.IsValidIndex(NextWave))
	{
		return false;
	}
	const int32 Threats = CalculateWaveThreatCount(NextWave);
	if (Threats <= 0)
	{
		return false;
	}
	CurrentWaveIndex = NextWave;
	RemainingThreatsInWave = Threats;
	return true;
}

bool ASkyguardMission10IntegrationDirector::NotifyThreatDestroyed(
	const int32 Amount)
{
	if (RemainingThreatsInWave <= 0 || Amount <= 0 ||
		RoutePhase == ESkyguardMission10RoutePhase::Failed)
	{
		return false;
	}
	RemainingThreatsInWave =
		FMath::Max(0, RemainingThreatsInWave - Amount);
	if (RemainingThreatsInWave == 0)
	{
		NotifyObjectiveProgress(TEXT("ClearEvacuationLanes"), 1);
		if (CurrentWaveIndex == 0)
		{
			RoutePhase = ESkyguardMission10RoutePhase::FerryTerminal;
		}
		else if (CurrentWaveIndex == 1)
		{
			RoutePhase = ESkyguardMission10RoutePhase::EvacuationShip;
		}
		else
		{
			RoutePhase = ESkyguardMission10RoutePhase::BossEngaged;
		}
	}
	return true;
}

bool ASkyguardMission10IntegrationDirector::ValidateWeaponRelease(
	const float CivilianSeparationMeters,
	const bool bShotIntersectsCivilianCorridor)
{
	const bool bSafe =
		!bShotIntersectsCivilianCorridor &&
		CivilianSeparationMeters >= MinimumWeaponSeparationMeters;
	if (!bSafe)
	{
		++RejectedWeaponReleases;
		return false;
	}
	if (LastFlight)
	{
		LastFlight->SetCivilianSeparationMeters(
			CivilianSeparationMeters);
	}
	return true;
}

bool ASkyguardMission10IntegrationDirector::NotifyProtectedGroupDamage(
	const ESkyguardMission10ProtectedGroup Group,
	const int32 Damage)
{
	FSkyguardMission10ProtectedRuntime* Runtime =
		FindProtectedGroup(Group);
	if (!Runtime || Damage <= 0 || Runtime->bDestroyed ||
		RoutePhase == ESkyguardMission10RoutePhase::Completed)
	{
		return false;
	}
	Runtime->Integrity = FMath::Max(0, Runtime->Integrity - Damage);
	Runtime->bDestroyed = Runtime->Integrity == 0;
	if (Runtime->bDestroyed)
	{
		static const FName ProtectObjective(TEXT("ProtectEvacuationHub"));
		if (CampaignRuntime &&
			CampaignRuntime->GetActiveMission() == ResolvedMission)
		{
			CampaignRuntime->FailObjective(ProtectObjective);
		}
		else if (LocalObjectiveRuntime)
		{
			LocalObjectiveRuntime->FailObjective(ProtectObjective);
		}
		RoutePhase = ESkyguardMission10RoutePhase::Failed;

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

void ASkyguardMission10IntegrationDirector::SynchronizeRuntimeState()
{
	if (!LastFlight || !ResolvedMission)
	{
		return;
	}
	const int32 Milestones =
		FMath::Clamp(LastFlight->GetObjectiveMilestonesReached(), 0, 4);
	const int32 NewMilestones =
		FMath::Max(0, Milestones - ObservedBossMilestones);
	if (NewMilestones > 0)
	{
		NotifyObjectiveProgress(TEXT("DefeatLastFlight"), NewMilestones);
		ObservedBossMilestones = Milestones;
	}
	if (LastFlight->GetBossPhase() == ESkyguardBossPhase::Defeated &&
		LastFlight->IsWreckDiverted())
	{
		USkyguardObjectiveRuntime* Objectives = GetObjectiveRuntime();
		if (Objectives &&
                Objectives->GetProgress(TEXT("ClearEvacuationLanes")).State ==
                ESkyguardMissionObjectiveState::Active)
        {
                if (CampaignRuntime &&
                        CampaignRuntime->GetActiveMission() == ResolvedMission)
                {
                        CampaignRuntime->CompleteSurviveObjectiveIfIntact(TEXT("ClearEvacuationLanes"));
                }
                else
                {
                        Objectives->CompleteSurviveObjectiveIfIntact(TEXT("ClearEvacuationLanes"));
                }
        }
		CompleteMissionIfReady();
	}
	UpdateReadiness();
}

bool ASkyguardMission10IntegrationDirector::NotifyObjectiveProgress(
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

int32 ASkyguardMission10IntegrationDirector::CalculateWaveThreatCount(
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

FSkyguardMission10ProtectedRuntime*
ASkyguardMission10IntegrationDirector::FindProtectedGroup(
	const ESkyguardMission10ProtectedGroup Group)
{
	return ProtectedGroups.FindByPredicate(
		[Group](const FSkyguardMission10ProtectedRuntime& Runtime)
		{
			return Runtime.Group == Group;
		});
}

const FSkyguardMission10ProtectedRuntime*
ASkyguardMission10IntegrationDirector::FindProtectedGroup(
	const ESkyguardMission10ProtectedGroup Group) const
{
	return ProtectedGroups.FindByPredicate(
		[Group](const FSkyguardMission10ProtectedRuntime& Runtime)
		{
			return Runtime.Group == Group;
		});
}

FSkyguardMission10ProtectedRuntime
ASkyguardMission10IntegrationDirector::GetProtectedGroup(
	const ESkyguardMission10ProtectedGroup Group) const
{
	const FSkyguardMission10ProtectedRuntime* Runtime =
		FindProtectedGroup(Group);
	return Runtime
		? *Runtime
		: FSkyguardMission10ProtectedRuntime();
}

int32 ASkyguardMission10IntegrationDirector::
	GetSurvivingProtectedGroupCount() const
{
	int32 Count = 0;
	for (const FSkyguardMission10ProtectedRuntime& Runtime :
		ProtectedGroups)
	{
		if (!Runtime.bDestroyed && Runtime.Integrity > 0)
		{
			++Count;
		}
	}
	return Count;
}

void ASkyguardMission10IntegrationDirector::UpdateEvacuationAnimation(
	const float DeltaSeconds)
{
	if (DeltaSeconds <= 0.f)
	{
		return;
	}
	EvacuationAnimationSeconds += DeltaSeconds;
	const float HighwayTravel =
		FMath::Fmod(EvacuationAnimationSeconds * 420.f, 18000.f);
	HighwayConvoyAnchor->SetRelativeLocation(
		FVector(8000.f + HighwayTravel, 50000.f, 100.f));
	BusAAnchor->SetRelativeLocation(FVector(0.f, 0.f, 0.f));
	BusBAnchor->SetRelativeLocation(FVector(-900.f, 120.f, 0.f));
	AmbulanceAAnchor->SetRelativeLocation(FVector(-1750.f, -100.f, 0.f));
	AmbulanceBAnchor->SetRelativeLocation(FVector(-2450.f, 80.f, 0.f));
	FerryTerminalAnchor->SetRelativeLocation(
		FVector(55000.f, 28000.f, 100.f));
	EvacuationShipAnchor->SetRelativeLocation(
		FVector(
			47000.f + FMath::Sin(EvacuationAnimationSeconds * 0.08f) * 350.f,
			5000.f,
			-50.f + FMath::Sin(EvacuationAnimationSeconds * 0.7f) * 22.f));
}

void ASkyguardMission10IntegrationDirector::ConfigurePresentation()
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
	AudioDirector->SetEngineState(0.86f, 0.86f, 235.f, 1.f);
	RadioChatter->ClearQueue();
	TArray<FSkyguardRadioLine> Lines;
	for (int32 Index = 0;
		Index < ResolvedMission->Presentation.RadioChatter.Num();
		++Index)
	{
		FSkyguardRadioLine Line;
		Line.LineId = FName(
			*FString::Printf(TEXT("M10_Briefing_%02d"), Index + 1));
		Line.Speaker = Index == 0
			? FText::FromString(TEXT("Evacuation Control"))
			: FText::FromString(TEXT("Pilot"));
		Line.Subtitle = ResolvedMission->Presentation.RadioChatter[Index];
		Line.Priority = 100 - Index;
		Line.EstimatedDurationSeconds = 3.f;
		Lines.Add(Line);
	}
	RadioChatter->PrimeLines(Lines);
	for (const FSkyguardRadioLine& Line : Lines)
	{
		RadioChatter->EnqueueLine(Line);
	}
	SkyguardMissionDirectorPresentationHelpers::BindHudHostToPresentation(
		this,
		SortiePresentation);
}

void ASkyguardMission10IntegrationDirector::TryLaunchSortie()
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
		RoutePhase == ESkyguardMission10RoutePhase::Highway)
	{
		StartPhaseWave();
	}
}

void ASkyguardMission10IntegrationDirector::CompleteMissionIfReady()
{
	if (bMissionCompleted ||
		RoutePhase != ESkyguardMission10RoutePhase::BossEngaged ||
		GetSurvivingProtectedGroupCount() != 3 || !LastFlight ||
		LastFlight->GetBossPhase() != ESkyguardBossPhase::Defeated ||
		!LastFlight->IsWreckDiverted())
	{
		return;
	}
	static const FName ProtectObjective(TEXT("ProtectEvacuationHub"));
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
		RoutePhase = ESkyguardMission10RoutePhase::Completed;
	}
}

void ASkyguardMission10IntegrationDirector::HandleBossPhaseChanged(
	ESkyguardBossPhase PreviousPhase,
	const ESkyguardBossPhase NewPhase)
{
	SynchronizeRuntimeState();
	if (NewPhase == ESkyguardBossPhase::Defeated && AudioDirector)
	{
		AudioDirector->TriggerEvent(
			ESkyguardAudioEvent::ExplosionHeavy,
			LastFlight
				? LastFlight->GetActorLocation()
				: GetActorLocation());
	}
}

void ASkyguardMission10IntegrationDirector::HandlePilotCommand(
	const ESkyguardPilotCommand Command)
{
	if (YakAircraft)
	{
		YakAircraft->IssuePilotCommand(Command);
	}
}

USkyguardObjectiveRuntime*
ASkyguardMission10IntegrationDirector::GetObjectiveRuntime() const
{
	if (CampaignRuntime &&
		CampaignRuntime->GetActiveMission() == ResolvedMission)
	{
		return CampaignRuntime->GetObjectiveRuntime();
	}
	return LocalObjectiveRuntime;
}

bool ASkyguardMission10IntegrationDirector::IsCorePlayableReady() const
{
	return Readiness.bMissionDefinitionValid &&
		Readiness.bCampaignDefinitionValid &&
		Readiness.bMapAssemblyReady &&
		Readiness.bYakRuntimeReady &&
		Readiness.bGunnerReady &&
		Readiness.bLastFlightReady &&
		Readiness.bObjectivesReady &&
		Readiness.bPhaseWavesReady &&
		Readiness.bEvacuationPresentationReady &&
		Readiness.bProtectedGroupsReady &&
		Readiness.bBriefingReady &&
		Readiness.bAudioReady &&
		Readiness.bSortiePresentationReady;
}

void ASkyguardMission10IntegrationDirector::UpdateReadiness()
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
			ESkyguardMissionSkylineStyle::HarborIndustrial &&
		MapAssembly->ValidateAssembly(AssemblyErrors);
	Readiness.bYakRuntimeReady =
		YakAircraft && YakAircraft->GetRearGunnerMount() &&
		YakAircraft->GetRearEyeMount() &&
		YakAircraft->GetRearWeaponMount();
	Readiness.bGunnerReady =
		Gunner && YakAircraft &&
		Gunner->GetAttachParentActor() == YakAircraft;
	Readiness.bLastFlightReady =
		LastFlight && LastFlight->PortGuidanceArray &&
		LastFlight->StarboardGuidanceArray &&
		LastFlight->PortStrikeBayMechanism &&
		LastFlight->StarboardStrikeBayMechanism &&
		LastFlight->PortCoolingSystem &&
		LastFlight->StarboardCoolingSystem &&
		LastFlight->Jammer &&
		LastFlight->PortEngine &&
		LastFlight->StarboardEngine &&
		LastFlight->CommandCore &&
		LastFlight->GetMaxDefeatDebrisPieces() <= 6;
	Readiness.bObjectivesReady =
		GetObjectiveRuntime() && ResolvedMission &&
		ResolvedMission->Objectives.Num() == 3;
	Readiness.bPhaseWavesReady =
		ResolvedMission && ResolvedMission->Waves.Num() == 3 &&
		CalculateWaveThreatCount(0) == 3 &&
		CalculateWaveThreatCount(1) == 4 &&
		CalculateWaveThreatCount(2) == 5;
	Readiness.bEvacuationPresentationReady =
		HighwayConvoyAnchor && BusAAnchor && BusBAnchor &&
		AmbulanceAAnchor && AmbulanceBAnchor &&
		FerryTerminalAnchor && EvacuationShipAnchor;
	Readiness.bProtectedGroupsReady =
		ProtectedGroups.Num() == 3 &&
		FindProtectedGroup(ESkyguardMission10ProtectedGroup::Convoy) &&
		FindProtectedGroup(
			ESkyguardMission10ProtectedGroup::FerryTerminal) &&
		FindProtectedGroup(
			ESkyguardMission10ProtectedGroup::EvacuationShip);
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
	Readiness.ProtectedGroupCount = ProtectedGroups.Num();
}

bool ASkyguardMission10IntegrationDirector::ValidateMissionContract(
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
		AddError(TEXT("Mission id must be M10_EvacuationFinale."));
	}
	if (Mission->Route.Points.Num() != 4)
	{
		AddError(TEXT("Mission 10 requires the governed four-point route."));
	}
	if (Mission->Objectives.Num() != 3)
	{
		AddError(TEXT("Mission 10 requires exactly three objectives."));
	}
	for (const FName RequiredObjective : {
		FName(TEXT("ProtectEvacuationHub")),
		FName(TEXT("ClearEvacuationLanes")),
		FName(TEXT("DefeatLastFlight"))})
	{
		if (!Mission->FindObjective(RequiredObjective))
		{
			AddError(FString::Printf(
				TEXT("Mission 10 is missing objective %s."),
				*RequiredObjective.ToString()));
		}
	}
	const FSkyguardObjectiveDefinition* Protect =
		Mission->FindObjective(TEXT("ProtectEvacuationHub"));
	const FSkyguardObjectiveDefinition* Lanes =
		Mission->FindObjective(TEXT("ClearEvacuationLanes"));
	const FSkyguardObjectiveDefinition* Defeat =
		Mission->FindObjective(TEXT("DefeatLastFlight"));
	if ((Protect && Protect->RequiredProgress != 1) ||
		(Lanes && Lanes->RequiredProgress != 4) ||
		(Defeat && Defeat->RequiredProgress != 4))
	{
		AddError(TEXT(
			"Mission 10 objective progress must be protect=1, "
			"lanes=4 and boss=4."));
	}
	const TArray<FName> Ids = {
		FName(TEXT("JammerArray")),
		FName(TEXT("PayloadController")),
		FName(TEXT("ArmorSeam")),
		FName(TEXT("TwinEngineCore"))};
	const TArray<FName> Weapons = {
		FName(TEXT("Rifle")), FName(TEXT("Rifle")),
		FName(TEXT("Rifle")), FName(TEXT("Igla"))};
	const TArray<FName> Exposes = {
		FName(TEXT("PayloadController")),
		FName(TEXT("ArmorSeam")),
		FName(TEXT("TwinEngineCore")), NAME_None};
	if (Mission->Boss.BossId != TEXT("LastFlight") ||
		Mission->Boss.DefeatObjectiveId != TEXT("DefeatLastFlight") ||
		Mission->Boss.WeakPoints.Num() != 4 ||
		Mission->Boss.MaximumBreakupPieces > 6)
	{
		AddError(TEXT("Mission 10 Last Flight contract is invalid."));
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
					TEXT("Last Flight governed graph differs at index %d."),
					Index));
			}
		}
	}
	if (Mission->Waves.Num() != 3)
	{
		AddError(TEXT("Mission 10 requires three phase-tied waves."));
	}
	if (Mission->Weather.ProfileId != TEXT("EvacuationDawn"))
	{
		AddError(TEXT("Mission 10 weather must be EvacuationDawn."));
	}
	if (Mission->Presentation.Briefing.IsEmpty() ||
		Mission->Presentation.RadioChatter.Num() < 3)
	{
		AddError(TEXT("Mission 10 briefing/radio contract is incomplete."));
	}
	return OutErrors.IsEmpty();
}
