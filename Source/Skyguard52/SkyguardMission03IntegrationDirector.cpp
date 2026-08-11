#include "SkyguardMission03IntegrationDirector.h"

#include "SkyguardAudioDirectorComponent.h"
#include "SkyguardBossWeakPointComponent.h"
#include "SkyguardCampaignDefinition.h"
#include "SkyguardCampaignSubsystem.h"
#include "SkyguardGunner.h"
#include "SkyguardMissionBriefingComponent.h"
#include "SkyguardMissionDefinition.h"
#include "SkyguardMissionMapAssemblyDirector.h"
#include "SkyguardObjectiveRuntime.h"
#include "SkyguardRadioChatterComponent.h"
#include "SkyguardRoadHunterBoss.h"
#include "SkyguardYak52Aircraft.h"
#include "Components/SceneComponent.h"
#include "Components/SplineComponent.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "EngineUtils.h"

namespace
{
	template <typename T>
	T* FindFirstMission03Actor(UWorld* World)
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
	T* SpawnMission03Actor(
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

ASkyguardMission03IntegrationDirector::ASkyguardMission03IntegrationDirector()
{
	PrimaryActorTick.bCanEverTick = true;
	Root = CreateDefaultSubobject<USceneComponent>(
		TEXT("Mission03IntegrationRoot"));
	SetRootComponent(Root);
	ConvoyRuntimeAnchor = CreateDefaultSubobject<USceneComponent>(
		TEXT("ConvoyRuntimeAnchor"));
	ConvoyRuntimeAnchor->SetupAttachment(Root);
	Briefing = CreateDefaultSubobject<USkyguardMissionBriefingComponent>(
		TEXT("Briefing"));
	AudioDirector = CreateDefaultSubobject<USkyguardAudioDirectorComponent>(
		TEXT("AudioDirector"));
	RadioChatter = CreateDefaultSubobject<USkyguardRadioChatterComponent>(
		TEXT("RadioChatter"));

	CampaignDefinition = TSoftObjectPtr<USkyguardCampaignDefinition>(
		FSoftObjectPath(
			TEXT("/Game/Skyguard/Data/Campaign_v1/DA_Campaign_Skyguard52.DA_Campaign_Skyguard52")));
	MissionDefinition = TSoftObjectPtr<USkyguardMissionDefinition>(
		FSoftObjectPath(
			TEXT("/Game/Skyguard/Data/Campaign_v1/DA_Mission_M03_ConvoyEscort.DA_Mission_M03_ConvoyEscort")));
	Tags.AddUnique(TEXT("Skyguard.Mission03.PlayableIntegration"));
	Tags.AddUnique(TEXT("Skyguard.PackagePrep.Native"));
}

void ASkyguardMission03IntegrationDirector::BeginPlay()
{
	Super::BeginPlay();
	if (bAutoInitialize)
	{
		InitializePlayableMission();
	}
}

void ASkyguardMission03IntegrationDirector::Tick(const float DeltaSeconds)
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
		AudioDirector->SetEngineState(
			FMath::Clamp(YakAircraft->GetPropellerRPM() / 2800.f, 0.f, 1.f),
			0.82f, 220.f, 1.f);
	}
}

bool ASkyguardMission03IntegrationDirector::InitializePlayableMission()
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

bool ASkyguardMission03IntegrationDirector::ConfigureMissionDefinition(
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
			this, TEXT("Mission03LocalObjectives"));
	LocalObjectiveRuntime->InitializeObjectives(Mission->Objectives);
	WaveState = ESkyguardMission03WaveState::AwaitingWave;
	ConvoyRouteState = ESkyguardConvoyRouteState::Holding;
	CurrentWaveIndex = -1;
	RemainingThreatsInWave = 0;
	ConvoyIntegrity = MaximumConvoyIntegrity;
	ConvoyDistanceCentimeters = 0.f;
	ObservedBossWeakPointsDestroyed = 0;
	bCameraObjectiveRecorded = false;
	return true;
}

