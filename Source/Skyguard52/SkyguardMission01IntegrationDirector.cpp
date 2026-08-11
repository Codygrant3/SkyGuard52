#include "SkyguardMission01IntegrationDirector.h"

#include "SkyguardAudioDirectorComponent.h"
#include "SkyguardCampaignDefinition.h"
#include "SkyguardCampaignSubsystem.h"
#include "SkyguardGunner.h"
#include "SkyguardMission01EnvironmentDirector.h"
#include "SkyguardMissionBriefingComponent.h"
#include "SkyguardMissionDefinition.h"
#include "SkyguardObjectiveRuntime.h"
#include "SkyguardPathfinderBoss.h"
#include "SkyguardDrone.h"
#include "SkyguardRadioChatterComponent.h"
#include "SkyguardSortiePresentationComponent.h"
#include "SkyguardYak52Aircraft.h"
#include "Components/SceneComponent.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerController.h"

namespace
{
	template <typename T>
	T* FindFirstActor(UWorld* World)
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
	T* SpawnBoundedActor(UWorld* World, const FVector& Location, const FRotator& Rotation)
	{
		if (!World)
		{
			return nullptr;
		}
		FActorSpawnParameters Parameters;
		Parameters.SpawnCollisionHandlingOverride =
			ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
		return World->SpawnActor<T>(T::StaticClass(), Location, Rotation, Parameters);
	}
}

ASkyguardMission01IntegrationDirector::ASkyguardMission01IntegrationDirector()
{
	PrimaryActorTick.bCanEverTick = true;

	Root = CreateDefaultSubobject<USceneComponent>(TEXT("Mission01IntegrationRoot"));
	SetRootComponent(Root);

	Briefing =
		CreateDefaultSubobject<USkyguardMissionBriefingComponent>(TEXT("Briefing"));
	AudioDirector =
		CreateDefaultSubobject<USkyguardAudioDirectorComponent>(TEXT("AudioDirector"));
	RadioChatter =
		CreateDefaultSubobject<USkyguardRadioChatterComponent>(TEXT("RadioChatter"));
	SortiePresentation =
		CreateDefaultSubobject<USkyguardSortiePresentationComponent>(
			TEXT("SortiePresentation"));

	CampaignDefinition = TSoftObjectPtr<USkyguardCampaignDefinition>(
		FSoftObjectPath(
			TEXT("/Game/Skyguard/Data/Campaign_v1/DA_Campaign_Skyguard52.DA_Campaign_Skyguard52")));
	MissionDefinition = TSoftObjectPtr<USkyguardMissionDefinition>(
		FSoftObjectPath(
			TEXT("/Game/Skyguard/Data/Campaign_v1/DA_Mission_M01_CoastalIntercept.DA_Mission_M01_CoastalIntercept")));

	Tags.AddUnique(TEXT("Skyguard.Mission01.PlayableIntegration"));
	Tags.AddUnique(TEXT("Skyguard.PackagePrep.Native"));
}

void ASkyguardMission01IntegrationDirector::BeginPlay()
{
	Super::BeginPlay();
	ASkyguardDrone::OnAnyCityImpacted.AddUObject(
		this,
		&ASkyguardMission01IntegrationDirector::HandleDroneCityImpact);
	if (bAutoInitialize)
	{
		InitializePlayableMission();
	}
}

void ASkyguardMission01IntegrationDirector::EndPlay(
	const EEndPlayReason::Type EndPlayReason)
{
	ASkyguardDrone::OnAnyCityImpacted.RemoveAll(this);
	Super::EndPlay(EndPlayReason);
}

void ASkyguardMission01IntegrationDirector::HandleDroneCityImpact(
	ASkyguardDrone* Drone)
{
	if (!Drone || !bInitialized || bMissionCompleted)
	{
		return;
	}
	NotifyProtectedAssetFailed();
}

void ASkyguardMission01IntegrationDirector::Tick(const float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	if (!bInitialized)
	{
		return;
	}

	Briefing->AdvanceBriefing(DeltaSeconds);
	TryLaunchSortie();
	if (bSortieLaunched)
	{
		SynchronizeRuntimeState();
	}

	if (YakAircraft && AudioDirector)
	{
		const float NormalizedRpm =
			FMath::Clamp(YakAircraft->GetPropellerRPM() / 2800.f, 0.f, 1.f);
		AudioDirector->SetEngineState(NormalizedRpm, 0.82f, 220.f, 1.f);
	}
}

