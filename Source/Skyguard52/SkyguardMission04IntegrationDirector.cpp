#include "SkyguardMission04IntegrationDirector.h"

#include "SkyguardAudioDirectorComponent.h"
#include "SkyguardBlackKiteBoss.h"
#include "SkyguardBossWeakPointComponent.h"
#include "SkyguardCampaignDefinition.h"
#include "SkyguardCampaignSubsystem.h"
#include "SkyguardGunner.h"
#include "SkyguardMissionBriefingComponent.h"
#include "SkyguardMissionDefinition.h"
#include "SkyguardMissionMapAssemblyDirector.h"
#include "SkyguardObjectiveRuntime.h"
#include "SkyguardRadioChatterComponent.h"
#include "SkyguardYak52Aircraft.h"
#include "Components/SceneComponent.h"
#include "Components/SpotLightComponent.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "EngineUtils.h"

namespace
{
	template <typename T>
	T* FindFirstMission04Actor(UWorld* World)
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
	T* SpawnMission04Actor(
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

ASkyguardMission04IntegrationDirector::ASkyguardMission04IntegrationDirector()
{
	PrimaryActorTick.bCanEverTick = true;
	Root = CreateDefaultSubobject<USceneComponent>(
		TEXT("Mission04IntegrationRoot"));
	SetRootComponent(Root);
	SearchlightPort = CreateDefaultSubobject<USpotLightComponent>(
		TEXT("SearchlightPort"));
	SearchlightPort->SetupAttachment(Root);
	SearchlightPort->SetRelativeLocation(FVector(31000.f, 24000.f, 180.f));
	SearchlightPort->SetIntensity(450000.f);
	SearchlightPort->SetOuterConeAngle(18.f);
	SearchlightStarboard = CreateDefaultSubobject<USpotLightComponent>(
		TEXT("SearchlightStarboard"));
	SearchlightStarboard->SetupAttachment(Root);
	SearchlightStarboard->SetRelativeLocation(FVector(35000.f, 26000.f, 180.f));
	SearchlightStarboard->SetIntensity(450000.f);
	SearchlightStarboard->SetOuterConeAngle(18.f);
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
			TEXT("/Game/Skyguard/Data/Campaign_v1/DA_Mission_M04_NightBlackout.DA_Mission_M04_NightBlackout")));
	SetSearchlightPresentation(false);
	Tags.AddUnique(TEXT("Skyguard.Mission04.PlayableIntegration"));
	Tags.AddUnique(TEXT("Skyguard.PackagePrep.Native"));
}

void ASkyguardMission04IntegrationDirector::BeginPlay()
{
	Super::BeginPlay();
	if (bAutoInitialize)
	{
		InitializePlayableMission();
	}
}

void ASkyguardMission04IntegrationDirector::Tick(const float DeltaSeconds)
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

bool ASkyguardMission04IntegrationDirector::InitializePlayableMission()
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

bool ASkyguardMission04IntegrationDirector::ConfigureMissionDefinition(
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
			this, TEXT("Mission04LocalObjectives"));
	LocalObjectiveRuntime->InitializeObjectives(Mission->Objectives);
	WaveState = ESkyguardMission04WaveState::AwaitingWave;
	CurrentWaveIndex = -1;
	RemainingThreatsInWave = 0;
	SubstationIntegrity = MaximumSubstationIntegrity;
	SearchlightRuntime = FSkyguardSearchlightTrackRuntime();
	ObservedBossWeakPointsDestroyed = 0;
	bMissionCompleted = false;
	SetSearchlightPresentation(false);
	return true;
}

