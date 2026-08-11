#include "SkyguardMission02IntegrationDirector.h"

#include "SkyguardAudioDirectorComponent.h"
#include "SkyguardBreakwaterBoss.h"
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
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "EngineUtils.h"

namespace
{
	template <typename T>
	T* FindFirstMission02Actor(UWorld* World)
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
	T* SpawnMission02Actor(
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

ASkyguardMission02IntegrationDirector::ASkyguardMission02IntegrationDirector()
{
	PrimaryActorTick.bCanEverTick = true;

	Root = CreateDefaultSubobject<USceneComponent>(
		TEXT("Mission02IntegrationRoot"));
	SetRootComponent(Root);
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
			TEXT("/Game/Skyguard/Data/Campaign_v1/DA_Mission_M02_HarborShield.DA_Mission_M02_HarborShield")));

	Tags.AddUnique(TEXT("Skyguard.Mission02.PlayableIntegration"));
	Tags.AddUnique(TEXT("Skyguard.PackagePrep.Native"));
}

void ASkyguardMission02IntegrationDirector::BeginPlay()
{
	Super::BeginPlay();
	if (bAutoInitialize)
	{
		InitializePlayableMission();
	}
}

void ASkyguardMission02IntegrationDirector::Tick(const float DeltaSeconds)
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
		AudioDirector->SetEngineState(
			NormalizedRpm, 0.82f, 220.f, 1.f);
	}
}

bool ASkyguardMission02IntegrationDirector::InitializePlayableMission()
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

bool ASkyguardMission02IntegrationDirector::ConfigureMissionDefinition(
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
			this, TEXT("Mission02LocalObjectives"));
	LocalObjectiveRuntime->InitializeObjectives(Mission->Objectives);
	Readiness.ObjectiveCount = Mission->Objectives.Num();
	Readiness.WaveCount = Mission->Waves.Num();
	WaveState = ESkyguardMission02WaveState::AwaitingWave;
	CurrentWaveIndex = -1;
	RemainingThreatsInWave = 0;
	FuelTerminalIntegrity = MaximumFuelTerminalIntegrity;
	ObservedGovernedWeakPointsDestroyed = 0;
	ObservedArmorLatchesDestroyed = 0;
	return true;
}

void ASkyguardMission02IntegrationDirector::ResolveOrSpawnActors()
{
	UWorld* World = GetWorld();
	MapAssembly =
		FindFirstMission02Actor<ASkyguardMissionMapAssemblyDirector>(World);
	YakAircraft = FindFirstMission02Actor<ASkyguardYak52Aircraft>(World);
	Gunner = FindFirstMission02Actor<ASkyguardGunner>(World);
	Breakwater = FindFirstMission02Actor<ASkyguardBreakwaterBoss>(World);

	if (bAllowBoundedActorSpawning)
	{
		if (!YakAircraft)
		{
			YakAircraft = SpawnMission02Actor<ASkyguardYak52Aircraft>(
				World, YakSpawnLocation, YakSpawnRotation);
		}
		if (!Gunner)
		{
			Gunner = SpawnMission02Actor<ASkyguardGunner>(
				World, YakSpawnLocation, YakSpawnRotation);
		}
		if (!Breakwater)
		{
			Breakwater = SpawnMission02Actor<ASkyguardBreakwaterBoss>(
				World, BreakwaterSpawnLocation, BreakwaterSpawnRotation);
		}
	}

	BindRuntimeActors(MapAssembly, YakAircraft, Gunner, Breakwater);
}

void ASkyguardMission02IntegrationDirector::BindRuntimeActors(
	ASkyguardMissionMapAssemblyDirector* InMapAssembly,
	ASkyguardYak52Aircraft* Aircraft,
	ASkyguardGunner* InGunner,
	ASkyguardBreakwaterBoss* InBreakwater)
{
	if (Breakwater && Breakwater != InBreakwater)
	{
		Breakwater->OnBossPhaseChanged.RemoveDynamic(
			this,
			&ASkyguardMission02IntegrationDirector::HandleBossPhaseChanged);
		Breakwater->OnPilotCommandNative.RemoveAll(this);
	}

	MapAssembly = InMapAssembly;
	YakAircraft = Aircraft;
	Gunner = InGunner;
	Breakwater = InBreakwater;
	ObservedGovernedWeakPointsDestroyed = CountGovernedBossProgress();
	ObservedArmorLatchesDestroyed = CountDestroyedArmorLatches();

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
	if (Breakwater)
	{
		Breakwater->OnBossPhaseChanged.AddUniqueDynamic(
			this,
			&ASkyguardMission02IntegrationDirector::HandleBossPhaseChanged);
		Breakwater->OnPilotCommandNative.RemoveAll(this);
		Breakwater->OnPilotCommandNative.AddUObject(
			this,
			&ASkyguardMission02IntegrationDirector::HandlePilotCommand);
	}
	UpdateReadiness();
}

