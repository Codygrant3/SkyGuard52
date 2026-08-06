#include "SkyguardGameMode.h"
#include "SkyguardGunner.h"
#include "SkyguardYak52Aircraft.h"
#include "SkyguardCampaignDefinition.h"
#include "SkyguardCampaignSubsystem.h"
#include "SkyguardGameUserSettings.h"
#include "Components/SceneComponent.h"
#include "Dom/JsonObject.h"
#include "Engine/GameInstance.h"
#include "EngineUtils.h"
#include "GameFramework/Controller.h"
#include "GameFramework/InputSettings.h"
#include "GameFramework/PlayerController.h"
#include "HAL/FileManager.h"
#include "HAL/PlatformMisc.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/App.h"
#include "Misc/CommandLine.h"
#include "Misc/DateTime.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Misc/Parse.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"
#include "TimerManager.h"

namespace
{
	TSharedRef<FJsonObject> MakeValidationCase(
		const FString& Name,
		const bool bPassed,
		const FString& Detail)
	{
		const TSharedRef<FJsonObject> Case = MakeShared<FJsonObject>();
		Case->SetStringField(TEXT("name"), Name);
		Case->SetStringField(TEXT("result"), bPassed ? TEXT("PASS") : TEXT("FAIL"));
		Case->SetStringField(TEXT("detail"), Detail);
		return Case;
	}

	void AddValidationCase(
		TArray<TSharedPtr<FJsonValue>>& Cases,
		bool& bAllPassed,
		const FString& Name,
		const bool bPassed,
		const FString& Detail)
	{
		Cases.Add(MakeShared<FJsonValueObject>(
			MakeValidationCase(Name, bPassed, Detail)));
		bAllPassed &= bPassed;
	}

	bool HasActionMapping(const FName Name)
	{
		const UInputSettings* Settings = GetDefault<UInputSettings>();
		if (!Settings)
		{
			return false;
		}
		TArray<FInputActionKeyMapping> Mappings;
		Settings->GetActionMappingByName(Name, Mappings);
		return Mappings.Num() > 0;
	}

	bool HasAxisMapping(const FName Name)
	{
		const UInputSettings* Settings = GetDefault<UInputSettings>();
		if (!Settings)
		{
			return false;
		}
		TArray<FInputAxisKeyMapping> Mappings;
		Settings->GetAxisMappingByName(Name, Mappings);
		return Mappings.Num() > 0;
	}
}

ASkyguardGameMode::ASkyguardGameMode()
{
	DefaultPawnClass = ASkyguardGunner::StaticClass();
}

APawn* ASkyguardGameMode::SpawnDefaultPawnAtTransform_Implementation(
	AController* NewPlayer,
	const FTransform& SpawnTransform)
{
	UWorld* World = GetWorld();
	if (!World || !NewPlayer)
	{
		return nullptr;
	}

	for (TActorIterator<ASkyguardGunner> It(World); It; ++It)
	{
		ASkyguardGunner* ExistingGunner = *It;
		if (IsValid(ExistingGunner) &&
			(!ExistingGunner->GetController() ||
			 ExistingGunner->GetController() == NewPlayer))
		{
			return ExistingGunner;
		}
	}

	FTransform SafeSpawnTransform = SpawnTransform;
	for (TActorIterator<ASkyguardYak52Aircraft> It(World); It; ++It)
	{
		ASkyguardYak52Aircraft* Aircraft = *It;
		if (IsValid(Aircraft) && Aircraft->GetRearGunnerMount())
		{
			SafeSpawnTransform =
				Aircraft->GetRearGunnerMount()->GetComponentTransform();
			break;
		}
	}

	UClass* PawnClass = GetDefaultPawnClassForController(NewPlayer);
	if (!PawnClass)
	{
		return nullptr;
	}

	FActorSpawnParameters Parameters;
	Parameters.Owner = NewPlayer;
	Parameters.SpawnCollisionHandlingOverride =
		ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
	return World->SpawnActor<APawn>(
		PawnClass,
		SafeSpawnTransform,
		Parameters);
}