void ASkyguardMission04IntegrationDirector::ResolveOrSpawnActors()
{
	UWorld* World = GetWorld();
	MapAssembly =
		FindFirstMission04Actor<ASkyguardMissionMapAssemblyDirector>(World);
	YakAircraft = FindFirstMission04Actor<ASkyguardYak52Aircraft>(World);
	Gunner = FindFirstMission04Actor<ASkyguardGunner>(World);
	BlackKite = FindFirstMission04Actor<ASkyguardBlackKiteBoss>(World);
	if (bAllowBoundedActorSpawning)
	{
		if (!YakAircraft)
		{
			YakAircraft = SpawnMission04Actor<ASkyguardYak52Aircraft>(
				World, YakSpawnLocation, YakSpawnRotation);
		}
		if (!Gunner)
		{
			Gunner = SpawnMission04Actor<ASkyguardGunner>(
				World, YakSpawnLocation, YakSpawnRotation);
		}
		if (!BlackKite)
		{
			BlackKite = SpawnMission04Actor<ASkyguardBlackKiteBoss>(
				World, BlackKiteSpawnLocation, BlackKiteSpawnRotation);
		}
	}
	BindRuntimeActors(MapAssembly, YakAircraft, Gunner, BlackKite);
}

void ASkyguardMission04IntegrationDirector::BindRuntimeActors(
	ASkyguardMissionMapAssemblyDirector* InMapAssembly,
	ASkyguardYak52Aircraft* Aircraft,
	ASkyguardGunner* InGunner,
	ASkyguardBlackKiteBoss* InBlackKite)
{
	if (BlackKite && BlackKite != InBlackKite)
	{
		BlackKite->OnBossPhaseChanged.RemoveDynamic(
			this,
			&ASkyguardMission04IntegrationDirector::HandleBossPhaseChanged);
		BlackKite->OnPilotCommandNative.RemoveAll(this);
	}
	MapAssembly = InMapAssembly;
	YakAircraft = Aircraft;
	Gunner = InGunner;
	BlackKite = InBlackKite;
	ObservedBossWeakPointsDestroyed =
		BlackKite ? BlackKite->GetTelemetry().WeakPointsDestroyed : 0;
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
	if (BlackKite)
	{
		BlackKite->OnBossPhaseChanged.AddUniqueDynamic(
			this,
			&ASkyguardMission04IntegrationDirector::HandleBossPhaseChanged);
		BlackKite->OnPilotCommandNative.RemoveAll(this);
		BlackKite->OnPilotCommandNative.AddUObject(
			this,
			&ASkyguardMission04IntegrationDirector::HandlePilotCommand);
	}
	UpdateReadiness();
}

bool ASkyguardMission04IntegrationDirector::StartNextWave()
{
	if (!ResolvedMission ||
		WaveState != ESkyguardMission04WaveState::AwaitingWave)
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
	WaveState = ESkyguardMission04WaveState::WaveActive;
	return true;
}

bool ASkyguardMission04IntegrationDirector::NotifyThreatDestroyed(
	const int32 Amount)
{
	if (WaveState != ESkyguardMission04WaveState::WaveActive ||
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
			? ESkyguardMission04WaveState::BossEngaged
			: ESkyguardMission04WaveState::AwaitingWave;
	}
	return true;
}

bool ASkyguardMission04IntegrationDirector::StartSearchlightWindow(
	const float WindowSeconds)
{
	if (!BlackKite || WindowSeconds <= 0.f ||
		SearchlightRuntime.bActive ||
		(WaveState != ESkyguardMission04WaveState::WaveActive &&
			WaveState != ESkyguardMission04WaveState::BossEngaged))
	{
		return false;
	}
	SearchlightRuntime.bActive = true;
	SearchlightRuntime.bBossTracked = false;
	SearchlightRuntime.RemainingSeconds = WindowSeconds;
	SearchlightRuntime.HeldSeconds = 0.f;
	BlackKite->SetSearchlightTracked(false);
	SetSearchlightPresentation(true);
	return true;
}