bool ASkyguardMission02IntegrationDirector::StartNextWave()
{
	if (!ResolvedMission ||
		WaveState != ESkyguardMission02WaveState::AwaitingWave)
	{
		return false;
	}

	const int32 NextWaveIndex = CurrentWaveIndex + 1;
	if (!ResolvedMission->Waves.IsValidIndex(NextWaveIndex))
	{
		return false;
	}

	const int32 ThreatCount = CalculateWaveThreatCount(NextWaveIndex);
	if (ThreatCount <= 0)
	{
		return false;
	}

	CurrentWaveIndex = NextWaveIndex;
	RemainingThreatsInWave = ThreatCount;
	WaveState = ESkyguardMission02WaveState::WaveActive;
	return true;
}

bool ASkyguardMission02IntegrationDirector::NotifyThreatDestroyed(
	const int32 Amount)
{
	if (WaveState != ESkyguardMission02WaveState::WaveActive ||
		Amount <= 0)
	{
		return false;
	}

	RemainingThreatsInWave =
		FMath::Max(0, RemainingThreatsInWave - Amount);
	if (RemainingThreatsInWave == 0)
	{
		const bool bLastWave =
			ResolvedMission &&
			CurrentWaveIndex == ResolvedMission->Waves.Num() - 1;
		WaveState = bLastWave
			? ESkyguardMission02WaveState::BossEngaged
			: ESkyguardMission02WaveState::AwaitingWave;
		if (bLastWave)
		{
			SynchronizeRuntimeState();
		}
	}
	return true;
}

bool ASkyguardMission02IntegrationDirector::NotifyFuelTerminalDamage(
	const int32 Damage)
{
	if (Damage <= 0 ||
		WaveState == ESkyguardMission02WaveState::Completed ||
		WaveState == ESkyguardMission02WaveState::Failed)
	{
		return false;
	}

	FuelTerminalIntegrity =
		FMath::Max(0, FuelTerminalIntegrity - Damage);
	if (FuelTerminalIntegrity == 0)
	{
		static const FName ProtectObjective(TEXT("ProtectFuelTerminal"));
		if (CampaignRuntime &&
			CampaignRuntime->GetActiveMission() == ResolvedMission)
		{
			CampaignRuntime->FailObjective(ProtectObjective);
		}
		else if (LocalObjectiveRuntime)
		{
			LocalObjectiveRuntime->FailObjective(ProtectObjective);
		}
		WaveState = ESkyguardMission02WaveState::Failed;
	}
	return true;
}

void ASkyguardMission02IntegrationDirector::SynchronizeRuntimeState()
{
	if (!Breakwater || !ResolvedMission)
	{
		return;
	}

	const int32 ArmorLatchesDestroyed = CountDestroyedArmorLatches();
	const int32 NewArmorLatches =
		FMath::Max(
			0, ArmorLatchesDestroyed - ObservedArmorLatchesDestroyed);
	if (NewArmorLatches > 0)
	{
		NotifyObjectiveProgress(TEXT("StripArmorPanels"), NewArmorLatches);
		ObservedArmorLatchesDestroyed = ArmorLatchesDestroyed;
	}

	const int32 GovernedProgress = CountGovernedBossProgress();
	const int32 NewGovernedProgress =
		FMath::Max(
			0,
			GovernedProgress - ObservedGovernedWeakPointsDestroyed);
	if (NewGovernedProgress > 0)
	{
		NotifyObjectiveProgress(TEXT("DefeatBreakwater"), NewGovernedProgress);
		ObservedGovernedWeakPointsDestroyed = GovernedProgress;
	}

	if (Breakwater->GetBossPhase() == ESkyguardBossPhase::Defeated)
	{
		CompleteMissionIfReady();
	}
	UpdateReadiness();
}