bool ASkyguardMission01IntegrationDirector::InitializePlayableMission()
{
	if (bInitialized)
	{
		UpdateReadiness();
		return IsCorePlayableReady();
	}

	ResolvedMission = MissionDefinition.LoadSynchronous();
	ResolvedCampaign = CampaignDefinition.LoadSynchronous();

	TArray<FText> ContractErrors;
	if (!ValidateMissionContract(ResolvedMission, ContractErrors))
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
				// Restore prior completions before StartMission unlock checks.
				CampaignRuntime->LoadCampaignFromSlot(
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

bool ASkyguardMission01IntegrationDirector::ConfigureMissionDefinition(
	USkyguardMissionDefinition* Mission)
{
	TArray<FText> Errors;
	if (!ValidateMissionContract(Mission, Errors))
	{
		return false;
	}

	ResolvedMission = Mission;
	LocalObjectiveRuntime =
		NewObject<USkyguardObjectiveRuntime>(this, TEXT("Mission01LocalObjectives"));
	LocalObjectiveRuntime->InitializeObjectives(Mission->Objectives);
	Readiness.ObjectiveCount = Mission->Objectives.Num();
	return true;
}

void ASkyguardMission01IntegrationDirector::ResolveOrSpawnActors()
{
	UWorld* World = GetWorld();
	Environment = FindFirstActor<ASkyguardMission01EnvironmentDirector>(World);
	YakAircraft = FindFirstActor<ASkyguardYak52Aircraft>(World);
	Gunner = nullptr;
	if (APlayerController* PlayerController =
			World ? World->GetFirstPlayerController() : nullptr)
	{
		Gunner = Cast<ASkyguardGunner>(PlayerController->GetPawn());
	}
	if (!Gunner)
	{
		Gunner = FindFirstActor<ASkyguardGunner>(World);
	}
	Pathfinder = FindFirstActor<ASkyguardPathfinderBoss>(World);

	if (bAllowBoundedActorSpawning)
	{
		if (!YakAircraft)
		{
			YakAircraft = SpawnBoundedActor<ASkyguardYak52Aircraft>(
				World, YakSpawnLocation, YakSpawnRotation);
		}
		if (!Gunner)
		{
			Gunner = SpawnBoundedActor<ASkyguardGunner>(
				World, YakSpawnLocation, YakSpawnRotation);
		}
		if (!Pathfinder)
		{
			Pathfinder = SpawnBoundedActor<ASkyguardPathfinderBoss>(
				World, PathfinderSpawnLocation, PathfinderSpawnRotation);
		}
	}

	BindRuntimeActors(YakAircraft, Gunner, Pathfinder);
}

void ASkyguardMission01IntegrationDirector::BindRuntimeActors(
	ASkyguardYak52Aircraft* Aircraft,
	ASkyguardGunner* InGunner,
	ASkyguardPathfinderBoss* InPathfinder)
{
	if (Pathfinder && Pathfinder != InPathfinder)
	{
		Pathfinder->OnBossPhaseChanged.RemoveDynamic(
			this,
			&ASkyguardMission01IntegrationDirector::HandleBossPhaseChanged);
		Pathfinder->OnPilotCommandNative.RemoveAll(this);
	}

	YakAircraft = Aircraft;
	Gunner = InGunner;
	if (Gunner)
	{
		Gunner->ResetSortieCombatStats();
	}
	Pathfinder = InPathfinder;
	ObservedWeakPointsDestroyed = Pathfinder
		? Pathfinder->GetTelemetry().WeakPointsDestroyed
		: 0;

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
	if (Pathfinder)
	{
		Pathfinder->OnBossPhaseChanged.AddUniqueDynamic(
			this,
			&ASkyguardMission01IntegrationDirector::HandleBossPhaseChanged);
		Pathfinder->OnPilotCommandNative.RemoveAll(this);
		Pathfinder->OnPilotCommandNative.AddUObject(
			this,
			&ASkyguardMission01IntegrationDirector::HandlePilotCommand);
	}
	UpdateReadiness();
}

void ASkyguardMission01IntegrationDirector::ConfigurePresentation()
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
			*FString::Printf(TEXT("M01_Briefing_%02d"), Index + 1));
		Line.Speaker = Index == 0
			? FText::FromString(TEXT("Coastal Radar"))
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
	Readiness.RadioLineCount = Lines.Num();
}