bool ASkyguardMission04IntegrationDirector::AdvanceSearchlightTrack(
	const float DeltaSeconds,
	const bool bBossInTrack)
{
	if (!SearchlightRuntime.bActive || DeltaSeconds <= 0.f)
	{
		return false;
	}
	SearchlightRuntime.bBossTracked = bBossInTrack;
	SearchlightRuntime.RemainingSeconds =
		FMath::Max(0.f, SearchlightRuntime.RemainingSeconds - DeltaSeconds);
	if (bBossInTrack)
	{
		SearchlightRuntime.HeldSeconds += DeltaSeconds;
		BlackKite->SetSearchlightTracked(true);
	}
	else
	{
		SearchlightRuntime.HeldSeconds = 0.f;
		BlackKite->SetSearchlightTracked(false);
	}
	if (SearchlightRuntime.HeldSeconds >= RequiredTrackSeconds)
	{
		SearchlightRuntime.bActive = false;
		SearchlightRuntime.bBossTracked = true;
		++SearchlightRuntime.CompletedPasses;
		NotifyObjectiveProgress(TEXT("HoldSearchlightTrack"), 1);
		SetSearchlightPresentation(true);
		return true;
	}
	if (SearchlightRuntime.RemainingSeconds <= 0.f)
	{
		SearchlightRuntime.bActive = false;
		SearchlightRuntime.bBossTracked = false;
		BlackKite->SetSearchlightTracked(false);
		SetSearchlightPresentation(false);
		NotifySubstationDamage(MissedTrackDamage);
		return false;
	}
	return true;
}

bool ASkyguardMission04IntegrationDirector::NotifySubstationDamage(
	const int32 Damage)
{
	if (Damage <= 0 || SubstationIntegrity <= 0 ||
		WaveState == ESkyguardMission04WaveState::Completed)
	{
		return false;
	}
	SubstationIntegrity = FMath::Max(0, SubstationIntegrity - Damage);
	if (SubstationIntegrity == 0)
	{
		static const FName ProtectObjective(TEXT("ProtectSubstation"));
		if (CampaignRuntime &&
			CampaignRuntime->GetActiveMission() == ResolvedMission)
		{
			CampaignRuntime->FailObjective(ProtectObjective);
		}
		else if (LocalObjectiveRuntime)
		{
			LocalObjectiveRuntime->FailObjective(ProtectObjective);
		}
		WaveState = ESkyguardMission04WaveState::Failed;
		SetSearchlightPresentation(false);
	}
	return true;
}

void ASkyguardMission04IntegrationDirector::SynchronizeRuntimeState()
{
	if (!BlackKite || !ResolvedMission)
	{
		return;
	}
	const int32 Destroyed = FMath::Clamp(
		BlackKite->GetTelemetry().WeakPointsDestroyed, 0, 4);
	const int32 NewDestroyed =
		FMath::Max(0, Destroyed - ObservedBossWeakPointsDestroyed);
	if (NewDestroyed > 0)
	{
		NotifyObjectiveProgress(TEXT("DefeatBlackKite"), NewDestroyed);
		ObservedBossWeakPointsDestroyed = Destroyed;
	}
	if (BlackKite->GetBossPhase() == ESkyguardBossPhase::Defeated)
	{
		CompleteMissionIfReady();
	}
	UpdateReadiness();
}

bool ASkyguardMission04IntegrationDirector::NotifyObjectiveProgress(
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

int32 ASkyguardMission04IntegrationDirector::CalculateWaveThreatCount(
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

void ASkyguardMission04IntegrationDirector::ConfigurePresentation()
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
			*FString::Printf(TEXT("M04_Briefing_%02d"), Index + 1));
		Line.Speaker = Index == 0
			? FText::FromString(TEXT("Grid Control"))
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

void ASkyguardMission04IntegrationDirector::TryLaunchSortie()
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
		WaveState == ESkyguardMission04WaveState::AwaitingWave)
	{
		StartNextWave();
	}
}