void ASkyguardMission03IntegrationDirector::ResolveOrSpawnActors()
{
	UWorld* World = GetWorld();
	MapAssembly =
		FindFirstMission03Actor<ASkyguardMissionMapAssemblyDirector>(World);
	YakAircraft = FindFirstMission03Actor<ASkyguardYak52Aircraft>(World);
	Gunner = FindFirstMission03Actor<ASkyguardGunner>(World);
	RoadHunter = FindFirstMission03Actor<ASkyguardRoadHunterBoss>(World);
	if (bAllowBoundedActorSpawning)
	{
		if (!YakAircraft)
		{
			YakAircraft = SpawnMission03Actor<ASkyguardYak52Aircraft>(
				World, YakSpawnLocation, YakSpawnRotation);
		}
		if (!Gunner)
		{
			Gunner = SpawnMission03Actor<ASkyguardGunner>(
				World, YakSpawnLocation, YakSpawnRotation);
		}
		if (!RoadHunter)
		{
			RoadHunter = SpawnMission03Actor<ASkyguardRoadHunterBoss>(
				World, RoadHunterSpawnLocation, RoadHunterSpawnRotation);
		}
	}
	BindRuntimeActors(MapAssembly, YakAircraft, Gunner, RoadHunter);
}

void ASkyguardMission03IntegrationDirector::BindRuntimeActors(
	ASkyguardMissionMapAssemblyDirector* InMapAssembly,
	ASkyguardYak52Aircraft* Aircraft,
	ASkyguardGunner* InGunner,
	ASkyguardRoadHunterBoss* InRoadHunter)
{
	if (RoadHunter && RoadHunter != InRoadHunter)
	{
		RoadHunter->OnBossPhaseChanged.RemoveDynamic(
			this,
			&ASkyguardMission03IntegrationDirector::HandleBossPhaseChanged);
		RoadHunter->OnPilotCommandNative.RemoveAll(this);
	}
	MapAssembly = InMapAssembly;
	YakAircraft = Aircraft;
	Gunner = InGunner;
	RoadHunter = InRoadHunter;
	ObservedBossWeakPointsDestroyed =
		RoadHunter ? RoadHunter->GetTelemetry().WeakPointsDestroyed : 0;
	bCameraObjectiveRecorded =
		RoadHunter && RoadHunter->TargetingCamera->bDestroyed;
	if (ConvoyRuntimeAnchor && GetConvoyRouteLength() > KINDA_SMALL_NUMBER)
	{
		ConvoyRuntimeAnchor->SetWorldLocation(GetConvoyWorldLocation());
	}

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
	if (RoadHunter)
	{
		RoadHunter->OnBossPhaseChanged.AddUniqueDynamic(
			this,
			&ASkyguardMission03IntegrationDirector::HandleBossPhaseChanged);
		RoadHunter->OnPilotCommandNative.RemoveAll(this);
		RoadHunter->OnPilotCommandNative.AddUObject(
			this,
			&ASkyguardMission03IntegrationDirector::HandlePilotCommand);
	}
	UpdateReadiness();
}

bool ASkyguardMission03IntegrationDirector::StartNextWave()
{
	if (!ResolvedMission ||
		WaveState != ESkyguardMission03WaveState::AwaitingWave)
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
	WaveState = ESkyguardMission03WaveState::WaveActive;
	if (ConvoyRouteState == ESkyguardConvoyRouteState::Holding)
	{
		ConvoyRouteState = ESkyguardConvoyRouteState::Advancing;
	}
	return true;
}

bool ASkyguardMission03IntegrationDirector::NotifyThreatDestroyed(
	const int32 Amount)
{
	if (WaveState != ESkyguardMission03WaveState::WaveActive || Amount <= 0)
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
			? ESkyguardMission03WaveState::BossEngaged
			: ESkyguardMission03WaveState::AwaitingWave;
		if (bLast)
		{
			SynchronizeRuntimeState();
		}
	}
	return true;
}

bool ASkyguardMission03IntegrationDirector::AdvanceConvoyByDistance(
	const float DistanceCentimeters)
{
	if (DistanceCentimeters <= 0.f ||
		ConvoyRouteState != ESkyguardConvoyRouteState::Advancing ||
		WaveState == ESkyguardMission03WaveState::Failed ||
		WaveState == ESkyguardMission03WaveState::Completed)
	{
		return false;
	}
	const float RouteLength = GetConvoyRouteLength();
	if (RouteLength <= KINDA_SMALL_NUMBER)
	{
		return false;
	}
	ConvoyDistanceCentimeters =
		FMath::Min(RouteLength, ConvoyDistanceCentimeters + DistanceCentimeters);
	if (ConvoyRuntimeAnchor)
	{
		ConvoyRuntimeAnchor->SetWorldLocation(GetConvoyWorldLocation());
	}
	if (ConvoyDistanceCentimeters >= RouteLength - KINDA_SMALL_NUMBER)
	{
		ConvoyRouteState = ESkyguardConvoyRouteState::TunnelReached;
		CompleteMissionIfReady();
	}
	return true;
}