void ASkyguardGameMode::BeginPlay()
{
	Super::BeginPlay();

	float SmokeSeconds = 0.f;
	if (!FParse::Value(
			FCommandLine::Get(),
			TEXT("SkyguardStartupSmokeSeconds="),
			SmokeSeconds))
	{
		FParse::Value(
			FCommandLine::Get(),
			TEXT("SkyguardRuntimeValidationArtifact="),
			RuntimeValidationArtifactPath);
		FParse::Value(
			FCommandLine::Get(),
			TEXT("SkyguardRuntimeValidationPhase="),
			RuntimeValidationPhase);
		if (!RuntimeValidationArtifactPath.IsEmpty() &&
			(RuntimeValidationPhase == 1 || RuntimeValidationPhase == 2))
		{
			GetWorldTimerManager().SetTimer(
				RuntimeValidationTimer,
				this,
				&ASkyguardGameMode::RunPackagedRuntimeValidation,
				1.f,
				false);
		}
		return;
	}

	SmokeSeconds = FMath::Clamp(SmokeSeconds, 1.f, 600.f);
	FParse::Value(
		FCommandLine::Get(),
		TEXT("SkyguardStartupSmokeReceipt="),
		StartupSmokeReceiptPath);
	StartupSmokeMapName = GetWorld() ? GetWorld()->GetMapName() : TEXT("None");
	WriteStartupSmokeReceipt(TEXT("MAP_READY"));
	GetWorldTimerManager().SetTimer(
		StartupSmokeTimer,
		this,
		&ASkyguardGameMode::CompleteStartupSmoke,
		SmokeSeconds,
		false);
}

void ASkyguardGameMode::CompleteStartupSmoke()
{
	WriteStartupSmokeReceipt(TEXT("COMPLETE"));
	FPlatformMisc::RequestExitWithStatus(
		false,
		0,
		TEXT("SkyguardStartupSmokeComplete"));
}