void ASkyguardMission04IntegrationDirector::CompleteMissionIfReady()
{
	if (bMissionCompleted ||
		WaveState != ESkyguardMission04WaveState::BossEngaged ||
		SubstationIntegrity <= 0 || !BlackKite ||
		BlackKite->GetBossPhase() != ESkyguardBossPhase::Defeated)
	{
		return;
	}
	static const FName ProtectObjective(TEXT("ProtectSubstation"));
	USkyguardObjectiveRuntime* Objectives = GetObjectiveRuntime();
	if (Objectives &&
		Objectives->GetProgress(ProtectObjective).State ==
			ESkyguardMissionObjectiveState::Active)
	{
		NotifyObjectiveProgress(ProtectObjective, 1);
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
		bMissionCompleted =
			CampaignRuntime->CompleteActiveMission(Result);
	}
	else
	{
		bMissionCompleted = true;
	}
	if (bMissionCompleted)
	{
		WaveState = ESkyguardMission04WaveState::Completed;
		SetSearchlightPresentation(false);
	}
}

void ASkyguardMission04IntegrationDirector::SetSearchlightPresentation(
	const bool bEnabled)
{
	if (SearchlightPort)
	{
		SearchlightPort->SetVisibility(bEnabled);
	}
	if (SearchlightStarboard)
	{
		SearchlightStarboard->SetVisibility(bEnabled);
	}
}

void ASkyguardMission04IntegrationDirector::HandleBossPhaseChanged(
	ESkyguardBossPhase PreviousPhase,
	const ESkyguardBossPhase NewPhase)
{
	SynchronizeRuntimeState();
	if (NewPhase == ESkyguardBossPhase::Defeated && AudioDirector)
	{
		AudioDirector->TriggerEvent(
			ESkyguardAudioEvent::ExplosionHeavy,
			BlackKite ? BlackKite->GetActorLocation() : GetActorLocation());
	}
}

void ASkyguardMission04IntegrationDirector::HandlePilotCommand(
	const ESkyguardPilotCommand Command)
{
	if (YakAircraft)
	{
		YakAircraft->IssuePilotCommand(Command);
	}
}

USkyguardObjectiveRuntime*
ASkyguardMission04IntegrationDirector::GetObjectiveRuntime() const
{
	if (CampaignRuntime &&
		CampaignRuntime->GetActiveMission() == ResolvedMission)
	{
		return CampaignRuntime->GetObjectiveRuntime();
	}
	return LocalObjectiveRuntime;
}

bool ASkyguardMission04IntegrationDirector::IsCorePlayableReady() const
{
	return Readiness.bMissionDefinitionValid &&
		Readiness.bCampaignDefinitionValid &&
		Readiness.bMapAssemblyReady &&
		Readiness.bYakRuntimeReady &&
		Readiness.bGunnerReady &&
		Readiness.bBlackKiteReady &&
		Readiness.bObjectivesReady &&
		Readiness.bWavesReady &&
		Readiness.bSearchlightsReady &&
		Readiness.bSubstationReady &&
		Readiness.bBriefingReady &&
		Readiness.bAudioReady;
}

void ASkyguardMission04IntegrationDirector::UpdateReadiness()
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
			ESkyguardMissionSkylineStyle::BlackoutUrban &&
		MapAssembly->ValidateAssembly(AssemblyErrors);
	Readiness.bYakRuntimeReady =
		YakAircraft && YakAircraft->GetRearGunnerMount() &&
		YakAircraft->GetRearEyeMount() &&
		YakAircraft->GetRearWeaponMount();
	Readiness.bGunnerReady =
		Gunner && YakAircraft &&
		Gunner->GetAttachParentActor() == YakAircraft;
	Readiness.bBlackKiteReady =
		BlackKite && BlackKite->PortNavigationVane &&
		BlackKite->StarboardNavigationVane &&
		BlackKite->Jammer && BlackKite->PowerBus &&
		BlackKite->GetMaxDefeatDebrisPieces() <= 3;
	Readiness.bObjectivesReady =
		GetObjectiveRuntime() && ResolvedMission &&
		ResolvedMission->Objectives.Num() == 3;
	Readiness.bWavesReady =
		ResolvedMission && ResolvedMission->Waves.Num() == 3 &&
		CalculateWaveThreatCount(0) == 2 &&
		CalculateWaveThreatCount(1) == 3 &&
		CalculateWaveThreatCount(2) == 4;
	Readiness.bSearchlightsReady =
		SearchlightPort && SearchlightStarboard &&
		RequiredTrackSeconds > 0.f;
	Readiness.bSubstationReady =
		SubstationIntegrity > 0 &&
		SubstationIntegrity <= MaximumSubstationIntegrity;
	Readiness.bBriefingReady =
		Briefing &&
		Briefing->GetBriefingState() !=
			ESkyguardMissionBriefingState::Unconfigured;
	Readiness.bAudioReady = AudioDirector && RadioChatter;
	Readiness.ObjectiveCount =
		ResolvedMission ? ResolvedMission->Objectives.Num() : 0;
	Readiness.WaveCount =
		ResolvedMission ? ResolvedMission->Waves.Num() : 0;
}