bool ASkyguardMission02IntegrationDirector::NotifyObjectiveProgress(
	const FName ObjectiveId,
	const int32 Amount)
{
	if (!ResolvedMission ||
		ObjectiveId.IsNone() ||
		Amount <= 0 ||
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

int32 ASkyguardMission02IntegrationDirector::CalculateWaveThreatCount(
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

int32 ASkyguardMission02IntegrationDirector::CountGovernedBossProgress() const
{
	if (!Breakwater)
	{
		return 0;
	}

	int32 Count = 0;
	Count += Breakwater->PortLatch->bDestroyed ? 1 : 0;
	Count += Breakwater->StarboardLatch->bDestroyed ? 1 : 0;
	Count += Breakwater->DecoyPods->bDestroyed ? 1 : 0;
	if (Breakwater->Engine->bDestroyed)
	{
		++Count;
	}
	else if (Breakwater->IsEmergencyRifleFinishArmed() &&
		Breakwater->ElevatorLinkage->bDestroyed)
	{
		++Count;
	}
	return FMath::Min(4, Count);
}

int32 ASkyguardMission02IntegrationDirector::CountDestroyedArmorLatches() const
{
	if (!Breakwater)
	{
		return 0;
	}
	return
		(Breakwater->PortLatch->bDestroyed ? 1 : 0) +
		(Breakwater->StarboardLatch->bDestroyed ? 1 : 0);
}

void ASkyguardMission02IntegrationDirector::ConfigurePresentation()
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
			*FString::Printf(TEXT("M02_Briefing_%02d"), Index + 1));
		Line.Speaker = Index == 0
			? FText::FromString(TEXT("Harbor Control"))
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

void ASkyguardMission02IntegrationDirector::TryLaunchSortie()
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
		WaveState == ESkyguardMission02WaveState::AwaitingWave)
	{
		StartNextWave();
	}
}

