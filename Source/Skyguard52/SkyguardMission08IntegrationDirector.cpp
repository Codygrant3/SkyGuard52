#include "SkyguardMission08IntegrationDirector.h"

#include "SkyguardDrone.h"
#include "SkyguardAudioDirectorComponent.h"
#include "SkyguardCampaignDefinition.h"
#include "SkyguardCampaignSubsystem.h"
#include "SkyguardGunner.h"
#include "SkyguardLifelineHunterBoss.h"
#include "SkyguardMissionBriefingComponent.h"
#include "SkyguardMissionDefinition.h"
#include "SkyguardMissionDirectorCampaignHelpers.h"
#include "SkyguardMissionDirectorPresentationHelpers.h"
#include "SkyguardMissionMapAssemblyDirector.h"
#include "SkyguardObjectiveRuntime.h"
#include "SkyguardRadioChatterComponent.h"
#include "SkyguardSortiePresentationComponent.h"
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
	T* FindFirstMission08Actor(UWorld* World)
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
	T* SpawnMission08Actor(
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

ASkyguardMission08IntegrationDirector::ASkyguardMission08IntegrationDirector()
{
	PrimaryActorTick.bCanEverTick = true;
	Root = CreateDefaultSubobject<USceneComponent>(
		TEXT("Mission08IntegrationRoot"));
	SetRootComponent(Root);
	RescueHelicopterAnchor = CreateDefaultSubobject<USceneComponent>(
		TEXT("RescueHelicopterAnchor"));
	RescueHelicopterAnchor->SetupAttachment(Root);
	HoistCableAnchor = CreateDefaultSubobject<USceneComponent>(
		TEXT("HoistCableAnchor"));
	HoistCableAnchor->SetupAttachment(RescueHelicopterAnchor);
	SurvivorsAnchor = CreateDefaultSubobject<USceneComponent>(
		TEXT("SurvivorsAnchor"));
	SurvivorsAnchor->SetupAttachment(Root);
	RaftsAnchor = CreateDefaultSubobject<USceneComponent>(
		TEXT("RaftsAnchor"));
	RaftsAnchor->SetupAttachment(Root);
	RescueVesselAnchor = CreateDefaultSubobject<USceneComponent>(
		TEXT("RescueVesselAnchor"));
	RescueVesselAnchor->SetupAttachment(Root);
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
			TEXT("/Game/Skyguard/Data/Campaign_v1/DA_Mission_M08_RescueCover.DA_Mission_M08_RescueCover")));
	Tags.AddUnique(TEXT("Skyguard.Mission08.PlayableIntegration"));
	Tags.AddUnique(TEXT("Skyguard.PackagePrep.Native"));
}

void ASkyguardMission08IntegrationDirector::BeginPlay()
{
	Super::BeginPlay();
	ASkyguardDrone::OnAnyCityImpacted.AddUObject(
		this,
		&ASkyguardMission08IntegrationDirector::HandleDroneCityImpact);
	if (bAutoInitialize)
	{
		InitializePlayableMission();
	}
}

void ASkyguardMission08IntegrationDirector::EndPlay(
	const EEndPlayReason::Type EndPlayReason)
{
	ASkyguardDrone::OnAnyCityImpacted.RemoveAll(this);
	if (LifelineHunter)
	{
		LifelineHunter->OnBossPhaseChanged.RemoveDynamic(
			this,
			&ASkyguardMission08IntegrationDirector::HandleBossPhaseChanged);
		LifelineHunter->OnPilotCommandNative.RemoveAll(this);
	}
	Super::EndPlay(EndPlayReason);
}

void ASkyguardMission08IntegrationDirector::HandleDroneCityImpact(
	ASkyguardDrone* Drone)
{
	if (!Drone || !bInitialized || bMissionCompleted)
	{
		return;
	}
	NotifyProtectedAssetFailed();
}

bool ASkyguardMission08IntegrationDirector::NotifyProtectedAssetFailed()
{
	return NotifyProtectedTargetDamage(
		ESkyguardMission08ProtectedTarget::RescueHelicopter,
		FMath::Max(MaximumProtectedTargetIntegrity, 1));
}

