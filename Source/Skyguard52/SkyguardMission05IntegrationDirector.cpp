#include "SkyguardMission05IntegrationDirector.h"

#include "SkyguardDrone.h"
#include "SkyguardAudioDirectorComponent.h"
#include "SkyguardBossWeakPointComponent.h"
#include "SkyguardCampaignDefinition.h"
#include "SkyguardCampaignSubsystem.h"
#include "SkyguardGunner.h"
#include "SkyguardMissionBriefingComponent.h"
#include "SkyguardMissionDefinition.h"
#include "SkyguardMissionDirectorCampaignHelpers.h"
#include "SkyguardMissionDirectorPresentationHelpers.h"
#include "SkyguardMissionMapAssemblyDirector.h"
#include "SkyguardObjectiveRuntime.h"
#include "SkyguardRadioChatterComponent.h"
#include "SkyguardSortiePresentationComponent.h"
#include "SkyguardTempestBoss.h"
#include "SkyguardPlayerAircraft.h"
#include "SkyguardStormRainBeatKit.h"
#include "SkyguardYak52Aircraft.h"
#include "Components/SceneComponent.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "EngineUtils.h"

namespace
{
	template <typename T>
	T* FindFirstMission05Actor(UWorld* World)
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
	T* SpawnMission05Actor(
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

ASkyguardMission05IntegrationDirector::ASkyguardMission05IntegrationDirector()
{
	PrimaryActorTick.bCanEverTick = true;
	Root = CreateDefaultSubobject<USceneComponent>(
		TEXT("Mission05IntegrationRoot"));
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
			TEXT("/Game/Skyguard/Data/Campaign_v1/DA_Mission_M05_StormFront.DA_Mission_M05_StormFront")));
	Tags.AddUnique(TEXT("Skyguard.Mission05.PlayableIntegration"));
	Tags.AddUnique(TEXT("Skyguard.PackagePrep.Native"));
}

void ASkyguardMission05IntegrationDirector::BeginPlay()
{
	Super::BeginPlay();
	ASkyguardDrone::OnAnyCityImpacted.AddUObject(
		this,
		&ASkyguardMission05IntegrationDirector::HandleDroneCityImpact);
	if (bAutoInitialize)
	{
		InitializePlayableMission();
	}
}

void ASkyguardMission05IntegrationDirector::EndPlay(
	const EEndPlayReason::Type EndPlayReason)
{
	ASkyguardDrone::OnAnyCityImpacted.RemoveAll(this);
	if (Tempest)
	{
		Tempest->OnBossPhaseChanged.RemoveDynamic(
			this,
			&ASkyguardMission05IntegrationDirector::HandleBossPhaseChanged);
		Tempest->OnPilotCommandNative.RemoveAll(this);
	}
	Super::EndPlay(EndPlayReason);
}

void ASkyguardMission05IntegrationDirector::HandleDroneCityImpact(
	ASkyguardDrone* Drone)
{
	if (!Drone || !bInitialized || bMissionCompleted)
	{
		return;
	}
	NotifyProtectedAssetFailed();
}

bool ASkyguardMission05IntegrationDirector::NotifyProtectedAssetFailed()
{
	return NotifyProtectedTargetDamage(
		ESkyguardMission05ProtectedTarget::OffshorePlatform,
		FMath::Max(MaximumProtectedTargetIntegrity, 1));
}