bool ASkyguardGameMode::WriteStartupSmokeReceipt(const TCHAR* State) const
{
	if (StartupSmokeReceiptPath.IsEmpty())
	{
		return false;
	}

	const FString ReceiptDirectory = FPaths::GetPath(StartupSmokeReceiptPath);
	if (!ReceiptDirectory.IsEmpty())
	{
		IFileManager::Get().MakeDirectory(*ReceiptDirectory, true);
	}

	const TSharedRef<FJsonObject> Receipt = MakeShared<FJsonObject>();
	Receipt->SetStringField(
		TEXT("schema"),
		TEXT("skyguard.shipping-startup-smoke.v1"));
	Receipt->SetStringField(TEXT("state"), State);
	Receipt->SetStringField(TEXT("map"), StartupSmokeMapName);
	Receipt->SetStringField(TEXT("rhi"), FApp::GetGraphicsRHI());
	Receipt->SetStringField(
		TEXT("written_at_utc"),
		FDateTime::UtcNow().ToIso8601());

	FString Json;
	const TSharedRef<TJsonWriter<>> Writer =
		TJsonWriterFactory<>::Create(&Json);
	if (!FJsonSerializer::Serialize(Receipt, Writer))
	{
		return false;
	}
	return FFileHelper::SaveStringToFile(
		Json,
		*StartupSmokeReceiptPath,
		FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
}

void ASkyguardGameMode::RunPackagedRuntimeValidation()
{
	TArray<TSharedPtr<FJsonValue>> InputCases;
	TArray<TSharedPtr<FJsonValue>> SaveCases;
	TArray<TSharedPtr<FJsonValue>> SettingsCases;
	bool bInputPassed = true;
	bool bSavePassed = true;
	bool bSettingsPassed = true;

	APlayerController* PlayerController =
		GetWorld() ? GetWorld()->GetFirstPlayerController() : nullptr;
	ASkyguardGunner* Gunner = PlayerController
		? Cast<ASkyguardGunner>(PlayerController->GetPawn())
		: nullptr;
	int32 GunnerCount = 0;
	for (TActorIterator<ASkyguardGunner> It(GetWorld()); It; ++It)
	{
		++GunnerCount;
	}
	ASkyguardYak52Aircraft* YakAircraft = nullptr;
	for (TActorIterator<ASkyguardYak52Aircraft> It(GetWorld()); It; ++It)
	{
		YakAircraft = *It;
		break;
	}
	AddValidationCase(
		InputCases, bInputPassed, TEXT("player_controller_exists"),
		PlayerController != nullptr, TEXT("World has a player controller"));
	AddValidationCase(
		InputCases, bInputPassed, TEXT("player_possesses_gunner"),
		Gunner != nullptr,
		TEXT("Player controller pawn is SkyguardGunner"));
	AddValidationCase(
		InputCases, bInputPassed, TEXT("controller_pawn_reciprocity"),
		Gunner && Gunner->GetController() == PlayerController,
		TEXT("Gunner controller and player-controller pawn agree"));
	AddValidationCase(
		InputCases, bInputPassed, TEXT("exactly_one_gunner"),
		GunnerCount == 1,
		FString::Printf(TEXT("Runtime gunner count is %d"), GunnerCount));
	AddValidationCase(
		InputCases, bInputPassed, TEXT("gunner_mounted_to_yak"),
		Gunner && YakAircraft &&
			Gunner->GetAttachParentActor() == YakAircraft,
		TEXT("Possessed gunner is attached to the Yak-52"));
	AddValidationCase(
		InputCases, bInputPassed, TEXT("action_fire_bound"),
		HasActionMapping(TEXT("Fire")), TEXT("DefaultInput Fire mapping"));
	AddValidationCase(
		InputCases, bInputPassed, TEXT("action_ads_bound"),
		HasActionMapping(TEXT("ADS")), TEXT("DefaultInput ADS mapping"));
	AddValidationCase(
		InputCases, bInputPassed, TEXT("action_switch_weapon_bound"),
		HasActionMapping(TEXT("SwitchWeapon")),
		TEXT("DefaultInput SwitchWeapon mapping"));
	AddValidationCase(
		InputCases, bInputPassed, TEXT("action_launch_igla_bound"),
		HasActionMapping(TEXT("LaunchIgla")),
		TEXT("DefaultInput LaunchIgla mapping"));
	AddValidationCase(
		InputCases, bInputPassed, TEXT("axis_turn_bound"),
		HasAxisMapping(TEXT("Turn")), TEXT("DefaultInput Turn mapping"));
	AddValidationCase(
		InputCases, bInputPassed, TEXT("axis_lookup_bound"),
		HasAxisMapping(TEXT("LookUp")), TEXT("DefaultInput LookUp mapping"));

	bool bAdsFireCoexists = false;
	bool bForwardBlocked = false;
	bool bSideAllowed = false;
	if (Gunner)
	{
		Gunner->ADSPressed();
		Gunner->FirePressed();
		bAdsFireCoexists = Gunner->bADS && Gunner->bFireHeld;
		Gunner->FireReleased();
		Gunner->ADSReleased();
		Gunner->Yaw = 0.f;
		bForwardBlocked = !Gunner->IsRifleDirectionOutsidePilotSafetyArc();
		Gunner->Yaw = Gunner->MinimumSafeSideFireYaw + 5.f;
		bSideAllowed = Gunner->IsRifleDirectionOutsidePilotSafetyArc();
	}
	AddValidationCase(
		InputCases, bInputPassed, TEXT("ads_plus_left_fire_coexists"),
		Gunner && bAdsFireCoexists,
		TEXT("ADS remains active while left fire is held"));
	AddValidationCase(
		InputCases, bInputPassed, TEXT("pilot_forward_safety_arc_blocks"),
		Gunner && bForwardBlocked,
		TEXT("Forward centerline is a no-fire sector"));
	AddValidationCase(
		InputCases, bInputPassed, TEXT("side_fire_sector_allows"),
		Gunner && bSideAllowed,
		TEXT("Rifle clears the pilot safety arc at side yaw"));

	const FString SlotName = TEXT("SkyguardPhase8RuntimeValidation");
	UGameInstance* GameInstance = GetGameInstance();
	USkyguardCampaignSubsystem* CampaignSubsystem = GameInstance
		? GameInstance->GetSubsystem<USkyguardCampaignSubsystem>()
		: nullptr;
	USkyguardCampaignDefinition* Campaign = LoadObject<USkyguardCampaignDefinition>(
		nullptr,
		TEXT("/Game/Skyguard/Data/Campaign_v1/DA_Campaign_Skyguard52.DA_Campaign_Skyguard52"));
	const bool bCampaignConfigured =
		CampaignSubsystem && Campaign &&
		CampaignSubsystem->ConfigureCampaign(Campaign);
	AddValidationCase(
		SaveCases, bSavePassed, TEXT("campaign_configured"),
		bCampaignConfigured, TEXT("Cooked campaign DataAsset configured"));

	if (RuntimeValidationPhase == 1)
	{
		const bool bPriorSlotCleared =
			!UGameplayStatics::DoesSaveGameExist(SlotName, 0) ||
			(CampaignSubsystem &&
			 CampaignSubsystem->DeleteCampaignSlot(SlotName, 0));
		AddValidationCase(
			SaveCases, bSavePassed, TEXT("prior_validation_slot_cleared"),
			bPriorSlotCleared, TEXT("Validation starts from a clean slot"));
		const bool bSaved =
			bCampaignConfigured &&
			CampaignSubsystem->SaveCampaignToSlot(SlotName, 0);
		AddValidationCase(
			SaveCases, bSavePassed, TEXT("campaign_saved_to_disk"),
			bSaved, TEXT("SaveCampaignToSlot returned true"));
		AddValidationCase(
			SaveCases, bSavePassed, TEXT("campaign_slot_exists"),
			UGameplayStatics::DoesSaveGameExist(SlotName, 0),
			TEXT("Disk slot is visible after save"));
	}
	else
	{
		const bool bSlotExists =
			UGameplayStatics::DoesSaveGameExist(SlotName, 0);
		AddValidationCase(
			SaveCases, bSavePassed, TEXT("campaign_slot_survived_relaunch"),
			bSlotExists, TEXT("Phase 1 disk slot exists in phase 2"));
		const bool bLoaded =
			bCampaignConfigured &&
			CampaignSubsystem->LoadCampaignFromSlot(SlotName, 0);
		AddValidationCase(
			SaveCases, bSavePassed, TEXT("campaign_loaded_after_relaunch"),
			bLoaded, TEXT("LoadCampaignFromSlot returned true"));
		const bool bDeleted =
			CampaignSubsystem &&
			CampaignSubsystem->DeleteCampaignSlot(SlotName, 0);
		AddValidationCase(
			SaveCases, bSavePassed, TEXT("validation_slot_deleted"),
			bDeleted, TEXT("Validation slot cleanup returned true"));
		AddValidationCase(
			SaveCases, bSavePassed, TEXT("validation_slot_absent"),
			!UGameplayStatics::DoesSaveGameExist(SlotName, 0),
			TEXT("Validation slot is absent after cleanup"));
	}

	USkyguardGameUserSettings* UserSettings =
		USkyguardGameUserSettings::GetSkyguardGameUserSettings();
	AddValidationCase(
		SettingsCases, bSettingsPassed, TEXT("settings_instance_available"),
		UserSettings != nullptr, TEXT("Skyguard GameUserSettings instance"));
	if (RuntimeValidationPhase == 1 && UserSettings)
	{
		UserSettings->SetMasterVolume(0.73f);
		UserSettings->SetMouseSensitivity(0.11f);
		UserSettings->SetInvertVerticalLook(true);
		UserSettings->SetCameraShakeScale(0.64f);
		UserSettings->ApplyAndSaveSettings(false);
		AddValidationCase(
			SettingsCases, bSettingsPassed, TEXT("master_volume_seeded"),
			FMath::IsNearlyEqual(UserSettings->GetMasterVolume(), 0.73f),
			TEXT("Master volume set to validation value"));
		AddValidationCase(
			SettingsCases, bSettingsPassed, TEXT("mouse_sensitivity_seeded"),
			FMath::IsNearlyEqual(UserSettings->GetMouseSensitivity(), 0.11f),
			TEXT("Mouse sensitivity set to validation value"));
		AddValidationCase(
			SettingsCases, bSettingsPassed, TEXT("invert_look_seeded"),
			UserSettings->GetInvertVerticalLook(),
			TEXT("Invert vertical look enabled"));
		AddValidationCase(
			SettingsCases, bSettingsPassed, TEXT("camera_shake_seeded"),
			FMath::IsNearlyEqual(UserSettings->GetCameraShakeScale(), 0.64f),
			TEXT("Camera shake set to validation value"));
	}
	else if (UserSettings)
	{
		AddValidationCase(
			SettingsCases, bSettingsPassed, TEXT("master_volume_persisted"),
			FMath::IsNearlyEqual(UserSettings->GetMasterVolume(), 0.73f),
			TEXT("Master volume survived relaunch"));
		AddValidationCase(
			SettingsCases, bSettingsPassed, TEXT("mouse_sensitivity_persisted"),
			FMath::IsNearlyEqual(UserSettings->GetMouseSensitivity(), 0.11f),
			TEXT("Mouse sensitivity survived relaunch"));
		AddValidationCase(
			SettingsCases, bSettingsPassed, TEXT("invert_look_persisted"),
			UserSettings->GetInvertVerticalLook(),
			TEXT("Invert vertical look survived relaunch"));
		AddValidationCase(
			SettingsCases, bSettingsPassed, TEXT("camera_shake_persisted"),
			FMath::IsNearlyEqual(UserSettings->GetCameraShakeScale(), 0.64f),
			TEXT("Camera shake survived relaunch"));
		UserSettings->SetToDefaults();
		UserSettings->ApplyAndSaveSettings(false);
	}

	const bool bAllPassed = bInputPassed && bSavePassed && bSettingsPassed;
	const TSharedRef<FJsonObject> Receipt = MakeShared<FJsonObject>();
	Receipt->SetStringField(
		TEXT("schema"),
		TEXT("skyguard.packaged-runtime-validation-launch.v1"));
	Receipt->SetNumberField(TEXT("phase"), RuntimeValidationPhase);
	Receipt->SetStringField(
		TEXT("gate"), bAllPassed ? TEXT("PASS") : TEXT("FAIL"));
	Receipt->SetStringField(
		TEXT("map"),
		GetWorld() ? GetWorld()->GetMapName() : TEXT("None"));
	Receipt->SetStringField(TEXT("rhi"), FApp::GetGraphicsRHI());
	Receipt->SetArrayField(TEXT("input_cases"), InputCases);
	Receipt->SetArrayField(TEXT("save_cases"), SaveCases);
	Receipt->SetArrayField(TEXT("settings_cases"), SettingsCases);
	Receipt->SetStringField(
		TEXT("written_at_utc"),
		FDateTime::UtcNow().ToIso8601());

	const FString Directory = FPaths::GetPath(RuntimeValidationArtifactPath);
	IFileManager::Get().MakeDirectory(*Directory, true);
	FString Json;
	const TSharedRef<TJsonWriter<>> Writer =
		TJsonWriterFactory<>::Create(&Json);
	const bool bSerialized = FJsonSerializer::Serialize(Receipt, Writer);
	const bool bWritten = bSerialized && FFileHelper::SaveStringToFile(
		Json,
		*RuntimeValidationArtifactPath,
		FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
	FPlatformMisc::RequestExitWithStatus(
		false,
		bAllPassed && bWritten ? 0 : 1,
		TEXT("SkyguardRuntimeValidationComplete"));
}