bool ASkyguardMission04IntegrationDirector::ValidateMissionContract(
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
		AddError(TEXT("Mission id must be M04_NightBlackout."));
	}
	if (Mission->Route.Points.Num() < 4)
	{
		AddError(TEXT("Mission 4 route requires at least four points."));
	}
	if (Mission->Objectives.Num() != 3)
	{
		AddError(TEXT("Mission 4 requires exactly three objectives."));
	}
	for (const FName RequiredObjective : {
		FName(TEXT("ProtectSubstation")),
		FName(TEXT("HoldSearchlightTrack")),
		FName(TEXT("DefeatBlackKite"))})
	{
		if (!Mission->FindObjective(RequiredObjective))
		{
			AddError(FString::Printf(
				TEXT("Mission 4 is missing objective %s."),
				*RequiredObjective.ToString()));
		}
	}
	const FSkyguardObjectiveDefinition* ProtectObjective =
		Mission->FindObjective(TEXT("ProtectSubstation"));
	const FSkyguardObjectiveDefinition* SearchlightObjective =
		Mission->FindObjective(TEXT("HoldSearchlightTrack"));
	const FSkyguardObjectiveDefinition* DefeatObjective =
		Mission->FindObjective(TEXT("DefeatBlackKite"));
	if ((ProtectObjective && ProtectObjective->RequiredProgress != 1) ||
		(SearchlightObjective &&
			SearchlightObjective->RequiredProgress != 3) ||
		(DefeatObjective && DefeatObjective->RequiredProgress != 4))
	{
		AddError(TEXT(
			"Mission 4 objective progress must be protect=1, "
			"searchlight=3 and boss=4."));
	}
	const TArray<FName> Ids = {
		FName(TEXT("PortNavigationVane")),
		FName(TEXT("StarboardNavigationVane")),
		FName(TEXT("Jammer")), FName(TEXT("PowerBus"))};
	const TArray<FName> Weapons = {
		FName(TEXT("Rifle")), FName(TEXT("Rifle")),
		FName(TEXT("Rifle")), FName(TEXT("Igla"))};
	const TArray<FName> Exposes = {
		FName(TEXT("Jammer")), FName(TEXT("Jammer")),
		FName(TEXT("PowerBus")), NAME_None};
	if (Mission->Boss.BossId != TEXT("BlackKite") ||
		Mission->Boss.DefeatObjectiveId != TEXT("DefeatBlackKite") ||
		Mission->Boss.WeakPoints.Num() != 4 ||
		Mission->Boss.MaximumBreakupPieces > 3)
	{
		AddError(TEXT("Mission 4 Black Kite boss contract is invalid."));
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
					TEXT("Black Kite graph differs at index %d."),
					Index));
			}
		}
	}
	if (Mission->Waves.Num() != 3)
	{
		AddError(TEXT("Mission 4 requires exactly three waves."));
	}
	if (Mission->Weather.ProfileId != TEXT("BlackoutNight"))
	{
		AddError(TEXT("Mission 4 weather must be BlackoutNight."));
	}
	if (Mission->Presentation.Briefing.IsEmpty() ||
		Mission->Presentation.RadioChatter.Num() < 3)
	{
		AddError(TEXT("Mission 4 briefing/radio contract is incomplete."));
	}
	return OutErrors.IsEmpty();
}