bool ASkyguardMission01IntegrationDirector::NotifyObjectiveProgress(
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

bool ASkyguardMission01IntegrationDirector::NotifyProtectedAssetFailed()
{
	static const FName ProtectObjective(TEXT("ProtectCoastalRadar"));
	bool bFailedObjective = false;
	if (CampaignRuntime &&
		CampaignRuntime->GetActiveMission() == ResolvedMission)
	{
		bFailedObjective = CampaignRuntime->FailObjective(ProtectObjective);
		if (!bMissionCompleted)
		{
			FSkyguardMissionResult Result;
			CampaignRuntime->FillResultCombatStats(Result, Gunner, this);
			bMissionCompleted = CampaignRuntime->FailActiveMission(
				Result,
				CampaignSaveSlotName,
				CampaignSaveUserIndex);
			if (SortiePresentation)
			{
				SortiePresentation->RefreshDebrief();
			}
		}
		return bFailedObjective;
	}
	bFailedObjective = LocalObjectiveRuntime &&
		LocalObjectiveRuntime->FailObjective(ProtectObjective);
	if (bFailedObjective)
	{
		bMissionCompleted = true;
	}
	return bFailedObjective;
}

void ASkyguardMission01IntegrationDirector::SynchronizeRuntimeState()
{
	if (!Pathfinder || !ResolvedMission)
	{
		return;
	}

	const int32 Destroyed =
		FMath::Clamp(Pathfinder->GetTelemetry().WeakPointsDestroyed, 0, 4);
	const int32 NewWeakPoints =
		FMath::Max(0, Destroyed - ObservedWeakPointsDestroyed);
	if (NewWeakPoints > 0)
	{
		NotifyObjectiveProgress(TEXT("DefeatPathfinder"), NewWeakPoints);

		const int32 PreviousCommandProgress =
			FMath::Min(2, ObservedWeakPointsDestroyed);
		const int32 CurrentCommandProgress = FMath::Min(2, Destroyed);
		if (CurrentCommandProgress > PreviousCommandProgress)
		{
			NotifyObjectiveProgress(
				TEXT("DisableCommandNetwork"),
				CurrentCommandProgress - PreviousCommandProgress);
		}
		ObservedWeakPointsDestroyed = Destroyed;
	}

	if (Pathfinder->GetBossPhase() == ESkyguardBossPhase::Defeated)
	{
		CompleteMissionIfReady();
	}
	UpdateReadiness();
}

void ASkyguardMission01IntegrationDirector::TryLaunchSortie()
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
		return;
	}
	if (bAutoLaunchAfterBriefing && Briefing->AcknowledgeAndLaunch())
	{
		bSortieLaunched = true;
		SortiePresentation->SetSortieLaunched();
	}
}

void ASkyguardMission01IntegrationDirector::CompleteMissionIfReady()
{
	if (bMissionCompleted)
	{
		return;
	}

	static const FName ProtectObjective(TEXT("ProtectCoastalRadar"));
	USkyguardObjectiveRuntime* Objectives = GetObjectiveRuntime();
	if (Objectives)
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
		FSkyguardMissionResult Result;
		CampaignRuntime->FillResultCombatStats(Result, Gunner, this);
		bMissionCompleted = CampaignRuntime->FinalizeActiveMission(
			Result,
			CampaignSaveSlotName,
			CampaignSaveUserIndex);
		SortiePresentation->RefreshDebrief();
	}
	else
	{
		bMissionCompleted = true;
	}
}

void ASkyguardMission01IntegrationDirector::HandleBossPhaseChanged(
	ESkyguardBossPhase PreviousPhase,
	const ESkyguardBossPhase NewPhase)
{
	SynchronizeRuntimeState();
	if (NewPhase == ESkyguardBossPhase::Defeated && AudioDirector)
	{
		AudioDirector->TriggerEvent(
			ESkyguardAudioEvent::ExplosionHeavy,
			Pathfinder ? Pathfinder->GetActorLocation() : GetActorLocation());
	}
}

void ASkyguardMission01IntegrationDirector::HandlePilotCommand(
	const ESkyguardPilotCommand Command)
{
	if (YakAircraft)
	{
		YakAircraft->IssuePilotCommand(Command);
	}
}