bool ASkyguardMission03IntegrationDirector::NotifyConvoyDamage(
	const int32 Damage)
{
	if (Damage <= 0 ||
		ConvoyRouteState == ESkyguardConvoyRouteState::Destroyed ||
		WaveState == ESkyguardMission03WaveState::Completed)
	{
		return false;
	}
	ConvoyIntegrity = FMath::Max(0, ConvoyIntegrity - Damage);
	if (ConvoyIntegrity == 0)
	{
		static const FName ProtectObjective(TEXT("ProtectConvoyCore"));
		if (CampaignRuntime &&
			CampaignRuntime->GetActiveMission() == ResolvedMission)
		{
			CampaignRuntime->FailObjective(ProtectObjective);
		}
		else if (LocalObjectiveRuntime)
		{
			LocalObjectiveRuntime->FailObjective(ProtectObjective);
		}
		ConvoyRouteState = ESkyguardConvoyRouteState::Destroyed;
		WaveState = ESkyguardMission03WaveState::Failed;
	}
	return true;
}

void ASkyguardMission03IntegrationDirector::SynchronizeRuntimeState()
{
	if (!RoadHunter || !ResolvedMission)
	{
		return;
	}
	if (RoadHunter->TargetingCamera->bDestroyed &&
		!bCameraObjectiveRecorded)
	{
		NotifyObjectiveProgress(TEXT("BlindTargetingCamera"), 1);
		bCameraObjectiveRecorded = true;
	}
	const int32 Destroyed =
		FMath::Clamp(
			RoadHunter->GetTelemetry().WeakPointsDestroyed, 0, 4);
	const int32 NewDestroyed =
		FMath::Max(0, Destroyed - ObservedBossWeakPointsDestroyed);
	if (NewDestroyed > 0)
	{
		NotifyObjectiveProgress(TEXT("DefeatRoadHunter"), NewDestroyed);
		ObservedBossWeakPointsDestroyed = Destroyed;
	}
	if (RoadHunter->GetBossPhase() == ESkyguardBossPhase::Defeated)
	{
		CompleteMissionIfReady();
	}
	UpdateReadiness();
}