void ASkyguardMission02IntegrationDirector::CompleteMissionIfReady()
{
	if (bMissionCompleted ||
		WaveState != ESkyguardMission02WaveState::BossEngaged)
	{
		return;
	}

	static const FName ProtectObjective(TEXT("ProtectFuelTerminal"));
	USkyguardObjectiveRuntime* Objectives = GetObjectiveRuntime();
	if (Objectives && FuelTerminalIntegrity > 0)
	{
		const FSkyguardObjectiveProgress ProtectProgress =
			Objectives->GetProgress(ProtectObjective);
		if (ProtectProgress.State ==
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
	}

	Objectives = GetObjectiveRuntime();
	if (!Objectives ||
		Objectives->HasTerminalFailure() ||
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
		WaveState = ESkyguardMission02WaveState::Completed;
	}
}

void ASkyguardMission02IntegrationDirector::HandleBossPhaseChanged(
	ESkyguardBossPhase PreviousPhase,
	const ESkyguardBossPhase NewPhase)
{
	SynchronizeRuntimeState();
	if (NewPhase == ESkyguardBossPhase::Defeated && AudioDirector)
	{
		AudioDirector->TriggerEvent(
			ESkyguardAudioEvent::ExplosionHeavy,
			Breakwater
				? Breakwater->GetActorLocation()
				: GetActorLocation());
	}
}

void ASkyguardMission02IntegrationDirector::HandlePilotCommand(
	const ESkyguardPilotCommand Command)
{
	if (YakAircraft)
	{
		YakAircraft->IssuePilotCommand(Command);
	}
}

USkyguardObjectiveRuntime*
ASkyguardMission02IntegrationDirector::GetObjectiveRuntime() const
{
	if (CampaignRuntime &&
		CampaignRuntime->GetActiveMission() == ResolvedMission)
	{
		return CampaignRuntime->GetObjectiveRuntime();
	}
	return LocalObjectiveRuntime;
}

bool ASkyguardMission02IntegrationDirector::IsCorePlayableReady() const
{
	return Readiness.bMissionDefinitionValid &&
		Readiness.bCampaignDefinitionValid &&
		Readiness.bMapAssemblyReady &&
		Readiness.bYakRuntimeReady &&
		Readiness.bGunnerReady &&
		Readiness.bBreakwaterReady &&
		Readiness.bObjectivesReady &&
		Readiness.bWavesReady &&
		Readiness.bBriefingReady &&
		Readiness.bAudioReady;
}

void ASkyguardMission02IntegrationDirector::UpdateReadiness()
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
		YakAircraft &&
		YakAircraft->GetRearGunnerMount() &&
		YakAircraft->GetRearEyeMount() &&
		YakAircraft->GetRearWeaponMount();
	Readiness.bGunnerReady =
		Gunner && YakAircraft &&
		Gunner->GetAttachParentActor() == YakAircraft;
	Readiness.bBreakwaterReady =
		Breakwater &&
		Breakwater->PortLatch &&
		Breakwater->StarboardLatch &&
		Breakwater->DecoyPods &&
		Breakwater->Engine &&
		Breakwater->ElevatorLinkage &&
		Breakwater->GetMaxDefeatDebrisPieces() <= 3;
	Readiness.bObjectivesReady =
		GetObjectiveRuntime() &&
		ResolvedMission &&
		ResolvedMission->Objectives.Num() == 3;
	Readiness.bWavesReady =
		ResolvedMission &&
		ResolvedMission->Waves.Num() == 3 &&
		CalculateWaveThreatCount(0) == 2 &&
		CalculateWaveThreatCount(1) == 3 &&
		CalculateWaveThreatCount(2) == 4;
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

bool ASkyguardMission02IntegrationDirector::ValidateMissionContract(
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
		AddError(TEXT("Mission id must be M02_HarborShield."));
	}
	if (Mission->Route.Points.Num() < 4)
	{
		AddError(TEXT("Mission 2 route requires at least four points."));
	}
	if (Mission->Objectives.Num() != 3)
	{
		AddError(TEXT("Mission 2 requires exactly three governed objectives."));
	}
	for (const FName RequiredObjective : {
		FName(TEXT("ProtectFuelTerminal")),
		FName(TEXT("StripArmorPanels")),
		FName(TEXT("DefeatBreakwater"))})
	{
		if (!Mission->FindObjective(RequiredObjective))
		{
			AddError(FString::Printf(
				TEXT("Mission 2 is missing objective %s."),
				*RequiredObjective.ToString()));
		}
	}

	const TArray<FName> ExpectedIds = {
		FName(TEXT("PortLatch")),
		FName(TEXT("StarboardLatch")),
		FName(TEXT("DecoyPods")),
		FName(TEXT("Engine"))};
	const TArray<FName> ExpectedWeapons = {
		FName(TEXT("Rifle")),
		FName(TEXT("Rifle")),
		FName(TEXT("Rifle")),
		FName(TEXT("Igla"))};
	const TArray<FName> ExpectedExposes = {
		FName(TEXT("StarboardLatch")),
		FName(TEXT("DecoyPods")),
		FName(TEXT("Engine")),
		NAME_None};
	if (Mission->Boss.BossId != TEXT("Breakwater") ||
		Mission->Boss.DefeatObjectiveId != TEXT("DefeatBreakwater") ||
		Mission->Boss.WeakPoints.Num() != ExpectedIds.Num() ||
		Mission->Boss.MaximumBreakupPieces > 3)
	{
		AddError(TEXT("Mission 2 Breakwater boss contract is invalid."));
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
					TEXT("Breakwater weak-point graph differs at index %d."),
					Index));
			}
		}
	}
	if (Mission->Waves.Num() != 3)
	{
		AddError(TEXT("Mission 2 requires exactly three governed waves."));
	}
	if (Mission->Weather.ProfileId != TEXT("HarborOvercast"))
	{
		AddError(TEXT("Mission 2 weather must be HarborOvercast."));
	}
	if (Mission->Presentation.Briefing.IsEmpty() ||
		Mission->Presentation.RadioChatter.Num() < 3 ||
		Mission->Presentation.MinimumBriefingWarmupSeconds < 0.f)
	{
		AddError(TEXT("Mission 2 briefing/radio contract is incomplete."));
	}
	return OutErrors.IsEmpty();
}