USkyguardObjectiveRuntime*
ASkyguardMission01IntegrationDirector::GetObjectiveRuntime() const
{
	if (CampaignRuntime &&
		CampaignRuntime->GetActiveMission() == ResolvedMission)
	{
		return CampaignRuntime->GetObjectiveRuntime();
	}
	return LocalObjectiveRuntime;
}

bool ASkyguardMission01IntegrationDirector::IsCorePlayableReady() const
{
	return Readiness.bMissionDefinitionValid &&
		Readiness.bCampaignDefinitionValid &&
		Readiness.bEnvironmentReady &&
		Readiness.bYakRuntimeReady &&
		Readiness.bGunnerReady &&
		Readiness.bPathfinderReady &&
		Readiness.bObjectivesReady &&
		Readiness.bBriefingReady &&
		Readiness.bAudioReady &&
		Readiness.bSortiePresentationReady;
}

void ASkyguardMission01IntegrationDirector::UpdateReadiness()
{
	TArray<FText> Errors;
	Readiness.bMissionDefinitionValid =
		ValidateMissionContract(ResolvedMission, Errors);
	Readiness.bCampaignDefinitionValid =
		ResolvedCampaign &&
		ResolvedCampaign->FindMission(GetMissionId()) == ResolvedMission;
	Readiness.bEnvironmentReady =
		Environment &&
		Environment->HasContinuousCoastline() &&
		Environment->IsRouteExclusionSafe();
	Readiness.bYakRuntimeReady =
		YakAircraft &&
		YakAircraft->GetRearGunnerMount() &&
		YakAircraft->GetRearEyeMount() &&
		YakAircraft->GetRearWeaponMount();
	Readiness.bGunnerReady =
		Gunner && YakAircraft &&
		Gunner->GetAttachParentActor() == YakAircraft;
	Readiness.bPathfinderReady =
		Pathfinder &&
		Pathfinder->GetDefeatDebrisPieceCount() == 4 &&
		Pathfinder->GetMaxDefeatDebrisPieces() <= 4 &&
		Pathfinder->EncounterController;
	Readiness.bObjectivesReady =
		GetObjectiveRuntime() && ResolvedMission &&
		ResolvedMission->Objectives.Num() == 3;
	Readiness.bBriefingReady =
		Briefing &&
		Briefing->GetBriefingState() !=
			ESkyguardMissionBriefingState::Unconfigured;
	Readiness.bAudioReady = AudioDirector && RadioChatter;
	Readiness.bSortiePresentationReady =
		SortiePresentation && SortiePresentation->IsConfigured();
	Readiness.ObjectiveCount =
		ResolvedMission ? ResolvedMission->Objectives.Num() : 0;
	Readiness.RadioLineCount =
		ResolvedMission
			? ResolvedMission->Presentation.RadioChatter.Num()
			: 0;
}

bool ASkyguardMission01IntegrationDirector::ValidateMissionContract(
	const USkyguardMissionDefinition* Mission,
	TArray<FText>& OutErrors)
{
	OutErrors.Reset();
	auto AddError = [&OutErrors](const TCHAR* Message)
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
		AddError(TEXT("Mission id must be M01_CoastalIntercept."));
	}
	if (Mission->Route.Points.Num() < 4)
	{
		AddError(TEXT("Mission 1 route requires at least four points."));
	}
	if (Mission->Objectives.Num() != 3)
	{
		AddError(TEXT("Mission 1 requires exactly three governed objectives."));
	}
	for (const FName RequiredObjective : {
		FName(TEXT("ProtectCoastalRadar")),
		FName(TEXT("DisableCommandNetwork")),
		FName(TEXT("DefeatPathfinder"))})
	{
		if (!Mission->FindObjective(RequiredObjective))
		{
			OutErrors.Add(FText::FromString(FString::Printf(
				TEXT("Mission 1 is missing objective %s."),
				*RequiredObjective.ToString())));
		}
	}
	if (Mission->Boss.BossId != TEXT("Pathfinder") ||
		Mission->Boss.WeakPoints.Num() != 4 ||
		Mission->Boss.MaximumBreakupPieces != 4)
	{
		AddError(TEXT("Mission 1 Pathfinder boss contract is invalid."));
	}
	if (Mission->Presentation.Briefing.IsEmpty() ||
		Mission->Presentation.RadioChatter.Num() < 3 ||
		Mission->Presentation.MinimumBriefingWarmupSeconds < 0.f)
	{
		AddError(TEXT("Mission 1 briefing/radio contract is incomplete."));
	}
	return OutErrors.IsEmpty();
}