bool ASkyguardMission03IntegrationDirector::NotifyObjectiveProgress(
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

int32 ASkyguardMission03IntegrationDirector::CalculateWaveThreatCount(
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

float ASkyguardMission03IntegrationDirector::GetConvoyRouteLength() const
{
	return MapAssembly && MapAssembly->FlightRouteSpline
		? MapAssembly->FlightRouteSpline->GetSplineLength()
		: 0.f;
}

float ASkyguardMission03IntegrationDirector::GetConvoyRouteAlpha() const
{
	const float Length = GetConvoyRouteLength();
	return Length > KINDA_SMALL_NUMBER
		? FMath::Clamp(ConvoyDistanceCentimeters / Length, 0.f, 1.f)
		: 0.f;
}

FVector ASkyguardMission03IntegrationDirector::GetConvoyWorldLocation() const
{
	return MapAssembly && MapAssembly->FlightRouteSpline
		? MapAssembly->FlightRouteSpline->GetLocationAtDistanceAlongSpline(
			ConvoyDistanceCentimeters,
			ESplineCoordinateSpace::World)
		: FVector::ZeroVector;
}

void ASkyguardMission03IntegrationDirector::ConfigurePresentation()
{
	if (!ResolvedMission)
	{
		return;
	}
	Briefing->ConfigureFromMission(ResolvedMission);
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
			*FString::Printf(TEXT("M03_Briefing_%02d"), Index + 1));
		Line.Speaker = Index == 0
			? FText::FromString(TEXT("Convoy Lead"))
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

void ASkyguardMission03IntegrationDirector::TryLaunchSortie()
{
	if (bSortieLaunched || !Briefing->CanLaunch())
	{
		return;
	}
	if (Briefing->GetBriefingState() ==
		ESkyguardMissionBriefingState::Launched)
	{
		bSortieLaunched = true;
	}
	else if (bAutoLaunchAfterBriefing &&
		Briefing->AcknowledgeAndLaunch())
	{
		bSortieLaunched = true;
	}
	if (bSortieLaunched &&
		WaveState == ESkyguardMission03WaveState::AwaitingWave)
	{
		StartNextWave();
	}
}

void ASkyguardMission03IntegrationDirector::CompleteMissionIfReady()
{
	if (bMissionCompleted ||
		WaveState != ESkyguardMission03WaveState::BossEngaged ||
		ConvoyRouteState != ESkyguardConvoyRouteState::TunnelReached ||
		!RoadHunter ||
		RoadHunter->GetBossPhase() != ESkyguardBossPhase::Defeated)
	{
		return;
	}
	static const FName ProtectObjective(TEXT("ProtectConvoyCore"));
	USkyguardObjectiveRuntime* Objectives = GetObjectiveRuntime();
	if (Objectives && ConvoyIntegrity > 0 &&
		Objectives->GetProgress(ProtectObjective).State ==
			ESkyguardMissionObjectiveState::Active)
	{
		if (CampaignRuntime &&
                                CampaignRuntime->GetActiveMission() == ResolvedMission)
                        {
                                CampaignRuntime->CompleteSurviveObjectiveIfIntact(ProtectObjective);
                        }
                        else if (Objectives)
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
		bMissionCompleted = CampaignRuntime->FinalizeActiveMission(
			Result,
			CampaignSaveSlotName,
			CampaignSaveUserIndex);
	}
	else
	{
		bMissionCompleted = true;
	}
	if (bMissionCompleted)
	{
		WaveState = ESkyguardMission03WaveState::Completed;
	}
}

void ASkyguardMission03IntegrationDirector::HandleBossPhaseChanged(
	ESkyguardBossPhase PreviousPhase,
	const ESkyguardBossPhase NewPhase)
{
	SynchronizeRuntimeState();
	if (NewPhase == ESkyguardBossPhase::Defeated && AudioDirector)
	{
		AudioDirector->TriggerEvent(
			ESkyguardAudioEvent::ExplosionHeavy,
			RoadHunter
				? RoadHunter->GetActorLocation()
				: GetActorLocation());
	}
}

void ASkyguardMission03IntegrationDirector::HandlePilotCommand(
	const ESkyguardPilotCommand Command)
{
	if (YakAircraft)
	{
		YakAircraft->IssuePilotCommand(Command);
	}
}

USkyguardObjectiveRuntime*
ASkyguardMission03IntegrationDirector::GetObjectiveRuntime() const
{
	if (CampaignRuntime &&
		CampaignRuntime->GetActiveMission() == ResolvedMission)
	{
		return CampaignRuntime->GetObjectiveRuntime();
	}
	return LocalObjectiveRuntime;
}

bool ASkyguardMission03IntegrationDirector::IsCorePlayableReady() const
{
	return Readiness.bMissionDefinitionValid &&
		Readiness.bCampaignDefinitionValid &&
		Readiness.bMapAssemblyReady &&
		Readiness.bYakRuntimeReady &&
		Readiness.bGunnerReady &&
		Readiness.bRoadHunterReady &&
		Readiness.bObjectivesReady &&
		Readiness.bWavesReady &&
		Readiness.bConvoyRouteReady &&
		Readiness.bBriefingReady &&
		Readiness.bAudioReady;
}

void ASkyguardMission03IntegrationDirector::UpdateReadiness()
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
			ESkyguardMissionSkylineStyle::CoastalHighway &&
		MapAssembly->ValidateAssembly(AssemblyErrors);
	Readiness.bYakRuntimeReady =
		YakAircraft && YakAircraft->GetRearGunnerMount() &&
		YakAircraft->GetRearEyeMount() &&
		YakAircraft->GetRearWeaponMount();
	Readiness.bGunnerReady =
		Gunner && YakAircraft &&
		Gunner->GetAttachParentActor() == YakAircraft;
	Readiness.bRoadHunterReady =
		RoadHunter &&
		RoadHunter->TargetingCamera &&
		RoadHunter->LeftActuator &&
		RoadHunter->RightActuator &&
		RoadHunter->Engine &&
		RoadHunter->GetMaxDefeatDebrisPieces() <= 3;
	Readiness.bObjectivesReady =
		GetObjectiveRuntime() && ResolvedMission &&
		ResolvedMission->Objectives.Num() == 3;
	Readiness.bWavesReady =
		ResolvedMission && ResolvedMission->Waves.Num() == 3 &&
		CalculateWaveThreatCount(0) == 2 &&
		CalculateWaveThreatCount(1) == 3 &&
		CalculateWaveThreatCount(2) == 4;
	Readiness.bConvoyRouteReady =
		ConvoyRuntimeAnchor &&
		MapAssembly && MapAssembly->FlightRouteSpline &&
		GetConvoyRouteLength() > 1000.f;
	Readiness.bBriefingReady =
		Briefing &&
		Briefing->GetBriefingState() !=
			ESkyguardMissionBriefingState::Unconfigured;
	Readiness.bAudioReady = AudioDirector && RadioChatter;
	Readiness.ObjectiveCount =
		ResolvedMission ? ResolvedMission->Objectives.Num() : 0;
	Readiness.WaveCount =
		ResolvedMission ? ResolvedMission->Waves.Num() : 0;
	Readiness.RadioLineCount =
		ResolvedMission
			? ResolvedMission->Presentation.RadioChatter.Num()
			: 0;
}

bool ASkyguardMission03IntegrationDirector::ValidateMissionContract(
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
		AddError(TEXT("Mission id must be M03_ConvoyEscort."));
	}
	if (Mission->Route.Points.Num() < 4)
	{
		AddError(TEXT("Mission 3 route requires at least four points."));
	}
	if (Mission->Objectives.Num() != 3)
	{
		AddError(TEXT("Mission 3 requires exactly three objectives."));
	}
	for (const FName RequiredObjective : {
		FName(TEXT("ProtectConvoyCore")),
		FName(TEXT("BlindTargetingCamera")),
		FName(TEXT("DefeatRoadHunter"))})
	{
		if (!Mission->FindObjective(RequiredObjective))
		{
			AddError(FString::Printf(
				TEXT("Mission 3 is missing objective %s."),
				*RequiredObjective.ToString()));
		}
	}
	const TArray<FName> ExpectedIds = {
		FName(TEXT("TargetingCamera")),
		FName(TEXT("LeftActuator")),
		FName(TEXT("RightActuator")),
		FName(TEXT("Engine"))};
	const TArray<FName> ExpectedWeapons = {
		FName(TEXT("Rifle")), FName(TEXT("Rifle")),
		FName(TEXT("Rifle")), FName(TEXT("Igla"))};
	const TArray<FName> ExpectedExposes = {
		FName(TEXT("LeftActuator")), FName(TEXT("Engine")),
		FName(TEXT("Engine")), NAME_None};
	if (Mission->Boss.BossId != TEXT("RoadHunter") ||
		Mission->Boss.DefeatObjectiveId != TEXT("DefeatRoadHunter") ||
		Mission->Boss.WeakPoints.Num() != 4 ||
		Mission->Boss.MaximumBreakupPieces > 3)
	{
		AddError(TEXT("Mission 3 Road Hunter boss contract is invalid."));
	}
	else
	{
		for (int32 Index = 0; Index < ExpectedIds.Num(); ++Index)
		{
			const FSkyguardBossWeakPointDefinition& WeakPoint =
				Mission->Boss.WeakPoints[Index];
			if (WeakPoint.WeakPointId != ExpectedIds[Index] ||
				WeakPoint.RequiredWeapon != ExpectedWeapons[Index] ||
				WeakPoint.ExposesWeakPointId != ExpectedExposes[Index])
			{
				AddError(FString::Printf(
					TEXT("Road Hunter weak-point graph differs at index %d."),
					Index));
			}
		}
	}
	if (Mission->Waves.Num() != 3)
	{
		AddError(TEXT("Mission 3 requires exactly three waves."));
	}
	if (Mission->Weather.ProfileId != TEXT("DryMorning"))
	{
		AddError(TEXT("Mission 3 weather must be DryMorning."));
	}
	if (Mission->Presentation.Briefing.IsEmpty() ||
		Mission->Presentation.RadioChatter.Num() < 3)
	{
		AddError(TEXT("Mission 3 briefing/radio contract is incomplete."));
	}
	return OutErrors.IsEmpty();
}