void ASkyguardMission05IntegrationDirector::Tick(const float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	if (!bInitialized)
	{
		return;
	}
	Briefing->AdvanceBriefing(DeltaSeconds);
	TryLaunchSortie();
	TickStormRainBeatKit(DeltaSeconds);
	if (StormRuntime.bLightningActive)
	{
		AdvanceLightningWindow(DeltaSeconds);
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

bool ASkyguardMission05IntegrationDirector::InitializePlayableMission()
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

bool ASkyguardMission05IntegrationDirector::ConfigureMissionDefinition(
	USkyguardMissionDefinition* Mission)
{
	TArray<FText> Errors;
	if (!ValidateMissionContract(Mission, Errors))
	{
		return false;
	}
	ResolvedMission = Mission;
	LocalObjectiveRuntime = NewObject<USkyguardObjectiveRuntime>(
		this, TEXT("Mission05LocalObjectives"));
	LocalObjectiveRuntime->InitializeObjectives(Mission->Objectives);
	WaveState = ESkyguardMission05WaveState::AwaitingWave;
	CurrentWaveIndex = -1;
	RemainingThreatsInWave = 0;
	ObservedBossWeakPointsDestroyed = 0;
	ObservedDischargeBoomsDestroyed = 0;
	StormRuntime = FSkyguardStormRuntime();
	StormRainBeatIndex = 0;
	StormRainBeatElapsed = 0.f;
	ProtectedTargets.Reset();
	for (const ESkyguardMission05ProtectedTarget Target : {
		ESkyguardMission05ProtectedTarget::OffshorePlatform,
		ESkyguardMission05ProtectedTarget::DistressedTrawler})
	{
		FSkyguardMission05ProtectedTargetRuntime Runtime;
		Runtime.Target = Target;
		Runtime.Integrity = MaximumProtectedTargetIntegrity;
		ProtectedTargets.Add(Runtime);
	}
	bMissionCompleted = false;
	return true;
}

void ASkyguardMission05IntegrationDirector::ResolveOrSpawnActors()
{
	UWorld* World = GetWorld();
	MapAssembly =
		FindFirstMission05Actor<ASkyguardMissionMapAssemblyDirector>(World);
	YakAircraft = FindFirstMission05Actor<ASkyguardYak52Aircraft>(World);
	Gunner = FindFirstMission05Actor<ASkyguardGunner>(World);
	Tempest = FindFirstMission05Actor<ASkyguardTempestBoss>(World);
	if (bAllowBoundedActorSpawning)
	{
		if (!YakAircraft)
		{
			YakAircraft = SpawnMission05Actor<ASkyguardYak52Aircraft>(
				World, YakSpawnLocation, YakSpawnRotation);
		}
		if (!Gunner)
		{
			Gunner = SpawnMission05Actor<ASkyguardGunner>(
				World, YakSpawnLocation, YakSpawnRotation);
		}
		if (!Tempest)
		{
			Tempest = SpawnMission05Actor<ASkyguardTempestBoss>(
				World, TempestSpawnLocation, TempestSpawnRotation);
		}
	}
	BindRuntimeActors(MapAssembly, YakAircraft, Gunner, Tempest);
}

void ASkyguardMission05IntegrationDirector::BindRuntimeActors(
	ASkyguardMissionMapAssemblyDirector* InMapAssembly,
	ASkyguardYak52Aircraft* Aircraft,
	ASkyguardGunner* InGunner,
	ASkyguardTempestBoss* InTempest)
{
	if (Tempest && Tempest != InTempest)
	{
		Tempest->OnBossPhaseChanged.RemoveDynamic(
			this,
			&ASkyguardMission05IntegrationDirector::HandleBossPhaseChanged);
		Tempest->OnPilotCommandNative.RemoveAll(this);
	}
	MapAssembly = InMapAssembly;
	YakAircraft = Aircraft;
	Gunner = InGunner;
	if (Gunner)
	{
		Gunner->ResetSortieCombatStats();
		ApplyStormRainPlayContract(Gunner);
	}
	Tempest = InTempest;
	ObservedBossWeakPointsDestroyed =
		Tempest ? Tempest->GetTelemetry().WeakPointsDestroyed : 0;
	ObservedDischargeBoomsDestroyed = CountDestroyedDischargeBooms();
	if (YakAircraft)
	{
		YakAircraft->SetEnginePower(0.82f);
		YakAircraft->SetRearCanopyOpen(true);
	}
	FSkyguardPlayerAircraft::AttachGunner(Gunner, YakAircraft);
	if (Tempest)
	{
		Tempest->OnBossPhaseChanged.AddUniqueDynamic(
			this,
			&ASkyguardMission05IntegrationDirector::HandleBossPhaseChanged);
		Tempest->OnPilotCommandNative.RemoveAll(this);
		Tempest->OnPilotCommandNative.AddUObject(
			this,
			&ASkyguardMission05IntegrationDirector::HandlePilotCommand);
	}
	UpdateReadiness();
}

bool ASkyguardMission05IntegrationDirector::StartNextWave()
{
	if (!ResolvedMission ||
		WaveState != ESkyguardMission05WaveState::AwaitingWave)
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
	WaveState = ESkyguardMission05WaveState::WaveActive;
	return true;
}

bool ASkyguardMission05IntegrationDirector::NotifyThreatDestroyed(
	const int32 Amount)
{
	if (WaveState != ESkyguardMission05WaveState::WaveActive ||
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
			? ESkyguardMission05WaveState::BossEngaged
			: ESkyguardMission05WaveState::AwaitingWave;
	}
	return true;
}

bool ASkyguardMission05IntegrationDirector::TriggerLightningWindow(
	const float DurationSeconds)
{
	if (!Tempest || DurationSeconds <= 0.f ||
		StormRuntime.bLightningActive ||
		(WaveState != ESkyguardMission05WaveState::WaveActive &&
			WaveState != ESkyguardMission05WaveState::BossEngaged))
	{
		return false;
	}
	StormRuntime.bLightningActive = true;
	StormRuntime.LightningRemainingSeconds = DurationSeconds;
	++StormRuntime.LightningFlashCount;
	Tempest->SetLightningExposed(true);
	if (AudioDirector)
	{
		AudioDirector->TriggerEvent(
			ESkyguardAudioEvent::ExplosionSmall,
			Tempest->GetActorLocation());
	}
	return true;
}

bool ASkyguardMission05IntegrationDirector::AdvanceLightningWindow(
	const float DeltaSeconds)
{
	if (!StormRuntime.bLightningActive || DeltaSeconds <= 0.f)
	{
		return false;
	}
	StormRuntime.LightningRemainingSeconds =
		FMath::Max(
			0.f,
			StormRuntime.LightningRemainingSeconds - DeltaSeconds);
	if (StormRuntime.LightningRemainingSeconds <= 0.f)
	{
		StormRuntime.bLightningActive = false;
		Tempest->SetLightningExposed(false);
	}
	return true;
}

bool ASkyguardMission05IntegrationDirector::AdvanceTurbulence(
	const float DeltaSeconds,
	const float Turbulence,
	const bool bMaintainingAim)
{
	if (!Tempest || DeltaSeconds <= 0.f ||
		WaveState == ESkyguardMission05WaveState::Failed ||
		WaveState == ESkyguardMission05WaveState::Completed)
	{
		return false;
	}
	StormRuntime.Turbulence = FMath::Clamp(Turbulence, 0.f, 1.f);
	StormRuntime.bMaintainingAim = bMaintainingAim;
	Tempest->ApplyCorrectiveBankGust(StormRuntime.Turbulence);
	if (!bMaintainingAim)
	{
		Tempest->AdvanceStabilizedIglaLock(
			0.f, StormRuntime.Turbulence);
		return true;
	}
	return Tempest->AdvanceStabilizedIglaLock(
		DeltaSeconds, StormRuntime.Turbulence);
}

bool ASkyguardMission05IntegrationDirector::NotifyProtectedTargetDamage(
	const ESkyguardMission05ProtectedTarget Target,
	const int32 Damage)
{
	FSkyguardMission05ProtectedTargetRuntime* Runtime =
		FindProtectedTarget(Target);
	if (!Runtime || Damage <= 0 || Runtime->bDestroyed ||
		WaveState == ESkyguardMission05WaveState::Completed)
	{
		return false;
	}
	Runtime->Integrity = FMath::Max(0, Runtime->Integrity - Damage);
	Runtime->bDestroyed = Runtime->Integrity == 0;
	if (Runtime->bDestroyed)
	{
		static const FName ProtectObjective(TEXT("ProtectOffshoreCrew"));
		if (CampaignRuntime &&
			CampaignRuntime->GetActiveMission() == ResolvedMission)
		{
			CampaignRuntime->FailObjective(ProtectObjective);
		}
		else if (LocalObjectiveRuntime)
		{
			LocalObjectiveRuntime->FailObjective(ProtectObjective);
		}
		WaveState = ESkyguardMission05WaveState::Failed;

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

void ASkyguardMission05IntegrationDirector::SynchronizeRuntimeState()
{
	if (!Tempest || !ResolvedMission)
	{
		return;
	}
	const int32 DestroyedBooms = CountDestroyedDischargeBooms();
	const int32 NewBooms =
		FMath::Max(0, DestroyedBooms - ObservedDischargeBoomsDestroyed);
	if (NewBooms > 0)
	{
		NotifyObjectiveProgress(TEXT("DisableDischargeBooms"), NewBooms);
		ObservedDischargeBoomsDestroyed = DestroyedBooms;
	}
	const int32 Destroyed = FMath::Clamp(
		Tempest->GetTelemetry().WeakPointsDestroyed, 0, 4);
	const int32 NewDestroyed =
		FMath::Max(0, Destroyed - ObservedBossWeakPointsDestroyed);
	if (NewDestroyed > 0)
	{
		NotifyObjectiveProgress(TEXT("DefeatTempest"), NewDestroyed);
		ObservedBossWeakPointsDestroyed = Destroyed;
	}
	if (Tempest->GetBossPhase() == ESkyguardBossPhase::Defeated)
	{
		CompleteMissionIfReady();
	}
	UpdateReadiness();
}

bool ASkyguardMission05IntegrationDirector::NotifyObjectiveProgress(
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

int32 ASkyguardMission05IntegrationDirector::CalculateWaveThreatCount(
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
ASkyguardMission05IntegrationDirector::CountDestroyedDischargeBooms() const
{
	if (!Tempest)
	{
		return 0;
	}
	return (Tempest->PortDischargeBoom->bDestroyed ? 1 : 0) +
		(Tempest->StarboardDischargeBoom->bDestroyed ? 1 : 0);
}

FSkyguardMission05ProtectedTargetRuntime*
ASkyguardMission05IntegrationDirector::FindProtectedTarget(
	const ESkyguardMission05ProtectedTarget Target)
{
	return ProtectedTargets.FindByPredicate(
		[Target](const FSkyguardMission05ProtectedTargetRuntime& Runtime)
		{
			return Runtime.Target == Target;
		});
}

const FSkyguardMission05ProtectedTargetRuntime*
ASkyguardMission05IntegrationDirector::FindProtectedTarget(
	const ESkyguardMission05ProtectedTarget Target) const
{
	return ProtectedTargets.FindByPredicate(
		[Target](const FSkyguardMission05ProtectedTargetRuntime& Runtime)
		{
			return Runtime.Target == Target;
		});
}

FSkyguardMission05ProtectedTargetRuntime
ASkyguardMission05IntegrationDirector::GetProtectedTarget(
	const ESkyguardMission05ProtectedTarget Target) const
{
	const FSkyguardMission05ProtectedTargetRuntime* Runtime =
		FindProtectedTarget(Target);
	return Runtime
		? *Runtime
		: FSkyguardMission05ProtectedTargetRuntime();
}

int32 ASkyguardMission05IntegrationDirector::GetSurvivingTargetCount() const
{
	int32 Count = 0;
	for (const FSkyguardMission05ProtectedTargetRuntime& Runtime :
		ProtectedTargets)
	{
		if (!Runtime.bDestroyed && Runtime.Integrity > 0)
		{
			++Count;
		}
	}
	return Count;
}

void ASkyguardMission05IntegrationDirector::ConfigurePresentation()
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
			*FString::Printf(TEXT("M05_Briefing_%02d"), Index + 1));
		Line.Speaker = Index == 0
			? FText::FromString(TEXT("Trawler Master"))
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
	SkyguardMissionDirectorPresentationHelpers::BindHudHostToPresentation(
		this,
		SortiePresentation);
}

void ASkyguardMission05IntegrationDirector::TryLaunchSortie()
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
		WaveState == ESkyguardMission05WaveState::AwaitingWave)
	{
		StartNextWave();
	}
}

void ASkyguardMission05IntegrationDirector::CompleteMissionIfReady()
{
	if (bMissionCompleted ||
		WaveState != ESkyguardMission05WaveState::BossEngaged ||
		GetSurvivingTargetCount() != 2 || !Tempest ||
		Tempest->GetBossPhase() != ESkyguardBossPhase::Defeated)
	{
		return;
	}
	static const FName ProtectObjective(TEXT("ProtectOffshoreCrew"));
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
		WaveState = ESkyguardMission05WaveState::Completed;
	}
}

void ASkyguardMission05IntegrationDirector::HandleBossPhaseChanged(
	ESkyguardBossPhase PreviousPhase,
	const ESkyguardBossPhase NewPhase)
{
	SynchronizeRuntimeState();
	if (NewPhase == ESkyguardBossPhase::Defeated && AudioDirector)
	{
		AudioDirector->TriggerEvent(
			ESkyguardAudioEvent::ExplosionHeavy,
			Tempest ? Tempest->GetActorLocation() : GetActorLocation());
	}
}

void ASkyguardMission05IntegrationDirector::HandlePilotCommand(
	const ESkyguardPilotCommand Command)
{
	if (YakAircraft)
	{
		YakAircraft->IssuePilotCommand(Command);
	}
}

const FSkyguardStormRainBeatKit&
ASkyguardMission05IntegrationDirector::GetStormRainBeatKit()
{
	return SkyguardStormRainBeatKits::RiverHammer();
}

bool ASkyguardMission05IntegrationDirector::ApplyStormRainPlayContract(
	ASkyguardGunner* InGunner) const
{
	return SkyguardStormRainBeatKits::ApplyHydraForClusters(
		InGunner,
		GetStormRainBeatKit());
}

ESkyguardStormRainBeatKind
ASkyguardMission05IntegrationDirector::GetStormRainBeatKind() const
{
	const int32 Safe = FMath::Clamp(
		StormRainBeatIndex,
		0,
		FSkyguardStormRainBeatKit::BeatCount - 1);
	return GetStormRainBeatKit().Kinds[Safe];
}

void ASkyguardMission05IntegrationDirector::TickStormRainBeatKit(
	const float ElapsedSeconds)
{
	StormRainBeatElapsed += FMath::Max(ElapsedSeconds, 0.f);
	StormRainBeatIndex = SkyguardStormRainBeatKits::BeatIndexForElapsed(
		GetMissionId(),
		StormRainBeatElapsed);
}

USkyguardObjectiveRuntime*
ASkyguardMission05IntegrationDirector::GetObjectiveRuntime() const
{
	if (CampaignRuntime &&
		CampaignRuntime->GetActiveMission() == ResolvedMission)
	{
		return CampaignRuntime->GetObjectiveRuntime();
	}
	return LocalObjectiveRuntime;
}

bool ASkyguardMission05IntegrationDirector::IsCorePlayableReady() const
{
	return Readiness.bMissionDefinitionValid &&
		Readiness.bCampaignDefinitionValid &&
		Readiness.bMapAssemblyReady &&
		Readiness.bYakRuntimeReady &&
		Readiness.bGunnerReady &&
		Readiness.bTempestReady &&
		Readiness.bObjectivesReady &&
		Readiness.bWavesReady &&
		Readiness.bStormRuntimeReady &&
		Readiness.bProtectedTargetsReady &&
		Readiness.bBriefingReady &&
		Readiness.bAudioReady &&
		Readiness.bSortiePresentationReady;
}

void ASkyguardMission05IntegrationDirector::UpdateReadiness()
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
			ESkyguardMissionSkylineStyle::OffshoreStorm &&
		MapAssembly->ValidateAssembly(AssemblyErrors);
	Readiness.bYakRuntimeReady =
		YakAircraft && YakAircraft->GetRearGunnerMount() &&
		YakAircraft->GetRearEyeMount() &&
		YakAircraft->GetRearWeaponMount();
	Readiness.bGunnerReady =
		Gunner && YakAircraft &&
		Gunner->GetAttachParentActor() == YakAircraft;
	Readiness.bTempestReady =
		Tempest && Tempest->PortDischargeBoom &&
		Tempest->StarboardDischargeBoom &&
		Tempest->ControlServo && Tempest->EngineIntake &&
		Tempest->GetMaxDefeatDebrisPieces() <= 3;
	Readiness.bObjectivesReady =
		GetObjectiveRuntime() && ResolvedMission &&
		ResolvedMission->Objectives.Num() == 3;
	Readiness.bWavesReady =
		ResolvedMission && ResolvedMission->Waves.Num() == 3 &&
		CalculateWaveThreatCount(0) == 2 &&
		CalculateWaveThreatCount(1) == 3 &&
		CalculateWaveThreatCount(2) == 4;
	Readiness.bStormRuntimeReady =
		StormRuntime.Turbulence >= 0.f &&
		StormRuntime.Turbulence <= 1.f;
	Readiness.bProtectedTargetsReady =
		ProtectedTargets.Num() == 2 &&
		FindProtectedTarget(
			ESkyguardMission05ProtectedTarget::OffshorePlatform) &&
		FindProtectedTarget(
			ESkyguardMission05ProtectedTarget::DistressedTrawler);
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

bool ASkyguardMission05IntegrationDirector::ValidateMissionContract(
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
		AddError(TEXT("Mission id must be M05_StormFront."));
	}
	if (Mission->Route.Points.Num() < 4)
	{
		AddError(TEXT("Mission 5 route requires at least four points."));
	}
	if (Mission->Objectives.Num() != 3)
	{
		AddError(TEXT("Mission 5 requires exactly three objectives."));
	}
	for (const FName RequiredObjective : {
		FName(TEXT("ProtectOffshoreCrew")),
		FName(TEXT("DisableDischargeBooms")),
		FName(TEXT("DefeatTempest"))})
	{
		if (!Mission->FindObjective(RequiredObjective))
		{
			AddError(FString::Printf(
				TEXT("Mission 5 is missing objective %s."),
				*RequiredObjective.ToString()));
		}
	}
	const FSkyguardObjectiveDefinition* Protect =
		Mission->FindObjective(TEXT("ProtectOffshoreCrew"));
	const FSkyguardObjectiveDefinition* Disable =
		Mission->FindObjective(TEXT("DisableDischargeBooms"));
	const FSkyguardObjectiveDefinition* Defeat =
		Mission->FindObjective(TEXT("DefeatTempest"));
	if ((Protect && Protect->RequiredProgress != 1) ||
		(Disable && Disable->RequiredProgress != 2) ||
		(Defeat && Defeat->RequiredProgress != 4))
	{
		AddError(TEXT(
			"Mission 5 objective progress must be protect=1, "
			"booms=2 and boss=4."));
	}
	const TArray<FName> Ids = {
		FName(TEXT("PortDischargeBoom")),
		FName(TEXT("StarboardDischargeBoom")),
		FName(TEXT("ControlServo")),
		FName(TEXT("EngineIntake"))};
	const TArray<FName> Weapons = {
		FName(TEXT("Rifle")), FName(TEXT("Rifle")),
		FName(TEXT("Rifle")), FName(TEXT("Igla"))};
	const TArray<FName> Exposes = {
		FName(TEXT("ControlServo")), FName(TEXT("ControlServo")),
		FName(TEXT("EngineIntake")), NAME_None};
	if (Mission->Boss.BossId != TEXT("Tempest") ||
		Mission->Boss.DefeatObjectiveId != TEXT("DefeatTempest") ||
		Mission->Boss.WeakPoints.Num() != 4 ||
		Mission->Boss.MaximumBreakupPieces > 3)
	{
		AddError(TEXT("Mission 5 Tempest boss contract is invalid."));
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
					TEXT("Tempest graph differs at index %d."),
					Index));
			}
		}
	}
	if (Mission->Waves.Num() != 3)
	{
		AddError(TEXT("Mission 5 requires exactly three waves."));
	}
	if (Mission->Weather.ProfileId != TEXT("SevereSquall"))
	{
		AddError(TEXT("Mission 5 weather must be SevereSquall."));
	}
	if (Mission->Presentation.Briefing.IsEmpty() ||
		Mission->Presentation.RadioChatter.Num() < 3)
	{
		AddError(TEXT("Mission 5 briefing/radio contract is incomplete."));
	}
	return OutErrors.IsEmpty();
}