void ASkyguardMission08IntegrationDirector::Tick(const float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	if (!bInitialized)
	{
		return;
	}
	Briefing->AdvanceBriefing(DeltaSeconds);
	TryLaunchSortie();
	TickStormRainBeatKit(DeltaSeconds);
	UpdateRescueAnimation(DeltaSeconds);
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

bool ASkyguardMission08IntegrationDirector::InitializePlayableMission()
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

bool ASkyguardMission08IntegrationDirector::ConfigureMissionDefinition(
	USkyguardMissionDefinition* Mission)
{
	TArray<FText> Errors;
	if (!ValidateMissionContract(Mission, Errors))
	{
		return false;
	}
	ResolvedMission = Mission;
	LocalObjectiveRuntime = NewObject<USkyguardObjectiveRuntime>(
		this, TEXT("Mission08LocalObjectives"));
	LocalObjectiveRuntime->InitializeObjectives(Mission->Objectives);
	WaveState = ESkyguardMission08WaveState::AwaitingWave;
	CurrentWaveIndex = -1;
	RemainingThreatsInWave = 0;
	ObservedBossWeakPointsDestroyed = 0;
	RejectedWeaponReleases = 0;
	RescueAnimationSeconds = 0.f;
	HoistRuntime = FSkyguardHoistWindowRuntime();
	StormRainBeatIndex = 0;
	StormRainBeatElapsed = 0.f;
	ProtectedTargets.Reset();
	for (const ESkyguardMission08ProtectedTarget Target : {
		ESkyguardMission08ProtectedTarget::RescueHelicopter,
		ESkyguardMission08ProtectedTarget::SurvivorsAndRafts,
		ESkyguardMission08ProtectedTarget::RescueVessel})
	{
		FSkyguardMission08ProtectedTargetRuntime Runtime;
		Runtime.Target = Target;
		Runtime.Integrity = MaximumProtectedTargetIntegrity;
		ProtectedTargets.Add(Runtime);
	}
	bMissionCompleted = false;
	return true;
}

void ASkyguardMission08IntegrationDirector::ResolveOrSpawnActors()
{
	UWorld* World = GetWorld();
	MapAssembly =
		FindFirstMission08Actor<ASkyguardMissionMapAssemblyDirector>(World);
	YakAircraft = FindFirstMission08Actor<ASkyguardYak52Aircraft>(World);
	Gunner = FindFirstMission08Actor<ASkyguardGunner>(World);
	LifelineHunter =
		FindFirstMission08Actor<ASkyguardLifelineHunterBoss>(World);
	if (bAllowBoundedActorSpawning)
	{
		if (!YakAircraft)
		{
			YakAircraft = SpawnMission08Actor<ASkyguardYak52Aircraft>(
				World, YakSpawnLocation, YakSpawnRotation);
		}
		if (!Gunner)
		{
			Gunner = SpawnMission08Actor<ASkyguardGunner>(
				World, YakSpawnLocation, YakSpawnRotation);
		}
		if (!LifelineHunter)
		{
			LifelineHunter =
				SpawnMission08Actor<ASkyguardLifelineHunterBoss>(
					World,
					LifelineHunterSpawnLocation,
					LifelineHunterSpawnRotation);
		}
	}
	BindRuntimeActors(
		MapAssembly, YakAircraft, Gunner, LifelineHunter);
}

void ASkyguardMission08IntegrationDirector::BindRuntimeActors(
	ASkyguardMissionMapAssemblyDirector* InMapAssembly,
	ASkyguardYak52Aircraft* Aircraft,
	ASkyguardGunner* InGunner,
	ASkyguardLifelineHunterBoss* InLifelineHunter)
{
	if (LifelineHunter && LifelineHunter != InLifelineHunter)
	{
		LifelineHunter->OnBossPhaseChanged.RemoveDynamic(
			this,
			&ASkyguardMission08IntegrationDirector::HandleBossPhaseChanged);
		LifelineHunter->OnPilotCommandNative.RemoveAll(this);
	}
	MapAssembly = InMapAssembly;
	YakAircraft = Aircraft;
	Gunner = InGunner;
	if (Gunner)
	{
		Gunner->ResetSortieCombatStats();
		ApplyStormRainPlayContract(Gunner);
	}
	LifelineHunter = InLifelineHunter;
	ObservedBossWeakPointsDestroyed =
		LifelineHunter
			? LifelineHunter->GetTelemetry().WeakPointsDestroyed
			: 0;
	if (YakAircraft)
	{
		YakAircraft->SetEnginePower(0.82f);
		YakAircraft->SetRearCanopyOpen(true);
	}
	FSkyguardPlayerAircraft::AttachGunner(Gunner, YakAircraft);
	if (LifelineHunter)
	{
		LifelineHunter->OnBossPhaseChanged.AddUniqueDynamic(
			this,
			&ASkyguardMission08IntegrationDirector::HandleBossPhaseChanged);
		LifelineHunter->OnPilotCommandNative.RemoveAll(this);
		LifelineHunter->OnPilotCommandNative.AddUObject(
			this,
			&ASkyguardMission08IntegrationDirector::HandlePilotCommand);
	}
	UpdateReadiness();
}

bool ASkyguardMission08IntegrationDirector::StartNextWave()
{
	if (!ResolvedMission ||
		WaveState != ESkyguardMission08WaveState::AwaitingWave)
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
	WaveState = ESkyguardMission08WaveState::WaveActive;
	return true;
}

bool ASkyguardMission08IntegrationDirector::NotifyThreatDestroyed(
	const int32 Amount)
{
	if (WaveState != ESkyguardMission08WaveState::WaveActive ||
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
			? ESkyguardMission08WaveState::BossEngaged
			: ESkyguardMission08WaveState::AwaitingWave;
	}
	return true;
}

bool ASkyguardMission08IntegrationDirector::StartHoistWindow(
	const float WindowSeconds)
{
	if (WindowSeconds <= 0.f || HoistRuntime.bActive ||
		HoistRuntime.CompletedWindows >= 3 ||
		(WaveState != ESkyguardMission08WaveState::WaveActive &&
			WaveState != ESkyguardMission08WaveState::BossEngaged))
	{
		return false;
	}
	HoistRuntime.bActive = true;
	HoistRuntime.RemainingSeconds = WindowSeconds;
	HoistRuntime.CoveredSeconds = 0.f;
	return true;
}

bool ASkyguardMission08IntegrationDirector::AdvanceHoistWindow(
	const float DeltaSeconds,
	const bool bCoverMaintained)
{
	if (!HoistRuntime.bActive || DeltaSeconds <= 0.f)
	{
		return false;
	}
	HoistRuntime.RemainingSeconds =
		FMath::Max(0.f, HoistRuntime.RemainingSeconds - DeltaSeconds);
	HoistRuntime.CoveredSeconds = bCoverMaintained
		? HoistRuntime.CoveredSeconds + DeltaSeconds
		: 0.f;
	if (HoistRuntime.CoveredSeconds >= RequiredCoveredSeconds)
	{
		HoistRuntime.bActive = false;
		++HoistRuntime.CompletedWindows;
		NotifyObjectiveProgress(TEXT("CompleteHoistWindows"), 1);
		return true;
	}
	if (HoistRuntime.RemainingSeconds <= 0.f)
	{
		HoistRuntime.bActive = false;
		NotifyProtectedTargetDamage(
			ESkyguardMission08ProtectedTarget::SurvivorsAndRafts, 35);
		return false;
	}
	return true;
}

bool ASkyguardMission08IntegrationDirector::ValidateWeaponRelease(
	const float FriendlySeparationMeters,
	const bool bShotIntersectsFriendlyCorridor)
{
	const bool bSafe =
		!bShotIntersectsFriendlyCorridor &&
		FriendlySeparationMeters >= MinimumWeaponSeparationMeters;
	if (!bSafe)
	{
		++RejectedWeaponReleases;
		return false;
	}
	if (LifelineHunter)
	{
		LifelineHunter->SetFriendlySeparationMeters(
			FriendlySeparationMeters);
	}
	return true;
}

bool ASkyguardMission08IntegrationDirector::NotifyProtectedTargetDamage(
	const ESkyguardMission08ProtectedTarget Target,
	const int32 Damage)
{
	FSkyguardMission08ProtectedTargetRuntime* Runtime =
		FindProtectedTarget(Target);
	if (!Runtime || Damage <= 0 || Runtime->bDestroyed ||
		WaveState == ESkyguardMission08WaveState::Completed)
	{
		return false;
	}
	Runtime->Integrity = FMath::Max(0, Runtime->Integrity - Damage);
	Runtime->bDestroyed = Runtime->Integrity == 0;
	if (Runtime->bDestroyed)
	{
		static const FName ProtectObjective(TEXT("ProtectRescueFlight"));
		if (CampaignRuntime &&
			CampaignRuntime->GetActiveMission() == ResolvedMission)
		{
			CampaignRuntime->FailObjective(ProtectObjective);
		}
		else if (LocalObjectiveRuntime)
		{
			LocalObjectiveRuntime->FailObjective(ProtectObjective);
		}
		WaveState = ESkyguardMission08WaveState::Failed;

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

void ASkyguardMission08IntegrationDirector::SynchronizeRuntimeState()
{
	if (!LifelineHunter || !ResolvedMission)
	{
		return;
	}
	const int32 Destroyed = FMath::Clamp(
		LifelineHunter->GetTelemetry().WeakPointsDestroyed, 0, 4);
	const int32 NewDestroyed =
		FMath::Max(0, Destroyed - ObservedBossWeakPointsDestroyed);
	if (NewDestroyed > 0)
	{
		NotifyObjectiveProgress(TEXT("DefeatLifelineHunter"), NewDestroyed);
		ObservedBossWeakPointsDestroyed = Destroyed;
	}
	if (LifelineHunter->GetBossPhase() ==
			ESkyguardBossPhase::Defeated &&
		LifelineHunter->IsCrashRedirected())
	{
		CompleteMissionIfReady();
	}
	UpdateReadiness();
}

bool ASkyguardMission08IntegrationDirector::NotifyObjectiveProgress(
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

int32 ASkyguardMission08IntegrationDirector::CalculateWaveThreatCount(
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

FSkyguardMission08ProtectedTargetRuntime*
ASkyguardMission08IntegrationDirector::FindProtectedTarget(
	const ESkyguardMission08ProtectedTarget Target)
{
	return ProtectedTargets.FindByPredicate(
		[Target](const FSkyguardMission08ProtectedTargetRuntime& Runtime)
		{
			return Runtime.Target == Target;
		});
}

const FSkyguardMission08ProtectedTargetRuntime*
ASkyguardMission08IntegrationDirector::FindProtectedTarget(
	const ESkyguardMission08ProtectedTarget Target) const
{
	return ProtectedTargets.FindByPredicate(
		[Target](const FSkyguardMission08ProtectedTargetRuntime& Runtime)
		{
			return Runtime.Target == Target;
		});
}

FSkyguardMission08ProtectedTargetRuntime
ASkyguardMission08IntegrationDirector::GetProtectedTarget(
	const ESkyguardMission08ProtectedTarget Target) const
{
	const FSkyguardMission08ProtectedTargetRuntime* Runtime =
		FindProtectedTarget(Target);
	return Runtime
		? *Runtime
		: FSkyguardMission08ProtectedTargetRuntime();
}

int32 ASkyguardMission08IntegrationDirector::GetSurvivingTargetCount() const
{
	int32 Count = 0;
	for (const FSkyguardMission08ProtectedTargetRuntime& Runtime :
		ProtectedTargets)
	{
		if (!Runtime.bDestroyed && Runtime.Integrity > 0)
		{
			++Count;
		}
	}
	return Count;
}

void ASkyguardMission08IntegrationDirector::UpdateRescueAnimation(
	const float DeltaSeconds)
{
	if (DeltaSeconds <= 0.f)
	{
		return;
	}
	RescueAnimationSeconds += DeltaSeconds;
	const float Angle = RescueAnimationSeconds * 0.22f;
	RescueHelicopterAnchor->SetRelativeLocation(
		FVector(
			39000.f + FMath::Cos(Angle) * 2400.f,
			18000.f + FMath::Sin(Angle) * 2400.f,
			5000.f + FMath::Sin(Angle * 2.f) * 70.f));
	HoistCableAnchor->SetRelativeLocation(
		FVector(0.f, 0.f, -650.f - FMath::Sin(Angle * 3.f) * 120.f));
	SurvivorsAnchor->SetRelativeLocation(
		FVector(42000.f, 8000.f, -80.f));
	RaftsAnchor->SetRelativeLocation(
		FVector(42000.f, 8000.f, -100.f + FMath::Sin(Angle * 2.5f) * 25.f));
	RescueVesselAnchor->SetRelativeLocation(
		FVector(
			28000.f + FMath::Sin(Angle * 0.6f) * 300.f,
			3000.f,
			-50.f + FMath::Sin(Angle * 2.f) * 18.f));
}

void ASkyguardMission08IntegrationDirector::ConfigurePresentation()
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
			*FString::Printf(TEXT("M08_Briefing_%02d"), Index + 1));
		Line.Speaker = Index == 0
			? FText::FromString(TEXT("Rescue One"))
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

void ASkyguardMission08IntegrationDirector::TryLaunchSortie()
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
		WaveState == ESkyguardMission08WaveState::AwaitingWave)
	{
		StartNextWave();
	}
}

void ASkyguardMission08IntegrationDirector::CompleteMissionIfReady()
{
	if (bMissionCompleted ||
		WaveState != ESkyguardMission08WaveState::BossEngaged ||
		HoistRuntime.CompletedWindows != 3 ||
		GetSurvivingTargetCount() != 3 || !LifelineHunter ||
		LifelineHunter->GetBossPhase() != ESkyguardBossPhase::Defeated ||
		!LifelineHunter->IsCrashRedirected())
	{
		return;
	}
	static const FName ProtectObjective(TEXT("ProtectRescueFlight"));
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
		WaveState = ESkyguardMission08WaveState::Completed;
	}
}

void ASkyguardMission08IntegrationDirector::HandleBossPhaseChanged(
	ESkyguardBossPhase PreviousPhase,
	const ESkyguardBossPhase NewPhase)
{
	SynchronizeRuntimeState();
	if (NewPhase == ESkyguardBossPhase::Defeated && AudioDirector)
	{
		AudioDirector->TriggerEvent(
			ESkyguardAudioEvent::ExplosionHeavy,
			LifelineHunter
				? LifelineHunter->GetActorLocation()
				: GetActorLocation());
	}
}

void ASkyguardMission08IntegrationDirector::HandlePilotCommand(
	const ESkyguardPilotCommand Command)
{
	if (YakAircraft)
	{
		YakAircraft->IssuePilotCommand(Command);
	}
}

const FSkyguardStormRainBeatKit&
ASkyguardMission08IntegrationDirector::GetStormRainBeatKit()
{
	return SkyguardStormRainBeatKits::IronRain();
}

bool ASkyguardMission08IntegrationDirector::ApplyStormRainPlayContract(
	ASkyguardGunner* InGunner) const
{
	return SkyguardStormRainBeatKits::ApplyHydraForClusters(
		InGunner,
		GetStormRainBeatKit());
}

ESkyguardStormRainBeatKind
ASkyguardMission08IntegrationDirector::GetStormRainBeatKind() const
{
	const int32 Safe = FMath::Clamp(
		StormRainBeatIndex,
		0,
		FSkyguardStormRainBeatKit::BeatCount - 1);
	return GetStormRainBeatKit().Kinds[Safe];
}

void ASkyguardMission08IntegrationDirector::TickStormRainBeatKit(
	const float ElapsedSeconds)
{
	StormRainBeatElapsed += FMath::Max(ElapsedSeconds, 0.f);
	StormRainBeatIndex = SkyguardStormRainBeatKits::BeatIndexForElapsed(
		GetMissionId(),
		StormRainBeatElapsed);
}

USkyguardObjectiveRuntime*
ASkyguardMission08IntegrationDirector::GetObjectiveRuntime() const
{
	if (CampaignRuntime &&
		CampaignRuntime->GetActiveMission() == ResolvedMission)
	{
		return CampaignRuntime->GetObjectiveRuntime();
	}
	return LocalObjectiveRuntime;
}

bool ASkyguardMission08IntegrationDirector::IsCorePlayableReady() const
{
	return Readiness.bMissionDefinitionValid &&
		Readiness.bCampaignDefinitionValid &&
		Readiness.bMapAssemblyReady &&
		Readiness.bYakRuntimeReady &&
		Readiness.bGunnerReady &&
		Readiness.bLifelineHunterReady &&
		Readiness.bObjectivesReady &&
		Readiness.bWavesReady &&
		Readiness.bRescueAnimationReady &&
		Readiness.bProtectedTargetsReady &&
		Readiness.bBriefingReady &&
		Readiness.bAudioReady &&
		Readiness.bSortiePresentationReady;
}

void ASkyguardMission08IntegrationDirector::UpdateReadiness()
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
	Readiness.bLifelineHunterReady =
		LifelineHunter && LifelineHunter->OpticalTracker &&
		LifelineHunter->WeaponServo &&
		LifelineHunter->CountermeasurePod &&
		LifelineHunter->Engine &&
		LifelineHunter->GetMaxDefeatDebrisPieces() <= 3;
	Readiness.bObjectivesReady =
		GetObjectiveRuntime() && ResolvedMission &&
		ResolvedMission->Objectives.Num() == 3;
	Readiness.bWavesReady =
		ResolvedMission && ResolvedMission->Waves.Num() == 3 &&
		CalculateWaveThreatCount(0) == 2 &&
		CalculateWaveThreatCount(1) == 3 &&
		CalculateWaveThreatCount(2) == 4;
	Readiness.bRescueAnimationReady =
		RescueHelicopterAnchor && HoistCableAnchor &&
		SurvivorsAnchor && RaftsAnchor && RescueVesselAnchor;
	Readiness.bProtectedTargetsReady =
		ProtectedTargets.Num() == 3 &&
		FindProtectedTarget(
			ESkyguardMission08ProtectedTarget::RescueHelicopter) &&
		FindProtectedTarget(
			ESkyguardMission08ProtectedTarget::SurvivorsAndRafts) &&
		FindProtectedTarget(
			ESkyguardMission08ProtectedTarget::RescueVessel);
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

bool ASkyguardMission08IntegrationDirector::ValidateMissionContract(
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
		AddError(TEXT("Mission id must be M08_RescueCover."));
	}
	if (Mission->Route.Points.Num() < 4)
	{
		AddError(TEXT("Mission 8 rescue orbit requires four route points."));
	}
	if (Mission->Objectives.Num() != 3)
	{
		AddError(TEXT("Mission 8 requires exactly three objectives."));
	}
	for (const FName RequiredObjective : {
		FName(TEXT("ProtectRescueFlight")),
		FName(TEXT("CompleteHoistWindows")),
		FName(TEXT("DefeatLifelineHunter"))})
	{
		if (!Mission->FindObjective(RequiredObjective))
		{
			AddError(FString::Printf(
				TEXT("Mission 8 is missing objective %s."),
				*RequiredObjective.ToString()));
		}
	}
	const FSkyguardObjectiveDefinition* Protect =
		Mission->FindObjective(TEXT("ProtectRescueFlight"));
	const FSkyguardObjectiveDefinition* Hoists =
		Mission->FindObjective(TEXT("CompleteHoistWindows"));
	const FSkyguardObjectiveDefinition* Defeat =
		Mission->FindObjective(TEXT("DefeatLifelineHunter"));
	if ((Protect && Protect->RequiredProgress != 1) ||
		(Hoists && Hoists->RequiredProgress != 3) ||
		(Defeat && Defeat->RequiredProgress != 4))
	{
		AddError(TEXT(
			"Mission 8 objective progress must be protect=1, "
			"hoists=3 and boss=4."));
	}
	const TArray<FName> Ids = {
		FName(TEXT("OpticalTracker")),
		FName(TEXT("WeaponServo")),
		FName(TEXT("CountermeasurePod")),
		FName(TEXT("Engine"))};
	const TArray<FName> Weapons = {
		FName(TEXT("Rifle")), FName(TEXT("Rifle")),
		FName(TEXT("Rifle")), FName(TEXT("Igla"))};
	const TArray<FName> Exposes = {
		FName(TEXT("WeaponServo")),
		FName(TEXT("CountermeasurePod")),
		FName(TEXT("Engine")), NAME_None};
	if (Mission->Boss.BossId != TEXT("LifelineHunter") ||
		Mission->Boss.DefeatObjectiveId !=
			TEXT("DefeatLifelineHunter") ||
		Mission->Boss.WeakPoints.Num() != 4 ||
		Mission->Boss.MaximumBreakupPieces > 3)
	{
		AddError(TEXT(
			"Mission 8 Lifeline Hunter boss contract is invalid."));
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
					TEXT("Lifeline Hunter graph differs at index %d."),
					Index));
			}
		}
	}
	if (Mission->Waves.Num() != 3)
	{
		AddError(TEXT("Mission 8 requires exactly three waves."));
	}
	if (Mission->Weather.ProfileId != TEXT("RescueSunset"))
	{
		AddError(TEXT("Mission 8 weather must be RescueSunset."));
	}
	if (Mission->Presentation.Briefing.IsEmpty() ||
		Mission->Presentation.RadioChatter.Num() < 3)
	{
		AddError(TEXT("Mission 8 briefing/radio contract is incomplete."));
	}
	return OutErrors.IsEmpty();
}
